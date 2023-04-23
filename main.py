import json
import time
from datetime import date, datetime
from logging import basicConfig, warning
from os import environ
from typing import List

import requests
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

BASE_URL = "https://ais.usvisa-info.com/en-fr/"
load_dotenv(find_dotenv())
FORMAT = '%(asctime)s: %(message)s'
basicConfig(format=FORMAT)


class AppointmentAvailable(BaseModel):
    date: date
    business_day: bool


class AppointmentAvailableList(BaseModel):
    __root__: List[AppointmentAvailable]


def send_text(bot_message):
    requests.get(f'https://api.telegram.org/bot{environ.get("TELEGRAM_TOKEN")}/sendMessage?chat_id='
                 f'{environ.get("TELEGRAM_HASH")}&parse_mode=Markdown&text={bot_message}')


def run():
    warning("Bot starting")
    current_date, msg, body = datetime.strptime(environ.get("CURRENT"), "%Y-%m-%d").date(), "No availabilities", []
    options = Options()
    options.add_argument('--headless')
    options.add_argument('ignore-certificate-errors')
    options.add_argument("--log-level=3")
    browser = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)

    warning("Login initiated")
    WebDriverWait(browser, 7)
    browser.get(f"{BASE_URL}niv/users/sign_in")
    browser.find_element(by=By.CLASS_NAME, value="down-arrow").click()
    time.sleep(.5)
    browser.find_element(by=By.ID, value="user_email").send_keys(environ.get("EMAIL"))
    browser.find_element(by=By.ID, value="user_password").send_keys(environ.get("PASSWORD"))
    browser.find_element(by=By.CLASS_NAME, value="icheckbox").click()  # Click Approve terms
    browser.find_element(by=By.NAME, value="commit").click()  # Click Submit to log in
    time.sleep(1)
    warning("Login done. Fetching availabilities")
    browser.get(f"{BASE_URL}niv/schedule/{environ.get('APPOINTMENT')}/appointment")  # Retrieve availabilities
    http_calls = [r for r in browser.requests if r.response and r.url.endswith("[expedite]=false")]
    browser.close()
    if http_calls:
        body = json.loads(http_calls[0].response.body)
        if body:
            warning("Computing first availability")
            best_date = min([a.date for a in AppointmentAvailableList(__root__=body).__root__ if a.business_day])
            if best_date < current_date:
                send_text(f"Earlier date found: {best_date.strftime('%d %b')}")
    else:
        send_text("No HTTP request matching expectations. Please investigate")

    warning(f"Shutting down. {msg}")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(e)
        send_text("Error happened. Please check")
