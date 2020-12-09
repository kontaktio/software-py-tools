import csv
import logging
import sys
from typing import List

import psycopg2 as psycopg2

from util.apps_api import create_entity_type, create_entity
from util.common import get_config, Config


def retrieve_gateways_from_db(macs):
    logging.info(f"Connecting to {get_config(Config.IM_DB_HOST)}...")
    conn = psycopg2.connect(
        host=get_config(Config.IM_DB_HOST),
        port=get_config(Config.IM_DB_PORT),
        database=get_config(Config.IM_DB_DATABASE),
        user=get_config(Config.IM_DB_USER),
        password=get_config(Config.IM_DB_PASSWORD),
    )
    logging.info(f"Connected to {get_config(Config.IM_DB_HOST)}")
    cursor = conn.cursor()
    t = tuple(macs)
    cursor.execute(
        """
        select
            device.unique_id,
            device.order_id
        from device
        where upper(properties->>'mac') in %s
        """,
        (t,),
    )
    records = cursor.fetchall()
    cursor.close()
    return records


def retrieve_macs_from_log(file_path: str):
    mac_list = list()
    with open(file_path) as csv_file:
        for row in csv_file:
            last = row.split(" ")[-1]
            mac = last[19:46].replace("%3A", ":")
            mac_list.append(mac)
    return mac_list


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    macs = retrieve_macs_from_log("data/parse_provision_logs/provision_logs.txt")
    logging.info(f"Found {len(macs)} gateway MACs in the log file (non-distinct)")
    gateways = retrieve_gateways_from_db(macs)
    logging.info(f"Found {len(gateways)} gateways for these MACs")
    GNE4Dw = [g[0] for g in gateways if g[1] == "GNE4Dw"]

    if GNE4Dw:
        logging.info(f"Found {len(GNE4Dw)} gateways from orderId GNE4Dw: {GNE4Dw}")
    else:
        logging.error(f"No gateways found")
