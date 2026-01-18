from flask import Flask, request, jsonify, g
import os
import time
import logging
import json
import psycopg2
import psycopg2.extras

# ======================
# Configuration
# ======================

PORT = int(os.getenv("BACKEND_PORT", 8001))
MAX_TODO_LENGTH = 140

DB_CONFIG = {
    "host": "todo-db-svc",
    "port": 3002,
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

# ======================
# JSON Logger (Loki)
# ======================

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Attach structured fields if provided
        if hasattr(record, "extra_data"):
            log.update(record.extra_data)

        return json.dumps(log)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("todo-backend")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

# ======================
# App
# ======================

app = Flask(__name__)

# ======================
# Database
# ======================

def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ======================
# Request Logging
# ======================

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    duration_ms = round((time.time() - g.start_time) * 1000, 2)

    logger.info(
        "http_request",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.remote_addr,
            }
        }
    )

    return response

# ======================
# Routes
# ======================

@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id, title, done FROM todos ORDER BY id;")
    todos = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify(todos), 200

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()

    if not data or "title" not in data or not data["title"].strip():
        logger.warning(
            "todo_rejected",
            extra={"extra_data": {"reason": "missing_or_empty_title"}}
        )
        return jsonify({"error": "Missing or empty 'title'"}), 400

    title = data["title"].strip()

    if len(title) > MAX_TODO_LENGTH:
        logger.warning(
            "todo_rejected",
            extra={
                "extra_data": {
                    "reason": "title_too_long",
                    "length": len(title),
                    "max_length": MAX_TODO_LENGTH,
                    "title_preview": title[:50],
                }
            }
        )
        return jsonify({
            "error": f"'title' must be {MAX_TODO_LENGTH} characters or fewer"
        }), 400

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        "INSERT INTO todos (title, done) VALUES (%s, %s) RETURNING id, title, done;",
        (title, bool(data.get("done", False)))
    )

    todo = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()

    logger.info(
        "todo_created",
        extra={
            "extra_data": {
                "todo_id": todo["id"],
                "title_length": len(todo["title"]),
                "done": todo["done"],
            }
        }
    )

    return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        "SELECT id, title, done FROM todos WHERE id = %s;",
        (todo_id,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify(dict(row)), 200

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    fields = []
    values = []

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "'title' cannot be empty"}), 400

        if len(title) > MAX_TODO_LENGTH:
            logger.warning(
                "todo_update_rejected",
                extra={
                    "extra_data": {
                        "todo_id": todo_id,
                        "reason": "title_too_long",
                        "length": len(title),
                        "max_length": MAX_TODO_LENGTH,
                    }
                }
            )
            return jsonify({
                "error": f"'title' must be {MAX_TODO_LENGTH} characters or fewer"
            }), 400

        fields.append("title = %s")
        values.append(title)

    if "done" in data:
        fields.append("done = %s")
        values.append(bool(data["done"]))

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(todo_id)

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        f"""
        UPDATE todos
        SET {', '.join(fields)}
        WHERE id = %s
        RETURNING id, title, done;
        """,
        values
    )

    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Todo not found"}), 404

    logger.info(
        "todo_updated",
        extra={
            "extra_data": {
                "todo_id": row["id"],
                "title_length": len(row["title"]),
                "done": row["done"],
            }
        }
    )

    return jsonify(dict(row)), 200

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM todos WHERE id = %s RETURNING id;", (todo_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        return jsonify({"error": "Todo not found"}), 404

    logger.info(
        "todo_deleted",
        extra={"extra_data": {"todo_id": todo_id}}
    )

    return jsonify({"message": "Todo deleted successfully"}), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ======================
# Entrypoint
# ======================

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=False)


