# Version: 2026-09-21 18:22 -- tests del codigo de cliente y de los usuarios que salen de el
import pytest

from app import auth, codigos, datos_arranque, models
from app.database import SessionLocal
from tests.conftest import auth as cabeceras, crear_cliente_con_usuario, login


class TestModuloCodigos:
    def test_normalizar_pasa_a_mayusculas_y_quita_acentos(self):
        assert codigos.normalizar_codigo(" mur ") == "MUR"
        assert codigos.normalizar_codigo("ñu1") == "NU1"

    @pytest.mark.parametrize("malo", ["", "ab", "abcd", "a-b", "a b", "mü!"])
    def test_normalizar_rechaza_lo_que_no_son_3_letras_o_cifras(self, malo):
        with pytest.raises(codigos.ErrorCodigo):
            codigos.normalizar_codigo(malo)

    def test_sugerir_usa_la_primera_palabra_con_significado(self):
        assert codigos.sugerir_codigo("Suministros Ereño S.A.", set()) == "SUM"
        assert codigos.sugerir_codigo("Ría de Vigo S.L.", set()) == "RIA"

    def test_sugerir_no_repite_un_codigo_ocupado(self):
        assert codigos.sugerir_codigo("Suministros Ereño S.A.", {"SUM"}) == "ERE"
        # sin mas palabras se cambia la ultima letra por una cifra
        assert codigos.sugerir_codigo("Astilleros", {"AST"}) == "AS1"

    def test_sugerir_rellena_los_nombres_cortos(self):
        assert codigos.sugerir_codigo("Xu", set()) == "XUX"

    def test_slug_quita_acentos_y_espacios(self):
        assert codigos.slug("A Coruña") == "a-coruna"
        assert codigos.slug("  Ereño ") == "ereno"

    def test_usuario_de_forma_el_nombre(self):
        assert codigos.usuario_de("MUR", "Bilbao", es_admin=False) == "mur-bilbao"
        assert codigos.usuario_de("MUR", "cualquiera", es_admin=True) == "mur-admin"
        with pytest.raises(codigos.ErrorCodigo):
            codigos.usuario_de("MUR", None, es_admin=False)


def _alta(client, admin_headers, razon, **extra):
    return client.post("/clientes", headers=admin_headers, json={
        "razon_social": razon, "primer_usuario": {"nombre_completo": "Admin", **extra.pop("primer", {})}, **extra})


class TestApiClientes:
    def test_sin_codigo_se_saca_de_la_razon_social(self, client, admin_headers):
        r = _alta(client, admin_headers, "Tornillos del Norte S.L.")
        assert r.status_code == 200, r.text
        assert r.json()["codigo"] == "TOR"

    def test_con_codigo_se_normaliza_y_el_primer_usuario_es_codigo_admin(self, client, admin_headers):
        r = _alta(client, admin_headers, "Astilleros Nuevos", codigo="ast")
        assert r.status_code == 200, r.text
        assert r.json()["codigo"] == "AST"
        usuarios = client.get("/usuarios", headers=admin_headers).json()
        assert any(u["username"] == "ast-admin" and u["rol"] == "admin_cliente" for u in usuarios)

    def test_el_usuario_escrito_a_mano_sigue_valiendo(self, client, admin_headers):
        r = _alta(client, admin_headers, "Otra Empresa", primer={"username": "jefe"})
        assert r.status_code == 200
        assert any(u["username"] == "jefe" for u in client.get("/usuarios", headers=admin_headers).json())

    def test_codigo_repetido_da_409_y_mal_formado_400(self, client, admin_headers):
        assert _alta(client, admin_headers, "Uno", codigo="ABC").status_code == 200
        assert _alta(client, admin_headers, "Dos", codigo="abc").status_code == 409
        assert _alta(client, admin_headers, "Tres", codigo="ab").status_code == 400

    def test_dos_clientes_sin_codigo_no_chocan(self, client, admin_headers):
        a = _alta(client, admin_headers, "Metalurgica Alfa").json()["codigo"]
        b = _alta(client, admin_headers, "Metalurgica Beta").json()["codigo"]
        assert a != b and {a, b} == {"MET", "BET"}

    def test_solo_el_admin_del_sistema_cambia_el_codigo(self, client, admin_headers):
        cliente, token = crear_cliente_con_usuario(client, admin_headers, "Cliente Uno", "uno-jefe")
        r = client.patch(f"/clientes/{cliente['id']}", headers=cabeceras(token), json={"codigo": "XYZ"})
        assert r.status_code == 403
        r = client.patch(f"/clientes/{cliente['id']}", headers=admin_headers, json={"codigo": "xyz"})
        assert r.status_code == 200 and r.json()["codigo"] == "XYZ"

    def test_cambiar_a_un_codigo_de_otro_da_409(self, client, admin_headers):
        _alta(client, admin_headers, "Uno", codigo="AAA")
        otro = _alta(client, admin_headers, "Dos", codigo="BBB").json()
        r = client.patch(f"/clientes/{otro['id']}", headers=admin_headers, json={"codigo": "AAA"})
        assert r.status_code == 409


class TestApiUsuarios:
    def test_un_usuario_sin_nombre_se_forma_con_codigo_y_sucursal(self, client, admin_headers):
        cliente = _alta(client, admin_headers, "Astilleros Murueta", codigo="MUR").json()
        r = client.post("/usuarios", headers=admin_headers, json={
            "nombre_completo": "Ana", "rol": "normal", "cliente_id": cliente["id"], "sucursal": "Bilbao"})
        assert r.status_code == 200, r.text
        assert r.json()["username"] == "mur-bilbao"
        # y otro cliente puede tener su propia sucursal de Bilbao
        otro = _alta(client, admin_headers, "Ferreteria Irazabal", codigo="IRA").json()
        r = client.post("/usuarios", headers=admin_headers, json={
            "nombre_completo": "Luis", "rol": "normal", "cliente_id": otro["id"], "sucursal": "Bilbao"})
        assert r.json()["username"] == "ira-bilbao"

    def test_la_misma_sucursal_dos_veces_da_409(self, client, admin_headers):
        cliente = _alta(client, admin_headers, "Astilleros Murueta", codigo="MUR").json()
        cuerpo = {"nombre_completo": "Ana", "rol": "normal", "cliente_id": cliente["id"], "sucursal": "Madrid"}
        assert client.post("/usuarios", headers=admin_headers, json=cuerpo).status_code == 200
        assert client.post("/usuarios", headers=admin_headers, json=cuerpo).status_code == 409

    def test_el_admin_de_empresa_crea_usuarios_de_su_cliente_sin_escribir_el_nombre(self, client, admin_headers):
        cliente = _alta(client, admin_headers, "Astilleros Murueta", codigo="MUR").json()
        token = login(client, "mur-admin", "1111")
        r = client.post("/usuarios", headers=cabeceras(token), json={
            "nombre_completo": "Eva", "rol": "normal", "sucursal": "Madrid"})
        assert r.status_code == 200, r.text
        assert r.json()["username"] == "mur-madrid" and r.json()["cliente_id"] == cliente["id"]

    def test_sin_nombre_ni_sucursal_da_400(self, client, admin_headers):
        cliente = _alta(client, admin_headers, "Astilleros Murueta", codigo="MUR").json()
        r = client.post("/usuarios", headers=admin_headers, json={
            "nombre_completo": "Ana", "rol": "normal", "cliente_id": cliente["id"]})
        assert r.status_code == 400


TEXTO_NUEVO = """Cliente:
    R.S.: Astilleros Uno S.L.
    Cod.: uno
    Cif : B11111111
        sucursal admin -> Murueta
        sucursal -> Bilbao
        sucursal -> A Coruña   nombre -> Ana Lopez
        user normal-> antiguo   sucursal -> Madrid
    R.S.: Suministros Dos S.A.
    Cif : A22222222
        sucursal admin -> Ereño
        sucursal -> Bilbao
"""


class TestFicheroDeArranque:
    def test_los_usuarios_salen_del_codigo_y_la_sucursal(self):
        uno, dos = datos_arranque.parsear(TEXTO_NUEVO)
        assert uno.codigo == "UNO"
        assert [u.username for u in uno.usuarios] == ["uno-admin", "uno-bilbao", "uno-a-coruna", "antiguo"]
        assert uno.usuarios[0].rol == "admin_cliente" and uno.usuarios[1].rol == "normal"
        assert uno.usuarios[2].nombre_completo == "Ana Lopez"
        assert uno.usuarios[1].nombre_completo == "Operario Bilbao"

    def test_sin_codigo_se_saca_de_la_razon_social_y_dos_bilbao_conviven(self):
        _, dos = datos_arranque.parsear(TEXTO_NUEVO)
        assert dos.codigo == "SUM"
        assert [u.username for u in dos.usuarios] == ["sum-admin", "sum-bilbao"]

    @pytest.mark.parametrize("texto,mensaje", [
        ("R.S.: A\n Cod.: ab\n sucursal admin -> X\n", "3 letras"),
        ("R.S.: A\n Cod.: AAA\n sucursal admin -> X\nR.S.: B\n Cod.: aaa\n sucursal admin -> Y\n", "esta en dos clientes"),
        ("R.S.: A\n Cod.: AAA\n sucursal admin -> X\n sucursal -> Y\n sucursal -> y\n", "esta repetido"),
        ("sucursal -> Y\n", "antes de ningun cliente"),
        ("R.S.: A\n Cod.: AAA\n sucursal -> Y\n", "ningun 'user admin'"),
    ])
    def test_errores_con_mensaje(self, texto, mensaje):
        with pytest.raises(datos_arranque.ErrorDatosArranque, match=mensaje):
            datos_arranque.parsear(texto)

    def test_el_fichero_real_usa_codigos_y_usuarios_unicos(self):
        from pathlib import Path
        import os
        repo = Path(os.environ.get("TALLER_REPO_DIR", Path(__file__).resolve().parents[2]))
        ruta = repo / "Documentacion" / "UsuariosBBDDArranque.txt"
        if not ruta.is_file():
            pytest.skip("no hay fichero de arranque en este entorno")
        clientes = datos_arranque.leer(ruta)
        assert [c.codigo for c in clientes] == ["MUR", "ERE", "IRA"]
        assert "mur-bilbao" in [u.username for u in clientes[0].usuarios]
        assert "ere-bilbao" in [u.username for u in clientes[1].usuarios]


class TestCargarConCodigos:
    def test_una_base_vacia_se_siembra_con_codigos_y_usuarios_nuevos(self, client, admin_headers, tmp_path):
        # la base del test ya trae los clientes de ejemplo (con codigo); se comprueba la de ejemplo
        codigos_en_base = {c["codigo"] for c in client.get("/clientes", headers=admin_headers).json()}
        assert codigos_en_base == {"ERE", "MUN", "BUS"}
        usuarios = {u["username"] for u in client.get("/usuarios", headers=admin_headers).json()}
        assert {"ere-admin", "ere-bermeo", "mun-admin", "bus-admin"} <= usuarios

    def test_renombrar_pasa_los_usuarios_antiguos_al_nombre_nuevo(self, client, admin_headers, tmp_path):
        # un cliente "antiguo": usuarios con nombres a mano y sin codigo
        db = SessionLocal()
        try:
            c = models.Cliente(razon_social="Astilleros Murueta S.L.", cif="B77777777", activo=True)
            db.add(c)
            db.flush()
            db.add(models.Usuario(username="murueta", nombre_completo="Admin", rol="admin_cliente", cliente_id=c.id,
                                  sucursal="Murueta", activo=True, password_hash=auth.hash_password("1111")))
            db.add(models.Usuario(username="bilbao", nombre_completo="Ana", rol="normal", cliente_id=c.id,
                                  sucursal="bilbao", activo=True, password_hash=auth.hash_password("1111")))
            db.commit()
            ini = datos_arranque.parsear(
                "R.S.: Astilleros Murueta S.L.\n Cod.: MUR\n Cif : B77777777\n"
                " sucursal admin -> Murueta\n sucursal -> Bilbao\n sucursal -> Madrid\n")
            # sin --renombrar: se omite el cliente entero, como siempre
            r = datos_arranque.cargar(db, ini, auth.hash_password("1111"), solo_los_que_faltan=True)
            assert r["clientes_omitidos"] and not r["usuarios_renombrados"]
            r = datos_arranque.cargar(db, ini, auth.hash_password("1111"), solo_los_que_faltan=True, renombrar=True)
            assert sorted(r["usuarios_renombrados"]) == ["bilbao -> mur-bilbao", "murueta -> mur-admin"]
            assert r["usuarios_nuevos"] == ["mur-madrid"]
            db.expire_all()
            assert db.query(models.Cliente).filter_by(cif="B77777777").one().codigo == "MUR"
            # idempotente
            r2 = datos_arranque.cargar(db, ini, auth.hash_password("1111"), solo_los_que_faltan=True, renombrar=True)
            assert not r2["usuarios_renombrados"] and not r2["usuarios_nuevos"]
        finally:
            db.close()
        assert login(client, "mur-bilbao", "1111")

    def test_los_clientes_sin_codigo_de_una_base_antigua_reciben_uno(self, client):
        db = SessionLocal()
        try:
            db.add(models.Cliente(razon_social="Cliente Antiguo S.L.", activo=True))
            db.commit()
            asignados = codigos.asignar_faltantes(db)
            assert asignados == ["Cliente Antiguo S.L. -> CLI"]
            assert codigos.asignar_faltantes(db) == []
        finally:
            db.close()
