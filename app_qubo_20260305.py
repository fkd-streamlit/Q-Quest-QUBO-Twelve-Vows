# -*- coding: utf-8 -*-
"""
Q-Quest-QUBO : Quantum Shintaku (2026-03-05 spec)
-------------------------------------------------
仕様変更（要約版 2026-03-05）に対応：
- 4門は撤廃
- 入力は「3軸（顕↔密 / 智↔悲 / 和↔荒）」スライダー
- 十二因縁 ↔ 12誓願（介入点） ↔ 12神（語り手）を一貫した説明線で接続
- 12神の選択は one-hot QUBO（Simulated Annealing でサンプリング）

Excel（統合）シート想定：
1) 十二因縁と12誓願の統合
2) 12神の本質・性格・3軸ベクトルとその説明
3) 神と誓願の因果律マトリクス（距離ベース）
4) 神と誓願の因果律マトリクス（意味ベース）
"""

import math
import random
import re
import io
import hashlib
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
from typing import List, Dict, Tuple, Optional

# ============================================================
# Streamlit config（必ず最初）
# ============================================================
st.set_page_config(
    page_title="Q-Quest-QUBO｜量子神託（3軸→誓願→QUBO）",
    layout="wide",
)

# ============================================================
# THEME / CSS（app_qubo.py の黒基調UIを踏襲）
# ============================================================
# CSSを最初に適用（st.set_page_configの直後）
def _load_space_css_from_legacy_app() -> str | None:
    """
    既存の app_qubo.py の SPACE_CSS を抽出して適用する（UI踏襲の最短経路）。
    """
    legacy = Path(__file__).with_name("app_qubo.py")
    if not legacy.exists():
        return None
    try:
        txt = legacy.read_text(encoding="utf-8")
    except Exception:
        return None

    # app_qubo.pyのCSSを抽出
    # SPACE_CSS = """<style>...CSS...</style>"""のパターン
    # st.markdown(SPACE_CSS, unsafe_allow_html=True)の直前までを取得
    m = re.search(
        r'SPACE_CSS\s*=\s*"""\s*\n\s*<style>\s*\n(.*?)\n\s*</style>\s*\n\s*"""\s*\n\s*st\.markdown\(SPACE_CSS',
        txt,
        re.S | re.M,
    )
    if not m:
        # フォールバック: <style>タグなしのパターン（直接CSS）
        m = re.search(
            r'SPACE_CSS\s*=\s*"""(.*?)"""\s*\n\s*st\.markdown\(SPACE_CSS',
            txt,
            re.S,
        )
    if not m:
        return None
    css = m.group(1)
    css = css.strip()
    # <style>タグが含まれている場合は削除
    css = re.sub(r'^\s*<style>\s*', '', css, flags=re.M)
    css = re.sub(r'\s*</style>\s*$', '', css, flags=re.M)
    return css if css else None


# app_qubo.py から完全なCSSを直接読み込む（抽出失敗時は完全版フォールバック）
_legacy_css = _load_space_css_from_legacy_app()
if _legacy_css:
    # app_qubo.pyのCSSをそのまま使用（確実に黒背景）
    SPACE_CSS = f"<style>\n{_legacy_css}\n</style>"
    # すぐに適用
    st.markdown(SPACE_CSS, unsafe_allow_html=True)
else:
    # フォールバック: app_qubo.py の完全なCSS（白文字を確実に表示）
    SPACE_CSS = """
<style>
/* --- App background (黒背景を強制・最優先) --- */
html,
body,
body > div,
body > div > div,
.stApp,
.stApp > div,
.stApp > div > div,
.stApp > div > div > div {
  background:
    radial-gradient(circle at 18% 24%, rgba(110,150,255,0.12), transparent 38%),
    radial-gradient(circle at 78% 68%, rgba(255,160,220,0.08), transparent 44%),
    radial-gradient(circle at 50% 50%, rgba(255,255,255,0.03), transparent 55%),
    linear-gradient(180deg, rgba(6,8,18,1), rgba(10,12,26,1)) !important;
  background-color: rgba(6,8,18,1) !important;
  background-image: 
    radial-gradient(circle at 18% 24%, rgba(110,150,255,0.12), transparent 38%),
    radial-gradient(circle at 78% 68%, rgba(255,160,220,0.08), transparent 44%),
    radial-gradient(circle at 50% 50%, rgba(255,255,255,0.03), transparent 55%),
    linear-gradient(180deg, rgba(6,8,18,1), rgba(10,12,26,1)) !important;
}

/* --- Main content area background (黒背景を強制) --- */
.main,
.main > div,
.main .block-container,
.main .block-container > div {
  background: rgba(10,12,26,0.95) !important;
  background-color: rgba(10,12,26,0.95) !important;
}

/* --- Block container background (黒背景を強制) --- */
.block-container,
.block-container > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div {
  background: rgba(10,12,26,0.95) !important;
  background-color: rgba(10,12,26,0.95) !important;
}

/* --- すべての白背景を黒に上書き（より強力に） --- */
[style*="background-color: rgb(255"],
[style*="background-color:rgb(255"],
[style*="background: rgb(255"],
[style*="background:rgb(255"],
[style*="#ffffff"],
[style*="#FFFFFF"],
[style*="background-color: white"],
[style*="background: white"],
div[style*="background"],
section[style*="background"],
main[style*="background"] {
  background-color: rgba(10,12,26,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}

/* --- Streamlitのデフォルト白背景を強制上書き（最優先） --- */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > div,
div[data-testid="stAppViewContainer"] > div > div,
div[data-testid="stAppViewContainer"] > div > div > div,
#root,
#root > div,
#root > div > div {
  background-color: rgba(6,8,18,1) !important;
  background: rgba(6,8,18,1) !important;
}

/* --- すべてのdiv要素の背景を黒に（最強力） --- */
div:not([class*="st"]):not([data-testid*="st"]) {
  background-color: transparent !important;
}

div[class*="st"],
div[data-testid*="st"],
section[class*="st"],
section[data-testid*="st"] {
  background-color: rgba(6,8,18,0.98) !important;
  background: rgba(6,8,18,0.98) !important;
}

/* --- header / toolbar (Share, GitHub icon area) --- */
header[data-testid="stHeader"]{
  background: rgba(6,8,18,0.90) !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
div[data-testid="stToolbar"]{
  background: rgba(6,8,18,0.90) !important;
}
div[data-testid="stToolbar"] *{
  color: rgba(245,245,255,0.85) !important;
  fill: rgba(245,245,255,0.85) !important;
}
a, a:visited { color: rgba(170,210,255,0.95) !important; }

/* --- Base typography --- */
.block-container{ padding-top: 1.2rem; }
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li{
  font-family: "Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif;
  letter-spacing: 0.02em;
  color: rgba(245,245,255,0.92);
}
h1,h2,h3,h4,h5,h6{
  font-family: "Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif !important;
  font-weight: 650 !important;
  color: rgba(245,245,255,0.95) !important;
  text-shadow: 0 2px 18px rgba(0,0,0,0.45);
}

/* --- Captions and labels --- */
[data-testid="stCaption"],
[data-testid="stCaption"] *,
.stCaption,
.stCaption * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Radio button labels --- */
[data-baseweb="radio"] label,
[data-baseweb="radio"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Slider labels --- */
[data-baseweb="slider"] label,
[data-baseweb="slider"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Number input labels --- */
[data-baseweb="input"] label,
[data-baseweb="input"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- All text elements (より強力に) --- */
.block-container p,
.block-container span,
.block-container div,
.block-container label,
.block-container strong,
.block-container b,
.block-container em,
.block-container i,
.block-container h1,
.block-container h2,
.block-container h3,
.block-container h4,
.block-container h5,
.block-container h6 {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Streamlit widget labels (より強力に) --- */
div[data-testid="stRadio"] label,
div[data-testid="stSlider"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {
  color: rgba(245,245,255,0.95) !important;
}

/* --- すべてのテキスト要素を強制的に白に（グローバル・最優先） --- */
.stApp p,
.stApp span,
.stApp div,
.stApp label,
.stApp strong,
.stApp b,
.stApp em,
.stApp i {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"]{
  background: rgba(6,8,18,0.95) !important;
  border-right: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(10px);
}
section[data-testid="stSidebar"] *{
  color: rgba(245,245,255,0.92) !important;
}

/* --- Sidebar content boxes --- */
section[data-testid="stSidebar"] > div {
  background: rgba(6,8,18,0.95) !important;
}
section[data-testid="stSidebar"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-baseweb="input"] {
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}

/* --- inputs: make text visible --- */
textarea, input[type="text"], input[type="number"] {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}
textarea::placeholder, input::placeholder {
  color: rgba(245,245,255,0.55) !important;
}

/* --- Streamlit specific input components --- */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
  background: rgba(10,12,26,0.95) !important;
}
div[data-baseweb="base-input"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}

/* --- Text area specific --- */
div[data-testid="stTextArea"] textarea {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}

/* --- Text input specific --- */
div[data-testid="stTextInput"] input {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}

/* --- Sidebar selectbox, slider, toggle --- */
section[data-testid="stSidebar"] [data-baseweb="select"],
section[data-testid="stSidebar"] [data-baseweb="slider"],
section[data-testid="stSidebar"] [data-baseweb="checkbox"] {
  background: rgba(10,12,26,0.95) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}

/* --- Slider track and thumb --- */
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
  background: rgba(100,150,255,0.8) !important;
}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"]:hover {
  background: rgba(120,170,255,1) !important;
}

/* --- Toggle/Checkbox --- */
section[data-testid="stSidebar"] [data-baseweb="checkbox"] label {
  color: rgba(245,245,255,0.95) !important;
}

/* --- file uploader (black panel fix) --- */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] > div,
div[data-testid="stFileUploader"] > div > div {
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
  border-radius: 14px !important;
  padding: 10px !important;
}
/* すべてのテキストを白に */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] *,
div[data-testid="stFileUploader"] * * {
  color: rgba(245,245,255,0.95) !important;
}
/* ドラッグ&ドロップエリア */
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"],
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"] * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border-color: rgba(255,255,255,0.20) !important;
}
/* ファイルアップローダーの内部テキスト */
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] div,
div[data-testid="stFileUploader"] label {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}
/* ボタン */
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] [role="button"] {
  background: rgba(20,30,50,0.8) !important;
  color: rgba(245,245,255,0.95) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
}
div[data-testid="stFileUploader"] button:hover,
div[data-testid="stFileUploader"] [role="button"]:hover {
  background: rgba(30,40,60,0.9) !important;
}
/* アップロード済みファイル名 */
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"] [data-baseweb="file-name"],
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"] [data-baseweb="file-size"] {
  color: rgba(245,245,255,0.95) !important;
}
/* 白い背景を黒に上書き */
div[data-testid="stFileUploader"] [style*="background-color: rgb(255"],
div[data-testid="stFileUploader"] [style*="background-color:rgb(255"],
div[data-testid="stFileUploader"] [style*="background: rgb(255"],
div[data-testid="stFileUploader"] [style*="background:rgb(255"],
div[data-testid="stFileUploader"] [style*="#ffffff"],
div[data-testid="stFileUploader"] [style*="#FFFFFF"] {
  background-color: rgba(10,12,26,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
}
/* 薄い灰色の文字を白に */
div[data-testid="stFileUploader"] [style*="color: rgb(128"],
div[data-testid="stFileUploader"] [style*="color:rgb(128"],
div[data-testid="stFileUploader"] [style*="color: rgb(200"],
div[data-testid="stFileUploader"] [style*="color:rgb(200"],
div[data-testid="stFileUploader"] [style*="color: rgb(150"],
div[data-testid="stFileUploader"] [style*="color:rgb(150"] {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Expander (折りたたみ可能セクション) - より強力に --- */
div[data-testid="stExpander"],
div[data-testid="stExpander"] > div,
div[data-testid="stExpander"] > div > div,
div[data-testid="stExpander"] > div > div > div {
  background: rgba(10,12,26,0.95) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  border-radius: 8px !important;
  color: rgba(245,245,255,0.95) !important;
}
/* Expanderのタイトル（ヘッダー） */
div[data-testid="stExpander"] [data-baseweb="accordion"],
div[data-testid="stExpander"] [data-baseweb="accordion"] * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stExpander"] [data-baseweb="accordion"] button,
div[data-testid="stExpander"] [data-baseweb="accordion"] [role="button"],
div[data-testid="stExpander"] summary {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border: none !important;
}
div[data-testid="stExpander"] [data-baseweb="accordion"] button *,
div[data-testid="stExpander"] [data-baseweb="accordion"] [role="button"] *,
div[data-testid="stExpander"] summary *,
div[data-testid="stExpander"] [data-baseweb="accordion"] button * * {
  color: rgba(245,245,255,0.95) !important;
}
/* Expanderのコンテンツ */
div[data-testid="stExpander"] [data-baseweb="accordion-panel"],
div[data-testid="stExpander"] [data-baseweb="accordion-panel"] *,
div[data-testid="stExpander"] [data-baseweb="accordion-panel"] * * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
}
/* Expander内のすべてのテキスト（最優先） */
div[data-testid="stExpander"],
div[data-testid="stExpander"] *,
div[data-testid="stExpander"] * *,
div[data-testid="stExpander"] * * *,
div[data-testid="stExpander"] * * * * {
  color: rgba(245,245,255,0.95) !important;
}
/* Expander内のmarkdownテキスト */
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] div,
div[data-testid="stExpander"] strong,
div[data-testid="stExpander"] b,
div[data-testid="stExpander"] h1,
div[data-testid="stExpander"] h2,
div[data-testid="stExpander"] h3,
div[data-testid="stExpander"] h4,
div[data-testid="stExpander"] h5,
div[data-testid="stExpander"] h6 {
  color: rgba(245,245,255,0.95) !important;
}
/* Expander内のDataFrameも白文字に */
div[data-testid="stExpander"] div[data-testid="stDataFrame"],
div[data-testid="stExpander"] div[data-testid="stDataFrame"] *,
div[data-testid="stExpander"] div[data-testid="stDataFrame"] * * {
  color: rgba(245,245,255,0.95) !important;
}
/* Expander内のst.markdownコンテンツ */
div[data-testid="stExpander"] [data-testid="stMarkdownContainer"],
div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] *,
div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] * * {
  color: rgba(245,245,255,0.95) !important;
}
/* 白い背景を黒に上書き */
div[data-testid="stExpander"] [style*="background-color: rgb(255"],
div[data-testid="stExpander"] [style*="background-color:rgb(255"],
div[data-testid="stExpander"] [style*="background: rgb(255"],
div[data-testid="stExpander"] [style*="background:rgb(255"],
div[data-testid="stExpander"] [style*="#ffffff"],
div[data-testid="stExpander"] [style*="#FFFFFF"] {
  background-color: rgba(10,12,26,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
}
/* 黒い文字を白に上書き（すべてのパターン） */
div[data-testid="stExpander"] [style*="color"],
div[data-testid="stExpander"] [style*="color"] * {
  color: rgba(245,245,255,0.95) !important;
}
/* 特定の色パターンも上書き */
div[data-testid="stExpander"] [style*="color: rgb(0"],
div[data-testid="stExpander"] [style*="color:rgb(0"],
div[data-testid="stExpander"] [style*="color: rgb(38"],
div[data-testid="stExpander"] [style*="color:rgb(38"],
div[data-testid="stExpander"] [style*="color: rgb(49"],
div[data-testid="stExpander"] [style*="color:rgb(49"],
div[data-testid="stExpander"] [style*="color: rgb(19"],
div[data-testid="stExpander"] [style*="color:rgb(19"] {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Cards --- */
.card{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 16px 16px 12px 16px;
  box-shadow: 0 18px 60px rgba(0,0,0,0.22);
}
.smallnote{opacity:0.80; font-size:0.92rem;}

/* --- Dataframe/Table : force dark --- */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div,
div[data-testid="stDataFrame"] > div > div,
div[data-testid="stDataFrame"] > div > div > div {
  border-radius: 16px !important;
  overflow: hidden !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  background: rgba(10,12,26,0.95) !important;
}
/* Force all text to white - comprehensive override (最優先) */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] *,
div[data-testid="stDataFrame"] * *,
div[data-testid="stDataFrame"] * * *,
div[data-testid="stDataFrame"] * * * * {
  color: rgba(245,245,255,0.95) !important;
}
/* さらに強力: すべてのテキストノードを強制 */
div[data-testid="stDataFrame"] {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] * {
  color: rgba(245,245,255,0.95) !important;
}
/* BaseWeb Table (Streamlit DataFrame internal) - より強力に --- */
div[data-testid="stDataFrame"] [data-baseweb="table"],
div[data-testid="stDataFrame"] [data-baseweb="table"] *,
div[data-testid="stDataFrame"] [data-baseweb="table"] * *,
div[data-testid="stDataFrame"] [data-baseweb="table"] * * *,
div[data-testid="stDataFrame"] [data-baseweb="table"] * * * * {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}
/* BaseWebのすべての要素 */
div[data-testid="stDataFrame"] [data-baseweb] {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] [data-baseweb] * {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] [data-baseweb="table"] [data-baseweb="table-head"],
div[data-testid="stDataFrame"] [data-baseweb="table"] [data-baseweb="table-body"],
div[data-testid="stDataFrame"] [data-baseweb="table"] [data-baseweb="table-head"] *,
div[data-testid="stDataFrame"] [data-baseweb="table"] [data-baseweb="table-body"] * {
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}
div[data-testid="stDataFrame"] [role="grid"],
div[data-testid="stDataFrame"] [role="row"],
div[data-testid="stDataFrame"] [role="rowgroup"],
div[data-testid="stDataFrame"] [role="gridcell"],
div[data-testid="stDataFrame"] [role="columnheader"]{
  color: rgba(245,245,255,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}
div[data-testid="stDataFrame"] [role="gridcell"] *,
div[data-testid="stDataFrame"] [role="gridcell"] * *,
div[data-testid="stDataFrame"] [role="columnheader"] *,
div[data-testid="stDataFrame"] [role="columnheader"] * * {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] [role="columnheader"],
div[data-testid="stDataFrame"] [role="columnheader"] *,
div[data-testid="stDataFrame"] [role="columnheader"] * * {
  background: rgba(15,18,35,0.98) !important;
  color: rgba(245,245,255,1) !important;
  border-bottom: 1px solid rgba(255,255,255,0.15) !important;
  font-weight: 600 !important;
}
div[data-testid="stDataFrame"] [role="gridcell"],
div[data-testid="stDataFrame"] [role="gridcell"] *,
div[data-testid="stDataFrame"] [role="gridcell"] * * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
div[data-testid="stDataFrame"] [data-testid="stTable"] {
  background: rgba(10,12,26,0.95) !important;
}

/* --- Streamlit DataFrame wrapper --- */
div[data-testid="stDataFrame"] > div[style*="background"] {
  background: rgba(10,12,26,0.95) !important;
}

/* --- st.table fallback --- */
table,
table * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
}
thead tr th,
thead tr th * {
  background: rgba(15,18,35,0.98) !important;
  color: rgba(245,245,255,1) !important;
  border-bottom: 1px solid rgba(255,255,255,0.15) !important;
  font-weight: 600 !important;
}
tbody tr td,
tbody tr td * {
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
tbody tr:hover td {
  background: rgba(15,18,35,0.8) !important;
}

/* --- Force all table elements to dark --- */
[data-testid="stDataFrame"] [style*="background-color"],
[data-testid="stDataFrame"] [style*="background"],
[data-testid="stDataFrame"] div[style],
[data-testid="stDataFrame"] span[style] {
  background-color: rgba(10,12,26,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
}

/* --- Override any white backgrounds in tables --- */
div[data-testid="stDataFrame"] [style*="rgb(255, 255, 255)"],
div[data-testid="stDataFrame"] [style*="rgb(255,255,255)"],
div[data-testid="stDataFrame"] [style*="#ffffff"],
div[data-testid="stDataFrame"] [style*="#FFFFFF"] {
  background-color: rgba(10,12,26,0.95) !important;
  background: rgba(10,12,26,0.95) !important;
  color: rgba(245,245,255,0.95) !important;
}

/* --- Force text color in all table cells --- */
div[data-testid="stDataFrame"] p,
div[data-testid="stDataFrame"] span,
div[data-testid="stDataFrame"] div,
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th,
div[data-testid="stDataFrame"] [role="gridcell"] *,
div[data-testid="stDataFrame"] [role="columnheader"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Force white text in all table elements (override any black text) --- */
div[data-testid="stDataFrame"] [style*="color: rgb(0"],
div[data-testid="stDataFrame"] [style*="color:rgb(0"],
div[data-testid="stDataFrame"] [style*="color:#000"],
div[data-testid="stDataFrame"] [style*="color:#000000"],
div[data-testid="stDataFrame"] [style*="color: rgb(38"],
div[data-testid="stDataFrame"] [style*="color:rgb(38"],
div[data-testid="stDataFrame"] [style*="color: rgb(49"],
div[data-testid="stDataFrame"] [style*="color:rgb(49"] {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Force all text in tables to be white (comprehensive) --- */
div[data-testid="stDataFrame"] *,
div[data-testid="stDataFrame"] * *,
div[data-testid="stDataFrame"] * * * {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] [class*="text"],
div[data-testid="stDataFrame"] [class*="Text"],
div[data-testid="stDataFrame"] [class*="data"],
div[data-testid="stDataFrame"] [class*="Data"] {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Override Streamlit's default table text colors --- */
div[data-testid="stDataFrame"] [data-testid="stTable"] *,
div[data-testid="stDataFrame"] [data-testid="stTable"] * *,
div[data-testid="stDataFrame"] [data-testid="stTable"] [class*="data"] *,
div[data-testid="stDataFrame"] [class*="data"] *,
div[data-testid="stDataFrame"] [class*="Data"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Force white text in all DataFrame wrapper elements --- */
[data-testid="stDataFrame"] [class*="stDataFrame"] *,
[data-testid="stDataFrame"] [class*="dataframe"] *,
[data-testid="stDataFrame"] [class*="DataFrame"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Override any inline styles that set text color to black/dark --- */
div[data-testid="stDataFrame"] [style],
div[data-testid="stDataFrame"] [style] *,
div[data-testid="stDataFrame"] [style] * * {
  color: rgba(245,245,255,0.95) !important;
}
/* インラインスタイルの色指定を無視して強制上書き */
div[data-testid="stDataFrame"] [style*="color"],
div[data-testid="stDataFrame"] [style*="color"] * {
  color: rgba(245,245,255,0.95) !important;
}
/* すべてのテキストコンテンツを強制的に白に */
div[data-testid="stDataFrame"] ::before,
div[data-testid="stDataFrame"] ::after {
  color: rgba(245,245,255,0.95) !important;
}

/* --- さらに強力なセレクタ: すべてのテキストノードを強制的に白に --- */
div[data-testid="stDataFrame"] * {
  color: rgba(245,245,255,0.95) !important;
}
/* すべての要素タイプに適用 */
div[data-testid="stDataFrame"] p,
div[data-testid="stDataFrame"] span,
div[data-testid="stDataFrame"] div,
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th,
div[data-testid="stDataFrame"] tr,
div[data-testid="stDataFrame"] table,
div[data-testid="stDataFrame"] thead,
div[data-testid="stDataFrame"] tbody,
div[data-testid="stDataFrame"] tfoot {
  color: rgba(245,245,255,0.95) !important;
}

/* --- BaseWebの特定のクラス名にも対応 --- */
div[data-testid="stDataFrame"] [class*="BaseTable"],
div[data-testid="stDataFrame"] [class*="base-table"],
div[data-testid="stDataFrame"] [class*="Table"],
div[data-testid="stDataFrame"] [class*="table"] {
  color: rgba(245,245,255,0.95) !important;
}
div[data-testid="stDataFrame"] [class*="BaseTable"] *,
div[data-testid="stDataFrame"] [class*="base-table"] *,
div[data-testid="stDataFrame"] [class*="Table"] *,
div[data-testid="stDataFrame"] [class*="table"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- すべてのメインコンテンツのテキストを白に（最優先） --- */
.main .block-container,
.main .block-container *,
.main [data-testid="stMarkdownContainer"],
.main [data-testid="stMarkdownContainer"] * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- st.write, st.text, st.markdown などの出力を白に --- */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {
  color: rgba(245,245,255,0.95) !important;
}

/* --- すべてのテキスト要素を強制的に白に（グローバル） --- */
body,
body *,
.stApp,
.stApp * {
  color: rgba(245,245,255,0.95) !important;
}

/* --- Streamlitのメッセージボックス（info, success, warning, error）の背景を黒に --- */
div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlert"] > div > div,
div[data-baseweb="notification"],
div[data-baseweb="notification"] > div {
  background-color: rgba(6,8,18,0.95) !important;
  background: rgba(6,8,18,0.95) !important;
  border-color: rgba(255,255,255,0.2) !important;
}

/* --- Streamlitのすべての要素の背景を黒に（最終手段） --- */
div[class],
section[class],
main[class],
article[class] {
  background-color: rgba(6,8,18,0.95) !important;
  background: rgba(6,8,18,0.95) !important;
}

/* --- さらに強力な背景色の強制（Streamlit要素のみ） --- */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > div,
div[data-testid="stAppViewContainer"] > div > div,
div[data-testid="stAppViewContainer"] > div > div > div,
div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"] > div,
div[data-testid="stVerticalBlock"] > div > div,
div[data-testid="stHorizontalBlock"],
div[data-testid="stHorizontalBlock"] > div,
div[data-testid="stHorizontalBlock"] > div > div,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"] > div,
#root,
#root > div,
#root > div > div {
  background-color: rgba(6,8,18,1) !important;
  background: rgba(6,8,18,1) !important;
}

/* --- メインコンテンツエリアの背景を確実に黒に --- */
.main,
.main > div,
.main .block-container,
.main .block-container > div,
.main .block-container > div > div,
.block-container,
.block-container > div,
.block-container > div > div {
  background-color: rgba(6,8,18,0.98) !important;
  background: rgba(6,8,18,0.98) !important;
}

/* --- すべてのStreamlit要素の背景を黒に（最強力） --- */
[class*="st"],
[data-testid*="st"] {
  background-color: rgba(6,8,18,0.95) !important;
  background: rgba(6,8,18,0.95) !important;
}
</style>
"""
st.markdown(SPACE_CSS, unsafe_allow_html=True)

# ============================================================
# QUBO core
# ============================================================
def build_qubo_onehot(linear_E: np.ndarray, P: float) -> np.ndarray:
    """
    E(x)=ΣE_i x_i + P(Σx-1)^2
    """
    linear_E = np.asarray(linear_E, float)
    n = len(linear_E)
    Q = np.zeros((n, n), float)
    for i in range(n):
        Q[i, i] += linear_E[i] - P
        for j in range(i + 1, n):
            Q[i, j] += 2 * P
    return Q

def energy(Q: np.ndarray, x: np.ndarray) -> float:
    return float(x @ Q @ x)

def onehot_index(x: np.ndarray):
    idx = np.where(x == 1)[0]
    return int(idx[0]) if len(idx) == 1 else None

def sa_sample(Q: np.ndarray, num_reads=240, sweeps=420, t0=5.0, t1=0.2, seed=0):
    rng = random.Random(seed)
    n = Q.shape[0]
    samples, energies = [], []

    for _ in range(num_reads):
        x = np.array([rng.randint(0, 1) for _ in range(n)], int)
        E = energy(Q, x)

        for s in range(sweeps):
            t = t0 + (t1 - t0) * (s / max(1, sweeps - 1))
            i = rng.randrange(n)
            xn = x.copy()
            xn[i] ^= 1
            En = energy(Q, xn)
            if En <= E or rng.random() < math.exp(-(En - E) / max(t, 1e-9)):
                x, E = xn, En

        samples.append(x)
        energies.append(E)

    return np.array(samples), np.array(energies)

# ============================================================
# Excel load helpers
# ============================================================
S_INNEN = "十二因縁と12誓願の統合"
S_CHAR3 = "12神の本質・性格・3軸ベクトルとその説明"
S_MAT_DIST = "神と誓願の因果律マトリクス（距離ベース） "
S_MAT_MEAN = "神と誓願の因果律マトリクス（意味ベース）  "

def norm_col(s: str) -> str:
    s = str(s or "")
    s = s.replace("　", " ").strip()
    s = s.upper()
    s = re.sub(r"[\s\-]+", "_", s)
    s = s.replace("＿", "_")
    return s

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def make_seed(s: str) -> int:
    import zlib
    return int(zlib.adler32(s.encode("utf-8")) & 0xFFFFFFFF)

def softmax(x: np.ndarray, tau: float = 1.0) -> np.ndarray:
    """Softmax function with temperature parameter"""
    x = np.array(x, dtype=float)
    tau = max(1e-6, float(tau))
    z = (x - np.max(x)) / tau
    e = np.exp(z)
    return e / np.sum(e)

def load_quotes(quotes_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """QUOTESシートを読み込んで正規化"""
    if quotes_df is None or len(quotes_df) == 0:
        return pd.DataFrame(
            [
                ("Q_0001", "成功は、自分の強みを活かすことから始まる。", "ピーター・ドラッカー", "ja"),
                ("Q_0002", "困難な瞬間こそ、真の性格が現れる。", "アルフレッド・A・モンテパート", "ja"),
                ("Q_0003", "幸福とは、自分自身を探す旅の中で見つけるものだ。", "リリアン・デュ・デュヴェル", "ja"),
            ],
            columns=["QUOTE_ID", "QUOTE", "SOURCE", "LANG"],
        )

    try:
        cols = {norm_col(c): c for c in quotes_df.columns}
        qid = cols.get("QUOTE_ID") or cols.get("ID") or cols.get("Q_ID")
        qt = cols.get("QUOTE") or cols.get("格言") or cols.get("言葉") or cols.get("テキスト")
        src = cols.get("SOURCE") or cols.get("出典") or cols.get("作者") or cols.get("出所")
        lang = cols.get("LANG") or cols.get("LANGUAGE")

        # 必須列のチェック
        if not qt:
            # QUOTE列が見つからない場合はデフォルトにフォールバック
            return pd.DataFrame(
                [
                    ("Q_0001", "成功は、自分の強みを活かすことから始まる。", "ピーター・ドラッカー", "ja"),
                    ("Q_0002", "困難な瞬間こそ、真の性格が現れる。", "アルフレッド・A・モンテパート", "ja"),
                    ("Q_0003", "幸福とは、自分自身を探す旅の中で見つけるものだ。", "リリアン・デュ・デュヴェル", "ja"),
                ],
                columns=["QUOTE_ID", "QUOTE", "SOURCE", "LANG"],
            )

        use = []
        for key, col in [("QUOTE_ID", qid), ("QUOTE", qt), ("SOURCE", src), ("LANG", lang)]:
            if col:
                use.append(col)

        tmp = quotes_df[use].copy()
        rename = {}
        if qid: rename[qid] = "QUOTE_ID"
        if qt:  rename[qt]  = "QUOTE"
        if src: rename[src] = "SOURCE"
        if lang:rename[lang]= "LANG"
        tmp = tmp.rename(columns=rename)
        if "LANG" not in tmp.columns:
            tmp["LANG"] = "ja"
        if "QUOTE_ID" not in tmp.columns:
            # QUOTE_IDがない場合は自動生成
            tmp["QUOTE_ID"] = [f"Q_{i+1:04d}" for i in range(len(tmp))]
        if "SOURCE" not in tmp.columns:
            # SOURCEがない場合は空文字列
            tmp["SOURCE"] = ""
        tmp["QUOTE"] = tmp["QUOTE"].astype(str).str.strip()
        tmp = tmp[tmp["QUOTE"].str.len() > 0].reset_index(drop=True)
        return tmp
    except Exception as e:
        # エラーが発生した場合はデフォルトにフォールバック
        return pd.DataFrame(
            [
                ("Q_0001", "成功は、自分の強みを活かすことから始まる。", "ピーター・ドラッカー", "ja"),
                ("Q_0002", "困難な瞬間こそ、真の性格が現れる。", "アルフレッド・A・モンテパート", "ja"),
                ("Q_0003", "幸福とは、自分自身を探す旅の中で見つけるものだ。", "リリアン・デュ・デュヴェル", "ja"),
            ],
            columns=["QUOTE_ID", "QUOTE", "SOURCE", "LANG"],
        )

def pick_quotes_by_temperature(dfq: pd.DataFrame, lang: str, k: int, tau: float, seed: int) -> pd.DataFrame:
    """温度パラメータを使ってQUOTESから格言を選択"""
    d = dfq.copy()
    d["LANG"] = d["LANG"].astype(str).str.strip().str.lower()
    lang = (lang or "ja").strip().lower()
    pool = d[d["LANG"].str.contains(lang, na=False)]
    if len(pool) < k:
        pool = d  # fallback

    rng = np.random.default_rng(seed)
    # pseudo-score: length preference + small noise
    s = pool["QUOTE"].astype(str).str.len().values.astype(float)
    s = (s - s.mean()) / (s.std() + 1e-6)
    s = -np.abs(s) + rng.normal(0, 0.35, size=len(pool))
    p = softmax(s, tau=max(0.2, float(tau)))
    idx = rng.choice(np.arange(len(pool)), size=min(k, len(pool)), replace=False, p=p)
    out = pool.iloc[idx].copy().reset_index(drop=True)
    return out

def render_dataframe_as_html_table(df: pd.DataFrame, max_rows: Optional[int] = None) -> str:
    """
    DataFrameをHTMLテーブルとして表示（白文字・黒背景で確実に）
    """
    from html import escape
    if df is None or len(df) == 0:
        return "<div style='color:rgba(245,245,255,0.95);'>データがありません。</div>"
    
    df_display = df.head(max_rows) if max_rows else df
    
    html = """
    <div style='overflow-x:auto; border-radius:8px; border:1px solid rgba(255,255,255,0.15); background:rgba(10,12,26,0.95);'>
    <table style='width:100%; border-collapse:collapse; color:rgba(245,245,255,0.95);'>
    <thead>
    <tr style='background:rgba(15,18,35,0.98); border-bottom:1px solid rgba(255,255,255,0.15);'>
    """
    
    for col in df_display.columns:
        html += f"<th style='padding:12px 16px; text-align:left; font-weight:600; color:rgba(245,245,255,1); border-bottom:1px solid rgba(255,255,255,0.15);'>{escape(str(col))}</th>"
    
    html += """
    </tr>
    </thead>
    <tbody>
    """
    
    for _, row in df_display.iterrows():
        html += "<tr style='border-bottom:1px solid rgba(255,255,255,0.08);'>"
        for col in df_display.columns:
            val = row[col]
            if pd.notna(val):
                # 数値の場合は適切にフォーマット
                if isinstance(val, (int, float)):
                    if isinstance(val, float):
                        val_str = f"{val:.3f}" if abs(val) < 1000 else f"{val:.2f}"
                    else:
                        val_str = str(val)
                else:
                    val_str = str(val)
            else:
                val_str = ""
            val_escaped = escape(val_str)
            html += f"<td style='padding:12px 16px; color:rgba(245,245,255,0.95); background:rgba(10,12,26,0.95);'>{val_escaped}</td>"
        html += "</tr>"
    
    html += """
    </tbody>
    </table>
    </div>
    """
    
    return html

@st.cache_data(show_spinner=False)
def load_excel_pack(excel_bytes: bytes, file_hash: str):
    bio = io.BytesIO(excel_bytes)
    xls = pd.ExcelFile(bio)
    out = {}
    # デバッグ: すべてのシート名を確認
    all_sheet_names_from_excel = xls.sheet_names
    for name in all_sheet_names_from_excel:
        try:
            df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=name, engine="openpyxl")
            out[name] = df
        except Exception as e:
            # エラーが発生したシートはスキップ
            continue
    return out

def find_sheet(sheets: dict, candidates):
    cand_norm = [norm_col(c) for c in candidates]
    for k, df in sheets.items():
        if norm_col(k) in cand_norm:
            return k, df
    # fallback: contains match
    for k, df in sheets.items():
        nk = norm_col(k)
        for c in cand_norm:
            if c and c in nk:
                return k, df
    return None, None

def detect_vow_columns(df: pd.DataFrame):
    cols = list(df.columns)
    normed = [norm_col(c) for c in cols]
    vow_cols = []
    for c, nc in zip(cols, normed):
        if re.fullmatch(r"VOW_?\d{1,2}", nc):
            vow_cols.append(c)
        elif re.fullmatch(r"VOW_?\d{1,2}\.0", nc):
            vow_cols.append(c)
    if not vow_cols:
        for c, nc in zip(cols, normed):
            if "VOW" in nc and re.search(r"\d", nc):
                vow_cols.append(c)
    def vow_key(col):
        m = re.search(r"(\d{1,2})", norm_col(col))
        return int(m.group(1)) if m else 999
    vow_cols = sorted(list(dict.fromkeys(vow_cols)), key=vow_key)
    return vow_cols

def pick_col(df: pd.DataFrame, candidates, sheet_name: str):
    mp = {}
    for c in df.columns:
        nc = norm_col(c)
        if nc not in mp:
            mp[nc] = c
    for cand in candidates:
        nc = norm_col(cand)
        if nc in mp:
            return mp[nc]
    st.error(f"Excelシート『{sheet_name}』に必要な列が見つかりません。候補={candidates}\n検出列={list(df.columns)}")
    st.stop()

def to_vow_id(x) -> str:
    s = str(x or "").strip()
    m = re.search(r"(\d{1,2})", s)
    if m:
        return f"VOW_{int(m.group(1)):02d}"
    return norm_col(s)

def to_char_id(x) -> str:
    s = str(x or "").strip()
    m = re.search(r"(\d{1,2})", s)
    if m:
        return f"CHAR_{int(m.group(1)):02d}"
    return norm_col(s)

def must_columns(df: pd.DataFrame, cols, sheet_name: str):
    miss = [c for c in cols if c not in df.columns]
    if miss:
        st.error(f"Excelシート『{sheet_name}』に必要な列がありません: {miss}")
        st.stop()

def safe_float(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default

def unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v if n < 1e-12 else (v / n)

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = unit(a)
    b = unit(b)
    d = float(np.dot(a, b))
    return max(-1.0, min(1.0, d))

def normalize01(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, float)
    mn, mx = float(np.min(v)), float(np.max(v))
    if mx - mn < 1e-12:
        return np.zeros_like(v)
    return (v - mn) / (mx - mn)

# ============================================================
# Text input and keyword extraction
# ============================================================
STOP_TOKENS = set([
    "した","たい","いる","こと","それ","これ","ため","よう","ので","から",
    "です","ます","ある","ない","そして","でも","しかし","また",
    "自分","私","あなた","もの","感じ","気持ち","今日",
    "に","を","が","は","と","も","で","へ","や","の",
])

def extract_keywords(text: str, top_n: int = 6) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    # split by punctuation/spaces
    cleaned = re.sub(r"[0-9０-９、。．,.!！?？\(\)\[\]{}「」『』\"'：:;／/\\\n\r\t]+", " ", text)
    toks = [t.strip() for t in re.split(r"\s+", cleaned) if t.strip()]
    toks = [t for t in toks if (len(t) >= 2 and t not in STOP_TOKENS)]
    if not toks:
        return []
    # prioritize longer tokens
    toks = sorted(list(dict.fromkeys(toks)), key=lambda s: (-len(s), s))
    return toks[:top_n]

def text_to_vow_vec(text: str, vows_df: pd.DataFrame, vow_cols: List[str], ngram: int = 3) -> np.ndarray:
    text = (text or "").strip()
    if not text:
        return np.zeros(len(vow_cols), dtype=float)
    
    # build tokens by char ngram
    t = re.sub(r"\s+", "", text)
    grams = []
    n = max(1, int(ngram))
    if len(t) <= n:
        grams = [t]
    else:
        grams = [t[i:i+n] for i in range(len(t)-n+1)]
    
    # score vow title hits
    scores = np.zeros(len(vow_cols), dtype=float)
    titles = vows_df["TITLE"].astype(str).tolist() if "TITLE" in vows_df.columns else []
    for i, title in enumerate(titles[:len(vow_cols)]):
        tt = re.sub(r"\s+", "", str(title))
        hit = 0
        for g in grams:
            if g and g in tt:
                hit += 1
        scores[i] = hit
    
    # normalize to 0..1 scale
    if scores.max() > 0:
        scores = scores / scores.max()
    return scores

# ============================================================
# Word sphere art
# ============================================================
GLOBAL_WORDS_DATABASE = [
    "世界平和","貢献","成長","学び","挑戦","夢","希望","未来",
    "感謝","愛","幸せ","喜び","安心","充実","満足","平和",
    "努力","継続","忍耐","誠実","正直","優しさ","思いやり","共感",
    "調和","バランス","自然","美","真実","自由","正義","道",
    "絆","つながり","家族","友人","仲間","信頼","尊敬","協力",
    "今","瞬間","過程","変化","進化","発展","循環","流れ",
    "静けさ","集中","覚悟","決意","勇気","強さ","柔軟性","寛容",
]

CATEGORIES = {
    "願い": ["世界平和","貢献","成長","夢","希望","未来"],
    "感情": ["感謝","愛","幸せ","喜び","安心","満足","平和"],
    "行動": ["努力","継続","忍耐","誠実","正直","挑戦","学び"],
    "哲学": ["調和","バランス","自然","美","道","真実","自由","正義"],
    "関係": ["絆","つながり","家族","友人","仲間","信頼","尊敬","協力"],
    "内的": ["静けさ","集中","覚悟","決意","勇気","強さ","柔軟性","寛容"],
    "時間": ["今","瞬間","過程","変化","進化","発展","循環","流れ"],
}

def calculate_semantic_similarity(word1: str, word2: str) -> float:
    if word1 == word2:
        return 1.0
    common_chars = set(word1) & set(word2)
    char_sim = len(common_chars) / max(len(set(word1)), len(set(word2)), 1)
    
    category_sim = 0.0
    for _, ws in CATEGORIES.items():
        w1_in = word1 in ws
        w2_in = word2 in ws
        if w1_in and w2_in:
            category_sim = 1.0
            break
        elif w1_in or w2_in:
            category_sim = max(category_sim, 0.3)
    
    len_sim = 1.0 - abs(len(word1) - len(word2)) / max(len(word1), len(word2), 1)
    similarity = 0.4 * char_sim + 0.4 * category_sim + 0.2 * len_sim
    return float(np.clip(similarity, 0.0, 1.0))

def energy_between(word1: str, word2: str, rng: np.random.Generator, jitter: float) -> float:
    sim = calculate_semantic_similarity(word1, word2)
    e = -2.0 * sim + 0.5
    if jitter > 0:
        e += rng.normal(0, jitter)
    return float(e)

def build_word_network(center_words: List[str], n_total: int, rng: np.random.Generator, jitter: float) -> Dict:
    base = list(dict.fromkeys(center_words + GLOBAL_WORDS_DATABASE))
    energies = {}
    for w in base:
        if w in center_words:
            energies[w] = -3.0
        else:
            e_list = [energy_between(c, w, rng, jitter) for c in center_words] if center_words else [0.0]
            energies[w] = float(np.mean(e_list))
    # pick low energy words
    picked = [w for w, _ in sorted(energies.items(), key=lambda x: x[1])]
    selected = []
    for w in center_words:
        if w in picked and w not in selected:
            selected.append(w)
    for w in picked:
        if w not in selected:
            selected.append(w)
        if len(selected) >= n_total:
            break
    
    # edges: connect strongly related pairs
    edges = []
    for i in range(len(selected)):
        for j in range(i+1, len(selected)):
            e = energy_between(selected[i], selected[j], rng, jitter=0.0)
            if e < -0.65:
                edges.append((i, j, float(e)))
    return {"words": selected, "energies": {w: energies[w] for w in selected}, "edges": edges}

def layout_sphere(words: List[str], energies: Dict[str,float], center_words: List[str], rng: np.random.Generator) -> np.ndarray:
    n = len(words)
    pos = np.zeros((n,3), dtype=float)
    # golden spiral on sphere-ish
    ga = np.pi * (3 - np.sqrt(5))
    for k in range(n):
        y = 1 - (2*k)/(max(1, n-1))
        r = np.sqrt(max(0.0, 1 - y*y))
        th = ga*k
        x = np.cos(th)*r
        z = np.sin(th)*r
        
        w = words[k]
        e = energies.get(w, 0.0)
        # lower energy -> closer to center
        rad = 0.55 + min(2.4, max(0.1, (e+3.0)))  # e around [-3..]
        rad = np.clip(rad, 0.45, 2.6)
        pos[k] = np.array([x,y,z]) * rad
    
    # pull center words closer to origin
    for i,w in enumerate(words):
        if w in set(center_words):
            pos[i] *= 0.35
    # tiny noise for aesthetics but stable by seed
    pos += rng.normal(0, 0.015, size=pos.shape)
    return pos

def plot_word_sphere(center_words: List[str], user_keywords: List[str], seed: int, star_count: int = 700) -> go.Figure:
    rng = np.random.default_rng(seed)
    center = [w for w in user_keywords if w] or center_words[:1]
    network = build_word_network(center, n_total=34, rng=rng, jitter=0.06)
    words = network["words"]
    energies = network["energies"]
    edges = network["edges"]
    pos = layout_sphere(words, energies, center, rng)
    
    fig = go.Figure()
    
    # stars
    sr = np.random.default_rng(12345)
    sx = sr.uniform(-3.2, 3.2, star_count)
    sy = sr.uniform(-2.4, 2.4, star_count)
    sz = sr.uniform(-2.0, 2.0, star_count)
    alpha = np.full(star_count, 0.20, dtype=float)
    star_size = sr.uniform(1.0, 2.2, star_count)
    star_colors = [f"rgba(255,255,255,{a})" for a in alpha]
    fig.add_trace(go.Scatter3d(
        x=sx,y=sy,z=sz, mode="markers",
        marker=dict(size=star_size, color=star_colors),
        hoverinfo="skip", showlegend=False
    ))
    
    # edges
    xE,yE,zE = [],[],[]
    for i,j,e in edges:
        x0,y0,z0 = pos[i]
        x1,y1,z1 = pos[j]
        xE += [x0,x1,None]
        yE += [y0,y1,None]
        zE += [z0,z1,None]
    fig.add_trace(go.Scatter3d(
        x=xE,y=yE,z=zE, mode="lines",
        line=dict(width=1, color="rgba(200,220,255,0.20)"),
        hoverinfo="skip", showlegend=False
    ))
    
    # nodes
    center_set = set(center)
    sizes, colors, labels = [], [], []
    for w in words:
        e = energies.get(w, 0.0)
        if w in center_set:
            sizes.append(26)
            colors.append("rgba(255,235,100,0.98)")
            labels.append(w)
        else:
            sizes.append(10 + int(7*min(1.0, abs(e)/3.0)))
            colors.append("rgba(220,240,255,0.70)" if e < -0.8 else "rgba(255,255,255,0.55)")
            labels.append(w)
    
    idx_center = np.array([i for i,w in enumerate(words) if w in center_set], dtype=int)
    idx_other  = np.array([i for i,w in enumerate(words) if w not in center_set], dtype=int)
    
    if len(idx_other) > 0:
        fig.add_trace(go.Scatter3d(
            x=pos[idx_other,0], y=pos[idx_other,1], z=pos[idx_other,2],
            mode="markers+text",
            text=[labels[i] for i in idx_other],
            textposition="top center",
            textfont=dict(size=14, color="rgba(245,245,255,0.92)"),
            marker=dict(size=[sizes[i] for i in idx_other], color=[colors[i] for i in idx_other],
                        line=dict(width=1, color="rgba(0,0,0,0.10)")),
            hovertemplate="<b>%{text}</b><extra></extra>",
            showlegend=False
        ))
    
    if len(idx_center) > 0:
        fig.add_trace(go.Scatter3d(
            x=pos[idx_center,0], y=pos[idx_center,1], z=pos[idx_center,2],
            mode="markers+text",
            text=[labels[i] for i in idx_center],
            textposition="top center",
            textfont=dict(size=20, color="rgba(255,80,80,1.0)"),
            marker=dict(size=[sizes[i] for i in idx_center], color=[colors[i] for i in idx_center],
                        line=dict(width=2, color="rgba(255,80,80,0.85)")),
            hovertemplate="<b>%{text}</b><br>中心語<extra></extra>",
            showlegend=False
        ))
    
    fig.update_layout(
        paper_bgcolor="rgba(6,8,18,1)",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(6,8,18,1)",
            camera=dict(eye=dict(x=1.55, y=1.10, z=1.05)),
            dragmode="orbit",
        ),
        margin=dict(l=0,r=0,t=0,b=0),
        height=520
    )
    return fig

# ============================================================
# UI
# ============================================================
st.title("🔮 Q-Quest-QUBO｜量子神託（3軸→誓願→QUBO one-hot）")

with st.sidebar:
    st.header("📁 データ")
    excel_file = st.file_uploader("統合Excel（20260305 版）", type=["xlsx"])

    st.header("🧭 方式選択")
    mat_mode = st.radio(
        "神×誓願 相性表",
        ["距離ベース（3軸の近さ）", "意味ベース（ロア共鳴）"],
        index=0,
    )

    st.header("⚙ QUBO設定")
    P_user = st.slider("one-hot ペナルティ P", 1.0, 200.0, 40.0, 1.0)
    num_reads = st.slider("サンプル数", 50, 800, 240, 10)
    sweeps = st.slider("SA sweeps", 50, 1500, 420, 10)
    seed = st.number_input("乱数シード", min_value=0, max_value=999999, value=0, step=1)

    run = st.button("🧪 QUBOで観測")

if excel_file is None:
    st.info("左サイドバーから **統合Excel（20260305版）** をアップロードしてください。")
    st.stop()

# ============================================================
# Excel parse
# ============================================================
excel_bytes = excel_file.getvalue()
file_hash = sha256_hex(excel_bytes)
sheets = load_excel_pack(excel_bytes, file_hash)

name_innen, df_innen = find_sheet(sheets, [S_INNEN, "十二因縁と12誓願の統合 ", "十二因縁と１２誓願の統合"])
name_char3, df_char3 = find_sheet(sheets, [S_CHAR3, "12神の本質・性格・3軸ベクトルとその説明 ", "１２神の本質・性格・３軸ベクトルとその説明"])
if mat_mode.startswith("距離"):
    mat_candidates = [S_MAT_DIST, "神と誓願の因果律マトリクス（距離ベース）"]
else:
    mat_candidates = [S_MAT_MEAN, "神と誓願の因果律マトリクス（意味ベース）"]
name_mat, df_mat = find_sheet(sheets, mat_candidates)

# QUOTESシート（任意）- より柔軟な検索
# まず、find_sheet関数を使って検索（app_qubo.pyと同じ方法）
quotes_candidates = ["QUOTES", "QUOTE", "格言", "格言一覧", "Quotes", "quotes"]
name_quotes, df_quotes_raw = find_sheet(sheets, quotes_candidates)

# find_sheetで見つからなかった場合、より柔軟な検索を試みる
if df_quotes_raw is None:
    all_sheet_names = list(sheets.keys())
    # 方法1: 部分一致（"quote"または"格言"が含まれているかチェック）
    for sheet_name in all_sheet_names:
        sheet_name_clean = str(sheet_name).strip().lower()
        if "quote" in sheet_name_clean or "格言" in sheet_name_clean:
            name_quotes = sheet_name
            df_quotes_raw = sheets[sheet_name]
            break

# 方法2: Excelファイルから直接シート名を取得して検索（最後の手段）
if df_quotes_raw is None:
    try:
        bio = io.BytesIO(excel_bytes)
        xls = pd.ExcelFile(bio)
        excel_sheet_names = xls.sheet_names
        # Excelファイルから直接取得したシート名で検索
        for excel_sheet_name in excel_sheet_names:
            excel_sheet_clean = str(excel_sheet_name).strip()
            excel_sheet_norm = norm_col(excel_sheet_clean)
            excel_sheet_lower = excel_sheet_clean.lower()
            # "QUOTE"または"格言"が含まれているかチェック
            if ("quote" in excel_sheet_lower or "格言" in excel_sheet_name or 
                "QUOTE" in excel_sheet_norm):
                # このシート名で読み込みを試みる
                try:
                    df_temp = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=excel_sheet_name, engine="openpyxl")
                    if df_temp is not None and len(df_temp) > 0:
                        name_quotes = excel_sheet_name
                        df_quotes_raw = df_temp
                        # sheetsにも追加（次回の検索で見つかるように）
                        sheets[excel_sheet_name] = df_temp
                        break
                except Exception:
                    continue
    except Exception:
        pass

# デバッグ用：すべてのシート名を確認
all_sheet_names = list(sheets.keys())

# デバッグ情報（開発用）
if df_quotes_raw is None:
    st.sidebar.warning(f"⚠️ QUOTESシートが見つかりません。\n検出されたシート: {', '.join(all_sheet_names[:15])}")
    # より詳細なデバッグ情報
    with st.sidebar.expander("🔍 シート検索の詳細", expanded=True):
        st.write(f"**検索候補**: {quotes_candidates}")
        st.write(f"**検出されたシート数**: {len(all_sheet_names)}")
        st.write(f"**すべてのシート名（読み込み済み）**:")
        for i, sn in enumerate(all_sheet_names, 1):
            sn_norm = norm_col(sn)
            st.write(f"{i}. `{sn}` (正規化: `{sn_norm}`)")
            # "QUOTE"が含まれているかチェック
            if "QUOTE" in sn_norm or "quote" in str(sn).lower() or "格言" in str(sn):
                st.write(f"   ⚠️ このシートはQUOTESの可能性があります！")
        
        # Excelファイルから直接取得したシート名も表示
        try:
            bio = io.BytesIO(excel_bytes)
            xls = pd.ExcelFile(bio)
            excel_sheet_names = xls.sheet_names
            st.write(f"**Excelファイルから直接取得したシート名（全{len(excel_sheet_names)}件）**:")
            for i, esn in enumerate(excel_sheet_names, 1):
                esn_norm = norm_col(esn)
                esn_lower = str(esn).lower()
                esn_repr = repr(esn)  # 見えない文字を確認するため
                st.write(f"{i}. `{esn}` (正規化: `{esn_norm}`, repr: `{esn_repr}`)")
                # "QUOTE"が含まれているかチェック
                if "QUOTE" in esn_norm or "quote" in esn_lower or "格言" in str(esn):
                    st.write(f"   ⚠️ **このシートはQUOTESの可能性があります！**")
                    # このシートが読み込み済みシートに含まれているかチェック
                    if esn not in all_sheet_names:
                        st.write(f"   ⚠️ しかし、このシートは読み込み済みシートに含まれていません！")
                        # このシートを読み込もうとする
                        try:
                            st.write(f"   🔄 このシートを読み込もうとしています...")
                            df_test = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=esn, engine="openpyxl")
                            if df_test is not None and len(df_test) > 0:
                                st.write(f"   ✅ 読み込み成功！行数: {len(df_test)}, 列数: {len(df_test.columns)}")
                                st.write(f"   📋 列名: {list(df_test.columns)}")
                        except Exception as e:
                            st.write(f"   ❌ 読み込みエラー: {e}")
            
            # QUOTESシートが見つからない場合の追加情報
            st.write(f"**⚠️ QUOTESシートが見つかりませんでした。**")
            st.write(f"以下の可能性があります：")
            st.write(f"1. ExcelファイルにQUOTESシートが存在しない")
            st.write(f"2. QUOTESシートの名前が異なる（例：全角スペース、特殊文字など）")
            st.write(f"3. QUOTESシートが非表示になっている")
            st.write(f"4. Excelファイルが古いバージョンで、QUOTESシートがまだ追加されていない")
            st.write(f"")
            st.write(f"**対処方法：**")
            st.write(f"1. Excelファイルを開いて、QUOTESシートが存在するか確認してください")
            st.write(f"2. QUOTESシートが存在する場合、シート名を正確に「QUOTES」にしてください")
            st.write(f"3. QUOTESシートが非表示になっている場合、表示してください")
            st.write(f"4. Excelファイルを保存して、再度アップロードしてください")
        except Exception as e:
            st.write(f"Excelファイルの読み込みエラー: {e}")
else:
    st.sidebar.success(f"✅ QUOTESシートを検出: `{name_quotes}`")

if df_innen is None or df_char3 is None or df_mat is None:
    st.error(
        "必須シートが見つかりません。\n"
        f"- 内訳: innen={name_innen}, char3={name_char3}, mat={name_mat}\n"
        f"- 検出シート: {list(sheets.keys())}"
    )
    st.stop()

# QUOTESシートの読み込み
df_quotes = load_quotes(df_quotes_raw)
if df_quotes_raw is not None and len(df_quotes) > 0:
    st.sidebar.success(f"✅ QUOTESシート読み込み完了（{len(df_quotes)}件の格言）")
    # QUOTESシートの構造を確認
    required_cols = ["QUOTE_ID", "QUOTE", "SOURCE", "LANG"]
    missing_cols = [c for c in required_cols if c not in df_quotes.columns]
    if missing_cols:
        st.sidebar.warning(f"⚠️ QUOTESシートに推奨列が不足: {missing_cols}")
    else:
        st.sidebar.info(f"📋 QUOTESシート構造: {', '.join(df_quotes.columns.tolist())}")
elif df_quotes_raw is None:
    st.sidebar.info("ℹ️ QUOTESシートが見つかりません（任意）")

# Innen: required cols (lenient)
col_vow_id = pick_col(df_innen, ["VOW_ID", "VOWID", "誓願ID", "誓願_ID", "誓願"], name_innen)
col_title = pick_col(df_innen, ["TITLE", "タイトル", "題", "題名"], name_innen)
col_subtitle = pick_col(df_innen, ["SUBTITLE", "サブタイトル", "副題", "補足"], name_innen)
col_innen = pick_col(df_innen, ["十二因縁", "12因縁"], name_innen)
col_modern = pick_col(df_innen, ["この段で起きがちなこと（現代語）", "この段で起きがちなこと", "現代語"], name_innen)
col_intervene = pick_col(df_innen, ["つながりの理由（介入点）", "つながりの理由", "介入点"], name_innen)

df_innen = df_innen.copy()
df_innen["VOW_ID_N"] = df_innen[col_vow_id].apply(to_vow_id)

# Char3: required cols (lenient)
col_char_id = pick_col(df_char3, ["ID", "CHAR_ID", "神ID", "キャラID"], name_char3)
col_god_name = pick_col(df_char3, ["神名", "公式キャラ名", "キャラ名", "NAME"], name_char3)
col_ax1 = pick_col(df_char3, ["(-)顕:密(+)", "顕:密", "顕密", "存在"], name_char3)
col_ax2 = pick_col(df_char3, ["(-)智:悲(+)", "智:悲", "智悲", "作用"], name_char3)
col_ax3 = pick_col(df_char3, ["(-)和:荒(+)", "和:荒", "和荒", "魂"], name_char3)
col_tip = pick_col(df_char3, ["性格・口調ヒント", "性格口調ヒント", "口調ヒント", "性格"], name_char3)

# Matrix: required cols (lenient)
col_m_char_id = pick_col(df_mat, ["CHAR_ID", "ID", "キャラID", "神ID"], name_mat)
col_m_img = pick_col(df_mat, ["IMAGE_FILE", "IMAGE", "画像", "画像ファイル", "ファイル名"], name_mat)
col_m_name = pick_col(df_mat, ["公式キャラ名", "神名", "キャラ名", "NAME"], name_mat)

vow_cols_raw = detect_vow_columns(df_mat)
if len(vow_cols_raw) < 12:
    st.error(f"相性表の誓願列（VOW系）が 12 本未満です（検出={len(vow_cols_raw)}）: {vow_cols_raw}")
    st.stop()
if len(vow_cols_raw) > 12:
    vow_cols_raw = vow_cols_raw[:12]

vow_ids = [to_vow_id(c) for c in vow_cols_raw]

# 12神（相性表側の行）
char_names = df_mat[col_m_name].astype(str).tolist()
img_files = df_mat[col_m_img].astype(str).tolist()
W = df_mat[vow_cols_raw].fillna(0).to_numpy(float)  # (12, 12)

# 3軸（IDで join）
df_axes = df_char3[[col_char_id, col_god_name, col_ax1, col_ax2, col_ax3, col_tip]].copy()
df_axes[col_char_id] = df_axes[col_char_id].astype(str)
df_axes["CHAR_ID_N"] = df_axes[col_char_id].apply(to_char_id)
axes_map = {r["CHAR_ID_N"]: r for _, r in df_axes.iterrows()}
# 相性表順に並べた軸ベクトル
char_axes = []
char_tips = []
for cid in df_mat[col_m_char_id].astype(str).tolist():
    r = axes_map.get(to_char_id(cid))
    if r is None:
        char_axes.append([0.0, 0.0, 0.0])
        char_tips.append("")
    else:
        char_axes.append([safe_float(r[col_ax1]), safe_float(r[col_ax2]), safe_float(r[col_ax3])])
        char_tips.append(str(r.get(col_tip, "")))
char_axes = np.array(char_axes, float)  # (12, 3)

# 誓願辞書（タイトル）
vow_dict = df_innen.drop_duplicates(subset=["VOW_ID_N"])[["VOW_ID_N", col_title, col_subtitle]].copy()
vow_title = {r["VOW_ID_N"]: str(r[col_title]) for _, r in vow_dict.iterrows()}
vow_sub = {r["VOW_ID_N"]: str(r[col_subtitle]) for _, r in vow_dict.iterrows()}

# ============================================================
# Step0: テキスト入力（app_qubo.py仕様）
# ============================================================
st.subheader("📝 テキスト入力（任意）")

user_text = st.text_area(
    "今日の悩み・気持ちを一文でどうぞ",
    value=st.session_state.get("user_text", ""),
    height=100,
    placeholder="例：疲れていて決断ができない…",
    key="user_text_input"
)
st.session_state["user_text"] = user_text

# テキストから誓願ベクトルを計算（app_qubo.py仕様）
vow_dict_df = df_innen.drop_duplicates(subset=["VOW_ID_N"])[[col_title]].copy()
vow_dict_df["TITLE"] = vow_dict_df[col_title].astype(str)
text_vow_vec = text_to_vow_vec(user_text, vow_dict_df, vow_ids, ngram=3) if user_text else np.zeros(len(vow_ids), dtype=float)

# ============================================================
# Step1: 3軸入力
# ============================================================
st.subheader("① 3軸スライダー（顕↔密 / 智↔悲 / 和↔荒）")

col1, col2, col3 = st.columns(3)
with col1:
    a_exist = st.slider("存在：(-)顕 ↔ 密(+)", -1.0, 1.0, 0.0, 0.1)
with col2:
    a_act = st.slider("作用：(-)智 ↔ 悲(+)", -1.0, 1.0, 0.0, 0.1)
with col3:
    a_soul = st.slider("魂：(-)和 ↔ 荒(+)", -1.0, 1.0, 0.0, 0.1)

u = np.array([a_exist, a_act, a_soul], float)
u_n = unit(u)

st.caption("※3軸は「神の性格座標」です。ユーザーの現在地（気分/状態）を座標として入力します。")

# ============================================================
# Step2: 3軸 → 12誓願（予測）
# ============================================================
st.subheader("② 予測12誓願（3軸 → 誓願ベクトル推定）")

# 誓願の「3軸ベクトル」を相性表 W と 12神軸 char_axes から推定：
# vow_vec[j] = Σ_i max(W[i,j],0) * char_axes[i]
# ユーザー座標 u と vow_vec の cos を誓願必要度とする
vow_vecs = []
n_vows = len(vow_ids)  # vow_ids の長さ（通常12）
for j in range(n_vows):
    w = np.maximum(W[:, j], 0.0)
    if float(np.sum(w)) < 1e-12:
        vv = np.zeros(3)
    else:
        vv = (w[:, None] * char_axes).sum(axis=0) / float(np.sum(w))
    vow_vecs.append(unit(vv))
vow_vecs = np.array(vow_vecs, float)  # (n_vows, 3)

v_need = np.array([cosine(u_n, vow_vecs[j]) for j in range(n_vows)], float)
# cos(-1..1) → 0..1
v_need01 = (v_need + 1.0) / 2.0
v_user = normalize01(v_need01)

vow_table = []
for j, vid in enumerate(vow_ids):
    vow_table.append({
        "VOW_ID": vid,
        "TITLE": vow_title.get(vid, vid),
        "SUBTITLE": vow_sub.get(vid, ""),
        "need(0-1)": float(v_user[j]),
        "raw_cos": float(v_need[j]),
    })
df_vpred = pd.DataFrame(vow_table).sort_values("need(0-1)", ascending=False)

# HTMLテーブルとして表示（白文字・黒背景で確実に）
html_table_vpred = render_dataframe_as_html_table(df_vpred[["VOW_ID", "TITLE", "SUBTITLE", "need(0-1)"]])
st.markdown(html_table_vpred, unsafe_allow_html=True)

st.caption("※「誓願＝介入メニュー」。3軸の現在地から、今必要になりやすい誓願を推定しています（説明可能性のためのモデル化）。")

# ============================================================
# Step2.5: キーワード抽出と球体アート（app_qubo.py仕様）
# ============================================================
if user_text:
    st.subheader("🔍 キーワード抽出と球体アート")
    
    kw = extract_keywords(user_text, top_n=6)
    colA, colB = st.columns([1.0, 1.6], gap="large")
    with colA:
        st.markdown("### 抽出キーワード")
        if kw:
            st.markdown("**" + " / ".join(kw) + "**")
            st.caption("※簡易抽出です（形態素解析なし）。短文だと少なくなることがあります。")
        else:
            st.info("入力が短い/空のため、キーワードが抽出できません（2文字以上の語が必要です）。")
    
    with colB:
        st.markdown("### 🌐 単語の球体（誓願→キーワード→縁のネットワーク）")
        if kw:
            seed_sphere = make_seed(user_text + "|sphere")
            fig = plot_word_sphere(center_words=GLOBAL_WORDS_DATABASE, user_keywords=kw, seed=seed_sphere, star_count=850)
            st.plotly_chart(fig, use_container_width=True, config={
                "displayModeBar": True,
                "scrollZoom": True,
                "displaylogo": False,
                "doubleClick": "reset",
            })
        else:
            st.info("キーワードが抽出できませんでした。")

# ============================================================
# Step3: 12誓願 → 12神（QUBO one-hot）
# ============================================================
st.subheader("③ 12神をQUBOで観測（one-hot）")

# 線形スコア：神が得意な誓願に、必要度が乗るほど高得点
score = W @ v_user  # (12,)
linear_E = -score

P_min = float(np.max(np.abs(linear_E)) * 3.0 + 1.0)
P = max(float(P_user), P_min)
Q = build_qubo_onehot(linear_E, P)

st.caption(f"ペナルティPは自動下限 P_min={P_min:.2f} を確保しつつ、ユーザー指定と比較して採用します → P={P:.2f}")

if run:
    samples, Es = sa_sample(Q, num_reads=num_reads, sweeps=sweeps, seed=int(seed))

    idxs = [onehot_index(x) for x in samples]
    idxs = [k for k in idxs if k is not None]

    counts = np.zeros(len(char_names), int)
    for k in idxs:
        counts[k] += 1

    best_k = min(
        [(energy(Q, x), onehot_index(x)) for x in samples if onehot_index(x) is not None],
        key=lambda t: t[0],
    )[1]

    st.session_state["counts"] = counts
    st.session_state["best_k"] = int(best_k)
    st.session_state["P"] = float(P)
    st.session_state["v_user"] = v_user
    st.session_state["score"] = score

# ============================================================
# Result
# ============================================================
if "best_k" in st.session_state:
    k = int(st.session_state["best_k"])
    st.markdown("---")
    st.subheader("🌟 観測された神（QUBO解）")
    
    # キャラクター画像（左）と神託（右）を横並びに配置
    col_char, col_oracle = st.columns([1, 2])
    
    with col_char:
        st.write(f"**{char_names[k]}**")
        # 画像表示（assets パスは従来踏襲・小さく表示）
        img_path = Path("assets/images/characters") / img_files[k]
        if img_path.exists():
            st.image(Image.open(img_path), width=250)
        else:
            st.info(f"画像ファイルが見つかりませんでした: {img_path}")
        
        # 性格ヒント（3軸）
        ax = char_axes[k]
        st.write("**3軸（神の性格）**")
        st.write(
            f"- 存在（顕↔密）: {ax[0]:+.1f}\n"
            f"- 作用（智↔悲）: {ax[1]:+.1f}\n"
            f"- 魂（和↔荒）: {ax[2]:+.1f}"
        )
        if char_tips[k]:
            st.write("**性格・口調ヒント**")
            st.write(char_tips[k])
    
    with col_oracle:
        # 神託表示（右側）
        st.subheader("💬 神託（観測された神からのメッセージ）")
        v_user = st.session_state["v_user"]
        score = st.session_state["score"]
        contrib = W[k, :] * v_user  # (12,)
        order = np.argsort(contrib)[::-1]
        top_vid = vow_ids[order[0]]
        top_vow_title = vow_title.get(top_vid, top_vid)
        
        # シンプルな神託文を生成
        oracle_text = f"{char_names[k]}が語る：\n\n"
        oracle_text += f"「{top_vow_title}」という誓願が、今のあなたに響いています。\n\n"
        
        r = df_innen[df_innen["VOW_ID_N"].astype(str) == str(top_vid)]
        if len(r) >= 1:
            r0 = r.iloc[0]
            oracle_text += f"十二因縁の「{str(r0[col_innen])}」の段にいます。\n"
            oracle_text += f"この段で起きがちなこと：{str(r0[col_modern])}\n\n"
            oracle_text += f"介入点：{str(r0[col_intervene])}"
        
        st.markdown(
            f"<div style='background:rgba(40,120,80,0.40); border:1px solid rgba(80,200,140,0.60); padding:24px; border-radius:12px; color:rgba(245,255,250,1); line-height:1.9; margin-top:12px; box-shadow: 0 4px 20px rgba(40,120,80,0.3); white-space:pre-wrap;'>{oracle_text}</div>",
            unsafe_allow_html=True
        )

    # 観測分布
    st.subheader("📊 観測分布（サンプリング）")
    hist = pd.DataFrame({"神": char_names, "count": st.session_state["counts"]}).sort_values("count", ascending=False)
    st.bar_chart(hist.set_index("神"))

    # どの誓願に反応したか（上位）
    st.subheader("🧩 この神託が指している誓願（上位）")
    v_user = st.session_state["v_user"]
    score = st.session_state["score"]
    contrib = W[k, :] * v_user  # (12,)
    order = np.argsort(contrib)[::-1]
    topN = 4
    rows = []
    for idx in order[:topN]:
        vid = vow_ids[idx]
        rows.append({
            "VOW_ID": vid,
            "TITLE": vow_title.get(vid, vid),
            "need": float(v_user[idx]),
            "compat": float(W[k, idx]),
            "contrib": float(contrib[idx]),
        })
    df_top_vows = pd.DataFrame(rows)
    # HTMLテーブルとして表示（白文字・黒背景で確実に）
    html_table_top = render_dataframe_as_html_table(df_top_vows)
    st.markdown(html_table_top, unsafe_allow_html=True)
    
    # QUOTES神託（温度付きで選択）
    if len(df_quotes) > 0:
        st.subheader("📜 QUOTES神託（温度付きで選択）")
        quote_tau = st.slider("格言温度（高→ランダム / 低→上位固定）", 0.2, 2.5, 1.2, 0.1, key="quote_tau")
        # シードを温度と組み合わせて、温度が変わると格言も変わるようにする
        # 温度の値を使ってシードを生成（温度が変わると異なる格言が選ばれる）
        # 温度の値を小数点3桁まで含めてシードに含める
        # さらに、温度が変わったことを検知するために、前回の温度と比較
        if "last_quote_tau" not in st.session_state:
            st.session_state["last_quote_tau"] = quote_tau
            st.session_state["quote_seed_offset"] = 0
        
        # 温度が変わったら、シードオフセットを増やす（0.05以上の変化で検知）
        if abs(st.session_state.get("last_quote_tau", quote_tau) - quote_tau) > 0.05:
            st.session_state["quote_seed_offset"] = st.session_state.get("quote_seed_offset", 0) + 1
            st.session_state["last_quote_tau"] = quote_tau
        
        quote_seed_base = (user_text or "") + f"|quotes_temp|{quote_tau:.3f}|{seed}|offset_{st.session_state.get('quote_seed_offset', 0)}"
        quote_seed = make_seed(quote_seed_base)
        
        qpick_temp = pick_quotes_by_temperature(
            df_quotes,
            lang="ja",
            k=3,
            tau=quote_tau,
            seed=quote_seed,
        )
        
        if len(qpick_temp) > 0:
            for idx, row in qpick_temp.iterrows():
                quote_text = str(row.get("QUOTE", "")).strip()
                source_text = str(row.get("SOURCE", "")).strip()
                if quote_text:
                    quote_display = f"「{quote_text}」"
                    if source_text and source_text != "nan":
                        quote_display += f"\n\n— {source_text}"
                    st.markdown(
                        f"<div style='background:rgba(40,120,80,0.40); border:1px solid rgba(80,200,140,0.60); padding:24px; border-radius:12px; color:rgba(245,255,250,1); line-height:1.9; margin-top:12px; box-shadow: 0 4px 20px rgba(40,120,80,0.3); white-space:pre-wrap;'>{quote_display}</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.info("QUOTES神託が見つかりませんでした。")
    
    # 十二因縁ストーリー
    st.subheader("📜 十二因縁（診断）→ 誓願（介入）→ 神（語り手）")
    if len(r) >= 1:
        r0 = r.iloc[0]
        st.write(f"**今、強く出ている誓願**：{top_vow_title}")
        st.write(f"**対応する十二因縁**：{str(r0[col_innen])}")
        st.write(f"**現代語（起きがちなこと）**：{str(r0[col_modern])}")
        st.write(f"**介入点（つながりの理由）**：{str(r0[col_intervene])}")
    else:
        st.info("十二因縁シートに、上位誓願の対応行が見つかりませんでした。")

    # QUBO 証拠表示
    st.subheader("🧠 QUBO 証拠（one-hot）")
    x = [1 if i == k else 0 for i in range(len(char_names))]
    st.code(
        f"E(x)=ΣE_i x_i + P(Σx-1)^2\n"
        f"P={st.session_state['P']:.2f}\n"
        f"linear_E(=-score)={np.round((-score), 3).tolist()}\n"
        f"x={x}",
        language="text",
    )

else:
    st.info("左サイドバーで設定して、**🧪 QUBOで観測** を押してください。")
