**Idioma:** Español · [English](INSTALAR_WINDOWS.en.md) · [Euskara](INSTALAR_WINDOWS.eu.md)

_Última modificación: 2026-09-27 18:13_

# Instalar en Windows

> **Probado de verdad el 2026-09-23** en un PC físico con Windows 10 22H2 (Intel): instalación limpia desde el repo público, `docker compose up -d --build` y la web en `http://localhost:8000` funcionando, sin errores en el arranque.

Esta guía cubre **la web de pedidos** (`Taller_Administracion`), probada y
funcionando, y al final **la celda con los robots**, que **funciona en Windows desde el
2026-09-24** (primera prueba): ver
[La celda con los robots en Windows](#la-celda-con-los-robots-en-windows).
En Linux se arranca como siempre (ver [LANZAR_PROYECTO.md](LANZAR_PROYECTO.md)).

> **En Windows nunca se lanza `arrancar_todo.sh`**, que es para Linux. Para la
> web sola basta `docker compose`; para todo, `arrancar_windows.bat`.

## Antes de empezar: ¿tu Windows sirve?

Docker Desktop necesita **WSL 2**, que a su vez necesita **Hyper-V**, que a su
vez necesita que el procesador tenga la **virtualización activada**. De ahí
salen los dos casos que hay que mirar antes de perder tiempo:

| Dónde corre tu Windows | ¿Funciona? |
|---|---|
| PC físico | **Sí**, activando la virtualización en la BIOS si hiciera falta |
| Máquina virtual de VirtualBox | **No**, y no tiene arreglo (ver más abajo) |

### Comprobar la virtualización

**Ctrl+Mayús+Esc** (Administrador de tareas) → pestaña **Rendimiento** →
**CPU**. Busca **Virtualización**: tiene que poner **Habilitado**.

Si pone *Deshabilitado*, se activa en la BIOS:

1. Reinicia y entra en la BIOS pulsando repetidamente **F2** o **Supr** nada
   más encender (según el equipo puede ser **F1**, **F10** o **Esc**; la
   pantalla de arranque suele indicarlo).
2. Busca la opción y ponla en **Enabled**:
   - **Intel:** `Intel Virtualization Technology` o `VT-x`.
   - **AMD:** `SVM Mode` o `AMD-V`.

   Suele estar en **Advanced → CPU Configuration**; en portátiles a veces
   está en **Security** o **Configuration**.
3. Guarda y sal (normalmente **F10**).

## Si `wsl` solo te enseña la pantalla de ayuda

Pasa en un Windows 10 recién instalado: `wsl --install`, `wsl --update` e incluso
`wsl -l -v` responden con la lista de opciones en vez de hacer nada. **No es un
error de sintaxis**: significa que las funciones de Windows para WSL no están
activadas. Se activan a mano, en PowerShell **como administrador**:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Cada una debe acabar con *La operación se completó correctamente*. Después
**reinicia** Windows y baja el kernel con `wsl --update --web-download` (ver más
abajo). Otro reinicio, y ya se puede abrir Docker Desktop.

## Instalación

1. **Docker Desktop para Windows**, desde [docker.com](https://www.docker.com/products/docker-desktop/),
   dejando marcada la opción *Use WSL 2*. Reinicia el PC cuando lo pida.
2. Abre Docker Desktop. Si te pide iniciar sesión, **no hace falta cuenta**:
   busca el enlace pequeño de *Skip* o *Continue without signing in*.
   Espera a que abajo a la izquierda ponga **Engine running**.
3. **Git for Windows**, desde [git-scm.com](https://git-scm.com/download/win)
   (vale con «Siguiente» a todo).
4. **Webots** (solo si quieres también los robots; para la web sola no hace
   falta):
   - Descarga el instalador directamente de aquí:
     [webots-R2025a_setup.exe](https://github.com/cyberbotics/webots/releases/download/R2025a/webots-R2025a_setup.exe)
     (unos 250 MB). Tiene que ser **exactamente la versión R2025a**, la misma
     que usa el proyecto; no cojas una más nueva.
   - Ábrelo. Cuando pregunte para quién instalarlo, elige **solo para mí**
     (*Install for me only*): así no pide permisos de administrador.
   - Deja el resto de opciones como vienen y termina la instalación.
   - No hay versión portable (sin instalar) para Windows.
5. **Descarga el proyecto.** En PowerShell, en la carpeta donde lo quieras
   (por ejemplo `C:\carga`):

   ```powershell
   git clone https://github.com/virtual-robotic/virtual-robotic.git
   ```

6. **Arráncalo**, de una de estas dos formas:
   - **Solo la web de pedidos:**

     ```powershell
     cd virtual-robotic\Taller_Administracion
     docker compose up -d --build
     ```

     La primera vez tarda un rato, porque construye la imagen. Para pararla:
     `docker compose down` en esa misma carpeta.
   - **Todo, con los robots:** con **`arrancar_windows.bat`** (ver cómo
     lanzarlo justo debajo, y qué hace en
     [La celda con los robots en Windows](#la-celda-con-los-robots-en-windows)).
     Para pararlo todo: **`cerrar_windows.bat`** (cierra también Webots).

   **Cómo se lanza un fichero `.bat`**, cualquiera de las dos formas:
   - **Con el ratón:** abre la carpeta del proyecto (`virtual-robotic`) en el
     Explorador de archivos y haz **doble clic** en `arrancar_windows.bat`.
     Se abre una ventana negra que va contando lo que hace; **no la cierres**
     hasta que al final ponga *«Presione una tecla para continuar»*.
   - **Desde PowerShell**, dentro de la carpeta del proyecto:

     ```powershell
     .\arrancar_windows.bat
     ```

   Lo mismo para apagar, con `cerrar_windows.bat`. Si Windows avisa de que el
   fichero puede ser peligroso, es porque viene de internet: pulsa *Más
   información* → *Ejecutar de todas formas*.
7. Abre la web en `http://localhost:8000` y entra con **admin** / **admin**.
   Si has arrancado también los robots, el **panel de control** se abre solo
   en el navegador (`http://localhost:6080/vnc.html`) y Webots en su ventana.

   Con `admin` **no se pueden hacer pedidos**: `admin` es el taller (reparte y
   factura). Para pedir, entra como un cliente, por ejemplo **`ere-admin`**
   con contraseña **`1111`**. Más detalles en el README, «Quién hace qué en la
   web».

Lanza los comandos desde **tu propia ventana de PowerShell**, no por SSH ni
desde un servicio: Docker guarda sus credenciales en el Gestor de credenciales
de Windows y, fuera de tu sesión, falla con *«Una sesión de inicio especificada
no existe»*.

## Problemas que nos hemos encontrado de verdad

Aquí solo los de **instalar**. Los que pasan ya con todo en marcha (robots
que no conectan, va lento, el `git pull` falla…) están en
[PROBLEMAS_CONOCIDOS.md](PROBLEMAS_CONOCIDOS.md).

### «Virtualization support not detected»

Docker Desktop no encuentra la virtualización. Dos causas posibles:

- **En un PC físico:** está desactivada en la BIOS. Ver *Comprobar la
  virtualización*, más arriba.
- **Dentro de VirtualBox:** no tiene solución. Ver el apartado siguiente.

### Windows dentro de VirtualBox: no se puede, y no es culpa tuya

**Docker Desktop no puede funcionar con un Windows instalado en VirtualBox.**
WSL 2 necesita Hyper-V, y **VirtualBox no soporta Hyper-V como hipervisor
anidado** ([documentación de Oracle](https://docs.oracle.com/en/virtualization/virtualbox/6.0/admin/nested-virt.html)).

Lo comprobamos a fondo el 2026-09-23 antes de rendirnos: ni activando la
virtualización anidada (`VBoxManage modifyvm "<VM>" --nested-hw-virt on`), ni
subiendo a 8 GB de RAM y 6 procesadores, ni quitando el proveedor de
paravirtualización. El motivo técnico está en el registro de la propia VM
(`Logs/VBox.log`): en la línea `Gst: 8000000a/...`, que es el CPUID de
funciones de virtualización que VirtualBox ofrece al huésped, el valor de EDX
sale `0x000000c8` — **el bit 0 (tablas de página anidadas, NPT) está a cero**,
y el hipervisor de Windows exige esa función para arrancar.

Cuidado con un detalle que despista: dentro de esa VM, Windows responde
`HypervisorPresent = True` y `VirtualizationFirmwareEnabled = True`. Ese
«True» es **engañoso** — corresponde a la interfaz de paravirtualización que
anuncia el propio VirtualBox, no al hipervisor de Windows.

**No depende de que el ordenador sea AMD o Intel.** La limitación es de
VirtualBox, no del procesador: nosotros lo probamos en un AMD, y en un Intel
pasaría lo mismo (allí esa función se llama EPT en vez de NPT, pero VirtualBox
tampoco se la deja usar a Windows).

Para probar en Windows hace falta un **PC con Windows de verdad**.

**Una alternativa, sin probar todavía:** en un equipo Linux, usar **KVM**
(el programa *virt-manager*) en lugar de VirtualBox para la máquina virtual de
Windows. KVM sí le pasa esa función a Windows, así que Docker Desktop debería
arrancar dentro. Eso sí, la parte 3D de una máquina virtual sigue siendo
floja para Webots.

### `wsl --install` acaba en «Error catastrófico»

Pasa al instalar o actualizar WSL, normalmente porque la descarga va por la
Microsoft Store. Reinicia Windows y usa la vía que la salta (baja el
componente de GitHub):

```powershell
wsl --update --web-download
```

Después, `wsl --status` no debe quejarse de que falta el kernel.

### `500 Internal Server Error ... dockerDesktopLinuxEngine/_ping`

Solo significa que **el motor de Docker no está en marcha**; el proyecto no
tiene nada que ver. Abre Docker Desktop, espera a *Engine running* y repite el
comando.

### La web se reinicia sin parar y no responde

Si en el registro (`docker logs taller_admin_api`) ves una y otra vez
*«WatchFiles detected changes … Reloading…»*, es la **recarga automática**
del código, pensada solo para quien lo está programando. En Windows las marcas
de tiempo de los ficheros montados bailan y la recarga entra en bucle. Desde el
2026-09-24 **viene apagada por defecto**; solo se enciende si en
`Taller_Administracion/.env` pones `TALLER_RELOAD=1`. En Windows, no la
enciendas.

## La celda con los robots en Windows

> **Probado el 2026-09-24** en el mismo PC con Windows 10: Webots R2025a
> instalado en Windows, los 6 controladores conectados desde Docker, y el
> panel de control en el navegador moviendo los robots. Es la primera prueba:
> falta usarlo un rato largo.

**Cómo se monta.** Webots va **instalado en el propio Windows** (el de Docker
necesita una pantalla de Linux, que Windows no tiene, y muere con *«could not
connect to display»*). En Docker solo va **ROS 2**, que llega a ese Webots por
la red. El **panel de control** sale en una **pestaña del navegador**, porque
también es una ventana de Linux.

**Qué hay que instalar:** lo mismo que para la web, más **Webots** (paso 4
de la [Instalación](#instalación)).

**Arrancar:** doble clic en **`arrancar_windows.bat`**, en la raíz del proyecto.
Hace, por orden:

1. Comprueba que Docker Desktop está en marcha.
2. Levanta la web de pedidos.
3. Levanta el contenedor de ROS 2 (con
   `Lab.Panda 2.4/.devcontainer/docker-compose.windows.yml`) y compila. La
   primera vez tarda bastante: baja una imagen de varios GB.
4. Abre Webots con el mundo de la celda y espera a que acepte conexiones. La
   primera vez Webots baja texturas; si el **Firewall de Windows** pregunta,
   **permítele** en redes privadas.
5. Lanza la celda y espera a los 6 controladores.
6. Abre el panel en el navegador: `http://localhost:6080/vnc.html`.

**Apagar:** `cerrar_windows.bat`. Desde el 2026-09-26 cierra también la
ventana de Webots. No hace falta guardar nada: al volver a arrancar, la celda
empieza de cero como siempre.

**Si la primera vez Webots sale sin robots** (y con aspecto raro, sin
texturas): está bajando los modelos de internet y el mundo se abrió antes de
tenerlos. Cierra Webots y vuelve a lanzar `arrancar_windows.bat`; la segunda
vez ya los tiene (nos pasó el 2026-09-24). No uses *Reload World*: a nosotros
nos cerró Webots.

**Lo que falta por ver:**

1. **En un PC viejo va lento.** En un portátil de 2012 la simulación va a
   **0.15x–0.22x**, es decir, entre 5 y 7 veces más despacio que la realidad.
   Ese número se ve en la barra de arriba de Webots, al lado del reloj.

   No es que el ordenador no dé más de sí: Webots apenas trabaja. Lo que
   frena son los mensajes entre Webots y los robots, que están dentro de
   Docker, y sobre todo **las imágenes de las dos cámaras**, que viajaban en
   cada paso de la simulación (31 por segundo). **Mejorado el 2026-09-25**:
   ahora mandan 10 por segundo, que es más que suficiente para que los robots
   vean los cubos. En un portátil moderno con Windows 11 la producción casi se
   duplicó (de un cubo cada 43–49 segundos a uno cada 24) y la simulación va
   a la misma velocidad que la realidad (1.0x).

   *Si quieres cambiarlo:* son los dos ficheros de las cámaras de arriba,
   `overhead_camera.urdf` (la del Loader) y `overhead_camera_sorter.urdf` (la
   del Sorter), en la carpeta `Lab.Panda 2.4/ros2_ws/src/panda_controller/resource/`.
   El número está en la línea `<updateRate>10</updateRate>`: son las fotos por
   segundo. Menos fotos, más rápido va todo, pero los robots ven con más
   retraso. Sirve igual en Linux.

   Antes, a esa velocidad, **al Sorter se le rompía el dedo de la pinza** muy
   a menudo. **Ya está arreglado** (2026-09-24): ahora los robots cuentan el
   tiempo con el reloj de Webots y no con el del ordenador, así que aunque
   todo vaya lento, se mueven bien. Si aun así se rompe, rearmar no basta:
   cierra Webots y vuelve a lanzar `arrancar_windows.bat`.

   **Arreglado el 2026-09-26: el Loader se quedaba «bailando» sin fin** al
   empezar un lote, y el panel seguía diciendo que el lote estaba en marcha.
   Al empezar cada lote el robot menea la muñeca 5 segundos para avisar; ese
   rato lo cronometraba mal si el lote arrancaba muy deprisa, y el baile no
   acababa nunca. Con varias cadenas pasaba más. Si te pasa con una versión
   anterior, vuelve a lanzar esa cadena (`arrancar_windows.bat`, o
   `crear_linea_windows.bat` con su número). Ojo: después de cortar un lote a
   medias, el panel tarda **2 minutos** en dejar lanzar otro (espera por si
   aún llega alguna pieza).
2. En el panel del navegador, las ventanitas (p. ej. la clave de
   *Configuración*) ya reciben el teclado solas y tienen barra de título para
   moverlas. Con una versión anterior al 26-09-2026 había que **hacer clic
   dentro del recuadro** antes de escribir.
3. Las Raspberry Pi Pico por USB: en Windows no llegan al contenedor, así que
   el LED del Loader no funcionará (el resto sí, la Pico es opcional).

**Por qué no hace falta tocar el código.** En nuestro mundo **todos los
controladores son `<extern>`**: Webots no los ejecuta, se conectan desde fuera,
por TCP al puerto 1234. La variable `WEBOTS_SHARED_FOLDER` no comparte ninguna
carpeta: solo hace que el conector de ROS 2 use TCP hacia
`host.docker.internal`, que en Windows Docker Desktop hace apuntar al propio
Windows. (De paso nos libra de un fallo conocido del conector con WSL: está en
la otra rama del código, la que no usamos.)

### Varias cadenas en el mismo Windows

**Probado el 2026-09-25 con 4 cadenas a la vez** en un portátil con Windows 11.
Cada cadena tiene su propio Webots, su contenedor de ROS 2 y su panel:

| Cadena | Webots en el puerto | Panel en el navegador |
|---|---|---|
| 1 | 1234 | `http://localhost:6080/vnc.html` |
| 2 | 1235 | `http://localhost:6081/vnc.html` |
| N (hasta 9) | 1233+N | `http://localhost:` 6079+N |

- **Primero la cadena 1**, con `arrancar_windows.bat` como siempre.
- **Para añadir otra:** doble clic en **`crear_linea_windows.bat`**. Te
  pregunta el número de cadena (2 a 9) y su Nº de máquina (que no se repita
  con otra cadena). Abre su propio Webots y su panel.
- **Para apagar solo una:** `cerrar_windows.bat 3` (desde PowerShell, en la
  carpeta del proyecto): para esa cadena y cierra su Webots; las demás siguen.
  Sin número, `cerrar_windows.bat` apaga todas las cadenas, sus Webots y la web.
- **Sin preguntas:** `arrancar_windows.bat 3 30` hace lo mismo que
  `crear_linea_windows.bat` para la cadena 3 con el Nº de máquina 30. El Nº se
  puede dejar y ponerlo luego en la pestaña *Configuración* del panel. Sin
  ningún número, `arrancar_windows.bat` arranca la cadena 1.
- Todas trabajan para **la misma web de pedidos**.

**Cuánto aguanta el ordenador.** Probado el 2026-09-26 en ese portátil
(Windows 11, 30 GB de memoria), con las 4 cadenas fabricando a la vez:

| | Antes (cámaras a 31 fotos/s) | Ahora (cámaras a 10 fotos/s) |
|---|---|---|
| Velocidad de cada cadena (1x = como la realidad) | 0.18x | entre 0.35x y 0.5x |
| Cada cadena saca un cubo cada… | — | ~57 segundos |
| Carga del procesador / de la tarjeta gráfica | 60 % / 55 % | 77 % / 73 % |

Con 4 cadenas el portátil ya va bastante cargado: **4 es un buen techo**. Una
quinta haría ir más despacio a todas.

**Al abrirse, Webots enseña solo la vista 3D** (sin los paneles de edición),
para que quepan varias ventanas. Si quieres ver algún panel, está en el menú
*View*.

### Cadenas en otros ordenadores, trabajando para la web de Windows

Otra forma de tener más cadenas, **probada el 2026-09-24**: la web y una
cadena en el PC con Windows, y **dos cadenas más en otro equipo con Linux**
(una máquina virtual de Linux Mint), las tres trabajando para la **misma web
de pedidos**. En el equipo Linux, cada cadena se crea apuntando a la web del
Windows:

```bash
./crear_linea.sh 3 33 http://IP_DEL_WINDOWS:8000
./crear_linea.sh 4 34 http://IP_DEL_WINDOWS:8000
```

- Cada cadena necesita su propio **Nº de máquina** (aquí 10 la de Windows, 33
  y 34 las de Linux), para que el reparto de pedidos no se cruce.
- El Firewall de Windows tiene que dejar entrar al puerto 8000; se comprueba
  abriendo `http://IP_DEL_WINDOWS:8000` desde el equipo Linux.
- Una máquina virtual con 4 procesadores y 6 GB de RAM mueve dos cadenas, pero
  va al límite. Las imágenes necesitan unos 14 GB de disco: si no caben, ver
  [PROBLEMAS_CONOCIDOS.md](PROBLEMAS_CONOCIDOS.md) (añadir un segundo disco
  para Docker).

## Otra forma (experimental): construirlo desde cero con Claude Code

En vez de descargar el proyecto con `git clone`, se puede pedir a
**Claude Code** que lo vuelva a construir entero, partiendo de una carpeta
vacía. Para eso está el fichero
[Promt Genera Proyecto Virtual Robotic.md](Documentacion/Promt%20Genera%20Proyecto%20Virtual%20Robotic.md):
explica cómo usarlo y trae la orden que hay que pegarle a Claude.

- **Probado el 27-09-2026 solo en Linux** (una máquina virtual Linux Mint):
  Claude lo construyó entero en unas 6 horas de trabajo y funcionó. **En
  Windows no se ha probado todavía**: los `.bat` que genera no se han
  ejecutado nunca en un PC con Windows.
- **No sustituye a la instalación normal**: para usar el proyecto, lo rápido y
  seguro es lo de arriba.
- Es una **foto del proyecto a 27-09-2026**: lo que cambie después no estará.
- Está solo en castellano.
