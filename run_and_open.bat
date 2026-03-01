@echo off
echo ========================================
echo   Iniciando servidor y abriendo navegador
echo ========================================
echo.

REM Obtener la IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)

:found
REM Limpiar espacios
set IP=%IP: =%

echo Tu IP local es: %IP%
echo.
echo Abriendo navegador en tu PC...
start http://localhost:8000
echo.
echo Para acceder desde Android:
echo   http://%IP%:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Ejecutar Django en 0.0.0.0
python manage.py runserver 0.0.0.0:8000

pause
