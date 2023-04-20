## US Ambassy in Paris bot

Allows to retrieve availabilities from the [US embassy in Paris](https://ais.usvisa-info.com/en-fr/ ) and notify you
easily.

# Setup

1) Download project and set up a virtual environment `venv`.
2) Download [chromedriver](https://chromedriver.chromium.org/downloads).exe and put it at the root of the project
3) Create a .env file at the root of the project and provide following information (example env-example):
    1) EMAIL: the email to log in to the website
    2) PASSWORD: the password to login
    3) APPOINTMENT: appointment number (ex 48415831). You'll find it in the url when you use the website
    4) CURRENT: your current appointment date (YYYY-MM-DD). The bot will notify you only if an earlier availability
       appears.
    5) TELEGRAM_HASH: the id of the telegram conversation to right the alert on
    6) TELEGRAM_TOKEN: the token to allow the bot to send messages on the chat
4) Add a task scheduler to run every hour or execute manually `main.py`
5) Wait for an alert and book it as quickly as possible

# Telegram information

If you don't know how to set up the telegram bot to notify you, follow this
link: https://core.telegram.org/api#getting-started

# Task scheduler
Create a Windows scheduled task to run every hour; 
- Program script: PROJECT_PATH\venv\Scripts\python.exe 
- Argument: PROJECT_PATH\main.py