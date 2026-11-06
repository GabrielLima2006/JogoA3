@echo off
rem Roda o jogo pelo codigo-fonte (para quem mexe no codigo).
rem Para so jogar, use o instalador da pagina de releases.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python nao foi encontrado neste computador.
    echo Para jogar sem instalar nada, baixe o instalador em:
    echo https://github.com/GabrielLima2006/JogoA3/releases/latest
    pause
    exit /b 1
)

python -c "import pygame" >nul 2>nul
if errorlevel 1 (
    echo Instalando o pygame-ce, so na primeira vez...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Nao foi possivel instalar o pygame-ce. Verifique a internet e tente de novo.
        pause
        exit /b 1
    )
)

python main.py
if errorlevel 1 pause
