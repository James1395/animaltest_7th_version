from __future__ import annotations
"""地図レイヤ（UTM で 1km メッシュ生成 → WGS84 に戻して Choropleth 描画）。"""

from typing import Iterable, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyproj import CRS, Transformer


def japan_basemap():
    """日本全体の carto-positron ベースマップを返す。"""
    df = pd.DataFrame(dict(lat=[36.2048], lon=[138.2529]))
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=3.7, height=540)
    fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
    return fig


# ---------- 内部：座標変換 & メッシュ生成 ----------


def _utm_crs_for_lon(lon: float) -> CRS:
    """与えられた経度に対し、北半球の UTM ゾーン CRS を返す。"""
    zone = int(np.floor((lon + 180) / 6) + 1)
    return CRS.from_epsg(32600 + zone)


def _make_transformers_for_bbox(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> Tuple[Transformer, Transformer]:
    """WGS84(度) ↔ UTM(メートル) の変換器（正/逆）を返す。"""
    lon_center = (min_lon + max_lon) / 2.0
    utm = _utm_crs_for_lon(lon_center)
    wgs84 = CRS.from_epsg(4326)
    to_m = Transformer.from_crs(wgs84, utm, always_xy=True)
    to_deg = Transformer.from_crs(utm, wgs84, always_xy=True)
    return to_m, to_deg


def _iter_cells(bounds_m: Tuple[float, float, float, float], cell_size_m: float) -> Iterable[Tuple[int, int, list]]:
    """メートル座標 bbox を `cell_size_m` 正方格子で走査し、(col,row,polygon_xy[m]) を返す。"""
    min_x, min_y, max_x, max_y = bounds_m
    xs = np.arange(min_x, max_x, cell_size_m)
    ys = np.arange(min_y, max_y, cell_size_m)
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            poly = [(x, y), (x + cell_size_m, y), (x + cell_size_m, y + cell_size_m), (x, y + cell_size_m), (x, y)]
            yield c, r, poly


# ---------- 公開 API ----------


def make_mesh_for_bbox(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    km_step: float = 1.0,
    padding_km: float = 0.0,
):
    """BBox に **真の 1km** 格子（UTM ベース）を生成し、GeoJSON とセル中心 DF を返す。"""
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
    """格子ごとの確率を Choroplethmapbox で可視化する（外枠は 0.10 固定）。"""
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
        mapbox_zoom=6.5,
        mapbox_center={"lat": float(center_lat), "lon": float(center_lon)},
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig
