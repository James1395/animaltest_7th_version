from __future__ import annotations
"""
アプリ本体（Flake8 整形済み）。
- タイトル: 獣害BIツール
- Sidebar に UI を集約
- 最小確率しきい値: 0.0..1.0（step 0.1）
- メッシュ: UTM による真の 1km × 1km
- 外枠線幅: 0.10（固定）
"""
import streamlit as st
from pbi.geo_regions import (
    prefecture_selector,
    hokkaido_split_selector,
    get_region_center,
)
from pbi.ui_filters import (
    species_selector,
    get_pref_bbox,
    is_species_present,
    clamp_horizon,
    normalize_time_of_day,
)
from pbi.core_foundation import render_frame, list_base_dates, color_scale_blue_purple
from pbi.map_layers import make_mesh_for_bbox, plot_probability_heatmap, japan_basemap
from pbi.mock_data import synth_probabilities


def render_app() -> None:
    """アプリ全体をレンダリングする。"""
    st.set_page_config(page_title="獣害BIツール", page_icon="🦌", layout="wide")

    # --- Sidebar ---
    st.sidebar.header("フィルタ / Filters")
    prefecture = prefecture_selector()
    hokkaido_part = hokkaido_split_selector(prefecture)
    species = species_selector()

    base_date = st.sidebar.selectbox("基準日 / Base date", list_base_dates(), index=0)
    horizon_days = clamp_horizon(st.sidebar.slider("予測日数 / Forecast days", 1, 30, 7))
    time_of_day = normalize_time_of_day(
        st.sidebar.radio("時間帯 / Time of day", ["午前", "午後"], index=0, horizontal=True)
    )

    st.sidebar.caption("表示の調整 / Display")
    grid_opacity = st.sidebar.slider("網格透明度 / Grid opacity", 0.10, 1.00, 1.00, 0.05)
    min_prob = st.sidebar.slider(
        "出現確率の最小閾値 / Min probability", min_value=0.0, max_value=1.0, value=0.0, step=0.1
    )

    # --- Main ---
    container = render_frame(title="獣害BIツール")
    with container:
        center_lat, center_lon = get_region_center(prefecture, hokkaido_part)

        if not is_species_present(prefecture, hokkaido_part, species):
            st.warning(f"この地域では '{species}' の生息情報がありません。別の組み合わせをお試しください。")
            st.plotly_chart(japan_basemap(), use_container_width=True, config={"scrollZoom": True})
            return

        min_lon, min_lat, max_lon, max_lat = get_pref_bbox(prefecture, hokkaido_part)
        mesh_gj, centers_df = make_mesh_for_bbox(
            min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat, km_step=1, padding_km=0
        )
        probs_df = synth_probabilities(
            cells_df=centers_df,
            species=species,
            base_date=base_date,
            time_of_day=time_of_day,
            horizon_days=horizon_days,
            data_df=None,
        )

        colorscale = color_scale_blue_purple()
        fig = plot_probability_heatmap(
            mesh_geojson=mesh_gj,
            probs_df=probs_df,
            center_lat=center_lat,
            center_lon=center_lon,
            colorscale=colorscale,
            opacity=grid_opacity,
            grid_outline_width=0.10,
            min_prob=float(min_prob),
            center_label=prefecture if prefecture != "北海道" else f"北海道（{hokkaido_part}）",
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
