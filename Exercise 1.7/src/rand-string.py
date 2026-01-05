import random
import string
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def generate_random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def current_log(random_string):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {random_string}"
    print(message)
    return message

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = current_log(self.server.random_string)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())

def start_http_server(random_string, port=3000):
    server = HTTPServer(("", port), Handler)
    server.random_string = random_string
    print(f"HTTP server listening on port {port}")
    server.serve_forever()

def main():
    random_string = generate_random_string()

    print("Application started.")
    print(f"Generated string: {random_string}\n")

    # Start HTTP server in background thread
    threading.Thread(
        target=start_http_server,
        args=(random_string,),
        daemon=True
    ).start()

    # Periodic logging every 5 seconds
    while True:
        current_log(random_string)
        time.sleep(5)

if __name__ == "__main__":
    main()

