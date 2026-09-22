# Version: 2026-09-15 18:20 -- tests de productos (Color.codigo debe ser alfabetico, editable)
"""Catalogo de productos: alta/baja/modificacion, codigo unico por
producto, LED opcional (unico entre productos activos si se asigna)."""


def _id_led(client, admin_headers, codigo):
    colores = client.get("/colores", headers=admin_headers).json()
    return next(c["id"] for c in colores if c["codigo"] == codigo)


def test_seed_tiene_los_tres_productos_reales(client, admin_headers):
    r = client.get("/productos", headers=admin_headers)
    assert r.status_code == 200
    codigos = {p["codigo"] for p in r.json()}
    assert codigos == {"100", "200", "300"}
    leds = {p["led_codigo"] for p in r.json()}
    assert leds == {"R", "G", "B"}


def test_paleta_colores_trae_los_7(client, admin_headers):
    r = client.get("/paleta_colores", headers=admin_headers)
    assert r.status_code == 200
    assert set(r.json()) == {"R", "G", "B", "Y", "M", "C", "W"}


def test_crear_producto_ok(client, admin_headers):
    id_led = _id_led(client, admin_headers, "Y")
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV", "id_led": id_led}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["nombre"] == "Clavos"
    assert body["codigo"] == "CLV"
    assert body["led_codigo"] == "Y"
    assert body["activo"] is True


def test_crear_producto_sin_led_ok(client, admin_headers):
    """El LED es opcional (sesion 2026-09-15): un producto puramente
    administrativo, sin representacion fisica, tiene que poder darse de
    alta igual."""
    r = client.post("/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV"})
    assert r.status_code == 200
    body = r.json()
    assert body["id_led"] is None
    assert body["led_codigo"] is None


def test_producto_nace_con_grupo_cadena_cero(client, admin_headers):
    r = client.post("/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV"})
    assert r.json()["grupo_cadena"] == 0


def test_crear_y_cambiar_grupo_cadena(client, admin_headers):
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV", "grupo_cadena": 10}
    )
    assert r.status_code == 200
    assert r.json()["grupo_cadena"] == 10
    r = client.patch(f"/productos/{r.json()['id']}", headers=admin_headers, json={"grupo_cadena": 20})
    assert r.status_code == 200
    assert r.json()["grupo_cadena"] == 20


def test_grupo_cadena_fuera_de_rango_rechazado(client, admin_headers):
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV", "grupo_cadena": 100}
    )
    assert r.status_code == 400
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV", "grupo_cadena": -1}
    )
    assert r.status_code == 400


def test_no_se_puede_repetir_led(client, admin_headers):
    id_led = _id_led(client, admin_headers, "Y")
    client.post("/productos", headers=admin_headers, json={"nombre": "Clavos", "codigo": "CLV", "id_led": id_led})
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Otra cosa", "codigo": "OTR", "id_led": id_led}
    )
    assert r.status_code == 400


def test_no_se_puede_repetir_nombre(client, admin_headers):
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Tornillos", "codigo": "TOR"}
    )
    assert r.status_code == 400


def test_no_se_puede_repetir_codigo(client, admin_headers):
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Otro nombre", "codigo": "100"}
    )
    assert r.status_code == 400


def test_codigo_invalido_rechazado(client, admin_headers):
    # ni de 2 ni de 4 caracteres, ni con simbolos -- exactamente 3 alfanumericos
    for codigo in ("CL", "CLAV", "CL-V"):
        r = client.post(
            "/productos", headers=admin_headers, json={"nombre": "Cosa Rara", "codigo": codigo}
        )
        assert r.status_code == 400, codigo


def test_id_led_inexistente_rechazado(client, admin_headers):
    r = client.post(
        "/productos", headers=admin_headers, json={"nombre": "Cosa Rara", "codigo": "CLV", "id_led": 999999}
    )
    assert r.status_code == 400


def test_nombre_vacio_rechazado(client, admin_headers):
    r = client.post("/productos", headers=admin_headers, json={"nombre": "   ", "codigo": "CLV"})
    assert r.status_code == 400


def test_baja_logica_no_borra_el_producto(client, admin_headers):
    productos = client.get("/productos", headers=admin_headers).json()
    tornillos = next(p for p in productos if p["led_codigo"] == "R")

    r = client.patch(
        f"/productos/{tornillos['id']}", headers=admin_headers, json={"activo": False}
    )
    assert r.status_code == 200
    assert r.json()["activo"] is False

    # sigue apareciendo en el listado (baja logica, no DELETE fisico)
    productos_tras_baja = client.get("/productos", headers=admin_headers).json()
    assert any(p["id"] == tornillos["id"] for p in productos_tras_baja)


def test_patch_sin_cambios_da_400(client, admin_headers):
    productos = client.get("/productos", headers=admin_headers).json()
    pid = productos[0]["id"]
    r = client.patch(f"/productos/{pid}", headers=admin_headers, json={})
    assert r.status_code == 400


def test_solo_admin_sistema_puede_crear_productos(client, admin_headers):
    from .conftest import crear_cliente_con_usuario

    _cliente, token_cliente = crear_cliente_con_usuario(
        client, admin_headers, "Ferreteria Sur", "ferreteria_sur"
    )
    r = client.post(
        "/productos",
        headers={"X-Session-Token": token_cliente},
        json={"nombre": "Intento", "codigo": "INT"},
    )
    assert r.status_code == 403


class TestColores:
    """Alta/baja/modificacion del catalogo de colores (sesion 2026-09-15):
    ya no viven hardcodeados, ver PALETA_COLORES en la version vieja de
    main.py."""

    def test_crear_color_ok(self, client, admin_headers):
        r = client.post(
            "/colores", headers=admin_headers,
            json={"codigo": "P", "nombre": "Purpura", "r": 120, "g": 30, "b": 200, "fisico": False},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["codigo"] == "P"
        assert body["activo"] is True

    def test_no_se_puede_repetir_codigo_color(self, client, admin_headers):
        client.post("/colores", headers=admin_headers, json={"codigo": "P", "nombre": "Purpura", "r": 1, "g": 1, "b": 1})
        r = client.post("/colores", headers=admin_headers, json={"codigo": "P", "nombre": "Otro", "r": 2, "g": 2, "b": 2})
        assert r.status_code == 400

    def test_rgb_fuera_de_rango_rechazado(self, client, admin_headers):
        r = client.post("/colores", headers=admin_headers, json={"codigo": "P", "nombre": "Purpura", "r": 300, "g": 1, "b": 1})
        assert r.status_code == 400

    def test_baja_logica_de_color(self, client, admin_headers):
        colores = client.get("/colores", headers=admin_headers).json()
        amarillo = next(c for c in colores if c["codigo"] == "Y")
        r = client.patch(f"/colores/{amarillo['id']}", headers=admin_headers, json={"activo": False})
        assert r.status_code == 200
        assert r.json()["activo"] is False

    def test_codigo_no_alfabetico_rechazado(self, client, admin_headers):
        """Bug real visto en vivo (sesion 2026-09-15): un codigo "8" se
        colo sin avisar y el Loader lo rechazo al lanzar produccion
        ("only_color no es una letra de color valida") -- el codigo viaja
        tal cual como 'only_color' a un parametro ROS2, que exige
        alfabetico."""
        for codigo in ("8", "R2", "R-", ""):
            r = client.post(
                "/colores", headers=admin_headers,
                json={"codigo": codigo, "nombre": "Malo", "r": 1, "g": 1, "b": 1},
            )
            assert r.status_code == 400, codigo

    def test_editar_codigo_no_alfabetico_rechazado(self, client, admin_headers):
        colores = client.get("/colores", headers=admin_headers).json()
        amarillo = next(c for c in colores if c["codigo"] == "Y")
        r = client.patch(f"/colores/{amarillo['id']}", headers=admin_headers, json={"codigo": "9"})
        assert r.status_code == 400

    def test_editar_codigo_ok(self, client, admin_headers):
        colores = client.get("/colores", headers=admin_headers).json()
        amarillo = next(c for c in colores if c["codigo"] == "Y")
        r = client.patch(f"/colores/{amarillo['id']}", headers=admin_headers, json={"codigo": "AM"})
        assert r.status_code == 200, r.text
        assert r.json()["codigo"] == "AM"
        # sigue apareciendo en /colores, pero no en /paleta_colores (solo activos)
        assert any(c["id"] == amarillo["id"] for c in client.get("/colores", headers=admin_headers).json())
        assert "Y" not in client.get("/paleta_colores", headers=admin_headers).json()


class TestSubproductos:
    def test_crear_subproducto_ok(self, client, admin_headers):
        productos = client.get("/productos", headers=admin_headers).json()
        tornillos = next(p for p in productos if p["led_codigo"] == "R")
        r = client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tornillos["id"], "nombre": "Tornillo 30mm", "codigo": "9999"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["codigo_completo"] == f"{tornillos['codigo']}9999"

    def test_codigo_repetido_en_mismo_producto_rechazado(self, client, admin_headers):
        productos = client.get("/productos", headers=admin_headers).json()
        tornillos = next(p for p in productos if p["led_codigo"] == "R")
        client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tornillos["id"], "nombre": "A", "codigo": "9999"},
        )
        r = client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tornillos["id"], "nombre": "B", "codigo": "9999"},
        )
        assert r.status_code == 400

    def test_mismo_codigo_en_otro_producto_ok(self, client, admin_headers):
        """El codigo de subproducto es unico DENTRO de su producto, no
        global -- el codigo completo (producto+subproducto) ya lo
        distingue."""
        productos = client.get("/productos", headers=admin_headers).json()
        tornillos = next(p for p in productos if p["led_codigo"] == "R")
        tuercas = next(p for p in productos if p["led_codigo"] == "G")
        client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tornillos["id"], "nombre": "A", "codigo": "9999"},
        )
        r = client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tuercas["id"], "nombre": "B", "codigo": "9999"},
        )
        assert r.status_code == 200

    def test_codigo_invalido_rechazado(self, client, admin_headers):
        productos = client.get("/productos", headers=admin_headers).json()
        tornillos = productos[0]
        r = client.post(
            "/subproductos", headers=admin_headers,
            json={"producto_id": tornillos["id"], "nombre": "A", "codigo": "99"},
        )
        assert r.status_code == 400


class TestPaquetes:
    def test_crear_paquete_ok(self, client, admin_headers):
        subproductos = client.get("/subproductos", headers=admin_headers).json()
        r = client.post(
            "/paquetes", headers=admin_headers,
            json={
                "nombre": "Kit de prueba", "codigo": "KIT1",
                "componentes": [{"subproducto_id": subproductos[0]["id"], "cantidad": 5}],
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["nombre"] == "Kit de prueba"
        assert len(body["componentes"]) == 1
        assert body["componentes"][0]["cantidad"] == 5

    def test_paquete_sin_componentes_rechazado(self, client, admin_headers):
        r = client.post(
            "/paquetes", headers=admin_headers,
            json={"nombre": "Kit vacio", "codigo": "KIT2", "componentes": []},
        )
        assert r.status_code == 400

    def test_seed_trae_el_paquete_de_10(self, client, admin_headers):
        paquetes = client.get("/paquetes", headers=admin_headers).json()
        p010 = next(p for p in paquetes if p["codigo"] == "P010")
        assert len(p010["componentes"]) == 3
        assert all(c["cantidad"] == 10 for c in p010["componentes"])
