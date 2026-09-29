#!/usr/bin/env bash
# Version: 2026-09-29 13:40 -- arranca aunque la Pico del Loader del .env no este enchufada. Antes: Webots solo con la vista 3D
# 2026-09-12: arranca todo el proyecto de un tiron -- Taller_Administracion,
# la simulacion (Webots+ROS2), compila si hace falta, lanza la celda
# completa en segundo plano y al final abre el panel de control manual
# (teleop_gui) como unica ventana interactiva. Pensado para "quiero
# probarlo todo sin tener que abrir 5 terminales" (sin hardware real: no
# toca las Raspberry Pi Pico -- si las tienes, se activan desde el panel,
# pestaña Configuracion, ver LANZAR_PROYECTO.md paso 4).
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== 0/5 -- Version (Ver. AAMM.NNNNN, ver panel y teleop_gui) =="
"$DIR/generar_version.sh"

echo "== 1/5 -- Taller_Administracion =="
(cd "$DIR/Taller_Administracion" && docker compose up -d --build)

echo "== 2/5 -- Simulacion (Webots + ROS2) =="
# Webots solo con la vista 3D (sin arbol de escena, consola ni editor), igual
# que en Windows (2026-09-26): Webots lee que paneles se ven de
# worlds/.panda_industrial_cell.wbproj y lo reescribe al salir, asi que se pone
# la plantilla cada vez. Para ver un panel durante la sesion: menu View.
# rm antes del cp: Webots (root dentro de Docker) lo reescribe como root al
# salir y un cp encima fallaba en silencio (visto en la VM, 2026-09-26); la
# carpeta es nuestra, asi que borrarlo si se puede.
rm -f "$DIR/Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"
cp "$DIR/Lab.Panda 2.4/worlds/vista_solo_3d.wbproj.plantilla" "$DIR/Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj" 2>/dev/null || true
xhost +local:docker >/dev/null 2>&1 || echo "(xhost no disponible -- sigo igualmente, puede que Webots no dibuje si no hay sesion grafica)"
# Pico del Loader (2026-09-29): si el .env apunta a una Pico que ahora no esta enchufada, Docker
# no encuentra el dispositivo y NO arranca el contenedor ("error gathering device information").
# En ese caso se arranca sin ella (lo mismo que sin .env) y se avisa; al enchufarla vuelve a usarse.
PICO_LOADER=${LOADER_PICO_DEVICE:-$(grep -E '^LOADER_PICO_DEVICE=' "$DIR/Lab.Panda 2.4/.devcontainer/.env" 2>/dev/null | cut -d= -f2-)}
if [ -n "$PICO_LOADER" ] && [ ! -e "$PICO_LOADER" ]; then
  echo "AVISO: la Pico del Loader ($PICO_LOADER) no esta enchufada -- arranco sin ella."
  export LOADER_PICO_DEVICE=/dev/null
fi
(cd "$DIR/Lab.Panda 2.4/.devcontainer" && docker compose up -d --build)

echo "== 3/5 -- Compilando el paquete ROS2 (necesario la primera vez) =="
docker exec ros2_panda_dev24 bash -c "cd /workspace && colcon build --packages-select panda_controller --symlink-install"

echo "== 4/5 -- Lanzando la celda completa en segundo plano =="

lanzar_celda() {
  # Reinicio del contenedor y no un pkill (2026-09-24): pkill mata "ros2
  # launch" pero deja vivos sus hijos (button_listener, drivers...), que se
  # quedaban conectados a Webots y duplicados en cada relanzamiento (Webots
  # rechazaba luego los nuevos con "Giving up"). Visto en Windows con 3
  # button_listener a la vez. Reiniciar mata todo lo de dentro de golpe.
  docker restart ros2_panda_dev24 >/dev/null
  docker exec ros2_panda_dev24 bash -c "rm -f /tmp/robot_launch.log"
  # docker exec -d NO es una shell interactiva -- no lee ~/.bashrc, asi que
  # hay que sourcear ROS a mano (base + overlay del workspace) o 'ros2' no
  # se encuentra (bug real, visto probando este script).
  docker exec -d ros2_panda_dev24 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"
}

# Devuelve 0 si conectan los 6 controladores dentro del tiempo dado, 1 si no.
esperar_controladores() {
  local segundos="$1" i n
  for i in $(seq 1 "$segundos"); do
    # 'grep -c' devuelve exit code 1 cuando cuenta 0 -- sin el '; true' eso
    # se confundia con un fallo real y duplicaba la salida (bug real visto
    # probando este script).
    n=$(docker exec ros2_panda_dev24 bash -c "grep -c 'Controller successfully connected' /tmp/robot_launch.log 2>/dev/null; true")
    n=${n:-0}
    if [ "$n" -ge 6 ] 2>/dev/null; then
      echo "Listo: 6 controladores conectados (tras ${i}s)."
      return 0
    fi
    sleep 1
  done
  return 1
}

# Webots escribe "extern controller: Waiting for ... connection" por cada robot
# <extern> cuando termina de cargar el mundo (6 en la celda). Lanzar los
# controladores antes les hacia reintentar, dejando una conexion de mas por
# controlador (visto con crear_linea.sh, 2026-09-24; aqui pasaba igual, solo
# que a veces daba tiempo). Se cuenta solo desde el ultimo arranque del
# contenedor, para que no valgan avisos de uno anterior.
esperar_webots() {
  local segundos="$1" desde i n
  desde=$(docker inspect -f '{{.State.StartedAt}}' webots_panda_sim24)
  for i in $(seq 1 "$segundos"); do
    n=$(docker logs --since "$desde" webots_panda_sim24 2>&1 | grep -c "extern controller: Waiting for" || true)
    if [ "${n:-0}" -ge 6 ] 2>/dev/null; then
      echo "Webots ha cargado el mundo (tras ${i}s)."
      return 0
    fi
    sleep 1
  done
  echo "AVISO: Webots no ha terminado de cargar en ${segundos}s -- lanzo igualmente."
}

echo "Esperando a que Webots cargue el mundo (hasta 120s)..."
esperar_webots 120
lanzar_celda
echo "Esperando a que conecten los 6 controladores (hasta 60s)..."
if ! esperar_controladores 60; then
  # Arreglo conocido (visto varias veces, en esta VM y en la maquina real):
  # Webots a veces se queda colgado cargando el mundo la primera vez que
  # arranca en frio -- un 'docker restart' lo desatasca. Se intenta solo,
  # y si tras eso sigue sin conectar, ahi si hace falta mirarlo a mano.
  echo "No han conectado en 60s -- probando el arreglo conocido: reiniciar Webots en frio."
  docker restart webots_panda_sim24 >/dev/null
  echo "Esperando a que Webots vuelva a cargar el mundo (hasta 120s)..."
  esperar_webots 120
  lanzar_celda
  echo "Reintentando la espera de los 6 controladores (hasta 60s mas)..."
  if ! esperar_controladores 60; then
    echo "AVISO: sigue sin conectar tras el reinicio en frio."
    echo "Revisa el log de ROS2 con: docker exec ros2_panda_dev24 cat /tmp/robot_launch.log"
    echo "Y el de Webots con:        docker logs webots_panda_sim24 --tail 30"
    echo "Sigo igualmente al panel de control por si acaso, pero probablemente falle tambien."
  fi
fi

echo "== 5/5 -- Abriendo el panel de control manual =="
docker exec -it ros2_panda_dev24 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && ros2 run panda_controller teleop_gui"
