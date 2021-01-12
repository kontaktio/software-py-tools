import logging
import sys

from jwt import jwt, jwk_from_pem

from util.common import get_config, Config

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    private_key_path = get_config(Config.PRIVATE_KEY)
    # Payload format used when DNA-S calls IM API
    payload = {
        "userId": 12345,
        "iby": "Common Services",
        "type": "user_access_token",
        "username": "user@kontakt.io",
        "tenantid": 6789,
        "tenantId": 6789,
        "iat": 1610458439,
        "exp": 1610480039,
    }
    with open(private_key_path, "rb") as fh:
        key = jwk_from_pem(fh.read())
        encoded_jwt = jwt.JWT().encode(payload=payload, key=key, alg="RS256")
    print(encoded_jwt)
