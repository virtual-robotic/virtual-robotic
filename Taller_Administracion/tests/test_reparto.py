# Version: 2026-09-19 10:30 -- tests de la fase de reparto (Pedidos Taller / Reparto / albaranes)
"""Ciclo de un pedido en dos etapas (sesion 2026-09-19): el taller/almacen deja
las piezas LISTAS (cantidad_completada) y el reparto las ENTREGA
(cantidad_repartida) generando un albaran. `reparto_automatico` gobierna la
primera etapa (asignar stock) y `expedicion_automatica` la segunda."""
import datetime

from .conftest import (
    asignar_producto,
    auth,
    crear_cliente_con_usuario,
    crear_usuario_normal,
    login,
    producto_por_color,
    subproducto_por_color,
)
from .test_almacen import _preparar_pedido


def _config(client, admin_headers, **kw):
    r = client.patch("/almacen/configuracion", headers=admin_headers, json=kw)
    assert r.status_code == 200, r.text
    return r.json()


def _pieza(client, color="R", **kw):
    r = client.post("/taller/cubo_clasificado", json={"color": color, **kw})
    assert r.status_code == 200, r.text
    return r.json()


def _pedido(client, headers, pedido_id):
    return client.get(f"/pedidos/{pedido_id}", headers=headers).json()


def test_por_defecto_todo_automatico_el_pedido_termina_repartido_con_albaran(client, admin_headers):
    ctx = _preparar_pedido(client, admin_headers, cantidad=2)
    _pieza(client)
    ultimo = _pieza(client)
    assert ultimo["pedido"]["estado"] == "completado"
    assert ultimo["pedido"]["cantidad_repartida"] == 2

    repartos = client.get("/repartos", headers=admin_headers).json()
    assert len(repartos) == 1
    assert repartos[0]["automatico"] is True
    assert repartos[0]["numero"] == f"ALB-{datetime.datetime.utcnow().year}-000001"
    assert [(l["pedido_id"], l["cantidad"]) for l in repartos[0]["lineas"]] == [(ctx["pedido"]["id"], 2)]


def test_expedicion_manual_deja_el_pedido_listo_sin_albaran(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=2)
    _pieza(client)
    ultimo = _pieza(client)
    assert ultimo["pedido"]["estado"] == "listo"
    assert ultimo["pedido"]["cantidad_completada"] == 2
    assert ultimo["pedido"]["cantidad_repartida"] == 0
    assert ultimo["pedido"]["para_repartir"] == 2
    assert ultimo["pedido"]["falta_fabricar"] == 0
    assert client.get("/repartos", headers=admin_headers).json() == []
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "listo"


def test_expedir_a_mano_genera_albaran_y_cierra_el_pedido(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _pieza(client)
    r = client.post("/reparto/expedir", headers=admin_headers, json={"pedido_ids": [ctx["pedido"]["id"]]})
    assert r.status_code == 200, r.text
    (albaran,) = r.json()
    assert albaran["automatico"] is False
    assert albaran["usuario_id"] is not None
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "completado"
    # repartir dos veces no duplica nada
    assert client.post("/reparto/expedir", headers=admin_headers, json={}).json() == []


def test_un_albaran_por_cliente_con_numeros_correlativos(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    a = _preparar_pedido(client, admin_headers, color="R", cantidad=1)
    b = _preparar_pedido(client, admin_headers, color="G", cantidad=1)
    # otro pedido del MISMO cliente que a
    sub_b = subproducto_por_color(client, admin_headers, "B")
    prod_b = producto_por_color(client, admin_headers, "B")
    asignar_producto(client, admin_headers, a["pedido"]["cliente_id"], prod_b["id"])
    c = client.post("/pedidos", headers=auth(a["tok_normal"]),
                    json={"subproducto_id": sub_b["id"], "cantidad_pedida": 1}).json()
    _pieza(client, "R")
    _pieza(client, "G")
    _pieza(client, "B")

    albaranes = client.post("/reparto/expedir", headers=admin_headers, json={}).json()
    assert len(albaranes) == 2  # dos clientes -> dos albaranes
    numeros = sorted(x["numero"] for x in albaranes)
    anio = datetime.datetime.utcnow().year
    assert numeros == [f"ALB-{anio}-000001", f"ALB-{anio}-000002"]
    del_cliente_a = next(x for x in albaranes if x["cliente_id"] == a["pedido"]["cliente_id"])
    assert sorted(l["pedido_id"] for l in del_cliente_a["lineas"]) == sorted([a["pedido"]["id"], c["id"]])
    assert any(x["cliente_id"] == b["pedido"]["cliente_id"] for x in albaranes)


def test_entrega_parcial_y_luego_el_resto(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=3)
    _pieza(client)
    _pieza(client)
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["para_repartir"], p["falta_fabricar"]) == ("en_proceso", 2, 1)

    client.post("/reparto/expedir", headers=admin_headers, json={})
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["cantidad_repartida"], p["para_repartir"]) == ("en_proceso", 2, 0)

    _pieza(client)
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "listo"
    client.post("/reparto/expedir", headers=admin_headers, json={})
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["cantidad_repartida"]) == ("completado", 3)
    cantidades = [l["cantidad"] for r in client.get("/repartos", headers=admin_headers).json() for l in r["lineas"]]
    assert sorted(cantidades) == [1, 2]


def test_activar_expedicion_automatica_saca_lo_que_esperaba_listo(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _pieza(client)
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "listo"
    _config(client, admin_headers, expedicion_automatica=True)
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "completado"
    assert len(client.get("/repartos", headers=admin_headers).json()) == 1


def test_pedido_listo_ya_no_recibe_mas_piezas(client, admin_headers):
    """Un pedido 'listo' tiene todo lo que pidio: la pieza siguiente va al
    stock, no se le vuelve a asignar (aunque venga con su pedido_id)."""
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    _pieza(client)
    r = _pieza(client, pedido_id=ctx["pedido"]["id"])
    assert r["pedido"] is None
    assert r["stock_actual"] == 1
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["cantidad_completada"] == 1


def test_repartir_a_mano_un_pedido_cubierto_por_stock_lo_asigna_y_entrega(client, admin_headers):
    _config(client, admin_headers, reparto_automatico=False, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, color="B", cantidad=4)
    client.post("/almacen/ajustar", headers=admin_headers,
                json={"producto_id": ctx["producto"]["id"], "cantidad": 4})
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["stock_disponible"], p["para_repartir"], p["falta_fabricar"]) == ("pendiente", 4, 4, 0)

    client.post("/reparto/expedir", headers=admin_headers, json={"pedido_ids": [ctx["pedido"]["id"]]})
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["cantidad_repartida"]) == ("completado", 4)
    stock = next(s for s in client.get("/stock", headers=admin_headers).json()
                 if s["producto_id"] == ctx["producto"]["id"])
    assert stock["cantidad_actual"] == 0


def test_asignar_stock_con_expedicion_manual_deja_el_pedido_listo(client, admin_headers):
    _config(client, admin_headers, reparto_automatico=False, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, color="B", cantidad=2)
    client.post("/almacen/ajustar", headers=admin_headers,
                json={"producto_id": ctx["producto"]["id"], "cantidad": 2})
    client.post("/almacen/repartir", headers=admin_headers)
    assert _pedido(client, admin_headers, ctx["pedido"]["id"])["estado"] == "listo"


def test_pedido_nuevo_con_stock_y_expedicion_automatica_nace_completado(client, admin_headers):
    for _ in range(2):
        _pieza(client)
    ctx = _preparar_pedido(client, admin_headers, cantidad=2)
    p = _pedido(client, admin_headers, ctx["pedido"]["id"])
    assert (p["estado"], p["cantidad_repartida"]) == ("completado", 2)


def test_precio_y_iva_quedan_congelados_en_el_pedido_y_el_albaran(client, admin_headers):
    sub = subproducto_por_color(client, admin_headers, "R")
    r = client.patch(f"/subproductos/{sub['id']}", headers=admin_headers,
                     json={"precio_centimos": 150, "iva_porcentaje": 21})
    assert r.status_code == 200, r.text
    ctx = _preparar_pedido(client, admin_headers, cantidad=2)
    assert ctx["pedido"]["precio_unitario_centimos"] == 150

    # la tarifa sube DESPUES de pedir: lo vendido no cambia
    client.patch(f"/subproductos/{sub['id']}", headers=admin_headers, json={"precio_centimos": 999})
    _pieza(client)
    _pieza(client)
    (albaran,) = client.get("/repartos", headers=admin_headers).json()
    (linea,) = albaran["lineas"]
    assert linea["precio_unitario_centimos"] == 150
    assert linea["base_centimos"] == 300
    # 300 de base + 21% = 63 de IVA -> 363
    assert (albaran["base_centimos"], albaran["iva_centimos"], albaran["total_centimos"]) == (300, 63, 363)


def test_la_descripcion_del_albaran_no_cambia_si_se_renombra_el_subproducto(client, admin_headers):
    sub = subproducto_por_color(client, admin_headers, "R")
    _preparar_pedido(client, admin_headers, cantidad=1)
    _pieza(client)
    client.patch(f"/subproductos/{sub['id']}", headers=admin_headers, json={"nombre": "Nombre nuevo"})
    (albaran,) = client.get("/repartos", headers=admin_headers).json()
    assert "Nombre nuevo" not in albaran["lineas"][0]["descripcion"]


def test_precio_negativo_o_iva_fuera_de_rango_se_rechazan(client, admin_headers):
    sub = subproducto_por_color(client, admin_headers, "R")
    assert client.patch(f"/subproductos/{sub['id']}", headers=admin_headers,
                        json={"precio_centimos": -1}).status_code == 400
    assert client.patch(f"/subproductos/{sub['id']}", headers=admin_headers,
                        json={"iva_porcentaje": 101}).status_code == 400


def test_config_parcial_no_pisa_el_otro_interruptor(client, admin_headers):
    _config(client, admin_headers, reparto_automatico=False)
    cfg = _config(client, admin_headers, expedicion_automatica=False)
    assert (cfg["reparto_automatico"], cfg["expedicion_automatica"]) == (False, False)
    cfg = _config(client, admin_headers, expedicion_automatica=True)
    assert (cfg["reparto_automatico"], cfg["expedicion_automatica"]) == (False, True)
    assert client.patch("/almacen/configuracion", headers=admin_headers, json={}).status_code == 400


class TestPermisosAlbaranes:
    def _albaran_de(self, client, admin_headers, color):
        ctx = _preparar_pedido(client, admin_headers, color=color, cantidad=1)
        _pieza(client, color)
        return ctx

    def test_admin_cliente_solo_ve_los_albaranes_de_su_empresa(self, client, admin_headers):
        a = self._albaran_de(client, admin_headers, "R")
        b = self._albaran_de(client, admin_headers, "G")
        propios = client.get("/repartos", headers=auth(a["tok_admin_cliente"])).json()
        assert [x["cliente_id"] for x in propios] == [a["pedido"]["cliente_id"]]
        ajeno_id = client.get("/repartos", headers=admin_headers).json()
        ajeno = next(x for x in ajeno_id if x["cliente_id"] == b["pedido"]["cliente_id"])
        assert client.get(f"/repartos/{ajeno['id']}", headers=auth(a["tok_admin_cliente"])).status_code == 403

    def test_usuario_normal_no_ve_albaranes_ni_reparte(self, client, admin_headers):
        a = self._albaran_de(client, admin_headers, "R")
        assert client.get("/repartos", headers=auth(a["tok_normal"])).status_code == 403
        assert client.post("/reparto/expedir", headers=auth(a["tok_normal"]), json={}).status_code == 403

    def test_solo_admin_sistema_reparta(self, client, admin_headers):
        a = self._albaran_de(client, admin_headers, "R")
        r = client.post("/reparto/expedir", headers=auth(a["tok_admin_cliente"]), json={})
        assert r.status_code == 403

    def test_expedir_pedido_inexistente_da_404(self, client, admin_headers):
        r = client.post("/reparto/expedir", headers=admin_headers, json={"pedido_ids": [9999]})
        assert r.status_code == 404


def test_datos_fiscales_del_cliente_se_guardan(client, admin_headers):
    cliente, _tok = crear_cliente_con_usuario(client, admin_headers, "Fiscal SL", "fiscal")
    r = client.patch(
        f"/clientes/{cliente['id']}", headers=admin_headers,
        json={"cif": "B12345678", "direccion": "Calle Mayor 1", "codigo_postal": "48001",
              "poblacion": "Bilbao", "provincia": "Bizkaia", "email_facturacion": "facturas@fiscal.test"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["direccion"] == "Calle Mayor 1"
    assert r.json()["email_facturacion"] == "facturas@fiscal.test"


def test_pedido_cancelado_no_se_reparte(client, admin_headers):
    _config(client, admin_headers, expedicion_automatica=False)
    ctx = _preparar_pedido(client, admin_headers, cantidad=1)
    client.post(f"/pedidos/{ctx['pedido']['id']}/cancelar", headers=admin_headers)
    assert client.post("/reparto/expedir", headers=admin_headers, json={}).json() == []


def test_iva_redondea_el_medio_centimo_hacia_arriba(client, admin_headers):
    """5 x 10 cts = 50 de base; 25% de 50 = 12,5 -> 13 (round() de Python daria
    12, y una factura no puede redondear al par)."""
    sub = subproducto_por_color(client, admin_headers, "R")
    client.patch(f"/subproductos/{sub['id']}", headers=admin_headers,
                 json={"precio_centimos": 10, "iva_porcentaje": 25})
    _preparar_pedido(client, admin_headers, cantidad=5)
    for _ in range(5):
        _pieza(client)
    (albaran,) = client.get("/repartos", headers=admin_headers).json()
    assert (albaran["base_centimos"], albaran["iva_centimos"], albaran["total_centimos"]) == (50, 13, 63)
