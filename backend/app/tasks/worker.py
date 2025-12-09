# backend/app/tasks/worker.py
import os, io, tarfile, uuid
import pandas as pd
from ..utils.logger import logger
from ..parsers import summary_parser, batvol_parser, battemp_parser
from ..analysis.cell_analysis import per_cell_stats, health_score_from_stats
from ..storage.parquet_store import ParquetStore
from ..config import settings

def process_tar_single(task_id, tar_path, pm=None):
    """
    Process one tar.gz file: parse summary, batVol, batTemp; compute per-cell stats; save CSVs; return summary info
    """
    if pm:
        pm.update(task_id, f"processing {os.path.basename(tar_path)}", 10)
    # find members by pattern by scanning tar
    with tarfile.open(tar_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        # simple selection heuristics
        summary_member = next((m for m in members if 'summary' in m.name.lower() and m.name.lower().endswith('.csv')), None)
        batvol_member = next((m for m in members if 'batvol' in m.name.lower() and m.name.lower().endswith('.csv')), None)
        battemp_member = next((m for m in members if 'battemp' in m.name.lower() and m.name.lower().endswith('.csv')), None)
        res = {}
        store = ParquetStore(task_id)
        # process batvol
        if batvol_member:
            f = tar.extractfile(batvol_member)
            stats_accum = {}
            # stream parse
            for chunk in batvol_parser.parse(f):
                stats = per_cell_stats(chunk, prefix='V')
                # merge incremental: simple approach - accumulate using DataFrame then final stats
                # for simplicity, append chunk to list (small chunks) -> build full DF? For now we'll accumulate via pandas concat in memory per file.
                # But to keep memory small, here we compute chunk-level stats and merge numerically (omitted for brevity).
                # Simpler approach: collect per-column accumulators is best; due to brevity we create DataFrame at end as demo.
                if 'batvol_df_chunks' not in res:
                    res['batvol_df_chunks'] = []
                res['batvol_df_chunks'].append(chunk)
            if 'batvol_df_chunks' in res:
                full = pd.concat(res['batvol_df_chunks'], ignore_index=True)
                stats_full = per_cell_stats(full, prefix='V')
                # health scores
                scores = health_score_from_stats(stats_full)
                # write CSVs
                df_stats = pd.DataFrame.from_dict(stats_full, orient='index').reset_index().rename(columns={'index':'column'})
                df_scores = pd.DataFrame([{"cell":k,"score":v} for k,v in scores.items()])
                store.save_summary_csv(os.path.basename(tar_path).replace('.tar.gz','') + "_batvol_stats", df_stats)
                store.save_summary_csv(os.path.basename(tar_path).replace('.tar.gz','') + "_batvol_health", df_scores)
                res['batvol_stats'] = df_stats.to_dict(orient='records')[:5]
        # process battemp
        if battemp_member:
            f = tar.extractfile(battemp_member)
            for chunk in battemp_parser.parse(f):
                if 'battemp_chunks' not in res:
                    res['battemp_chunks'] = []
                res['battemp_chunks'].append(chunk)
            if 'battemp_chunks' in res:
                fullt = pd.concat(res['battemp_chunks'], ignore_index=True)
                tcols = [c for c in fullt.columns if c.startswith('T')]
                tstats = {}
                for c in tcols:
                    arr = pd.to_numeric(fullt[c], errors='coerce')
                    tstats[c] = {'mean': float(arr.mean()) if arr.count()>0 else None, 'std': float(arr.std()) if arr.count()>1 else None}
                df_t = pd.DataFrame.from_dict(tstats, orient='index').reset_index().rename(columns={'index':'sensor'})
                store.save_summary_csv(os.path.basename(tar_path).replace('.tar.gz','') + "_battemp_stats", df_t)
                res['battemp_stats'] = df_t.to_dict(orient='records')[:5]
        # summary file reading
        if summary_member:
            f = tar.extractfile(summary_member)
            for chunk in summary_parser.parse(f):
                if 'summary_chunks' not in res:
                    res['summary_chunks'] = []
                res['summary_chunks'].append(chunk)
            if 'summary_chunks' in res:
                big = pd.concat(res['summary_chunks'], ignore_index=True)
                # compute some simple overview stats
                overview = {}
                if 'totalVol' in big.columns:
                    overview['vol_mean'] = float(pd.to_numeric(big['totalVol'], errors='coerce').mean())
                store.save_summary_csv(os.path.basename(tar_path).replace('.tar.gz','') + "_summary_head", big.head(5))
                res['summary_head'] = big.head(3).to_dict(orient='records')
        if pm:
            pm.update(task_id, f"finished {os.path.basename(tar_path)}", 90)
    return res
