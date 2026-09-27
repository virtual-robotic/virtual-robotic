@echo off
rem Version: 2026-09-26 09:17 -- varias cadenas; vista 3D; relanza la celda si Webots aun no habia cargado el mundo
rem El equivalente de arrancar_todo.sh para Windows. Se lanza con doble clic.
rem Necesita: Docker Desktop abierto (Engine running) y Webots R2025a instalado.
rem Ver INSTALAR_WINDOWS.md, apartado "La celda con los robots en Windows".
rem
rem Uso:  arrancar_windows.bat                   la cadena 1 (lo normal)
rem       arrancar_windows.bat N [numero_maquina] otra cadena N (2 a 9) en este
rem                                               mismo Windows, con su Webots
rem Para crear otra cadena con doble clic: crear_linea_windows.bat (pregunta los datos).
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "DEVC=%~dp0Lab.Panda 2.4\.devcontainer"
set "MUNDO=%~dp0Lab.Panda 2.4\worlds\panda_industrial_cell.wbt"

set "N=%~1"
if "%N%"=="" set "N=1"
set "NUM_MAQUINA=%~2"
for /f "delims=123456789" %%x in ("%N%") do (
  echo El numero de cadena tiene que ser de 1 a 9 ^(has puesto "%N%"^).
  goto :fin
)
if %N% gtr 9 ( echo El numero de cadena tiene que ser de 1 a 9. & goto :fin )

rem Lo de cada cadena (ver docker-compose.windows.yml): la 1 usa lo de siempre.
if "%N%"=="1" (
  set "LINEA_SUFIJO="
  set "PROYECTO=devcontainer"
) else (
  set "LINEA_SUFIJO=_linea%N%"
  set "PROYECTO=devcontainer%N%win"
)
set /a LINEA_DOMINIO=30+N
set /a LINEA_WEBOTS=1233+N
set /a LINEA_PANEL=6079+N
set /a LINEA_BOTON=5001+N
set "ROS=ros2_panda_dev24%LINEA_SUFIJO%"
set "PANEL_URL=http://localhost:%LINEA_PANEL%/vnc.html?autoconnect=1&resize=scale"
echo Cadena %N%: contenedor %ROS%, Webots en el puerto %LINEA_WEBOTS%, panel en el %LINEA_PANEL%.

echo == 0/6 -- Comprobando Docker ==
docker info >nul 2>&1
if errorlevel 1 (
  echo Docker no responde. Abre Docker Desktop, espera a "Engine running" y vuelve a lanzar esto.
  goto :fin
)

echo == 1/6 -- Web de pedidos (Taller_Administracion) ==
rem Una sola web para todas las cadenas: si ya esta en marcha, no pasa nada.
pushd "%~dp0Taller_Administracion"
docker compose up -d --build
if errorlevel 1 ( popd & goto :error )
popd

echo == 2/6 -- ROS 2 (sin el Webots de Linux: aqui se usa el de Windows) ==
pushd "%DEVC%"
docker compose -p %PROYECTO% -f docker-compose.windows.yml up -d --build
if errorlevel 1 ( popd & goto :error )
popd

echo == 3/6 -- Compilando el paquete ROS 2 (la primera vez tarda) ==
docker exec %ROS% bash -c "source /opt/ros/humble/setup.bash && cd /workspace && colcon build --packages-select panda_controller --symlink-install"
if errorlevel 1 goto :error

if not "%NUM_MAQUINA%"=="" (
  echo Poniendo el Nº de maquina %NUM_MAQUINA% a esta cadena...
  docker exec %ROS% python3 -c "import json,os,socket; p='/workspace/config_maquina_'+socket.gethostname()+'.json'; d=json.load(open(p)) if os.path.exists(p) else {}; d['numero_maquina']=int('%NUM_MAQUINA%'); json.dump(d,open(p,'w')); print('  escrito',p)"
)

echo == 4/6 -- Webots (el de esta cadena, puerto %LINEA_WEBOTS%) ==
rem Si ya esta abierto (su puerto contesta), no se abre otro.
docker exec %ROS% bash -c "timeout 1 bash -c '</dev/tcp/host.docker.internal/%LINEA_WEBOTS%'" >nul 2>&1
if not errorlevel 1 (
  echo Webots de esta cadena ya estaba abierto.
  goto :esperar_webots
)
set "WEBOTS="
if exist "%LOCALAPPDATA%\Programs\Webots\msys64\mingw64\bin\webotsw.exe" set "WEBOTS=%LOCALAPPDATA%\Programs\Webots\msys64\mingw64\bin\webotsw.exe"
if exist "%ProgramFiles%\Webots\msys64\mingw64\bin\webotsw.exe" set "WEBOTS=%ProgramFiles%\Webots\msys64\mingw64\bin\webotsw.exe"
rem Solo la vista 3D, sin arbol de escena, consola ni editor: Webots lee que
rem paneles se ven de worlds\.panda_industrial_cell.wbproj (y lo reescribe al
rem salir), asi que se pone la plantilla cada vez. Para ver un panel durante la
rem sesion: menu View. La plantilla se hizo el 2026-09-25 con Webots R2025a.
copy /y "%~dp0Lab.Panda 2.4\worlds\vista_solo_3d.wbproj.plantilla" "%~dp0Lab.Panda 2.4\worlds\.panda_industrial_cell.wbproj" >nul 2>&1
if defined WEBOTS (
  start "" "%WEBOTS%" --mode=realtime --port=%LINEA_WEBOTS% "%MUNDO%"
) else (
  echo No encuentro Webots instalado. Abrelo tu con --port=%LINEA_WEBOTS% y carga este mundo:
  echo   %MUNDO%
)

:esperar_webots
rem La primera vez Webots baja texturas y el Firewall de Windows puede
rem preguntar: hay que PERMITIR a Webots en redes privadas.
echo Esperando a que Webots acepte conexiones (hasta 5 minutos)...
set /a n=0
:bucle_webots
docker exec %ROS% bash -c "timeout 1 bash -c '</dev/tcp/host.docker.internal/%LINEA_WEBOTS%'" >nul 2>&1
if not errorlevel 1 goto :webots_listo
set /a n+=1
if %n% geq 300 (
  echo Webots no contesta en el puerto %LINEA_WEBOTS%. Mira que este abierto con el mundo
  echo cargado y que el Firewall de Windows le deje recibir conexiones.
  goto :fin
)
timeout /t 1 /nobreak >nul
goto :bucle_webots
:webots_listo
rem El puerto se abre un poco antes de que el mundo termine de cargar.
timeout /t 10 /nobreak >nul
echo Webots listo.

echo == 5/6 -- Lanzando la celda ==
rem Hasta 3 intentos (2026-09-26): el puerto de Webots se abre ANTES de que el
rem mundo termine de cargar (la primera vez tarda mucho, bajando modelos), y
rem si los controladores llegan antes de que esten los robots se rinden a los
rem ~50 s ("Giving up"). Visto en Windows 11. Entonces se relanza la celda.
set /a intento=0
:lanzar_celda
set /a intento+=1
rem Reinicio del contenedor y no un pkill: pkill mata "ros2 launch" pero deja
rem vivos sus hijos (button_listener, drivers...), y cada arranque sumaba otra
rem copia (visto 3 button_listener el 2026-09-24).
docker restart %ROS% >nul
docker exec -d %ROS% bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"
echo Esperando a que conecten los 6 controladores (intento %intento% de 3)...
set /a n=0
:bucle_ctrl
for /f %%c in ('docker exec %ROS% bash -c "grep -c 'Controller successfully connected' /tmp/robot_launch.log 2>/dev/null; true"') do set "c=%%c"
if "%c%"=="" set "c=0"
if %c% geq 6 goto :ctrl_listos
set /a n+=1
rem Si alguno ya se ha rendido, no hay que esperar mas: a relanzar.
for /f %%g in ('docker exec %ROS% bash -c "grep -c 'Giving up' /tmp/robot_launch.log 2>/dev/null; true"') do set "g=%%g"
if "%g%"=="" set "g=0"
if %g% geq 1 goto :reintentar
if %n% geq 90 goto :reintentar
timeout /t 1 /nobreak >nul
goto :bucle_ctrl
:reintentar
if %intento% lss 3 (
  echo Solo han conectado %c% de 6: Webots seguia cargando el mundo. Relanzo la celda...
  timeout /t 15 /nobreak >nul
  goto :lanzar_celda
)
echo AVISO: tras 3 intentos solo han conectado %c% de 6. Log: docker exec %ROS% cat /tmp/robot_launch.log
echo Si en Webots faltan los robots o se ha quedado en "Downloading assets": cierra
echo Webots y vuelve a lanzar este arrancar_windows.bat.
goto :panel
:ctrl_listos
set /a n+=1
if %n% geq 120 (
  echo AVISO: solo han conectado %c% de 6. Log: docker exec %ROS% cat /tmp/robot_launch.log
  echo Si en Webots faltan los robots: pasa la primera vez, mientras baja los
  echo modelos. Cierra Webots y vuelve a lanzar este arrancar_windows.bat.
  goto :panel
)
timeout /t 1 /nobreak >nul
goto :bucle_ctrl
:ctrl_listos
echo Listo: 6 controladores conectados.

:panel
echo == 6/6 -- Panel de control (en el navegador) ==
docker exec -d %ROS% panel_web.sh
timeout /t 8 /nobreak >nul
start "" "%PANEL_URL%"
echo.
echo Cadena %N% en marcha.
echo Panel de control: http://localhost:%LINEA_PANEL%/vnc.html
echo Web de pedidos:   http://localhost:8000
if not "%N%"=="1" echo Pon a esta cadena un nombre y un Nº de maquina propios en su panel, pestaña Configuracion.
echo Para apagarlo todo: cerrar_windows.bat
goto :fin

:error
echo.
echo Algo ha fallado en el paso anterior (mira el mensaje de arriba).

:fin
echo.
pause
