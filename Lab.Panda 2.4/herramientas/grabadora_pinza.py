#!/usr/bin/env python3
# Version: 2026-09-29 12:40 -- grabadora de dedos, articulaciones y cubos para investigar roturas de pinza
"""Graba sin parar (a /tmp/grabadora.csv) dedos, ordenes de articulaciones y posicion real de
los cubos de los DOS robots, para ver que pasa justo antes de una dislocacion de pinza.

Con ella se encontraron el 2026-09-29 las tres causas de roturas arregladas ese dia (encaje de la
bandeja deshecho por la cinta, carrera Sorter-bandeja y el cubo "flotando" en la pinza del Loader).

Uso, con la celda en marcha (una grabadora por cadena, dentro de su contenedor ros2):
    docker cp grabadora_pinza.py ros2_panda_dev24:/tmp/
    docker exec -d ros2_panda_dev24 bash -c "source /opt/ros/humble/setup.bash && python3 /tmp/grabadora_pinza.py"
Cada linea: hora;que;valores (separados por ';'). Crece unos 3 MB por hora."""
import time
import rclpy
from std_msgs.msg import Float64MultiArray, Float64

rclpy.init()
n = rclpy.create_node('grabadora_pinza')
f = open('/tmp/grabadora.csv', 'a', buffering=1)
def apunta(nombre):
    return lambda m: f.write(f"{time.time():.3f};{nombre};{';'.join(f'{x:.4f}' for x in (m.data if hasattr(m.data, '__len__') else [m.data]))}\n")
for robot in ('loader', 'sorter'):
    n.create_subscription(Float64MultiArray, f'/{robot}/gripper_state', apunta(f'{robot}_dedos'), 10)
    n.create_subscription(Float64MultiArray, f'/{robot}/joint_positions', apunta(f'{robot}_articulaciones'), 10)
    n.create_subscription(Float64, f'/{robot}/gripper_position', apunta(f'{robot}_orden_pinza'), 10)
n.create_subscription(Float64MultiArray, '/warehouse/cube_positions', apunta('cubos'), 10)
rclpy.spin(n)
