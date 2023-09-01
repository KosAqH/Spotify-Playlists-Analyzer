import pandas as pd
import json

import plotly
import plotly.express as px
import plotly.figure_factory as ff

from .spotify_api import SpotifyApi

class AudioData:
    """
    Class grouping some utilities function to transform data requested with API.
    """
    def __init__(self):
        """
        Constructor of class do nothing
        """
        pass

    def mergeTracksData(self, df_metadata: pd.DataFrame, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Function merges dataframes with metadata and features.

            Args:
                df_metadata (pd.DataFrame) - 
                df_features (pd.DataFrame) -

            Returns:
                new_df (pd.DataFrame) - 
        """
        cols_to_use = df_features.columns.difference(df_metadata.columns) #avoiding duplicates
        new_df = df_metadata.merge(df_features[cols_to_use], 
                                   left_index=True, 
                                   right_index=True,
                                   )
        new_df["duration_s"] = new_df["duration_ms"] / 1000
        return new_df
    
    def GetTotalDuration(self, df: pd.DataFrame, unit = "second") -> float:
        """
        Function calculates total duration of playlist and converts it to chosen unit.

            Args:
                df (pd.DataFrame) - dataframe containing data regarding tracks. It has to have
                    'duration_ms' column.
                unit (str) - one of the values: 'second', 's', 'milisecond', 'ms', 'minute', 'min'
                    'hour', 'h'

            Returns:
                duration (float) - total duration of playlist in chosen unit  
        """
        duration = df["duration_ms"].sum() 

        if unit == "second" or unit == "s":
            return duration / 1000
        elif unit == "milisecond" or unit == "ms":
            return duration
        elif unit == "minute" or unit == "min":
            return duration / 60000
        elif unit == "hour" or unit == "h":
            return duration / 3600000
        
        raise ValueError("Wrong unit name!")
    
    def createRadarPlot(self, df: pd.DataFrame) -> str:
        """
        Function creates line polar plot of means of audio features. 

            Args:
                df (pd.DataFrame) - df containing audio features and column 'no', that makes 
                    possible to distinguish between playlists

            Returns:
                figJSON (str) - string containing plotly js script that renders plot on page 
        """
        columns = ["acousticness", "danceability", "energy", "instrumentalness", "valence"]
        means1 = [df[df["no"]==1][col].mean() for col in columns]
        means2 = [df[df["no"]==2][col].mean() for col in columns]

        new_df = pd.DataFrame(columns=["means", "playlist"], index=columns*2)
        new_df["means"] = means1+means2
        new_df["playlist"] = [0,0,0,0,0,1,1,1,1,1]
        new_df["playlist"].replace({0:"Playlist left", 1:"Playlist right" }, inplace=True)

        fig = px.line_polar(new_df, r="means", theta = new_df.index, color="playlist", 
                            color_discrete_sequence = ["Red", "Blue"],
                            line_close=True, markers=True)
        fig.update_traces(fill='toself')

        figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return figJSON


    def getSpotifyStatistic(self, df: pd.DataFrame, stat_name:str):
        """
        Function prepares dictionary with statistics on one chosen audio feature.

            Args:
                df (pd.DataFrame) - dataframe contains track's features
                stat_name (str) - name of feature

            Returns:
                d (dict) - containing statistics and plot of given audio feature
        """
        top_artists, top_titles, top_vals = self.getTopNumerical(df, stat_name, 3)
        bot_artists, bot_titles, bot_vals = self.getTopNumerical(df, stat_name, 3, get_bottom=True)

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

    def getSpotifyComparisonStatistic(self, df: pd.DataFrame, stat_name: str) -> list[dict]:
        """
        Function prepares dictionary with statistics on one chosen audio feature for two
            playlists.

            Args:
                df (pd.DataFrame) - dataframe contains track's features
                stat_name (str) - name of feature

            Returns:
                d (dict) - containing statistics and plot of given audio feature for two playlists
        """
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
            top_ar, top_ti, top_va = self.getTopNumerical(df, stat_name, 3)
            bot_ar, bot_ti, bot_va = self.getTopNumerical(df, stat_name, 3, get_bottom=True)

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

    def getTopNumerical(self, 
                        df: pd.DataFrame, 
                        column: str, 
                        topn: int, 
                        add_exaquo: bool = False, 
                        get_bottom: bool = False) -> [list, list, list]:
        """
        Function returns top n biggest or lowest values of one of track's audio feature.
            Also artist and title of track is returned.

            Args:
                df (pd.DataFrame) - df containing data describing tracks
                column (str) - name of audio feature
                topn (int) - number of values to return
                get_bottom (bool) - if true, then returns lowest instead of biggest values

            Returns:
                artists (list[str]) - authors of top tracks
                titles (list[str]) - titles of top tracks
                values (list[str]) - values of chosen feature
        """

        extracted_data = df.sort_values(by=column, ascending = get_bottom).head(topn)[["name", "artist_name", column]]
        values = extracted_data[column].to_list()
        artists = extracted_data["artist_name"].to_list()
        titles = extracted_data["name"].to_list()

        if add_exaquo: # not in use by now
            pass
            # s = df[column].value_counts()[(df[column].value_counts() == values[-1]) & (~df[column].value_counts().index.isin(keys))]
            # values += (list(s.values))
            # keys += (list(s.index))

        return artists, titles, values


    def getTop(self, 
               df: pd.DataFrame, 
               column: str, 
               topn: int, 
               api: SpotifyApi, 
               add_exaquo: bool = False) -> list[dict]:
        """
        Function returns top n values that occur most common in data.

            Args:
                df (pd.DataFrame) - df containing data describing tracks
                column (str) - name of feature to count
                topn (int) - number of values to return
                api (SpotifyApi object) - initialized spotify api object

            Returns:
                top_items (list[dict]) - list with dicts. Each dict contains info
                    about one of most common items.
        """
        
        keys = list(df[column].value_counts().head(topn).index)
        values = list(df[column].value_counts().head(topn).values)
        top_items = []

        if column == "artist_id":
            retrieving_func = api.retrieveArtistMetadata
        elif column == "album_id":
            retrieving_func = api.retrieveAlbumMetadata
        else:
            raise ValueError("Wrong column value!")
        
        top_items = retrieving_func(keys)
        for i, _ in enumerate(keys):
            top_items[i]["count"] = values[i]

        if add_exaquo: # not in use by now
            pass
            # s = df[column].value_counts()[(df[column].value_counts() == values[-1]) & (~df[column].value_counts().index.isin(keys))]
            # values += (list(s.values))
            # keys += (list(s.index))

        return top_items