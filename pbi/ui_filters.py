from __future__ import annotations

import json

try:
    from validation import validate_species_for_prefecture  # fallback
except Exception:
    validate_species_for_prefecture = None  # type: ignore

from pathlib import Path

import streamlit as st

from pbi.geo_regions import get_region_center


def species_selector() -> str:
    """種別（熊・鹿・猪）を選択するセレクタをサイドバーに表示する関数.

    Streamlit のサイドバーに種別の選択ボックスを表示し、選択された種名を返します。

    引数:
        なし

    戻り値:
        str: 選択された種名。

    例外:
        Streamlit の内部処理や描画時に例外が発生する可能性があります。

    使用例:
        >>> species_selector()

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    return st.sidebar.selectbox("種別 / Species", options=["熊", "鹿", "猪"], index=0)


def is_species_present(prefecture: str, hokkaido_part: str | None, species_jp: str) -> bool:
    """指定した地域・種別の生息情報が存在するか判定する関数.

    presence.json が存在する場合はその内容を参照し、なければ常に True を返します。

    引数:
        prefecture (str): 対象の都道府県名。
        hokkaido_part (Optional[str]): 北海道の場合の分区名（道南・道央・道北・道東）、それ以外は None。
        species_jp (str): 対象の種名。

    戻り値:
        bool: 生息情報が存在する場合は True、存在しない場合は False。

    例外:
        ファイルIOやJSONパース時に例外が発生する可能性があります。

    使用例:
        >>> is_species_present(prefecture, hokkaido_part, species_jp)

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    override = Path("data/presence.json")
    if override.exists():
        data = json.loads(override.read_text(encoding="utf-8"))
        key = prefecture if (prefecture != "北海道" or not hokkaido_part) else f"北海道|{hokkaido_part}"
        return bool(data.get(key, {}).get(species_jp, True))
    return True


def get_pref_bbox(prefecture: str, hokkaido_part: str | None) -> tuple[float, float, float, float]:
    """指定した都道府県・北海道分区のバウンディングボックス（経度緯度）を取得する関数.

    bboxes.json が存在する場合はその内容を参照し、なければ中心座標±0.8度の範囲を返します。

    引数:
        prefecture (str): 対象の都道府県名。
        hokkaido_part (Optional[str]): 北海道の場合の分区名（道南・道央・道北・道東）、それ以外は None。

    戻り値:
        Tuple[float, float, float, float]: (min_lon, min_lat, max_lon, max_lat)

    例外:
        ファイルIOやJSONパース時に例外が発生する可能性があります。

    使用例:
        >>> get_pref_bbox(prefecture, hokkaido_part)

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    override = Path("data/pref_bboxes.json")
    if override.exists():
        data = json.loads(override.read_text(encoding="utf-8"))
        key = prefecture if (prefecture != "北海道" or not hokkaido_part) else f"北海道|{hokkaido_part}"
        v = data.get(key)
        if v and len(v) == 4:
            return float(v[0]), float(v[1]), float(v[2]), float(v[3])
    lat, lon = get_region_center(prefecture, hokkaido_part)
    return (lon - 0.8, lat - 0.8, lon + 0.8, lat + 0.8)


def clamp_horizon(days: int) -> int:
    """予測日数を1〜30の範囲に制限する関数.

    引数:
        days (int): 入力された予測日数。

    戻り値:
        int: 1〜30の範囲に制限された予測日数。

    例外:
        型変換や比較時に例外が発生する可能性があります。

    使用例:
        >>> clamp_horizon(days)

    注意:
        引数の型と値域を事前に検証してください。
    """
    return max(1, min(30, int(days)))


def normalize_time_of_day(value: str) -> str:
    """時間帯の値を「午前」または「午後」に正規化する関数.

    引数:
        value (str): 入力された時間帯（例: "午前", "AM", "morning", "午後" など）。

    戻り値:
        str: "午前" または "午後"。

    例外:
        型変換や比較時に例外が発生する可能性があります。

    使用例:
        >>> normalize_time_of_day(value)

    注意:
        引数の型と値域を事前に検証してください。
    """
    return "午前" if value in ("午前", "AM", "am", "morning") else "午後"
