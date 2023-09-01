from . import app
from flask import render_template, redirect, request
from app.forms import SpotifyURL, SpotifyDoubleURL
import pandas as pd

from .spotify_api.spotify_api import SpotifyApi
from .spotify_api.spotify_utils import get_token, load_playlist_info, extractIdFromURL, UpdatePlaylistMeta
from .spotify_api.audio_data import AudioData

STATISTICS = ["duration_s", "tempo", "acousticness", "danceability", "energy", "instrumentalness", "loudness", "valence"]

@app.route("/")
def index():
    spotify_url = SpotifyURL()
    spotify_double_url = SpotifyDoubleURL()

    return render_template('index.html', 
                           url_form_analysis = spotify_url, 
                           url_form_comparison = spotify_double_url)

@app.route("/index_post", methods=["POST"])
def index_post():
    ad = AudioData()

    if request.form.get('url'):
        url = request.form.get('url')
        id = extractIdFromURL(url)
        if not id:
            id = url

    token = get_token()
    api = SpotifyApi(token)

    playlist_meta = api.retrievePlaylistMetadata(id)

    ids = api.retrieveIdsFromPlaylist(id, playlist_meta["total_count"])
    tracks_info = load_playlist_info(api, ids)      

    playlist_meta = UpdatePlaylistMeta(playlist_meta, ad, tracks_info, api)
    info = tracks_info[STATISTICS].describe().round(4).drop("count").to_dict()

    statistics_data = []
    for s in STATISTICS:
        statistics_data.append(ad.getSpotifyStatistic(tracks_info, s))
    
    return render_template('analysis.html', 
                           playlist_info = playlist_meta, 
                           statistics_data = statistics_data, 
                           info = info
                           )

@app.route("/p_comp_post", methods=["POST"])
def playlists_comparison_post():
    urls = []
    playlists_meta = []
    dfs = []

    token = get_token()
    api = SpotifyApi(token)
    ad = AudioData()

    if request.form.get('url1') and request.form.get('url2'):
        urls += [request.form.get('url1'), request.form.get('url2')]

    for url in urls:
        id = extractIdFromURL(url)
        playlist_meta = api.retrievePlaylistMetadata(id)
        
        ids = api.retrieveIdsFromPlaylist(id, playlist_meta["total_count"])
        tracks_info = load_playlist_info(api, ids)
        dfs.append(tracks_info)

        playlist_meta = UpdatePlaylistMeta(playlist_meta, ad, tracks_info, api)
        playlists_meta.append(playlist_meta)

    dfs[0]["no"] = 1
    dfs[1]["no"] = 2

    df = pd.concat([dfs[0], dfs[1]], axis=0)

    statistics_data = []
    for s in STATISTICS:
        statistics_data.append(ad.getSpotifyComparisonStatistic(df, s))

    info = [dfs[0][STATISTICS].describe().round(4).drop("count").to_dict(),
            dfs[1][STATISTICS].describe().round(4).drop("count").to_dict()]
    
    radar_plot = ad.createRadarPlot(df)

    return render_template('playlists_comparison_post.html',
                           playlists_info = playlists_meta,
                           statistics_data = statistics_data,
                           radar = radar_plot,
                           info = info)