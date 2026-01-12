import os
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.getenv("PORT", 8000))
DATA_DIR = "/src/data"
IMAGE_PATH = os.path.join(DATA_DIR, "image.jpg")
TIMESTAMP_PATH = os.path.join(DATA_DIR, "timestamp.txt")
IMAGE_URL = "https://picsum.photos/1200"
CACHE_SECONDS = 600  # 10 minutes

def fetch_new_image():
    os.makedirs(DATA_DIR, exist_ok=True)
    urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)
    with open(TIMESTAMP_PATH, "w") as f:
        f.write(str(time.time()))

def image_age():
    if not os.path.exists(TIMESTAMP_PATH):
        return None
    with open(TIMESTAMP_PATH, "r") as f:
        return time.time() - float(f.read())

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
    
    def handle_root(self):
        # Fetch new image if none exists OR if cache expired
        if not os.path.exists(IMAGE_PATH):
            fetch_new_image()
        else:
            age = image_age()
            if age is not None and age >= CACHE_SECONDS:
                fetch_new_image()
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        
        # Hardcoded TODOs
        todos = ["Buy groceries", "Finish homework", "Call Alice"]
        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>Random Image + Todo</title>
          </head>
          <body>
            <h1>Cached Random Image</h1>
            <img src="/image" width="600"/>
            <h2>Todo List</h2>
            <form id="todo-form">
              <input type="text" id="todo-input" maxlength="140" placeholder="Enter your todo (max 140 chars)"/>
              <button type="submit">Send</button>
            </form>
            <ul id="todo-list">
              {''.join(f'<li>{todo}</li>' for todo in todos)}
            </ul>
          </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))
    
    def handle_image(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.end_headers()
        with open(IMAGE_PATH, "rb") as f:
            self.wfile.write(f.read())

def start_server():
    server = HTTPServer(("", PORT), Handler)
    print(f"Server started on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()

