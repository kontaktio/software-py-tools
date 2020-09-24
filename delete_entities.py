import logging
import sys

from util.apps_api import (
    get_entity_types,
    delete_entity,
    get_entities,
    delete_entity_type,
)


def delete_entities_parallel():
    import multiprocessing as mp

    pool = mp.Pool(mp.cpu_count())
    entities = get_entities()
    while entities:
        logging.info(f"Removing a batch of {len(entities)} entities:")
        pool.map(delete_entity, entities)
        entities = get_entities()
    pool.close()


def delete_entities():
    """
    Obsolete, use delete_entities_parallel() instead.
    """
    entities = get_entities()
    while entities:
        logging.info(f"Removing a batch of {len(entities)} entities:")
        for i, entity in enumerate(entities):
            delete_entity(entity)
            logging.info(
                f"{i+1}/{len(entities)} Entity {entity['id']} {entity['name']}"
            )
        entities = get_entities()


def delete_entity_types():
    entity_types = get_entity_types()
    while entity_types:
        logging.info(f"Removing a batch of {len(entity_types)} entity types:")
        for i, entity_type in enumerate(entity_types):
            delete_entity_type(entity_type)
            logging.info(
                f"{i+1}/{len(entity_types)} Entity type {entity_type['id']} {entity_type['name']}"
            )
        entity_types = get_entity_types()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Delete all entities from Apps API account:
    delete_entities_parallel()

    # delete all/one entity type(s) from Apps API account (comment out as needed)
    # delete_entity_type_by_name("default")
    delete_entity_types()
