from flask import Flask, request, jsonify
import os
import threading

app = Flask(__name__)
PORT = int(os.getenv("BACKEND_PORT", 8001))

# In-memory storage for todos
todos = []
# Thread lock for safe concurrent access
todos_lock = threading.Lock()

@app.route("/todos", methods=["GET"])
def get_todos():
    """
    Return the list of todos as JSON.
    """
    with todos_lock:
        return jsonify(todos), 200

@app.route("/todos", methods=["POST"])
def create_todo():
    """
    Create a new todo from JSON payload.
    Example payload: {"title": "Buy milk", "done": false}
    """
    data = request.get_json()
    
    if not data or "title" not in data:
        return jsonify({"error": "Missing 'title' field"}), 400
    
    # Validate title is not empty
    if not data["title"].strip():
        return jsonify({"error": "'title' cannot be empty"}), 400
    
    with todos_lock:
        # Generate new ID based on existing todos
        new_id = max([t["id"] for t in todos], default=0) + 1
        
        todo = {
            "id": new_id,
            "title": data["title"].strip(),
            "done": bool(data.get("done", False))
        }
        todos.append(todo)
        
    return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    """
    Get a specific todo by ID.
    """
    with todos_lock:
        todo = next((t for t in todos if t["id"] == todo_id), None)
        
    if todo:
        return jsonify(todo), 200
    return jsonify({"error": "Todo not found"}), 404

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """
    Update a todo by ID.
    Example payload: {"title": "Buy milk and eggs", "done": true}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    with todos_lock:
        todo = next((t for t in todos if t["id"] == todo_id), None)
        
        if not todo:
            return jsonify({"error": "Todo not found"}), 404
        
        # Update fields if provided
        if "title" in data:
            if not data["title"].strip():
                return jsonify({"error": "'title' cannot be empty"}), 400
            todo["title"] = data["title"].strip()
        
        if "done" in data:
            todo["done"] = bool(data["done"])
    
    return jsonify(todo), 200

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """
    Delete a todo by ID.
    """
    with todos_lock:
        global todos
        initial_length = len(todos)
        todos = [t for t in todos if t["id"] != todo_id]
        
        if len(todos) == initial_length:
            return jsonify({"error": "Todo not found"}), 404
    
    return jsonify({"message": "Todo deleted successfully"}), 200

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=BACKEND_PORT, debug=False)

