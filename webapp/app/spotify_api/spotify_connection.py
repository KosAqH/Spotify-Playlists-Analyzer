import requests

class SpotifyConn:
    """
    Class used for connecting with API and obtaining access token.
    """
    def __init__(self):
        """
        Constructor sets variables of necessary URL's.
        """
        self.auth_url = 'https://accounts.spotify.com/api/token'
        self.api_url = "https://api.spotify.com/v1/"

    def authorize(self, client_id: str, api_secret: str) -> None:
        """
        Function sends request to obtain access token. Token is saved as 
            a private attribute of class. None value is returned.

            Args:
                client_id (str) - client id, loaded from env variables
                api_secrets (str) - api key, loaded from env variables
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': api_secret,
        }

        self._auth_response = requests.post(self.auth_url, data=data)
        self._access_token = self._auth_response.json().get('access_token')

    def get_access_token(self) -> str:
        """
        Getter function that returns access token.

            Returns:
                _access_token (str) - acces token that has to be added to every API request
        """
        return self._access_token

if __name__ == "__main__":
    pass