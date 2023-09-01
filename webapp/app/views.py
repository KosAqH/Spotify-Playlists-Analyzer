from . import app
from flask import render_template, redirect, request
from app.forms import SpotifyURL, SpotifyDoubleURL
import plotly.express as px
import plotly
import plotly.figure_factory as ff
import plotly.graph_objects as go
import json
import pandas as pd
import re

from .spotify_api.spotify_connection import SpotifyConn
from .spotify_api.spotify_api import SpotifyApi
from .spotify_api.spotify_utils import load_credentials, load_playlist_info
from .spotify_api.audio_data import AudioData

@app.route("/")
def index():
    spotify_url = SpotifyURL()
    spotify_double_url = SpotifyDoubleURL()

    return render_template('index.html', 
                           url_form_analysis = spotify_url, 
                           url_form_comparison = spotify_double_url)

@app.route("/index_post", methods=["POST"])
def index_post():

    if request.form.get('url'):
        url = request.form.get('url')
        id = extractIdFromURL(url)
        if not id:
            id = url

    token = get_spotify_access_token()
    api = SpotifyApi(token)

    # p = api.RequestPlaylist(id)
    playlist_meta = api.retrievePlaylistMetadata(id)

    ids = api.retrieveIdsFromPlaylist(id, playlist_meta["total_count"])
    tracks_info = load_playlist_info(api, ids)

    ad = AudioData()
    playlist_meta["total_minutes"] = round(ad.GetTotalDuration(tracks_info, unit="min"))
    playlist_meta["hours"] = playlist_meta["total_minutes"] // 60
    playlist_meta["minutes"] = playlist_meta["total_minutes"] % 60
    playlist_meta["top_artist"] = getTop(tracks_info, "artist_id", 3, api)
    playlist_meta["top_album"] = getTop(tracks_info, "album_id", 3, api)
    playlist_meta["top_genre"] = "placeholder"
    playlist_meta["total_count"] = tracks_info.shape[0]

    statistics = ["duration_s", "tempo", "acousticness", "danceability", "energy", "instrumentalness", "loudness", "valence"]

    info = tracks_info[statistics].describe().round(4).drop("count").to_dict()

    statistics_data = []
    for s in statistics:
        statistics_data.append(getSpotifyStatistic(tracks_info, s))
    
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

    token = get_spotify_access_token()
    api = SpotifyApi(token)

    if request.form.get('url1') and request.form.get('url2'):
        urls += [request.form.get('url1'), request.form.get('url2')]

    for url in urls:
        id = extractIdFromURL(url)
        if not id:
            id = url
        # p = api.RequestPlaylist(id)
        playlist_meta = api.retrievePlaylistMetadata(id)
        

        ids = api.retrieveIdsFromPlaylist(id, playlist_meta["total_count"])
        tracks_info = load_playlist_info(api, ids)
        dfs.append(tracks_info)

        ad = AudioData()
        playlist_meta["total_minutes"] = round(ad.GetTotalDuration(tracks_info, unit="min"))
        playlist_meta["hours"] = playlist_meta["total_minutes"] // 60
        playlist_meta["minutes"] = playlist_meta["total_minutes"] % 60
        playlist_meta["top_artist"] = getTop(tracks_info, "artist_id", 3, api)
        playlist_meta["top_album"] = getTop(tracks_info, "album_id", 3, api)
        playlist_meta["top_genre"] = "placeholder"
        playlist_meta["total_count"] = tracks_info.shape[0]

        playlists_meta.append(playlist_meta)

    statistics = ["duration_s", "tempo", "acousticness", "danceability", "energy", "instrumentalness", "loudness", "valence"]

    dfs[0]["no"] = 1
    dfs[1]["no"] = 2

    df = pd.concat([dfs[0], dfs[1]], axis=0)

    statistics_data = []
    for s in statistics:
        statistics_data.append(getSpotifyComparisonStatistic(df, s))

    info = [dfs[0][statistics].describe().round(4).drop("count").to_dict(),
            dfs[1][statistics].describe().round(4).drop("count").to_dict()]
    
    radar_plot = createRadarPlot(df)

    print(playlists_meta[1])
    return render_template('playlists_comparison_post.html',
                           playlists_info = playlists_meta,
                           statistics_data = statistics_data,
                           radar = radar_plot,
                           info = info)


##### MOVE IT TO OTHER FILE LATER

def createRadarPlot(df):
    columns = ["acousticness", "danceability", "energy", "instrumentalness", "valence"]
    means1 = [df[df["no"]==1][col].mean() for col in columns]
    # for col in columns:
    #     means1.append(df[df["no"]==0][col].mean())
    means2 = [df[df["no"]==2][col].mean() for col in columns]
    # for col in columns:
    #     means2.append(df[df["no"]==0][col].mean())

    new_df = pd.DataFrame(columns=["means", "playlist"], index=columns*2)
    new_df["means"] = means1+means2
    new_df["playlist"] = [0,0,0,0,0,1,1,1,1,1]
    new_df["playlist"].replace({0:"Playlist left", 1:"Playlist right" }, inplace=True)

    fig = px.line_polar(new_df, r="means", theta = new_df.index, color="playlist", 
                        color_discrete_sequence = ["Red", "Blue"],
                        labels= ["Playlist left", "Playlist right"],
                        line_close=True, markers=True)
    fig.update_traces(fill='toself')

    figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return figJSON


def getSpotifyStatistic(df, stat_name):

    top_artists, top_titles, top_vals = getTopNumerical(df, stat_name, 3)
    bot_artists, bot_titles, bot_vals = getTopNumerical(df, stat_name, 3, get_bottom=True)

    fig = px.histogram(df, x=stat_name, nbins=10, marginal="violin")
    figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    stats_description = {}
    with open(".\\data\\descriptions.json") as f:
        stats_description = dict(json.load(f))
    d={
        "name": stat_name,
        "desc": stats_description[stat_name],
        "top_artists": top_artists,
        "top_values": top_vals,
        "top_titles": top_titles,
        "bot_artists": bot_artists,
        "bot_values": bot_vals,
        "bot_titles": bot_titles,
        "plot": figJSON
    }
    return d

def getSpotifyComparisonStatistic(df: pd.DataFrame, stat_name):
    df1 = df[df["no"] == 1].drop_duplicates('id')
    df2 = df[df["no"] == 2].drop_duplicates('id')

    l1 = df1[stat_name].to_list()
    l2 = df2[stat_name].to_list()
    ar1 = df1["artist_name"].to_list()
    ar2 = df2["artist_name"].to_list()
    t1 = df1["name"].to_list()
    t2 = df2["name"].to_list()
    r1 = []
    r2 = []

    for i in range(len(ar1)):
        r1.append(f"{t1[i]} by {ar1[i]}")
    for i in range(len(ar2)):
        r2.append(f"{t2[i]} by {ar2[i]}")

    top_val = df[stat_name].max()
    bot_val = df[stat_name].min()

    fig = ff.create_distplot([l1, l2],
                             ["Playlist left", "Playlist right"],
                             bin_size=((top_val-bot_val) / 10),
                             rug_text  = [r1, r2],
                             colors = ["Red", "Blue"] 
        )
    fig.update_layout(legend = dict(traceorder = "normal"))
    figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    stats_description = {}
    with open(".\\data\\descriptions.json") as f:
        stats_description = dict(json.load(f))

    top_artists = []
    top_vals = []
    top_titles = []
    bot_artists = []
    bot_vals = []
    bot_titles = []



    for df in [df1, df2]:
        top_ar, top_ti, top_va = getTopNumerical(df, stat_name, 3)
        bot_ar, bot_ti, bot_va = getTopNumerical(df, stat_name, 3, get_bottom=True)

        top_artists.append(top_ar)
        top_vals.append(top_va)
        top_titles.append(top_ti)
        bot_artists.append(bot_ar)
        bot_vals.append(bot_va)
        bot_titles.append(bot_ti)

    d={
        "name": stat_name,
        "desc": stats_description[stat_name],
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
    # if max_value == 1:
    #     return {}
    
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
