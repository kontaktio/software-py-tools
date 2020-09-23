import logging
import os
from enum import Enum, auto
from pathlib import Path

import requests
from dotenv import load_dotenv


class Config(Enum):
    APPS_API_URL = auto()
    APPS_API_KEY = auto()
    IM_DB_HOST = auto()
    IM_DB_DATABASE = auto()
    IM_DB_USER = auto()
    IM_DB_PASSWORD = auto()


def get_config(key: Config):
    if Config.APPS_API_KEY.name not in os.environ:
        load_dotenv(dotenv_path=Path(".") / ".env", verbose=True)
    return os.environ[key.name]


HEADERS = {
    "Api-Key": get_config(Config.APPS_API_KEY),
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def post(url, json):
    try:
        response = requests.post(url, json=json, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(
            f"POST {url}\n{json}\nRESP {response.status_code} {response.content}"
        )
        raise


def put(url, json):
    try:
        response = requests.put(url, json=json, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(
            f"PUT {url}\n{json}\nRESP {response.status_code} {response.content}"
        )
        raise


def get(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(f"GET {url}\nRESP {response.status_code} {response.content}")
        raise


def delete(url):
    try:
        response = requests.delete(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(f"DELETE {url}\nRESP {response.status_code} {response.content}")
        raise
