# 獣害予測BIツール — 說明文件（繁體中文）

> **目的**：用 **Streamlit + Plotly** 建構的日本野生動物風險視覺化 Demo，將 **1km 網格（UTM）** 轉回 **WGS84** 顯示，支援都道府縣/北海道四分區、物種、基準日、時間帶、預測天數、透明度與機率閾值等切換。

---

## 1) 功能總覽

- **地圖底圖**：Plotly Mapbox（`carto-positron`），預設縮放 `6.5`。
- **1km 真網格**：由 `make_mesh_for_bbox` 產生（解析度：1km × 1km（km_step=1.0, 最小0.1）；WGS84 ↔︎ UTM でメッシュ計算後に WGS84 へ戻す）。
- **熱區著色**：`plot_probability_heatmap` 以合成或資料檔之 `prob` 欄位繪製 Choropleth；輪廓線固定 `0.1`；色盤 `color_scale_blue_purple()（青→紫）`。
- **存在性驗證**：`is_species_present` 以 `data/presence.json があれば参照、なければ True` 驗證組合，不存在則顯示日文警告：「この種は該当地域には存在しません。」。
- **BBox 來源**：`data/pref_bboxes.json（存在しない場合は中心±0.8度を使用）`；若未提供則以中心座標 ±0.8° 估算；北海道 key 如 `北海道は "北海道|道央" のように分区をキーに含める`。

---

## 2) 介面（UI）設定 — 與程式碼對齊

- **都道府県 / Prefecture**
  - 元件：`selectbox`（選項：47都道府県（PREFS 定義））
  - 預設值：`東京都`（`PREFS.index("東京都")`）
- **北海道の分区 / Hokkaido split**
  - 元件：`selectbox (conditional)`；條件顯示：`Prefecture == "北海道"`
  - 選項：`道南, 道央, 道北, 道東`；預設：`道央`
- **種別 / Species**
  - 元件：`selectbox`；選項：`熊, 鹿, 猪`；預設：`熊`
- **基準日 / Base date**
  - 元件：`selectbox`；來源：list_base_dates(max_items=3) → 今日(JST)から 0,1,2 日分（YYYY-MM-DD）
  - 今日（JST）：`2025-09-09`；預設為今日（索引 0）
- **予測日数 / Forecast days**
  - 元件：`slider`；範圍：`1–30`；預設：`7`；備註：clamp_horizon(days) により 1..30 に強制
- **時間帯 / Time of day**
  - 元件：`radio (horizontal)`；選項：`午前, 午後`；預設：`午前`；正規化：`normalize_time_of_day(value)`
- **網格透明度 / Grid opacity**
  - 元件：`slider`；範圍：`0.1–1.0`；步進：`0.05`；預設：`1.0`
- **出現確率の最小閾値 / Min probability**
  - 元件：`slider`；範圍：`0.0–1.0`；步進：`0.1`；預設：`0.0`

> **提示**：透明度 `1.0` 代表網格完全不透明；若希望看清底圖道路與行政界線，可把透明度降到 ~0.4–0.6，或提升 `出現確率の最小閾値 / Min probability` 以凸顯高機率區域。

---

## 3) 架構與模組

- `app.py`：入口（呼叫 `core.render_app()`）。
- `main.py`：主流程與畫面佈局、呼叫各子模組。
- `map_layers.py`：UTM↔WGS84 轉換、1km 網格生成、Choropleth。
- `ui_filters.py`：側欄控制（物種、預測日數、時間帶、透明度、閾值等）與工具（`clamp_horizon`, `normalize_time_of_day`, `get_pref_bbox`）。
- `geo_regions.py` / `geo.py`：都道府縣清單、北海道分區與中心點座標、預設為「東京都」。 
- `validation.py`：組合可用性檢查與警告訊息。
- `mock_data.py`：合成概率（以 seed 再現性生成）。
- `core_foundation.py`：畫面框架、JST 日期工具、藍→紫色盤。

---

## 4) 安裝與執行（Windows PowerShell）

```powershell
# 建立與啟用 venv
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\.venv\Scripts\Activate

# 安裝套件（若無 requirements.txt，可先安裝最小依賴）
pip install --upgrade pip
pip install -r requirements.txt
# or
pip install streamlit plotly pandas numpy pyproj

# 啟動
streamlit run app.py
```

**常見問題**  
- `streamlit : The term 'streamlit' is not recognized` → 未啟用 venv 或未安裝 `streamlit`。  
- `Fatal error in launcher: Unable to create process...` → 刪除 `.venv` 後重新建立並安裝依賴。  
- PowerShell 執行權限錯誤 → 已使用 `Set-ExecutionPolicy`。

---

## 5) 開發建議與資料

- **快取與分割**：大型地理資料請分區；使用 `st.cache_data` 快取讀檔。  
- **PR 工作流**：避免直接 push `main`；使用 `feature → PR → merge`。  
- **地圖授權**：OSM 與日本地理院（GSI）需要依條款標示與控制流量。  
- **調參建議**：
  - 若底圖被網格蓋住 → 將透明度降至 0.4–0.6。
  - 只看高風險 → 將最小概率提高到 0.5/0.6 以上。

---

## 6) 版本與責任聲明
- 以 2025-09-09 的程式碼為準（本 README 與 UI 參數對齊於最新檔）。
- 本專案為示範用途；對資料準確性與用途不做任何保證。
