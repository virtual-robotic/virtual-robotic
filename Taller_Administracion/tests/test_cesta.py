# Version: 2026-09-19 19:27 -- tests: pedido de varias lineas (cesta) = un albaran
"""POST /pedidos/multiple: varias lineas de una vez. Un pedido por linea, todos del mismo grupo de
entrega; salen juntos en UN albaran cuando estan todos listos."""
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


def _cliente(client, admin_headers, colores="RGB"):
    global _n
    _n += 1
    cliente, tok_admin = crear_cliente_con_usuario(client, admin_headers, f"Empresa cesta{_n}", f"cesta{_n}")
    for color in colores:
        asignar_producto(client, admin_headers, cliente["id"], producto_por_color(client, admin_headers, color)["id"])
    crear_usuario_normal(client, admin_headers, cliente["id"], f"op_cesta{_n}")
    return cliente, auth(login(client, f"op_cesta{_n}")), auth(tok_admin)


def _lineas(client, admin_headers, **cantidades):
    return [{"subproducto_id": subproducto_por_color(client, admin_headers, c)["id"], "cantidad_pedida": n}
            for c, n in cantidades.items()]


def _piezas(client, color, n):
    for _ in range(n):
        client.post("/taller/cubo_clasificado", json={"color": color, "subproducto_id": sub_id(color)})


def _albaranes(client, admin_headers):
    return client.get("/repartos", headers=admin_headers).json()


def test_una_cesta_crea_un_pedido_por_linea_del_mismo_grupo(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    r = client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=3, G=2, B=1)})
    assert r.status_code == 200, r.text
    pedidos = r.json()
    assert sorted(p["cantidad_pedida"] for p in pedidos) == [1, 2, 3]
    assert len({p["grupo_entrega"] for p in pedidos}) == 1 and pedidos[0]["grupo_entrega"] is not None
    assert all(p["paquete_nombre"] is None for p in pedidos)


def test_una_cesta_sale_en_un_solo_albaran_cuando_esta_entera(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=2, G=2, B=2, )})
    _piezas(client, "R", 2)
    _piezas(client, "G", 2)
    assert _albaranes(client, admin_headers) == []          # falta una linea: no sale nada
    _piezas(client, "B", 2)
    (albaran,) = _albaranes(client, admin_headers)           # UN albaran con las tres lineas
    assert sorted(l["cantidad"] for l in albaran["lineas"]) == [2, 2, 2]
    assert albaran["paquetes"] == []                          # no es un paquete
    assert {p["estado"] for p in client.get("/pedidos", headers=admin_headers).json()} == {"completado"}


def test_si_el_almacen_ya_cubre_toda_la_cesta_sale_un_albaran_al_pedirla(client, admin_headers):
    _piezas(client, "R", 2)
    _piezas(client, "G", 2)
    _c, tok, _ta = _cliente(client, admin_headers)
    client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=2, G=2)})
    (albaran,) = _albaranes(client, admin_headers)
    assert len(albaran["lineas"]) == 2


def test_una_sola_linea_es_un_pedido_normal_sin_grupo(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    (pedido,) = client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=4)}).json()
    assert pedido["grupo_entrega"] is None


def test_dos_lineas_del_mismo_subproducto_se_suman(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    sub = subproducto_por_color(client, admin_headers, "R")["id"]
    lineas = [{"subproducto_id": sub, "cantidad_pedida": 3}, {"subproducto_id": sub, "cantidad_pedida": 4}]
    (pedido,) = client.post("/pedidos/multiple", headers=tok, json={"lineas": lineas}).json()
    assert pedido["cantidad_pedida"] == 7


def test_dos_cestas_del_mismo_cliente_son_dos_albaranes(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    for _ in range(2):
        client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=1, G=1)})
    _piezas(client, "R", 2)
    _piezas(client, "G", 2)
    assert len(_albaranes(client, admin_headers)) == 2


def test_pedidos_sueltos_seguidos_siguen_siendo_albaranes_distintos(client, admin_headers):
    """Cuatro clics en Pedir NO son una cesta: cada uno sale por su cuenta."""
    _c, tok, _ta = _cliente(client, admin_headers)
    for c in "RGB":
        sub = subproducto_por_color(client, admin_headers, c)["id"]
        client.post("/pedidos", headers=tok, json={"subproducto_id": sub, "cantidad_pedida": 1})
    for c in "RGB":
        _piezas(client, c, 1)
    assert len(_albaranes(client, admin_headers)) == 3


def test_es_todo_o_nada_una_linea_mala_no_crea_ninguna(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers, colores="R")      # solo tiene asignado el rojo
    antes = len(client.get("/pedidos", headers=admin_headers).json())
    malas = _lineas(client, admin_headers, R=1, G=1)                   # la verde no la tiene asignada
    assert client.post("/pedidos/multiple", headers=tok, json={"lineas": malas}).status_code == 403
    assert client.post("/pedidos/multiple", headers=tok, json={"lineas": [
        {"subproducto_id": malas[0]["subproducto_id"], "cantidad_pedida": 1},
        {"subproducto_id": 99999, "cantidad_pedida": 1}]}).status_code == 400
    assert len(client.get("/pedidos", headers=admin_headers).json()) == antes


def test_validaciones_basicas(client, admin_headers):
    _c, tok, _ta = _cliente(client, admin_headers)
    assert client.post("/pedidos/multiple", headers=tok, json={"lineas": []}).status_code == 400
    assert client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=0)}).status_code == 400
    assert client.post("/pedidos/multiple", headers=tok, json={"lineas": _lineas(client, admin_headers, R=-2)}).status_code == 400


def test_solo_piden_el_admin_de_cliente_y_el_usuario_normal(client, admin_headers):
    _c, tok, tok_admin_cliente = _cliente(client, admin_headers)
    lineas = _lineas(client, admin_headers, R=1, G=1)
    assert client.post("/pedidos/multiple", headers=tok_admin_cliente, json={"lineas": lineas}).status_code == 200
    assert client.post("/pedidos/multiple", headers=admin_headers, json={"lineas": lineas}).status_code == 403


class TestCestaConPaquetes:
    def _paquete(self, client, admin_headers):
        return next(p for p in client.get("/paquetes", headers=admin_headers).json() if p["codigo"] == "P010")

    def test_productos_y_un_paquete_juntos_salen_en_un_solo_albaran(self, client, admin_headers):
        _c, tok, _ta = _cliente(client, admin_headers)
        paq = self._paquete(client, admin_headers)
        # 2 tornillos sueltos + 1 paquete (10 tornillos, 10 tuercas, 10 arandelas)
        r = client.post("/pedidos/multiple", headers=tok, json={
            "lineas": _lineas(client, admin_headers, R=2), "paquetes": [{"paquete_id": paq["id"], "cantidad": 1}]})
        assert r.status_code == 200, r.text
        pedidos = r.json()
        assert len(pedidos) == 4     # 1 suelto + 3 componentes del paquete (los tornillos NO se mezclan)
        assert len({p["grupo_entrega"] for p in pedidos}) == 1
        assert sorted(p["paquete_nombre"] or "-" for p in pedidos) == ["-", "Paquete de 10", "Paquete de 10", "Paquete de 10"]
        _piezas(client, "R", 12)
        _piezas(client, "G", 10)
        assert _albaranes(client, admin_headers) == []
        _piezas(client, "B", 10)
        (albaran,) = _albaranes(client, admin_headers)
        assert len(albaran["lineas"]) == 5 and albaran["paquetes"] == ["Paquete de 10"]   # suelto + paquete + 3 componentes

    def test_solo_paquetes_en_la_cesta_tambien_es_un_albaran(self, client, admin_headers):
        _c, tok, _ta = _cliente(client, admin_headers)
        paq = self._paquete(client, admin_headers)
        client.post("/pedidos/multiple", headers=tok, json={"paquetes": [{"paquete_id": paq["id"], "cantidad": 2}]})
        for color in "RGB":
            _piezas(client, color, 20)
        (albaran,) = _albaranes(client, admin_headers)
        assert sorted(l["cantidad"] for l in albaran["lineas"]) == [2, 20, 20, 20]

    def test_dos_paquetes_iguales_en_la_cesta_se_suman(self, client, admin_headers):
        _c, tok, _ta = _cliente(client, admin_headers)
        paq = self._paquete(client, admin_headers)
        pedidos = client.post("/pedidos/multiple", headers=tok, json={
            "paquetes": [{"paquete_id": paq["id"], "cantidad": 1}, {"paquete_id": paq["id"], "cantidad": 2}]}).json()
        assert sorted(p["cantidad_pedida"] for p in pedidos) == [30, 30, 30]

    def test_un_paquete_con_un_producto_no_asignado_no_crea_nada(self, client, admin_headers):
        _c, tok, _ta = _cliente(client, admin_headers, colores="R")     # el paquete lleva tuercas y arandelas
        paq = self._paquete(client, admin_headers)
        antes = len(client.get("/pedidos", headers=admin_headers).json())
        r = client.post("/pedidos/multiple", headers=tok, json={
            "lineas": _lineas(client, admin_headers, R=1), "paquetes": [{"paquete_id": paq["id"], "cantidad": 1}]})
        assert r.status_code == 403
        assert len(client.get("/pedidos", headers=admin_headers).json()) == antes

    def test_paquete_inexistente_o_cantidad_cero(self, client, admin_headers):
        _c, tok, _ta = _cliente(client, admin_headers)
        assert client.post("/pedidos/multiple", headers=tok, json={"paquetes": [{"paquete_id": 9999, "cantidad": 1}]}).status_code == 400
        paq = self._paquete(client, admin_headers)
        assert client.post("/pedidos/multiple", headers=tok, json={"paquetes": [{"paquete_id": paq["id"], "cantidad": 0}]}).status_code == 400
