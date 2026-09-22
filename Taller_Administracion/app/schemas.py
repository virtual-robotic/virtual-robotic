# Version: 2026-09-21 18:22 -- esquemas: codigo de cliente, usuario opcional; precio propio de paquete
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class ColorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    r: int
    g: int
    b: int
    fisico: bool
    activo: bool


class ColorCreate(BaseModel):
    codigo: str
    nombre: str
    r: int
    g: int
    b: int
    fisico: bool = False


class ColorUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    r: Optional[int] = None
    g: Optional[int] = None
    b: Optional[int] = None
    fisico: Optional[bool] = None
    activo: Optional[bool] = None


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo: str
    activo: bool
    grupo_cadena: int = 0
    id_led: Optional[int] = None
    # Aplanado desde producto.led.codigo (si hay LED asignado) para que
    # panel.html y teleop_gui.py puedan seguir pintando bolita/letra sin
    # tener que consultar /colores aparte -- mismo hueco que ocupaba el
    # antiguo campo "color".
    led_codigo: Optional[str] = None


class ProductoCreate(BaseModel):
    nombre: str
    codigo: str  # 3 caracteres alfanumericos
    grupo_cadena: int = 0  # ver Producto.grupo_cadena en models.py
    id_led: Optional[int] = None  # opcional: LED que enciende este producto


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    activo: Optional[bool] = None
    grupo_cadena: Optional[int] = None
    id_led: Optional[int] = None


class SubproductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    nombre: str
    codigo: str
    codigo_completo: str
    activo: bool
    precio_centimos: int = 0
    iva_porcentaje: int = 21


class SubproductoCreate(BaseModel):
    producto_id: int
    nombre: str
    codigo: str  # 4 caracteres alfanumericos, unico dentro del producto
    precio_centimos: int = 0
    iva_porcentaje: int = 21


class SubproductoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    activo: Optional[bool] = None
    precio_centimos: Optional[int] = None
    iva_porcentaje: Optional[int] = None


class PaqueteComponenteIn(BaseModel):
    subproducto_id: int
    cantidad: int


class PaqueteComponenteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    subproducto_id: int
    cantidad: int
    subproducto: SubproductoOut


class PaqueteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo: str
    activo: bool
    # Precio de UN paquete; None = sin precio propio (se cobra la suma de sus componentes).
    precio_centimos: Optional[int] = None
    iva_porcentaje: int = 21
    componentes: list[PaqueteComponenteOut] = []


class PaqueteCreate(BaseModel):
    nombre: str
    codigo: str
    componentes: list[PaqueteComponenteIn]
    precio_centimos: Optional[int] = None
    iva_porcentaje: int = 21


class PaqueteUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    activo: Optional[bool] = None
    # Con exclude_unset: enviar precio_centimos=null QUITA el precio propio; no enviarlo lo deja como esta.
    precio_centimos: Optional[int] = None
    iva_porcentaje: Optional[int] = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nombre_completo: str
    rol: str
    cliente_id: Optional[int] = None
    sucursal: Optional[str] = None
    activo: bool
    creado_en: datetime.datetime


class UsuarioCreate(BaseModel):
    username: Optional[str] = None  # sin el, se forma con el codigo del cliente y la sucursal (mur-bilbao)
    nombre_completo: str
    rol: str = "normal"
    cliente_id: Optional[int] = None
    sucursal: Optional[str] = None
    password: Optional[str] = None


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    rol: Optional[str] = None
    sucursal: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    usuario: UsuarioOut


class ClientePrimerUsuario(BaseModel):
    username: Optional[str] = None  # sin el, <codigo>-admin
    nombre_completo: str
    password: Optional[str] = None


class ClienteCreate(BaseModel):
    razon_social: str
    codigo: Optional[str] = None  # 3 letras/cifras; sin el, se saca de la razon social
    cif: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    poblacion: Optional[str] = None
    provincia: Optional[str] = None
    email_facturacion: Optional[str] = None
    primer_usuario: ClientePrimerUsuario


class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    codigo: Optional[str] = None
    cif: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    poblacion: Optional[str] = None
    provincia: Optional[str] = None
    email_facturacion: Optional[str] = None
    activo: Optional[bool] = None


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    razon_social: str
    codigo: Optional[str] = None
    cif: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    poblacion: Optional[str] = None
    provincia: Optional[str] = None
    email_facturacion: Optional[str] = None
    activo: bool
    creado_en: datetime.datetime


class ClienteProductoAsignar(BaseModel):
    producto_id: int


class PedidoCreate(BaseModel):
    subproducto_id: int
    cantidad_pedida: int


class PedidoLineaCreate(BaseModel):
    subproducto_id: int
    cantidad_pedida: int


class PedidoPaqueteLineaCreate(BaseModel):
    paquete_id: int
    cantidad: int


class PedidoMultipleCreate(BaseModel):
    """POST /pedidos/multiple: la cesta. Productos sueltos Y/O paquetes, todo de una vez. Todo lo que
    lleve se entrega junto, en UN albaran."""
    lineas: list[PedidoLineaCreate] = []
    paquetes: list[PedidoPaqueteLineaCreate] = []


class PedidoPorPaqueteCreate(BaseModel):
    """POST /pedidos/paquete: genera un Pedido normal por cada componente
    del paquete (cantidad_pedida = cantidad * componente.cantidad). Nunca
    crea stock ni fila propia de "paquete" -- ver Paquete en models.py."""

    paquete_id: int
    cantidad: int


class PedidoReclamar(BaseModel):
    """Ver Pedido.numero_maquina en models.py. 'forzar' solo para
    administracion -- salta la comprobacion de "libre o mio" y asigna
    directamente (uso: reasignar un pedido cuya maquina se ha caido con
    el numero puesto, o dirigir un pedido concreto a una maquina concreta
    a mano)."""
    numero_maquina: int
    forzar: bool = False
    # Grupo Cadena de la maquina que reclama (sesion 2026-09-14): un
    # pedido puesto a nombre del GRUPO (numero_maquina == grupo_cadena) lo
    # puede coger cualquier maquina de ese grupo. 0 = sin grupo (lo de
    # siempre: solo libre o mio).
    grupo_cadena: int = 0


class UsuarioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nombre_completo: str
    sucursal: Optional[str] = None


class PedidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subproducto_id: int
    producto_id: int
    paquete_origen_id: Optional[int] = None
    paquete_nombre: Optional[str] = None
    paquete_pedido_id: Optional[int] = None
    # Precio de UN paquete (congelado al pedir) y cuantos; None si el pedido es suelto o el paquete
    # no tiene precio propio. Los componentes de un paquete con precio propio salen a 0 EUR.
    paquete_precio_centimos: Optional[int] = None
    paquete_cantidad: Optional[int] = None
    grupo_entrega: Optional[int] = None
    cliente_id: int
    usuario_id: int
    usuario: UsuarioResumen
    cantidad_pedida: int
    cantidad_completada: int
    cantidad_repartida: int = 0
    estado: str
    urgente: bool
    precio_unitario_centimos: int = 0
    iva_porcentaje: int = 21
    precio_origen: str = "tarifa_general"
    numero_maquina: int = 0
    creado_en: datetime.datetime
    subproducto: SubproductoOut
    producto: ProductoOut
    stock_disponible: int = 0
    # Calculados (ver _con_stock_disponible en main.py), no son columnas.
    # falta_fabricar > 0  => el pedido tiene trabajo para el taller (lo que
    #   ni esta listo ni lo cubre el stock libre): es lo que ve Pedidos Taller.
    # para_repartir       => lo que se puede entregar YA: piezas listas sin
    #   repartir + lo que el stock libre cubre: es lo que ve Reparto.
    falta_fabricar: int = 0
    para_repartir: int = 0
    # Calculados desde los MovimientoStock del pedido, no son columnas (ver
    # _con_tiempos_de_proceso en main.py). None = aun no ha recibido piezas.
    segundos_proceso: Optional[float] = None
    segundos_total: Optional[float] = None


class PedidoUpdate(BaseModel):
    urgente: bool


class CuboClasificado(BaseModel):
    """Evento de la celda: un cubo ha llegado a su caja de color.

    Siempre suma 1 al stock. Si el reparto automatico esta activo (el unico
    interruptor de la regla), se aplica ademas a un pedido pendiente de ese
    color: el indicado en pedido_id si sigue activo, si no el mas urgente y
    antiguo. forzar_reparto se admite por compatibilidad pero no cambia nada.

    El producto a resolver (sesion 2026-09-15, peticion explicita del
    usuario: "el LED es una parte nuestra para jugar pero no tiene que
    influir en la logica de negocio"): si viene 'pedido_id', el producto
    sale de ESE pedido; si no, de 'producto_id' si viene; solo si ninguno
    de los dos viene se resuelve por color/LED (compatibilidad con
    llamadas antiguas). 'color' sigue siendo obligatorio como dato
    informativo (el color fisico real del cubo), pero deja de ser
    obligatorio para IDENTIFICAR el producto.
    """

    color: str
    pedido_id: Optional[int] = None
    producto_id: Optional[int] = None
    forzar_reparto: bool = False
    # Quien la ha fabricado (sesion 2026-09-14, bug real con dos cadenas: una
    # pieza de la maquina 20 completo un pedido de la maquina 10). Si viene
    # numero_maquina, la pieza solo puede ir a pedidos con numero_maquina
    # igual a esa maquina o a su grupo_cadena -- los mismos que ve su panel.
    # None = comportamiento de siempre (cualquier pedido de ese color).
    numero_maquina: Optional[int] = None
    grupo_cadena: int = 0


class AjusteStock(BaseModel):
    producto_id: int
    cantidad: int


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    producto_id: int
    cantidad_actual: int
    actualizado_en: Optional[datetime.datetime] = None
    producto: ProductoOut


class MovimientoStockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    tipo: str
    cantidad: int
    motivo: str
    pedido_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha: datetime.datetime


class ConfiguracionAlmacenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    reparto_automatico: bool
    expedicion_automatica: bool
    factor_piezas: int


class ConfiguracionAlmacenUpdate(BaseModel):
    # Los tres opcionales: cada interruptor se toca desde su propia pestana
    # (Almacen / Reparto / Facturacion) sin pisar el del otro.
    reparto_automatico: Optional[bool] = None
    expedicion_automatica: Optional[bool] = None
    factor_piezas: Optional[Literal[1, 10, 100, 1000]] = None


class ExpedirPedidos(BaseModel):
    """POST /reparto/expedir. pedido_ids=None (o ausente) = todo lo que se
    pueda entregar ahora."""
    pedido_ids: Optional[list[int]] = None


class DesgloseIvaOut(BaseModel):
    iva_porcentaje: int
    base_centimos: int
    iva_centimos: int


class RepartoLineaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pedido_id: Optional[int] = None
    subproducto_id: Optional[int] = None
    tipo: str = "normal"                    # normal | paquete | componente
    paquete_pedido_id: Optional[int] = None
    paquete_nombre: Optional[str] = None
    paquete_cantidad: Optional[int] = None
    descripcion: str
    cantidad: int
    precio_unitario_centimos: int
    iva_porcentaje: int
    base_centimos: int = 0


class RepartoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    cliente_id: int
    cliente: ClienteOut
    fecha: datetime.datetime
    usuario_id: Optional[int] = None
    automatico: bool
    lineas: list[RepartoLineaOut]
    # Importes en centimos, calculados de las lineas (ver importes.py).
    base_centimos: int = 0
    iva_centimos: int = 0
    total_centimos: int = 0
    desglose_iva: list["DesgloseIvaOut"] = []
    # Numero de la factura vigente que lo recoge; None = sin facturar.
    factura_numero: Optional[str] = None
    # Nombres de los paquetes cuyos pedidos van en este albaran (vacio si no hay ninguno).
    paquetes: list[str] = []


class CuboClasificadoResultado(BaseModel):
    color: str
    stock_actual: int
    pedido: Optional[PedidoOut] = None


class EventoProduccionCreate(BaseModel):
    robot: str
    color: str
    tipo: str


class EventoProduccionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    robot: str
    color: str
    tipo: str
    fecha: datetime.datetime


class DiagnosticoColor(BaseModel):
    # None si el producto no tiene LED asignado (sesion 2026-09-15): sin
    # color no hay eventos de la celda que cruzar, pero se sigue listando.
    color: Optional[str] = None
    producto_nombre: str
    led_loader: int
    led_sorter: int
    agarre_falso: int
    limite_alcance: int
    fallo_definitivo: int
    piezas_reales: int
    piezas_reales_total: int
    estado: str


class DiagnosticoOut(BaseModel):
    ventana_minutos: int
    por_color: list[DiagnosticoColor]
    eventos_recientes: list[EventoProduccionOut]


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tabla: str
    registro_id: int
    accion: str
    usuario_id: Optional[int] = None
    detalle: Optional[str] = None
    fecha: datetime.datetime


# ------------------------------------------------ precios, tarifas y facturas


class TarifaClienteIn(BaseModel):
    precio_centimos: int


class TarifaClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cliente_id: int
    subproducto_id: int
    precio_centimos: int
    actualizado_en: Optional[datetime.datetime] = None


class TarifaClientePaqueteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cliente_id: int
    paquete_id: int
    precio_centimos: int
    actualizado_en: Optional[datetime.datetime] = None


class HistorialPrecioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
    subproducto_id: Optional[int] = None
    paquete_id: Optional[int] = None
    # Descripcion de la pieza o del paquete al que se refiere el cambio.
    subproducto_descripcion: str = ""
    cliente_id: Optional[int] = None
    cliente_razon_social: Optional[str] = None
    pedido_id: Optional[int] = None
    reparto_linea_id: Optional[int] = None
    precio_anterior_centimos: Optional[int] = None
    precio_nuevo_centimos: Optional[int] = None
    iva_anterior: Optional[int] = None
    iva_nuevo: Optional[int] = None
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None
    fecha: datetime.datetime


class CorregirPrecio(BaseModel):
    """PATCH /pedidos/{id}/precio y /repartos/lineas/{id}/precio. El motivo es
    obligatorio: es lo que se lee luego en el historial para explicar el importe."""
    precio_centimos: int
    iva_porcentaje: Optional[int] = None
    motivo: str


class EmisorIn(BaseModel):
    razon_social: str
    cif: str
    direccion: str
    email: Optional[str] = None
    serie_facturas: str = "FAC"
    serie_rectificativas: str = "RECT"
    por_defecto: bool = False


class EmisorUpdate(BaseModel):
    razon_social: Optional[str] = None
    cif: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    serie_facturas: Optional[str] = None
    serie_rectificativas: Optional[str] = None
    por_defecto: Optional[bool] = None
    activo: Optional[bool] = None


class EmisorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    razon_social: str
    cif: str
    direccion: str
    email: Optional[str] = None
    serie_facturas: str
    serie_rectificativas: str
    por_defecto: bool
    activo: bool
    # True si ya ha emitido alguna factura (entonces sus series ya no se pueden cambiar).
    con_facturas: bool = False


class FacturarIn(BaseModel):
    cliente_id: int
    # None = el emisor por defecto.
    emisor_id: Optional[int] = None
    # None = todos los albaranes de ese cliente aun sin facturar.
    reparto_ids: Optional[list[int]] = None
    # Por defecto se rechazan lineas a 0 EUR (casi siempre un precio sin poner).
    permitir_lineas_a_cero: bool = False


class PagoIn(BaseModel):
    metodo_pago: Optional[str] = None


class AnularIn(BaseModel):
    motivo: str


class FacturaLineaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reparto_linea_id: Optional[int] = None
    albaran_numero: Optional[str] = None
    tipo: str = "normal"
    paquete_pedido_id: Optional[int] = None
    paquete_nombre: Optional[str] = None
    paquete_cantidad: Optional[int] = None
    descripcion: str
    cantidad: int
    precio_unitario_centimos: int
    iva_porcentaje: int
    base_centimos: int = 0


class FacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    tipo: str
    estado: str
    cliente_id: int
    rectifica_id: Optional[int] = None
    emisor_id: Optional[int] = None
    rectifica_numero: Optional[str] = None
    rectificada_por_numero: Optional[str] = None
    motivo: Optional[str] = None
    fecha: datetime.datetime
    usuario_id: Optional[int] = None
    emisor_razon_social: Optional[str] = None
    emisor_cif: Optional[str] = None
    emisor_direccion: Optional[str] = None
    emisor_email: Optional[str] = None
    cliente_razon_social: str
    cliente_cif: str
    cliente_direccion: str
    cliente_email: Optional[str] = None
    fecha_pago: Optional[datetime.datetime] = None
    metodo_pago: Optional[str] = None
    cobrada: bool = False
    albaranes: list[str] = []
    lineas: list[FacturaLineaOut]
    base_centimos: int = 0
    iva_centimos: int = 0
    total_centimos: int = 0
    desglose_iva: list[DesgloseIvaOut] = []
