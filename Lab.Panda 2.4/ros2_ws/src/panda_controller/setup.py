# Version: 2026-09-29 13:41 -- quitadas las 7 demos antiguas de un robot (cinematica DH vieja)
from setuptools import setup
import os
from glob import glob

package_name = 'panda_controller'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'resource'), glob('resource/*.urdf')),
    ],
    install_requires=['setuptools', 'ikpy'],
    zip_safe=True,
    maintainer='aladin',
    maintainer_email='aladin@example.com',
    description='Controlador ROS2 para el brazo Franka Emika Panda (con pinza real) en Webots',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_gui = panda_controller.teleop_gui:main',
            'led_publisher = panda_controller.led_publisher:main',
            'led_publisher_usb = panda_controller.led_publisher_usb:main',
            'cube_shuttle_demo = panda_controller.cube_shuttle_demo:main',
            'stack_tower_demo = panda_controller.stack_tower_demo:main',
            'button_listener = panda_controller.button_listener:main',
            'estop_panel = panda_controller.estop_panel:main',
            'loader_demo = panda_controller.loader_demo:main',
            'sorter_demo = panda_controller.sorter_demo:main',
            'grasp_yaw_test = panda_controller.grasp_yaw_test:main',
            'sorter_hover_test = panda_controller.sorter_hover_test:main',
        ],
    },
)
