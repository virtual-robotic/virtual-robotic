#!/usr/bin/env bash
# Version: 2026-09-24 20:23 -- Docker en un segundo disco de una maquina virtual
# Para una maquina virtual Linux sin sitio para las imagenes (~14 GB):
# formatea el segundo disco (/dev/sdb, SOLO si esta vacio, sin formato) y
# hace que Docker guarde ahi sus cosas. Probado el 2026-09-24.
# Uso: sudo bash vm_disco_docker.sh
set -euo pipefail
DISCO=/dev/sdb
DATOS=/srv/docker_datos

[ "$(id -u)" = 0 ] || { echo "Lanzalo con sudo: sudo bash $0"; exit 1; }
[ -b "$DISCO" ] || { echo "No veo $DISCO -- esta conectado el disco nuevo?"; exit 1; }
if lsblk -no FSTYPE "$DISCO" | grep -q .; then
  echo "$DISCO ya tiene formato -- no lo toco (ya se hizo antes?)."
else
  echo "== Formateando $DISCO (disco nuevo y vacio) =="
  mkfs.ext4 -q -L docker_datos "$DISCO"
fi

echo "== Parando Docker =="
systemctl stop docker.socket docker containerd

mkdir -p "$DATOS"
grep -q "LABEL=docker_datos" /etc/fstab || echo "LABEL=docker_datos $DATOS ext4 defaults 0 2" >> /etc/fstab
mountpoint -q "$DATOS" || mount "$DATOS"

for d in docker containerd; do
  if ! grep -q " /var/lib/$d none bind" /etc/fstab; then
    mkdir -p "$DATOS/$d"
    rsync -aHAX "/var/lib/$d/" "$DATOS/$d/"
    echo "$DATOS/$d /var/lib/$d none bind 0 0" >> /etc/fstab
  fi
  mountpoint -q "/var/lib/$d" || mount "/var/lib/$d"
done

echo "== Arrancando Docker =="
systemctl start containerd docker
echo
df -h "$DATOS" | tail -1
echo "Hecho: Docker guarda ya sus imagenes en el disco nuevo."
