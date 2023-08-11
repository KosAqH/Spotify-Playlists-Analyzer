import os
from dotenv import load_dotenv
import requests

class SpotifyConn:
    def __init__(self):
        self.auth_url = 'https://accounts.spotify.com/api/token'
        self.api_url = "https://api.spotify.com/v1/"

    def authorize(self, client_id: str, api_secret: str) -> None:
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': api_secret,
        }

        self._auth_response = requests.post(self.auth_url, data=data)
        self._access_token = self._auth_response.json().get('access_token')

    def get_access_token(self) -> str:
        return self._access_token

if __name__ == "__main__":
    pass