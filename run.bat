@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv (
  py -3.13 -m venv .venv
  if errorlevel 1 py -3.12 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
pause
