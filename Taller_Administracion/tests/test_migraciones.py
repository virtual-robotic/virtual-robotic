# Version: 2026-09-19 11:19 -- tests de la migracion de columnas nuevas
"""migrar_columnas_faltantes: una base creada con un modelo ANTERIOR (tabla sin
las columnas nuevas) se pone al dia sin perder los datos que ya tenia."""
from sqlalchemy import create_engine, inspect, text

from app import models
from app.migraciones import migrar_columnas_faltantes


def _base_vieja(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'vieja.db'}")
    with engine.begin() as c:
        # 'pedidos' tal como era antes de la fase de reparto: sin cantidad_repartida,
        # precio_unitario_centimos, iva_porcentaje ni precio_origen.
        c.execute(text(
            "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, subproducto_id INTEGER NOT NULL, "
            "producto_id INTEGER NOT NULL, paquete_origen_id INTEGER, cliente_id INTEGER NOT NULL, "
            "usuario_id INTEGER NOT NULL, cantidad_pedida INTEGER NOT NULL, "
            "cantidad_completada INTEGER NOT NULL, estado VARCHAR NOT NULL, urgente BOOLEAN NOT NULL, "
            "numero_maquina INTEGER NOT NULL, creado_en DATETIME)"
        ))
        c.execute(text(
            "INSERT INTO pedidos (subproducto_id, producto_id, cliente_id, usuario_id, cantidad_pedida, "
            "cantidad_completada, estado, urgente, numero_maquina) VALUES (1,1,1,1,5,2,'en_proceso',0,33)"
        ))
    return engine


def test_anade_las_columnas_que_faltan_con_su_valor_por_defecto_y_conserva_los_datos(tmp_path):
    engine = _base_vieja(tmp_path)
    anadidas = migrar_columnas_faltantes(engine, models.Base)
    assert {"pedidos.cantidad_repartida", "pedidos.precio_unitario_centimos",
            "pedidos.iva_porcentaje", "pedidos.precio_origen"} <= set(anadidas)
    columnas = {c["name"] for c in inspect(engine).get_columns("pedidos")}
    assert "cantidad_repartida" in columnas
    with engine.connect() as c:
        fila = c.execute(text(
            "SELECT cantidad_pedida, cantidad_completada, numero_maquina, cantidad_repartida, "
            "precio_unitario_centimos, iva_porcentaje, precio_origen FROM pedidos"
        )).one()
    assert tuple(fila) == (5, 2, 33, 0, 0, 21, "tarifa_general")


def test_es_idempotente(tmp_path):
    engine = _base_vieja(tmp_path)
    migrar_columnas_faltantes(engine, models.Base)
    assert migrar_columnas_faltantes(engine, models.Base) == []


def test_no_toca_las_tablas_que_no_existen(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'vacia.db'}")
    assert migrar_columnas_faltantes(engine, models.Base) == []
    assert not inspect(engine).has_table("pedidos")  # las crea create_all, no esto


def test_avisa_de_una_columna_que_el_modelo_admite_null_pero_la_base_tiene_not_null(tmp_path, caplog):
    """Caso real: historial_precios.subproducto_id era NOT NULL y un precio de paquete no lo lleva."""
    import logging
    engine = create_engine(f"sqlite:///{tmp_path / 'vieja2.db'}")
    with engine.begin() as c:
        c.execute(text(
            "CREATE TABLE historial_precios (id INTEGER PRIMARY KEY, tipo VARCHAR NOT NULL, "
            "subproducto_id INTEGER NOT NULL, fecha DATETIME NOT NULL)"))
    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        migrar_columnas_faltantes(engine, models.Base)
    assert any("historial_precios.subproducto_id" in r.getMessage() for r in caplog.records)
