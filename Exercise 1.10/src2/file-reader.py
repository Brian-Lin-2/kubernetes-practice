from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.getenv("PORT", 8000))
LOG_FILE = os.getenv("LOG_FILE", "/src/data/output.log")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ["/", "/logs"]:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        try:
            with open(LOG_FILE, "r") as f:
                content = f.read()
        except FileNotFoundError:
            content = "Log file not found."

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

def start_server():
    server = HTTPServer(("", PORT), Handler)
    print(f"Log reader running on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()

