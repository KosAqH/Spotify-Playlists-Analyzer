import pandas as pd

class AudioData:
    def __init__(self):
        pass

    def mergeTracksData(self, df_metadata: pd.DataFrame, df_features: pd.DataFrame) -> pd.DataFrame:
        # new_df = df_metadata.merge(df_features, on="id")
        cols_to_use = df_features.columns.difference(df_metadata.columns) #avoiding duplicates
        new_df = df_metadata.merge(df_features[cols_to_use], 
                                   left_index=True, 
                                   right_index=True,
                                   )
        return new_df
    
    def GetTotalDuration(self, df: pd.DataFrame, unit = "second") -> float:
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