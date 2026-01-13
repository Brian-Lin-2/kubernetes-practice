import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.getenv("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
  pass

def start_server():
  server = HTTPServer(("", PORT), Handler)
  
  print(f"Server started on port {PORT}")
  server.serve_forever()

if __name__ == "__main__":
  start_server() 
