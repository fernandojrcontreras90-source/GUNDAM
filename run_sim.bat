@echo off
cd %~dp0
pip install -r requirements.txt
streamlit run simulator.py
pause
