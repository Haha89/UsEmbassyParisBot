import json
import time
from datetime import date, datetime
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


class AppointmentAvailable(BaseModel):
    date: date
    business_day: bool

    def __str__(self):
        return f"Apt {self.date.isoformat()} - {'Open' if self.business_day else 'Holiday'}"


class AppointmentAvailableList(BaseModel):
    __root__: List[AppointmentAvailable]

    def __str__(self):
        return '\n'.join(map(str, self.__root__))


def run():
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)

    WebDriverWait(browser, 7)
    browser.get(f"{BASE_URL}niv/users/sign_in")
    browser.find_element(by=By.CLASS_NAME, value="down-arrow").click()
    time.sleep(.5)
    browser.find_element(by=By.ID, value="user_email").send_keys(environ.get("EMAIL"))
    browser.find_element(by=By.ID, value="user_password").send_keys(environ.get("PASSWORD"))
    browser.find_element(by=By.CLASS_NAME, value="icheckbox").click()  # Click Approve terms
    browser.find_element(by=By.NAME, value="commit").click()  # Click Submit to log in
    time.sleep(2)
    browser.get(f"{BASE_URL}niv/schedule/{environ.get('APPOINTMENT')}/appointment")  # Retrieve availabilities

    body = None
    for request in browser.requests:
        if request.response and request.url.endswith("[expedite]=false"):
            body = request.response.body
    browser.close()
    if not body:
        print("Error: no http request found")

    best_date = min([a.date for a in AppointmentAvailableList(__root__=json.loads(body)).__root__ if a.business_day])
    if best_date < datetime.strptime(environ.get("CURRENT"), "%Y-%m-%d").date():
        send_text(f"Alert: date found {best_date}")


def send_text(bot_message):
    requests.get(f'https://api.telegram.org/bot{environ.get("TELEGRAM_TOKEN")}/sendMessage?chat_id='
                 f'{environ.get("TELEGRAM_HASH")}&parse_mode=Markdown&text={bot_message}')


if __name__ == "__main__":
    run()
