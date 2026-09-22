# Version: 2026-09-20 11:00 -- contabilidad: precio propio de paquete, emisores, tarifas, historial de precios, correccion de precios y facturas
"""Control de precios y facturacion (sesion 2026-09-19).

Como se controla un precio, de origen a factura:
  1. TARIFA: Subproducto.precio_centimos (general) o TarifaCliente (especial).
  2. PEDIDO: al crearlo se COPIA la tarifa que le toca y su origen
     (tarifa_general / tarifa_cliente / manual). Cambiar la tarifa despues no lo toca.
  3. ALBARAN: al entregar se copia el precio del pedido a cada linea.
  4. FACTURA: agrupa albaranes SIN facturar de un cliente y copia lineas y datos fiscales.
Cada cambio de precio deja una fila en HistorialPrecio (quien, cuando, de-a, por que).
Una correccion despues de emitir la factura se hace con una RECTIFICATIVA, nunca
editando la factura; la rectificativa libera los albaranes para volver a facturarse."""
import datetime
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import auth, importes, models, schemas
from .auditoria import audit
from .database import get_db

router = APIRouter()

ADMIN = auth.ROL_ADMIN_SISTEMA


def validar_precio_iva(precio_centimos: int, iva_porcentaje: int) -> None:
    if precio_centimos < 0:
        raise HTTPException(400, "El precio no puede ser negativo.")
    if not 0 <= iva_porcentaje <= 100:
        raise HTTPException(400, "El IVA tiene que estar entre 0 y 100.")


def registrar_precio(db: Session, *, tipo, usuario_id, subproducto_id=None, paquete_id=None, motivo=None,
                     cliente_id=None, pedido_id=None, reparto_linea_id=None, precio_anterior=None,
                     precio_nuevo=None, iva_anterior=None, iva_nuevo=None) -> None:
    """Una fila en el libro de precios. No hace commit: va en la misma
    transaccion que el cambio que registra, para que no puedan separarse."""
    db.add(models.HistorialPrecio(
        tipo=tipo, subproducto_id=subproducto_id, paquete_id=paquete_id, cliente_id=cliente_id, pedido_id=pedido_id,
        reparto_linea_id=reparto_linea_id, precio_anterior_centimos=precio_anterior,
        precio_nuevo_centimos=precio_nuevo, iva_anterior=iva_anterior, iva_nuevo=iva_nuevo,
        motivo=motivo, usuario_id=usuario_id,
    ))


def precio_para(db: Session, cliente_id: int, subproducto: models.Subproducto) -> tuple[int, str]:
    """(precio, origen) que le toca a este cliente en este subproducto HOY."""
    tarifa = db.get(models.TarifaCliente, (cliente_id, subproducto.id))
    if tarifa is not None:
        return tarifa.precio_centimos, "tarifa_cliente"
    return subproducto.precio_centimos, "tarifa_general"


def precio_para_paquete(db: Session, cliente_id: int, paquete: models.Paquete) -> tuple[int | None, str | None]:
    """(precio de UN paquete, origen) que le toca a este cliente HOY. (None, None) = el paquete no
    tiene precio propio: sus componentes se cobran cada uno a su tarifa."""
    tarifa = db.get(models.TarifaClientePaquete, (cliente_id, paquete.id))
    if tarifa is not None:
        return tarifa.precio_centimos, "paquete_cliente"
    if paquete.precio_centimos is not None:
        return paquete.precio_centimos, "paquete_general"
    return None, None


# ------------------------------------------------------------------ tarifas


def _cliente_o_404(db: Session, cliente_id: int) -> models.Cliente:
    cliente = db.get(models.Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(404, "Cliente no encontrado.")
    return cliente


@router.get("/clientes/{cliente_id}/tarifas", response_model=list[schemas.TarifaClienteOut])
def listar_tarifas(
    cliente_id: int,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN, auth.ROL_ADMIN_CLIENTE)),
    db: Session = Depends(get_db),
):
    if usuario.rol == auth.ROL_ADMIN_CLIENTE and usuario.cliente_id != cliente_id:
        raise HTTPException(403, "No tienes permiso para ver las tarifas de otro cliente.")
    return db.query(models.TarifaCliente).filter_by(cliente_id=cliente_id).all()


@router.put("/clientes/{cliente_id}/tarifas/{subproducto_id}", response_model=schemas.TarifaClienteOut)
def fijar_tarifa(
    cliente_id: int,
    subproducto_id: int,
    payload: schemas.TarifaClienteIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Precio especial para este cliente. Solo vale para pedidos NUEVOS."""
    _cliente_o_404(db, cliente_id)
    subproducto = db.get(models.Subproducto, subproducto_id)
    if subproducto is None:
        raise HTTPException(404, "Subproducto no encontrado.")
    validar_precio_iva(payload.precio_centimos, subproducto.iva_porcentaje)
    tarifa = db.get(models.TarifaCliente, (cliente_id, subproducto_id))
    anterior = tarifa.precio_centimos if tarifa else None
    if tarifa is None:
        tarifa = models.TarifaCliente(cliente_id=cliente_id, subproducto_id=subproducto_id,
                                      precio_centimos=payload.precio_centimos)
        db.add(tarifa)
    else:
        tarifa.precio_centimos = payload.precio_centimos
    tarifa.actualizado_en = datetime.datetime.utcnow()
    tarifa.actualizado_por_id = usuario.id
    if anterior != payload.precio_centimos:
        registrar_precio(db, tipo="tarifa_cliente", subproducto_id=subproducto_id, cliente_id=cliente_id,
                         usuario_id=usuario.id, precio_anterior=anterior, precio_nuevo=payload.precio_centimos)
    db.commit()
    db.refresh(tarifa)
    audit(db, "tarifas_cliente", cliente_id, "modificacion", usuario.id,
          f"subproducto {subproducto_id}: {anterior} -> {payload.precio_centimos}")
    return tarifa


@router.delete("/clientes/{cliente_id}/tarifas/{subproducto_id}")
def quitar_tarifa(
    cliente_id: int,
    subproducto_id: int,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Vuelve a la tarifa general para ese cliente."""
    tarifa = db.get(models.TarifaCliente, (cliente_id, subproducto_id))
    if tarifa is None:
        raise HTTPException(404, "Ese cliente no tiene tarifa especial para ese subproducto.")
    registrar_precio(db, tipo="tarifa_cliente", subproducto_id=subproducto_id, cliente_id=cliente_id,
                     usuario_id=usuario.id, precio_anterior=tarifa.precio_centimos, precio_nuevo=None)
    db.delete(tarifa)
    db.commit()
    audit(db, "tarifas_cliente", cliente_id, "baja", usuario.id, f"subproducto {subproducto_id}")
    return {"ok": True}


@router.get("/historial_precios", response_model=list[schemas.HistorialPrecioOut])
def historial_precios(
    subproducto_id: int | None = None,
    cliente_id: int | None = None,
    limite: int = 200,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    query = db.query(models.HistorialPrecio)
    if subproducto_id is not None:
        query = query.filter(models.HistorialPrecio.subproducto_id == subproducto_id)  # los de paquete no llevan subproducto
    if cliente_id is not None:
        query = query.filter(models.HistorialPrecio.cliente_id == cliente_id)
    filas = query.order_by(models.HistorialPrecio.fecha.desc(), models.HistorialPrecio.id.desc()).limit(limite).all()
    for fila in filas:
        if fila.paquete is not None:
            fila.subproducto_descripcion = f"Paquete: {fila.paquete.nombre} ({fila.paquete.codigo})"
        elif fila.subproducto is not None:
            sub = fila.subproducto
            fila.subproducto_descripcion = f"{sub.producto.nombre} · {sub.nombre} ({sub.codigo_completo})"
        fila.cliente_razon_social = fila.cliente.razon_social if fila.cliente else None
    return filas


# ------------------------------------------------------ tarifas de paquete


@router.get("/clientes/{cliente_id}/tarifas_paquete", response_model=list[schemas.TarifaClientePaqueteOut])
def listar_tarifas_paquete(
    cliente_id: int,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN, auth.ROL_ADMIN_CLIENTE)),
    db: Session = Depends(get_db),
):
    if usuario.rol == auth.ROL_ADMIN_CLIENTE and usuario.cliente_id != cliente_id:
        raise HTTPException(403, "No tienes permiso para ver las tarifas de otro cliente.")
    return db.query(models.TarifaClientePaquete).filter_by(cliente_id=cliente_id).all()


@router.put("/clientes/{cliente_id}/tarifas_paquete/{paquete_id}", response_model=schemas.TarifaClientePaqueteOut)
def fijar_tarifa_paquete(
    cliente_id: int,
    paquete_id: int,
    payload: schemas.TarifaClienteIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Precio especial de UN paquete para este cliente. Solo vale para pedidos NUEVOS."""
    _cliente_o_404(db, cliente_id)
    paquete = db.get(models.Paquete, paquete_id)
    if paquete is None:
        raise HTTPException(404, "Paquete no encontrado.")
    validar_precio_iva(payload.precio_centimos, paquete.iva_porcentaje)
    tarifa = db.get(models.TarifaClientePaquete, (cliente_id, paquete_id))
    anterior = tarifa.precio_centimos if tarifa else None
    if tarifa is None:
        tarifa = models.TarifaClientePaquete(cliente_id=cliente_id, paquete_id=paquete_id,
                                             precio_centimos=payload.precio_centimos)
        db.add(tarifa)
    else:
        tarifa.precio_centimos = payload.precio_centimos
    tarifa.actualizado_en = datetime.datetime.utcnow()
    tarifa.actualizado_por_id = usuario.id
    if anterior != payload.precio_centimos:
        registrar_precio(db, tipo="paquete_cliente", paquete_id=paquete_id, cliente_id=cliente_id,
                         usuario_id=usuario.id, precio_anterior=anterior, precio_nuevo=payload.precio_centimos)
    db.commit()
    db.refresh(tarifa)
    audit(db, "tarifas_cliente_paquete", cliente_id, "modificacion", usuario.id,
          f"paquete {paquete_id}: {anterior} -> {payload.precio_centimos}")
    return tarifa


@router.delete("/clientes/{cliente_id}/tarifas_paquete/{paquete_id}")
def quitar_tarifa_paquete(
    cliente_id: int,
    paquete_id: int,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    tarifa = db.get(models.TarifaClientePaquete, (cliente_id, paquete_id))
    if tarifa is None:
        raise HTTPException(404, "Ese cliente no tiene tarifa especial para ese paquete.")
    registrar_precio(db, tipo="paquete_cliente", paquete_id=paquete_id, cliente_id=cliente_id,
                     usuario_id=usuario.id, precio_anterior=tarifa.precio_centimos, precio_nuevo=None)
    db.delete(tarifa)
    db.commit()
    audit(db, "tarifas_cliente_paquete", cliente_id, "baja", usuario.id, f"paquete {paquete_id}")
    return {"ok": True}


# ------------------------------------------------- correcciones de precio


@router.patch("/pedidos/{pedido_id}/precio")
def corregir_precio_pedido(
    pedido_id: int,
    payload: schemas.CorregirPrecio,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Corrige el precio de un pedido AUN NO ENTREGADO (lo ya entregado consta
    en albaranes: ahi se corrige con PATCH /repartos/lineas/{id}/precio)."""
    pedido = db.get(models.Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if pedido.estado in ("completado", "cancelado") or pedido.cantidad_repartida > 0:
        raise HTTPException(
            409,
            "Este pedido ya tiene piezas entregadas o esta cerrado: corrige el precio en las "
            "lineas de su albaran (si aun no esta facturado).",
        )
    if pedido.paquete_pedido is not None and pedido.paquete_pedido.precio_unitario_centimos is not None:
        raise HTTPException(
            409, "Este producto forma parte de un paquete con precio propio: el precio se corrige en el "
                 "pedido del paquete (PATCH /pedidos-paquete/{id}/precio), no en el producto.")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(400, "Indica el motivo del cambio de precio.")
    iva = pedido.iva_porcentaje if payload.iva_porcentaje is None else payload.iva_porcentaje
    validar_precio_iva(payload.precio_centimos, iva)
    registrar_precio(db, tipo="pedido", subproducto_id=pedido.subproducto_id, cliente_id=pedido.cliente_id,
                     pedido_id=pedido.id, usuario_id=usuario.id, motivo=motivo,
                     precio_anterior=pedido.precio_unitario_centimos, precio_nuevo=payload.precio_centimos,
                     iva_anterior=pedido.iva_porcentaje, iva_nuevo=iva)
    pedido.precio_unitario_centimos = payload.precio_centimos
    pedido.iva_porcentaje = iva
    pedido.precio_origen = "manual"
    db.commit()
    audit(db, "pedidos", pedido.id, "modificacion", usuario.id,
          f"precio -> {payload.precio_centimos} (IVA {iva}): {motivo}")
    return {"id": pedido.id, "precio_unitario_centimos": pedido.precio_unitario_centimos,
            "iva_porcentaje": pedido.iva_porcentaje, "precio_origen": pedido.precio_origen}


@router.patch("/pedidos-paquete/{pp_id}/precio")
def corregir_precio_pedido_paquete(
    pp_id: int,
    payload: schemas.CorregirPrecio,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Corrige el precio de UN paquete de un pedido AUN NO ENTREGADO (el paquete se entrega entero,
    asi que o esta sin entregar o su precio consta en un albaran)."""
    pp = db.get(models.PedidoPaquete, pp_id)
    if pp is None:
        raise HTTPException(404, "Pedido de paquete no encontrado.")
    if pp.cantidad_repartida > 0:
        raise HTTPException(409, "Este paquete ya esta entregado: corrige el precio en la linea de su albaran "
                                 "(si aun no esta facturado).")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(400, "Indica el motivo del cambio de precio.")
    iva = pp.iva_porcentaje if payload.iva_porcentaje is None else payload.iva_porcentaje
    validar_precio_iva(payload.precio_centimos, iva)
    registrar_precio(db, tipo="pedido_paquete", paquete_id=pp.paquete_id, cliente_id=pp.cliente_id,
                     usuario_id=usuario.id, motivo=motivo, precio_anterior=pp.precio_unitario_centimos,
                     precio_nuevo=payload.precio_centimos, iva_anterior=pp.iva_porcentaje, iva_nuevo=iva)
    pp.precio_unitario_centimos = payload.precio_centimos
    pp.iva_porcentaje = iva
    pp.precio_origen = "manual"
    for componente in pp.componentes:   # un paquete con precio propio: sus productos no llevan precio
        componente.precio_unitario_centimos = 0
        componente.iva_porcentaje = iva
        componente.precio_origen = "paquete"
    db.commit()
    audit(db, "pedidos_paquete", pp.id, "modificacion", usuario.id, f"precio -> {payload.precio_centimos}: {motivo}")
    return {"id": pp.id, "precio_unitario_centimos": pp.precio_unitario_centimos, "iva_porcentaje": pp.iva_porcentaje}


def _numeros_facturados(db: Session, reparto_ids: list[int]) -> dict[int, str]:
    """{reparto_id: numero de la factura VIGENTE que lo recoge}. Una factura
    anulada (con su rectificativa) libera el albaran."""
    if not reparto_ids:
        return {}
    filas = (
        db.query(models.RepartoLinea.reparto_id, models.Factura.numero)
        .join(models.FacturaLinea, models.FacturaLinea.reparto_linea_id == models.RepartoLinea.id)
        .join(models.Factura, models.Factura.id == models.FacturaLinea.factura_id)
        .filter(models.RepartoLinea.reparto_id.in_(reparto_ids))
        .filter(models.Factura.estado == "emitida", models.Factura.tipo == "factura")
        .all()
    )
    return {reparto_id: numero for reparto_id, numero in filas}


def con_factura(db: Session, repartos: list[models.Reparto]) -> list[models.Reparto]:
    """Rellena factura_numero (None = sin facturar) y los paquetes de cada albaran."""
    numeros = _numeros_facturados(db, [r.id for r in repartos])
    for reparto in repartos:
        reparto.factura_numero = numeros.get(reparto.id)
        reparto.paquetes = sorted({l.paquete_nombre for l in reparto.lineas if l.paquete_nombre})
    return repartos


@router.patch("/repartos/lineas/{linea_id}/precio")
def corregir_precio_linea_albaran(
    linea_id: int,
    payload: schemas.CorregirPrecio,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Corrige el precio de una linea de albaran que TODAVIA NO esta facturada
    (cantidad, pedido y fecha no se tocan nunca). Queda en el historial con el
    motivo. Ya facturada: se anula la factura con una rectificativa y se corrige."""
    linea = db.get(models.RepartoLinea, linea_id)
    if linea is None:
        raise HTTPException(404, "Linea de albaran no encontrada.")
    if linea.reparto_id in _numeros_facturados(db, [linea.reparto_id]):
        raise HTTPException(409, "Este albaran ya esta facturado: anula la factura (rectificativa) antes de corregir el precio.")
    if linea.tipo == "componente":
        raise HTTPException(400, "Las lineas de lo que lleva un paquete no llevan precio: corrige el de la linea del paquete.")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(400, "Indica el motivo del cambio de precio.")
    iva = linea.iva_porcentaje if payload.iva_porcentaje is None else payload.iva_porcentaje
    validar_precio_iva(payload.precio_centimos, iva)
    paquete_id = None
    if linea.tipo == "paquete" and linea.paquete_pedido_id:
        pp = db.get(models.PedidoPaquete, linea.paquete_pedido_id)
        paquete_id = pp.paquete_id if pp else None
    registrar_precio(db, tipo="albaran", subproducto_id=linea.subproducto_id, paquete_id=paquete_id,
                     cliente_id=linea.reparto.cliente_id, pedido_id=linea.pedido_id,
                     reparto_linea_id=linea.id, usuario_id=usuario.id, motivo=motivo,
                     precio_anterior=linea.precio_unitario_centimos, precio_nuevo=payload.precio_centimos,
                     iva_anterior=linea.iva_porcentaje, iva_nuevo=iva)
    linea.precio_unitario_centimos = payload.precio_centimos
    linea.iva_porcentaje = iva
    if linea.tipo == "paquete":   # el IVA del paquete es el de sus componentes informativos
        for hermana in linea.reparto.lineas:
            if hermana.tipo == "componente" and hermana.paquete_pedido_id == linea.paquete_pedido_id:
                hermana.iva_porcentaje = iva
    db.commit()
    audit(db, "reparto_lineas", linea.id, "modificacion", usuario.id,
          f"{linea.reparto.numero}: precio -> {payload.precio_centimos} (IVA {iva}): {motivo}")
    return {"id": linea.id, "precio_unitario_centimos": linea.precio_unitario_centimos,
            "iva_porcentaje": linea.iva_porcentaje}


# ---------------------------------------------------------------- emisores

SERIE_VALIDA = re.compile(r"^[A-Z0-9]{2,8}$")


def _emisor_out(db: Session, emisores: list[models.Emisor]) -> list[models.Emisor]:
    con = {f for (f,) in db.query(models.Factura.emisor_id).filter(models.Factura.emisor_id.isnot(None)).distinct()}
    for e in emisores:
        e.con_facturas = e.id in con
    return emisores


def _validar_series(db: Session, fac: str, rect: str, propio_id: int | None) -> tuple[str, str]:
    fac, rect = fac.strip().upper(), rect.strip().upper()
    for serie in (fac, rect):
        if not SERIE_VALIDA.match(serie):
            raise HTTPException(400, f"La serie '{serie}' no vale: entre 2 y 8 letras o numeros, sin espacios.")
    if fac == rect:
        raise HTTPException(400, "La serie de facturas y la de rectificativas tienen que ser distintas.")
    for otro in db.query(models.Emisor).filter(models.Emisor.id != (propio_id or 0)).all():
        if {fac, rect} & {otro.serie_facturas, otro.serie_rectificativas}:
            raise HTTPException(409, f"Esa serie ya la usa '{otro.razon_social}': cada empresa tiene su propia numeracion.")
    return fac, rect


def _datos_emisor(razon_social, cif, direccion) -> tuple[str, str, str]:
    datos = tuple((v or "").strip() for v in (razon_social, cif, direccion))
    if not all(datos):
        raise HTTPException(400, "Una empresa emisora necesita razon social, CIF y direccion.")
    return datos


@router.get("/emisores", response_model=list[schemas.EmisorOut])
def listar_emisores(
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    return _emisor_out(db, db.query(models.Emisor).order_by(models.Emisor.id).all())


@router.post("/emisores", response_model=schemas.EmisorOut)
def crear_emisor(
    payload: schemas.EmisorIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    razon, cif, direccion = _datos_emisor(payload.razon_social, payload.cif, payload.direccion)
    fac, rect = _validar_series(db, payload.serie_facturas, payload.serie_rectificativas, None)
    primero = db.query(models.Emisor).count() == 0
    if payload.por_defecto or primero:
        db.query(models.Emisor).update({"por_defecto": False})
    emisor = models.Emisor(razon_social=razon, cif=cif, direccion=direccion, email=(payload.email or "").strip() or None,
                           serie_facturas=fac, serie_rectificativas=rect,
                           por_defecto=payload.por_defecto or primero, activo=True)
    db.add(emisor)
    db.commit()
    db.refresh(emisor)
    audit(db, "emisores", emisor.id, "alta", usuario.id, f"{razon} ({cif}) series {fac}/{rect}")
    return _emisor_out(db, [emisor])[0]


@router.patch("/emisores/{emisor_id}", response_model=schemas.EmisorOut)
def modificar_emisor(
    emisor_id: int,
    payload: schemas.EmisorUpdate,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Cambiar los datos NO altera las facturas ya emitidas (llevan su copia). Las series
    no se pueden cambiar cuando ya hay facturas: se romperia la correlatividad."""
    emisor = db.get(models.Emisor, emisor_id)
    if emisor is None:
        raise HTTPException(404, "Empresa emisora no encontrada.")
    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    if {"razon_social", "cif", "direccion"} & cambios.keys():
        emisor.razon_social, emisor.cif, emisor.direccion = _datos_emisor(
            cambios.get("razon_social", emisor.razon_social), cambios.get("cif", emisor.cif),
            cambios.get("direccion", emisor.direccion))
    if "email" in cambios:
        emisor.email = (cambios["email"] or "").strip() or None
    if {"serie_facturas", "serie_rectificativas"} & cambios.keys():
        fac, rect = _validar_series(db, cambios.get("serie_facturas", emisor.serie_facturas),
                                    cambios.get("serie_rectificativas", emisor.serie_rectificativas), emisor.id)
        if (fac, rect) != (emisor.serie_facturas, emisor.serie_rectificativas):
            if _emisor_out(db, [emisor])[0].con_facturas:
                raise HTTPException(409, "Esta empresa ya ha emitido facturas: su numeracion (serie) no se puede cambiar.")
            emisor.serie_facturas, emisor.serie_rectificativas = fac, rect
    if cambios.get("por_defecto") is True:
        if emisor.activo is False or cambios.get("activo") is False:
            raise HTTPException(400, "Una empresa desactivada no puede ser la de por defecto.")
        db.query(models.Emisor).filter(models.Emisor.id != emisor.id).update({"por_defecto": False})
        emisor.por_defecto = True
    if "activo" in cambios:
        emisor.activo = cambios["activo"]
        if not emisor.activo and emisor.por_defecto:
            emisor.por_defecto = False
            otra = db.query(models.Emisor).filter(models.Emisor.id != emisor.id, models.Emisor.activo.is_(True)).first()
            if otra is not None:
                otra.por_defecto = True
    db.commit()
    db.refresh(emisor)
    audit(db, "emisores", emisor.id, "modificacion", usuario.id, str({k: v for k, v in cambios.items()}))
    return _emisor_out(db, [emisor])[0]


# ----------------------------------------------------------------- facturas


def _siguiente_numero(db: Session, serie: str, fecha: datetime.datetime) -> str:
    prefijo = f"{serie}-{fecha.year}-"
    ultimo = (
        db.query(func.max(models.Factura.numero))
        .filter(models.Factura.numero.like(f"{prefijo}%"))
        .scalar()
    )
    siguiente = int(ultimo.rsplit("-", 1)[1]) + 1 if ultimo else 1
    return f"{prefijo}{siguiente:06d}"


def _direccion_fiscal(cliente: models.Cliente) -> str:
    partes = [cliente.direccion or "", " ".join(x for x in (cliente.codigo_postal, cliente.poblacion) if x)]
    texto = ", ".join(p for p in partes if p)
    if cliente.provincia:
        texto += f" ({cliente.provincia})"
    return texto


def _facturas_out(db: Session, facturas: list[models.Factura]) -> list[models.Factura]:
    """Rellena importes y datos derivados (no se guardan: salen de las lineas)."""
    rectificativas = {}
    if facturas:
        for r in (db.query(models.Factura)
                  .filter(models.Factura.rectifica_id.in_([f.id for f in facturas])).all()):
            rectificativas[r.rectifica_id] = r.numero
    for f in facturas:
        for linea in f.lineas:
            linea.base_centimos = linea.cantidad * linea.precio_unitario_centimos
        calculo = importes.calcular(f.lineas)
        f.base_centimos, f.iva_centimos, f.total_centimos = calculo.base, calculo.iva, calculo.total
        f.desglose_iva = calculo.desglose
        f.cobrada = f.fecha_pago is not None
        f.albaranes = sorted({l.albaran_numero for l in f.lineas if l.albaran_numero})
        f.rectificada_por_numero = rectificativas.get(f.id)
        f.rectifica_numero = f.rectifica.numero if f.rectifica_id else None
    return facturas


# rectifica_numero necesita la relacion; se declara aqui para no ensuciar models.py
models.Factura.rectifica = models.relationship(
    "Factura", remote_side=[models.Factura.id], foreign_keys=[models.Factura.rectifica_id]
)


def _factura_o_404(db: Session, factura_id: int, usuario: models.Usuario) -> models.Factura:
    factura = db.get(models.Factura, factura_id)
    if factura is None:
        raise HTTPException(404, "Factura no encontrada.")
    if usuario.rol == auth.ROL_ADMIN_CLIENTE and factura.cliente_id != usuario.cliente_id:
        raise HTTPException(403, "No tienes permiso para ver esta factura.")
    return factura


@router.post("/facturas", response_model=schemas.FacturaOut)
def emitir_factura(
    payload: schemas.FacturarIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Una factura para UN cliente con sus albaranes aun sin facturar (todos, o
    los indicados). Exige datos fiscales, rechaza lineas sin precio salvo que se
    permitan, y copia lineas y datos del cliente: la factura ya no depende de nada."""
    cliente = _cliente_o_404(db, payload.cliente_id)
    if payload.emisor_id is not None:
        emisor = db.get(models.Emisor, payload.emisor_id)
        if emisor is None or not emisor.activo:
            raise HTTPException(400, "Esa empresa emisora no existe o esta desactivada.")
    else:
        emisor = db.query(models.Emisor).filter_by(por_defecto=True, activo=True).first()
        if emisor is None:
            raise HTTPException(400, "No hay ninguna empresa emisora por defecto: crea o activa una en "
                                     "Administracion > Empresas antes de facturar.")
    faltan = [n for n, v in (("CIF", cliente.cif), ("direccion", cliente.direccion)) if not (v or "").strip()]
    if faltan:
        raise HTTPException(400, f"Faltan datos fiscales de '{cliente.razon_social}' para facturar: "
                                 f"{', '.join(faltan)} (pestana Clientes).")
    query = db.query(models.Reparto).filter(models.Reparto.cliente_id == cliente.id)
    if payload.reparto_ids is not None:
        ids = set(payload.reparto_ids)
        query = query.filter(models.Reparto.id.in_(ids))
    repartos = query.order_by(models.Reparto.fecha, models.Reparto.id).all()
    if payload.reparto_ids is not None and {r.id for r in repartos} != ids:
        raise HTTPException(404, "Algun albaran no existe o no es de ese cliente.")
    ya = _numeros_facturados(db, [r.id for r in repartos])
    if payload.reparto_ids is not None and ya:
        por_id = {r.id: r.numero for r in repartos}
        raise HTTPException(409, "Ya facturado: " + ", ".join(f"{por_id[i]} (en {n})" for i, n in ya.items()))
    repartos = [r for r in repartos if r.id not in ya]
    if not repartos:
        raise HTTPException(400, "No hay albaranes pendientes de facturar para este cliente.")
    a_cero = [r.numero for r in repartos for l in r.lineas
              if l.precio_unitario_centimos == 0 and l.tipo != "componente"]
    if a_cero and not payload.permitir_lineas_a_cero:
        raise HTTPException(
            400, "Hay lineas sin precio (0 EUR) en: " + ", ".join(sorted(set(a_cero))) +
                 ". Corrige el precio de esas lineas antes de facturar (o confirma que son gratuitas).")
    ahora = datetime.datetime.utcnow()
    factura = models.Factura(
        numero=_siguiente_numero(db, emisor.serie_facturas, ahora), tipo="factura", estado="emitida",
        cliente_id=cliente.id, fecha=ahora, usuario_id=usuario.id, emisor_id=emisor.id,
        emisor_razon_social=emisor.razon_social, emisor_cif=emisor.cif,
        emisor_direccion=emisor.direccion, emisor_email=emisor.email,
        cliente_razon_social=cliente.razon_social,
        cliente_cif=cliente.cif.strip(), cliente_direccion=_direccion_fiscal(cliente),
        cliente_email=cliente.email_facturacion,
    )
    db.add(factura)
    db.flush()
    for reparto in repartos:
        for linea in reparto.lineas:
            db.add(models.FacturaLinea(
                factura_id=factura.id, reparto_linea_id=linea.id, albaran_numero=reparto.numero,
                tipo=linea.tipo, paquete_pedido_id=linea.paquete_pedido_id, paquete_nombre=linea.paquete_nombre,
                paquete_cantidad=linea.paquete_cantidad,
                descripcion=linea.descripcion, cantidad=linea.cantidad,
                precio_unitario_centimos=linea.precio_unitario_centimos, iva_porcentaje=linea.iva_porcentaje,
            ))
    db.commit()
    db.refresh(factura)
    audit(db, "facturas", factura.id, "alta", usuario.id,
          f"{factura.numero}: {', '.join(r.numero for r in repartos)}")
    return _facturas_out(db, [factura])[0]


@router.get("/facturas", response_model=list[schemas.FacturaOut])
def listar_facturas(
    cliente_id: int | None = None,
    limite: int = 200,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN, auth.ROL_ADMIN_CLIENTE)),
    db: Session = Depends(get_db),
):
    query = db.query(models.Factura)
    if usuario.rol == auth.ROL_ADMIN_CLIENTE:
        query = query.filter(models.Factura.cliente_id == usuario.cliente_id)
    elif cliente_id is not None:
        query = query.filter(models.Factura.cliente_id == cliente_id)
    facturas = query.order_by(models.Factura.fecha.desc(), models.Factura.id.desc()).limit(limite).all()
    return _facturas_out(db, facturas)


@router.get("/facturas/{factura_id}", response_model=schemas.FacturaOut)
def obtener_factura(
    factura_id: int,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN, auth.ROL_ADMIN_CLIENTE)),
    db: Session = Depends(get_db),
):
    return _facturas_out(db, [_factura_o_404(db, factura_id, usuario)])[0]


@router.post("/facturas/{factura_id}/pagar", response_model=schemas.FacturaOut)
def marcar_cobrada(
    factura_id: int,
    payload: schemas.PagoIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    factura = _factura_o_404(db, factura_id, usuario)
    if factura.tipo != "factura" or factura.estado != "emitida":
        raise HTTPException(409, "Solo se puede cobrar una factura emitida (no anulada ni rectificativa).")
    if factura.fecha_pago is not None:
        raise HTTPException(409, "Esta factura ya esta cobrada.")
    factura.fecha_pago = datetime.datetime.utcnow()
    factura.metodo_pago = (payload.metodo_pago or "").strip() or None
    db.commit()
    audit(db, "facturas", factura.id, "modificacion", usuario.id,
          f"{factura.numero} cobrada ({factura.metodo_pago or 'sin metodo'})")
    return _facturas_out(db, [factura])[0]


@router.post("/facturas/{factura_id}/anular", response_model=schemas.FacturaOut)
def anular_factura(
    factura_id: int,
    payload: schemas.AnularIn,
    usuario: models.Usuario = Depends(auth.require_roles(ADMIN)),
    db: Session = Depends(get_db),
):
    """Anula una factura emitiendo su RECTIFICATIVA (mismas lineas, cantidades
    negativas, serie RECT). La original queda 'anulada' -- nunca se borra ni se
    edita -- y sus albaranes quedan libres para facturarse de nuevo."""
    original = _factura_o_404(db, factura_id, usuario)
    if original.tipo != "factura" or original.estado != "emitida":
        raise HTTPException(409, "Solo se puede anular una factura emitida (no una rectificativa ni una ya anulada).")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(400, "Indica el motivo de la rectificacion.")
    ahora = datetime.datetime.utcnow()
    emisor = db.get(models.Emisor, original.emisor_id) if original.emisor_id else None
    rectificativa = models.Factura(
        numero=_siguiente_numero(db, emisor.serie_rectificativas if emisor else "RECT", ahora),
        tipo="rectificativa", estado="emitida", emisor_id=original.emisor_id,
        cliente_id=original.cliente_id, rectifica_id=original.id, motivo=motivo, fecha=ahora,
        usuario_id=usuario.id, emisor_razon_social=original.emisor_razon_social,
        emisor_cif=original.emisor_cif, emisor_direccion=original.emisor_direccion,
        emisor_email=original.emisor_email, cliente_razon_social=original.cliente_razon_social,
        cliente_cif=original.cliente_cif, cliente_direccion=original.cliente_direccion,
        cliente_email=original.cliente_email,
    )
    db.add(rectificativa)
    db.flush()
    for linea in original.lineas:
        db.add(models.FacturaLinea(
            factura_id=rectificativa.id, reparto_linea_id=None, albaran_numero=linea.albaran_numero,
            tipo=linea.tipo, paquete_pedido_id=linea.paquete_pedido_id, paquete_nombre=linea.paquete_nombre,
            paquete_cantidad=(-linea.paquete_cantidad if linea.paquete_cantidad else linea.paquete_cantidad),
            descripcion=linea.descripcion, cantidad=-linea.cantidad,
            precio_unitario_centimos=linea.precio_unitario_centimos, iva_porcentaje=linea.iva_porcentaje,
        ))
    original.estado = "anulada"
    db.commit()
    db.refresh(rectificativa)
    audit(db, "facturas", original.id, "baja", usuario.id, f"{original.numero} anulada por {rectificativa.numero}: {motivo}")
    return _facturas_out(db, [rectificativa])[0]
