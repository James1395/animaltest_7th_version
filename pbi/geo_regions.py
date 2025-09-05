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
    """
    都道府県を選択するためのセレクタをサイドバーに表示する関数。

    Streamlit のサイドバーに都道府県の選択ボックスを表示し、選択された都道府県名を返します。

    引数:
        なし

    戻り値:
        str: 選択された都道府県名。

    例外:
        Streamlit の内部処理や描画時に例外が発生する可能性があります。

    使用例:
        >>> prefecture_selector()

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    default_index = PREFS.index("東京都")
    return st.sidebar.selectbox("都道府県 / Prefecture", options=PREFS, index=default_index)


def hokkaido_split_selector(prefecture: str) -> Optional[str]:
    """
    北海道の場合に分区（道南・道央・道北・道東）を選択するセレクタをサイドバーに表示する関数。

    引数:
        prefecture (str): 対象の都道府県名。

    戻り値:
        Optional[str]: 北海道の場合は選択された分区名、それ以外は None。

    例外:
        Streamlit の内部処理や描画時に例外が発生する可能性があります。

    使用例:
        >>> hokkaido_split_selector("北海道")

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    if prefecture != "北海道":
        return None
    return st.sidebar.selectbox("北海道の分区", ["道南", "道央", "道北", "道東"], index=1)


def get_region_center(prefecture: str, hokkaido_area: Optional[str]) -> Tuple[float, float]:
    """
    指定した都道府県および北海道分区の中心座標（緯度・経度）を取得する関数。

    引数:
        prefecture (str): 対象の都道府県名。
        hokkaido_area (Optional[str]): 北海道の場合の分区名（道南・道央・道北・道東）、それ以外は None。

    戻り値:
        Tuple[float, float]: 中心座標（緯度, 経度）。

    例外:
        内部で呼び出す実装（_get_center_impl）に依存し、例外が発生する可能性があります。

    使用例:
        >>> get_region_center("東京都", None)
        >>> get_region_center("北海道", "道央")

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    return _get_center_impl(prefecture, hokkaido_area)
