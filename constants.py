import os

ADMIN_PIN = os.environ.get("VPSH_ADMIN_PIN")
TOKEN = os.environ.get("VPSH_TOKEN")
SERVER_URL = os.environ.get("VPSH_SERVER")

PATH_TO_CONFIG = "config.json"

WC_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
APP_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"