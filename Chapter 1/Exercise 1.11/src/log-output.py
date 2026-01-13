import os
import random
import string
from datetime import datetime
from flask import Flask

app = Flask(__name__)

DATA_FILE = "/src/data/request_count.txt"

def generate_random_string(length=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/")
def log_output():
    # Read the current count
    try:
        with open(DATA_FILE, "r") as f:
            count = f.read().strip()
    except FileNotFoundError:
        count = "0"

    timestamp = datetime.utcnow().isoformat()
    random_string = generate_random_string()

    return f"Timestamp: {timestamp}\nRandom String: {random_string}\nPing-pong count: {count}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

