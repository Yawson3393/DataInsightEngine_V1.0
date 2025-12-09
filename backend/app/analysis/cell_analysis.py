# backend/app/analysis/cell_analysis.py
import numpy as np
import pandas as pd

def per_cell_stats(df, prefix='V'):
    """
    df: DataFrame containing V1..Vn columns (numeric)
    returns dict col -> stats
    """
    vcols = [c for c in df.columns if c.startswith(prefix)]
    out = {}
    for c in vcols:
        arr = pd.to_numeric(df[c], errors='coerce')
        out[c] = {
            'count': int(arr.count()),
            'nan': int(arr.isna().sum()),
            'mean': float(arr.mean()) if arr.count()>0 else None,
            'std': float(arr.std()) if arr.count()>1 else None,
            'min': float(arr.min()) if arr.count()>0 else None,
            'max': float(arr.max()) if arr.count()>0 else None
        }
    return out

def health_score_from_stats(stats_dict):
    """
    Given per-cell stats dict, compute simple health score:
    normalized deviation of mean from median + normalized std.
    Higher score -> worse.
    """
    import numpy as np
    cells = list(stats_dict.keys())
    means = np.array([stats_dict[c]['mean'] if stats_dict[c]['mean'] is not None else np.nan for c in cells])
    stds = np.array([stats_dict[c]['std'] if stats_dict[c]['std'] is not None else np.nan for c in cells])
    # robust normalization
    m_med = np.nanmedian(means); m_mad = np.nanmedian(np.abs(means - m_med)) or 1.0
    s_med = np.nanmedian(stds); s_mad = np.nanmedian(np.abs(stds - s_med)) or 1.0
    z_mean = (means - m_med) / m_mad
    z_std = (stds - s_med) / s_mad
    score = np.nan_to_num(z_mean) + np.nan_to_num(z_std)
    return dict(zip(cells, score.tolist()))
