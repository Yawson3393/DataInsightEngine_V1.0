# backend/app/aligner/timeline_aligner.py
import pandas as pd
import numpy as np

def align_to_grid(df, time_col='time', freq='5S', method='linear'):
    """
    Align DataFrame to regular time grid at freq (e.g. '5S').
    Returns reindexed DataFrame with time index.
    """
    if time_col not in df.columns:
        raise ValueError("time_col not found")
    df = df.dropna(subset=[time_col]).set_index(time_col)
    df = df[~df.index.duplicated(keep='first')]
    start = df.index.min()
    end = df.index.max()
    new_idx = pd.date_range(start, end, freq=freq)
    df2 = df.reindex(new_idx)
    # interpolate numeric columns
    numeric = df2.select_dtypes(include=[np.number]).columns
    if method == 'linear' and len(numeric)>0:
        df2[numeric] = df2[numeric].interpolate(method='time', limit_direction='both')
    return df2.reset_index().rename(columns={'index': time_col})
