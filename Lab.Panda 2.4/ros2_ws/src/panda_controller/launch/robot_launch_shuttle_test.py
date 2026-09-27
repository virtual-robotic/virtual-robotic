"""Lanza el Sorter + su camara + el nuevo SorterShuttleSupervisor
(worlds/panda_shuttle_test.wbt) -- mundo de prueba aislado (sesion
2026-09-06) para validar la bandeja/transbordador determinista del punto
de recogida sin Loader ni cinta fisica.

    ros2 launch panda_controller robot_launch_shuttle_test.py
"""

import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_controller import WebotsController

# Puerto de Webots para los controladores <extern> (1234 si no se dice otra
# cosa). Solo hace falta cambiarlo si en la MISMA maquina corre mas de un
# Webots, p.ej. dos cadenas con Webots nativo en Windows (ver
# INSTALAR_WINDOWS.md): cada una escucha en el suyo.
WEBOTS_PORT = os.environ.get('WEBOTS_PORT', '1234')


def generate_launch_description():
    package_dir = get_package_share_directory('panda_controller')
    urdf = os.path.join(package_dir, 'resource', 'panda_webots.urdf')
    cam_sorter_urdf = os.path.join(package_dir, 'resource', 'overhead_camera_sorter.urdf')
    shuttle_urdf = os.path.join(package_dir, 'resource', 'sorter_shuttle_supervisor.urdf')

    sorter_driver = WebotsController(
        robot_name='Sorter',
        namespace='sorter',
        port=WEBOTS_PORT,
        parameters=[{'robot_description': urdf}],
    )

    cam_sorter_driver = WebotsController(
        robot_name='OverheadCamSorter',
        port=WEBOTS_PORT,
        parameters=[{'robot_description': cam_sorter_urdf}],
    )

    shuttle_driver = WebotsController(
        robot_name='SorterShuttleSupervisor',
        port=WEBOTS_PORT,
        parameters=[{'robot_description': shuttle_urdf}],
    )

    return LaunchDescription([
        sorter_driver,
        cam_sorter_driver,
        shuttle_driver,
    ])
