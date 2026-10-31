@echo off
python -m venv .venv
call .venv\Scripts\activate
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
echo Edit .env and add your Gemini API key, then run again.
pause
python app.py
