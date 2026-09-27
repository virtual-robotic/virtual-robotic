#!/usr/bin/env python3
# Version: 2026-09-26 11:38 -- panel de control: traducciones EN/EU de restablecer la clave
"""
Teleoperacion manual del Panda con botones (Tkinter), en vez de teclado
(`teleop_manual.py`). Mismo motor por debajo (misma cinematica DH
modificada duplicada, mismo filtro de salto articular grande para no
"escapar" de golpe -- ver teleop_manual.py para el porque de cada uno de
estos detalles), pero controlado con clicks de raton sobre una ventana.

Necesita que el DISPLAY este reenviado al contenedor (ya lo esta: es el
mismo mecanismo con el que se ve la ventana de Webots, ver
`.devcontainer/docker-compose.yml` -- DISPLAY + /tmp/.X11-unix +
.Xauthority montados en ros2_panda_dev).

Como lanzarlo (con Webots en PLAY y `robot_launch.py` corriendo):

    ros2 run panda_controller teleop_gui
"""

import hashlib
import hmac
import json
import math
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, Float64, String, Bool

from panda_controller import config_cadena
from panda_controller.overhead_vision import OverheadLocator, COLOR_NAMES
from panda_controller.sorter_demo import LOTE_COLOR_QOS
try:
    # Generado por generar_version.sh (raiz del repo) a partir de git --
    # no esta en el repo, ver .gitignore. Si falta (colcon build sin
    # pasar por arrancar_todo.sh) no debe romper el arranque por esto.
    from panda_controller.version import VERSION
except ImportError:
    VERSION = "sin-version"

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk

# Paleta industrial (sesion 2026-08-27, mismo aspecto que estop_panel.py):
# se reutiliza el panel de teleoperacion tal cual, no uno nuevo, para que
# STOP/REARME y el jog vivan en la misma ventana.
BG = '#1c1c1c'
PANEL_BG = '#2a2a2a'
YELLOW = '#f5c400'
RED = '#c81e1e'
RED_DARK = '#8f1414'
GREEN = '#2e9e3b'
GREY = '#555555'
GREY_TEXT = '#aaaaaa'
TEXT_LIGHT = '#eaeaea'

# Centinela para 'only_color' cuando el producto elegido no tiene LED
# asignado en Taller_Administracion (sesion 2026-09-15): tiene que ser
# alfabetico (loader_demo.py exige only_color.isalpha()) y no coincidir
# con ningun codigo de color real -- se manda igual que un color de
# verdad (fija el LED de producto, cycles=piezas exactas), pero
# led_publisher_usb.py lo reconoce como caso especial y hace parpadear
# el LED en blanco en vez de un color fijo (no hay color que mostrar).
# Ni sorter_demo.py ni loader_demo.py necesitan saber de este caso -- para
# ellos es un 'only_color' cualquiera, ver _lanzar_produccion.
SIN_COLOR = 'SINCOLOR'

# Colores reales de cada LED, para la pestaña "Raspberry Pi Pico" (sesion
# 2026-09-17, a peticion del usuario: "esto es porque no tenemos la pi
# pico con todos los robot" -- sin Pico fisica conectada no hay forma de
# ver que color estaria encendiendo, asi que el panel simula el mismo
# comportamiento con un dibujo. Mismo vocabulario de comandos que aceptan
# de verdad led_publisher.py/led_publisher_usb.py (ver esos ficheros);
# los RGB de amarillo/magenta/cian calibrados a ojo estan copiados tal
# cual de COLOR_A_RGB en led_publisher_usb.py.
LED_AGARRE_COLOR = {
    'r': '#ff3b30', 'rojo': '#ff3b30', 'red': '#ff3b30',
    'g': '#34c759', 'verde': '#34c759', 'green': '#34c759',
    'b': '#0a84ff', 'azul': '#0a84ff', 'blue': '#0a84ff',
}
LED_PRODUCTO_COLOR = dict(LED_AGARRE_COLOR, y='#ff3c00', m='#c800c8', c='#00c8c8', w='#ffffff')
LED_APAGADO = ('0', 'apagar', 'off', 'rearme', 'rearm', '')
LED_ALARMA = ('parada', 'stop')

# Umbral de disparo del HC-SR04 del Loader, copiado tal cual de
# DISTANCIA_MIN_CM en Rasberry_Pi_Pico_USB_Loader/main.py (sesion
# 2026-09-18, fader simulador en la pestaña Raspberry Pi Pico) -- si ese
# valor cambia en el firmware, cambiarlo tambien aqui para que el
# simulador dispare en el mismo punto que la Pico real.
UMBRAL_HCSR04_CM = 10

# Numero de maquina de ESTA celda (sesion 2026-09-13, ver
# Documentacion/analisis_ampliacion_taller.md): reparte que pedidos
# fabrica cada celda cuando haya mas de una -- con una sola celda (estado
# actual) no tiene efecto practico, siempre coge todo. Persistido en un
# fichero dentro de /workspace (montado del host, ver docker-compose.yml
# de Lab.Panda 2.4), para que se mantenga aunque se reinicie el
# contenedor -- a proposito NO se guarda dentro de build/install/log
# (esos se borran con cada colcon build limpio).
# Bug real encontrado al arrancar la linea 2 (sesion 2026-09-13): las dos
# lineas comparten el MISMO ../ros2_ws (mismo codigo, a proposito, ver
# .devcontainer2/docker-compose.yml) -- con una ruta fija, las dos
# escribirian el mismo fichero y se pisarian el numero de maquina entre
# si. Se separa por hostname del contenedor, que YA es distinto por
# diseno (ros2_panda_dev24 / ros2_panda_dev24_linea2, container_name en
# cada docker-compose.yml) -- no hace falta ninguna variable de entorno
# nueva.
CONFIG_MAQUINA_PATH = config_cadena.CONFIG_PATH
# Rango de los desplegables Nº Maquina y Grupo Cadena (peticion explicita
# del usuario, sesion 2026-09-14: los dos de 0 a 99; antes Nº Maquina era
# 1..5). OJO con Nº Maquina 0: en Taller_Administracion 0 significa
# "pedido libre", asi que el servidor rechaza reclamar con 0 -- se deja
# elegir, pero con aviso (ver guardar_numero_maquina).
MIN_MAQUINA, MAX_MAQUINA = 0, 99
MIN_GRUPO_CADENA, MAX_GRUPO_CADENA = 0, 99
# Clave maestra para poder GUARDAR el Nº Maquina (no para nada mas) --
# es un control fisico compartido, sin login como la web, asi que
# cualquiera que se acerque al panel podria cambiarlo sin querer. Mismo
# valor por defecto que TALLER_MASTER_PASSWORD en Taller_Administracion
# a proposito, para que sea la misma clave que ya conoce quien usa el
# proyecto -- no relacionado tecnicamente (viven en proyectos distintos),
# es solo una convencion para no tener dos claves distintas que recordar.
CLAVE_MAQUINA = '1111'
# Largo minimo de una clave nueva (pestaña Configuracion, "Cambiar clave").
MIN_LARGO_CLAVE = 4
# Restablecer la clave con el boton de parada (2026-09-21): manteniendolo SEGUNDOS_RESET_CLAVE segundos
# (el fisico de la Pico USB del Loader -- lo mide la propia Pico, ver Rasberry_Pi_Pico_USB_Loader/main.py --
# o cualquiera de los dos simulados de la pestaña Raspberry Pi Pico) el panel ofrece volver a la clave de
# fabrica. Solo con la pestaña Configuracion o Raspberry Pi Pico abierta y tras confirmar.
SEGUNDOS_RESET_CLAVE = 10
SEGUNDOS_AVISO_OLED = 6  # cuanto rato se ve 'Contrasena reseteada' antes de volver al texto anterior
# La fuente de la OLED es ASCII (sin ñ): por eso 'Contrasena'.
AVISO_OLED_CLAVE = 'MSG:Contrasena|reseteada'


def _hash_clave(clave: str, sal_hex: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), bytes.fromhex(sal_hex), 100_000).hex()


def _clave_correcta(clave: str) -> bool:
    """La clave que desbloquea la pestaña Configuracion: la que se haya cambiado desde el propio
    panel (guardada como sal + hash en el config de ESTA linea, nunca en claro) o, si nunca se ha
    cambiado, CLAVE_MAQUINA. Olvidada la nueva: borrar la entrada 'clave_config' del fichero
    config_maquina*.json de la linea devuelve la de fabrica."""
    guardada = _leer_config_panel().get('clave_config')
    if isinstance(guardada, dict) and guardada.get('sal') and guardada.get('hash'):
        try:
            return hmac.compare_digest(_hash_clave(clave, guardada['sal']), guardada['hash'])
        except ValueError:
            return False
    return hmac.compare_digest(clave.encode('utf-8'), CLAVE_MAQUINA.encode('utf-8'))


def _guardar_clave_config(clave: str) -> None:
    sal = os.urandom(16).hex()
    _escribir_config_panel({'clave_config': {'sal': sal, 'hash': _hash_clave(clave, sal)}})


def _restablecer_clave_config() -> None:
    """Vuelve a la clave de fabrica (CLAVE_MAQUINA) borrando la entrada 'clave_config' del config."""
    config_cadena.quitar('clave_config')


# Lectura/escritura del fichero: en config_cadena.py desde el 2026-09-14,
# porque tambien lo leen sorter_demo.py y el supervisor del almacen.
_leer_config_panel = config_cadena.leer
_escribir_config_panel = config_cadena.escribir
_cargar_numero_maquina = config_cadena.numero_maquina
_cargar_grupo_cadena = config_cadena.grupo_cadena  # ver fetch_pedidos_pendientes
_cargar_etiqueta = config_cadena.etiqueta
_cargar_idioma = config_cadena.idioma
_cargar_taller_api_base = config_cadena.taller_api_base


def _guardar_numero_maquina(numero: int) -> None:
    _escribir_config_panel({'numero_maquina': numero})


def _guardar_grupo_cadena(numero: int) -> None:
    _escribir_config_panel({'grupo_cadena': numero})


def _guardar_etiqueta(texto: str) -> None:
    _escribir_config_panel({'etiqueta': texto})


def _guardar_taller_api_base(url: str) -> None:
    _escribir_config_panel({'taller_api_base': url})


def _guardar_idioma(codigo: str) -> None:
    _escribir_config_panel({'idioma': codigo})


# Idiomas ofrecidos en la pestaña Configuracion (sesion 2026-09-17, a
# peticion del usuario: "que idiomas pondrias"). De momento el panel
# SOLO guarda la preferencia -- no hay todavia traduccion real de la
# interfaz, ver _construir_pestana_config. Español por ser el idioma en
# el que esta todo escrito hoy; Euskera por donde vive el proyecto (Ria
# de Gernika); Ingles para que cualquiera que vea el repo lo entienda.
IDIOMAS = {'es': 'Español', 'en': 'English', 'eu': 'Euskera'}
IDIOMAS_INVERSO = {nombre: codigo for codigo, nombre in IDIOMAS.items()}

# Traducciones del panel (sesion 2026-09-17, a peticion del usuario: "que
# funcione el traductor" -- hasta ahora el selector de arriba solo
# guardaba la preferencia). El texto en castellano de cada sitio de la UI
# es DIRECTAMENTE la clave del diccionario (ver TeleopApp.t) -- asi no
# hace falta inventar ni mantener nombres de clave aparte: donde antes
# habia texto='...' ahora hay texto=self.t('...'), y si algun dia se anade
# un texto sin entrada aqui, self.t() devuelve el propio castellano en vez
# de romper. Solo cubre lo que ve el operario (etiquetas, botones,
# mensajes de estado, dialogos); el log de auditoria (self._audit) y los
# logs de ROS (self.node.get_logger()) se quedan en castellano a
# proposito -- son para depurar, no para el operario.
TRADUCCIONES = {
    'en': {
        'PANEL DE CONTROL MANUAL': 'MANUAL CONTROL PANEL',
        'EN MARCHA': 'RUNNING',
        'Pantalla Pico': 'Pico display',
        'PARADO': 'STOPPED',
        'PARADA\nDE EMERGENCIA': 'EMERGENCY\nSTOP',
        'REARME': 'RESET',
        'Nombre de la cadena:': 'Line name:',
        'URL de Taller_Administracion:': 'Taller_Administracion URL:',
        'Robot controlado:': 'Controlling robot:',
        'Listo.': 'Ready.',
        'Mover TCP (mundo)': 'Move TCP (world)',
        'X+\nadelante': 'X+\nforward',
        'X-\natras': 'X-\nback',
        'Z+\nsubir': 'Z+\nup',
        'Z-\nbajar': 'Z-\ndown',
        '📷 Centrar sobre cubo (X/Y, vision)': '📷 Center on cube (X/Y, vision)',
        'Paso': 'Step',
        '- paso': '- step',
        '+ paso': '+ step',
        'Girar pinza': 'Rotate gripper',
        '↺\nGirar-': '↺\nRotate-',
        '↻\nGirar+': '↻\nRotate+',
        'Pinza y postura': 'Gripper & pose',
        'ABRIR\npinza': 'OPEN\ngripper',
        'CERRAR\npinza': 'CLOSE\ngripper',
        'Orientar\npinza abajo': 'Aim\ngripper down',
        'LED': 'LED',
        'Rojo': 'Red',
        'Verde': 'Green',
        'Azul': 'Blue',
        'Apagar': 'Off',
        '  Movimiento  ': '  Movement  ',
        '  Producción  ': '  Production  ',
        '  Configuración  ': '  Settings  ',
        'Resumen por producto (varios pedidos a la vez)': 'Summary by product (several orders at once)',
        'Lanzar todo el resumen (uno detrás de otro)': 'Launch whole summary (one after another)',
        'Pedidos pendientes (Taller_Administracion)': 'Pending orders (Taller_Administracion)',
        'Sin lote en curso.': 'No batch running.',
        '🔁 Repetir último lote': '🔁 Repeat last batch',
        'Configuración': 'Settings',
        'Clave para desbloquear la configuración:': 'Password to unlock settings:',
        'Clave incorrecta': 'Wrong password',
        'La configuración sigue bloqueada.': 'Settings stay locked.',
        '🔓 Configuración desbloqueada': '🔓 Settings unlocked',
        '🔒 Configuración bloqueada': '🔒 Settings locked',
        'Bloquear': 'Lock',
        'Desbloquear (clave)': 'Unlock (password)',
        'Grupo Cadena:': 'Line group:',
        'Nº Máquina:': 'Machine No.:',
        'Guardar': 'Save',
        'Panel:': 'Panel:',
        'Se aplica al momento en todo el panel.': 'Applies immediately across the panel.',
        'Automático: lanzar pedidos solo, sin tocar nada': 'Automatic: launch orders by itself, hands-off',
        'Raspberry Pi Pico de esta cadena (contenedor {host})': 'Raspberry Pi Pico for this line (container {host})',
        'Aplicar configuración de las Pico': 'Apply Pico settings',
        'Cada Pico solo puede estar en UNA cadena: si otra cadena ya la tiene, se pide '
        'confirmación y aquella la suelta sola en unos segundos.\n'
        'El botón físico de la Pico W del Sorter no se elige aquí: avisa siempre a la '
        'cadena que publica el puerto 5002 en su docker-compose.yml (hoy la cadena 1).':
            'Each Pico can only belong to ONE line: if another line already has it, you get '
            'a confirmation and that line lets it go on its own in a few seconds.\n'
            "The Sorter's Pico W physical button isn't chosen here: it always notifies the "
            'line that publishes port 5002 in its docker-compose.yml (today, line 1).',
        'Panel de control manual - Panda': 'Manual control panel - Panda',
        'Sin pedidos pendientes.': 'No pending orders.',
        'Sin conexión con Taller_Administracion ({base}).': 'No connection to Taller_Administracion ({base}).',
        'Sin conexion con Taller_Administracion ({base}).': 'No connection to Taller_Administracion ({base}).',
        'No hay pedidos pendientes.': 'No pending orders.',
        'sin LED': 'no LED',
        'Lanzando...': 'Launching...',
        'Lanzar todo': 'Launch all',
        '+1 pieza': '+1 piece',
        'Lanzar este pedido': 'Launch this order',
        'pedido': 'order',
        'pedidos': 'orders',
        'hechas': 'done',
        'por fabricar': 'left to make',
        '{nombre} ({codigo} · {color}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})':
            '{nombre} ({codigo} · {color}): {completada}/{pedida} done -- {restante} left to make ({n} {plural})',
        '    · {nombre_sub} ({codigo}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})':
            '    · {nombre_sub} ({codigo}): {completada}/{pedida} done -- {restante} left to make ({n} {plural})',
        'Todavía no se ha lanzado ningún lote que repetir.': 'No batch has been launched yet to repeat.',
        'Ya hay un lote en curso (el Sorter aún no ha clasificado todas sus piezas) -- espera a que termine.':
            'A batch is already running (the Sorter hasn\'t sorted all its pieces yet) -- wait for it to finish.',
        'Ya hay una cola de lotes en marcha -- espera a que termine.': 'A batch queue is already running -- wait for it to finish.',
        '"{nombre}" ya no tiene unidades pendientes.': '"{nombre}" has no pending units left.',
        'Ya hay una producción en curso -- espera a que termine.': 'A production run is already going -- wait for it to finish.',
        'Sin conexión con Taller_Administracion.': 'No connection to Taller_Administracion.',
        'No hay pedidos pendientes que fabricar.': 'No pending orders to make.',
        'Fabricando {etiqueta} (Loader lanzado, Sorter activo). Logs en /tmp/lote_loader.log y /tmp/lote_sorter.log.':
            'Making {etiqueta} (Loader launched, Sorter active). Logs at /tmp/lote_loader.log and /tmp/lote_sorter.log.',
        'Ya hay un loader_demo corriendo fuera del panel -- espera a que termine o páralo.':
            'A loader_demo is already running outside the panel -- wait for it to finish or stop it.',
        'sin lotes lanzados todavía': 'no batches launched yet',
        'EN CURSO': 'RUNNING',
        'terminado (código {code})': 'finished (code {code})',
        'activo': 'active',
        'activo (externo)': 'active (external)',
        'sin arrancar': 'not started',
        'parado': 'stopped',
        'Lote Loader: {estado_loader}  |  Sorter: {estado_sorter}{progreso}': 'Loader batch: {estado_loader}  |  Sorter: {estado_sorter}{progreso}',
        '  |  Fabricadas: {hechas}/{objetivo} ({color})': '  |  Made: {hechas}/{objetivo} ({color})',
        '  |  Fabricadas: {hechas}/{objetivo} ({detalle})': '  |  Made: {hechas}/{objetivo} ({detalle})',
        'Repetir último lote': 'Repeat last batch',
        'Confirmar pedido': 'Confirm order',
        'Confirmar producción de todo el resumen': 'Confirm production of the whole summary',
        'Confirmar producto': 'Confirm product',
        'Nº Máquina 0': 'Machine No. 0',
        'Confirmar HOME': 'Confirm HOME',
        '¿Continuar?': 'Continue?',
        'Sí': 'Yes',
        'Nombre de la cadena guardado: "{texto}" (se mantiene en el próximo arranque).':
            'Line name saved: "{texto}" (kept on next startup).',
        'Nombre de la cadena borrado.': 'Line name cleared.',
        'URL de Taller_Administracion guardada: "{texto}" (se mantiene en el próximo arranque).':
            'Taller_Administracion URL saved: "{texto}" (kept on next startup).',
        'URL de Taller_Administracion restaurada al valor por defecto de esta máquina.':
            'Taller_Administracion URL reset to this machine\'s default.',
        'Nº Máquina guardado: {numero} (se mantiene en el próximo arranque).': 'Machine No. saved: {numero} (kept on next startup).',
        'Grupo Cadena guardado: {numero} (se mantiene en el próximo arranque).': 'Line group saved: {numero} (kept on next startup).',
        'Idioma guardado: {etiqueta}.': 'Language saved: {etiqueta}.',
        'Modo Automático ACTIVADO: lanzará los pedidos pendientes solo, sin confirmar.':
            'Automatic mode ON: it will launch pending orders by itself, without confirming.',
        'Modo Automático desactivado.': 'Automatic mode off.',
        '{corto}: arrancada ({valor})': '{corto}: started ({valor})',
        '{corto}: ya estaba en marcha': '{corto}: was already running',
        '{corto}: parada': '{corto}: stopped',
        'Pico: {mensajes}.': 'Pico: {mensajes}.',
        'sin cambios': 'no changes',
        'El puerto {valor} no existe en este contenedor ({host}).\n\n'
        'La Pico USB solo se ve desde la cadena que la tiene en el bloque '
        '"devices:" de su docker-compose.yml (y con la Pico enchufada al '
        'arrancar el contenedor).':
            "Port {valor} doesn't exist in this container ({host}).\n\n"
            'The USB Pico is only visible from the line that has it in the '
            '"devices:" block of its docker-compose.yml (and with the Pico '
            'plugged in when the container starts).',
        'Esta Pico la tiene ahora la cadena "{otra}" ({host}).\n\n'
        '¿Pasarla a esta cadena? La otra dejará de usarla en unos segundos.':
            'Line "{otra}" ({host}) currently has this Pico.\n\n'
            'Move it to this line? The other line will stop using it in a few seconds.',
        '{corto}: la ha pasado a la cadena "{otra}".': '{corto}: handed it over to line "{otra}".',
        '● en marcha': '● running',
        '⚠ puente parado, reintentando': '⚠ bridge down, retrying',
        'en la cadena "{nombre}"': 'on line "{nombre}"',
        '● en marcha (lanzado a mano, fuera de esta configuración)': '● running (launched manually, outside this config)',
        '○ no usada en esta cadena': '○ not used on this line',
        'Listo (pinza orientada hacia abajo). ': 'Ready (gripper aimed down). ',
        'Controlando ahora: {label}. ': 'Now controlling: {label}. ',
        'Movido.': 'Moved.',
        'Pinza -> ABIERTA': 'Gripper -> OPEN',
        'PARADA activa -- rearma antes de abrir.': 'STOP active -- reset before opening.',
        'Pinza -> CERRADA': 'Gripper -> CLOSED',
        'PARADA activa -- rearma antes de cerrar.': 'STOP active -- reset before closing.',
        'Vuelto a HOME y pinza reorientada hacia abajo. ': 'Back at HOME, gripper re-aimed down. ',
        'rojo': 'red', 'verde': 'green', 'azul': 'blue', 'apagado': 'off',
        'LED -> {nombre}': 'LED -> {nombre}',
        'PARADA manual enviada desde el panel.': 'Manual STOP sent from the panel.',
        'Rearme enviado -- puedes seguir moviendo el brazo.': 'Reset sent -- you can keep moving the arm.',
        'PARADA DE EMERGENCIA ACTIVA (fisica, manual o de otra demo).': 'EMERGENCY STOP ACTIVE (physical, manual, or from another demo).',
        'Pieza {color} registrada en el pedido #{id} ({completada}/{pedida}).':
            'Piece {color} logged on order #{id} ({completada}/{pedida}).',
        'Pieza {color} guardada en stock (sin pedido pendiente, o reparto manual activo) -- {stock} unidades.':
            'Piece {color} saved to stock (no pending order, or manual allocation is on) -- {stock} units.',
        'No se pudo registrar la pieza {color}: {info}': "Couldn't log piece {color}: {info}",
        'Identidad de la cadena': 'Line identity',
        'Idioma': 'Language',
        'Producción': 'Production',
        '(sin nombre)': '(no name)',
        'ninguna': 'none',
        'SÍ': 'YES',
        'no': 'no',
        'Grupo Cadena: {grupo}   ·   Nº Máquina: {maquina}   ·   Automático: {automatico}\nPico en esta cadena: {picos}\nTaller_Administracion: {taller}':
            'Line group: {grupo}   ·   Machine No.: {maquina}   ·   Automatic: {automatico}\nPico on this line: {picos}\nTaller_Administracion: {taller}',
        '\n\nOjo: este lote estaba atado al pedido #{id} -- si ya se completó, repetirlo fabricará piezas de más (van a Stock, no se pierden, pero no las pidió nadie).':
            '\n\nHeads up: this batch was tied to order #{id} -- if it\'s already complete, repeating it will make extra '
            "pieces (they go to Stock, not wasted, but nobody ordered them).",
        'Esto repite el último lote: {cantidad} unidad(es) de "{etiqueta}".\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.':
            'This repeats the last batch: {cantidad} unit(s) of "{etiqueta}".\n'
            "If you're controlling the Loader or Sorter by hand right now, they'll fight over the arm with the automatic demo.",
        'Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}" para el pedido #{pedido_id}.\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            'This launches the Loader and Sorter to make {cantidad} unit(s) of "{nombre}" for order #{pedido_id}.\n'
            "If you're controlling the Loader or Sorter by hand right now, they'll fight over the arm with the automatic demo.\n\nContinue?",
        'No se ha podido reclamar el pedido #{pid} para esta máquina (ya asignado a otra, o sin conexión) -- lote cancelado, se reintentará solo en el próximo ciclo.':
            "Couldn't claim order #{pid} for this machine (already assigned to another, or no connection) -- batch cancelled, it will retry on its own next cycle.",
        'Esto va a fabricar, UN PRODUCTO DETRAS DE OTRO (el siguiente no empieza hasta que el anterior termine de verdad, LED de producto fijo por lote):':
            "This will make ONE PRODUCT AFTER ANOTHER (the next one doesn't start until the previous one is really done, product LED fixed per batch):",
        'Si estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            "If you're controlling the Loader or Sorter by hand right now, they'll fight over the arm with the automatic demo.\n\nContinue?",
        'En Taller_Administracion el 0 significa "pedido libre, sin máquina".\n\nCon Nº Máquina 0 este panel NO podrá coger pedidos (el servidor lo rechaza), ni a mano ni en Automático.\n\n¿Guardar 0 igualmente?':
            'In Taller_Administracion, 0 means "unassigned order, no machine".\n\n'
            "With Machine No. 0 this panel will NOT be able to take orders (the server rejects it), neither by hand nor Automatic.\n\nSave 0 anyway?",
        'Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}", sumando todos los pedidos pendientes de ese producto.\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            'This launches the Loader and Sorter to make {cantidad} unit(s) of "{nombre}", adding up all pending orders for that product.\n'
            "If you're controlling the Loader or Sorter by hand right now, they'll fight over the arm with the automatic demo.\n\nContinue?",
        'Esto mueve el brazo entero a la posicion de reposo (HOME).\nSi estabas cerca de un cubo, se alejara de el.\n\nContinuar?':
            "This moves the whole arm to its rest position (HOME).\nIf you were near a cube, it will move away from it.\n\nContinue?",
        '  Raspberry Pi Pico  ': '  Raspberry Pi Pico  ',
        'Pico del Loader (USB)': "Loader's Pico (USB)",
        'Pico del Sorter (Wi-Fi)': "Sorter's Pico (Wi-Fi)",
        'Simulación de los LED -- útil si esta máquina no tiene la Raspberry Pi Pico física '
        'conectada: sin hardware, aquí se ve igual el mismo color que encendería.':
            "LED simulation -- useful if this machine doesn't have the physical Raspberry Pi Pico "
            "connected: without hardware, you can still see the same color it would light up.",
        'Agarre': 'Grip',
        'Producto': 'Product',
        'Apagado': 'Off',
        'Amarillo': 'Yellow',
        'Magenta': 'Magenta',
        'Cian': 'Cyan',
        'Blanco': 'White',
        'Alarma (parpadeando)': 'Alarm (blinking)',
        'Sin color (parpadeando)': 'No color (blinking)',
        'HC-SR04': 'HC-SR04',
        'Simula distancia (HC-SR04):': 'Simulate distance (HC-SR04):',
        '{cm:.0f} cm -- ¡detectado! (parada)': '{cm:.0f} cm -- detected! (stop)',
        '{cm:.0f} cm -- libre': '{cm:.0f} cm -- clear',
        # --- 2026-09-21: textos que faltaban + cambio de clave
        'AUTOMÁTICO DETENIDO para "{nombre}": se ha fabricado {tandas} veces seguidas y el pedido no avanza, así que las piezas no están llegando al Taller.\n\nRevisa la red: este panel usa el Taller en {base}. Comprueba que esa dirección es la del servidor donde está el pedido, que responde desde esta máquina y que el Sorter puede llegar a ella (pestaña Configuración, URL de Taller_Administracion).\n\nEl resto de productos sigue en Automático. Para reintentar este, desmarca y vuelve a marcar Automático.': 'AUTOMATIC STOPPED for "{nombre}": it has been made {tandas} times in a row and the order is not moving forward, so the pieces are not reaching the Workshop.\n\nCheck the network: this panel uses the Workshop at {base}. Make sure that address is the server where the order is, that it answers from this machine and that the Sorter can reach it (Settings tab, Taller_Administracion URL).\n\nThe rest of the products stay in Automatic. To retry this one, untick and tick Automatic again.',
        'Automático detenido': 'Automatic stopped',
        'Fabricando:': 'Making:',
        'HOME': 'HOME',
        'Loader listo': 'Loader ready',
        'Mostrar pestaña "Producción"': 'Show "Production" tab',
        'Mostrar pestaña "Raspberry Pi Pico"': 'Show "Raspberry Pi Pico" tab',
        'Pantalla OLED (simulada):': 'OLED display (simulated):',
        'Y+': 'Y+',
        'Y-': 'Y-',
        'sin lote': 'no batch',
        'Pico del Loader (USB: LED, LED producto, botón y HC-SR04)': "Loader's Pico (USB: LED, product LED, button and HC-SR04)",
        'Pico W del Sorter (Wi-Fi: LED)': "Sorter's Pico W (Wi-Fi: LED)",
        'Puerto serie:': 'Serial port:',
        'IP de la Pico:': 'Pico IP:',
        'Cambiar clave de configuración': 'Change settings password',
        'Clave nueva:': 'New password:',
        'Repite la clave:': 'Repeat password:',
        'Cambiar clave': 'Change password',
        'Escribe la clave nueva dos veces.': 'Type the new password twice.',
        'Las dos claves no coinciden.': 'The two passwords do not match.',
        'La clave nueva tiene que tener al menos {n} caracteres.': 'The new password must be at least {n} characters long.',
        'La clave nueva es igual que la actual.': 'The new password is the same as the current one.',
        'Clave cambiada. Desde ahora se pide la nueva para desbloquear.': 'Password changed. From now on the new one is asked to unlock.',
        # 2026-09-26: restablecer la clave (pulsacion larga del boton del Loader)
        'Clave restablecida a la de fábrica ({clave}).': 'Key reset to the factory one ({clave}).',
        'Mantén pulsado {s} s para restablecer la clave': 'Hold for {s} s to reset the key',
        'Pulsación larga ignorada: para restablecer la clave hay que tener abierta la pestaña Configuración o Raspberry Pi Pico.': 'Long press ignored: to reset the key, the Settings or Raspberry Pi Pico tab has to be open.',
        'Restablecer la clave': 'Reset the key',
        'Restableciendo la clave en {s} s... suelta para cancelar': 'Resetting the key in {s} s... release to cancel',
        'Restablecimiento de la clave cancelado.': 'Key reset cancelled.',
        '¿Restablecer la clave de configuración a la de fábrica ({clave})?': 'Reset the settings key to the factory one ({clave})?',
    },
    'eu': {
        'PANEL DE CONTROL MANUAL': 'ESKUZKO KONTROL-PANELA',
        'EN MARCHA': 'MARTXAN',
        'Pantalla Pico': 'Pico pantaila',
        'PARADO': 'GELDITUTA',
        'PARADA\nDE EMERGENCIA': 'LARRIALDI\nGELDIALDIA',
        'REARME': 'BERRABIARAZI',
        'Nombre de la cadena:': 'Katearen izena:',
        'URL de Taller_Administracion:': 'Taller_Administracion-ren URL-a:',
        'Robot controlado:': 'Kontrolatzen den robota:',
        'Listo.': 'Prest.',
        'Mover TCP (mundo)': 'TCP mugitu (mundua)',
        'X+\nadelante': 'X+\naurrera',
        'X-\natras': 'X-\natzera',
        'Z+\nsubir': 'Z+\ngora',
        'Z-\nbajar': 'Z-\nbehera',
        '📷 Centrar sobre cubo (X/Y, vision)': '📷 Kuboan zentratu (X/Y, ikusmena)',
        'Paso': 'Urratsa',
        '- paso': '- urratsa',
        '+ paso': '+ urratsa',
        'Girar pinza': 'Pintza biratu',
        '↺\nGirar-': '↺\nBiratu-',
        '↻\nGirar+': '↻\nBiratu+',
        'Pinza y postura': 'Pintza eta jarrera',
        'ABRIR\npinza': 'IREKI\npintza',
        'CERRAR\npinza': 'ITXI\npintza',
        'Orientar\npinza abajo': 'Pintza\nbeherantz',
        'LED': 'LED',
        'Rojo': 'Gorria',
        'Verde': 'Berdea',
        'Azul': 'Urdina',
        'Apagar': 'Itzali',
        '  Movimiento  ': '  Mugimendua  ',
        '  Producción  ': '  Ekoizpena  ',
        '  Configuración  ': '  Konfigurazioa  ',
        'Resumen por producto (varios pedidos a la vez)': 'Produktuko laburpena (hainbat eskaera batera)',
        'Lanzar todo el resumen (uno detrás de otro)': 'Laburpen osoa abiarazi (bata bestearen atzetik)',
        'Pedidos pendientes (Taller_Administracion)': 'Eskaera falta direnak (Taller_Administracion)',
        'Sin lote en curso.': 'Ez dago lorik martxan.',
        '🔁 Repetir último lote': '🔁 Azken lotea errepikatu',
        'Configuración': 'Konfigurazioa',
        'Clave para desbloquear la configuración:': 'Konfigurazioa desblokeatzeko klabea:',
        'Clave incorrecta': 'Klabea okerra',
        'La configuración sigue bloqueada.': 'Konfigurazioa blokeatuta jarraitzen du.',
        '🔓 Configuración desbloqueada': '🔓 Konfigurazioa desblokeatuta',
        '🔒 Configuración bloqueada': '🔒 Konfigurazioa blokeatuta',
        'Bloquear': 'Blokeatu',
        'Desbloquear (clave)': 'Desblokeatu (klabea)',
        'Grupo Cadena:': 'Kate taldea:',
        'Nº Máquina:': 'Makina zk.:',
        'Guardar': 'Gorde',
        'Panel:': 'Panela:',
        'Se aplica al momento en todo el panel.': 'Berehala aplikatzen da panel osoan.',
        'Automático: lanzar pedidos solo, sin tocar nada': 'Automatikoa: eskaerak bakarrik abiarazi, ezer ukitu gabe',
        'Raspberry Pi Pico de esta cadena (contenedor {host})': 'Kate honetako Raspberry Pi Pico ({host} edukiontzia)',
        'Aplicar configuración de las Pico': 'Picoen konfigurazioa aplikatu',
        'Cada Pico solo puede estar en UNA cadena: si otra cadena ya la tiene, se pide '
        'confirmación y aquella la suelta sola en unos segundos.\n'
        'El botón físico de la Pico W del Sorter no se elige aquí: avisa siempre a la '
        'cadena que publica el puerto 5002 en su docker-compose.yml (hoy la cadena 1).':
            'Pico bakoitza KATE BAKAR batekoa izan daiteke: beste kate batek jadanik badu, '
            'berrespena eskatzen da eta harek segundo batzuetan uzten dio erabiltzeari.\n'
            'Sorter-eko Pico W-aren benetako botoia ez da hemen aukeratzen: beti 5002 '
            'portua bere docker-compose.yml-en argitaratzen duen kateari abisatzen dio '
            '(gaur, 1 katea).',
        'Panel de control manual - Panda': 'Eskuzko kontrol-panela - Panda',
        'Sin pedidos pendientes.': 'Ez dago eskaerarik zain.',
        'Sin conexión con Taller_Administracion ({base}).': 'Ez dago konexiorik Taller_Administracion-ekin ({base}).',
        'Sin conexion con Taller_Administracion ({base}).': 'Ez dago konexiorik Taller_Administracion-ekin ({base}).',
        'No hay pedidos pendientes.': 'Ez dago eskaerarik zain.',
        'sin LED': 'LEDrik gabe',
        'Lanzando...': 'Abiarazten...',
        'Lanzar todo': 'Dena abiarazi',
        '+1 pieza': '+1 pieza',
        'Lanzar este pedido': 'Eskaera hau abiarazi',
        'pedido': 'eskaera',
        'pedidos': 'eskaera',
        'hechas': 'eginda',
        'por fabricar': 'egiteko',
        '{nombre} ({codigo} · {color}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})':
            '{nombre} ({codigo} · {color}): {completada}/{pedida} eginda -- {restante} egiteko ({n} {plural})',
        '    · {nombre_sub} ({codigo}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})':
            '    · {nombre_sub} ({codigo}): {completada}/{pedida} eginda -- {restante} egiteko ({n} {plural})',
        'Todavía no se ha lanzado ningún lote que repetir.': 'Oraindik ez da loterik abiarazi errepikatzeko.',
        'Ya hay un lote en curso (el Sorter aún no ha clasificado todas sus piezas) -- espera a que termine.':
            'Badago dagoeneko lote bat martxan (Sorter-ek oraindik ez ditu pieza guztiak sailkatu) -- itxaron amaitu arte.',
        'Ya hay una cola de lotes en marcha -- espera a que termine.': 'Badago dagoeneko loteen ilara bat martxan -- itxaron amaitu arte.',
        '"{nombre}" ya no tiene unidades pendientes.': '"{nombre}"-k ez du unitate zainik gehiago.',
        'Ya hay una producción en curso -- espera a que termine.': 'Badago dagoeneko ekoizpen bat martxan -- itxaron amaitu arte.',
        'Sin conexión con Taller_Administracion.': 'Ez dago konexiorik Taller_Administracion-ekin.',
        'No hay pedidos pendientes que fabricar.': 'Ez dago egiteko eskaerarik zain.',
        'Fabricando {etiqueta} (Loader lanzado, Sorter activo). Logs en /tmp/lote_loader.log y /tmp/lote_sorter.log.':
            '{etiqueta} egiten (Loader abiarazita, Sorter aktibo). Erregistroak: /tmp/lote_loader.log eta /tmp/lote_sorter.log.',
        'Ya hay un loader_demo corriendo fuera del panel -- espera a que termine o páralo.':
            'Badago dagoeneko loader_demo bat panelaz kanpo martxan -- itxaron amaitu arte edo gelditu ezazu.',
        'sin lotes lanzados todavía': 'oraindik loterik abiarazi gabe',
        'EN CURSO': 'MARTXAN',
        'terminado (código {code})': 'amaituta ({code} kodea)',
        'activo': 'aktibo',
        'activo (externo)': 'aktibo (kanpokoa)',
        'sin arrancar': 'abiarazi gabe',
        'parado': 'geldituta',
        'Lote Loader: {estado_loader}  |  Sorter: {estado_sorter}{progreso}': 'Loader lotea: {estado_loader}  |  Sorter: {estado_sorter}{progreso}',
        '  |  Fabricadas: {hechas}/{objetivo} ({color})': '  |  Eginda: {hechas}/{objetivo} ({color})',
        '  |  Fabricadas: {hechas}/{objetivo} ({detalle})': '  |  Eginda: {hechas}/{objetivo} ({detalle})',
        'Repetir último lote': 'Azken lotea errepikatu',
        'Confirmar pedido': 'Eskaera berretsi',
        'Confirmar producción de todo el resumen': 'Laburpen osoaren ekoizpena berretsi',
        'Confirmar producto': 'Produktua berretsi',
        'Nº Máquina 0': 'Makina zk. 0',
        'Confirmar HOME': 'HOME berretsi',
        '¿Continuar?': 'Jarraitu?',
        'Sí': 'Bai',
        'Nombre de la cadena guardado: "{texto}" (se mantiene en el próximo arranque).':
            'Katearen izena gordeta: "{texto}" (hurrengo abioan mantentzen da).',
        'Nombre de la cadena borrado.': 'Katearen izena ezabatuta.',
        'URL de Taller_Administracion guardada: "{texto}" (se mantiene en el próximo arranque).':
            'Taller_Administracion-ren URL-a gordeta: "{texto}" (hurrengo abioan mantentzen da).',
        'URL de Taller_Administracion restaurada al valor por defecto de esta máquina.':
            'Taller_Administracion-ren URL-a makina honen balio lehenetsira leheneratuta.',
        'Nº Máquina guardado: {numero} (se mantiene en el próximo arranque).': 'Makina zk. gordeta: {numero} (hurrengo abioan mantentzen da).',
        'Grupo Cadena guardado: {numero} (se mantiene en el próximo arranque).': 'Kate taldea gordeta: {numero} (hurrengo abioan mantentzen da).',
        'Idioma guardado: {etiqueta}.': 'Hizkuntza gordeta: {etiqueta}.',
        'Modo Automático ACTIVADO: lanzará los pedidos pendientes solo, sin confirmar.':
            'Modu automatikoa PIZTUTA: eskaera falta direnak bakarrik abiaraziko ditu, berretsi gabe.',
        'Modo Automático desactivado.': 'Modu automatikoa itzalita.',
        '{corto}: arrancada ({valor})': '{corto}: abiarazita ({valor})',
        '{corto}: ya estaba en marcha': '{corto}: martxan zegoen jada',
        '{corto}: parada': '{corto}: geldituta',
        'Pico: {mensajes}.': 'Pico: {mensajes}.',
        'sin cambios': 'aldaketarik gabe',
        'El puerto {valor} no existe en este contenedor ({host}).\n\n'
        'La Pico USB solo se ve desde la cadena que la tiene en el bloque '
        '"devices:" de su docker-compose.yml (y con la Pico enchufada al '
        'arrancar el contenedor).':
            '{valor} ataka ez dago edukiontzi honetan ({host}).\n\n'
            'USB Pico bere docker-compose.yml-eko "devices:" blokean daukan '
            'kateatik bakarrik ikusten da (eta Pico entxufatuta edukiontzia '
            'abiaraztean).',
        'Esta Pico la tiene ahora la cadena "{otra}" ({host}).\n\n'
        '¿Pasarla a esta cadena? La otra dejará de usarla en unos segundos.':
            '"{otra}" kateak ({host}) du orain Pico hau.\n\n'
            'Kate honetara pasatu? Besteak segundo batzuetan utziko dio erabiltzeari.',
        '{corto}: la ha pasado a la cadena "{otra}".': '{corto}: "{otra}" kateari pasatu dio.',
        '● en marcha': '● martxan',
        '⚠ puente parado, reintentando': '⚠ zubia geldituta, berriz saiatzen',
        'en la cadena "{nombre}"': '"{nombre}" katean',
        '● en marcha (lanzado a mano, fuera de esta configuración)': '● martxan (eskuz abiarazita, konfigurazio honetatik kanpo)',
        '○ no usada en esta cadena': '○ kate honetan erabili gabe',
        'Listo (pinza orientada hacia abajo). ': 'Prest (pintza beherantz orientatuta). ',
        'Controlando ahora: {label}. ': 'Orain kontrolatzen: {label}. ',
        'Movido.': 'Mugituta.',
        'Pinza -> ABIERTA': 'Pintza -> IREKITA',
        'PARADA activa -- rearma antes de abrir.': 'GELDIALDIA aktibo -- berrabiarazi ireki aurretik.',
        'Pinza -> CERRADA': 'Pintza -> ITXITA',
        'PARADA activa -- rearma antes de cerrar.': 'GELDIALDIA aktibo -- berrabiarazi itxi aurretik.',
        'Vuelto a HOME y pinza reorientada hacia abajo. ': 'HOME-ra itzulita eta pintza beherantz orientatuta berriz. ',
        'rojo': 'gorria', 'verde': 'berdea', 'azul': 'urdina', 'apagado': 'itzalita',
        'LED -> {nombre}': 'LED -> {nombre}',
        'PARADA manual enviada desde el panel.': 'Eskuzko GELDIALDIA bidalita paneletik.',
        'Rearme enviado -- puedes seguir moviendo el brazo.': 'Berrabiarazia bidalita -- besoa mugitzen jarrai dezakezu.',
        'PARADA DE EMERGENCIA ACTIVA (fisica, manual o de otra demo).': 'LARRIALDI GELDIALDIA AKTIBO (fisikoa, eskuzkoa edo beste demo batena).',
        'Pieza {color} registrada en el pedido #{id} ({completada}/{pedida}).':
            '{color} pieza #{id} eskaeran erregistratuta ({completada}/{pedida}).',
        'Pieza {color} guardada en stock (sin pedido pendiente, o reparto manual activo) -- {stock} unidades.':
            '{color} pieza stock-ean gordeta (eskaerarik zain ez, edo banaketa eskuzkoa piztuta) -- {stock} unitate.',
        'No se pudo registrar la pieza {color}: {info}': 'Ezin izan da {color} pieza erregistratu: {info}',
        'Identidad de la cadena': 'Katearen identitatea',
        'Idioma': 'Hizkuntza',
        'Producción': 'Ekoizpena',
        '(sin nombre)': '(izenik gabe)',
        'ninguna': 'bat ere ez',
        'SÍ': 'BAI',
        'no': 'ez',
        'Grupo Cadena: {grupo}   ·   Nº Máquina: {maquina}   ·   Automático: {automatico}\nPico en esta cadena: {picos}\nTaller_Administracion: {taller}':
            'Kate taldea: {grupo}   ·   Makina zk.: {maquina}   ·   Automatikoa: {automatico}\nKate honetako Pico: {picos}\nTaller_Administracion: {taller}',
        '\n\nOjo: este lote estaba atado al pedido #{id} -- si ya se completó, repetirlo fabricará piezas de más (van a Stock, no se pierden, pero no las pidió nadie).':
            '\n\nKontuz: lote hau #{id} eskaerari lotuta zegoen -- dagoeneko osatuta badago, errepikatzeak pieza gehiegi '
            'egingo ditu (Stock-era doaz, ez dira galtzen, baina inork ez ditu eskatu).',
        'Esto repite el último lote: {cantidad} unidad(es) de "{etiqueta}".\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.':
            'Honek azken lotea errepikatzen du: "{etiqueta}"-ren {cantidad} unitate.\n'
            'Orain Loader edo Sorter eskuz kontrolatzen ari bazara, demo automatikoarekin besoagatik borrokatuko dira.',
        'Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}" para el pedido #{pedido_id}.\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            'Honek Loader eta Sorter abiarazten ditu #{pedido_id} eskaerarako "{nombre}"-ren {cantidad} unitate egiteko.\n'
            'Orain Loader edo Sorter eskuz kontrolatzen ari bazara, demo automatikoarekin besoagatik borrokatuko dira.\n\nJarraitu?',
        'No se ha podido reclamar el pedido #{pid} para esta máquina (ya asignado a otra, o sin conexión) -- lote cancelado, se reintentará solo en el próximo ciclo.':
            'Ezin izan da #{pid} eskaera makina honentzat erreklamatu (beste bati esleituta, edo konexiorik gabe) -- '
            'lotea bertan behera utzita, hurrengo zikloan bakarrik berriz saiatuko da.',
        'Esto va a fabricar, UN PRODUCTO DETRAS DE OTRO (el siguiente no empieza hasta que el anterior termine de verdad, LED de producto fijo por lote):':
            'Honek PRODUKTU BAT BESTEAREN ATZETIK egingo du (hurrengoa ez da hasiko aurrekoa benetan amaitu arte, '
            'produktu LEDa finko loteko):',
        'Si estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            'Orain Loader edo Sorter eskuz kontrolatzen ari bazara, demo automatikoarekin besoagatik borrokatuko dira.\n\nJarraitu?',
        'En Taller_Administracion el 0 significa "pedido libre, sin máquina".\n\nCon Nº Máquina 0 este panel NO podrá coger pedidos (el servidor lo rechaza), ni a mano ni en Automático.\n\n¿Guardar 0 igualmente?':
            'Taller_Administracion-en 0 zenbakiak "eskaera librea, makinarik gabe" esan nahi du.\n\n'
            'Makina zk. 0 jarrita, panel honek EZIN izango ditu eskaerak hartu (zerbitzariak ukatu egiten du), ez eskuz ez Automatikoan.\n\nGorde 0 hala ere?',
        'Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}", sumando todos los pedidos pendientes de ese producto.\nSi estás controlando el Loader o el Sorter a mano ahora mismo, se pelearán por el brazo con la demo automática.\n\n¿Continuar?':
            'Honek Loader eta Sorter abiarazten ditu "{nombre}"-ren {cantidad} unitate egiteko, produktu horren eskaera '
            'falta guztiak batuta.\nOrain Loader edo Sorter eskuz kontrolatzen ari bazara, demo automatikoarekin besoagatik borrokatuko dira.\n\nJarraitu?',
        'Esto mueve el brazo entero a la posicion de reposo (HOME).\nSi estabas cerca de un cubo, se alejara de el.\n\nContinuar?':
            'Honek beso osoa atseden posiziora (HOME) mugitzen du.\nKubo baten ondoan bazeunden, hartatik urrunduko da.\n\nJarraitu?',
        '  Raspberry Pi Pico  ': '  Raspberry Pi Pico  ',
        'Pico del Loader (USB)': 'Loader-en Pico (USB)',
        'Pico del Sorter (Wi-Fi)': 'Sorter-en Pico (Wi-Fi)',
        'Simulación de los LED -- útil si esta máquina no tiene la Raspberry Pi Pico física '
        'conectada: sin hardware, aquí se ve igual el mismo color que encendería.':
            'LEDen simulazioa -- lagungarria makina honek Raspberry Pi Pico fisikoa konektatuta ez '
            'badu: hardwarerik gabe, hemen ikus daiteke piztuko lukeen kolore bera.',
        'Agarre': 'Heldua',
        'Producto': 'Produktua',
        'Apagado': 'Itzalita',
        'Amarillo': 'Horia',
        'Magenta': 'Magenta',
        'Cian': 'Ziana',
        'Blanco': 'Zuria',
        'Alarma (parpadeando)': 'Alarma (keinuka)',
        'Sin color (parpadeando)': 'Kolorerik gabe (keinuka)',
        'HC-SR04': 'HC-SR04',
        'Simula distancia (HC-SR04):': 'Distantzia simulatu (HC-SR04):',
        '{cm:.0f} cm -- ¡detectado! (parada)': '{cm:.0f} cm -- detektatuta! (gelditu)',
        '{cm:.0f} cm -- libre': '{cm:.0f} cm -- libre',
        # --- 2026-09-21: textos que faltaban + cambio de clave
        'AUTOMÁTICO DETENIDO para "{nombre}": se ha fabricado {tandas} veces seguidas y el pedido no avanza, así que las piezas no están llegando al Taller.\n\nRevisa la red: este panel usa el Taller en {base}. Comprueba que esa dirección es la del servidor donde está el pedido, que responde desde esta máquina y que el Sorter puede llegar a ella (pestaña Configuración, URL de Taller_Administracion).\n\nEl resto de productos sigue en Automático. Para reintentar este, desmarca y vuelve a marcar Automático.': 'AUTOMATIKOA GELDITU DA "{nombre}" produkturako: {tandas} aldiz jarraian fabrikatu da eta eskaerak ez du aurrera egiten, beraz piezak ez dira Tailerrera iristen.\n\nAztertu sarea: panel honek Taller hau erabiltzen du: {base}. Egiaztatu helbide hori eskaera dagoen zerbitzariarena dela, makina honetatik erantzuten duela eta Sorter-ak iristen dela (Konfigurazioa fitxa, Taller_Administracion-en URL-a).\n\nBeste produktuek Automatikoan jarraitzen dute. Hau berriro saiatzeko, desmarkatu eta markatu berriro Automatikoa.',
        'Automático detenido': 'Automatikoa geldituta',
        'Fabricando:': 'Fabrikatzen:',
        'HOME': 'HOME',
        'Loader listo': 'Loader prest',
        'Mostrar pestaña "Producción"': 'Erakutsi "Ekoizpena" fitxa',
        'Mostrar pestaña "Raspberry Pi Pico"': 'Erakutsi "Raspberry Pi Pico" fitxa',
        'Pantalla OLED (simulada):': 'OLED pantaila (simulatua):',
        'Y+': 'Y+',
        'Y-': 'Y-',
        'sin lote': 'lote gabe',
        'Pico del Loader (USB: LED, LED producto, botón y HC-SR04)': 'Loader-en Pico (USB: LED-a, produktuaren LED-a, botoia eta HC-SR04)',
        'Pico W del Sorter (Wi-Fi: LED)': 'Sorter-en Pico W (Wi-Fi: LED-a)',
        'Puerto serie:': 'Serie-portua:',
        'IP de la Pico:': 'Pico-ren IP-a:',
        'Cambiar clave de configuración': 'Aldatu konfigurazioaren klabea',
        'Clave nueva:': 'Klabe berria:',
        'Repite la clave:': 'Errepikatu klabea:',
        'Cambiar clave': 'Aldatu klabea',
        'Escribe la clave nueva dos veces.': 'Idatzi klabe berria bi aldiz.',
        'Las dos claves no coinciden.': 'Bi klabeak ez datoz bat.',
        'La clave nueva tiene que tener al menos {n} caracteres.': 'Klabe berriak {n} karaktere izan behar ditu gutxienez.',
        'La clave nueva es igual que la actual.': 'Klabe berria egungoaren berdina da.',
        'Clave cambiada. Desde ahora se pide la nueva para desbloquear.': 'Klabea aldatu da. Hemendik aurrera berria eskatuko da desblokeatzeko.',
        # 2026-09-26: restablecer la clave (pulsacion larga del boton del Loader)
        'Clave restablecida a la de fábrica ({clave}).': 'Gakoa fabrikakora berrezarri da ({clave}).',
        'Mantén pulsado {s} s para restablecer la clave': 'Eutsi {s} s gakoa berrezartzeko',
        'Pulsación larga ignorada: para restablecer la clave hay que tener abierta la pestaña Configuración o Raspberry Pi Pico.': 'Sakatze luzea ez da kontuan hartu: gakoa berrezartzeko Konfigurazioa edo Raspberry Pi Pico fitxak irekita egon behar du.',
        'Restablecer la clave': 'Gakoa berrezarri',
        'Restableciendo la clave en {s} s... suelta para cancelar': 'Gakoa {s} s barru berrezarriko da... askatu bertan behera uzteko',
        'Restablecimiento de la clave cancelado.': 'Gakoa berrezartzea bertan behera utzi da.',
        '¿Restablecer la clave de configuración a la de fábrica ({clave})?': 'Konfigurazio-gakoa fabrikakora berrezarri ({clave})?',
    },
}


# Raspberry Pi Pico de la celda (sesion 2026-09-14, pestaña Configuracion):
# con dos lineas de produccion a la vez, cada Pico fisica tiene que
# obedecer a UNA sola. El panel arranca/para el puente de cada Pico en
# SU contenedor segun lo marcado aqui, en vez de lanzarlos a mano (paso 4
# de LANZAR_PROYECTO.md) en el contenedor correcto.
# El boton fisico de la Pico W del Sorter (button_listener) NO esta aqui a
# proposito: la Pico llama al PC por el puerto 5002 del host, y ese puerto
# lo publica solo el docker-compose.yml de una linea (la 1) -- no se puede
# cambiar de linea desde el panel, solo tocando los compose.
PICOS = {
    'loader_usb': {
        'nombre': 'Pico del Loader (USB: LED, LED producto, botón y HC-SR04)',
        'corto': 'Loader USB',
        'ejecutable': 'led_publisher_usb',
        'param': 'serial_port',
        'etiqueta_param': 'Puerto serie:',
        'defecto': '/dev/ttyACM_LOADER',
    },
    'sorter_wifi': {
        'nombre': 'Pico W del Sorter (Wi-Fi: LED)',
        'corto': 'Sorter Wi-Fi',
        'ejecutable': 'led_publisher',
        'param': 'pico_ip',
        'etiqueta_param': 'IP de la Pico:',
        'defecto': '192.168.1.101',
    },
}
# Fichero COMPARTIDO por todas las lineas (a diferencia de
# CONFIG_MAQUINA_PATH, que es uno por contenedor): las dos lineas montan el
# mismo ../ros2_ws en /workspace, asi que aqui es donde cada panel ve que
# Pico tiene ya otra linea. {clave_pico: {'host': hostname, 'nombre': ...}}
PICO_ASIGNACION_PATH = '/workspace/pico_asignacion.json'
MI_HOST = socket.gethostname()
# Si un puente asignado a esta linea se muere, el panel lo relanza solo,
# pero no mas de una vez cada tantos segundos (por si muere nada mas
# arrancar, para no quedarse en bucle lanzando procesos).
PICO_REINTENTO_S = 15.0

# Un lote con el Loader ya terminado pero con piezas sin contar se da por
# cerrado tras este tiempo SIN ninguna entrega nueva (ver
# TeleopApp._lote_en_curso). Una pieza normal tarda ~25s en el Sorter y un
# agarre con reintentos puede llegar a 60s -- 120s deja margen de sobra.
LOTE_SIN_ENTREGAS_S = 120.0
# Espera tras cerrar un lote antes de que Automatico vuelva a mirar el
# almacen (ver TeleopApp._lote_recien_cerrado).
MARGEN_TALLER_S = 6.0
# Modo Automatico: tandas seguidas SIN que avance un producto (ni baja lo que
# falta ni sube lo completado) tras las que se deja de lanzar ESE producto y se
# avisa (ver TeleopApp._vigilar_progreso_auto). Bug real 2026-09-19: las piezas
# se avisaban a otro Taller distinto del que mostraba el panel, los pedidos no
# avanzaban nunca y el mismo pedido se relanzaba sin fin.
AUTO_MAX_TANDAS_SIN_PROGRESO = 2


def _leer_asignacion_picos() -> dict:
    try:
        with open(PICO_ASIGNACION_PATH) as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def _escribir_asignacion_picos(datos: dict) -> None:
    with open(PICO_ASIGNACION_PATH, 'w') as f:
        json.dump(datos, f)


def _cargar_config_picos() -> dict:
    """{clave_pico: {'activa': bool, 'valor': str}} de ESTA linea, con los
    valores por defecto de PICOS para lo que nunca se haya guardado."""
    guardado = _leer_config_panel().get('picos', {}) or {}
    config = {}
    for clave, pico in PICOS.items():
        g = guardado.get(clave, {}) or {}
        config[clave] = {
            'activa': bool(g.get('activa', False)),
            'valor': str(g.get('valor') or pico['defecto']),
        }
    return config


def _patron_puente(ejecutable: str) -> str:
    # '( |$)' para que 'led_publisher' no coincida tambien con
    # 'led_publisher_usb'. Ruta del ejecutable real, no 'ros2 run ...' (ver
    # _demo_vivo, mismo motivo).
    return f'panda_controller/lib/panda_controller/{ejecutable}( |$)'


def _puente_vivo(ejecutable: str) -> bool:
    try:
        return subprocess.run(['pgrep', '-f', _patron_puente(ejecutable)],
                              capture_output=True, timeout=2).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _lanzar_puente(ejecutable: str, param: str, valor: str) -> subprocess.Popen:
    """Proceso independiente del panel (start_new_session): si se cierra
    la ventana, el LED fisico sigue funcionando igual que cuando el puente
    se lanzaba a mano. Salida a /tmp/<ejecutable>.log dentro del contenedor."""
    log = open(f'/tmp/{ejecutable}.log', 'a')
    try:
        return subprocess.Popen(
            ['ros2', 'run', 'panda_controller', ejecutable, '--ros-args', '-p', f'{param}:={valor}'],
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    finally:
        log.close()  # el hijo ya tiene su propia copia del descriptor


def _parar_puente(ejecutable: str) -> None:
    """Para el puente lo haya lanzado este panel o no (pkill por la ruta
    del ejecutable real). SIGTERM y, si en 3s no ha salido, SIGKILL."""
    patron = _patron_puente(ejecutable)
    try:
        subprocess.run(['pkill', '-TERM', '-f', patron], capture_output=True, timeout=2)
        for _ in range(30):
            if not _puente_vivo(ejecutable):
                return
            time.sleep(0.1)
        subprocess.run(['pkill', '-KILL', '-f', patron], capture_output=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        pass

PANDA_MDH = [
    (0.0,     0.0,        0.333),
    (0.0,    -math.pi/2,  0.0),
    (0.0,     math.pi/2,  0.316),
    (0.0825,  math.pi/2,  0.0),
    (-0.0825, -math.pi/2, 0.384),
    (0.0,     math.pi/2,  0.0),
    (0.088,   math.pi/2,  0.0),
]

FLANGE_TO_TCP_Z = 0.107 + 0.1034  # brida (0.107) + mano/dedos (~0.1034)

HOME_POSITIONS = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]

GRASP_R = np.array([
    [1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0],
    [0.0, 0.0, -1.0],
])


def rz(theta):
    """Rotacion pura alrededor del eje Z de la propia pinza (postmultiplicada
    sobre GRASP_R): gira el agarre sin tocar la orientacion "mirando hacia
    abajo". Mismo convenio que panda_ikpy_kinematics.rz (sesion 2026-08-27,
    botones de giro de la mano en el panel manual)."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ])


STEP_DEFAULT = 0.01  # 1 cm
STEP_MIN = 0.002
STEP_MAX = 0.05
YAW_STEP_DEG = 5.0
MAX_JOINT_JUMP_DEG = 25.0
_MAX_SPLIT_DEPTH = 4  # 2**4 = 16 sub-pasos como maximo por click

# Limites reales de cada articulacion, tal como los imprime my_robot_driver.py
# al arrancar (leidos del propio motor en Webots). OJO: para panda_joint4 el
# limite inferior (-3.1416) esta pegado casi exacto al punto -pi/+pi -- ver
# _publish_joint para el bug real que esto causaba con el wrap-around
# generico por modulo.
JOINT_LIMITS = [
    (-2.9671, 2.9671),
    (-1.8326, 1.8326),
    (-2.9671, 2.9671),
    (-3.1416, -0.4000),
    (-2.9671, 2.9671),
    (-0.0873, 3.8223),
    (-2.9671, 2.9671),
]
JOINT_LIMITS_LO = np.array([lo for lo, hi in JOINT_LIMITS])
JOINT_LIMITS_HI = np.array([hi for lo, hi in JOINT_LIMITS])

# Selector de robot en el propio panel (sesion 2026-08-30): antes, para
# controlar el Sorter en vez del Loader habia que MATAR la ventana y
# relanzarla entera con otros --ros-args (ver LANZAR_PROYECTO.md 5b, ahora
# obsoleto). El preset 'loader' se sigue construyendo a partir de los
# parametros ROS declarados en __init__ (para no romper overrides ya
# existentes); el del 'sorter' se fija aqui con los mismos valores que ya
# se pasaban a mano por CLI -- si algun dia cambia la base o la camara del
# Sorter en el mundo, se actualiza SOLO aqui.
SORTER_PRESET = {
    'label': 'Sorter',
    'joint_topic': '/sorter/joint_positions',
    'gripper_topic': '/sorter/gripper_position',
    'led_topic': '/comando_led',  # Pico W de siempre, con el boton de parada
    'base': (0.0, 1.0, 0.74),
    # Giro de la base (sesion 2026-09-11): el Sorter esta girado 26.6 grados
    # en el mundo (DEF PANDA_SORTER rotation, SORTER_BASE_YAW en sorter_demo.py).
    # Sin esto el panel calculaba mal su TCP "mundo" y los botones X/Y y
    # "Centrar sobre cubo" lo movian en direcciones giradas 26.6 grados.
    'base_yaw': 0.4636,
    'camera_topic': '/overhead_camera_sorter/image_color',
    'camera': (0.25, 1.30, 2.27),
    'table_x': (0.35, 0.65),
    'table_y': (0.95, 1.35),
}

def mdh_transform(a_prev, alpha_prev, d, theta):
    ca, sa = math.cos(alpha_prev), math.sin(alpha_prev)
    ct, st = math.cos(theta), math.sin(theta)
    return np.array([
        [ct, -st, 0.0, a_prev],
        [st * ca, ct * ca, -sa, -sa * d],
        [st * sa, ct * sa, ca, ca * d],
        [0.0, 0.0, 0.0, 1.0],
    ])


def forward_kinematics(thetas):
    T = np.eye(4)
    for theta, (a_prev, alpha_prev, d) in zip(thetas, PANDA_MDH):
        T = T @ mdh_transform(a_prev, alpha_prev, d, theta)
    T_flange = np.eye(4)
    T_flange[2, 3] = FLANGE_TO_TCP_Z
    return T @ T_flange


def rotation_error(r_current, r_target):
    r_err = r_target @ r_current.T
    cos_theta = np.clip((np.trace(r_err) - 1.0) / 2.0, -1.0, 1.0)
    theta = math.acos(cos_theta)
    if abs(theta) < 1e-8:
        return np.zeros(3)
    axis = np.array([
        r_err[2, 1] - r_err[1, 2],
        r_err[0, 2] - r_err[2, 0],
        r_err[1, 0] - r_err[0, 1],
    ]) / (2.0 * math.sin(theta))
    return axis * theta


def numeric_jacobian(thetas, eps=1e-6):
    n = len(thetas)
    T0 = forward_kinematics(thetas)
    p0, r0 = T0[:3, 3], T0[:3, :3]
    J = np.zeros((6, n))
    for i in range(n):
        dthetas = thetas.copy()
        dthetas[i] += eps
        Ti = forward_kinematics(dthetas)
        J[:3, i] = (Ti[:3, 3] - p0) / eps
        dR = Ti[:3, :3] @ r0.T
        J[3:, i] = np.array([
            dR[2, 1] - dR[1, 2],
            dR[0, 2] - dR[2, 0],
            dR[1, 0] - dR[0, 1],
        ]) / (2.0 * eps)
    return J


def inverse_kinematics(target_pos, target_r, theta_init, max_iters=300,
                        tol=1e-4, damping=0.05):
    thetas = np.array(theta_init, dtype=float)
    err = np.zeros(6)
    for iteration in range(max_iters):
        T = forward_kinematics(thetas)
        pos_err = target_pos - T[:3, 3]
        rot_err = rotation_error(T[:3, :3], target_r)
        err = np.concatenate([pos_err, rot_err])
        if np.linalg.norm(err) < tol:
            return thetas, True, iteration, float(np.linalg.norm(err))
        J = numeric_jacobian(thetas)
        JJt = J @ J.T + (damping ** 2) * np.eye(6)
        dtheta = J.T @ np.linalg.solve(JJt, err)
        thetas = thetas + dtheta
    return thetas, False, max_iters, float(np.linalg.norm(err))


def _pendiente_de_fabricar(pedido) -> int:
    """Piezas que hay que FABRICAR de verdad para un pedido: lo que le
    falta menos lo que ya hay en el almacen reservado para el
    (stock_disponible, el reparto FIFO que simula el Taller). Sesion
    2026-09-14, bug real: se lanzaba lo que faltaba sin descontar el stock
    ya fabricado -- con 8 Tuercas en el almacen se lanzaron 10 mas en vez de
    2. Con el reparto automatico apagado el pedido no avanza hasta
    "Repartir stock", pero el almacen queda justo con lo pedido."""
    falta = pedido.get('cantidad_pedida', 0) - pedido.get('cantidad_completada', 0)
    return max(0, falta - pedido.get('stock_disponible', 0))


def _demo_vivo(nombre):
    """¿Hay ya un proceso 'sorter_demo'/'loader_demo' corriendo en este
    contenedor, lo haya lanzado este panel o no? (sesion 2026-09-11). El panel
    solo conocia los procesos que lanzaba EL MISMO (self.proc_*): al cerrarlo y
    reabrirlo, el sorter_demo anterior seguia vivo y el panel lanzaba OTRO
    encima -- dos generaciones mandando ordenes contradictorias al mismo brazo,
    fallo que ya rompio la pinza. El patron es la ruta del ejecutable real (no
    'ros2 run ...', que tras el exec ya no aparece en su linea de comandos)."""
    try:
        return subprocess.run(
            ['pgrep', '-f', f'panda_controller/lib/panda_controller/{nombre}'],
            capture_output=True, timeout=2).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class TeleopGuiNode(Node):
    """Solo la parte ROS2 (publishers + cinematica + estado). Sin
    dependencia de Tkinter aqui, para que sea facil de razonar por
    separado -- la ventana (TeleopApp) la usa por composicion."""

    def __init__(self):
        super().__init__('teleop_gui')

        # Selector de robot (sesion 2026-08-30): que robot se controla AL
        # ARRANCAR ('loader' o 'sorter') -- despues se puede cambiar sin
        # reiniciar la ventana con los botones LOADER/SORTER del panel
        # (ver apply_preset). Los parametros de abajo (robot_base_*,
        # joint_topic, etc.) siguen definiendo el preset 'loader' tal cual
        # (para no romper overrides ya existentes); el preset 'sorter' es
        # la constante SORTER_PRESET de arriba.
        self.declare_parameter('robot', 'loader')
        self.declare_parameter('joint_topic', '/loader/joint_positions')
        self.declare_parameter('gripper_topic', '/loader/gripper_position')
        self.declare_parameter('led_topic', '/comando_led_loader')
        self.declare_parameter('robot_base_x', 0.5)
        self.declare_parameter('robot_base_y', -0.3)
        self.declare_parameter('robot_base_z', 0.74)
        self.declare_parameter('robot_base_yaw', 0.0)
        self.declare_parameter('gripper_open_position', 0.04)
        self.declare_parameter('gripper_closed_position', 0.025)
        self.declare_parameter('joint_offsets_deg', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -90.0])
        self.declare_parameter('max_wait_seconds', 45.0)
        # Posicion articular COMANDADA real de arranque (sesion 2026-08-27,
        # entrega de control manual desde sorter_hover_test.py): si viene
        # rellena (7 valores), la ventana arranca YA en esa pose en vez de
        # en HOME -- sin esto, al entregar el control justo encima del
        # cubo, el primer align_gripper_down() de la ventana calcularia
        # desde una pose de partida (HOME) que no es la real, y el brazo
        # daria un salto grande e indeseado nada mas abrir el panel.
        # Lista vacia como default confunde a rclpy (infiere BYTE_ARRAY y
        # luego rechaza el DOUBLE_ARRAY real que llega por -p) -- un
        # placeholder de longitud 1 (nunca 7 de verdad) fuerza el tipo
        # correcto y sigue distinguiendose de "no venia dado".
        self.declare_parameter('initial_commanded_joints', [0.0])

        # Camara cenital para "Centrar sobre cubo" (sesion 2026-08-27, a
        # peticion del usuario: entrar centrado a mano con los botones de 1cm
        # es dificil sin ver la alineacion real) -- defaults EXACTAMENTE los
        # de la camara original del Loader (overhead_vision.py), para lanzar
        # el panel con el Sorter hay que pasar sus propios valores (ver
        # sorter_demo.py: SORTER_CAM_*, SORTER_TABLE_*_RANGE).
        self.declare_parameter('camera_topic', '/overhead_camera/image_color')
        self.declare_parameter('camera_x', 0.5)
        self.declare_parameter('camera_y', 0.0)
        self.declare_parameter('camera_z', 2.27)
        self.declare_parameter('camera_table_x_min', 0.15)
        self.declare_parameter('camera_table_x_max', 0.85)
        self.declare_parameter('camera_table_y_min', -0.55)
        self.declare_parameter('camera_table_y_max', 0.55)
        self.declare_parameter('cube_table_z', 0.77)

        # Panel de pedidos (sesion 2026-08-28): Taller_Administracion vive en
        # OTRO contenedor/proyecto (docker-compose propio, red propia), no en
        # panda_ros_net -- 'taller_host' llega hasta el host real via el
        # extra_hosts añadido a ros2_app en docker-compose.yml (host-gateway),
        # y desde ahi el puerto 8000 publicado del otro proyecto. Nombre
        # deliberadamente DISTINTO del 'host.docker.internal' que ya usa el
        # servicio webots (ese apunta al propio contenedor webots, no al
        # host real -- mismo nombre con significado distinto habria sido
        # una trampa para el futuro). Parametro por si algun dia cambia la
        # URL/puerto.
        # 'taller_host' solo resuelve dentro de ESTA maquina. Si la linea
        # se lanza en OTRO ordenador de la red y Taller_Administracion
        # vive en uno distinto, hace falta una URL/IP real -- se guarda
        # por maquina en la pestaña Configuracion (config_cadena.py) y,
        # si hay una guardada, manda sobre este valor por defecto (sesion
        # 2026-09-18). self._taller_api_base_defecto se guarda para poder
        # volver a el si se borra el campo de la pestaña.
        self.declare_parameter('taller_api_base', 'http://taller_host:8000')
        self._taller_api_base_defecto = str(self.get_parameter('taller_api_base').value)
        self.taller_api_base = _cargar_taller_api_base() or self._taller_api_base_defecto
        # Taller_Administracion paso a exigir sesion real en /pedidos
        # (sesion 2026-08-29, sistema de usuarios/roles) -- el panel del
        # operador necesita ver TODOS los pedidos pendientes de cualquier
        # cliente, no solo los de una empresa, asi que se loguea como
        # admin_sistema (admin/admin -- sesion 2026-09-12 renombro el admin
        # sembrado de "aladin" a "admin" con contrasena real, ver auth.py
        # de ese proyecto). Token en memoria, se renueva solo si caduca/el
        # otro servidor se reinicia (ver _taller_login).
        self.taller_token = None
        # Ver CONFIG_MAQUINA_PATH mas arriba -- se carga aqui una vez, al
        # arrancar el nodo, y se mantiene en memoria hasta que la interfaz
        # (TeleopApp.guardar_numero_maquina) lo cambie y lo vuelva a guardar.
        self.numero_maquina = _cargar_numero_maquina()
        # Igual que numero_maquina: en memoria, lo cambia
        # TeleopApp.guardar_grupo_cadena. Decide que pedidos se ven y se
        # pueden reclamar (ver fetch_pedidos_pendientes).
        self.grupo_cadena = _cargar_grupo_cadena()
        self.cube_table_z = float(self.get_parameter('cube_table_z').value)

        self._presets = {
            'loader': {
                'label': 'Loader',
                'joint_topic': str(self.get_parameter('joint_topic').value),
                'gripper_topic': str(self.get_parameter('gripper_topic').value),
                'led_topic': str(self.get_parameter('led_topic').value),
                'base': (
                    float(self.get_parameter('robot_base_x').value),
                    float(self.get_parameter('robot_base_y').value),
                    float(self.get_parameter('robot_base_z').value),
                ),
                'base_yaw': float(self.get_parameter('robot_base_yaw').value),
                'camera_topic': str(self.get_parameter('camera_topic').value),
                'camera': (
                    float(self.get_parameter('camera_x').value),
                    float(self.get_parameter('camera_y').value),
                    float(self.get_parameter('camera_z').value),
                ),
                'table_x': (
                    float(self.get_parameter('camera_table_x_min').value),
                    float(self.get_parameter('camera_table_x_max').value),
                ),
                'table_y': (
                    float(self.get_parameter('camera_table_y_min').value),
                    float(self.get_parameter('camera_table_y_max').value),
                ),
            },
            'sorter': dict(SORTER_PRESET),
        }

        # Publishers FIJOS a las dos Picos, independientes de cual robot
        # este seleccionado en el panel (sesion 2026-09-03, bug real:
        # send_stop/send_rearm usaban self.pub_led, que apply_preset()
        # destruye y recrea segun el selector LOADER/SORTER -- con el
        # panel en modo Loader, REARME solo llegaba a la Pico del Loader
        # y la Pico W del Sorter se quedaba parpadeando en rojo para
        # siempre, aunque /emergency_stop -- el aviso de verdad que para
        # el brazo -- SI es global. El parpadeo es solo cosmetico, pero
        # el usuario lo ve como "no puedo apagarlo desde el panel"). Aqui
        # SIEMPRE se avisa a las dos Picos a la vez, venga de donde venga
        # la parada.
        self.pub_led_loader = self.create_publisher(String, self._presets['loader']['led_topic'], 10)
        self.pub_led_sorter = self.create_publisher(String, self._presets['sorter']['led_topic'], 10)

        # Nombre del producto para la pantalla OLED de la Pico del Loader
        # (sesion 2026-09-18). Este panel es el unico que conoce el NOMBRE
        # del producto (lo saca de Taller_Administracion); de aqui para
        # abajo -- loader_demo, sorter_demo, led_publisher_usb -- solo
        # viajan letras de color. Publicar aunque no haya pantalla no
        # cuesta nada ni cambia nada, igual que con los LED.
        self.pub_texto_producto = self.create_publisher(String, '/texto_producto', 10)

        # Estado de los 3 LEDs para pintar "bolas" en el panel (sesion
        # 2026-09-17, a peticion del usuario: "si no hay rasberri pi vemos
        # aqui lo hace" -- las Pico son opcionales, ver
        # [[robotica_pico_dos_dispositivos_led]], pero el comando LED se
        # publica igual este o no la Pico fisica para recibirlo. Escuchando
        # los mismos topics que ya se publican (agarre Loader/Sorter +
        # producto) el panel puede pintar el color de verdad SIN depender
        # de que haya hardware conectado -- funciona tanto si el comando
        # viene de este mismo panel (jog manual) como de loader_demo/
        # sorter_demo en produccion automatica.
        self.led_loader_cmd = '0'
        self.led_sorter_cmd = '0'
        self.led_producto_cmd = '0'
        self.create_subscription(String, self._presets['loader']['led_topic'], self._on_led_loader, 10)
        self.create_subscription(String, self._presets['sorter']['led_topic'], self._on_led_sorter, 10)
        self.create_subscription(String, '/comando_led_producto', self._on_led_producto, 10)

        # Mismo principio que los LED de arriba, aplicado a la pantalla
        # OLED del Loader (sesion 2026-09-18, a peticion del usuario: "creo
        # que tenemos mas lineas sin usar... añade el display al simulador
        # de rasberri pi pico"): escuchando el mismo topic que ya reenvia
        # led_publisher_usb a la Pico de verdad, el panel puede simular lo
        # que dice la pantalla SIN depender de que haya una OLED fisica
        # conectada.
        self.texto_producto_cmd = ''
        self.create_subscription(String, '/texto_producto', self._on_texto_producto, 10)
        # Pulsacion larga del boton fisico de la Pico del Loader (ver
        # led_publisher_usb): el hilo de ROS solo levanta la bandera y el
        # panel (hilo de Tk) la atiende en _vigilar_reset_clave.
        self.reset_clave_pedido = False
        self.create_subscription(Bool, '/reset_clave_pedido', self._on_reset_clave_pedido, 10)

        self.gripper_open = float(self.get_parameter('gripper_open_position').value)
        self.gripper_closed = float(self.get_parameter('gripper_closed_position').value)
        offsets_deg = list(self.get_parameter('joint_offsets_deg').value)
        self.offsets_rad = np.radians(offsets_deg)
        self.max_wait_seconds = float(self.get_parameter('max_wait_seconds').value)

        # robot_name/pub_joint/pub_gripper/pub_led/base/locator: ninguno
        # existe todavia -- apply_preset() los crea desde cero (misma
        # ruta de codigo que usara luego el selector LOADER/SORTER del
        # panel para cambiar en caliente, ver TeleopApp.switch_robot).
        self.robot_name = None
        self.pub_joint = None
        self.pub_gripper = None
        self.pub_led = None
        self.locator = None
        self.apply_preset(str(self.get_parameter('robot').value))

        # STOP/REARME integrados en el mismo panel (sesion 2026-08-27, antes
        # solo existian en estop_panel.py): mismo topic /emergency_stop de
        # toda la celda, asi que un STOP desde aqui pausa tambien cualquier
        # demo automatica (loader_demo/sorter_demo) que este corriendo a la
        # vez, y viceversa -- todos escuchan el mismo topic global.
        self.stopped = False
        self._on_stop_change = None  # lo fija TeleopApp tras construir la UI
        self.pub_stop = self.create_publisher(Bool, '/emergency_stop', 10)
        self.create_subscription(Bool, '/emergency_stop', self._on_emergency_stop, 10)

        # Contador de piezas REALMENTE fabricadas, sesion 2026-08-31 --
        # correccion del usuario: el contador de progreso del panel NO debe
        # depender de si Taller_Administracion tiene el reparto automatico
        # activado o no ("si el operario le ha pedido que haga 20 piezas
        # hace 20 piezas y se va al almacen, es administracion quien decide
        # luego el reparto"). Se cuenta aqui, del lado del robot, escuchando
        # la MISMA confirmacion de entrega real que ya usa
        # warehouse_supervisor_driver.py para reciclar -- no depende en
        # nada de Taller_Administracion ni de si hay pedidos o no.
        self.entregas_color = {'R': 0, 'G': 0, 'B': 0}
        self.ultima_entrega_t = None  # time.monotonic() de la ultima entrega real
        self.create_subscription(String, '/warehouse/cube_delivered', self._on_cube_delivered, 10)

        # Aviso de "lote nuevo" para el Sorter (sesion 2026-08-31, ver
        # SorterDemo._on_nuevo_lote): el Loader es un proceso nuevo en cada
        # lote y ya baila solo al arrancar, pero el Sorter persiste entre
        # lotes -- necesita que se le avise por topic.
        self.pub_nuevo_lote = self.create_publisher(Bool, '/production/nuevo_lote', 10)
        # Color objetivo del lote activo (sesion 2026-09-01, ver
        # SorterDemo._on_lote_color_objetivo): '' = sin lote de un solo
        # producto (reparto mixto), letra = todo lo entregado en este lote
        # cuenta como ese producto. QoS latched (TRANSIENT_LOCAL) para que
        # el Sorter lo reciba aunque arranque despues de este publish.
        self.pub_lote_color_objetivo = self.create_publisher(
            String, '/production/lote_color_objetivo', LOTE_COLOR_QOS)

        self.home_raw = np.array(HOME_POSITIONS) - self.offsets_rad
        initial_commanded = list(self.get_parameter('initial_commanded_joints').value)
        if len(initial_commanded) == 7:
            self.thetas = np.array(initial_commanded) - self.offsets_rad
            self.get_logger().info(
                f'Arrancando en pose entregada (no HOME): {list(np.round(initial_commanded, 4))}')
        else:
            self.thetas = self.home_raw.copy()
        self.step = STEP_DEFAULT
        # Giro de la pinza alrededor de su propio eje Z (sesion 2026-08-27,
        # botones de giro): 0.0 = orientacion base GRASP_R, sin girar. Se
        # resetea a 0.0 en HOME/Orientar-abajo porque esas acciones ya
        # reorientan directamente a GRASP_R (yaw=0) -- sin resetearlo aqui
        # el estado mostrado/usado quedaria desincronizado del giro real.
        self.yaw = 0.0
        self.yaw_step = np.radians(YAW_STEP_DEG)

        # Entrada de control por topic, ademas de los botones: permite
        # automatizar secuencias de movimientos (script externo) usando
        # exactamente el mismo motor/estado que la GUI, sin reimplementar la
        # cinematica por fuera ni perder la continuidad de self.thetas.
        # Formatos: "move dx dy dz", "open", "close", "home", "align".
        self.create_subscription(String, '/teleop_auto_cmd', self._on_auto_cmd, 10)

    def apply_preset(self, name):
        """Recrea publishers/locator/base para el robot 'name' ('loader' o
        'sorter'). Se llama una vez al arrancar y de nuevo cada vez que el
        operario cambia de robot desde el panel (sesion 2026-08-30) -- NO
        toca self.thetas/self.yaw (eso lo decide quien la llama: al
        arrancar se respeta initial_commanded_joints/HOME de siempre; al
        cambiar de robot en caliente, TeleopApp.switch_robot los resetea a
        HOME antes de reorientar, porque la pose articular de un robot no
        tiene por que ser una postura valida/segura para el otro)."""
        if name not in self._presets:
            raise ValueError(f"robot '{name}' desconocido, debe ser uno de {list(self._presets)}")
        preset = self._presets[name]
        if self.pub_joint is not None:
            self.destroy_publisher(self.pub_joint)
            self.destroy_publisher(self.pub_gripper)
            self.destroy_publisher(self.pub_led)
        if self.locator is not None:
            self.destroy_subscription(self.locator.sub)

        self.robot_name = name
        self.pub_joint = self.create_publisher(Float64MultiArray, preset['joint_topic'], 10)
        self.pub_gripper = self.create_publisher(Float64, preset['gripper_topic'], 10)
        self.pub_led = self.create_publisher(String, preset['led_topic'], 10)
        self.base = np.array(preset['base'])
        # La cinematica del panel (forward_kinematics/inverse_kinematics) trabaja
        # en el marco de la BASE del robot; el mundo se obtiene girando base_yaw
        # en Z (ver SORTER_PRESET). Con 0.0 (Loader) todo queda igual que antes.
        self.base_yaw = float(preset.get('base_yaw', 0.0))
        self.locator = OverheadLocator(
            self, topic=preset['camera_topic'],
            cam_x=preset['camera'][0], cam_y=preset['camera'][1], cam_z=preset['camera'][2],
            table_x_range=preset['table_x'], table_y_range=preset['table_y'])
        self.get_logger().info(
            f"Controlando ahora: {preset['label']} "
            f"(joints={preset['joint_topic']}, led={preset['led_topic']})")

    def _on_auto_cmd(self, msg: String):
        parts = msg.data.strip().split()
        if not parts:
            return
        cmd = parts[0]
        if cmd == 'move' and len(parts) == 4:
            dx, dy, dz = (float(x) for x in parts[1:])
            ok, text = self.move_delta(dx, dy, dz)
            p = self.tcp_world()
            self.get_logger().info(
                f'[auto] move dx={dx:.4f} dy={dy:.4f} dz={dz:.4f} -> '
                f'{"OK" if ok else "RECHAZADO"} pos=({p[0]:.4f},{p[1]:.4f},{p[2]:.4f}) {text}')
        elif cmd == 'open':
            ok = self.set_gripper(self.gripper_open)
            self.get_logger().info(f'[auto] ABRIR pinza -> {"OK" if ok else "RECHAZADO (parado)"}')
        elif cmd == 'close':
            ok = self.set_gripper(self.gripper_closed)
            self.get_logger().info(f'[auto] CERRAR pinza -> {"OK" if ok else "RECHAZADO (parado)"}')
        elif cmd == 'home':
            ok, text = self.go_home()
            self.get_logger().info(f'[auto] HOME -> {"OK" if ok else "RECHAZADO"} {text}')
        elif cmd == 'align':
            ok, text = self.align_gripper_down()
            self.get_logger().info(f'[auto] align -> {"OK" if ok else "RECHAZADO"} {text}')
        elif cmd == 'rotate' and len(parts) == 2:
            dyaw = np.radians(float(parts[1]))
            ok, text = self.rotate_delta(dyaw)
            self.get_logger().info(f'[auto] rotate {parts[1]} deg -> {"OK" if ok else "RECHAZADO"} {text}')
        else:
            self.get_logger().warn(f'[auto] comando no reconocido: {msg.data!r}')

    def wait_for_subscribers(self):
        elapsed = 0.0
        while rclpy.ok() and elapsed < self.max_wait_seconds:
            ready = (
                self.pub_joint.get_subscription_count() > 0
                and self.pub_gripper.get_subscription_count() > 0
            )
            if ready:
                return True
            rclpy.spin_once(self, timeout_sec=0.1)
            elapsed += 0.1
        return False

    def _publish_joint(self, raw_thetas):
        # NO se envuelve con modulo (x+pi)%(2pi)-pi: para jogging continuo
        # con pasos pequenos, raw_thetas ya se mantiene en un rango sensato
        # (siempre sembrado desde el valor anterior). Envolver por modulo
        # puede producir un salto de ~2pi en el angulo COMANDADO cuando el
        # valor bruto cruza por poco el borde -pi/+pi -- justo el caso de
        # panda_joint4, cuyo limite real inferior (-3.1416) esta pegado a ese
        # borde. Bug real visto en Webots: warnings "too big/too low
        # requested position" con valores ~+-3.13 y el brazo dando un salto
        # visual grande ("se ha encogido") aunque el angulo bruto solo habia
        # cambiado un poco. En vez de envolver, se recorta a los limites
        # reales de cada articulacion (ver move_delta para el rechazo previo
        # si el recorte necesario es grande).
        commanded = raw_thetas + self.offsets_rad
        clamped = np.clip(commanded, JOINT_LIMITS_LO, JOINT_LIMITS_HI)
        self.pub_joint.publish(Float64MultiArray(data=clamped.tolist()))
        # Reconciliar self.thetas con lo que REALMENTE se ha mandado (clamped),
        # no con el resultado bruto de la IK: el recorte a limites reales se
        # permite silenciosamente hasta 1 deg (ver _clamp_excess_deg), y sin
        # esto ese recorte se pierde -- self.thetas se va alejando poco a poco
        # de la pose fisica real en Webots aunque cada paso individual parezca
        # aceptado, arrastrando un error grande tras muchos pasos seguidos en
        # la misma direccion (bug real: 130 pasos automatizados via
        # /teleop_auto_cmd terminaron a >30cm de donde el propio codigo credia
        # estar, confirmado con el supervisor orientation_probe).
        self.thetas = clamped - self.offsets_rad
        return clamped

    def tcp_world(self):
        return rz(self.base_yaw) @ forward_kinematics(self.thetas)[:3, 3] + self.base

    def _clamp_excess_deg(self, thetas):
        commanded = thetas + self.offsets_rad
        clamped = np.clip(commanded, JOINT_LIMITS_LO, JOINT_LIMITS_HI)
        return float(np.degrees(np.max(np.abs(commanded - clamped))))

    # OJO (2026-09-11): el jog manual NO se bloquea durante la parada de
    # emergencia, a proposito. La parada es una PAUSA, no un abort: el
    # operario tiene que poder mover el brazo a mano (desatascar un cubo,
    # apartarlo del sensor de proximidad HC-SR04 del Loader) y al rearmar el
    # robot retoma donde lo dejo (ver _wait_while_stopped en
    # cube_shuttle_demo.py). En el proyecto replica se metieron guardas
    # "if self.stopped" aqui creyendo que era un bug, y dejaban al operario
    # sin forma de recuperar la celda. No anadirlas.
    def move_delta(self, dx, dy, dz, _depth=0, _split=False):
        """Devuelve (ok, mensaje). Mismo filtro de salto grande que
        teleop_manual.py: solo se acepta la solucion continua sembrada
        desde la pose actual, nunca una de semillas aleatorias, para que un
        click nunca haga que el brazo "salte" a otra configuracion. Ademas
        se rechaza si la solucion se sale de verdad de los limites reales de
        alguna articulacion (ver _publish_joint).

        Si el paso pedido exige un giro grande (posible cambio de rama del
        codo/singularidad), en vez de rechazarlo de golpe se subdivide en dos
        mitades y se resuelven/publican una tras otra (recursivo, hasta
        _MAX_SPLIT_DEPTH veces) -- el mismo efecto que pulsar "- paso" y
        repetir el click a mano, pero automatico. Si ni el paso mas pequeno
        cabe bajo el limite, se rechaza igual que antes.

        YA NO bloquea con la parada de emergencia activa (sesion 2026-09-10,
        peticion explicita del usuario): "cuando salta la parada de
        emergencia tiene que dejar mover el robot a mano" -- justo lo que
        hace falta para liberar a mano un dedo trabado sin esperar a que el
        rearme (que no arregla nada fisico por si solo) lo resuelva. Riesgo
        conocido y ACEPTADO por el usuario: si hay una demo automatica
        (sorter_demo/loader_demo) en pausa por esta misma parada, su
        self.real_theta (la ultima pose que ELLA comando, no una lectura de
        sensor) se queda desactualizado -- al rearmar puede pedir un
        movimiento grande de golpe para "volver" a donde ella cree que
        estaba, en vez de continuar suave desde donde lo dejaste. No hay
        proteccion automatica contra eso todavia."""
        target_world = self.tcp_world() + np.array([dx, dy, dz])
        # Mundo -> marco de la base (giro -base_yaw), en posicion Y en
        # orientacion: el giro 'yaw' de la pinza es respecto al MUNDO.
        target_base = rz(-self.base_yaw) @ (target_world - self.base)
        target_r = rz(-self.base_yaw) @ GRASP_R @ rz(self.yaw)
        thetas, converged, iters, err = inverse_kinematics(target_base, target_r, self.thetas)
        if not converged:
            return False, f'No puedo llegar ahi (IK no convergio, error={err:.4f}).'
        jump_deg = float(np.degrees(np.max(np.abs(thetas - self.thetas))))
        if jump_deg > MAX_JOINT_JUMP_DEG:
            if _depth < _MAX_SPLIT_DEPTH and max(abs(dx), abs(dy), abs(dz)) > STEP_MIN:
                half = (dx / 2.0, dy / 2.0, dz / 2.0)
                ok1, msg1 = self.move_delta(*half, _depth=_depth + 1, _split=True)
                if not ok1:
                    return False, f'Subdividido pero atascado a mitad de camino: {msg1}'
                ok2, msg2 = self.move_delta(*half, _depth=_depth + 1, _split=True)
                if not ok2:
                    return False, f'Subdividido pero atascado a mitad de camino: {msg2}'
                return True, f'OK (dividido en pasos mas pequenos, giro maximo visto {jump_deg:.1f} deg)'
            return False, (f'Ese movimiento exige un giro de {jump_deg:.1f} deg en alguna '
                            'articulacion incluso en el paso mas pequeno (posible singularidad '
                            'real); prueba otra direccion.')
        excess_deg = self._clamp_excess_deg(thetas)
        if excess_deg > 1.0:
            return False, (f'Esa posicion se sale {excess_deg:.1f} deg del limite real de '
                            'alguna articulacion (probable estas tocando el limite fisico del '
                            'brazo); prueba otra direccion. No me muevo.')
        self.thetas = thetas
        self._publish_joint(self.thetas)
        if _split:
            time.sleep(0.15)
        return True, 'OK' if not _split else 'OK (paso intermedio)'

    def go_home(self):
        # Ya no bloquea con la parada activa -- ver move_delta() para el
        # porque completo (sesion 2026-09-10).
        self.thetas = self.home_raw.copy()
        self.yaw = 0.0
        self._publish_joint(self.thetas)
        return True, 'OK'

    def align_gripper_down(self):
        """Sin filtro de salto articular (ver teleop_manual.py): reorientar
        desde HOME es una reconfiguracion grande pero deliberada. Si mantiene
        el filtro de limites reales de articulacion. Ya no bloquea con la
        parada activa -- ver move_delta() para el porque completo
        (sesion 2026-09-10)."""
        current_pos = forward_kinematics(self.thetas)[:3, 3]
        thetas, converged, iters, err = inverse_kinematics(
            current_pos, rz(-self.base_yaw) @ GRASP_R, self.thetas)
        if not converged:
            return False, f'No he podido orientar la pinza (error={err:.4f}).'
        excess_deg = self._clamp_excess_deg(thetas)
        if excess_deg > 1.0:
            return False, (f'La orientacion hacia abajo aqui se sale {excess_deg:.1f} deg del '
                            'limite real de alguna articulacion. No me muevo.')
        jump_deg = float(np.degrees(np.max(np.abs(thetas - self.thetas))))
        self.thetas = thetas
        self.yaw = 0.0
        self._publish_joint(self.thetas)
        return True, f'Pinza orientada hacia abajo (giro {jump_deg:.1f} deg).'

    def rotate_delta(self, dyaw):
        """Gira la pinza alrededor de su propio eje Z sin mover el TCP
        (misma posicion, solo orientacion) -- mismo filtro de salto grande y
        de limites reales que move_delta, para que un click nunca "salte" a
        otra configuracion del brazo. Ya no bloquea con la parada activa --
        ver move_delta() para el porque completo (sesion 2026-09-10)."""
        current_pos = forward_kinematics(self.thetas)[:3, 3]
        new_yaw = self.yaw + dyaw
        target_r = rz(-self.base_yaw) @ GRASP_R @ rz(new_yaw)
        thetas, converged, iters, err = inverse_kinematics(current_pos, target_r, self.thetas)
        if not converged:
            return False, f'No puedo girar ahi (IK no convergio, error={err:.4f}).'
        jump_deg = float(np.degrees(np.max(np.abs(thetas - self.thetas))))
        if jump_deg > MAX_JOINT_JUMP_DEG:
            return False, (f'Ese giro exige {jump_deg:.1f} deg de golpe en alguna articulacion '
                            '(posible singularidad); prueba un paso mas pequeno.')
        excess_deg = self._clamp_excess_deg(thetas)
        if excess_deg > 1.0:
            return False, (f'Ese giro se sale {excess_deg:.1f} deg del limite real de alguna '
                            'articulacion. No giro.')
        self.thetas = thetas
        self.yaw = new_yaw
        self._publish_joint(self.thetas)
        return True, f'Girado a {np.degrees(self.yaw):.1f} grados.'

    def center_on_cube(self):
        """Ajusta SOLO X/Y (misma Z) para quedar centrado sobre el cubo que
        vea la camara cenital ahora mismo, usando la misma localizacion de
        un solo disparo que el agarre automatico -- deja el descenso final
        (Z) en manos del usuario, que es la parte que de verdad quiere
        controlar el mismo. Ya no bloquea con la parada activa -- ver
        move_delta() para el porque completo (sesion 2026-09-10)."""
        color = self.locator.detect_color()
        if color is None:
            return False, 'No se ve ningun cubo en la camara cenital.'
        located = self.locator.locate_with_yaw(self.cube_table_z, color=color)
        if located is None:
            return False, 'Cubo detectado pero no se pudo localizar con precision.'
        x, y, _yaw_offset = located
        current = self.tcp_world()
        # Salvaguarda (sesion 2026-08-27, aviso real del usuario: un
        # centrado hecho demasiado bajo golpeo el cubo de lado y salio
        # disparado): el ajuste de X/Y solo se hace si la pinza esta a
        # AL MENOS 5cm por encima de la mesa/cinta -- un movimiento lateral
        # a ras del cubo es un golpe, no un centrado.
        min_safe_z = self.cube_table_z + 0.05
        if current[2] < min_safe_z:
            return False, (f'Demasiado bajo para centrar sin riesgo (z={current[2]:.3f}, '
                            f'hace falta al menos {min_safe_z:.3f}) -- sube primero con Z+.')
        dx, dy = float(x - current[0]), float(y - current[1])
        ok, msg = self.move_delta(dx, dy, 0.0)
        name = COLOR_NAMES.get(color, color)
        if ok:
            return True, f'Centrado sobre cubo {name} en ({x:.3f},{y:.3f}).'
        return False, f'Cubo {name} visto en ({x:.3f},{y:.3f}) pero el movimiento fue rechazado: {msg}'

    def set_gripper(self, position):
        # Ya no bloquea con la parada activa (sesion 2026-09-10, peticion
        # explicita del usuario) -- es justo el control que hace falta para
        # soltar a mano un dedo trabado ("se ha roto la pinza y no puedo
        # rearmar") sin esperar a que el rearme, que no arregla nada fisico
        # por si solo, lo resuelva. Ver move_delta() para el riesgo conocido
        # y aceptado (demo automatica en pausa con self.real_theta
        # desactualizado).
        self.pub_gripper.publish(Float64(data=position))
        return True

    def set_led(self, letter):
        self.pub_led.publish(String(data=letter))

    def _on_led_loader(self, msg):
        self.led_loader_cmd = msg.data.strip()

    def _on_led_sorter(self, msg):
        self.led_sorter_cmd = msg.data.strip()

    def _on_led_producto(self, msg):
        self.led_producto_cmd = msg.data.strip()

    def _on_texto_producto(self, msg):
        self.texto_producto_cmd = msg.data

    def _on_reset_clave_pedido(self, msg):
        if msg.data:
            self.reset_clave_pedido = True

    def _on_emergency_stop(self, msg):
        if bool(msg.data) != self.stopped:
            self.stopped = bool(msg.data)
            if self._on_stop_change is not None:
                self._on_stop_change(self.stopped)

    def _on_cube_delivered(self, msg):
        color = msg.data.strip().upper()
        if color in self.entregas_color:
            self.entregas_color[color] += 1
            self.ultima_entrega_t = time.monotonic()  # ver TeleopApp._lote_en_curso

    def send_stop(self):
        self.pub_stop.publish(Bool(data=True))
        # Igual que estop_panel.py: avisa tambien a las Picos para que
        # parpadeen en rojo, mismo efecto visual venga la parada de donde
        # venga. A LAS DOS siempre (ver pub_led_loader/pub_led_sorter),
        # no solo a la del robot seleccionado en el panel -- /emergency_stop
        # es global, el aviso visual tiene que serlo tambien.
        self.pub_led_loader.publish(String(data='parada'))
        self.pub_led_sorter.publish(String(data='parada'))

    def send_rearm(self):
        self.pub_stop.publish(Bool(data=False))
        self.pub_led_loader.publish(String(data='rearme'))
        self.pub_led_sorter.publish(String(data='rearme'))

    def _taller_login(self):
        """POST /login como admin_sistema (admin/admin) -- necesario desde
        que Taller_Administracion exige sesion real en /pedidos (sesion
        2026-08-29). Devuelve True/False; no lanza."""
        url = self.taller_api_base.rstrip('/') + '/login'
        body = json.dumps({'username': 'admin', 'password': 'admin'}).encode('utf-8')
        req = urllib.request.Request(
            url, data=body, method='POST', headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                self.taller_token = json.loads(resp.read().decode('utf-8'))['token']
            return True
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
            self.taller_token = None
            return False

    def fetch_pedidos_pendientes(self):
        """GET /pedidos en Taller_Administracion, filtrando los que no
        estan 'completado'. Devuelve None si el servidor no responde o no
        hay sesion valida -- el panel de teleop no debe romperse por
        esto, el operador simplemente ve el aviso de sin conexion.
        Se loguea solo (una vez, y de nuevo si el token caduca -- p.ej.
        el otro servidor se reinicio y perdio sus sesiones en memoria)
        para ver TODOS los pedidos de cualquier cliente, no solo uno."""
        if self.taller_token is None and not self._taller_login():
            return None
        url = self.taller_api_base.rstrip('/') + '/pedidos'
        for reintento in (1, 2):
            req = urllib.request.Request(url, headers={'X-Session-Token': self.taller_token})
            try:
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    pedidos = json.loads(resp.read().decode('utf-8'))
                # 'cancelado' (sesion 2026-09-10, nuevo en Taller_Administracion)
                # tampoco es "pendiente" para el operario -- antes solo se
                # excluia 'completado', asi que un pedido cancelado se seguia
                # ofreciendo aqui como si hubiera que fabricarlo.
                #
                # Ademas: un pedido cuyo stock_disponible YA cubre el 100% de
                # lo que falta se oculta tambien (peticion explicita del
                # usuario, sesion 2026-09-10: "un operario solo tiene que ver
                # lo que tiene pendiente, no lo que ya fabrico"). stock_disponible
                # simula el mismo reparto FIFO que haria /almacen/repartir SIN
                # tocar la BBDD (ver _con_stock_disponible en Taller_Administracion),
                # asi que funciona igual con reparto_automatico activado o no --
                # a diferencia de 'estado', que con el interruptor desactivado se
                # queda en 'pendiente' aunque ya este todo fabricado (ver memoria
                # robotica_taller_administracion.md). Esto NO cambia el estado
                # real del pedido en la BBDD ni lo reparte -- es solo un filtro
                # de la vista del operario; admin_cliente/admin_sistema lo siguen
                # viendo tal cual en el panel web de administracion.
                # numero_maquina del pedido (sesion 2026-09-14, a peticion
                # del usuario, antes era "0 o el mio"): solo los que estan a
                # nombre del Grupo Cadena de esta celda o de su Nº Maquina.
                # Los libres (0) solo salen si el grupo es 0. El grupo sirve
                # para reconfigurar la fabrica: una cadena solo hace ciertas
                # piezas. Filtrado aqui (el unico sitio donde se obtienen
                # pedidos pendientes) para que lo herede cualquier camino
                # que lance produccion, boton o modo Automatico.
                return [
                    p for p in pedidos
                    if p.get('estado') not in ('completado', 'cancelado')
                    and p.get('stock_disponible', 0) < (p.get('cantidad_pedida', 0) - p.get('cantidad_completada', 0))
                    and p.get('numero_maquina', 0) in (self.grupo_cadena, self.numero_maquina)
                ]
            except urllib.error.HTTPError as e:
                if e.code in (401, 422) and reintento == 1 and self._taller_login():
                    continue
                return None
            except (urllib.error.URLError, TimeoutError, ValueError):
                return None
        return None

    def reclamar_pedido(self, pedido_id, forzar=False) -> bool:
        """POST /pedidos/{id}/reclamar con self.numero_maquina -- hay que
        llamarlo ANTES de lanzar produccion para ese pedido (ver
        _lanzar_produccion y sus llamantes). True si lo consigue (estaba
        libre, o ya era mio); False si esta cogido por otra celda o hay
        cualquier fallo de red -- en los dos casos, quien llama no debe
        lanzar produccion para ese pedido."""
        if self.taller_token is None and not self._taller_login():
            return False
        url = f"{self.taller_api_base.rstrip('/')}/pedidos/{pedido_id}/reclamar"
        body = json.dumps({'numero_maquina': self.numero_maquina, 'grupo_cadena': self.grupo_cadena,
                           'forzar': forzar}).encode('utf-8')
        for reintento in (1, 2):
            req = urllib.request.Request(
                url, data=body, method='POST',
                headers={'X-Session-Token': self.taller_token, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    resp.read()
                return True
            except urllib.error.HTTPError as e:
                if e.code in (401, 422) and reintento == 1 and self._taller_login():
                    continue
                return False  # 409 incluido: ya es de otra celda
            except (urllib.error.URLError, TimeoutError, ValueError):
                return False
        return False

    def marcar_cubo_clasificado(self, color, producto_id=None):
        """POST /taller/cubo_clasificado -- lo llama el operador a mano
        desde el panel justo despues de colocar la pieza el mismo, ya que
        de momento no hay ninguna celda automatica publicando esto por su
        cuenta (ver README de Taller_Administracion).

        'producto_id' (sesion 2026-09-15, a peticion explicita del
        usuario: "el LED es una parte nuestra para jugar pero no tiene
        que influir en la logica de negocio"): identifica el producto
        directamente, sin pasar por el color -- funciona igual con o sin
        LED asignado. Si no se manda, el backend sigue resolviendo por
        color como hasta ahora (compatibilidad)."""
        url = self.taller_api_base.rstrip('/') + '/taller/cubo_clasificado'
        # Maquina y grupo (2026-09-14): la pieza solo cuenta para pedidos de
        # esta cadena, no para los de otra (ver CuboClasificado en el Taller).
        cuerpo = {'color': color, 'numero_maquina': self.numero_maquina,
                  'grupo_cadena': self.grupo_cadena}
        if producto_id is not None:
            cuerpo['producto_id'] = producto_id
        body = json.dumps(cuerpo).encode('utf-8')
        req = urllib.request.Request(
            url, data=body, method='POST',
            headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return True, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            # Cuerpo no-JSON (p.ej. un 500 en texto plano): antes json.loads
            # lanzaba aqui mismo y la excepcion escapaba al callback de Tk.
            cuerpo = e.read().decode('utf-8', errors='replace')
            try:
                detail = json.loads(cuerpo).get('detail', cuerpo)
            except ValueError:
                detail = cuerpo or str(e)
            return False, detail
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            return False, str(e)


class TeleopApp:
    """Aspecto de cuadro de mando industrial (sesion 2026-08-27, mismo
    convenio de colores que estop_panel.py) -- STOP/REARME viven en el
    mismo panel que el jog en vez de en una ventana aparte, para poder
    parar el brazo sin soltar el ratón del control manual."""

    def t(self, texto_es, **kwargs):
        """Traduce 'texto_es' (el propio castellano hace de clave, ver
        TRADUCCIONES mas arriba) al idioma activo; si no hay entrada para
        ese idioma o esa clave, devuelve el castellano tal cual -- nunca
        revienta por un texto sin traducir todavia."""
        texto = texto_es if self.idioma == 'es' else TRADUCCIONES.get(self.idioma, {}).get(texto_es, texto_es)
        return texto.format(**kwargs) if kwargs else texto

    def _retraducir_estaticos(self):
        """Llamado desde guardar_idioma(): aplica self.idioma a todo lo
        que se construyo UNA sola vez (ver self._i18n_widgets, rellenado
        por self.t()/mkbtn/mkframe/boton al crear cada widget) para que
        se vea el cambio YA, sin reiniciar el panel. Los bloques que se
        reconstruyen solos cada pocos segundos (pedidos pendientes,
        estado del lote) NO se fuerzan aqui a proposito -- llamarlos aqui
        duplicaria su propio root.after(...) de refresco periodico (ver
        refresh_pedidos/_poll_lote) y dejaria dos ciclos corriendo a la
        vez; se traducen solos en su proximo refresco normal (unos
        segundos como mucho)."""
        for widget, dato, kind in self._i18n_widgets:
            if kind == 'text':
                widget.config(text=self.t(dato))
            elif kind == 'text_fmt':
                clave, kwargs = dato
                widget.config(text=self.t(clave, **kwargs))
            elif kind == 'tab':
                clave, tab_widget = dato
                self.notebook.tab(tab_widget, text=self.t(clave))
        self._actualizar_titulo_ventana()
        self._actualizar_resumen_config()
        self._aplicar_bloqueo_config(self._config_desbloqueada)
        self._refrescar_estado_picos()

    def __init__(self, node: TeleopGuiNode):
        self.node = node
        self.node._on_stop_change = self.on_stop_change
        self.idioma = _cargar_idioma()
        self._i18n_widgets = []  # [(widget, texto_es, kind), ...] -- ver self.t() y _retraducir_estaticos
        self._reset_clave_token = None      # pulsacion simulada en curso (ver _pulsar_parada_simulada)
        self._reset_clave_dialogo = False   # ya hay una confirmacion abierta
        self._oled_previo_aviso = ''        # texto de la OLED que se repone tras el aviso
        self.root = tk.Tk()
        self.root.title(f'{self.t("Panel de control manual - Panda")} -- Ver. {VERSION}')
        self.root.configure(bg=BG)
        # Arranca ya a tamaño de pantalla completa (sesion 2026-09-17,
        # reportado por el usuario: "va bien cuando esta pantalla completa
        # pero no se ven si no estan a pantalla completa") -- sin esto,
        # Tkinter abre la ventana a su tamaño "pedido" segun el contenido,
        # que en pantallas normales puede quedarse mas pequeño que lo que
        # de verdad hace falta para ver todo (con muchos pedidos/pestañas
        # no hay barra de scroll fuera de las pestañas). self.root.state
        # ('zoomed') no es fiable en todos los gestores de ventanas X11 --
        # geometry() con el tamaño real de pantalla si lo es en todos. El
        # usuario puede seguir redimensionando/desmaximizando a mano
        # despues si quiere, esto solo fija el tamaño de ARRANQUE.
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0')

        # Panel entero con scroll (sesion 2026-09-17, reportado por el
        # usuario con captura: sin maximizar la ventana, con esta pantalla
        # se corta por la derecha -- "Nombre de la cadena"/resumen -- y por
        # abajo -- la fila Y+/Z- de Mover TCP -- sin forma de llegar a lo
        # cortado. El arranque a pantalla completa (mas arriba) no basta
        # por si solo: el usuario puede desmaximizar, o tener una pantalla
        # mas pequeña que el contenido. Mismo patron Canvas+Scrollbar que
        # ya se usaba dentro de las pestañas Configuracion/Produccion (ver
        # _construir_pestana_config y "Pedidos pendientes"), ahora tambien
        # ENVOLVIENDO TODO -- cabecera, STOP/REARME y las pestañas -- con
        # barra vertical Y horizontal. self.root ya no lleva widgets
        # directamente: todo cuelga de 'main_frame', el frame real que
        # vive dentro del canvas.
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        main_vscroll = tk.Scrollbar(self.root, orient='vertical', command=main_canvas.yview)
        main_hscroll = tk.Scrollbar(self.root, orient='horizontal', command=main_canvas.xview)
        main_frame = tk.Frame(main_canvas, bg=BG)
        main_frame.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))
        main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
        main_canvas.configure(yscrollcommand=main_vscroll.set, xscrollcommand=main_hscroll.set)
        main_canvas.grid(row=0, column=0, sticky='nsew')
        main_vscroll.grid(row=0, column=1, sticky='ns')
        main_hscroll.grid(row=1, column=0, sticky='we')

        def _main_mousewheel(event):
            main_canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

        def _main_shift_mousewheel(event):
            main_canvas.xview_scroll(-1 if event.delta > 0 else 1, 'units')

        def _main_bind_wheel(_event):
            main_canvas.bind_all('<MouseWheel>', _main_mousewheel)
            main_canvas.bind_all('<Shift-MouseWheel>', _main_shift_mousewheel)

        def _main_unbind_wheel(_event):
            main_canvas.unbind_all('<MouseWheel>')
            main_canvas.unbind_all('<Shift-MouseWheel>')

        main_canvas.bind('<Enter>', _main_bind_wheel)
        main_canvas.bind('<Leave>', _main_unbind_wheel)

        title_font = tkfont.Font(family='Arial', size=15, weight='bold')
        status_font = tkfont.Font(family='Arial', size=13, weight='bold')
        big = tkfont.Font(family='Arial', size=12, weight='bold')
        mono = tkfont.Font(family='monospace', size=11)
        self.big_font, self.mono_font = big, mono

        header = tk.Label(main_frame, text=self.t('PANEL DE CONTROL MANUAL'),
                           font=title_font, bg=BG, fg=YELLOW)
        header.grid(row=0, column=0, columnspan=5, padx=18, pady=(16, 4))
        self._i18n_widgets.append((header, 'PANEL DE CONTROL MANUAL', 'text'))

        # Ver. AAMM.NNNNN en la esquina, con place() para no tocar el grid
        # de arriba (sesion 2026-09-15, peticion explicita: verse tambien
        # aqui y no solo en el panel web).
        version_label = tk.Label(main_frame, text=f'Ver. {VERSION}',
                                  font=('Arial', 9), bg=BG, fg=GREY_TEXT)
        version_label.place(relx=1.0, x=-8, y=4, anchor='ne')

        stripe = tk.Canvas(main_frame, width=600, height=10, bg=BG, highlightthickness=0)
        stripe.grid(row=1, column=0, columnspan=5, pady=(0, 10))
        n_stripes = 30
        w = 600 / n_stripes
        for i in range(n_stripes):
            color = YELLOW if i % 2 == 0 else '#000000'
            stripe.create_rectangle(i * w, 0, (i + 1) * w, 10, fill=color, outline='')

        # --- STOP / REARME / estado, arriba del todo -----------------
        stop_panel = tk.Frame(main_frame, bg=PANEL_BG, bd=4, relief='ridge')
        stop_panel.grid(row=2, column=0, columnspan=5, padx=18, pady=(0, 10), sticky='we')

        # EN MARCHA + estado del lote, apiladas en una sola celda del grid
        # (sesion 2026-09-18, a peticion del usuario: "la informacion lote
        # loader sin lotes y sorter activo pon en la cabecera de en
        # marcha") -- antes el estado del lote solo se veia en la pestaña
        # Producción; aqui se ve desde cualquier pestaña sin cambiar de
        # una. self.lote_status_var es el mismo StringVar de siempre
        # (usado tambien mas abajo por la etiqueta de esa pestaña) --
        # _actualizar_estado_lote sigue siendo el unico sitio que lo pone.
        status_header = tk.Frame(stop_panel, bg=PANEL_BG)
        status_header.grid(row=0, column=0, columnspan=2, sticky='we')

        self.status_var = tk.StringVar(value=self.t('EN MARCHA'))
        self.status_label = tk.Label(status_header, textvariable=self.status_var, font=status_font,
                                      bg=PANEL_BG, fg=GREEN, pady=4)
        self.status_label.pack(fill='x')

        self.lote_status_var = tk.StringVar(value=self.t('Sin lote en curso.'))
        self.lote_status_header_label = tk.Label(
            status_header, textvariable=self.lote_status_var, font=self.mono_font,
            bg=PANEL_BG, fg=TEXT_LIGHT, justify='center')
        self.lote_status_header_label.pack(fill='x', pady=(0, 4))

        # Nombre de la cadena, libre, para diferenciar un panel de otro
        # (sesion 2026-09-13, a peticion del usuario: con dos lineas a la
        # vez las dos ventanas se ven identicas). Pide la misma clave que
        # el Nº Maquina (peticion explicita del usuario) antes de guardar
        # -- ver guardar_etiqueta. Se guarda en el mismo fichero que el Nº
        # Maquina (ver _escribir_config_panel), y se aplica tambien al
        # titulo de la ventana (se ve en la barra de tareas/alt-tab sin ni abrir el
        # panel).
        self.stop_btn = tk.Button(
            stop_panel, text=self.t('PARADA\nDE EMERGENCIA'), font=big, width=15, height=3,
            bg=RED, fg='white', activebackground=RED_DARK, activeforeground='white',
            relief='raised', bd=6, command=self.do_stop)
        self.stop_btn.grid(row=1, column=0, padx=14, pady=10)
        self._i18n_widgets.append((self.stop_btn, 'PARADA\nDE EMERGENCIA', 'text'))

        self.rearm_btn = tk.Button(
            stop_panel, text=self.t('REARME'), font=big, width=15, height=3,
            relief='raised', bd=6, state='disabled', command=self.do_rearm)
        self.rearm_btn.grid(row=1, column=1, padx=14, pady=10)
        self._i18n_widgets.append((self.rearm_btn, 'REARME', 'text'))

        # Etiqueta libre, a la derecha de STOP/REARME -- ahi sobraba mucho
        # hueco (stop_panel ocupa todo el ancho de la ventana, sticky='we',
        # pero por dentro solo usaba 2 columnas). Letra GRANDE a proposito
        # (peticion explicita del usuario: el triple que status_font) para
        # que se lea de un vistazo desde lejos, que es todo el sentido de
        # esto -- "Nombre de la cadena", no "Etiqueta" (mismo campo, texto
        # mas claro de lo que representa: que linea de produccion es esta).
        # Desde la sesion 2026-09-14 aqui solo se MUESTRA (a peticion del
        # usuario: nombre, Nº Maquina, Automatico y Pico se editan en la
        # pestaña Configuracion, con clave). Se sigue viendo grande en la
        # cabecera porque es para saber de un vistazo que linea es.
        etiqueta_font = tkfont.Font(family='Arial', size=status_font.cget('size') * 3, weight='bold')
        etiqueta_frame = tk.Frame(stop_panel, bg=PANEL_BG)
        etiqueta_frame.grid(row=1, column=2, columnspan=3, padx=(20, 14), sticky='w')
        lbl_nombre_cadena = tk.Label(etiqueta_frame, text=self.t('Nombre de la cadena:'), font=status_font,
                                      bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl_nombre_cadena.pack(anchor='w')
        self._i18n_widgets.append((lbl_nombre_cadena, 'Nombre de la cadena:', 'text'))
        self.etiqueta_mostrada_var = tk.StringVar()
        self.etiqueta_mostrada_label = tk.Label(
            etiqueta_frame, textvariable=self.etiqueta_mostrada_var, font=etiqueta_font,
            bg=PANEL_BG, fg=YELLOW)
        self.etiqueta_mostrada_label.pack(anchor='w', pady=(4, 6))
        # Resumen de solo lectura de la configuracion de la celda.
        self.resumen_config_var = tk.StringVar()
        tk.Label(etiqueta_frame, textvariable=self.resumen_config_var, font=self.mono_font,
                 bg=PANEL_BG, fg=TEXT_LIGHT, justify='left').pack(anchor='w')
        # Literal de la pantalla OLED de la Pico del Loader (sesion 2026-09-19,
        # a peticion del usuario: "debajo de Taller de Administracion, en una
        # linea si entra"). Es el MISMO texto que la OLED simulada de la
        # pestaña Pico (ver _refrescar_leds), aqui unido en una sola linea; si
        # no cabe, wraplength lo parte en vez de ensanchar la ventana.
        self.oled_linea_var = tk.StringVar()
        tk.Label(etiqueta_frame, textvariable=self.oled_linea_var, font=self.mono_font,
                 bg=PANEL_BG, fg=TEXT_LIGHT, justify='left', wraplength=900).pack(anchor='w')

        # Estado de los controles de la pestaña Configuracion -- declarado
        # AQUI, antes de construir la UI, porque _actualizar_resumen_config
        # y los widgets de esa pestaña ya los necesitan (declararlos despues
        # revienta con AttributeError, bug real visto el 2026-09-13).
        self.etiqueta_var = tk.StringVar(value=_cargar_etiqueta())
        self.auto_produccion = tk.BooleanVar(value=False)
        valor_inicial = (self.node.numero_maquina
                         if MIN_MAQUINA <= self.node.numero_maquina <= MAX_MAQUINA else 1)
        self.numero_maquina_var = tk.IntVar(value=valor_inicial)
        self.grupo_cadena_var = tk.IntVar(value=_cargar_grupo_cadena())
        self.taller_api_base_var = tk.StringVar(value=_cargar_taller_api_base())

        # --- selector de robot (sesion 2026-08-30): antes habia que matar
        # la ventana y relanzarla con otros --ros-args para pasar de
        # controlar el Loader al Sorter (ver LANZAR_PROYECTO.md, ahora
        # obsoleto en ese punto) -- ahora se cambia aqui mismo, sin
        # reiniciar nada. El boton del robot activo se resalta en amarillo.
        robot_row = tk.Frame(stop_panel, bg=PANEL_BG)
        robot_row.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        lbl_robot = tk.Label(robot_row, text=self.t('Robot controlado:'), font=big, bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl_robot.grid(row=0, column=0, padx=(0, 8))
        self._i18n_widgets.append((lbl_robot, 'Robot controlado:', 'text'))
        self.robot_btns = {}
        for i, name in enumerate(('loader', 'sorter')):
            b = tk.Button(robot_row, text=name.upper(), font=big, width=10,
                          command=lambda n=name: self.switch_robot(n),
                          relief='raised', bd=4)
            b.grid(row=0, column=1 + i, padx=4)
            self.robot_btns[name] = b
        self.update_robot_buttons()

        self.pos_var = tk.StringVar()
        self.step_var = tk.StringVar()
        self.log_var = tk.StringVar(value=self.t('Listo.'))

        self._jog_buttons = []

        def mkbtn(parent, text, cmd, row, col, width=8, track=True, colspan=1):
            b = tk.Button(parent, text=self.t(text), font=big, width=width, command=cmd,
                          bg=PANEL_BG, fg=TEXT_LIGHT, activebackground='#3a3a3a',
                          activeforeground=TEXT_LIGHT, relief='raised', bd=4)
            b.grid(row=row, column=col, columnspan=colspan, padx=3, pady=3, sticky='we')
            self._i18n_widgets.append((b, text, 'text'))
            if track:
                self._jog_buttons.append(b)
            return b

        def mkframe(parent, text):
            f = tk.LabelFrame(parent, text=self.t(text), font=big, bg=PANEL_BG, fg=YELLOW, bd=3, relief='groove')
            self._i18n_widgets.append((f, text, 'text'))
            return f

        # --- pestañas "Movimiento" / "Producción" (sesion 2026-08-30,
        # rediseño pedido por el usuario: "control manual profesional...
        # que pueda acceder a todo" -- con muchos pedidos pendientes la
        # ventana de una sola columna se quedaba mas alta que la pantalla
        # y los botones de abajo quedaban inalcanzables, sin scroll. Las
        # pestañas separan lo que se usa constantemente (mover el brazo)
        # de lo que se consulta de vez en cuando (pedidos/lotes), asi cada
        # una cabe sola en pantalla. STOP/REARME y el selector de robot se
        # quedan FUERA de las pestañas, siempre visibles -- un control de
        # seguridad no deberia poder quedar escondido detras de una
        # pestaña.
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Panda.TNotebook', background=BG, borderwidth=0)
        style.configure('Panda.TNotebook.Tab', background=PANEL_BG, foreground=TEXT_LIGHT,
                         font=big, padding=[16, 8], borderwidth=0)
        style.map('Panda.TNotebook.Tab',
                  background=[('selected', YELLOW)], foreground=[('selected', 'black')])
        # Combobox del Nº Maquina (ver mas abajo) -- 'clam' es el unico tema
        # que deja recolorear el desplegable a juego con el resto del panel
        # oscuro, por eso ya se fijaba arriba para el Notebook tambien.
        style.configure('Panda.TCombobox', fieldbackground=PANEL_BG, background=PANEL_BG,
                         foreground=TEXT_LIGHT, arrowcolor=TEXT_LIGHT, borderwidth=0)
        style.map('Panda.TCombobox', fieldbackground=[('readonly', PANEL_BG)],
                  foreground=[('readonly', TEXT_LIGHT)])

        notebook = ttk.Notebook(main_frame, style='Panda.TNotebook')
        notebook.grid(row=3, column=0, columnspan=5, padx=18, pady=(4, 16), sticky='nsew')
        main_frame.grid_rowconfigure(3, weight=1)

        tab_movimiento = tk.Frame(notebook, bg=BG)
        tab_produccion = tk.Frame(notebook, bg=BG)
        tab_picos_led = tk.Frame(notebook, bg=BG)
        tab_config = tk.Frame(notebook, bg=BG)
        notebook.add(tab_movimiento, text=self.t('  Movimiento  '))
        notebook.add(tab_produccion, text=self.t('  Producción  '))
        notebook.add(tab_picos_led, text=self.t('  Raspberry Pi Pico  '))
        notebook.add(tab_config, text=self.t('  Configuración  '))
        self.notebook, self.tab_config = notebook, tab_config
        self.tab_produccion, self.tab_picos_led = tab_produccion, tab_picos_led
        # Pestañas ocultables (sesion 2026-09-18, a peticion del usuario:
        # "debajo de idioma añades un check para decir que se vea o no se
        # vea la pestaña de rasberri pi pico y otro... para la pestaña de
        # produccion") -- preferencia por cadena (mismo fichero que idioma/
        # etiqueta, ver config_cadena.py), aplicada ya aqui mismo antes de
        # construir el resto, para que arranque ya oculta si asi se dejo la
        # ultima vez (no hace falta esperar a la pestaña Configuracion).
        _conf_inicial = _leer_config_panel()
        if not bool(_conf_inicial.get('pestana_produccion_visible', True)):
            notebook.tab(tab_produccion, state='hidden')
        if not bool(_conf_inicial.get('pestana_picos_visible', True)):
            notebook.tab(tab_picos_led, state='hidden')
        self._i18n_widgets.append((notebook, ('  Movimiento  ', tab_movimiento), 'tab'))
        self._i18n_widgets.append((notebook, ('  Producción  ', tab_produccion), 'tab'))
        self._i18n_widgets.append((notebook, ('  Raspberry Pi Pico  ', tab_picos_led), 'tab'))
        self._i18n_widgets.append((notebook, ('  Configuración  ', tab_config), 'tab'))
        # Al salir de la pestaña se vuelve a bloquear sola: que no se quede
        # abierta para el siguiente que pase por delante del panel.
        notebook.bind('<<NotebookTabChanged>>', self._on_cambio_pestana)

        # ================= Pestaña "Movimiento" =================
        pos_label = tk.Label(tab_movimiento, textvariable=self.pos_var, font=mono, bg=BG, fg=TEXT_LIGHT, justify='left')
        pos_label.grid(row=0, column=0, columnspan=5, sticky='w', pady=(4, 2))

        step_label = tk.Label(tab_movimiento, textvariable=self.step_var, font=mono, bg=BG, fg=TEXT_LIGHT)
        step_label.grid(row=1, column=0, columnspan=5, sticky='w')

        # --- movimiento XYZ ---
        move_frame = mkframe(tab_movimiento, 'Mover TCP (mundo)')
        move_frame.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky='n')

        mkbtn(move_frame, 'Y-', lambda: self.do_move(0, -self.node.step, 0), 1, 0)
        mkbtn(move_frame, 'X+\nadelante', lambda: self.do_move(self.node.step, 0, 0), 0, 1)
        mkbtn(move_frame, 'X-\natras', lambda: self.do_move(-self.node.step, 0, 0), 2, 1)
        mkbtn(move_frame, 'Y+', lambda: self.do_move(0, self.node.step, 0), 1, 2)
        mkbtn(move_frame, 'Z+\nsubir', lambda: self.do_move(0, 0, self.node.step), 0, 3)
        mkbtn(move_frame, 'Z-\nbajar', lambda: self.do_move(0, 0, -self.node.step), 2, 3)
        mkbtn(move_frame, '📷 Centrar sobre cubo (X/Y, vision)', self.do_center,
              3, 0, width=20, colspan=4)

        step_frame = mkframe(tab_movimiento, 'Paso')
        step_frame.grid(row=2, column=2, padx=8, pady=8, sticky='n')
        mkbtn(step_frame, '- paso', self.step_down, 0, 0, width=10, track=False)
        mkbtn(step_frame, '+ paso', self.step_up, 1, 0, width=10, track=False)

        # --- giro de la pinza (yaw) ---
        rotate_frame = mkframe(tab_movimiento, 'Girar pinza')
        rotate_frame.grid(row=2, column=4, padx=8, pady=8, sticky='n')
        mkbtn(rotate_frame, '↺\nGirar-', lambda: self.do_rotate(-self.node.yaw_step), 0, 0, width=10)
        mkbtn(rotate_frame, '↻\nGirar+', lambda: self.do_rotate(self.node.yaw_step), 1, 0, width=10)

        # --- pinza / home / orientar ---
        action_frame = mkframe(tab_movimiento, 'Pinza y postura')
        action_frame.grid(row=2, column=3, padx=8, pady=8, sticky='n')
        mkbtn(action_frame, 'ABRIR\npinza', self.do_open, 0, 0, width=10)
        mkbtn(action_frame, 'CERRAR\npinza', self.do_close, 1, 0, width=10)
        mkbtn(action_frame, 'HOME', self.do_home, 2, 0, width=10)
        mkbtn(action_frame, 'Orientar\npinza abajo', self.do_align, 3, 0, width=10)

        # --- LED ---
        led_frame = mkframe(tab_movimiento, 'LED')
        led_frame.grid(row=3, column=0, columnspan=5, padx=8, pady=(0, 8), sticky='we')
        mkbtn(led_frame, 'Rojo', lambda: self.do_led('R'), 0, 0, width=8, track=False)
        mkbtn(led_frame, 'Verde', lambda: self.do_led('G'), 0, 1, width=8, track=False)
        mkbtn(led_frame, 'Azul', lambda: self.do_led('B'), 0, 2, width=8, track=False)
        mkbtn(led_frame, 'Apagar', lambda: self.do_led('0'), 0, 3, width=8, track=False)

        self.log_label = tk.Label(tab_movimiento, textvariable=self.log_var, font=mono, bg=BG,
                                   fg=GREEN, wraplength=760, justify='left')
        self.log_label.grid(row=4, column=0, columnspan=5, sticky='w', pady=(4, 8))

        # ================= Pestaña "Producción" =================
        # --- pedidos pendientes (Taller_Administracion), sesion 2026-08-28:
        # el operador ve aqui que falta por hacer y marca cada pieza a mano
        # segun la va colocando, mientras no exista una celda automatica que
        # avise sola. Si el otro proyecto no esta levantado, se avisa sin
        # romper el resto del panel.
        # --- Resumen por producto (sesion 2026-09-01, a peticion del
        # usuario: "si hay dos lotes de tornillos, uno con 3 y otro con
        # 2, el lote seria de cinco, para hacer todos los tornillos a la
        # vez"): agrupa TODOS los pedidos pendientes por producto y
        # muestra un total + un boton "Lanzar todo" por producto -- ENCIMA
        # de la lista de pedidos individuales (que sigue debajo tal cual,
        # por si el operario quiere ver el detalle de cliente/fecha de
        # cada uno). Se decidio ASI, en la misma pestaña, en vez de una
        # pestaña nueva (el usuario pidio "plantea tu como seria mejor" --
        # una pestaña aparte solo duplicaria la misma lista sin aportar
        # nada, y obligaria a cambiar de vista para pasar del resumen al
        # detalle). Reconstruido cada vez que refresh_pedidos() vuelve a
        # pedir la lista (mismos 4s), no tiene sondeo propio.
        resumen_frame = mkframe(tab_produccion, 'Resumen por producto (varios pedidos a la vez)')
        resumen_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky='we')
        self.resumen_producto_frame = resumen_frame

        # Boton "Lanzar todo el resumen" (sesion 2026-09-03, sustituye al
        # antiguo "Lanzar todos los pedidos pendientes" -- peticion
        # explicita del usuario: "quita [el boton] de pedidos pendientes
        # y le anades a resumen por producto, asi que si le damos al
        # boton lanzamos todo el resumen por producto"). El antiguo boton
        # lanzaba UN lote mixto de los tres colores fisicos a la vez
        # (color=None) -- no podia representar productos SIN cubo fisico
        # (Y/M/C/W, ver "modo comodin" en Taller_Administracion) ni fijar
        # el LED de producto a uno solo. Este nuevo lanza cada producto
        # del resumen, UNO DETRAS DE OTRO (misma mecanica que el "Lanzar
        # todo" de un solo producto, ver lanzar_producto_agrupado): hasta
        # que el lote actual no termina DE VERDAD (ver
        # _actualizar_estado_lote, que dispara _lanzar_siguiente_de_cola)
        # no arranca el siguiente, y el LED de producto se queda fijo
        # solo mientras dura ESE lote -- exactamente lo pedido.
        self.btn_lanzar_resumen = tk.Button(
            tab_produccion, text=self.t('Lanzar todo el resumen (uno detrás de otro)'), font=big,
            bg=PANEL_BG, fg=TEXT_LIGHT, activebackground='#3a3a3a', activeforeground=TEXT_LIGHT,
            command=self.lanzar_todo_resumen)
        self.btn_lanzar_resumen.grid(row=1, column=0, padx=8, pady=(0, 8), sticky='w')
        self._i18n_widgets.append((self.btn_lanzar_resumen, 'Lanzar todo el resumen (uno detrás de otro)', 'text'))

        # Interruptor "Automatico" y Nº Maquina: viven en la pestaña
        # Configuracion desde la sesion 2026-09-14 (ver _construir_pestana_config).

        # Lista de pedidos individuales CON SCROLL (sesion 2026-09-02, a
        # peticion del usuario: con muchos pedidos a la vez, antes se
        # cortaba en MAX_PEDIDOS_VISIBLES filas con un texto "...y N mas"
        # -- se podia LANZAR todo con el boton de abajo, pero no se podia
        # VER ni tocar (+1 pieza / lanzar este pedido) el resto sin salir
        # del panel. Canvas+Scrollbar de toda la vida de Tkinter (un
        # tk.Frame no se puede desplazar solo): la rueda del raton
        # desplaza mientras el cursor esta encima de la lista.
        pedidos_label_frame = mkframe(tab_produccion, 'Pedidos pendientes (Taller_Administracion)')
        pedidos_label_frame.grid(row=2, column=0, padx=8, pady=(4, 4), sticky='nsew')
        # Esta fila (y no las de arriba, que son de tamaño fijo) es la que
        # se lleva el espacio de mas si se agranda la ventana (sesion
        # 2026-09-15, a peticion del usuario: la altura fija no bastaba,
        # "un poco mas grande sigue sin entrar" -- con esto, maximizar la
        # ventana agranda tambien esta caja, no solo dibuja hueco vacio).
        tab_produccion.grid_rowconfigure(2, weight=1)
        pedidos_label_frame.grid_rowconfigure(0, weight=1)

        # Altura de partida subida de 200 a 460 (sesion 2026-09-15), y a 900
        # el 2026-09-18 -- revertido a 460 el mismo dia a peticion del
        # usuario ("reduce el tamaño de antes"): con el ancho de sobra no
        # hacia falta tanto alto, el propio scroll vertical de este canvas
        # ya llega a todo.
        # Ancho explicito (sesion 2026-09-18, a peticion del usuario:
        # "pedidos pendientes su marco mas ancho hay botones que no se
        # ven") -- sin 'width', un Canvas no crece solo con lo que se
        # dibuje dentro (a diferencia de un Frame): se quedaba con el
        # ancho de la columna que marcasen los DEMAS widgets de esa
        # columna (el resumen de arriba, mas corto), recortando por la
        # derecha la fila de cada pedido (texto + botones "+1 pieza" /
        # "Lanzar este pedido"). 1100 le da margen de sobra; si la ventana
        # es mas estrecha que eso, el scroll horizontal del panel entero
        # (ver mas arriba en __init__) deja llegar igualmente al boton.
        pedidos_canvas = tk.Canvas(pedidos_label_frame, bg=PANEL_BG, highlightthickness=0, width=1100, height=460)
        pedidos_scrollbar = tk.Scrollbar(pedidos_label_frame, orient='vertical', command=pedidos_canvas.yview)
        pedidos_frame = tk.Frame(pedidos_canvas, bg=PANEL_BG)
        pedidos_frame.bind('<Configure>', lambda e: pedidos_canvas.configure(scrollregion=pedidos_canvas.bbox('all')))
        pedidos_canvas.create_window((0, 0), window=pedidos_frame, anchor='nw')
        pedidos_canvas.configure(yscrollcommand=pedidos_scrollbar.set)
        pedidos_canvas.grid(row=0, column=0, sticky='nsew')
        pedidos_scrollbar.grid(row=0, column=1, sticky='ns')
        pedidos_label_frame.grid_columnconfigure(0, weight=1)

        def _pedidos_mousewheel(event):
            pedidos_canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

        def _pedidos_bind_wheel(_event):
            pedidos_canvas.bind_all('<MouseWheel>', _pedidos_mousewheel)

        def _pedidos_unbind_wheel(_event):
            pedidos_canvas.unbind_all('<MouseWheel>')

        pedidos_canvas.bind('<Enter>', _pedidos_bind_wheel)
        pedidos_canvas.bind('<Leave>', _pedidos_unbind_wheel)

        self.pedidos_frame = pedidos_frame

        # Estado del lote en curso (sesion 2026-09-15: se retiro SOLO el
        # lanzador manual por producto -- "Lanzar lote", el desplegable
        # suelto de producto+cantidad sin atar a ningun pedido real -- a
        # peticion explicita del usuario. "Lanzar este pedido" y "Repetir
        # ultimo lote" se quedan, ver mas abajo. self.lote_status_var se
        # declara ahora en la cabecera (junto a EN MARCHA, sesion
        # 2026-09-18) -- aqui solo se repite el mismo StringVar en esta
        # pestaña, por si se prefiere mirar aqui en vez de en la cabecera.
        tk.Label(tab_produccion, textvariable=self.lote_status_var, font=self.mono_font,
                 bg=PANEL_BG, fg=TEXT_LIGHT, justify='left'
                 ).grid(row=3, column=0, padx=8, pady=(0, 4), sticky='w')

        # "Repetir último lote" (sesion 2026-09-10, peticion explicita del
        # usuario: poder repetir el ultimo lote lanzado -- "Lanzar este
        # pedido" o un tramo de "Lanzar todo el resumen", da igual por
        # cual de los dos, _lanzar_produccion es el unico punto de paso
        # comun. Guarda los mismos argumentos que recibio aquella vez y
        # los reenvia identicos. Empieza deshabilitado -- no hay nada que
        # repetir hasta el primer lanzamiento.
        self.repetir_lote_btn = tk.Button(
            tab_produccion, text=self.t('🔁 Repetir último lote'), font=big, bg=PANEL_BG, fg=TEXT_LIGHT,
            activebackground='#3a3a3a', activeforeground=TEXT_LIGHT,
            state='disabled', command=self.repetir_ultimo_lote,
        )
        self.repetir_lote_btn.grid(row=4, column=0, padx=8, pady=(0, 16), sticky='w')
        self._i18n_widgets.append((self.repetir_lote_btn, '🔁 Repetir último lote', 'text'))

        self.proc_loader = None   # subprocess.Popen del lote en curso (o None)
        self.proc_sorter = None   # subprocess.Popen de sorter_demo (persistente)
        self.lote_inicio_entregas = None   # foto de entregas al lanzar el lote actual
        self.lote_objetivo_por_color = {}  # {color: cantidad pedida en este lote}
        self.lote_color_objetivo = None    # None = mixto, letra = lote de un solo producto
        self.lote_producto_objetivo = None  # codigo del producto en curso (identidad real, no el color)
        self.pedido_id_en_curso = None  # id del pedido lanzado con "Lanzar este pedido", None si no hay uno en curso
        self.producto_en_curso = None  # color lanzado con "Lanzar todo" (resumen por producto), None si no hay uno en curso
        self.cola_lotes = []  # [(color, cantidad, nombre), ...] pendientes de "Lanzar todo el resumen", uno detras de otro
        # Vigilancia del modo Automatico (ver _vigilar_progreso_auto).
        self._auto_previo = {}          # codigo -> (restante, completada) al lanzar la ultima tanda automatica
        self._auto_lanzados = set()     # codigos de los que _lanzar_siguiente_de_cola ha lanzado un lote desde entonces
        self._auto_sin_progreso = {}    # codigo -> tandas automaticas seguidas sin avance
        self._auto_bloqueados = {}      # codigo -> restante en el que se dejo de lanzar automaticamente
        self._ultimo_lote_args = None  # kwargs de la ultima _lanzar_produccion, para "Repetir ultimo lote"
        self._loader_fin_t = None  # time.monotonic() al ver terminado el Loader del lote actual
        self._lote_cerrado_t = None  # time.monotonic() al darse por cerrado el lote actual
        self._aviso_lote_incompleto = False

        # ================= Pestaña "Raspberry Pi Pico" =================
        self._construir_pestana_picos(tab_picos_led, mkframe)

        # ================= Pestaña "Configuración" =================
        self._construir_pestana_config(tab_config, mkframe)
        self._actualizar_titulo_ventana()

        self.refresh_position()
        self.refresh_step()

        # Orientar la pinza hacia abajo YA, al abrir la ventana: el brazo
        # arranca en HOME_POSITIONS, cuya orientacion NO coincide con
        # GRASP_R (ver teleop_manual.py), asi que sin este paso los botones
        # de "Mover TCP" se rechazan todos de entrada (bug real reportado
        # por el usuario: "lo que esta dentro mover tcp no funciona") porque
        # exigirian ese giro grande de golpe. Asi la ventana arranca ya lista
        # para mover en XYZ sin que haga falta saber que pulsar antes.
        ok, msg = self.node.align_gripper_down()
        self.refresh_position()
        self.log(self.t('Listo (pinza orientada hacia abajo). ') + msg, ok)

        self.set_stopped_ui(self.node.stopped)
        self._spin_tick()
        self.refresh_pedidos()
        self._poll_lote()
        self._vigilar_picos()
        self._refrescar_leds()
        self._vigilar_reset_clave()

    # ----------------------------------------------------------------
    # Pestaña "Raspberry Pi Pico" (sesion 2026-09-17, a peticion del
    # usuario: "creamos una pestaña nueva que se llame rasberri pi pico y
    # simula los led... esto es porque no tenemos la pi pico con todos
    # los robot" -- las Pico son opcionales (ver
    # [[robotica_pico_dos_dispositivos_led]]), asi que en una maquina sin
    # hardware conectado no hay forma de ver que color estaria
    # encendiendo cada LED. Esta pestaña NO manda nada -- solo escucha
    # los mismos topics que ya publican led_publisher.py/
    # led_publisher_usb.py (ver TeleopGuiNode._on_led_loader/_on_led_
    # sorter/_on_led_producto) y dibuja el mismo comportamiento (color
    # fijo, apagado o parpadeo), venga el comando del jog manual de este
    # panel o de una produccion automatica en marcha.
    # ----------------------------------------------------------------
    def _construir_pestana_picos(self, tab, mkframe):
        _texto_intro_picos = (
            'Simulación de los LED -- útil si esta máquina no tiene la Raspberry Pi Pico física '
            'conectada: sin hardware, aquí se ve igual el mismo color que encendería.')
        lbl_intro = tk.Label(
            tab, font=self.mono_font, bg=BG, fg=GREY_TEXT, justify='left', wraplength=760,
            text=self.t(_texto_intro_picos),
        )
        lbl_intro.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 4), sticky='w')
        self._i18n_widgets.append((lbl_intro, _texto_intro_picos, 'text'))

        loader_frame = mkframe(tab, 'Pico del Loader (USB)')
        loader_frame.grid(row=1, column=0, padx=8, pady=8, sticky='n')
        self._bola_loader, self._bola_producto = self._fila_picos(loader_frame, con_producto=True, con_hcsr04=True)

        sorter_frame = mkframe(tab, 'Pico del Sorter (Wi-Fi)')
        sorter_frame.grid(row=1, column=1, padx=8, pady=8, sticky='n')
        self._bola_sorter, _sin_producto = self._fila_picos(sorter_frame, con_producto=False, con_hcsr04=False)

    def _fila_picos(self, parent, con_producto, con_hcsr04):
        """Dibuja el pequeño gráfico de una placa Pico (silueta
        reconocible, no un plano eléctrico real -- petición explícita del
        usuario: "con un pequeño grafico") con la(s) bola(s) de LED
        encima, y un botón de PARADA DE EMERGENCIA real dentro de ESTE
        mismo recuadro (sesion 2026-09-17: primero se probo dibujado
        clicable dentro del grafico, el usuario dijo "no me gusta" y
        pidio en su lugar "un boton de parada de emrgencia como antes...
        en vez de un boton general un boton en cada recuadro" -- uno por
        Pico, no uno solo compartido). Ambos mandan lo mismo que el STOP
        de arriba del todo (self.do_stop): un solo /emergency_stop
        global, no uno nuevo por Pico. Devuelve (bola_agarre,
        bola_producto|None), cada una (canvas, id_ovalo, StringVar) --
        ver _refrescar_leds."""
        # Ancho/alto mas margen vertical que la primera version (sesion
        # 2026-09-17, a peticion del usuario: "una flecha o algo que se
        # sepa que led es cada uno como el producto o agarre") -- cada
        # bola lleva ahora su etiqueta fija ("Agarre"/"Producto") y una
        # flechita apuntandole DENTRO del propio dibujo, no solo el texto
        # dinamico de abajo (que dice el color, no cual es cual). Con
        # HC-SR04 (solo Loader) el lienzo se ensancha para el tercer
        # icono (sesion 2026-09-18, a peticion del usuario: "le falta el
        # HC-SR04").
        ancho, alto = (280 if con_hcsr04 else 200), 112
        canvas = tk.Canvas(parent, width=ancho, height=alto, bg=PANEL_BG, highlightthickness=0)
        canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 4))
        canvas.create_rectangle(20, 15, ancho - 20, alto - 15, fill='#0b3d20', outline='#1f6b3a', width=2)
        for x in range(28, ancho - 20, 16):
            canvas.create_rectangle(x, 10, x + 6, 16, fill='#c9c9c9', outline='')
            canvas.create_rectangle(x, alto - 16, x + 6, alto - 10, fill='#c9c9c9', outline='')
        canvas.create_text(ancho / 2, 24, text='PICO', fill='#6fae86', font=('Arial', 8, 'bold'))

        def _etiqueta_y_flecha(cx, texto_es):
            canvas.create_text(cx, 36, text=self.t(texto_es), fill=TEXT_LIGHT, font=('Arial', 7, 'bold'))
            canvas.create_line(cx, 40, cx, 46, fill=TEXT_LIGHT, width=1, arrow='last', arrowshape=(5, 6, 3))

        if con_hcsr04:
            cx_agarre, cx_producto, cx_hcsr04 = 55, 140, 225
        else:
            cx_agarre, cx_producto = (70 if con_producto else ancho / 2), 130

        _etiqueta_y_flecha(cx_agarre, 'Agarre')
        oval_agarre = canvas.create_oval(cx_agarre - 12, 48, cx_agarre + 12, 72, fill=GREY, outline=TEXT_LIGHT, width=2)
        texto_agarre = tk.StringVar()
        lbl_agarre = tk.Label(parent, textvariable=texto_agarre, font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl_agarre.grid(row=1, column=0, pady=(0, 8), columnspan=1 if con_producto else 2)
        bola_agarre = (canvas, oval_agarre, texto_agarre)

        bola_producto = None
        if con_producto:
            _etiqueta_y_flecha(cx_producto, 'Producto')
            oval_producto = canvas.create_oval(cx_producto - 12, 48, cx_producto + 12, 72, fill=GREY, outline=TEXT_LIGHT, width=2)
            texto_producto = tk.StringVar()
            tk.Label(parent, textvariable=texto_producto, font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT
                     ).grid(row=1, column=1, pady=(0, 8))
            bola_producto = (canvas, oval_producto, texto_producto)

        siguiente_fila = 2
        if con_hcsr04:
            # El sensor de verdad no manda distancia por ROS -- la propia
            # Pico decide en su firmware y avisa con "BOTON_PARADA" por el
            # mismo cable USB que el boton fisico (ver led_publisher_usb.py
            # ::_leer_de_pico). Aqui no hay topic que escuchar, asi que en
            # vez de una bola de color se simula con un mando -- "como si
            # fuera el volumen de una mesa de mezcla" (peticion explicita
            # del usuario) -- que dispara la MISMA parada (self.do_stop)
            # en cuanto baja del umbral real del firmware.
            _etiqueta_y_flecha(cx_hcsr04, 'HC-SR04')
            item_hcsr04 = canvas.create_rectangle(cx_hcsr04 - 16, 50, cx_hcsr04 + 16, 68,
                                                   fill=GREY, outline=TEXT_LIGHT, width=2)
            canvas.create_text(cx_hcsr04, 59, text=')))', fill=BG, font=('Arial', 8, 'bold'))

            fila_hcsr04 = tk.Frame(parent, bg=PANEL_BG)
            fila_hcsr04.grid(row=siguiente_fila, column=0, columnspan=2, padx=8, pady=(4, 6))
            siguiente_fila += 1
            lbl_hcsr04 = tk.Label(fila_hcsr04, text=self.t('Simula distancia (HC-SR04):'),
                                   font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT)
            lbl_hcsr04.pack(side='top')
            self._i18n_widgets.append((lbl_hcsr04, 'Simula distancia (HC-SR04):', 'text'))
            fila_control = tk.Frame(fila_hcsr04, bg=PANEL_BG)
            fila_control.pack(side='top', pady=(4, 0))
            texto_hcsr04 = tk.StringVar()
            estado_disparo = {'activo': False}

            def _mover_hcsr04(valor_str, texto_hcsr04=texto_hcsr04, item_hcsr04=item_hcsr04,
                               canvas=canvas, estado_disparo=estado_disparo):
                cm = float(valor_str)
                if cm < UMBRAL_HCSR04_CM:
                    canvas.itemconfig(item_hcsr04, fill=RED)
                    texto_hcsr04.set(self.t('{cm:.0f} cm -- ¡detectado! (parada)', cm=cm))
                    if not estado_disparo['activo']:
                        estado_disparo['activo'] = True
                        self.do_stop()
                else:
                    canvas.itemconfig(item_hcsr04, fill=GREY)
                    texto_hcsr04.set(self.t('{cm:.0f} cm -- libre', cm=cm))
                    estado_disparo['activo'] = False

            # 'mesa de mezcla': fader vertical, arriba = lejos (libre),
            # abajo = cerca (dispara) -- misma intuicion que bajar el
            # volumen. from_/to invertidos a proposito para eso.
            slider_hcsr04 = tk.Scale(
                fila_control, from_=50, to=0, orient='vertical', length=110, width=20,
                showvalue=False, resolution=1, bg=PANEL_BG, fg=TEXT_LIGHT,
                troughcolor=BG, highlightthickness=0, sliderrelief='raised',
                activebackground=YELLOW, command=_mover_hcsr04)
            slider_hcsr04.set(50)
            slider_hcsr04.pack(side='left', padx=(0, 8))
            lbl_valor_hcsr04 = tk.Label(fila_control, textvariable=texto_hcsr04, font=self.mono_font,
                                         bg=PANEL_BG, fg=TEXT_LIGHT, justify='left')
            lbl_valor_hcsr04.pack(side='left')
            _mover_hcsr04('50')

        oled_var = None
        if con_producto:
            # Pantalla OLED simulada (sesion 2026-09-18, a peticion del
            # usuario: "añade el display al simulador de rasberri pi
            # pico") -- mismo principio que las bolas de LED: escucha
            # /texto_producto (el mismo topic que reenvia led_publisher_usb
            # a la pantalla fisica, ver Rasberry_Pi_Pico_USB_Loader/
            # main.py::mostrar_oled) y pinta igual aunque no haya OLED de
            # verdad conectada. Solo en el Loader -- es el unico con
            # pantalla fisica.
            fila_oled = tk.Frame(parent, bg=PANEL_BG)
            fila_oled.grid(row=siguiente_fila, column=0, columnspan=2, padx=8, pady=(4, 6))
            siguiente_fila += 1
            lbl_oled_titulo = tk.Label(fila_oled, text=self.t('Pantalla OLED (simulada):'),
                                        font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT)
            lbl_oled_titulo.pack(side='top')
            self._i18n_widgets.append((lbl_oled_titulo, 'Pantalla OLED (simulada):', 'text'))
            oled_var = tk.StringVar()
            tk.Label(fila_oled, textvariable=oled_var, font=('Courier', 10, 'bold'),
                     bg='black', fg='#39ff14', justify='left', anchor='w',
                     width=17, height=4, relief='sunken', bd=3, padx=4, pady=2
                     ).pack(side='top', pady=(4, 0))

        boton_parada = tk.Button(
            parent, text=self.t('PARADA\nDE EMERGENCIA'), font=self.mono_font, width=16, height=2,
            bg=RED, fg='white', activebackground=RED_DARK, activeforeground='white',
            relief='raised', bd=4)
        boton_parada.grid(row=siguiente_fila, column=0, columnspan=2, padx=8, pady=(2, 2))
        self._i18n_widgets.append((boton_parada, 'PARADA\nDE EMERGENCIA', 'text'))
        # Como el boton fisico: la parada salta AL PULSAR (no al soltar) y, si se mantiene
        # SEGUNDOS_RESET_CLAVE segundos, se ofrece restablecer la clave de configuracion.
        aviso_reset = tk.StringVar(value=self.t('Mantén pulsado {s} s para restablecer la clave', s=SEGUNDOS_RESET_CLAVE))
        boton_parada.bind('<ButtonPress-1>', lambda _e, v=aviso_reset: self._pulsar_parada_simulada(v))
        boton_parada.bind('<ButtonRelease-1>', lambda _e, v=aviso_reset: self._soltar_parada_simulada(v))
        tk.Label(parent, textvariable=aviso_reset, font=('Arial', 8), bg=PANEL_BG, fg=GREY_TEXT,
                 wraplength=250, justify='center').grid(row=siguiente_fila + 1, column=0, columnspan=2, pady=(0, 10))

        if oled_var is not None:
            self._oled_sim_var = oled_var  # ver _refrescar_leds

        return bola_agarre, bola_producto

    def _estado_led(self, cmd, producto=False):
        """(clase, color_hex_o_None, nombre_traducido) para un comando LED
        crudo tal como llega por el topic -- mismo vocabulario que aceptan
        de verdad led_publisher.py/led_publisher_usb.py."""
        c = (cmd or '').strip().lower()
        if c in LED_ALARMA:
            return 'parpadeo', '#ff3b30', self.t('Alarma (parpadeando)')
        if producto and c == SIN_COLOR.lower():
            return 'parpadeo', '#ffffff', self.t('Sin color (parpadeando)')
        if c in LED_APAGADO:
            return 'apagado', None, self.t('Apagado')
        color = (LED_PRODUCTO_COLOR if producto else LED_AGARRE_COLOR).get(c)
        if color is None:
            return 'apagado', None, self.t('Apagado')
        nombre_es = {'r': 'Rojo', 'g': 'Verde', 'b': 'Azul',
                     'y': 'Amarillo', 'm': 'Magenta', 'c': 'Cian', 'w': 'Blanco'}.get(c, c.upper())
        return 'fijo', color, self.t(nombre_es)

    def _refrescar_leds(self):
        """Cada 300ms: repinta las 3 bolas de la pestaña Raspberry Pi Pico
        segun el ultimo comando visto en cada topic (ver
        TeleopGuiNode._on_led_loader/_on_led_sorter/_on_led_producto). El
        parpadeo (alarma / SINCOLOR) se simula alternando color/apagado
        con el reloj -- no hace falta que la Pico real exista para verlo."""
        parpadeo_on = (time.monotonic() % 0.6) < 0.3
        for bola, cmd, es_producto, prefijo in (
                (self._bola_loader, self.node.led_loader_cmd, False, 'Agarre'),
                (self._bola_sorter, self.node.led_sorter_cmd, False, 'Agarre'),
                (self._bola_producto, self.node.led_producto_cmd, True, 'Producto')):
            canvas, oval, texto_var = bola
            estado, color, nombre = self._estado_led(cmd, producto=es_producto)
            if estado == 'apagado':
                relleno = GREY
            elif estado == 'parpadeo':
                relleno = color if parpadeo_on else GREY
            else:
                relleno = color
            canvas.itemconfig(oval, fill=relleno)
            texto_var.set(f'{self.t(prefijo)}: {nombre}')
        # Pantalla OLED simulada (ver _fila_picos): mismo formato en lineas
        # que pinta la Pico real (Rasberry_Pi_Pico_USB_Loader/main.py::
        # mostrar_oled) -- '|' separa nombre/variante/codigo, cada uno en
        # su propia linea.
        texto = self.node.texto_producto_cmd
        if texto.startswith('MSG:'):  # aviso del panel (p. ej. clave restablecida), sin 'Fabricando:'
            lineas = texto[len('MSG:'):].split('|')
        elif texto:
            lineas = [self.t('Fabricando:')] + texto.split('|')
        else:
            lineas = [self.t('Loader listo'), self.t('sin lote')]
        self._oled_sim_var.set('\n'.join(lineas[:4]))
        # 'Fabricando:' lleva dos puntos y se une con un espacio; 'Loader listo'
        # no, y va con ' · ' como el resto.
        self.oled_linea_var.set(
            f"{self.t('Pantalla Pico')}: " + lineas[0] + (' ' if lineas[0].endswith(':') else ' · ')
            + ' · '.join(lineas[1:4]))
        self.root.after(300, self._refrescar_leds)

    # ----------------------------------------------------------------
    # Pestaña "Configuración" (sesion 2026-09-14, a peticion del usuario:
    # "crea una pestaña mas que seria configuracion y necesitariamos clave
    # y metes lo de lanzar pedidos automaticos, nº maquina y el nombre de
    # la cadena, y la configuracion de las pi pico"). Una sola clave
    # (CLAVE_MAQUINA) desbloquea TODA la pestaña, en vez de pedirla en cada
    # control por separado como antes; se vuelve a bloquear sola al
    # cambiar de pestaña.
    # ----------------------------------------------------------------
    def _construir_pestana_config(self, tab_real, mkframe):
        big = self.big_font
        self._config_desbloqueada = False
        self._config_widgets = []  # [(widget, estado cuando esta desbloqueada), ...]

        # Pestaña entera con scroll (sesion 2026-09-17, reportado por el
        # usuario con captura: con el bloque "Idioma" nuevo ya no cabe
        # todo -- se corta por abajo (el aviso de las Pico, el boton de
        # aplicar) sin ninguna forma de bajar. Mismo patron
        # Canvas+Scrollbar que "Pedidos pendientes" en la pestaña
        # Produccion -- un tk.Frame normal no se puede desplazar solo.
        tab_real.grid_rowconfigure(0, weight=1)
        tab_real.grid_columnconfigure(0, weight=1)
        config_canvas = tk.Canvas(tab_real, bg=BG, highlightthickness=0)
        config_scrollbar = tk.Scrollbar(tab_real, orient='vertical', command=config_canvas.yview)
        tab = tk.Frame(config_canvas, bg=BG)
        tab.bind('<Configure>', lambda e: config_canvas.configure(scrollregion=config_canvas.bbox('all')))
        config_canvas.create_window((0, 0), window=tab, anchor='nw')
        config_canvas.configure(yscrollcommand=config_scrollbar.set)
        config_canvas.grid(row=0, column=0, sticky='nsew')
        config_scrollbar.grid(row=0, column=1, sticky='ns')

        def _config_mousewheel(event):
            config_canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

        def _config_bind_wheel(_event):
            config_canvas.bind_all('<MouseWheel>', _config_mousewheel)

        def _config_unbind_wheel(_event):
            config_canvas.unbind_all('<MouseWheel>')

        config_canvas.bind('<Enter>', _config_bind_wheel)
        config_canvas.bind('<Leave>', _config_unbind_wheel)

        def boton(parent, text, cmd):
            b = tk.Button(parent, text=self.t(text), font=big, bg=PANEL_BG, fg=TEXT_LIGHT,
                         activebackground='#3a3a3a', activeforeground=TEXT_LIGHT, command=cmd)
            if text:
                self._i18n_widgets.append((b, text, 'text'))
            return b

        # --- barra de bloqueo ---
        lock_frame = tk.Frame(tab, bg=PANEL_BG, bd=3, relief='groove')
        lock_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky='we')
        self.lock_estado_var = tk.StringVar()
        self.lock_estado_label = tk.Label(lock_frame, textvariable=self.lock_estado_var, font=big,
                                          bg=PANEL_BG, fg=YELLOW)
        self.lock_estado_label.pack(side='left', padx=10, pady=8)
        self.lock_btn = boton(lock_frame, '', self._alternar_bloqueo_config)
        self.lock_btn.pack(side='right', padx=10, pady=8)

        # --- identidad de la cadena ---
        ident = mkframe(tab, 'Identidad de la cadena')
        ident.grid(row=1, column=0, padx=8, pady=4, sticky='we')
        lbl = tk.Label(ident, text=self.t('Nombre de la cadena:'), font=big, bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl.grid(row=0, column=0, padx=6, pady=6, sticky='w')
        self._i18n_widgets.append((lbl, 'Nombre de la cadena:', 'text'))
        e = tk.Entry(ident, textvariable=self.etiqueta_var, font=big, width=20,
                     bg=BG, fg=YELLOW, insertbackground=TEXT_LIGHT, disabledbackground=BG,
                     disabledforeground=GREY_TEXT)
        e.grid(row=0, column=1, padx=6, pady=6, sticky='w')
        e.bind('<Return>', lambda ev: self.guardar_etiqueta())
        b = boton(ident, 'Guardar', self.guardar_etiqueta)
        b.grid(row=0, column=2, padx=6, pady=6)
        self._config_widgets += [(e, 'normal'), (b, 'normal')]

        # Grupo Cadena y Nº Maquina: desplegables 0..99 (height = filas
        # visibles al abrir la lista, con scroll para el resto).
        # self.node.numero_maquina es el valor en uso; el desplegable solo
        # lo cambia al pulsar Guardar.
        for fila, texto, var, rango, guardar in (
                (1, 'Grupo Cadena:', self.grupo_cadena_var,
                 range(MIN_GRUPO_CADENA, MAX_GRUPO_CADENA + 1), self.guardar_grupo_cadena),
                (2, 'Nº Máquina:', self.numero_maquina_var,
                 range(MIN_MAQUINA, MAX_MAQUINA + 1), self.guardar_numero_maquina)):
            lbl_fila = tk.Label(ident, text=self.t(texto), font=big, bg=PANEL_BG, fg=TEXT_LIGHT)
            lbl_fila.grid(row=fila, column=0, padx=6, pady=6, sticky='w')
            self._i18n_widgets.append((lbl_fila, texto, 'text'))
            c = ttk.Combobox(ident, textvariable=var, values=list(rango), state='disabled',
                             style='Panda.TCombobox', width=3, height=15, font=self.mono_font)
            c.grid(row=fila, column=1, padx=6, pady=6, sticky='w')
            b = boton(ident, 'Guardar', guardar)
            b.grid(row=fila, column=2, padx=6, pady=6)
            self._config_widgets += [(c, 'readonly'), (b, 'normal')]

        # URL de Taller_Administracion (sesion 2026-09-18): solo hace
        # falta rellenarla si esta linea se lanza en OTRO ordenador de la
        # red y Taller_Administracion vive en uno distinto -- ver
        # config_cadena.taller_api_base. Vacio = usa el valor por defecto
        # del contenedor ('taller_host', solo llega a esta misma maquina).
        lbl_taller = tk.Label(ident, text=self.t('URL de Taller_Administracion:'), font=big,
                               bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl_taller.grid(row=3, column=0, padx=6, pady=6, sticky='w')
        self._i18n_widgets.append((lbl_taller, 'URL de Taller_Administracion:', 'text'))
        e_taller = tk.Entry(ident, textvariable=self.taller_api_base_var, font=big, width=26,
                             bg=BG, fg=YELLOW, insertbackground=TEXT_LIGHT, disabledbackground=BG,
                             disabledforeground=GREY_TEXT)
        e_taller.grid(row=3, column=1, padx=6, pady=6, sticky='w')
        e_taller.bind('<Return>', lambda ev: self.guardar_taller_api_base())
        b_taller = boton(ident, 'Guardar', self.guardar_taller_api_base)
        b_taller.grid(row=3, column=2, padx=6, pady=6)
        self._config_widgets += [(e_taller, 'normal'), (b_taller, 'normal')]

        # --- idioma (sesion 2026-09-17: de momento solo guarda la
        # preferencia, ver IDIOMAS mas arriba -- la interfaz todavia no
        # se traduce). A la derecha de "Identidad de la cadena", misma
        # fila, para no hacer crecer la pestaña en vertical -- ya se
        # queda sin sitio (no hay barra de scroll en esta pestaña).
        idioma_frame = mkframe(tab, 'Idioma')
        idioma_frame.grid(row=1, column=1, padx=8, pady=4, sticky='wn')
        lbl_panel = tk.Label(idioma_frame, text=self.t('Panel:'), font=big, bg=PANEL_BG, fg=TEXT_LIGHT)
        lbl_panel.grid(row=0, column=0, padx=6, pady=6, sticky='w')
        self._i18n_widgets.append((lbl_panel, 'Panel:', 'text'))
        self.idioma_var = tk.StringVar(value=IDIOMAS.get(_cargar_idioma(), 'Español'))
        c = ttk.Combobox(idioma_frame, textvariable=self.idioma_var, values=list(IDIOMAS.values()),
                         state='disabled', style='Panda.TCombobox', width=10, font=self.mono_font)
        c.grid(row=0, column=1, padx=6, pady=6, sticky='w')
        b = boton(idioma_frame, 'Guardar', self.guardar_idioma)
        b.grid(row=0, column=2, padx=6, pady=6)
        self._config_widgets += [(c, 'readonly'), (b, 'normal')]
        lbl_idioma_hint = tk.Label(
            idioma_frame, font=self.mono_font, bg=PANEL_BG, fg=GREY_TEXT, justify='left', wraplength=260,
            text=self.t('Se aplica al momento en todo el panel.'),
        )
        lbl_idioma_hint.grid(row=1, column=0, columnspan=3, padx=6, pady=(0, 6), sticky='w')
        self._i18n_widgets.append((lbl_idioma_hint, 'Se aplica al momento en todo el panel.', 'text'))

        # --- pestañas visibles (sesion 2026-09-18, a peticion del
        # usuario: "debajo de idioma añades un check para decir que se
        # vea o no se vea la pestaña de rasberri pi pico y otro... para
        # la pestaña de produccion") -- para cadenas donde esa pestaña no
        # se usa nunca (p.ej. sin Pico fisica de verdad, o sin produccion
        # automatica desde este panel) y sobra en la barra. El estado
        # inicial ya se aplico mas arriba, justo al crear el notebook;
        # aqui solo hace falta que el check se pueda tocar (desbloqueo) y
        # aplique + guarde al vuelo.
        self.pestana_produccion_visible_var = tk.BooleanVar(
            value=bool(_leer_config_panel().get('pestana_produccion_visible', True)))
        self.pestana_picos_visible_var = tk.BooleanVar(
            value=bool(_leer_config_panel().get('pestana_picos_visible', True)))

        def _toggle_pestana(notebook_tab, var, clave):
            self.notebook.tab(notebook_tab, state='normal' if var.get() else 'hidden')
            _escribir_config_panel({clave: var.get()})

        cb_prod_visible = tk.Checkbutton(
            idioma_frame, text=self.t('Mostrar pestaña "Producción"'),
            variable=self.pestana_produccion_visible_var, font=self.mono_font,
            bg=PANEL_BG, fg=TEXT_LIGHT, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=TEXT_LIGHT, disabledforeground=GREY_TEXT,
            command=lambda: _toggle_pestana(
                self.tab_produccion, self.pestana_produccion_visible_var, 'pestana_produccion_visible'))
        cb_prod_visible.grid(row=2, column=0, columnspan=3, padx=6, pady=(4, 0), sticky='w')
        self._config_widgets.append((cb_prod_visible, 'normal'))
        self._i18n_widgets.append((cb_prod_visible, 'Mostrar pestaña "Producción"', 'text'))

        cb_picos_visible = tk.Checkbutton(
            idioma_frame, text=self.t('Mostrar pestaña "Raspberry Pi Pico"'),
            variable=self.pestana_picos_visible_var, font=self.mono_font,
            bg=PANEL_BG, fg=TEXT_LIGHT, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=TEXT_LIGHT, disabledforeground=GREY_TEXT,
            command=lambda: _toggle_pestana(
                self.tab_picos_led, self.pestana_picos_visible_var, 'pestana_picos_visible'))
        cb_picos_visible.grid(row=3, column=0, columnspan=3, padx=6, pady=(0, 6), sticky='w')
        self._config_widgets.append((cb_picos_visible, 'normal'))
        self._i18n_widgets.append((cb_picos_visible, 'Mostrar pestaña "Raspberry Pi Pico"', 'text'))

        # --- cambiar la clave de la configuracion (2026-09-21, a peticion del usuario: "clave nueva
        # debajo... el campo y repite clave"). Recuadro PROPIO debajo de Idioma, estrecho (cabe en
        # el mismo ancho que Idioma; dentro de Idioma se cortaba y faltaban botones). Solo se
        # puede tocar con la pestaña ya desbloqueada (o sea, conociendo la clave actual); la
        # nueva se escribe dos veces.
        self.clave_nueva_var = tk.StringVar()
        self.clave_repetida_var = tk.StringVar()
        self.clave_msg_var = tk.StringVar()
        clave_frame = mkframe(tab, 'Cambiar clave de configuración')
        clave_frame.grid(row=2, column=1, padx=8, pady=4, sticky='wn')
        entradas_clave = []
        for fila, texto_es, var in ((0, 'Clave nueva:', self.clave_nueva_var),
                                    (1, 'Repite la clave:', self.clave_repetida_var)):
            lbl = tk.Label(clave_frame, text=self.t(texto_es), font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT)
            lbl.grid(row=fila, column=0, padx=6, pady=3, sticky='w')
            self._i18n_widgets.append((lbl, texto_es, 'text'))
            ent = tk.Entry(clave_frame, textvariable=var, show='*', font=self.mono_font, width=14,
                           bg=BG, fg=YELLOW, insertbackground=TEXT_LIGHT, disabledbackground=BG,
                           disabledforeground=GREY_TEXT)
            ent.grid(row=fila, column=1, padx=6, pady=3, sticky='w')
            entradas_clave.append(ent)
            self._config_widgets.append((ent, 'normal'))
        entradas_clave[1].bind('<Return>', lambda ev: self.cambiar_clave_config())
        b_clave = boton(clave_frame, 'Cambiar clave', self.cambiar_clave_config)
        b_clave.grid(row=2, column=0, columnspan=2, padx=6, pady=(4, 3), sticky='w')
        self._config_widgets.append((b_clave, 'normal'))
        self.clave_msg_label = tk.Label(clave_frame, textvariable=self.clave_msg_var, font=self.mono_font,
                                        bg=PANEL_BG, fg=GREY_TEXT, justify='left', wraplength=260)
        self.clave_msg_label.grid(row=3, column=0, columnspan=2, padx=6, pady=(0, 6), sticky='w')

        # --- produccion ---
        prod = mkframe(tab, 'Producción')
        prod.grid(row=2, column=0, padx=8, pady=4, sticky='we')
        # selectcolor fijado a mano: en temas oscuros el indicador del
        # Checkbutton se queda casi invisible con los colores por defecto.
        cb = tk.Checkbutton(
            prod, text=self.t('Automático: lanzar pedidos solo, sin tocar nada'),
            variable=self.auto_produccion, font=self.mono_font,
            bg=PANEL_BG, fg='#66bb6a', selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground='#66bb6a',
            disabledforeground=GREY_TEXT, command=self.toggle_auto_produccion)
        cb.grid(row=0, column=0, padx=6, pady=6, sticky='w')
        self._config_widgets.append((cb, 'normal'))
        self._i18n_widgets.append((cb, 'Automático: lanzar pedidos solo, sin tocar nada', 'text'))

        # --- Raspberry Pi Pico ---
        picos = tk.LabelFrame(
            tab, text=self.t('Raspberry Pi Pico de esta cadena (contenedor {host})', host=MI_HOST),
            font=big, bg=PANEL_BG, fg=YELLOW, bd=3, relief='groove')
        self._i18n_widgets.append((picos, ('Raspberry Pi Pico de esta cadena (contenedor {host})', {'host': MI_HOST}), 'text_fmt'))
        picos.grid(row=3, column=0, padx=8, pady=4, sticky='we')
        config = _cargar_config_picos()
        self.pico_activa_vars, self.pico_valor_vars, self.pico_estado_vars = {}, {}, {}
        self.pico_estado_labels = {}
        self._pico_ultimo_lanzamiento = {clave: 0.0 for clave in PICOS}
        for fila, (clave, pico) in enumerate(PICOS.items()):
            base = fila * 2
            self.pico_activa_vars[clave] = tk.BooleanVar(value=config[clave]['activa'])
            self.pico_valor_vars[clave] = tk.StringVar(value=config[clave]['valor'])
            self.pico_estado_vars[clave] = tk.StringVar()
            cb = tk.Checkbutton(
                picos, text=self.t(pico['nombre']), variable=self.pico_activa_vars[clave], font=big,
                bg=PANEL_BG, fg=TEXT_LIGHT, selectcolor=PANEL_BG,
                activebackground=PANEL_BG, activeforeground=TEXT_LIGHT, disabledforeground=GREY_TEXT)
            cb.grid(row=base, column=0, columnspan=3, padx=6, pady=(8, 0), sticky='w')
            self._i18n_widgets.append((cb, pico['nombre'], 'text'))
            lbl_param = tk.Label(picos, text=self.t(pico['etiqueta_param']), font=self.mono_font,
                                 bg=PANEL_BG, fg=TEXT_LIGHT)
            lbl_param.grid(row=base + 1, column=0, padx=(30, 6), pady=(2, 6), sticky='w')
            self._i18n_widgets.append((lbl_param, pico['etiqueta_param'], 'text'))
            e = tk.Entry(picos, textvariable=self.pico_valor_vars[clave], font=self.mono_font, width=22,
                         bg=BG, fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, disabledbackground=BG,
                         disabledforeground=GREY_TEXT)
            e.grid(row=base + 1, column=1, padx=6, pady=(2, 6), sticky='w')
            lbl = tk.Label(picos, textvariable=self.pico_estado_vars[clave], font=self.mono_font,
                           bg=PANEL_BG, fg=GREY_TEXT, justify='left', wraplength=300)
            lbl.grid(row=base + 1, column=2, padx=6, pady=(2, 6), sticky='w')
            self.pico_estado_labels[clave] = lbl
            self._config_widgets += [(cb, 'normal'), (e, 'normal')]
        b = boton(picos, 'Aplicar configuración de las Pico', self.aplicar_config_picos)
        b.grid(row=len(PICOS) * 2, column=0, columnspan=3, padx=6, pady=(4, 6), sticky='w')
        self._config_widgets.append((b, 'normal'))
        _texto_hint_picos = (
            'Cada Pico solo puede estar en UNA cadena: si otra cadena ya la tiene, se pide '
            'confirmación y aquella la suelta sola en unos segundos.\n'
            'El botón físico de la Pico W del Sorter no se elige aquí: avisa siempre a la '
            'cadena que publica el puerto 5002 en su docker-compose.yml (hoy la cadena 1).')
        lbl_hint_picos = tk.Label(
            picos, font=self.mono_font, bg=PANEL_BG, fg=GREY_TEXT, justify='left', wraplength=700,
            text=self.t(_texto_hint_picos),
        )
        lbl_hint_picos.grid(row=len(PICOS) * 2 + 1, column=0, columnspan=3, padx=6, pady=(0, 6), sticky='w')
        self._i18n_widgets.append((lbl_hint_picos, _texto_hint_picos, 'text'))

        self.config_status_var = tk.StringVar(value='')
        tk.Label(tab, textvariable=self.config_status_var, font=self.mono_font, bg=BG, fg=TEXT_LIGHT,
                 justify='left', wraplength=760).grid(row=4, column=0, padx=8, pady=(4, 12), sticky='w')

        self._aplicar_bloqueo_config(False)

    def _alternar_bloqueo_config(self):
        if self._config_desbloqueada:
            self._aplicar_bloqueo_config(False)
            return
        clave = simpledialog.askstring(
            self.t('Configuración'), self.t('Clave para desbloquear la configuración:'), show='*', parent=self.root)
        if clave is None:  # ha pulsado Cancelar, no hace falta avisar de nada
            return
        if not _clave_correcta(clave):
            messagebox.showerror(self.t('Clave incorrecta'), self.t('La configuración sigue bloqueada.'), parent=self.root)
            return
        self._audit('Configuración desbloqueada')
        self._aplicar_bloqueo_config(True)

    def _aplicar_bloqueo_config(self, desbloqueada):
        if not desbloqueada:
            # Lo escrito y no guardado se descarta: la pestaña bloqueada
            # enseña siempre lo que hay de verdad en uso.
            self.etiqueta_var.set(_cargar_etiqueta())
            self.numero_maquina_var.set(self.node.numero_maquina)
            self.grupo_cadena_var.set(_cargar_grupo_cadena())
            self.taller_api_base_var.set(_cargar_taller_api_base())
            self.clave_nueva_var.set('')
            self.clave_repetida_var.set('')
            self.clave_msg_var.set('')
            for clave, datos in _cargar_config_picos().items():
                self.pico_activa_vars[clave].set(datos['activa'])
                self.pico_valor_vars[clave].set(datos['valor'])
        self._config_desbloqueada = desbloqueada
        for widget, estado in self._config_widgets:
            widget.config(state=estado if desbloqueada else 'disabled')
        if desbloqueada:
            self.lock_estado_var.set(self.t('🔓 Configuración desbloqueada'))
            self.lock_estado_label.config(fg=GREEN)
            self.lock_btn.config(text=self.t('Bloquear'))
        else:
            self.lock_estado_var.set(self.t('🔒 Configuración bloqueada'))
            self.lock_estado_label.config(fg=YELLOW)
            self.lock_btn.config(text=self.t('Desbloquear (clave)'))
        self._actualizar_resumen_config()

    def _on_cambio_pestana(self, _event):
        if self._config_desbloqueada and self.notebook.select() != str(self.tab_config):
            self._aplicar_bloqueo_config(False)

    def _actualizar_resumen_config(self):
        etiqueta = _cargar_etiqueta()
        self.etiqueta_mostrada_var.set(etiqueta or self.t('(sin nombre)'))
        self.etiqueta_mostrada_label.config(fg=YELLOW if etiqueta else GREY_TEXT)
        config = _cargar_config_picos()
        picos = ', '.join(PICOS[c]['corto'] for c, d in config.items() if d['activa']) or self.t('ninguna')
        self.resumen_config_var.set(self.t(
            'Grupo Cadena: {grupo}   ·   '
            'Nº Máquina: {maquina}   ·   '
            'Automático: {automatico}\n'
            'Pico en esta cadena: {picos}\n'
            'Taller_Administracion: {taller}',
            grupo=_cargar_grupo_cadena(), maquina=self.node.numero_maquina,
            automatico=self.t('SÍ') if self.auto_produccion.get() else self.t('no'), picos=picos,
            taller=self.node.taller_api_base))

    def aplicar_config_picos(self):
        """Boton 'Aplicar configuración de las Pico': guarda lo marcado,
        reclama/suelta cada Pico en el fichero compartido entre lineas y
        arranca/para su puente en ESTE contenedor."""
        if not self._config_desbloqueada:
            return
        anterior = _cargar_config_picos()
        nueva = {}
        mensajes = []
        nombre_cadena = _cargar_etiqueta() or MI_HOST
        for clave, pico in PICOS.items():
            activa = self.pico_activa_vars[clave].get()
            valor = self.pico_valor_vars[clave].get().strip() or pico['defecto']
            self.pico_valor_vars[clave].set(valor)
            asignacion = _leer_asignacion_picos()
            dueno = asignacion.get(clave) or {}

            if activa:
                if clave == 'loader_usb' and not os.path.exists(valor):
                    messagebox.showerror(
                        pico['corto'],
                        self.t('El puerto {valor} no existe en este contenedor ({host}).\n\n'
                               'La Pico USB solo se ve desde la cadena que la tiene en el bloque '
                               '"devices:" de su docker-compose.yml (y con la Pico enchufada al '
                               'arrancar el contenedor).', valor=valor, host=MI_HOST), parent=self.root)
                    activa = False
                elif dueno.get('host') and dueno['host'] != MI_HOST:
                    otra = dueno.get('nombre') or dueno['host']
                    if not messagebox.askyesno(
                            pico['corto'],
                            self.t('Esta Pico la tiene ahora la cadena "{otra}" ({host}).\n\n'
                                   '¿Pasarla a esta cadena? La otra dejará de usarla en unos segundos.',
                                   otra=otra, host=dueno["host"]),
                            parent=self.root):
                        activa = False
            if not activa:
                self.pico_activa_vars[clave].set(False)

            if activa:
                asignacion[clave] = {'host': MI_HOST, 'nombre': nombre_cadena}
                _escribir_asignacion_picos(asignacion)
                vivo = _puente_vivo(pico['ejecutable'])
                if vivo and valor != anterior[clave]['valor']:
                    _parar_puente(pico['ejecutable'])
                    vivo = False
                if not vivo:
                    _lanzar_puente(pico['ejecutable'], pico['param'], valor)
                    self._pico_ultimo_lanzamiento[clave] = time.monotonic()
                    mensajes.append(self.t('{corto}: arrancada ({valor})', corto=pico['corto'], valor=valor))
                else:
                    mensajes.append(self.t('{corto}: ya estaba en marcha', corto=pico['corto']))
            else:
                if dueno.get('host') == MI_HOST:
                    asignacion.pop(clave, None)
                    _escribir_asignacion_picos(asignacion)
                if anterior[clave]['activa'] and _puente_vivo(pico['ejecutable']):
                    _parar_puente(pico['ejecutable'])
                    mensajes.append(self.t('{corto}: parada', corto=pico['corto']))
            nueva[clave] = {'activa': activa, 'valor': valor}

        _escribir_config_panel({'picos': nueva})
        self._audit(f'Aplicar configuración Pico: {nueva}')
        self.config_status_var.set(self.t('Pico: {mensajes}.', mensajes='; '.join(mensajes) if mensajes else self.t('sin cambios')))
        self._actualizar_resumen_config()
        self._refrescar_estado_picos()

    def _vigilar_picos(self):
        """Cada 3s: si otra linea se ha quedado una Pico de las nuestras,
        se suelta (y se para su puente); si una Pico asignada a esta linea
        tiene el puente caido, se relanza (como mucho cada PICO_REINTENTO_S)."""
        config = _cargar_config_picos()
        asignacion = _leer_asignacion_picos()
        cambios = False
        for clave, pico in PICOS.items():
            if not config[clave]['activa']:
                continue
            dueno = asignacion.get(clave) or {}
            if dueno.get('host') and dueno['host'] != MI_HOST:
                # Otra cadena la ha reclamado: soltarla.
                _parar_puente(pico['ejecutable'])
                config[clave]['activa'] = False
                cambios = True
                otra = dueno.get('nombre') or dueno['host']
                self.config_status_var.set(self.t('{corto}: la ha pasado a la cadena "{otra}".', corto=pico['corto'], otra=otra))
                self.node.get_logger().warning(f'Pico {clave} reasignada a {dueno["host"]} -- puente parado.')
                if not self._config_desbloqueada:
                    self.pico_activa_vars[clave].set(False)
                continue
            if not dueno.get('host'):
                # Nadie la tiene apuntada (primer arranque, o fichero borrado): es nuestra.
                asignacion[clave] = {'host': MI_HOST, 'nombre': _cargar_etiqueta() or MI_HOST}
                _escribir_asignacion_picos(asignacion)
            if (not _puente_vivo(pico['ejecutable'])
                    and time.monotonic() - self._pico_ultimo_lanzamiento[clave] > PICO_REINTENTO_S):
                _lanzar_puente(pico['ejecutable'], pico['param'], config[clave]['valor'])
                self._pico_ultimo_lanzamiento[clave] = time.monotonic()
                self.node.get_logger().info(f'Puente {pico["ejecutable"]} (re)lanzado por el panel.')
        if cambios:
            _escribir_config_panel({'picos': config})
            self._actualizar_resumen_config()
        self._refrescar_estado_picos()
        self.root.after(3000, self._vigilar_picos)

    def _refrescar_estado_picos(self):
        config = _cargar_config_picos()
        asignacion = _leer_asignacion_picos()
        for clave, pico in PICOS.items():
            vivo = _puente_vivo(pico['ejecutable'])
            dueno = asignacion.get(clave) or {}
            if config[clave]['activa']:
                texto, color = (self.t('● en marcha'), GREEN) if vivo else (self.t('⚠ puente parado, reintentando'), RED)
            elif dueno.get('host') and dueno['host'] != MI_HOST:
                texto, color = self.t('en la cadena "{nombre}"', nombre=dueno.get("nombre") or dueno["host"]), YELLOW
            elif vivo:
                texto, color = self.t('● en marcha (lanzado a mano, fuera de esta configuración)'), YELLOW
            else:
                texto, color = self.t('○ no usada en esta cadena'), GREY_TEXT
            self.pico_estado_vars[clave].set(texto)
            self.pico_estado_labels[clave].config(fg=color)

    def switch_robot(self, name):
        if name == self.node.robot_name:
            return
        self._audit(f'Cambiar de robot -> {name}')
        self.node.apply_preset(name)
        # Reset a HOME (sesion 2026-08-30): la pose articular de un robot
        # no es necesariamente una postura valida/segura para el otro (cada
        # uno vive en un sitio distinto de la celda) -- no tiene sentido
        # arrastrar self.thetas del robot anterior.
        self.node.thetas = self.node.home_raw.copy()
        self.node.yaw = 0.0
        self.update_robot_buttons()
        ok, msg = self.node.align_gripper_down()
        self.refresh_position()
        self.log(self.t('Controlando ahora: {label}. ', label=self.node._presets[name]['label']) + msg, ok)

    def update_robot_buttons(self):
        for name, btn in self.robot_btns.items():
            activo = name == self.node.robot_name
            btn.config(
                bg=YELLOW if activo else PANEL_BG,
                fg='black' if activo else TEXT_LIGHT,
                activebackground='#c9a400' if activo else '#3a3a3a',
                relief='sunken' if activo else 'raised',
            )

    def repetir_ultimo_lote(self):
        """Repite el ultimo lote lanzado, exactamente con los mismos
        argumentos que recibio _lanzar_produccion aquella vez (sesion
        2026-09-10, peticion explicita del usuario). Vale tanto para un
        pedido real como para un tramo de resumen porque
        _lanzar_produccion es el unico punto de paso comun.

        Ojo si el ultimo lote llevaba 'pedido_id' (vino de "Lanzar este
        pedido"): repetir con la MISMA cantidad puede fabricar de mas si
        ese pedido ya quedo cubierto -- no se recalcula aqui lo que falta
        de verdad (para eso, 'Lanzar este pedido' desde la lista, que si
        relee la cantidad restante). El aviso de confirmacion deja claro
        que cantidad va a repetir para que el operario lo vea antes de
        aceptar."""
        args = self._ultimo_lote_args
        if args is None:
            self.lote_status_var.set(self.t('Todavía no se ha lanzado ningún lote que repetir.'))
            return
        if self._lote_en_curso():
            self.lote_status_var.set(self.t('Ya hay un lote en curso (el Sorter aún no ha clasificado todas sus piezas) -- espera a que termine.'))
            return
        if self.cola_lotes:
            self.lote_status_var.set(self.t('Ya hay una cola de lotes en marcha -- espera a que termine.'))
            return
        aviso_pedido = (
            self.t('\n\nOjo: este lote estaba atado al pedido #{id} -- si ya se '
                   'completó, repetirlo fabricará piezas de más (van a Stock, no se pierden, pero '
                   'no las pidió nadie).', id=args["pedido_id"]) if args['pedido_id'] is not None else ''
        )
        if not messagebox.askyesno(
            self.t('Repetir último lote'),
            self.t('Esto repite el último lote: {cantidad} unidad(es) de "{etiqueta}".\n'
                   'Si estás controlando el Loader o el Sorter a mano ahora mismo, '
                   'se pelearán por el brazo con la demo automática.', cantidad=args["cantidad"], etiqueta=args["etiqueta"])
            + aviso_pedido + '\n\n' + self.t('¿Continuar?'),
        ):
            return
        self._audit(f'Repetir último lote: {args["etiqueta"]} x{args["cantidad"]}')
        if args['pedido_id'] is not None:
            self.pedido_id_en_curso = args['pedido_id']
        elif args.get('codigo') is not None:
            self.producto_en_curso = args['codigo']  # para pintar "Lanzar todo" en verde
        self._lanzar_produccion(**args)

    def lanzar_pedido(self, pedido_id, color, cantidad, nombre, codigo=None, texto_oled=None):
        """'Lanzar este pedido' (sesion 2026-09-01): lanza al Loader y al
        Sorter para UN pedido real concreto de la lista, con su cantidad
        restante ya calculada -- no hace falta elegir producto ni escribir
        cantidad a mano. Al terminar, el operario tiene que pulsar el
        siguiente 'Lanzar este pedido' el mismo a proposito (no se
        encadenan solos): entre pedido y pedido el operario puede
        necesitar cambiar de produccion a mano.

        'pedido_id' (mismo dia, bug real visto en vivo): cada pieza se ata
        a ESTE pedido en concreto en Taller_Administracion (ver
        _lanzar_produccion), asi que se completa de verdad aunque el
        interruptor de reparto_automatico este desactivado -- antes se
        quedaba "pendiente" para siempre pese a que el stock ya tuviera
        piezas de sobra, porque nadie pulsaba "Repartir stock" a mano."""
        if cantidad < 1:
            self.lote_status_var.set(self.t('"{nombre}" ya no tiene unidades pendientes.', nombre=nombre))
            return
        if self._lote_en_curso():
            self.lote_status_var.set(self.t('Ya hay un lote en curso (el Sorter aún no ha clasificado todas sus piezas) -- espera a que termine.'))
            return
        if not messagebox.askyesno(
            self.t('Confirmar pedido'),
            self.t('Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}" '
                   'para el pedido #{pedido_id}.\n'
                   'Si estás controlando el Loader o el Sorter a mano ahora mismo, '
                   'se pelearán por el brazo con la demo automática.\n\n¿Continuar?',
                   cantidad=cantidad, nombre=nombre, pedido_id=pedido_id),
        ):
            return
        if not self._reclamar_grupo([pedido_id]):
            return
        self._audit(f'Lanzar este pedido: #{pedido_id} {nombre} x{cantidad}')
        self.pedido_id_en_curso = pedido_id  # para pintar el boton en verde, ver refresh_pedidos()
        self._lanzar_produccion(color, cantidad, nombre, pedido_id=pedido_id, codigo=codigo, texto_oled=texto_oled)

    def _lanzar_produccion(self, color, cantidad, etiqueta, pedido_id=None, forzar_reparto=False,
                            codigo=None, producto_id=None, texto_oled=None):
        """Arranca sorter_demo (si no esta ya vivo, persiste entre lotes) y
        un loader_demo nuevo. 'color'=None hace que loader_demo cicle los
        TRES colores a la vez (comportamiento de por defecto de
        CRATE_CUBES, un R+un G+un B por vuelta, 'cantidad' vueltas) --
        usado por 'Lanzar todos los pedidos pendientes' (sesion
        2026-08-30, segunda vuelta: la primera version hacia un color
        detras de otro con una cola, pero el usuario lo probo y le parecio
        demasiado lento/pesado de ver -- "esto asi es un coñazo y poco
        productivo" -- así que ahora reparte YA los tres colores dentro
        del mismo lote, igual que hacia el Loader originalmente antes de
        que existiera 'only_color'). 'color'=<letra> (desde 'Lanzar este
        pedido', o un tramo de "Lanzar todo el resumen") sigue
        restringiendo a un solo color --
        pero ojo, "restringir" ya NO significa que el Loader solo coja ese
        cubo fisico (ver loader_demo.py, sesion 2026-09-01: 'cubes =
        CRATE_CUBES' es fijo, SIEMPRE usa los 3 cubos reales). 'only_color'
        es solo la ETIQUETA del producto que se esta fabricando -- fija el
        LED de producto y hace que el Sorter cuente cada entrega real como
        ESTE producto (ver SorterDemo._lote_color_objetivo), sea cual sea
        el color real del cubo que la genero. Por eso vale igual para un
        producto con cubo fisico (R/G/B) que para uno "solo LED" (Y/M/C/W,
        sesion 2026-09-02, catalogo ampliable) -- no hay que distinguirlos
        aqui, loader_demo.py ya no exige que 'only_color' sea un color
        de CRATE_CUBES."""
        # Un loader_demo vivo que NO lanzo este panel (otra ventana anterior, o
        # uno lanzado a mano por terminal): no lanzar otro encima, se pelearian
        # por el brazo del Loader (ver _demo_vivo).
        if (self.proc_loader is None or self.proc_loader.poll() is not None) and _demo_vivo('loader_demo'):
            self.lote_status_var.set(
                self.t('Ya hay un loader_demo corriendo fuera del panel -- espera a que termine o páralo.'))
            self.pedido_id_en_curso = None
            self.producto_en_curso = None
            self.cola_lotes = []
            return
        # Recordar EXACTAMENTE estos argumentos para "Repetir ultimo lote"
        # (sesion 2026-09-10) -- da igual por que puerta se llego aqui
        # (Lanzar este pedido / un tramo de Lanzar todo el resumen),
        # _lanzar_produccion es el unico sitio por el que pasan todos, asi
        # que es el sitio correcto para guardarlo una sola vez.
        self._ultimo_lote_args = dict(
            color=color, cantidad=cantidad, etiqueta=etiqueta,
            pedido_id=pedido_id, forzar_reparto=forzar_reparto, codigo=codigo, producto_id=producto_id,
            texto_oled=texto_oled,
        )
        self.repetir_lote_btn.config(state='normal')
        # Salida a fichero, NO a DEVNULL (bug real, sesion 2026-08-30: con
        # DEVNULL, si un lote se queda sin hacer nada -- p.ej. un cubo
        # descolocado tras una prueba anterior, o el otro robot ocupado a
        # mano en el mismo topic -- no habia forma de ver el motivo, ni
        # desde el panel ni por fuera).
        # Si ya hay un sorter_demo vivo (de una ventana anterior del panel o
        # lanzado a mano) se reutiliza: es persistente entre lotes y escucha
        # /production/* igual. Lanzar otro encima es el fallo de _demo_vivo.
        if (self.proc_sorter is None or self.proc_sorter.poll() is not None) and not _demo_vivo('sorter_demo'):
            log_sorter = open('/tmp/lote_sorter.log', 'w')
            self.proc_sorter = subprocess.Popen([
                'ros2', 'run', 'panda_controller', 'sorter_demo', '--ros-args',
                '-r', '__ns:=/sorter',
                '-p', 'robot_base_x:=0.0', '-p', 'robot_base_y:=1.00', '-p', 'robot_base_z:=0.74',
            ], stdout=log_sorter, stderr=subprocess.STDOUT)
        loader_args = [
            'ros2', 'run', 'panda_controller', 'loader_demo', '--ros-args',
            '-r', '__ns:=/loader',
            '-p', f'cycles:={cantidad}', '-p', 'led_topic:=/comando_led_loader',
            '-p', 'led_topic_producto:=/comando_led_producto',
        ]
        if color is not None:
            # Comillas EXPLICITAS alrededor del valor (sesion 2026-09-02,
            # bug real): ROS2 interpreta '-p nombre:=valor' como YAML, y
            # en YAML 'Y'/'y'/'N'/'n'/'yes'/'no'/'on'/'off' son literales
            # BOOLEANOS -- 'only_color:=Y' (amarillo) se convertia en
            # 'True' en vez de la letra "Y", y loader_demo.py crasheaba al
            # declarar el parametro (tipo STRING esperado, BOOL recibido).
            # Forzando comillas YAML se interpreta siempre como texto, sea
            # cual sea la letra.
            loader_args += ['-p', f'only_color:="{color}"']
        log_loader = open('/tmp/lote_loader.log', 'w')
        self.proc_loader = subprocess.Popen(loader_args, stdout=log_loader, stderr=subprocess.STDOUT)
        # Rotulo de la pantalla OLED del Loader: quien lo apaga al acabar es
        # led_publisher_usb cuando sorter_demo da el lote por cerrado (mismo
        # momento que el LED de producto), asi que aqui solo hay que
        # encenderlo. 'texto_oled' (con '|' separando nombre/variante/
        # codigo en lineas propias, ver lanzar_pedido) si viene informado;
        # si no (Lanzar todo el resumen / Lanzar todo por producto, sin
        # variante concreta que mostrar), se cae a 'etiqueta' tal cual.
        self.node.pub_texto_producto.publish(String(data=(texto_oled if texto_oled is not None else etiqueta) or ''))
        # Contador de piezas de ESTE lote (sesion 2026-08-31): foto de las
        # entregas totales acumuladas hasta ahora (self.node.entregas_color,
        # ver TeleopGuiNode._on_cube_delivered) y el objetivo pedido -- la
        # diferencia en cada refresco (_actualizar_estado_lote) es lo
        # fabricado DE VERDAD en este lote, sin mirar para nada si
        # Taller_Administracion tiene el reparto automatico activado o no
        # (eso es una decision administrativa aparte, ver conversacion).
        self.lote_inicio_entregas = dict(self.node.entregas_color)
        self._loader_fin_t = None  # ver _lote_en_curso
        self._lote_cerrado_t = None  # ver _lote_recien_cerrado
        self._aviso_lote_incompleto = False
        self.lote_color_objetivo = color  # None = mixto, letra = un solo producto
        # Codigo del producto (identidad real, ver _agrupar_pedidos_por_producto
        # -- sesion 2026-09-15: agrupar/reidentificar por 'color' mezclaba
        # productos distintos sin LED, todos bajo el mismo SIN_COLOR).
        # None si no se lanzo desde un producto identificado (lote mixto).
        self.lote_producto_objetivo = codigo
        colores_lote = [color] if color is not None else ['R', 'G', 'B']
        self.lote_objetivo_por_color = {c: cantidad for c in colores_lote}
        # Avisa al Sorter (si ya estaba vivo de un lote anterior) para que
        # aparque y baile antes de seguir -- el Loader, al ser un proceso
        # nuevo, ya lo hace solo al arrancar (ver loader_demo.py).
        self.node.pub_nuevo_lote.publish(Bool(data=True))
        # Color objetivo para el Sorter (sesion 2026-09-01, ver
        # SorterDemo._on_lote_color_objetivo): con un solo producto, toda
        # entrega de este lote cuenta como 'color' aunque el cubo real sea
        # de otro color (el Loader ya usa los 3 cubos, ver loader_demo.py).
        # Formato 'COLOR:CANTIDAD:PEDIDO_ID', COLOR vacio en reparto mixto
        # (cada cubo sigue contando por su color real). La cantidad es
        # SIEMPRE el total de piezas de verdad -- en reparto mixto son
        # los 3 colores a la vez ('cantidad' vueltas x 3, ver loader_demo.py
        # objetivo_piezas), no las vueltas en si. Le dice al Sorter cuando
        # el lote esta REALMENTE terminado (bug real, sesion 2026-09-01:
        # antes en reparto mixto nunca se avisaba de que habia terminado,
        # el LED de producto se quedaba encendido con el ultimo color real
        # visto) para apagar entonces el LED de producto -- no cuando el
        # Loader simplemente acaba de descargar en la cinta. pedido_id
        # (relleno solo desde 'Lanzar este pedido') ata cada entrega a ESE
        # pedido concreto sin depender del interruptor de reparto_automatico.
        # 'forzar_reparto' (mismo dia, "Lanzar todo este producto": varios
        # pedidos reales del mismo producto sumados, sin un pedido_id
        # unico) hace que cada pieza se aplique igual al pedido pendiente
        # mas antiguo de ese color, tambien sin mirar el interruptor.
        # 'producto_id' (sesion 2026-09-15, peticion explicita del usuario:
        # "el LED no tiene que influir en la logica de negocio") -- el
        # Sorter lo reenvia tal cual a /taller/cubo_clasificado, que lo usa
        # para identificar el producto SIN pasar por color/LED (ver
        # CuboClasificado en el backend). Necesario aqui porque este es el
        # caso ("Lanzar todo el resumen"/forzar_reparto) que NO lleva
        # pedido_id unico -- sin esto, un producto sin LED no podria
        # completar sus pedidos con este boton.
        total_piezas = cantidad if color is not None else cantidad * 3
        mensaje_lote = (
            f'{color or ""}:{total_piezas}:{pedido_id or ""}:'
            f'{"1" if forzar_reparto else ""}:{producto_id or ""}'
        )
        self.node.pub_lote_color_objetivo.publish(String(data=mensaje_lote))
        self.lote_status_var.set(self.t(
            'Fabricando {etiqueta} (Loader lanzado, Sorter activo). '
            'Logs en /tmp/lote_loader.log y /tmp/lote_sorter.log.', etiqueta=etiqueta))

    def _agrupar_pedidos_por_producto(self, pedidos):
        """Agrupa pedidos activos por producto (CODIGO -- sesion 2026-09-15,
        corregido en la misma sesion: agrupar por color/led_codigo mezclaba
        productos DISTINTOS que no tuvieran LED, todos bajo el mismo
        centinela SIN_COLOR, como si fueran el mismo producto), sumando lo
        que falta por completar de cada uno (puede haber varios pedidos del
        mismo producto, de distintos clientes). Compartido por
        _refrescar_resumen_productos (solo mostrar) y lanzar_todo_resumen
        (fabricar de verdad) -- una sola fuente para el mismo calculo.
        Ademas de 'restante' (lo que hay que fabricar), suma 'completada'
        y 'pedida' (sesion 2026-09-03, a peticion del usuario: "podemos
        saber cuantas piezas estan hechas y cuantas faltan" -- en
        'Pedidos pendientes' ya se veia por pedido individual
        (completada/pedida), pero el resumen agrupado solo mostraba lo
        pendiente, no el total hecho de ese producto entre todos sus
        pedidos). Tambien guarda 'ids' -- sesion 2026-09-13, necesario
        para reclamar (ver TeleopGuiNode.reclamar_pedido) cada pedido
        concreto antes de lanzar produccion para el grupo entero. 'color'
        (el led_codigo, o SIN_COLOR si no tiene) va como dato de cada
        grupo, para lanzarlo -- ya NO es la clave de agrupacion.
        'subproductos' (sesion 2026-09-15, a peticion del usuario: "los
        clavos unos son de 10 y otros son de 20, eso tambien tiene que
        saberlo el operario" -- y despues, "desglosa tambien por
        subproducto" en el resumen, no solo en corchetes) suma por
        separado 'restante'/'completada'/'pedida' de cada VARIANTE dentro
        del producto -- la celda fabrica igual sea cual sea (mismo
        color/producto, no distingue subproducto), pero el operario tiene
        que poder ver el desglose completo, con los mismos numeros que ya
        ve por producto entero."""
        por_producto = {}
        for p in pedidos:
            producto = p['producto']
            subproducto = p['subproducto']
            codigo = producto['codigo']
            color = producto['led_codigo'] or SIN_COLOR
            restante = _pendiente_de_fabricar(p)
            if restante <= 0:
                continue
            fila = por_producto.setdefault(
                codigo, {'nombre': producto['nombre'], 'color': color, 'producto_id': producto['id'],
                         'restante': 0, 'n_pedidos': 0, 'completada': 0, 'pedida': 0, 'ids': [],
                         'subproductos': {}})
            fila['restante'] += restante
            fila['n_pedidos'] += 1
            fila['completada'] += p['cantidad_completada']
            fila['pedida'] += p['cantidad_pedida']
            fila['ids'].append(p['id'])
            sub = fila['subproductos'].setdefault(
                subproducto['nombre'],
                {'codigo_completo': subproducto['codigo_completo'],
                 'restante': 0, 'completada': 0, 'pedida': 0, 'n_pedidos': 0})
            sub['restante'] += restante
            sub['completada'] += p['cantidad_completada']
            sub['pedida'] += p['cantidad_pedida']
            sub['n_pedidos'] += 1
        return por_producto

    def _texto_oled_producto(self, nombre, subproductos):
        """Mismo formato 'producto|subproducto|codigo' que ya usa 'Lanzar
        este pedido' (ver etiqueta_completa/texto_oled en refresh_pedidos),
        pero para un lote AGRUPADO (Resumen por producto, Lanzar todo el
        resumen, Modo Automatico, cola de _lanzar_siguiente_de_cola) -- ahi
        no hay un pedido unico, sino la suma de 'subproductos' que ya
        calcula _agrupar_pedidos_por_producto. Bug real, sesion 2026-09-18:
        estos caminos nunca pasaban texto_oled, asi que la pantalla se
        quedaba solo con el nombre del producto ('Fabricando: Arandelas',
        sin variante ni codigo). Con una sola variante en el grupo se
        puede dar el mismo detalle completo que un pedido individual; con
        varias mezcladas en el mismo lote no hay una unica que mostrar, se
        deja solo el nombre."""
        if len(subproductos) == 1:
            (nombre_sub, sub), = subproductos.items()
            return f"{nombre}|{nombre_sub}|{sub['codigo_completo']}"
        return nombre

    def _reclamar_grupo(self, ids) -> bool:
        """Reclama TODOS los pedidos de 'ids' para esta máquina (ver
        TeleopGuiNode.reclamar_pedido) antes de lanzar producción -- si
        alguno falla (otra celda se lo quedó primero, o fallo de red), no
        se lanza nada: mejor reintentar en el siguiente refresco con los
        datos ya al día que fabricar de menos sin que el operario se
        entere. Los que sí se reclamaron en un intento fallido se quedan
        reclamados -- no hace daño, ya los tiene esta máquina para la
        próxima vez."""
        for pid in ids:
            if not self.node.reclamar_pedido(pid):
                self.log(self.t(
                    'No se ha podido reclamar el pedido #{pid} para esta máquina '
                    '(ya asignado a otra, o sin conexión) -- lote cancelado, se '
                    'reintentará solo en el próximo ciclo.', pid=pid), False)
                return False
        return True

    def lanzar_todo_resumen(self):
        """'Lanzar todo el resumen' (sesion 2026-09-03, sustituye a
        'Lanzar todos los pedidos pendientes' -- ver comentario junto al
        boton, mas arriba, para el porque del cambio). Encola cada
        producto del 'Resumen por producto' y los va lanzando UNO DETRAS
        DE OTRO (ver _lanzar_siguiente_de_cola / _actualizar_estado_lote):
        mismo mecanismo que 'Lanzar todo' de un solo producto
        (lanzar_producto_agrupado, LED fijo, forzar_reparto=True), solo
        que encadenado automaticamente sin pulsar boton por boton."""
        if self._lote_en_curso():
            self.lote_status_var.set(self.t('Ya hay una producción en curso -- espera a que termine.'))
            return
        if self.cola_lotes:
            self.lote_status_var.set(self.t('Ya hay una cola de lotes en marcha -- espera a que termine.'))
            return
        pedidos = self.node.fetch_pedidos_pendientes()
        if pedidos is None:
            self.lote_status_var.set(self.t('Sin conexión con Taller_Administracion.'))
            return
        por_producto = self._agrupar_pedidos_por_producto(pedidos)
        if not por_producto:
            self.lote_status_var.set(self.t('No hay pedidos pendientes que fabricar.'))
            return
        items = [(codigo, info['color'], info['restante'], info['nombre'], info['ids'], info['producto_id'], info['subproductos'])
                 for codigo, info in sorted(por_producto.items())]
        resumen = ', '.join(
            f'{nombre} ({color}) x{cantidad}' for _codigo, color, cantidad, nombre, _ids, _pid, _subs in items)
        if not messagebox.askyesno(
            self.t('Confirmar producción de todo el resumen'),
            self.t('Esto va a fabricar, UN PRODUCTO DETRAS DE OTRO (el siguiente no empieza '
                   'hasta que el anterior termine de verdad, LED de producto fijo por lote):')
            + f'\n{resumen}\n\n' +
            self.t('Si estás controlando el Loader o el Sorter a mano ahora mismo, '
                   'se pelearán por el brazo con la demo automática.\n\n¿Continuar?'),
        ):
            return
        self._encolar_resumen(items, resumen, 'Lanzar todo el resumen (uno detrás de otro)')

    def _encolar_resumen(self, items, resumen, motivo):
        """Parte comun de lanzar_todo_resumen() (boton, con dialogo de
        confirmacion) y el modo Automatico en refresh_pedidos() (sin
        dialogo -- no hay nadie para pulsar "Si" cada 4s)."""
        self._audit(f'{motivo}: {resumen}')
        self.cola_lotes = items
        self._lanzar_siguiente_de_cola()

    def _auto_lanzar_si_toca(self, pedidos):
        """Modo Automatico (checkbox, sesion 2026-09-13): mismo camino que
        el boton 'Lanzar todo el resumen', pero disparado solo desde
        refresh_pedidos() (cada 4s) en vez de a mano, y sin dialogo de
        confirmacion. Mismas guardas que el boton (nada en curso, nada en
        cola) para no lanzar un lote encima de otro. 'pedidos' viene ya
        pedido por refresh_pedidos(), no se vuelve a pedir aqui."""
        if not self.auto_produccion.get():
            return
        if pedidos is None or not pedidos:
            return
        if self._lote_en_curso() or self._lote_recien_cerrado():
            return
        if self.cola_lotes:
            return
        por_producto = self._vigilar_progreso_auto(self._agrupar_pedidos_por_producto(pedidos))
        if not por_producto:
            return
        # El producto que se estaba fabricando va primero (mismo criterio que
        # _lanzar_siguiente_de_cola: no cambiar de producto con pedidos suyos
        # pendientes). Por CODIGO, no por color -- ver lote_producto_objetivo.
        ultimo = self.lote_producto_objetivo
        items = [(codigo, info['color'], info['restante'], info['nombre'], info['ids'], info['producto_id'], info['subproductos'])
                 for codigo, info in sorted(por_producto.items(), key=lambda kv: (kv[0] != ultimo, kv[0]))]
        resumen = ', '.join(
            f'{nombre} ({color}) x{cantidad}' for _codigo, color, cantidad, nombre, _ids, _pid, _subs in items)
        self._encolar_resumen(items, resumen, 'Automático (sin confirmar)')

    def _vigilar_progreso_auto(self, por_producto):
        """Freno del modo Automatico (2026-09-19). Automatico relanza lo que
        sigue pendiente, asi que si las piezas fabricadas NO llegan a apuntarse
        (Taller en otra direccion, red caida...) repetiria el mismo pedido sin
        fin. Aqui se compara cada tanda con la anterior: si un producto que se
        lanzo no avanza (no baja lo que falta ni sube lo completado)
        AUTO_MAX_TANDAS_SIN_PROGRESO veces seguidas, se deja de lanzar ESE
        producto -- el resto sigue -- y se avisa. Se libera solo si avanza por
        otra via, o al volver a marcar Automatico. Devuelve por_producto sin
        los bloqueados y deja guardada la foto para la proxima tanda."""
        for codigo in list(self._auto_bloqueados):
            info = por_producto.get(codigo)
            if info is None or info['restante'] < self._auto_bloqueados[codigo]:
                del self._auto_bloqueados[codigo]
                self._auto_sin_progreso.pop(codigo, None)
                self._audit(f'Automático: {codigo} avanza otra vez, se reanuda')
        for codigo in self._auto_lanzados:
            previo = self._auto_previo.get(codigo)
            info = por_producto.get(codigo)
            if previo is None:
                continue
            avanza = info is None or info['restante'] < previo[0] or info['completada'] > previo[1]
            if avanza:
                self._auto_sin_progreso[codigo] = 0
                continue
            self._auto_sin_progreso[codigo] = self._auto_sin_progreso.get(codigo, 0) + 1
            if self._auto_sin_progreso[codigo] >= AUTO_MAX_TANDAS_SIN_PROGRESO and codigo not in self._auto_bloqueados:
                self._auto_bloqueados[codigo] = info['restante']
                self._avisar_auto_sin_progreso(info['nombre'], self._auto_sin_progreso[codigo])
        self._auto_lanzados = set()
        disponibles = {c: i for c, i in por_producto.items() if c not in self._auto_bloqueados}
        self._auto_previo = {c: (i['restante'], i['completada']) for c, i in disponibles.items()}
        return disponibles

    def _avisar_auto_sin_progreso(self, nombre, tandas):
        base = self.node.taller_api_base
        mensaje = self.t(
            'AUTOMÁTICO DETENIDO para "{nombre}": se ha fabricado {tandas} veces seguidas y el pedido no avanza, '
            'así que las piezas no están llegando al Taller.\n\nRevisa la red: este panel usa el Taller en {base}. '
            'Comprueba que esa dirección es la del servidor donde está el pedido, que responde desde esta máquina '
            'y que el Sorter puede llegar a ella (pestaña Configuración, URL de Taller_Administracion).\n\n'
            'El resto de productos sigue en Automático. Para reintentar este, desmarca y vuelve a marcar Automático.',
            nombre=nombre, tandas=tandas, base=base)
        self.node.get_logger().warning(f'[auto] {mensaje}')
        self._audit(f'Automático detenido para "{nombre}" tras {tandas} tandas sin progreso (Taller: {base})')
        self.lote_status_var.set(mensaje.split('\n', 1)[0])
        self.config_status_var.set(mensaje.split('\n', 1)[0])
        self.root.after(0, lambda: messagebox.showwarning(self.t('Automático detenido'), mensaje))

    def _actualizar_titulo_ventana(self):
        """El titulo de la ventana (barra de tareas/alt-tab) tambien lleva
        la etiqueta -- asi se diferencia un panel de otro sin ni tener que
        mirar dentro de la ventana."""
        etiqueta = _cargar_etiqueta().strip()
        titulo = self.t('Panel de control manual - Panda')
        self.root.title(f'{titulo} [{etiqueta}]' if etiqueta else titulo)

    def guardar_etiqueta(self):
        """Boton 'Guardar' (o Enter) junto al campo Nombre de la cadena, en
        la pestaña Configuracion. Ya no pide clave aqui: la pestaña entera
        solo se puede tocar tras desbloquearla con CLAVE_MAQUINA."""
        if not self._config_desbloqueada:
            return
        texto = self.etiqueta_var.get().strip()
        if texto == _cargar_etiqueta():
            return  # no ha cambiado nada
        _guardar_etiqueta(texto)
        self._audit(f'Nombre de la cadena -> "{texto}"')
        self._actualizar_titulo_ventana()
        self._actualizar_resumen_config()
        self.config_status_var.set(
            self.t('Nombre de la cadena guardado: "{texto}" (se mantiene en el próximo arranque).', texto=texto) if texto
            else self.t('Nombre de la cadena borrado.'))

    def guardar_taller_api_base(self):
        """Boton 'Guardar' junto al campo URL de Taller_Administracion.
        Solo hace falta rellenarlo si esta linea corre en OTRO ordenador
        de la red distinto del que tiene Taller_Administracion (ver
        config_cadena.taller_api_base). Vacio = vuelve al valor por
        defecto del contenedor. Fuerza un re-login (taller_token=None)
        porque cambia de servidor -- ver fetch_pedidos_pendientes."""
        if not self._config_desbloqueada:
            return
        texto = self.taller_api_base_var.get().strip()
        if texto == _cargar_taller_api_base():
            return  # no ha cambiado nada
        _guardar_taller_api_base(texto)
        self.node.taller_api_base = texto or self.node._taller_api_base_defecto
        self.node.taller_token = None
        self._audit(f'URL de Taller_Administracion -> "{self.node.taller_api_base}"')
        self._actualizar_resumen_config()
        self.config_status_var.set(
            self.t('URL de Taller_Administracion guardada: "{texto}" (se mantiene en el próximo arranque).', texto=texto) if texto
            else self.t('URL de Taller_Administracion restaurada al valor por defecto de esta máquina.'))

    def guardar_numero_maquina(self):
        """Boton 'Guardar' junto al desplegable Nº Máquina -- ver
        CONFIG_MAQUINA_PATH. Cambia self.node.numero_maquina en caliente
        (afecta al siguiente refresco de pedidos, sin reiniciar nada) Y lo
        persiste en disco para el proximo arranque."""
        if not self._config_desbloqueada:
            return
        numero = self.numero_maquina_var.get()
        if numero == self.node.numero_maquina:
            return  # no ha cambiado nada
        if numero == 0 and not messagebox.askyesno(
                self.t('Nº Máquina 0'),
                self.t('En Taller_Administracion el 0 significa "pedido libre, sin máquina".\n\n'
                       'Con Nº Máquina 0 este panel NO podrá coger pedidos (el servidor lo rechaza), '
                       'ni a mano ni en Automático.\n\n¿Guardar 0 igualmente?'), parent=self.root):
            self.numero_maquina_var.set(self.node.numero_maquina)
            return
        self.node.numero_maquina = numero
        _guardar_numero_maquina(numero)
        self._audit(f'Nº Máquina -> {numero}')
        self._actualizar_resumen_config()
        self.config_status_var.set(self.t('Nº Máquina guardado: {numero} (se mantiene en el próximo arranque).', numero=numero))

    def guardar_grupo_cadena(self):
        """Boton 'Guardar' junto al desplegable Grupo Cadena."""
        if not self._config_desbloqueada:
            return
        numero = self.grupo_cadena_var.get()
        if numero == _cargar_grupo_cadena():
            return  # no ha cambiado nada
        self.node.grupo_cadena = numero
        _guardar_grupo_cadena(numero)
        self._audit(f'Grupo Cadena -> {numero}')
        self._actualizar_resumen_config()
        self.config_status_var.set(self.t('Grupo Cadena guardado: {numero} (se mantiene en el próximo arranque).', numero=numero))

    def cambiar_clave_config(self):
        """Boton 'Cambiar clave' (pestaña Configuracion, debajo de Idioma): la clave nueva se
        escribe DOS veces y solo se guarda si coinciden y tiene un largo minimo."""
        if not self._config_desbloqueada:
            return
        nueva, repetida = self.clave_nueva_var.get(), self.clave_repetida_var.get()
        error = None
        if not nueva or not repetida:
            error = self.t('Escribe la clave nueva dos veces.')
        elif nueva != repetida:
            error = self.t('Las dos claves no coinciden.')
        elif len(nueva) < MIN_LARGO_CLAVE:
            error = self.t('La clave nueva tiene que tener al menos {n} caracteres.', n=MIN_LARGO_CLAVE)
        elif _clave_correcta(nueva):
            error = self.t('La clave nueva es igual que la actual.')
        if error:
            self.clave_msg_var.set(error)
            self.clave_msg_label.config(fg=RED)
            return
        _guardar_clave_config(nueva)
        self._audit('Clave de configuración cambiada')
        self.clave_nueva_var.set('')
        self.clave_repetida_var.set('')
        self.clave_msg_var.set(self.t('Clave cambiada. Desde ahora se pide la nueva para desbloquear.'))
        self.clave_msg_label.config(fg=GREEN)

    def guardar_idioma(self):
        """Boton 'Guardar' junto al desplegable Idioma (sesion 2026-09-17,
        a peticion del usuario: "que funcione el traductor"). Guarda la
        preferencia Y retraduce ya mismo todo lo que se puede retraducir
        sin reiniciar -- ver _retraducir_estaticos."""
        if not self._config_desbloqueada:
            return
        etiqueta_idioma = self.idioma_var.get()
        codigo = IDIOMAS_INVERSO.get(etiqueta_idioma, 'es')
        if codigo == self.idioma:
            return  # no ha cambiado nada
        _guardar_idioma(codigo)
        self.idioma = codigo
        self._audit(f'Idioma -> {etiqueta_idioma}')
        self._retraducir_estaticos()
        self.config_status_var.set(self.t('Idioma guardado: {etiqueta}.', etiqueta=etiqueta_idioma))

    def toggle_auto_produccion(self):
        """Callback del Checkbutton 'Automático' (pestaña Configuracion,
        protegida con clave en bloque). Tkinter ya ha cambiado la variable
        antes de llamar aqui."""
        nuevo_valor = self.auto_produccion.get()
        self._audit(f'Automático -> {nuevo_valor}')
        self._auto_bloqueados.clear()
        self._auto_sin_progreso.clear()
        self._auto_previo = {}
        self._actualizar_resumen_config()
        mensaje = self.t('Modo Automático ACTIVADO: lanzará los pedidos pendientes solo, sin confirmar.'
                          if nuevo_valor else 'Modo Automático desactivado.')
        self.config_status_var.set(mensaje)
        self.lote_status_var.set(mensaje)

    def _lanzar_siguiente_de_cola(self):
        """Saca el siguiente producto de self.cola_lotes y lo lanza como
        un lote normal de un solo producto. Llamado una vez al confirmar
        'Lanzar todo el resumen', y despues cada vez que
        _actualizar_estado_lote detecta que el lote EN CURSO ha
        terminado de verdad (Sorter ha contado tantas entregas reales
        como pedia el lote, no solo que el Loader haya acabado de
        descargar en la cinta -- ver sorter_demo.py::run())."""
        if not self.cola_lotes:
            return
        if self.proc_loader is not None and self.proc_loader.poll() is None:
            # No deberia pasar (solo se llama cuando el lote anterior ya
            # ha terminado de verdad), pero por seguridad no lanzar dos
            # loader_demo a la vez -- reintentar en el siguiente sondeo.
            self.root.after(2000, self._lanzar_siguiente_de_cola)
            return
        # Cantidades AL DIA, no las de cuando se lleno la cola (sesion
        # 2026-09-14, aviso real del usuario: haciendo 10 Arandelas metio
        # otro pedido de 1; al terminar, la cola paso a Tuercas y la Arandela
        # nueva se quedo esperando al final). Se vuelven a pedir los pedidos:
        #  - si el producto que se acaba de fabricar tiene pedidos nuevos,
        #    se terminan antes de cambiar de producto;
        #  - el resto de la cola se recalcula con lo que falta ahora (puede
        #    haber stock nuevo o pedidos cancelados desde entonces).
        pedidos = self.node.fetch_pedidos_pendientes()
        if pedidos is not None:
            por_producto = self._agrupar_pedidos_por_producto(pedidos)
            # Por CODIGO, no por color -- ver lote_producto_objetivo (sesion
            # 2026-09-15, corregido: dos productos sin LED compartian el
            # mismo centinela SIN_COLOR, se pisaban entre si aqui).
            ultimo = self.lote_producto_objetivo
            if ultimo is not None and por_producto.get(ultimo, {}).get('restante', 0) > 0:
                info = por_producto[ultimo]
                nueva_fila = (ultimo, info['color'], info['restante'], info['nombre'], info['ids'], info['producto_id'], info['subproductos'])
                if all(item[0] != ultimo for item in self.cola_lotes):
                    self.cola_lotes.insert(0, nueva_fila)
                else:  # ya estaba mas atras en la cola: adelantarlo
                    self.cola_lotes = [item for item in self.cola_lotes if item[0] != ultimo]
                    self.cola_lotes.insert(0, nueva_fila)
                self._audit(f'Mismo producto con pedidos nuevos, se termina antes de cambiar: '
                            f'{info["nombre"]} ({info["color"]}) x{info["restante"]}')
            cola_al_dia = []
            for item_codigo, _color, _cantidad, _nombre, _ids, _pid, _subs in self.cola_lotes:
                info = por_producto.get(item_codigo)
                if info and info['restante'] > 0:
                    cola_al_dia.append(
                        (item_codigo, info['color'], info['restante'], info['nombre'], info['ids'], info['producto_id'], info['subproductos']))
            self.cola_lotes = cola_al_dia
            if not self.cola_lotes:
                return
        codigo, color, cantidad, nombre, ids, producto_id, subproductos = self.cola_lotes.pop(0)
        if not self._reclamar_grupo(ids):
            # No se ha podido reclamar (ver _reclamar_grupo) -- se salta
            # este producto y se sigue con el siguiente de la cola, en vez
            # de dejar la cola entera colgada esperando a este.
            self.root.after(500, self._lanzar_siguiente_de_cola)
            return
        self.producto_en_curso = codigo
        self._auto_lanzados.add(codigo)
        self._lanzar_produccion(color, cantidad, nombre, forzar_reparto=True, codigo=codigo, producto_id=producto_id,
                                 texto_oled=self._texto_oled_producto(nombre, subproductos))

    def _progreso_lote(self):
        """(hechas, objetivo) del lote actual, contadas por las entregas
        reales del Sorter. Un solo producto: cuenta cualquier color (el
        Loader usa los 3 cubos); mixto: la suma de los tres colores."""
        if self.lote_inicio_entregas is None or not self.lote_objetivo_por_color:
            return 0, 0
        hechas = sum(self.node.entregas_color.get(c, 0) - self.lote_inicio_entregas.get(c, 0)
                     for c in ('R', 'G', 'B'))
        return hechas, sum(self.lote_objetivo_por_color.values())

    def _lote_en_curso(self):
        """¿Sigue vivo el lote actual? (sesion 2026-09-14, bug real de
        sobreproduccion con dos cadenas). Antes solo se miraba si el
        proceso del Loader seguia vivo -- pero el Loader termina en cuanto
        deja el ultimo cubo en la cinta, y el Sorter tarda todavia ~25s por
        pieza en clasificar las que quedan. En ese hueco el pedido seguia
        pendiente y el modo Automatico relanzaba la cantidad ENTERA: un
        pedido de 1 se lanzo 3 veces, uno de 5 dos veces, y las piezas que
        seguian en la cinta se contaban como el producto del lote nuevo.

        Ahora el lote termina cuando el Sorter ha contado todas sus piezas.
        Si alguna se pierde por el camino (agarre fallido que el almacen
        recicla), el lote nunca llegaria al objetivo: por eso, con el Loader
        ya terminado, se da por cerrado tras LOTE_SIN_ENTREGAS_S sin
        ninguna entrega nueva."""
        if self.proc_loader is None:
            return False
        if self.proc_loader.poll() is None:
            return True
        hechas, objetivo = self._progreso_lote()
        if hechas >= objetivo:
            self._marcar_lote_cerrado()
            return False
        ahora = time.monotonic()
        if self._loader_fin_t is None:
            self._loader_fin_t = ahora
        ultima_actividad = max(self._loader_fin_t, self.node.ultima_entrega_t or 0.0)
        if ahora - ultima_actividad < LOTE_SIN_ENTREGAS_S:
            return True
        if not self._aviso_lote_incompleto:
            self._aviso_lote_incompleto = True
            self.node.get_logger().warning(
                f'Lote cerrado INCOMPLETO: {hechas}/{objetivo} piezas y {LOTE_SIN_ENTREGAS_S:.0f}s '
                'sin ninguna entrega nueva (alguna pieza se ha perdido por el camino).')
        self._marcar_lote_cerrado()
        return False

    def _marcar_lote_cerrado(self):
        if self._lote_cerrado_t is None:
            self._lote_cerrado_t = time.monotonic()

    def _lote_recien_cerrado(self):
        """El Sorter publica la entrega (con la que este panel cierra el
        lote) justo ANTES de apuntar la pieza en el Taller -- durante ese
        instante el almacen todavia no la cuenta, y Automatico lanzaria una
        pieza de mas. Se espera MARGEN_TALLER_S tras cerrar el lote."""
        return (self._lote_cerrado_t is not None
                and time.monotonic() - self._lote_cerrado_t < MARGEN_TALLER_S)

    def _actualizar_estado_lote(self):
        if self.proc_loader is None:
            estado_loader = self.t('sin lotes lanzados todavía')
        elif self.proc_loader.poll() is None:
            estado_loader = self.t('EN CURSO')
        else:
            estado_loader = self.t('terminado (código {code})', code=self.proc_loader.returncode)
            # El Loader terminar de descargar en la cinta no es el mismo
            # instante en que el Sorter termina de clasificar (ver
            # sorter_demo.py), pero para los botones "Lanzar este pedido"/
            # "Lanzar todo" en verde basta con esto: en cuanto el Loader ya
            # no esta vivo, ya no hay riesgo de mandar dos lotes a la vez,
            # que es lo que este color intenta evitar visualmente.
            self.pedido_id_en_curso = None
            self.producto_en_curso = None
        if self.proc_sorter is not None and self.proc_sorter.poll() is None:
            estado_sorter = self.t('activo')
        elif _demo_vivo('sorter_demo'):
            estado_sorter = self.t('activo (externo)')
        else:
            estado_sorter = self.t('sin arrancar') if self.proc_sorter is None else self.t('parado')
        progreso = ''
        if self.lote_inicio_entregas is not None and self.lote_objetivo_por_color:
            # Piezas de verdad fabricadas en ESTE lote (ver _lanzar_produccion):
            # diferencia entre las entregas totales acumuladas ahora y la foto
            # de cuando se lanzo, contadas por el propio robot al confirmar
            # cada entrega real -- no depende de Taller_Administracion ni de
            # si su reparto automatico esta activado.
            if self.lote_color_objetivo is not None:
                # Lote de un solo producto (sesion 2026-09-01, correccion
                # real del usuario): el Loader usa los 3 cubos, asi que una
                # entrega de CUALQUIER color cuenta para este producto --
                # sumar los tres en vez de exigir que coincida el color
                # real (ver loader_demo.py y SorterDemo._lote_color_objetivo).
                objetivo = self.lote_objetivo_por_color[self.lote_color_objetivo]
                hechas_total = sum(
                    self.node.entregas_color.get(c, 0) - self.lote_inicio_entregas.get(c, 0)
                    for c in ('R', 'G', 'B'))
                progreso = self.t('  |  Fabricadas: {hechas}/{objetivo} ({color})',
                                   hechas=hechas_total, objetivo=objetivo, color=self.lote_color_objetivo)
                # Lote REALMENTE terminado (sesion 2026-09-03): el Sorter
                # ya ha contado tantas entregas reales como pedia el lote
                # (mismo criterio que apaga el LED de producto en
                # sorter_demo.py::run(), no solo que el Loader haya
                # acabado de descargar en la cinta) -- si viene de
                # "Lanzar todo el resumen" (self.cola_lotes no vacio),
                # este es el momento de encadenar el siguiente producto.
                # (el encadenado vive al final del metodo desde 2026-09-14,
                # para los dos tipos de lote y con el cierre por tiempo de
                # _lote_en_curso)
            else:
                partes = []
                hechas_total = 0
                objetivo_total = 0
                for c, objetivo in self.lote_objetivo_por_color.items():
                    hechas = self.node.entregas_color.get(c, 0) - self.lote_inicio_entregas.get(c, 0)
                    partes.append(f'{c}:{hechas}/{objetivo}')
                    hechas_total += hechas
                    objetivo_total += objetivo
                progreso = self.t('  |  Fabricadas: {hechas}/{objetivo} ({detalle})',
                                   hechas=hechas_total, objetivo=objetivo_total, detalle=" ".join(partes))
        self.lote_status_var.set(self.t('Lote Loader: {estado_loader}  |  Sorter: {estado_sorter}{progreso}',
                                         estado_loader=estado_loader, estado_sorter=estado_sorter, progreso=progreso))
        # Siguiente producto de "Lanzar todo el resumen" / Automatico: solo
        # cuando el lote actual ha terminado DE VERDAD (ver _lote_en_curso).
        # _lote_recien_cerrado: mismos segundos de margen que Automatico, para
        # que el Taller ya cuente la ultima pieza al recalcular la cola.
        if self.cola_lotes and not self._lote_en_curso() and not self._lote_recien_cerrado():
            self._lanzar_siguiente_de_cola()

    def _poll_lote(self):
        self._actualizar_estado_lote()
        self.root.after(2000, self._poll_lote)

    def _refrescar_resumen_productos(self, pedidos):
        """Bloque 'Resumen por producto' (sesion 2026-09-01): agrupa todos
        los pedidos pendientes por producto y muestra el total + un boton
        'Lanzar todo' por producto. Reconstruido junto con refresh_pedidos()
        (mismos 4s), no tiene sondeo propio."""
        for child in self.resumen_producto_frame.winfo_children():
            child.destroy()
        if not pedidos:
            tk.Label(self.resumen_producto_frame,
                     text=self.t('Sin pedidos pendientes.') if pedidos == [] else
                     self.t('Sin conexión con Taller_Administracion ({base}).', base=self.node.taller_api_base),
                     font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT if pedidos == [] else '#ff6b6b'
                     ).grid(row=0, column=0, sticky='w', padx=6, pady=4)
            return
        por_producto = self._agrupar_pedidos_por_producto(pedidos)
        fila_grid = 0
        for codigo, info in sorted(por_producto.items()):
            plural = self.t('pedido') if info['n_pedidos'] == 1 else self.t('pedidos')
            # Codigo de producto + LED (sesion 2026-09-15, a peticion del
            # usuario: "donde pone el led pones el codigo tambien") -- el
            # codigo es la identidad real (ver _agrupar_pedidos_por_producto),
            # el LED es un dato aparte que puede no existir ('sin LED' en
            # vez del centinela interno SIN_COLOR, que no le dice nada al
            # operario).
            color_mostrado = self.t('sin LED') if info['color'] == SIN_COLOR else info['color']
            texto = self.t(
                '{nombre} ({codigo} · {color}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})',
                nombre=info['nombre'], codigo=codigo, color=color_mostrado,
                completada=info['completada'], pedida=info['pedida'],
                restante=info['restante'], n=info['n_pedidos'], plural=plural)
            tk.Label(self.resumen_producto_frame, text=texto, font=self.mono_font,
                     bg=PANEL_BG, fg=TEXT_LIGHT).grid(row=fila_grid, column=0, sticky='w', padx=6, pady=2)
            en_curso = (self.producto_en_curso == codigo)
            color_boton = '#2e7d32' if en_curso else PANEL_BG
            tk.Button(self.resumen_producto_frame,
                      text=self.t('Lanzando...') if en_curso else self.t('Lanzar todo'), font=self.big_font,
                      bg=color_boton, fg=TEXT_LIGHT,
                      activebackground='#2e7d32' if en_curso else '#3a3a3a', activeforeground=TEXT_LIGHT,
                      command=lambda cod=codigo, c=info['color'], n=info['nombre'], r=info['restante'], ids=info['ids'], pid=info['producto_id'], subs=info['subproductos']:
                      self.lanzar_producto_agrupado(cod, c, r, n, ids, pid, subs)
                      ).grid(row=fila_grid, column=1, padx=6, pady=2)
            fila_grid += 1
            # Desglose por variante, una fila propia por subproducto
            # (sesion 2026-09-15, a peticion del usuario, primero en
            # corchetes en la misma linea, despues "desglosa tambien por
            # subproducto" -- con sus propios numeros, no solo el nombre).
            # Se omite si solo hay una variante: seria identico a la fila
            # de arriba.
            if len(info['subproductos']) > 1:
                for nombre_sub, sub in sorted(info['subproductos'].items()):
                    plural_sub = self.t('pedido') if sub['n_pedidos'] == 1 else self.t('pedidos')
                    texto_sub = self.t(
                        '    · {nombre_sub} ({codigo}): {completada}/{pedida} hechas -- {restante} por fabricar ({n} {plural})',
                        nombre_sub=nombre_sub, codigo=sub['codigo_completo'],
                        completada=sub['completada'], pedida=sub['pedida'],
                        restante=sub['restante'], n=sub['n_pedidos'], plural=plural_sub)
                    tk.Label(self.resumen_producto_frame, text=texto_sub, font=self.mono_font,
                             bg=PANEL_BG, fg=GREY_TEXT).grid(row=fila_grid, column=0, sticky='w', padx=6, pady=1)
                    fila_grid += 1

    def lanzar_producto_agrupado(self, codigo, color, cantidad, nombre, ids, producto_id, subproductos):
        """'Lanzar todo' del resumen por producto (sesion 2026-09-01, a
        peticion del usuario: "si hay dos lotes de tornillos, uno con 3 y
        otro con 2, el lote seria de cinco, para hacer todos los tornillos
        a la vez"). A diferencia de lanzar_pedido() no hay un pedido_id
        unico al que atar cada pieza (pueden ser varios pedidos distintos)
        -- se manda forzar_reparto=True para que cada pieza se aplique
        igual al pedido pendiente MAS ANTIGUO de ese color, sin depender
        del interruptor reparto_automatico (mismo problema real que
        lanzar_pedido, ver _lanzar_produccion). 'ids' (sesion 2026-09-13):
        los pedidos concretos que forman este grupo, para reclamarlos
        antes de lanzar -- ver _reclamar_grupo."""
        if cantidad < 1:
            self.lote_status_var.set(self.t('"{nombre}" ya no tiene unidades pendientes.', nombre=nombre))
            return
        if self._lote_en_curso():
            self.lote_status_var.set(self.t('Ya hay un lote en curso (el Sorter aún no ha clasificado todas sus piezas) -- espera a que termine.'))
            return
        if not messagebox.askyesno(
            self.t('Confirmar producto'),
            self.t('Esto lanza al Loader y al Sorter a fabricar {cantidad} unidad(es) de "{nombre}", '
                   'sumando todos los pedidos pendientes de ese producto.\n'
                   'Si estás controlando el Loader o el Sorter a mano ahora mismo, '
                   'se pelearán por el brazo con la demo automática.\n\n¿Continuar?', cantidad=cantidad, nombre=nombre),
        ):
            return
        if not self._reclamar_grupo(ids):
            return
        self._audit(f'Lanzar todo el producto: {nombre} x{cantidad}')
        self.producto_en_curso = codigo  # para pintar el boton en verde, ver _refrescar_resumen_productos()
        self._lanzar_produccion(color, cantidad, nombre, forzar_reparto=True, codigo=codigo, producto_id=producto_id,
                                 texto_oled=self._texto_oled_producto(nombre, subproductos))

    def refresh_pedidos(self):
        for child in self.pedidos_frame.winfo_children():
            child.destroy()
        pedidos = self.node.fetch_pedidos_pendientes()
        self._refrescar_resumen_productos(pedidos)
        self._auto_lanzar_si_toca(pedidos)
        if pedidos is None:
            tk.Label(self.pedidos_frame, text=self.t('Sin conexion con Taller_Administracion ({base}).', base=self.node.taller_api_base),
                     font=self.mono_font, bg=PANEL_BG, fg='#ff6b6b'
                     ).grid(row=0, column=0, sticky='w', padx=6, pady=4)
        elif not pedidos:
            tk.Label(self.pedidos_frame, text=self.t('No hay pedidos pendientes.'),
                     font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT
                     ).grid(row=0, column=0, sticky='w', padx=6, pady=4)
        else:
            # Antes se cortaba en MAX_PEDIDOS_VISIBLES filas con un texto
            # "...y N mas" (sesion 2026-08-30) -- ahora que la lista tiene
            # su propio scroll (sesion 2026-09-02, ver mas arriba), se
            # muestran TODOS, ya vienen ordenados por fecha desde el
            # backend.
            for i, p in enumerate(pedidos):
                producto = p['producto']
                subproducto = p['subproducto']
                # Sesion 2026-09-15: 'color' paso a ser 'led_codigo',
                # opcional. El LED es decorativo, no tiene que influir en
                # la logica de negocio (peticion explicita del usuario) --
                # "+1 pieza" y "Lanzar este pedido" funcionan igual con o
                # sin LED, mandando producto_id/pedido_id directamente en
                # vez de depender de resolver un color.
                color = producto.get('led_codigo')
                # El nombre del subproducto (variante, p.ej. "Clavo 10mm")
                # tiene que verse aqui -- a peticion del usuario: dos
                # pedidos del mismo producto pueden ser variantes distintas
                # que el operario necesita distinguir, aunque la celda las
                # fabrique igual (mismo color/producto, ver "modo comodin").
                # Codigo de producto + LED (sesion 2026-09-15, a peticion
                # del usuario: "donde pone el led pones el codigo tambien")
                # y codigo COMPLETO del subproducto (mismo dia, "pones el
                # codigo completo del subproducto" -- producto+subproducto,
                # ver Subproducto.codigo_completo en el backend).
                texto = (f"{producto['nombre']} · {subproducto['nombre']} ({subproducto['codigo_completo']}) "
                         f"({producto['codigo']} · {color or 'sin LED'}): "
                         f"{p['cantidad_completada']}/{p['cantidad_pedida']} -- {p['estado']}")
                tk.Label(self.pedidos_frame, text=texto, font=self.mono_font, bg=PANEL_BG, fg=TEXT_LIGHT
                         ).grid(row=i, column=0, sticky='w', padx=6, pady=2)
                tk.Button(self.pedidos_frame, text=self.t('+1 pieza'), font=self.big_font,
                          bg=PANEL_BG, fg=TEXT_LIGHT, activebackground='#3a3a3a', activeforeground=TEXT_LIGHT,
                          command=lambda c=(color or SIN_COLOR), pid=producto['id']: self.do_marcar_pieza(c, producto_id=pid)
                          ).grid(row=i, column=1, padx=6, pady=2)
                color = color or SIN_COLOR
                # "Lanzar este pedido" (sesion 2026-09-01, a peticion del
                # usuario: "mira si puedo seleccionar el lote que quiero
                # lanzar" -- entre pedido y pedido el operario cambia de
                # produccion a mano, no quiere que se enlacen solos.
                # Lanza SOLO este pedido como lote de un solo producto
                # (mismo mecanismo que un tramo de "Lanzar todo el
                # resumen": LED fijo, usa los 3 cubos como material, ver
                # _lanzar_produccion), con la cantidad que falta de ESTE
                # pedido en concreto.
                restante = _pendiente_de_fabricar(p)
                # Verde mientras ESTE pedido este en curso de verdad
                # (sesion 2026-09-01, a peticion del usuario: "pon el
                # boton en verde para saber que se ha lanzado") --
                # self.pedido_id_en_curso se fija en lanzar_pedido() y se
                # limpia en _actualizar_estado_lote() en cuanto el Loader
                # termina (vivo o no, ver ese metodo). Como este frame se
                # destruye y recrea entero cada 4s (ver arriba), no basta
                # con cambiar el color del boton ya creado -- hay que
                # volver a pintarlo en verde cada vez que se reconstruye.
                en_curso = (self.pedido_id_en_curso == p['id'])
                color_boton = '#2e7d32' if en_curso else PANEL_BG
                # Etiqueta con variante + codigo, no solo el nombre del
                # producto (sesion 2026-09-18, aviso del usuario: "solo me
                # dices tuercas dime tambien 10mm y el codigo del
                # producto") -- se ve en la confirmacion, en la cabecera
                # ("Lote Loader: ...") y en la pantalla OLED del Loader
                # (ver TeleopGuiNode.pub_texto_producto). 'codigo' (el
                # parametro de lanzar_pedido, usado para agrupar lotes)
                # sigue siendo SOLO el del producto -- no tocarlo.
                etiqueta_completa = f"{producto['nombre']} {subproducto['nombre']} ({subproducto['codigo_completo']})"
                # Version en 3 lineas para la OLED (mismo dia, peticion
                # de seguido: "para lo de 10mm pon en la linea de abajo y
                # en la siguiente linea el codigo") -- '|' separa cada
                # trozo en su propia fila en la Pico (ver mostrar_oled en
                # Rasberry_Pi_Pico_USB_Loader/main.py), en vez de partir
                # el texto plano cada 16 caracteres a ciegas (cortaba
                # palabras como "10mm" a mitad si caia justo en el corte).
                texto_oled = f"{producto['nombre']}|{subproducto['nombre']}|{subproducto['codigo_completo']}"
                tk.Button(self.pedidos_frame,
                          text=self.t('Lanzando...') if en_curso else self.t('Lanzar este pedido'), font=self.big_font,
                          bg=color_boton, fg=TEXT_LIGHT,
                          activebackground='#2e7d32' if en_curso else '#3a3a3a', activeforeground=TEXT_LIGHT,
                          command=lambda pid=p['id'], c=color, n=etiqueta_completa, r=restante, cod=producto['codigo'], txt=texto_oled:
                          self.lanzar_pedido(pid, c, r, n, codigo=cod, texto_oled=txt)
                          ).grid(row=i, column=2, padx=6, pady=2)
        self.root.after(4000, self.refresh_pedidos)

    def do_marcar_pieza(self, color, producto_id=None):
        ok, info = self.node.marcar_cubo_clasificado(color, producto_id=producto_id)
        if ok:
            pedido = info.get('pedido')
            if pedido is not None:
                self.log(self.t('Pieza {color} registrada en el pedido #{id} ({completada}/{pedida}).',
                                 color=color, id=pedido["id"], completada=pedido["cantidad_completada"],
                                 pedida=pedido["cantidad_pedida"]), True)
            else:
                self.log(self.t('Pieza {color} guardada en stock (sin pedido pendiente, o reparto manual activo) -- {stock} unidades.',
                                 color=color, stock=info.get("stock_actual", "?")), True)
        else:
            self.log(self.t('No se pudo registrar la pieza {color}: {info}', color=color, info=info), False)
        self.refresh_pedidos()

    def _spin_tick(self):
        rclpy.spin_once(self.node, timeout_sec=0.0)
        self.root.after(50, self._spin_tick)

    def refresh_position(self):
        p = self.node.tcp_world()
        self.pos_var.set(
            f'TCP mundo:  x={p[0]:.4f}   y={p[1]:.4f}   z={p[2]:.4f}   '
            f'giro={np.degrees(self.node.yaw):.1f} deg')

    def refresh_step(self):
        self.step_var.set(f'Paso actual: {self.node.step * 100:.2f} cm')

    def log(self, msg, ok=True):
        self.log_var.set(msg)
        self.log_label.config(fg=GREEN if ok else '#ff6b6b')

    def do_stop(self):
        self.node.send_stop()
        self.log(self.t('PARADA manual enviada desde el panel.'), ok=False)

    def _pulsar_parada_simulada(self, aviso_var):
        """Boton rojo simulado de la pestaña Pico: parada al pulsar y cuenta atras del reset de clave."""
        self.do_stop()
        token = time.monotonic()
        self._reset_clave_token = token
        self._contar_reset_clave(aviso_var, token)

    def _soltar_parada_simulada(self, aviso_var):
        if self._reset_clave_token is not None:
            self._reset_clave_token = None  # soltado antes de tiempo: no pasa nada
            aviso_var.set(self.t('Mantén pulsado {s} s para restablecer la clave', s=SEGUNDOS_RESET_CLAVE))

    def _contar_reset_clave(self, aviso_var, token):
        if self._reset_clave_token != token:
            return  # soltado, o ya hay otra pulsacion
        falta = SEGUNDOS_RESET_CLAVE - (time.monotonic() - token)
        if falta <= 0:
            self._reset_clave_token = None
            aviso_var.set(self.t('Mantén pulsado {s} s para restablecer la clave', s=SEGUNDOS_RESET_CLAVE))
            self._pedir_reset_clave()
            return
        aviso_var.set(self.t('Restableciendo la clave en {s} s... suelta para cancelar', s=math.ceil(falta)))
        self.root.after(200, lambda: self._contar_reset_clave(aviso_var, token))

    def _vigilar_reset_clave(self):
        """Cada 300 ms: atiende la pulsacion larga del boton FISICO (la senal llega por ROS)."""
        if self.node.reset_clave_pedido:
            self.node.reset_clave_pedido = False
            self._pedir_reset_clave()
        self.root.after(300, self._vigilar_reset_clave)

    def _pedir_reset_clave(self):
        """Pulsacion larga (fisica o simulada): vuelve a la clave de fabrica si se esta mirando la
        pestaña Configuracion o Raspberry Pi Pico y el operario lo confirma. En cualquier otra
        pestaña se ignora: hace falta estar delante del panel."""
        if self._reset_clave_dialogo:
            return
        if self.notebook.select() not in (str(self.tab_config), str(self.tab_picos_led)):
            self.log(self.t('Pulsación larga ignorada: para restablecer la clave hay que tener abierta '
                            'la pestaña Configuración o Raspberry Pi Pico.'), ok=False)
            return
        self._reset_clave_dialogo = True
        try:
            if not messagebox.askyesno(
                    self.t('Restablecer la clave'),
                    self.t('¿Restablecer la clave de configuración a la de fábrica ({clave})?', clave=CLAVE_MAQUINA),
                    parent=self.root):
                self.log(self.t('Restablecimiento de la clave cancelado.'))
                return
            _restablecer_clave_config()
            self._audit('Clave de configuración restablecida a la de fábrica (pulsación larga del botón)')
            self.log(self.t('Clave restablecida a la de fábrica ({clave}).', clave=CLAVE_MAQUINA))
            self._avisar_oled_clave_restablecida()
        finally:
            self._reset_clave_dialogo = False

    def _avisar_oled_clave_restablecida(self):
        """'Contrasena reseteada' en la OLED (real y simulada) unos segundos; despues vuelve lo que habia."""
        previo = self.node.texto_producto_cmd
        if previo.startswith('MSG:'):
            previo = self._oled_previo_aviso  # un segundo reset seguido: no tomar el aviso por el texto de antes
        self._oled_previo_aviso = previo
        self.node.pub_texto_producto.publish(String(data=AVISO_OLED_CLAVE))

        def _reponer():
            if self.node.texto_producto_cmd == AVISO_OLED_CLAVE:  # si ha llegado otro texto, se respeta
                self.node.pub_texto_producto.publish(String(data=self._oled_previo_aviso))
        self.root.after(int(SEGUNDOS_AVISO_OLED * 1000), _reponer)

    def do_rearm(self):
        self.node.send_rearm()
        self.log(self.t('Rearme enviado -- puedes seguir moviendo el brazo.'))

    def on_stop_change(self, stopped):
        self.set_stopped_ui(stopped)
        if stopped:
            self.log(self.t('PARADA DE EMERGENCIA ACTIVA (fisica, manual o de otra demo).'), ok=False)

    def set_stopped_ui(self, stopped):
        if stopped:
            self.status_var.set(self.t('PARADO'))
            self.status_label.config(fg=RED)
            self.rearm_btn.config(state='normal', bg=YELLOW, fg='black',
                                   activebackground='#c9a400', activeforeground='black')
        else:
            self.status_var.set(self.t('EN MARCHA'))
            self.status_label.config(fg=GREEN)
            self.rearm_btn.config(state='disabled', bg=GREY, fg=GREY_TEXT,
                                   activebackground=GREY, activeforeground=GREY_TEXT)
        # Los botones de jog/pinza/postura YA NO se deshabilitan durante la
        # parada (sesion 2026-09-10, cambio de rumbo explicito del usuario:
        # "cuando salta la parada de emergencia tiene que dejar mover el
        # robot a mano" -- necesita poder liberar a mano un dedo trabado en
        # vez de solo esperar a REARME, que no arregla nada fisico por si
        # solo). node.move_delta/set_gripper/etc. ya no rechazan la orden
        # tampoco -- ver esos metodos para el riesgo conocido y aceptado
        # (self.real_theta de una demo automatica en pausa puede quedar
        # desactualizado). Se deja _jog_buttons y este metodo tal cual por
        # si se quiere volver a deshabilitar algo especifico en el futuro,
        # simplemente no se tocan aqui.

    def _audit(self, msg):
        # Registro de CADA clic con marca de tiempo en el log del nodo (que
        # va a /tmp/teleop_gui.log si se lanzo con stdout redirigido) -- para
        # poder saber con certeza que boton se pulso de verdad ante un
        # comportamiento inesperado, en vez de tener que adivinarlo (bug de
        # diagnostico real: un salto a HOME que no se pudo explicar sin
        # saber si fue un click en el boton HOME o el resultado de otro
        # boton).
        self.node.get_logger().info(f'[click] {msg}')

    def do_move(self, dx, dy, dz):
        ok, msg = self.node.move_delta(dx, dy, dz)
        p = self.node.tcp_world()
        # Registrar el RESULTADO (no solo la intencion) con la posicion TCP
        # resultante: sin esto, un click rechazado (IK no convergio / fuera
        # de limites) queda indistinguible en el log de uno aceptado, y
        # reconstruir a posteriori donde estaba realmente la pinza en un
        # momento dado (p.ej. al pulsar CERRAR) se vuelve una suma a ciegas
        # que puede arrastrar error si algun click intermedio se rechazo.
        self._audit(f'Mover TCP dx={dx:.4f} dy={dy:.4f} dz={dz:.4f} -> '
                     f'{"OK" if ok else "RECHAZADO"} pos=({p[0]:.4f},{p[1]:.4f},{p[2]:.4f})')
        self.refresh_position()
        self.log(msg if not ok else self.t('Movido.'), ok)

    def step_down(self):
        self.node.step = max(STEP_MIN, self.node.step / 2.0)
        self.refresh_step()

    def step_up(self):
        self.node.step = min(STEP_MAX, self.node.step * 2.0)
        self.refresh_step()

    def do_center(self):
        ok, msg = self.node.center_on_cube()
        self._audit(f'Centrar sobre cubo -> {"OK" if ok else "RECHAZADO"} {msg}')
        self.refresh_position()
        self.log(msg, ok)

    def do_rotate(self, dyaw):
        ok, msg = self.node.rotate_delta(dyaw)
        self._audit(f'Girar pinza dyaw={np.degrees(dyaw):.1f} deg -> '
                     f'{"OK" if ok else "RECHAZADO"} {msg}')
        self.refresh_position()
        self.log(msg, ok)

    def do_open(self):
        p = self.node.tcp_world()
        self._audit(f'ABRIR pinza pos=({p[0]:.4f},{p[1]:.4f},{p[2]:.4f})')
        ok = self.node.set_gripper(self.node.gripper_open)
        self.log(self.t('Pinza -> ABIERTA') if ok else self.t('PARADA activa -- rearma antes de abrir.'), ok)

    def do_close(self):
        p = self.node.tcp_world()
        self._audit(f'CERRAR pinza pos=({p[0]:.4f},{p[1]:.4f},{p[2]:.4f})')
        ok = self.node.set_gripper(self.node.gripper_closed)
        self.log(self.t('Pinza -> CERRADA') if ok else self.t('PARADA activa -- rearma antes de cerrar.'), ok)

    def do_home(self):
        # HOME esta pegado a otros botones de uso frecuente (Abrir/Cerrar
        # pinza, Orientar pinza abajo) en la misma columna -- un misclick ahi
        # manda el brazo a HOME sin querer y se ve como un "salto" raro
        # (reportado por el usuario). Se pide confirmacion porque es la
        # unica accion de este panel que reposiciona el brazo entero de
        # golpe a un sitio lejos de donde este trabajando.
        if not messagebox.askyesno(
            self.t('Confirmar HOME'),
            self.t('Esto mueve el brazo entero a la posicion de reposo (HOME).\n'
                   'Si estabas cerca de un cubo, se alejara de el.\n\n'
                   'Continuar?'),
        ):
            self._audit('HOME cancelado por el usuario (dialogo de confirmacion)')
            return
        self._audit('HOME confirmado')
        ok_home, msg_home = self.node.go_home()
        if not ok_home:
            self.refresh_position()
            self.log(msg_home, False)
            return
        # Encadenar la reorientacion aqui tambien: igual que al arrancar la
        # ventana, HOME_POSITIONS no deja la pinza mirando hacia abajo, y
        # sin este paso los botones de "Mover TCP" volverian a rechazarse
        # todos tras pulsar HOME.
        ok, msg = self.node.align_gripper_down()
        self.refresh_position()
        self.log(self.t('Vuelto a HOME y pinza reorientada hacia abajo. ') + msg, ok)

    def do_align(self):
        self._audit('Orientar pinza abajo')
        ok, msg = self.node.align_gripper_down()
        self.refresh_position()
        self.log(msg, ok)

    def do_led(self, letter):
        names = {'R': 'rojo', 'G': 'verde', 'B': 'azul', '0': 'apagado'}
        self._audit(f'LED -> {names[letter]}')
        self.node.set_led(letter)
        self.log(self.t('LED -> {nombre}', nombre=self.t(names[letter])))

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    node = TeleopGuiNode()
    node.get_logger().info('Esperando a que el driver se suscriba...')
    if not node.wait_for_subscribers():
        node.get_logger().error(
            f'Nadie se ha suscrito tras {node.max_wait_seconds:.0f}s '
            "(revisa que 'ros2 launch panda_controller robot_launch.py' este corriendo)."
        )
        node.destroy_node()
        rclpy.shutdown()
        return
    node.get_logger().info('Driver suscrito. Abriendo ventana...')

    app = TeleopApp(node)
    try:
        app.run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
