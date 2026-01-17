from flask import Flask, request, jsonify
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)
PORT = int(os.getenv("BACKEND_PORT", 8001))

DB_CONFIG = {
    "host": "todo-db-svc",
    "port": 3002,
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

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
        return jsonify({"error": "Missing or empty 'title'"}), 400

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        "INSERT INTO todos (title, done) VALUES (%s, %s) RETURNING id, title, done;",
        (data["title"].strip(), bool(data.get("done", False)))
    )

    todo = dict(cur.fetchone())
    conn.commit()

    cur.close()
    conn.close()
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
        if not data["title"].strip():
            return jsonify({"error": "'title' cannot be empty"}), 400
        fields.append("title = %s")
        values.append(data["title"].strip())

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

    return jsonify({"message": "Todo deleted successfully"}), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=False)


