# Version: 2026-09-29 14:39 -- la IP de la Pico se pasa siempre como argumento (no se guarda la de la red en git)
# Cliente de prueba para el servidor TCP de main.py.
# EJECUTAR EN EL PC (no en la Pico), con la Pico ya encendida y conectada al Wi-Fi.
#
# Uso:
#   python3 test_cliente_pc.py <ip_de_la_pico>

import socket
import sys
import time

PICO_PORT = 5001


def enviar(ip, comando):
    with socket.create_connection((ip, PICO_PORT), timeout=3) as s:
        s.sendall(comando.encode("utf-8"))
    print("Enviado:", comando)


def main():
    if len(sys.argv) < 2:
        print('Uso: python3 test_cliente_pc.py <ip_de_la_pico>   (la IP la ensena la Pico al conectarse al Wi-Fi)')
        sys.exit(1)
    ip = sys.argv[1]
    print(f"Probando la Pico en {ip}:{PICO_PORT} ...")

    secuencia = [
        ("R", "debería encenderse el LED rojo"),
        ("G", "debería encenderse el LED verde"),
        ("B", "debería encenderse el LED azul"),
        ("0", "deberían apagarse los tres"),
    ]

    for comando, esperado in secuencia:
        try:
            enviar(ip, comando)
            print("  ->", esperado)
        except OSError as e:
            print(f"  -> ERROR conectando con la Pico: {e}")
            print("     Comprueba: Pico encendida, misma red Wi-Fi, IP correcta.")
            return
        time.sleep(2)

    print("Prueba terminada.")


if __name__ == "__main__":
    main()
