import json

from . import DATADIR

DEFAULT_VERSION = 2

JWKS_TEST_FILENAME = str(DATADIR / "samtrafiken-test.json")
JWKS_PROD_FILENAME = str(DATADIR / "samtrafiken-prod.json")


_ENVIRONMENTS = {
    1: {
        "test": {
            "keys_filename": JWKS_TEST_FILENAME,
            "jwks": json.load(open(JWKS_TEST_FILENAME)),
            "metadata_url": "https://bobmetadata-pp.samtrafiken.se/api/v1/participantMetadata",
        },
        "prod": {
            "keys_filename": JWKS_PROD_FILENAME,
            "jwks": json.load(open(JWKS_PROD_FILENAME)),
            "metadata_url": "https://bobmetadata.samtrafiken.se/api/v1/participantMetadata",
        },
    },
    2: {
        "test": {
            "keys_filename": JWKS_TEST_FILENAME,
            "jwks": json.load(open(JWKS_TEST_FILENAME)),
            "metadata_url": "https://bobmetadata-pp.samtrafiken.se/api/v2/participantMetadata",
        },
        "prod": {
            "keys_filename": JWKS_PROD_FILENAME,
            "jwks": json.load(open(JWKS_PROD_FILENAME)),
            "metadata_url": "https://bobmetadata.samtrafiken.se/api/v2/participantMetadata",
        },
    },
}


def where(env: str = "prod", version: int = DEFAULT_VERSION) -> str:
    return _ENVIRONMENTS[version][env]["keys_filename"]


def trusted_jwks(env: str = "prod", version: int = DEFAULT_VERSION) -> dict:
    return _ENVIRONMENTS[version][env]["jwks"]


def metadata_url(env: str = "prod", version: int = DEFAULT_VERSION) -> str:
    return _ENVIRONMENTS[version][env]["metadata_url"]
