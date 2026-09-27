@echo off
rem Version: 2026-09-25 17:21 -- primera version: pregunta N y Nº de maquina y llama a arrancar_windows.bat -- SIN PROBAR
rem Crear (o volver a abrir) otra cadena en este mismo Windows, con doble clic.
rem Es lo mismo que "arrancar_windows.bat N [numero_maquina]", pero preguntando.
rem Cada cadena lleva su propio Webots (puerto 1233+N) y su panel (6079+N);
rem la web de pedidos es una sola para todas.
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo Crear otra cadena de produccion en este Windows
echo ================================================
echo La cadena 1 es la de siempre (arrancar_windows.bat sin nada).
echo Las otras van de la 2 a la 9. Si la cadena ya existe, simplemente se vuelve a abrir.
echo.

:pedir_n
set "N="
set /p "N=Numero de cadena (2 a 9, Intro sin nada = salir): "
if "%N%"=="" goto :eof
for /f "delims=23456789" %%x in ("%N%") do (
  echo   Tiene que ser un numero de 2 a 9.
  goto :pedir_n
)
if %N% gtr 9 ( echo   Tiene que ser un numero de 2 a 9. & goto :pedir_n )

:pedir_maquina
set "NUM_MAQUINA="
set /p "NUM_MAQUINA=Nº de maquina, 0 a 99 (Intro = no tocarlo, se pone luego en el panel): "
if "%NUM_MAQUINA%"=="" goto :lanzar
for /f "delims=0123456789" %%x in ("%NUM_MAQUINA%") do (
  echo   Tiene que ser un numero de 0 a 99, o Intro para dejarlo.
  goto :pedir_maquina
)
if %NUM_MAQUINA% gtr 99 ( echo   Tiene que ser un numero de 0 a 99. & goto :pedir_maquina )

:lanzar
echo.
if "%NUM_MAQUINA%"=="" (
  echo Lanzando la cadena %N%...
) else (
  echo Lanzando la cadena %N% con el Nº de maquina %NUM_MAQUINA%...
)
echo.
rem arrancar_windows.bat ya hace su propio "pause" al terminar.
call "%~dp0arrancar_windows.bat" %N% %NUM_MAQUINA%
