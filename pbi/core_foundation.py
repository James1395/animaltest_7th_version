from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

import streamlit as st


def render_frame(title: str = "獣害BIツール"):
    """ページタイトルを表示し、その後の UI を配置するコンテナを返す。"""
    st.title(title)
    return st.container()


def _today_jst():
    """JST(+09:00) の現在日時を返す。"""
    return datetime.now(timezone(timedelta(hours=9)))


def list_base_dates(max_items: int = 3) -> List[str]:
    """基準日として「今日／昨日／一昨日」の 3 日を返す（JST）。"""
    base = _today_jst().date()
    days = [0, 1, 2][: max(1, int(max_items))]
    return [(base - timedelta(days=i)).strftime("%Y-%m-%d") for i in days]


def color_scale_blue_purple():
    """透明度 0 を含む青→紫のカラースケールを返す。"""
    return [
        [0.00, "rgba(0, 0, 0, 0.0)"],
        [0.01, "rgba(0, 102, 255, 0.35)"],
        [0.25, "rgba(0, 92, 230, 0.55)"],
        [0.50, "rgba(0, 72, 200, 0.75)"],
        [0.75, "rgba(80, 40, 200, 0.9)"],
        [1.00, "rgba(128, 0, 200, 1.0)"],
    ]
