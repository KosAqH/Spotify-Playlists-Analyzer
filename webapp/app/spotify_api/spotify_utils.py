import os
from dotenv import load_dotenv
import pandas as pd
from app.spotify_api.audio_data import AudioData
from app.spotify_api.spotify_api import SpotifyApi

def load_credentials():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    secret_key = os.getenv("API_SECRET")
    return client_id, secret_key

def load_playlist_info(api: object, ids: list) -> pd.DataFrame:
    meta = api.retrieveSongsMetadata(ids)
    features = api.retrieveSongsAudioFeatures(ids)

    df_meta = pd.DataFrame(meta)
    df_af = pd.DataFrame(features)

    AD = AudioData()
    df = AD.mergeTracksData(df_meta, df_af)
    return df

def extract_id():
    pass

if __name__ == "__main__":
    pass