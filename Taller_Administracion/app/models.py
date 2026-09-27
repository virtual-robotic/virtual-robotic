# Version: 2026-09-26 18:40 -- modelos: permisos por grupo de los empleados
import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    razon_social = Column(String, nullable=False)
    # Codigo corto (3 letras/cifras, unico): de el salen los usuarios (mur-bilbao). Ver app/codigos.py.
    codigo = Column(String(3), nullable=True)
    cif = Column(String, nullable=True)
    # Datos fiscales (sesion 2026-09-19, preparando la facturacion): todos
    # opcionales -- una factura los exige, un pedido no. Cuando exista
    # Factura se copiaran a ella (una factura no puede cambiar si luego se
    # edita el cliente), no se leeran de aqui.
    direccion = Column(String, nullable=True)
    codigo_postal = Column(String, nullable=True)
    poblacion = Column(String, nullable=True)
    provincia = Column(String, nullable=True)
    email_facturacion = Column(String, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    modificado_en = Column(DateTime, nullable=True)
    modificado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    usuarios = relationship(
        "Usuario", foreign_keys="Usuario.cliente_id", back_populates="cliente"
    )
    pedidos = relationship("Pedido", back_populates="cliente")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    nombre_completo = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="normal")
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    sucursal = Column(String, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    # Solo cuentan en rol "empleado" (ver auth.tiene_permiso): que grupos del panel ve.
    permiso_produccion = Column(Boolean, nullable=False, default=False)
    permiso_contabilidad = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    modificado_en = Column(DateTime, nullable=True)
    modificado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    cliente = relationship(
        "Cliente", foreign_keys=[cliente_id], back_populates="usuarios"
    )
    pedidos = relationship("Pedido", back_populates="usuario")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    tabla = Column(String, nullable=False)
    registro_id = Column(Integer, nullable=False)
    accion = Column(String, nullable=False)  # alta / baja / modificacion
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    detalle = Column(String, nullable=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)


class Color(Base):
    """Catalogo de colores/LED (sesion 2026-09-15): antes vivia hardcodeado
    como PALETA_COLORES en main.py y ERA el producto (Producto.color unico).
    Ahora es un catalogo aparte, con RGB libre y alta/baja/modificacion --
    un producto puede tener un LED asignado (o ninguno), pero ya no es su
    identidad. `codigo` sigue siendo el mismo alfabeto de letras de siempre
    (R/G/B/Y/M/C/W...) porque la celda fisica (sorter_demo.py,
    cube_shuttle_demo.py) sigue mandando ese string suelto -- no se toca.
    """

    __tablename__ = "colores"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    r = Column(Integer, nullable=False)
    g = Column(Integer, nullable=False)
    b = Column(Integer, nullable=False)
    # Si hay cubo fisico de verdad en Webots (R/G/B) o es solo LED/software
    # (like antes Y/M/C/W) -- mismo significado que "fisico" en la paleta vieja.
    fisico = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)  # baja logica


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    # Codigo alfanumerico de 3 caracteres (sesion 2026-09-15, sustituye a
    # "color" como identidad del producto -- ver Documentacion/aladin_cambio BBDD.txt).
    codigo = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)  # baja logica: nunca se borra
    # Grupo Cadena que fabrica este producto (sesion 2026-09-14): cada
    # pedido nuevo nace con numero_maquina = este valor, asi solo lo ven y
    # lo cogen las cadenas de ese grupo. 0 = cualquiera (pedido libre).
    grupo_cadena = Column(Integer, nullable=False, default=0)
    # LED opcional (sesion 2026-09-15): antes "color" era obligatorio y
    # ERA el producto. Ahora es una asignacion aparte, puede no haber
    # ninguna (producto sin representacion fisica). Unico entre los
    # productos activos -- se valida a mano en main.py, igual que se
    # validaba "color" antes (ver _migrar_columnas_faltantes).
    id_led = Column(Integer, ForeignKey("colores.id"), nullable=True)

    led = relationship("Color")
    subproductos = relationship("Subproducto", back_populates="producto")
    pedidos = relationship("Pedido", back_populates="producto")
    stock = relationship("Stock", back_populates="producto", uselist=False)

    @property
    def led_codigo(self) -> str | None:
        return self.led.codigo if self.led is not None else None


class Subproducto(Base):
    """Variante concreta de un producto (sesion 2026-09-15): p.ej.
    "Tornillo de 10mm" dentro del producto "Tornillos". La celda fisica NO
    distingue subproductos (solo sabe fabricar/clasificar por color, a
    nivel de Producto) -- Stock y MovimientoStock siguen colgando de
    producto_id sin cambios; el pedido es lo que ahora cuelga de aqui.
    """

    __tablename__ = "subproductos"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    nombre = Column(String, nullable=False)
    # 4 caracteres alfanumericos, unico DENTRO de su producto (no global):
    # el codigo completo que se ensena es producto.codigo + este, ver
    # codigo_completo mas abajo.
    codigo = Column(String, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    # Tarifa vigente (sesion 2026-09-19). Enteros, NUNCA float: 1,25 EUR =
    # 125 centimos -- con dinero, los redondeos de coma flotante acaban
    # descuadrando una factura. Cambiarla NO toca los pedidos ya hechos:
    # cada Pedido guarda su propia copia del precio (ver Pedido).
    precio_centimos = Column(Integer, nullable=False, default=0)
    iva_porcentaje = Column(Integer, nullable=False, default=21)

    producto = relationship("Producto", back_populates="subproductos")
    pedidos = relationship("Pedido", back_populates="subproducto")

    __table_args__ = (UniqueConstraint("producto_id", "codigo", name="uq_subproducto_codigo_por_producto"),)

    @property
    def codigo_completo(self) -> str:
        return f"{self.producto.codigo}{self.codigo}"


class Paquete(Base):
    """Kit cerrado de varios subproductos con cantidad fija cada uno
    (sesion 2026-09-15, p.ej. "Paquete de 10" = 10 tornillos + 10 tuercas
    + 10 arandelas). Nunca tiene stock propio: pedirlo genera N pedidos
    normales (uno por componente, ver POST /pedidos/paquete en main.py) --
    no toca el motor de reparto para nada.
    """

    __tablename__ = "paquetes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    codigo = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    # Precio PROPIO del paquete (sesion 2026-09-20), por paquete y en centimos. NULL = sin precio
    # propio: se cobra la suma de sus componentes, cada uno a su tarifa. Con precio, el albaran y
    # la factura llevan UNA linea del paquete y debajo, sin precio, lo que lleva.
    precio_centimos = Column(Integer, nullable=True)
    iva_porcentaje = Column(Integer, nullable=False, default=21)

    componentes = relationship("PaqueteComponente", back_populates="paquete")


class PaqueteComponente(Base):
    """Receta del paquete: mismo patron que ClienteProducto (tabla puente
    con clave compuesta), con una cantidad por componente."""

    __tablename__ = "paquete_componentes"

    paquete_id = Column(Integer, ForeignKey("paquetes.id"), primary_key=True)
    subproducto_id = Column(Integer, ForeignKey("subproductos.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False)

    paquete = relationship("Paquete", back_populates="componentes")
    subproducto = relationship("Subproducto")


class ClienteProducto(Base):
    __tablename__ = "cliente_productos"

    cliente_id = Column(Integer, ForeignKey("clientes.id"), primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    asignado_en = Column(DateTime, default=datetime.datetime.utcnow)
    asignado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    cliente = relationship("Cliente", backref="productos_asignados")
    producto = relationship("Producto", backref="clientes_asignados")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    # Sesion 2026-09-15: antes colgaba de producto_id directo; ahora cuelga
    # del subproducto concreto pedido. producto_id se mantiene tambien,
    # DESNORMALIZADO A PROPOSITO (= subproducto.producto_id en el momento
    # de crear el pedido): es la clave con la que Stock/MovimientoStock y
    # todo el motor de reparto (_servir_desde_stock, cubo_clasificado)
    # siguen trabajando sin cambiar de comportamiento -- el robot solo
    # sabe de color/producto, nunca de subproducto.
    subproducto_id = Column(Integer, ForeignKey("subproductos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    # Solo si el pedido nacio de pedir un Paquete (POST /pedidos/paquete):
    # agrupa visualmente en el panel los N pedidos que vinieron del mismo
    # paquete. No participa en nada del motor de reparto.
    paquete_origen_id = Column(Integer, ForeignKey("paquetes.id"), nullable=True)
    # Pedidos que se hicieron JUNTOS y se entregan JUNTOS, en UN albaran (sesion 2026-09-19): los
    # componentes de un paquete, o las lineas de una cesta (POST /pedidos/multiple). Todos llevan
    # el mismo valor (el id del primero); NULL = pedido suelto. paquete_origen_id, en cambio, solo
    # dice de que paquete es. La columna en la BBDD se llama grupo_paquete (nombre de cuando solo
    # servia para paquetes); el atributo es grupo_entrega para no tener que migrar.
    grupo_entrega = Column("grupo_paquete", Integer, nullable=True)
    # Si es un componente de un paquete: el pedido de paquete al que pertenece (uno por paquete
    # pedido; guarda el precio del paquete congelado). NULL en un pedido suelto.
    paquete_pedido_id = Column(Integer, ForeignKey("pedidos_paquete.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cantidad_pedida = Column(Integer, nullable=False)
    # Piezas YA LISTAS para este pedido (fabricadas para el o asignadas desde
    # el stock): salen del stock libre y quedan reservadas a su nombre.
    cantidad_completada = Column(Integer, nullable=False, default=0)
    # Piezas ya ENTREGADAS al cliente (sesion 2026-09-19): las que constan en
    # un albaran (Reparto). Siempre <= cantidad_completada. La diferencia es
    # lo que espera en la pestana Reparto.
    cantidad_repartida = Column(Integer, nullable=False, default=0)
    # pendiente (nada listo) -> en_proceso (algo listo, falta) -> listo (todo
    # listo, sin repartir) -> completado (todo repartido); o cancelado.
    # "completado" significa REPARTIDO, ya no "fabricado".
    estado = Column(String, nullable=False, default="pendiente")
    urgente = Column(Boolean, nullable=False, default=False)
    # Precio y IVA CONGELADOS al crear el pedido (copia de Subproducto):
    # lo vendido no cambia si luego se toca la tarifa.
    precio_unitario_centimos = Column(Integer, nullable=False, default=0)
    iva_porcentaje = Column(Integer, nullable=False, default=21)
    # De donde salio ese precio: tarifa_general (Subproducto), tarifa_cliente
    # (TarifaCliente) o manual (corregido por administracion, ver HistorialPrecio).
    precio_origen = Column(String, nullable=False, default="tarifa_general")
    # 0 = sin asignar (libre para cualquier maquina). La maquina que decide
    # fabricarlo escribe aqui su propio numero -- ver auth.py/main.py
    # POST /pedidos/{id}/reclamar. Pensado para repartir produccion entre
    # varias celdas sin que dos fabriquen lo mismo (ver analisis en
    # Documentacion/analisis_ampliacion_taller.md). Con una sola celda
    # (estado actual del proyecto) no tiene efecto practico, pero deja el
    # terreno preparado para cuando haya una segunda.
    numero_maquina = Column(Integer, nullable=False, default=0)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)

    subproducto = relationship("Subproducto", back_populates="pedidos")
    producto = relationship("Producto", back_populates="pedidos")
    paquete_origen = relationship("Paquete")
    paquete_pedido = relationship("PedidoPaquete", back_populates="componentes")

    @property
    def paquete_nombre(self) -> str | None:
        return self.paquete_origen.nombre if self.paquete_origen is not None else None

    @property
    def paquete_precio_centimos(self) -> int | None:
        """Precio de UN paquete (congelado al pedir); None = pedido suelto o paquete sin precio propio."""
        return self.paquete_pedido.precio_unitario_centimos if self.paquete_pedido is not None else None

    @property
    def paquete_cantidad(self) -> int | None:
        return self.paquete_pedido.cantidad if self.paquete_pedido is not None else None
    cliente = relationship("Cliente", back_populates="pedidos")
    usuario = relationship("Usuario", back_populates="pedidos")


class PedidoPaquete(Base):
    """UN paquete pedido (sesion 2026-09-20): cuantos y a que precio. Sus componentes son Pedidos
    normales (uno por producto) que apuntan aqui con Pedido.paquete_pedido_id. Guarda el precio del
    paquete CONGELADO al pedir, igual que el pedido de un producto suelto. Un paquete se entrega
    entero, todo de una vez (ver _entregar en main.py): cantidad_repartida es 0 o cantidad."""

    __tablename__ = "pedidos_paquete"

    id = Column(Integer, primary_key=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)  # numero de paquetes
    cantidad_repartida = Column(Integer, nullable=False, default=0)
    # Precio de UN paquete; None = sin precio propio (los componentes se cobran por separado).
    precio_unitario_centimos = Column(Integer, nullable=True)
    iva_porcentaje = Column(Integer, nullable=False, default=21)
    precio_origen = Column(String, nullable=True)  # paquete_general | paquete_cliente | manual
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)

    paquete = relationship("Paquete")
    componentes = relationship("Pedido", back_populates="paquete_pedido")


class Stock(Base):
    __tablename__ = "stock"

    producto_id = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    cantidad_actual = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    producto = relationship("Producto", back_populates="stock")


class MovimientoStock(Base):
    """Libro de solo anadir: nunca se edita ni se borra una fila existente."""

    __tablename__ = "movimientos_stock"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String, nullable=False)  # entrada / salida
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)  # produccion, asignacion_pedido (stock libre -> pedido), ajuste_manual
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)


class EventoProduccion(Base):
    __tablename__ = "eventos_produccion"

    id = Column(Integer, primary_key=True)
    robot = Column(String, nullable=False)  # loader / sorter / desconocido
    color = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)


class ConfiguracionAlmacen(Base):
    __tablename__ = "configuracion_almacen"

    id = Column(Integer, primary_key=True)  # fila unica, id = 1
    # Etapa 1 (almacen): el stock libre se asigna solo a los pedidos.
    reparto_automatico = Column(Boolean, nullable=False, default=True)
    # Etapa 2 (reparto, sesion 2026-09-19): lo que un pedido tiene listo se
    # entrega solo, generando el albaran. Apagado, espera en la pestana
    # Reparto hasta que alguien lo reparta.
    expedicion_automatica = Column(Boolean, nullable=False, default=True)
    # Solo de cara a imprimir (sesion 2026-09-22): multiplica cantidad e importes
    # en la factura/albaran YA generados para que la demo se vea con mas piezas y
    # mas factura. Nunca toca Pedido/RepartoLinea/FacturaLinea reales: el stock,
    # el reparto automatico y el historial de precios siguen viendo los numeros
    # de verdad. Valores validos: 1, 10, 100, 1000.
    factor_piezas = Column(Integer, nullable=False, default=1)
    # OBSOLETO: antes habia UN solo emisor aqui. Ahora son varios (tabla emisores); estas
    # columnas solo se conservan para pasar el emisor antiguo a la tabla nueva al arrancar.
    emisor_razon_social = Column(String, nullable=True)
    emisor_cif = Column(String, nullable=True)
    emisor_direccion = Column(String, nullable=True)
    emisor_email = Column(String, nullable=True)


class Emisor(Base):
    """Empresa que emite facturas (sesion 2026-09-19): puede haber varias, cada una con
    su CIF, su direccion y su NUMERACION propia (serie). Al emitir una factura se copian
    sus datos a la factura; editar el emisor despues no la cambia. Nunca se borra (una
    factura apunta a ella): se desactiva."""

    __tablename__ = "emisores"

    id = Column(Integer, primary_key=True)
    razon_social = Column(String, nullable=False)
    cif = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    email = Column(String, nullable=True)
    # Prefijo de la numeracion: FAC-2026-000001 / RECT-2026-000001. Distinto en cada emisor
    # (dos empresas no pueden compartir contador) y fijo una vez emitida su primera factura.
    serie_facturas = Column(String, unique=True, nullable=False, default="FAC")
    serie_rectificativas = Column(String, unique=True, nullable=False, default="RECT")
    por_defecto = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)


class Reparto(Base):
    """Albaran: una entrega de piezas a UN cliente (sesion 2026-09-19).

    Es el hecho que se factura -- la factura futura agrupara albaranes, no
    pedidos. Solo se anade, nunca se edita ni se borra (como
    MovimientoStock); un error se corrige con otro reparto, no reescribiendo
    este. `numero` es correlativo por anio (ALB-2026-000001).
    """

    __tablename__ = "repartos"

    id = Column(Integer, primary_key=True)
    numero = Column(String, unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Quien lo dio de salida a mano; None si salio solo (expedicion automatica).
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    automatico = Column(Boolean, nullable=False, default=False)

    cliente = relationship("Cliente")
    lineas = relationship("RepartoLinea", back_populates="reparto", order_by="RepartoLinea.id")


class RepartoLinea(Base):
    __tablename__ = "reparto_lineas"

    id = Column(Integer, primary_key=True)
    reparto_id = Column(Integer, ForeignKey("repartos.id"), nullable=False)
    # NULL en la linea de un PAQUETE (no es de un solo pedido ni de un solo producto).
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    subproducto_id = Column(Integer, ForeignKey("subproductos.id"), nullable=True)
    # normal | paquete (la linea del paquete, con su precio) | componente (lo que lleva, SIN precio:
    # ya va en el del paquete). Las lineas de un paquete sin precio propio son 'normal' con
    # paquete_pedido_id, solo para agruparlas al mostrarlas.
    tipo = Column(String, nullable=False, default="normal")
    paquete_pedido_id = Column(Integer, ForeignKey("pedidos_paquete.id"), nullable=True)
    paquete_nombre = Column(String, nullable=True)   # copia, como la descripcion
    paquete_cantidad = Column(Integer, nullable=True)  # cuantos paquetes
    # Texto y precio COPIADOS en el momento de la entrega: el albaran tiene
    # que seguir diciendo lo mismo aunque luego se renombre o cambie de
    # precio el subproducto.
    descripcion = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario_centimos = Column(Integer, nullable=False, default=0)
    iva_porcentaje = Column(Integer, nullable=False, default=21)

    reparto = relationship("Reparto", back_populates="lineas")


class TarifaCliente(Base):
    """Precio especial de un subproducto para UN cliente (sesion 2026-09-19).
    Sin fila, el cliente paga la tarifa general (Subproducto.precio_centimos).
    Se aplica al CREAR un pedido; no toca los ya hechos."""

    __tablename__ = "tarifas_cliente"

    cliente_id = Column(Integer, ForeignKey("clientes.id"), primary_key=True)
    subproducto_id = Column(Integer, ForeignKey("subproductos.id"), primary_key=True)
    precio_centimos = Column(Integer, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.datetime.utcnow)
    actualizado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    cliente = relationship("Cliente")
    subproducto = relationship("Subproducto")


class TarifaClientePaquete(Base):
    """Precio especial de un PAQUETE para UN cliente (como TarifaCliente, pero de paquetes)."""

    __tablename__ = "tarifas_cliente_paquete"

    cliente_id = Column(Integer, ForeignKey("clientes.id"), primary_key=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"), primary_key=True)
    precio_centimos = Column(Integer, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.datetime.utcnow)
    actualizado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    cliente = relationship("Cliente")
    paquete = relationship("Paquete")


class HistorialPrecio(Base):
    """Libro de solo anadir de TODO cambio de precio (sesion 2026-09-19): quien
    lo cambio, cuando, de cuanto a cuanto y por que. Sin esto, editar una
    tarifa borraba el valor anterior y no habia forma de explicar un importe.
    tipo: tarifa_general | tarifa_cliente | pedido | albaran | paquete_general | paquete_cliente |
    pedido_paquete. Los de paquete llevan paquete_id y NO subproducto_id. precio_nuevo NULL = se
    quito la tarifa del cliente (vuelve a la general) o el paquete se quedo sin precio propio."""

    __tablename__ = "historial_precios"

    id = Column(Integer, primary_key=True)
    tipo = Column(String, nullable=False)
    subproducto_id = Column(Integer, ForeignKey("subproductos.id"), nullable=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    reparto_linea_id = Column(Integer, ForeignKey("reparto_lineas.id"), nullable=True)
    precio_anterior_centimos = Column(Integer, nullable=True)
    precio_nuevo_centimos = Column(Integer, nullable=True)
    iva_anterior = Column(Integer, nullable=True)
    iva_nuevo = Column(Integer, nullable=True)
    motivo = Column(String, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    subproducto = relationship("Subproducto")
    paquete = relationship("Paquete")
    cliente = relationship("Cliente")


class Factura(Base):
    """Factura o rectificativa (sesion 2026-09-19). Agrupa albaranes (Reparto)
    de UN cliente. Es un documento cerrado: solo se anade. Se corrige con una
    rectificativa, que la anula (estado 'anulada' en la original) y lleva las
    mismas lineas con cantidad NEGATIVA; el albaran queda libre para volver a
    facturarse. Numeracion correlativa por anio y por serie: FAC-AAAA-nnnnnn
    para facturas y RECT-AAAA-nnnnnn para rectificativas.

    Los datos fiscales del cliente se COPIAN aqui al emitir: una factura no
    puede cambiar porque luego se edite la ficha del cliente."""

    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True)
    numero = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False, default="factura")  # factura | rectificativa
    estado = Column(String, nullable=False, default="emitida")  # emitida | anulada
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    rectifica_id = Column(Integer, ForeignKey("facturas.id"), nullable=True)
    emisor_id = Column(Integer, ForeignKey("emisores.id"), nullable=True)
    motivo = Column(String, nullable=True)  # de la rectificativa
    fecha = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    # Copia de los datos del EMISOR (ConfiguracionAlmacen) al emitir.
    emisor_razon_social = Column(String, nullable=True)
    emisor_cif = Column(String, nullable=True)
    emisor_direccion = Column(String, nullable=True)
    emisor_email = Column(String, nullable=True)
    # Copia de los datos fiscales del cliente en el momento de emitir.
    cliente_razon_social = Column(String, nullable=False)
    cliente_cif = Column(String, nullable=False)
    cliente_direccion = Column(String, nullable=False)
    cliente_email = Column(String, nullable=True)
    # Cobro (solo en facturas, no en rectificativas).
    fecha_pago = Column(DateTime, nullable=True)
    metodo_pago = Column(String, nullable=True)

    cliente = relationship("Cliente")
    lineas = relationship("FacturaLinea", back_populates="factura", order_by="FacturaLinea.id")


class FacturaLinea(Base):
    __tablename__ = "factura_lineas"

    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    # Linea de albaran que se factura. Esta facturada si tiene una FacturaLinea
    # en una factura 'emitida' de tipo 'factura' (ver facturacion.py).
    reparto_linea_id = Column(Integer, ForeignKey("reparto_lineas.id"), nullable=True)
    albaran_numero = Column(String, nullable=True)
    tipo = Column(String, nullable=False, default="normal")  # normal | paquete | componente (ver RepartoLinea)
    paquete_pedido_id = Column(Integer, nullable=True)
    paquete_nombre = Column(String, nullable=True)
    paquete_cantidad = Column(Integer, nullable=True)
    descripcion = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)  # negativa en una rectificativa
    precio_unitario_centimos = Column(Integer, nullable=False)
    iva_porcentaje = Column(Integer, nullable=False)

    factura = relationship("Factura", back_populates="lineas")
