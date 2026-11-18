@echo off
setlocal
pushd "%~dp0" || (
    echo Could not open the modcascade folder.
    pause
    exit /b 1
)

set "MODCASCADE_PYTHON=.venv\Scripts\python.exe"
if not exist "%MODCASCADE_PYTHON%" (
    echo Creating the Python environment...
    python -m venv .venv
    if errorlevel 1 goto failed
)

"%MODCASCADE_PYTHON%" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing modcascade dependencies...
    "%MODCASCADE_PYTHON%" -m pip install -e .
    if errorlevel 1 goto failed
)

echo API docs: http://127.0.0.1:8000/docs
"%MODCASCADE_PYTHON%" -m uvicorn modcascade.api.main:app
if errorlevel 1 goto failed

popd
exit /b 0

:failed
echo.
echo modcascade could not start. See the error above.
popd
pause
exit /b 1
