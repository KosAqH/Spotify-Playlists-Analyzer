from . import app
from flask import render_template, redirect
from app.forms import SpotifyURL

from .spotify_api.spotify_connection import SpotifyConn
from .spotify_api.spotify_api import SpotifyApi
from .spotify_api.spotify_utils import load_credentials


# main = Blueprint('main', __name__) only for blueprints

@app.route("/")
def index():
    spotify_url = SpotifyURL()
    return render_template('index.html', url_form = spotify_url)

@app.route("/index_post", methods=["POST"])
def index_post():
    token = get_spotify_access_token()
    api = SpotifyApi(token)

    p = api.RequestPlaylist("71mFAErIZDf0h18roaz9oq")  # 387OhCc6mEbm96wzfFfhpp
    print(len(api.retrieveIdsFromPlaylist(p)))

    # p = api.GetPlaylistInfo("387OhCc6mEbm96wzfFfhpp")
    d = api.RetrievePlaylistMetadata(p)

    print(d)
    return render_template('analysis.html')

@app.route("/analysis")
def analysis():
    print("analysis")
    return render_template('analysis.html')

def get_spotify_access_token():
    api_key, api_secret = load_credentials()
    conn = SpotifyConn()
    conn.authorize(api_key, api_secret)
    token = conn.get_access_token()
    return token
