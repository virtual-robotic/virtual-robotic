# Version: 2026-09-21 18:22 -- carga a mano el fichero de clientes y usuarios iniciales en una base que YA tiene datos (--renombrar)
"""    docker exec taller_admin_api python -m app.cargar_arranque [--fichero RUTA] [--renombrar]

Anade los clientes y usuarios del fichero (por defecto Documentacion/UsuariosBBDDArranque.txt)
que falten en la base actual, SIN borrar ni cambiar nada: un cliente con el mismo CIF o un
usuario con el mismo nombre se omite y se lista. Pensado para una base en produccion, donde
el arranque automatico (solo para bases vacias) no aplica. Los usuarios nuevos nacen con la
contrasena inicial (TALLER_PASSWORD_INICIAL, por defecto 1111).

Con --renombrar, los clientes que ya existen (mismo CIF) reciben el codigo del fichero y sus
usuarios de la misma sucursal y rol pasan a llamarse como pide el fichero (murueta -> mur-admin);
los pedidos y albaranes no se tocan. Sirve para pasar una base antigua a los usuarios por codigo."""
import argparse
from pathlib import Path

from . import auth, datos_arranque
from .database import SessionLocal
from .main import PASSWORD_INICIAL, REPO_DIR


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fichero", type=Path, default=None)
    ap.add_argument("--renombrar", action="store_true",
                    help="pasa los usuarios existentes al nombre que sale del codigo de su cliente")
    args = ap.parse_args()
    ruta = args.fichero or datos_arranque.ruta_por_defecto(REPO_DIR)
    iniciales = datos_arranque.leer(ruta)
    if iniciales is None:
        print(f"No existe el fichero: {ruta}")
        return 1
    db = SessionLocal()
    try:
        r = datos_arranque.cargar(db, iniciales, auth.hash_password(PASSWORD_INICIAL), solo_los_que_faltan=True, renombrar=args.renombrar)
    finally:
        db.close()
    print(f"Fichero: {ruta}")
    for titulo, clave in (("Clientes nuevos", "clientes_nuevos"), ("Clientes omitidos", "clientes_omitidos"),
                          ("Usuarios nuevos", "usuarios_nuevos"), ("Usuarios omitidos", "usuarios_omitidos"),
                          ("Usuarios renombrados", "usuarios_renombrados"), ("Avisos", "avisos")):
        print(f"{titulo}: {len(r[clave])}" + ("  -> " + ", ".join(r[clave]) if r[clave] else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
