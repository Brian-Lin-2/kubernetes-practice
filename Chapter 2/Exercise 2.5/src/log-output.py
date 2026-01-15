import os
import random
import string
from datetime import datetime
import requests
from flask import Flask

app = Flask(__name__)

PING_PONG_URL = "http://ping-log-svc:3000/count"

# Config locations
MESSAGE = os.getenv("MESSAGE", "MESSAGE not set")
INFO_FILE_PATH = "/config/information.txt"


def generate_random_string(length=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def read_info_file():
    try:
        with open(INFO_FILE_PATH, "r") as f:
            return f.read().strip()
    except Exception:
        return "information.txt not found"


@app.route("/")
def log_output():
    try:
        response = requests.get(PING_PONG_URL, timeout=2)
        response.raise_for_status()
        count = response.json().get("count", 0)
    except Exception:
        count = "unavailable"

    timestamp = datetime.utcnow().isoformat() + "Z"
    random_string = generate_random_string()
    file_content = read_info_file()

    return (
        f"{file_content}\n"
        f"{MESSAGE}\n"
        f"{timestamp}: {random_string}.\n"
        f"Ping / Pongs: {count}\n"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)


