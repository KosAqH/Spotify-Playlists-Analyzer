import os
from dotenv import load_dotenv
import pandas as pd
from app.spotify_api.audio_data import AudioData
from app.spotify_api.spotify_api import SpotifyApi
from app.spotify_api.spotify_connection import SpotifyConn

def load_credentials() -> [str, str]:
    """
    Function loads client id and api key from .env file. More info about this method of
        authentication may be found here: 
        https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow

        Returns:
            client_id (str)
            secret_key (str)
    """
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    secret_key = os.getenv("API_SECRET")
    return client_id, secret_key

def load_playlist_info(api: SpotifyApi, ids: list) -> pd.DataFrame:
    """
    Function returns Dataframe object that contains both audio features and metadata
        requested from Spotify's API. 

        Args:
            api (SpotifyApi object): initialized with access token object of class Spotify Api
            ids (list[str]): list of ids of all songs we want to get data about

        Returns:
            df (DataFrame object): df containing metadata and audio features data of all songs
                that id was passed to the function
    """
    meta = api.retrieveSongsMetadata(ids)
    features = api.retrieveSongsAudioFeatures(ids)

    df_meta = pd.DataFrame(meta)
    df_af = pd.DataFrame(features)

    AD = AudioData()
    df = AD.mergeTracksData(df_meta, df_af)
    return df

def get_token() -> str:
    """
    Function returns access token neccesary to connect to Spotify Api.

        Returns:
            token (str) - access token to spotify api
    """
    api_key, api_secret = load_credentials()
    conn = SpotifyConn()
    conn.authorize(api_key, api_secret)
    token = conn.get_access_token()
    return token

if __name__ == "__main__":
    pass