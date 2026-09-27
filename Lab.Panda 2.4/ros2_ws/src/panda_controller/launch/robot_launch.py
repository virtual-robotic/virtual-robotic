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

    panda_driver = WebotsController(
        robot_name='Panda',
        port=WEBOTS_PORT,
        parameters=[
            {'robot_description': os.path.join(package_dir, 'resource', 'panda_webots.urdf')},
        ]
    )

    overhead_cam_driver = WebotsController(
        robot_name='OverheadCam',
        parameters=[
            {'robot_description': os.path.join(package_dir, 'resource', 'overhead_camera.urdf')},
        ]
    )

    return LaunchDescription([
        panda_driver,
        overhead_cam_driver,
    ])
