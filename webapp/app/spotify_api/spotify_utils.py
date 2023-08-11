import os
from dotenv import load_dotenv

def load_credentials():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    secret_key = os.getenv("API_SECRET")
    return client_id, secret_key

if __name__ == "__main__":
    pass