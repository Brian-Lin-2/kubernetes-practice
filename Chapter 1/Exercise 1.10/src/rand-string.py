import time
import random
import string
from datetime import datetime

OUTPUT_FILE = "/src/data/output.log"
INTERVAL_SECONDS = 5

def generate_random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    random_string = generate_random_string()

    while True:
        timestamp = datetime.utcnow().isoformat()
        line = f"{timestamp} {random_string}\n"

        with open(OUTPUT_FILE, "a") as f:
            f.write(line)

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()

