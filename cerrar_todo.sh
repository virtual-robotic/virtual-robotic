#!/usr/bin/env bash
# Version: 2026-09-14 20:13 -- cerrar_todo.sh (apaga tambien las cadenas 2, 3...)
# 2026-09-12: para y elimina los contenedores de los dos proyectos
# (Lab.Panda 2.4 y Taller_Administracion). Complementario a
# arrancar_todo.sh. Seguro de ejecutar aunque no haya nada corriendo --
# no aborta si un "docker compose down" no encuentra nada que parar.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cadenas extra (.devcontainer2, .devcontainer3...), sesion 2026-09-14:
# antes solo se apagaba la 1 y la 2 se quedaba encendida.
for extra in "$DIR/Lab.Panda 2.4"/.devcontainer[0-9]*; do
  [ -f "$extra/docker-compose.yml" ] || continue
  echo "== Parando cadena extra $(basename "$extra") =="
  (cd "$extra" && docker compose down)
done

echo "== Parando Lab.Panda 2.4 (simulacion) =="
(cd "$DIR/Lab.Panda 2.4/.devcontainer" && docker compose down)

echo "== Parando Taller_Administracion =="
(cd "$DIR/Taller_Administracion" && docker compose down)

echo
echo "Comprobando que no quede nada del proyecto corriendo:"
restos=$(docker ps -a --format '{{.Names}}' | grep -E "^(webots_panda_sim24|ros2_panda_dev24)(_linea[0-9]+)?$|^taller_admin_api$")
if [ -n "$restos" ]; then
  echo "AVISO: todavia queda esto por limpiar a mano:"
  echo "$restos"
else
  echo "Todo limpio."
fi
