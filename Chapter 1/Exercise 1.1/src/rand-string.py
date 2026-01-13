import random
import string
import time
from datetime import datetime

def generate_random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    # Generate and store the random string on startup
    random_string = generate_random_string()

    print("Application started.")
    print(f"Generated string: {random_string}\n")

    # Output every 5 seconds
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {random_string}")
        time.sleep(5)

if __name__ == "__main__":
    main()

