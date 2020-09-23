import logging

from util.common import post, get, put, delete, get_config, Config


# Entities
# TODO Support more than 2000 records
def get_entities():
    response = get(f"{get_config(Config.APPS_API_URL)}/v2/entities?size=2000")
    entities = response.json()["content"]
    logging.info(f"Found {len(entities)} entities!")
    return entities


def delete_entity(entity):
    req_body = {"id": entity["id"], "status": "Removed"}
    put(
        f"{get_config(Config.APPS_API_URL)}/v2/entities/status", json=req_body,
    )


# Entity types
def create_entity_type(entity_type):
    resp = post(
        f"{get_config(Config.APPS_API_URL)}/v2/entities/types", json=entity_type,
    )
    created = resp.json()
    logging.info(f"New entity type: {created['id']} {created['name']}")
    return created


def get_entity_types():
    response = get(f"{get_config(Config.APPS_API_URL)}/v2/entities/types?size=2000")
    entity_types = response.json()["content"]
    logging.info(f"Found {len(entity_types)} entity types!")
    return entity_types


def get_entity_type_by_id(entity_type_id: int):
    resp = get(f"{get_config(Config.APPS_API_URL)}/v2/entities/types/{entity_type_id}")
    return resp.json()


def get_entity_type_by_name(entity_type_name: str):
    entity_types = get_entity_types()
    requested_type = [t for t in entity_types if t["name"] == entity_type_name]
    return requested_type if requested_type else None


def delete_entity_type(entity_type):
    delete_entity_type_by_id(entity_type["id"])


def delete_entity_type_by_id(entity_type_id):
    delete(f"{get_config(Config.APPS_API_URL)}/v2/entities/types/{entity_type_id}")


def delete_entity_type_by_name(name: str):
    entity_types = get_entity_types()
    requested_type = [t for t in entity_types if t["name"] == name]
    if requested_type:
        delete_entity_type(requested_type)
