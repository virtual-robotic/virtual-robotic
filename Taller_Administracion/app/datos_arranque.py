# Version: 2026-09-21 18:22 -- codigo de cliente y usuarios generados; lee y CARGA Documentacion/UsuariosBBDDArranque.txt (clientes y usuarios iniciales)
"""Clientes y usuarios con los que arranca una base de datos VACIA.

Se leen de un fichero de texto que se edita a mano (por defecto
Documentacion/UsuariosBBDDArranque.txt, o el de TALLER_DATOS_ARRANQUE):

    Cliente:
        R.S.: Astilleros Murueta S.L.        <- razon social; empieza un cliente nuevo
        Cif : B48111222
        Dir.: Carretera Bermeo 34
        C.P.: 48333
        Pob.: Murueta
        Pro.: Bizkaia
        cor.: administracion@example.com
        Productos: 100, 200                  <- OPCIONAL: codigos o nombres; sin la linea, TODOS
        Cod.: MUR                            <- OPCIONAL: 3 letras/cifras; sin ella se saca de la razon social
            sucursal admin -> Murueta        <- usuario mur-admin   (sale del codigo: no se escribe)
            sucursal -> Bilbao   nombre -> Ana Lopez   <- usuario mur-bilbao; nombre OPCIONAL
            user normal-> bilbao2   sucursal -> Bilbao   <- forma antigua, con el usuario escrito a mano (sigue valiendo)

Lo demas (titulo, 'Admin -> Admin.sistema', 'Cliente:', lineas vacias o con #) se
ignora. Un error se dice con su numero de linea y PARA el arranque: mejor eso que
cargar a medias unos clientes que luego no se sabe por que faltan.

Nombre completo de un usuario sin 'nombre ->': 'Administrador <sucursal>' si es
admin y 'Operario <sucursal>' si es normal. Ver app/codigos.py."""
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import func

from . import codigos

ETIQUETAS = {
    "r.s.": "razon_social",
    "cif": "cif",
    "dir.": "direccion",
    "c.p.": "codigo_postal",
    "pob.": "poblacion",
    "pro.": "provincia",
    "cor.": "email_facturacion",
    "cod.": "codigo",
    "productos": "productos",
}
LINEA_ETIQUETA = re.compile(r"^([A-Za-z.]+)\s*:\s*(.*)$")
LINEA_USUARIO = re.compile(
    r"^user\s+(admin|normal)\s*->\s*(\S+)\s+sucursal\s*->\s*(.+?)(?:\s+nombre\s*->\s*(.+))?$", re.IGNORECASE
)


# 'sucursal admin -> Murueta' / 'sucursal -> Bilbao   nombre -> Ana': el usuario se forma con el codigo del cliente.
LINEA_SUCURSAL = re.compile(r"^sucursal(?:\s+(admin))?\s*->\s*(.+?)(?:\s+nombre\s*->\s*(.+))?$", re.IGNORECASE)


class ErrorDatosArranque(ValueError):
    pass


@dataclass
class UsuarioInicial:
    username: str  # "" = se forma con el codigo del cliente y la sucursal (al terminar de leer)
    rol: str  # admin_cliente | normal
    sucursal: str
    nombre_completo: str
    linea: int = 0


@dataclass
class ClienteInicial:
    razon_social: str
    codigo: str = ""
    cif: str = ""
    direccion: str = ""
    codigo_postal: str = ""
    poblacion: str = ""
    provincia: str = ""
    email_facturacion: str = ""
    productos: list[str] | None = None  # None = todos
    usuarios: list[UsuarioInicial] = field(default_factory=list)

    def datos_fiscales(self) -> dict:
        return {c: (getattr(self, c) or None) for c in
                ("direccion", "codigo_postal", "poblacion", "provincia", "email_facturacion")}


def _sucursal(texto: str) -> str:
    texto = texto.strip()
    return texto.capitalize() if texto.islower() else texto  # 'bilbao' -> 'Bilbao'; respeta 'A Coruna'


def _completar_codigos_y_usuarios(clientes: list["ClienteInicial"], vistos: dict[str, int]) -> None:
    """Valida los codigos de cliente (3 letras/cifras, sin repetir), da uno a los que no lo traen y
    forma el usuario de los que no lo llevan escrito (<codigo>-admin, <codigo>-<sucursal>)."""
    ocupados: dict[str, str] = {}
    for c in clientes:
        if not c.codigo:
            continue
        try:
            c.codigo = codigos.normalizar_codigo(c.codigo)
        except codigos.ErrorCodigo as e:
            raise ErrorDatosArranque(f"Cliente '{c.razon_social}': {e}")
        if c.codigo in ocupados:
            raise ErrorDatosArranque(f"El codigo '{c.codigo}' esta en dos clientes: '{ocupados[c.codigo]}' y '{c.razon_social}'.")
        ocupados[c.codigo] = c.razon_social
    for c in clientes:
        if not c.codigo:
            c.codigo = codigos.sugerir_codigo(c.razon_social, set(ocupados))
            ocupados[c.codigo] = c.razon_social
    for c in clientes:
        for u in c.usuarios:
            if u.username:
                continue
            try:
                u.username = codigos.usuario_de(c.codigo, u.sucursal, u.rol == "admin_cliente")
            except codigos.ErrorCodigo as e:
                raise ErrorDatosArranque(f"Linea {u.linea}: {e}")
            if u.username in vistos:
                raise ErrorDatosArranque(
                    f"Linea {u.linea}: el usuario '{u.username}' esta repetido (ya salia en la linea {vistos[u.username]}).")
            vistos[u.username] = u.linea


def parsear(texto: str) -> list[ClienteInicial]:
    clientes: list[ClienteInicial] = []
    vistos: dict[str, int] = {}
    actual: ClienteInicial | None = None
    for n, cruda in enumerate(texto.splitlines(), start=1):
        linea = cruda.strip()
        if not linea or linea.startswith("#"):
            continue
        m_suc = LINEA_SUCURSAL.match(linea)
        if m_suc:
            if actual is None:
                raise ErrorDatosArranque(f"Linea {n}: una sucursal antes de ningun cliente ('R.S.: ...').")
            tipo, sucursal, nombre = m_suc.groups()
            rol = "admin_cliente" if tipo else "normal"
            sucursal = _sucursal(sucursal)
            if not nombre:
                nombre = f"{'Administrador' if rol == 'admin_cliente' else 'Operario'} {sucursal}"
            actual.usuarios.append(UsuarioInicial("", rol, sucursal, nombre.strip(), n))
            continue
        m_user = LINEA_USUARIO.match(linea)
        if m_user:
            if actual is None:
                raise ErrorDatosArranque(f"Linea {n}: un usuario antes de ningun cliente ('R.S.: ...').")
            tipo, username, sucursal, nombre = m_user.groups()
            username = username.strip().lower()
            if username in vistos:
                raise ErrorDatosArranque(f"Linea {n}: el usuario '{username}' esta repetido (ya salia en la linea {vistos[username]}).")
            vistos[username] = n
            rol = "admin_cliente" if tipo.lower() == "admin" else "normal"
            sucursal = _sucursal(sucursal)
            if not nombre:
                nombre = f"{'Administrador' if rol == 'admin_cliente' else 'Operario'} {sucursal}"
            actual.usuarios.append(UsuarioInicial(username, rol, sucursal, nombre.strip(), n))
            continue
        m = LINEA_ETIQUETA.match(linea)
        if m and m.group(1).lower() in ETIQUETAS:
            campo, valor = ETIQUETAS[m.group(1).lower()], m.group(2).strip()
            if campo == "razon_social":
                if not valor:
                    raise ErrorDatosArranque(f"Linea {n}: 'R.S.:' sin razon social.")
                actual = ClienteInicial(razon_social=valor)
                clientes.append(actual)
            elif actual is None:
                raise ErrorDatosArranque(f"Linea {n}: '{m.group(1)}' antes de ningun cliente ('R.S.: ...').")
            elif campo == "productos":
                actual.productos = [p.strip() for p in valor.split(",") if p.strip()]
            else:
                setattr(actual, campo, valor)
            continue
        # cualquier otra cosa (titulo, 'Cliente:', 'Admin -> Admin.sistema'...) se ignora
    _completar_codigos_y_usuarios(clientes, vistos)
    for c in clientes:
        if not c.usuarios:
            raise ErrorDatosArranque(f"El cliente '{c.razon_social}' no tiene ningun usuario.")
        if not any(u.rol == "admin_cliente" for u in c.usuarios):
            raise ErrorDatosArranque(f"El cliente '{c.razon_social}' no tiene ningun 'user admin' (hace falta uno para gestionar la empresa).")
    return clientes


def ruta_por_defecto(repo_dir: Path) -> Path:
    return Path(os.environ.get("TALLER_DATOS_ARRANQUE") or (repo_dir / "Documentacion" / "UsuariosBBDDArranque.txt"))


def leer(ruta: Path) -> list[ClienteInicial] | None:
    """None si el fichero no existe (se usan los clientes de ejemplo del codigo)."""
    if not ruta.is_file():
        return None
    return parsear(ruta.read_text(encoding="utf-8"))


def productos_de(inicial: ClienteInicial, productos: list) -> list:
    """Productos que puede pedir un cliente inicial: todos, o los de su linea 'Productos:'
    (por codigo o por nombre)."""
    if inicial.productos is None:
        return productos
    elegidos = []
    for pedido in inicial.productos:
        clave = pedido.strip().lower()
        encontrado = next((p for p in productos if clave in (p.codigo.lower(), p.nombre.lower())), None)
        if encontrado is None:
            raise ErrorDatosArranque(
                f"'{inicial.razon_social}': el producto '{pedido}' no existe (codigos: "
                f"{', '.join(p.codigo for p in productos)}).")
        elegidos.append(encontrado)
    return elegidos


def cargar(db, iniciales: list[ClienteInicial], password_hash: str, solo_los_que_faltan: bool = False,
           renombrar: bool = False) -> dict:
    """Crea clientes, usuarios y catalogo. Con solo_los_que_faltan=True (base que YA tiene
    datos) no toca nada existente: un cliente con el mismo CIF o un usuario con el mismo
    nombre se OMITE y se cuenta en el resumen, en vez de duplicarlo o pisarlo.

    Con renombrar=True (solo tiene sentido junto a solo_los_que_faltan) un cliente que ya existe
    (mismo CIF) recibe el codigo del fichero y sus usuarios de la misma sucursal y rol pasan al
    nombre nuevo (murueta -> mur-admin); los que falten se crean. Es el paso de los usuarios
    antiguos a los que salen del codigo."""
    from . import models  # aqui y no arriba: el lector se prueba sin base de datos

    resumen = {"clientes_nuevos": [], "clientes_omitidos": [], "usuarios_nuevos": [], "usuarios_omitidos": [],
               "usuarios_renombrados": [], "avisos": []}
    productos = db.query(models.Producto).all()
    ocupados = {c for (c,) in db.query(models.Cliente.codigo).filter(models.Cliente.codigo.isnot(None)).all()}
    for ini in iniciales:
        cliente = None
        if solo_los_que_faltan and ini.cif:
            cliente = db.query(models.Cliente).filter(models.Cliente.cif == ini.cif).first()
        if cliente is not None and not renombrar:
            resumen["clientes_omitidos"].append(
                f"{ini.razon_social} (CIF {ini.cif} ya existe como '{cliente.razon_social}')")
            continue
        if cliente is not None:
            _poner_codigo(db, cliente, ini, ocupados, resumen)
            nombres_fichero = {x.username for x in ini.usuarios}
            for u in ini.usuarios:
                if db.query(models.Usuario).filter_by(username=u.username).first():
                    resumen["usuarios_omitidos"].append(f"{u.username} (ya existe)")
                    continue
                antiguo = (
                    db.query(models.Usuario)
                    .filter(models.Usuario.cliente_id == cliente.id, models.Usuario.rol == u.rol,
                            func.lower(models.Usuario.sucursal) == u.sucursal.lower(),
                            ~models.Usuario.username.in_(nombres_fichero))
                    .order_by(models.Usuario.id).first()
                )
                if antiguo is not None:
                    resumen["usuarios_renombrados"].append(f"{antiguo.username} -> {u.username}")
                    antiguo.username = u.username
                    continue
                db.add(models.Usuario(username=u.username, nombre_completo=u.nombre_completo, rol=u.rol,
                                      cliente_id=cliente.id, sucursal=u.sucursal, activo=True,
                                      password_hash=password_hash))
                resumen["usuarios_nuevos"].append(u.username)
            continue
        codigo = ini.codigo
        if not codigo or codigo in ocupados:
            sugerido = codigos.sugerir_codigo(ini.razon_social, ocupados)
            if codigo:
                resumen["avisos"].append(f"{ini.razon_social}: el codigo {codigo} ya es de otro cliente; uso {sugerido}")
            codigo = sugerido
        ocupados.add(codigo)
        cliente = models.Cliente(razon_social=ini.razon_social, codigo=codigo, cif=ini.cif or None, activo=True,
                                 **ini.datos_fiscales())
        db.add(cliente)
        db.flush()
        resumen["clientes_nuevos"].append(ini.razon_social)
        for u in ini.usuarios:
            if solo_los_que_faltan and db.query(models.Usuario).filter_by(username=u.username).first():
                resumen["usuarios_omitidos"].append(f"{u.username} (ya existe)")
                continue
            db.add(models.Usuario(username=u.username, nombre_completo=u.nombre_completo, rol=u.rol,
                                  cliente_id=cliente.id, sucursal=u.sucursal, activo=True, password_hash=password_hash))
            resumen["usuarios_nuevos"].append(u.username)
        for producto in productos_de(ini, productos):
            db.add(models.ClienteProducto(cliente_id=cliente.id, producto_id=producto.id))
    db.commit()
    return resumen


def _poner_codigo(db, cliente, ini: ClienteInicial, ocupados: set, resumen: dict) -> None:
    """Cliente que ya existe: si el fichero trae un codigo distinto y libre, se lo pone."""
    if not ini.codigo or cliente.codigo == ini.codigo:
        return
    if ini.codigo in ocupados:
        resumen["avisos"].append(f"{ini.razon_social}: el codigo {ini.codigo} ya es de otro cliente; se queda con {cliente.codigo}")
        return
    ocupados.discard(cliente.codigo)
    cliente.codigo = ini.codigo
    ocupados.add(ini.codigo)
    db.flush()
