from . import app
from flask import render_template, redirect, request
from app.forms import SpotifyURL
import plotly.express as px
import plotly
import json
import pandas as pd
import re

from .spotify_api.spotify_connection import SpotifyConn
from .spotify_api.spotify_api import SpotifyApi
from .spotify_api.spotify_utils import load_credentials, load_playlist_info
from .spotify_api.audio_data import AudioData


# main = Blueprint('main', __name__) only for blueprints

@app.route("/")
def index():
    spotify_url = SpotifyURL()
    return render_template('index.html', url_form = spotify_url)

@app.route("/index_post", methods=["POST"])
def index_post():

    if request.form.get('url'):
        url = request.form.get('url')
        id = extractIdFromURL(url)
        if not id:
            id = url


    #TODO load id from form
    token = get_spotify_access_token()
    api = SpotifyApi(token)

    p = api.RequestPlaylist(id)
    playlist_meta = api.RetrievePlaylistMetadata(p)

    ids = api.retrieveIdsFromPlaylist(id, playlist_meta["total_count"])

    tracks_info = load_playlist_info(api, ids)

    fig = px.scatter(tracks_info, x="valence", y="danceability", size = "popularity", hover_data=['artist_name', 'name'])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    ad = AudioData()
    playlist_meta["total_minutes"] = round(ad.GetTotalDuration(tracks_info, unit="min"))
    playlist_meta["hours"] = playlist_meta["total_minutes"] // 60
    playlist_meta["minutes"] = playlist_meta["total_minutes"] % 60
    playlist_meta["top_artist"] = getTop(tracks_info, "artist_id", 3, api)
    playlist_meta["top_album"] = getTop(tracks_info, "album_id", 3, api)
    playlist_meta["top_genre"] = "placeholder"

    statistics = ["duration_ms", "tempo", "acousticness", "danceability", "energy", "instrumentalness", "valence"]

    statistics_data = []
    for s in statistics:
        statistics_data.append(getSpotifyStatistic(tracks_info, s))
    
    spotify_url = SpotifyURL()

    return render_template('analysis.html', 
                           playlist_info = playlist_meta, 
                           statistics_data = statistics_data, 
                           graph=graphJSON,
                           url_form = spotify_url #temporary
                           )

@app.route("/analysis")
def analysis():
    print("analysis")
    return render_template('analysis.html')



##### MOVE IT TO OTHER FILE LATER

def getSpotifyStatistic(df, stat_name):

    top_artists, top_titles, top_vals = getTopNumerical(df, stat_name, 3)
    bot_artists, bot_titles, bot_vals = getTopNumerical(df, stat_name, 3, get_bottom=True)

    fig = px.histogram(df, x=stat_name, nbins=10, marginal="violin")
    figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    d={
        "name": stat_name,
        "top_artists": top_artists,
        "top_values": top_vals,
        "top_titles": top_titles,
        "bot_artists": bot_artists,
        "bot_values": bot_vals,
        "bot_titles": bot_titles,
        "plot": figJSON
    }
    return d

def getTopNumerical(df: pd.DataFrame, column: str, topn: int, add_exaquo = False, get_bottom = False):

    extracted_data = df.sort_values(by=column, ascending = get_bottom).head(topn)[["name", "artist_name", column]]
    values = extracted_data[column].to_list()
    artists = extracted_data["artist_name"].to_list()
    titles = extracted_data["name"].to_list()

    if add_exaquo:
        s = df[column].value_counts()[(df[column].value_counts() == values[-1]) & (~df[column].value_counts().index.isin(keys))]
        values += (list(s.values))
        keys += (list(s.index))

    return artists, titles, values


def getTop(df: pd.DataFrame, column, topn, api: SpotifyApi, add_exaquo = False):
    max_value = df[column].value_counts().max()
    if max_value == 1:
        return {}
    
    extracted_data = df[column].value_counts().head(topn)
    keys = list(df[column].value_counts().head(topn).index)
    values = list(df[column].value_counts().head(topn).values)

    artist_meta = []
    album_meta = []

    if column == "artist_id":
        artist_meta = api.retrieveArtistMetadata(keys)
        for i, key in enumerate(keys):
            artist_meta[i]["count"] = values[i]
    elif column == "album_id":
        album_meta = api.retrieveAlbumMetadata(keys)
        for i, key in enumerate(keys):
            album_meta[i]["count"] = values[i]

    if add_exaquo:
        s = df[column].value_counts()[(df[column].value_counts() == values[-1]) & (~df[column].value_counts().index.isin(keys))]
        values += (list(s.values))
        keys += (list(s.index))

    return artist_meta or album_meta

def extractIdFromURL(url: str) -> str:
    pattern = "(?<=playlist/).*(?=\?)" 
    # looking for all chars between 'playlist/' phrase and '?' char
    match = re.search(pattern, url)
    if match:
        return match.group()
    else:
        return url

def get_spotify_access_token():
    api_key, api_secret = load_credentials()
    conn = SpotifyConn()
    conn.authorize(api_key, api_secret)
    token = conn.get_access_token()
    return token
