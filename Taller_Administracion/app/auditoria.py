# Version: 2026-09-19 11:17 -- auditoria compartida (antes _audit vivia solo en main.py)
"""Registro de auditoria: quien hizo que y cuando. Vive aqui, no en main.py,
para que los routers (facturacion.py) lo usen sin importar main (circular)."""
from sqlalchemy.orm import Session

from . import models


def audit(
    db: Session,
    tabla: str,
    registro_id: int,
    accion: str,
    usuario_id: int | None,
    detalle: str | None = None,
) -> None:
    db.add(
        models.AuditLog(
            tabla=tabla,
            registro_id=registro_id,
            accion=accion,
            usuario_id=usuario_id,
            detalle=detalle,
        )
    )
    db.commit()
