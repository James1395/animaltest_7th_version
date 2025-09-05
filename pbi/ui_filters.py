from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st
from pbi.geo_regions import get_region_center


def species_selector() -> str:
    """物種選択。表示・内部値ともに日本語（「熊」「鹿」「猪」）。"""
    return st.sidebar.selectbox("種別 / Species", options=["熊", "鹿", "猪"], index=0)


def is_species_present(prefecture: str, hokkaido_part: Optional[str], species_jp: str) -> bool:
    """地域×物種の生息可否（外部 JSON があれば優先）。"""
    override = Path("data/presence.json")
    if override.exists():
        data = json.loads(override.read_text(encoding="utf-8"))
        key = prefecture if (prefecture != "北海道" or not hokkaido_part) else f"北海道|{hokkaido_part}"
        return bool(data.get(key, {}).get(species_jp, True))
    return True


def get_pref_bbox(prefecture: str, hokkaido_part: Optional[str]) -> Tuple[float, float, float, float]:
    """対象地域の概略 BBox（WGS84度：min_lon, min_lat, max_lon, max_lat）。"""
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
    """予測水平（1..30 に丸め）。"""
    return max(1, min(30, int(days)))


def normalize_time_of_day(value: str) -> str:
    """"午前"/"午後" の二値に正規化。"""
    return "午前" if value in ("午前", "AM", "am", "morning") else "午後"
