#!/usr/bin/env bash
# Version: 2026-09-26 11:57 -- Webots solo con la vista 3D (plantilla .wbproj, como en Windows)
# Hace de un tiron los pasos 1 a 4 de Documentacion/anadir_cadena_produccion.html:
# copia la plantilla .devcontainer2, le cambia los tres nombres (cajas, red,
# ROS_DOMAIN_ID) para que no choque con ninguna otra linea, la enciende,
# compila si hace falta y lanza la celda -- y de paso, si se le dan, deja ya
# escritos el Nº Maquina / Grupo Cadena / URL de Taller_Administracion (el
# mismo fichero que edita la pestaña Configuracion del panel), para no tener
# que rellenarlos a mano tras abrir la ventana.
#
# Si ".devcontainerN" YA existe (una linea que se creo otro dia), no copia
# nada ni la vuelve a renombrar -- simplemente la enciende y la lanza tal
# cual esta, como un "volver a entrar". Asi sirve tanto para crear una
# linea nueva como para reabrir una que ya tenias, sin tener que acordarte
# de los comandos sueltos de docker compose / docker exec.
#
# Uso: crear_linea.sh <N> [numero_maquina] [url_taller_administracion] [grupo_cadena]
#
#   N                          Obligatorio. Numero de la linea nueva (3, 4...
#                              nunca 1 ni 2, esas ya existen). ROS_DOMAIN_ID
#                              de esa linea sera 30+N (32 para la 2, 33 para
#                              la 3... mismo criterio que anadir_cadena_produccion.html).
#   numero_maquina              Opcional, 0 a 99.
#   url_taller_administracion   Opcional. Solo hace falta si esta linea vive en
#                               OTRO ordenador distinto del que tiene Taller_Administracion
#                               (ver "otro ordenador fisico" en anadir_cadena_produccion.html).
#                               P.ej. http://192.168.1.XXX:8000
#   grupo_cadena                Opcional, 0 a 99.
#
# Al final abre el panel de control (ventana interactiva, en primer plano) --
# igual que el paso 5/5 de arrancar_todo.sh.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PANDA_DIR="$DIR/Lab.Panda 2.4"
PLANTILLA="$PANDA_DIR/.devcontainer2"

uso() {
  cat <<EOF
Uso: $(basename "$0") <N> [numero_maquina] [url_taller_administracion] [grupo_cadena]

Ejemplos:
  $(basename "$0") 3
  $(basename "$0") 3 3
  $(basename "$0") 3 3 http://192.168.1.XXX:8000
  $(basename "$0") 3 3 http://192.168.1.XXX:8000 0
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  uso
  exit 0
fi
if [ "${1:-}" = "" ]; then
  uso
  exit 1
fi

N="$1"
NUMERO_MAQUINA="${2:-}"
URL_TALLER="${3:-}"
GRUPO_CADENA="${4:-}"

if ! [[ "$N" =~ ^[0-9]+$ ]] || [ "$N" -lt 3 ] || [ "$N" -gt 69 ]; then
  echo "Error: N tiene que ser un numero entre 3 y 69 (1 y 2 ya existen; ROS_DOMAIN_ID = 30+N tiene que quedar en un rango valido)." >&2
  exit 1
fi
for valor in "$NUMERO_MAQUINA" "$GRUPO_CADENA"; do
  if [ -n "$valor" ] && { ! [[ "$valor" =~ ^[0-9]+$ ]] || [ "$valor" -lt 0 ] || [ "$valor" -gt 99 ]; }; then
    echo "Error: '$valor' tiene que ser un numero entre 0 y 99." >&2
    exit 1
  fi
done

DESTINO="$PANDA_DIR/.devcontainer$N"
CONTENEDOR="ros2_panda_dev24_linea$N"
WEBOTS_CONTENEDOR="webots_panda_sim24_linea$N"
DOMINIO=$((30 + N))

if [ -d "$DESTINO" ]; then
  echo "== '.devcontainer$N' ya existe -- la vuelvo a arrancar tal cual esta (sin tocar plantilla ni nombres) =="
else
  if [ ! -d "$PLANTILLA" ]; then
    echo "Error: no encuentro la plantilla '$PLANTILLA'." >&2
    exit 1
  fi

  echo "== 1/6 -- Copiando la plantilla a .devcontainer$N =="
  cp -r "$PLANTILLA" "$DESTINO"
  # Es la prueba de la topologia de Windows solo para la cadena 2 (puerto 1235):
  # copiada a otra cadena seria un fichero con datos que no le corresponden.
  rm -f "$DESTINO/docker-compose.windows-sim.yml"

  echo "== 2/6 -- Renombrando cajas/red/dominio (linea2 -> linea$N, ROS_DOMAIN_ID 32 -> $DOMINIO) =="
  sed -i -e "s/linea2/linea$N/g" -e "s/ROS_DOMAIN_ID=32/ROS_DOMAIN_ID=$DOMINIO/g" "$DESTINO/docker-compose.yml"
fi

# Genera Ver. AAMM.NNNNN (Taller_Administracion/app/version.py y version.py del panel de
# control). Sin esto el panel de control de la linea nueva pone "Ver. sin-version": ese
# fichero no esta en git y solo lo creaba arrancar_todo.sh.
"$DIR/generar_version.sh" >/dev/null 2>&1 || echo "(no se pudo generar la version -- el panel pondra 'sin-version')"

echo "== 3/6 -- Encendiendo la linea $N =="
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
(cd "$DESTINO" && docker compose up -d --build)

echo "== 4/6 -- Compilando el paquete ROS2 (necesario la primera vez que se usa este workspace) =="
# El ros2_ws es COMPARTIDO entre todas las lineas de esta maquina (mismo
# codigo, mismo install/ -- ver comentario en docker-compose.yml). Si ya
# lo compilo otra linea antes, esto es practicamente instantaneo; si esta
# maquina nunca ha compilado nada (p.ej. usar crear_linea.sh como PRIMER
# paso en una instalacion limpia, sin haber pasado antes por
# arrancar_todo.sh), aqui es donde se hace -- sin este paso, el panel
# fallaba con "setup.bash: No such file or directory" (visto en vivo en
# la VM de pruebas, sesion 2026-09-18).
docker exec "$CONTENEDOR" bash -c "source /opt/ros/humble/setup.bash && cd /workspace && colcon build --packages-select panda_controller --symlink-install"

if [ -n "$NUMERO_MAQUINA$URL_TALLER$GRUPO_CADENA" ]; then
  echo "== Dejando ya configurada esta linea (Nº Maquina / Grupo Cadena / URL Taller_Administracion) =="
  HOST_CONTENEDOR=$(docker exec "$CONTENEDOR" hostname)
  docker exec -i "$CONTENEDOR" python3 - "$HOST_CONTENEDOR" "$NUMERO_MAQUINA" "$URL_TALLER" "$GRUPO_CADENA" <<'PYEOF'
import json
import sys

host, numero_maquina, url, grupo_cadena = sys.argv[1:5]
ruta = f"/workspace/config_maquina_{host}.json"

try:
    with open(ruta) as f:
        datos = json.load(f)
    if not isinstance(datos, dict):
        datos = {}
except (OSError, ValueError):
    datos = {}

if numero_maquina:
    datos['numero_maquina'] = int(numero_maquina)
if url:
    datos['taller_api_base'] = url
if grupo_cadena:
    datos['grupo_cadena'] = int(grupo_cadena)

with open(ruta, 'w') as f:
    json.dump(datos, f)

print(f"Escrito {ruta}: {json.dumps(datos, ensure_ascii=False)}")
PYEOF
fi

echo "== 5/6 -- Lanzando la celda completa en segundo plano =="

lanzar_celda() {
  # Reinicio del contenedor y no un pkill: mata tambien los hijos de un
  # "ros2 launch" anterior (ver arrancar_todo.sh, 2026-09-24).
  docker restart "$CONTENEDOR" >/dev/null
  docker exec "$CONTENEDOR" bash -c "rm -f /tmp/robot_launch.log"
  docker exec -d "$CONTENEDOR" bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"
}

esperar_controladores() {
  local segundos="$1" i n
  for i in $(seq 1 "$segundos"); do
    n=$(docker exec "$CONTENEDOR" bash -c "grep -c 'Controller successfully connected' /tmp/robot_launch.log 2>/dev/null; true")
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
# controlador (visto con crear_linea.sh 3, 2026-09-24). Se cuenta solo desde el
# ultimo arranque del contenedor, para que no valgan avisos de uno anterior.
esperar_webots() {
  local segundos="$1" desde i n
  desde=$(docker inspect -f '{{.State.StartedAt}}' "$WEBOTS_CONTENEDOR")
  for i in $(seq 1 "$segundos"); do
    n=$(docker logs --since "$desde" "$WEBOTS_CONTENEDOR" 2>&1 | grep -c "extern controller: Waiting for" || true)
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
  # Mismo arreglo conocido que arrancar_todo.sh: Webots a veces se queda
  # colgado cargando el mundo la primera vez que arranca en frio.
  echo "No han conectado en 60s -- probando el arreglo conocido: reiniciar Webots en frio."
  docker restart "$WEBOTS_CONTENEDOR" >/dev/null
  echo "Esperando a que Webots vuelva a cargar el mundo (hasta 120s)..."
  esperar_webots 120
  lanzar_celda
  echo "Reintentando la espera de los 6 controladores (hasta 60s mas)..."
  if ! esperar_controladores 60; then
    echo "AVISO: sigue sin conectar tras el reinicio en frio."
    echo "Revisa el log de ROS2 con: docker exec $CONTENEDOR cat /tmp/robot_launch.log"
    echo "Y el de Webots con:        docker logs webots_panda_sim24_linea$N --tail 30"
    echo "Sigo igualmente al panel de control por si acaso, pero probablemente falle tambien."
  fi
fi

echo "== 6/6 -- Abriendo el panel de control manual de la linea $N =="
docker exec -it "$CONTENEDOR" bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && ros2 run panda_controller teleop_gui"
