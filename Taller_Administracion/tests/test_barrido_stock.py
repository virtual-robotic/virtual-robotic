# Version: 2026-09-20 11:22 -- tests del barrido de stock parado
"""barrer_stock: asigna el stock libre a los pedidos que cubre POR COMPLETO. Nace del incidente del
2026-09-19: la pieza 9 de 10 entro al almacen sin asignarse y el pedido se quedo parado."""
from app.database import SessionLocal
from app.main import barrer_stock

from .conftest import sub_de_producto, sub_id, auth
from .test_almacen import _preparar_pedido
from .test_paquete_un_albaran import _albaranes, _cliente_con_todo, _paquete, _pedir, _piezas


def _barrer():
    db = SessionLocal()
    try:
        return [p.id for p in barrer_stock(db)]
    finally:
        db.close()


def _pedido(client, headers, pedido_id):
    return client.get(f"/pedidos/{pedido_id}", headers=headers).json()


def _config(client, admin_headers, **kw):
    assert client.patch("/almacen/configuracion", headers=admin_headers, json=kw).status_code == 200


def _stock_huerfano(client, admin_headers, producto_id, n):
    """Stock que entra SIN asignarse a ningun pedido (ajuste manual: no dispara la asignacion)."""
    assert client.post("/almacen/ajustar", headers=admin_headers,
                       json={"subproducto_id": sub_de_producto(producto_id), "cantidad": n}).status_code == 200


def test_el_caso_del_9_de_10_la_pieza_que_faltaba_esta_en_el_almacen(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=10)
    pid = ctx["pedido"]["id"]
    _piezas(client, "R", 9)                                    # 9 asignadas al pedido
    _stock_huerfano(client, admin_headers, ctx["producto"]["id"], 1)   # la 10 entro al almacen sin asignarse
    p = _pedido(client, admin_headers, pid)
    assert (p["cantidad_completada"], p["falta_fabricar"], p["stock_disponible"]) == (9, 0, 1)  # parado: nadie fabricaria
    assert _barrer() == [pid]
    p = _pedido(client, admin_headers, pid)
    assert (p["cantidad_completada"], p["estado"], p["cantidad_repartida"]) == (10, "completado", 10)
    assert len(_albaranes(client, admin_headers)) == 1


def test_una_pieza_de_otra_maquina_no_completa_el_pedido_al_llegar_pero_el_barrido_si_lo_cierra(client, admin_headers):
    """La regla del 2026-09-14 sigue valiendo AL LLEGAR la pieza; el barrido solo actua cuando el stock cubre el pedido entero."""
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    client.post(f"/pedidos/{ctx['pedido']['id']}/reclamar", headers=admin_headers, json={"numero_maquina": 10, "forzar": True})
    r = client.post("/taller/cubo_clasificado", json={"color": "R", "subproducto_id": sub_id("R"), "numero_maquina": 20})
    assert r.json()["pedido"] is None and r.json()["stock_actual"] == 1     # al llegar: al almacen
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "pendiente"
    assert _barrer() == [ctx["pedido"]["id"]]                                # el barrido, despues, lo cierra
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "completado"


def test_no_asigna_si_el_stock_no_cubre_el_pedido_entero(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=5)
    _config(client, admin_headers, reparto_automatico=False)
    _piezas(client, "R", 2)                                                   # 2 al almacen, sin asignar
    _config(client, admin_headers, reparto_automatico=True)
    assert _barrer() == []
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["cantidad_completada"], p["stock_disponible"]) == (0, 2)


def test_un_pedido_sin_cubrir_no_bloquea_a_los_siguientes(client, admin_headers):
    grande = _preparar_pedido(client, admin_headers, cantidad=5)
    pequeno = _preparar_pedido(client, admin_headers, cantidad=1)
    _stock_huerfano(client, admin_headers, grande["producto"]["id"], 1)
    assert _barrer() == [pequeno["pedido"]["id"]]
    assert _pedido(client, admin_headers, grande["pedido"]["id"])["cantidad_completada"] == 0


def test_respeta_la_urgencia_y_luego_la_antiguedad(client, admin_headers):
    # Los tres pedidos existen ANTES de que entre el stock (si no, el propio alta ya se lo llevaria).
    viejo = _preparar_pedido(client, admin_headers, cantidad=1)
    medio = _preparar_pedido(client, admin_headers, cantidad=1)
    urgente = _preparar_pedido(client, admin_headers, cantidad=1)
    client.patch(f"/pedidos/{urgente['pedido']['id']}", headers=admin_headers, json={"urgente": True})
    producto_id = viejo["producto"]["id"]
    _stock_huerfano(client, admin_headers, producto_id, 1)
    assert _barrer() == [urgente["pedido"]["id"]]        # el urgente, aunque sea el mas nuevo
    _stock_huerfano(client, admin_headers, producto_id, 1)
    assert _barrer() == [viejo["pedido"]["id"]]          # luego, por antiguedad
    _stock_huerfano(client, admin_headers, producto_id, 1)
    assert _barrer() == [medio["pedido"]["id"]]


def test_con_el_reparto_automatico_apagado_no_hace_nada(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _config(client, admin_headers, reparto_automatico=False)
    _stock_huerfano(client, admin_headers, ctx["producto"]["id"], 1)
    assert _barrer() == []
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "pendiente"


def test_es_idempotente(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _stock_huerfano(client, admin_headers, ctx["producto"]["id"], 1)
    assert len(_barrer()) == 1
    assert _barrer() == []


def test_con_la_expedicion_manual_deja_el_pedido_listo_sin_albaran(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _config(client, admin_headers, expedicion_automatica=False)
    _stock_huerfano(client, admin_headers, ctx["producto"]["id"], 1)
    _barrer()
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "listo"
    assert _albaranes(client, admin_headers) == []


def test_un_paquete_asignado_por_el_barrido_sale_entero_en_un_albaran(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    _config(client, admin_headers, reparto_automatico=False)
    _pedir(client, tok, _paquete(client, admin_headers))
    for color in "RGB":
        _piezas(client, color, 10)                           # todo al almacen, sin asignar
    assert _albaranes(client, admin_headers) == []
    _config(client, admin_headers, reparto_automatico=True)
    assert len(_barrer()) == 3
    (albaran,) = _albaranes(client, admin_headers)
    assert len(albaran["lineas"]) == 4                       # el paquete + sus 3 productos


def test_deja_rastro_en_la_auditoria(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _stock_huerfano(client, admin_headers, ctx["producto"]["id"], 1)
    _barrer()
    auditoria = client.get("/audit", headers=admin_headers).json()
    assert any("barrido de stock" in (a["detalle"] or "") and a["usuario_id"] is None for a in auditoria)
