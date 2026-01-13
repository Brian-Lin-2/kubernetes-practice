from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000
counter = 0

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter

        if self.path != "/pingpong":
            self.send_response(404)
            self.end_headers()
            return

        response = f"pong {counter}\n"
        counter += 1

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("", PORT), Handler)
    print(f"Server running on port {PORT}")
    server.serve_forever()

