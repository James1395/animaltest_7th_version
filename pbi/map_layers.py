from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pyproj import CRS, Transformer

"""地図レイヤ（UTM で 1km メッシュ生成 → WGS84 に戻して Choropleth 描画）."""

@st.cache_resource(show_spinner=False)
def japan_basemap():
    """日本全体のベースマップを返す関数.

    この関数は日本の中心付近を表示する Plotly の Mapbox 図を返します。
    実データに依存せず、初期表示やフォールバック用途で使用されます。

    引数:
        なし

    戻り値:
        plotly.graph_objs._figure.Figure: 日本地図のベースマップ。

    例外:
        Plotly や pandas の内部処理で例外が発生する可能性があります。

    使用例:
        >>> fig = japan_basemap()
        >>> # Streamlit での描画例: st.plotly_chart(fig, use_container_width=True)

    注意:
        - 外部状態（ファイル、環境変数、グローバル設定）に依存する場合があります。
        - 表示スタイルは "carto-positron" 固定です。必要に応じて Mapbox のトークン設定が必要です。
    """
    df = pd.DataFrame(dict(lat=[36.2048], lon=[138.2529]))
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=4, height=540)
    fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
    return fig


# ---------- 内部：座標変換 & メッシュ生成 ----------


def _utm_crs_for_lon(lon: float) -> CRS:
    """経度から対応するUTM座標系（CRS）を返す関数.

    引数:
        lon (float): 経度（度）。

    戻り値:
        pyproj.CRS: 対応するUTM座標系。

    例外:
        CRS 生成時に pyproj の例外が発生する可能性があります。

    使用例:
        >>> _utm_crs_for_lon(139.7)

    注意:
        - 経度の値域（-180〜180）を想定しています。
        - 日本域は一般に 51〜54帯に該当します。
    """
    zone = int(np.floor((lon + 180) / 6) + 1)
    return CRS.from_epsg(32600 + zone)


def _make_transformers_for_bbox(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> tuple[Transformer, Transformer]:
    """指定したバウンディングボックスに基づき、WGS84<->UTM の変換器を返す関数.

    引数:
        min_lon (float): 最小経度（度）。
        min_lat (float): 最小緯度（度）。
        max_lon (float): 最大経度（度）。
        max_lat (float): 最大緯度（度）。

    戻り値:
        Tuple[Transformer, Transformer]: (WGS84→UTM, UTM→WGS84) の変換器。

    例外:
        pyproj の内部処理で例外が発生する可能性があります。

    使用例:
        >>> to_m, to_deg = _make_transformers_for_bbox(139.6, 35.6, 139.8, 35.8)

    注意:
        - 入力 bbox の中心経度から UTM 帯を推定します。
        - always_xy=True により (lon, lat) 順での変換を保証します。
    """
    lon_center = (min_lon + max_lon) / 2.0
    utm = _utm_crs_for_lon(lon_center)
    wgs84 = CRS.from_epsg(4326)
    to_m = Transformer.from_crs(wgs84, utm, always_xy=True)
    to_deg = Transformer.from_crs(utm, wgs84, always_xy=True)
    return to_m, to_deg


def _iter_cells(bounds_m: tuple[float, float, float, float], cell_size_m: float) -> Iterable[tuple[int, int, list]]:
    """指定した範囲とセルサイズでメッシュセルを生成するイテレータ.

    引数:
        bounds_m (Tuple[float, float, float, float]): (min_x, min_y, max_x, max_y) のメートル単位バウンディングボックス。
        cell_size_m (float): セル1辺の長さ（メートル）。

    戻り値:
        Iterable[Tuple[int, int, list]]: (列, 行, ポリゴン座標リスト) のタプルを返すイテレータ。

    例外:
        numpy の arange などで例外が発生する可能性があります。

    使用例:
        >>> for c, r, poly in _iter_cells((0, 0, 2000, 2000), 1000): ...
        ...     pass

    注意:
        - 右上端は半開区間として扱われるため、最大値ちょうどは含みません。
        - 生成されるポリゴンは (x, y) の時計回り座標列です。
    """
    min_x, min_y, max_x, max_y = bounds_m
    xs = np.arange(min_x, max_x, cell_size_m)
    ys = np.arange(min_y, max_y, cell_size_m)
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            poly = [(x, y), (x + cell_size_m, y), (x + cell_size_m, y + cell_size_m), (x, y + cell_size_m), (x, y)]
            yield c, r, poly


# ---------- 公開 API ----------


@st.cache_data(show_spinner=False)
def make_mesh_for_bbox(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    km_step: float = 1.0,
    padding_km: float = 0.0,
):
    """指定したバウンディングボックス内に 1km メッシュを生成する関数.

    引数:
        min_lon (float): 最小経度（度）。
        min_lat (float): 最小緯度（度）。
        max_lon (float): 最大経度（度）。
        max_lat (float): 最大緯度（度）。
        km_step (float): メッシュ1辺の長さ（km 単位、デフォルト 1.0）。
        padding_km (float): 外側パディング（km 単位、デフォルト 0.0）。

    戻り値:
        Tuple[dict, pd.DataFrame]: GeoJSON 形式のメッシュと中心点情報の DataFrame。
            - GeoJSON: FeatureCollection（各 Feature は "properties.id" を持つ）
            - DataFrame: 列 {id, cell_id, lat, lon}

    例外:
        座標変換や DataFrame 生成時に例外が発生する可能性があります。

    使用例:
        >>> gj, centers = make_mesh_for_bbox(139.6, 35.6, 139.8, 35.8, 1.0, 0.0)

    注意:
        - UTM に変換後に格子生成し、WGS84 に戻します（距離の歪み低減）。
        - `km_step` と `padding_km` は 0 未満にならないようバリデーションしてください。
    """
    to_m, to_deg = _make_transformers_for_bbox(min_lon, min_lat, max_lon, max_lat)

    # BBox をメートルに
    x0, y0 = to_m.transform(min_lon, min_lat)
    x1, y1 = to_m.transform(max_lon, max_lat)
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0

    pad = float(padding_km) * 1000.0
    cell = max(0.1, float(km_step)) * 1000.0
    bounds = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)

    features = []
    rows = []
    fid = 0
    for c, r, poly_m in _iter_cells(bounds, cell):
        # 中心点（m）
        cx = (poly_m[0][0] + poly_m[2][0]) / 2.0
        cy = (poly_m[0][1] + poly_m[2][1]) / 2.0

        # ポリゴンと中心を WGS84 に戻す
        poly_lonlat = [to_deg.transform(px, py) for (px, py) in poly_m]
        cen_lon, cen_lat = to_deg.transform(cx, cy)

        features.append(
            {
                "type": "Feature",
                "id": fid,
                "properties": {"id": fid, "row": int(r), "col": int(c)},
                "geometry": {"type": "Polygon", "coordinates": [poly_lonlat]},
            }
        )
        rows.append({"id": fid, "cell_id": fid, "lat": float(cen_lat), "lon": float(cen_lon)})
        fid += 1

    gj = {"type": "FeatureCollection", "features": features}
    df = pd.DataFrame(rows)
    return gj, df


def plot_probability_heatmap(
    mesh_geojson: dict,
    probs_df: pd.DataFrame,
    center_lat: float,
    center_lon: float,
    colorscale,
    opacity: float = 1.0,
    grid_outline_width: float = 0.10,
    min_prob: float = 0.0,
    center_label: str = "center",
):
    """確率ヒートマップを地図上に描画する関数.

    指定したメッシュ GeoJSON と確率データをもとに、Plotly の Choroplethmapbox でヒートマップを描画します。
    UI の色・スタイルは外部から与えられる `colorscale` と引数で制御します（コードでは変更しません）。

    引数:
        mesh_geojson (dict): メッシュの GeoJSON（Feature の "properties.id" を featureidkey に対応させる）。
        probs_df (pd.DataFrame): セルごとの確率データ。少なくとも {cell_id または id, prob} 列が必要。
        center_lat (float): 地図の中心緯度。
        center_lon (float): 地図の中心経度。
        colorscale: カラースケール（Plotly の colorscale 仕様）。
        opacity (float): メッシュの透明度（デフォルト 1.0）。
        grid_outline_width (float): メッシュ外枠線幅（デフォルト 0.10）。
        min_prob (float): 表示する最小確率（デフォルト 0.0）。
        center_label (str): 地図中央のラベル（デフォルト "center"）。

    戻り値:
        plotly.graph_objs._figure.Figure: 確率ヒートマップ付き地図。

    例外:
        DataFrame や Plotly の内部処理で例外が発生する可能性があります。

    使用例:
        >>> fig = plot_probability_heatmap(mesh_geojson, probs_df, 35.6, 139.7, colorscale)

    注意:
        - `probs_df` に必要列が欠落している場合はフォールバックとして `japan_basemap()` を返します。
        - `min_prob` で z 値をフィルタします。z は [0,1] を想定しています。
        - `mapbox_style` は "carto-positron"、`mapbox_zoom` は 6.5 に固定しています（UI 側要件に合わせて変更しません）。
    """
    df = probs_df.copy()
    id_col = "cell_id" if "cell_id" in df.columns else ("id" if "id" in df.columns else None)
    if id_col is None or "prob" not in df.columns:
        return japan_basemap()

    df = df.loc[df["prob"].astype(float) >= float(min_prob)]
    feature_ids = df[id_col].astype(int).tolist()
    z = df["prob"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(
        go.Choroplethmapbox(
            geojson=mesh_geojson,
            featureidkey="properties.id",
            locations=feature_ids,
            z=z,
            colorscale=colorscale,
            zmin=0.0,
            zmax=1.0,
            marker=dict(line=dict(width=float(grid_outline_width))),
            showscale=True,
            name="Probability",
            marker_opacity=float(opacity),
        )
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        uirevision="base",
        mapbox_zoom=6.5,
        mapbox_center={"lat": float(center_lat), "lon": float(center_lon)},
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig
