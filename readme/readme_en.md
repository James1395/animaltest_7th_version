# Animal Risk Web (JP) — Documentation (English)

**Purpose**: A **Streamlit + Plotly** demo that visualizes wildlife risk across Japan on a **1 km UTM grid**, converted back to **WGS84** for display. You can switch prefectures (with a 4-way Hokkaido split), species, base date, time of day, forecast horizon, grid opacity, and a minimum probability threshold.

---

## 1) Feature Highlights

- **Basemap**: Plotly Mapbox (`carto-positron`) with default zoom `6.5`.
- **True 1 km grid**: Generated via `make_mesh_for_bbox` (resolution: 1km × 1km（km_step=1.0, 最小0.1）; WGS84 ↔︎ UTM でメッシュ計算後に WGS84 へ戻す).
- **Heatmap**: `plot_probability_heatmap` draws a choropleth using the `prob` column; outline width `0.1`; color scale `color_scale_blue_purple()（青→紫）`.
- **Presence check**: `is_species_present` (uses data/presence.json があれば参照、なければ True). If absent, show warning: “この種は該当地域には存在しません。” (Japanese).
- **Bounding boxes**: `data/pref_bboxes.json（存在しない場合は中心±0.8度を使用）`; falls back to center ±0.8°. For Hokkaido, key like `北海道は "北海道|道央" のように分区をキーに含める`.

---

## 2) UI (aligned with code)

- **都道府県 / Prefecture**
  - Widget: `selectbox` (options: 47都道府県（PREFS 定義）)
  - Default: `東京都` (`PREFS.index("東京都")`)
- **北海道の分区 / Hokkaido split**
  - Widget: `selectbox (conditional)`; visible when `Prefecture == "北海道"`
  - Options: `道南, 道央, 道北, 道東`; Default: `道央`
- **種別 / Species**
  - Widget: `selectbox`; Options: `熊, 鹿, 猪`; Default: `熊`
- **基準日 / Base date**
  - Widget: `selectbox`; Source: list_base_dates(max_items=3) → 今日(JST)から 0,1,2 日分（YYYY-MM-DD）
  - Today (JST): `2025-09-09`; default index 0
- **予測日数 / Forecast days**
  - Widget: `slider`; Range: `1–30`; Default: `7`; Note: clamp_horizon(days) により 1..30 に強制
- **時間帯 / Time of day**
  - Widget: `radio (horizontal)`; Options: `午前, 午後`; Default: `午前`; Normalizer: `normalize_time_of_day(value)`
- **網格透明度 / Grid opacity**
  - Widget: `slider`; Range: `0.1–1.0`; Step: `0.05`; Default: `1.0`
- **出現確率の最小閾値 / Min probability**
  - Widget: `slider`; Range: `0.0–1.0`; Step: `0.1`; Default: `0.0`

> **Tip**: To keep roads and boundaries readable, lower grid opacity to ~0.4–0.6, or raise the min probability to focus on high-risk cells.

---

## 3) Architecture & Modules

- `app.py`: Entry point (`core.render_app()`).
- `main.py`: Layout and app flow.
- `map_layers.py`: UTM↔WGS84 conversion, 1 km mesh, choropleth.
- `ui_filters.py`: Sidebar controls (`clamp_horizon`, `normalize_time_of_day`, `get_pref_bbox`, etc.).
- `geo_regions.py` / `geo.py`: Prefecture list, Hokkaido split, center coordinates; default prefecture is Tokyo.
- `validation.py`: Combination availability checks and warnings.
- `mock_data.py`: Synthetic probabilities (seeded for reproducibility).
- `core_foundation.py`: Frame, JST date helpers, blue→purple color scale.

---

## 4) Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\.venv\Scripts\Activate

pip install --upgrade pip
pip install -r requirements.txt
# or minimal
pip install streamlit plotly pandas numpy pyproj

streamlit run app.py
```

**Troubleshooting**  
- `'streamlit' not recognized` → Activate venv and install dependencies.  
- Launcher fatal error → Recreate `.venv`.  
- PowerShell policy → Use `Set-ExecutionPolicy`.

---

## 5) Development Notes

- Split large geodata and cache with `st.cache_data`.
- Prefer PR-based workflow instead of pushing to `main`.
- Respect OSM & GSI licenses.
- Tune opacity and min probability for clarity.

---

## 6) Disclaimer
- Aligned with code as of 2025-09-09.
- Demo only; no warranties on data accuracy or completeness.
