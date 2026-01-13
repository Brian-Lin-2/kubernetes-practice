import random
import string
from datetime import datetime
import requests
from flask import Flask

app = Flask(__name__)

PING_PONG_URL = "http://ping-log-svc:3000/count"

def generate_random_string(length=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/")
def log_output():
    try:
        response = requests.get(PING_PONG_URL, timeout=2)
        response.raise_for_status()
        count = response.json().get("count", 0)
    except Exception:
        count = "unavailable"

    timestamp = datetime.utcnow().isoformat()
    random_string = generate_random_string()

    return (
        f"Timestamp: {timestamp}\n"
        f"Random String: {random_string}\n"
        f"Ping-pong count: {count}\n"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)


