@echo off
title Atlas AQAR Dashboard
echo ======================================================
echo Launching Atlas AQAR Interactive Streamlit Dashboard...
echo URL: http://localhost:8501
echo ======================================================
cd /d "%~dp0"
set PYTHONPATH=%~dp0;%PYTHONPATH%
.\.venv\Scripts\streamlit.exe run src\dashboard\app.py
pause
