from __future__ import annotations

from typing import List, Optional, Tuple

import streamlit as st
from utils.geo import get_region_center as _get_center_impl


PREFS: List[str] = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県",
]


def prefecture_selector() -> str:
    """都道府県の選択 UI を表示し、選択結果を返す。既定は「東京都」。"""
    default_index = PREFS.index("東京都")
    return st.sidebar.selectbox("都道府県 / Prefecture", options=PREFS, index=default_index)


def hokkaido_split_selector(prefecture: str) -> Optional[str]:
    """北海道選択時のみ分区を選択。その他は None。"""
    if prefecture != "北海道":
        return None
    return st.sidebar.selectbox("北海道の分区", ["道南", "道央", "道北", "道東"], index=1)


def get_region_center(prefecture: str, hokkaido_area: Optional[str]) -> Tuple[float, float]:
    """地域の地図中心座標（緯度, 経度）を返す。"""
    return _get_center_impl(prefecture, hokkaido_area)
