# animaltest_7th_version

# 獣害予測BIツール — ドキュメント（日本語）

**目的**：**Streamlit + Plotly** による日本国内の野生動物リスク可視化デモ。**1km メッシュ（UTM）** を計算し、**WGS84** に戻して描画します。都道府県／北海道4分割、種別、基準日、時間帯、予測日数、透明度、最小確率しきい値を切り替え可能。

---

## 1) 機能概要

- **ベースマップ**：Plotly Mapbox（`carto-positron`）、デフォルトズーム `6.5`。
- **真の1kmメッシュ**：`make_mesh_for_bbox`（解像度：1km × 1km（km_step=1.0, 最小0.1）；WGS84 ↔︎ UTM でメッシュ計算後に WGS84 へ戻す）。
- **ヒートマップ**：`plot_probability_heatmap` が `prob` を Choropleth として描画。枠線 `0.1`、カラースケール `color_scale_blue_purple()（青→紫）`。
- **生息有無の検証**：`is_species_present` （data/presence.json があれば参照、なければ True）。無い場合は警告：「この種は該当地域には存在しません。」。
- **バウンディングボックス**：`data/pref_bboxes.json（存在しない場合は中心±0.8度を使用）`（無い場合は中心±0.8°）。北海道は `北海道は "北海道|道央" のように分区をキーに含める`。

---

## 2) UI（コードに一致）

- **都道府県 / Prefecture**
  - ウィジェット：`selectbox`（選択肢：47都道府県（PREFS 定義））
  - 既定値：`東京都`（`PREFS.index("東京都")`）
- **北海道の分区 / Hokkaido split**
  - ウィジェット：`selectbox (conditional)`；表示条件：`Prefecture == "北海道"`
  - 選択肢：`道南, 道央, 道北, 道東`／既定：`道央`
- **種別 / Species**
  - ウィジェット：`selectbox`；選択肢：`熊, 鹿, 猪`／既定：`熊`
- **基準日 / Base date**
  - ウィジェット：`selectbox`；供給源：list_base_dates(max_items=3) → 今日(JST)から 0,1,2 日分（YYYY-MM-DD）
  - 今日（JST）：`2025-09-09`（index 0）
- **予測日数 / Forecast days**
  - ウィジェット：`slider`；範囲：`1〜30`／既定：`7`／備考：clamp_horizon(days) により 1..30 に強制
- **時間帯 / Time of day**
  - ウィジェット：`radio (horizontal)`；選択肢：`午前, 午後`／既定：`午前`；正規化：`normalize_time_of_day(value)`
- **網格透明度 / Grid opacity**
  - ウィジェット：`slider`；範囲：`0.1〜1.0`／ステップ：`0.05`／既定：`1.0`
- **出現確率の最小閾値 / Min probability**
  - ウィジェット：`slider`；範囲：`0.0〜1.0`／ステップ：`0.1`／既定：`0.0`

> **Tips**：底図の道路や境界線を見やすくするには、透明度を 0.4〜0.6 に下げる、または最小確率を 0.5 以上に上げるのが有効です。

---

## 3) 構成とモジュール

- `app.py`：エントリーポイント（`core.render_app()`）。
- `main.py`：画面レイアウト・アプリフロー。
- `map_layers.py`：UTM↔WGS84 変換、1km メッシュ、Choropleth。
- `ui_filters.py`：サイドバー UI（`clamp_horizon`, `normalize_time_of_day`, `get_pref_bbox` など）。
- `geo_regions.py` / `geo.py`：都道府県一覧、北海道分割、中心座標。デフォルトは「東京都」。
- `validation.py`：組合せの存在チェックと警告表示。
- `mock_data.py`：合成確率データの生成（再現性あり）。
- `core_foundation.py`：フレーム、JST 日付ユーティリティ、カラースケール。

---

## 4) セットアップ（Windows PowerShell）

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\.venv\Scripts\Activate

pip install --upgrade pip
pip install -r requirements.txt
# または
pip install streamlit plotly pandas numpy pyproj

streamlit run app.py
```

**トラブルシューティング**  
- `streamlit` が見つからない → venv の有効化・依存インストールを確認。  
- ランチャーの致命的エラー → `.venv` を作り直す。  
- PowerShell の実行権限 → `Set-ExecutionPolicy` を実施。

---

## 5) 開発ガイド

- 大きな地理データは分割し、`st.cache_data` を活用。
- 直接 `main` に push せず、PR ベースで運用。
- OSM/GSI のライセンス表記・流量に留意。
- 透明度・最小確率の調整で表示品質を最適化。

---

## 6) 免責
- 2025-09-09 時点のコードに基づく記載です。
- デモ用途であり、正確性・完全性を保証しません。
