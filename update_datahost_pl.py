import logging
import sys

import psycopg2

from util.common import get_config, Config
from util.im_api import create_config


def get_all(email: str):
    conn = psycopg2.connect(
        host=get_config(Config.IM_DB_HOST),
        port=get_config(Config.IM_DB_PORT),
        database=get_config(Config.IM_DB_DATABASE),
        user=get_config(Config.IM_DB_USER),
        password=get_config(Config.IM_DB_PASSWORD),
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        select
            d.unique_id,
            m.api_key,
            applications->'system'->>'dataHost'
        from device d
                 join manager m on d.manager_id = m.id
        where
                model='PORTAL_LIGHT' and m.email=%s
        """,
        (email,),
    )
    records = cursor.fetchall()
    cursor.close()
    mapped = [{"unique_id": r[0], "api_key": r[1], "data_host": r[2]} for r in records]
    return mapped


def update_datahost(pls, datahost: str):
    for i, pl in enumerate(pls):
        if pl["data_host"] != datahost:
            create_config(
                {
                    "uniqueId": pl["unique_id"],
                    "deviceType": "GATEWAY",
                    "applications.system.dataHost": datahost,
                },
                pl["api_key"],
            )
            logging.info(
                f"{i+1}/{len(pls)} dataHost set to {datahost} for {pl['unique_id']}"
            )
        else:
            logging.info(
                f"{i+1}/{len(pls)} dataHost already = {datahost} for {pl['unique_id']}"
            )


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # See data/incorrect_datahosts.sql
    accounts = ["a.penpeski+ebg@kontakt.io", "p.gera+barclays@kontakt.io"]
    for account in accounts:
        pls = get_all(account)
        if pls:
            logging.info(f"Found {len(pls)} PLs in {account} account")
            update_datahost(pls, "https://event-processor.prod.kontakt.io")
        else:
            logging.info(f"No PLs found in {account} account")
