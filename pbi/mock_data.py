from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def synth_probabilities(
    cells_df: pd.DataFrame,
    species: str,
    base_date: str,
    time_of_day: str,
    horizon_days: int,
    data_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """セル ID ごとの確率を 0..1 で生成する（決定性乱数）。"""
    n = len(cells_df)
    seed = abs(hash((species, base_date, time_of_day, int(horizon_days)))) % (2**32)
    rng = np.random.default_rng(seed)
    prob = rng.random(n) ** 2

    out = pd.DataFrame()
    if "cell_id" in cells_df.columns:
        out["cell_id"] = cells_df["cell_id"].astype(int).values
    elif "id" in cells_df.columns:
        out["cell_id"] = cells_df["id"].astype(int).values
    else:
        out["cell_id"] = np.arange(n, dtype=int)
    out["prob"] = prob
    return out
