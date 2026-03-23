@echo off
echo ==============================
echo SUBIENDO PROYECTO A GITHUB 🚀
echo ==============================

:: Configuración
set REPO_URL=https://github.com/Simonchuelo/catalogo.git
set BRANCH=main

:: Inicializar git si no existe
if not exist .git (
    echo Inicializando repositorio...
    git init
)

:: Agregar repositorio remoto (solo si no existe)
git remote | findstr origin >nul
if errorlevel 1 (
    echo Agregando repositorio remoto...
    git remote add origin %REPO_URL%
)

:: Agregar archivos
echo Agregando archivos...
git add .

:: Commit
echo Haciendo commit...
git commit -m "Actualizacion automatica %date% %time%"

:: Subir a GitHub
echo Subiendo a GitHub...
git push -u origin %BRANCH%

echo ==============================
echo LISTO ✅
pause