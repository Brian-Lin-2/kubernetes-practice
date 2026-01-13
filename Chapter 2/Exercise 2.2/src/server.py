import os
import time
import urllib.request
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = int(os.getenv("PORT", 8000))
DATA_DIR = "/src/data"
IMAGE_PATH = os.path.join(DATA_DIR, "image.jpg")
TIMESTAMP_PATH = os.path.join(DATA_DIR, "timestamp.txt")
EXPIRED_ONCE_PATH = os.path.join(DATA_DIR, "expired_once.txt")
IMAGE_URL = "https://picsum.photos/1200"
CACHE_SECONDS = 600  # 10 minutes
TODO_BACKEND_URL = "http://todo-server-svc:3001/todos"

def fetch_new_image():
    os.makedirs(DATA_DIR, exist_ok=True)
    urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)
    with open(TIMESTAMP_PATH, "w") as f:
        f.write(str(time.time()))
    # Reset expired-once flag
    if os.path.exists(EXPIRED_ONCE_PATH):
        os.remove(EXPIRED_ONCE_PATH)

def image_age():
    if not os.path.exists(TIMESTAMP_PATH):
        return None
    with open(TIMESTAMP_PATH, "r") as f:
        return time.time() - float(f.read())

def fetch_todos():
    try:
        response = requests.get(TODO_BACKEND_URL, timeout=2)
        response.raise_for_status()
        todos = response.json()
        return todos
    except Exception as e:
        print(f"Error fetching todos: {e}")
        return []

def create_todo(title, done=False):
    try:
        payload = {"title": title, "done": done}
        response = requests.post(
            TODO_BACKEND_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error creating todo: {e}")
        return None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.handle_root()
        elif self.path == "/image":
            self.handle_image()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        if self.path == "/todos":
            self.handle_post_todo()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def handle_root(self):
        # Image caching logic
        if not os.path.exists(IMAGE_PATH):
            fetch_new_image()
        else:
            age = image_age()
            if age is not None and age >= CACHE_SECONDS:
                if os.path.exists(EXPIRED_ONCE_PATH):
                    fetch_new_image()
                else:
                    with open(EXPIRED_ONCE_PATH, "w") as f:
                        f.write("used")

        # Fetch todos from backend
        todos = fetch_todos()

        # Build HTML with form to add todos
        todos_html = "<ul>" + "".join(
            f"<li>{t.get('id')}: {t.get('title')} (Done: {t.get('done')})</li>" 
            for t in todos
        ) + "</ul>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>Random Image + Todos</title>
            <style>
              body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
              input, button {{ padding: 10px; margin: 5px; }}
              input[type="text"] {{ width: 300px; }}
              button {{ background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
              button:hover {{ background-color: #45a049; }}
              ul {{ list-style-type: none; padding: 0; }}
              li {{ padding: 10px; margin: 5px 0; background-color: #f0f0f0; border-radius: 5px; }}
            </style>
          </head>
          <body>
            <h1>Cached Random Image</h1>
            <img src="/image" width="600"/>
            
            <h2>Todo List</h2>
            <form id="todoForm">
              <input type="text" id="todoTitle" placeholder="Enter todo title" required>
              <label>
                <input type="checkbox" id="todoDone"> Done
              </label>
              <button type="submit">Add Todo</button>
            </form>
            {todos_html}
            
            <script>
              document.getElementById('todoForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const title = document.getElementById('todoTitle').value;
                const done = document.getElementById('todoDone').checked;
                
                try {{
                  const response = await fetch('/todos', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{title, done}})
                  }});
                  
                  if (response.ok) {{
                    window.location.reload();
                  }} else {{
                    alert('Failed to add todo');
                  }}
                }} catch (error) {{
                  alert('Error: ' + error.message);
                }}
              }});
            </script>
          </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def handle_image(self):
        if not os.path.exists(IMAGE_PATH):
            fetch_new_image()
        
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.end_headers()
        with open(IMAGE_PATH, "rb") as f:
            self.wfile.write(f.read())

    def handle_post_todo(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            title = data.get('title')
            done = data.get('done', False)
            
            if not title:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Title is required"}).encode('utf-8'))
                return
            
            # Create todo on backend
            result = create_todo(title, done)
            
            if result:
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Failed to create todo"}).encode('utf-8'))
                
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
        except Exception as e:
            print(f"Error handling POST: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

def start_server():
    server = HTTPServer(("", PORT), Handler)
    print(f"Server started on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()

