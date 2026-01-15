from flask import Flask, jsonify

app = Flask(__name__)

# In-memory counter
count = 0

@app.route("/pingpong")
def pingpong():
    global count
    count += 1
    return f"Pong! Count: {count}\n"

@app.route("/count")
def get_count():
    return jsonify({"count": count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

