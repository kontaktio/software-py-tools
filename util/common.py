import logging
import os
from enum import Enum, auto
from pathlib import Path

import requests
from dotenv import load_dotenv

API_KEY = "Api-Key"


class Config(Enum):
    APPS_API_URL = auto()
    APPS_API_KEY = auto()
    IM_API_URL = auto()

    APPS_DB_HOST = auto()
    APPS_DB_PORT = auto()
    APPS_DB_DATABASE = auto()
    APPS_DB_USER = auto()
    APPS_DB_PASSWORD = auto()
    IM_DB_HOST = auto()
    IM_DB_PORT = auto()
    IM_DB_DATABASE = auto()
    IM_DB_USER = auto()
    IM_DB_PASSWORD = auto()


def get_config(key: Config):
    if Config.APPS_API_KEY.name not in os.environ:
        load_dotenv(dotenv_path=Path(".") / ".env", verbose=True)
    return os.environ[key.name]


def post(url, headers, json=None, params=None):
    try:
        if params:
            response = requests.post(url, headers=headers, params=params)
        else:
            response = requests.post(url, json=json, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(
            f"POST {url} params {params}\n{headers}\n{json}"
            f"\nRESP {response.status_code} {response.content}"
        )
        raise


def put(url, headers, json):
    try:
        response = requests.put(url, json=json, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(
            f"PUT {url}\n{json}\nRESP {response.status_code} {response.content}"
        )
        raise


def get(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(f"GET {url}\nRESP {response.status_code} {response.content}")
        raise


def delete(url, headers):
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException:
        logging.error(f"DELETE {url}\nRESP {response.status_code} {response.content}")
        raise
