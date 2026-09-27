**Idioma:** Español · [English](PROBLEMAS_CONOCIDOS.en.md) · [Euskara](PROBLEMAS_CONOCIDOS.eu.md)

_Última modificación: 2026-09-26 18:25_

# Problemas conocidos

Solo lo que nos ha pasado de verdad, con su arreglo. Es el **único sitio**
con los problemas y sus soluciones: las guías enlazan aquí.

Los problemas de **instalar** en Windows (la virtualización, WSL, Docker
Desktop…) están en su guía: [INSTALAR_WINDOWS.md](INSTALAR_WINDOWS.md),
apartado «Problemas que nos hemos encontrado de verdad».

## Celda con robots (Linux)

**Los controladores no conectan / Webots se queda cargando la primera vez.**
Pasa a veces en frío. `arrancar_todo.sh` y `crear_linea.sh` ya lo intentan
solos con un `docker restart` de Webots. A mano:
`docker restart webots_panda_sim24 ros2_panda_dev24` y volver a lanzar.

**Tras relanzar, Webots dice «Giving up» o «Address already in use».**
Quedaron vivos controladores de la vez anterior (un `pkill` de `ros2 launch`
no mata a sus hijos). Arreglo: `docker restart` de los dos contenedores
(Webots y ROS 2) y volver a lanzar.

**El dedo de la pinza del Sorter se rompe.** Rearmar no sirve: hay que
reiniciar Webots. En un equipo lento pasaba muy a menudo; desde el 2026-09-24
los robots miden sus esperas con el reloj de la simulación y ya no (ver
*Windows*, más abajo).

**Hay procesos repetidos dentro del contenedor de ROS 2** (varios
`button_listener`). Pasaba al relanzar la celda: el script mataba el
`ros2 launch` pero no a sus hijos. Desde el 2026-09-24 los scripts reinician
el contenedor antes de lanzar.

**En una máquina virtual no hay sitio para Docker.** Las imágenes de Webots
y ROS 2 ocupan unos 14 GB. Si el disco de la máquina virtual no da para más,
lo más fácil y seguro es **darle un segundo disco solo para Docker**, sin
tocar el del sistema:

1. Apaga la máquina virtual.
2. En VirtualBox, crea un disco nuevo (40 GB van bien) y conéctalo a la
   máquina. Si VirtualBox no te deja, es que al controlador *SATA* le falta un
   hueco: en la configuración, súbele los puertos a 2.
3. Enciende la máquina virtual y, dentro, pon ese disco como el sitio donde
   Docker guarda sus cosas (las carpetas `/var/lib/docker` y
   `/var/lib/containerd`).

Así lo hicimos el 2026-09-24: el paso 3 lo hace el script `vm_disco_docker.sh` del proyecto,
que se lanza con `sudo`.

## Web de pedidos

**Se reinicia sin parar («WatchFiles detected changes … Reloading»).**
Es la recarga automática para programar. Desde el 2026-09-24 viene apagada;
solo se enciende con `TALLER_RELOAD=1` en `Taller_Administracion/.env`.
En Windows, no la enciendas.

**En el almacén no aparecen arandelas (u otro producto).** No es un fallo:
cada unidad fabricada se asigna al momento a los pedidos que la esperan, así
que el stock se queda en 0 mientras haya pedidos pendientes.

**Los vídeos de la portada no arrancan en Safari (Mac o iPhone).** Safari
pide los vídeos a trozos y nuestra web solo sabía mandarlos enteros (Chrome y
Firefox se conforman con eso). Arreglado el 2026-09-26, pero **sin comprobar
todavía en un Safari de verdad**: no tenemos un Mac para probarlo. Si lo
pruebas, cuéntanos si funciona.

## Windows

**Va lento (Webots a 0.15x–0.22x en un PC viejo).** No es que el ordenador no
dé más de sí: Webots espera muchas veces por segundo a que le contesten los
robots, que están dentro de Docker, y en Windows esos mensajes van despacio.
Lo que más pesaba eran las fotos de las dos cámaras que miran desde arriba,
que se mandaban sin parar. **Mejorado el 2026-09-25** (10 fotos por segundo):
en un portátil con Windows 11 una cadena pasó a ir a la misma velocidad que la
realidad (1x), y con **4 cadenas a la vez** cada una va a 0.35x–0.5x (antes
0.18x). Cómo cambiar las fotos por segundo: ver [INSTALAR_WINDOWS.md](INSTALAR_WINDOWS.md).

**El Loader se queda meneando la muñeca sin parar al empezar un lote, y el
panel dice que el lote sigue en marcha.** Arreglado el 2026-09-26. Al empezar
cada lote el robot menea la muñeca 5 segundos para avisar, y ese rato lo
cronometraba mal si el lote arrancaba muy deprisa (pasaba más con varias
cadenas). Con una versión anterior: vuelve a lanzar esa cadena. Tras cortar un
lote a medias, el panel tarda **2 minutos** en dejar lanzar otro.

**La primera vez Webots se queda en «Downloading assets 72 %».** Se ha
quedado colgado bajando dibujos de la escena de internet. Ciérralo (si no
responde, `cerrar_windows.bat` ya lo cierra) y vuelve a lanzar: lo que bajó
se guarda, y la segunda vez carga.

**El `git pull` falla por un `.wbproj`.** Webots reescribe esos ficheros; desde
el 2026-09-24 git ya no los sigue. Si pasa con un clon antiguo:
`git checkout -- "Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"` y otra
vez `git pull`.

**El `git pull` pide usuario y falla la autenticación.** Borra la clave
guardada con `cmdkey /delete:git:http://IP_DE_GITEA:3000` y repite.

Los problemas de instalación (virtualización, WSL que solo enseña la ayuda,
«Error catastrófico», `500 … _ping`, VirtualBox) están en
[INSTALAR_WINDOWS.md](INSTALAR_WINDOWS.md).
