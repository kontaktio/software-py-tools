import hashlib
import logging
import sys

import psycopg2 as psycopg2

from util.common import get_config, Config


def get_salt(email: str):
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
            salt
        from manager
        where email=%s
        """,
        (email,),
    )
    records = cursor.fetchall()
    if len(records) != 1:
        raise RuntimeError(
            f"Wanted to find one account for {email}, found {len(records)} instead"
        )
    return records[0][0]


def generate_password_hash(password_plaintext: str, salt: str):
    return hashlib.sha512(
        bytearray.fromhex(salt) + bytes(password_plaintext, "ascii")
    ).hexdigest()


def update_password_hash(email: str, password_hash: str):
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
        update manager
        set password = %s
        where email = %s
        """,
        (password_hash, email),
    )
    records_updated = cursor.rowcount
    conn.commit()
    cursor.close()
    if records_updated != 1:
        raise RuntimeError(
            f"Tried to update password hash for {email} "
            f"but updated {len(records_updated)} instead"
        )


# Required env. variables:
# IM_DB_*
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    email = "someone@kontakt.io"
    new_password = "secret"

    salt = get_salt(email)
    pw_hash = generate_password_hash(new_password, salt)
    update_password_hash(email, pw_hash)
    logging.info(f"New credentials:\nUser: {email}\nPassword: {new_password}")
