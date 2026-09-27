"""Empleados de nuestra empresa con permiso por grupo (sesion 2026-09-26):
Antonio (jefe de taller) solo Produccion, Maria (administrativa) solo
Contabilidad, Juan las dos. Administracion sigue siendo solo del admin."""
from app import auth as auth_module

from .conftest import asignar_producto, auth, crear_cliente_con_usuario, login, producto_por_color, subproducto_por_color


def _empleado(client, admin_headers, username, produccion=False, contabilidad=False, password="clave-" + "x"):
    r = client.post("/usuarios", headers=admin_headers, json={
        "username": username, "nombre_completo": username.capitalize(), "rol": "empleado",
        "password": password, "permiso_produccion": produccion, "permiso_contabilidad": contabilidad,
    })
    assert r.status_code == 200, r.text
    return r.json(), auth(login(client, username, password))


def _pedido_de_un_cliente(client, admin_headers):
    cliente, tok = crear_cliente_con_usuario(client, admin_headers, "Astilleros Prueba", "apr-admin")
    asignar_producto(client, admin_headers, cliente["id"], producto_por_color(client, admin_headers, "R")["id"])
    sub = subproducto_por_color(client, admin_headers, "R")["id"]
    r = client.post("/pedidos", headers=auth(tok), json={"subproducto_id": sub, "cantidad_pedida": 3})
    assert r.status_code == 200, r.text
    return r.json()


def test_alta_de_empleado_sin_cliente_y_con_sus_permisos(client, admin_headers):
    u, h = _empleado(client, admin_headers, "antonio", produccion=True)
    assert u["cliente_id"] is None
    yo = client.get("/me", headers=h).json()
    assert yo["rol"] == "empleado"
    assert yo["permiso_produccion"] is True and yo["permiso_contabilidad"] is False


def test_antonio_solo_produccion(client, admin_headers):
    _u, h = _empleado(client, admin_headers, "antonio", produccion=True)
    for ruta in ("/taller/diagnostico", "/movimientos_stock", "/pedidos", "/repartos", "/clientes"):
        assert client.get(ruta, headers=h).status_code == 200, ruta
    for ruta in ("/facturas", "/historial_precios", "/audit", "/usuarios"):
        assert client.get(ruta, headers=h).status_code == 403, ruta
    assert client.post("/colores", headers=h, json={"codigo": "P", "nombre": "Rosa", "r": 1, "g": 0, "b": 0}).status_code == 403


def test_maria_solo_contabilidad(client, admin_headers):
    _u, h = _empleado(client, admin_headers, "maria", contabilidad=True)
    for ruta in ("/facturas", "/historial_precios", "/emisores", "/repartos", "/pedidos"):
        assert client.get(ruta, headers=h).status_code == 200, ruta
    for ruta in ("/taller/diagnostico", "/movimientos_stock", "/audit", "/usuarios"):
        assert client.get(ruta, headers=h).status_code == 403, ruta
    assert client.post("/almacen/repartir", headers=h).status_code == 403
    # las empresas emisoras se crean en Administracion: solo el admin
    assert client.post("/emisores", headers=h, json={"razon_social": "X", "cif": "B1", "direccion": "Calle 1"}).status_code == 403


def test_juan_las_dos(client, admin_headers):
    _u, h = _empleado(client, admin_headers, "juan", produccion=True, contabilidad=True)
    for ruta in ("/taller/diagnostico", "/facturas", "/historial_precios", "/movimientos_stock"):
        assert client.get(ruta, headers=h).status_code == 200, ruta
    assert client.get("/audit", headers=h).status_code == 403


def test_produccion_gestiona_pedidos_de_cualquier_cliente_y_contabilidad_no(client, admin_headers):
    pedido = _pedido_de_un_cliente(client, admin_headers)
    _a, antonio = _empleado(client, admin_headers, "antonio", produccion=True)
    _m, maria = _empleado(client, admin_headers, "maria", contabilidad=True)
    assert client.patch(f"/pedidos/{pedido['id']}", headers=maria, json={"urgente": True}).status_code == 403
    r = client.patch(f"/pedidos/{pedido['id']}", headers=antonio, json={"urgente": True})
    assert r.status_code == 200 and r.json()["urgente"] is True
    assert client.post(f"/pedidos/{pedido['id']}/reclamar", headers=antonio,
                       json={"numero_maquina": 3, "forzar": True}).status_code == 200
    # corregir el precio es de Contabilidad
    assert client.patch(f"/pedidos/{pedido['id']}/precio", headers=antonio,
                        json={"precio_centimos": 50, "motivo": "x"}).status_code == 403
    assert client.post(f"/pedidos/{pedido['id']}/cancelar", headers=antonio).status_code == 200


def test_empleado_no_hace_pedidos(client, admin_headers):
    _u, h = _empleado(client, admin_headers, "juan", produccion=True, contabilidad=True)
    sub = subproducto_por_color(client, admin_headers, "R")["id"]
    assert client.post("/pedidos", headers=h, json={"subproducto_id": sub, "cantidad_pedida": 1}).status_code == 403


def test_empleado_sin_permisos_no_ve_nada(client, admin_headers):
    _u, h = _empleado(client, admin_headers, "nadie")
    assert client.get("/pedidos", headers=h).status_code == 403
    assert client.get("/facturas", headers=h).status_code == 403
    assert client.get("/clientes", headers=h).json() == []


def test_cambiar_permisos_hace_efecto(client, admin_headers):
    u, h = _empleado(client, admin_headers, "antonio", produccion=True)
    assert client.get("/facturas", headers=h).status_code == 403
    r = client.patch(f"/usuarios/{u['id']}", headers=admin_headers, json={"permiso_contabilidad": True})
    assert r.status_code == 200 and r.json()["permiso_contabilidad"] is True
    assert client.get("/facturas", headers=h).status_code == 200


def test_empleado_necesita_usuario_y_contrasena(client, admin_headers):
    base = {"nombre_completo": "Antonio", "rol": "empleado", "permiso_produccion": True}
    assert client.post("/usuarios", headers=admin_headers, json={**base, "password": "x"}).status_code == 400
    assert client.post("/usuarios", headers=admin_headers, json={**base, "username": "antonio"}).status_code == 400


def test_la_clave_maestra_no_vale_para_empleados_fuera_de_desarrollo(client, admin_headers, monkeypatch):
    _empleado(client, admin_headers, "antonio", produccion=True, password="suya")
    monkeypatch.setattr(auth_module, "DEV_MODE", False)
    assert client.post("/login", json={"username": "antonio", "password": "1111"}).status_code == 401
    assert client.post("/login", json={"username": "antonio", "password": "suya"}).status_code == 200


def test_admin_cliente_no_crea_ni_toca_empleados(client, admin_headers):
    _c, tok = crear_cliente_con_usuario(client, admin_headers, "Empresa Cuatro", "cuatro")
    r = client.post("/usuarios", headers=auth(tok), json={
        "username": "colado", "nombre_completo": "Colado", "rol": "empleado", "password": "x",
        "permiso_produccion": True, "permiso_contabilidad": True})
    assert r.status_code == 403
    u, _h = _empleado(client, admin_headers, "antonio", produccion=True)
    assert client.patch(f"/usuarios/{u['id']}", headers=auth(tok),
                        json={"permiso_contabilidad": True}).status_code == 403


def test_un_usuario_de_cliente_no_se_convierte_en_empleado(client, admin_headers):
    _c, _tok = crear_cliente_con_usuario(client, admin_headers, "Empresa Cinco", "cinco")
    usuario = next(u for u in client.get("/usuarios", headers=admin_headers).json() if u["username"] == "cinco")
    r = client.patch(f"/usuarios/{usuario['id']}", headers=admin_headers, json={"rol": "empleado"})
    assert r.status_code == 400
    u, _h = _empleado(client, admin_headers, "antonio", produccion=True)
    assert client.patch(f"/usuarios/{u['id']}", headers=admin_headers, json={"rol": "normal"}).status_code == 400
