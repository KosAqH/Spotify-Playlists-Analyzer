import pandas as pd

class AudioData:
    """
    Class containing some utilities function to transform data requested with API.
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