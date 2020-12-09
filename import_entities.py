import csv
import logging
import sys
from typing import List

import psycopg2 as psycopg2

from util.apps_api import create_entity_type, create_entity
from util.common import get_config, Config


def retrieve_entities_from_db(*order_ids):
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
    cursor.execute(
        """
        select
            device.unique_id,
            lower(b.mac)
        from device
        join beacon b on device.id = b.id
        where device.order_id in %s
        """,
        (order_ids,),
    )
    records = cursor.fetchall()
    logging.info(f"Found {len(records)} beacons in orders {order_ids}")
    cursor.close()
    return records


def retrieve_entities_from_csv(file_path: str):
    entities = list()
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            entities.append({row[0], row[1]})
    return entities


def import_entities(
    entities: List,
    entity_type=None,
    entity_type_name="default - created by software-py-tools",
):
    if not entity_type:
        entity_type = create_entity_type(
            {
                "name": entity_type_name,
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
        create_entity(req_body)
        logging.info(f"{i+1}/{len(entities)} Beacon {unique_id} {mac}")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Pick one: load CSV list of uniqueId,mac OR
    # entities = retrieve_entities_from_csv("data/import_entities/sample_beacon_list.csv")

    # ...load all beacons from order_id in IM API
    entities = retrieve_entities_from_db("Kh4aHD", "8M4vtD", "884659", "182094")

    if entities:
        logging.info(f"Going to import {len(entities)} entities")

        # Pick one: find entity type and append new entities to it....
        # entity_type = get_entity_type_by_id(123)
        # entity_type = get_entity_type_by_name("default")
        # import_entities(entities, entity_type)

        # ... OR create entities with a brand new entity type
        import_entities(entities)
        # import_entities(entities, entity_type_name="your custom type name")
    else:
        logging.error(f"No entities found")
