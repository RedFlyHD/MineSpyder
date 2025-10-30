@echo off
title MineSpyder - Minecraft Server Scanner

echo 🕷️  Lancement de MineSpyder...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.7 ou plus récent
    pause
    exit /b 1
)

REM Afficher la version de Python
echo ✅ Python détecté:
python --version
echo.

REM Vérifier les dépendances
echo 📦 Vérification des dépendances...
python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Installation des dépendances requise
    echo Installation automatique...
    python -m pip install requests Pillow psutil
    if %errorlevel% neq 0 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

REM Lancer l'application
echo.
echo 🚀 Lancement de MineSpyder...
echo.
python main.py

echo.
echo 👋 MineSpyder fermé
pause
