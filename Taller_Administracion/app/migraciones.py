# Version: 2026-09-21 18:22 -- migracion minima: anade columnas nuevas y avisa de las que ya no admiten NULL en el modelo
"""No hay Alembic. create_all() crea las TABLAS que faltan pero nunca anade
columnas a una ya existente, asi que cada cambio del modelo obligaba a borrar
la base de datos. Esto cubre el caso comun (columnas NUEVAS): compara cada tabla
con el modelo y hace ALTER TABLE ... ADD COLUMN de las que faltan.

Limites, a proposito: solo ANADE columnas (no renombra, no cambia tipos, no
borra) y una columna NOT NULL necesita valor por defecto en el modelo (SQLite no
permite anadirla sin uno). Lo que no pueda hacer, lo dice en voz alta en vez de
fallar callado. Un cambio mas grande sigue pidiendo migracion a mano."""
import logging
import warnings

from sqlalchemy import inspect, text
from sqlalchemy.exc import SAWarning

log = logging.getLogger("uvicorn.error")


def _literal(valor):
    if isinstance(valor, bool):
        return str(int(valor))
    if isinstance(valor, (int, float)):
        return str(valor)
    return "'" + str(valor).replace("'", "''") + "'"


def _tablas(base):
    """Las tablas del modelo en orden. clientes y usuarios se referencian entre si (quien los creo),
    y SQLAlchemy avisa del ciclo cada vez: es a proposito y no cambia nada aqui."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SAWarning)
        return list(base.metadata.sorted_tables)


def migrar_columnas_faltantes(engine, base) -> list[str]:
    """Devuelve las columnas anadidas ('tabla.columna')."""
    anadidas = []
    inspector = inspect(engine)
    with engine.begin() as conn:
        for tabla in _tablas(base):
            if not inspector.has_table(tabla.name):
                continue  # la crea create_all
            existentes = {c["name"] for c in inspector.get_columns(tabla.name)}
            for col in tabla.columns:
                if col.name in existentes:
                    continue
                defecto = ""
                if col.default is not None and col.default.is_scalar:
                    defecto = f" DEFAULT {_literal(col.default.arg)}"
                if not col.nullable and not defecto:
                    log.warning(
                        "MIGRACION: %s.%s es NOT NULL y no tiene valor por defecto: "
                        "hay que anadirla a mano (o borrar la base de datos).",
                        tabla.name, col.name,
                    )
                    continue
                tipo = col.type.compile(engine.dialect)
                nulo = " NOT NULL" if not col.nullable else ""
                conn.execute(text(
                    f'ALTER TABLE "{tabla.name}" ADD COLUMN "{col.name}" {tipo}{nulo}{defecto}'
                ))
                anadidas.append(f"{tabla.name}.{col.name}")
    if anadidas:
        log.info("MIGRACION: columnas anadidas: %s", ", ".join(anadidas))
    _avisar_columnas_que_ahora_admiten_null(engine, base, inspector)
    return anadidas


def _avisar_columnas_que_ahora_admiten_null(engine, base, inspector) -> None:
    """SQLite no permite quitar un NOT NULL con ALTER: si el modelo pasa una columna a NULL-able
    y la base ya la tenia NOT NULL, los INSERT con NULL fallan. No se arregla sola: se avisa en el
    log (hay que recrear la base de datos, o rehacer esa tabla a mano)."""
    pendientes = []
    for tabla in _tablas(base):
        if not inspector.has_table(tabla.name):
            continue
        en_bd = {c["name"]: c for c in inspector.get_columns(tabla.name)}
        for col in tabla.columns:
            if col.nullable and col.name in en_bd and not en_bd[col.name]["nullable"] and not col.primary_key:
                pendientes.append(f"{tabla.name}.{col.name}")
    if pendientes:
        log.warning(
            "MIGRACION: estas columnas admiten NULL en el modelo pero la base las tiene NOT NULL "
            "(hay que recrear la base de datos para usar las funciones que las necesitan): %s",
            ", ".join(pendientes))
