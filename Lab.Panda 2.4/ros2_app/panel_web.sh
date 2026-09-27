#!/usr/bin/env bash
# Version: 2026-09-26 18:10 -- panel de control en el navegador (con gestor de ventanas)
# Enciende una pantalla virtual (:99), la sirve por web con noVNC en el puerto
# 6080 y abre en ella el panel de control (teleop_gui). Pensado para Windows,
# que no tiene pantalla de Linux: se ve en http://localhost:6080/vnc.html
# Es seguro llamarlo dos veces: lo que ya este en marcha no se duplica.
# Sin "set -u": el setup.bash de ROS usa variables sin definir y se cortaba.

export DISPLAY=:99
ANCHO_ALTO="${PANEL_WEB_RESOLUCION:-1600x900}"

if ! pgrep -x Xvfb >/dev/null; then
  Xvfb :99 -screen 0 "${ANCHO_ALTO}x24" -nolisten tcp >/tmp/xvfb.log 2>&1 &
  sleep 1
fi
# Gestor de ventanas: da el teclado a cada ventana nueva (sin tener que hacer
# clic antes) y le pone barra de titulo para poder moverla o cerrarla.
# "command -v": si la imagen es anterior y no lo trae, se sigue sin el.
if command -v openbox >/dev/null && ! pgrep -x openbox >/dev/null; then
  openbox >/tmp/openbox.log 2>&1 &
  sleep 1
fi
if ! pgrep -x x11vnc >/dev/null; then
  # -localhost: el VNC solo se oye dentro del contenedor; hacia fuera sale
  # unicamente la pagina de noVNC.
  x11vnc -display :99 -forever -shared -nopw -localhost -quiet >/tmp/x11vnc.log 2>&1 &
  sleep 1
fi
if ! pgrep -f "[w]ebsockify.*6080" >/dev/null; then
  websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
fi

source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash
exec ros2 run panda_controller teleop_gui
