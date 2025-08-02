@echo off
title PHAROS 2s
chcp 65001 >nul
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python main.py
pause
