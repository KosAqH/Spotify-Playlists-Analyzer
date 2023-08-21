import pandas as pd

class AudioData:
    def __init__(self):
        pass

    def mergeTracksData(df_metadata: pd.DataFrame, df_features: pd.DataFrame) -> pd.DataFrame:
        new_df = df_metadata.merge(df_features, on="id")
        return new_df