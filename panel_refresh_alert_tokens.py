import logging
import sys
from datetime import datetime, timedelta

import psycopg2 as psycopg2

from util.common import get_config, Config
from util.im_api import create_expiring_token


def get_panel_alerts_created_by():
    conn = psycopg2.connect(
        host=get_config(Config.PANEL_DB_HOST),
        port=get_config(Config.PANEL_DB_PORT),
        database=get_config(Config.PANEL_DB_DATABASE),
        user=get_config(Config.PANEL_DB_USER),
        password=get_config(Config.PANEL_DB_PASSWORD),
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        select distinct
            created_by
        from alert_definition
        """,
    )
    records = cursor.fetchall()
    return records


def get_api_keys(user_ids: list):
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
            id, api_key
        from manager
        where id in %s
        and active is true
        """,
        (tuple(user_ids),),
    )
    records = cursor.fetchall()
    return records


def remove_alerts_by(user_ids: set):
    conn = psycopg2.connect(
        host=get_config(Config.PANEL_DB_HOST),
        port=get_config(Config.PANEL_DB_PORT),
        database=get_config(Config.PANEL_DB_DATABASE),
        user=get_config(Config.PANEL_DB_USER),
        password=get_config(Config.PANEL_DB_PASSWORD),
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        select id
        from alert_definition
        where created_by in %s
        """,
        (tuple(user_ids),),
    )
    alert_ids = cursor.fetchall()[0]
    cursor.execute(
        """
            delete from alert_recipient where alert_definition_id in %s;
            delete from alert_result where alert_definition_id in %s;
            delete from alert_trigger where alert_definition_id in %s;
            delete from alert_definition where id in %s;
        """,
        (
            alert_ids,
            alert_ids,
            alert_ids,
            alert_ids,
        ),
    )
    records_updated = cursor.rowcount
    conn.commit()
    cursor.close()
    logging.info(
        f"Deleted {records_updated} alerts " f"for {len(user_ids)} inactive users."
    )


def generate_tokens(users: list):
    tokens = list()
    for i, user in enumerate(users):
        token = create_expiring_token(datetime.now() + timedelta(days=5), user[1])
        tokens.append((user[0], token))
        logging.info(f"{i+1}/{len(users)} tokens regenerated")
    return tokens


def update_tokens(tokens: list):
    conn = psycopg2.connect(
        host=get_config(Config.PANEL_DB_HOST),
        port=get_config(Config.PANEL_DB_PORT),
        database=get_config(Config.PANEL_DB_DATABASE),
        user=get_config(Config.PANEL_DB_USER),
        password=get_config(Config.PANEL_DB_PASSWORD),
    )
    cursor = conn.cursor()
    for i, token in enumerate(tokens):
        cursor.execute(
            """
            update alert_definition
            set api_token = %s
            where created_by = %s
            """,
            (token[1], token[0]),
        )
        conn.commit()
        records_updated = cursor.rowcount
        if records_updated < 1:
            logging.error(
                f"Tried to update api token for alert created by {token[0]} "
                f"but modified row count was 0"
            )
        logging.info(f"{i+1}/{len(tokens)} tokens updated in Panel API DB")
    cursor.close()


# Required env. variables:
# PANEL_DB_*
# IM_DB_*
# IM_API_URL
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    alert_users = get_panel_alerts_created_by()
    if alert_users:
        logging.info(f"Found {len(alert_users)} users that created alerts in panel API")
    else:
        logging.error("No alert definitions found!")

    user_id_to_api_key = get_api_keys(alert_users)
    logging.info(f"Found {len(user_id_to_api_key)} active users in IM API")

    if len(alert_users) > len(user_id_to_api_key):
        panel_users = {u[0] for u in alert_users}
        im_users = {u[0] for u in user_id_to_api_key}
        inactive = panel_users.difference(im_users)
        logging.info(f"Deleting alert definition for {len(inactive)} inactive users")
        remove_alerts_by(inactive)

    user_id_to_token = generate_tokens(user_id_to_api_key)

    update_tokens(user_id_to_token)

    logging.info(f"Done!")
