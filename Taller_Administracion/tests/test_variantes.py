# Version: 2026-09-28 21:05 -- cada subproducto es una pieza distinta (stock y reparto por variante)
"""Decision del usuario (2026-09-28): "las de 10mm con las de 10mm y las de 20mm con las de 20mm".
Tornillo 10mm y Tornillo 20mm son del mismo producto (y del mismo LED), pero son piezas distintas:
una nunca completa un pedido de la otra, ni al llegar ni desde el almacen."""
from app import models
from app.database import SessionLocal
from app.main import _pasar_stock_antiguo_de_una_variante, barrer_stock

from .conftest import (
    asignar_producto,
    auth,
    crear_cliente_con_usuario,
    crear_usuario_normal,
    login,
    producto_por_color,
)

_contador = 0


def _variantes_rojo(client, admin_headers):
    """(producto Tornillos, Tornillo 10mm, Tornillo 20mm) del seed."""
    producto = producto_por_color(client, admin_headers, "R")
    subs = client.get("/subproductos", headers=admin_headers, params={"producto_id": producto["id"]}).json()
    por_nombre = {s["nombre"]: s for s in subs}
    return producto, por_nombre["Tornillo 10mm"], por_nombre["Tornillo 20mm"]


def _pedir(client, admin_headers, producto, sub, cantidad):
    global _contador
    _contador += 1
    cliente, _tok = crear_cliente_con_usuario(client, admin_headers, f"Empresa var{_contador}", f"var{_contador}")
    asignar_producto(client, admin_headers, cliente["id"], producto["id"])
    crear_usuario_normal(client, admin_headers, cliente["id"], f"opvar{_contador}")
    r = client.post("/pedidos", headers=auth(login(client, f"opvar{_contador}")),
                    json={"subproducto_id": sub["id"], "cantidad_pedida": cantidad})
    assert r.status_code == 200, r.text
    return r.json()


def _pedido(client, admin_headers, pedido_id):
    return client.get(f"/pedidos/{pedido_id}", headers=admin_headers).json()


def _stock(client, admin_headers, sub):
    return next(s["cantidad_actual"] for s in client.get("/stock", headers=admin_headers).json()
                if s["subproducto_id"] == sub["id"])


def test_una_pieza_de_10mm_no_completa_un_pedido_de_20mm(client, admin_headers):
    producto, m10, m20 = _variantes_rojo(client, admin_headers)
    p20 = _pedir(client, admin_headers, producto, m20, 1)
    r = client.post("/taller/cubo_clasificado", json={"color": "R", "subproducto_id": m10["id"]})
    assert r.json()["pedido"] is None                      # no hay pedido de 10mm: al almacen
    assert _pedido(client, admin_headers, p20["id"])["cantidad_completada"] == 0
    assert _stock(client, admin_headers, m10) == 1 and _stock(client, admin_headers, m20) == 0


def test_cada_pieza_va_al_pedido_de_su_variante_aunque_el_otro_sea_mas_antiguo(client, admin_headers):
    producto, m10, m20 = _variantes_rojo(client, admin_headers)
    p10 = _pedir(client, admin_headers, producto, m10, 1)   # mas antiguo
    p20 = _pedir(client, admin_headers, producto, m20, 1)
    r = client.post("/taller/cubo_clasificado", json={"color": "R", "subproducto_id": m20["id"]})
    assert r.json()["pedido"]["id"] == p20["id"]
    assert _pedido(client, admin_headers, p10["id"])["cantidad_completada"] == 0


def test_el_stock_de_una_variante_no_cubre_pedidos_de_la_otra(client, admin_headers):
    producto, m10, m20 = _variantes_rojo(client, admin_headers)
    client.post("/almacen/ajustar", headers=admin_headers, json={"subproducto_id": m10["id"], "cantidad": 5})
    p20 = _pedir(client, admin_headers, producto, m20, 2)   # al pedirlo, no se sirve del stock de 10mm
    p = _pedido(client, admin_headers, p20["id"])
    assert (p["cantidad_completada"], p["stock_disponible"], p["falta_fabricar"]) == (0, 0, 2)
    db = SessionLocal()
    try:
        assert barrer_stock(db) == []                        # ni el barrido
    finally:
        db.close()
    assert _stock(client, admin_headers, m10) == 5


def test_el_stock_de_su_variante_si_lo_cubre(client, admin_headers):
    producto, m10, _m20 = _variantes_rojo(client, admin_headers)
    client.post("/almacen/ajustar", headers=admin_headers, json={"subproducto_id": m10["id"], "cantidad": 2})
    p10 = _pedir(client, admin_headers, producto, m10, 2)
    assert _pedido(client, admin_headers, p10["id"])["cantidad_completada"] == 2


def test_el_almacen_tiene_una_fila_por_variante(client, admin_headers):
    _producto, m10, m20 = _variantes_rojo(client, admin_headers)
    ids = [s["subproducto_id"] for s in client.get("/stock", headers=admin_headers).json()]
    assert m10["id"] in ids and m20["id"] in ids


def _meter_stock_antiguo(producto_id, cantidad):
    db = SessionLocal()
    try:
        db.add(models.Stock(producto_id=producto_id, cantidad_actual=cantidad))
        db.commit()
    finally:
        db.close()


def test_pasar_stock_antiguo_a_una_variante(client, admin_headers):
    producto, m10, m20 = _variantes_rojo(client, admin_headers)
    _meter_stock_antiguo(producto["id"], 7)
    r = client.post("/almacen/pasar_a_variante", headers=admin_headers,
                    json={"producto_id": producto["id"], "subproducto_id": m20["id"], "cantidad": 3})
    assert r.status_code == 200, r.text
    assert r.json()["cantidad_actual"] == 3
    antiguo = client.get("/stock/antiguo", headers=admin_headers).json()
    assert [(s["producto_id"], s["cantidad_actual"]) for s in antiguo] == [(producto["id"], 4)]
    motivos = [m["motivo"] for m in client.get("/movimientos_stock", headers=admin_headers).json()]
    assert motivos.count("paso_a_variante") == 2             # salida del antiguo + entrada en la variante


def test_pasar_stock_antiguo_rechaza_de_mas_o_de_otro_producto(client, admin_headers):
    producto, m10, _m20 = _variantes_rojo(client, admin_headers)
    otro = producto_por_color(client, admin_headers, "G")
    _meter_stock_antiguo(producto["id"], 2)
    de_mas = client.post("/almacen/pasar_a_variante", headers=admin_headers,
                         json={"producto_id": producto["id"], "subproducto_id": m10["id"], "cantidad": 3})
    assert de_mas.status_code == 400
    ajeno = client.post("/almacen/pasar_a_variante", headers=admin_headers,
                        json={"producto_id": otro["id"], "subproducto_id": m10["id"], "cantidad": 1})
    assert ajeno.status_code == 400


def test_al_arrancar_el_stock_antiguo_de_una_sola_variante_pasa_solo(client, admin_headers):
    tuercas = producto_por_color(client, admin_headers, "G")    # una sola variante en el seed
    tornillos, m10, m20 = _variantes_rojo(client, admin_headers)  # dos variantes
    _meter_stock_antiguo(tuercas["id"], 6)
    _meter_stock_antiguo(tornillos["id"], 7)
    db = SessionLocal()
    try:
        _pasar_stock_antiguo_de_una_variante(db)
    finally:
        db.close()
    antiguo = client.get("/stock/antiguo", headers=admin_headers).json()
    assert [(s["producto_id"], s["cantidad_actual"]) for s in antiguo] == [(tornillos["id"], 7)]  # lo decide el operario
    tuerca = client.get("/subproductos", headers=admin_headers, params={"producto_id": tuercas["id"]}).json()[0]
    assert _stock(client, admin_headers, tuerca) == 6
