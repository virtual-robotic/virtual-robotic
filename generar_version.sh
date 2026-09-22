#!/usr/bin/env bash
# Version: 2026-09-15 -- generar_version.sh (Ver. AAMM.NNNNN a partir de git)
# La llama arrancar_todo.sh antes de tocar Docker. Calcula la version que
# se ve en el panel web y en teleop_gui a partir del propio git -- AAMM
# del ultimo commit + numero total de commits (crece solo, nunca se
# resetea). No hace falta acordarse de subirla a mano: sale sola de lo
# que hay commiteado en cada momento. Los .py que genera estan en
# .gitignore, se recalculan siempre que se lanza el proyecto.
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

AAMM=$(git log -1 --format=%cd --date=format:%y%m 2>/dev/null || echo "0000")
SEQ=$(printf '%05d' "$(git rev-list --count HEAD 2>/dev/null || echo 0)")
VERSION="${AAMM}.${SEQ}"

for DESTINO in \
  "$DIR/Taller_Administracion/app/version.py" \
  "$DIR/Lab.Panda 2.4/ros2_ws/src/panda_controller/panda_controller/version.py"
do
  cat > "$DESTINO" <<EOF
# Generado automaticamente por generar_version.sh -- no editar a mano
VERSION = "$VERSION"
EOF
done

echo "Version generada: Ver. $VERSION"
