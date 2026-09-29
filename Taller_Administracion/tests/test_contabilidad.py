# Version: 2026-09-19 11:24 -- tests de tarifas, historial de precios, correcciones y facturas
"""Control de precios de origen a factura (ver contabilidad.py): tarifa general y
por cliente, precio congelado en el pedido, historial, correccion antes de
facturar, factura con datos fiscales copiados y rectificativa que libera albaranes."""
import datetime

from .conftest import (
    sub_id,
    asignar_producto,
    auth,
    crear_cliente_con_usuario,
    producto_por_color,
    subproducto_por_color,
)
from .test_almacen import _preparar_pedido

ANIO = datetime.datetime.utcnow().year


def _pieza(client, color="R"):
    r = client.post("/taller/cubo_clasificado", json={"color": color, "subproducto_id": sub_id(color)})
    assert r.status_code == 200, r.text
    return r.json()


def _fiscal(client, admin_headers, cliente_id, **extra):
    datos = {"cif": "B12345678", "direccion": "Calle Mayor 1", "codigo_postal": "48001",
             "poblacion": "Bilbao", "provincia": "Bizkaia", **extra}
    r = client.patch(f"/clientes/{cliente_id}", headers=admin_headers, json=datos)
    assert r.status_code == 200, r.text


def _albaran(client, admin_headers, color="R", cantidad=2, fiscal=True):
    """Pedido de un cliente nuevo, fabricado y repartido: devuelve (ctx, albaran)."""
    ctx = _preparar_pedido(client, admin_headers, color=color, cantidad=cantidad)
    if fiscal:
        _fiscal(client, admin_headers, ctx["pedido"]["cliente_id"])
    for _ in range(cantidad):
        _pieza(client, color)
    repartos = client.get("/repartos", headers=admin_headers).json()
    albaran = next(r for r in repartos if r["cliente_id"] == ctx["pedido"]["cliente_id"])
    return ctx, albaran


def _facturar(client, admin_headers, cliente_id, **kw):
    return client.post("/facturas", headers=admin_headers, json={"cliente_id": cliente_id, **kw})


class TestTarifas:
    def test_tarifa_de_cliente_se_aplica_a_sus_pedidos_nuevos_y_no_a_los_de_otros(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")  # 12 cts de tarifa general
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        antes = a["pedido"]
        assert (antes["precio_unitario_centimos"], antes["precio_origen"]) == (12, "tarifa_general")

        r = client.put(f"/clientes/{a['pedido']['cliente_id']}/tarifas/{sub['id']}",
                       headers=admin_headers, json={"precio_centimos": 9})
        assert r.status_code == 200, r.text
        nuevo = client.post("/pedidos", headers=auth(a["tok_normal"]),
                            json={"subproducto_id": sub["id"], "cantidad_pedida": 1}).json()
        assert (nuevo["precio_unitario_centimos"], nuevo["precio_origen"]) == (9, "tarifa_cliente")
        # el pedido anterior conserva SU precio
        viejo = client.get(f"/pedidos/{antes['id']}", headers=admin_headers).json()
        assert viejo["precio_unitario_centimos"] == 12
        # otro cliente sigue con la general
        b = _preparar_pedido(client, admin_headers, cantidad=1)
        assert (b["pedido"]["precio_unitario_centimos"], b["pedido"]["precio_origen"]) == (12, "tarifa_general")

    def test_quitar_tarifa_vuelve_a_la_general(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        cid = a["pedido"]["cliente_id"]
        client.put(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers, json={"precio_centimos": 5})
        assert client.delete(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers).status_code == 200
        nuevo = client.post("/pedidos", headers=auth(a["tok_normal"]),
                            json={"subproducto_id": sub["id"], "cantidad_pedida": 1}).json()
        assert (nuevo["precio_unitario_centimos"], nuevo["precio_origen"]) == (12, "tarifa_general")
        assert client.delete(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers).status_code == 404

    def test_tarifa_negativa_se_rechaza(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        r = client.put(f"/clientes/{a['pedido']['cliente_id']}/tarifas/{sub['id']}",
                       headers=admin_headers, json={"precio_centimos": -1})
        assert r.status_code == 400

    def test_solo_admin_sistema_fija_tarifas_y_el_cliente_ve_solo_las_suyas(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        b = _preparar_pedido(client, admin_headers, cantidad=1)
        cid_a, cid_b = a["pedido"]["cliente_id"], b["pedido"]["cliente_id"]
        assert client.put(f"/clientes/{cid_a}/tarifas/{sub['id']}", headers=auth(a["tok_admin_cliente"]),
                          json={"precio_centimos": 1}).status_code == 403
        client.put(f"/clientes/{cid_a}/tarifas/{sub['id']}", headers=admin_headers, json={"precio_centimos": 7})
        assert len(client.get(f"/clientes/{cid_a}/tarifas", headers=auth(a["tok_admin_cliente"])).json()) == 1
        assert client.get(f"/clientes/{cid_b}/tarifas", headers=auth(a["tok_admin_cliente"])).status_code == 403


class TestHistorialDePrecios:
    def test_cambiar_la_tarifa_general_deja_anterior_nuevo_y_autor(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        client.patch(f"/subproductos/{sub['id']}", headers=admin_headers, json={"precio_centimos": 20})
        (fila,) = client.get("/historial_precios", headers=admin_headers,
                             params={"subproducto_id": sub["id"]}).json()
        assert (fila["tipo"], fila["precio_anterior_centimos"], fila["precio_nuevo_centimos"]) == ("tarifa_general", 12, 20)
        assert fila["usuario_id"] is not None
        assert "Tornillo" in fila["subproducto_descripcion"]

    def test_guardar_sin_cambiar_el_precio_no_ensucia_el_historial(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        client.patch(f"/subproductos/{sub['id']}", headers=admin_headers,
                     json={"nombre": "Otro nombre", "precio_centimos": 12})
        assert client.get("/historial_precios", headers=admin_headers).json() == []

    def test_tarifa_de_cliente_y_su_baja_quedan_registradas(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        cid = a["pedido"]["cliente_id"]
        client.put(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers, json={"precio_centimos": 9})
        client.put(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers, json={"precio_centimos": 8})
        client.delete(f"/clientes/{cid}/tarifas/{sub['id']}", headers=admin_headers)
        filas = client.get("/historial_precios", headers=admin_headers, params={"cliente_id": cid}).json()
        # mas reciente primero: la baja (8 -> nada), el cambio (9 -> 8) y el alta (nada -> 9)
        assert [(f["precio_anterior_centimos"], f["precio_nuevo_centimos"]) for f in filas] == [
            (8, None), (9, 8), (None, 9)]
        assert all(f["cliente_razon_social"] for f in filas)

    def test_solo_admin_sistema_ve_el_historial(self, client, admin_headers):
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        assert client.get("/historial_precios", headers=auth(a["tok_admin_cliente"])).status_code == 403


class TestCorregirPrecios:
    def test_corregir_precio_de_pedido_pendiente_queda_manual_y_con_motivo(self, client, admin_headers):
        a = _preparar_pedido(client, admin_headers, cantidad=3)
        pid = a["pedido"]["id"]
        r = client.patch(f"/pedidos/{pid}/precio", headers=admin_headers,
                         json={"precio_centimos": 30, "motivo": "acuerdo con el cliente"})
        assert r.status_code == 200, r.text
        p = client.get(f"/pedidos/{pid}", headers=admin_headers).json()
        assert (p["precio_unitario_centimos"], p["precio_origen"]) == (30, "manual")
        fila = client.get("/historial_precios", headers=admin_headers).json()[0]
        assert (fila["tipo"], fila["pedido_id"], fila["motivo"]) == ("pedido", pid, "acuerdo con el cliente")
        assert (fila["precio_anterior_centimos"], fila["precio_nuevo_centimos"]) == (12, 30)

    def test_el_motivo_es_obligatorio(self, client, admin_headers):
        a = _preparar_pedido(client, admin_headers, cantidad=1)
        r = client.patch(f"/pedidos/{a['pedido']['id']}/precio", headers=admin_headers,
                         json={"precio_centimos": 30, "motivo": "  "})
        assert r.status_code == 400

    def test_no_se_corrige_un_pedido_ya_entregado(self, client, admin_headers):
        ctx, _alb = _albaran(client, admin_headers, cantidad=1)
        r = client.patch(f"/pedidos/{ctx['pedido']['id']}/precio", headers=admin_headers,
                         json={"precio_centimos": 30, "motivo": "x"})
        assert r.status_code == 409

    def test_corregir_una_linea_de_albaran_no_facturada_cambia_sus_importes(self, client, admin_headers):
        _ctx, alb = _albaran(client, admin_headers, cantidad=2)
        linea = alb["lineas"][0]
        r = client.patch(f"/repartos/lineas/{linea['id']}/precio", headers=admin_headers,
                         json={"precio_centimos": 50, "motivo": "precio mal puesto"})
        assert r.status_code == 200, r.text
        despues = client.get(f"/repartos/{alb['id']}", headers=admin_headers).json()
        assert despues["base_centimos"] == 100  # 2 x 50
        assert despues["lineas"][0]["cantidad"] == 2  # la cantidad nunca se toca
        fila = client.get("/historial_precios", headers=admin_headers).json()[0]
        assert (fila["tipo"], fila["reparto_linea_id"]) == ("albaran", linea["id"])

    def test_una_linea_ya_facturada_no_se_corrige(self, client, admin_headers):
        ctx, alb = _albaran(client, admin_headers, cantidad=1)
        assert _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).status_code == 200
        r = client.patch(f"/repartos/lineas/{alb['lineas'][0]['id']}/precio", headers=admin_headers,
                         json={"precio_centimos": 50, "motivo": "x"})
        assert r.status_code == 409

    def test_solo_admin_sistema_corrige(self, client, admin_headers):
        ctx, alb = _albaran(client, admin_headers, cantidad=1)
        t = auth(ctx["tok_admin_cliente"])
        assert client.patch(f"/pedidos/{ctx['pedido']['id']}/precio", headers=t,
                            json={"precio_centimos": 1, "motivo": "x"}).status_code == 403
        assert client.patch(f"/repartos/lineas/{alb['lineas'][0]['id']}/precio", headers=t,
                            json={"precio_centimos": 1, "motivo": "x"}).status_code == 403


class TestFacturar:
    def test_factura_con_lineas_datos_fiscales_e_importes(self, client, admin_headers):
        ctx, alb = _albaran(client, admin_headers, cantidad=5)  # 5 x 12 = 60, IVA 21% = 12,6 -> 13
        r = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"])
        assert r.status_code == 200, r.text
        f = r.json()
        assert f["numero"] == f"FAC-{ANIO}-000001"
        assert (f["tipo"], f["estado"], f["cobrada"]) == ("factura", "emitida", False)
        assert f["albaranes"] == [alb["numero"]]
        assert (f["base_centimos"], f["iva_centimos"], f["total_centimos"]) == (60, 13, 73)
        assert f["desglose_iva"] == [{"iva_porcentaje": 21, "base_centimos": 60, "iva_centimos": 13}]
        assert (f["cliente_cif"], f["cliente_direccion"]) == ("B12345678", "Calle Mayor 1, 48001 Bilbao (Bizkaia)")
        # el albarán ya sabe en que factura esta
        assert client.get(f"/repartos/{alb['id']}", headers=admin_headers).json()["factura_numero"] == f["numero"]

    def test_faltan_datos_fiscales_no_se_factura(self, client, admin_headers):
        ctx, _alb = _albaran(client, admin_headers, cantidad=1, fiscal=False)
        r = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"])
        assert r.status_code == 400
        assert "CIF" in r.json()["detail"] and "direccion" in r.json()["detail"]

    def test_no_se_factura_dos_veces_el_mismo_albaran(self, client, admin_headers):
        ctx, alb = _albaran(client, admin_headers, cantidad=1)
        cid = ctx["pedido"]["cliente_id"]
        f = _facturar(client, admin_headers, cid).json()
        # pedir el mismo albaran a mano -> 409 con el numero de la factura
        r = _facturar(client, admin_headers, cid, reparto_ids=[alb["id"]])
        assert r.status_code == 409 and f["numero"] in r.json()["detail"]
        # y "todo lo pendiente" ya no encuentra nada
        assert _facturar(client, admin_headers, cid).status_code == 400

    def test_albaran_de_otro_cliente_da_404(self, client, admin_headers):
        _ctx_a, alb_a = _albaran(client, admin_headers, color="R", cantidad=1)
        ctx_b, _alb_b = _albaran(client, admin_headers, color="G", cantidad=1)
        r = _facturar(client, admin_headers, ctx_b["pedido"]["cliente_id"], reparto_ids=[alb_a["id"]])
        assert r.status_code == 404

    def test_lineas_a_cero_se_rechazan_salvo_que_se_permitan(self, client, admin_headers):
        sub = subproducto_por_color(client, admin_headers, "R")
        client.patch(f"/subproductos/{sub['id']}", headers=admin_headers, json={"precio_centimos": 0})
        ctx, alb = _albaran(client, admin_headers, cantidad=1)
        cid = ctx["pedido"]["cliente_id"]
        r = _facturar(client, admin_headers, cid)
        assert r.status_code == 400 and alb["numero"] in r.json()["detail"]
        assert _facturar(client, admin_headers, cid, permitir_lineas_a_cero=True).status_code == 200

    def test_dos_tipos_de_iva_se_desglosan_por_tipo(self, client, admin_headers):
        r_sub = subproducto_por_color(client, admin_headers, "R")
        g_sub = subproducto_por_color(client, admin_headers, "G")
        client.patch(f"/subproductos/{g_sub['id']}", headers=admin_headers, json={"iva_porcentaje": 10})
        a = _preparar_pedido(client, admin_headers, color="R", cantidad=5)  # 5 x 12 = 60 al 21%
        asignar_producto(client, admin_headers, a["pedido"]["cliente_id"],
                         producto_por_color(client, admin_headers, "G")["id"])
        client.post("/pedidos", headers=auth(a["tok_normal"]),
                    json={"subproducto_id": g_sub["id"], "cantidad_pedida": 4})  # 4 x 8 = 32 al 10%
        _fiscal(client, admin_headers, a["pedido"]["cliente_id"])
        for _ in range(5):
            _pieza(client, "R")
        for _ in range(4):
            _pieza(client, "G")
        f = _facturar(client, admin_headers, a["pedido"]["cliente_id"]).json()
        assert f["desglose_iva"] == [
            {"iva_porcentaje": 10, "base_centimos": 32, "iva_centimos": 3},   # 3,2 -> 3
            {"iva_porcentaje": 21, "base_centimos": 60, "iva_centimos": 13},  # 12,6 -> 13
        ]
        assert (f["base_centimos"], f["iva_centimos"], f["total_centimos"]) == (92, 16, 108)

    def test_factura_y_albaran_cuadran_al_centimo(self, client, admin_headers):
        ctx, alb = _albaran(client, admin_headers, cantidad=5)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        assert f["total_centimos"] == alb["total_centimos"]

    def test_la_factura_conserva_los_datos_fiscales_aunque_se_edite_el_cliente(self, client, admin_headers):
        ctx, _alb = _albaran(client, admin_headers, cantidad=1)
        cid = ctx["pedido"]["cliente_id"]
        f = _facturar(client, admin_headers, cid).json()
        client.patch(f"/clientes/{cid}", headers=admin_headers,
                     json={"razon_social": "Nombre Nuevo SL", "direccion": "Otra calle 9"})
        despues = client.get(f"/facturas/{f['id']}", headers=admin_headers).json()
        assert despues["cliente_razon_social"] != "Nombre Nuevo SL"
        assert despues["cliente_direccion"].startswith("Calle Mayor 1")


class TestRectificativa:
    def _factura(self, client, admin_headers, cantidad=5):
        ctx, alb = _albaran(client, admin_headers, cantidad=cantidad)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        return ctx, alb, f

    def test_anular_emite_una_rectificativa_exactamente_negativa(self, client, admin_headers):
        _ctx, _alb, f = self._factura(client, admin_headers)
        r = client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "precio erroneo"})
        assert r.status_code == 200, r.text
        rect = r.json()
        assert rect["numero"] == f"RECT-{ANIO}-000001"
        assert (rect["tipo"], rect["rectifica_numero"], rect["motivo"]) == ("rectificativa", f["numero"], "precio erroneo")
        assert (rect["base_centimos"], rect["iva_centimos"], rect["total_centimos"]) == (-60, -13, -73)
        assert all(l["cantidad"] < 0 for l in rect["lineas"])
        original = client.get(f"/facturas/{f['id']}", headers=admin_headers).json()
        assert original["estado"] == "anulada" and original["rectificada_por_numero"] == rect["numero"]

    def test_al_anular_el_albaran_queda_libre_y_se_puede_refacturar_corregido(self, client, admin_headers):
        ctx, alb, f = self._factura(client, admin_headers, cantidad=2)
        client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "precio"})
        assert client.get(f"/repartos/{alb['id']}", headers=admin_headers).json()["factura_numero"] is None
        client.patch(f"/repartos/lineas/{alb['lineas'][0]['id']}/precio", headers=admin_headers,
                     json={"precio_centimos": 100, "motivo": "correcto"})
        nueva = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"])
        assert nueva.status_code == 200
        assert nueva.json()["numero"] == f"FAC-{ANIO}-000002"  # el numero no se reutiliza
        assert nueva.json()["base_centimos"] == 200

    def test_no_se_anula_dos_veces_ni_una_rectificativa_ni_sin_motivo(self, client, admin_headers):
        _ctx, _alb, f = self._factura(client, admin_headers, cantidad=1)
        assert client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": " "}).status_code == 400
        rect = client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "x"}).json()
        assert client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "x"}).status_code == 409
        assert client.post(f"/facturas/{rect['id']}/anular", headers=admin_headers, json={"motivo": "x"}).status_code == 409

    def test_series_de_numeracion_independientes(self, client, admin_headers):
        _c1, _a1, f1 = self._factura(client, admin_headers, cantidad=1)
        _c2, _a2, f2 = self._factura(client, admin_headers, cantidad=1)
        assert (f1["numero"], f2["numero"]) == (f"FAC-{ANIO}-000001", f"FAC-{ANIO}-000002")
        rect = client.post(f"/facturas/{f2['id']}/anular", headers=admin_headers, json={"motivo": "x"}).json()
        assert rect["numero"] == f"RECT-{ANIO}-000001"


class TestCobro:
    def test_marcar_cobrada_y_no_dos_veces(self, client, admin_headers):
        ctx, _alb = _albaran(client, admin_headers, cantidad=1)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        r = client.post(f"/facturas/{f['id']}/pagar", headers=admin_headers, json={"metodo_pago": "transferencia"})
        assert r.status_code == 200 and r.json()["cobrada"] is True
        assert r.json()["metodo_pago"] == "transferencia"
        assert client.post(f"/facturas/{f['id']}/pagar", headers=admin_headers, json={}).status_code == 409

    def test_no_se_cobra_una_factura_anulada(self, client, admin_headers):
        ctx, _alb = _albaran(client, admin_headers, cantidad=1)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "x"})
        assert client.post(f"/facturas/{f['id']}/pagar", headers=admin_headers, json={}).status_code == 409


class TestPermisosFacturas:
    def test_admin_cliente_ve_solo_sus_facturas_y_no_puede_operar(self, client, admin_headers):
        a, _alb_a = _albaran(client, admin_headers, color="R", cantidad=1)
        b, _alb_b = _albaran(client, admin_headers, color="G", cantidad=1)
        fa = _facturar(client, admin_headers, a["pedido"]["cliente_id"]).json()
        fb = _facturar(client, admin_headers, b["pedido"]["cliente_id"]).json()
        t = auth(a["tok_admin_cliente"])
        assert [f["id"] for f in client.get("/facturas", headers=t).json()] == [fa["id"]]
        assert client.get(f"/facturas/{fa['id']}", headers=t).status_code == 200
        assert client.get(f"/facturas/{fb['id']}", headers=t).status_code == 403
        assert client.post("/facturas", headers=t, json={"cliente_id": a["pedido"]["cliente_id"]}).status_code == 403
        assert client.post(f"/facturas/{fa['id']}/pagar", headers=t, json={}).status_code == 403
        assert client.post(f"/facturas/{fa['id']}/anular", headers=t, json={"motivo": "x"}).status_code == 403

    def test_usuario_normal_no_ve_facturas(self, client, admin_headers):
        a, _alb = _albaran(client, admin_headers, cantidad=1)
        assert client.get("/facturas", headers=auth(a["tok_normal"])).status_code == 403


def _emisor(client, admin_headers, **extra):
    datos = {"razon_social": "Segunda Empresa S.L.", "cif": "B22222222", "direccion": "Calle Otra 2, 48002 Bilbao",
             "serie_facturas": "SEG", "serie_rectificativas": "RSEG", **extra}
    r = client.post("/emisores", headers=admin_headers, json=datos)
    assert r.status_code == 200, r.text
    return r.json()


class TestEmisores:
    """Varias empresas que facturan, cada una con su numeracion (serie)."""

    def test_arranca_con_un_emisor_de_ejemplo_por_defecto(self, client, admin_headers):
        (e,) = client.get("/emisores", headers=admin_headers).json()
        assert (e["por_defecto"], e["activo"], e["serie_facturas"], e["serie_rectificativas"]) == (True, True, "FAC", "RECT")

    def test_cada_emisor_numera_por_su_cuenta(self, client, admin_headers):
        seg = _emisor(client, admin_headers)
        a, _ = _albaran(client, admin_headers, color="R", cantidad=1)
        b, _ = _albaran(client, admin_headers, color="G", cantidad=1)
        f1 = _facturar(client, admin_headers, a["pedido"]["cliente_id"]).json()                      # por defecto
        f2 = _facturar(client, admin_headers, b["pedido"]["cliente_id"], emisor_id=seg["id"]).json()  # la otra
        assert f1["numero"] == f"FAC-{ANIO}-000001" and f2["numero"] == f"SEG-{ANIO}-000001"
        assert (f2["emisor_id"], f2["emisor_cif"], f2["emisor_razon_social"]) == (seg["id"], "B22222222", "Segunda Empresa S.L.")
        # la rectificativa usa la serie de rectificativas de SU emisor
        rect = client.post(f"/facturas/{f2['id']}/anular", headers=admin_headers, json={"motivo": "x"}).json()
        assert rect["numero"] == f"RSEG-{ANIO}-000001" and rect["emisor_id"] == seg["id"]

    def test_el_emisor_por_defecto_es_el_que_se_usa_si_no_se_indica(self, client, admin_headers):
        seg = _emisor(client, admin_headers, por_defecto=True)
        ctx, _ = _albaran(client, admin_headers, cantidad=1)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        assert f["emisor_id"] == seg["id"] and f["numero"].startswith("SEG-")
        assert sum(e["por_defecto"] for e in client.get("/emisores", headers=admin_headers).json()) == 1

    def test_no_se_factura_con_un_emisor_desactivado_o_inexistente(self, client, admin_headers):
        seg = _emisor(client, admin_headers)
        client.patch(f"/emisores/{seg['id']}", headers=admin_headers, json={"activo": False})
        ctx, _ = _albaran(client, admin_headers, cantidad=1)
        cid = ctx["pedido"]["cliente_id"]
        assert _facturar(client, admin_headers, cid, emisor_id=seg["id"]).status_code == 400
        assert _facturar(client, admin_headers, cid, emisor_id=9999).status_code == 400

    def test_sin_ningun_emisor_por_defecto_no_se_factura(self, client, admin_headers):
        (e,) = client.get("/emisores", headers=admin_headers).json()
        client.patch(f"/emisores/{e['id']}", headers=admin_headers, json={"activo": False})
        ctx, _ = _albaran(client, admin_headers, cantidad=1)
        r = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"])
        assert r.status_code == 400 and "Empresas" in r.json()["detail"]

    def test_desactivar_el_emisor_por_defecto_pasa_el_por_defecto_a_otro_activo(self, client, admin_headers):
        seg = _emisor(client, admin_headers)
        (base,) = [e for e in client.get("/emisores", headers=admin_headers).json() if e["id"] != seg["id"]]
        client.patch(f"/emisores/{base['id']}", headers=admin_headers, json={"activo": False})
        por_id = {e["id"]: e for e in client.get("/emisores", headers=admin_headers).json()}
        assert (por_id[base["id"]]["por_defecto"], por_id[seg["id"]]["por_defecto"]) == (False, True)

    def test_las_series_no_se_repiten_ni_se_confunden(self, client, admin_headers):
        _emisor(client, admin_headers)
        malo = {"razon_social": "X", "cif": "B3", "direccion": "d"}
        assert client.post("/emisores", headers=admin_headers, json={**malo, "serie_facturas": "SEG", "serie_rectificativas": "R3"}).status_code == 409
        assert client.post("/emisores", headers=admin_headers, json={**malo, "serie_facturas": "FAC", "serie_rectificativas": "R3"}).status_code == 409
        assert client.post("/emisores", headers=admin_headers, json={**malo, "serie_facturas": "AA", "serie_rectificativas": "AA"}).status_code == 400
        assert client.post("/emisores", headers=admin_headers, json={**malo, "serie_facturas": "a b", "serie_rectificativas": "R3"}).status_code == 400

    def test_la_serie_no_se_cambia_cuando_ya_hay_facturas(self, client, admin_headers):
        (e,) = client.get("/emisores", headers=admin_headers).json()
        assert client.patch(f"/emisores/{e['id']}", headers=admin_headers, json={"serie_facturas": "NUEVA"}).status_code == 200
        ctx, _ = _albaran(client, admin_headers, cantidad=1)
        _facturar(client, admin_headers, ctx["pedido"]["cliente_id"])
        r = client.patch(f"/emisores/{e['id']}", headers=admin_headers, json={"serie_facturas": "OTRA"})
        assert r.status_code == 409
        assert client.get("/emisores", headers=admin_headers).json()[0]["con_facturas"] is True

    def test_una_empresa_emisora_necesita_razon_cif_y_direccion(self, client, admin_headers):
        r = client.post("/emisores", headers=admin_headers, json={"razon_social": "X", "cif": " ", "direccion": "d"})
        assert r.status_code == 400

    def test_editar_el_emisor_no_cambia_las_facturas_ya_emitidas(self, client, admin_headers):
        (e,) = client.get("/emisores", headers=admin_headers).json()
        ctx, _ = _albaran(client, admin_headers, cantidad=1)
        f = _facturar(client, admin_headers, ctx["pedido"]["cliente_id"]).json()
        client.patch(f"/emisores/{e['id']}", headers=admin_headers, json={"razon_social": "Nombre Nuevo SL", "cif": "B99999999"})
        despues = client.get(f"/facturas/{f['id']}", headers=admin_headers).json()
        assert despues["emisor_cif"] == "B00000000" and "Virtual Robotic" in despues["emisor_razon_social"]
        rect = client.post(f"/facturas/{f['id']}/anular", headers=admin_headers, json={"motivo": "x"}).json()
        assert rect["emisor_cif"] == "B00000000"  # hereda el de la ORIGINAL, no el actual

    def test_solo_admin_sistema_gestiona_emisores(self, client, admin_headers):
        a, _ = _albaran(client, admin_headers, cantidad=1)
        t = auth(a["tok_admin_cliente"])
        assert client.get("/emisores", headers=t).status_code == 403
        assert client.post("/emisores", headers=t, json={"razon_social": "X", "cif": "B1", "direccion": "d"}).status_code == 403


def test_el_emisor_unico_de_una_base_antigua_pasa_a_la_tabla_de_emisores(client):
    """Bases creadas antes de existir varias empresas guardaban UN emisor en configuracion_almacen."""
    from app import models as m
    from app.database import SessionLocal
    from app.main import sembrar_datos

    db = SessionLocal()
    try:
        db.query(m.Emisor).delete()
        cfg = db.query(m.ConfiguracionAlmacen).filter_by(id=1).one()
        cfg.emisor_razon_social, cfg.emisor_cif = "Empresa Vieja SL", "B12345678"
        cfg.emisor_direccion, cfg.emisor_email = "Calle Antigua 3", "vieja@example.com"
        db.commit()
    finally:
        db.close()
    sembrar_datos()
    db = SessionLocal()
    try:
        (e,) = db.query(m.Emisor).all()
        assert (e.razon_social, e.cif, e.por_defecto, e.activo) == ("Empresa Vieja SL", "B12345678", True, True)
        assert (e.serie_facturas, e.serie_rectificativas) == ("FAC", "RECT")
    finally:
        db.close()
