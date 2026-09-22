"""Fixtures compartidas. IMPORTANTE: la variable de entorno TALLER_DB_PATH
se fija a un fichero temporal ANTES de importar nada de `app` -- database.py
lee esa variable en el momento del import y crea el engine ahi mismo, asi
que si `app.main` (o cualquier submodulo) se importara antes de este punto,
los tests escribirian sobre data/taller.db, la base de datos REAL de
produccion con pedidos de verdad. No mover este bloque de sitio ni
reordenar los imports de arriba del fichero.
"""
import os
import shutil
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="taller_tests_")
os.environ["TALLER_DB_PATH"] = os.path.join(_TMP_DIR, "test.db")
os.environ["TALLER_MASTER_PASSWORD"] = "1111"
# Los tests NO deben depender del fichero de arranque que edita el usuario a mano: si se
# equivocara al editarlo, fallarian todos. Apuntan a un fichero que no existe, asi se
# siembran los clientes de ejemplo del codigo (ver _clientes_iniciales en main.py).
os.environ["TALLER_DATOS_ARRANQUE"] = os.path.join(_TMP_DIR, "no_existe.txt")
# El barrido periodico de stock corre solo en produccion; en los tests se apaga (seria un hilo que
# cambia stock y pedidos mientras se comprueban) y se prueba llamando a barrer_stock() a mano.
os.environ["TALLER_BARRIDO_SEGUNDOS"] = "0"
os.environ["TALLER_DEV_MODE"] = "true"  # los tests representan nuestro entorno de desarrollo

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402

ADMIN_USERNAME = "admin"
# "1111" (la maestra) y no la password real "admin" del admin sembrado:
# este valor tambien se usa como password por defecto al crear OTROS
# usuarios en los tests (crear_cliente_con_usuario), que no tienen
# password_hash propio y dependen de la maestra + TALLER_DEV_MODE=true.
ADMIN_PASSWORD = "1111"


@pytest.fixture(scope="session", autouse=True)
def _limpiar_tmp_dir_al_final():
    yield
    shutil.rmtree(_TMP_DIR, ignore_errors=True)


@pytest.fixture()
def client():
    """Cliente HTTP con una BBDD limpia y recien sembrada en cada test.

    drop_all + create_all sobre el mismo engine de test (nunca toca el
    fichero real) y luego entra en el TestClient como context manager, que
    dispara el evento startup de la app (sembrar_datos: productos R/G/B,
    usuario 'admin' admin_sistema, configuracion con reparto_automatico
    activo) -- exactamente el mismo camino que sigue la app en produccion,
    no una reimplementacion aparte del seed.
    """
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def login(client, username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
    r = client.post("/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def auth(token):
    return {"X-Session-Token": token}


@pytest.fixture()
def admin_token(client):
    return login(client)


@pytest.fixture()
def admin_headers(admin_token):
    return auth(admin_token)


def crear_cliente_con_usuario(client, admin_headers, razon_social, username, password=None):
    """Alta de cliente + su primer admin_cliente, como hace la app de verdad
    (POST /clientes crea las dos cosas a la vez). Devuelve (cliente, token
    de ese admin_cliente)."""
    r = client.post(
        "/clientes",
        headers=admin_headers,
        json={
            "razon_social": razon_social,
            "cif": None,
            "primer_usuario": {
                "username": username,
                "nombre_completo": f"Admin de {razon_social}",
                "password": password,
            },
        },
    )
    assert r.status_code == 200, r.text
    cliente = r.json()
    token = login(client, username, password or ADMIN_PASSWORD)
    return cliente, token


def asignar_producto(client, admin_headers, cliente_id, producto_id):
    r = client.post(
        f"/clientes/{cliente_id}/productos",
        headers=admin_headers,
        json={"producto_id": producto_id},
    )
    assert r.status_code == 200, r.text
    return r.json()


def producto_por_color(client, admin_headers, color):
    """Sesion 2026-09-15: 'color' paso a ser 'led_codigo' (ver
    Documentacion/aladin_cambio BBDD.txt) -- se mantiene el nombre de esta
    funcion (usada en casi todos los tests) para no tener que renombrar
    cada llamada."""
    productos = client.get("/productos", headers=admin_headers).json()
    return next(p for p in productos if p["led_codigo"] == color)


def subproducto_por_color(client, admin_headers, color):
    """El pedido ya no cuelga del producto directo, sino de un
    subproducto suyo -- para los tests basta con el primero que tenga
    (el seed siembra al menos uno por producto, ver SEED_SUBPRODUCTOS en
    main.py)."""
    producto = producto_por_color(client, admin_headers, color)
    subproductos = client.get(
        "/subproductos", headers=admin_headers, params={"producto_id": producto["id"]}
    ).json()
    return subproductos[0]


def crear_usuario_normal(client, admin_headers, cliente_id, username, sucursal=None):
    r = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": username,
            "nombre_completo": f"Operario {username}",
            "rol": "normal",
            "cliente_id": cliente_id,
            "sucursal": sucursal,
            "password": None,
        },
    )
    assert r.status_code == 200, r.text
    return r.json()
