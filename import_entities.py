import csv
import logging
import sys
from typing import List

import psycopg2 as psycopg2

from util.api import create_entity_type
from util.common import get_config, post, Config


def retrieve_entities_from_db(order_id):
    conn = psycopg2.connect(
        host=get_config(Config.IM_DB_HOST),
        database=get_config(Config.IM_DB_DATABASE),
        user=get_config(Config.IM_DB_USER),
        password=get_config(Config.IM_DB_PASSWORD),
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        select
            device.unique_id,
            lower(b.mac)
        from device
        join beacon b on device.id = b.id
        where device.order_id=%s
        """,
        (order_id,),
    )
    records = cursor.fetchall()
    return records


def retrieve_entities_from_csv(file_path: str):
    entities = list()
    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            entities.append({row[0], row[1]})
    return entities


def import_entities(entities: List, entity_type=None):
    if not entity_type:
        entity_type = create_entity_type(
            {
                "name": "default",
                "sensors": [{"name": "rssi", "role": "rssi"}],
                "attributes": [
                    {
                        "id": "uniqueId",
                        "type": "externalId",
                        "name": "External Id",
                        "isNew": True,
                    }
                ],
            }
        )
    attribute = entity_type["attributes"][0]
    sensor = entity_type["sensors"][0]
    sensor["entityTypeSensor"] = {"id": sensor["id"]}
    sensor["field"] = sensor["name"]
    for i, entity in enumerate(entities):
        unique_id = entity[0]
        mac = entity[1]
        attribute["value"] = unique_id
        sensor["sensor"] = mac
        req_body = {
            "name": f"Beacon {unique_id}",
            "notes": "Generated by software-py-tools",
            "attributes": [attribute],
            "sensors": [sensor],
            "entityType": entity_type,
            "startDate": None,
            "endDate": None,
            "status": "Active",
        }
        post(
            f"{get_config(Config.APPS_API_URL)}/v2/entities", json=req_body,
        )
        logging.info(f"{i+1}/{len(entities)} Entity {unique_id} {mac}")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Pick one: load CSV list of uniqueId,mac OR
    # entities = retrieve_entities_from_csv("data/sample_beacon_list.csv")

    # ...load all beacons from order_id in IM API
    entities = retrieve_entities_from_db("xrXHmv")

    if entities:
        logging.info(f"Going to import {len(entities)} entities")

        # Pick one: find entity type first OR
        # entity_type = get_entity_type_by_id(123)
        # entity_type = get_entity_type_by_name("default")
        # import_entities(entities, entity_type)

        # ...create entities with new entity type
        import_entities(entities)
