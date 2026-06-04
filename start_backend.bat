@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
python backend\main.py > backend.log 2>&1
