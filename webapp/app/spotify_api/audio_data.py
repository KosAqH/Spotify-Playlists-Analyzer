import pandas as pd

class AudioData:
    def __init__(self):
        pass

    def mergeTracksData(self, df_metadata: pd.DataFrame, df_features: pd.DataFrame) -> pd.DataFrame:
        new_df = df_metadata.merge(df_features, on="id")
        return new_df
    
    def GetTotalDuration(self, df: pd.DataFrame, unit = "second") -> float:
        duration = df["duration_ms_x"].sum() 

        if unit == "second" or unit == "s":
            return duration / 1000
        elif unit == "milisecond" or unit == "ms":
            return duration
        elif unit == "minute" or unit == "min":
            return duration / 60000
        elif unit == "hour" or unit == "h":
            return duration / 3600000
        
        raise ValueError("Wrong unit name!")