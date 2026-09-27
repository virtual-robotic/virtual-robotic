# Version: 2026-09-27 18:35 -- descarga de las plantillas Word (/plantillas). Antes: Taller_Administracion API (empleados con permiso por grupo: Produccion/Contabilidad)
import asyncio
import datetime
import logging
import os
import subprocess
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from . import auth, codigos, contabilidad, datos_arranque, importes, models, schemas
from .auditoria import audit as _audit
from .database import Base, SessionLocal, engine, get_db
from .migraciones import migrar_columnas_faltantes

log = logging.getLogger("uvicorn.error")

BASE_DIR = Path(__file__).resolve().parent
# Repo padre (montado solo lectura por docker-compose.yml, ver MANUALES mas
# abajo) -- se necesita ya aqui arriba para el fallback de VERSION.
REPO_DIR = Path(os.environ.get("TALLER_REPO_DIR", BASE_DIR.parent.parent))


def _version_desde_git(repo_dir: Path) -> str | None:
    """Mismo calculo que generar_version.sh, por si nadie lo ha corrido
    todavia (sesion 2026-09-16: un "docker compose up -d --build" recien
    clonado, sin pasar por arrancar_todo.sh, se quedaba en "sin-version"
    para siempre -- esto lo autocura la primera vez que arranca la API,
    sin depender de que alguien se acuerde de ese paso a mano). Nunca
    lanza: si no hay git, no hay .git montado, o cualquier otro fallo,
    simplemente no hay version calculada y se cae al "sin-version" de
    siempre."""
    try:
        # "-c safe.directory=*": el repo montado en el contenedor es del
        # host, con otro dueño -- sin esto git rechaza tocarlo con
        # "detected dubious ownership" (visto en vivo probando esto).
        git_base = ["git", "-c", "safe.directory=*"]
        aamm = subprocess.run(
            [*git_base, "log", "-1", "--format=%cd", "--date=format:%y%m"],
            cwd=repo_dir, capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        total = subprocess.run(
            [*git_base, "rev-list", "--count", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        if not aamm or not total:
            return None
        return f"{aamm}.{int(total):05d}"
    except Exception:
        return None


def _version_estatica() -> str | None:
    """El version.py que deja generar_version.sh (no esta en el repo, ver
    .gitignore): es una FOTO FIJA de cuando se corrio el script, asi que dos
    maquinas pueden enseñar numeros distintos aunque tengan el mismo commit
    si una de las dos no lo ha vuelto a correr. Por eso es el ultimo recurso,
    no el primero (sesion 2026-09-22: confundio, parecia que el codigo no
    estaba actualizado y solo era este fichero desfasado)."""
    try:
        from .version import VERSION as v
        return v
    except ImportError:
        return None


# Primero SIEMPRE se intenta calcular en vivo desde git: asi el numero
# cuadra con lo que de verdad hay subido, sin depender de que alguien se
# acuerde de correr generar_version.sh en cada maquina. Ese fichero solo se
# usa si no hay git disponible (p.ej. una imagen sin el repo montado).
VERSION = _version_desde_git(REPO_DIR) or _version_estatica() or "sin-version"

# Mismo rango que los desplegables Grupo Cadena / Nº Maquina del panel de
# control (teleop_gui.py).
GRUPO_CADENA_MIN, GRUPO_CADENA_MAX = 0, 99


def _validar_grupo_cadena(grupo: int) -> int:
    if not GRUPO_CADENA_MIN <= grupo <= GRUPO_CADENA_MAX:
        raise HTTPException(
            400, f"Grupo cadena tiene que estar entre {GRUPO_CADENA_MIN} y {GRUPO_CADENA_MAX}."
        )
    return grupo


def _codigo_valido(codigo: str, longitud: int) -> bool:
    return bool(codigo) and len(codigo) == longitud and codigo.isalnum()


def _paleta_colores_dict(db: Session) -> dict:
    """Mismo shape que la antigua PALETA_COLORES hardcodeada (sesion
    2026-09-15: ahora viene de la tabla `colores`, ver models.Color) --
    panel.html y teleop_gui.py siguen leyendo /paleta_colores igual que
    siempre, sin tocar nada de ese lado."""
    colores = db.query(models.Color).filter(models.Color.activo == True).all()  # noqa: E712
    return {
        c.codigo: {
            "nombre": c.nombre,
            "rgb": f"#{c.r:02x}{c.g:02x}{c.b:02x}",
            "fisico": c.fisico,
        }
        for c in colores
    }


# Sesion 2026-09-15: colores/productos/subproductos/paquetes se rediseñan
# de raiz (ver Documentacion/aladin_cambio BBDD.txt) -- las tablas viejas
# (productos/pedidos/stock/movimientos_stock, forma incompatible) se
# tiran antes de este cambio, asi que el seed de abajo arranca en limpio.
SEED_COLORES = [
    # codigo, nombre, r, g, b, fisico (mismos 7 de siempre, misma paleta)
    ("R", "Rojo", 230, 66, 58, True),
    ("G", "Verde", 45, 160, 90, True),
    ("B", "Azul", 55, 120, 200, True),
    ("Y", "Amarillo", 225, 196, 40, False),
    ("M", "Magenta", 190, 60, 180, False),
    ("C", "Cian", 45, 171, 168, False),
    ("W", "Blanco", 232, 232, 226, False),
]
SEED_PRODUCTOS = [
    # nombre, codigo (3 car.), codigo_led (o None), grupo_cadena
    ("Tornillos", "100", "R", 0),
    ("Tuercas", "200", "G", 0),
    ("Arandelas", "300", "B", 0),
]
SEED_SUBPRODUCTOS = [
    # codigo_producto, nombre, codigo (4 car.), precio en centimos (sin IVA;
    # de ejemplo, para que los albaranes salgan con importes desde el principio)
    ("100", "Tornillo 10mm", "2222", 12),
    ("100", "Tornillo 20mm", "A20X", 18),
    ("200", "Tuerca 10mm", "3001", 8),
    ("300", "Arandela 10mm", "4001", 5),
]
SEED_PAQUETES = [
    # nombre, codigo, [(codigo_producto, codigo_subproducto, cantidad), ...], precio del paquete en
    # centimos (de ejemplo, algo por debajo de la suma de sus componentes: 2,50 y 6,20 EUR)
    ("Paquete de 10", "P010", [("100", "2222", 10), ("200", "3001", 10), ("300", "4001", 10)], 220),
    ("Paquete de 20", "P020", [("100", "A20X", 20), ("200", "3001", 20), ("300", "4001", 20)], 550),
]
# Empresas de ejemplo (sesion 2026-09-16, peticion explicita del usuario:
# "que tenga usuarios, productos y todo eso" para poder jugar con datos
# nada mas clonar el proyecto en una maquina nueva). Password de todos:
# la maestra TALLER_MASTER_PASSWORD (por defecto "1111") -- con
# TALLER_DEV_MODE=true (ver docker-compose.yml) vale para cualquier rol,
# asi que no hace falta guardar un password_hash propio para estos.
SEED_CLIENTES = [
    # razon_social, codigo de cliente, cif, [(username, nombre_completo, rol, sucursal), ...], [codigo_producto asignado, ...],
    # datos fiscales de ejemplo (sin ellos un cliente no se puede facturar, ver contabilidad.py)
    (
        "Ferreteria Ereno S.L.", "ERE", "B48123456",
        [
            ("ere-admin", "Admin Ereno", auth.ROL_ADMIN_CLIENTE, "Gernika"),
            ("ere-bermeo", "Operario Bermeo", auth.ROL_NORMAL, "Bermeo"),
        ],
        ["100", "200", "300"],
        {"direccion": "Calle Barrenkale 12", "codigo_postal": "48300", "poblacion": "Gernika-Lumo",
         "provincia": "Bizkaia", "email_facturacion": "facturas@ereno.example"},
    ),
    (
        "Suministros Mungia S.A.", "MUN", "A48765432",
        [
            ("mun-admin", "Admin Mungia", auth.ROL_ADMIN_CLIENTE, "Mungia"),
            ("mun-larrabetzu", "Operario Larrabetzu", auth.ROL_NORMAL, "Larrabetzu"),
        ],
        ["100", "300"],
        {"direccion": "Polígono Industrial Mungia, nave 4", "codigo_postal": "48100", "poblacion": "Mungia",
         "provincia": "Bizkaia", "email_facturacion": "facturas@suministrosmungia.example"},
    ),
    (
        "Construcciones Busturia S.L.", "BUS", "B48111222",
        [("bus-admin", "Admin Busturia", auth.ROL_ADMIN_CLIENTE, "Busturia")],
        ["200"],
        {"direccion": "Kalea Nagusia 3", "codigo_postal": "48350", "poblacion": "Busturia",
         "provincia": "Bizkaia", "email_facturacion": "facturas@busturia.example"},
    ),
]
# Ciclo de un pedido (sesion 2026-09-19): pendiente -> en_proceso -> listo ->
# completado, o cancelado. "listo" = todas las piezas reservadas para el pedido,
# pendiente de entregar (pestana Reparto); "completado" = REPARTIDO, con su
# albaran. Estos tres ya no necesitan piezas: ni la celda las fabrica para
# ellos ni el stock se les asigna.
ESTADOS_NO_ASIGNABLES = ("listo", "completado", "cancelado")
# Estados en los que el pedido sigue vivo para el cliente (aun no repartido del todo).
ESTADOS_ABIERTOS = ("pendiente", "en_proceso", "listo")
MOTIVO_ASIGNACION = "asignacion_pedido"  # salida de stock libre hacia un pedido (antes "envio_pedido")


def _estado_pedido(pedido: models.Pedido) -> str:
    """Estado que corresponde a las cantidades del pedido (una sola regla, la
    usan la asignacion de stock, la celda y el reparto)."""
    if pedido.estado == "cancelado":
        return "cancelado"
    if pedido.cantidad_repartida >= pedido.cantidad_pedida:
        return "completado"
    if pedido.cantidad_completada >= pedido.cantidad_pedida:
        return "listo"
    if pedido.cantidad_completada > 0:
        return "en_proceso"
    return "pendiente"


_validar_precio_iva = contabilidad.validar_precio_iva


TIPOS_EVENTO_PRODUCCION = {
    "led_encendido",
    "agarre_falso",
    "limite_alcance",
    "fallo_definitivo",
}

# No hay Alembic: create_all() solo crea tablas que no existen, nunca
# anade columnas a una ya existente. Como este cambio reestructura
# productos/pedidos/stock/movimientos_stock de raiz (columnas
# incompatibles con las de antes), esas 4 tablas se tiran a mano una vez
# (ver Documentacion/aladin_cambio BBDD.txt) antes de desplegar este
# codigo -- clientes/usuarios/audit_log/eventos_produccion no cambian de
# forma y no se tocan. A partir de aqui, create_all() ya crea todo
# (incluidas colores/subproductos/paquetes/paquete_componentes, nuevas)
# con la forma correcta desde el principio.
Base.metadata.create_all(bind=engine)
# Columnas NUEVAS en tablas que ya existian (create_all no las anade): ver migraciones.py.
migrar_columnas_faltantes(engine, Base)

app = FastAPI(title="Taller - Administracion")
app.include_router(contabilidad.router)


# Videos de la portada (sesion 2026-09-26): Safari solo reproduce un <video>
# si el servidor contesta a "Range: bytes=..." con un 206 y ese trozo. El
# StaticFiles de starlette 0.38 (el que trae fastapi 0.115.0) ignora Range y
# siempre manda el fichero entero con 200 -> en Safari el video no arranca
# (Chrome/Firefox si lo toleran). Esta ruta va ANTES del mount de /static
# para que la encuentre primero; los clips pesan ~400 KB, se leen enteros.
@app.get("/static/img/{nombre}.mp4", include_in_schema=False)
def video_con_range(nombre: str, range: str | None = Header(default=None)) -> Response:
    carpeta = (BASE_DIR / "static" / "img").resolve()
    ruta = (carpeta / f"{nombre}.mp4").resolve()
    if ruta.parent != carpeta or not ruta.is_file():
        raise HTTPException(status_code=404, detail="Not Found")
    datos = ruta.read_bytes()
    total = len(datos)
    cabeceras = {"Accept-Ranges": "bytes"}
    if not range:
        return Response(datos, media_type="video/mp4", headers=cabeceras)
    try:
        unidad, _, trozo = range.partition("=")
        inicio_txt, _, fin_txt = trozo.split(",")[0].strip().partition("-")
        if unidad.strip() != "bytes":
            raise ValueError
        if inicio_txt == "":  # "bytes=-500" = los ultimos 500
            inicio, fin = max(total - int(fin_txt), 0), total - 1
        else:
            inicio = int(inicio_txt)
            fin = min(int(fin_txt), total - 1) if fin_txt else total - 1
        if inicio > fin or inicio >= total:
            raise ValueError
    except ValueError:
        return Response(status_code=416, headers={**cabeceras, "Content-Range": f"bytes */{total}"})
    cabeceras["Content-Range"] = f"bytes {inicio}-{fin}/{total}"
    return Response(datos[inicio:fin + 1], status_code=206, media_type="video/mp4", headers=cabeceras)


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.middleware("http")
async def _sin_cache_en_static(request, call_next):
    # StaticFiles (arriba) no lleva el NO_CACHE de mas abajo -- solo pone
    # ETag/Last-Modified, y sin Cache-Control el navegador puede servir un
    # .js/.html de /static/ de su cache SIN preguntar al servidor durante un
    # rato (cache heuristica de la RFC 7234). Sesion 2026-09-22: eso hizo que
    # el selector de idioma pareciera "no traducir nada" con un
    # i18n_panel.js viejo en cache, pese a que el servidor ya tenia el
    # nuevo -- mismo sintoma que ya describe el comentario de NO_CACHE unas
    # lineas mas abajo, pero esta vez en un fichero cargado por <script src>,
    # no en la pagina misma.
    respuesta = await call_next(request)
    if request.url.path.startswith("/static/"):
        respuesta.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return respuesta


def _servir_desde_stock(db: Session, pedido: models.Pedido) -> None:
    stock_row = (
        db.query(models.Stock).filter(models.Stock.producto_id == pedido.producto_id).first()
    )
    if stock_row is None or stock_row.cantidad_actual <= 0:
        return
    restante = pedido.cantidad_pedida - pedido.cantidad_completada
    if restante <= 0:
        return
    servir = min(stock_row.cantidad_actual, restante)
    if servir <= 0:
        return
    stock_row.cantidad_actual -= servir
    stock_row.actualizado_en = datetime.datetime.utcnow()
    pedido.cantidad_completada += servir
    pedido.estado = _estado_pedido(pedido)
    db.add(
        models.MovimientoStock(
            producto_id=pedido.producto_id,
            tipo="salida",
            cantidad=servir,
            motivo=MOTIVO_ASIGNACION,
            pedido_id=pedido.id,
            usuario_id=pedido.usuario_id,
        )
    )
    db.commit()


def _con_stock_disponible(
    db: Session, pedidos: list[models.Pedido]
) -> list[models.Pedido]:
    """Rellena stock_disponible simulando el reparto FIFO real, sin tocar la base."""
    productos_ids = {p.producto_id for p in pedidos}
    asignado_por_pedido: dict[int, int] = {}
    for producto_id in productos_ids:
        stock_row = (
            db.query(models.Stock).filter(models.Stock.producto_id == producto_id).first()
        )
        disponible = stock_row.cantidad_actual if stock_row else 0
        activos = (
            db.query(models.Pedido)
            .filter(models.Pedido.producto_id == producto_id)
            .filter(models.Pedido.estado.notin_(ESTADOS_NO_ASIGNABLES))
            .all()
        )
        activos.sort(key=lambda p: (not p.urgente, p.creado_en))
        for pedido in activos:
            restante = pedido.cantidad_pedida - pedido.cantidad_completada
            asignado = max(0, min(disponible, restante))
            asignado_por_pedido[pedido.id] = asignado
            disponible -= asignado
    for pedido in pedidos:
        pedido.stock_disponible = asignado_por_pedido.get(pedido.id, 0)
        if pedido.estado in ("pendiente", "en_proceso"):
            pedido.falta_fabricar = max(
                0, pedido.cantidad_pedida - pedido.cantidad_completada - pedido.stock_disponible
            )
        else:
            pedido.falta_fabricar = 0
        if pedido.estado in ESTADOS_ABIERTOS:
            pedido.para_repartir = (
                pedido.cantidad_completada - pedido.cantidad_repartida + pedido.stock_disponible
            )
        else:
            pedido.para_repartir = 0
    _con_tiempos_de_proceso(db, pedidos)
    return pedidos


def _con_tiempos_de_proceso(db: Session, pedidos: list[models.Pedido]) -> None:
    """Rellena cuanto ha tardado cada lote, sin columnas nuevas en Pedido.

    Cada unidad que entra a un pedido deja su MovimientoStock de salida con
    fecha (ver cubo_clasificado / _servir_desde_stock; es la ASIGNACION al
    pedido, no la entrega al cliente, que consta en el albaran), asi que el tiempo real
    sale de la primera y la ultima: 'proceso' es lo que tardo en completarse
    una vez empezo a recibir piezas, y 'total' incluye ademas la espera en cola
    desde que se hizo el pedido. Un lote servido de golpe desde almacen da
    proceso=0 a proposito: no se fabrico nada, salio de stock.

    Una sola consulta agregada para toda la lista (no una por pedido).
    """
    ids = [p.id for p in pedidos]
    for pedido in pedidos:
        pedido.segundos_proceso = None
        pedido.segundos_total = None
    if not ids:
        return
    filas = (
        db.query(
            models.MovimientoStock.pedido_id,
            func.min(models.MovimientoStock.fecha),
            func.max(models.MovimientoStock.fecha),
            func.count(models.MovimientoStock.id),
        )
        .filter(models.MovimientoStock.pedido_id.in_(ids))
        .filter(models.MovimientoStock.motivo == MOTIVO_ASIGNACION)
        .group_by(models.MovimientoStock.pedido_id)
        .all()
    )
    por_pedido = {fila[0]: (fila[1], fila[2], fila[3]) for fila in filas}
    for pedido in pedidos:
        datos = por_pedido.get(pedido.id)
        if datos is None:
            continue
        primera, ultima, _n = datos
        if primera is None or ultima is None:
            continue
        pedido.segundos_proceso = max(0.0, (ultima - primera).total_seconds())
        if pedido.creado_en is not None:
            pedido.segundos_total = max(0.0, (ultima - pedido.creado_en).total_seconds())


# ------------------------------------------------------- reparto / albaranes


def _siguiente_numero_albaran(db: Session, fecha: datetime.datetime) -> str:
    """ALB-<anio>-<serie de 6 cifras>, correlativo por anio. Sale del ultimo
    numero ya guardado (no de un contador aparte) y tiene UNIQUE en la BBDD:
    si dos repartos llegaran a la vez, el segundo falla en vez de duplicar."""
    prefijo = f"ALB-{fecha.year}-"
    ultimo = (
        db.query(func.max(models.Reparto.numero))
        .filter(models.Reparto.numero.like(f"{prefijo}%"))
        .scalar()
    )
    siguiente = int(ultimo.rsplit("-", 1)[1]) + 1 if ultimo else 1
    return f"{prefijo}{siguiente:06d}"


def _entregar(
    db: Session, pedidos: list[models.Pedido], usuario_id: int | None, automatico: bool
) -> list[models.Reparto]:
    """Entrega al cliente lo que cada pedido tiene LISTO y aun no repartido
    (cantidad_completada - cantidad_repartida). Un albaran por cliente. No toca el stock: las piezas
    ya salieron del stock libre cuando se asignaron al pedido (ver MOTIVO_ASIGNACION).

    Un PAQUETE se entrega ENTERO (decision del usuario 2026-09-20): sus componentes solo salen cuando
    estan TODOS listos, y siempre juntos. Con precio propio el albaran lleva UNA linea del paquete (con
    su precio) y debajo, sin precio, lo que lleva; sin precio propio, cada componente con el suyo
    pero agrupados bajo el paquete."""
    hermanos_de: dict[int, list[models.Pedido]] = {}
    completo: dict[int, bool] = {}
    candidatos: list[models.Pedido] = []
    vistos: set[int] = set()

    def anadir(p: models.Pedido) -> None:
        if p.id not in vistos:
            vistos.add(p.id)
            candidatos.append(p)

    for pedido in pedidos:
        if pedido.estado == "cancelado" or pedido.cantidad_completada - pedido.cantidad_repartida <= 0:
            continue
        pp_id = pedido.paquete_pedido_id
        if pp_id is None:
            anadir(pedido)
            continue
        if pp_id not in completo:
            hermanos_de[pp_id] = db.query(models.Pedido).filter(
                models.Pedido.paquete_pedido_id == pp_id, models.Pedido.estado != "cancelado").all()
            completo[pp_id] = all(h.cantidad_completada >= h.cantidad_pedida for h in hermanos_de[pp_id])
            if completo[pp_id]:
                for h in hermanos_de[pp_id]:
                    if h.cantidad_completada - h.cantidad_repartida > 0:
                        anadir(h)   # el paquete sale entero aunque solo se hayan pedido algunos de sus componentes
    ahora = datetime.datetime.utcnow()
    por_cliente: dict[int, list[models.Pedido]] = {}
    for pedido in candidatos:
        por_cliente.setdefault(pedido.cliente_id, []).append(pedido)
    repartos = []
    for cliente_id, items in por_cliente.items():
        reparto = models.Reparto(
            numero=_siguiente_numero_albaran(db, ahora),
            cliente_id=cliente_id,
            fecha=ahora,
            usuario_id=usuario_id,
            automatico=automatico,
        )
        db.add(reparto)
        db.flush()  # SessionLocal es autoflush=False: sin esto el siguiente numero se repetiria
        paquetes_hechos: set[int] = set()
        for pedido in items:
            cantidad = pedido.cantidad_completada - pedido.cantidad_repartida
            sub = pedido.subproducto
            descripcion = f"{pedido.producto.nombre} · {sub.nombre} ({sub.codigo_completo})"
            pp = pedido.paquete_pedido
            if pp is None:
                db.add(models.RepartoLinea(
                    reparto_id=reparto.id, pedido_id=pedido.id, subproducto_id=sub.id, descripcion=descripcion,
                    cantidad=cantidad, precio_unitario_centimos=pedido.precio_unitario_centimos,
                    iva_porcentaje=pedido.iva_porcentaje))
            else:
                paq = pp.paquete
                if pp.precio_unitario_centimos is not None and pp.id not in paquetes_hechos:
                    paquetes_hechos.add(pp.id)   # la linea del paquete, con su precio, una sola vez
                    db.add(models.RepartoLinea(
                        reparto_id=reparto.id, pedido_id=None, subproducto_id=None, tipo="paquete",
                        paquete_pedido_id=pp.id, paquete_nombre=paq.nombre, paquete_cantidad=pp.cantidad,
                        descripcion=f"{paq.nombre} ({paq.codigo})", cantidad=pp.cantidad,
                        precio_unitario_centimos=pp.precio_unitario_centimos, iva_porcentaje=pp.iva_porcentaje))
                db.add(models.RepartoLinea(
                    reparto_id=reparto.id, pedido_id=pedido.id, subproducto_id=sub.id,
                    tipo="componente" if pp.precio_unitario_centimos is not None else "normal",
                    paquete_pedido_id=pp.id, paquete_nombre=paq.nombre, paquete_cantidad=pp.cantidad,
                    descripcion=descripcion, cantidad=cantidad,
                    precio_unitario_centimos=pedido.precio_unitario_centimos, iva_porcentaje=pedido.iva_porcentaje))
                pp.cantidad_repartida = pp.cantidad
            pedido.cantidad_repartida += cantidad
            pedido.estado = _estado_pedido(pedido)
        repartos.append(reparto)
    db.commit()
    for reparto in repartos:
        detalle = ", ".join(f"#{l.pedido_id} x{l.cantidad}" for l in reparto.lineas if l.pedido_id)
        _audit(db, "repartos", reparto.id, "alta", usuario_id, f"{reparto.numero}: {detalle}")
    return repartos


def _servir_y_expedir(db: Session, pedidos: list[models.Pedido]) -> None:
    """Con el reparto automatico, asigna el stock libre a estos pedidos y, con la expedicion
    automatica, entrega los que queden listos."""
    config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
    if not (config and config.reparto_automatico):
        return
    for pedido in pedidos:
        _servir_desde_stock(db, pedido)
        db.refresh(pedido)
    _expedir_listos_si_automatico(db, pedidos)
    for pedido in pedidos:
        db.refresh(pedido)


# Barrido periodico de stock (sesion 2026-09-20, a peticion del usuario). Incidente real: una pieza
# entro al almacen sin asignarse a su pedido (el servidor estaba reiniciandose, o la fabrico otra
# maquina) y el pedido se quedo parado en 9/10, porque la celda lo ve "cubierto por stock" y no
# fabrica mas, y el reparto automatico solo asignaba al LLEGAR una pieza. Cada BARRIDO_SEGUNDOS se
# mira si el stock libre cubre por completo algun pedido abierto y se le asigna. 0 = desactivado
# (los tests lo apagan para ser deterministas).
BARRIDO_SEGUNDOS = float(os.environ.get("TALLER_BARRIDO_SEGUNDOS", "10"))
log_barrido = logging.getLogger("uvicorn.error")


def barrer_stock(db: Session) -> list[models.Pedido]:
    """Asigna el stock libre a los pedidos abiertos que CUBRE POR COMPLETO (todo lo que les falta).
    Solo con el reparto automatico activo. Por orden de urgencia y antiguedad; un pedido que el stock
    no cubre entero se salta (no bloquea a los siguientes) y se sigue asignando al llegar piezas.
    Con la expedicion automatica, lo que quede listo sale como siempre (los paquetes, enteros)."""
    config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
    if not (config and config.reparto_automatico):
        return []
    asignados: list[models.Pedido] = []
    for stock_row in db.query(models.Stock).filter(models.Stock.cantidad_actual > 0).all():
        pedidos = (
            db.query(models.Pedido)
            .filter(models.Pedido.producto_id == stock_row.producto_id)
            .filter(models.Pedido.estado.notin_(ESTADOS_NO_ASIGNABLES))
            .order_by(models.Pedido.urgente.desc(), models.Pedido.creado_en.asc(), models.Pedido.id.asc())
            .all()
        )
        for pedido in pedidos:
            db.refresh(stock_row)
            restante = pedido.cantidad_pedida - pedido.cantidad_completada
            if restante > 0 and stock_row.cantidad_actual >= restante:
                _servir_desde_stock(db, pedido)
                db.refresh(pedido)
                asignados.append(pedido)
    if asignados:
        _audit(db, "pedidos", 0, "modificacion", None,
               f"barrido de stock: {', '.join('#%d' % p.id for p in asignados)}")
        _expedir_listos_si_automatico(db, asignados)
        for pedido in asignados:
            db.refresh(pedido)
    return asignados


def _barrer_en_sesion() -> None:
    db = SessionLocal()
    try:
        barrer_stock(db)
    finally:
        db.close()


async def _bucle_barrido() -> None:
    while True:
        await asyncio.sleep(BARRIDO_SEGUNDOS)
        try:
            await asyncio.to_thread(_barrer_en_sesion)
        except Exception as exc:  # un fallo puntual (base ocupada...) no debe parar el barrido
            log_barrido.warning("barrido de stock: %s", exc)


@app.on_event("startup")
async def iniciar_barrido() -> None:
    if BARRIDO_SEGUNDOS > 0:
        asyncio.create_task(_bucle_barrido())


def _con_su_grupo(db: Session, pedidos: list[models.Pedido], solo_abiertos: bool = False) -> list[models.Pedido]:
    """Los pedidos dados MAS los de su mismo grupo (paquete o cesta): se entregan enteros, en un albaran."""
    grupos = {p.grupo_entrega for p in pedidos if p.grupo_entrega is not None}
    if not grupos:
        return pedidos
    query = db.query(models.Pedido).filter(models.Pedido.grupo_entrega.in_(grupos))
    query = query.filter(models.Pedido.estado.in_(ESTADOS_ABIERTOS) if solo_abiertos else models.Pedido.estado != "cancelado")
    ids = {p.id for p in pedidos}
    return pedidos + [m for m in query.order_by(models.Pedido.id).all() if m.id not in ids]


def _pedidos_que_salen_solos(db: Session, pedidos: list[models.Pedido]) -> list[models.Pedido]:
    """Un pedido suelto sale cuando esta 'listo'. Los de un GRUPO (paquete o cesta) solo cuando TODO
    el grupo esta listo, y entonces todos juntos (un albaran por grupo, no uno por pedido)."""
    salen, vistos = [], set()
    for p in pedidos:
        if p.grupo_entrega is None:
            if p.estado == "listo":
                salen.append(p)
        elif p.grupo_entrega not in vistos:
            vistos.add(p.grupo_entrega)
            miembros = _con_su_grupo(db, [p])
            if all(m.cantidad_completada >= m.cantidad_pedida for m in miembros):
                salen.extend(m for m in miembros if m.cantidad_completada > m.cantidad_repartida)
    return salen


def _expedir_listos_si_automatico(
    db: Session, pedidos: list[models.Pedido], usuario_id: int | None = None
) -> list[models.Reparto]:
    """Con la expedicion automatica activa, los pedidos que acaban de quedar
    'listo' (todas sus piezas) salen solos. Solo los completos: entregar cada
    pieza suelta generaria un albaran por cubo."""
    config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
    if not (config and config.expedicion_automatica):
        return []
    listos = _pedidos_que_salen_solos(db, pedidos)
    return _entregar(db, listos, usuario_id, True) if listos else []


def _con_importes(repartos: list[models.Reparto]) -> list[models.Reparto]:
    """Rellena base/IVA/total y desglose por tipo (en centimos) sin guardarlos:
    se derivan de las lineas, asi no pueden desincronizarse. Regla de calculo
    unica con las facturas: ver importes.py."""
    for reparto in repartos:
        for linea in reparto.lineas:
            linea.base_centimos = linea.cantidad * linea.precio_unitario_centimos
        calculo = importes.calcular(reparto.lineas)
        reparto.base_centimos = calculo.base
        reparto.iva_centimos = calculo.iva
        reparto.total_centimos = calculo.total
        reparto.desglose_iva = calculo.desglose
    return repartos


# Contrasena con la que nacen los usuarios sembrados desde el fichero de arranque
# (por ahora 1111, a peticion del usuario). Cada usuario la cambia luego, o se puede
# poner otra al arrancar con TALLER_PASSWORD_INICIAL. No es un secreto: 1111 ya es
# la contrasena maestra de desarrollo.
PASSWORD_INICIAL = os.environ.get("TALLER_PASSWORD_INICIAL", "1111")


def _clientes_iniciales() -> list[datos_arranque.ClienteInicial]:
    """Los del fichero de arranque; si no existe, los de ejemplo del codigo."""
    del_fichero = datos_arranque.leer(datos_arranque.ruta_por_defecto(REPO_DIR))
    if del_fichero is not None:
        return del_fichero
    ejemplo = []
    for razon_social, codigo, cif, usuarios, codigos_producto, fiscal in SEED_CLIENTES:
        ejemplo.append(datos_arranque.ClienteInicial(
            razon_social=razon_social, codigo=codigo, cif=cif, productos=list(codigos_producto), **fiscal,
            usuarios=[datos_arranque.UsuarioInicial(u, rol, sucursal, nombre)
                      for u, nombre, rol, sucursal in usuarios],
        ))
    return ejemplo


@app.on_event("startup")
def sembrar_datos() -> None:
    db = SessionLocal()
    try:
        if db.query(models.Color).count() == 0:
            for codigo, nombre, r, g, b, fisico in SEED_COLORES:
                db.add(models.Color(codigo=codigo, nombre=nombre, r=r, g=g, b=b, fisico=fisico, activo=True))
            db.commit()
        if db.query(models.Producto).count() == 0:
            colores_por_codigo = {c.codigo: c for c in db.query(models.Color).all()}
            productos_por_codigo = {}
            for nombre, codigo, codigo_led, grupo in SEED_PRODUCTOS:
                led = colores_por_codigo.get(codigo_led) if codigo_led else None
                producto = models.Producto(
                    nombre=nombre, codigo=codigo, grupo_cadena=grupo,
                    id_led=led.id if led else None, activo=True,
                )
                db.add(producto)
                productos_por_codigo[codigo] = producto
            db.commit()
            for codigo_producto, nombre, codigo, precio_centimos in SEED_SUBPRODUCTOS:
                db.add(models.Subproducto(
                    producto_id=productos_por_codigo[codigo_producto].id,
                    nombre=nombre, codigo=codigo, activo=True,
                    precio_centimos=precio_centimos,
                ))
            db.commit()
            subproductos_por_clave = {
                (s.producto_id, s.codigo): s for s in db.query(models.Subproducto).all()
            }
            for nombre, codigo, componentes, precio_paquete in SEED_PAQUETES:
                paquete = models.Paquete(nombre=nombre, codigo=codigo, activo=True, precio_centimos=precio_paquete)
                db.add(paquete)
                db.flush()
                for codigo_producto, codigo_subproducto, cantidad in componentes:
                    sub = subproductos_por_clave[
                        (productos_por_codigo[codigo_producto].id, codigo_subproducto)
                    ]
                    db.add(models.PaqueteComponente(
                        paquete_id=paquete.id, subproducto_id=sub.id, cantidad=cantidad,
                    ))
            db.commit()
        if db.query(models.Cliente).count() == 0:
            datos_arranque.cargar(db, _clientes_iniciales(), auth.hash_password(PASSWORD_INICIAL))
        # Clientes de bases anteriores a los codigos: se les da uno (sin renombrar a sus usuarios).
        for linea in codigos.asignar_faltantes(db):
            log.info("CODIGO de cliente asignado: %s", linea)
        try:
            db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_clientes_codigo ON clientes (codigo)"))
            db.commit()
        except Exception:  # dos clientes con el mismo codigo puesto a mano: se avisa, no se cae
            db.rollback()
            log.warning("No he podido crear el indice unico de clientes.codigo: hay codigos repetidos.")
        # OJO (2026-09-16): esto ya NO es "if no hay ningun usuario" -- desde
        # que se siembran usuarios de los SEED_CLIENTES de arriba, puede
        # haber usuarios sin que exista todavia "admin". Se busca por
        # username exacto para no depender del orden de los otros seeds.
        if db.query(models.Usuario).filter(models.Usuario.username == "admin").first() is None:
            admin_password = os.environ.get("TALLER_ADMIN_PASSWORD", "admin")
            db.add(
                models.Usuario(
                    username="admin",
                    nombre_completo="Administrador",
                    rol=auth.ROL_ADMIN_SISTEMA,
                    cliente_id=None,
                    password_hash=auth.hash_password(admin_password),
                    activo=True,
                )
            )
            db.commit()
        else:
            # Migracion de bases de datos ya sembradas antes de este cambio
            # (usuario "aladin" sin password_hash propia, solo entraba con
            # la maestra): lo pasamos a "admin" con contrasena real, una
            # vez, para que el endurecimiento de auth.check_password no
            # deje fuera al admin de siempre.
            legado = (
                db.query(models.Usuario)
                .filter(models.Usuario.username == "aladin")
                .first()
            )
            if legado is not None and legado.username != "admin":
                legado.username = "admin"
                if not legado.password_hash:
                    admin_password = os.environ.get("TALLER_ADMIN_PASSWORD", "admin")
                    legado.password_hash = auth.hash_password(admin_password)
                db.commit()
        if db.query(models.ConfiguracionAlmacen).filter_by(id=1).first() is None:
            db.add(models.ConfiguracionAlmacen(id=1, reparto_automatico=True, expedicion_automatica=True))
            db.commit()
        if db.query(models.Emisor).count() == 0:
            # Base con el emisor UNICO de antes (columnas obsoletas de configuracion_almacen):
            # pasa a la tabla nueva. Si no lo hay, un emisor de EJEMPLO para poder facturar nada
            # mas arrancar: cambiarlo por los datos reales (Administracion > Empresas).
            config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
            if config.emisor_razon_social and config.emisor_cif and config.emisor_direccion:
                db.add(models.Emisor(razon_social=config.emisor_razon_social, cif=config.emisor_cif,
                                     direccion=config.emisor_direccion, email=config.emisor_email,
                                     por_defecto=True, activo=True))
            else:
                db.add(models.Emisor(razon_social="Virtual Robotic (empresa de ejemplo)", cif="B00000000",
                                     direccion="Calle de Ejemplo 1, 48000 Bilbao (Bizkaia)",
                                     email="facturacion@virtualrobotic.example", por_defecto=True, activo=True))
            db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------- generales


NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate"}
# Sin cache a proposito en todo lo servido aqui: el panel se toca a menudo
# y el navegador se quedaba con la version vieja -- el sintoma es siempre
# el mismo y despista mucho (un boton nuevo que "no aparece", o que no
# responde al clic) hasta que alguien se acuerda de recargar con Ctrl+Shift+R.

# Manuales del repo (proyecto padre, montado solo lectura -- ver
# docker-compose.yml) enlazados desde landing.html "Como esta hecho".
# REPO_DIR ya se resuelve arriba del todo, junto al fallback de VERSION.
MANUALES = {
    "lanzar": REPO_DIR / "LANZAR_PROYECTO.md",
    "taller": REPO_DIR / "Taller_Administracion" / "README.md",
    # 2026-09-26: la parte tecnica del README de la web vive aparte.
    "taller-tecnico": REPO_DIR / "Taller_Administracion" / "DETALLE_TECNICO.md",
    "panda": REPO_DIR / "Lab.Panda 2.4" / "resumen_proyecto_panda.md",
}


@app.get("/")
def landing() -> FileResponse:
    return FileResponse(str(BASE_DIR / "static" / "landing.html"), headers=NO_CACHE)


@app.get("/panel")
def panel() -> FileResponse:
    return FileResponse(str(BASE_DIR / "static" / "panel.html"), headers=NO_CACHE)


@app.get("/manual/{nombre}")
def manual(nombre: str) -> FileResponse:
    # Pagina con el mismo diseno que landing.html -- pinta el markdown en
    # el navegador via JS (ver static/manual.html), leyendo el crudo de
    # /manual/{nombre}/raw. Antes esta misma ruta devolvia el .md sin mas
    # (texto plano, "sin pulir para visitas" tal cual decia la propia
    # landing) -- peticion del usuario 2026-09-16: que sean bonitos de
    # leer, a juego con el resto de la pagina.
    if nombre not in MANUALES:
        raise HTTPException(404, "Manual no encontrado.")
    return FileResponse(str(BASE_DIR / "static" / "manual.html"), headers=NO_CACHE)


@app.get("/manual/{nombre}/raw")
def manual_raw(nombre: str, lang: str = "es") -> FileResponse:
    # Sesion 2026-09-22: el usuario quiere compartir el proyecto, asi que
    # estos tres manuales (antes solo en castellano) tienen ahora traduccion
    # EN/EU -- como fichero hermano "<nombre>.<lang>.md" junto al original
    # (p.ej. LANZAR_PROYECTO.en.md). Es una FOTO FIJA: si el .md en
    # castellano cambia despues, las traducciones no se actualizan solas.
    # Si no existe el fichero del idioma pedido (o lang="es"), cae al
    # castellano -- nunca un 404 solo por pedir un idioma sin traducir.
    ruta = MANUALES.get(nombre)
    if ruta is None or not ruta.exists():
        raise HTTPException(404, "Manual no encontrado.")
    if lang in ("en", "eu"):
        ruta_traducida = ruta.with_name(f"{ruta.stem}.{lang}{ruta.suffix}")
        if ruta_traducida.exists():
            ruta = ruta_traducida
    return FileResponse(str(ruta), media_type="text/markdown; charset=utf-8", headers=NO_CACHE)


@app.get("/manual/{nombre}/assets/{ruta_asset:path}")
def manual_asset(nombre: str, ruta_asset: str) -> FileResponse:
    # Las imagenes que el .md referencia con ruta relativa (ej. "img/x.png")
    # se resuelven respecto a la carpeta del propio fichero, igual que hace
    # GitHub/Gitea al ver el .md directamente -- manual.html reescribe esos
    # <img src> para pasar por aqui (ver static/manual.html), porque si no
    # el navegador los resolveria relativos a /manual/{nombre}, que no
    # existe como ruta de ficheros real.
    ruta_manual = MANUALES.get(nombre)
    if ruta_manual is None:
        raise HTTPException(404, "Manual no encontrado.")
    base_dir = ruta_manual.parent.resolve()
    destino = (base_dir / ruta_asset).resolve()
    try:
        destino.relative_to(base_dir)
    except ValueError:
        raise HTTPException(404, "Recurso no encontrado.")
    if not destino.is_file():
        raise HTTPException(404, "Recurso no encontrado.")
    # Un manual que enlaza a OTRO manual (p.ej. README de la web ->
    # DETALLE_TECNICO.md): se abre con su pagina bonita, no como texto crudo.
    # Tambien sus traducciones hermanas (DETALLE_TECNICO.en.md...): el idioma
    # lo pone luego el selector de la propia pagina del manual.
    for clave, ruta in MANUALES.items():
        hermanas = {ruta.resolve()} | {
            ruta.with_name(f"{ruta.stem}.{lang}{ruta.suffix}").resolve() for lang in ("en", "eu")
        }
        if destino in hermanas:
            return RedirectResponse(f"/manual/{clave}")
    return FileResponse(str(destino), headers=NO_CACHE)


# Plantillas Word de configuracion del taller (2026-09-27, peticion del
# usuario: descargarlas desde la portada y desde Administracion -> Empresas).
# Se leen del repo montado (Documentacion/Plantillas, las genera
# generar_plantillas.py), asi siempre sale la ultima. Lista cerrada: esta
# ruta no debe servir ningun otro fichero del repo.
PLANTILLAS = {
    "Configuracion_Taller_EJEMPLO.docx": REPO_DIR / "Documentacion" / "Plantillas" / "Configuracion_Taller_EJEMPLO.docx",
    "Configuracion_Taller_VACIA.docx": REPO_DIR / "Documentacion" / "Plantillas" / "Configuracion_Taller_VACIA.docx",
}


@app.get("/plantillas/{nombre}")
def plantilla(nombre: str) -> FileResponse:
    ruta = PLANTILLAS.get(nombre)
    if ruta is None or not ruta.is_file():
        raise HTTPException(404, "Plantilla no encontrada.")
    return FileResponse(
        str(ruta),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=nombre,
        headers=NO_CACHE,
    )


@app.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    username_norm = payload.username.strip().lower()
    usuario = (
        db.query(models.Usuario).filter(models.Usuario.username == username_norm).first()
    )
    if usuario is None or not usuario.activo or not auth.check_password(payload.password, usuario):
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")
    token = auth.create_session(usuario.id)
    return schemas.LoginResponse(token=token, usuario=usuario)


@app.post("/logout")
def logout(x_session_token: str | None = Header(default=None)):
    if x_session_token:
        auth.destroy_session(x_session_token)
    return {"ok": True}


@app.get("/me", response_model=schemas.UsuarioOut)
def me(usuario: models.Usuario = Depends(auth.get_current_usuario)):
    return usuario


@app.get("/paleta_colores")
def paleta_colores(db: Session = Depends(get_db)):
    return _paleta_colores_dict(db)


@app.get("/version")
def version():
    return {"version": VERSION}


# ---------------------------------------------------------------- productos


@app.get("/productos", response_model=list[schemas.ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).order_by(models.Producto.id).all()


def _validar_id_led(db: Session, id_led: int | None, producto_id: int | None = None) -> None:
    """id_led es opcional (sesion 2026-09-15) pero, si se manda, tiene que
    existir y no estar ya en uso por otro producto activo -- mismo
    criterio de unicidad que tenia 'color' antes."""
    if id_led is None:
        return
    color = db.query(models.Color).filter(models.Color.id == id_led).first()
    if color is None or not color.activo:
        raise HTTPException(400, "El LED indicado no existe o esta de baja.")
    query = db.query(models.Producto).filter(
        models.Producto.id_led == id_led, models.Producto.activo == True  # noqa: E712
    )
    if producto_id is not None:
        query = query.filter(models.Producto.id != producto_id)
    if query.first():
        raise HTTPException(400, f"El LED '{color.codigo}' ya lo usa otro producto.")


@app.post("/productos", response_model=schemas.ProductoOut)
def crear_producto(
    payload: schemas.ProductoCreate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(400, "El nombre no puede estar vacio.")
    codigo = payload.codigo.strip().upper()
    if not _codigo_valido(codigo, 3):
        raise HTTPException(400, "El codigo de producto tiene que ser alfanumerico de 3 caracteres.")
    if db.query(models.Producto).filter(models.Producto.nombre == nombre).first():
        raise HTTPException(400, f"Ya existe un producto llamado '{nombre}'.")
    if db.query(models.Producto).filter(models.Producto.codigo == codigo).first():
        raise HTTPException(400, f"El codigo '{codigo}' ya lo usa otro producto.")
    _validar_id_led(db, payload.id_led)
    grupo = _validar_grupo_cadena(payload.grupo_cadena)
    producto = models.Producto(
        nombre=nombre, codigo=codigo, activo=True, grupo_cadena=grupo, id_led=payload.id_led
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    _audit(db, "productos", producto.id, "alta", usuario.id, f"{nombre} ({codigo}) grupo {grupo}")
    return producto


@app.patch("/productos/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    payload: schemas.ProductoUpdate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    if "nombre" in cambios:
        nombre = (cambios["nombre"] or "").strip()
        if not nombre:
            raise HTTPException(400, "El nombre no puede estar vacio.")
        existente = (
            db.query(models.Producto)
            .filter(models.Producto.nombre == nombre, models.Producto.id != producto_id)
            .first()
        )
        if existente:
            raise HTTPException(400, f"Ya existe un producto llamado '{nombre}'.")
        producto.nombre = nombre
    if "codigo" in cambios:
        codigo = (cambios["codigo"] or "").strip().upper()
        if not _codigo_valido(codigo, 3):
            raise HTTPException(400, "El codigo de producto tiene que ser alfanumerico de 3 caracteres.")
        existente = (
            db.query(models.Producto)
            .filter(models.Producto.codigo == codigo, models.Producto.id != producto_id)
            .first()
        )
        if existente:
            raise HTTPException(400, f"El codigo '{codigo}' ya lo usa otro producto.")
        producto.codigo = codigo
    if "id_led" in cambios:
        _validar_id_led(db, cambios["id_led"], producto_id=producto_id)
        producto.id_led = cambios["id_led"]
    if "activo" in cambios:
        producto.activo = cambios["activo"]
    if cambios.get("grupo_cadena") is not None:
        # Solo afecta a los pedidos que se den de alta A PARTIR de ahora;
        # los que ya existen conservan su numero_maquina.
        producto.grupo_cadena = _validar_grupo_cadena(cambios["grupo_cadena"])
    db.commit()
    db.refresh(producto)
    _audit(db, "productos", producto.id, "modificacion", usuario.id, str(cambios))
    return producto


# ------------------------------------------------------------------- colores


@app.get("/colores", response_model=list[schemas.ColorOut])
def listar_colores(db: Session = Depends(get_db)):
    return db.query(models.Color).order_by(models.Color.id).all()


@app.post("/colores", response_model=schemas.ColorOut)
def crear_color(
    payload: schemas.ColorCreate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    codigo = payload.codigo.strip().upper()
    if not codigo:
        raise HTTPException(400, "El codigo de color no puede estar vacio.")
    # Sesion 2026-09-15, bug real visto en vivo: un codigo "8" (numero) se
    # colo sin avisar y el Loader lo rechazo en seco al lanzar ("only_color
    # no es una letra de color valida", ver loader_demo.py) -- el codigo
    # viaja tal cual como 'only_color' de un parametro ROS2, que exige
    # alfabetico (ademas, una letra sola tipo Y/N se interpretaria como
    # booleano YAML si no fuera por las comillas que ya pone teleop_gui.py).
    if not codigo.isalpha():
        raise HTTPException(
            400, f"El codigo '{codigo}' no es valido: tiene que ser alfabetico (sin numeros ni simbolos)."
        )
    if db.query(models.Color).filter(models.Color.codigo == codigo).first():
        raise HTTPException(400, f"Ya existe un color con codigo '{codigo}'.")
    for campo, valor in (("r", payload.r), ("g", payload.g), ("b", payload.b)):
        if not 0 <= valor <= 255:
            raise HTTPException(400, f"'{campo}' tiene que estar entre 0 y 255.")
    color = models.Color(
        codigo=codigo, nombre=payload.nombre.strip(), r=payload.r, g=payload.g, b=payload.b,
        fisico=payload.fisico, activo=True,
    )
    db.add(color)
    db.commit()
    db.refresh(color)
    _audit(db, "colores", color.id, "alta", usuario.id, codigo)
    return color


@app.patch("/colores/{color_id}", response_model=schemas.ColorOut)
def actualizar_color(
    color_id: int,
    payload: schemas.ColorUpdate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    color = db.query(models.Color).filter(models.Color.id == color_id).first()
    if color is None:
        raise HTTPException(404, "Color no encontrado.")
    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    for campo in ("r", "g", "b"):
        if cambios.get(campo) is not None and not 0 <= cambios[campo] <= 255:
            raise HTTPException(400, f"'{campo}' tiene que estar entre 0 y 255.")
    if "codigo" in cambios:
        nuevo_codigo = (cambios["codigo"] or "").strip().upper()
        if not nuevo_codigo:
            raise HTTPException(400, "El codigo de color no puede estar vacio.")
        if not nuevo_codigo.isalpha():
            raise HTTPException(
                400, f"El codigo '{nuevo_codigo}' no es valido: tiene que ser alfabetico (sin numeros ni simbolos)."
            )
        existente = (
            db.query(models.Color)
            .filter(models.Color.codigo == nuevo_codigo, models.Color.id != color_id)
            .first()
        )
        if existente:
            raise HTTPException(400, f"Ya existe un color con codigo '{nuevo_codigo}'.")
        color.codigo = nuevo_codigo
    for campo in ("nombre", "r", "g", "b", "fisico", "activo"):
        if campo in cambios:
            setattr(color, campo, cambios[campo])
    db.commit()
    db.refresh(color)
    _audit(db, "colores", color.id, "modificacion", usuario.id, str(cambios))
    return color


# --------------------------------------------------------------- subproductos


@app.get("/subproductos", response_model=list[schemas.SubproductoOut])
def listar_subproductos(producto_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Subproducto)
    if producto_id is not None:
        query = query.filter(models.Subproducto.producto_id == producto_id)
    return query.order_by(models.Subproducto.id).all()


@app.post("/subproductos", response_model=schemas.SubproductoOut)
def crear_subproducto(
    payload: schemas.SubproductoCreate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if producto is None or not producto.activo:
        raise HTTPException(400, "El producto no existe o esta de baja.")
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(400, "El nombre no puede estar vacio.")
    codigo = payload.codigo.strip().upper()
    if not _codigo_valido(codigo, 4):
        raise HTTPException(400, "El codigo de subproducto tiene que ser alfanumerico de 4 caracteres.")
    existente = (
        db.query(models.Subproducto)
        .filter(models.Subproducto.producto_id == producto.id, models.Subproducto.codigo == codigo)
        .first()
    )
    if existente:
        raise HTTPException(400, f"'{producto.nombre}' ya tiene un subproducto con codigo '{codigo}'.")
    _validar_precio_iva(payload.precio_centimos, payload.iva_porcentaje)
    subproducto = models.Subproducto(
        producto_id=producto.id, nombre=nombre, codigo=codigo, activo=True,
        precio_centimos=payload.precio_centimos, iva_porcentaje=payload.iva_porcentaje,
    )
    db.add(subproducto)
    db.commit()
    db.refresh(subproducto)
    _audit(db, "subproductos", subproducto.id, "alta", usuario.id, f"{nombre} ({producto.codigo}{codigo})")
    return subproducto


@app.patch("/subproductos/{subproducto_id}", response_model=schemas.SubproductoOut)
def actualizar_subproducto(
    subproducto_id: int,
    payload: schemas.SubproductoUpdate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    subproducto = db.query(models.Subproducto).filter(models.Subproducto.id == subproducto_id).first()
    if subproducto is None:
        raise HTTPException(404, "Subproducto no encontrado.")
    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    if "nombre" in cambios:
        nombre = (cambios["nombre"] or "").strip()
        if not nombre:
            raise HTTPException(400, "El nombre no puede estar vacio.")
        subproducto.nombre = nombre
    if "codigo" in cambios:
        codigo = (cambios["codigo"] or "").strip().upper()
        if not _codigo_valido(codigo, 4):
            raise HTTPException(400, "El codigo de subproducto tiene que ser alfanumerico de 4 caracteres.")
        existente = (
            db.query(models.Subproducto)
            .filter(
                models.Subproducto.producto_id == subproducto.producto_id,
                models.Subproducto.codigo == codigo,
                models.Subproducto.id != subproducto_id,
            )
            .first()
        )
        if existente:
            raise HTTPException(400, f"Ya hay otro subproducto de este producto con codigo '{codigo}'.")
        subproducto.codigo = codigo
    if "activo" in cambios:
        subproducto.activo = cambios["activo"]
    if "precio_centimos" in cambios or "iva_porcentaje" in cambios:
        precio = cambios.get("precio_centimos", subproducto.precio_centimos)
        iva = cambios.get("iva_porcentaje", subproducto.iva_porcentaje)
        _validar_precio_iva(precio, iva)
        if (precio, iva) != (subproducto.precio_centimos, subproducto.iva_porcentaje):
            contabilidad.registrar_precio(
                db, tipo="tarifa_general", subproducto_id=subproducto.id, usuario_id=usuario.id,
                precio_anterior=subproducto.precio_centimos, precio_nuevo=precio,
                iva_anterior=subproducto.iva_porcentaje, iva_nuevo=iva)
        subproducto.precio_centimos = precio
        subproducto.iva_porcentaje = iva
    db.commit()
    db.refresh(subproducto)
    _audit(db, "subproductos", subproducto.id, "modificacion", usuario.id, str(cambios))
    return subproducto


# ------------------------------------------------------------------ paquetes


@app.get("/paquetes", response_model=list[schemas.PaqueteOut])
def listar_paquetes(db: Session = Depends(get_db)):
    return db.query(models.Paquete).order_by(models.Paquete.id).all()


@app.post("/paquetes", response_model=schemas.PaqueteOut)
def crear_paquete(
    payload: schemas.PaqueteCreate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(400, "El nombre no puede estar vacio.")
    codigo = payload.codigo.strip().upper()
    if not codigo:
        raise HTTPException(400, "El codigo de paquete no puede estar vacio.")
    if db.query(models.Paquete).filter(models.Paquete.codigo == codigo).first():
        raise HTTPException(400, f"Ya existe un paquete con codigo '{codigo}'.")
    if not payload.componentes:
        raise HTTPException(400, "Un paquete necesita al menos un componente.")
    if payload.precio_centimos is not None:
        _validar_precio_iva(payload.precio_centimos, payload.iva_porcentaje)
    paquete = models.Paquete(nombre=nombre, codigo=codigo, activo=True,
                             precio_centimos=payload.precio_centimos, iva_porcentaje=payload.iva_porcentaje)
    db.add(paquete)
    db.flush()
    for c in payload.componentes:
        if c.cantidad <= 0:
            raise HTTPException(400, "La cantidad de cada componente tiene que ser mayor que 0.")
        sub = db.query(models.Subproducto).filter(models.Subproducto.id == c.subproducto_id).first()
        if sub is None or not sub.activo:
            raise HTTPException(400, f"El subproducto {c.subproducto_id} no existe o esta de baja.")
        db.add(models.PaqueteComponente(paquete_id=paquete.id, subproducto_id=c.subproducto_id, cantidad=c.cantidad))
    db.commit()
    db.refresh(paquete)
    _audit(db, "paquetes", paquete.id, "alta", usuario.id, f"{nombre} ({codigo}), {len(payload.componentes)} componentes")
    return paquete


@app.patch("/paquetes/{paquete_id}", response_model=schemas.PaqueteOut)
def actualizar_paquete(
    paquete_id: int,
    payload: schemas.PaqueteUpdate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    paquete = db.query(models.Paquete).filter(models.Paquete.id == paquete_id).first()
    if paquete is None:
        raise HTTPException(404, "Paquete no encontrado.")
    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    if "nombre" in cambios:
        nombre = (cambios["nombre"] or "").strip()
        if not nombre:
            raise HTTPException(400, "El nombre no puede estar vacio.")
        paquete.nombre = nombre
    if "codigo" in cambios:
        codigo = (cambios["codigo"] or "").strip().upper()
        if not codigo:
            raise HTTPException(400, "El codigo de paquete no puede estar vacio.")
        existente = (
            db.query(models.Paquete)
            .filter(models.Paquete.codigo == codigo, models.Paquete.id != paquete_id)
            .first()
        )
        if existente:
            raise HTTPException(400, f"Ya existe un paquete con codigo '{codigo}'.")
        paquete.codigo = codigo
    if "activo" in cambios:
        paquete.activo = cambios["activo"]
    if "precio_centimos" in cambios or "iva_porcentaje" in cambios:
        precio = cambios["precio_centimos"] if "precio_centimos" in cambios else paquete.precio_centimos
        iva = cambios.get("iva_porcentaje", paquete.iva_porcentaje)
        if iva is None:
            iva = paquete.iva_porcentaje
        if precio is not None:
            _validar_precio_iva(precio, iva)
        if (precio, iva) != (paquete.precio_centimos, paquete.iva_porcentaje):
            contabilidad.registrar_precio(
                db, tipo="paquete_general", paquete_id=paquete.id, usuario_id=usuario.id,
                precio_anterior=paquete.precio_centimos, precio_nuevo=precio,
                iva_anterior=paquete.iva_porcentaje, iva_nuevo=iva)
        paquete.precio_centimos, paquete.iva_porcentaje = precio, iva
    db.commit()
    db.refresh(paquete)
    _audit(db, "paquetes", paquete.id, "modificacion", usuario.id, str(cambios))
    return paquete


# ----------------------------------------------------------------- usuarios


@app.get("/usuarios", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_SISTEMA, auth.ROL_ADMIN_CLIENTE)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(models.Usuario)
    if usuario.rol == auth.ROL_ADMIN_CLIENTE:
        query = query.filter(models.Usuario.cliente_id == usuario.cliente_id)
    return query.order_by(models.Usuario.id).all()


@app.post("/usuarios", response_model=schemas.UsuarioOut)
def crear_usuario(
    payload: schemas.UsuarioCreate,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_SISTEMA, auth.ROL_ADMIN_CLIENTE)
    ),
    db: Session = Depends(get_db),
):
    if payload.rol not in auth.ROLES_VALIDOS:
        raise HTTPException(400, f"Rol '{payload.rol}' no valido.")
    cliente_id = payload.cliente_id
    if usuario.rol == auth.ROL_ADMIN_CLIENTE:
        if payload.rol in (auth.ROL_ADMIN_SISTEMA, auth.ROL_EMPLEADO):
            raise HTTPException(403, "No puedes crear usuarios de la empresa.")
        cliente_id = usuario.cliente_id
    es_empleado = payload.rol == auth.ROL_EMPLEADO
    if es_empleado:
        # Gente de nuestra empresa: sin cliente, con usuario puesto a mano y
        # con contrasena propia (la clave maestra no les vale, ver auth.check_password).
        cliente_id = None
        if not (payload.username or "").strip():
            raise HTTPException(400, "Un empleado necesita un nombre de usuario (p. ej. antonio).")
        if not payload.password:
            raise HTTPException(400, "Un empleado necesita una contrasena.")
    elif payload.rol != auth.ROL_ADMIN_SISTEMA and cliente_id is None:
        raise HTTPException(400, "Este rol necesita un cliente.")
    # El login busca por username.strip().lower(): se guarda ya normalizado
    # para que un usuario creado con mayusculas pueda entrar. Sin username, se forma con
    # el codigo del cliente y la sucursal (mur-bilbao) o <codigo>-admin.
    username = (payload.username or "").strip().lower()
    if not username:
        cliente_del_usuario = (
            db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first() if cliente_id else None
        )
        if cliente_del_usuario is None or not cliente_del_usuario.codigo:
            raise HTTPException(400, "Falta el usuario: solo se forma solo para los usuarios de un cliente con codigo.")
        try:
            username = codigos.usuario_de(
                cliente_del_usuario.codigo, payload.sucursal, payload.rol == auth.ROL_ADMIN_CLIENTE)
        except codigos.ErrorCodigo as e:
            raise HTTPException(400, str(e))
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        raise HTTPException(409, f"El usuario '{username}' ya existe.")
    nuevo = models.Usuario(
        username=username,
        nombre_completo=payload.nombre_completo,
        rol=payload.rol,
        cliente_id=cliente_id,
        sucursal=payload.sucursal,
        activo=True,
        password_hash=auth.hash_password(payload.password) if payload.password else None,
        permiso_produccion=es_empleado and payload.permiso_produccion,
        permiso_contabilidad=es_empleado and payload.permiso_contabilidad,
        creado_por_id=usuario.id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    _audit(db, "usuarios", nuevo.id, "alta", usuario.id, username)
    return nuevo


@app.patch("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    payload: schemas.UsuarioUpdate,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_SISTEMA, auth.ROL_ADMIN_CLIENTE)
    ),
    db: Session = Depends(get_db),
):
    objetivo = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if objetivo is None:
        raise HTTPException(404, "Usuario no encontrado.")
    if not auth.puede_gestionar_cliente(usuario, objetivo.cliente_id):
        raise HTTPException(403, "No tienes permiso para gestionar este usuario.")
    cambios = payload.model_dump(exclude_unset=True)
    if "rol" in cambios:
        if cambios["rol"] not in auth.ROLES_VALIDOS:
            raise HTTPException(400, f"Rol '{cambios['rol']}' no valido.")
        if usuario.rol == auth.ROL_ADMIN_CLIENTE and cambios["rol"] in (auth.ROL_ADMIN_SISTEMA, auth.ROL_EMPLEADO):
            raise HTTPException(403, "No puedes ascender a administrador del sistema.")
        # Empleado = sin cliente: no se convierte un usuario de cliente en empleado
        # ni al reves (se crea uno nuevo); entre admin_sistema y empleado si se puede.
        if (cambios["rol"] == auth.ROL_EMPLEADO) != (objetivo.rol == auth.ROL_EMPLEADO) and objetivo.cliente_id is not None:
            raise HTTPException(400, "Un usuario de un cliente no puede pasar a empleado de la empresa: crea uno nuevo.")
        if objetivo.rol == auth.ROL_EMPLEADO and cambios["rol"] in (auth.ROL_ADMIN_CLIENTE, auth.ROL_NORMAL):
            raise HTTPException(400, "Un empleado no tiene cliente: crea un usuario nuevo en el cliente.")
        objetivo.rol = cambios["rol"]
    for permiso in ("permiso_produccion", "permiso_contabilidad"):
        if cambios.get(permiso) is not None:
            if usuario.rol != auth.ROL_ADMIN_SISTEMA:
                raise HTTPException(403, "Solo el administrador del sistema cambia los permisos.")
            setattr(objetivo, permiso, cambios[permiso])
    if "nombre_completo" in cambios:
        objetivo.nombre_completo = cambios["nombre_completo"]
    if "sucursal" in cambios:
        objetivo.sucursal = cambios["sucursal"]
    if cambios.get("password"):
        objetivo.password_hash = auth.hash_password(cambios["password"])
    dado_de_baja = False
    if "activo" in cambios:
        objetivo.activo = cambios["activo"]
        dado_de_baja = cambios["activo"] is False
    objetivo.modificado_en = datetime.datetime.utcnow()
    objetivo.modificado_por_id = usuario.id
    db.commit()
    db.refresh(objetivo)
    _audit(
        db,
        "usuarios",
        objetivo.id,
        "baja" if dado_de_baja else "modificacion",
        usuario.id,
        str(cambios),
    )
    return objetivo


# ----------------------------------------------------------------- clientes


@app.get("/clientes", response_model=list[schemas.ClienteOut])
def listar_clientes(
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    query = db.query(models.Cliente)
    if not auth.es_interno(usuario):
        query = query.filter(models.Cliente.id == usuario.cliente_id)
    return query.order_by(models.Cliente.id).all()


@app.post("/clientes", response_model=schemas.ClienteOut)
def crear_cliente(
    payload: schemas.ClienteCreate,
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    # Codigo del cliente: el que llegue (3 letras/cifras, sin repetir) o uno sacado de la razon social.
    ocupados = {c for (c,) in db.query(models.Cliente.codigo).filter(models.Cliente.codigo.isnot(None)).all()}
    try:
        if payload.codigo and payload.codigo.strip():
            codigo = codigos.normalizar_codigo(payload.codigo)
            if codigo in ocupados:
                raise HTTPException(409, f"El codigo '{codigo}' ya es de otro cliente.")
        else:
            codigo = codigos.sugerir_codigo(payload.razon_social, ocupados)
    except codigos.ErrorCodigo as e:
        raise HTTPException(400, str(e))
    # El login busca por username.strip().lower(): se guarda ya normalizado. Sin usuario, <codigo>-admin.
    primer_username = (payload.primer_usuario.username or "").strip().lower() or codigos.usuario_de(codigo, None, True)
    if db.query(models.Usuario).filter(models.Usuario.username == primer_username).first():
        raise HTTPException(409, f"El usuario '{primer_username}' ya existe.")
    cliente = models.Cliente(
        razon_social=payload.razon_social,
        codigo=codigo,
        cif=payload.cif,
        direccion=payload.direccion,
        codigo_postal=payload.codigo_postal,
        poblacion=payload.poblacion,
        provincia=payload.provincia,
        email_facturacion=payload.email_facturacion,
        activo=True,
        creado_por_id=usuario.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    _audit(db, "clientes", cliente.id, "alta", usuario.id, payload.razon_social)

    primer_usuario = models.Usuario(
        username=primer_username,
        nombre_completo=payload.primer_usuario.nombre_completo,
        rol=auth.ROL_ADMIN_CLIENTE,
        cliente_id=cliente.id,
        activo=True,
        password_hash=(
            auth.hash_password(payload.primer_usuario.password)
            if payload.primer_usuario.password
            else None
        ),
        creado_por_id=usuario.id,
    )
    db.add(primer_usuario)
    db.commit()
    db.refresh(primer_usuario)
    _audit(db, "usuarios", primer_usuario.id, "alta", usuario.id, primer_username)
    return cliente


@app.patch("/clientes/{cliente_id}", response_model=schemas.ClienteOut)
def actualizar_cliente(
    cliente_id: int,
    payload: schemas.ClienteUpdate,
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(404, "Cliente no encontrado.")
    if not auth.puede_gestionar_cliente(usuario, cliente_id):
        raise HTTPException(403, "No tienes permiso para gestionar este cliente.")
    cambios = payload.model_dump(exclude_unset=True)
    if "activo" in cambios and usuario.rol != auth.ROL_ADMIN_SISTEMA:
        raise HTTPException(403, "Solo un administrador del sistema puede cambiar el alta/baja.")
    if "razon_social" in cambios:
        cliente.razon_social = cambios["razon_social"]
    if cambios.get("codigo") and cambios["codigo"].strip():
        if usuario.rol != auth.ROL_ADMIN_SISTEMA:
            raise HTTPException(403, "Solo un administrador del sistema puede cambiar el codigo del cliente.")
        try:
            nuevo_codigo = codigos.normalizar_codigo(cambios["codigo"])
        except codigos.ErrorCodigo as e:
            raise HTTPException(400, str(e))
        otro = db.query(models.Cliente).filter(
            models.Cliente.codigo == nuevo_codigo, models.Cliente.id != cliente.id).first()
        if otro is not None:
            raise HTTPException(409, f"El codigo '{nuevo_codigo}' ya es de '{otro.razon_social}'.")
        cliente.codigo = nuevo_codigo
    if "cif" in cambios:
        cliente.cif = cambios["cif"]
    for campo_fiscal in ("direccion", "codigo_postal", "poblacion", "provincia", "email_facturacion"):
        if campo_fiscal in cambios:
            setattr(cliente, campo_fiscal, (cambios[campo_fiscal] or "").strip() or None)
    if "activo" in cambios:
        cliente.activo = cambios["activo"]
    cliente.modificado_en = datetime.datetime.utcnow()
    cliente.modificado_por_id = usuario.id
    db.commit()
    db.refresh(cliente)
    _audit(db, "clientes", cliente.id, "modificacion", usuario.id, str(cambios))
    return cliente


@app.get("/clientes/{cliente_id}/productos", response_model=list[schemas.ProductoOut])
def productos_de_cliente(
    cliente_id: int,
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    if not (
        auth.puede_gestionar_cliente(usuario, cliente_id) or usuario.cliente_id == cliente_id
        or auth.es_interno(usuario)
    ):
        raise HTTPException(403, "No tienes permiso para ver estos productos.")
    asignaciones = (
        db.query(models.ClienteProducto)
        .filter(models.ClienteProducto.cliente_id == cliente_id)
        .all()
    )
    return [a.producto for a in asignaciones]


@app.post("/clientes/{cliente_id}/productos", response_model=list[schemas.ProductoOut])
def asignar_producto(
    cliente_id: int,
    payload: schemas.ClienteProductoAsignar,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_SISTEMA, auth.ROL_ADMIN_CLIENTE)
    ),
    db: Session = Depends(get_db),
):
    if not auth.puede_gestionar_cliente(usuario, cliente_id):
        raise HTTPException(403, "No tienes permiso para gestionar este cliente.")
    producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if producto is None or not producto.activo:
        raise HTTPException(400, "El producto no existe o esta de baja.")
    existente = (
        db.query(models.ClienteProducto)
        .filter_by(cliente_id=cliente_id, producto_id=payload.producto_id)
        .first()
    )
    if existente is None:
        db.add(
            models.ClienteProducto(
                cliente_id=cliente_id,
                producto_id=payload.producto_id,
                asignado_por_id=usuario.id,
            )
        )
        db.commit()
    asignaciones = (
        db.query(models.ClienteProducto)
        .filter(models.ClienteProducto.cliente_id == cliente_id)
        .all()
    )
    return [a.producto for a in asignaciones]


@app.delete("/clientes/{cliente_id}/productos/{producto_id}", response_model=list[schemas.ProductoOut])
def quitar_producto(
    cliente_id: int,
    producto_id: int,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_SISTEMA, auth.ROL_ADMIN_CLIENTE)
    ),
    db: Session = Depends(get_db),
):
    if not auth.puede_gestionar_cliente(usuario, cliente_id):
        raise HTTPException(403, "No tienes permiso para gestionar este cliente.")
    db.query(models.ClienteProducto).filter_by(
        cliente_id=cliente_id, producto_id=producto_id
    ).delete()
    db.commit()
    asignaciones = (
        db.query(models.ClienteProducto)
        .filter(models.ClienteProducto.cliente_id == cliente_id)
        .all()
    )
    return [a.producto for a in asignaciones]


# ------------------------------------------------------------------ pedidos


def _crear_pedido_de_subproducto(
    db: Session, cliente_id: int, usuario_id: int, subproducto: models.Subproducto,
    cantidad_pedida: int, paquete_origen_id: int | None = None, servir: bool = True,
    paquete_pedido: models.PedidoPaquete | None = None,
) -> models.Pedido:
    """Motor comun de alta de pedido, usado por POST /pedidos, POST
    /pedidos/paquete (uno por componente) y reprocesar_pedido.
    cliente_id/usuario_id van explicitos (no se deducen del usuario que
    hace la llamada): en crear_pedido son el propio solicitante, pero en
    reprocesar_pedido el pedido nuevo tiene que seguir siendo del cliente
    y usuario ORIGINALES aunque lo reprocese un administrador.
    producto_id se guarda DESNORMALIZADO desde subproducto.producto_id a
    proposito -- ver Pedido en models.py: el motor de reparto
    (_servir_desde_stock, cubo_clasificado...) sigue trabajando por
    producto_id sin cambios."""
    producto = subproducto.producto
    precio, origen_precio = contabilidad.precio_para(db, cliente_id, subproducto)
    iva = subproducto.iva_porcentaje
    if paquete_pedido is not None and paquete_pedido.precio_unitario_centimos is not None:
        # Componente de un paquete CON precio propio: el precio esta en el paquete, no en el producto.
        precio, origen_precio, iva = 0, "paquete", paquete_pedido.iva_porcentaje
    pedido = models.Pedido(
        subproducto_id=subproducto.id,
        producto_id=producto.id,
        paquete_origen_id=paquete_origen_id,
        cliente_id=cliente_id,
        usuario_id=usuario_id,
        cantidad_pedida=cantidad_pedida,
        cantidad_completada=0,
        cantidad_repartida=0,
        estado="pendiente",
        urgente=False,
        # Precio de hoy (tarifa del cliente si la tiene, si no la general),
        # congelado: ver Pedido.precio_unitario_centimos y contabilidad.py.
        precio_unitario_centimos=precio,
        iva_porcentaje=iva,
        precio_origen=origen_precio,
        paquete_pedido_id=paquete_pedido.id if paquete_pedido is not None else None,
        # Nace a nombre del Grupo Cadena del producto (0 = libre).
        numero_maquina=producto.grupo_cadena,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    if servir:  # un pedido de paquete espera a tener a todos sus hermanos (ver crear_pedido_paquete)
        _servir_y_expedir(db, [pedido])
    return pedido


def _nuevo_pedido_paquete(db: Session, cliente_id: int, paquete: models.Paquete, cantidad: int) -> models.PedidoPaquete:
    """UN paquete pedido, con su precio de hoy congelado (tarifa del cliente o general; None = sin
    precio propio). Se crea antes que sus componentes, que apuntan a el."""
    precio, origen = contabilidad.precio_para_paquete(db, cliente_id, paquete)
    pp = models.PedidoPaquete(
        paquete_id=paquete.id, cliente_id=cliente_id, cantidad=cantidad, cantidad_repartida=0,
        precio_unitario_centimos=precio, iva_porcentaje=paquete.iva_porcentaje, precio_origen=origen)
    db.add(pp)
    db.flush()
    return pp


@app.post("/pedidos", response_model=schemas.PedidoOut)
def crear_pedido(
    payload: schemas.PedidoCreate,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_CLIENTE, auth.ROL_NORMAL)
    ),
    db: Session = Depends(get_db),
):
    subproducto = (
        db.query(models.Subproducto).filter(models.Subproducto.id == payload.subproducto_id).first()
    )
    if subproducto is None or not subproducto.activo:
        raise HTTPException(400, "El subproducto no existe o esta de baja.")
    producto = subproducto.producto
    if not producto.activo:
        raise HTTPException(400, "El producto de este subproducto esta de baja.")
    if payload.cantidad_pedida <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor que 0.")
    asignado = (
        db.query(models.ClienteProducto)
        .filter_by(cliente_id=usuario.cliente_id, producto_id=producto.id)
        .first()
    )
    if asignado is None:
        raise HTTPException(403, "Este producto no esta asignado a tu empresa.")
    pedido = _crear_pedido_de_subproducto(
        db, usuario.cliente_id, usuario.id, subproducto, payload.cantidad_pedida
    )
    _audit(
        db, "pedidos", pedido.id, "alta", usuario.id,
        f"{producto.nombre} {subproducto.nombre} x{payload.cantidad_pedida}",
    )
    return _con_stock_disponible(db, [pedido])[0]


@app.post("/pedidos/multiple", response_model=list[schemas.PedidoOut])
def crear_pedido_multiple(
    payload: schemas.PedidoMultipleCreate,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_CLIENTE, auth.ROL_NORMAL)
    ),
    db: Session = Depends(get_db),
):
    """La CESTA: productos sueltos y/o paquetes pedidos de una vez. Genera un Pedido por linea (y uno
    por componente de cada paquete), todos del mismo grupo de entrega, que salen JUNTOS en UN solo
    albaran cuando estan todos listos. Se valida todo antes de crear nada: o se crea todo, o nada.
    Dos lineas del mismo subproducto se suman; un subproducto que viene de un paquete se mantiene
    aparte del pedido suelto (conserva su paquete)."""
    if not payload.lineas and not payload.paquetes:
        raise HTTPException(400, "Anade al menos un producto o un paquete al pedido.")
    if len(payload.lineas) + len(payload.paquetes) > 50:
        raise HTTPException(400, "Demasiadas lineas en un solo pedido (maximo 50).")

    def comprobar(subproducto: models.Subproducto | None, etiqueta: str) -> None:
        if subproducto is None or not subproducto.activo or not subproducto.producto.activo:
            raise HTTPException(400, f"{etiqueta} no existe o esta de baja.")
        asignado = (
            db.query(models.ClienteProducto)
            .filter_by(cliente_id=usuario.cliente_id, producto_id=subproducto.producto.id)
            .first()
        )
        if asignado is None:
            raise HTTPException(403, f"'{subproducto.producto.nombre}' no esta asignado a tu empresa.")

    sueltos: dict[int, list] = {}          # subproducto_id -> [subproducto, cantidad]
    paquetes: dict[int, list] = {}         # paquete_id -> [paquete, cantidad de paquetes]
    for linea in payload.lineas:
        if linea.cantidad_pedida <= 0:
            raise HTTPException(400, "La cantidad de cada linea debe ser mayor que 0.")
        sub = db.query(models.Subproducto).filter(models.Subproducto.id == linea.subproducto_id).first()
        comprobar(sub, f"El subproducto {linea.subproducto_id}")
        sueltos.setdefault(sub.id, [sub, 0])[1] += linea.cantidad_pedida
    for linea in payload.paquetes:
        if linea.cantidad <= 0:
            raise HTTPException(400, "La cantidad de cada paquete debe ser mayor que 0.")
        paquete = db.query(models.Paquete).filter(models.Paquete.id == linea.paquete_id).first()
        if paquete is None or not paquete.activo:
            raise HTTPException(400, f"El paquete {linea.paquete_id} no existe o esta de baja.")
        if not paquete.componentes:
            raise HTTPException(400, f"El paquete '{paquete.nombre}' no tiene componentes.")
        for comp in paquete.componentes:
            comprobar(comp.subproducto, f"'{comp.subproducto.nombre}' (del paquete '{paquete.nombre}')")
        paquetes.setdefault(paquete.id, [paquete, 0])[1] += linea.cantidad

    pedidos = []
    total_lineas = len(sueltos) + len(paquetes)
    for subproducto, cantidad in sueltos.values():
        pedido = _crear_pedido_de_subproducto(
            db, usuario.cliente_id, usuario.id, subproducto, cantidad, servir=False)
        pedidos.append(pedido)
        _audit(db, "pedidos", pedido.id, "alta", usuario.id,
               f"cesta de {total_lineas} linea(s) -- {subproducto.producto.nombre} {subproducto.nombre} x{cantidad}")
    for paquete, cantidad in paquetes.values():
        pp = _nuevo_pedido_paquete(db, usuario.cliente_id, paquete, cantidad)
        for comp in paquete.componentes:
            pedido = _crear_pedido_de_subproducto(
                db, usuario.cliente_id, usuario.id, comp.subproducto, cantidad * comp.cantidad,
                paquete_origen_id=paquete.id, servir=False, paquete_pedido=pp)
            pedidos.append(pedido)
            _audit(db, "pedidos", pedido.id, "alta", usuario.id,
                   f"cesta de {total_lineas} linea(s) -- {comp.subproducto.nombre} x{pedido.cantidad_pedida} (paquete {paquete.nombre} x{cantidad})")
    if len(pedidos) >= 2:  # un solo pedido es un pedido normal, sin grupo
        for pedido in pedidos:
            pedido.grupo_entrega = pedidos[0].id
        db.commit()
    _servir_y_expedir(db, pedidos)
    return _con_stock_disponible(db, pedidos)


@app.post("/pedidos/paquete", response_model=list[schemas.PedidoOut])
def crear_pedido_paquete(
    payload: schemas.PedidoPorPaqueteCreate,
    usuario: models.Usuario = Depends(
        auth.require_roles(auth.ROL_ADMIN_CLIENTE, auth.ROL_NORMAL)
    ),
    db: Session = Depends(get_db),
):
    """Pedir un Paquete no crea nada de stock propio: genera un Pedido
    normal por cada componente (misma cantidad_pedida = cantidad *
    componente.cantidad), cada uno pasando por las mismas reglas y el
    mismo motor de reparto que un pedido suelto -- ver Paquete en
    models.py."""
    paquete = db.query(models.Paquete).filter(models.Paquete.id == payload.paquete_id).first()
    if paquete is None or not paquete.activo:
        raise HTTPException(400, "El paquete no existe o esta de baja.")
    if payload.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor que 0.")
    if not paquete.componentes:
        raise HTTPException(400, "Este paquete no tiene componentes.")
    # Se valida ANTES de crear nada: o se generan los pedidos de los N
    # componentes, o no se genera ninguno.
    for comp in paquete.componentes:
        producto = comp.subproducto.producto
        if not producto.activo or not comp.subproducto.activo:
            raise HTTPException(400, f"'{producto.nombre} {comp.subproducto.nombre}' esta de baja.")
        asignado = (
            db.query(models.ClienteProducto)
            .filter_by(cliente_id=usuario.cliente_id, producto_id=producto.id)
            .first()
        )
        if asignado is None:
            raise HTTPException(403, f"'{producto.nombre}' no esta asignado a tu empresa.")
    pedidos = []
    pp = _nuevo_pedido_paquete(db, usuario.cliente_id, paquete, payload.cantidad)
    for comp in paquete.componentes:
        pedido = _crear_pedido_de_subproducto(
            db, usuario.cliente_id, usuario.id, comp.subproducto,
            payload.cantidad * comp.cantidad, paquete_origen_id=paquete.id, servir=False,
            paquete_pedido=pp,
        )
        pedidos.append(pedido)
        _audit(
            db, "pedidos", pedido.id, "alta", usuario.id,
            f"paquete {paquete.nombre} x{payload.cantidad} -- {comp.subproducto.nombre} x{pedido.cantidad_pedida}",
        )
    # Todos los componentes de ESTE pedido de paquete comparten grupo (el id del primero): se
    # entregan juntos. Se hace DESPUES de crearlos todos, para que no salga uno suelto antes
    # de que existan sus hermanos.
    for pedido in pedidos:
        pedido.grupo_entrega = pedidos[0].id
    db.commit()
    _servir_y_expedir(db, pedidos)
    return _con_stock_disponible(db, pedidos)


@app.get("/pedidos", response_model=list[schemas.PedidoOut])
def listar_pedidos(
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    if usuario.rol == auth.ROL_EMPLEADO and not auth.es_interno(usuario):
        raise HTTPException(403, "No tienes permiso para esto.")
    query = db.query(models.Pedido)
    if usuario.rol == auth.ROL_NORMAL:
        query = query.filter(models.Pedido.usuario_id == usuario.id)
    elif usuario.rol == auth.ROL_ADMIN_CLIENTE:
        query = query.filter(models.Pedido.cliente_id == usuario.cliente_id)
    pedidos = query.order_by(models.Pedido.creado_en.asc()).all()
    return _con_stock_disponible(db, pedidos)


@app.get("/pedidos/{pedido_id}", response_model=schemas.PedidoOut)
def obtener_pedido(
    pedido_id: int,
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if usuario.rol == auth.ROL_NORMAL and pedido.usuario_id != usuario.id:
        raise HTTPException(403, "No tienes permiso para ver este pedido.")
    if usuario.rol == auth.ROL_ADMIN_CLIENTE and pedido.cliente_id != usuario.cliente_id:
        raise HTTPException(403, "No tienes permiso para ver este pedido.")
    if usuario.rol == auth.ROL_EMPLEADO and not auth.es_interno(usuario):
        raise HTTPException(403, "No tienes permiso para ver este pedido.")
    return _con_stock_disponible(db, [pedido])[0]


@app.patch("/pedidos/{pedido_id}", response_model=schemas.PedidoOut)
def actualizar_pedido(
    pedido_id: int,
    payload: schemas.PedidoUpdate,
    usuario: models.Usuario = Depends(
        auth.require_permiso(auth.PRODUCCION, roles_extra=(auth.ROL_ADMIN_CLIENTE,))
    ),
    db: Session = Depends(get_db),
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if not (auth.tiene_permiso(usuario, auth.PRODUCCION) or auth.puede_gestionar_cliente(usuario, pedido.cliente_id)):
        raise HTTPException(403, "No tienes permiso para gestionar este pedido.")
    pedido.urgente = payload.urgente
    db.commit()
    db.refresh(pedido)
    return _con_stock_disponible(db, [pedido])[0]


@app.post("/pedidos/{pedido_id}/cancelar", response_model=schemas.PedidoOut)
def cancelar_pedido(
    pedido_id: int,
    usuario: models.Usuario = Depends(
        auth.require_permiso(auth.PRODUCCION, roles_extra=(auth.ROL_ADMIN_CLIENTE,))
    ),
    db: Session = Depends(get_db),
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if not (auth.tiene_permiso(usuario, auth.PRODUCCION) or auth.puede_gestionar_cliente(usuario, pedido.cliente_id)):
        raise HTTPException(403, "No tienes permiso para gestionar este pedido.")
    if pedido.estado != "pendiente":
        raise HTTPException(
            400,
            f"Solo se puede cancelar un pedido 'pendiente' -- este esta '{pedido.estado}' "
            f"({pedido.cantidad_completada}/{pedido.cantidad_pedida} ya fabricadas).",
        )
    pedido.estado = "cancelado"
    db.commit()
    db.refresh(pedido)
    _audit(db, "pedidos", pedido.id, "baja", usuario.id, "cancelado")
    return _con_stock_disponible(db, [pedido])[0]


@app.post("/pedidos/{pedido_id}/reclamar", response_model=schemas.PedidoOut)
def reclamar_pedido(
    pedido_id: int,
    payload: schemas.PedidoReclamar,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    """Marca un pedido como asignado a una maquina/celda concreta -- ver
    Pedido.numero_maquina y Documentacion/analisis_ampliacion_taller.md.
    Con una sola celda (estado actual del proyecto) siempre tiene exito;
    la comprobacion de abajo es la que hace que, con dos o mas, no puedan
    quedarse el mismo pedido las dos a la vez."""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if payload.numero_maquina <= 0:
        raise HTTPException(400, "numero_maquina tiene que ser mayor que 0 (0 significa libre).")
    if payload.forzar:
        pedido.numero_maquina = payload.numero_maquina
        db.commit()
    else:
        # UPDATE condicionado (no "leo, comparo en Python, escribo" en dos
        # pasos): solo escribe si sigue libre (0), ya era mio, o esta a
        # nombre de mi grupo (sesion 2026-09-14, ver PedidoReclamar). Es lo
        # que evita que dos maquinas preguntando casi a la vez se queden las
        # dos con el mismo pedido: la primera lo pasa a su numero y la
        # segunda ya no lo encuentra con el numero del grupo.
        reclamables = {0, payload.numero_maquina}
        if payload.grupo_cadena > 0:
            reclamables.add(payload.grupo_cadena)
        filas = (
            db.query(models.Pedido)
            .filter(
                models.Pedido.id == pedido_id,
                models.Pedido.numero_maquina.in_(sorted(reclamables)),
            )
            .update({"numero_maquina": payload.numero_maquina})
        )
        db.commit()
        if filas == 0:
            db.refresh(pedido)
            raise HTTPException(
                409, f"Este pedido ya esta asignado a la maquina nº {pedido.numero_maquina}."
            )
    db.refresh(pedido)
    return _con_stock_disponible(db, [pedido])[0]


@app.post("/pedidos/{pedido_id}/liberar", response_model=schemas.PedidoOut)
def liberar_pedido(
    pedido_id: int,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    """Vuelve a poner numero_maquina a 0 (libre) -- para el caso de una
    maquina que se cayo con un pedido reclamado a su nombre y necesita
    liberarse a mano. Sin condicion: administracion manda."""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    pedido.numero_maquina = 0
    db.commit()
    db.refresh(pedido)
    return _con_stock_disponible(db, [pedido])[0]


@app.post("/pedidos/{pedido_id}/reprocesar", response_model=schemas.PedidoOut)
def reprocesar_pedido(
    pedido_id: int,
    usuario: models.Usuario = Depends(
        auth.require_permiso(auth.PRODUCCION, roles_extra=(auth.ROL_ADMIN_CLIENTE,))
    ),
    db: Session = Depends(get_db),
):
    """Vuelve a mandar al taller un lote ya completado.

    Crea un pedido NUEVO identico (mismo producto, cliente, solicitante y
    cantidad) en vez de reabrir el viejo: asi el historico de que aquel lote
    SE FABRICO de verdad no se pierde, y el reproceso se puede cancelar como
    cualquier otro pedido si era un error. Pasa por las mismas reglas que un
    pedido normal (producto activo, asignado al cliente, y reparto_automatico
    como unico gate para servirlo desde stock) -- si hay stock suficiente en
    almacen y el reparto automatico esta activo, se sirve de ahi en vez de
    fabricarlo, igual que cualquier pedido nuevo.
    """
    original = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if original is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if not (auth.tiene_permiso(usuario, auth.PRODUCCION) or auth.puede_gestionar_cliente(usuario, original.cliente_id)):
        raise HTTPException(403, "No tienes permiso para gestionar este pedido.")
    if original.estado != "completado":
        raise HTTPException(
            400,
            f"Solo se puede volver a procesar un pedido ya completado -- "
            f"este esta '{original.estado}'.",
        )
    subproducto = (
        db.query(models.Subproducto).filter(models.Subproducto.id == original.subproducto_id).first()
    )
    if subproducto is None or not subproducto.activo:
        raise HTTPException(
            400, "El subproducto esta de baja: dalo de alta antes de volver a fabricarlo."
        )
    producto = subproducto.producto
    if not producto.activo:
        raise HTTPException(
            400, "El producto esta de baja: dalo de alta antes de volver a fabricarlo."
        )
    asignado = (
        db.query(models.ClienteProducto)
        .filter_by(cliente_id=original.cliente_id, producto_id=producto.id)
        .first()
    )
    if asignado is None:
        raise HTTPException(
            403, f"'{producto.nombre}' ya no esta asignado al catalogo de esa empresa."
        )

    # Grupo ACTUAL del producto, no el del pedido original (que ademas ya
    # tendra el numero de la maquina que lo fabrico) -- ver
    # _crear_pedido_de_subproducto.
    nuevo = _crear_pedido_de_subproducto(
        db, original.cliente_id, original.usuario_id, subproducto, original.cantidad_pedida
    )
    _audit(
        db,
        "pedidos",
        nuevo.id,
        "alta",
        usuario.id,
        f"reproceso del pedido {original.id} -- {producto.nombre} x{nuevo.cantidad_pedida}",
    )
    return _con_stock_disponible(db, [nuevo])[0]


# ------------------------------------------------------------- celda -> taller


@app.post("/taller/cubo_clasificado", response_model=schemas.CuboClasificadoResultado)
def cubo_clasificado(payload: schemas.CuboClasificado, db: Session = Depends(get_db)):
    color = payload.color.upper()
    # Resolucion del producto (sesion 2026-09-15, peticion explicita del
    # usuario: el LED no puede ser un requisito para que esto funcione).
    # Prioridad: pedido_id (el pedido YA dice de que producto es) >
    # producto_id (el llamante ya lo identifico) > color/LED (compatibilidad
    # con llamadas que no conocen todavia el producto exacto).
    producto = None
    if payload.pedido_id is not None:
        pedido_ref = db.query(models.Pedido).filter(models.Pedido.id == payload.pedido_id).first()
        if pedido_ref is not None:
            producto = db.query(models.Producto).filter(models.Producto.id == pedido_ref.producto_id).first()
    if producto is None and payload.producto_id is not None:
        producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if producto is None:
        color_row = db.query(models.Color).filter(
            models.Color.codigo == color, models.Color.activo == True  # noqa: E712
        ).first()
        if color_row is None:
            raise HTTPException(400, f"Color '{color}' no valido.")
        producto = db.query(models.Producto).filter(models.Producto.id_led == color_row.id).first()
    if producto is None:
        raise HTTPException(404, f"No hay producto para el color '{color}'.")

    stock_row = db.query(models.Stock).filter_by(producto_id=producto.id).first()
    if stock_row is None:
        stock_row = models.Stock(producto_id=producto.id, cantidad_actual=0)
        db.add(stock_row)
        db.flush()
    stock_row.cantidad_actual += 1
    stock_row.actualizado_en = datetime.datetime.utcnow()
    db.add(
        models.MovimientoStock(
            producto_id=producto.id, tipo="entrada", cantidad=1, motivo="produccion"
        )
    )
    db.commit()

    pedido_resultado = None
    config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
    if config and config.reparto_automatico:
        # Pedidos a los que puede ir esta pieza (ver CuboClasificado.numero_maquina):
        # sin maquina, cualquiera; con maquina, solo los suyos o los de su grupo.
        def _pedidos_de_quien_fabrica(query):
            if payload.numero_maquina is None:
                return query
            return query.filter(
                models.Pedido.numero_maquina.in_(sorted({payload.numero_maquina, payload.grupo_cadena}))
            )

        candidato = None
        if payload.pedido_id is not None:
            candidato = _pedidos_de_quien_fabrica(
                db.query(models.Pedido)
                .filter(models.Pedido.id == payload.pedido_id)
                .filter(models.Pedido.producto_id == producto.id)
                .filter(models.Pedido.estado.notin_(ESTADOS_NO_ASIGNABLES))
            ).first()
        if candidato is None:
            orden = [models.Pedido.urgente.desc(), models.Pedido.creado_en.asc()]
            if payload.numero_maquina is not None:
                # Primero los ya reclamados por esta maquina, luego los del grupo.
                orden.insert(0, (models.Pedido.numero_maquina == payload.numero_maquina).desc())
            candidato = _pedidos_de_quien_fabrica(
                db.query(models.Pedido)
                .filter(models.Pedido.producto_id == producto.id)
                .filter(models.Pedido.estado.notin_(ESTADOS_NO_ASIGNABLES))
            ).order_by(*orden).first()
        if candidato is not None:
            if payload.numero_maquina is not None and candidato.numero_maquina != payload.numero_maquina:
                # Pedido del grupo: pasa a ser de esta maquina, igual que al reclamarlo.
                candidato.numero_maquina = payload.numero_maquina
            stock_row.cantidad_actual -= 1
            stock_row.actualizado_en = datetime.datetime.utcnow()
            candidato.cantidad_completada += 1
            candidato.estado = _estado_pedido(candidato)
            db.add(
                models.MovimientoStock(
                    producto_id=producto.id,
                    tipo="salida",
                    cantidad=1,
                    motivo=MOTIVO_ASIGNACION,
                    pedido_id=candidato.id,
                )
            )
            db.commit()
            db.refresh(candidato)
            _expedir_listos_si_automatico(db, [candidato])
            db.refresh(candidato)
            pedido_resultado = _con_stock_disponible(db, [candidato])[0]

    db.refresh(stock_row)
    return schemas.CuboClasificadoResultado(
        color=color, stock_actual=stock_row.cantidad_actual, pedido=pedido_resultado
    )


@app.post("/taller/evento_produccion", response_model=schemas.EventoProduccionOut)
def evento_produccion(payload: schemas.EventoProduccionCreate, db: Session = Depends(get_db)):
    robot = (payload.robot or "").strip().lower() or "desconocido"
    if payload.tipo not in TIPOS_EVENTO_PRODUCCION:
        raise HTTPException(400, f"Tipo de evento '{payload.tipo}' no valido.")
    evento = models.EventoProduccion(robot=robot, color=payload.color, tipo=payload.tipo)
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


@app.get("/taller/diagnostico", response_model=schemas.DiagnosticoOut)
def diagnostico(
    ventana_minutos: int = 60,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    desde = datetime.datetime.utcnow() - datetime.timedelta(minutes=ventana_minutos)
    productos = db.query(models.Producto).order_by(models.Producto.id).all()
    por_color = []
    for producto in productos:
        # Sin LED asignado, este producto no tiene produccion fisica que
        # cruzar -- se lista igualmente pero sin eventos.
        eventos_ventana = (
            db.query(models.EventoProduccion)
            .filter(models.EventoProduccion.color == producto.led_codigo)
            .filter(models.EventoProduccion.fecha >= desde)
            .all()
            if producto.led_codigo
            else []
        )
        led_loader = sum(
            1 for e in eventos_ventana if e.tipo == "led_encendido" and e.robot == "loader"
        )
        led_sorter = sum(
            1 for e in eventos_ventana if e.tipo == "led_encendido" and e.robot == "sorter"
        )
        agarre_falso = sum(1 for e in eventos_ventana if e.tipo == "agarre_falso")
        limite_alcance = sum(1 for e in eventos_ventana if e.tipo == "limite_alcance")
        fallo_definitivo = sum(1 for e in eventos_ventana if e.tipo == "fallo_definitivo")
        piezas_reales = (
            db.query(models.MovimientoStock)
            .filter(models.MovimientoStock.producto_id == producto.id)
            .filter(models.MovimientoStock.motivo == "produccion")
            .filter(models.MovimientoStock.fecha >= desde)
            .count()
        )
        piezas_reales_total = (
            db.query(models.MovimientoStock)
            .filter(models.MovimientoStock.producto_id == producto.id)
            .filter(models.MovimientoStock.motivo == "produccion")
            .count()
        )
        if fallo_definitivo > 0:
            estado = "critico"
        elif limite_alcance > 0 or agarre_falso > piezas_reales:
            estado = "atencion"
        else:
            estado = "ok"
        por_color.append(
            schemas.DiagnosticoColor(
                color=producto.led_codigo,
                producto_nombre=producto.nombre,
                led_loader=led_loader,
                led_sorter=led_sorter,
                agarre_falso=agarre_falso,
                limite_alcance=limite_alcance,
                fallo_definitivo=fallo_definitivo,
                piezas_reales=piezas_reales,
                piezas_reales_total=piezas_reales_total,
                estado=estado,
            )
        )
    eventos_recientes = (
        db.query(models.EventoProduccion)
        .order_by(models.EventoProduccion.fecha.desc())
        .limit(50)
        .all()
    )
    return schemas.DiagnosticoOut(
        ventana_minutos=ventana_minutos, por_color=por_color, eventos_recientes=eventos_recientes
    )


# ------------------------------------------------------------------- almacen


@app.get("/stock", response_model=list[schemas.StockOut])
def listar_stock(
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    return db.query(models.Stock).order_by(models.Stock.producto_id).all()


@app.get("/movimientos_stock", response_model=list[schemas.MovimientoStockOut])
def listar_movimientos(
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    return db.query(models.MovimientoStock).order_by(models.MovimientoStock.fecha.desc()).all()


@app.post("/almacen/repartir")
def repartir_stock(
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    pedidos_activos = (
        db.query(models.Pedido)
        .filter(models.Pedido.estado.notin_(ESTADOS_NO_ASIGNABLES))
        .order_by(models.Pedido.urgente.desc(), models.Pedido.creado_en.asc())
        .all()
    )
    repartidos = []
    for pedido in pedidos_activos:
        completada_antes = pedido.cantidad_completada
        _servir_desde_stock(db, pedido)
        db.refresh(pedido)
        if pedido.cantidad_completada > completada_antes:
            repartidos.append(pedido)
    if repartidos:
        _audit(
            db,
            "pedidos",
            0,
            "modificacion",
            usuario.id,
            f"asignacion de stock: {len(repartidos)} pedido(s)",
        )
        _expedir_listos_si_automatico(db, repartidos, usuario.id)
        for pedido in repartidos:
            db.refresh(pedido)
    return {"repartidos": _con_stock_disponible(db, repartidos)}


@app.post("/almacen/ajustar", response_model=schemas.StockOut)
def ajustar_stock(
    payload: schemas.AjusteStock,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    if payload.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor que 0.")
    producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    stock_row = db.query(models.Stock).filter_by(producto_id=payload.producto_id).first()
    if stock_row is None:
        stock_row = models.Stock(producto_id=payload.producto_id, cantidad_actual=0)
        db.add(stock_row)
        db.flush()
    stock_row.cantidad_actual += payload.cantidad
    stock_row.actualizado_en = datetime.datetime.utcnow()
    db.add(
        models.MovimientoStock(
            producto_id=payload.producto_id,
            tipo="entrada",
            cantidad=payload.cantidad,
            motivo="ajuste_manual",
            usuario_id=usuario.id,
        )
    )
    db.commit()
    db.refresh(stock_row)
    _audit(db, "stock", payload.producto_id, "modificacion", usuario.id, f"+{payload.cantidad}")
    return stock_row


@app.post("/almacen/quitar", response_model=schemas.StockOut)
def quitar_stock(
    payload: schemas.AjusteStock,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    if payload.cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor que 0.")
    stock_row = db.query(models.Stock).filter_by(producto_id=payload.producto_id).first()
    disponible = stock_row.cantidad_actual if stock_row else 0
    if payload.cantidad > disponible:
        unidad = "unidad" if disponible == 1 else "unidades"
        raise HTTPException(400, f"Solo hay {disponible} {unidad} disponibles.")
    stock_row.cantidad_actual -= payload.cantidad
    stock_row.actualizado_en = datetime.datetime.utcnow()
    db.add(
        models.MovimientoStock(
            producto_id=payload.producto_id,
            tipo="salida",
            cantidad=payload.cantidad,
            motivo="ajuste_manual",
            usuario_id=usuario.id,
        )
    )
    db.commit()
    db.refresh(stock_row)
    _audit(db, "stock", payload.producto_id, "modificacion", usuario.id, f"-{payload.cantidad}")
    return stock_row


@app.get("/almacen/configuracion", response_model=schemas.ConfiguracionAlmacenOut)
def obtener_configuracion(
    usuario: models.Usuario = Depends(auth.get_current_usuario),
    db: Session = Depends(get_db),
):
    return db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()


@app.patch("/almacen/configuracion", response_model=schemas.ConfiguracionAlmacenOut)
def actualizar_configuracion(
    payload: schemas.ConfiguracionAlmacenUpdate,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    cambios = payload.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(400, "No se ha indicado ningun cambio.")
    config = db.query(models.ConfiguracionAlmacen).filter_by(id=1).first()
    if "reparto_automatico" in cambios:
        config.reparto_automatico = cambios["reparto_automatico"]
    activa_expedicion = cambios.get("expedicion_automatica") and not config.expedicion_automatica
    if "expedicion_automatica" in cambios:
        config.expedicion_automatica = cambios["expedicion_automatica"]
    if "factor_piezas" in cambios:
        config.factor_piezas = cambios["factor_piezas"]
    db.commit()
    db.refresh(config)
    _audit(db, "configuracion_almacen", 1, "modificacion", usuario.id, str(cambios))
    if activa_expedicion:
        # Al pasar a automatico, lo que ya esperaba listo sale ahora mismo:
        # si no, se quedaria en la pestana Reparto hasta el siguiente pedido.
        listos = _pedidos_que_salen_solos(
            db, db.query(models.Pedido).filter(models.Pedido.estado == "listo").all())
        _entregar(db, listos, usuario.id, True)
    return config


@app.post("/reparto/expedir", response_model=list[schemas.RepartoOut])
def expedir(
    payload: schemas.ExpedirPedidos,
    usuario: models.Usuario = Depends(auth.require_permiso(auth.PRODUCCION)),
    db: Session = Depends(get_db),
):
    """Reparto manual: entrega lo que hay para los pedidos indicados (o para
    todos). Primero asigna el stock libre que los cubre -- pulsar Repartir en
    un pedido cubierto por el almacen lo asigna y lo entrega de una vez, aunque
    la asignacion automatica este apagada -- y luego genera los albaranes."""
    query = db.query(models.Pedido)
    if payload.pedido_ids is not None:
        ids = set(payload.pedido_ids)
        encontrados = {p.id for p in query.filter(models.Pedido.id.in_(ids)).all()}
        if ids - encontrados:
            raise HTTPException(404, f"Pedido no encontrado: {sorted(ids - encontrados)}")
        query = query.filter(models.Pedido.id.in_(ids))
    pedidos = (
        query.filter(models.Pedido.estado.in_(ESTADOS_ABIERTOS))
        .order_by(models.Pedido.urgente.desc(), models.Pedido.creado_en.asc())
        .all()
    )
    if payload.pedido_ids is not None:
        pedidos = _con_su_grupo(db, pedidos, solo_abiertos=True)  # un paquete se reparte entero
    for pedido in pedidos:
        _servir_desde_stock(db, pedido)
        db.refresh(pedido)
    repartos = _entregar(db, pedidos, usuario.id, False)
    return contabilidad.con_factura(db, _con_importes(repartos))


@app.get("/repartos", response_model=list[schemas.RepartoOut])
def listar_repartos(
    cliente_id: int | None = None,
    limite: int = 200,
    usuario: models.Usuario = Depends(
        auth.require_permiso(auth.PRODUCCION, auth.CONTABILIDAD, roles_extra=(auth.ROL_ADMIN_CLIENTE,))
    ),
    db: Session = Depends(get_db),
):
    query = db.query(models.Reparto)
    if usuario.rol == auth.ROL_ADMIN_CLIENTE:
        query = query.filter(models.Reparto.cliente_id == usuario.cliente_id)
    elif cliente_id is not None:
        query = query.filter(models.Reparto.cliente_id == cliente_id)
    repartos = query.order_by(models.Reparto.fecha.desc(), models.Reparto.id.desc()).limit(limite).all()
    return contabilidad.con_factura(db, _con_importes(repartos))


@app.get("/repartos/{reparto_id}", response_model=schemas.RepartoOut)
def obtener_reparto(
    reparto_id: int,
    usuario: models.Usuario = Depends(
        auth.require_permiso(auth.PRODUCCION, auth.CONTABILIDAD, roles_extra=(auth.ROL_ADMIN_CLIENTE,))
    ),
    db: Session = Depends(get_db),
):
    reparto = db.query(models.Reparto).filter(models.Reparto.id == reparto_id).first()
    if reparto is None:
        raise HTTPException(404, "Albaran no encontrado.")
    if usuario.rol == auth.ROL_ADMIN_CLIENTE and reparto.cliente_id != usuario.cliente_id:
        raise HTTPException(403, "No tienes permiso para ver este albaran.")
    return contabilidad.con_factura(db, _con_importes([reparto]))[0]


@app.get("/audit", response_model=list[schemas.AuditLogOut])
def listar_audit(
    usuario: models.Usuario = Depends(auth.require_roles(auth.ROL_ADMIN_SISTEMA)),
    db: Session = Depends(get_db),
):
    return db.query(models.AuditLog).order_by(models.AuditLog.fecha.desc()).all()
