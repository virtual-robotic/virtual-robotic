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

### Probarlo con los usuarios de ejemplo

| Entras como… | Contraseña | Eres… |
|---|---|---|
| `admin` | `admin` | El taller: ve todo, manda fabricar, reparte y factura. No hace pedidos. |
| `ere-admin` | `1111` | Un cliente de ejemplo: hace pedidos y ve los suyos. |

### Meter piezas a mano en el almacén

En la pestaña **Almacén** (solo el taller), cada producto tiene los botones
**«Añadir a stock»** y **«Quitar de stock»**, para piezas que no vienen de
los robots: compradas fuera, inventario, devoluciones. Cada una queda
apuntada en *Movimientos* como «ajuste manual». Con el reparto automático
encendido, se dan solas a los pedidos que pueden completar enteros; si solo
cubren una parte, esperan a los robots o al botón **«Asignar stock»** de la
pestaña **Reparto**.

---

**¿Quieres saber cómo está hecha por dentro?** (rutas, base de datos,
arranque, cada pestaña del panel, pruebas automáticas…): está en
[DETALLE_TECNICO.md](DETALLE_TECNICO.md).
