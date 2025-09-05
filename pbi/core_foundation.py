from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

import streamlit as st


def render_frame(title: str = "獣害BIツール"):
    """
    アプリケーションのフレーム（コンテナ）を描画する関数。

    この関数は Streamlit のタイトルを設定し、コンテナを返します。

    引数:
        title (str): 画面上部に表示するタイトル。デフォルトは "獣害BIツール"。

    戻り値:
        Streamlit のコンテナオブジェクト。

    例外:
        Streamlit の内部処理や描画時に例外が発生する可能性があります。

    使用例:
        >>> render_frame("タイトル")

    注意:
        外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        パフォーマンスや副作用（IO等）に注意してください。
    """
    st.title(title)
    return st.container()


def _today_jst():
    """
    現在日時（日本標準時）を取得する関数。

    この関数はタイムゾーン付きの現在日時を返します。

    引数:
        なし

    戻り値:
        datetime: 日本標準時（JST）の現在日時。

    例外:
        datetime モジュールの内部例外が発生する可能性があります。

    使用例:
        >>> _today_jst()

    注意:
        システム時刻やタイムゾーン設定に依存します。
    """
    return datetime.now(timezone(timedelta(hours=9)))


def list_base_dates(max_items: int = 3) -> List[str]:
    """
    基準日から過去数日分の日付リストを返す関数。

    この関数は今日（JST）から `max_items` 日分のYYYY-MM-DD形式の日付文字列リストを返します。

    引数:
        max_items (int): 取得する日付の数。デフォルトは3。

    戻り値:
        List[str]: 日付文字列（YYYY-MM-DD）のリスト。

    例外:
        引数が不正な場合や日付計算時に例外が発生する可能性があります。

    使用例:
        >>> list_base_dates(3)

    注意:
        システム時刻やタイムゾーン設定に依存します。
        引数の型と値域を事前に検証してください。
    """
    base = _today_jst().date()
    days = [0, 1, 2][: max(1, int(max_items))]
    return [(base - timedelta(days=i)).strftime("%Y-%m-%d") for i in days]


def color_scale_blue_purple():
    """
    青から紫へのカラースケールを返す関数。

    この関数はグラデーション用のカラースケールリストを返します。

    引数:
        なし

    戻り値:
        List[List[float, str]]: カラースケールのリスト。

    例外:
        なし

    使用例:
        >>> color_scale_blue_purple()

    注意:
        カラースケールの値や形式は用途に応じて調整してください。
    """
    return [
        [0.00, "rgba(0, 0, 0, 0.0)"],
        [0.01, "rgba(0, 102, 255, 0.35)"],
        [0.25, "rgba(0, 92, 230, 0.55)"],
        [0.50, "rgba(0, 72, 200, 0.75)"],
        [0.75, "rgba(80, 40, 200, 0.9)"],
        [1.00, "rgba(128, 0, 200, 1.0)"],
    ]
