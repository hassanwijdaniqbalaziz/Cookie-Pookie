@echo off
title Cookie Pookie Webapp
echo ========================================================
echo         Launching Cookie Pookie Streamlit App...
echo ========================================================
if exist ".venv\Scripts\streamlit.exe" (
    ".venv\Scripts\streamlit.exe" run app.py
) else (
    streamlit run app.py
)
pause

