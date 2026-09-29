# Version: 2026-09-19 19:15 -- tests: un paquete se entrega en UN solo albaran
"""Pedir un Paquete crea un pedido por componente (ver crear_pedido_paquete). Se entregan
JUNTOS, en un albaran, cuando el paquete entero esta listo -- no un albaran por componente."""
from .conftest import (
    sub_id,
    asignar_producto,
    auth,
    crear_cliente_con_usuario,
    crear_usuario_normal,
    login,
    producto_por_color,
    subproducto_por_color,
)

_n = 0


def _cliente_con_todo(client, admin_headers):
    """Cliente nuevo con los tres productos asignados y un usuario normal."""
    global _n
    _n += 1
    cliente, _tok = crear_cliente_con_usuario(client, admin_headers, f"Empresa paq{_n}", f"paq{_n}")
    for color in "RGB":
        asignar_producto(client, admin_headers, cliente["id"], producto_por_color(client, admin_headers, color)["id"])
    crear_usuario_normal(client, admin_headers, cliente["id"], f"op_paq{_n}")
    return cliente, auth(login(client, f"op_paq{_n}"))


def _paquete(client, admin_headers, codigo="P010"):
    return next(p for p in client.get("/paquetes", headers=admin_headers).json() if p["codigo"] == codigo)


def _pedir(client, headers, paquete, cantidad=1):
    r = client.post("/pedidos/paquete", headers=headers, json={"paquete_id": paquete["id"], "cantidad": cantidad})
    assert r.status_code == 200, r.text
    return r.json()


def _piezas(client, color, n):
    for _ in range(n):
        assert client.post("/taller/cubo_clasificado", json={"color": color, "subproducto_id": sub_id(color)}).status_code == 200


def _albaranes(client, admin_headers):
    return client.get("/repartos", headers=admin_headers).json()


def test_los_componentes_de_un_paquete_comparten_grupo(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    pedidos = _pedir(client, tok, _paquete(client, admin_headers))
    assert len(pedidos) == 3
    assert len({p["grupo_entrega"] for p in pedidos}) == 1 and pedidos[0]["grupo_entrega"] is not None
    assert {p["paquete_nombre"] for p in pedidos} == {"Paquete de 10"}
    # un pedido suelto no lleva grupo
    sub = subproducto_por_color(client, admin_headers, "R")
    suelto = client.post("/pedidos", headers=tok, json={"subproducto_id": sub["id"], "cantidad_pedida": 1}).json()
    assert suelto["grupo_entrega"] is None


def test_un_paquete_sale_en_un_solo_albaran_cuando_esta_entero(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    _pedir(client, tok, _paquete(client, admin_headers))          # 10 tornillos + 10 tuercas + 10 arandelas
    _piezas(client, "R", 10)
    _piezas(client, "G", 10)
    assert _albaranes(client, admin_headers) == []                # dos componentes listos: aun NO sale nada
    _piezas(client, "B", 10)                                       # el ultimo componente
    (albaran,) = _albaranes(client, admin_headers)                 # UN albaran...
    assert sorted(l["cantidad"] for l in albaran["lineas"]) == [1, 10, 10, 10]   # ...la linea del paquete + sus 3 componentes
    assert albaran["paquetes"] == ["Paquete de 10"]
    pedidos = client.get("/pedidos", headers=admin_headers).json()
    assert {p["estado"] for p in pedidos} == {"completado"}


def test_mientras_el_paquete_esta_a_medias_sus_pedidos_esperan_como_listo(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    _pedir(client, tok, _paquete(client, admin_headers))
    _piezas(client, "R", 10)
    estados = {p["subproducto"]["nombre"]: p["estado"] for p in client.get("/pedidos", headers=admin_headers).json()}
    assert estados["Tornillo 10mm"] == "listo" and estados["Tuerca 10mm"] == "pendiente"


def test_si_el_almacen_ya_cubre_el_paquete_sale_en_un_albaran_al_pedirlo(client, admin_headers):
    _piezas(client, "R", 10)
    _piezas(client, "G", 10)
    _piezas(client, "B", 10)
    _c, tok = _cliente_con_todo(client, admin_headers)
    _pedir(client, tok, _paquete(client, admin_headers))
    (albaran,) = _albaranes(client, admin_headers)
    assert len(albaran["lineas"]) == 4       # el paquete + sus 3 componentes


def test_dos_paquetes_del_mismo_cliente_son_dos_albaranes(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    p = _paquete(client, admin_headers)
    _pedir(client, tok, p)
    _pedir(client, tok, p)
    _piezas(client, "R", 20)
    _piezas(client, "G", 20)
    _piezas(client, "B", 20)
    albaranes = _albaranes(client, admin_headers)
    assert len(albaranes) == 2 and all(len(a["lineas"]) == 4 for a in albaranes)


def test_la_cantidad_del_paquete_multiplica_pero_sigue_siendo_un_albaran(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    _pedir(client, tok, _paquete(client, admin_headers), cantidad=2)   # 20 de cada
    _piezas(client, "R", 20)
    _piezas(client, "G", 20)
    _piezas(client, "B", 20)
    (albaran,) = _albaranes(client, admin_headers)
    assert sorted(l["cantidad"] for l in albaran["lineas"]) == [2, 20, 20, 20]   # 2 paquetes + sus componentes


def test_un_pedido_suelto_sigue_saliendo_por_su_cuenta(client, admin_headers):
    _c, tok = _cliente_con_todo(client, admin_headers)
    sub = subproducto_por_color(client, admin_headers, "R")
    client.post("/pedidos", headers=tok, json={"subproducto_id": sub["id"], "cantidad_pedida": 2})
    _pedir(client, tok, _paquete(client, admin_headers))
    _piezas(client, "R", 12)     # 2 al suelto (mas antiguo) y 10 al paquete
    albaranes = _albaranes(client, admin_headers)
    assert len(albaranes) == 1 and albaranes[0]["paquetes"] == []   # solo salio el suelto; el paquete espera


class TestExpedicionManualYActivarla:
    def _listos(self, client, admin_headers):
        client.patch("/almacen/configuracion", headers=admin_headers, json={"expedicion_automatica": False})
        _c, tok = _cliente_con_todo(client, admin_headers)
        pedidos = _pedir(client, tok, _paquete(client, admin_headers))
        for color in "RGB":
            _piezas(client, color, 10)
        return pedidos

    def test_repartir_un_pedido_del_paquete_reparte_el_paquete_entero_en_un_albaran(self, client, admin_headers):
        pedidos = self._listos(client, admin_headers)
        r = client.post("/reparto/expedir", headers=admin_headers, json={"pedido_ids": [pedidos[0]["id"]]})
        (albaran,) = r.json()
        assert len(albaran["lineas"]) == 4
        assert {p["estado"] for p in client.get("/pedidos", headers=admin_headers).json()} == {"completado"}

    def test_activar_la_expedicion_automatica_saca_el_paquete_completo_en_uno(self, client, admin_headers):
        self._listos(client, admin_headers)
        client.patch("/almacen/configuracion", headers=admin_headers, json={"expedicion_automatica": True})
        (albaran,) = _albaranes(client, admin_headers)
        assert len(albaran["lineas"]) == 4

    def test_activar_la_expedicion_no_saca_un_paquete_a_medias(self, client, admin_headers):
        client.patch("/almacen/configuracion", headers=admin_headers, json={"expedicion_automatica": False})
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, _paquete(client, admin_headers))
        _piezas(client, "R", 10)
        client.patch("/almacen/configuracion", headers=admin_headers, json={"expedicion_automatica": True})
        assert _albaranes(client, admin_headers) == []
