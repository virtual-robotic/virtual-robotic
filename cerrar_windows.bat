@echo off
rem Version: 2026-09-26 10:05 -- cierra tambien el Webots de cada cadena (el que escucha en el puerto 1233+N)
rem Apaga lo que arranca arrancar_windows.bat (y crear_linea_windows.bat),
rem incluido el Webots de cada cadena. Se cierra a la fuerza: no guarda nada del
rem mundo, y la vista de Webots la repone arrancar_windows.bat con su plantilla.
rem
rem Uso:  cerrar_windows.bat      TODAS las cadenas y la web de pedidos
rem       cerrar_windows.bat N    solo la cadena N (1 a 9); la web y las demas siguen
rem
rem No usa docker-compose.windows.yml: busca los contenedores por nombre y para
rem su proyecto (devcontainer = cadena 1, devcontainerNwin = cadena N), asi
rem funciona aunque se haya cambiado el fichero despues de arrancar.
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "SOLO=%~1"
if "%SOLO%"=="" goto :solo_ok
for /f "delims=123456789" %%x in ("%SOLO%") do (
  echo El numero de cadena tiene que ser de 1 a 9 ^(has puesto "%SOLO%"^).
  goto :fin
)
if %SOLO% gtr 9 ( echo El numero de cadena tiene que ser de 1 a 9. & goto :fin )
:solo_ok

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker no responde: si Docker Desktop esta cerrado, ya esta todo parado.
  goto :fin
)

echo == Parando ROS 2 ==
set "PARADAS=0"
for /f "usebackq delims=" %%c in (`docker ps -a --filter "name=ros2_panda_dev24" --format "{{.Names}}"`) do call :parar_cadena %%c
if "%PARADAS%"=="0" echo No habia ninguna cadena en marcha.

echo == Cerrando Webots ==
rem Sin numero: el de todas las cadenas posibles, tenga o no contenedor (p.ej.
rem un Webots que se quedo abierto de otra vez).
set "CERRADOS=0"
if "%SOLO%"=="" (
  for /l %%k in (1,1,9) do call :cerrar_webots %%k
) else (
  call :cerrar_webots %SOLO%
)
if "%CERRADOS%"=="0" echo No habia ningun Webots abierto.

if not "%SOLO%"=="" goto :hecho
echo == Parando la web de pedidos ==
pushd "%~dp0Taller_Administracion"
docker compose down
popd

:hecho
echo.
echo Hecho.
goto :fin

rem ---- %1 = numero de cadena; su Webots escucha en el puerto 1233+N
rem (ver arrancar_windows.bat). Solo se cierra si ese proceso es de verdad Webots.
:cerrar_webots
set /a PUERTO=1233+%1
for /f "tokens=5" %%p in ('netstat -ano -p tcp ^| findstr LISTENING ^| findstr /c:":%PUERTO% "') do (
  tasklist /fi "PID eq %%p" | findstr /i webots >nul && (
    taskkill /pid %%p /f >nul 2>&1
    echo Webots de la cadena %1 cerrado ^(puerto %PUERTO%^).
    set /a CERRADOS+=1
  )
)
goto :eof

rem ---- %1 = nombre del contenedor: ros2_panda_dev24 o ros2_panda_dev24_lineaN
:parar_cadena
set "C=%~1"
set "K="
if "%C%"=="ros2_panda_dev24" set "K=1"
if defined K goto :parar_k_ok
set "K=%C:ros2_panda_dev24_linea=%"
rem K tiene que ser una sola cifra 2..9; si no, es otro contenedor que
rem casualmente contiene el nombre, y no es nuestro.
if not "%K:~1%"=="" goto :eof
for /f "delims=23456789" %%x in ("%K%") do goto :eof
:parar_k_ok
if "%K%"=="1" (set "PROYECTO=devcontainer") else (set "PROYECTO=devcontainer%K%win")
if not "%SOLO%"=="" if not "%SOLO%"=="%K%" goto :eof
echo Cadena %K% (%C%, proyecto %PROYECTO%)...
docker compose -p %PROYECTO% down
rem Si el proyecto no se llamaba asi (arrancado a mano, otro -p...), al menos
rem que no se quede el contenedor vivo.
docker inspect %C% >nul 2>&1
if not errorlevel 1 docker rm -f %C% >nul
set /a PARADAS+=1
goto :eof

:fin
echo.
pause
