_Última modificación: 2026-09-29 14:38_

# Prompt para generar el proyecto Virtual Robotic desde cero

> **Qué es este fichero.** Todo lo necesario para que **Claude Code**, en otro
> ordenador y partiendo de una carpeta vacía, vuelva a construir el proyecto
> *Virtual Robotic* entero: la celda con los dos brazos robóticos simulados, su
> panel de control, el programa de las dos Raspberry Pi Pico y la web de pedidos
> con su almacén, albaranes y facturas.
>
> No lleva el código fuente: lo **describe** con el detalle suficiente para
> escribirlo otra vez (números exactos, pasos, nombres, reglas). Solo lleva
> copiados tal cual, al final, los dos ficheros de datos que no se pueden
> adivinar: el escenario 3D de Webots y la «cadena» del brazo para calcular sus
> movimientos.
>
> Está sacado del proyecto original tal como estaba el 2026-09-27 (versión
> 2609.00254 del repositorio).
>
> **Probado el 2026-09-27** en una máquina virtual Linux Mint (10 GB de RAM,
> 6 procesadores): Claude Code hizo las 13 fases partiendo solo de este
> fichero, en unas 6 horas de trabajo (se paró dos veces por el límite de uso
> de Claude y siguió al volver). Resultado: web con 320 tests en verde, celda
> con los 6 controladores, lote largo de **40 piezas en 16 minutos sin romper
> ninguna pinza**, y dos cadenas trabajando a la vez. **Sin probar:** Windows y
> las Pico de verdad (solo simuladas). Lo que falló en esa prueba ya está
> corregido en este fichero.

---

## Parte 1 — Para ti: cómo usar este fichero

### Qué vas a tener al final

- **Una celda de fábrica simulada** en Webots (un programa que imita la física
  de verdad): dos brazos robóticos Panda. El **Loader** coge cubos de colores
  de una caja y los deja en una cinta; el **Sorter** los recoge al final de la
  cinta y los clasifica por color. Los cubos vuelven solos a la caja, así que
  nunca se acaba el material.
- **Un panel de control** (una ventana con botones) para mover los brazos a
  mano, parar la celda en caso de emergencia y lanzar la fabricación de
  pedidos.
- **Una web de pedidos** que hace de oficina del taller: los clientes piden,
  los robots fabrican, el almacén se lleva solo y salen albaranes y facturas.
- **El programa de dos Raspberry Pi Pico** (opcionales): LEDs de colores, dos
  botones de parada de emergencia de verdad, un sensor de proximidad y una
  pantallita. Sin ellas todo funciona igual.
- Los **scripts de arranque** para Linux y para Windows, y la posibilidad de
  tener **varias líneas de producción** trabajando para la misma web.
- La **documentación** en castellano, inglés y euskera.

### Qué necesitas

| | Solo la web de pedidos | Todo, con los robots |
|---|---|---|
| Ordenador | Cualquiera con Linux o Windows | Linux Mint / Ubuntu 24.04 con escritorio gráfico, o un **PC de verdad** con Windows 10/11 (no vale Windows dentro de VirtualBox) |
| Programas | Docker (con `docker compose`) y Git | Lo mismo; en Windows, además **Webots R2025a** |
| Disco / memoria | ~1 GB | ~15 GB libres y 8 GB de RAM o más |
| Internet | La primera vez | La primera vez (se descarga Webots, varios GB) |
| Claude Code | Sí | Sí |

Opcional, para el hardware real: dos Raspberry Pi Pico (una **Pico W** con
Wi-Fi y una normal), dos LED RGB, dos pulsadores, un sensor HC-SR04, una
pantalla OLED SSD1306, resistencias, protoboard y el programa **Thonny**.
La lista exacta está en la sección D de la especificación.

### Cómo se usa, paso a paso

1. Crea una **carpeta vacía** para el proyecto, por ejemplo
   `~/Proyectos/VirtualRobotic` (sin tildes ni espacios en la ruta, mejor).
2. Copia **este fichero** dentro de esa carpeta, con este mismo nombre.
3. Abre una terminal en esa carpeta y arranca **Claude Code** (`claude`), o
   abre la carpeta con VS Code y su extensión de Claude Code.
4. Copia y pega la orden de la **Parte 2** (justo debajo).
5. Claude irá **fase a fase** (son 13). Al terminar cada una te enseñará lo
   que ha comprobado de verdad y esperará a que le digas **«sigue»**. No hay
   prisa: se puede hacer en varios días; si cierras Claude, al volver dile
   «seguimos por la fase N de este fichero».
   - Al empezar te preguntará **qué nombre poner como autor** en la licencia y
     si guarda este fichero en Git (lo normal: sí). Tenlo pensado.
   - Si no quieres que te pregunte más, dile **«sigue y no preguntes»**: decidirá
     lo razonable y te lo contará al terminar cada fase.
   - Para que no te pida permiso a cada comando, puedes arrancarlo con
     `claude --dangerously-skip-permissions`, pero **solo en un ordenador o
     máquina virtual de pruebas**, nunca en uno con tus cosas.
6. Hay cosas que **tienes que hacer tú**, porque Claude no puede tocar tu
   pantalla ni tus cables:

| Cuándo | Qué haces tú |
|---|---|
| Fase 4 (Docker de la celda) | Dejar la terminal abierta mientras se construye la imagen de Webots: la primera vez puede parecer colgada un buen rato hacia el 70-80 %. **No la cortes.** |
| Fases 4 a 8 | Mirar la ventana de Webots y el panel cuando Claude te lo pida y decirle lo que ves |
| Fase 9 (Pico) | Si tienes las Pico: montarlas según el esquema, rellenar tu Wi-Fi en `wifi_config.py` y grabar el programa con Thonny (*Guardar como → dispositivo → main.py*) |
| Fase 11 (Windows) | Si vas a usar Windows: instalar Docker Desktop, Git y Webots R2025a |
| Fase 12 (documentación) | Hacer las capturas y los vídeos de tu propia celda (Claude te dice cuáles y dónde guardarlos) |
| Fase 13 (validación) | Dejar un lote largo (15 minutos o más) fabricando y mirar cuántas piezas salen |

### Lo que este fichero NO trae (y qué hacer)

- **Las fotos y los vídeos** del original. Se sacan de tu propia simulación
  cuando ya funcione (Webots graba vídeo y hace capturas). Hasta entonces, la
  web usa huecos con el mismo nombre de fichero.
- **Tus claves Wi-Fi.** En el repositorio solo van plantillas; las tuyas las
  pones tú y **nunca se suben a Git**.
- **El historial de Git** y **los datos reales** de la base de datos: el
  proyecto nuevo empieza limpio, con datos de ejemplo para jugar.
- **Las traducciones palabra por palabra.** Claude las vuelve a escribir (el
  euskera conviene que lo revise alguien que lo hable).

### Palabras que vas a oír (glosario)

| Palabra | Qué es, en cristiano |
|---|---|
| **Docker / contenedor** | Una «caja» con su propio Linux dentro, donde va instalado todo lo que necesita un programa. Así no hay que instalar nada a mano en tu ordenador. Una **imagen** es la plantilla de la caja; el **contenedor** es la caja en marcha. |
| **Docker Compose** | Un fichero (`docker-compose.yml`) que dice qué cajas arrancar juntas y cómo se hablan. |
| **Webots** | El simulador 3D: robots, cinta, cubos, física y cámaras. |
| **ROS 2** | El «sistema nervioso» de los robots: muchos programas pequeños (**nodos**) que se mandan mensajes por **topics** (canales con nombre, como `/emergency_stop`). |
| **launch** | Un fichero que arranca de golpe varios nodos de ROS 2. |
| **Controlador `<extern>`** | Un robot de Webots cuyo programa no corre dentro de Webots sino fuera (en el contenedor de ROS 2), conectado por red. |
| **Supervisor** | Un «robot» invisible de Webots con superpoderes: puede ver y mover cualquier objeto del mundo. Aquí hay dos: el almacén y la bandeja. |
| **Cinemática inversa (IK)** | El cálculo que dice qué ángulo poner en cada articulación del brazo para que la pinza llegue a un punto. |
| **TCP** | *Tool Center Point*: el punto entre los dedos de la pinza, el que se lleva a los sitios. |
| **URDF** | Un fichero de texto que describe las piezas de un robot y cómo se unen. |
| **Loader / Sorter** | Los dos brazos: el que **carga** la cinta y el que **clasifica**. |
| **Tope** | La pieza al final de la cinta donde se paran los cubos para que el Sorter los coja. |
| **Bandeja (shuttle)** | Un ayudante invisible que deja cada cubo bien colocado en el tope. |
| **Lote** | Una tanda de fabricación: «haz 10 tuercas». |
| **Pedido, stock, reparto, albarán** | Lo que pide un cliente; lo que hay guardado en el almacén; la entrega al cliente; el papel que acompaña la entrega. |
| **Factura rectificativa** | La factura que anula otra que estaba mal (una factura nunca se borra ni se edita). |
| **Raspberry Pi Pico** | Una placa diminuta (unos 5 €) que se programa en **MicroPython**; se carga con **Thonny**. |
| **HC-SR04 / OLED** | Un sensor de distancia por ultrasonidos / una pantallita. |
| **FastAPI / SQLite** | Con qué está hecha la web: el servidor (FastAPI, en Python) y la base de datos (SQLite, un solo fichero). |
| **Cadena / línea de producción** | Una celda completa (un Webots con sus dos robots). Puede haber varias trabajando para la misma web. |
| **Nº Máquina / Grupo Cadena** | El número de cada línea y el grupo de líneas que fabrica un producto; sirven para que dos líneas no hagan el mismo pedido. |

---

## Parte 2 — La orden para Claude Code

Copia y pega esto en Claude Code, dentro de la carpeta del proyecto:

```text
Lee entero el fichero «Promt Genera Proyecto Virtual Robotic.md» de esta
carpeta (en trozos si hace falta, incluidos los anexos del final). Construye
el proyecto que describe, FASE A FASE según la sección 4, respetando al
carácter los nombres, los números y las rutas. Al terminar cada fase, pasa sus
pruebas, enséñame lo que has medido de verdad (no lo que supones) y espera a
que te diga «sigue». No inventes valores: si algo no está en el fichero,
pregúntame. Háblame siempre en castellano y en lenguaje sencillo, como a un
aficionado.
```

---

## Parte 3 — Especificación completa (para Claude Code)

A partir de aquí el texto va dirigido a Claude Code. Las explicaciones siguen
siendo sencillas, pero los números y los nombres son exactos.

**Índice**: 1 Cómo trabajar · 2 Visión de conjunto · 3 Carpetas · 4 Fases ·
A Entorno, Docker y scripts · B Mundo de Webots · C Paquete ROS 2 (C.1 paquete,
C.2 URDF, C.3 launch, C.4 topics, C.5 driver del brazo, C.6 almacén, C.7
bandeja, C.8 configuración de la línea, C.9 cinemática, C.10 visión, C.11 clase
común, C.12 Loader, C.13 Sorter, C.14 panel de control, C.15 puentes, C.16
ventanita de parada) · D Raspberry Pi Pico · E Web de pedidos · F Varias líneas
y Windows · G Documentación · H Validación final · I Lecciones y trampas ·
J Problemas conocidos · Anexo 1 Mundo · Anexo 2 URDF de la cinemática.

### 1. Cómo tienes que trabajar

1. **Idioma.** Todo en **castellano**: comentarios, mensajes de log, interfaz y
   documentación. Explica las cosas al usuario como a un aficionado, sin
   jerga (y si usas una palabra técnica, dila en cristiano la primera vez).
   Las interfaces que lo piden (web y panel) se traducen además a inglés y
   euskera.
2. **Los números son sagrados.** Casi todas las constantes de este proyecto
   se ajustaron **midiendo en vivo** tras fallos reales (pinzas rotas, cubos
   perdidos, agarres falsos). Un valor «más redondo» o «más lógico» rompe
   cosas que costaron días. Si un valor parece raro, la especificación explica
   por qué es así: **no se toca**.
3. **Los nombres son un contrato.** Nombres de carpetas (también
   `Lab.Panda 2.4`, con espacio, y `Rasberry_Pi_Pico`, con la errata),
   contenedores, redes, topics, parámetros, `DEF` del mundo, nombres de robot,
   puertos, rutas de la web y comandos de las Pico se usan en muchos sitios a
   la vez. Respétalos al carácter.
4. **Fase a fase.** Construye por fases (sección 4). Una fase solo está hecha
   cuando pasan sus pruebas **medidas** (números reales, logs reales). Enseña
   el resultado y espera al usuario.
5. **Primera línea de versión.** Cada fichero fuente que crees o edites lleva
   en su primera línea un comentario con la fecha y hora reales (sácalas con
   `date "+%Y-%m-%d %H:%M"`) y qué cambia, por ejemplo
   `# Version: 2026-09-27 10:15 -- Loader: espera de hueco en la cinta`.
   Excepciones: en los scripts ejecutables la línea `#!` va **siempre la
   primera** y la de versión justo debajo; en los `.md` la primera línea es
   `_Última modificación: AAAA-MM-DD HH:MM_`; en HTML es un comentario
   `<!-- Version: ... -->`.
6. **Los comentarios explican el porqué**, sobre todo cuando un valor viene de
   un fallo medido.
7. **Código compartido Loader/Sorter.** Un ajuste que solo necesita un robot
   se hace como **atributo de la instancia** con valor por defecto en la clase
   común y sobrescrito en la subclase. Nunca cambiando una constante global ni
   un paso común para arreglar un robot (rompió dos veces al otro).
8. **Busca el patrón, no el síntoma.** Al arreglar un fallo, busca el mismo
   patrón en todo el código y no lo vuelvas a escribir en código nuevo.
9. **Tras editar un `.py` de ROS 2**: `colcon build` **y** matar y relanzar el
   proceso que lo usa. Probar un comando suelto en otra terminal no prueba el
   código que está corriendo.
10. **Un solo proceso de cada cosa.** Dos copias del mismo programa mandando
    órdenes al mismo brazo ya rompieron la pinza. Compruébalo con `ps`.
11. **Negocio:** nunca repartas stock a pedidos por tu cuenta
    (`/almacen/repartir`, `/reparto/expedir`): es decisión del usuario.
12. **Secretos:** nunca escribas claves reales en ficheros que vayan a Git.
    Las de la Wi-Fi de la Pico van en plantillas.
13. **Git:** un commit local al cerrar cada fase (mensaje en castellano que
    explique la causa, no solo el cambio). No subas nada a ningún remoto si el
    usuario no lo pide.
14. **Si algo no está aquí, pregunta.** No inventes valores.

### 2. Qué es el sistema (visión de conjunto)

Una **celda industrial simulada** en Webots con dos brazos Franka Emika Panda,
conectada opcionalmente a hardware real (dos Raspberry Pi Pico) y a un
**sistema de pedidos, almacén y facturación** web. Los cubos de colores hacen
de productos reales (tornillos, tuercas, arandelas…).

Flujo de producción:

1. Un cliente hace un **pedido** en la web. El pedido nace a nombre del
   *Grupo Cadena* de su producto.
2. En el **panel de control** de una línea (o en modo Automático) se lanza un
   **lote**: «fabrica N unidades del producto X».
3. El **Loader** coge cubos de su caja (solo hay 3 cubos físicos: rojo, verde y
   azul; usa los tres para cualquier producto) y los deja en la **cinta**.
4. La cinta lleva el cubo hasta el **tope**. La **bandeja** (un Supervisor) lo
   centra y lo gira 10°.
5. El **Sorter** lo ve con su cámara cenital, lo coge y lo deja en la caja de
   su color.
6. Al confirmarse la entrega, el **almacén** (otro Supervisor) teletransporta
   ese cubo de vuelta a la caja del Loader: 3 cubos bastan para fabricar sin
   fin.
7. Cada entrega se avisa por HTTP a la web, que suma la pieza al stock y, si el
   **reparto automático** está activo, la asigna al pedido que toca. Con la
   **expedición automática**, un pedido completo sale solo con su **albarán**.
   Los albaranes se juntan en **facturas**.
8. Cada robot enciende **su LED** (una Pico por robot) con el color del cubo
   que agarra; el Loader tiene además un LED y una pantalla de **producto**.
9. Dos **botones físicos** (uno por Pico), un **sensor de proximidad** y el
   panel **paran la celda entera**; el rearme continúa exactamente donde se
   quedó (es una pausa, no un aborto).

```
                              ┌──────────────── PC anfitrión (Linux con X11) ───────────────────┐
 Pico W (Sorter) ── Wi-Fi ────┼──► :5002 button_listener (dentro de ros2_panda_dev24)          │
 IP_DE_LA_PICO:5001 ◄─────────┼─── led_publisher (TCP, una conexión por comando)               │
 Pico (Loader) ──── USB ──────┼──► /dev/ttyACM_LOADER ◄─► led_publisher_usb (serie 115200)     │
                              │                                                                  │
                              │  ┌── red docker "panda_ros_net" (ROS_DOMAIN_ID=31) ─────────┐   │
                              │  │ webots_panda_sim24 ◄── TCP 1234 ──► ros2_panda_dev24     │   │
                              │  │ Webots R2025a                      ROS 2 Humble          │   │
                              │  │ panda_industrial_cell.wbt          launch + nodos + panel│   │
                              │  └────────────────────────────────────────────│─────────────┘   │
                              │                           taller_host:8000 ▼ (host-gateway)     │
                              │  taller_admin_api (FastAPI + SQLite) ── puerto 8000 del PC      │
                              └──────────────────────────────────────────────────────────────────┘
```

En **Windows** cambia la topología: Webots va instalado en el propio Windows
(no en Docker), solo ROS 2 va en un contenedor que llega a Webots por
`host.docker.internal`, y el panel de control se ve en el navegador (noVNC).
Ver sección F.

### 3. Estructura de carpetas (exacta)

`<RAIZ>` es la carpeta del proyecto. Los nombres de carpeta se mantienen
**como en el original** (con el espacio de `Lab.Panda 2.4` y la errata de
`Rasberry_Pi_Pico`), porque los usan los scripts, la web (rutas de manuales) y
la documentación.

```
<RAIZ>/
├── README.md  README.en.md  README.eu.md
├── LANZAR_PROYECTO.md (+ .en.md, .eu.md)       guía de arranque en Linux
├── INSTALAR_WINDOWS.md (+ .en.md, .eu.md)      guía de Windows
├── PROBLEMAS_CONOCIDOS.md (+ .en.md, .eu.md)   el único sitio con problemas y arreglos
├── LICENSE                                     MIT
├── .gitignore  .gitattributes
├── arrancar_todo.sh  cerrar_todo.sh  crear_linea.sh  generar_version.sh  vm_disco_docker.sh
├── arrancar_windows.bat  cerrar_windows.bat  crear_linea_windows.bat
├── img/                                        capturas para los README
├── Documentacion/
│   ├── UsuariosBBDDArranque.txt                clientes y usuarios con los que nace la base de datos
│   ├── PI_PICO_montaje.html                    montaje de las dos Pico (con esquemas)
│   ├── anadir_cadena_produccion.md (+ .html)   guía de varias líneas
│   └── Plantillas/generar_plantillas.py        (opcional, fase 12) plantillas Word de configuración
├── Lab.Panda 2.4/                              LA CELDA
│   ├── .gitignore
│   ├── resumen_proyecto_panda.md (+ .en.md, .eu.md)   se sirve en la web como /manual/panda
│   ├── detalle_tecnico_panda.md
│   ├── img/                                    imágenes del resumen (panda_robot.jpg, ...)
│   ├── .devcontainer/
│   │   ├── docker-compose.yml                  línea 1 en Linux
│   │   ├── docker-compose.windows.yml          cualquier línea en Windows
│   │   ├── docker-compose.windows-sim.yml      prueba en Linux de la topología de Windows
│   │   ├── devcontainer.json
│   │   ├── .env                                (local, NO va a Git) LOADER_PICO_DEVICE=...
│   │   └── webots_asset_cache/                 (local, NO va a Git) texturas descargadas
│   ├── .devcontainer2/                         plantilla de la línea 2
│   │   ├── docker-compose.yml
│   │   └── docker-compose.windows-sim.yml
│   ├── webots/Dockerfile
│   ├── ros2_app/Dockerfile  ros2_app/panel_web.sh
│   ├── worlds/
│   │   ├── panda_industrial_cell.wbt           ANEXO 1, copiado tal cual
│   │   └── vista_solo_3d.wbproj.plantilla
│   └── ros2_ws/
│       └── src/panda_controller/
│           ├── package.xml  setup.py  setup.cfg
│           ├── resource/  panda_controller (vacío)  panda_webots.urdf  panda_ikpy.urdf (ANEXO 2)
│           │              overhead_camera.urdf  overhead_camera_sorter.urdf
│           │              warehouse_supervisor.urdf  sorter_shuttle_supervisor.urdf
│           ├── launch/robot_launch_industrial_cell.py
│           ├── test/  test_copyright.py  test_flake8.py  test_pep257.py   (plantilla estándar ament)
│           └── panda_controller/
│               ├── __init__.py (vacío)
│               ├── my_robot_driver.py                plugin de Webots de cada brazo
│               ├── warehouse_supervisor_driver.py    plugin: almacén, cinta, reloj, letrero
│               ├── sorter_shuttle_supervisor_driver.py  plugin: bandeja
│               ├── panda_ikpy_kinematics.py
│               ├── overhead_vision.py
│               ├── cube_shuttle_demo.py              clase común de los dos robots
│               ├── loader_demo.py   sorter_demo.py
│               ├── config_cadena.py                  configuración de ESTA línea
│               ├── teleop_gui.py                     panel de control
│               ├── estop_panel.py                    ventanita de parada (antigua, redundante)
│               ├── led_publisher.py  led_publisher_usb.py  button_listener.py
│               └── version.py                        (generado, NO va a Git)
├── Taller_Administracion/                      LA WEB
│   ├── Dockerfile  docker-compose.yml  requirements.txt  requirements-dev.txt  pytest.ini  .gitignore
│   ├── README.md (+ .en.md, .eu.md)            uso, para aficionados
│   ├── DETALLE_TECNICO.md (+ .en.md, .eu.md)   por dentro
│   ├── img/                                    capturas para el README
│   ├── app/
│   │   ├── __init__.py  main.py  database.py  models.py  schemas.py  auth.py  codigos.py
│   │   ├── importes.py  auditoria.py  contabilidad.py  datos_arranque.py  cargar_arranque.py
│   │   ├── migraciones.py  version.py (generado, NO va a Git)
│   │   └── static/  landing.html  panel.html  manual.html  guia_administracion.html
│   │                i18n_landing.js  i18n_panel.js  i18n_guia.js
│   │                img/  webots_cell.jpg  pico_hardware.jpg  celda_trabajando_1.jpg/.mp4  celda_trabajando_2.jpg/.mp4
│   ├── data/                                   taller.db (se crea sola, NO va a Git)
│   └── tests/  __init__.py  conftest.py  test_*.py
├── Virtual_Robotic/                            la portada suelta, para abrir con doble clic
│   ├── index.html  i18n_landing.js  README.md  img/
├── Rasberry_Pi_Pico/                           Pico W del Sorter
│   ├── main.py  wifi_config.py (plantilla)  webrepl_cfg.py (plantilla)  LEEME.md
│   └── test_rgb.py  test_boton_led.py  led_gpio14.py  prueba_webrepl.py  test_cliente_pc.py
└── Rasberry_Pi_Pico_USB_Loader/                Pico del Loader
    └── main.py  ssd1306.py  test_hcsr04.py
```

**Lo que existía en el original y NO se construye** (demos y pruebas antiguas
que ya no se usan): las demos de un solo robot (`move_above_ball`,
`pick_and_place`, `visit_balls`, `lift_ball`, `vision_lift_cube`,
`best_color_repeat_lift`, `teleop_manual`, `stack_tower_demo`), las
herramientas de puesta a punto (`grasp_yaw_test`, `sorter_hover_test`,
`cube_vision.py`), los mundos y launch de prueba, la carpeta `controllers/`
(calibración ya hecha), los parches descartados y los PDF desactualizados.

### 4. Orden de construcción (fases)

| Fase | Qué se construye | Secciones | Se da por buena cuando… |
|---|---|---|---|
| 1 | Carpetas, Git, `.gitignore`, `.gitattributes`, `LICENSE`, `generar_version.sh` | 3, A | `git status` limpio; `./generar_version.sh` escribe los dos `version.py` |
| 2 | Web de pedidos: servidor, base de datos, reglas y **tests** | E.1–E.10, E.14 | `docker compose up -d --build` en `Taller_Administracion`; `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/version` → 200; **todos los tests en verde** (pytest dentro del contenedor) |
| 3 | Web de pedidos: panel, portada, manuales e idiomas | E.11–E.13 | En el navegador: `admin`/`admin` entra y ve las 3 secciones; `ere-admin`/`1111` hace un pedido con la cesta; el pedido pasa a *repartido* con albarán al llegar piezas (simuladas con `POST /taller/cubo_clasificado`); ES/EN/EU cambia los textos |
| 4 | Docker de la celda y mundo Webots | A, B, Anexo 1 | Webots abre el mundo y su log muestra **6** `extern controller: Waiting for` |
| 5 | Paquete ROS 2: driver, supervisores, launch | C.1–C.8 | `ros2 launch` → **6** `Controller successfully connected`; `/warehouse/cube_positions` = `0.5,0.16,0.77, 0.35,0.16,0.77, 0.65,0.16,0.77` (±1 mm); `/clock` publica; un solo `button_listener` |
| 6 | Cinemática, visión, clase común y Loader | C.9–C.12, Anexo 2 | `loader_demo cycles:=1` deja los 3 cubos en la cinta: 3 `pinza cerrada (agarre verificado…)` y 0 `agarre falso` |
| 7 | Sorter | C.13 | `sorter_demo` + `loader_demo cycles:=2`: 6 `CUBO CLASIFICADO`, cada cubo en su caja y reciclado a la del Loader; la web recibe 6 piezas |
| 8 | Panel de control `teleop_gui` | C.14 | Jog en ejes del mundo con los dos robots, STOP/REARME, cambiar Loader/Sorter, lanzar un pedido real de la web y ver `Fabricadas: n/n`; pestaña Pico simulada; pestaña Configuración con clave |
| 9 | Firmware de las Pico y puentes | C.15–C.16, D | Con hardware: LED de agarre en las dos Pico, los dos botones y el HC-SR04 paran la celda, la OLED muestra el producto. Sin hardware: los puentes arrancan y no rompen nada |
| 10 | Scripts de Linux y varias líneas | A.6, F.1–F.2 | `./arrancar_todo.sh` levanta todo y abre el panel; `./crear_linea.sh 3` levanta una tercera línea aislada; `./cerrar_todo.sh` deja «Todo limpio» |
| 11 | Windows | F.3 | En un PC con Windows: `arrancar_windows.bat` → 6 controladores y panel en `http://localhost:6080/vnc.html` (si el usuario no tiene Windows, se deja hecho y sin probar, y se dice así) |
| 12 | Documentación (ES, EN, EU) e imágenes | G | Todos los `.md` de la sección 3 escritos; las capturas hechas por el usuario en su sitio |
| 13 | Validación final | H | Lote de **≥15 min**: ritmo de unos **2 clasificados por minuto** y sin rachas de pinza dislocada |

Si el usuario solo quiere la web, las fases 2, 3 y 12 (parte web) bastan.

---

## A. Entorno, Docker y scripts

### A.1 Versiones que funcionan (medidas en el original)

Varias piezas se instalan de repositorios «rodantes» (siempre la última). Estas
son las versiones con las que todo funciona; si algo raro pasa en un montaje
nuevo, es lo primero que hay que mirar.

| Dónde | Pieza | Versión |
|---|---|---|
| Contenedor ROS 2 (`osrf/ros:humble-desktop-full`) | Ubuntu / Python | 22.04 / 3.10 |
| | ROS 2 | Humble |
| | `ros-humble-webots-ros2` | 2025.0.0 |
| | ikpy (pip) | **4.0.0** (fijada) |
| | pyserial (pip) | **3.5** (fijada) |
| | numpy / scipy / OpenCV | los del sistema (1.21 / 1.8 / 4.5) |
| Contenedor Webots (misma imagen base) | Webots | **R2025a** (fijado: `webots=2025a`) |
| Contenedor web (`python:3.12-slim`) | fastapi / uvicorn[standard] / SQLAlchemy / pydantic | 0.115.0 / 0.30.6 / 2.0.35 / 2.9.2 (fijadas) |
| Tests de la web | pytest / httpx / pytest-cov | 8.3.3 / 0.27.2 / 5.0.0 |
| Anfitrión | Docker Engine con `docker compose` v2 | 29.x / 2.40 |

**Webots y `webots-ros2` van por parejas** (R2025a ↔ 2025.0.0). Con Webots
R2023b y el driver 2025.0.0 el Supervisor del almacén da *Segmentation fault*
y las cámaras dejan de entregar imágenes. Por eso Webots se fija a R2025a,
aunque los modelos 3D del mundo vengan de la rama R2023b (ver sección B).

### A.2 Red, puertos y nombres

| Qué | Valor | Notas |
|---|---|---|
| Contenedores (línea 1) | `webots_panda_sim24`, `ros2_panda_dev24` | El `24` viene de la versión 2.4; se mantiene |
| Contenedor web | `taller_admin_api` | Una sola web para todas las líneas |
| Red de la línea 1 | `panda_ros_net` (Compose la llama `devcontainer_panda_ros_net`) | El nombre de la carpeta `.devcontainer` da el nombre de proyecto `devcontainer` |
| ROS 2 | `ROS_DOMAIN_ID=31` (línea N: `30+N`), `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` | |
| Webots ↔ controladores | TCP **1234** (en Windows, línea N: `1233+N`) | Todos los robots `<extern>` comparten puerto; se distinguen por nombre |
| Web | `http://localhost:8000` | Desde el móvil: `http://<IP-del-PC>:8000` |
| Web vista desde el contenedor ROS | `http://taller_host:8000` | `taller_host` = `host-gateway` |
| Webots visto desde el contenedor ROS | `host.docker.internal` | En Linux es un **alias de red** del contenedor de Webots; en Windows apunta al propio Windows. **No confundir con `taller_host`** |
| Pico W (Sorter) | `IP_DE_LA_PICO:5001` (ejemplo, se cambia en el panel) | Servidor TCP de LED |
| Aviso del botón de la Pico W | puerto **5002** del PC | Lo escucha `button_listener`; publicado solo por la línea 1 |
| Panel en el navegador (Windows) | `http://localhost:6080/vnc.html` (línea N: `6079+N`) | noVNC |

### A.3 `Lab.Panda 2.4/webots/Dockerfile`

```dockerfile
FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y \
    wget gnupg2 ca-certificates lsb-release software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Webots FIJADO a R2025a: el repositorio de Cyberbotics es rodante y "webots" a
# secas instala lo que toque ese dia. Con "=2025a" un rebuild futuro FALLA con un
# error claro si deja de estar disponible, en vez de instalar otra en silencio.
# Va emparejado con ros-humble-webots-ros2 2025.0.0 (R2023b + ese driver = segfault
# del Supervisor del almacen y camaras sin imagen).
RUN mkdir -p /etc/apt/keyrings \
    && wget -qO /etc/apt/keyrings/Cyberbotics.asc https://cyberbotics.com/Cyberbotics.asc \
    && echo "deb [signed-by=/etc/apt/keyrings/Cyberbotics.asc] https://cyberbotics.com/debian/ binary-amd64/" > /etc/apt/sources.list.d/Cyberbotics.list \
    && apt-get update \
    && apt-get install -y webots=2025a \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ros-humble-webots-ros2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && exec \"$@\"", "--"]
```

### A.4 `Lab.Panda 2.4/ros2_app/Dockerfile` y `panel_web.sh`

```dockerfile
FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-pip \
    ros-humble-webots-ros2 \
    && rm -rf /var/lib/apt/lists/*

# ikpy: cinematica inversa (panda_ikpy_kinematics.py). Aqui para que sobreviva a recrear el contenedor.
RUN pip3 install ikpy==4.0.0
# pyserial: led_publisher_usb.py (Pico del Loader por USB).
RUN pip3 install pyserial==3.5

# Panel de control en el navegador (Windows y equipos sin pantalla Linux):
# pantalla virtual (Xvfb) + gestor de ventanas minimo (openbox: da el teclado a
# cada ventana nueva y le pone barra de titulo) + VNC (x11vnc) + noVNC en el 6080.
# Solo se usa si se lanza panel_web.sh; en Linux el panel sale como ventana normal.
RUN apt-get update && apt-get install -y \
    xvfb \
    openbox \
    x11vnc \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*
COPY panel_web.sh /usr/local/bin/panel_web.sh
# sed: por si el repo se clono en Windows con saltos de linea CRLF.
RUN sed -i 's/\r$//' /usr/local/bin/panel_web.sh && chmod +x /usr/local/bin/panel_web.sh

WORKDIR /workspace

# Autosource: ROS base y, si existe, el overlay del workspace ya compilado.
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi" >> ~/.bashrc

ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi && exec \"$@\"", "--"]
```

Ojo: `~/.bashrc` solo lo leen las shells interactivas. Los comandos no
interactivos (`docker exec ros2_panda_dev24 bash -c "…"`) tienen que hacer
`source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash`
ellos mismos.

`ros2_app/panel_web.sh` (se puede llamar dos veces sin duplicar nada; **sin**
`set -u`, porque el `setup.bash` de ROS usa variables sin definir):

```bash
#!/usr/bin/env bash
# Version: ... -- panel de control en el navegador (con gestor de ventanas)
# Enciende una pantalla virtual (:99), la sirve por web con noVNC en el 6080 y
# abre en ella el panel (teleop_gui). Se ve en http://localhost:6080/vnc.html
export DISPLAY=:99
ANCHO_ALTO="${PANEL_WEB_RESOLUCION:-1600x900}"
if ! pgrep -x Xvfb >/dev/null; then
  Xvfb :99 -screen 0 "${ANCHO_ALTO}x24" -nolisten tcp >/tmp/xvfb.log 2>&1 &
  sleep 1
fi
if command -v openbox >/dev/null && ! pgrep -x openbox >/dev/null; then
  openbox >/tmp/openbox.log 2>&1 &
  sleep 1
fi
if ! pgrep -x x11vnc >/dev/null; then
  # -localhost: el VNC solo se oye dentro del contenedor; fuera sale solo noVNC.
  x11vnc -display :99 -forever -shared -nopw -localhost -quiet >/tmp/x11vnc.log 2>&1 &
  sleep 1
fi
if ! pgrep -f "[w]ebsockify.*6080" >/dev/null; then
  websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
fi
source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash
exec ros2 run panda_controller teleop_gui
```

### A.5 `Lab.Panda 2.4/.devcontainer/docker-compose.yml` (línea 1, Linux)

```yaml
services:
  webots:
    build:
      context: ../webots
      dockerfile: Dockerfile
    container_name: webots_panda_sim24
    hostname: webots_panda_sim24
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
      - ROS_DOMAIN_ID=31
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ${HOME}/.Xauthority:/root/.Xauthority:ro
      - ../worlds:/workspace/worlds
      # Cache de texturas/mallas que Webots baja de GitHub al cargar el mundo:
      # persistente en el anfitrion para no redescargar en cada recreate (la
      # descarga es lenta e inestable y bloqueaba el arranque en frio).
      - ./webots_asset_cache:/root/.cache/Cyberbotics
    devices:
      - /dev/dri:/dev/dri          # sin tarjeta grafica (VM): comentar esta linea
    networks:
      panda_ros_net:
        aliases:
          - host.docker.internal   # asi encuentra ROS 2 a Webots
    privileged: true
    command: webots --stdout --stderr --batch --mode=realtime /workspace/worlds/panda_industrial_cell.wbt

  ros2_app:
    build:
      context: ../ros2_app
      dockerfile: Dockerfile
    container_name: ros2_panda_dev24
    hostname: ros2_panda_dev24
    environment:
      - ROS_DOMAIN_ID=31
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
      - WEBOTS_SHARED_FOLDER=/tmp/webots_shared:/tmp/webots_shared
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
    volumes:
      - ../ros2_ws:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ${HOME}/.Xauthority:/root/.Xauthority:ro
    networks:
      - panda_ros_net
    ports:
      - "5002:5002"                 # aviso del boton fisico de la Pico W (button_listener)
    extra_hosts:
      - "taller_host:host-gateway"  # para llegar a la web (puerto 8000 del anfitrion)
    # Pico del Loader por USB, OPCIONAL de verdad: un "devices:" con una ruta que
    # no existe tumba el arranque del contenedor entero, asi que por defecto se
    # mapea /dev/null (existe siempre). Para activar la Pico real en una maquina
    # que la tenga: mirar "ls -l /dev/serial/by-id/" (ruta estable, no ttyACM0)
    # y crear .devcontainer/.env (NO va a git) con:
    #   LOADER_PICO_DEVICE=/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_XXXX-if00
    # y "docker compose up -d" para recrear ros2_app.
    devices:
      - "${LOADER_PICO_DEVICE:-/dev/null}:/dev/ttyACM_LOADER"
    depends_on:
      - webots
    stdin_open: true
    tty: true
    command: bash

networks:
  panda_ros_net:
    driver: bridge
```

Detalles que importan:

- El mapeo de la Pico USB se aplica **solo al crear el contenedor**: tras
  reconectar la Pico hace falta `docker compose up -d --force-recreate ros2_app`
  (un `docker restart` no vuelve a aplicar `devices`).
- `ros2_app` monta `../ros2_ws` como `/workspace`: el código se edita en el
  anfitrión y se compila dentro; `build/`, `install/` y `log/` quedan en el
  anfitrión (y no van a Git).
- `devcontainer.json` (para abrir la carpeta con VS Code Dev Containers):

```json
{
  "name": "ROS2 Dev (conectado a Webots - Panda)",
  "dockerComposeFile": "docker-compose.yml",
  "service": "ros2_app",
  "workspaceFolder": "/workspace",
  "shutdownAction": "stopCompose",
  "customizations": { "vscode": { "extensions": ["ms-vscode.cpptools", "ms-python.python", "ms-iot.vscode-ros"] } }
}
```

- `docker-compose.windows-sim.yml` (solo para probar en Linux la topología de
  Windows; se usa con `-f docker-compose.yml -f docker-compose.windows-sim.yml`):
  publica `1234:1234` en el servicio `webots` y en `ros2_app` añade
  `extra_hosts` `taller_host:host-gateway` y `host.docker.internal:host-gateway`
  (el `/etc/hosts` gana al DNS interno, así la conexión sale al anfitrión y
  vuelve a entrar).

### A.6 Scripts de la raíz (Linux)

Todos con `#!/usr/bin/env bash` en la primera línea y la de versión debajo.
Se guardan con saltos de línea **LF** (ver `.gitattributes`).

**`generar_version.sh`** — calcula `Ver. AAMM.NNNNN`: `AAMM` = año y mes del
último commit (`git log -1 --format=%cd --date=format:%y%m`, `0000` si no hay
git) y `NNNNN` = número total de commits con 5 cifras
(`git rev-list --count HEAD`). Escribe
`VERSION = "AAMM.NNNNN"` en `Taller_Administracion/app/version.py` y en
`Lab.Panda 2.4/ros2_ws/src/panda_controller/panda_controller/version.py`, con
la cabecera `# Generado automaticamente por generar_version.sh -- no editar a
mano`. Imprime `Version generada: Ver. ...`. Los dos ficheros van en
`.gitignore` (si se commitean quedan desfasados en el siguiente commit).

**`arrancar_todo.sh`** — arranca todo de un tirón y termina abriendo el panel
(sin tocar las Pico; esas se activan en el panel). `set -e`. Pasos:

0. `generar_version.sh`.
1. `docker compose up -d --build` en `Taller_Administracion`.
2. Plantilla de vista de Webots: `rm -f "Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"`
   y copiar ahí `vista_solo_3d.wbproj.plantilla` (Webots reescribe ese fichero
   como root al salir y un `cp` encima fallaba en silencio: por eso el `rm`
   antes). `xhost +local:docker` (si falla, avisar y seguir).
   `docker compose up -d --build` en `Lab.Panda 2.4/.devcontainer`.
3. Compilar: `docker exec ros2_panda_dev24 bash -c "cd /workspace && colcon build --packages-select panda_controller --symlink-install"`.
4. Lanzar la celda en segundo plano con tres funciones:
   - `esperar_webots N`: cuenta en `docker logs --since <StartedAt del contenedor> webots_panda_sim24`
     las líneas `extern controller: Waiting for` hasta que haya **6** (máximo N s;
     si no, avisa y sigue). Lanzar los controladores antes de que Webots termine
     de cargar les hacía reintentar y dejaba conexiones de más.
   - `lanzar_celda`: **`docker restart ros2_panda_dev24`** (no un `pkill`:
     `pkill` mata `ros2 launch` pero deja vivos a sus hijos, que seguían
     conectados y duplicados), borrar `/tmp/robot_launch.log` y
     `docker exec -d ros2_panda_dev24 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"`.
   - `esperar_controladores N`: cuenta `Controller successfully connected` en
     ese log hasta **6** (ojo: `grep -c` devuelve código 1 con 0 coincidencias;
     añadir `; true`).
   - Secuencia: `esperar_webots 120` → `lanzar_celda` → `esperar_controladores 60`.
     Si no conectan: `docker restart webots_panda_sim24` (arreglo conocido del
     arranque en frío), `esperar_webots 120`, `lanzar_celda`,
     `esperar_controladores 60`; si sigue sin conectar, decir dónde mirar
     (`docker exec ros2_panda_dev24 cat /tmp/robot_launch.log`,
     `docker logs webots_panda_sim24 --tail 30`) y seguir igualmente.
5. Abrir el panel en primer plano:
   `docker exec -it ros2_panda_dev24 bash -c "source … && ros2 run panda_controller teleop_gui"`.
   Poner `-it` **solo si hay una terminal delante** (`[ -t 0 ]`); si no (por
   ejemplo, lanzado desde otro programa), usar `docker exec` sin `-it`: con
   `-it` falla con «the input device is not a TTY». Igual en `crear_linea.sh`.
   Ojo al cerrar: el panel **no atiende la señal normal de terminar**
   (SIGTERM); si hay que cerrarlo a mano, `pkill -KILL`. Y en los `pkill -f`
   escribir el patrón con corchetes (`'[t]eleop_gui'`) para que no se mate a
   sí mismo el propio comando.

**`cerrar_todo.sh`** — sin `set -e` (no debe abortar si no hay nada que
parar): primero `docker compose down` en cada `Lab.Panda 2.4/.devcontainer[0-9]*`
que tenga `docker-compose.yml`, luego en `.devcontainer` y en
`Taller_Administracion`. Al final lista lo que quede con
`docker ps -a --format '{{.Names}}' | grep -E "^(webots_panda_sim24|ros2_panda_dev24)(_linea[0-9]+)?$|^taller_admin_api$"`
y dice «Todo limpio.» o qué queda.

**`vm_disco_docker.sh`** (para una máquina virtual Linux sin sitio: las
imágenes ocupan unos 14 GB) — se lanza con `sudo`. Formatea `/dev/sdb` en ext4
con etiqueta `docker_datos` **solo si no tiene formato**, para Docker
(`systemctl stop docker.socket docker containerd`), monta el disco en
`/srv/docker_datos` (línea `LABEL=docker_datos` en `/etc/fstab`), copia con
`rsync -aHAX` `/var/lib/docker` y `/var/lib/containerd` al disco nuevo, añade
montajes *bind* en `/etc/fstab` y vuelve a arrancar Docker. Es idempotente.

**`crear_linea.sh`** — ver sección F.2.

### A.7 `.gitignore` y `.gitattributes` de la raíz

`.gitignore`:

```
**/ros2_ws/build/
**/ros2_ws/install/
**/ros2_ws/log/
__pycache__/
*.pyc
.claude/
Lab.Panda 2.4/.devcontainer/webots_asset_cache/
Lab.Panda 2.4/.devcontainer/.env
Taller_Administracion/.env
Taller_Administracion/app/version.py
Lab.Panda 2.4/ros2_ws/src/panda_controller/panda_controller/version.py
*.wbproj
claude_memoria/
img/webots_video_*.mp4
```

(Cada bloque con un comentario del porqué: los `.wbproj` los reescribe Webots
y bloqueaban el `git pull` en Windows; el `.env` de la Pico es propio de cada
máquina; los vídeos originales grandes no van a Git.)

`Lab.Panda 2.4/.gitignore`:

```
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
ros2_ws/config_maquina_*.json
ros2_ws/pico_asignacion.json
**/__pycache__/
*.pyc
.vscode/
```

`Taller_Administracion/.gitignore`: `__pycache__/`, `*.pyc`, `data/*.db`.

`.gitattributes` (imprescindible para Windows):

```
# Los .bat necesitan CRLF (con LF, cmd se lia con las etiquetas y los goto).
*.bat text eol=crlf
# Los .sh se ejecutan en Linux o en los contenedores; con CRLF fallan
# ("bash\r: No such file or directory"). Git for Windows los convertia al clonar.
*.sh text eol=lf
```

Opcional: si la carpeta vive dentro de MEGAsync, un `ros2_ws/.megaignore` con
`-d:build`, `-d:install`, `-d:log` (MEGA marcaba como error lo que genera
`colcon`).

`LICENSE`: MIT, con el nombre del autor que diga el usuario y el año 2026.

### A.8 Permisos de Claude Code (recomendado)

Para trabajar cómodo, un `.claude/settings.local.json` (no va a Git) que
permita sin preguntar `docker *`, `docker exec *`, `git *`, `curl *`,
`grep *`, `xhost +local:docker` y `python3 -c '*'`, y que pida confirmación
para `sudo *`. El sandbox de Bash de Claude Code rompe el acceso a Docker y a
la red local de la Pico: no usarlo. Pregunta al usuario qué carpetas
personales quiere que queden fuera de tu alcance.

### A.9 Copias de seguridad (recomendado, fase 12)

Una copia = el historial de git y la base de datos:

```bash
git bundle create "<carpeta>/<nombre>.bundle" --all && git bundle verify "<carpeta>/<nombre>.bundle"
```

La base de datos se copia **en caliente** con la API de `sqlite3` (un `cp`
con el servidor encendido no es seguro), y se comprueba con
`pragma integrity_check` → `ok`:

```python
import sqlite3
src = sqlite3.connect('Taller_Administracion/data/taller.db')
dst = sqlite3.connect('<carpeta>/<nombre> - taller.db')
src.backup(dst); dst.close()
```

Si el usuario tiene un NAS o una carpeta en la nube, se puede hacer un script
`backup_nas.sh` que haga las dos cosas, etiquete el commit (`git tag
backup-AAAA-MM-DD_HH-MM`) y, si el NAS responde a `ping`, sincronice por
`rsync` (si no responde, avisa y deja hecha la copia local). Pregunta al
usuario los datos de su NAS; no los inventes.

---

## B. El mundo de Webots (`worlds/panda_industrial_cell.wbt`)

**El fichero completo va en el Anexo 1: cópialo tal cual, carácter a
carácter.** Aquí se explica qué hay dentro, para entenderlo y para validarlo.
Coordenadas en metros, Z hacia arriba; rotaciones en formato Webots
`eje_x eje_y eje_z ángulo_rad`.

### B.1 Geometría de referencia

- Superficie de mesas y cinta: **z = 0,74**. Cubos de 6 cm: centro en
  **z = 0,77**, cara de arriba en 0,80.
- **Loader**: base en (0,5; −0,3; 0,74), mirando a +Y.
- **Sorter**: base en (0,0; 1,00; 0,74), **girada 26,6°** (0,4636 rad =
  atan2(0,25; 0,50)) hacia el punto de recogida (0,5; 1,25).
- Distribución en **L**: el Sorter está al lado de la cinta, no al final; sus
  cajas de color están delante de él, lejos de la cinta en X (así su cámara no
  confunde un cubo ya clasificado con uno nuevo).
- Alcance fiable del Panda (validado con el solver): profundidad
  `objetivo_y − base_y` entre 0,45 y 0,60 delante del robot; lateral seguro
  hasta ±0,20.
- Sin `basicTimeStep` explícito: paso por defecto de Webots (32 ms).

### B.2 Qué contiene

- Cabecera `#VRML_SIM R2025a utf8`. Los PROTO externos vienen de la rama
  **R2023b** de Webots en GitHub (`TexturedBackground`, `TexturedBackgroundLight`,
  `Floor`, `Panda`, `PandaHand`, `Table`, `ConveyorBelt`) y `Extrusion` de
  **R2025a**. Es una mezcla heredada e inofensiva (solo avisos de
  compatibilidad): **no cambiarla**, la calibración de la cinemática se hizo
  con estos modelos. Algunas texturas no se descargan: es cosmético y aceptado.
- `WorldInfo` con título «Celda Industrial - Loader + Cinta + Sorter».
  `Viewpoint` de arranque en diagonal hacia el centro de la celda
  (`orientation -0.2224 0.0548 0.9734 2.6711`, `position 2.7 -0.75 2.2`).
- **Estación del Loader**: mesa `table_loader` (0,5; −0,33; 0) de
  0,8×1,14×0,74; robot `DEF PANDA_LOADER Panda` `name "Loader"`,
  `controller "<extern>"`, con `PandaHand` y una cámara de muñeca
  `wrist_camera` (publica `/panda_camera`, nadie la usa, pero se deja);
  cámara cenital `DEF OVERHEAD_CAM_LOADER Robot` `name "OverheadCamLoader"` en
  (0,5; 0; 2,27) con una `Camera` `overhead_camera` (girada `0 1 0 1.5708`,
  `fieldOfView 0.9`, 320×240).
- **Caja del Loader de tres paredes** (`CRATE_WALL_FRONT/LEFT/RIGHT`); la del
  lado de la cinta se quitó a propósito (un cubo podía quedar entre pared y
  cinta y la pinza agarraba las dos cosas).
- **Los tres únicos cubos**: `DEF CUBO_ROJO` en (0,5; 0,16; 0,77),
  `DEF CUBO_VERDE` en (0,35; 0,16; 0,77), `DEF CUBO_AZUL` en (0,65; 0,16; 0,77);
  cajas de 0,06 con `physics` de masa 0,05.
- **Dos Supervisores sin cuerpo**: `DEF WAREHOUSE_SUPERVISOR Robot`
  `name "WarehouseSupervisor"` en (3; 3; 1) y `DEF SORTER_SHUTTLE_SUPERVISOR
  Robot` `name "SorterShuttleSupervisor"` en (3; 3,5; 1), los dos `<extern>` y
  `supervisor TRUE`.
- **La cinta** `DEF BELT ConveyorBelt` `name "Belt"` en (0,5; 0,79; 0) girada
  90°, `size 1.1 0.3 0.74`, `speed 0.15`: la banda va de y=0,24 a y=1,34 y de
  x=0,35 a x=0,65. `ConveyorBelt` **no tiene campo `controller`**: solo se para
  cambiando su campo `speed` desde un Supervisor.
- **El tope** `DEF BELT_END_STOP` (palo 5): una `Extrusion` apoyada en la
  cinta (z = 0,740, **no flota**), cuya cara de parada queda en **y = 1,300**
  (medido: el cubo se para con su centro en y = 1,2700).
- **El embudo** (palos 1 y 2): `BELT_RAIL_L_EMBUDO` y `BELT_RAIL_R_EMBUDO`,
  cajas giradas ±0,1543 rad que estrechan la cinta. Flotan a 0,755 a propósito.
- **El tramo recto** (palos 3 y 4, donde agarra el Sorter):
  `BELT_RAIL_L_RECTO` en x=0,460 y `BELT_RAIL_R_RECTO` en x=0,540, `Extrusion`
  apoyadas en 0,740. **Trampa:** el perfil crece hacia fuera desde la
  `translation`, así que las caras interiores reales están en **x = 0,445 y
  x = 0,555** → canal de **11 cm**. Y **no se toca el orden de los vértices**:
  una pieza y su espejo con el mismo orden invierten las caras y los cubos se
  «cuelan» dentro. Los palos 3, 4 y 5 tienen área con signo −0,00435.
- **Estación del Sorter**: marca visual amarilla `DEF SORTER_TRAY` (sin
  física) en (0,5; 1,25; 0,741); `DEF PANDA_SORTER Panda` `name "Sorter"` con
  `rotation 0 0 1 0.4636` y `PandaHand` (sin cámara de muñeca); mesa
  `table_sorter` (0; 1,225; 0) de 0,5×0,85×0,74 (**no ensanchar**: se
  solaparía con la cinta); cámara cenital `DEF OVERHEAD_CAM_SORTER Robot`
  `name "OverheadCamSorter"` en (0,25; 1,30; 2,27) con `Camera`
  `overhead_camera_sorter`.
- **Cajas de color** (placas estáticas de 0,14×0,14×0,02): `CAJA_ROJA` en
  (0; 1,45; 0,75), `CAJA_VERDE` en (−0,15; 1,45; 0,75), `CAJA_AZUL` en
  (0,15; 1,45; 0,75).

### B.3 Por qué el canal mide 11 cm (no tocar)

El Sorter agarra siempre girado +90° (sección C.13): así ningún dedo entra en
el tope, pero los dedos abiertos (8 cm) cruzan el canal. Medido: con 9 cm hubo
25 dislocaciones de pinza por lote; con 11 cm, cero. A 12 cm caben dos cubos en
paralelo. El único rango válido es [110..120) mm y se está en 110. La fracción
de cubos imposibles de coger es `2·margen/(canal − lado)`: estrechar el canal
es la dirección equivocada.

### B.4 Nombres que el código busca en el mundo (contrato)

| Quién | Busca | Por |
|---|---|---|
| Launch | Robots `Loader`, `Sorter`, `OverheadCamLoader`, `OverheadCamSorter`, `WarehouseSupervisor`, `SorterShuttleSupervisor` | `name` |
| `my_robot_driver` | `panda_joint1..7`, `panda_finger::right`, `panda_finger::left`, `panda_finger::right_sensor`, `panda_finger::left_sensor` | dispositivos del PROTO |
| URDF de cámaras | `overhead_camera`, `overhead_camera_sorter`, `wrist_camera` | `name` de la Camera |
| Supervisores | `CUBO_ROJO`, `CUBO_VERDE`, `CUBO_AZUL`, `BELT` | `DEF` |

### B.5 Plantilla de vista (`worlds/vista_solo_3d.wbproj.plantilla`)

Webots guarda qué paneles se ven en `worlds/.panda_industrial_cell.wbproj` y
lo reescribe al salir. Los scripts copian esta plantilla antes de arrancar
para que Webots abra **solo con la vista 3D** (sin árbol de escena, consola ni
editor) y con las tres cámaras visibles. Contenido exacto:

```
Webots Project File version R2025a
perspectives: 000000ff00000000fd00000002000000010000011c00000333fc0200000001fb0000001400540065007800740045006400690074006f00720000000015000003330000003f00ffffff0000000300000780000000d9fc0100000001fb0000001a0043006f006e0073006f006c00650041006c006c0041006c006c0000000000000007800000006900ffffff000006620000033300000001000000020000000100000008fc00000000
simulationViewPerspectives: 000000ff000000010000000200000000000006620100000002010000000100
sceneTreePerspectives: 000000ff00000001000000030000021e000000d9000000000100000002010000000200
maximizedDockId: -1
centralWidgetVisible: 1
orthographicViewHeight: 1
textFiles: -1
consoles: Console:All:All
renderingDevicePerspectives: Loader:wrist_camera;1;1;0;0
renderingDevicePerspectives: OverheadCamLoader:overhead_camera;1;1;0;0
renderingDevicePerspectives: OverheadCamSorter:overhead_camera_sorter;1;1;0;0
```

### B.6 Cómo validar un cambio de geometría

Cambiar → reiniciar Webots → **mirar la pieza en pantalla** → medir con un
cubo suelto: soltarlo con `/warehouse/mover_cubo_manual` (`COLOR:X:Y`) y
registrar `/warehouse/cube_positions`. Nunca fiarse solo del número de la
`translation`.

---

## C. El paquete ROS 2 `panda_controller`

Paquete **ament_python** en `Lab.Panda 2.4/ros2_ws/src/panda_controller/`.
Todo el código Python de la celda vive aquí, también los plugins que Webots
carga a través de `webots_ros2_driver`. Se compila dentro de
`ros2_panda_dev24`, en `/workspace`:

```bash
colcon build --packages-select panda_controller --symlink-install
```

### C.1 `package.xml`, `setup.py`, `setup.cfg`

`package.xml` (formato 3): nombre `panda_controller`, versión `0.0.1`,
descripción «Controlador ROS2 para el brazo Franka Emika Panda (con pinza
real) en Webots», licencia Apache-2.0; `depend`: `rclpy`,
`webots_ros2_driver`, `geometry_msgs`, `sensor_msgs`, `std_msgs`,
`rosgraph_msgs`; `test_depend`: `ament_copyright`, `ament_flake8`,
`ament_pep257`, `python3-pytest`; `build_type` `ament_python`.

`setup.cfg`:

```
[develop]
script_dir=$base/lib/panda_controller
[install]
install_scripts=$base/lib/panda_controller
```

`setup.py`: `packages=['panda_controller']`; `data_files` con el índice
ament (`resource/panda_controller`, fichero vacío), `package.xml`,
`launch/*.py` en `share/panda_controller/launch` y `resource/*.urdf` en
`share/panda_controller/resource`; `install_requires=['setuptools', 'ikpy']`.
Puntos de entrada (`console_scripts`):

```
teleop_gui        = panda_controller.teleop_gui:main
led_publisher     = panda_controller.led_publisher:main
led_publisher_usb = panda_controller.led_publisher_usb:main
button_listener   = panda_controller.button_listener:main
estop_panel       = panda_controller.estop_panel:main
loader_demo       = panda_controller.loader_demo:main
sorter_demo       = panda_controller.sorter_demo:main
```

### C.2 Recursos URDF (contenido exacto)

`webots_ros2_driver` usa estos URDF para saber qué plugin cargar y qué
dispositivos puentear a ROS.

`resource/panda_webots.urdf` (los dos brazos):

```xml
<?xml version="1.0"?>
<robot name="Panda">
  <webots>
    <plugin type="panda_controller.my_robot_driver.MyRobotDriver" />
    <device reference="panda_joint1" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint2" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint3" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint4" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint5" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint6" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_joint7" type="RotationalMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_finger_joint1" type="LinearMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="panda_finger_joint2" type="LinearMotor"><ros><enabled>true</enabled></ros></device>
    <device reference="wrist_camera" type="Camera">
      <ros>
        <enabled>true</enabled>
        <topicName>/panda_camera</topicName>
      </ros>
    </device>
  </webots>
</robot>
```

(`panda_finger_joint1/2` no existen en el PROTO: los dedos de verdad se llaman
`panda_finger::right/left` y los mueve el plugin. Se dejan así.)

`resource/overhead_camera.urdf`:

```xml
<?xml version="1.0"?>
<robot name="overhead_camera">
  <link name="base_link"/>
  <webots>
    <device reference="overhead_camera" type="Camera">
      <ros>
        <enabled>true</enabled>
        <!-- 10 imagenes por segundo de simulacion en vez de una por paso (31): desde
             Docker Desktop cada imagen viaja por TCP a Webots y frenaba la celda.
             La vision pide un fotograma nuevo cuando lo necesita. -->
        <updateRate>10</updateRate>
        <topicName>/overhead_camera</topicName>
      </ros>
    </device>
  </webots>
</robot>
```

`resource/overhead_camera_sorter.urdf`: igual, con `robot name="overhead_camera_sorter"`,
`reference="overhead_camera_sorter"` y `topicName` `/overhead_camera_sorter`
(también `updateRate` 10).

`resource/warehouse_supervisor.urdf`:

```xml
<?xml version="1.0"?>
<robot name="warehouse_supervisor">
  <link name="base_link"/>
  <webots>
    <plugin type="panda_controller.warehouse_supervisor_driver.WarehouseSupervisorDriver" />
  </webots>
</robot>
```

`resource/sorter_shuttle_supervisor.urdf`: igual, con `robot
name="sorter_shuttle_supervisor"` y `plugin
type="panda_controller.sorter_shuttle_supervisor_driver.SorterShuttleSupervisorDriver"`.

`resource/panda_ikpy.urdf`: **Anexo 2, copiado tal cual.**

### C.3 Launch `launch/robot_launch_industrial_cell.py`

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_controller import WebotsController

# Puerto de Webots (1234 si no se dice otra cosa). Solo cambia si en la MISMA
# maquina corre mas de un Webots (varias cadenas en Windows).
WEBOTS_PORT = os.environ.get('WEBOTS_PORT', '1234')


def generate_launch_description():
    d = get_package_share_directory('panda_controller')
    r = lambda f: os.path.join(d, 'resource', f)
    return LaunchDescription([
        WebotsController(robot_name='Loader', namespace='loader', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('panda_webots.urdf')}]),
        WebotsController(robot_name='Sorter', namespace='sorter', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('panda_webots.urdf')}]),
        WebotsController(robot_name='OverheadCamLoader', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('overhead_camera.urdf')}]),
        WebotsController(robot_name='OverheadCamSorter', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('overhead_camera_sorter.urdf')}]),
        WebotsController(robot_name='WarehouseSupervisor', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('warehouse_supervisor.urdf')}]),
        WebotsController(robot_name='SorterShuttleSupervisor', port=WEBOTS_PORT,
                         parameters=[{'robot_description': r('sorter_shuttle_supervisor.urdf')}]),
        # El puente del boton de la Pico W va AQUI: antes era un paso manual aparte
        # y se olvidaba (el boton "no funcionaba").
        Node(package='panda_controller', executable='button_listener'),
    ])
```

(En el original cada controlador va en una variable con su comentario; el
resultado es este.) Resultado esperado: **6** líneas `Controller successfully
connected`. **El `namespace=` de `WebotsController` NO llega al plugin
Python** (allí `properties` llega vacío): solo afecta al nodo nativo y al
puente de cámara. Por eso el driver se pone el namespace él solo (C.5).

### C.4 Mapa de topics y llamadas HTTP

QoS por defecto (profundidad 10) salvo que se diga otra cosa. Los nombres
relativos (sin `/`) cuelgan del namespace del proceso (`/loader` o `/sorter`).

| Topic | Tipo | Publica | Escucha | Contenido |
|---|---|---|---|---|
| `/loader/joint_positions`, `/sorter/joint_positions` | `std_msgs/Float64MultiArray` | demos, panel | driver del robot | 7 ángulos **reales** (rad) |
| `/loader/gripper_position`, `/sorter/gripper_position` | `std_msgs/Float64` | demos, panel | driver | apertura por dedo (m, 0..0,04), la misma a los dos dedos |
| `/loader/gripper_state`, `/sorter/gripper_state` | `Float64MultiArray` | driver (cada paso) | demos | `[sensor_dedo_right, sensor_dedo_left]` en m |
| `/overhead_camera/image_color` | `sensor_msgs/Image` (BGRA 320×240) | cámara del Loader | Loader, panel | |
| `/overhead_camera_sorter/image_color` | `sensor_msgs/Image` | cámara del Sorter | Sorter, panel | |
| `/panda_camera/image_color` | `sensor_msgs/Image` | muñeca del Loader | nadie | |
| `/clock` | `rosgraph_msgs/Clock` | almacén (cada paso) | demos | hora de la **simulación** |
| `/warehouse/cube_positions` | `Float64MultiArray` | almacén (cada paso) | demos | 9 valores fijos `Rx,Ry,Rz, Gx,Gy,Gz, Bx,By,Bz` (posición real) |
| `/warehouse/cube_delivered` | `std_msgs/String` | Sorter | almacén, panel | `R`/`G`/`B` (color **físico** real) |
| `/warehouse/belt_pause` | `std_msgs/Bool` | Sorter | almacén (velocidad de la cinta), bandeja (se congela), Loader (espera) | `true` = cinta parada |
| `/warehouse/mover_cubo_manual` | `std_msgs/String` | a mano | almacén | `COLOR:X:Y` (z fija 0,77, giro 0) |
| `/emergency_stop` | `std_msgs/Bool` | `button_listener`, `led_publisher_usb`, panel, `estop_panel`, demos (parada automática por pinza) | demos, panel, `estop_panel` | `true` = parada, `false` = rearme. **Global** |
| `/comando_led` | `std_msgs/String` | Sorter, demos (alarma), panel | `led_publisher` (Pico W) | `R`/`G`/`B`/`0` (+ sinónimos), `parada`, `rearme` |
| `/comando_led_loader` | `std_msgs/String` | Loader, demos (alarma), panel, `estop_panel` | `led_publisher_usb` | igual |
| `/comando_led_producto` | `std_msgs/String` | Loader (enciende), Sorter (apaga al cerrar el lote) | `led_publisher_usb`, panel | letra de color (`R G B Y M C W`), `SINCOLOR` o `0` |
| `/texto_producto` | `std_msgs/String` | panel | `led_publisher_usb` (OLED), panel (OLED simulada) | `nombre\|variante\|código`, vacío, o `MSG:título\|línea` |
| `/reset_clave_pedido` | `std_msgs/Bool` | `led_publisher_usb` | panel | pulsación larga (10 s) del botón del Loader |
| `/production/nuevo_lote` | `std_msgs/Bool` | panel | Sorter | `true` al lanzar cada lote |
| `/production/lote_color_objetivo` | `std_msgs/String` | panel | Sorter | `COLOR:CANTIDAD:PEDIDO_ID:FORZAR:PRODUCTO_ID`. **QoS profundidad 1, `TRANSIENT_LOCAL`** en los dos lados |
| `/teleop_auto_cmd` | `std_msgs/String` | scripts externos | panel | `move dx dy dz`, `open`, `close`, `home`, `align`, `rotate grados` |

**Llamadas HTTP de la celda a la web** (todas con **timeout de 1,5 s** y «mejor
esfuerzo»: un fallo se apunta en el log y **nunca** para un robot):

| Quién | Llamada | Cuándo |
|---|---|---|
| Sorter | `POST /taller/cubo_clasificado {color, forzar_reparto, numero_maquina, grupo_cadena[, pedido_id][, producto_id]}` | tras cada entrega real |
| Loader y Sorter | `POST /taller/evento_produccion {robot, color, tipo}` | eventos de diagnóstico |
| Panel | `POST /login` (admin/admin), `GET /pedidos` (cabecera `X-Session-Token`), `POST /pedidos/{id}/reclamar`, `POST /taller/cubo_clasificado` («+1 pieza») | panel |

La URL base es `http://taller_host:8000` salvo que en la pestaña
Configuración del panel se haya guardado otra (línea en otro ordenador); los
demos la **releen en cada aviso** (C.8).

**Procesos con la celda funcionando** (dentro de `ros2_panda_dev24`, **una sola
generación** de cada uno): `ros2 launch …` con sus 6 drivers y
`button_listener`; `led_publisher` y/o `led_publisher_usb` (si hay Pico);
`teleop_gui`; `sorter_demo` (persistente entre lotes) y `loader_demo` (uno por
lote), lanzados por el panel.

### C.5 `my_robot_driver.py` — plugin de Webots de cada Panda

Clase `MyRobotDriver` con el patrón de plugin de `webots_ros2_driver`:
`init(self, webots_node, properties)` y `step(self)`. Una instancia por brazo.

```python
JOINT_NAMES = ['panda_joint1', ..., 'panda_joint7']
FINGER_JOINT_NAMES = ['panda_finger::right', 'panda_finger::left']          # LinearMotor
FINGER_SENSOR_NAMES = ['panda_finger::right_sensor', 'panda_finger::left_sensor']
HOME_POSITIONS = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
COMMANDED_VELOCITY = 1.4    # rad/s por articulacion
FINGER_VELOCITY = 0.02      # m/s de los dedos
FINGER_FORCE = 20.0         # N maximos por dedo (el PROTO admite 100)
```

Por qué: `panda_joint4` no admite 0 (su máximo es −0,4), `HOME` es la
postura «ready» de Franka. `COMMANDED_VELOCITY = 1.4` va **emparejada** con
`step_sleep = 0.15` de los demos (si se toca una, se toca la otra); 2,0 se
probó y se descartó (cubos soltados por inercia, pinza dislocada).
`FINGER_VELOCITY` 0,02 suaviza el golpe de cierre (con 0,05 empujaba al cubo
vecino). `FINGER_FORCE` 20 N: con 100 un cierre asimétrico lanzaba el cubo;
con 5 el agarre girado no sujetaba.

`init`:

1. Listar por `print` **todos** los dispositivos del robot (diagnóstico).
2. Cada articulación: `getDevice`; si falta, aviso y `None`. Si existe:
   `setPosition(home)` y `setVelocity(COMMANDED_VELOCITY)` (en `try`:
   `setPosition` sola no mueve si la velocidad del PROTO es 0).
3. Cada dedo: `setVelocity(FINGER_VELOCITY)` y `setAvailableForce(FINGER_FORCE)`
   (cada una en su `try`). Sensores de dedo: `enable(int(robot.getBasicTimeStep()))`.
4. **Namespace**: `nombre = robot.getName()`;
   `namespace = None if nombre == 'Panda' else nombre.lower()` → `loader` /
   `sorter`. `rclpy.init(args=None)`; `rclpy.create_node('panda_driver', namespace=namespace)`.
5. Suscripciones **relativas** `joint_positions` (`Float64MultiArray`) y
   `gripper_position` (`Float64`); publicador relativo `gripper_state`.
6. Imprimir los límites de cada motor (`getMinPosition`/`getMaxPosition`).

Callbacks y paso: `joint_positions` → `setPosition` a los 7 (ignorando
`None`); `gripper_position` → el mismo valor a los dos dedos. Los mensajes de
cada comando van a **DEBUG**, no INFO (8 líneas por comando llenaban el log:
más de 70.000 en media hora). `step()`: `rclpy.spin_once(node, timeout_sec=0)`
y publicar `gripper_state = [sensor o nan, …]` **en cada paso**.

Límites reales de referencia: articulaciones `[-2.9671, 2.9671]`,
`[-1.8326, 1.8326]`, `[-2.9671, 2.9671]`, `[-3.1416, -0.4]`,
`[-2.9671, 2.9671]`, `[-0.0873, 3.8223]`, `[-2.9671, 2.9671]`; dedos `[0, 0.04]` m.

### C.6 `warehouse_supervisor_driver.py` — almacén, cinta, reloj y letrero

Plugin del robot `WarehouseSupervisor` (`supervisor TRUE`). Nodo
`warehouse_supervisor`, sin namespace.

```python
CRATE_POSITIONS = {'R': (0.5, 0.16, 0.77), 'G': (0.35, 0.16, 0.77), 'B': (0.65, 0.16, 0.77)}
CUBE_DEF_NAMES = {'R': 'CUBO_ROJO', 'G': 'CUBO_VERDE', 'B': 'CUBO_AZUL'}
FLOOR_Z = 0.5 ; CHECK_PERIOD_S = 1.0 ; GRACE_S = 3.0
SORTER_PICKUP_X, SORTER_PICKUP_Y = 0.5, 1.25 ; PICKUP_CHECK_RADIUS = 0.20
CRATE_ZONE = ((0.15, 0.85), (-0.15, 0.35))
BELT_ZONE  = ((0.20, 0.80), (0.35, 1.40))
BOXES_ZONE = ((-0.35, 0.35), (1.30, 1.60))
LEGIT_ZONES = (CRATE_ZONE, BELT_ZONE, BOXES_ZONE)
GRACE_LOST_S = 30.0 ; GRACE_STUCK_S = 90.0 ; STUCK_MOVE_EPS = 0.02
LETRERO_PERIODO_S = 2.0 ; LETRERO_ID = 0 ; LETRERO_COLOR = 0xF5C400 ; LETRERO_TAMANO = 0.075
```

`_in_zone(x, y, ((x0, x1), (y0, y1)))` = `x0 ≤ x ≤ x1 and y0 ≤ y ≤ y1`.

- `init`: localizar los 3 `DEF` de cubo (aviso si falta alguno);
  `belt = getFromDef('BELT')`, campo `speed` y velocidad normal = su valor
  inicial (0,15). Nodo ROS. Suscripciones: `/warehouse/cube_delivered`,
  `/warehouse/belt_pause`, `/warehouse/mover_cubo_manual`. Publicadores:
  `/warehouse/cube_positions` y **`/clock`**. Log `Almacen listo -- n/3 cubos
  localizados, … Control de cinta: OK (velocidad normal 0.15 m/s, escuchando
  /warehouse/belt_pause).`
- `belt_pause`: `speed = 0.0` si `true`, la normal si `false`.
- `cube_delivered` (color): si el cubo real sigue a menos de
  `PICKUP_CHECK_RADIUS` del punto de recogida → **entrega falsa**: log de
  error y **no** se recicla. Si no → reciclar con motivo «entrega confirmada
  por el Sorter».
- Reciclar = `translation = CRATE_POSITIONS[color]`, `rotation = [0, 0, 1, 0]`,
  `resetPhysics()` y log `Cubo C reciclado de vuelta a la caja del Loader en (…) (motivo).`
- `mover_cubo_manual` (`COLOR:X:Y`): el mismo teletransporte a `(x, y, 0.77)`;
  formato inválido o color desconocido → aviso.
- `step()`: `spin_once(0)`; publicar **`/clock`** con `robot.getTime()`
  (segundos y nanosegundos) en **cada paso**; publicar las 9 posiciones en cada
  paso (orden R, G, B; `0,0,0` si falta un cubo); cada `LETRERO_PERIODO_S` de
  tiempo **real** (`time.monotonic`), actualizar el letrero; cada
  `CHECK_PERIOD_S` de tiempo de simulación:
  - **Caídos**: `z < FLOOR_Z` durante `GRACE_S` seguidos → reciclar («rescate
    automatico, cubo caido»).
  - **Perdidos**: fuera de las 3 zonas durante `GRACE_LOST_S` → reciclar
    («… cubo perdido lejos de las zonas de trabajo»).
  - **Atascados**: dentro de `BELT_ZONE` moviéndose menos de `STUCK_MOVE_EPS`
    desde una referencia durante `GRACE_STUCK_S` → reciclar («… cubo atascado
    en la cinta»). Un movimiento mayor reinicia la referencia. En la caja o en
    las cajas de color no se mira el atasco.
- **Por qué `/clock`**: nadie publicaba la hora de la simulación y los robots
  medían sus esperas con el reloj del ordenador; en un PC lento (Webots a
  0,22x) todo les pasaba 4-5 veces más deprisa dentro de la simulación: el
  brazo no llegaba, la pinza cerraba a destiempo y el dedo del Sorter se
  dislocaba en 4 de 7 agarres.
- **Letrero**: pinta arriba a la izquierda de la vista 3D el nombre de la
  línea, leído del mismo fichero que guarda el panel (`config_cadena.leer()`;
  este plugin corre en el contenedor ROS de su línea, así que el `hostname`
  coincide). Texto:
  `f'{nombre o "Cadena sin nombre"}\nGrupo {grupo_cadena, 0}  ·  Máquina {numero_maquina, 1}'`.
  Solo llama a `robot.setLabel(LETRERO_ID, texto, 0.01, 0.01, LETRERO_TAMANO,
  LETRERO_COLOR, 0.0, 'Arial Black')` si el texto cambió. Un fallo del letrero
  nunca tumba el almacén (`try`, aviso por `print`).

### C.7 `sorter_shuttle_supervisor_driver.py` — la bandeja

Plugin del robot `SorterShuttleSupervisor` (`supervisor TRUE`). Nodo
`sorter_shuttle_supervisor`. Lee la posición real de los cubos por `getFromDef`
(no depende de otro nodo); de ROS solo escucha `/warehouse/belt_pause`.

```python
PICKUP_X, PICKUP_Y, DOCK_Z = 0.5, 1.25, 0.77
DOCK_YAW_DEG = 10.0 ; DOCK_YAW_RAD = math.radians(DOCK_YAW_DEG)
CATCH_RADIUS = 0.035     # < 6 cm entre cubos en cola: solo engancha al que ya toca el tope
RELEASE_RADIUS = 0.15    # mas lejos: el Sorter ya se lo llevo
CHECK_PERIOD_S = 0.5 ; STABLE_TOLERANCE = 0.01
STOP_FACE_Y = 1.300 ; CUBE_HALF = 0.03 ; DOCK_HOLGURA_TOPE = 0.001
DOCK_Y_MAX = STOP_FACE_Y - CUBE_HALF * (math.cos(DOCK_YAW_RAD) + math.sin(DOCK_YAW_RAD)) - DOCK_HOLGURA_TOPE  # 1.26425
```

- Estado: `docked` (colores ya encajados), última lectura por color, último
  chequeo y `paused`.
- `belt_pause` → `paused`. **Mientras está en pausa no se toca nada**: el
  Sorter ya está bajando a por ese cubo (teletransportarlo bajo la pinza la
  rompió una vez).
- `step()`: `spin_once(0)`; si `paused`, salir; cada `CHECK_PERIOD_S`, para
  cada cubo, `dist` al punto de recogida:
  - Si está en `docked`: si `dist > RELEASE_RADIUS`, sacarlo de `docked`. Nada más.
  - Si `dist > CATCH_RADIUS`: olvidar su última lectura.
  - Si hay lectura anterior y `|Δx|` y `|Δy|` < `STABLE_TOLERANCE` → **encajar**.
    Si no, guardar la lectura.
- **Encajar**: corrige **solo X y el giro, la Y se queda** (igualarla a 1,25
  mandaba el cubo 1,6 cm atrás, la cinta lo reempujaba descentrado y
  permitía dos cubos en el mismo sitio). `y = min(y_real, DOCK_Y_MAX)`: girado
  10° el cubo es más ancho en Y y su esquina entraba 4,7 mm en el tope (la
  física lo expulsaba de golpe); así se coloca ~6 mm atrás y la cinta lo
  arrima suave. `translation = [PICKUP_X, y, DOCK_Z]`, `rotation = [0, 0, 1,
  DOCK_YAW_RAD]`, `resetPhysics()`, `docked.add(color)` y log `Cubo C encajado
  en la bandeja (0.5,y,0.77) girado 10.0 grados.`
- **Descartado, no repetir**: re-centrar continuamente un cubo ya encajado. La
  cinta empuja sin parar y entraba en bucle cada 0,4-0,5 s sin converger. La
  bandeja encaja **una vez**; el rescate por atasco del almacén (90 s) es la
  red de seguridad.

### C.8 `config_cadena.py` — la configuración de ESTA línea

Módulo sin Tkinter ni rclpy (lo leen el panel, el Sorter, el Loader y el
almacén). Un fichero **por contenedor**, porque las líneas comparten el mismo
`ros2_ws` (con una ruta fija se pisaban):

```python
CONFIG_PATH = f'/workspace/config_maquina_{socket.gethostname()}.json'
def leer() -> dict        # {} si no existe o esta corrupto
def escribir(cambios)      # actualiza SOLO esas claves
def quitar(clave)          # borra una entrada
def numero_maquina() -> int   # 'numero_maquina', por defecto 1
def grupo_cadena() -> int     # 'grupo_cadena', por defecto 0
def etiqueta() -> str         # 'etiqueta' (nombre de la cadena), ''
def idioma() -> str           # 'idioma', 'es'
def taller_api_base() -> str  # 'taller_api_base', '' = usar el de por defecto del contenedor
```

Claves que puede tener el fichero: `numero_maquina`, `grupo_cadena`,
`etiqueta`, `idioma`, `taller_api_base`, `picos`
(`{clave_pico: {activa, valor}}`), `clave_config` (`{sal, hash}`),
`pestana_produccion_visible`, `pestana_picos_visible`. Aparte, compartido por
todas las líneas: `/workspace/pico_asignacion.json`
(`{clave_pico: {host, nombre}}`, qué línea tiene cada Pico). Los dos van en
`.gitignore`.

### C.9 `panda_ikpy_kinematics.py` — cinemática (cálculo de ángulos)

Cinemática inversa con **ikpy 4.0.0** sobre `resource/panda_ikpy.urdf`
(Anexo 2), validada contra la posición real en Webots con error < 5 mm.

```python
DEFAULT_BASE = np.array([0.5, -0.3, 0.74])
SNAPSHOT = np.array([0.0, 0.0, 0.0, -1.7708, -1.6, 1.6, 0.79])   # "cero" del URDF exportado
HOME_POSITIONS = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
GRASP_R = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])   # pinza mirando abajo
CORRECTION_Z = -0.16
JOINT_LO = np.array([-2.9671, -1.8326, -2.9671, -3.1416, -2.9671, -0.0873, -2.9671])
JOINT_HI = np.array([ 2.9671,  1.8326,  2.9671, -0.4,     2.9671,  3.8223,  2.9671])
CONVERGENCE_TOL_M = 0.02
SEED_BOUND_MARGIN = 1e-6
GRIPPER_OPEN = 0.04
GRIPPER_CLOSED = 0.017

def rz(theta):   # giro puro en Z
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
```

- `SNAPSHOT`: la postura «cero» del URDF exportado no es el cero de Franka; a
  lo que devuelve ikpy hay que **sumarle** `SNAPSHOT` para tener ángulos
  reales de motor.
- `CORRECTION_Z = -0.16`: corrección medida del desfase brida→punto de pinza.
- `CONVERGENCE_TOL_M = 0.02`: 5 mm era demasiado estricto (ruido normal de
  ~1 cm); 2 cm sigue cazando los mínimos locales gordos (6,4 cm).
- `GRIPPER_CLOSED = 0.017`: valor **por defecto**; los dos robots lo
  sustituyen por 0,014 como atributo de instancia (regla 7).

`_urdf_path()` = `share/panda_controller/resource/panda_ikpy.urdf`.

Clase `PandaIkpyKinematics(base=None, base_yaw=0.0)`:

- `self.base` = `DEFAULT_BASE` o `np.asarray(base)`; `self.base_yaw`.
- `self.chain = Chain.from_urdf_file(_urdf_path())` (11 eslabones: origen,
  fijo de la base, 7 articulaciones, fijo de la mano y fijo del TCP).
- `seed_from_real(real_theta)` → `[0, 0] + list(real_theta − SNAPSHOT) + [0, 0]`.
- `_clip_seed(seed)`: para cada eslabón con límites finitos: si
  `hi − lo ≤ 2·SEED_BOUND_MARGIN` (fijo) → el punto medio; si no,
  `clip(seed[i], lo + margen, hi − margen)`. Motivo: scipy aborta con
  `ValueError("x0 is infeasible")` si la semilla cae un pelo fuera, y eso
  mataba el proceso del Loader.
- `solve(x, y, z, target_r, seed, check_convergence=False)` → `(real_theta, result, ok)`:
  1. `target_local = [x, y, z + CORRECTION_Z] − base`; `target_r_local = target_r`.
  2. Si `base_yaw ≠ 0`: `target_local = rz(−base_yaw) @ target_local` y
     `target_r_local = rz(−base_yaw) @ target_r`.
  3. `result = chain.inverse_kinematics(target_local, target_orientation=target_r_local,
     orientation_mode='all', initial_position=_clip_seed(seed))`. Si lanza
     `ValueError` o `LinAlgError`: devolver `(seed[2:9] + SNAPSHOT, list(seed), False)`.
  4. `real_theta = result[2:9] + SNAPSHOT`; `ok = all(JOINT_LO ≤ real_theta ≤ JOINT_HI)`.
  5. Si `ok and check_convergence`: cinemática directa y
     `ok = ‖fk[:3,3] − target_local‖ ≤ CONVERGENCE_TOL_M`.

`check_convergence` es **opcional a propósito**: siempre activo aborta tramos
por el aire que no importan; se exige solo en el paso final de agarrar o dejar.

**Si hubiera que regenerar el URDF** (no debería): un controlador local con
`supervisor TRUE` sobre el Panda del PROTO R2023b ejecuta
`Supervisor().getUrdf()`; al resultado se le quitan el eslabón `wrist_camera`
y su articulación, las dos articulaciones prismáticas de los dedos y sus
eslabones, y se añade al final un TCP fijo `panda_tcp` colgando de
`panda hand` con `origin xyz="0 0 0.1034"`. Después hay que **volver a
validar** `SNAPSHOT` y `CORRECTION_Z` contra la posición real en Webots.

### C.10 `overhead_vision.py` — ver los cubos desde arriba

Una cámara fija mirando recto hacia abajo: geometría conocida, se localiza en
**un solo disparo**, sin mover el brazo.

```python
CAM_X, CAM_Y, CAM_Z = 0.5, 0.0, 2.27        # camara del Loader (valores por defecto)
FOV = 0.9 ; IMG_W, IMG_H = 320, 240
COLOR_RANGES = {                             # HSV de OpenCV (H 0..179)
    'R': [((0, 150, 20), (10, 255, 255)), ((160, 150, 20), (179, 255, 255))],
    'G': [((40, 150, 20), (85, 255, 255))],
    'B': [((95, 150, 20), (130, 255, 255))],
}
COLOR_NAMES = {'R': 'rojo', 'G': 'verde', 'B': 'azul'}
MIN_CONTOUR_AREA = 80
MAX_CONTOUR_AREA = 600      # la textura de la cinta daba "cubos rojos" enormes
_TABLE_X_RANGE = (0.15, 0.85) ; _TABLE_Y_RANGE = (-0.55, 0.55)
```

Clase `OverheadLocator(node, topic='/overhead_camera/image_color', cam_x, cam_y,
cam_z, fov, img_w, img_h, table_x_range, table_y_range, prefer_closest_to_wall=False)`:

- Guarda la suscripción en `self.sub` (para poder destruirla al cambiar de
  cámara). El callback **solo guarda el último mensaje**; la conversión
  (`frombuffer(...).reshape(h, w, 4)` → `cv2.cvtColor(BGRA2BGR)`) se hace
  **bajo demanda** en `_esperar_frame(timeout)`: pone el mensaje a `None`, hace
  `rclpy.spin_once(node, 0.1)` hasta que llega uno **nuevo** o se agota el
  tiempo (reloj del ordenador), y lo devuelve convertido o `None`.
- Proyección (cámara girada `0 1 0 1.5708`: arriba de la imagen = +X del
  mundo, derecha = −Y):
  ```
  d = cam_z − target_z ;  scale = d · tan(fov/2) / (img_w/2)     # m por pixel
  pixel→mundo:  x = cam_x − (py − img_h/2)·scale ;  y = cam_y − (px − img_w/2)·scale
  mundo→pixel:  px = img_w/2 + (cam_y − y)/scale ;  py = img_h/2 + (cam_x − x)/scale
  ```
- **Recorte a la mesa**: el rectángulo de píxeles que envuelve las 4 esquinas
  de `table_x_range × table_y_range` proyectadas a z = 0,74; lo de fuera se
  enmascara (el suelo granate caía en el rango del rojo).
- `_detect_centroid(bgr, color)`: HSV → OR de las máscaras del color → AND con
  el recorte → `findContours(RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)`. Para cada
  contorno con área entre MIN y MAX y `m00 ≠ 0`: centroide por momentos y
  `angle_deg = cv2.minAreaRect(c)[2]`. Gana el de mayor clave: el **área** por
  defecto; con `prefer_closest_to_wall=True` (solo el Sorter), la **mayor Y
  de mundo** del centroide proyectado a z = 0,77 (el cubo más pegado al
  tope). Devuelve `(área, cx, cy, ángulo)` o `None`.
- `locate(target_z, color='R', timeout=3.0)` → `(x, y)` o `None`.
- `locate_with_yaw(target_z, color='R', timeout=3.0)` → `(x, y, yaw)`:
  `yaw = radians(angle_deg) mod (π/2)`; si > π/4, restar π/2 (un cubo visto
  desde arriba se repite cada 90°).
- `detect_color(timeout=3.0)` → `'R'|'G'|'B'|None`: prueba los tres y gana el
  de mayor clave.
- Sin imagen: aviso `[overhead] sin frame de la camara cenital.`; sin contorno:
  `[overhead] cubo <nombre> no detectado en la imagen cenital.`; con éxito:
  `[overhead] <nombre>: blob=(px,py) -> mundo=(x,y)[, giro=G grados]`.

**Plano de proyección**: los demos proyectan a `CUBE_VISION_Z = 0,80` (la
cara de arriba, que es lo que ve la cámara), no al centro: el sesgo medio baja
de 7,7 mm a 3,4 mm.

### C.11 `cube_shuttle_demo.py` — clase común `CubeShuttleDemo`

Nodo ROS 2 (`Node('cube_shuttle_demo')`) con toda la mecánica de «coger un
cubo en A y dejarlo en B» que comparten **los dos robots**. `LoaderDemo` y
`SorterDemo` heredan de aquí. (El `main()` de demo de un solo robot no hace
falta.)

**Constantes** (exactas):

| Constante | Valor | Para qué |
|---|---|---|
| `CUBE_TABLE_Z` | 0.77 | centro del cubo apoyado |
| `CUBE_VISION_Z` | `CUBE_TABLE_Z + 0.03` | plano que ve la cámara |
| `CUBE_SIDE` | 0.06 | lado del cubo |
| `GRASP_REACH_MARGIN` | 0.001 | margen del hueco dedo-cubo antes de bajar |
| `AUTO_REARME_DISLOCACION_S` | 4.0 | espera antes de autorearmar una parada por pinza dislocada |
| `MAX_DISLOCACIONES_SEGUIDAS` | 3 | más de 3 seguidas → la parada queda firme |
| `HOVER_HIGH` | `CUBE_TABLE_Z + 0.20` | altura de tránsito |
| `HOVER_GRASP` | `CUBE_TABLE_Z + 0.10` | altura del TCP para agarrar y dejar |
| `SAFE_Z` | 1.30 | referencia hacia/desde HOME |
| `STILL_THERE_RADIUS` | 0.05 | «¿sigue el cubo en el origen?» |
| `YAW` | π/4 | giro base del agarre (por caras, no aristas) |
| `GRASP_VERIFY_MARGIN` | 0.004 | sensor de dedos: ~0,017 en vacío frente a ~0,026 con cubo |
| `MAX_GRASP_RETRIES` | 2 | reintentos por tramo (3 intentos) |
| `GROUND_TRUTH_MAX_DIST` | 0.35 | distancia máxima para ir a por un cubo según su posición real |
| `REACH_MAX_XY` | 0.85 | alcance horizontal máximo |
| `VISION_GROUND_TRUTH_MAX_DESVIO` | 0.10 | desvío cámara/real a partir del cual manda la real |
| `GRIPPER_DISLOCATION_MAX` | 0.05 | lectura de dedo mayor = pinza dislocada |
| `JUMP_MAX_RAD` | 0.6 | freno de salto articular entre pasos de una rampa |
| `GROUND_TRUTH_LIFT_FRACTION` | 0.28 | fracción mínima de la subida que debe subir el cubo de verdad |
| `RELOJ_SIM_CADUCA_S` | 2.0 | sin `/clock` en este tiempo, se usa el reloj del ordenador |
| `GRASP_SETTLE_S` | 0.4 | pausa antes de cerrar la pinza |
| `LIFT_SETTLE_S` | 0.3 | pausa antes de medir la subida |
| `CARRIED_MAX_DIST` | 0.12 | distancia máxima cubo-destino para dar el traslado por bueno |
| `CARRIED_TIMEOUT_S` | 3.0 | tiempo máximo esperando que el cubo llegue |

Pinza dislocada = lectura `< -0.005` **o** `> GRIPPER_DISLOCATION_MAX` en
cualquier dedo. (Aflojar el −0,005 se probó: el ritmo bajó de 1,97 a 1,63 por
minuto y hubo más roturas reales. **No aflojar.**)

```python
def shortest_grasp_yaw(yaw):          # la pinza es simetrica cada 180 grados
    return ((yaw + np.pi / 2.0) % np.pi) - np.pi / 2.0
```

**Parámetros ROS**: `lift` 0.15, `step_sleep` **0.15** (emparejado con
`COMMANDED_VELOCITY` 1.4), `max_wait_seconds` 15.0, `use_vision` True,
`robot_base_x/y/z` 0.5 / −0.3 / 0.74, `robot_base_yaw` 0.0, `led_topic`
`/comando_led`, `led_topic_producto` `''` (vacío = no se publica),
`taller_api_base` `http://taller_host:8000` (se declara **solo aquí**;
declararlo otra vez en una subclase da error). (Hay además `repetitions`,
`reps_per_color`, `colors`, `cube_x`, `cube_y`, `shift` de la demo de un
robot; se pueden declarar igual.) `self.robot_name =
get_namespace().strip('/') or 'desconocido'`.

**En `__init__`**: publicadores `joint_positions` y `gripper_position`
(relativos), `led_topic`, `led_topic_producto` (si no vacío),
`/emergency_stop`, `/comando_led` y `/comando_led_loader` (para la alarma,
siempre los dos). Suscripciones: `gripper_state` (relativo),
`/warehouse/cube_positions`, `/emergency_stop` y **`/clock`**. Estado:

```
kin = PandaIkpyKinematics(base=[robot_base_x, robot_base_y, robot_base_z], base_yaw=robot_base_yaw)
cur = kin.seed_from_real(HOME_POSITIONS)      # semilla de la IK
real_theta = HOME_POSITIONS.copy()            # ULTIMA POSTURA COMANDADA (no leida de ningun sensor)
base_grasp_yaw = YAW ; current_grasp_yaw = YAW
grasp_z = HOVER_GRASP ; grasp_close = GRIPPER_CLOSED
rotate_before_descend = False ; rotate_clearance_extra = 0.0 ; approach_open = GRIPPER_OPEN
locator = OverheadLocator(self)               # camara del Loader por defecto
cube_pos_real = {}   # {'R': (x,y,z), ...} desde /warehouse/cube_positions
emergency_stopped = False ; _pinza_perdida_avisada = False ; _auto_parada_ts = None
_dislocaciones_seguidas = 0 ; _led_producto_fijo = False
_sim_t = None ; _sim_t_recibido = 0.0 ; _rampa_objetivo = None
```

**Hecho clave**: `real_theta` es lo **comandado**, no una lectura. El brazo
va por detrás. **Nunca** se mide el estado físico justo después de publicar el
último paso: se espera o se sondea con tope de tiempo.

**Reloj de la simulación** (arreglo de 2026-09-24/26, importante en PCs
lentos):

- `_on_clock(msg)`: guarda `_sim_t` (s) y `_sim_t_recibido = time.monotonic()`.
- `_reloj_sim_vivo()`: `_sim_t` no es `None` y se recibió hace menos de
  `RELOJ_SIM_CADUCA_S`.
- `_ahora()`: `_sim_t` si el reloj está vivo, si no `time.time()`.
- `_cronometro()`: devuelve una función `transcurrido()` que suma bien aunque
  la fuente cambie a mitad (si empieza con el reloj del ordenador y luego llega
  `/clock`, guarda lo medido y sigue con la nueva fuente). Bug real que
  arregla: restar `_ahora() - t0` mezclando relojes dio negativo para siempre
  y el Loader se quedó «bailando» más de 8 minutos.
- `spin_for(s)`: si el reloj está vivo, espera `s` segundos **de simulación**
  (`spin_once(0.05)` en bucle mientras `_sim_t - t0 < s`); si no, `s` segundos
  reales procesando callbacks. **No usar `spin_once(timeout=s)` como espera**:
  vuelve en cuanto procesa un mensaje.
- `_publish(th)`: `real_theta = th`; publicar; `spin_once(0.02)`. Con reloj
  vivo: un paso cada `step_sleep` de **simulación**, acumulando el objetivo
  (`_rampa_objetivo += step_sleep`; si está en `None` o más de 1 s por detrás,
  se reengancha a `_sim_t`) y esperando con `spin_once(0.05)` (sale si el reloj
  muere). Sin reloj: `time.sleep(step_sleep)`.
- `_dance` y la verificación de traslado usan `_cronometro()`.

**Parada de emergencia y pinza dislocada**:

- `_on_gripper_state`: guarda la lectura; si hay dislocación →
  `_avisar_pinza_perdida()` (una vez hasta el rearme): log `PINZA DISLOCADA
  detectada ([…], rango real 0-0.04) -- lanzando parada de emergencia
  automatica.`, publica `/emergency_stop=True` y `parada` en los dos topics de
  LED, `_auto_parada_ts = ahora`, `_dislocaciones_seguidas += 1`.
- `_on_emergency_stop`: `True` y no parado → parado (log `PARADA DE EMERGENCIA
  recibida en /emergency_stop -- dejo de mover el brazo donde este.`).
  `False` y parado → no parado, `_pinza_perdida_avisada = False`,
  `_auto_parada_ts = None` (log `REARME recibido en /emergency_stop -- continuo
  donde me quede.`).
- `_wait_while_stopped(label)` → `bool`, **antes de cada paso**. Si no hay
  parada, `True`. Si la hay: log `En PAUSA por parada de emergencia durante
  "<label>" -- esperando rearme...`; mientras dure: si `not rclpy.ok()` →
  `False`; `spin_once(0.1)`; si hay `_auto_parada_ts` y han pasado
  `AUTO_REARME_DISLOCACION_S`: con más de `MAX_DISLOCACIONES_SEGUIDAS` → log
  `N dislocaciones SEGUIDAS sin un solo agarre bueno … NO me rearmo`, borrar
  el sello y **seguir esperando** a un humano; si no → log de autorrearme,
  publicar `rearme` en los dos LED y `/emergency_stop=False`. Al salir: si la
  pinza sigue fuera de rango, `_gripper(GRIPPER_OPEN, 0.5)` **antes** de
  continuar. Log `Rearmado -- continuo "<label>".` y `True`.
  Las paradas de botón o de panel **nunca** se autorrearman.

**Primitivas**:

- `wait_for_subscribers()`: hasta `max_wait_seconds`, que `joint_positions`
  **y** `gripper_position` tengan suscriptores.
- `_gripper(pos, wait)`: publicar y `spin_for(wait)` (con `time.sleep` el
  sensor de dedos no se actualizaba y la verificación leía el estado viejo).
- `_pause_conveyor(paused)`: aquí no hace nada (el Sorter lo sobrescribe).
- `_solve_step(x, y, z, r, check_convergence=False)` → `(th, ok)`: resolver
  con semilla `cur`; si `ok`, `cur = result`. Si no, reintentar **una** vez
  con semilla `kin.seed_from_real(real_theta)` (nunca desde HOME: daba saltos
  de hasta 100°); si tampoco, `cur = result` y `(th, False)`.
- `ramp(x, y, z_from, z_to, yaw_from, yaw_to, n, label, strict_final=False)`:
  para `i = 1..n`: `_wait_while_stopped`; interpolar z y giro;
  `r = GRASP_R @ rz(yaw)`; `_solve_step(..., check_convergence=strict_final and i == n)`.
  **Freno de salto**: desde el paso 2, si una articulación cambia más de
  `JUMP_MAX_RAD` respecto al paso anterior de la misma rampa → log
  `[freno salto IK] …` y fallo. Si falla: log `LIMITE en <label> (paso i/n, z=…)`
  y `False`; si va bien, `_publish(th)`. Al final, log `<label>: OK (x=… y=… z=…)`.
- `translate(x_from, y_from, x_to, y_to, z, yaw, n, label)`: igual
  interpolando X e Y con Z y giro fijos; **sin** convergencia ni freno.
- `park_at_home()`: 10 pasos interpolando **en espacio articular** desde
  `real_theta` hasta `HOME_POSITIONS` (con `_wait_while_stopped` en cada uno);
  `cur = seed_from_real(HOME)`; log `aparcado en HOME real`. No usa IK: es la
  vía de escape cuando el solver acaba de fallar.
- `_dance(duration=5.0)`: aviso de «lote nuevo»: durante 5 s (medidos con
  `_cronometro()`), solo la articulación 7 oscila `0.35·sin(2π·t/0.6)` rad
  alrededor de la postura actual; al final vuelve al centro. Respeta la parada.

**LED y diagnóstico**:

- `_set_led(letra)`: publica en `led_topic`; si `letra != '0'` y no
  `_led_producto_fijo` → `_set_led_producto(letra)`; si es R/G/B → evento
  `led_encendido`.
- `_set_led_producto(letra)`: publica en `led_topic_producto` si existe.
- `_taller_base()`: `(config_cadena.taller_api_base() or taller_api_base).rstrip('/')`,
  **releído en cada aviso** (bug real: con la línea en otro ordenador el panel
  cogía los pedidos del servidor remoto y las piezas se avisaban al local; el
  pedido nunca avanzaba y el modo Automático lo relanzaba sin fin).
- `_notificar_evento_produccion(tipo, color)`: `POST {base}/taller/evento_produccion`
  con `{"robot", "color", "tipo"}`, timeout 1,5 s; cualquier error → aviso
  `[diagnostico] …` y seguir. Tipos: `led_encendido`, `agarre_falso`,
  `limite_alcance`, `fallo_definitivo`.

**`approach_and_grasp(x, y, color='R')` → `(ok, cogido)`**:

1. `cur = seed_from_real(HOME_POSITIONS)` (cada tramo parte de una semilla
   conocida: encadenar semillas derivaba hacia los límites).
2. `_gripper(approach_open, 0.5)`; `hover_z = HOVER_HIGH + rotate_clearance_extra`.
3. `ramp(x, y, SAFE_Z, hover_z, 0, 0, 10, 'bajada a hover')` — si falla, `(False, False)`.
4. `_gripper(approach_open, 0.0)` (reafirmar abierta).
5. Si `rotate_before_descend`: `ramp(x, y, hover_z, hover_z, 0, current_grasp_yaw, 10,
   'giro a orientacion de agarre (parado, a altura segura)')` y
   `yaw_from = current_grasp_yaw`; si no, `yaw_from = 0`.
6. `_pause_conveyor(True)`.
7. `ramp(x, y, hover_z, grasp_z, yaw_from, current_grasp_yaw, 30,
   'aproximacion final + giro real', strict_final=True)`. Si falla: evento
   `limite_alcance`, `_pause_conveyor(False)`, `(False, False)`.
8. `spin_for(GRASP_SETTLE_S)`; `_wait_while_stopped('pinza junto al cubo, sin cerrar')`
   (si `False`: reanudar cinta y `(False, False)`).
9. `_grasp_z_before = cube_pos_real[color][2]` si existe.
10. `_gripper(grasp_close, 2.0)`; `cogido = _verify_grasp()` (sin datos →
    `True`; si no, media de los dos dedos `> grasp_close + GRASP_VERIFY_MARGIN`).
11. Si cogido: `_set_led(color)`, log `pinza cerrada (agarre verificado por
    sensor de dedos), LED <c> encendido`, `_dislocaciones_seguidas = 0`. Si no:
    reanudar cinta y aviso `pinza cerrada pero SIN agarre verificado (…)`.
12. `(True, cogido)`.

**`lift_shift_place(x_from, y_from, x_to, y_to, place_z=None, place_yaw=None, color=None)` → `bool`**:

1. `yaw_place = place_yaw or current_grasp_yaw`; `target_z = place_z or grasp_z`;
   `z_lift = max(grasp_z, target_z) + lift`.
2. `ok = ramp(x_from, y_from, grasp_z, z_lift, g, g, 8, 'levantar 15cm')`.
3. **`_pause_conveyor(False)` pase lo que pase**; si `not ok` → `False`.
4. `spin_for(LIFT_SETTLE_S)`.
5. **Verificar la subida**: con posición real (color dado y conocido):
   `subida = z_actual − _grasp_z_before`; si `< lift · GROUND_TRUTH_LIFT_FRACTION`
   (4,2 cm) → log `[verificacion ground truth] el cubo X NO subio lo esperado …`,
   evento `agarre_falso`, abrir 0,5 s, LED `0`, `False`. Sin posición real: si
   `not _verify_grasp()` → log `[verificacion pinza] agarre PERDIDO …`, lo mismo.
6. Si `yaw_place ≠ current_grasp_yaw`: `ramp(..., z_lift, z_lift, g, yaw_place, 8,
   'girar muneca ya despejado de la pared')` (girar **después** de subir:
   girar mientras sube barría la pared).
7. `translate(x_from, y_from, x_to, y_to, z_lift, yaw_place, 12, 'desplazar a destino fijo')`.
8. Con color: `locate_with_yaw(CUBE_VISION_Z, color)`; si ve un cubo de ese
   color a menos de `STILL_THERE_RADIUS` del origen → log `[verificacion camara]
   agarre FALSO …`, evento, abrir, LED `0`, `False`.
9. `pasos = 8` sin `place_z`; si no, `max(8, round((z_lift − target_z)/0.005))`.
   `ramp(x_to, y_to, z_lift, target_z, yaw_place, yaw_place, pasos,
   'bajar a depositar (reverso de levantar)')`. **Si falla, se suelta
   igualmente** (el brazo ya está sobre el destino).
10. `_gripper(GRIPPER_OPEN, 1.2)`; `_set_led('0')`; log `pinza abierta (soltado), LED apagado`.
11. Verificar el traslado **después** de soltar (con color y posición real):
    sondear cada 0,1 s hasta `CARRIED_TIMEOUT_S` la distancia horizontal
    cubo-destino; si al final `> CARRIED_MAX_DIST` → log `[verificacion
    transporte] …`, evento `agarre_falso`, `False`.
12. **Desde aquí la entrega está hecha y nada la convierte en fallo**:
    `ramp` de retirada recta hasta `max(HOVER_HIGH, target_z)` (12 pasos,
    `'retirada (sube recto, sin girar)'`), luego hasta `SAFE_Z` (10 pasos,
    `'subir a home (sigue recto, sin girar)'`); si una falla, `park_at_home()`
    y `True`; al final `park_at_home()` y `True`.

**`leg(source, dest, tag, color='R', place_z=None, place_yaw=None)` → `bool`**:
`source` y `dest` son puntos **fijos** (la visión corrige dónde agarrar, nunca
adónde se lleva: si no, el patrón deriva). Para `intento = 1 .. MAX_GRASP_RETRIES+1`:

1. `(x, y) = source`; `current_grasp_yaw = base_grasp_yaw`.
2. Si `intento > 1` y visión: `park_at_home()` (despejar la cámara: tras un
   fallo el brazo tapaba el cubo).
3. Con visión: `locate_with_yaw(CUBE_VISION_Z, color)`.
   - **No lo ve**: con posición real: si está a más de `GROUND_TRUTH_MAX_DIST`
     de `source` → error y `return False` (no perseguir un cubo que ya no es
     suyo); si no, usar la posición real. Sin posición real, seguir con la supuesta.
   - **Lo ve**: `(x, y, yaw_off)`; `current_grasp_yaw = base_grasp_yaw + yaw_off`;
     log `[vision] cubo relocalizado en (…) (guess era (…)), giro real=G grados extra`.
     Si la posición real se desvía más de `VISION_GROUND_TRUTH_MAX_DESVIO`: si
     la real está a más de `GROUND_TRUTH_MAX_DIST` del origen → `False`; si no,
     usar la real y `current_grasp_yaw = base_grasp_yaw`.
4. **Siempre**: `current_grasp_yaw = _adjust_grasp_yaw_for_obstacles(x, y)`;
   `(x, y) = _adjust_grasp_position_for_obstacles(x, y)`;
   `current_grasp_yaw = shortest_grasp_yaw(current_grasp_yaw)`.
5. Hueco: con posición real, `hueco = (2·approach_open − CUBE_SIDE)/2`; si la
   distancia del punto de agarre al cubo real `> max(hueco − GRASP_REACH_MARGIN, 0)`
   → log `[<tag>] puedo cerrar en (…) pero el cubo X esta en (…) … NO bajo …`,
   evento `limite_alcance`, `False`.
6. Alcance: distancia horizontal a `kin.base` `> REACH_MAX_XY` → log y `False`.
7. Log `-- <tag> (intento N): coger en (x,y) -> dejar en (x_to,y_to)`.
8. `ok, cogido = approach_and_grasp(x, y, color)`; si `not ok` → `False`.
9. Si cogido: si `lift_shift_place(...)` → `True`; si no, aviso `[<tag>] agarre
   falso (camara) -- reintentando desde cero...` y siguiente intento.
10. Si no cogido: abrir 0,5 s y aviso `[<tag>] reintentando agarre...`.

Agotados: log `[<tag>] agotados los reintentos sin agarre verificado.`,
evento `fallo_definitivo`, `False`.

Ganchos que sobrescribe el Sorter: `_adjust_grasp_yaw_for_obstacles`,
`_adjust_grasp_position_for_obstacles`, `_pause_conveyor`, `park_at_home`.

### C.12 `loader_demo.py` — `LoaderDemo(CubeShuttleDemo)`

Vacía la caja en la cinta. Un proceso **nuevo por lote**:

```bash
ros2 run panda_controller loader_demo --ros-args -r __ns:=/loader \
  -p cycles:=<N> -p led_topic:=/comando_led_loader -p led_topic_producto:=/comando_led_producto \
  [-p only_color:="<LETRA>"]     # comillas YAML obligatorias: Y/N/y/n/on/off se leen como booleanos
```

```python
RECYCLE_WAIT_RETRIES = 40 ; RECYCLE_WAIT_SECONDS = 1.0
CRATE_CUBES = [('R', 0.5, 0.16), ('G', 0.35, 0.16), ('B', 0.65, 0.16)]
BELT_DROP_X = 0.5
BELT_DROP_Y = 0.28        # el unico punto de la cinta que el Loader alcanza de verdad (error IK 0,1 cm)
DROP_CLEAR_RADIUS = 0.10 ; DROP_CLEAR_RETRIES = 40 ; DROP_CLEAR_WAIT = 0.5
```

`__init__`: `super().__init__()`; parámetros `only_color` (`''`) y `cycles`
(1); **`self.grasp_close = 0.014`** (con 0,017 se le caían los cubos al
arrancar el traslado); `belt_paused` y suscripción de solo lectura a
`/warehouse/belt_pause`.

- `_esperar_reciclado(color, x, y)`: espera **indefinida** a que la cámara
  vuelva a ver ese color en la caja (`locate_with_yaw`), `spin_for(1.0)` entre
  intentos y aviso cada 40 (`[reciclado] el cubo X lleva Ns sin volver a la caja …`).
  Aplica **la misma regla que C.11**: si lo que ve la cámara se desvía más de
  `VISION_GROUND_TRUTH_MAX_DESVIO` de la posición real del cubo, manda la real
  (medido: las baldosas granates del suelo dan un «rojo» a 27 cm del cubo; sin
  la regla, el Loader esperaba para siempre al rojo).
- `_esperar_hueco_en_cinta()`: espera indefinida hasta que la cinta **no**
  esté parada **y** ningún cubo real esté a menos de `DROP_CLEAR_RADIUS` de
  `(BELT_DROP_X, BELT_DROP_Y)`; `spin_for(0.5)`; aviso cada 40.

`run()`:

1. `only_color = param.strip().upper()`; `cycles = int(param)`.
2. `cycles > 1` sin visión → error y `False` (no puede confirmar el reciclado).
3. `only_color` no alfabético → error y `False`. **No** se valida contra R/G/B:
   es solo la **etiqueta del producto** (puede ser Y/M/C/W o `SINCOLOR`).
4. `park_at_home()`; `_dance()`.
5. Con `only_color`: `_led_producto_fijo = True`; `_set_led_producto(only_color)`.
6. `cubos = CRATE_CUBES` **siempre** (los tres cubos son la materia prima).
   `objetivo = cycles` con `only_color`, si no `cycles × 3`.
7. `entregados = 0`; `usos = {R:0, G:0, B:0}`. Mientras `entregados < objetivo`,
   para cada `(color, x, y)`: si ya se llegó, salir; `usos[color] += 1`; si
   `usos > 1` → `_esperar_reciclado`; `_esperar_hueco_en_cinta()`; log
   `--- [n/objetivo] Descargando cubo C en (x,y) -> cinta (0.50,0.28) ---`;
   `leg((x, y), (BELT_DROP_X, BELT_DROP_Y), f'descargar_{C}_{n}', color=C)`. Si
   falla: log, `park_at_home()` y **seguir con el siguiente** (no abandonar el
   lote); si va bien, `entregados += 1`.
8. Log `CAJA VACIADA: N cubo(s) en la cinta.` y `True`. **No** apaga el LED de
   producto: lo apaga el Sorter al contar la última entrega real.

`main()`: `wait_for_subscribers()`; si falla, log `Nadie se ha suscrito tras
Ns (…)`; si no, `run()`.

### C.13 `sorter_demo.py` — `SorterDemo(CubeShuttleDemo)`

Proceso **persistente entre lotes** (el panel lo lanza una vez y lo reutiliza):

```bash
ros2 run panda_controller sorter_demo --ros-args -r __ns:=/sorter \
  -p robot_base_x:=0.0 -p robot_base_y:=1.00 -p robot_base_z:=0.74
```

```python
LOTE_COLOR_QOS = QoSProfile(depth=1, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
SORTER_BASE = (0.0, 1.00, 0.74)
SORTER_BASE_YAW = 0.4636          # = rotation del PANDA_SORTER en el mundo
PICKUP_X = 0.5 ; PICKUP_Y = 1.25
RAIL_X_L = 0.445 ; RAIL_X_R = 0.555     # caras REALES de los carriles
RAIL_SAFETY_MARGIN = 0.004
BOXES = {'R': (0.0, 1.45), 'G': (-0.15, 1.45), 'B': (0.15, 1.45)}
SORTER_CAM_TOPIC = '/overhead_camera_sorter/image_color'
SORTER_CAM_X, SORTER_CAM_Y, SORTER_CAM_Z = 0.25, 1.30, 2.27
SORTER_TABLE_X_RANGE = (0.35, 0.65) ; SORTER_TABLE_Y_RANGE = (0.95, 1.35)
DETECT_RETRIES = 40 ; DETECT_RETRY_WAIT = 1.0
STILL_MOVING_CHECKS = 10 ; STILL_MOVING_WAIT = 0.5 ; STILL_MOVING_TOLERANCE = 0.01
SORTER_PARK_POSITIONS = HOME_POSITIONS.copy(); SORTER_PARK_POSITIONS[0] += 1.4   # base girada: no tapa su camara
```

`LOTE_COLOR_QOS` lo importa también el panel.

`__init__` (sobre lo de la clase común):

```
kin = PandaIkpyKinematics(base=SORTER_BASE, base_yaw=SORTER_BASE_YAW)   # se fuerza, no fiarse de parametros
cur = kin.seed_from_real(real_theta)
base_grasp_yaw = YAW ; current_grasp_yaw = YAW ; place_yaw = YAW
rotate_before_descend = True        # girar arriba y bajar recto (7.a activacion; las roturas eran por geometria)
grasp_close = 0.014
approach_open = 0.040               # con canal de 11 cm (0.033/0.036 fueron pasos intermedios ya superados)
grasp_z += 0.005                    # 0.875: medio centimetro mas alto que el Loader
```

- **Cámara propia**: primero `destroy_subscription(self.locator.sub)` (la del
  Loader que creó la clase común; si no, se quedaba suscrito para nada) y
  después `OverheadLocator(self, topic=SORTER_CAM_TOPIC, cam_x/y/z=SORTER_CAM_*,
  table_x_range=SORTER_TABLE_X_RANGE, table_y_range=SORTER_TABLE_Y_RANGE,
  prefer_closest_to_wall=True)`.
- Publicadores: `/warehouse/cube_delivered`, `/warehouse/belt_pause`,
  `/comando_led_producto`. Suscripciones: `/production/nuevo_lote` (→
  `_nuevo_lote_pendiente = True`) y `/production/lote_color_objetivo`
  (`LOTE_COLOR_QOS`).
- Estado del lote: `_nuevo_lote_pendiente`, `_lote_color_objetivo = ''`,
  `_lote_activo = False`, `_lote_cantidad_objetivo = None`,
  `_lote_entregadas = 0`, `_lote_pedido_id = None`,
  `_lote_forzar_reparto = False`, `_lote_producto_id = None`.

Métodos:

- `_pause_conveyor(p)`: publica `/warehouse/belt_pause = p`.
- `_adjust_grasp_yaw_for_obstacles(x, y)`: **siempre** `current_grasp_yaw + π/2`
  (sin condición), con log `[colision] giro de agarre ajustado +90 grados para
  no cerrar paralelo a la pared/fila (eje de cierre estaba a D grados del eje
  peligroso).` con `D = |((grados(current) + 45) mod 180) − 90|`. El +90 es
  **obligatorio**: el cubo reposa tocando el tope y sin él un dedo entraría
  1 cm dentro del tope.
- `_adjust_grasp_position_for_obstacles(x, y)`: acota X para que ningún dedo
  caiga en un carril: `x_min = RAIL_X_L + approach_open + RAIL_SAFETY_MARGIN`
  (0,489), `x_max = RAIL_X_R − approach_open − RAIL_SAFETY_MARGIN` (0,511); si
  acota, aviso `[colision] agarre en x=… pondria un dedo dentro de un carril …
  -- acotado a x=….`
- `_esperar_color()`: bucle **infinito**: si `_nuevo_lote_pendiente` → a
  `False`, `park_at_home()` y `_dance()` (punto seguro, nunca con un cubo a
  medio coger); `locator.detect_color()`; si hay color, devolverlo; aviso cada
  40 intentos (`[sorter] sin ver NINGUN cubo desde hace Ns …`); `spin_for(1.0)`.
- `_esperar_cubo_quieto(color)`: hasta 10 lecturas `locate_with_yaw` cada
  0,5 s; `True` cuando dos seguidas distan menos de 0,01 (si una no lo ve, se
  reinicia la comparación); `False` si se agotan.
- `_notificar_taller(color, pedido_id=None, forzar_reparto=False, producto_id=None)`:
  `POST {_taller_base()}/taller/cubo_clasificado` con `{"color", "forzar_reparto",
  "numero_maquina": config_cadena.numero_maquina(), "grupo_cadena":
  config_cadena.grupo_cadena()}` más `pedido_id` y `producto_id` si vienen
  (releídos en cada pieza: un cambio en el panel vale al instante). Timeout
  1,5 s. Respuesta con `pedido` → log `[taller] pedido #id actualizado (c/p,
  estado).`; sin pedido → `[taller] sin pedido pendiente para C (o reparto
  manual activo) -- guardado en stock (N unidades).`; errores → aviso y seguir.
  (Bug real que evitan `numero_maquina/grupo_cadena`: una pieza de la máquina
  20 completó un pedido de la máquina 10.)
- `_on_lote_color_objetivo(msg)`: formato `COLOR:CANTIDAD:PEDIDO_ID:FORZAR:PRODUCTO_ID`.
  Siempre `_lote_entregadas = 0`. Mensaje vacío → sin lote (todo a valores
  iniciales; log `[lote] sin lote activo -- cada cubo cuenta por su color real.`).
  Si no: `color = partes[0].upper()`, `cantidad`, `pedido_id` y `producto_id`
  enteros o `None`, `forzar = partes[3] == '1'`; `_lote_activo = True`. Log
  `[lote] producto objetivo activo: toda entrega cuenta como C (objetivo N
  unidad(es)[, pedido #id]), sea del color real que sea.` o, con color vacío,
  `[lote] reparto mixto activo (objetivo N pieza(s) en total) …`.
- `park_at_home()` (sobrescrito): igual, hacia `SORTER_PARK_POSITIONS`; log
  `aparcado (postura Sorter, camara despejada)`.

`run()`:

```
park_at_home(); _dance(); clasificados = 0
bucle infinito:
    color = _esperar_color()
    si not _esperar_cubo_quieto(color): aviso y continuar
    dest = BOXES.get(color, BOXES['R'])
    log '--- Cubo <nombre> detectado en la cinta -> caja <nombre> (x, y) ---'
    si not leg((PICKUP_X, PICKUP_Y), dest, f'clasificar_{color}', color=color, place_yaw=place_yaw):
        log '[C] fallo recogiendo/clasificando … sigo esperando (no me caigo).'
        park_at_home(); continuar          # si no, el brazo colgado tapa su camara para siempre
    log 'CUBO CLASIFICADO en la caja <nombre>.'
    publicar /warehouse/cube_delivered = color       # SIEMPRE el color fisico real
    color_taller = _lote_color_objetivo or color
    si color_taller != color: log '[lote] cubo <nombre> entregado, contado como producto X (…)'
    _notificar_taller(color_taller, pedido_id=_lote_pedido_id, forzar_reparto=_lote_forzar_reparto,
                      producto_id=_lote_producto_id)
    si _lote_activo:
        _lote_entregadas += 1
        si hay objetivo y entregadas >= objetivo:
            publicar '0' en /comando_led_producto
            log '[lote] n/N unidad(es) de <etiqueta> completadas de verdad -- LED de producto apagado, lote cerrado.'
            reiniciar el estado del lote
    spin_for(0.2); clasificados += 1
```

`main()`: igual que el Loader.

### C.14 `teleop_gui.py` — el panel de control

Ventana **Tkinter** (dentro de `ros2_panda_dev24`, dibujada en el X11 del
anfitrión; en Windows, en la pantalla virtual de `panel_web.sh`) desde la que
se maneja **toda** la línea: mover a mano los dos brazos, parar y rearmar,
ver y lanzar los pedidos de la web, simular las Pico y configurar la línea.
Se lanza con `ros2 run panda_controller teleop_gui` cuando la celda ya está
conectada. Separación: `TeleopGuiNode(Node)` (ROS, cinemática y estado, sin
Tkinter) y `TeleopApp` (la ventana), por composición.

#### C.14.1 Constantes

```python
# Paleta (la misma que estop_panel)
BG='#1c1c1c'; PANEL_BG='#2a2a2a'; YELLOW='#f5c400'; RED='#c81e1e'; RED_DARK='#8f1414'
GREEN='#2e9e3b'; GREY='#555555'; GREY_TEXT='#aaaaaa'; TEXT_LIGHT='#eaeaea'
SIN_COLOR = 'SINCOLOR'     # only_color de un producto sin LED: alfabetico, no es ningun color real
LED_AGARRE_COLOR = {'r'/'rojo'/'red': '#ff3b30', 'g'/'verde'/'green': '#34c759', 'b'/'azul'/'blue': '#0a84ff'}
LED_PRODUCTO_COLOR = LED_AGARRE_COLOR + {'y': '#ff3c00', 'm': '#c800c8', 'c': '#00c8c8', 'w': '#ffffff'}
LED_APAGADO = ('0', 'apagar', 'off', 'rearme', 'rearm', '') ; LED_ALARMA = ('parada', 'stop')
UMBRAL_HCSR04_CM = 10      # el mismo DISTANCIA_MIN_CM del firmware del Loader
MIN_MAQUINA, MAX_MAQUINA = 0, 99 ; MIN_GRUPO_CADENA, MAX_GRUPO_CADENA = 0, 99
CLAVE_MAQUINA = '1111'     # clave de fabrica de la pestana Configuracion
MIN_LARGO_CLAVE = 4
SEGUNDOS_RESET_CLAVE = 10 ; SEGUNDOS_AVISO_OLED = 6 ; AVISO_OLED_CLAVE = 'MSG:Contrasena|reseteada'
PICO_ASIGNACION_PATH = '/workspace/pico_asignacion.json' ; MI_HOST = socket.gethostname()
PICO_REINTENTO_S = 15.0         # no relanzar un puente caido mas de una vez cada 15 s
LOTE_SIN_ENTREGAS_S = 120.0     # lote con el Loader ya terminado y sin entregas: se da por cerrado
MARGEN_TALLER_S = 6.0           # tras cerrar un lote, Automatico espera esto antes de mirar el almacen
AUTO_MAX_TANDAS_SIN_PROGRESO = 2
PICOS = {
  'loader_usb':  {'nombre': 'Pico del Loader (USB: LED, LED producto, botón y HC-SR04)', 'corto': 'Loader USB',
                  'ejecutable': 'led_publisher_usb', 'param': 'serial_port', 'etiqueta_param': 'Puerto serie:',
                  'defecto': '/dev/ttyACM_LOADER'},
  'sorter_wifi': {'nombre': 'Pico W del Sorter (Wi-Fi: LED)', 'corto': 'Sorter Wi-Fi',
                  'ejecutable': 'led_publisher', 'param': 'pico_ip', 'etiqueta_param': 'IP de la Pico:',
                  'defecto': 'IP_DE_LA_PICO'},
}
```

La clave de Configuración se guarda **cifrada** en el fichero de la línea
como `clave_config = {sal, hash}` con `pbkdf2_hmac('sha256', clave, sal, 100_000)`
y se compara con `hmac.compare_digest`; si no hay ninguna guardada vale
`CLAVE_MAQUINA`. Olvidada: borrar `clave_config` del fichero vuelve a `1111`.

#### C.14.2 Cinemática del panel: la MISMA cadena de ikpy que los robots

**Importante (medido en la prueba del 27-09-2026):** el panel usa la misma
cadena de ikpy (Anexo 2, `PandaIkpyKinematics`) que ya coge cubos de verdad en
las fases 6 y 7. **No uses** el modelo DH estándar del Franka (`PANDA_MDH`,
`FLANGE_TO_TCP_Z`): **no coincide con el Panda de Webots**. Con los ángulos
con los que los robots cogen cubos, el DH sitúa la pinza a 15-27 cm de donde
está de verdad; con él, el panel creía estar encima del cubo y cerraba en el
vacío. (El proyecto original todavía lleva ese DH; es un fallo conocido.)

```python
HOME_POSITIONS = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
GRASP_R = [[1,0,0],[0,-1,0],[0,0,-1]]
STEP_DEFAULT = 0.01 ; STEP_MIN = 0.002 ; STEP_MAX = 0.05
YAW_STEP_DEG = 5.0 ; MAX_JOINT_JUMP_DEG = 25.0 ; _MAX_SPLIT_DEPTH = 4
JOINT_LIMITS = [(-2.9671, 2.9671), (-1.8326, 1.8326), (-2.9671, 2.9671), (-3.1416, -0.4000),
                (-2.9671, 2.9671), (-0.0873, 3.8223), (-2.9671, 2.9671)]
```

- Se importan de los módulos de los robots: `CORRECTION_Z` y
  `PandaIkpyKinematics` (C.9); `SAFE_Z`, `YAW` y
  `VISION_GROUND_TRUTH_MAX_DESVIO` (C.11).
- Al elegir robot (`apply_preset`): `self.kin = PandaIkpyKinematics(base=base, base_yaw=base_yaw)`.
- `tcp_mundo(kin, comandados)`: `fk = kin.chain.forward_kinematics(kin.seed_from_real(comandados))`;
  `p = rz(kin.base_yaw) @ fk[:3,3] + kin.base`; `p[2] -= CORRECTION_Z`
  (la misma corrección medida que usa `solve()`). Es la posición de la pinza
  **en el mundo** que enseña el panel.
- `_ir_a(destino_mundo, yaw, freno=True)`: `kin.solve(x, y, z, GRASP_R @ rz(yaw + YAW),
  kin.seed_from_real(actual), check_convergence=True)`. **El «giro 0» del panel es
  `YAW` (π/4)**, el agarre por caras de los robots: con giro 0 de verdad la
  pinza abierta no cabe alrededor del cubo. Si no converge: «fuera de los
  límites» (exceso > 1°) o «no se puede llegar ahí». Si el salto articular
  supera 25° y hay freno: partir el trayecto en dos mitades (hasta 4 niveles,
  mitad > `STEP_MIN`, `sleep(0.15)` entre subpasos).
- Ángulos «en bruto»: `comandado = bruto + offsets`, con
  `joint_offsets_deg = [0, 0, 0, 0, 0, 0, −90]` por defecto.
- `_pendiente_de_fabricar(pedido)` = `max(0, pedida − completada − stock_disponible)`
  (bug real: se lanzaban 10 tuercas con 8 ya en el almacén).
- `_demo_vivo(nombre)`: `pgrep -f 'panda_controller/lib/panda_controller/<nombre>'`
  (la ruta del ejecutable real; `ros2 run …` desaparece de la línea de
  comandos tras el `exec`).
- Puentes de las Pico: `_patron_puente(ej)` =
  `f'panda_controller/lib/panda_controller/{ej}( |$)'` (para que
  `led_publisher` no case con `led_publisher_usb`); `_puente_vivo` con `pgrep`;
  `_lanzar_puente(ej, param, valor)` = `Popen(['ros2','run','panda_controller',ej,'--ros-args','-p',f'{param}:={valor}'],
  stdin=DEVNULL, stdout=/tmp/<ej>.log (append), stderr=STDOUT, start_new_session=True)`
  (sesión propia: si se cierra el panel, el LED sigue funcionando);
  `_parar_puente(ej)`: `pkill -TERM -f patrón`, esperar hasta 3 s y
  `pkill -KILL`.

#### C.14.3 `TeleopGuiNode`: parámetros, presets y publicadores

Parámetros (preset `loader`): `robot` (`loader`), `joint_topic`
`/loader/joint_positions`, `gripper_topic` `/loader/gripper_position`,
`led_topic` `/comando_led_loader`, `robot_base_x/y/z` 0.5 / −0.3 / 0.74,
`robot_base_yaw` 0.0, `gripper_open_position` 0.04, `gripper_closed_position`
0.025, `joint_offsets_deg` `[0,0,0,0,0,0,-90]`, `max_wait_seconds` 45.0,
`initial_commanded_joints` `[0.0]` (un solo valor para que rclpy infiera
`double[]`; con 7 valores arranca en esa pose), `camera_topic`
`/overhead_camera/image_color`, `camera_x/y/z` 0.5 / 0.0 / 2.27,
`camera_table_x_min/max` 0.15 / 0.85, `camera_table_y_min/max` −0.55 / 0.55,
`cube_table_z` 0.77, `taller_api_base` `http://taller_host:8000` (si hay una
URL guardada en Configuración, manda esa; se guarda el valor por defecto para
volver a él si se borra el campo).

Preset `sorter` (constante): `joint_topic /sorter/joint_positions`,
`gripper_topic /sorter/gripper_position`, `led_topic /comando_led`,
`base (0.0, 1.0, 0.74)`, **`base_yaw 0.4636`**, cámara
`/overhead_camera_sorter/image_color` en `(0.25, 1.30, 2.27)`, recorte
`x (0.35, 0.65)`, `y (0.95, 1.35)`.

`apply_preset(nombre)`: destruye publicadores de articulaciones, pinza y LED
y la suscripción del localizador anterior (`destroy_subscription(locator.sub)`)
y los recrea con el preset (log `Controlando ahora: <Label> (joints=…, led=…)`).
**Giro de la base**: con `ψ = base_yaw`: `tcp_world() = rz(ψ) @ FK(thetas)[:3,3] + base`;
al mover, `objetivo_base = rz(−ψ) @ (objetivo_mundo − base)` y la orientación
`rz(−ψ) @ GRASP_R @ rz(yaw)`. Así X+ es +X del mundo también con el Sorter.

Publicadores y suscripciones **fijos** (no dependen del preset):
`/comando_led_loader` y `/comando_led` (STOP y REARME avisan **siempre a las
dos Pico**: antes, con el panel en modo Loader, la Pico del Sorter se quedaba
parpadeando para siempre); `/texto_producto` (publica y escucha, para la OLED
simulada); escucha los tres topics de LED y `/reset_clave_pedido`;
`/emergency_stop` (publica y escucha); `/warehouse/cube_delivered` → contador
`entregas_color = {R, G, B}` y `ultima_entrega_t` (entregas **reales**,
independientes de la web y del reparto); `/production/nuevo_lote` (Bool) y
`/production/lote_color_objetivo` (String, `LOTE_COLOR_QOS` importado de
`sorter_demo`); `/teleop_auto_cmd` (`move dx dy dz` | `open` | `close` |
`home` | `align` | `rotate grados`, con log `[auto] …` del resultado).

Operaciones:

- `wait_for_subscribers()`: hasta `max_wait_seconds`; si nadie escucha, log
  `Nadie se ha suscrito tras 45s (…)` y salir **sin** abrir la ventana.
- `_publish_joint(bruto)`: `comandado = bruto + offsets`, recortar a
  `JOINT_LIMITS`, publicar y **`thetas = recortado − offsets`** (si no, el
  estado interno se alejaba de la pose real: 130 pasos acabaron a 30 cm). Sin
  «envolver» por módulo (el límite de `joint4`, −3,1416, está pegado a ±π y el
  envoltorio daba saltos de 2π).
- `move_delta(dx, dy, dz)` → `(ok, mensaje)`: `_ir_a(tcp_mundo + delta, yaw)`
  (ver C.14.2: freno de 25° con subdivisión, límites, no converge → rechazo).
  **NO se bloquea durante una parada de emergencia** (a propósito:
  la parada es una pausa y el operario tiene que poder mover el brazo para
  desatascar un cubo o liberar un dedo; esto ya se «arregló» mal una vez).
- `go_home()`: publica `HOME_POSITIONS − offsets` y `yaw = 0`.
- `align_gripper_down()`: `_ir_a([x, y, min(z, SAFE_Z)], 0, freno=False)`
  (sin freno: reconfiguración deliberada). En HOME la pinza del PROTO de
  Webots está alta (z ≈ 1,68 m) y de lado; con la pinza hacia abajo ese punto
  es inalcanzable, por eso se baja como mucho a `SAFE_Z` (1,30), la misma
  referencia que usan los robots al salir de HOME.
- `rotate_delta(dyaw)`: `_ir_a(tcp_mundo, yaw + dyaw)` (freno de 25° y límites).
- `center_on_cube()`: `detect_color` + `locate_with_yaw(cube_table_z)`, y
  luego **la misma regla que los robots (C.11)**: si lo que ve la cámara se
  desvía más de `VISION_GROUND_TRUTH_MAX_DESVIO` (10 cm) de la posición real de
  ese color (`/warehouse/cube_positions`), manda la real y se avisa en el log
  (medido: las baldosas granates del suelo dan un rojo fantasma a 27 cm del
  cubo y el centrado iba a por él). Exige TCP ≥ `cube_table_z + 0.05` — si no:
  «Demasiado bajo para centrar sin riesgo…» —; luego `move_delta(dx, dy, 0)`.
- `set_gripper(pos)` (siempre, también en parada).
- `send_stop()`: `/emergency_stop=True` y `parada` a las dos Pico;
  `send_rearm()`: `False` y `rearme` a las dos.
- **Web** (timeouts 1,5 s, nunca rompen la ventana):
  - `_taller_login()`: `POST /login {"username":"admin","password":"admin"}` → token.
    (Ojo: esa clave va escrita en el código; si el usuario cambia la contraseña
    de `admin` en la web, el panel deja de ver pedidos. Díselo al usuario.)
  - `fetch_pedidos_pendientes()`: login si hace falta; `GET /pedidos` con
    `X-Session-Token`; ante 401/422 relogin una vez. Filtra: estado ∉
    {completado, cancelado} **y** `stock_disponible < pedida − completada`
    (lo que ya cubre el almacén no se le enseña al operario) **y**
    `numero_maquina ∈ {grupo_cadena, numero_maquina}` de esta línea (los
    libres, 0, solo salen si el grupo es 0). `None` si no hay conexión.
  - `reclamar_pedido(id)`: `POST /pedidos/{id}/reclamar {numero_maquina,
    grupo_cadena, forzar:false}`; `True` si lo consigue (libre, ya mío o de mi
    grupo); `False` con 409 o error de red.
  - `marcar_cubo_clasificado(color, producto_id=None)`: `POST
    /taller/cubo_clasificado {color, numero_maquina, grupo_cadena[, producto_id]}`
    → `(True, json)` o `(False, detalle)`; si el cuerpo del error no es JSON,
    usar el texto tal cual.

#### C.14.4 La ventana (`TeleopApp`)

Título `Panel de control manual - Panda [<nombre de la cadena>]`. Arranca a
**tamaño de pantalla completa** (`geometry` con el tamaño real de la
pantalla) y **todo el contenido va dentro de un lienzo con barras de
desplazamiento** vertical y horizontal (con pantallas pequeñas se cortaba).
Fuentes Arial 15 negrita (título), 13 negrita (estado), 12 negrita (botones),
monospace 11. `Ver. <VERSION>` pequeño arriba a la derecha (de `version.py`;
si falta, `sin-version`).

De arriba abajo:

1. Rótulo `PANEL DE CONTROL MANUAL` (amarillo) y franja de 30 rectángulos
   amarillo/negro alternos (600×10).
2. **Siempre visible, fuera de las pestañas** (marco `ridge`):
   - Estado `EN MARCHA` (verde) / `PARADO` (rojo) y, debajo, la línea de estado
     del lote (la misma que en Producción).
   - Botón rojo `PARADA\nDE EMERGENCIA` (15×3) y `REARME` (15×3; gris y
     deshabilitado salvo en parada, entonces amarillo).
   - A la derecha, **el nombre de la cadena en letra enorme** (tres veces la de
     estado, amarillo; `(sin nombre)` en gris), un resumen de solo lectura
     (`Grupo Cadena: g · Nº Máquina: m · Automático: SÍ/no`, `Pico en esta
     cadena: …`, `Taller_Administracion: <url>`) y la línea de la pantalla
     OLED (`Pantalla Pico: Fabricando: Tuercas · Tuerca 10mm · 2003001`).
   - `Robot controlado:` con `LOADER` y `SORTER` (el activo en amarillo y
     hundido). Cambiar de robot: `apply_preset`, volver a HOME y orientar la
     pinza abajo.
3. `ttk.Notebook` (tema `clam`, pestañas oscuras y amarilla la seleccionada)
   con cuatro pestañas:

**Movimiento**: `TCP mundo: x=… y=… z=… giro=… deg` y `Paso actual: N cm`.
Marco `Mover TCP (mundo)`: cuadrícula `Y-` (1,0), `X+\nadelante` (0,1),
`X-\natras` (2,1), `Y+` (1,2), `Z+\nsubir` (0,3), `Z-\nbajar` (2,3) y
`📷 Centrar sobre cubo (X/Y, vision)` (fila 3, 4 columnas). Marco `Paso`:
`- paso` / `+ paso` (divide o duplica entre 0,2 y 5 cm). Marco `Pinza y
postura`: `ABRIR\npinza`, `CERRAR\npinza`, `HOME` (**con diálogo de
confirmación**: está pegado a botones de uso frecuente) y `Orientar\npinza
abajo`. Marco `Girar pinza`: `↺\nGirar-` / `↻\nGirar+` (5°). Marco `LED`:
`Rojo`, `Verde`, `Azul`, `Apagar` (al LED del robot elegido). Línea de
mensajes (verde si bien, `#ff6b6b` si no).

**Producción**:
- Marco `Resumen por producto (varios pedidos a la vez)`, reconstruido cada
  4 s: agrupa los pedidos por **código de producto** (no por color: dos
  productos sin LED se mezclaban) y por cada uno muestra
  `Nombre (código · LED o «sin LED»): completada/pedida hechas -- N por
  fabricar (M pedido/s)` y un botón `Lanzar todo` (verde `#2e7d32` y
  `Lanzando...` si es el producto en curso); debajo, si hay más de una
  variante, una fila gris por **subproducto** con sus propios números. Sin
  pedidos: `Sin pedidos pendientes.`; sin conexión: `Sin conexión con
  Taller_Administracion (<url>).` en rojo.
- Botón `Lanzar todo el resumen (uno detrás de otro)`.
- Marco `Pedidos pendientes (Taller_Administracion)` con scroll propio
  (lienzo de 1100×460 que crece con la ventana; rueda del ratón): por pedido,
  `Producto · Variante (código completo) (código · LED): completada/pedida --
  estado`, `+1 pieza` y `Lanzar este pedido` (verde `Lanzando...` si es el
  lanzado).
- Línea de estado del lote y botón `🔁 Repetir último lote` (deshabilitado
  hasta el primer lanzamiento).

**Raspberry Pi Pico** (simulación: no manda nada, solo escucha los mismos
topics que los puentes, para ver los LED sin hardware):
- Texto de introducción y dos recuadros, `Pico del Loader (USB)` y
  `Pico del Sorter (Wi-Fi)`, cada uno con un dibujo de la placa (rectángulo
  verde con pines, rótulo PICO), bolas de LED con su etiqueta y flechita
  (`Agarre`, y en el Loader también `Producto`), y el texto del color.
- En el Loader, un **HC-SR04 simulado**: un deslizador vertical tipo mesa de
  mezclas (arriba 50 cm = lejos, abajo 0) que a menos de
  `UMBRAL_HCSR04_CM` pinta el sensor en rojo, dice `N cm -- ¡detectado!
  (parada)` y dispara **una** parada (hasta volver a subir); y una **OLED
  simulada** (letra Courier verde sobre negro, 17×4) que pinta igual que la
  real: `Fabricando:` + las líneas separadas por `|`, o `Loader listo / sin
  lote`, o el aviso `MSG:`.
- En cada recuadro, un botón rojo `PARADA\nDE EMERGENCIA` que para **al
  pulsar** (no al soltar) y, si se mantiene `SEGUNDOS_RESET_CLAVE`, ofrece
  restablecer la clave (con cuenta atrás `Restableciendo la clave en N s...
  suelta para cancelar`).
- Repintado cada 300 ms; los parpadeos (alarma, `SINCOLOR`) se simulan con el
  reloj (0,3 s encendido / 0,3 s apagado).

**Configuración** (con scroll; **bloqueada con clave**; se vuelve a bloquear
sola al cambiar de pestaña, y lo no guardado se descarta):
- Barra `🔒 Configuración bloqueada` / `🔓 Configuración desbloqueada` con
  botón `Desbloquear (clave)` / `Bloquear` (diálogo con la clave oculta).
- `Identidad de la cadena`: `Nombre de la cadena:` (texto, Guardar o Intro;
  cambia el título de la ventana y el letrero de Webots), `Grupo Cadena:` y
  `Nº Máquina:` (desplegables 0..99 con Guardar; con Nº Máquina **0** se
  avisa de que así no podrá coger pedidos y se pide confirmación),
  `URL de Taller_Administracion:` (vacío = la de por defecto del contenedor;
  al guardar se fuerza un nuevo login).
- `Idioma`: desplegable Español/English/Euskera + Guardar («Se aplica al
  momento en todo el panel»); dos casillas `Mostrar pestaña "Producción"` y
  `Mostrar pestaña "Raspberry Pi Pico"` (se aplican y guardan al momento).
- `Cambiar clave de configuración`: clave nueva dos veces; se guarda solo si
  coinciden, tienen al menos 4 caracteres y no es la actual.
- `Producción`: casilla `Automático: lanzar pedidos solo, sin tocar nada`.
- `Raspberry Pi Pico de esta cadena (contenedor <host>)`: por cada Pico una
  casilla, su parámetro (puerto serie o IP) y su estado (`● en marcha`,
  `⚠ puente parado, reintentando`, `en la cadena "<nombre>"`,
  `● en marcha (lanzado a mano, fuera de esta configuración)`,
  `○ no usada en esta cadena`), el botón `Aplicar configuración de las Pico` y
  una nota: cada Pico solo puede estar en UNA cadena; el botón de la Pico W
  avisa siempre a la cadena que publica el puerto 5002 (la 1).
- Línea de mensajes de la configuración.

**Traducción del panel**: diccionario `TRADUCCIONES = {'en': {...}, 'eu': {...}}`
cuya **clave es el propio texto en castellano**; `t(texto_es, **vars)`
devuelve la traducción o el castellano si falta (nunca falla). Cada widget
creado con texto se apunta en una lista para retraducirlo al momento al
cambiar de idioma; lo que se reconstruye solo (pedidos, estado del lote) se
traduce en su siguiente refresco. Traduce **todo lo que ve el operario**
(etiquetas, botones, diálogos, mensajes); los logs se quedan en castellano.

#### C.14.5 Lanzar producción

Cuatro caminos, todos acaban en
`_lanzar_produccion(color, cantidad, etiqueta, pedido_id=None, forzar_reparto=False, codigo=None, producto_id=None, texto_oled=None)`:

- `Lanzar este pedido`: cantidad = `_pendiente_de_fabricar(p)`, `pedido_id`,
  color = `led_codigo` o `SIN_COLOR`, `texto_oled = "Producto|Variante|CódigoCompleto"`.
- `Lanzar todo` (un producto del resumen) y cada tramo de `Lanzar todo el
  resumen` y del modo Automático: `forzar_reparto=True`, `producto_id`,
  `codigo`, y `texto_oled` = `nombre|variante|código` si el grupo tiene una
  sola variante, si no solo el nombre.
- `Repetir último lote`: los mismos argumentos de la última vez (aviso si iba
  atado a un pedido: puede fabricar de más).

Antes de lanzar, cada botón: comprueba que no hay un lote en curso
(`_lote_en_curso`) ni cola; pide confirmación («si estás controlando el Loader
o el Sorter a mano, se pelearán por el brazo…»); y **reclama** en la web todos
los pedidos del grupo (`_reclamar_grupo`; si uno falla, no se lanza nada y se
dice que se reintentará).

`_lanzar_produccion`:

1. Si hay un `loader_demo` vivo que no lanzó este panel → negarse: `Ya hay un
   loader_demo corriendo fuera del panel -- espera a que termine o páralo.`
2. Guardar los argumentos para «Repetir» y habilitar ese botón.
3. Si no hay `sorter_demo` vivo (propio o ajeno): `Popen(['ros2','run',
   'panda_controller','sorter_demo','--ros-args','-r','__ns:=/sorter','-p',
   'robot_base_x:=0.0','-p','robot_base_y:=1.00','-p','robot_base_z:=0.74'])`
   con salida a `/tmp/lote_sorter.log` (modo `w`). Si hay uno vivo, se
   reutiliza (estado `activo (externo)`).
4. `Popen` del `loader_demo` con `cycles:={cantidad}`, los dos topics de LED y,
   si hay color, `-p only_color:="{color}"` (**comillas obligatorias**: YAML lee
   `Y`, `N`, `on`… como booleanos y el Loader petaba), salida a
   `/tmp/lote_loader.log`.
5. Publicar en `/texto_producto` el `texto_oled` (o la etiqueta).
6. Foto de `entregas_color`; reiniciar los marcadores de cierre; guardar color
   y código del producto; objetivo por color (`{color: cantidad}` o los tres).
7. Publicar `/production/nuevo_lote = True` (el Sorter aparca y baila).
8. Publicar `/production/lote_color_objetivo` =
   `f'{color or ""}:{total}:{pedido_id or ""}:{"1" if forzar_reparto else ""}:{producto_id or ""}'`,
   con `total = cantidad` si hay color o `cantidad × 3` si es mixto.
9. Estado: `Fabricando <etiqueta> (Loader lanzado, Sorter activo). Logs en
   /tmp/lote_loader.log y /tmp/lote_sorter.log.`

**Cuándo termina un lote** (`_lote_en_curso`, bug real de sobreproducción con
dos líneas: el Loader termina en cuanto deja el último cubo, pero el Sorter
tarda ~25 s por pieza en clasificar las que quedan, y en ese hueco Automático
relanzaba la cantidad entera): el lote sigue en curso mientras el Loader viva;
con el Loader terminado, se cierra cuando el Sorter ha contado todas las
piezas (`hechas ≥ objetivo`, sumando las entregas de **los tres** colores
desde la foto, porque el Loader usa los tres cubos) o tras
`LOTE_SIN_ENTREGAS_S` sin ninguna entrega nueva (aviso `Lote cerrado
INCOMPLETO`). `_lote_recien_cerrado()`: durante `MARGEN_TALLER_S` tras cerrar
(el Sorter publica la entrega un instante antes de apuntarla en la web).

`_actualizar_estado_lote()` (cada 2 s): `Lote Loader: sin lotes lanzados
todavía | EN CURSO | terminado (código N)  |  Sorter: sin arrancar | activo |
activo (externo) | parado  |  Fabricadas: h/o (C)` (o, mixto,
`Fabricadas: h/o (R:x/y G:… B:…)`). Si hay cola y el lote no está en curso
ni recién cerrado → `_lanzar_siguiente_de_cola()`.

`_lanzar_siguiente_de_cola()`: vuelve a pedir los pedidos y **recalcula la
cola con los números al día**; si el producto que se acaba de fabricar tiene
pedidos nuevos, se termina antes de cambiar de producto (se pone el primero);
reclama el grupo (si no puede, salta al siguiente) y lo lanza.

**Modo Automático** (`_auto_lanzar_si_toca`, desde el refresco de 4 s): si
está marcado, hay pedidos, no hay lote en curso ni recién cerrado ni cola →
encola el resumen entero **sin preguntar**, con el último producto fabricado
primero. **Freno** (`_vigilar_progreso_auto`): si un producto lanzado no
avanza (ni baja lo que falta ni sube lo completado)
`AUTO_MAX_TANDAS_SIN_PROGRESO` tandas seguidas, se deja de lanzar **ese**
producto y se avisa con un diálogo `AUTOMÁTICO DETENIDO para "<nombre>" …`
(explica que las piezas no llegan a la web y que revise la URL); se libera si
avanza por otra vía o al volver a marcar Automático.

`+1 pieza`: `marcar_cubo_clasificado` a mano y mensaje con el resultado
(`Pieza C registrada en el pedido #id (c/p).` o `… guardada en stock …`).

#### C.14.6 Pico desde el panel (`aplicar_config_picos`, `_vigilar_picos`)

- **Aplicar** (solo desbloqueado): para cada Pico, si se marca: la USB exige
  que exista el puerto en **este** contenedor (si no, error explicando que la
  Pico USB solo se ve desde la línea que la tiene en su `devices:`); si otra
  línea la tiene en `pico_asignacion.json`, pedir confirmación para
  quitársela. Apuntarla a nombre de este `host`, parar el puente si cambió el
  parámetro y lanzarlo si no vive. Si se desmarca: soltarla y parar su
  puente. Guardar `picos` en el fichero de la línea.
- **Vigilar** (cada 3 s): si otra línea se ha quedado una Pico nuestra, parar
  el puente y desmarcarla; si nadie la tiene apuntada, apuntarla; si su puente
  está caído, relanzarlo como mucho cada `PICO_REINTENTO_S`. Refrescar estados.

#### C.14.7 Restablecer la clave con el botón

Pulsación larga (10 s) del botón físico del Loader (llega por
`/reset_clave_pedido`) o de un botón rojo simulado: **solo** si está abierta
la pestaña Configuración o Raspberry Pi Pico (si no: «Pulsación larga
ignorada…»), con diálogo de confirmación. Al aceptar: borrar `clave_config`
(vuelve `1111`) y publicar `MSG:Contrasena|reseteada` en `/texto_producto`
durante 6 s, reponiendo después el texto que había (si no ha llegado otro).
La fuente de la OLED es ASCII: sin eñes ni tildes.

#### C.14.8 Al abrir y bucles

Al abrir: orientar la pinza abajo (desde HOME, sin esto todos los botones XYZ
se rechazaban) y arrancar los ciclos: `spin_once` cada 50 ms, pedidos cada
4 s, estado del lote cada 2 s, Pico cada 3 s, LED simulados cada 300 ms,
petición de reset de clave cada 300 ms. Cada clic se apunta en el log como
`[click] …` (con el resultado y la posición del TCP en los movimientos).

### C.15 Puentes con el hardware

**`led_publisher.py`** (Pico W del Sorter). Nodo `led_publisher`. Parámetros
`pico_ip` (`IP_DE_LA_PICO`), `pico_port` (5001), `socket_timeout` (2.0).
Escucha `/comando_led`. **Una conexión TCP por comando** (conectar, enviar,
cerrar). Traducción (en minúsculas): `r|rojo|red → R`, `g|verde|green → G`,
`b|azul|blue → B`, `0|apagar|off → 0`, `rearme|rearm → REARME`,
`parada|stop → PARADA`; otro → aviso `Comando LED no reconocido`. **Al
arrancar envía `REARME`** (la Pico guarda su estado: si la celda se reinicia
con la Pico parpadeando, nadie la rearmaría). Error de conexión → log y seguir.

**`led_publisher_usb.py`** (Pico del Loader). Nodo `led_publisher_usb`.
Parámetros `serial_port` (`/dev/ttyACM_LOADER`), `baudrate` (115200),
`led_topic` (`/comando_led_loader`), `led_topic_producto`
(`/comando_led_producto`), `texto_topic` (`/texto_producto`).

- Puerto con `pyserial` (`timeout=1.0`) protegido por un *lock*. Si no abre:
  error una vez y reintento en cada envío (el nodo sigue vivo sin la Pico).
  Envío `comando + '\n'`; error de escritura → cerrar y reintentar después.
- LED de agarre: misma traducción que el puente Wi-Fi.
- LED de producto (tabla **gemela** de la paleta de la web; si se añade un
  color, en los dos sitios):
  ```python
  COLOR_A_RGB = {'R': (255, 0, 0), 'G': (0, 255, 0), 'B': (0, 0, 255),
                 'Y': (255, 60, 0),      # calibrado a ojo: el verde del LED satura mas que el rojo
                 'M': (200, 0, 200), 'C': (0, 200, 200), 'W': (255, 255, 255)}
  ```
  `/comando_led_producto`: `SINCOLOR` → hilo que **parpadea en blanco**
  (`PROD:255,255,255` / `PROD:0,0,0` cada 0,4 s) hasta el siguiente comando;
  `0|APAGAR|OFF` → `PROD:0,0,0` y además `TXT:` (limpia la pantalla: es el fin
  de lote); letra conocida → `PROD:r,g,b`; otra → aviso. Cualquier comando
  para un parpadeo en marcha.
- `/texto_producto`: sustituir saltos de línea por espacios; si empieza por
  `MSG:` se manda tal cual; si no, `TXT:` + texto.
- **Hilo lector**: lee líneas; `BOTON_PARADA` → publica `/emergency_stop=True`
  (aviso `PARADA DE EMERGENCIA recibida de la Pico del Loader …`);
  `BOTON_CLAVE_RESET` → publica `/reset_clave_pedido=True`. El resto (ecos de
  la Pico) se ignora.
- Al arrancar: `REARME`, `PROD:0,0,0` y `TXT:` (la Pico conserva lo último).

**`button_listener.py`** (aviso del botón de la Pico W). Nodo
`button_listener`, parámetros `listen_host` (`0.0.0.0`) y `listen_port`
(5002). Publica `/emergency_stop`. Hilo servidor TCP con `SO_REUSEADDR`,
`listen(1)`, `accept` con timeout 1 s; lee hasta 1024 bytes; si
`decode().strip().upper() == 'STOP'` → aviso y publicar `True`; otro texto →
aviso; cerrar. Si `bind()` falla (puerto ocupado por otro listener suelto):
log de error y **reintento cada 5 s** (antes el hilo moría en silencio y el
nodo quedaba «vivo pero sordo»). Prueba sin Pico: `echo -n "STOP" | ncat <IP_del_PC> 5002`.

### C.16 `estop_panel.py`

Ventanita solo con STOP y REARME (anterior al panel completo; redundante pero
se mantiene). Nodo `estop_panel`: publica y escucha `/emergency_stop`; STOP =
`True` + `parada`, REARME = `False` + `rearme`, **a las dos Pico**
(`/comando_led` y `/comando_led_loader`). Ventana `Panel de parada - Panda`:
rótulo `CONTROL DE PARADA DE EMERGENCIA`, franja de 18 rayas (360×10), estado,
`PARADA\nDE EMERGENCIA` (15×4) y `REARME` (15×4, deshabilitado salvo en
parada), línea de mensajes; `spin_once` cada 50 ms.

---

## D. Las dos Raspberry Pi Pico

Una Pico por robot. **Son opcionales**: sin ellas la celda funciona igual (el
panel las simula). Nacieron porque el proyecto empezó sin robot físico y se
quería tocar algo real; son el puente entre lo virtual y lo físico.

**Regla de trabajo**: si el usuario menciona un pin, un botón o un LED sin
decir la placa, **pregunta** si es la del Loader o la del Sorter (el GPIO16
tiene botón en las dos; asumirlo ya obligó a deshacer un LED entero).

### D.1 Resumen de cableado

| | **Sorter** (Pico W) | **Loader** (Pico sin Wi-Fi) |
|---|---|---|
| Habla con el PC | Wi-Fi: servidor en `<IP_de_la_Pico>:5001`; avisa del botón a `PC_IP:5002` | Cable USB (puerto serie) |
| LED de agarre (on/off) | GP13 R / GP14 G / GP15 B | GP13 / GP14 / GP15 |
| LED de producto (PWM 1000 Hz) | — | GP17 R / GP18 G / GP19 B |
| Botón de parada | GP16 a GND, *pull-up* interna | GP16 a GND, *pull-up* interna |
| Sensor de proximidad | — | HC-SR04: TRIG = GP20 (pata 26), ECHO = GP21 (pata 27) **por divisor** |
| Pantalla | — | OLED SSD1306 128×64 I2C: SDA = GP4, SCL = GP5 (**`SoftI2C`**) |
| Firmware | `Rasberry_Pi_Pico/main.py` | `Rasberry_Pi_Pico_USB_Loader/main.py` |

- **LED de agarre**: LED RGB de cátodo común; solo se enciende un color a la
  vez, así que basta **una resistencia de 220 Ω en el cátodo común**.
- **Botón**: un terminal a GP16 y el otro a GND; sin resistencia externa
  (`Pin.PULL_UP`): reposo = 1, pulsado = 0. Ojo con el pulsador de 4 patas:
  las dos de un mismo lado están unidas por dentro; hay que usar una de cada
  lado.
- **LED de producto**: LED RGB de 4 patas; una resistencia por canal: rojo
  **150 Ω**, verde **68 Ω**, azul **68 Ω**; cátodo directo a GND. Sin difusor
  los colores mezclados (amarillo) se ven como dos puntos: es óptica, no
  valores.
- **HC-SR04**: VCC a +5 V, GND común con la Pico (obligatorio). TRIG directo a
  GP20 (3,3 V bastan). **ECHO da 5 V**: pasa por un divisor R1 = 1 kΩ (en
  serie) y R2 = 2,2 kΩ (a GND) → ~3,44 V en GP21. Sin divisor se fríe el pin.
- **OLED**: `machine.SoftI2C(scl=Pin(5), sda=Pin(4), freq=50000)`. Con el I2C
  por hardware la pantalla aparece en el escaneo (0x3C) pero **toda escritura
  falla con `OSError EIO`**.
- Material (las dos juntas): 2 Pico (una W), 2 LED RGB de cátodo común,
  1 HC-SR04, 1 OLED SSD1306 0,96" I2C, 2 pulsadores, resistencias 220 Ω ×2,
  150 Ω, 68 Ω ×2, 1 kΩ y 2,2 kΩ, protoboard, cables y una fuente de 5 V para la
  regleta.

### D.2 Cómo se graba el programa (Thonny) — importante

- Nunca con **Run/F5** un `main.py` largo con tildes: Thonny lo manda por la
  consola en bruto y da un `SyntaxError` falso en una línea cualquiera.
  Siempre: *Archivo → Guardar como → la Pico → `main.py`* y el botón rojo
  **Stop/Restart**.
- Con la Pico del Loader: **desconectar Thonny** antes de usar el puente de
  ROS (Linux deja abrir el puerto a los dos y los bytes se reparten; el aviso
  del botón se lo puede quedar Thonny). La Pico del Loader es difícil de
  interrumpir con `mpremote`/Ctrl-C: usar Thonny.
- Tras reconectar la Pico del Loader, recrear el contenedor ROS
  (`docker compose up -d --force-recreate ros2_app`).
- Con otra Pico distinta, su ruta `by-id` cambia: actualizar el `.env`.

### D.3 Firmware del Sorter (`Rasberry_Pi_Pico/main.py`, Pico W)

Configuración en `wifi_config.py` (**plantilla** en Git):

```python
SSID = "TU_WIFI_AQUI"
PASSWORD = "TU_CLAVE_WIFI_AQUI"
# IP de TU ORDENADOR en la misma red Wi-Fi (para que el boton de parada avise
# a ROS2). Averiguala con "hostname -I" (busca algo como 192.168.1.XXX).
PC_IP = "192.168.1.XXX"
PC_PUERTO = 5002
```

`webrepl_cfg.py`: `PASS = 'TU_CLAVE_WEBREPL_AQUI'`. `LEEME.md` explica que
son plantillas y cómo evitar subir las claves:
`git update-index --skip-worktree Rasberry_Pi_Pico/wifi_config.py Rasberry_Pi_Pico/webrepl_cfg.py`.
Si una clave se cuela en un commit, hay que **cambiar la clave de la Wi-Fi**
(borrar el commit no basta).

Comportamiento (`machine`, `network`, `socket`, `time`, `webrepl`):

1. LED 13/14/15 como salida, apagados. Botón en 16 con *pull-up*.
2. **Antirrebote** (`comprobar_boton`, una vez por vuelta): si el valor cambia
   y lleva ≥ `DEBOUNCE_MS = 40` estable, se acepta; en flanco de bajada →
   `print("BOTON DE PARADA PULSADO")`, `parada_activa = True`, **apagar el LED
   en local al instante** (no depende de la red) y `avisar_parada_a_pc()`.
3. `avisar_parada_a_pc()`: sin `PC_IP`, aviso y nada; si no, socket TCP a
   `PC_IP:PC_PUERTO` con timeout 1 s, enviar `b"STOP"` y cerrar. Fallos: solo
   se imprimen.
4. **Parpadeo de parada**: mientras `parada_activa`, rojo alterno cada
   `PARPADEO_MS = 300`, verde y azul apagados.
5. Wi-Fi: `WLAN(STA_IF)`, `connect(SSID, PASSWORD)`. **Mientras conecta**
   (al arrancar y al reconectar), vueltas de 50 ms atendiendo el botón y el
   parpadeo (antes era un `sleep(1)` a ciegas y el botón no cortaba ni el LED).
   Imprimir la IP.
6. `webrepl.start()` (en `try`).
7. Servidor TCP en `(IP_propia, 5001)`, `SO_REUSEADDR`, `listen(1)`, **no
   bloqueante**; se recrea si cambia la IP tras reconectar.
8. Bucle cada 50 ms: botón; parpadeo; cada `CICLOS_CHEQUEO_WIFI = 100`
   vueltas (~5 s), si se cayó la Wi-Fi: cerrar la conexión, reconectar y
   recrear el servidor si cambió la IP. Aceptar **una** conexión; con
   conexión, `recv(1024)`: datos → `comando = decode().strip().upper()`,
   `print("Recibido comando RGB:", comando)`; vacío → cerrar (el PC abre una
   por comando); `OSError` distinto de 11 (EAGAIN) → cerrar. Cualquier
   excepción del bucle cierra la conexión y sigue.
9. Comandos: `PARADA` → parada (como el botón, sin avisar al PC); `REARME` →
   fin de parada y LED apagado (**el único que se acepta en parada**); en
   parada, cualquier otro se ignora; `R`/`G`/`B` → apagar y encender ese
   canal; `0`/`APAGAR` → apagar.

Scripts de prueba (en la misma carpeta): `test_rgb.py` (5 ciclos rojo→verde→
azul de 1 s), `test_boton_led.py` (el rojo se enciende mientras se pulsa),
`led_gpio14.py` (parpadeo del LED interno `Pin("LED")` y del GP14),
`prueba_webrepl.py` (conectar Wi-Fi y solo WebREPL) y `test_cliente_pc.py`
(se ejecuta en el PC: manda `R`, `G`, `B`, `0` cada 2 s a `<ip>:5001`).

### D.4 Firmware del Loader (`Rasberry_Pi_Pico_USB_Loader/main.py`, Pico sin Wi-Fi)

Sin red: lee comandos del propio USB (`sys.stdin`) y avisa escribiendo por el
mismo USB con `print`.

1. LED de agarre 13/14/15 como en la Pico W.
2. LED de producto: `PWM` en GP17/18/19 a 1000 Hz;
   `set_led_producto(r, g, b)` con cada canal 0..255 →
   `duty_u16(int(clamp(v) / 255 · 65535))`. Arranca apagado.
3. Botón GP16 con el mismo antirrebote de 40 ms, **pero solo dispara si no
   hay ya parada** (`if estado == 0 and not parada_activa`): este botón rebota
   mucho mientras se mantiene y, sin esa condición, inundaba el USB de avisos
   que llegaban corruptos. Al dispararse: `parada_activa = True`, LED apagado y
   `print('BOTON_PARADA')` (línea centinela para el puente).
4. **Pulsación larga** (`comprobar_pulsacion_larga`): mide cuánto lleva el
   botón pulsado; a los `LARGA_MS = 10000` imprime **una vez**
   `BOTON_CLAVE_RESET`. Un «soltado» solo cuenta si dura `SOLTADO_MS = 400`
   seguidos (los rebotes cortos no reinician la cuenta). No retrasa la parada
   normal. Solo cuenta el botón, nunca el HC-SR04.
5. **HC-SR04** (`comprobar_proximidad`, si no hay ya parada): TRIG a 0 5 µs,
   a 1 10 µs, a 0; `machine.time_pulse_us(ECHO, 1, 30000)`; negativo u
   `OSError` → sin lectura (no dispara); `cm = µs / 58`. Si
   `cm < DISTANCIA_MIN_CM = 10` → exactamente lo mismo que el botón (parada,
   LED apagado, `print('BOTON_PARADA')`). **Sin filtro de varias lecturas** a
   propósito (una parada de más es molesta pero segura; si da falsos positivos,
   bajar el umbral o mover el sensor, no quitar el aviso).
6. **OLED** (opcional, todo en `try`: sin pantalla sigue igual):
   `import ssd1306` y `SSD1306_I2C(128, 64, SoftI2C(scl=Pin(5), sda=Pin(4), freq=50000))`.
   `mostrar_oled(titulo, lineas)`: borrar, título en la fila 0 y cada línea en
   su fila (16, 28, 40, 52; máximo 16 caracteres cada una), `show()`; nunca
   lanza. Al arrancar: `Loader listo` / `sin lote`.
7. Parpadeo de parada igual (300 ms, solo el LED de agarre).
8. `select.poll()` sobre `sys.stdin` (`POLLIN`); `print('Pico Loader lista,
   esperando comandos RGB por USB (R/G/B/0)...')`.
9. Bucle: botón, pulsación larga, proximidad, parpadeo, `poll(50)`. Leer
   carácter a carácter hasta `\n` o `\r`; `crudo = buffer.strip()` (conserva
   mayúsculas para los textos), `comando = crudo.upper()`; vacíos se ignoran;
   `print('Recibido comando RGB:', comando)`.
10. Comandos: `PARADA` (parada sin línea centinela), `REARME` (fin de parada,
    LED apagado), `PROD:r,g,b` (LED de producto, **también en parada**:
    formato inválido → aviso), `TXT:<texto>` (OLED: `Fabricando:` y el texto
    partido por `|`; vacío → `Loader listo / sin lote`; también en parada),
    `MSG:<título>|<línea>…` (aviso con su propio título; también en parada);
    en parada, el resto se ignora; `R`/`G`/`B`/`0`/`APAGAR` → LED de agarre;
    otro → `Comando no reconocido: …`.

`ssd1306.py`: el driver **oficial de micropython-lib**
(`micropython/drivers/display/ssd1306/ssd1306.py`), sin modificar; se copia a
la Pico junto a `main.py`. `test_hcsr04.py`: prueba suelta del sensor (20
lecturas cada 300 ms, imprime la distancia o «sin eco»).

---

## E. La web de pedidos (`Taller_Administracion`)

Un proyecto **aparte** de la celda: solo se hablan por HTTP. Si está apagada,
la celda sigue funcionando; simplemente nadie apunta la producción. Hecha con
**FastAPI + SQLAlchemy + SQLite**, servida por uvicorn. La API interactiva
queda en `/docs`.

### E.1 Docker

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /workspace
# git: solo para calcular la VERSION desde el repo padre montado en /workspace/repo.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Recarga automatica SOLO si TALLER_RELOAD tiene valor (equipo de desarrollo, en
# Taller_Administracion/.env). Por defecto sin ella: en Windows uvicorn veia
# "cambios" sin parar en el repo montado y la web entraba en bucle de reinicios
# (acotarlo con --reload-dir no lo evito).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 ${TALLER_RELOAD:+--reload --reload-dir /workspace/app}"]
```

`docker-compose.yml`:

```yaml
services:
  admin_api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: taller_admin_api
    hostname: taller_admin_api
    volumes:
      - ./app:/workspace/app
      - ./data:/workspace/data
      - ./tests:/workspace/tests
      - ./pytest.ini:/workspace/pytest.ini
      - ./requirements-dev.txt:/workspace/requirements-dev.txt:ro   # para instalar pytest (E.14)
      - ..:/workspace/repo:ro          # repo padre: manuales y version
    ports:
      - "8000:8000"
    environment:
      - TALLER_DB_PATH=/workspace/data/taller.db
      - TALLER_DEV_MODE=true
      - TALLER_REPO_DIR=/workspace/repo
      - TALLER_RELOAD=${TALLER_RELOAD:-}   # vacio = sin recarga automatica (lo normal)
```

`requirements.txt`: `fastapi==0.115.0`, `uvicorn[standard]==0.30.6`,
`sqlalchemy==2.0.35`, `pydantic==2.9.2`. `requirements-dev.txt`:
`-r requirements.txt`, `pytest==8.3.3`, `httpx==0.27.2`, `pytest-cov==5.0.0`.
`pytest.ini`: `testpaths = tests`, `python_files = test_*.py`, `addopts = -q`.

Consecuencias: `data/taller.db` lo crea el contenedor (en Linux, como root:
desde el anfitrión no se escribe sin sudo; las correcciones de datos se hacen
por la API o con `docker exec`). Las sesiones viven **en memoria**: cada
reinicio del servidor las borra (el panel web vuelve solo al login).

Variables de entorno: `TALLER_DB_PATH`, `TALLER_DEV_MODE` (`true` en este
compose), `TALLER_MASTER_PASSWORD` (`1111`), `TALLER_ADMIN_PASSWORD`
(`admin`), `TALLER_PASSWORD_INICIAL` (`1111`), `TALLER_DATOS_ARRANQUE`
(fichero de clientes iniciales), `TALLER_REPO_DIR`, `TALLER_BARRIDO_SEGUNDOS`
(`10`; 0 = apagado), `TALLER_RELOAD`.

### E.2 Módulos

| Fichero | Qué hace |
|---|---|
| `database.py` | `DB_PATH = os.environ.get("TALLER_DB_PATH", "./data/taller.db")`; `create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})`; `SessionLocal` (autocommit y autoflush **apagados**); `Base`; `get_db()` |
| `models.py` | Tablas (E.3) |
| `schemas.py` | Modelos pydantic de entrada/salida (con `from_attributes`) |
| `auth.py` | Roles, contraseñas, sesiones, permisos (E.4) |
| `codigos.py` | Código de cliente de 3 caracteres y nombres de usuario (E.5) |
| `importes.py` | Base, IVA por tipo y total en céntimos (E.7) |
| `auditoria.py` | `audit(db, tabla, registro_id, accion, usuario_id, detalle)`: añade un `AuditLog` y hace commit |
| `contabilidad.py` | `APIRouter` con tarifas, historial de precios, correcciones, empresas emisoras y facturas (E.7) |
| `datos_arranque.py` | Lee y carga el fichero de clientes iniciales (E.8) |
| `cargar_arranque.py` | `python -m app.cargar_arranque [--fichero RUTA] [--renombrar]`: añade a una base que ya tiene datos lo que falte del fichero, sin borrar nada |
| `migraciones.py` | Migración mínima de columnas (E.9) |
| `main.py` | La app, el sembrado, el ciclo de pedidos, el almacén, el reparto y las rutas |

**Versión**: `VERSION = _version_desde_git(REPO_DIR) or _version_estatica() or "sin-version"`.
`_version_desde_git` hace lo mismo que `generar_version.sh` con
`git -c safe.directory=* …` (el repo montado es de otro dueño; sin eso git se
niega), timeout 5 s, y nunca lanza. `_version_estatica` lee `app/version.py`
(solo como último recurso: es una foto fija que puede estar desfasada).
`REPO_DIR = TALLER_REPO_DIR` o dos niveles por encima de `app/`.

Al importar `main.py`: `Base.metadata.create_all(bind=engine)` y
`migrar_columnas_faltantes(engine, Base)`; `app = FastAPI(title="Taller - Administracion")`;
`app.include_router(contabilidad.router)`.

### E.3 Modelo de datos (tablas)

Todas las fechas en UTC (`datetime.utcnow`). **Dinero siempre en céntimos
enteros**, nunca `float`. Nada se borra de verdad: bajas lógicas (`activo`).

- **`clientes`**: `id`, `razon_social` (obligatoria), `codigo` (3, único vía
  índice creado al arrancar), `cif`, `direccion`, `codigo_postal`,
  `poblacion`, `provincia`, `email_facturacion`, `activo`, `creado_en`,
  `creado_por_id`, `modificado_en`, `modificado_por_id`.
- **`usuarios`**: `id`, `username` (único, en minúsculas), `password_hash`
  (puede ser nulo), `nombre_completo`, `rol` (`admin_sistema` |
  `admin_cliente` | `normal` | `empleado`), `cliente_id` (nulo para
  `admin_sistema` y `empleado`), `sucursal`, `activo`, `permiso_produccion`,
  `permiso_contabilidad` (solo cuentan para `empleado`), sellos de alta y
  modificación.
- **`audit_log`**: `tabla`, `registro_id`, `accion` (`alta` | `baja` |
  `modificacion`), `usuario_id`, `detalle`, `fecha`.
- **`colores`**: `codigo` (único, **solo letras**), `nombre`, `r`, `g`, `b`,
  `fisico` (hay cubo real en Webots), `activo`.
- **`productos`**: `nombre` (único), `codigo` (3 alfanuméricos, único),
  `activo`, `grupo_cadena` (0..99; 0 = cualquiera), `id_led` (opcional, FK a
  `colores`; **único entre productos activos**, validado a mano). Propiedad
  `led_codigo`. El LED es **decoración**: nunca condiciona el negocio.
- **`subproductos`** (la variante que se pide de verdad): `producto_id`,
  `nombre`, `codigo` (4 alfanuméricos, único **dentro** de su producto:
  `UniqueConstraint("producto_id", "codigo")`), `activo`, `precio_centimos`
  (tarifa general, sin IVA), `iva_porcentaje` (21). Propiedad
  `codigo_completo = producto.codigo + codigo`.
- **`paquetes`**: `nombre` (único), `codigo` (único), `activo`,
  `precio_centimos` (**nulo = sin precio propio**: se cobra la suma de sus
  productos), `iva_porcentaje`. **`paquete_componentes`**: clave
  (`paquete_id`, `subproducto_id`) y `cantidad`. Un paquete nunca tiene stock.
- **`cliente_productos`** (el catálogo): clave (`cliente_id`, `producto_id`),
  `asignado_en`, `asignado_por_id`.
- **`pedidos`**: `subproducto_id`, `producto_id` (**desnormalizado a
  propósito** = el del subproducto: el stock y el reparto van por producto),
  `paquete_origen_id`, **`grupo_entrega`** (columna en la base llamada
  `grupo_paquete`: los pedidos que se entregan juntos, con el id del primero;
  nulo = suelto), `paquete_pedido_id` (FK a `pedidos_paquete`), `cliente_id`,
  `usuario_id`, `cantidad_pedida`, **`cantidad_completada`** (piezas **listas**
  reservadas al pedido), **`cantidad_repartida`** (ya entregadas en un
  albarán; siempre `repartida ≤ completada ≤ pedida`), `estado`, `urgente`,
  `precio_unitario_centimos` e `iva_porcentaje` (**congelados** al pedir),
  `precio_origen` (`tarifa_general` | `tarifa_cliente` | `manual` |
  `paquete`), `numero_maquina` (0 = libre), `creado_en`. Propiedades
  `paquete_nombre`, `paquete_precio_centimos`, `paquete_cantidad`.
- **`pedidos_paquete`** (UN paquete pedido): `paquete_id`, `cliente_id`,
  `cantidad` (de paquetes), `cantidad_repartida` (0 o toda: un paquete se
  entrega entero), `precio_unitario_centimos` (nulo = sin precio propio),
  `iva_porcentaje`, `precio_origen` (`paquete_general` | `paquete_cliente` |
  `manual`), `creado_en`. Sus productos son pedidos normales que apuntan aquí.
- **`stock`**: `producto_id` (clave), `cantidad_actual`, `actualizado_en`.
  El stock físico va por **producto** (una vez en el almacén no se distingue
  un tornillo de 10 mm de uno de 20).
- **`movimientos_stock`** (libro de **solo añadir**): `producto_id`, `tipo`
  (`entrada` | `salida`), `cantidad`, `motivo` (`produccion`,
  `asignacion_pedido`, `ajuste_manual`), `pedido_id`, `usuario_id`, `fecha`.
- **`eventos_produccion`**: `robot`, `color`, `tipo`, `fecha`.
- **`configuracion_almacen`** (fila única, id 1): `reparto_automatico` (True),
  `expedicion_automatica` (True), `factor_piezas` (1; 1/10/100/1000, solo para
  imprimir), y columnas obsoletas `emisor_*` (solo para migrar un emisor antiguo).
- **`emisores`** (empresas que facturan): `razon_social`, `cif`, `direccion`
  (obligatorios), `email`, `serie_facturas` (única, `FAC`), `serie_rectificativas`
  (única, `RECT`), `por_defecto`, `activo`. Nunca se borran: se desactivan.
- **`repartos`** (albaranes, **solo añadir**): `numero` (único,
  `ALB-AAAA-nnnnnn`), `cliente_id`, `fecha`, `usuario_id` (nulo si salió
  solo), `automatico`.
- **`reparto_lineas`**: `reparto_id`, `pedido_id` y `subproducto_id` (nulos en
  la línea de un paquete), `tipo` (`normal` | `paquete` | `componente`),
  `paquete_pedido_id`, `paquete_nombre`, `paquete_cantidad`, `descripcion`
  (copiada: `Producto · Variante (código completo)`), `cantidad`,
  `precio_unitario_centimos`, `iva_porcentaje`.
- **`tarifas_cliente`**: clave (`cliente_id`, `subproducto_id`),
  `precio_centimos`, `actualizado_en`, `actualizado_por_id`.
  **`tarifas_cliente_paquete`**: igual con `paquete_id`.
- **`historial_precios`** (solo añadir): `tipo` (`tarifa_general` |
  `tarifa_cliente` | `pedido` | `albaran` | `paquete_general` |
  `paquete_cliente` | `pedido_paquete`), `subproducto_id` o `paquete_id`,
  `cliente_id`, `pedido_id`, `reparto_linea_id`, `precio_anterior_centimos`,
  `precio_nuevo_centimos` (nulo = quitada la tarifa o paquete sin precio),
  `iva_anterior`, `iva_nuevo`, `motivo`, `usuario_id`, `fecha`.
- **`facturas`** (solo añadir): `numero` (único), `tipo` (`factura` |
  `rectificativa`), `estado` (`emitida` | `anulada`), `cliente_id`,
  `rectifica_id`, `emisor_id`, `motivo`, `fecha`, `usuario_id`, **copia** de
  los datos del emisor (`emisor_razon_social`, `emisor_cif`,
  `emisor_direccion`, `emisor_email`) y del cliente (`cliente_razon_social`,
  `cliente_cif`, `cliente_direccion`, `cliente_email`), `fecha_pago`,
  `metodo_pago`. Relación `rectifica` (a sí misma).
- **`factura_lineas`**: `factura_id`, `reparto_linea_id` (nulo en
  rectificativas), `albaran_numero`, `tipo`, `paquete_pedido_id`,
  `paquete_nombre`, `paquete_cantidad`, `descripcion`, `cantidad` (negativa en
  una rectificativa), `precio_unitario_centimos`, `iva_porcentaje`.

Base, IVA y total de albaranes y facturas **se calculan** de las líneas cada
vez (no se guardan: así no se descuadran).

### E.4 Usuarios, roles y permisos (`auth.py`)

- Roles: `admin_sistema` (el taller: todo), `admin_cliente` (gestiona su
  empresa: sus usuarios, su catálogo, sus pedidos, ve sus albaranes, facturas
  y tarifas), `normal` (hace pedidos y ve los suyos), `empleado` (gente del
  taller, sin cliente: ve **solo** las secciones que tenga marcadas,
  **Producción** y/o **Contabilidad**, nunca Administración; no hace pedidos;
  necesita usuario y contraseña propios).
- `hash_password`: sal hexadecimal de 16 bytes + `sha256(sal + clave)`,
  guardado como `sal$hash`. `verify_password` lo comprueba.
- `check_password(clave, usuario)`: la **maestra** (`TALLER_MASTER_PASSWORD`,
  `1111`) vale siempre para un `normal` y, con `TALLER_DEV_MODE=true`, para
  cualquier rol; fuera del modo desarrollo los demás roles necesitan su
  contraseña propia. Un usuario sin `password_hash` solo entra con la maestra.
- Sesiones: diccionario **en memoria** `token → usuario_id`; `create_session`
  (`secrets.token_hex(24)`), `destroy_session`. Cabecera `X-Session-Token`.
  `get_current_usuario`: sin token o usuario inactivo → **401** «Sesion no
  valida -- inicia sesion de nuevo.».
- `require_roles(*roles)` → 403 «No tienes permiso para esto.».
  `tiene_permiso(usuario, grupo)`: `admin_sistema` siempre; `empleado` según su
  casilla. `es_interno(usuario)`: tiene Producción o Contabilidad (ve los datos
  de **todos** los clientes). `require_permiso(*grupos, roles_extra=())`: pasa
  quien tenga alguno de los grupos o sea de `roles_extra` (p. ej.
  `admin_cliente`, que luego se limita a lo suyo).
  `puede_gestionar_cliente(usuario, cliente_id)`: `admin_sistema` sí;
  `admin_cliente` solo el suyo.

### E.5 Códigos de cliente y nombres de usuario (`codigos.py`)

Cada cliente tiene un **código de 3 letras o cifras** (MUR, ERE, IRA…). Los
usuarios salen de él: `<codigo>-admin` (el administrador de la empresa) y
`<codigo>-<sucursal>` (uno por sucursal: `mur-bilbao`). Así dos clientes
pueden tener cada uno su sucursal de Bilbao.

- `normalizar_codigo(texto)`: quitar tildes, mayúsculas, debe casar
  `^[A-Z0-9]{3}$` o lanza `ErrorCodigo` («… son 3 letras o cifras (por ejemplo MUR).»).
- `sugerir_codigo(razon_social, ocupados)`: palabras de la razón social sin
  tildes ni símbolos, quitando las vacías (`s l a u sl sa slu sc sll cb y de
  del la las el los e en`); candidatos: las 3 primeras letras de cada palabra
  (rellenando con `X`), luego las 2 primeras + una cifra 1-9, luego la primera
  + dos cifras 01-99; el primero libre. Ej.: «Suministros Ereño S.A.» → `SUM`
  (y si está cogido, `ERE`).
- `slug(texto)`: sin tildes, minúsculas, lo que no es letra o cifra → `-`
  (`A Coruña` → `a-coruna`).
- `usuario_de(codigo, sucursal, es_admin)` → `f"{codigo.lower()}-{'admin' if es_admin else slug(sucursal)}"`.
- `asignar_faltantes(db)`: al arrancar, da código a los clientes de bases
  antiguas que no lo tengan (sin renombrar a sus usuarios).

### E.6 El ciclo de un pedido (reglas de negocio)

```
        taller fabrica                       almacén asigna                reparto entrega
pedido ─────────────────► STOCK LIBRE ─────────────────────► LISTO ─────────────────────► REPARTIDO
       (cubo_clasificado)       reparto_automatico  (cantidad_completada)  expedicion_automatica  (albarán)
```

| Estado | Significa |
|---|---|
| `pendiente` | nada listo todavía |
| `en_proceso` | algo listo, falta el resto |
| `listo` | todo listo, sin entregar |
| `completado` | **repartido** (con albarán) |
| `cancelado` | cancelado (solo se puede si estaba `pendiente`) |

`_estado_pedido(p)`: cancelado se queda; `repartida ≥ pedida` → completado;
`completada ≥ pedida` → listo; `completada > 0` → en_proceso; si no,
pendiente. `ESTADOS_NO_ASIGNABLES = (listo, completado, cancelado)`;
`ESTADOS_ABIERTOS = (pendiente, en_proceso, listo)`.

Reglas:

1. **Crear un pedido** (`_crear_pedido_de_subproducto`): copia el precio que
   le toca **hoy** (`precio_para`: tarifa del cliente si la tiene, si no la
   general) y el IVA; si es componente de un paquete **con** precio propio,
   precio 0, origen `paquete` e IVA del paquete. Nace `pendiente`, no urgente y
   con `numero_maquina = producto.grupo_cadena`. Luego, salvo que se diga lo
   contrario, `_servir_y_expedir`.
2. **`_servir_desde_stock(pedido)`**: si hay stock libre de su producto, pasa
   `min(stock, lo que falta)` al pedido (`cantidad_completada`), resta stock y
   deja un movimiento `salida` / `asignacion_pedido`.
3. **`_servir_y_expedir(pedidos)`**: solo con `reparto_automatico`: servir
   desde stock cada pedido y después `_expedir_listos_si_automatico`.
4. **`_expedir_listos_si_automatico(pedidos)`**: solo con
   `expedicion_automatica`: entrega (`_entregar`, automático) los que
   `_pedidos_que_salen_solos`: un pedido suelto cuando está `listo`; los de un
   **grupo** (paquete o cesta) solo cuando **todo el grupo** tiene sus piezas,
   y entonces todos juntos (un albarán por grupo, no por pieza).
5. **`_entregar(pedidos, usuario_id, automatico)`**: entrega lo listo y no
   repartido (`completada − repartida`); **un albarán por cliente**. Un
   **paquete se entrega ENTERO**: sus componentes solo salen cuando están todos
   listos, y siempre juntos (aunque se haya pedido repartir solo uno). Con
   precio propio, el albarán lleva **una línea del paquete** (`tipo=paquete`,
   `descripcion "Nombre (CODIGO)"`, cantidad de paquetes, su precio) y debajo
   sus componentes **sin precio** (`tipo=componente`); sin precio propio, cada
   componente con su precio (`tipo=normal`) pero agrupado bajo el paquete
   (`paquete_pedido_id`, `paquete_nombre`). Número del albarán: siguiente del
   año (`ALB-{año}-{n:06d}`, sacado del mayor ya guardado; `db.flush()` tras
   cada uno porque la sesión no hace autoflush). Actualiza cantidades y estado
   y deja auditoría. No toca el stock (ya salió al asignar).
6. **`cubo_clasificado`** (lo manda la celda, **sin sesión**): resuelve el
   producto por `pedido_id` (el pedido ya dice de qué es) > `producto_id` >
   color/LED (compatibilidad; color inválido → 400 «Color 'X' no valido.»; sin
   producto con ese LED → 404). **Siempre** suma 1 al stock (movimiento
   `entrada` / `produccion`). Si `reparto_automatico`: busca el pedido abierto
   (no listo/completado/cancelado) de ese producto: el de `pedido_id` si sigue
   abierto y es de esta máquina; si no, el más urgente y antiguo; **si viene
   `numero_maquina`, solo pedidos con `numero_maquina ∈ {numero_maquina,
   grupo_cadena}`** y primero los ya reclamados por esta máquina (bug real: una
   pieza de la máquina 20 completó un pedido de la 10); un pedido del grupo
   pasa a ser de esta máquina. Le asigna la pieza (stock −1, `completada +1`,
   movimiento de asignación) y aplica la expedición automática. Responde
   **siempre 200**: `{color, stock_actual, pedido (o null)}`. `forzar_reparto`
   se acepta por compatibilidad pero **no cambia nada**: el único interruptor
   es `reparto_automatico`.
7. **Barrido de stock parado** (cada `TALLER_BARRIDO_SEGUNDOS`, 10, en una
   tarea de fondo al arrancar; `asyncio.to_thread`; un fallo puntual solo
   avisa): con `reparto_automatico`, para cada producto con stock, recorre sus
   pedidos abiertos por urgencia, antigüedad e id, y asigna solo a los que el
   stock **cubre por completo**; un pedido que no se cubre entero se salta (no
   bloquea a los siguientes). Deja auditoría («barrido de stock: #…») y aplica
   la expedición automática. Nace de un fallo real: la pieza 9 de 10 entró al
   almacén sin asignarse, la celda veía el pedido «cubierto por stock» y no
   fabricaba más, y el pedido se quedó parado para siempre.
8. **`stock_disponible`** (`_con_stock_disponible`, sin tocar la base):
   simula el reparto FIFO del stock libre entre los pedidos abiertos de cada
   producto (urgentes primero, luego antigüedad) y rellena en cada pedido
   `stock_disponible`, `falta_fabricar` (`pedida − completada −
   stock_disponible`, solo en pendiente/en_proceso) y `para_repartir`
   (`completada − repartida + stock_disponible`, en estados abiertos). La celda
   usa `stock_disponible` para no fabricar lo que ya hay.
9. **Tiempos** (`_con_tiempos_de_proceso`, una sola consulta agregada):
   `segundos_proceso` = de la primera a la última asignación de piezas al
   pedido; `segundos_total` = desde que se creó hasta la última. Servido de
   golpe desde el almacén → proceso 0 (la web lo muestra como «de stock»).
10. **Nunca** se reparte stock por iniciativa propia fuera de estas reglas:
    `/almacen/repartir` (asignar) y `/reparto/expedir` (entregar) son
    órdenes del operario.

### E.7 Contabilidad (`contabilidad.py`, `importes.py`)

```
TARIFA general (subproducto) ─┐
o TARIFA de cliente            ├─► PEDIDO (copia precio y origen) ─► ALBARÁN (copia) ─► FACTURA (copia)
                               ┘
```

- `validar_precio_iva`: precio ≥ 0 («El precio no puede ser negativo.»), IVA
  entre 0 y 100.
- `registrar_precio(...)`: una fila en `historial_precios` **en la misma
  transacción** que el cambio (sin commit propio). Cambiar una tarifa general
  o de paquete y **guardar sin cambiar nada no ensucia** el historial.
- `precio_para(db, cliente, sub)` → `(precio, 'tarifa_cliente'|'tarifa_general')`;
  `precio_para_paquete` → `(precio, 'paquete_cliente'|'paquete_general')` o
  `(None, None)`.
- **Correcciones** (con **motivo obligatorio**, «Indica el motivo del cambio de
  precio.»): `PATCH /pedidos/{id}/precio` (solo si no se ha entregado nada ni
  está cerrado → si no 409; un componente de paquete con precio → 409 «…se
  corrige en el pedido del paquete…»; queda `precio_origen=manual`);
  `PATCH /pedidos-paquete/{id}/precio` (si no está entregado; pone sus
  componentes a 0 con el IVA del paquete); `PATCH /repartos/lineas/{id}/precio`
  (solo si el albarán **no está facturado** → si no 409 «anula la factura
  (rectificativa) antes…»; una línea `componente` → 400; en la línea de un
  paquete, el IVA pasa también a sus componentes). La cantidad entregada no se
  toca nunca.
- **Importes** (`importes.py`): `cuota_iva(base, pct) = signo · ((|base|·pct + 50) // 100)`
  (medio céntimo hacia arriba y simétrico: una rectificativa da exactamente el
  negativo; el `round()` de Python redondea 12,5 a 12 y no vale). `calcular(lineas)`
  suma las bases **por tipo de IVA** y redondea **una vez por tipo** (como una
  factura española); devuelve base, IVA, total y desglose por tipo. Albarán y
  factura usan la misma regla: cuadran al céntimo.
- **Emisores**: series de 2 a 8 letras o cifras, la de facturas distinta de la
  de rectificativas y **ninguna repetida** en otro emisor (409); el primero que
  se crea es el de por defecto; la serie **no se puede cambiar** si ya ha
  emitido facturas (409); una empresa desactivada no puede ser la de por
  defecto; al desactivar la de por defecto, pasa a otra activa. Razón social,
  CIF y dirección obligatorios.
- **Facturar** (`POST /facturas {cliente_id, emisor_id?, reparto_ids?, permitir_lineas_a_cero}`):
  emisor indicado (activo) o el de por defecto (si no hay: 400 «No hay ninguna
  empresa emisora por defecto…»); el cliente necesita **CIF y dirección** (400
  «Faltan datos fiscales de … : CIF, direccion (pestana Clientes).»);
  albaranes sin facturar de **ese** cliente (todos o los indicados; uno ajeno o
  inexistente → 404; uno ya facturado → 409 «Ya facturado: …»); sin albaranes →
  400. Líneas a 0 € (que no sean `componente`) → 400 «Hay lineas sin precio
  (0 EUR) en: …» salvo `permitir_lineas_a_cero`. Número
  `{serie}-{año}-{n:06d}` (contador por serie y año). Copia líneas, precios,
  IVA y los datos de las dos partes (dirección del cliente como
  `direccion, CP Poblacion (Provincia)`).
- Un albarán está facturado si alguna de sus líneas está en una factura
  **emitida de tipo factura** (una anulada lo libera).
- **Cobrar** (`POST /facturas/{id}/pagar {metodo_pago}`): solo una factura
  emitida, no cobrada (409 si no).
- **Anular** (`POST /facturas/{id}/anular {motivo}`): solo una factura
  emitida (no una rectificativa ni una ya anulada); motivo obligatorio; emite
  la **rectificativa** (serie de rectificativas de su emisor, mismas líneas
  con cantidad **negativa**, sin `reparto_linea_id`) y deja la original
  `anulada`: sus albaranes quedan libres para volver a facturarse ya
  corregidos. Los números nunca se reutilizan.
- Las salidas de factura rellenan `base/iva/total_centimos`, `desglose_iva`,
  `cobrada`, `albaranes` (números), `rectificada_por_numero`, `rectifica_numero`.
  Los de albarán, `factura_numero` y `paquetes` (nombres).

### E.8 Datos con los que nace la base (`sembrar_datos`, al arrancar)

Solo si cada cosa está vacía (una base con datos no se pisa):

- **Colores** (código, nombre, r, g, b, físico): `R Rojo 230,66,58 sí`,
  `G Verde 45,160,90 sí`, `B Azul 55,120,200 sí`, `Y Amarillo 225,196,40 no`,
  `M Magenta 190,60,180 no`, `C Cian 45,171,168 no`, `W Blanco 232,232,226 no`.
- **Productos** (nombre, código, LED, grupo): `Tornillos 100 R 0`,
  `Tuercas 200 G 0`, `Arandelas 300 B 0`.
- **Subproductos** (producto, nombre, código, céntimos): `100 Tornillo 10mm 2222 12`,
  `100 Tornillo 20mm A20X 18`, `200 Tuerca 10mm 3001 8`, `300 Arandela 10mm 4001 5`.
- **Paquetes**: `Paquete de 10` `P010` = 10×`1002222` + 10×`2003001` +
  10×`3004001`, precio 220 céntimos; `Paquete de 20` `P020` = 20×`100A20X` +
  20×`2003001` + 20×`3004001`, precio 550.
- **Clientes y usuarios**: los del fichero `Documentacion/UsuariosBBDDArranque.txt`
  (o `TALLER_DATOS_ARRANQUE`), con contraseña inicial `1111` y el catálogo
  indicado (todos los productos si no hay línea `Productos:`). Si el fichero
  no existe, tres empresas de ejemplo del código (con datos fiscales para poder
  facturar): «Ferreteria Ereno S.L.» `ERE` `B48123456` (usuarios `ere-admin`
  admin de Gernika y `ere-bermeo` normal de Bermeo; productos 100, 200, 300),
  «Suministros Mungia S.A.» `MUN` `A48765432` (`mun-admin`, `mun-larrabetzu`;
  100, 300) y «Construcciones Busturia S.L.» `BUS` `B48111222` (`bus-admin`;
  200). (Los tests usan estos, no el fichero.) Sus datos fiscales, tal cual:
  - ERE: `Calle Barrenkale 12`, `48300`, `Gernika-Lumo`, `Bizkaia`, `facturas@ereno.example`.
  - MUN: `Polígono Industrial Mungia, nave 4`, `48100`, `Mungia`, `Bizkaia`,
    `facturas@suministrosmungia.example`.
  - BUS: `Kalea Nagusia 3`, `48350`, `Busturia`, `Bizkaia`, `facturas@busturia.example`.
- Asignar código a clientes que no lo tengan y crear el índice único
  `ix_clientes_codigo` (si hay repetidos, avisar sin caerse).
- **Usuario `admin`** (`admin_sistema`, nombre «Administrador», contraseña
  `TALLER_ADMIN_PASSWORD` = `admin`) si no existe. (Migración antigua: un
  usuario `aladin` sin contraseña pasa a llamarse `admin` con contraseña.)
- `configuracion_almacen` id 1 con los dos interruptores a `True`.
- Si no hay emisores: pasar el antiguo de `configuracion_almacen` si lo hay;
  si no, uno de ejemplo «Virtual Robotic (empresa de ejemplo)», `B00000000`,
  «Calle de Ejemplo 1, 48000 Bilbao (Bizkaia)»,
  `facturacion@virtualrobotic.example`, por defecto.

**El fichero de clientes iniciales** (`datos_arranque.py`), un texto que se
edita a mano (y **no lleva contraseñas**):

```
Cliente:
    R.S.: Astilleros Murueta S.L.        <- razón social; empieza un cliente
    Cod.: MUR                            <- OPCIONAL (3 letras/cifras); sin él, sale de la razón social
    Cif : B48111222
    Dir.: Carretera Bermeo 34
    C.P.: 48333
    Pob.: Murueta
    Pro.: Bizkaia
    cor.: administracion@example.com
    Productos: 100, Arandelas             <- OPCIONAL (código o nombre); sin ella, TODOS
        sucursal admin -> Murueta         <- usuario mur-admin (administrador de la empresa)
        sucursal -> Bilbao   nombre -> Ana López   <- usuario mur-bilbao (nombre OPCIONAL)
        user normal-> bilbao2   sucursal -> Bilbao  <- forma antigua, usuario escrito a mano (sigue valiendo)
```

Reglas del lector: se ignoran líneas vacías, las que empiezan por `#` y lo que
no sea del formato (títulos, `Cliente:`, `Admin -> Admin.sistema`); las
etiquetas no distinguen mayúsculas (`r.s.`, `cif`, `dir.`, `c.p.`, `pob.`,
`pro.`, `cor.`, `cod.`, `productos`). Usuarios en minúsculas; sucursal con
mayúscula inicial si venía toda en minúsculas. Nombre completo por defecto:
`Administrador <sucursal>` u `Operario <sucursal>`. **Un error para el
arranque diciendo la línea** (código mal formado o repetido, usuario repetido,
cliente sin usuarios o sin `sucursal admin`, producto inexistente, una
sucursal antes de ningún cliente…): mejor eso que cargar a medias.
`cargar(db, iniciales, hash, solo_los_que_faltan=False, renombrar=False)`
devuelve un resumen (clientes/usuarios nuevos, omitidos, renombrados,
avisos); con `solo_los_que_faltan`, un cliente con el mismo CIF o un usuario
con el mismo nombre se omite; con `renombrar`, a los clientes existentes se
les pone el código del fichero y sus usuarios de la misma sucursal y rol pasan
al nombre nuevo.

Contenido del `Documentacion/UsuariosBBDDArranque.txt` del original (datos de
ejemplo, se pueden usar tal cual):

```
Usuarios BBDD Inicial

Admin -> Admin.sistema

Cliente:
    R.S.: Astilleros Murueta S.L.
    Cod.: MUR
    Cif : B48111222
    Dir.: Carretera Bermeo 34
    C.P.: 48333
    Pob.: Murueta
    Pro.: Bizkaia
    cor.: administracion@AstillerosMurueta.com

        sucursal admin -> Murueta
        sucursal -> Bilbao
        sucursal -> Barcelona
        sucursal -> Madrid

    R.S.: Suministros Ereño S.A.
    Cod.: ERE
    Cif : A48765432
    Dir.: Barrio akorda-bollar, 6
    C.P.: 48222
    Pob.: Ereño
    Pro.: Bizkaia
    cor.: compras@sumierno.es

        sucursal admin -> Ereño
        sucursal -> Navarra
        sucursal -> Valencia
        sucursal -> Bilbao

    R.S.: Ferreteria Irazabal S.A.
    Cod.: IRA
    Cif : B48123456
    Dir.: Iparraguire, 12 bajo
    C.P.: 48666
    Pob.: Gernika
    Pro.: Bizkaia
    cor.: almacen@irazabal.eus

        sucursal admin -> Gernika
        sucursal -> Alava
        sucursal -> Donosti

# Los usuarios salen solos del codigo del cliente y la sucursal:
#   'sucursal admin -> Murueta'  ->  usuario mur-admin
#   'sucursal -> Bilbao'         ->  usuario mur-bilbao
# Todos nacen con la contrasena 1111.
```

### E.9 Migraciones (`migraciones.py`)

No hay Alembic. `create_all()` crea las tablas que faltan pero nunca añade
columnas, así que `migrar_columnas_faltantes(engine, Base)` compara cada tabla
existente con el modelo y hace `ALTER TABLE "t" ADD COLUMN "c" <tipo> [NOT NULL]
[DEFAULT v]` de las **nuevas** (los booleanos como 0/1, textos entre comillas).
Una columna `NOT NULL` sin valor por defecto no se puede añadir: lo **avisa**
en el log. Además avisa de las columnas que el modelo admite nulas pero la
base tiene `NOT NULL` (SQLite no deja quitarlo: hay que recrear la base).
Nunca renombra, cambia tipos ni borra. Es idempotente. (Silenciar el aviso
`SAWarning` del ciclo clientes↔usuarios al ordenar las tablas.)

### E.10 Rutas (API) y quién puede usarlas

Sin sesión: `POST /login {username, password}` → `{token, usuario}` (usuario
en minúsculas y sin espacios; inactivo o clave mala → 401 «Usuario o
contrasena incorrectos.»); `POST /logout`; `GET /paleta_colores`
(`{codigo: {nombre, rgb "#rrggbb", fisico}}` de los colores activos);
`GET /version` → `{version}`; `GET /productos`, `GET /colores`,
`GET /subproductos[?producto_id]`, `GET /paquetes` (con componentes);
`POST /taller/cubo_clasificado`; `POST /taller/evento_produccion
{robot, color, tipo}` (tipo ∈ `led_encendido`, `agarre_falso`,
`limite_alcance`, `fallo_definitivo`, si no 400; robot en minúsculas,
`desconocido` si vacío).

| Ruta | Quién | Notas |
|---|---|---|
| `GET /me` | con sesión | |
| `POST/PATCH /productos` | `admin_sistema` | nombre no vacío y único, código 3 alfanuméricos único (se pasa a mayúsculas), LED existente, activo y libre, grupo 0..99; PATCH sin cambios → 400; el grupo nuevo solo afecta a pedidos nuevos |
| `POST/PATCH /colores` | `admin_sistema` | código **solo letras** (un «8» colado rompió el Loader), único; r/g/b 0..255 |
| `POST/PATCH /subproductos` | `admin_sistema` | producto activo; código 4 alfanuméricos único en su producto; precio/IVA válidos; cambiar el precio deja historial |
| `POST/PATCH /paquetes` | `admin_sistema` | al menos un componente (cantidad > 0, subproducto activo); precio opcional; cambiarlo deja historial `paquete_general` |
| `GET /usuarios` | `admin_sistema`; `admin_cliente` (solo los suyos) | |
| `POST /usuarios` | `admin_sistema`, `admin_cliente` | un `admin_cliente` no crea `admin_sistema` ni `empleado` (403) y se **fuerza** su propio cliente (sin error si intenta otro); `empleado`: sin cliente, usuario y contraseña obligatorios; otros roles (salvo admin_sistema) necesitan cliente; usuario vacío → `<codigo>-<sucursal>`/`<codigo>-admin`; repetido → 409 |
| `PATCH /usuarios/{id}` | quien pueda gestionar su cliente | un `admin_cliente` no asciende a `admin_sistema`/`empleado`; un usuario de cliente no pasa a empleado ni al revés (400); permisos solo los cambia `admin_sistema`; `activo=false` se audita como baja |
| `GET /clientes` | con sesión | los internos ven todos; el resto, solo el suyo |
| `POST /clientes` | `admin_sistema` | código dado (normalizado, 409 si repetido) o sugerido; crea también su primer usuario `admin_cliente` (`<codigo>-admin` si no se da) |
| `PATCH /clientes/{id}` | quien pueda gestionarlo | alta/baja y código solo `admin_sistema` (403); código repetido → 409; campos fiscales vacíos → nulo |
| `GET /clientes/{id}/productos` | gestor, el propio cliente o interno | |
| `POST /clientes/{id}/productos`, `DELETE /clientes/{id}/productos/{pid}` | `admin_sistema`, `admin_cliente` (el suyo) | devuelven el catálogo actualizado |
| `POST /pedidos {subproducto_id, cantidad_pedida}` | `admin_cliente`, `normal` | producto asignado a su empresa (si no 403), activo, cantidad > 0 |
| `POST /pedidos/multiple {lineas:[{subproducto_id, cantidad_pedida}], paquetes:[{paquete_id, cantidad}]}` | `admin_cliente`, `normal` | **la cesta**: se valida todo antes de crear nada (todo o nada); máximo 50 líneas; dos líneas del mismo subproducto se suman, lo de un paquete va aparte; un pedido por línea y uno por componente de cada paquete; con 2 o más pedidos, todos con el mismo `grupo_entrega` (el id del primero); luego servir y expedir |
| `POST /pedidos/paquete {paquete_id, cantidad}` | `admin_cliente`, `normal` | un paquete solo (los componentes comparten grupo) |
| `GET /pedidos`, `GET /pedidos/{id}` | `normal` los suyos; `admin_cliente` los de su empresa; internos todos; un empleado sin permisos → 403 | ordenados por fecha; con `stock_disponible`, `falta_fabricar`, `para_repartir` y tiempos |
| `PATCH /pedidos/{id} {urgente}` | Producción o `admin_cliente` (los suyos) | |
| `POST /pedidos/{id}/cancelar` | igual | solo `pendiente`; si no: 400 «Solo se puede cancelar un pedido 'pendiente' -- este esta 'X' (c/p ya fabricadas).» |
| `POST /pedidos/{id}/reclamar {numero_maquina, forzar, grupo_cadena}` | Producción | `numero_maquina ≤ 0` → 400; con `forzar` asigna sin mirar; si no, **UPDATE condicionado** (solo si su número está en {0, el mío, mi grupo>0}); si no casa → 409 «Este pedido ya esta asignado a la maquina nº N.» (evita que dos máquinas se queden el mismo pedido) |
| `POST /pedidos/{id}/liberar` | Producción | vuelve a 0 |
| `POST /pedidos/{id}/reprocesar` | Producción o `admin_cliente` (los suyos) | solo `completado`; crea un pedido **nuevo** idéntico (mismo cliente y usuario original), con el grupo **actual** del producto; subproducto/producto de baja o no asignado → 400/403 |
| `GET /taller/diagnostico?ventana_minutos=60` | Producción | por producto: LED encendidos por robot, agarres falsos, límites, fallos definitivos, piezas reales (en la ventana y totales) y estado: `critico` si hay fallo definitivo, `atencion` si hay límite o más agarres falsos que piezas, `ok`; más los 50 eventos recientes |
| `GET /stock` | con sesión | |
| `GET /movimientos_stock` | Producción | más recientes primero |
| `POST /almacen/repartir` | Producción | «Asignar stock»: sirve desde stock todos los pedidos abiertos por urgencia y antigüedad; auditoría y expedición automática; devuelve `{repartidos:[…]}` |
| `POST /almacen/ajustar {producto_id, cantidad}` | Producción | entrada `ajuste_manual` (cantidad > 0) |
| `POST /almacen/quitar {producto_id, cantidad}` | Producción | no deja bajar de 0: 400 «Solo hay N unidades disponibles.» |
| `GET /almacen/configuracion` | con sesión | |
| `PATCH /almacen/configuracion` | Producción | cambio parcial (no pisa el otro interruptor); `factor_piezas` ∈ {1,10,100,1000}; al **encender** la expedición automática, lo que ya esperaba `listo` sale en ese momento (los paquetes enteros) |
| `POST /reparto/expedir {pedido_ids: [..] o null}` | Producción | reparto manual: ids inexistentes → 404; con ids, se añade **todo su grupo** (un paquete se reparte entero); primero asigna el stock libre que los cubre (aunque el reparto automático esté apagado) y luego genera los albaranes; se puede repartir un pedido a medias (salvo paquetes) |
| `GET /repartos?cliente_id&limite=200`, `GET /repartos/{id}` | Producción, Contabilidad, `admin_cliente` (los suyos) | con importes y factura |
| `GET /audit` | `admin_sistema` | |
| `GET /clientes/{id}/tarifas`, `…/tarifas_paquete` | Contabilidad, `admin_cliente` (las suyas) | |
| `PUT/DELETE /clientes/{id}/tarifas/{sub}`, `…/tarifas_paquete/{paq}` | Contabilidad | solo pedidos nuevos; quitar vuelve a la general y deja historial |
| `GET /historial_precios?subproducto_id&cliente_id&limite=200` | Contabilidad | con `subproducto_descripcion` (`Producto · Variante (código)` o `Paquete: Nombre (código)`) y razón social |
| `PATCH /pedidos/{id}/precio`, `/pedidos-paquete/{id}/precio`, `/repartos/lineas/{id}/precio` | Contabilidad | ver E.7 |
| `GET /emisores` | Producción o Contabilidad | con `con_facturas` |
| `POST/PATCH /emisores` | `admin_sistema` | ver E.7 |
| `POST /facturas`, `POST /facturas/{id}/pagar`, `/anular` | Contabilidad | ver E.7 |
| `GET /facturas?cliente_id&limite`, `GET /facturas/{id}` | Contabilidad, `admin_cliente` (las suyas) | |

Todas las altas, bajas y cambios dejan auditoría.

**Páginas y ficheros**:

- `GET /` → `static/landing.html`; `GET /panel` → `static/panel.html`; los dos
  con `Cache-Control: no-cache, no-store, must-revalidate` (el navegador se
  quedaba con versiones viejas y un botón nuevo «no aparecía»).
- `/static` montado con `StaticFiles` + un *middleware* que pone el mismo
  `no-cache` a todo lo de `/static/` (un `i18n_panel.js` viejo en caché hizo
  creer que el selector de idioma no traducía).
- **`GET /static/img/{nombre}.mp4`** definida **antes** del montaje de
  `/static`: responde a `Range: bytes=…` con **206** y el trozo
  (`Accept-Ranges`, `Content-Range`; `bytes=-N` = los últimos N; fuera de rango
  → 416 con `Content-Range: bytes */total`; sin `Range` → el fichero entero con
  200). Safari no reproduce vídeos sin esto; el `StaticFiles` de esa versión lo
  ignora. Solo ficheros de esa carpeta (comprobar que la ruta resuelta no se
  sale).
- **Manuales**: `MANUALES = {"lanzar": REPO/LANZAR_PROYECTO.md, "taller":
  REPO/Taller_Administracion/README.md, "taller-tecnico":
  REPO/Taller_Administracion/DETALLE_TECNICO.md, "panda": REPO/Lab.Panda
  2.4/resumen_proyecto_panda.md}`. `GET /manual/{nombre}` → `manual.html`
  (404 si no existe el nombre); `GET /manual/{nombre}/raw?lang=es|en|eu` → el
  markdown (`text/markdown; charset=utf-8`), la versión `<nombre>.<lang>.md` si
  existe y si no el castellano; `GET /manual/{nombre}/assets/{ruta}` → ficheros
  relativos a la carpeta del manual (sin salirse de ella; 404 si no); si el
  destino es otro manual o una de sus traducciones, **redirige** a
  `/manual/<clave>`.

### E.11 El panel web (`static/panel.html`)

Una sola página (HTML + CSS + JavaScript sin librerías), tema oscuro:
`--bg #1c1c1c`, `--panel #262626`, `--cabecera #2a2a2a`, `--texto #eaeaea`,
`--titulo #f5c400`, `--borde #444`; colores de estado: pendiente `#aaa`,
en_proceso `#f5c400`, listo `#4aa3df`, completado `#2e9e3b`, cancelado
`#c0392b`; fila urgente `#3a1f1f`. Barra superior de la marca (fondo
`#14100c`, borde `#8c3717`): el **anagrama** (SVG de abajo, color cobre
`#b97a34`), «VIRTUAL ROBOTIC» en *Big Shoulders Display* 800, el subtítulo
«· Sistema de pedidos y almacén», el selector **ES/EN/EU** y `Ver. <versión>`
(de `/version`). Fuentes de Google: Big Shoulders Display y IBM Plex Mono.

Anagrama (se usa también en la portada y en el albarán impreso):

```html
<svg viewBox="0 0 148 260" aria-hidden="true">
  <rect x="50" y="64" width="32" height="10" fill="currentColor"/>
  <rect x="58" y="70" width="16" height="176" fill="currentColor"/>
  <polygon points="8,136 24,136 46,190 30,190" fill="currentColor"/>
  <polygon points="74,136 58,136 36,190 52,190" fill="currentColor"/>
  <rect x="8" y="136" width="16" height="110" fill="currentColor"/>
  <rect x="58" y="136" width="50" height="14" fill="currentColor"/>
  <rect x="94" y="136" width="14" height="48" fill="currentColor"/>
  <rect x="58" y="170" width="50" height="14" fill="currentColor"/>
  <polygon points="94,184 108,184 128,246 112,246" fill="currentColor"/>
</svg>
```

Reglas generales:

- **Sesión compartida con la portada** en `sessionStorage` (`taller_token`,
  `taller_yo`): quien entra desde la portada no vuelve a hacer login. Al
  cargar, si hay sesión guardada, `GET /me`; si falla, al login.
- `api(ruta, opciones)`: añade `X-Session-Token` y `Content-Type`; **cualquier
  401** borra la sesión y vuelve al login («Sesion no valida -- inicia sesion
  de nuevo.»); en error, lanza con el `detail` del servidor o el texto.
- **Nunca `confirm()`/`alert()`**: diálogo propio (`#dlg-fondo`, fuera del
  contenido que se repinta) con Aceptar/Cancelar, Intro y Escape. Firefox y
  Chrome permiten «impedir más diálogos» y entonces `confirm()` devuelve
  `false` en silencio (botones muertos sin aviso). (Para pedir un número o un
  motivo se usa `prompt()`.)
- **Todo texto que viene del servidor se escapa** (`escapeHtml`): un producto
  llamado `<b>x</b>` se ve como texto.
- Fechas: el servidor da UTC sin zona; se añade `Z` y se muestran en hora local.
- Euros: céntimos / 100 con formato `es-ES` y dos decimales.
- Pestañas que se repintan solas cada 4 s: Pedidos, Pedidos Taller, Reparto
  (sin perder filtros ni selecciones).

**Menú en dos niveles**: arriba tres **secciones** (Producción, Contabilidad,
Administración; se oculta si el rol solo tiene una) y debajo sus pestañas.
Cada sección recuerda su última pestaña.

| Pestaña (sección) | Quién la ve |
|---|---|
| Pedidos (Producción) | todos (un empleado, solo si tiene Producción) |
| Pedidos Taller, Reparto, Almacén, Diagnóstico (Producción) | `admin_sistema`, empleado con Producción |
| Resumen (Contabilidad) | `admin_sistema`, `admin_cliente`, empleado con Contabilidad |
| Tarifas, Facturación (Contabilidad) | `admin_sistema`, empleado con Contabilidad |
| Albaranes, Facturas (Contabilidad) | `admin_cliente` |
| Empresas, Productos, Subproductos, Paquetes, Colores, Clientes, Auditoría (Administración) | `admin_sistema` |
| Catálogo, Usuarios (Administración) | `admin_sistema`, `admin_cliente` |

Cada pestaña empieza con un recuadro de **ayuda en lenguaje llano** (fondo
`#241f14`, borde izquierdo amarillo) que explica qué se hace ahí.

- **Pedidos**: los que no son internos ven el formulario **de la cesta**:
  desplegable con dos grupos, *Productos* (`Producto · Variante (código
  completo)` de los productos de su catálogo) y *Paquetes* (`Paquete: Nombre
  (código) · precio -- lo que lleva`), cantidad y `+ Añadir a la cesta`; la
  cesta se guarda en `localStorage` (`taller_cesta_<id_usuario>`) hasta pedirla,
  se pueden quitar líneas o vaciarla, y `Pedir la cesta (N líneas)` llama a
  `POST /pedidos/multiple` (mensaje: un solo pedido, o «N pedidos que se
  entregarán juntos, en un solo albarán…»). Tabla **Pedidos activos** con
  filtros (cliente, producto, «En almacén: cubre todo / cubre parte / sin
  stock», estado) y **Histórico**. Columnas: ID, Cliente (internos), Quién pide
  (nombre / sucursal; no para `normal`), Producto · Variante, Color (bolita del
  LED o «sin LED»), Cantidad, Precio ud. (con origen si no es la general; en un
  paquete con precio, «📦 en el paquete (precio)»; `✎` para corregir con
  Contabilidad), Completado, Repartido, En almacén (`cubre todo (n)` / `cubre a
  de b`), Estado, Máquina (con Producción: número editable 0-99 + `✓` que
  reclama **forzando** + `Liberar`), Tiempo («de stock» si fue 0), Urgente
  (casilla), Creado y acciones (`Cancelar` si está pendiente; en el histórico,
  `Volver a procesar` si está repartido, con mensaje según quede).
- **Pedidos Taller**: lo que **falta fabricar** (`pendiente`/`en_proceso` con
  `falta_fabricar > 0`, urgentes primero): pedido, listas, cubre el stock,
  **falta fabricar**, máquina, tiempo, urgente, cancelar.
- **Reparto**: los dos interruptores («Reparto automático (asignar el stock a
  los pedidos)» y «Reparto automático de lo listo (entregar y emitir
  albarán)»), el botón `Asignar stock a pedidos pendientes`, la tabla
  **Pendientes de reparto** (`para_repartir > 0`, con casillas, marcas «📦
  paquete» y «🛒 entrega conjunta», botones `Repartir`, `Repartir seleccionados
  (n)` y `Repartir todo`) y **Albaranes emitidos**.
- **Albaranes** (tabla común): número, fecha, cliente, líneas agrupadas por
  paquete (con precio o «sin precio» y `✎` si no está facturado y se tiene
  Contabilidad), base, IVA, total, factura, salida (automática/manual) y
  `Ver / imprimir`.
- **Documento imprimible** (albarán o factura): se abre en una ventana nueva
  lista para imprimir o guardar como PDF (botón «Imprimir / guardar PDF», que
  no sale al imprimir). Albarán: anagrama + «ALBARÁN número», fecha, paquetes,
  «Facturado en … / Sin facturar», datos del emisor por defecto (si el usuario
  puede leerlos), «Entregado a» con código y CIF, líneas (paquete en negrita y
  sus componentes con «incluye:»), base/IVA/total si hay precios y «Recibí
  conforme: ____». Factura: «FACTURA» o «FACTURA RECTIFICATIVA» (y a cuál
  rectifica y el motivo), sello rojo girado «ANULADA (RECT-…)» si lo está,
  emisor, cliente, líneas con su albarán, desglose de IVA por tipo, base, IVA,
  **TOTAL**, «Cobrada el …» si lo está, y la nota «esta es la factura de
  producción, pero todavía le faltan conceptos que llevaría una factura real
  (transporte, envío, recargos u otros gastos)». Con **factor de piezas** > 1
  se multiplican al pintar cantidades e importes (no el precio unitario) y se
  añade una nota; **nunca** cambia nada en la base de datos.
- **Resumen** (contable): tarjetas (Facturado este mes, Facturado en el año
  con IVA repercutido, Cobrado en el año, Pendiente de cobro, Entregado sin
  facturar con aviso de líneas sin precio); pendiente de cobro por antigüedad
  (hasta 30 días, 31-60, más de 60); para internos, desglose **por cliente**;
  botón **«Descargar libro de facturas (CSV)»** (separador `;`, coma decimal,
  BOM UTF-8, columnas Número, Tipo, Fecha, Empresa emisora, Cliente, CIF, Base,
  IVA, Total, Estado, Cobrada, Fecha cobro, Método cobro, Rectifica a). Solo
  cuentan las facturas **emitidas de tipo factura**.
- **Tarifas**: elegir cliente; tabla de subproductos activos (tarifa general,
  IVA y un campo «Tarifa de este cliente (€)» con Guardar/Quitar: vacío = la
  general) y otra igual de **paquetes**; debajo, el historial de cambios de
  precio (fecha, ámbito, pieza, cliente, antes, después, motivo).
- **Facturación**: aviso del **factor de piezas** (×1/×10/×100/×1000, «solo
  demo»); «Facturar como» (empresa emisora, por defecto la marcada) y enlace a
  Empresas; albaranes **pendientes de facturar agrupados por cliente** con
  casillas por albarán, por cliente y «Seleccionar todos» (casillas a medias
  si hace falta), `Facturar todo lo pendiente (n)` por cliente y `Facturar
  seleccionados (n)` (una factura por cliente); si el servidor rechaza líneas a
  0 €, se pregunta si facturarlas igualmente; tabla de facturas con estado
  (emitida · sin cobrar / cobrada / anulada / rectificativa), `Cobrar` (pide
  método, «transferencia» por defecto) y `Anular` (pide motivo).
- **Facturas** (`admin_cliente`): sus facturas, solo lectura, con Ver / imprimir.
- **Empresas**: alta (razón social, CIF, dirección, email, series) y tabla
  editable (series bloqueadas si ya facturó, radio «por defecto», casilla activa).
- **Productos**: alta y tabla editable (nombre, código, LED en un desplegable
  con «● Nombre (código) · solo LED -- en uso», el desplegable coloreado con el
  color elegido; grupo cadena con su explicación; activo).
- **Colores**: alta y tabla editable (muestra, código solo letras, nombre,
  R/G/B, físico, activo).
- **Subproductos**: alta (producto, nombre, código de 4, precio €, IVA %) y
  tabla editable con el código completo calculado.
- **Paquetes**: alta con filas de componentes (añadir/quitar), precio (vacío =
  suma) e IVA; tabla editable.
- **Catálogo**: el admin elige cliente; casillas por producto activo (asignar o
  quitar al momento). Un `admin_cliente` ve el suyo y puede editar su razón
  social y CIF.
- **Usuarios**: alta (usuario vacío = automático, nombre, rol —«Empleado de la
  empresa» solo para el admin, que muestra casillas Producción/Contabilidad y
  oculta cliente y sucursal—, cliente, sucursal, contraseña) y tabla editable
  (rol, permisos, sucursal, activo, nueva contraseña).
- **Clientes**: alta (razón social, código de 3, CIF, dirección, C.P.,
  población, provincia, email de facturación, usuario del primer admin —vacío
  = `código-admin`—, nombre y contraseña) y tabla editable.
- **Almacén**: stock por producto ordenado por código, con una fila gris por
  **variante pendiente** («Tornillo 10mm: 3 pendiente(s)»), cantidad y botones
  `Añadir a stock` / `Quitar de stock`; tabla de movimientos.
- **Diagnóstico**: ventana (15 min, 1 h, 6 h, 1 día); por producto, una
  tarjeta con su estado y barras (piezas reales, LED Loader, LED Sorter,
  agarre falso, límite de alcance, fallo definitivo) y el total histórico;
  últimos eventos.
- **Auditoría**: fecha, tabla, registro, acción, usuario, detalle.

**Idiomas del panel**: `t(clave, textoEs, vars)` busca en
`window.VR_I18N_PANEL[idioma][clave]` (fichero `static/i18n_panel.js` con los
bloques `en` y `eu`) y si no existe usa el castellano; `{nombre}` se sustituye
por `vars`. El idioma se guarda en `localStorage` (`vr_idioma`) y al
cambiarlo se repinta la cabecera, el menú y la pestaña activa. **Todo** el
panel debe estar en los tres idiomas.

### E.12 La portada (`static/landing.html`) y la copia suelta (`Virtual_Robotic/index.html`)

Página de presentación del proyecto, **en tono de aficionado** («Un
aficionado, dos brazos robóticos simulados y un almacén que se lleva solo.
Nada de esto es una empresa de verdad»), que además hace de **manual de
entrada**. Diseño claro/oscuro (según el sistema): tokens
`--bg #eef0e8`, `--bg-elevated #fff`, `--fg #16211f`, `--fg-muted #55655f`,
`--accent-brick #a8461f`, `--accent-brick-strong #8c3717`,
`--accent-copper #b97a34`, `--accent-water #2f645f`; en oscuro `--bg #101817`,
`--bg-elevated #182322`, `--fg #eee7da`, `--fg-muted #9fb0ac`,
`--accent-brick #c9683c`, `--accent-copper #d69a55`, `--accent-water #5b9a92`.
Fuentes Big Shoulders Display (títulos en mayúsculas), Archivo (texto) e IBM
Plex Mono (etiquetas). Aparición suave de las secciones al hacer scroll
(`IntersectionObserver`, con alternativa sin él).

Secciones: menú (Origen, Cómo funciona, Cómo está hecho, Juega con él, Código,
selector ES/EN/EU y botón **Entrar**); portada «VIRTUAL ROBOTIC» con
«Proyecto personal de robótica · Ría de Gernika» y «Construido con Claude Code
(Anthropic)»; **Origen** («De la curiosidad al taller entero»); **Cómo
funciona** («Tres piezas de una misma celda»: la captura `webots_cell.jpg`,
los dos vídeos `celda_trabajando_1/2.mp4` con `autoplay muted loop
playsinline` y su póster `.jpg`, y tres tarjetas: *Dos brazos que cogen y
clasifican*, *Reposición sin intervención*, *Almacén y trazabilidad*);
**Cómo está hecho** (Webots + ROS 2, Verificación por posición real, FastAPI +
SQLite, Dos Raspberry Pi Pico —opcionales, con la foto `pico_hardware.jpg` y
por qué están: el proyecto empezó sin robot de verdad y se quería tocar algo
físico— y enlaces a los manuales `/manual/lanzar`, `/manual/taller`,
`/manual/panda`); **Juega con él** (1 levanta el panel con `docker compose up
-d --build`, 2 entra con `admin`/`admin` o crea un normal que entra con
`1111`, 3 la celda es opcional); pie **Tócalo tú mismo** con lo que hace falta
para instalarlo en Linux y en Windows (Windows: la web con Docker Desktop y
Git; los robots con Webots R2025a instalado en Windows y `arrancar_windows.bat`;
Windows dentro de VirtualBox **no** funciona) y el enlace al repositorio si el
usuario tiene uno.

**Entrar** abre un diálogo de login (usuario `admin`, contraseña): en
`landing.html` es **real** (`POST /login`, guarda la sesión en
`sessionStorage` y va a `/panel`; si ya hay sesión, el menú muestra el usuario
y «Salir»). La copia `Virtual_Robotic/index.html` es la misma página para
abrir con doble clic sin Docker: rutas relativas (`img/…`, `../LANZAR_PROYECTO.md`),
botón «Producción» y un **cerrojo de cortesía** (`admin`/`admin` escrito en
el propio HTML, no es seguridad; lo dice el diálogo) que enlaza a
`http://localhost:8000`. **Si se toca una, se replica en la otra.**

Traducción: cada elemento con `data-i18n="clave"` (o `data-i18n-alt`,
`-title`, `-aria-label`) se sustituye con `window.VR_I18N[idioma][clave]`
(`i18n_landing.js`, idéntico en las dos copias); `window.VR_tr(textoEs)` para
textos creados por JavaScript; idioma en `localStorage` (`vr_idioma`).

### E.13 Manuales en la web y guía de administración

- `static/manual.html`: la misma estética que la portada, migas de pan
  («Principal → …»), selector ES/EN/EU; pide `/manual/{nombre}/raw?lang=…` y lo
  pinta con **marked** (`https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js`),
  reescribiendo las imágenes relativas para que pasen por
  `/manual/{nombre}/assets/…`.
- `static/guia_administracion.html` (se abre en `/static/guia_administracion.html`):
  «Cómo se administra esto», contado con un ejemplo (dar de alta a
  «Ferretería Sur»): los tres tipos de usuario, el ejemplo paso a paso, el flujo
  completo, quién pide / quién fabrica / piezas metidas a mano y una tabla de
  quién puede hacer qué. Traducida con `i18n_guia.js`.

### E.14 Tests automáticos (obligatorios en la fase 2)

pytest + `TestClient`, en `Taller_Administracion/tests/`. Se lanzan dentro del
contenedor:

```bash
docker exec taller_admin_api pip install -r requirements-dev.txt     # una vez
docker exec -w /workspace taller_admin_api python -m pytest -v
```

`conftest.py` — **muy importante**: fija las variables **antes** de importar
nada de `app` (el motor de base de datos se crea al importar `database.py`; si
no, los tests escribirían en la base **real**): `TALLER_DB_PATH` a un fichero
temporal, `TALLER_MASTER_PASSWORD=1111`, `TALLER_DATOS_ARRANQUE` a un fichero
que no existe (se usan los clientes de ejemplo del código, no el que edita el
usuario), `TALLER_BARRIDO_SEGUNDOS=0` (el barrido se prueba llamando a
`barrer_stock()` a mano) y `TALLER_DEV_MODE=true`. Fixture `client`: `drop_all`
+ `create_all` y `with TestClient(app)` (dispara el sembrado real). Borrar la
carpeta temporal al final. Ayudantes para loguearse y crear un cliente con su
usuario.

Qué deben comprobar, como mínimo (el original tiene ~260 tests):

- **Login**: admin con su clave real; la maestra vale para `normal` siempre y
  para admins solo en modo desarrollo; usuario sin distinguir mayúsculas;
  clave mala / usuario inexistente → 401; sin token o token basura → 401;
  logout invalida; usuario de baja no entra.
- **Productos, colores, subproductos, paquetes**: el sembrado (3 productos,
  7 colores, paquete de 10); altas con y sin LED; grupo cadena por defecto 0,
  editable y con rango; LED, nombre y código no repetibles; códigos inválidos
  (producto 3, subproducto 4, color solo letras, también al editar); baja
  lógica; PATCH vacío → 400; solo el admin crea.
- **Clientes y usuarios**: crear cliente crea su admin; un `admin_cliente` no
  ve otros clientes ni crea admins ni cuela usuarios en otra empresa (se fuerza
  la suya, sin 403) ni asciende; solo el admin da de alta/baja un cliente;
  usuario repetido → 409; un normal no lista usuarios.
- **Códigos de cliente**: normalizar, sugerir (primera palabra con
  significado, sin repetir, rellenando), `slug`, `usuario_de`; alta sin código,
  con código (primer usuario `código-admin`), usuario escrito a mano, código
  repetido 409 y mal formado 400, dos clientes sin código no chocan, solo el
  admin cambia el código, usuario sin nombre = código + sucursal, misma
  sucursal dos veces 409, sin nombre ni sucursal 400.
- **Fichero de arranque**: lectura completa, minúsculas y mayúscula inicial,
  nombre automático, productos por defecto o los de su línea, lo que no es del
  formato se ignora, errores con mensaje y línea, fichero inexistente → None,
  **el fichero real del repositorio es válido**, base vacía sembrada con él,
  contraseña inicial 1111, sin volver a sembrar si ya hay clientes,
  `cargar_arranque` añade lo que falta y es idempotente, `--renombrar`.
- **Pedidos**: crear; producto no asignado → 403; cantidad ≤ 0 → 400; producto
  de baja; alcance por rol; urgente; cancelar solo pendiente y con el mensaje
  completo; no cancelar dos veces; reprocesar (solo completado, 404, sesión,
  permisos, producto de baja 400); `numero_maquina` inicial = grupo del
  producto; reclamar libre, ya de otra 409, idempotente, forzar, del grupo (pasa
  a mi número), de otro grupo 409, número 0 → 400; liberar; un admin_cliente no
  reclama.
- **Cesta y paquetes**: un pedido por línea con el mismo grupo; sale en un solo
  albarán cuando está entera; si el almacén ya la cubre sale al pedirla; una
  línea sola = pedido normal; líneas iguales se suman; dos cestas = dos
  albaranes; todo o nada; validaciones; solo piden cliente y normal; productos
  y paquete juntos en un albarán; paquete con producto no asignado no crea
  nada; paquete entero en un albarán, esperando como `listo` mientras está a
  medias; la cantidad del paquete multiplica; repartir un componente reparte el
  paquete; activar la expedición saca paquetes completos y no los a medias.
- **Paquetes con precio**: el precio se congela; el albarán lleva la línea del
  paquete y sus componentes sin precio; dos paquetes se cobran dos veces; el IVA
  del paquete manda; tarifa de paquete por cliente y quitarla; permisos;
  historial; sin precio = suma agrupada; a mano no se entrega un paquete a
  medias; en una cesta los sueltos salen a medias pero el paquete espera;
  correcciones de precio (pedido de paquete sí, componente no, línea del paquete
  sí); la factura lo lleva igual; los componentes a 0 no bloquean; la
  rectificativa es el negativo exacto.
- **Almacén y reparto automático**: `cubo_clasificado` sin pedidos solo suma
  stock; color inválido; resolución por `producto_id` y por `pedido_id` (producto
  sin LED); aplica al más antiguo; completa al llegar a la cantidad; con el
  reparto apagado se queda en stock; pedido nuevo servido al instante si hay
  stock (y no si el reparto está apagado); pieza de otra máquina no completa mi
  pedido; va al pedido de su máquina aunque haya uno más antiguo; puede ir al
  de su grupo y lo pasa a su número; `pedido_id` de otra máquina se ignora; sin
  máquina, como siempre; urgente antes que antiguo; ajustar/quitar stock (no
  bajar de 0, solo producción); dos pedidos del mismo color no se solapan el
  stock; repartir a mano cumple lo que prometía `stock_disponible`.
- **Barrido**: el caso del 9 de 10; la pieza de otra máquina no completa al
  llegar pero el barrido sí; no asigna si no cubre entero; un pedido sin cubrir
  no bloquea a los siguientes; urgencia y antigüedad; apagado no hace nada;
  idempotente; con expedición manual deja `listo`; paquete sale entero;
  auditoría.
- **Reparto y albaranes**: por defecto todo automático y el pedido acaba
  repartido con albarán; expedición manual deja `listo`; expedir a mano genera
  albarán; un albarán por cliente con números correlativos; entrega parcial y
  luego el resto; activar la expedición saca lo que esperaba; un `listo` no
  recibe más piezas; repartir un pedido cubierto por stock lo asigna y entrega;
  asignar con expedición manual deja `listo`; pedido nuevo con stock y
  expedición automática nace repartido; precio e IVA congelados; la
  descripción del albarán no cambia si se renombra; precio negativo o IVA fuera
  de rango; configuración parcial; permisos por rol; pedido inexistente 404;
  datos fiscales; cancelado no se reparte; IVA redondea el medio céntimo arriba.
- **Contabilidad**: tarifa de cliente solo en sus pedidos nuevos; quitarla;
  negativa rechazada; permisos; historial (general, cliente, baja; guardar sin
  cambiar no ensucia); corregir precio de pedido pendiente (queda manual, motivo
  obligatorio, no si ya entregado); corregir línea de albarán no facturada y no
  facturada; factura con líneas, datos fiscales e importes; faltan datos → no;
  no facturar dos veces; albarán de otro cliente 404; líneas a 0 salvo
  permiso; dos tipos de IVA desglosados; factura y albarán cuadran al céntimo;
  la factura conserva los datos aunque se edite el cliente; anular emite el
  negativo exacto; el albarán queda libre y se refactura corregido; no anular
  dos veces ni una rectificativa ni sin motivo; series independientes; cobrar
  y no dos veces; no cobrar anulada; el cliente ve solo las suyas; el normal no
  ve facturas; emisores (ejemplo por defecto, numeración propia, por defecto
  usado, desactivado no factura, sin por defecto no factura, desactivar pasa el
  por defecto, series no se repiten, serie bloqueada con facturas, campos
  obligatorios, editar no cambia facturas emitidas, solo admin, emisor antiguo
  migrado).
- **Empleados**: alta sin cliente y con permisos; solo producción, solo
  contabilidad, las dos; producción gestiona pedidos de cualquier cliente y
  contabilidad no; no hacen pedidos; sin permisos no ven nada; cambiar permisos
  hace efecto; necesitan usuario y contraseña; la maestra no les vale fuera de
  desarrollo; un admin_cliente no crea ni toca empleados; un usuario de cliente
  no pasa a empleado.
- **Diagnóstico y auditoría**: tipos de evento; solo producción; estados ok,
  crítico, atención; la ventana excluye lo viejo; altas y cancelaciones dejan
  rastro; solo el admin ve la auditoría.
- **Tiempos**: sin movimientos → None; proceso = primera a última pieza;
  total desde la creación; servido de golpe → 0; varios pedidos independientes.
- **Migraciones**: añade columnas con su valor por defecto y conserva datos;
  idempotente; no toca tablas inexistentes; avisa de la columna que el modelo
  admite nula y la base no.
- **Vídeo con Range**: sin Range entero y con `Accept-Ranges`; primera sonda
  de Safari (`bytes=0-1` → 206); trozo abierto y sufijo; fuera de rango (416)
  e inexistente (404).

---

## F. Varias líneas de producción y Windows

Una **línea** (o cadena) = un Webots con sus dos robots, su contenedor ROS 2 y
su panel. Todas trabajan para **la misma web de pedidos**. Cada una necesita
su **Nº Máquina** propio (que no se repita) para que el reparto no se cruce;
el **Grupo Cadena** sirve para que un producto solo lo fabriquen las líneas de
un grupo (ejemplo: los clavos en el grupo 80; buena práctica: máquinas 1-49 y
grupos 50-99, para no confundir números).

Cómo encaja con la web: un pedido nace con `numero_maquina = grupo_cadena del
producto` (0 = libre). El panel de cada línea solo ve los pedidos con su
número o su grupo, los **reclama** antes de fabricar (UPDATE condicionado: dos
líneas no se quedan el mismo) y el Sorter avisa de cada pieza con su número y
su grupo. Un pedido reclamado por una línea que se apaga queda suyo hasta que
alguien pulse **Liberar** en la web.

### F.1 La plantilla de la línea 2 (`.devcontainer2/docker-compose.yml`, Linux)

Igual que la línea 1 (mismas imágenes, **mismo `../ros2_ws`** y un solo
`colcon build` para todas), cambiando solo:

- Contenedores `webots_panda_sim24_linea2` y `ros2_panda_dev24_linea2`
  (también `hostname`), red `panda_ros_net_linea2` (con el alias
  `host.docker.internal` para Webots), `ROS_DOMAIN_ID=32` en los dos servicios.
- Webots monta `../worlds` **`:ro`** (dos Webots abriendo el
  mismo mundo podrían pisarse al guardar; **no** montar `../controllers`, que
  este proyecto no tiene: Docker crearía una carpeta vacía) y **la misma caché de texturas** de la
  línea 1 (`../.devcontainer/webots_asset_cache`).
- `ros2_app` **sin `ports:`** (el 5002 del botón de la Pico W ya lo publica la
  línea 1: publicarlo dos veces haría fallar el arranque) y **sin `devices:`**
  (la línea 2 no tiene Pico USB).
- `docker-compose.windows-sim.yml` de la línea 2 (solo prueba): Webots con
  `--port=1235` y `ports: 1235:1235`; `ros2_app` con `WEBOTS_PORT=1235` y los
  dos `extra_hosts`.

### F.2 `crear_linea.sh` (Linux)

`crear_linea.sh <N> [numero_maquina] [url_taller_administracion] [grupo_cadena]`
(`-h`/`--help` muestra el uso y ejemplos). `set -euo pipefail`.

- Valida: N entero entre **3 y 69** (1 y 2 ya existen; `ROS_DOMAIN_ID = 30+N`
  debe quedar válido); máquina y grupo entre 0 y 99.
- Si `Lab.Panda 2.4/.devcontainerN` **ya existe**, no copia ni renombra nada:
  la vuelve a arrancar tal cual («volver a entrar»). Si no: copia
  `.devcontainer2`, **borra** su `docker-compose.windows-sim.yml` (es solo de la
  línea 2) y con `sed` cambia `linea2` → `lineaN` y `ROS_DOMAIN_ID=32` →
  `ROS_DOMAIN_ID=30+N`.
- `generar_version.sh` (si falla, avisar: el panel pondrá `sin-version`).
- Plantilla de vista de Webots (como en `arrancar_todo.sh`), `xhost`, y
  `docker compose up -d --build` en la carpeta nueva.
- Compilar dentro de `ros2_panda_dev24_lineaN` (si ya compiló otra línea es
  inmediato; sin esto, en una instalación limpia el panel fallaba con
  `setup.bash: No such file or directory`).
- Si se pasan máquina/URL/grupo: escribirlos en
  `/workspace/config_maquina_<hostname del contenedor>.json` con un pequeño
  Python dentro del contenedor (actualizando solo esas claves).
- Mismas funciones `esperar_webots` / `lanzar_celda` (reinicio del
  contenedor) / `esperar_controladores` y el mismo reintento que
  `arrancar_todo.sh`, con los nombres de la línea N; al final abre su panel.

### F.3 Windows

**Topología**: Webots R2025a **instalado en Windows** (el de Docker necesita una
pantalla de Linux y muere con «could not connect to display»); en Docker solo
ROS 2, que llega a Webots por `host.docker.internal` (Docker Desktop lo apunta
al propio Windows); el panel se ve en el navegador por noVNC. No hace falta
tocar el código: todos los controladores son `<extern>` por TCP, y la variable
`WEBOTS_SHARED_FOLDER` solo hace que el conector de ROS 2 use TCP hacia
`host.docker.internal` (de paso evita un fallo conocido del conector con WSL,
que está en la otra rama del código). Las Pico por USB no llegan al contenedor
en Windows (el LED del Loader no funciona; el resto sí).

**`.devcontainer/docker-compose.windows.yml`** (fichero completo, no un
añadido: el otro trae el Webots de Linux, X11 y la GPU):

```yaml
# Varias cadenas en el mismo Windows: arrancar_windows.bat pone estas variables
# segun el numero de cadena N (sin ellas, las de la cadena 1):
#   LINEA_SUFIJO  ""   / "_lineaN"   nombre del contenedor
#   LINEA_DOMINIO 31   / 30+N        ROS_DOMAIN_ID
#   LINEA_WEBOTS  1234 / 1233+N      puerto de SU Webots
#   LINEA_PANEL   6080 / 6079+N      panel en el navegador
#   LINEA_BOTON   5002 / 5001+N      boton de parada de la Pico Wi-Fi
services:
  ros2_app:
    build:
      context: ../ros2_app
      dockerfile: Dockerfile
    image: devcontainer-ros2_app          # la misma imagen para todas las cadenas
    container_name: ros2_panda_dev24${LINEA_SUFIJO:-}
    hostname: ros2_panda_dev24${LINEA_SUFIJO:-}
    environment:
      - ROS_DOMAIN_ID=${LINEA_DOMINIO:-31}
      - WEBOTS_PORT=${LINEA_WEBOTS:-1234}
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
      - WEBOTS_SHARED_FOLDER=/tmp/webots_shared:/tmp/webots_shared   # solo hace de interruptor TCP
      - DISPLAY=:99
    volumes:
      - ../ros2_ws:/workspace
    ports:
      - "${LINEA_BOTON:-5002}:5002"
      - "127.0.0.1:${LINEA_PANEL:-6080}:6080"   # solo en este equipo: el panel no pide clave para verse
    extra_hosts:
      - "taller_host:host-gateway"
      - "host.docker.internal:host-gateway"
    stdin_open: true
    tty: true
    command: bash
```

**`arrancar_windows.bat [N] [numero_maquina]`** (doble clic = línea 1; CRLF;
`setlocal`, `chcp 65001`, `cd /d "%~dp0"`):

1. Validar N de 1 a 9. Línea 1: sufijo vacío y proyecto Compose `devcontainer`;
   línea N: sufijo `_lineaN` y proyecto `devcontainerNwin`. Calcular
   `LINEA_DOMINIO=30+N`, `LINEA_WEBOTS=1233+N`, `LINEA_PANEL=6079+N`,
   `LINEA_BOTON=5001+N`; `PANEL_URL=http://localhost:<panel>/vnc.html?autoconnect=1&resize=scale`.
2. `docker info` (si no responde: «Abre Docker Desktop, espera a Engine
   running…»).
3. `docker compose up -d --build` en `Taller_Administracion` (una sola web).
4. `docker compose -p <proyecto> -f docker-compose.windows.yml up -d --build`.
5. Compilar el paquete dentro del contenedor. Si se dio Nº de máquina,
   escribirlo en `config_maquina_<hostname>.json` con `python3 -c`.
6. Webots: si su puerto ya contesta (`timeout 1 bash -c '</dev/tcp/host.docker.internal/<puerto>'`
   desde el contenedor), no abrir otro. Si no, buscar `webotsw.exe` en
   `%LOCALAPPDATA%\Programs\Webots\msys64\mingw64\bin\` y en
   `%ProgramFiles%\Webots\msys64\mingw64\bin\`, copiar la plantilla de vista a
   `worlds\.panda_industrial_cell.wbproj` y lanzar
   `start "" webotsw.exe --mode=realtime --port=<puerto> "<mundo>"` (si no se
   encuentra, decir cómo abrirlo a mano).
7. Esperar hasta **300 s** a que el puerto conteste (la primera vez baja
   texturas y el Firewall de Windows puede preguntar: **permitir** en redes
   privadas) y luego 10 s más (el puerto se abre antes de acabar de cargar el
   mundo).
8. Lanzar la celda con **hasta 3 intentos**: `docker restart` del contenedor y
   `ros2 launch` en segundo plano con log; contar `Controller successfully
   connected` hasta 6 (máximo 90 s); si aparece `Giving up` (un controlador se
   rindió porque llegó antes que los robots), esperar 15 s y relanzar.
   **Cuidado con un fallo del original**: la etiqueta `:ctrl_listos` está
   **duplicada** en su `.bat` y el `goto` salta a la primera, que vuelve a
   esperar hasta 120 vueltas y acaba diciendo «AVISO: solo han conectado 6 de
   6». Escríbelo bien: al llegar a 6, decir «Listo: 6 controladores
   conectados.» y seguir; al agotar los 3 intentos, avisar con el log y seguir
   al panel.
9. `docker exec -d <contenedor> panel_web.sh`, esperar 8 s y abrir la URL del
   panel en el navegador. Resumen final (panel, web, recordar poner nombre y
   Nº de máquina a una línea que no sea la 1, `cerrar_windows.bat`) y `pause`.

**`crear_linea_windows.bat`**: pregunta el número de línea (2 a 9; Intro vacío
= salir) y el Nº de máquina (0 a 99; Intro = no tocarlo), validando, y llama a
`arrancar_windows.bat N [máquina]`.

**`cerrar_windows.bat [N]`** (sin N: todas las líneas, sus Webots y la web;
con N: solo esa línea y su Webots):

- No usa el compose: busca contenedores con nombre `ros2_panda_dev24` o
  `ros2_panda_dev24_lineaK` (K una cifra de 2 a 9; cualquier otro nombre no es
  nuestro), hace `docker compose -p <devcontainer | devcontainerKwin> down` y,
  si el contenedor sigue vivo, `docker rm -f`.
- Cierra el Webots de cada línea: el proceso que escucha en el puerto
  `1233+K` (`netstat -ano -p tcp | findstr LISTENING`), **solo si ese proceso
  es Webots** (`tasklist`), con `taskkill /f`.
- Sin N, `docker compose down` de la web. Si Docker no responde: «ya está todo
  parado».

**Rendimiento medido**: en un portátil de 2012 la simulación iba a 0,15x-0,22x
(no por Webots, sino por los mensajes entre Webots y Docker, sobre todo las
imágenes de las cámaras); con las cámaras a 10 imágenes/s, un portátil moderno
con Windows 11 va a 1,0x y saca un cubo cada ~24 s; con **4 líneas** a la vez,
cada una a 0,35x-0,5x (un cubo cada ~57 s) y CPU/GPU al 77/73 %: **4 es un
buen techo**.

**Líneas en otros ordenadores**: por ejemplo la web y una línea en Windows y
dos líneas en una VM Linux, creadas con
`./crear_linea.sh 3 33 http://IP_DEL_WINDOWS:8000`. El Firewall de Windows
debe dejar entrar al 8000. **Trampa real**: al **clonar** una máquina virtual
se clonan también sus `config_maquina_*.json`, con el mismo Nº de máquina; hay
que cambiarlo en cada línea (si no, solo trabaja una). Y los productos en
grupo 0 los puede coger cualquiera.

---

## G. Documentación que hay que escribir (fase 12)

Todo en **lenguaje de aficionado** (explicar las palabras técnicas la primera
vez, frases cortas, ejemplos). Primera línea `_Última modificación: …_`.
Selector de idioma arriba (`**Idioma:** Español · [English](X.en.md) ·
[Euskara](X.eu.md)`) en los que van traducidos. El euskera, con el aviso de
que conviene revisarlo un hablante nativo.

| Fichero | Contenido |
|---|---|
| `README.md` (+EN, EU) | Qué es (proyecto personal de aficionado, no una empresa), captura y los dos vídeos, las tres partes (celda, web, Pico opcionales), «Construido junto con Claude Code (Anthropic)», **probarlo en 3 pasos** (solo la web), tabla «Quién hace qué en la web» (`admin`/`admin` = el taller, no hace pedidos; `ere-admin`/`1111` = un cliente de ejemplo, hace pedidos), tabla «¿Dónde está cada cosa?», tabla «Dónde funciona hoy» (Linux sí/sí; Windows PC sí/sí con Webots en Windows; Windows en VirtualBox no/no; Mac sin probar), qué hay en cada carpeta, licencia MIT explicada en sencillo |
| `LANZAR_PROYECTO.md` (+EN, EU) | Linux: instalar (`apt install git docker.io docker-compose-v2 x11-xserver-utils`, grupo `docker`), el atajo `./arrancar_todo.sh` (y por qué la primera vez mejor a mano: el build de Webots parece colgado al 70-80 % y **no hay que cortarlo**), los 3 contenedores, parte A (web) y parte B (celda) paso a paso: 0 Pico y sus claves Wi-Fi (`--skip-worktree`), 1 `xhost` + compose (quitar `/dev/dri` sin GPU), 2 `colcon build` (obligatorio la primera vez), 3 `ros2 launch` y esperar 6 conectados (si no, `docker restart webots_panda_sim24`), 4 puentes de LED (mejor desde el panel), 5 panel, 6 producción por terminal, 7 varias líneas; si algo se atasca (`docker restart webots_panda_sim24` repone los cubos; la web no se toca); apagar; parada de emergencia (botones, HC-SR04, panel, OLED; **rearmar de verdad es `Bool(false)` en `/emergency_stop`**, mandar `rearme` al LED solo apaga el parpadeo); protocolo de las Pico |
| `INSTALAR_WINDOWS.md` (+EN, EU) | ¿Tu Windows sirve? (virtualización en la BIOS; VirtualBox no, con la explicación del bit NPT/EPT; KVM como alternativa sin probar), `wsl` que solo enseña la ayuda (activar con `dism` las dos funciones y reiniciar, `wsl --update --web-download`), instalación (Docker Desktop sin cuenta, Git, Webots R2025a «solo para mí» desde `https://github.com/cyberbotics/webots/releases/download/R2025a/webots-R2025a_setup.exe`, clonar, `.bat` con doble clic o `.\arrancar_windows.bat`, aviso de SmartScreen), usar tu propia ventana de PowerShell (no SSH), problemas de instalación («Virtualization support not detected», «Error catastrófico», `500 … _ping`, bucle de recarga), la celda en Windows, varias cadenas (tabla de puertos), rendimiento y cadenas en otros ordenadores |
| `PROBLEMAS_CONOCIDOS.md` (+EN, EU) | El **único** sitio con problemas y arreglos (sección J) |
| `Taller_Administracion/README.md` (+EN, EU) | La web para quien no sabe informática: el viaje de un pedido con un ejemplo (Astilleros Murueta, sucursal de Bilbao, `mur-bilbao`): se pide con la cesta → se consigue (almacén o fabricando) → queda listo → se reparte (albarán) → se factura; quién puede hacer qué; cosas que conviene saber (precios congelados, nada se borra, el stock no se reparte a escondidas); usuarios de ejemplo; meter piezas a mano en el almacén. Con capturas |
| `Taller_Administracion/DETALLE_TECNICO.md` (+EN, EU) | La web por dentro: rutas servidas, arranque y sembrado, fichero de arranque y `cargar_arranque`, el panel pestaña a pestaña, modelo, ciclo de un pedido, precios y facturación, paquetes con precio, migraciones, roles, `cubo_clasificado`, tests (y cómo lanzarlos; nunca tocan la base real) |
| `Lab.Panda 2.4/resumen_proyecto_panda.md` (+EN, EU) | «Nuestra cadena de producción», para novatos: qué es Webots, de dónde viene el Panda (Franka Emika, cobot), nuestros dos Panda, la cinta, la bandeja, la visión, cómo se reponen los cubos, cómo se habla con la web, las Pico. Se sirve en `/manual/panda` |
| `Lab.Panda 2.4/detalle_tecnico_panda.md` | Detalle técnico de la celda (puede resumir las secciones B y C de este fichero) |
| `Documentacion/PI_PICO_montaje.html` | Montaje de las dos Pico con el diseño de la portada: por qué existen, las claves Wi-Fi, tabla resumen, cada bloque (LED de agarre, botón con pull-up —y el truco del pulsador de 4 patas—, LED de producto con sus resistencias, HC-SR04 con el divisor, OLED con `SoftI2C`), material, esquemas en SVG |
| `Documentacion/anadir_cadena_produccion.md` (+ `.html`) | Varias líneas: qué es una línea, los ficheros que lo hacen todo (tabla Linux/Windows), hacerlo a mano (copiar la plantilla, cambiar tres cosas, encender, lanzar, configurar el panel, apagar), cuántas caben |
| `Rasberry_Pi_Pico/LEEME.md` | Que las claves son plantillas y cómo no subirlas |
| `Virtual_Robotic/README.md` | Qué es la portada suelta y su cerrojo de cortesía |

**Imágenes y vídeos** (los hace el usuario cuando la celda funcione; hasta
entonces las páginas funcionan igual con los huecos):
`Virtual_Robotic/img/` y `Taller_Administracion/app/static/img/` (las mismas):
`webots_cell.jpg` (captura de Webots con los dos brazos y las ventanas de las
cámaras), `celda_trabajando_1.mp4/.jpg` y `celda_trabajando_2.mp4/.jpg` (clips
de ~30 s, comprimidos a ~400 KB, y su primer fotograma como póster),
`pico_hardware.jpg` (foto de las Pico), `panel_pico_simulada.jpg`;
`Taller_Administracion/img/` (capturas del README de la web:
`web_1_pedir_cesta.png` … `web_6_facturar.png`, `panel_pestanas.png`);
`Lab.Panda 2.4/img/` (`panda_robot.jpg`, `webots_cell.jpg`,
`panel_control_manual.png`); `img/` (capturas de los README y
`webots_atasco_72_porciento.png`). Explícale al usuario cómo grabar (Webots:
menú *File → Make Movie*; capturas con la herramienta del sistema) y cómo
comprimir con `ffmpeg` (p. ej. `-vf scale=960:-2 -c:v libx264 -crf 30 -an`).

**Opcional**: `Documentacion/Plantillas/generar_plantillas.py` (necesita
`python-docx`) genera dos plantillas Word, *EJEMPLO* y *VACÍA*, para apuntar a
mano la configuración de una instalación (empresas, clientes, productos,
líneas y dónde arranca cada una), con los campos que hay que cambiar marcados
con `*`. Preguntar al usuario si la quiere.

---

## H. Validación final (fase 13)

1. Web: todos los tests en verde; recorrido completo en el navegador
   (pedido con cesta → fabricado → repartido con albarán → facturado → cobrado
   → anulado con rectificativa → refacturado).
2. Celda: `/warehouse/cube_positions` correcto en reposo; tope y bandeja sin
   brazos: soltar un cubo con `G:0.5:1.05` y registrar 25 s: llega, se para
   en y ≈ 1,2700, la bandeja lo encaja en x = 0,5 girado 10° con
   **y ≤ 1,2643 y sin retroceso brusco**, z estable 0,770 ± 1 mm; devolverlo
   con `G:0.35:0.16`.
3. Cinemática: desde la base del Loader convergen (con `check_convergence`)
   los tres puntos de la caja a z 0,87 y el de dejar (0,5; 0,28; 0,87); desde
   el Sorter (base y giro reales), (0,5; 1,25; 0,875) y las tres cajas.
4. Panel: X+/Y+/Z± mueven el TCP en **ejes del mundo** con los dos robots;
   «Centrar sobre cubo» centra; HOME pide confirmación; STOP pausa la
   producción y los LED parpadean en **las dos** Pico; REARME continúa en el
   mismo paso; **con la parada activa el jog sigue funcionando**; cerrar y
   reabrir el panel **no** crea un segundo `sorter_demo`
   (`ps -eo args | grep -c 'lib/panda_controller/sorter_demo'` = 1).
5. Pico: el botón corta el LED en local, parpadea en rojo y la celda pasa a
   PARADO; con la Wi-Fi apagada el botón sigue cortando el LED; un botón
   mantenido pulsado solo manda **una** parada; la pulsación larga ofrece
   restablecer la clave; `led_publisher_usb` al arrancar manda `REARME`,
   `PROD:0,0,0` y `TXT:`; con otro `button_listener` ocupando el 5002, el
   nuevo reintenta cada 5 s y lo coge al liberarse.
6. **Lote largo** (la prueba que manda): 15 minutos o más desde el panel:
   ritmo de **unos 2 clasificados por minuto** (en un PC normal con Linux) y
   **ninguna racha** de pinza dislocada. Contar con
   `grep -c 'CUBO CLASIFICADO' /tmp/lote_sorter.log` y
   `grep -c 'PINZA DISLOCADA' …`. Un lote corto no vale: con el mismo código
   se han medido lotes de 27 clasificados y 3 dislocaciones y de 5 y 9.
7. Recuperación: tras `docker restart webots_panda_sim24` y relanzar, una sola
   generación de cada proceso y la producción continúa.

---

## I. Lecciones aprendidas, trampas y decisiones que parecen raras

Todo esto se aprendió **pagándolo** (días de fallos). Léelo antes de
«mejorar» nada.

### I.1 Reglas de trabajo

1. **Medir antes que razonar.** Los fallos largos se resolvieron en horas en
   cuanto se miraron los **valores** en el instante del fallo
   (`/sorter/gripper_state`, `/warehouse/cube_positions`), no el síntoma
   visual. Un dedo fuera de rango y el otro normal = dedo trabado contra algo
   rígido; los dos raros o un salto de articulaciones = mirar la cinemática.
2. **Los dos patrones que más han mordido**: medir el estado físico justo
   después de mandar un movimiento (`real_theta` es lo mandado, el brazo va
   por detrás); y **devolver fallo cuando el trabajo ya estaba hecho** (con la
   pinza abierta en el destino la entrega está hecha; si se da por fallo, no se
   publica, el reciclado se bloquea y la celda se para).
3. **Un cambio del agarre no vale hasta que un lote largo lo confirma**
   (clasificados por minuto en ≥15 min, no contar dislocaciones sueltas).
4. **Cambios de geometría**: cambiar → reiniciar Webots → mirar la pieza →
   medir con un cubo suelto.
5. **Parámetros ROS por línea de comandos**: una letra o palabra suelta
   siempre entre comillas YAML (`only_color:="Y"`).
6. **Probar sobre datos del usuario con cuidado**: la web suele estar abierta a
   la vez; para pruebas, un cliente propio; si se toca algo suyo por error,
   deshacerlo y decirlo.
7. **Limpieza de procesos**: tras reiniciar Webots, los procesos ROS de la
   celda quedan huérfanos y se reconectan solos: si se relanza encima, quedan
   dos generaciones. `pkill -f 'ros2 run …'` **no** los encuentra (el proceso
   real es `/workspace/install/panda_controller/lib/panda_controller/<nodo>`).
   Lo fiable: `docker restart ros2_panda_dev24` (o
   `docker exec ros2_panda_dev24 kill -9 -1`, que mata todo menos el bash).
   Si luego `ros2 topic …` falla: `ros2 daemon stop && ros2 daemon start`.
8. **Reiniciar un solo controlador** (no es `ros2 run webots_ros2_driver
   driver`): `$(ros2 pkg prefix webots_ros2_driver)/share/webots_ros2_driver/scripts/webots-controller
   --robot-name=<Nombre> --protocol=tcp --ip-address=host.docker.internal
   --port=1234 ros2 --ros-args -p robot_description:=<urdf>`. Si el almacén
   estuvo caído con producción, las entregas de ese hueco no se reciclaron:
   publicarlas a mano en `/warehouse/cube_delivered`.

### I.2 Trampas técnicas

| Trampa | Detalle |
|---|---|
| `spin_once(timeout=N)` como espera | Vuelve en cuanto procesa un mensaje: usar `spin_for` |
| `time.sleep` durante el cierre de la pinza | No procesa mensajes: el sensor de dedos no se actualiza |
| Reloj del ordenador en un PC lento | Todo pasa más deprisa dentro de la simulación: usar `/clock` |
| Mezclar relojes en un cronómetro | Resta negativa para siempre (el «baile infinito»): `_cronometro()` |
| Namespace de `WebotsController` | No llega al plugin Python: el driver usa `getName().lower()` |
| Puerto de Webots | Todos los `<extern>` comparten el 1234 (o el de su línea) |
| Lanzar los controladores antes de que cargue el mundo | Reintentan y dejan conexiones de más, o se rinden («Giving up»): esperar los 6 `Waiting for` |
| `pkill` de `ros2 launch` | Deja vivos a sus hijos: reiniciar el contenedor |
| `ConveyorBelt` | Sin campo `controller`; solo se para cambiando `speed` desde un Supervisor |
| Webots y `webots-ros2` | Van por parejas (R2025a ↔ 2025.0.0) |
| Texturas que no bajan / «Downloading assets 72 %» | Cosmético; la caché evita redescargar; si se cuelga, cerrar y volver a lanzar (lo bajado se guarda); el cuelgue en frío a veces es un *segfault*: `docker restart` |
| `Extrusion` de los carriles | Crece hacia fuera; el orden de vértices decide hacia dónde miran las caras |
| Carriles o tope flotando | Un hueco de 1,5 cm debajo deja una repisa donde se engancha el dedo |
| Pico USB y Docker | El mapeo se aplica al crear el contenedor: `--force-recreate`; ruta `by-id`, nunca `ttyACM0` |
| Pico USB y Thonny | No abrir el puerto con los dos a la vez |
| Thonny Run/F5 | `SyntaxError` falso con ficheros largos: Guardar como → dispositivo |
| Botones con rebote | Avisar solo si no hay ya parada activa |
| OLED con I2C por hardware | `OSError EIO` al escribir: `SoftI2C` |
| Web con recarga automática | Cada edición reinicia y borra sesiones; en Windows, bucle infinito: apagada por defecto |
| Web sin Alembic | Toda columna nueva, por `migraciones.py` (con valor por defecto si es NOT NULL) |
| `taller.db` de root | Desde el anfitrión no se escribe: por la API o `docker exec` |
| `host.docker.internal` vs `taller_host` | El primero es Webots (o el Windows); el segundo, el anfitrión |
| Caché del navegador | Sin `no-cache`, un JS o HTML viejo hace creer que el cambio no funciona |
| `confirm()`/`alert()` | El navegador puede bloquearlos en silencio: diálogo propio |
| Ficheros `.bat` y `.sh` | CRLF para `.bat`, LF para `.sh` (`.gitattributes`) |
| `.wbproj` | Webots lo reescribe (como root en Docker): fuera de Git y `rm` antes de copiar la plantilla |
| Clonar una VM | Se clona el Nº de máquina de cada línea: cambiarlo |

### I.3 Decisiones que parecen raras y son a propósito

- **Giro +90 del agarre del Sorter, siempre** (C.13) y canal de 11 cm (B.3).
- **`approach_open = 0.040` en el Sorter** (el máximo): cada milímetro de hueco
  es tolerancia a descentrado y giro.
- **`rotate_before_descend = True` en el Sorter**: se activó y desactivó 7
  veces; las roturas eran por geometría, no por esto.
- **Parada automática que se rearma sola** (4 s, máximo 3 seguidas): la
  dislocación salta con el brazo encima de su propia cámara; sin autorrearme
  la celda se quedaba ciega y muerta.
- **Con la parada activa se puede mover el brazo a mano** (petición expresa:
  hace falta para liberar un dedo o apartar el brazo del sensor). Riesgo
  aceptado: un demo en pausa conserva su `real_theta` viejo y al rearmar puede
  pedir un movimiento grande. **No añadir** bloqueos «por seguridad»: ya se
  hizo una vez y dejó al operario sin forma de recuperar la celda.
- **El Loader usa siempre los 3 cubos**: `only_color` es una **etiqueta**, no
  un filtro. Así un producto «solo LED» (Y/M/C/W) o sin LED se fabrica igual.
- **El LED nunca condiciona el negocio**: un producto sin LED se pide, se
  fabrica y se completa igual (por `pedido_id`/`producto_id`).
- **El contador del panel es independiente de la web**: producir y repartir
  son decisiones distintas («si el operario pide 20 piezas, hace 20 y van al
  almacén; administración decide el reparto»).
- **La bandeja encaja una sola vez.**
- **El botón de la Pico W va por Wi-Fi**: la idea es un módulo barato de
  parada lejos del PC.
- **Contraseña maestra `1111` y cerrojo de cortesía** en la portada suelta:
  decisión del usuario para jugar en red local; no es para Internet.
- **La factura lleva una nota** de que le faltan conceptos de una factura real.

### I.4 Intentos descartados (no repetir sin leer por qué)

| Intento | Resultado |
|---|---|
| Pieza de 50 mm | 0 clasificados y 39 abortos |
| Aflojar la detección de pinza dislocada | Ritmo 1,63 frente a 1,97/min y más roturas |
| Trocear en articulaciones los pasos de rampa | Revertido |
| Canal a 9 cm | 25 dislocaciones por lote |
| Velocidad de articulaciones a 2,0 rad/s | Cubos soltados por inercia, uno lanzado fuera del mundo, pinza dislocada |
| Re-centrado continuo de la bandeja | Bucle cada 0,4-0,5 s sin converger |
| Encajar la bandeja en y = 1,25 | La cinta lo reempujaba descentrado; dos cubos en el mismo sitio |
| Estrechar los carriles por debajo del cubo | Atasco y pinza rota |
| Verificar por cámara que el cubo llegó a su caja | No fiable con varias piezas en la caja |
| Webots R2023b | *Segfault* del Supervisor y cámaras sin imagen |
| Quitar el giro +90 | El cubo reposa tocando el tope: un dedo entraría en él |

---

## J. Problemas conocidos (contenido de `PROBLEMAS_CONOCIDOS.md`)

**Celda (Linux)**:
- Los controladores no conectan / Webots se queda cargando la primera vez →
  los scripts ya reinician Webots; a mano, `docker restart webots_panda_sim24
  ros2_panda_dev24` y relanzar.
- «Giving up» o «Address already in use» al relanzar → quedaron controladores
  vivos: reiniciar los dos contenedores.
- El dedo de la pinza del Sorter se rompe → rearmar no sirve: reiniciar Webots
  (guardar antes `/tmp/lote_sorter.log`). Desde el reloj de simulación pasa
  mucho menos.
- Procesos repetidos en el contenedor ROS → los scripts reinician el
  contenedor antes de lanzar.
- Cubo perdido que no vuelve → parar los demos y publicar su color en
  `/warehouse/cube_delivered` (no lo recicla si sigue a menos de 20 cm del
  punto de recogida, a propósito); o moverlo con `/warehouse/mover_cubo_manual`.
- LED de producto encendido tras reiniciar el Sorter a medias → publicar
  `''` en `/production/lote_color_objetivo` y `'0'` en `/comando_led_producto`.
- El botón de la Pico W no para → comprobar un solo `button_listener`, que
  `PC_IP` es la IP actual del PC y que el 5002 está publicado.
- Sin sitio para Docker en una VM → segundo disco y `vm_disco_docker.sh`.

**Web**: se reinicia sin parar (recarga automática: apagada por defecto); en el
almacén no aparece un producto (no es un fallo: cada unidad se asigna al
momento a los pedidos que la esperan); vídeos en Safari (arreglado con Range,
**sin comprobar** en un Safari de verdad).

**Windows**: va lento en un PC viejo (cámaras a 10 imágenes/s); el Loader se
quedaba «bailando» (arreglado; tras cortar un lote a medias, el panel tarda
2 minutos en dejar lanzar otro); «Downloading assets 72 %» (cerrar y volver a
lanzar); `git pull` falla por un `.wbproj` de un clon antiguo
(`git checkout -- "Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"`); el
`git pull` pide usuario (borrar la credencial guardada con `cmdkey /delete:…`).

**Problemas abiertos** (siguen sin arreglo definitivo; documentarlos, no
«arreglarlos» a ciegas):

1. **Dislocación intermitente de un dedo del Sorter** en el tope. Firma: al
   final del cierre o al empezar a subir, un dedo estirado (0,06-0,23) y/o el
   otro negativo; a veces el cubo no sube. La tercera de un lote puede ser
   permanente. Ideas sin probar: parar la cinta mientras un cubo espera
   encajado; piezas cilíndricas.
2. **El aviso a la web sale antes de que el almacén confirme el reciclado**: una
   entrega que el almacén rechace como falsa puede quedar contada en un pedido.
3. **Reparto entre clientes por orden de llegada**, no por prioridad de cliente.
4. **Contraseña maestra y cerrojo de cortesía**: solo para red local.
5. **Webots R2025a se ve regular** (texturas del R2023b que no bajan);
   ocasionalmente un *segfault* en el arranque en frío (se arregla reiniciando).
6. **Mac/Safari sin probar.**

---

## Anexo 1 — `Lab.Panda 2.4/worlds/panda_industrial_cell.wbt` (copiar tal cual)

El mundo de Webots completo, con sus comentarios (explican el porqué de cada medida). Copiarlo **carácter a carácter** a `Lab.Panda 2.4/worlds/panda_industrial_cell.wbt`. Comprobación: su SHA-256 empieza por `b3e69933c9a9fa70`.

```
#VRML_SIM R2025a utf8

EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/floors/protos/Floor.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/robots/franka_emika/panda/protos/Panda.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/robots/franka_emika/panda/protos/PandaHand.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/tables/protos/Table.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/factory/conveyors/protos/ConveyorBelt.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/geometries/protos/Extrusion.proto"

WorldInfo {
  info [
    "Celda industrial de dos robots (sesion 2026-08-27, v2 tras verificar alcance real con el solver): Loader saca cubos de la caja y los deja en la cinta; Sorter los recoge al otro lado y los clasifica por color."
  ]
  title "Celda Industrial - Loader + Cinta + Sorter"
}
# Camara de arranque (sesion 2026-09-14, a peticion del usuario: "siempre
# tengo que buscar los robots con el raton"). La anterior (pos 3.8 1.7 3.2)
# miraba casi horizontal y por encima de la celda. Esta mira en diagonal,
# desde ~3.1m, al centro de la celda (0.22, 0.55, 0.85): caja del Loader,
# cinta, Sorter y cajas de color a la vez. OJO: "Guardar" el mundo en
# Webots sobrescribe esto con la vista que haya en ese momento.
Viewpoint {
  orientation -0.2224 0.0548 0.9734 2.6711
  position 2.7 -0.75 2.2
}
TexturedBackground {
}
TexturedBackgroundLight {
}
Floor {
  size 6 6
}

# ============================================================
# GEOMETRIA VALIDADA CON EL SOLVER (sesion 2026-08-27), no a ojo:
# desde la base de CUALQUIER Panda (la cinematica solo depende de
# target-base, es invariante a donde este la base en el mundo), los
# puntos con agarre fiable (check_convergence=True) están en un
# rango de profundidad dy = target_y - base_y de aprox [0.45, 0.60]
# delante del robot, con dx lateral seguro hasta unos +-0.20 (probado
# +-0.15 y +-0.20 en ambos lados; -0.35 SI fallo, +0.35 no --
# asimetria real del brazo, no un error de calculo). Toda la
# geometria de abajo (caja, punto de la cinta, punto de recogida,
# cajas de clasificacion) esta anclada a esa ventana, verificada
# punto por punto con panda_ikpy_kinematics.solve(..., check_convergence=True)
# antes de escribir estos numeros -- NO extrapolar a ojo si se toca esto.
# ============================================================

# ============================================================
# ESTACION 1: LOADER
# ============================================================
Table {
  # Acortada de 1.2 a 1.14 de largo (sesion 2026-09-09, aviso del usuario:
  # "la mesa no has cortado donde esta la cinta"). Al acercar la cinta 6cm
  # (ver DEF BELT) la mesa, que llegaba a y=0.30, pasaba a cubrir los
  # primeros 6cm de la banda -- y justo ahi cae ahora el cubo
  # (BELT_DROP_Y=0.28). Un cubo posado sobre la mesa, que es fija, no lo
  # arrastra la cinta: se quedaria parado para siempre en el sitio exacto
  # donde el Loader lo suelta.
  # Ahora termina en y=0.24, que es donde empieza la banda movil, asi que
  # las dos superficies se tocan sin solaparse (ambas a z=0.74, sin
  # escalon). La base del Loader (y=-0.3) sigue de sobra sobre la mesa,
  # que va de y=-0.90 a 0.24.
  translation 0.5 -0.33 0
  name "table_loader"
  size 0.8 1.14 0.74
}
DEF PANDA_LOADER Panda {
  translation 0.5 -0.3 0.74
  name "Loader"
  controller "<extern>"
  endEffectorSlot [
    DEF LOADER_HAND PandaHand {
    }
    Camera {
      translation 0 0 0.12
      rotation 0 1 0 -1.5708
      name "wrist_camera"
      fieldOfView 0.9
      width 320
      height 240
    }
  ]
}
DEF OVERHEAD_CAM_LOADER Robot {
  translation 0.5 0 2.27
  name "OverheadCamLoader"
  controller "<extern>"
  children [
    Camera {
      rotation 0 1 0 1.5708
      name "overhead_camera"
      fieldOfView 0.9
      width 320
      height 240
    }
  ]
}

# Caja sobre la mesa 1: una sola fila de 3 cubos, EXACTAMENTE las
# mismas x/y que panda_un_cubo.wbt (dy=0.45 desde la base, probado).
DEF CRATE_WALL_FRONT Solid {
  translation 0.5 0.05 0.78
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.55 0.4 0.25
        roughness 0.6
      }
      geometry Box {
        size 0.5 0.01 0.08
      }
    }
  ]
  name "crate_wall_front"
  boundingObject Box {
    size 0.5 0.01 0.08
  }
}
# CRATE_WALL_BACK ELIMINADA (sesion 2026-09-09, decision del usuario:
# "yo quitaria toda la pared, como estaba parado intenta coger otra vez y
# pilla pared con cubo"). Era la pared del lado de la CINTA (y=0.25).
# Primero se rebajo de 8cm a 6cm, pero eso no bastaba: el problema no es
# la altura sino que un cubo puede acabar JUSTO al otro lado de ella, en
# la franja entre la pared y la cinta -- capturado en vivo, el cubo verde
# en (0.493,0.291) con la pared en y=0.25. Ahi el Loader baja a por el y
# la pinza abarca pared Y cubo a la vez, con la pared haciendo de tope
# fijo (el mismo patron de dedo trabado que rompe la pinza).
# Sin pared no hay nada que atrapar: los cubos de esa franja se recogen
# como cualquier otro. No hace falta para contener nada -- los cubos los
# repone el WarehouseSupervisor teletransportandolos a su sitio, no
# rodando, y las otras tres paredes de la caja siguen puestas.
# Ningun codigo referencia este DEF (comprobado en todo el paquete).
DEF CRATE_WALL_LEFT Solid {
  translation 0.25 0.15 0.78
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.55 0.4 0.25
        roughness 0.6
      }
      geometry Box {
        size 0.01 0.22 0.08
      }
    }
  ]
  name "crate_wall_left"
  boundingObject Box {
    size 0.01 0.22 0.08
  }
}
DEF CRATE_WALL_RIGHT Solid {
  translation 0.75 0.15 0.78
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.55 0.4 0.25
        roughness 0.6
      }
      geometry Box {
        size 0.01 0.22 0.08
      }
    }
  ]
  name "crate_wall_right"
  boundingObject Box {
    size 0.01 0.22 0.08
  }
}
# Vuelta a 3 cubos (sesion 2026-08-28): en vez de anadir mas cubos fisicos
# (probado antes, funcionaba pero se solapa con el alcance real y con la
# cinta segun donde se pongan), se reciclan estos mismos 3 -- ver
# DEF WAREHOUSE_SUPERVISOR mas abajo y warehouse_supervisor_driver.py: en
# cuanto el Sorter deja uno de verdad en su caja de color, el supervisor lo
# teletransporta de vuelta a este mismo punto de la caja del Loader, listo
# para reutilizar como si fuera materia prima nueva. Nunca hacen falta mas
# de 3 objetos reales en el mundo, por muchos pedidos que se procesen.
DEF CUBO_ROJO Solid {
  translation 0.5 0.16 0.77
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 1 0 0
        roughness 0.2
      }
      geometry Box {
        size 0.06 0.06 0.06
      }
    }
  ]
  name "cubo_rojo"
  boundingObject Box {
    size 0.06 0.06 0.06
  }
  physics Physics {
    density -1
    mass 0.05
  }
}
DEF CUBO_VERDE Solid {
  translation 0.35 0.16 0.77
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0 1 0
        roughness 0.2
      }
      geometry Box {
        size 0.06 0.06 0.06
      }
    }
  ]
  name "cubo_verde"
  boundingObject Box {
    size 0.06 0.06 0.06
  }
  physics Physics {
    density -1
    mass 0.05
  }
}
DEF CUBO_AZUL Solid {
  translation 0.65 0.16 0.77
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0 0 1
        roughness 0.2
      }
      geometry Box {
        size 0.06 0.06 0.06
      }
    }
  ]
  name "cubo_azul"
  boundingObject Box {
    size 0.06 0.06 0.06
  }
  physics Physics {
    density -1
    mass 0.05
  }
}

# Supervisor sin cuerpo fisico (sesion 2026-08-28): solo necesita acceso
# al arbol de escena para teletransportar los 3 cubos de vuelta a la caja
# del Loader en cuanto el Sorter confirma que uno se entrego de verdad
# (topic /warehouse/cube_delivered, publicado por cube_shuttle_demo.py
# solo tras pasar la verificacion de camara -- nunca por el sensor de
# dedos solo). Ver warehouse_supervisor_driver.py.
DEF WAREHOUSE_SUPERVISOR Robot {
  translation 3.0 3.0 1.0
  name "WarehouseSupervisor"
  controller "<extern>"
  supervisor TRUE
}

# Bandeja/transbordador del punto de recogida del Sorter -- prototipo de la
# sesion 2026-09-06 (worlds/panda_industrial_cell_shuttle.wbt), promovido a
# produccion el 2026-09-10. Encaja en pose exacta el cubo que llega
# descentrado tras deslizar y frenar contra el tope. Se porto AQUI en vez de
# lanzar el mundo del prototipo porque aquel se quedo en el 2026-09-06 y no
# tiene la base del Sorter girada 26,6 grados ni el canal a 11cm.
# Ver sorter_shuttle_supervisor_driver.py.
DEF SORTER_SHUTTLE_SUPERVISOR Robot {
  translation 3.0 3.5 1.0
  name "SorterShuttleSupervisor"
  controller "<extern>"
  supervisor TRUE
}

# ============================================================
# CINTA -- el punto de deposito (0.5, 0.30) es dy=0.60 desde la base
# del Loader (probado). size.z=0.74 para que la superficie quede a la
# altura de las mesas.
#
# CAMBIO DE LAYOUT (sesion 2026-08-27, a peticion del usuario -- "se
# puede poner la otra mesa en uno de los lados grandes de la cinta"):
# antes el Sorter estaba en linea recta al final de la cinta, con los
# dos brazos casi pegados entre si (confirmado feo en una captura de
# Webots). Ahora el Sorter esta AL LADO de la cinta (offset en X, no
# mas alla en Y) y alcanza la cinta de LADO, no de frente -- probado
# con el solver que el brazo llega igual de bien en esa direccion
# (dx=+0.5 funciona, no hacia falta girar el robot ni tocar la
# cinematica). Esto forma una ele de verdad sin extender
# panda_ikpy_kinematics.py para soportar rotacion de base (que no la
# soporta, solo traslacion).
#
# SEGUNDO AJUSTE (mismo dia, mas tarde -- aviso real del usuario): el
# tope de la cinta estaba demasiado pegado al punto de recogida -- el
# cubo se para justo apoyado en la pared, y la pinza (que cierra girada
# 45 grados) necesitaba meter un dedo en el hueco de la propia pared
# para agarrarlo. Se alejo el tope 15cm mas (y se alargo la cinta lo
# mismo para que siga empezando en el mismo sitio) para dar hueco real
# a la pinza -- el nuevo punto de recogida (dy=+0.25 desde la base del
# Sorter en vez de +0.15) sigue verificado con el solver.
# ============================================================
DEF BELT ConveyorBelt {
  # Acercada 6cm al Loader (sesion 2026-09-09, y=0.85 -> 0.79). MOTIVO
  # MEDIDO, no estetico: el Loader NO ALCANZA el punto de deposito. Con su
  # base en y=-0.3, el solver da error 0.1cm a y=0.30 y 38.5cm a y=0.70
  # (el BELT_DROP_Y que habia) -- y 0.70-0.385 = 0.315 es exactamente donde
  # aparecian los cubos. Nunca deposito donde creia: los soltaba en la
  # cabecera de la cinta, medio encima de su marco (que sobresale 1cm), y
  # la cinta se los llevaba, asi que el fallo quedaba tapado por la
  # produccion ("deja el cubo gran parte en la cinta y otra parte en el
  # marco y luego se va por la cinta").
  # La cinta pasa a ocupar y 0.24-1.34 (antes 0.30-1.40): asi el unico
  # punto que el brazo alcanza (~0.30) cae DENTRO de la banda en vez de
  # justo en el borde. Comprobado que no rompe el otro extremo:
  # BELT_END_STOP sigue en y=1.30 (dentro de la cinta) y el punto de
  # recogida del Sorter en y=1.25 tambien. La cabecera solapa 6cm con
  # table_loader (que llega a y=0.30), pero las dos superficies estan a
  # z=0.74, asi que quedan a ras y el cubo no encuentra escalon.
  translation 0.5 0.79 0
  rotation 0 0 1 1.5708
  name "Belt"
  size 1.1 0.3 0.74
  speed 0.15
}
# NOTA: ConveyorBelt no expone 'controller' como campo del PROTO --
# usa siempre su controlador interno "conveyor_belt", que solo lee
# speed/timer una vez al arrancar. Control en caliente desde ROS2
# (Fase 5) necesitara un Supervisor sobre el campo 'speed', no un
# extern-controller aqui.

# Cuna con pared en bajada (sesion 2026-09-04, palo 5 -- ver
# Documentacion/carriles_completo.html): mismo perfil que belt_rail_l/r_recto
# (2cm + 1cm plano, rampa recta a 9cm), pero orientado en la direccion de
# la cinta en vez de canal/fuera -- el lado bajo mira hacia la cinta (de
# donde vienen los cubos, cara sin tocar), el lado alto crece hacia el
# final de la cinta. Motivo: un cubo (verde) se colo por encima/mas alla
# de este tope, visto en vivo con ground truth a y=1.36-1.37, fuera del
# alcance de la camara del Sorter. Con la pared alta detras, un cubo no
# deberia poder escaparse tan facil. Spine a lo largo de X (no de Y como
# en los carriles rectos) -- si el crossSection sale invertido (crece
# hacia la cinta en vez de hacia el final), es el mismo "quirk" de
# inversion de eje, solo que en un eje distinto -- verificar con un cubo
# de prueba antes de dar por bueno.
DEF BELT_END_STOP Solid {
  # ALTURA (sesion 2026-09-11): mismo cambio que los carriles 3 y 4 del
  # 2026-09-10 (ver alli el porque completo) -- base de 0.755 a 0.740 (la
  # superficie real de la cinta) y pared de 0.02 a 0.015. Se habia quedado
  # sin hacer aqui, y este es justo el palo contra el que la bandeja deja
  # TODOS los cubos esperando al Sorter: flotaba 1,5cm sobre la cinta
  # (hueco por el que se puede colar la esquina inferior del cubo) y su
  # repisa quedaba en 0.775, por encima del centro del cubo (0.770).
  # Orden de vertices SIN TOCAR: area con signo -0.00435, igual que los
  # palos 3 y 4 tras su mismo cambio (ver carriles_completo.html).
  translation 0.5 1.30 0.740
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.2 0.2 0.2
        roughness 0.5
      }
      geometry Extrusion {
        crossSection [
          0.0 0.0
          0.0 0.015
          0.01 0.015
          0.09 0.09
          0.09 0.0
          0.0 0.0
        ]
        spine [
          -0.16 0.0 0.0
          0.16 0.0 0.0
        ]
      }
    }
  ]
  name "belt_end_stop"
  boundingObject Extrusion {
    crossSection [
      0.0 0.0
      0.0 0.015
      0.01 0.015
      0.09 0.09
      0.09 0.0
      0.0 0.0
    ]
    spine [
      -0.16 0.0 0.0
      0.16 0.0 0.0
    ]
  }
}

# CARRIL/EMBUDO de la cinta (sesion 2026-08-31, idea del usuario tras el
# arreglo de "check_convergence": el agarre honesto detecta y falla bien
# cuando un cubo esta en la zona x>=0.60 (o cerca de x=0.35), pero esa
# zona seguia siendo alcanzable POR EL CUBO -- este carril evita que el
# cubo llegue ahi, atacando la causa fisica en vez de solo detectarla.
# Ancho de la cinta real 0.3 (x de 0.35 a 0.65, ver DEF BELT). Zona ancha
# junto al Loader (dejar margen al caer, BELT_DROP_Y=0.55 en
# loader_demo.py cae justo aqui) que se va estrechando en rampa suave
# hasta un carril fijo de 10cm justo antes del punto de recogida del
# Sorter (PICKUP_X,PICKUP_Y=0.5,1.25 en sorter_demo.py) -- ahi es donde
# de verdad importa llegar centrado. Misma altura/grosor que
# BELT_END_STOP (top a z=0.77, la altura del propio cubo -- no estorba
# al agarre, que baja recto desde arriba entre los dos carriles, no
# encima de ellos). Angulo de la rampa ~8.8 grados, muy suave, para no
# frenar el cubo de golpe contra el carril.
# Revertido a la Box simple (sesion 2026-09-04): se probo aqui la misma
# cuna que belt_rail_l/r_recto, pero el usuario pidio dejar el embudo
# como estaba y aplicar el cambio solo en el tramo recto (3 y 4, ver
# Documentacion/cuatro_palos_embudo.html y palos_3_4_rampa_esquema.html
# para la numeracion). Geometria simple de siempre.
DEF BELT_RAIL_L_EMBUDO Solid {
  translation 0.415 0.775 0.755
  rotation 0 0 1 -0.1543
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.2 0.2 0.2
        roughness 0.5
      }
      geometry Box {
        size 0.015 0.4554 0.03
      }
    }
  ]
  name "belt_rail_l_embudo"
  boundingObject Box {
    size 0.015 0.4554 0.03
  }
}

DEF BELT_RAIL_R_EMBUDO Solid {
  translation 0.585 0.775 0.755
  rotation 0 0 1 0.1543
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.2 0.2 0.2
        roughness 0.5
      }
      geometry Box {
        size 0.015 0.4554 0.03
      }
    }
  ]
  name "belt_rail_r_embudo"
  boundingObject Box {
    size 0.015 0.4554 0.03
  }
}

# Carriles del tramo RECTO (donde agarra la pinza -- NO TOCAR, iba en
# serio). RE-REVERTIDO a la Box simple original (sesion 2026-09-03,
# segunda vez): se volvio a poner la pared inclinada pensando que el
# resbalon era por rotate_before_descend=False, pero CON
# rotate_before_descend=True Y la pared puesta el cubo volvio a caerse,
# REINTENTADO en sesion 2026-09-04: en su momento (sesion 2026-09-03) se
# probo esta misma cuna aqui y el cubo se resbalaba de la pinza al
# levantar -- se revirtio a la Box simple. Analisis posterior (mismo dia
# 2026-09-04, ver robotica_carril_rampa_agarre_abierto.md en memoria)
# encontro la causa REAL del resbalon: la cinta (DEF BELT) nunca se
# paraba durante el agarre, deslizando bajo el cubo en CADA intento del
# Sorter, con o sin esta pared -- confirmado revirtiendo la pared del
# todo y viendo que el fallo seguia igual. Con la cinta ya parandose de
# verdad durante el agarre (SorterDemo._pause_conveyor) y el cierre de
# pinza afinado (self.grasp_close=0.014), se reintenta esta pared con esa
# causa real ya corregida. Mismo perfil que belt_rail_l/r_embudo (2cm
# plano 1cm hacia el canal, rampa recta a 9cm hacia fuera) -- ver
# Documentacion/palos_3_4_rampa_esquema.html.
# OJO signo del crossSection (sesion 2026-09-04, bug real encontrado en
# vivo): con el signo "intuitivo" (X negativo/positivo = hacia fuera segun
# el lado) el Extrusion crecio hacia ADENTRO -- un cubo de prueba se quedo
# atascado en firme justo en la entrada del embudo, confirmado con la
# posicion real de WarehouseSupervisor (parado en seco, sin drift, durante
# 40s seguidos). Mismo "quirk" de inversion de eje X ya documentado en
# sesiones anteriores con esta pieza. Firmado aqui con el signo CONTRARIO
# al intuitivo (L con valores positivos, R con negativos) para compensar.
DEF BELT_RAIL_L_RECTO Solid {
  # Este es el palo 3, el del lado del Sorter (el robot esta en x=0.0, y
  # este carril en x=0.45). ES LA REFERENCIA BUENA: su perfil se ve
  # correcto y de el se copio el sentido del carril R. NO TOCAR el orden de
  # sus vertices (sesion 2026-09-10) -- ver la nota larga en BELT_RAIL_R_RECTO.
  # REVERTIDO a 0.45 (sesion 2026-09-09, causa raiz CONFIRMADA con datos
  # en vivo). El cierre de 1cm por lado de la sesion 2026-09-08 (0.45 ->
  # 0.46, y 0.55 -> 0.54 en el carril R) se valido solo con el CUBO
  # pasando (6cm, cabe de sobra) -- nunca con la PINZA entrando. La pinza
  # abierta mide 8cm de vano (2 x GRIPPER_OPEN=0.04) y, con el giro +90
  # de _adjust_grasp_yaw_for_obstacles (forzado SIEMPRE desde adf75ce),
  # los dedos se abren CRUZANDO el canal: 8cm de pinza en 8cm de hueco,
  # holgura cero. Capturado en el log del Sorter: 1s despues de cerrar y
  # verificar un buen agarre, un dedo marcaba -0.062 (fuera del rango
  # fisico 0-0.04) y el otro 0.0299 -- asimetria tipica de UN dedo
  # trabado contra un obstaculo fijo. Mismo atasco de dedo del
  # 2026-09-04, que entonces se arreglo ENSANCHANDO el canal.
  # NO volver a estrechar por debajo de 10cm entre los dos carriles sin
  # comprobar antes que la pinza ABIERTA y girada +90 sigue entrando.
  # ALTURA (sesion 2026-09-10): base bajada de 0.755 a 0.740 (la superficie
  # real de la cinta) y pared de 0.02 a 0.015. Antes el carril FLOTABA 1,5cm
  # sobre la cinta, asi que su repisa superior quedaba en z=0.775 -- por
  # ENCIMA del centro del cubo (0.770). Para agarrar un cubo de 6cm el dedo
  # tiene que bajar por su costado pasando de la mitad, y si el cubo estaba
  # desplazado hacia un carril el dedo caia justo sobre esa repisa: ese es el
  # dedo trabado de las dislocaciones. Bajar solo la pared no bastaba (con
  # pared 0 la repisa seguia en 0.755). Ahora la repisa queda en 0.755, 2cm
  # mas abajo, y ademas la pared agarra el cubo A RAS de cinta (franja 0-1,5cm
  # de su cara) en vez de dejar 1,5cm de hueco por debajo por el que se puede
  # colar una esquina.
  translation 0.460 1.14 0.740
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.2 0.2 0.2
        roughness 0.5
      }
      geometry Extrusion {
        crossSection [
          0.015 0.0
          0.015 0.015
          0.025 0.015
          0.105 0.09
          0.105 0.0
          0.015 0.0
        ]
        spine [
          0.0 -0.14 0.0
          0.0 0.14 0.0
        ]
      }
    }
  ]
  name "belt_rail_l_recto"
  boundingObject Extrusion {
    crossSection [
      0.015 0.0
      0.015 0.015
      0.025 0.015
      0.105 0.09
      0.105 0.0
      0.015 0.0
    ]
    spine [
      0.0 -0.14 0.0
      0.0 0.14 0.0
    ]
  }
}

DEF BELT_RAIL_R_RECTO Solid {
  # REVERTIDO a 0.55, pareja del carril L -- ver el porque alli.
  #
  # NO TOCAR EL ORDEN DE LOS VERTICES (sesion 2026-09-10, validado en
  # pantalla por el usuario: "ahora parece que esta bien"). Este palo se
  # veia como una L sin rampa y los cubos se le metian DENTRO y se perdian.
  # Causa: una pieza y su espejo NO se ven igual si se deja el mismo orden
  # de vertices -- el espejo invierte las normales, y las caras salen del
  # reves. Para que este se vea como el 3 (que es el bueno, el del lado del
  # Sorter), sus coordenadas van espejadas Y ADEMAS el recorrido invertido,
  # de forma que el area con signo del perfil quede del MISMO signo que la
  # del 3: los dos en -0.0046, y belt_end_stop igual.
  # Antes de dar por bueno cualquier cambio aqui: reiniciar Webots y MIRAR
  # la pieza. En esta misma sesion se invirtio por error el 3 (dando por
  # hecho que el bueno era este) y se vieron huecos los DOS palos.
  # ALTURA (sesion 2026-09-10): mismo cambio que en el carril L (ver alli el
  # porque completo) -- base de 0.755 a 0.740 y pared de 0.02 a 0.015. Los dos
  # tienen que ir SIEMPRE iguales: el canal es simetrico y un desnivel entre
  # ellos convertiria uno de los dos en el obstaculo que se intenta quitar.
  translation 0.540 1.14 0.740
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.2 0.2 0.2
        roughness 0.5
      }
      geometry Extrusion {
        crossSection [
          -0.015 0.0
          -0.105 0.0
          -0.105 0.09
          -0.025 0.015
          -0.015 0.015
          -0.015 0.0
        ]
        spine [
          0.0 -0.14 0.0
          0.0 0.14 0.0
        ]
      }
    }
  ]
  name "belt_rail_r_recto"
  boundingObject Extrusion {
    crossSection [
      -0.015 0.0
      -0.105 0.0
      -0.105 0.09
      -0.025 0.015
      -0.015 0.015
      -0.015 0.0
    ]
    spine [
      0.0 -0.14 0.0
      0.0 0.14 0.0
    ]
  }
}

# ============================================================
# ESTACION 2: SORTER -- AL LADO de la cinta (x=0.0, no en linea con
# ella), base en y=1.00 (mas lejos del Loader que en el primer intento
# -- separacion real entre las dos bases ~1.4m en vez de ~0.9m, a
# peticion del usuario tras verla demasiado apretada en Webots). El
# punto de recogida (tope de la cinta, 0.5,1.25 -- PICKUP_X/Y en
# sorter_demo.py, alejado 15cm mas del original 0.5,1.15 para dar hueco a
# la pinza girada, ver ese fichero) queda a dx=+0.50 dy=+0.25 de la base
# del Sorter -- MISMO desplazamiento relativo ya probado con el solver (la
# cinematica es invariante a donde este la base, solo importa
# target-base). Las 3 cajas quedan hacia ADELANTE
# del Sorter (dx=-0.15/0/+0.15, dy=+0.45, el mismo patron ya probado
# en la caja del Loader), en (x,1.45) -- lejos de la cinta en X, cero
# solape posible con su mesa.
#
# rotation 0.4636 rad (sesion 2026-09-08): base girada 26.6 grados hacia el
# punto de recogida real (atan2(0.25,0.50), ver PICKUP_X/Y y SORTER_BASE_YAW
# en sorter_demo.py -- deben coincidir). Validado sin choques contra
# BELT_RAIL_L/R_RECTO en una copia de este mismo mundo con un cubo en el
# punto de recogida (panda_industrial_cell_base_rotation_test.wbt).
# ============================================================

# Marca visual del punto de encaje de la bandeja (PICKUP_X/PICKUP_Y de
# sorter_demo.py y de sorter_shuttle_supervisor_driver.py). Solo decorativa
# -- 2mm de grosor, sin physics, para ver en Webots donde queda el cubo
# cuando la bandeja lo encaja.
DEF SORTER_TRAY Solid {
  translation 0.5 1.25 0.741
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.9 0.85 0.2
        roughness 0.6
      }
      geometry Box {
        size 0.08 0.08 0.002
      }
    }
  ]
  name "sorter_tray"
}

DEF PANDA_SORTER Panda {
  translation 0.0 1.00 0.74
  rotation 0 0 1 0.4636
  name "Sorter"
  controller "<extern>"
  endEffectorSlot [
    DEF SORTER_HAND PandaHand {
    }
  ]
}
# NOTA (sesion 2026-08-28): esta mesa se ensancho por error pensando que
# el cubo del tope de cinta flotaba sin apoyo -- en el MUNDO AISLADO
# (panda_sorter_grasp_test.wbt, sin ConveyorBelt) eso era cierto y hacia
# falta, pero AQUI el cubo/pared se apoyan en la propia DEF BELT
# ConveyorBelt (translation 0.5 0.85 0, size 1.1 0.3 0.74, rotada 90 en Z
# -> cubre x=[0.35,0.65] y=[0.30,1.40]), no en esta mesa. Ensancharla
# tambien aqui la hacia solaparse ~60cm con la cinta (aviso real del
# usuario mirando Webots). Vuelta a los valores originales, que ya
# cubrian correctamente la base del robot (x=0) y las cajas (x=-0.15..0.15).
Table {
  translation 0.0 1.225 0
  name "table_sorter"
  size 0.5 0.85 0.74
}
DEF OVERHEAD_CAM_SORTER Robot {
  translation 0.25 1.30 2.27
  name "OverheadCamSorter"
  controller "<extern>"
  children [
    Camera {
      rotation 0 1 0 1.5708
      name "overhead_camera_sorter"
      fieldOfView 0.9
      width 320
      height 240
    }
  ]
}

DEF CAJA_ROJA Solid {
  translation 0.0 1.45 0.75
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.6 0.15 0.1
        roughness 0.6
      }
      geometry Box {
        size 0.14 0.14 0.02
      }
    }
  ]
  name "caja_roja"
  boundingObject Box {
    size 0.14 0.14 0.02
  }
}
DEF CAJA_VERDE Solid {
  translation -0.15 1.45 0.75
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.1 0.5 0.15
        roughness 0.6
      }
      geometry Box {
        size 0.14 0.14 0.02
      }
    }
  ]
  name "caja_verde"
  boundingObject Box {
    size 0.14 0.14 0.02
  }
}
DEF CAJA_AZUL Solid {
  translation 0.15 1.45 0.75
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.1 0.2 0.55
        roughness 0.6
      }
      geometry Box {
        size 0.14 0.14 0.02
      }
    }
  ]
  name "caja_azul"
  boundingObject Box {
    size 0.14 0.14 0.02
  }
}

```

## Anexo 2 — `resource/panda_ikpy.urdf` (copiar tal cual)

La cadena del brazo para la cinemática (exportada de Webots y retocada a mano: sin cámara de muñeca, sin los dedos y con un TCP fijo a 0,1034 m de la mano). Toda la calibración (`SNAPSHOT`, `CORRECTION_Z`) depende de él. Copiarlo **carácter a carácter** a `Lab.Panda 2.4/ros2_ws/src/panda_controller/resource/panda_ikpy.urdf`. Comprobación: su SHA-256 empieza por `a2b535c2c8c15623`.

```xml
<robot name="Panda">
  <link name="base_link">
  </link>
  <link name="solid">
    <visual>
      <origin xyz="-0.04 0 0.005" rpy="0 0 0" />
      <geometry>
        <box size="0.23 0.16 0.01" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="-0.04 0 0.005" rpy="0 0 0" />
      <geometry>
        <box size="0.23 0.16 0.01" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0 0.11" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.056" length="0.22" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.11" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.056" length="0.22" />
      </geometry>
    </collision>
  </link>
  <joint name="base_link_solid_joint" type="fixed">
    <parent link="base_link" />
    <child link="solid" />
    <origin xyz="0 0 0" rpy="0 0 0" />
  </joint>
  <joint name="panda_joint1" type="revolute">
    <parent link="solid" />
    <child link="panda_link1" />
    <axis xyz="0 0 1" />
    <limit effort="87" lower="-2.9671" upper="2.9671" velocity="2.5" />
    <origin xyz="0 0 0.14" rpy="0 0 0" />
  </joint>
  <link name="panda_link1">
    <visual>
      <origin xyz="0 0 0.193" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.056" length="0.15" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.193" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.056" length="0.15" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0 0.118" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.056" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.118" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.056" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0 0.268" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.056" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.268" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.056" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 -0.034641 0.113" rpy="0.5236 0 0" />
      <geometry>
        <cylinder radius="0.04" length="0.2" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 -0.034641 0.113" rpy="0.5236 0 0" />
      <geometry>
        <cylinder radius="0.04" length="0.2" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint2" type="revolute">
    <parent link="panda_link1" />
    <child link="panda_link2" />
    <axis xyz="0 0 1" />
    <limit effort="87" lower="-1.8326" upper="1.8326" velocity="2.5" />
    <origin xyz="0 0 0.193" rpy="-1.570796 0 0" />
  </joint>
  <link name="panda_link2">
    <visual>
      <origin xyz="0 -0.195 0" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.055" length="0.11" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 -0.195 0" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.055" length="0.11" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 -0.195 -0.055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.055" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 -0.195 -0.055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.055" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 -0.195 0.055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.055" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 -0.195 0.055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.055" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 -0.069641 0.040621" rpy="-1.047195 0 0" />
      <geometry>
        <cylinder radius="0.04" length="0.16" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 -0.069641 0.040621" rpy="-1.047195 0 0" />
      <geometry>
        <cylinder radius="0.04" length="0.16" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint3" type="revolute">
    <parent link="panda_link2" />
    <child link="panda_link3" />
    <axis xyz="0 0 1" />
    <limit effort="87" lower="-2.9671" upper="2.9671" velocity="2.5" />
    <origin xyz="0 -0.195 0" rpy="1.570796 0 0" />
  </joint>
  <link name="panda_link3">
    <visual>
      <origin xyz="0.0825 0 0.121" rpy="-1.5708 0 0" />
      <geometry>
        <cylinder radius="0.052" length="0.12" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.0825 0 0.121" rpy="-1.5708 0 0" />
      <geometry>
        <cylinder radius="0.052" length="0.12" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.0825 0 0.061" rpy="-1.5708 0 0" />
      <geometry>
        <sphere radius="0.052" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.0825 0 0.061" rpy="-1.5708 0 0" />
      <geometry>
        <sphere radius="0.052" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.0825 0 0.181" rpy="-1.5708 0 0" />
      <geometry>
        <sphere radius="0.052" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.0825 0 0.181" rpy="-1.5708 0 0" />
      <geometry>
        <sphere radius="0.052" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint4" type="revolute">
    <parent link="panda_link3" />
    <child link="panda_link4" />
    <axis xyz="0.000001 0 1" />
    <limit effort="87" lower="-3.1416" upper="-0.4" velocity="2.5" />
    <origin xyz="0.0825 0 0.121" rpy="-1.570776 1.541592 -3.141572" />
  </joint>
  <link name="panda_link4">
    <visual>
      <origin xyz="-0.08 0.115 0" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.053" length="0.1" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="-0.08 0.115 0" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.053" length="0.1" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="-0.08 0.115 -0.05" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.053" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="-0.08 0.115 -0.05" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.053" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="-0.08 0.115 0.05" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.053" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="-0.08 0.115 0.05" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.053" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint5" type="revolute">
    <parent link="panda_link4" />
    <child link="panda_link5" />
    <axis xyz="0 0 1" />
    <limit effort="12" lower="-2.9671" upper="2.9671" velocity="3" />
    <origin xyz="-0.0825 0.125 0" rpy="-1.570796 0 0" />
  </joint>
  <link name="panda_link5">
    <visual>
      <origin xyz="0 0.037 0.259" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.048" length="0.093" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0.037 0.259" rpy="-1.570795 0 0" />
      <geometry>
        <cylinder radius="0.048" length="0.093" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0.037 0.2125" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.048" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0.037 0.2125" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.048" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0.037 0.3055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.048" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0.037 0.3055" rpy="-1.570795 0 0" />
      <geometry>
        <sphere radius="0.048" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0.085 0.154176" rpy="-0.19 0 0" />
      <geometry>
        <box size="0.05 0.04 0.2" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0.085 0.154176" rpy="-0.19 0 0" />
      <geometry>
        <box size="0.05 0.04 0.2" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint6" type="revolute">
    <parent link="panda_link5" />
    <child link="panda_link6" />
    <axis xyz="0 0 1" />
    <limit effort="12" lower="-0.0873" upper="3.8223" velocity="3" />
    <origin xyz="0 0 0.259" rpy="-1.570797 -1.541593 -3.141593" />
  </joint>
  <link name="panda_link6">
    <visual>
      <origin xyz="0.09 -0.015 0" rpy="1.5708 0 0" />
      <geometry>
        <cylinder radius="0.038" length="0.12" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.09 -0.015 0" rpy="1.5708 0 0" />
      <geometry>
        <cylinder radius="0.038" length="0.12" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.09 -0.015 0.06" rpy="1.5708 0 0" />
      <geometry>
        <sphere radius="0.038" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.09 -0.015 0.06" rpy="1.5708 0 0" />
      <geometry>
        <sphere radius="0.038" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.09 -0.015 -0.06" rpy="1.5708 0 0" />
      <geometry>
        <sphere radius="0.038" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.09 -0.015 -0.06" rpy="1.5708 0 0" />
      <geometry>
        <sphere radius="0.038" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_joint7" type="revolute">
    <parent link="panda_link6" />
    <child link="panda_link7" />
    <axis xyz="0 0 1" />
    <limit effort="12" lower="-2.9671" upper="2.9671" velocity="3" />
    <origin xyz="0.088 -0.058 0" rpy="1.570796 -0.79 0" />
  </joint>
  <link name="panda_link7">
    <visual>
      <origin xyz="0 0 0.017" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.044" length="0.044" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.017" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.044" length="0.044" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.042426 0.042427 0.024" rpy="0 0 0.785398" />
      <geometry>
        <box size="0.05 0.06 0.03" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.042426 0.042427 0.024" rpy="0 0 0.785398" />
      <geometry>
        <box size="0.05 0.06 0.03" />
      </geometry>
    </collision>
  </link>
  <link name="panda hand">
    <visual>
      <origin xyz="0 0 0.03" rpy="0 0 -0.785398" />
      <geometry>
        <box size="0.04 0.2 0.07" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.03" rpy="0 0 -0.785398" />
      <geometry>
        <box size="0.04 0.2 0.07" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0.04 0.04 -0.003" rpy="0 0 -0.785398" />
      <geometry>
        <box size="0.057 0.055 0.01" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0.04 0.04 -0.003" rpy="0 0 -0.785398" />
      <geometry>
        <box size="0.057 0.055 0.01" />
      </geometry>
    </collision>
    <visual>
      <origin xyz="0 0 0.004" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.032" length="0.007" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0.004" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.032" length="0.007" />
      </geometry>
    </collision>
  </link>
  <joint name="panda_link7_panda hand_joint" type="fixed">
    <parent link="panda_link7" />
    <child link="panda hand" />
    <origin xyz="0 0 0.107" rpy="0 0 0" />
  </joint>
  <link name="panda_tcp" /><joint name="panda_hand_tcp_joint" type="fixed"><parent link="panda hand" /><child link="panda_tcp" /><origin xyz="0 0 0.1034" rpy="0 0 0" /></joint></robot>
```

_Fin del fichero._
