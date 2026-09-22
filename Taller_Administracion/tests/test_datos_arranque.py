# Version: 2026-09-21 18:22 -- tests del fichero de clientes y usuarios iniciales
"""app/datos_arranque.py: el fichero de texto que se edita a mano y con el que arranca
una base de datos vacia."""
import os
from pathlib import Path

import pytest

from app import auth, datos_arranque, models
from app.database import SessionLocal, engine
from app.main import sembrar_datos

TEXTO = """Usuarios BBDD Inicial

Admin -> Admin.sistema

Cliente:
    R.S.: Astilleros Uno S.L.
    Cif : B11111111
    Dir.: Calle Larga 1
    C.P.: 48001
    Pob.: Bilbao
    Pro.: Bizkaia
    cor.: admin@uno.example

        user admin-> Uno    sucursal -> Bilbao
        user normal-> uno1   sucursal -> madrid
        user normal-> uno2   sucursal -> Sevilla    nombre -> Ana Lopez

    R.S.: Suministros Dos S.A.
    Cif : A22222222
    Productos: 100, Arandelas
        user admin-> dos     sucursal -> Gernika
"""


def _sembrar_desde(tmp_path, monkeypatch, texto):
    ruta = tmp_path / "arranque.txt"
    ruta.write_text(texto, encoding="utf-8")
    monkeypatch.setenv("TALLER_DATOS_ARRANQUE", str(ruta))
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    sembrar_datos()


class TestParser:
    def test_lee_clientes_datos_fiscales_y_usuarios(self):
        uno, dos = datos_arranque.parsear(TEXTO)
        assert (uno.razon_social, uno.cif, uno.direccion, uno.codigo_postal) == (
            "Astilleros Uno S.L.", "B11111111", "Calle Larga 1", "48001")
        assert (uno.poblacion, uno.provincia, uno.email_facturacion) == ("Bilbao", "Bizkaia", "admin@uno.example")
        assert [(u.username, u.rol) for u in uno.usuarios] == [
            ("uno", "admin_cliente"), ("uno1", "normal"), ("uno2", "normal")]
        assert dos.razon_social == "Suministros Dos S.A."

    def test_el_usuario_va_en_minusculas_y_la_sucursal_con_mayuscula_inicial(self):
        uno, _ = datos_arranque.parsear(TEXTO)
        assert uno.usuarios[0].username == "uno"       # 'Uno' -> 'uno': el login no distingue mayusculas
        assert uno.usuarios[1].sucursal == "Madrid"    # 'madrid' -> 'Madrid'

    def test_nombre_completo_automatico_o_el_indicado(self):
        uno, _ = datos_arranque.parsear(TEXTO)
        assert [u.nombre_completo for u in uno.usuarios] == ["Administrador Bilbao", "Operario Madrid", "Ana Lopez"]

    def test_productos_por_defecto_todos_o_los_de_su_linea(self):
        uno, dos = datos_arranque.parsear(TEXTO)
        assert uno.productos is None
        assert dos.productos == ["100", "Arandelas"]

    def test_lo_que_no_es_del_formato_se_ignora(self):
        assert len(datos_arranque.parsear("titulo suelto\n# comentario\n" + TEXTO)) == 2

    @pytest.mark.parametrize("texto, mensaje", [
        ("user admin-> a sucursal -> X\nR.S.: Uno\n", "Linea 1"),
        ("Cif : B1\n", "antes de ningun cliente"),
        ("R.S.: Uno\n user admin-> a sucursal -> X\nR.S.: Dos\n user admin-> a sucursal -> Y\n", "repetido"),
        ("R.S.: Uno\n user normal-> a sucursal -> X\n", "ningun 'user admin'"),
        ("R.S.: Uno\n", "ningun usuario"),
        ("R.S.:\n", "sin razon social"),
    ])
    def test_los_errores_dicen_que_pasa(self, texto, mensaje):
        with pytest.raises(datos_arranque.ErrorDatosArranque, match=mensaje):
            datos_arranque.parsear(texto)

    def test_fichero_inexistente_devuelve_none(self, tmp_path):
        assert datos_arranque.leer(tmp_path / "no.txt") is None

    def test_el_fichero_real_del_repo_es_valido(self):
        """Si se edita a mano y se rompe, este test lo dice ANTES de arrancar la base."""
        repo = Path(os.environ.get("TALLER_REPO_DIR", Path(__file__).resolve().parents[2]))
        ruta = repo / "Documentacion" / "UsuariosBBDDArranque.txt"
        if not ruta.is_file():
            pytest.skip("no hay fichero de arranque en este entorno")
        clientes = datos_arranque.leer(ruta)
        assert clientes, "el fichero no define ningun cliente"
        usernames = [u.username for c in clientes for u in c.usuarios]
        assert len(usernames) == len(set(usernames))
        assert all(c.cif for c in clientes), "todos los clientes necesitan CIF para poder facturar"


class TestSembrado:
    def test_una_base_vacia_se_siembra_con_los_clientes_del_fichero(self, tmp_path, monkeypatch):
        _sembrar_desde(tmp_path, monkeypatch, TEXTO)
        db = SessionLocal()
        try:
            clientes = {c.razon_social: c for c in db.query(models.Cliente).all()}
            assert set(clientes) == {"Astilleros Uno S.L.", "Suministros Dos S.A."}
            uno = clientes["Astilleros Uno S.L."]
            assert (uno.cif, uno.direccion, uno.provincia) == ("B11111111", "Calle Larga 1", "Bizkaia")
            usuarios = {u.username: u for u in db.query(models.Usuario).filter(models.Usuario.cliente_id == uno.id)}
            assert set(usuarios) == {"uno", "uno1", "uno2"}
            assert (usuarios["uno"].rol, usuarios["uno1"].rol) == ("admin_cliente", "normal")
            assert usuarios["uno1"].sucursal == "Madrid"
        finally:
            db.close()

    def test_los_usuarios_nacen_con_la_contrasena_inicial_1111(self, tmp_path, monkeypatch):
        _sembrar_desde(tmp_path, monkeypatch, TEXTO)
        db = SessionLocal()
        try:
            for username in ("uno", "uno1", "dos"):
                usuario = db.query(models.Usuario).filter_by(username=username).one()
                assert usuario.password_hash and auth.verify_password("1111", usuario.password_hash)
                assert not auth.verify_password("otra", usuario.password_hash)
        finally:
            db.close()

    def test_sin_linea_de_productos_el_cliente_puede_pedir_todos(self, tmp_path, monkeypatch):
        _sembrar_desde(tmp_path, monkeypatch, TEXTO)
        db = SessionLocal()
        try:
            total = db.query(models.Producto).count()
            uno = db.query(models.Cliente).filter_by(cif="B11111111").one()
            dos = db.query(models.Cliente).filter_by(cif="A22222222").one()
            assert db.query(models.ClienteProducto).filter_by(cliente_id=uno.id).count() == total
            # 'Productos: 100, Arandelas' -> Tornillos (100) y Arandelas (por nombre)
            nombres = {cp.producto.nombre for cp in db.query(models.ClienteProducto).filter_by(cliente_id=dos.id)}
            assert nombres == {"Tornillos", "Arandelas"}
        finally:
            db.close()

    def test_un_producto_que_no_existe_para_el_arranque_con_un_mensaje_claro(self, tmp_path, monkeypatch):
        texto = TEXTO.replace("Productos: 100, Arandelas", "Productos: 999")
        with pytest.raises(datos_arranque.ErrorDatosArranque, match="999"):
            _sembrar_desde(tmp_path, monkeypatch, texto)

    def test_el_usuario_sembrado_puede_entrar_y_pedir(self, tmp_path, monkeypatch, client):
        _sembrar_desde(tmp_path, monkeypatch, TEXTO)
        r = client.post("/login", json={"username": "uno1", "password": "1111"})
        assert r.status_code == 200, r.text
        assert r.json()["usuario"]["rol"] == "normal"

    def test_no_se_vuelve_a_sembrar_si_ya_hay_clientes(self, tmp_path, monkeypatch):
        _sembrar_desde(tmp_path, monkeypatch, TEXTO)
        (tmp_path / "arranque.txt").write_text("R.S.: Otro\n user admin-> otro sucursal -> X\n", encoding="utf-8")
        sembrar_datos()  # segunda vez, con un fichero distinto: no debe tocar lo que ya hay
        db = SessionLocal()
        try:
            assert db.query(models.Cliente).count() == 2
            assert db.query(models.Usuario).filter_by(username="otro").first() is None
        finally:
            db.close()


class TestCargarEnBaseConDatos:
    """cargar(solo_los_que_faltan=True): para una base en produccion, sin borrar nada."""

    def _cargar(self, tmp_path, texto):
        ruta = tmp_path / "otro.txt"
        ruta.write_text(texto, encoding="utf-8")
        db = SessionLocal()
        try:
            return datos_arranque.cargar(db, datos_arranque.leer(ruta), auth.hash_password("1111"),
                                         solo_los_que_faltan=True)
        finally:
            db.close()

    def test_anade_lo_que_falta_y_omite_lo_que_ya_existe(self, client, tmp_path):
        # la base de los tests ya trae 3 clientes de ejemplo; el CIF B48123456 es uno de ellos
        r = self._cargar(tmp_path, (
            "R.S.: Nombre Distinto S.A.\n Cif : B48123456\n user admin-> nuevo_a sucursal -> X\n"
            "R.S.: Cliente Nuevo S.L.\n Cif : B99999999\n user admin-> nuevo_b sucursal -> Y\n"
            " user normal-> ere-admin sucursal -> Z\n"))
        assert r["clientes_nuevos"] == ["Cliente Nuevo S.L."]
        assert len(r["clientes_omitidos"]) == 1 and "B48123456" in r["clientes_omitidos"][0]
        assert r["usuarios_nuevos"] == ["nuevo_b"]
        assert r["usuarios_omitidos"] == ["ere-admin (ya existe)"]  # ya es usuario del ejemplo

    def test_no_toca_los_clientes_existentes_y_es_idempotente(self, client, tmp_path):
        texto = "R.S.: Cliente Nuevo S.L.\n Cif : B99999999\n user admin-> nuevo_b sucursal -> Y\n"
        self._cargar(tmp_path, texto)
        segunda = self._cargar(tmp_path, texto)
        assert segunda["clientes_nuevos"] == [] and segunda["usuarios_nuevos"] == []
        db = SessionLocal()
        try:
            assert db.query(models.Cliente).filter_by(cif="B99999999").count() == 1
            assert db.query(models.Cliente).count() == 4  # los 3 de ejemplo + 1 nuevo
        finally:
            db.close()
