from __future__ import annotations

import numpy as np
import pandas as pd


def synth_probabilities(
    cells_df: pd.DataFrame,
    species: str,
    base_date: str,
    time_of_day: str,
    horizon_days: int,
    data_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """セルごとの出現確率を合成する関数.

    この関数は入力されたセル情報や条件（種名、基準日、時間帯、予測日数など）に基づき、乱数を用いて確率値を生成します。
    実際のデータやモデルには依存せず、主にデモやテスト用途で利用されます。

    引数:
        cells_df (pd.DataFrame): セル情報を含むDataFrame。'cell_id'または'id'列が必要です。
        species (str): 対象とする種名。
        base_date (str): 基準日（YYYY-MM-DD形式など）。
        time_of_day (str): 時間帯（例: "午前", "午後"）。
        horizon_days (int): 予測日数。
        data_df (Optional[pd.DataFrame]): 追加データ（未使用、デフォルトNone）。

    戻り値:
        pd.DataFrame: 'cell_id'列と'prob'列を持つDataFrame。

    例外:
        入力DataFrameに必要な列が存在しない場合や、乱数生成・型変換時に例外が発生する可能性があります。

    使用例:
        >>> synth_probabilities(cells_df, species, base_date, time_of_day, horizon_days)

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        引数の型と値域を事前に検証してください。
        パフォーマンスや副作用（乱数、時刻、IO）に注意してください。
    """
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
