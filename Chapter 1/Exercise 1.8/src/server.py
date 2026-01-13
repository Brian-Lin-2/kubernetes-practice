import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.getenv("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
              <head>
                <title>My Python Server</title>
              </head>
              <body>
                <p>Hello</p>
              </body>
            </html>
            """

            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def start_server():
    server = HTTPServer(("", PORT), Handler)
    print(f"Server started on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()

