@echo off
title Subir proyecto a GitHub

echo ==============================
echo SUBIENDO PROYECTO A GITHUB 🚀
echo ==============================

:: CONFIG
set REPO_URL=https://github.com/Simonchuelo/catalogo.git
set BRANCH=main

:: Configurar usuario (solo si no existe)
git config --global user.name >nul 2>&1
if errorlevel 1 (
    echo Configurando usuario...
    git config --global user.name "Simonchuelo"
    git config --global user.email "prueba404100@gmail.com"
)

:: Inicializar repo si no existe
if not exist .git (
    echo Inicializando repositorio...
    git init
)

:: Crear rama main
git branch -M %BRANCH%

:: Configurar remoto correctamente
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Agregando remoto...
    git remote add origin %REPO_URL%
) else (
    echo Actualizando remoto...
    git remote set-url origin %REPO_URL%
)

:: Agregar archivos
echo Agregando archivos...
git add .

:: Commit (solo si hay cambios)
git diff --cached --quiet
if errorlevel 1 (
    echo Haciendo commit...
    git commit -m "Actualizacion automatica"
) else (
    echo No hay cambios para commitear
)

:: Subir a GitHub
echo Subiendo a GitHub...
git push -u origin %BRANCH%

echo ==============================
echo PROCESO FINALIZADO ✅
echo ==============================
pause