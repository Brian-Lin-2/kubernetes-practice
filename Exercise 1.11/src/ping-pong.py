import os
from flask import Flask

app = Flask(__name__)

# Path to the shared file
DATA_FILE = "/src/data/request_count.txt"

# Ensure the file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        f.write("0\n")

@app.route("/pingpong")
def pingpong():
    # Read current count
    with open(DATA_FILE, "r") as f:
        count = int(f.read().strip())

    # Increment
    count += 1

    # Write back
    with open(DATA_FILE, "w") as f:
        f.write(f"{count}\n")

    return f"Pong! Count: {count}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

