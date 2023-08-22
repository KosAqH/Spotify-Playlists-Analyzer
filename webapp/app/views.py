from . import app
from flask import render_template, redirect
from app.forms import SpotifyURL
import plotly.express as px
import plotly
import json

from .spotify_api.spotify_connection import SpotifyConn
from .spotify_api.spotify_api import SpotifyApi
from .spotify_api.spotify_utils import load_credentials, load_playlist_info


# main = Blueprint('main', __name__) only for blueprints

@app.route("/")
def index():
    spotify_url = SpotifyURL()
    return render_template('index.html', url_form = spotify_url)

@app.route("/index_post", methods=["POST"])
def index_post():
    #TODO load id from form
    token = get_spotify_access_token()
    api = SpotifyApi(token)

    p = api.RequestPlaylist("3vFJuKtDQCYkFSrpUaf5Dh")  # 387OhCc6mEbm96wzfFfhpp
    playlist_meta = api.RetrievePlaylistMetadata(p)

    ids = api.retrieveIdsFromPlaylist("3vFJuKtDQCYkFSrpUaf5Dh", playlist_meta["total_count"])

    tracks_info = load_playlist_info(api, ids)

    fig = px.scatter(tracks_info, x="valence", y="danceability", size = "popularity", hover_data=['artist_name', 'name'])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('analysis.html', playlist_info = playlist_meta, tracks_info = tracks_info, graph=graphJSON)

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
