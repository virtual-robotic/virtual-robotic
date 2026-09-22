# Version: 2026-09-21 18:22 -- codigo de cliente (3 caracteres) y nombres de usuario que salen de el
"""Cada cliente tiene un CODIGO corto de 3 letras o cifras (MUR, ERE, IRA...), como el de los
productos. El usuario de una sucursal se forma con ese codigo:

    <codigo>-admin        el administrador de la empresa       mur-admin
    <codigo>-<sucursal>   un usuario de una sucursal           mur-bilbao

Asi dos clientes pueden tener cada uno su sucursal 'Bilbao' (mur-bilbao, ere-bilbao) sin
inventarse nombres como 'ereno3', y el usuario dice de un vistazo de que cliente viene un pedido."""
import re
import unicodedata

FORMATO_CODIGO = re.compile(r"^[A-Z0-9]{3}$")
# Palabras que no dicen nada de la empresa: no sirven para sacar el codigo.
PALABRAS_VACIAS = {"s", "l", "a", "u", "sl", "sa", "slu", "sc", "sll", "cb", "y", "de", "del", "la", "las", "el", "los", "e", "en"}


class ErrorCodigo(ValueError):
    pass


def _sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def normalizar_codigo(texto: str) -> str:
    """'mur' -> 'MUR'. Lanza ErrorCodigo si no son 3 letras o cifras."""
    codigo = _sin_acentos((texto or "").strip()).upper()
    if not FORMATO_CODIGO.match(codigo):
        raise ErrorCodigo(f"El codigo de cliente '{texto}' no vale: son 3 letras o cifras (por ejemplo MUR).")
    return codigo


def _palabras(razon_social: str) -> list[str]:
    limpio = re.sub(r"[^A-Za-z0-9 ]", " ", _sin_acentos(razon_social))
    palabras = [p for p in limpio.split() if p.lower() not in PALABRAS_VACIAS]
    return [p.upper() for p in palabras if any(c.isalnum() for c in p)]


def sugerir_codigo(razon_social: str, ocupados: set[str]) -> str:
    """Un codigo libre sacado de la razon social: las 3 primeras letras de su primera palabra con
    significado ('Suministros Ereno S.A.' -> SUM); si esta cogido, las de la siguiente palabra
    (ERE); si no, se cambia la ultima letra por una cifra."""
    palabras = _palabras(razon_social) or ["CLI"]
    candidatos = [p[:3].ljust(3, "X") for p in palabras]
    base = candidatos[0]
    candidatos += [base[:2] + str(n) for n in range(1, 10)]
    candidatos += [base[:1] + f"{n:02d}" for n in range(1, 100)]
    for c in candidatos:
        if c not in ocupados:
            return c
    raise ErrorCodigo(f"No he podido sacar un codigo libre para '{razon_social}'.")


def slug(texto: str) -> str:
    """'A Coruna' -> 'a-coruna'; 'Ereño' -> 'ereno'."""
    return re.sub(r"[^a-z0-9]+", "-", _sin_acentos(texto or "").lower()).strip("-")


def usuario_de(codigo: str, sucursal: str | None, es_admin: bool) -> str:
    """El nombre de usuario que toca a un usuario de esa sucursal."""
    parte = "admin" if es_admin else slug(sucursal or "")
    if not parte:
        raise ErrorCodigo("Para formar el usuario hace falta la sucursal.")
    return f"{codigo.lower()}-{parte}"


def asignar_faltantes(db) -> list[str]:
    """Da un codigo a los clientes que aun no lo tienen (bases anteriores a este cambio) y se
    asegura de que no haya dos iguales. Devuelve los que ha asignado ('Razon -> COD')."""
    from . import models  # aqui y no arriba: el modulo se prueba sin base de datos

    clientes = db.query(models.Cliente).order_by(models.Cliente.id).all()
    ocupados = {c.codigo for c in clientes if c.codigo}
    asignados = []
    for c in clientes:
        if c.codigo:
            continue
        c.codigo = sugerir_codigo(c.razon_social, ocupados)
        ocupados.add(c.codigo)
        asignados.append(f"{c.razon_social} -> {c.codigo}")
    if asignados:
        db.commit()
    return asignados
