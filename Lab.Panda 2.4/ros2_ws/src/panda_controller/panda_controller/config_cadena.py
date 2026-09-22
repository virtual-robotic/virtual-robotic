# Version: 2026-09-18 -- + taller_api_base (URL de Taller_Administracion por maquina)
"""Configuracion de ESTA cadena de produccion, la que se edita en la pestaña
Configuracion del panel (teleop_gui.py). Modulo aparte (sesion 2026-09-14)
porque la leen tres procesos distintos: el propio panel, el Sorter
(sorter_demo.py, para decirle al Taller que maquina ha fabricado cada pieza)
y el supervisor del almacen (letrero en Webots). Sin Tkinter ni rclpy, para
poder importarlo desde cualquiera.

Un fichero por contenedor (hostname), dentro de /workspace (montado del
host): las cadenas comparten el mismo ros2_ws, asi que con una ruta fija se
pisarian entre si (bug real al arrancar la linea 2, 2026-09-13).
"""

import json
import socket

CONFIG_PATH = f'/workspace/config_maquina_{socket.gethostname()}.json'


def leer() -> dict:
    try:
        with open(CONFIG_PATH) as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}  # primer arranque, o fichero corrupto: sin nada guardado todavia


def escribir(cambios: dict) -> None:
    """Actualiza SOLO las claves de 'cambios', sin tocar las demas."""
    datos = leer()
    datos.update(cambios)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(datos, f)


def quitar(clave: str) -> None:
    """Borra UNA entrada del fichero (por ejemplo 'clave_config', para volver a la clave de fabrica)."""
    datos = leer()
    if clave in datos:
        del datos[clave]
        with open(CONFIG_PATH, 'w') as f:
            json.dump(datos, f)


def _entero(clave: str, defecto: int) -> int:
    try:
        return int(leer().get(clave, defecto))
    except (ValueError, TypeError):
        return defecto


def numero_maquina() -> int:
    return _entero('numero_maquina', 1)


def grupo_cadena() -> int:
    return _entero('grupo_cadena', 0)


def etiqueta() -> str:
    return str(leer().get('etiqueta', '') or '')


def idioma() -> str:
    """Codigo de idioma preferido ('es'/'en'/'eu'), pestaña Configuracion.
    Sesion 2026-09-17: de momento solo se guarda la preferencia -- la
    interfaz en si todavia no se traduce, ver teleop_gui.py IDIOMAS."""
    return str(leer().get('idioma', 'es') or 'es')


def taller_api_base() -> str:
    """URL de Taller_Administracion para ESTA maquina, si se ha guardado
    una a mano en la pestaña Configuracion. Vacio ('') significa "usa el
    valor por defecto del contenedor" (el parametro ROS taller_api_base,
    'http://taller_host:8000' -- solo llega hasta el host real de ESTA
    maquina, ver docker-compose.yml). Hace falta rellenar esto cuando la
    linea se lanza en OTRO ordenador de la red y Taller_Administracion
    vive en uno distinto (sesion 2026-09-18)."""
    return str(leer().get('taller_api_base', '') or '')
