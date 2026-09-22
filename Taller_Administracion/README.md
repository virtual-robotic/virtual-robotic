# Nuestra web de pedidos

Si es la primera vez que la ves: esto es **la oficina del taller**. Aquí se piden
las piezas, se apunta qué se fabrica, se guarda lo que sobra en el almacén, se
entrega al cliente con su albarán y se factura. Los robots de la celda
(Loader y Sorter) son el **taller** de verdad; esta web es la que les dice
qué hace falta y apunta lo que van haciendo. No hace falta saber nada de
informática para seguir esta página: se cuenta con un pedido de ejemplo, paso a paso.

> Si esta web está apagada, la celda sigue funcionando igual. Lo único que pasa es que
> nadie apunta la producción en ningún pedido.

## El viaje de un pedido, de principio a fin

**🛒 Se pide** → **🏭 Se consigue** (del almacén o fabricándolo) → **✅ Queda listo** → **🚚 Se reparte** (albarán) → **🧾 Se factura**

Un ejemplo: la empresa *Astilleros Murueta* necesita 20 tornillos, 10 tuercas y
un paquete de piezas variadas, y lo pide su sucursal de Bilbao.

### 1. Se pide con la cesta 🛒

**Quién pide.** Lo pide un **usuario de un cliente**. Cada cliente (por ejemplo, Astilleros
Murueta) tiene un usuario administrador y, si quiere, uno por **sucursal** (Bilbao, Barcelona,
Madrid...). Quien necesita piezas abre la web en su navegador (en otra pestaña o en otro
ordenador, da igual), pulsa **Entrar** e identifica su usuario y su contraseña; en el ejemplo, el
usuario `mur-bilbao` de Astilleros Murueta. Al entrar solo ve la pestaña **Pedidos**, y en el desplegable
solo le salen las piezas que su empresa puede pedir. En cada pedido queda apuntado **qué cliente lo pide
y qué usuario lo hizo**; el administrador de la empresa ve los de todas sus sucursales, y el albarán y
la factura salen a nombre del **cliente**, no de la sucursal.

Es como una tienda: eliges un producto **o un paquete entero**, dices cuántos, y lo
metes en la cesta. Cuando la cesta está como quieres, pulsas **Pedir la cesta**.
Todo lo de una cesta viaja junto y saldrá **en un solo albarán**. Un pedido de
una sola cosa es simplemente una cesta con una línea.

![La pantalla de Pedidos: arriba se elige el producto o paquete, en medio está la cesta con tres líneas y debajo los pedidos que ya están en marcha, cada uno con su estado](img/web_1_pedir_cesta.png)

Debajo de la cesta cada pedido va cambiando de estado: *pendiente* (todavía no
se ha empezado), *en proceso* (se están consiguiendo las piezas), *listo para
reparto* (ya están todas, esperando salir) y *repartido* (ya se han entregado).

### 2. Se consigue: del almacén o fabricándolo 🏭

Lo primero que hace el sistema es mirar el **almacén**. Si ya hay piezas guardadas, se
le asignan al pedido al momento y no hace falta fabricar nada. Si no, lo que falta se
apunta en **Pedidos Taller**, que es la lista de la compra de los robots: la celda va
haciendo esas piezas y, según las termina, avisa a la web y el pedido avanza solo.

![La pestaña Pedidos Taller con lo que falta fabricar: 6 tuercas y 10 arandelas](img/web_2_fabricar.png)

Aquí se puede decidir en qué máquina se hace cada pedido, marcarlo como **urgente** o
cancelarlo.

![Los dos robots Panda trabajando en la celda: el Loader a la izquierda dejando cubos en la cinta, el Sorter arriba clasificándolos por color](img/webots_cell.jpg)

Nuestra cadena de producción, la que fabrica esas piezas, se explica en
[Nuestra cadena de producción](/manual/panda).

### 3. Queda listo y se reparte 🚚

Cuando ya están **todas** las piezas del pedido (de una cesta, todas las de la cesta),
llega la segunda etapa: **Reparto**. Se entrega al cliente y se apunta con un **albarán**,
que es el justificante de lo entregado. Tiene dos interruptores: uno para que el stock se
asigne solo a los pedidos, y otro para que lo que ya está listo se entregue solo. Apagado
este último, todo espera aquí hasta que alguien pulse **Repartir**.

![La pestaña Reparto: los interruptores, las piezas listas esperando entrega y los albaranes ya emitidos](img/web_3_reparto.png)

Un **paquete** siempre se entrega entero: si falta una sola pieza, el paquete
espera. Y una cesta espera hasta estar completa, para que el cliente reciba **un solo
albarán** en lugar de tres.

### 4. El albarán 📄

Es la hoja que acompaña a la entrega. Un paquete sale como **un paquete** (con su
precio) y debajo, en pequeño, lo que lleva dentro.

![Albaranes emitidos: el de arriba lleva dos productos y un paquete con sus tres componentes](img/web_4_albaran_emitido.png)

Se puede ver e imprimir (o guardar en PDF) con el logotipo de la empresa, los datos de
quien entrega y de quien recibe, y el importe con su IVA.

![El albarán tal como se imprime: cabecera con el logotipo, cliente, las líneas con su precio y el total](img/web_5_albaran_papel.png)

### 5. Se factura 🧾

Al final del mes (o cuando toque), los albaranes de un cliente que todavía no se han
cobrado se juntan en una **factura**. Se puede marcar todo, marcar los de un cliente, o
elegir albarán a albarán. Si hay un error, la factura no se edita: se anula con otra
**rectificativa** y los albaranes quedan libres para volver a facturarse ya corregidos.
Se puede facturar desde varias empresas, cada una con su numeración.

![La pestaña Facturación: los albaranes pendientes de cada cliente, con casillas para elegir cuáles facturar](img/web_6_facturar.png)

## Quién puede hacer qué

| Quien entra | Qué ve |
|---|---|
| **Usuario normal** (un empleado del cliente) | Solo la pestaña **Pedidos**: pide con la cesta y ve cómo van los suyos |
| **Administrador de una empresa cliente** | Lo anterior de toda su empresa, más sus albaranes y facturas |
| **Administrador del sistema** (el taller) | Todo: producción, contabilidad y los datos de base (productos, clientes, precios...) |

## Cosas que conviene saber

- **Los precios se congelan al pedir.** Si mañana cambia la tarifa, los pedidos ya hechos
  conservan el precio de cuando se pidieron. Cada cliente puede tener sus propios precios.
- **Nada se borra a escondidas.** Cualquier cambio de precio o de estado queda apuntado:
  quién, cuándo y de cuánto a cuánto.
- **El stock no se reparte a escondidas.** Hay un interruptor de *reparto automático*: encendido,
  las piezas guardadas se asignan solas a los pedidos que las necesitan; apagado, se quedan quietas
  hasta que alguien pulse **Asignar stock**.
- **Puedes jugar sin miedo**: es un proyecto de aprendizaje. Los datos de la demo son
  inventados y la contraseña de los usuarios de ejemplo es `1111`.

---

## Para quien quiera bajar al detalle técnico

Servidor web + base de datos de pedidos y almacén de la celda industrial. Es
un proyecto **separado** de la celda: solo se hablan por HTTP. Si está
apagado, la celda sigue funcionando, simplemente nadie apunta la producción.

Stack: FastAPI 0.115.0 + SQLAlchemy 2.0.35 + pydantic 2.9.2 + SQLite, servido
por uvicorn con `--reload`. API interactiva en `/docs`.

## Rutas servidas

- `/` — `app/static/landing.html`: la web de presentación "Virtual Robotic"
  (misma marca/tipografía que `../Virtual_Robotic/index.html`, pero aquí el
  login es de verdad porque esta misma app ya está corriendo).
  La portada se puede leer en **castellano, inglés y euskera** (selector ES/EN/EU de arriba): los textos
  traducidos están en `app/static/i18n_landing.js` (y la copia de `../Virtual_Robotic/`). El sistema de
  pedidos (`/panel`) y sus manuales siguen solo en castellano; el panel de control de los robots
  (`teleop_gui`) ya está en los tres idiomas.
- `/panel` — `app/static/panel.html`: el sistema real (pedidos, almacén,
  usuarios). Comparte sesión con `/` vía `sessionStorage` (`taller_token`,
  `taller_yo`): entra una vez desde la landing y ya no vuelve a pedir login.
- `/manual/{lanzar,taller,panda}` — sirve en crudo `LANZAR_PROYECTO.md`, el
  README de este proyecto y el resumen de `Lab.Panda 2.4`, enlazados desde la
  landing. Requiere el volumen `..:/workspace/repo:ro` del `docker-compose.yml`
  (repo padre montado solo lectura) — fuera de Docker cae solo a la ruta real
  en disco (`TALLER_REPO_DIR`, por defecto dos niveles por encima de `app/`).

## Arranque

```bash
docker compose up -d --build
```

Publica el puerto **8000** del host. `data/taller.db` se crea sola al
arrancar (dentro del volumen `./data`, ignorada por git). La primera vez que
arranca sin base de datos, el servidor siembra (ver `SEED_*` y
`sembrar_datos()` en `app/main.py`) datos de ejemplo para poder jugar sin
tener que dar de alta nada a mano:

- 7 colores de LED (R/G/B con cubo físico, Y/M/C/W solo LED), 3 productos
  (Tornillos/100, Tuercas/200, Arandelas/300) con sus subproductos (variantes
  de 10mm/20mm) y 2 paquetes de ejemplo (P010, P020).
- Los **clientes y usuarios iniciales**, leídos de
  `Documentacion/UsuariosBBDDArranque.txt` (ver "Clientes y usuarios de arranque"
  más abajo), todos con el catálogo completo y la contraseña inicial `1111`. Si ese
  fichero no existe, se siembran 3 empresas de ejemplo del código.
- Usuario `admin` (`admin_sistema`, contraseña `admin` por defecto —
  configurable con `TALLER_ADMIN_PASSWORD`).
- Configuración de almacén con `reparto_automatico = True` y
  `expedicion_automatica = True` (los dos interruptores del reparto, ver
  "Ciclo de un pedido").
- Precios de ejemplo en los subproductos (en céntimos, sin IVA; IVA 21 %) para
  que los albaranes salgan con importes desde el primer arranque, y una empresa
  emisora de ejemplo (para poder facturar; cámbiala en Administración → Empresas).

### Clientes y usuarios de arranque

Una base de datos **vacía** se llena con los clientes y usuarios de
`Documentacion/UsuariosBBDDArranque.txt` (o el fichero que diga
`TALLER_DATOS_ARRANQUE`). Es un texto que se edita a mano:

```
Cliente:
    R.S.: Astilleros Murueta S.L.        <- razón social; empieza un cliente
    Cod.: MUR                            <- OPCIONAL: código de 3 letras/cifras; sin él, sale de la razón social
    Cif : B48111222
    Dir.: Carretera Bermeo 34
    C.P.: 48333
    Pob.: Murueta
    Pro.: Bizkaia
    cor.: administracion@example.com
    Productos: 100, Arandelas             <- OPCIONAL (código o nombre); sin ella, TODOS
        sucursal admin -> Murueta         <- usuario  mur-admin   (administrador de la empresa)
        sucursal -> Bilbao   nombre -> Ana López   <- usuario  mur-bilbao   (nombre OPCIONAL)
        sucursal -> Madrid                <- usuario  mur-madrid
```

- **El usuario sale solo del código del cliente y la sucursal**: `<código>-admin` para el
  administrador de la empresa (`admin_cliente`) y `<código>-<sucursal>` para cada sucursal
  (`normal`). Así dos clientes pueden tener cada uno su sucursal de Bilbao (`mur-bilbao`,
  `ere-bilbao`) sin inventarse nombres, y por el usuario se ve de qué cliente viene un pedido.
  Sin `nombre ->`, el nombre completo es "Administrador <sucursal>" u "Operario <sucursal>".
  La forma antigua, con el usuario escrito a mano (`user normal-> bilbao2 sucursal -> Bilbao`),
  sigue valiendo. Los usuarios se guardan en minúsculas.
- En el panel (**Administración → Clientes**) el código se ve y se cambia (solo el administrador
  del sistema); al dar de alta un usuario, si dejas el usuario vacío se forma igual con el código
  del cliente y la sucursal. Los clientes de una base antigua reciben un código solos, sin
  renombrar a sus usuarios.
- Todos nacen con la contraseña **`1111`** (otra: `TALLER_PASSWORD_INICIAL`). El fichero
  **no lleva contraseñas** y no debe llevarlas: va al git compartido.
- Un error (código mal formado o repetido, usuario repetido, cliente sin `sucursal admin`,
  producto que no existe…) **para el arranque** diciendo la línea, en vez de cargar a medias.
  `tests/test_datos_arranque.py` y `tests/test_codigos_cliente.py` comprueban además que el
  fichero real es válido.
- Solo se usa con la base **vacía**. Para añadir lo que falte a una base que ya tiene
  datos, sin borrar nada (un cliente con el mismo CIF o un usuario con el mismo nombre
  se omite y se lista):

  ```bash
  docker exec taller_admin_api python -m app.cargar_arranque
  ```

  Para **pasar una base antigua a los usuarios por código**, añade `--renombrar`: los clientes
  que ya existen (mismo CIF) reciben el código del fichero y sus usuarios de la misma sucursal y
  rol pasan al nombre nuevo (`murueta` → `mur-admin`, `bilbao` → `mur-bilbao`); los pedidos y
  albaranes no se tocan.

Con `TALLER_DEV_MODE=true` (por defecto en el `docker-compose.yml` de este
repo) la contraseña maestra (`TALLER_MASTER_PASSWORD`, por defecto `1111`)
vale para entrar como cualquiera de los usuarios de ejemplo de arriba, sin
necesidad de contraseñas propias — pensado justo para clonar el repo en una
máquina nueva y tener algo con lo que jugar desde el primer arranque.

## El panel por dentro (pestaña a pestaña)

![El panel con el menú en dos niveles: arriba las tres secciones (Producción, Contabilidad, Administración) y debajo las pestañas de la sección elegida](img/panel_pestanas.png)

Una vez dentro de `/panel`, arriba del todo hay **tres secciones** y, dentro de
cada una, sus pestañas:

| Sección | Pestañas (admin_sistema) | Qué se hace ahí |
|---|---|---|
| **Producción** | Pedidos · Pedidos Taller · Reparto · Almacén · Diagnóstico | Lo del día a día: pedir, fabricar, guardar y entregar piezas |
| **Contabilidad** | Resumen · Tarifas · Facturación | Precios, facturas, cobros y cuánto queda por cobrar |
| **Administración** | Empresa · Productos · Subproductos · Paquetes · Colores · Catálogo · Usuarios · Clientes · Auditoría | Los datos de base: catálogo, clientes, usuarios y quién factura |

Un `admin_cliente` ve las mismas tres secciones pero recortadas (Producción:
Pedidos · Contabilidad: Resumen, Albaranes, Facturas · Administración:
Catálogo, Usuarios). Un usuario `normal` solo tiene Pedidos y no ve el menú de
secciones. Esto es lo que hace cada pestaña, contado sin tecnicismos:

- **Pedidos**: la pestaña del día a día. Se pide **siempre con la cesta**: eliges una pieza o un
  paquete entero y cuántas, **+ Añadir a la cesta**, y cuando está como quieres, **Pedir la cesta**. Todo lo
  de una cesta se entrega junto, en un solo albarán; un pedido de una sola cosa es una cesta de una línea.
  La cesta se guarda en el navegador hasta que se pide. Al pedirla, la celda se pone
  a fabricarlo sola. Según va progresando ves cuántas lleva hechas, si ya
  había stock guardado que cubre parte o todo el pedido sin fabricar nada
  nuevo, y en qué máquina se está haciendo (si tienes más de una línea de
  producción). Los pedidos "activos" son los que aún faltan por completar;
  el "histórico" son los que ya se acabaron o se cancelaron.
- **Productos**: el catálogo de qué se fabrica en general — "Tornillos",
  "Tuercas"... Cada producto lleva un código corto y, si quieres, puedes
  asignarle un LED de color: es pura decoración (se enciende en el brazo
  robot mientras lo fabrica) y no afecta en nada a que la producción
  funcione.
- **Subproductos**: las variantes concretas de cada producto — dentro de
  "Tornillos" puedes tener "Tornillo de 10mm" y "de 20mm". Esto es lo que
  de verdad se pide en un pedido, no el producto suelto.
- **Paquetes**: packs cerrados de varias piezas a la vez, tipo "Paquete de
  10" = 10 tornillos + 10 tuercas + 10 arandelas. No tienen stock propio:
  pedir un paquete simplemente crea un pedido normal por cada pieza que lo
  compone.
- **Colores**: el catálogo de colores de LED que puedes asignar a un
  producto. Los marcados como "físico" existen de verdad como cubo en la
  simulación; el resto son solo luces decorativas.
- **Catálogo**: aquí decides qué productos puede pedir cada cliente — si
  un producto no está marcado para uno, ese cliente ni lo ve en su
  desplegable de pedidos. Es un paso que hay que hacer sí o sí: a cada
  cliente nuevo hay que asignarle su catálogo a mano (no viene marcado
  nada por defecto), si no, aunque tenga usuarios ya no podrá pedir nada.
- **Usuarios**: quién puede entrar y qué puede tocar. La cadena de mando,
  de un vistazo:

  ```
  Admin. sistema  (tú)
    └─ ve y toca TODO, de todos los clientes

  Cliente (empresa) ── entra con su cuenta "Admin. cliente"
    └─ da de alta / edita / da de baja SUS Usuarios (rol "Normal")
         └─ cada Usuario "Normal" entra con la suya y hace SUS pedidos
  ```

  O sea: el cliente entra con su propia cuenta de administrador, gestiona
  a su gente (usuarios, sucursales) sin pedirle nada a administración, y
  cada uno de esos usuarios entra ya con su propia cuenta a pedir lo que
  necesite. Un "Admin. cliente" no puede ver ni tocar usuarios de otra
  empresa, ni crear un "Admin. sistema" nuevo — solo administración
  puede.
- **Clientes**: las empresas que usan el sistema. Cada una vive en su
  propio compartimento estanco, sin cruzarse nunca con las demás:

  ```
  Cliente "Ferretería Ereño"        Cliente "Suministros Mungia"
    ├─ sus Usuarios                   ├─ sus Usuarios
    ├─ su Catálogo (qué puede pedir)  ├─ su Catálogo
    └─ sus Pedidos                    └─ sus Pedidos

              -- nada se ve ni se mezcla entre uno y otro --
  ```

  Al dar de alta un cliente nuevo aquí, se crea a la vez su primer usuario
  "Admin. cliente" — con eso ya puede entrar y montarse el resto (sus
  propios usuarios en la pestaña Usuarios, su catálogo en la pestaña
  Catálogo) sin que administración tenga que hacer nada más.
- **Pedidos Taller** (solo `admin_sistema`): los pedidos que el almacén **no
  puede cubrir** y que hay que pedir al taller que fabrique. Solo sale lo que
  falta fabricar; desde aquí se asigna máquina, se marca urgente o se cancela.
- **Reparto** (solo `admin_sistema`): la segunda etapa. Lo que ya está listo
  (o lo cubre el stock) y falta **entregar al cliente**. Al repartir se emite
  un **albarán** por cliente. Aquí están los dos interruptores automáticos,
  el botón "Asignar stock a pedidos pendientes" y la lista de albaranes
  emitidos.
- **Resumen** (`admin_sistema` y `admin_cliente`): las cuentas de un vistazo —
  facturado este mes y este año, cobrado, pendiente de cobro (por antigüedad),
  entregado sin facturar y, para administración, el desglose por cliente. Solo
  cuentan las facturas vigentes. Incluye "Descargar libro de facturas (CSV)"
  para la gestoría.
- **Empresas** (solo `admin_sistema`): las empresas que **emiten facturas** — puede
  haber varias, cada una con su razón social, CIF, dirección y **numeración propia**
  (serie). Se marca una por defecto; una empresa no se borra, se desactiva.
- **Tarifas** (solo `admin_sistema`): el precio que paga cada cliente (tarifa
  especial o la general), de productos **y de paquetes**, y el historial de todos
  los cambios de precio.
- **Facturación** (solo `admin_sistema`): eliges con qué empresa facturas y ves los
  albaranes pendientes de facturar (con casillas para **seleccionar todos** o **todos los de un
  cliente**) (por cliente o seleccionados) y facturas emitidas, con
  cobrar, anular (rectificativa) y ver/imprimir.
- **Albaranes** y **Facturas** (solo `admin_cliente`): sus entregas y sus facturas,
  en solo lectura, con "Ver / imprimir".
- **Almacén**: el stock de piezas ya fabricadas y sus movimientos; se puede
  añadir o quitar a mano. Repartirlo entre los pedidos es cosa de la pestaña
  **Reparto**: ahí está el interruptor "Reparto automático" (con él encendido,
  el stock libre se **asigna** solo a los pedidos pendientes y las piezas
  quedan listas) y el botón "Asignar stock" para hacerlo a mano.
- **Diagnóstico**: un vistazo técnico a cómo va la producción de verdad
  (piezas hechas, fallos de agarre, límites de alcance...) — no hace falta
  mirarlo para el uso normal, es para cuando algo va mal y hay que
  investigar.
- **Auditoría**: el quién-hizo-qué-y-cuándo de todas las demás pestañas,
  por si algún día hay que reconstruir una historia.

Solo `admin_sistema` ve todas estas pestañas enteras; un `admin_cliente` o
un usuario `normal` ven una versión recortada, con solo lo que les toca
(ver "Roles" más abajo).

## Modelo

Cada **color** es la identidad del producto (`Producto.color` es único): la
celda solo distingue colores. R/G/B tienen cubo físico; Y/M/C/W son solo
colores de LED de producto (modo comodín), fabricados con los tres cubos
reales.

Tablas: `clientes`, `usuarios`, `audit_log`, `colores`, `productos`,
`subproductos`, `paquetes`, `paquete_componentes`, `cliente_productos`,
`pedidos`, `stock`, `movimientos_stock` (libro de solo añadir),
`eventos_produccion`, `configuracion_almacen` (fila única), `repartos` y
`reparto_lineas` (albaranes), `tarifas_cliente`, `historial_precios`,
`emisores` (empresas que facturan), `facturas` y `factura_lineas` (facturas y
rectificativas).

### Ciclo de un pedido (2026-09-19)

Un pedido pasa por **dos etapas**, y cada una tiene su interruptor:

```
        taller fabrica                        almacen asigna                  reparto entrega
 pedido ───────────────► STOCK LIBRE ─────────────────────► LISTO ─────────────────────► REPARTIDO
        (cubo_clasificado)        reparto_automatico   (cantidad_completada)  expedicion_automatica   (albaran)
```

| Estado | Significa | Dónde se ve |
|---|---|---|
| `pendiente` | Nada listo todavía | Pedidos, Pedidos Taller |
| `en_proceso` | Algo listo, falta el resto | Pedidos, Pedidos Taller y/o Reparto |
| `listo` | Todo listo, sin entregar | Pedidos, Reparto |
| `completado` | **Repartido** (con albarán) | Histórico |
| `cancelado` | Cancelado (solo si estaba `pendiente`) | Histórico |

- `cantidad_completada` = piezas **listas** para el pedido (ya salieron del
  stock libre); `cantidad_repartida` = las ya **entregadas** (constan en un
  albarán). Siempre `repartida <= completada <= pedida`.
- `falta_fabricar` (lo que ve Pedidos Taller) y `para_repartir` (lo que ve
  Reparto) se calculan en cada consulta; un pedido con el stock cubriendo solo
  una parte aparece en las dos pestañas.
- La expedición automática solo entrega pedidos **completos** (`listo`): si
  entregara cada pieza suelta saldría un albarán por cubo. A mano se puede
  repartir también un pedido a medias.
- **Un paquete y una cesta salen en UN albarán.** Pedir un paquete crea un pedido por componente,
  y la **cesta** (`POST /pedidos/multiple`: productos sueltos y/o paquetes pedidos de una vez) crea
  uno por línea; todos comparten `grupo_entrega`. Con la expedición automática esperan como `listo`
  hasta que **todo el grupo** está listo y entonces salen juntos, en un solo albarán (con el nombre
  de los paquetes que lleve). Con el reparto manual, repartir un pedido del grupo reparte el grupo
  entero. Se valida todo antes de crear nada (o entra todo, o nada). Dos cestas son dos albaranes. El panel
  solo pide con cesta (una cesta de una línea es un pedido suelto); `POST /pedidos` y `/pedidos/paquete`
  siguen existiendo en la API y sus pedidos salen cada uno por su cuenta.
- **Barrido de stock parado** (2026-09-20). Cada 10 s el servidor mira si el stock libre cubre **por completo**
  algún pedido abierto y, si el reparto automático está activo, se lo asigna (y, con la expedición automática,
  sale como siempre). Nace de un incidente real: la pieza 9 de 10 entró al almacén sin asignarse a su pedido,
  la celda lo veía "cubierto por stock" y no fabricaba más, y el pedido se quedó parado. Reglas: solo si el
  stock cubre TODO lo que le falta al pedido (un pedido que no se cubre entero no bloquea a los siguientes),
  por urgencia y antigüedad, y deja rastro en la auditoría ("barrido de stock: #…"). La regla del
  14/09 (una pieza de otra máquina no completa mi pedido *al llegar*) sigue igual; el barrido solo actúa
  cuando ya no falta nada por fabricar. `TALLER_BARRIDO_SEGUNDOS` (por defecto 10; 0 = desactivado; los tests lo
  apagan y llaman a `barrer_stock()` a mano).
- **Un paquete se entrega ENTERO** (decisión del usuario, 2026-09-20): sus productos solo salen
  cuando están todos listos y siempre juntos, también a mano; los productos sueltos de una cesta sí
  pueden salir a medias, el paquete espera.
- `POST /reparto/expedir` (solo `admin_sistema`) asigna primero el stock libre
  que cubre el pedido y luego lo entrega, aunque `reparto_automatico` esté
  apagado: pulsar Repartir es una orden explícita.
- La celda **no cambia**: sigue leyendo `cantidad_completada`, `estado` y
  `stock_disponible`. Un pedido `listo` no se le ofrece porque ya no falta nada.

### Control de precios y facturación (2026-09-19)

Cómo se controla un precio, de origen a factura (código en `app/contabilidad.py`):

```
 TARIFA general (Subproducto)   ─┐
 o TARIFA de cliente             ├─► PEDIDO (copia precio + origen) ─► ALBARÁN (copia) ─► FACTURA (copia)
                                 ┘        tarifa_general | tarifa_cliente | manual
```

- **Tarifas.** El precio general está en el subproducto. Un cliente puede tener
  una **tarifa especial** (pestaña *Tarifas*): sin ella paga la general. Cambiar
  una tarifa solo afecta a los pedidos **nuevos**; lo ya pedido conserva su precio.
- **Historial de precios** (`historial_precios`, solo se añade). Todo cambio de
  precio —tarifa general, tarifa de cliente, corrección de un pedido o de una
  línea de albarán— guarda quién, cuándo, de cuánto a cuánto, y el **motivo**
  (obligatorio en las correcciones).
- **Correcciones antes de facturar.** Un pedido aún no entregado se puede
  corregir (`PATCH /pedidos/{id}/precio`, queda con origen *manual*); una línea
  de albarán no facturada también (`PATCH /repartos/lineas/{id}/precio`). La
  cantidad entregada no se toca nunca. Una línea ya facturada no se corrige: se
  anula la factura.
- **Albarán** (`repartos` + `reparto_lineas`): solo se añade, número
  `ALB-AAAA-nnnnnn`. **Precios en céntimos enteros**, nunca `float`.
- **Factura** (`facturas` + `factura_lineas`): agrupa los albaranes **sin
  facturar** de UN cliente (todos, o los que elijas), número `FAC-AAAA-nnnnnn`.
  Copia las líneas, el precio, el IVA y los **datos fiscales de las dos partes**
  (quien factura y el cliente) en ese momento: si luego se edita el cliente o la
  empresa emisora, la factura no cambia. Exige CIF y dirección del cliente y una
  empresa emisora activa (Administración → Empresas), y rechaza líneas a 0 € salvo
  confirmación expresa.
- **Varias empresas emisoras** (`emisores`). Cada una tiene su serie de facturas y de
  rectificativas (`FAC`/`RECT`, `TVR`/`RTVR`…), distintas entre sí, y su propio contador
  por año. La serie no se puede cambiar cuando ya ha emitido facturas. La rectificativa
  usa la serie de rectificativas de la empresa de la factura original.
- **Rectificativa.** Una factura no se edita ni se borra: se **anula** emitiendo
  su rectificativa (`RECT-AAAA-nnnnnn`, mismas líneas con cantidad negativa, con
  motivo). La original queda `anulada` y sus albaranes quedan libres para volver
  a facturarse, ya corregidos. Los números no se reutilizan.
- **Cobro.** Una factura emitida se marca como cobrada (fecha y método).
- **IVA por tipo.** Se suman las bases del mismo porcentaje y se redondea **una**
  vez la cuota de ese grupo (medio céntimo hacia arriba, simétrico para
  negativos), como en una factura española. Es la misma regla (`app/importes.py`)
  para albaranes y facturas, así que un albarán y su factura cuadran al céntimo.
  Base, IVA y total **se derivan** de las líneas (no se guardan).

Quién puede qué: `admin_sistema` gestiona tarifas, correcciones, facturas,
cobros y anulaciones; `admin_cliente` solo **ve** sus tarifas, albaranes y
facturas (pestañas *Albaranes* y *Facturas*); `normal` no ve nada de esto.

Lo que **no** hay (a propósito): recargo de equivalencia y exenciones de IVA por
cliente, facturas por periodo/automáticas, pagos parciales o remesas, envío por
email de la factura, series de facturación configurables y exportación
contable (SII, Facturae). Cada uno se puede añadir encima de este modelo.

### Paquetes con precio propio (2026-09-20)

Un paquete puede tener **su precio** (`Paquete.precio_centimos`, por paquete y sin IVA, con su `iva_porcentaje`);
vacío = **sin precio propio** y se cobra la suma de sus productos, cada uno a su tarifa.

- **Con precio propio**, el albarán y la factura llevan **una línea del paquete** (`tipo = paquete`, con cantidad
  de paquetes y precio) y debajo, **sin precio**, lo que lleva (`tipo = componente`). Los productos de un paquete
  con precio salen a 0 € en el pedido a propósito: el precio está en el paquete y ni el albarán ni la factura
  rechazan esas líneas ("líneas a 0 €"). El IVA de los componentes es el del paquete, así que el desglose no
  saca una fila de IVA vacía.
- **Sin precio propio**, las líneas son las de siempre (`tipo = normal`) pero llevan `paquete_pedido_id` y el
  nombre del paquete, para agruparlas al mostrarlas.
- **`PedidoPaquete`** (`pedidos_paquete`) es UN paquete pedido: cuántos, y su precio y origen (`paquete_general`,
  `paquete_cliente` o `manual`) **congelados** al pedir. Sus productos son pedidos normales con
  `paquete_pedido_id`. Cambiar el precio del paquete después no toca lo ya pedido.
- **Tarifa por cliente para paquetes** (`tarifas_cliente_paquete`, pestaña *Tarifas*), igual que la de productos.
  Todo cambio de precio de paquete queda en `historial_precios` (`paquete_general`, `paquete_cliente`,
  `pedido_paquete`; llevan `paquete_id` y no `subproducto_id`).
- **Correcciones:** el precio de un paquete pedido y aún no entregado se corrige con
  `PATCH /pedidos-paquete/{id}/precio`; el de un producto suelto, como siempre. El producto de un paquete con
  precio propio no se corrige por separado (409). En un albarán se corrige la línea del paquete
  (`PATCH /repartos/lineas/{id}/precio`); la de un componente da 400.
- La rectificativa de una factura con paquete es exactamente su negativo, líneas de paquete incluidas.

**Al actualizar una base antigua:** este cambio hace NULL-ables `historial_precios.subproducto_id` y
`reparto_lineas.pedido_id/subproducto_id`, y SQLite no permite quitar un `NOT NULL` con `ALTER`. `migraciones.py`
lo detecta y **avisa en el log**, pero la solución es recrear la base (`data/taller.db`): se vuelve a llenar con
los clientes del fichero de arranque. Una base que ya no admite esos NULL solo falla al fijar un precio de
paquete o al entregar un paquete con precio propio.

### Migraciones

No hay Alembic. Al arrancar, `app/migraciones.py` compara cada tabla con el
modelo y hace `ALTER TABLE ... ADD COLUMN` de las columnas **nuevas**, así que un
cambio aditivo del modelo ya no obliga a borrar `data/taller.db`. Solo añade
(no renombra, no cambia tipos, no borra) y una columna `NOT NULL` necesita valor
por defecto; lo que no pueda hacer lo avisa en el log. Los valores de ejemplo del
seed (precios, emisor) solo se siembran en una base **vacía**.

## Roles

- `admin_sistema`: todo. Es el único que gestiona productos, clientes,
  almacén, diagnóstico y auditoría.
- `admin_cliente`: gestiona su empresa (usuarios propios, catálogo asignado,
  pedidos de su empresa).
- `normal`: hace pedidos y ve los suyos.

La contraseña maestra (`TALLER_MASTER_PASSWORD`, por defecto `1111`) vale
siempre para entrar como usuario `normal` — pensado para que quien solo
quiera "jugar" con el panel no necesite que le demos de alta una cuenta.
Para `admin_sistema`/`admin_cliente` la maestra **solo** cuela si
`TALLER_DEV_MODE=true` (activo en nuestro `docker-compose.yml` local); sin
ese flag hace falta la contraseña real de la cuenta. El usuario `admin`
sembrado siempre tiene contraseña real (`admin` por defecto), así que
funciona con o sin `TALLER_DEV_MODE`.

## `POST /taller/cubo_clasificado`

Evento que manda la celda cada vez que un cubo llega a su caja. **Siempre**
responde `200` y suma 1 al stock del color. Si el reparto automático está
activo (el único interruptor de la asignación), además **asigna** esa unidad a
un pedido pendiente (queda como pieza *lista* para él): el indicado en
`pedido_id` si sigue abierto, si no el más urgente y antiguo de ese producto.
Con `expedicion_automatica` activa, si con esa pieza el pedido queda completo
sale solo con su albarán; si no, queda `listo` esperando en Reparto. (En versiones anteriores de este
documento se decía que devolvía 404 si no había pedido pendiente: es falso,
siempre devuelve 200 con `pedido: null` en ese caso.)

**Nunca reparte stock a pedidos por iniciativa propia** fuera de esta regla:
`/almacen/repartir` (asignar stock) y `/reparto/expedir` (entregar) son
decisiones del operario.

## Endpoints

Ver `/docs` (Swagger generado por FastAPI) para el listado completo con
esquemas de entrada y salida.

## Tests automáticos (2026-09-11, ampliados 2026-09-19)

261 tests con pytest + `TestClient` de FastAPI, cubriendo login/roles,
productos, clientes/usuarios y sus límites de permiso, pedidos (alta,
alcance por rol, cancelar, **reprocesar**), almacén (`reparto_automatico`
como único gate, `cubo_clasificado`, reparto FIFO de `stock_disponible`,
ajustar/quitar stock), tiempos de proceso, diagnóstico y auditoría, y (`tests/test_reparto.py`) el
ciclo listo → repartido, los albaranes, los precios congelados y el IVA, y
(`tests/test_contabilidad.py`, `tests/test_migraciones.py`) tarifas, historial,
correcciones, facturas, rectificativas, cobros, permisos y la migración de columnas.

**Nunca tocan `data/taller.db`**: `tests/conftest.py` fija
`TALLER_DB_PATH` a un fichero temporal *antes* de importar nada de `app`
(la variable se lee en el momento del import en `database.py`), y cada
test arranca con una base de datos limpia y recién sembrada.

```bash
docker exec taller_admin_api pip install -r requirements-dev.txt   # una vez
docker exec -w /workspace taller_admin_api python -m pytest -v
```

Dos de los tests documentan regresiones reales de la sesión 2026-09-11
para que no se repitan sin que alguien se entere: el mensaje de error al
cancelar un pedido no pendiente (se rompió a `"c/p ya fabricadas"` en una
reescritura) y el comportamiento silencioso de `POST /usuarios` cuando un
`admin_cliente` intenta colar un usuario en otra empresa (no da 403:
ignora el `cliente_id` recibido y fuerza el suyo propio).
