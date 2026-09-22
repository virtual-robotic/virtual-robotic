# Version: 2026-09-20 11:05 -- tests: precio propio del paquete (linea de paquete + componentes sin precio)
"""Un paquete con precio propio se cobra a ese precio, no a la suma de sus componentes. En el
albaran y la factura sale UNA linea del paquete y debajo, sin precio, lo que lleva. Se entrega ENTERO."""
from .conftest import auth
from .test_paquete_un_albaran import _albaranes, _cliente_con_todo, _paquete, _pedir, _piezas


def _componentes(albaran):
    return [l for l in albaran["lineas"] if l["tipo"] == "componente"]


def _linea_paquete(albaran):
    (l,) = [l for l in albaran["lineas"] if l["tipo"] == "paquete"]
    return l


def _entero(client, colores="RGB", n=10):
    for c in colores:
        _piezas(client, c, n)


class TestPrecioPropio:
    def test_el_paquete_de_ejemplo_tiene_precio_y_el_pedido_lo_congela(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        assert paq["precio_centimos"] == 220 and paq["iva_porcentaje"] == 21
        _c, tok = _cliente_con_todo(client, admin_headers)
        pedidos = _pedir(client, tok, paq, cantidad=2)
        assert {p["paquete_precio_centimos"] for p in pedidos} == {220}
        assert {p["paquete_cantidad"] for p in pedidos} == {2}
        # los productos de un paquete con precio propio no llevan precio: va en el del paquete
        assert {p["precio_unitario_centimos"] for p in pedidos} == {0}
        assert {p["precio_origen"] for p in pedidos} == {"paquete"}
        # cambiar el precio despues no toca lo ya pedido
        client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"precio_centimos": 999})
        assert client.get(f"/pedidos/{pedidos[0]['id']}", headers=admin_headers).json()["paquete_precio_centimos"] == 220

    def test_el_albaran_lleva_la_linea_del_paquete_y_debajo_sus_componentes_sin_precio(self, client, admin_headers):
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, _paquete(client, admin_headers))
        _entero(client)
        (alb,) = _albaranes(client, admin_headers)
        linea = _linea_paquete(alb)
        assert (linea["cantidad"], linea["precio_unitario_centimos"], linea["descripcion"]) == (1, 220, "Paquete de 10 (P010)")
        assert linea["pedido_id"] is None and linea["subproducto_id"] is None
        comps = _componentes(alb)
        assert len(comps) == 3 and {c["precio_unitario_centimos"] for c in comps} == {0}
        assert {c["paquete_nombre"] for c in alb["lineas"]} == {"Paquete de 10"}
        # 2,20 + 21 % de IVA (0,462 -> 0,46) = 2,66; y NO sale una fila de IVA a 0 de los componentes
        assert (alb["base_centimos"], alb["iva_centimos"], alb["total_centimos"]) == (220, 46, 266)
        assert alb["desglose_iva"] == [{"iva_porcentaje": 21, "base_centimos": 220, "iva_centimos": 46}]
        assert alb["paquetes"] == ["Paquete de 10"]

    def test_dos_paquetes_se_cobran_dos_veces(self, client, admin_headers):
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, _paquete(client, admin_headers), cantidad=2)
        _entero(client, n=20)
        (alb,) = _albaranes(client, admin_headers)
        assert (_linea_paquete(alb)["cantidad"], alb["base_centimos"]) == (2, 440)

    def test_el_iva_del_paquete_manda_y_los_componentes_lo_siguen(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"iva_porcentaje": 10})
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, paq)
        _entero(client)
        (alb,) = _albaranes(client, admin_headers)
        assert {l["iva_porcentaje"] for l in alb["lineas"]} == {10}
        assert alb["desglose_iva"] == [{"iva_porcentaje": 10, "base_centimos": 220, "iva_centimos": 22}]


class TestTarifaDeClienteParaPaquetes:
    def test_un_cliente_puede_tener_otro_precio_de_paquete(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        a, tok_a = _cliente_con_todo(client, admin_headers)
        _b, tok_b = _cliente_con_todo(client, admin_headers)
        r = client.put(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=admin_headers, json={"precio_centimos": 150})
        assert r.status_code == 200, r.text
        pedidos_a = _pedir(client, tok_a, paq)
        pedidos_b = _pedir(client, tok_b, paq)
        assert ({p["paquete_precio_centimos"] for p in pedidos_a}, {p["precio_origen"] for p in pedidos_a}) == ({150}, {"paquete"})
        assert {p["paquete_precio_centimos"] for p in pedidos_b} == {220}

    def test_quitar_la_tarifa_vuelve_al_precio_general_y_queda_en_el_historial(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        a, tok_a = _cliente_con_todo(client, admin_headers)
        client.put(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=admin_headers, json={"precio_centimos": 150})
        assert client.delete(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=admin_headers).status_code == 200
        assert client.delete(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=admin_headers).status_code == 404
        assert {p["paquete_precio_centimos"] for p in _pedir(client, tok_a, paq)} == {220}
        historial = client.get("/historial_precios", headers=admin_headers, params={"cliente_id": a["id"]}).json()
        assert [(h["tipo"], h["precio_anterior_centimos"], h["precio_nuevo_centimos"]) for h in historial] == [
            ("paquete_cliente", 150, None), ("paquete_cliente", None, 150)]
        assert all(h["paquete_id"] == paq["id"] and h["subproducto_id"] is None for h in historial)
        assert historial[0]["subproducto_descripcion"] == "Paquete: Paquete de 10 (P010)"

    def test_permisos(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        a, tok_a = _cliente_con_todo(client, admin_headers)
        assert client.put(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=tok_a, json={"precio_centimos": 1}).status_code == 403
        client.put(f"/clientes/{a['id']}/tarifas_paquete/{paq['id']}", headers=admin_headers, json={"precio_centimos": 150})
        b, _ = _cliente_con_todo(client, admin_headers)
        assert client.get(f"/clientes/{b['id']}/tarifas_paquete", headers=auth(_admin_de(client, admin_headers, a))).status_code == 403


def _admin_de(client, admin_headers, cliente):
    """Token del admin_cliente que crea crear_cliente_con_usuario (username = 'paq<n>')."""
    from .conftest import login
    usuarios = client.get("/usuarios", headers=admin_headers).json()
    admin = next(u for u in usuarios if u["cliente_id"] == cliente["id"] and u["rol"] == "admin_cliente")
    return login(client, admin["username"])


class TestHistorialYPrecioGeneral:
    def test_cambiar_el_precio_del_paquete_deja_rastro(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"precio_centimos": 300})
        (h,) = client.get("/historial_precios", headers=admin_headers).json()
        assert (h["tipo"], h["precio_anterior_centimos"], h["precio_nuevo_centimos"]) == ("paquete_general", 220, 300)

    def test_precio_negativo_se_rechaza_y_guardar_sin_cambiar_no_ensucia(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        assert client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"precio_centimos": -1}).status_code == 400
        client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"nombre": "Otro", "precio_centimos": 220})
        assert client.get("/historial_precios", headers=admin_headers).json() == []

    def test_crear_un_paquete_con_precio(self, client, admin_headers):
        from .conftest import subproducto_por_color
        sub = subproducto_por_color(client, admin_headers, "R")
        r = client.post("/paquetes", headers=admin_headers, json={
            "nombre": "Kit", "codigo": "KIT1", "precio_centimos": 90, "iva_porcentaje": 10,
            "componentes": [{"subproducto_id": sub["id"], "cantidad": 3}]})
        assert r.status_code == 200, r.text
        assert (r.json()["precio_centimos"], r.json()["iva_porcentaje"]) == (90, 10)


class TestSinPrecioPropio:
    """precio_centimos = null: se cobra la suma de los componentes, cada uno a su tarifa."""

    def _sin_precio(self, client, admin_headers):
        paq = _paquete(client, admin_headers)
        r = client.patch(f"/paquetes/{paq['id']}", headers=admin_headers, json={"precio_centimos": None})
        assert r.status_code == 200 and r.json()["precio_centimos"] is None
        return paq

    def test_se_cobra_la_suma_pero_se_ve_agrupado_bajo_el_paquete(self, client, admin_headers):
        paq = self._sin_precio(client, admin_headers)
        _c, tok = _cliente_con_todo(client, admin_headers)
        pedidos = _pedir(client, tok, paq)
        assert {p["paquete_precio_centimos"] for p in pedidos} is not None and None in {p["paquete_precio_centimos"] for p in pedidos}
        assert sorted(p["precio_unitario_centimos"] for p in pedidos) == [5, 8, 12]
        _entero(client)
        (alb,) = _albaranes(client, admin_headers)
        assert [l["tipo"] for l in alb["lineas"]] == ["normal"] * 3            # no hay linea de paquete
        assert {l["paquete_nombre"] for l in alb["lineas"]} == {"Paquete de 10"}
        assert alb["base_centimos"] == 10 * (12 + 8 + 5)

    def test_quitar_el_precio_queda_en_el_historial(self, client, admin_headers):
        self._sin_precio(client, admin_headers)
        (h,) = client.get("/historial_precios", headers=admin_headers).json()
        assert (h["precio_anterior_centimos"], h["precio_nuevo_centimos"]) == (220, None)


class TestUnPaqueteSeEntregaEntero:
    def _manual(self, client, admin_headers):
        client.patch("/almacen/configuracion", headers=admin_headers, json={"expedicion_automatica": False})

    def test_a_mano_no_se_entrega_un_paquete_a_medias(self, client, admin_headers):
        self._manual(client, admin_headers)
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, _paquete(client, admin_headers))
        _piezas(client, "R", 10)
        _piezas(client, "G", 10)               # faltan las arandelas
        assert client.post("/reparto/expedir", headers=admin_headers, json={}).json() == []
        assert _albaranes(client, admin_headers) == []
        _piezas(client, "B", 10)
        (alb,) = client.post("/reparto/expedir", headers=admin_headers, json={}).json()
        assert len(alb["lineas"]) == 4

    def test_en_una_cesta_los_sueltos_salen_a_medias_pero_el_paquete_espera(self, client, admin_headers):
        from .conftest import subproducto_por_color
        self._manual(client, admin_headers)
        _c, tok = _cliente_con_todo(client, admin_headers)
        sub = subproducto_por_color(client, admin_headers, "R")
        pedidos = client.post("/pedidos/multiple", headers=tok, json={
            "lineas": [{"subproducto_id": sub["id"], "cantidad_pedida": 2}],
            "paquetes": [{"paquete_id": _paquete(client, admin_headers)["id"], "cantidad": 1}]}).json()
        _piezas(client, "R", 2)                # el suelto (mas antiguo) queda listo; el paquete no
        suelto = next(p for p in pedidos if p["paquete_nombre"] is None)
        (alb,) = client.post("/reparto/expedir", headers=admin_headers, json={"pedido_ids": [suelto["id"]]}).json()
        assert [l["tipo"] for l in alb["lineas"]] == ["normal"] and alb["paquetes"] == []


class TestCorreccionesDePrecioDePaquete:
    def test_el_precio_de_un_pedido_de_paquete_se_corrige_antes_de_entregar(self, client, admin_headers):
        _c, tok = _cliente_con_todo(client, admin_headers)
        pedidos = _pedir(client, tok, _paquete(client, admin_headers))
        pp = pedidos[0]["paquete_pedido_id"]
        assert client.patch(f"/pedidos-paquete/{pp}/precio", headers=admin_headers,
                            json={"precio_centimos": 180, "motivo": " "}).status_code == 400
        r = client.patch(f"/pedidos-paquete/{pp}/precio", headers=admin_headers,
                         json={"precio_centimos": 180, "motivo": "oferta"})
        assert r.status_code == 200, r.text
        _entero(client)
        (alb,) = _albaranes(client, admin_headers)
        assert _linea_paquete(alb)["precio_unitario_centimos"] == 180
        h = client.get("/historial_precios", headers=admin_headers).json()[0]
        assert (h["tipo"], h["precio_anterior_centimos"], h["precio_nuevo_centimos"], h["motivo"]) == ("pedido_paquete", 220, 180, "oferta")
        # ya entregado: 409
        assert client.patch(f"/pedidos-paquete/{pp}/precio", headers=admin_headers,
                            json={"precio_centimos": 1, "motivo": "x"}).status_code == 409

    def test_un_componente_de_paquete_con_precio_no_se_corrige_por_su_cuenta(self, client, admin_headers):
        _c, tok = _cliente_con_todo(client, admin_headers)
        pedidos = _pedir(client, tok, _paquete(client, admin_headers))
        r = client.patch(f"/pedidos/{pedidos[0]['id']}/precio", headers=admin_headers, json={"precio_centimos": 5, "motivo": "x"})
        assert r.status_code == 409 and "paquete" in r.json()["detail"]

    def test_en_el_albaran_se_corrige_la_linea_del_paquete_no_la_de_sus_componentes(self, client, admin_headers):
        _c, tok = _cliente_con_todo(client, admin_headers)
        _pedir(client, tok, _paquete(client, admin_headers))
        _entero(client)
        (alb,) = _albaranes(client, admin_headers)
        comp = _componentes(alb)[0]
        assert client.patch(f"/repartos/lineas/{comp['id']}/precio", headers=admin_headers,
                            json={"precio_centimos": 5, "motivo": "x"}).status_code == 400
        r = client.patch(f"/repartos/lineas/{_linea_paquete(alb)['id']}/precio", headers=admin_headers,
                         json={"precio_centimos": 300, "motivo": "error de precio"})
        assert r.status_code == 200, r.text
        despues = client.get(f"/repartos/{alb['id']}", headers=admin_headers).json()
        assert despues["base_centimos"] == 300
        h = client.get("/historial_precios", headers=admin_headers).json()[0]
        assert (h["tipo"], h["paquete_id"]) == ("albaran", _paquete(client, admin_headers)["id"])


class TestFacturaConPaquete:
    def _factura(self, client, admin_headers, cantidad=1):
        _c, tok = _cliente_con_todo(client, admin_headers)
        cliente_id = _c["id"]
        client.patch(f"/clientes/{cliente_id}", headers=admin_headers,
                     json={"cif": "B12345678", "direccion": "Calle Mayor 1"})
        _pedir(client, tok, _paquete(client, admin_headers), cantidad=cantidad)
        _entero(client, n=10 * cantidad)
        r = client.post("/facturas", headers=admin_headers, json={"cliente_id": cliente_id})
        assert r.status_code == 200, r.text
        return r.json()

    def test_la_factura_lleva_el_paquete_con_su_precio_y_los_componentes_sin_precio(self, client, admin_headers):
        f = self._factura(client, admin_headers)
        assert [l["tipo"] for l in f["lineas"]] == ["paquete", "componente", "componente", "componente"]
        assert (f["base_centimos"], f["iva_centimos"], f["total_centimos"]) == (220, 46, 266)
        assert all(l["paquete_nombre"] == "Paquete de 10" for l in f["lineas"])

    def test_los_componentes_a_cero_no_bloquean_la_factura_de_lineas_sin_precio(self, client, admin_headers):
        # el paquete tiene precio: los componentes a 0 EUR son lo normal y no deben rechazarse
        assert self._factura(client, admin_headers)["numero"].startswith("FAC-")

    def test_la_rectificativa_es_exactamente_el_negativo_tambien_en_el_paquete(self, client, admin_headers):
        f = self._factura(client, admin_headers, cantidad=2)
        rect = client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "x"}).json()
        assert (rect["base_centimos"], rect["iva_centimos"], rect["total_centimos"]) == (-440, -92, -532)
        assert [l["tipo"] for l in rect["lineas"]] == ["paquete", "componente", "componente", "componente"]
        assert rect["lineas"][0]["cantidad"] == -2 and rect["lineas"][0]["paquete_cantidad"] == -2
