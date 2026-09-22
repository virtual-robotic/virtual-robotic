# Nuestra cadena de producción

Si es la primera vez que ves este proyecto: esto es la parte que mueve
brazos robóticos de verdad (bueno, simulados) para fabricar y clasificar
piezas. No hace falta saber nada de robótica para seguir esta página —
se explica todo desde cero.

## Qué es Webots

**Webots** es un programa que simula robots en 3D: física real (peso,
rozamiento, colisiones), cámaras virtuales que "ven" lo mismo que verían
de verdad, y motores que se mueven exactamente como los del robot real.
Es de código abierto, lo hace la empresa Cyberbotics, y se usa mucho en
investigación y en la industria para probar un robot **antes** de
tocarlo físicamente — un error en la simulación no rompe nada ni le
hace daño a nadie.

En este proyecto, todo lo que ves — los brazos, la cinta transportadora,
los cubos de colores, las cámaras — vive dentro de Webots. No hay ningún
brazo robótico físico moviéndose en una nave; es un taller virtual
completo.

## De dónde viene el robot Panda

El **Panda** es un brazo robótico real, fabricado por la empresa alemana
**Franka Emika**. Es lo que se llama un "cobot" (robot colaborativo):
está pensado para trabajar cerca de personas sin jaulas de seguridad,
porque controla la fuerza que hace en cada movimiento y se puede
programar para ser preciso y suave. Es uno de los brazos más usados en
universidades y centros de investigación de robótica de todo el mundo.

Webots trae un modelo 3D oficial de este robot, con su geometría y su
física reales (7 articulaciones, límites de movimiento reales, la misma
pinza de dos dedos). Por eso lo que se prueba aquí en la simulación se
comporta igual que se comportaría el brazo de verdad.

![El robot Panda tal como lo pinta Webots: un brazo blanco de siete articulaciones, con la pinza de dos dedos al final, montado sobre una mesa](img/panda_robot.jpg)

## Nuestros dos Panda

Este proyecto no usa uno, sino **dos** brazos Panda, cada uno con su
propio trabajo dentro de una pequeña celda industrial:

- **Loader** ("el que carga"): coge piezas (cubos de colores) de una
  caja y las va dejando sobre una cinta transportadora.
- **Sorter** ("el que clasifica"): espera al final de la cinta, ve qué
  color de pieza llega con una cámara, la coge y la deja en la caja que
  le corresponde a ese color.

Entre los dos, cada pieza recorre el camino completo sola: se carga, se
transporta y se clasifica, sin que nadie tenga que tocar nada a mano.

Para simplificar (no hay una fábrica infinita de cubos detrás), en
cuanto una pieza termina de clasificarse **vuelve sola a su caja de
origen**, lista para que el Loader la vuelva a coger — así se simula un
sistema de producción continuo, que nunca se queda sin piezas, con solo
un puñado de cubos reales dando vueltas todo el rato.

![Los dos robots Panda trabajando en la celda: el Loader a la izquierda dejando cubos en la cinta, el Sorter arriba clasificándolos por color](img/webots_cell.jpg)

## Los "nodos": qué son y cuáles tenemos

Todo esto se controla con **ROS 2** (Robot Operating System), que es el
"sistema operativo" estándar para programar robots. La idea central de
ROS 2 son los **nodos**: programas pequeños e independientes, cada uno
con un trabajo concreto, que se hablan entre sí mandándose mensajes por
"canales" (llamados *topics*) — un poco como un grupo de walkie-talkies
donde cada aparato solo dice lo suyo y escucha lo que le interesa.

Estos son los nodos principales de esta celda, explicados en una línea:

- **El driver de Webots** (uno por robot): recibe órdenes de "mueve el
  brazo a esta posición" y hace que el robot simulado se mueva de
  verdad dentro de Webots. Es **la única pieza que sabe que el robot es
  de mentira**: el resto de nodos solo dicen "pon las articulaciones así"
  y "cierra la pinza tanto", sin saber quién obedece. Por eso, el día que
  tengamos un Panda de verdad, este driver iría contra **el robot real en
  lugar del simulador** y los demás nodos seguirían igual. (Habría que
  cambiarlo por el driver del propio Panda real y probar con cuidado la
  velocidad, la seguridad y las cámaras, que ahora también son simuladas.)
- **`loader_demo` / `sorter_demo`**: el "cerebro" de cada robot — deciden
  qué hacer paso a paso (ir a por una pieza, agarrarla, llevarla,
  soltarla) y se lo mandan al driver.
- **Las cámaras cenitales**: miran la mesa desde arriba y dicen "hay un
  cubo verde en esta posición" — así el robot sabe adónde ir sin que
  nadie le diga las coordenadas a mano.
- **El supervisor del almacén**: vigila que las piezas no se pierdan ni
  se queden en una posición imposible, y las recoloca si hace falta.
- **Los puentes de LED**: si hay una Raspberry Pi Pico física conectada,
  encienden un LED de verdad del color que se está fabricando. Sin
  Pico, la celda funciona exactamente igual, simplemente no hay luz
  física — si quieres ver la simulación igualmente, está en nuestro
  panel de control, en la pestaña **Raspberry Pi Pico**.
- **El panel de control** (`teleop_gui`): la ventana desde la que una
  persona mueve los robots a mano, lanza producción, y ve el estado de
  todo de un vistazo. Si algún día hay más de una celda funcionando a
  la vez (más de una "línea de producción"), **cada una lleva su propio
  panel independiente** — cada ventana controla solo los robots de su
  línea, aunque todas compartan el mismo panel de pedidos web.

![El panel de control manual: cabecera con EN MARCHA, estado del lote y parada de emergencia, y las pestañas Movimiento, Producción, Raspberry Pi Pico y Configuración](img/panel_control_manual.png)

<a href="/manual/lanzar/assets/Documentacion/panel_control_manual.html" style="display:block; margin:0 0 1.3rem; padding:1rem 1.2rem; background:var(--bg-elevated); border:1px solid var(--line); border-left:4px solid var(--accent-brick); border-radius:6px; text-decoration:none; color:inherit;">
  <strong style="color:var(--accent-brick);">📋 El panel de control manual, pestaña a pestaña</strong><br>
  <span style="color:var(--fg-muted); font-size:0.92rem;">Qué hace cada botón y cada pestaña, con una captura de cada una.</span>
</a>

## Más de una línea de producción

Como cada línea es un juego de contenedores independiente con su propio
panel (ver arriba), se puede encender una segunda, una tercera... en la
misma máquina, todas trabajando a la vez y compartiendo el mismo panel
de pedidos web, sin pisarse entre sí. Ya hay una plantilla lista y
probada para hacerlo — guía paso a paso, pensada para seguir sin ser
programador, en
[Cómo añadir una línea de producción más](/manual/lanzar/assets/Documentacion/anadir_cadena_produccion.html).

## Cómo verlo funcionando

Los pasos para arrancar la simulación (Webots + los robots + el panel
de control) están en [Cómo arranca todo](/manual/lanzar) — es la guía
pensada para seguir literalmente, copiando y pegando comandos.

## Si quieres el detalle técnico

Esta página se queda en el "qué es y para qué sirve". Toda la
arquitectura interna (cómo se calculan los movimientos, qué decisiones
de diseño se tomaron y por qué, el historial completo de cómo se fue
construyendo) está aparte, en
[`detalle_tecnico_panda.md`](detalle_tecnico_panda.md) — pensado para
quien quiera meterse a programar o modificar algo, no hace falta
leerlo para usar la celda.
