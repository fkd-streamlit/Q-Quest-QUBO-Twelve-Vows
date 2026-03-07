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
from html import escape
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go

# ============================================================
# Streamlit config（必ず最初）
# ============================================================
st.set_page_config(
    page_title="Q-Quest-QUBO｜量子神託（3軸→誓願→QUBO）",
    layout="wide",
)

# ============================================================
# SAFE THEME / CSS
# ============================================================
SPACE_CSS = """
<style>
:root{
  --bg0: #060812;
  --bg1: #0a0c1a;
  --panel: rgba(12,16,30,0.92);
  --panel2: rgba(18,24,42,0.92);
  --text: rgba(245,245,255,0.96);
  --muted: rgba(210,220,240,0.78);
  --line: rgba(255,255,255,0.14);
  --accent: #7fb2ff;
  --accent2: #ff7b7f;
  --good: rgba(60,140,95,0.35);
}

/* app background */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 18% 24%, rgba(110,150,255,0.10), transparent 36%),
    radial-gradient(circle at 78% 68%, rgba(255,160,220,0.08), transparent 42%),
    linear-gradient(180deg, var(--bg0), var(--bg1)) !important;
  color: var(--text) !important;
}

/* main containers */
.main .block-container {
  padding-top: 1.2rem;
  color: var(--text);
}

/* header */
header[data-testid="stHeader"]{
  background: rgba(6,8,18,0.85) !important;
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
div[data-testid="stToolbar"]{
  background: transparent !important;
}
div[data-testid="stToolbar"] *{
  color: var(--text) !important;
  fill: var(--text) !important;
}

/* typography */
h1, h2, h3, h4, h5, h6,
p, li, label, span, div[data-testid="stMarkdownContainer"] * {
  color: var(--text) !important;
}
[data-testid="stCaption"], .stCaption, [data-testid="stCaption"] * {
  color: var(--muted) !important;
}

/* sidebar */
section[data-testid="stSidebar"]{
  background: rgba(8,10,22,0.96) !important;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}

/* inputs */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
  background: var(--panel) !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
input[type="text"], input[type="number"], textarea {
  color: var(--text) !important;
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
textarea::placeholder, input::placeholder{
  color: rgba(245,245,255,0.50) !important;
}

/* file uploader */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] > div {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
}
div[data-testid="stFileUploader"] *{
  color: var(--text) !important;
}

/* radio */
div[data-testid="stRadio"] > div {
  gap: 0.35rem;
}
div[data-testid="stRadio"] label {
  color: var(--text) !important;
}
[data-baseweb="radio"] * {
  color: var(--text) !important;
}

/* sliders */
div[data-testid="stSlider"] {
  padding-top: 0.15rem;
  padding-bottom: 0.45rem;
}
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] span,
div[data-testid="stSlider"] p {
  color: var(--text) !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
  background: rgba(255,255,255,0.18) !important;
}
div[data-testid="stSlider"] [role="slider"] {
  background: var(--accent2) !important;
  border: 2px solid #ffd6d6 !important;
  box-shadow: 0 0 0 2px rgba(255,123,127,0.20) !important;
  width: 18px !important;
  height: 18px !important;
}
div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
  color: var(--accent2) !important;
  font-weight: 700 !important;
}

/* buttons */
.stButton > button {
  border-radius: 12px !important;
  background: linear-gradient(90deg, #3b5ea8, #5d7fd0) !important;
  color: white !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
}
.stButton > button:hover {
  filter: brightness(1.08);
}

/* alerts */
div[data-testid="stAlert"],
div[data-baseweb="notification"] {
  background: var(--panel2) !important;
  border: 1px solid var(--line) !important;
  color: var(--text) !important;
}

/* expander */
div[data-testid="stExpander"] > details,
div[data-testid="stExpander"] > div {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
div[data-testid="stExpander"] * {
  color: var(--text) !important;
}

/* dataframe/table */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div {
  background: var(--panel) !important;
  border-radius: 12px !important;
  border: 1px solid var(--line) !important;
}
div[data-testid="stDataFrame"] * {
  color: var(--text) !important;
}
table, thead, tbody, tr, td, th {
  color: var(--text) !important;
}

/* plotly wrapper */
.js-plotly-plot, .plotly, .plot-container {
  background: transparent !important;
}
</style>
"""
st.markdown(SPACE_CSS, unsafe_allow_html=True)

# ============================================================
# Constants
# ============================================================
S_INNEN = "十二因縁と12誓願の統合"
S_CHAR3 = "12神の本質・性格・3軸ベクトルとその説明"
S_MAT_DIST = "神と誓願の因果律マトリクス（距離ベース） "
S_MAT_MEAN = "神と誓願の因果律マトリクス（意味ベース）  "

STOP_TOKENS = {
    "した","たい","いる","こと","それ","これ","ため","よう","ので","から",
    "です","ます","ある","ない","そして","でも","しかし","また",
    "自分","私","あなた","もの","感じ","気持ち","今日",
    "に","を","が","は","と","も","で","へ","や","の",
}

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

# ============================================================
# Basic helpers
# ============================================================
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
    return int(zlib.adler32(s.encode("utf-8")) & 0xFFFFFFFF)


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


def softmax(x: np.ndarray, tau: float = 1.0) -> np.ndarray:
    x = np.array(x, dtype=float)
    tau = max(1e-6, float(tau))
    z = (x - np.max(x)) / tau
    e = np.exp(z)
    return e / np.sum(e)

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
# Excel helpers
# ============================================================
@st.cache_data(show_spinner=False)
def load_excel_pack(excel_bytes: bytes, file_hash: str):
    bio = io.BytesIO(excel_bytes)
    xls = pd.ExcelFile(bio)
    out = {}
    for name in xls.sheet_names:
        try:
            out[name] = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=name, engine="openpyxl")
        except Exception:
            continue
    return out


def find_sheet(sheets: dict, candidates):
    cand_norm = [norm_col(c) for c in candidates]
    for k, df in sheets.items():
        if norm_col(k) in cand_norm:
            return k, df
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

    return sorted(list(dict.fromkeys(vow_cols)), key=vow_key)


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
    st.error(
        f"Excelシート『{sheet_name}』に必要な列が見つかりません。"
        f"\n候補={candidates}\n検出列={list(df.columns)}"
    )
    st.stop()

# ============================================================
# QUOTES helpers
# ============================================================
def load_quotes(quotes_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    fallback = pd.DataFrame(
        [
            ("Q_0001", "成功は、自分の強みを活かすことから始まる。", "ピーター・ドラッカー", "ja"),
            ("Q_0002", "困難な瞬間こそ、真の性格が現れる。", "アルフレッド・A・モンテパート", "ja"),
            ("Q_0003", "幸福とは、自分自身を探す旅の中で見つけるものだ。", "リリアン・デュ・デュヴェル", "ja"),
        ],
        columns=["QUOTE_ID", "QUOTE", "SOURCE", "LANG"],
    )

    if quotes_df is None or len(quotes_df) == 0:
        return fallback

    try:
        cols = {norm_col(c): c for c in quotes_df.columns}
        qid = cols.get("QUOTE_ID") or cols.get("ID") or cols.get("Q_ID")
        qt = cols.get("QUOTE") or cols.get("格言") or cols.get("言葉") or cols.get("テキスト")
        src = cols.get("SOURCE") or cols.get("出典") or cols.get("作者") or cols.get("出所")
        lang = cols.get("LANG") or cols.get("LANGUAGE")

        if not qt:
            return fallback

        use = []
        for _, col in [("QUOTE_ID", qid), ("QUOTE", qt), ("SOURCE", src), ("LANG", lang)]:
            if col:
                use.append(col)

        tmp = quotes_df[use].copy()
        rename = {}
        if qid:
            rename[qid] = "QUOTE_ID"
        if qt:
            rename[qt] = "QUOTE"
        if src:
            rename[src] = "SOURCE"
        if lang:
            rename[lang] = "LANG"
        tmp = tmp.rename(columns=rename)

        if "LANG" not in tmp.columns:
            tmp["LANG"] = "ja"
        if "QUOTE_ID" not in tmp.columns:
            tmp["QUOTE_ID"] = [f"Q_{i+1:04d}" for i in range(len(tmp))]
        if "SOURCE" not in tmp.columns:
            tmp["SOURCE"] = ""

        tmp["QUOTE"] = tmp["QUOTE"].astype(str).str.strip()
        tmp = tmp[tmp["QUOTE"].str.len() > 0].reset_index(drop=True)
        return tmp if len(tmp) > 0 else fallback
    except Exception:
        return fallback


def pick_quotes_by_temperature(dfq: pd.DataFrame, lang: str, k: int, tau: float, seed: int) -> pd.DataFrame:
    d = dfq.copy()
    d["LANG"] = d["LANG"].astype(str).str.strip().str.lower()
    lang = (lang or "ja").strip().lower()
    pool = d[d["LANG"].str.contains(lang, na=False)]
    if len(pool) < k:
        pool = d

    rng = np.random.default_rng(seed)
    s = pool["QUOTE"].astype(str).str.len().values.astype(float)
    s = (s - s.mean()) / (s.std() + 1e-6)
    s = -np.abs(s) + rng.normal(0, 0.35, size=len(pool))
    p = softmax(s, tau=max(0.2, float(tau)))
    idx = rng.choice(np.arange(len(pool)), size=min(k, len(pool)), replace=False, p=p)
    return pool.iloc[idx].copy().reset_index(drop=True)

# ============================================================
# Rendering helpers
# ============================================================
def render_dataframe_as_html_table(df: pd.DataFrame, max_rows: Optional[int] = None) -> str:
    if df is None or len(df) == 0:
        return "<div style='color:rgba(245,245,255,0.95);'>データがありません。</div>"

    df_display = df.head(max_rows) if max_rows else df

    html = """
    <div style='overflow-x:auto; border-radius:10px; border:1px solid rgba(255,255,255,0.15); background:rgba(10,12,26,0.95);'>
      <table style='width:100%; border-collapse:collapse; color:rgba(245,245,255,0.95);'>
        <thead>
          <tr style='background:rgba(15,18,35,0.98); border-bottom:1px solid rgba(255,255,255,0.15);'>
    """
    for col in df_display.columns:
        html += (
            f"<th style='padding:12px 16px; text-align:left; font-weight:600; "
            f"color:rgba(245,245,255,1); border-bottom:1px solid rgba(255,255,255,0.15);'>"
            f"{escape(str(col))}</th>"
        )

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
                if isinstance(val, (int, float)):
                    if isinstance(val, float):
                        val_str = f"{val:.3f}" if abs(val) < 1000 else f"{val:.2f}"
                    else:
                        val_str = str(val)
                else:
                    val_str = str(val)
            else:
                val_str = ""
            html += (
                f"<td style='padding:12px 16px; color:rgba(245,245,255,0.95); "
                f"background:rgba(10,12,26,0.95);'>{escape(val_str)}</td>"
            )
        html += "</tr>"

    html += """
        </tbody>
      </table>
    </div>
    """
    return html


def render_glass_message(text: str) -> str:
    return (
        "<div style='background:rgba(40,120,80,0.35); "
        "border:1px solid rgba(80,200,140,0.55); "
        "padding:24px; border-radius:14px; color:rgba(245,255,250,1); "
        "line-height:1.9; margin-top:12px; box-shadow: 0 4px 20px rgba(40,120,80,0.22); "
        "white-space:pre-wrap;'>"
        f"{escape(text)}"
        "</div>"
    )

# ============================================================
# Text / keyword helpers
# ============================================================
def extract_keywords(text: str, top_n: int = 6) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    cleaned = re.sub(r"[0-9０-９、。．,.!！?？\(\)\[\]{}「」『』\"'：:;／/\\\\\n\r\t]+", " ", text)
    toks = [t.strip() for t in re.split(r"\s+", cleaned) if t.strip()]
    toks = [t for t in toks if len(t) >= 2 and t not in STOP_TOKENS]
    if not toks:
        return []
    toks = sorted(list(dict.fromkeys(toks)), key=lambda s: (-len(s), s))
    return toks[:top_n]


def text_to_vow_vec(text: str, vows_df: pd.DataFrame, vow_cols: List[str], ngram: int = 3) -> np.ndarray:
    text = (text or "").strip()
    if not text:
        return np.zeros(len(vow_cols), dtype=float)

    t = re.sub(r"\s+", "", text)
    n = max(1, int(ngram))
    grams = [t] if len(t) <= n else [t[i:i+n] for i in range(len(t)-n+1)]

    scores = np.zeros(len(vow_cols), dtype=float)
    titles = vows_df["TITLE"].astype(str).tolist() if "TITLE" in vows_df.columns else []
    for i, title in enumerate(titles[:len(vow_cols)]):
        tt = re.sub(r"\s+", "", str(title))
        hit = 0
        for g in grams:
            if g and g in tt:
                hit += 1
        scores[i] = hit

    if scores.max() > 0:
        scores = scores / scores.max()
    return scores

# ============================================================
# Word sphere art
# ============================================================
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

    edges = []
    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):
            e = energy_between(selected[i], selected[j], rng, jitter=0.0)
            if e < -0.65:
                edges.append((i, j, float(e)))

    return {"words": selected, "energies": {w: energies[w] for w in selected}, "edges": edges}


def layout_sphere(words: List[str], energies: Dict[str, float], center_words: List[str], rng: np.random.Generator) -> np.ndarray:
    n = len(words)
    pos = np.zeros((n, 3), dtype=float)
    ga = np.pi * (3 - np.sqrt(5))

    for k in range(n):
        y = 1 - (2 * k) / max(1, n - 1)
        r = np.sqrt(max(0.0, 1 - y * y))
        th = ga * k
        x = np.cos(th) * r
        z = np.sin(th) * r

        w = words[k]
        e = energies.get(w, 0.0)
        rad = 0.55 + min(2.4, max(0.1, (e + 3.0)))
        rad = np.clip(rad, 0.45, 2.6)
        pos[k] = np.array([x, y, z]) * rad

    center_set = set(center_words)
    for i, w in enumerate(words):
        if w in center_set:
            pos[i] *= 0.35

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

    sr = np.random.default_rng(12345)
    sx = sr.uniform(-3.2, 3.2, star_count)
    sy = sr.uniform(-2.4, 2.4, star_count)
    sz = sr.uniform(-2.0, 2.0, star_count)
    alpha = np.full(star_count, 0.20, dtype=float)
    star_size = sr.uniform(1.0, 2.2, star_count)
    star_colors = [f"rgba(255,255,255,{a})" for a in alpha]
    fig.add_trace(go.Scatter3d(
        x=sx, y=sy, z=sz, mode="markers",
        marker=dict(size=star_size, color=star_colors),
        hoverinfo="skip", showlegend=False
    ))

    xE, yE, zE = [], [], []
    for i, j, _ in edges:
        x0, y0, z0 = pos[i]
        x1, y1, z1 = pos[j]
        xE += [x0, x1, None]
        yE += [y0, y1, None]
        zE += [z0, z1, None]
    fig.add_trace(go.Scatter3d(
        x=xE, y=yE, z=zE, mode="lines",
        line=dict(width=1, color="rgba(200,220,255,0.20)"),
        hoverinfo="skip", showlegend=False
    ))

    center_set = set(center)
    sizes, colors, labels = [], [], []
    for w in words:
        e = energies.get(w, 0.0)
        if w in center_set:
            sizes.append(26)
            colors.append("rgba(255,235,100,0.98)")
            labels.append(w)
        else:
            sizes.append(10 + int(7 * min(1.0, abs(e) / 3.0)))
            colors.append("rgba(220,240,255,0.70)" if e < -0.8 else "rgba(255,255,255,0.55)")
            labels.append(w)

    idx_center = np.array([i for i, w in enumerate(words) if w in center_set], dtype=int)
    idx_other = np.array([i for i, w in enumerate(words) if w not in center_set], dtype=int)

    if len(idx_other) > 0:
        fig.add_trace(go.Scatter3d(
            x=pos[idx_other, 0], y=pos[idx_other, 1], z=pos[idx_other, 2],
            mode="markers+text",
            text=[labels[i] for i in idx_other],
            textposition="top center",
            textfont=dict(size=14, color="rgba(245,245,255,0.92)"),
            marker=dict(
                size=[sizes[i] for i in idx_other],
                color=[colors[i] for i in idx_other],
                line=dict(width=1, color="rgba(0,0,0,0.10)")
            ),
            hovertemplate="<b>%{text}</b><extra></extra>",
            showlegend=False
        ))

    if len(idx_center) > 0:
        fig.add_trace(go.Scatter3d(
            x=pos[idx_center, 0], y=pos[idx_center, 1], z=pos[idx_center, 2],
            mode="markers+text",
            text=[labels[i] for i in idx_center],
            textposition="top center",
            textfont=dict(size=20, color="rgba(255,80,80,1.0)"),
            marker=dict(
                size=[sizes[i] for i in idx_center],
                color=[colors[i] for i in idx_center],
                line=dict(width=2, color="rgba(255,80,80,0.85)")
            ),
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
        margin=dict(l=0, r=0, t=0, b=0),
        height=520
    )
    return fig

# ============================================================
# UI
# ============================================================
st.title("🔮 Q-Quest-QUBO｜量子神託（3軸→誓願→QUBO one-hot）")

with st.sidebar:
    st.header("📁 データ")
    excel_file = st.file_uploader("統合Excel（20260305版）", type=["xlsx"])

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

name_innen, df_innen = find_sheet(
    sheets,
    [S_INNEN, "十二因縁と12誓願の統合 ", "十二因縁と１２誓願の統合"]
)
name_char3, df_char3 = find_sheet(
    sheets,
    [S_CHAR3, "12神の本質・性格・3軸ベクトルとその説明 ", "１２神の本質・性格・３軸ベクトルとその説明"]
)

if mat_mode.startswith("距離"):
    mat_candidates = [S_MAT_DIST, "神と誓願の因果律マトリクス（距離ベース）"]
else:
    mat_candidates = [S_MAT_MEAN, "神と誓願の因果律マトリクス（意味ベース）"]
name_mat, df_mat = find_sheet(sheets, mat_candidates)

# QUOTESシート（任意）
quotes_candidates = ["QUOTES", "QUOTE", "格言", "格言一覧", "Quotes", "quotes"]
name_quotes, df_quotes_raw = find_sheet(sheets, quotes_candidates)

if df_quotes_raw is None:
    for sheet_name in sheets.keys():
        sheet_name_clean = str(sheet_name).strip().lower()
        if "quote" in sheet_name_clean or "格言" in sheet_name_clean:
            name_quotes = sheet_name
            df_quotes_raw = sheets[sheet_name]
            break

if df_quotes_raw is None:
    try:
        xls = pd.ExcelFile(io.BytesIO(excel_bytes))
        for excel_sheet_name in xls.sheet_names:
            excel_sheet_lower = str(excel_sheet_name).strip().lower()
            excel_sheet_norm = norm_col(excel_sheet_name)
            if "quote" in excel_sheet_lower or "格言" in str(excel_sheet_name) or "QUOTE" in excel_sheet_norm:
                try:
                    df_temp = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=excel_sheet_name, engine="openpyxl")
                    if df_temp is not None and len(df_temp) > 0:
                        name_quotes = excel_sheet_name
                        df_quotes_raw = df_temp
                        sheets[excel_sheet_name] = df_temp
                        break
                except Exception:
                    continue
    except Exception:
        pass

if df_quotes_raw is None:
    st.sidebar.warning("⚠️ QUOTESシートが見つかりません（任意）")
else:
    st.sidebar.success(f"✅ QUOTESシートを検出: `{name_quotes}`")

if df_innen is None or df_char3 is None or df_mat is None:
    st.error(
        "必須シートが見つかりません。\n"
        f"- innen={name_innen}, char3={name_char3}, mat={name_mat}\n"
        f"- 検出シート: {list(sheets.keys())}"
    )
    st.stop()

df_quotes = load_quotes(df_quotes_raw)
if df_quotes_raw is not None and len(df_quotes) > 0:
    st.sidebar.success(f"✅ QUOTESシート読み込み完了（{len(df_quotes)}件の格言）")

# Innen columns
col_vow_id = pick_col(df_innen, ["VOW_ID", "VOWID", "誓願ID", "誓願_ID", "誓願"], name_innen)
col_title = pick_col(df_innen, ["TITLE", "タイトル", "題", "題名"], name_innen)
col_subtitle = pick_col(df_innen, ["SUBTITLE", "サブタイトル", "副題", "補足"], name_innen)
col_innen = pick_col(df_innen, ["十二因縁", "12因縁"], name_innen)
col_modern = pick_col(df_innen, ["この段で起きがちなこと（現代語）", "この段で起きがちなこと", "現代語"], name_innen)
col_intervene = pick_col(df_innen, ["つながりの理由（介入点）", "つながりの理由", "介入点"], name_innen)

df_innen = df_innen.copy()
df_innen["VOW_ID_N"] = df_innen[col_vow_id].apply(to_vow_id)

# Char3 columns
col_char_id = pick_col(df_char3, ["ID", "CHAR_ID", "神ID", "キャラID"], name_char3)
col_god_name = pick_col(df_char3, ["神名", "公式キャラ名", "キャラ名", "NAME"], name_char3)
col_ax1 = pick_col(df_char3, ["(-)顕:密(+)", "顕:密", "顕密", "存在"], name_char3)
col_ax2 = pick_col(df_char3, ["(-)智:悲(+)", "智:悲", "智悲", "作用"], name_char3)
col_ax3 = pick_col(df_char3, ["(-)和:荒(+)", "和:荒", "和荒", "魂"], name_char3)
col_tip = pick_col(df_char3, ["性格・口調ヒント", "性格口調ヒント", "口調ヒント", "性格"], name_char3)

# Matrix columns
col_m_char_id = pick_col(df_mat, ["CHAR_ID", "ID", "キャラID", "神ID"], name_mat)
col_m_img = pick_col(df_mat, ["IMAGE_FILE", "IMAGE", "画像", "画像ファイル", "ファイル名"], name_mat)
col_m_name = pick_col(df_mat, ["公式キャラ名", "神名", "キャラ名", "NAME"], name_mat)

vow_cols_raw = detect_vow_columns(df_mat)
if len(vow_cols_raw) < 12:
    st.error(f"相性表の誓願列（VOW系）が12本未満です（検出={len(vow_cols_raw)}）: {vow_cols_raw}")
    st.stop()
if len(vow_cols_raw) > 12:
    vow_cols_raw = vow_cols_raw[:12]

vow_ids = [to_vow_id(c) for c in vow_cols_raw]

# Matrix values
char_names = df_mat[col_m_name].astype(str).tolist()
img_files = df_mat[col_m_img].astype(str).tolist()
W = df_mat[vow_cols_raw].fillna(0).to_numpy(float)

# Axes join
df_axes = df_char3[[col_char_id, col_god_name, col_ax1, col_ax2, col_ax3, col_tip]].copy()
df_axes[col_char_id] = df_axes[col_char_id].astype(str)
df_axes["CHAR_ID_N"] = df_axes[col_char_id].apply(to_char_id)
axes_map = {r["CHAR_ID_N"]: r for _, r in df_axes.iterrows()}

char_axes = []
char_tips = []
for cid in df_mat[col_m_char_id].astype(str).tolist():
    r_map = axes_map.get(to_char_id(cid))
    if r_map is None:
        char_axes.append([0.0, 0.0, 0.0])
        char_tips.append("")
    else:
        char_axes.append([
            safe_float(r_map[col_ax1]),
            safe_float(r_map[col_ax2]),
            safe_float(r_map[col_ax3]),
        ])
        char_tips.append(str(r_map.get(col_tip, "")))
char_axes = np.array(char_axes, float)

# Vow dictionaries
vow_dict = df_innen.drop_duplicates(subset=["VOW_ID_N"])[["VOW_ID_N", col_title, col_subtitle]].copy()
vow_title = {r["VOW_ID_N"]: str(r[col_title]) for _, r in vow_dict.iterrows()}
vow_sub = {r["VOW_ID_N"]: str(r[col_subtitle]) for _, r in vow_dict.iterrows()}

# ============================================================
# Step0: text input
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

vow_dict_df = df_innen.drop_duplicates(subset=["VOW_ID_N"])[[col_title]].copy()
vow_dict_df["TITLE"] = vow_dict_df[col_title].astype(str)
_ = text_to_vow_vec(user_text, vow_dict_df, vow_ids, ngram=3) if user_text else np.zeros(len(vow_ids), dtype=float)

# ============================================================
# Step1: 3-axis input
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
# Step2: 3-axis -> vows
# ============================================================
st.subheader("② 予測12誓願（3軸 → 誓願ベクトル推定）")

vow_vecs = []
n_vows = len(vow_ids)
for j in range(n_vows):
    w = np.maximum(W[:, j], 0.0)
    if float(np.sum(w)) < 1e-12:
        vv = np.zeros(3)
    else:
        vv = (w[:, None] * char_axes).sum(axis=0) / float(np.sum(w))
    vow_vecs.append(unit(vv))
vow_vecs = np.array(vow_vecs, float)

v_need = np.array([cosine(u_n, vow_vecs[j]) for j in range(n_vows)], float)
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

html_table_vpred = render_dataframe_as_html_table(df_vpred[["VOW_ID", "TITLE", "SUBTITLE", "need(0-1)"]])
st.markdown(html_table_vpred, unsafe_allow_html=True)

st.caption("※「誓願＝介入メニュー」。3軸の現在地から、今必要になりやすい誓願を推定しています。")

# ============================================================
# Step2.5: keyword sphere
# ============================================================
if user_text:
    st.subheader("🔍 キーワード抽出と球体アート")

    kw = extract_keywords(user_text, top_n=6)
    colA, colB = st.columns([1.0, 1.6], gap="large")

    with colA:
        st.markdown("### 抽出キーワード")
        if kw:
            st.markdown("**" + " / ".join(kw) + "**")
            st.caption("※簡易抽出です（形態素解析なし）。")
        else:
            st.info("入力が短い/空のため、キーワードが抽出できません。")

    with colB:
        st.markdown("### 🌐 単語の球体（誓願→キーワード→縁のネットワーク）")
        if kw:
            seed_sphere = make_seed(user_text + "|sphere")
            fig = plot_word_sphere(
                center_words=GLOBAL_WORDS_DATABASE,
                user_keywords=kw,
                seed=seed_sphere,
                star_count=850
            )
            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "displaylogo": False,
                    "doubleClick": "reset",
                }
            )
        else:
            st.info("キーワードが抽出できませんでした。")

# ============================================================
# Step3: vows -> god by QUBO
# ============================================================
st.subheader("③ 12神をQUBOで観測（one-hot）")

score = W @ v_user
linear_E = -score

P_min = float(np.max(np.abs(linear_E)) * 3.0 + 1.0)
P = max(float(P_user), P_min)
Q = build_qubo_onehot(linear_E, P)

st.caption(f"ペナルティPの自動下限 P_min={P_min:.2f} を考慮し、採用値は P={P:.2f} です。")

if run:
    samples, Es = sa_sample(Q, num_reads=num_reads, sweeps=sweeps, seed=int(seed))
    idxs = [onehot_index(x) for x in samples]
    idxs = [k for k in idxs if k is not None]

    counts = np.zeros(len(char_names), int)
    for k in idxs:
        counts[k] += 1

    valid = [(energy(Q, x), onehot_index(x)) for x in samples if onehot_index(x) is not None]
    if not valid:
        st.error("one-hot 解が見つかりませんでした。Pを上げて再実行してください。")
    else:
        best_k = min(valid, key=lambda t: t[0])[1]
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

    col_char, col_oracle = st.columns([1, 2])

    with col_char:
        st.write(f"**{char_names[k]}**")
        img_path = Path("assets/images/characters") / img_files[k]
        if img_path.exists():
            try:
                st.image(Image.open(img_path), width=250)
            except Exception:
                st.info(f"画像はありますが読み込めませんでした: {img_path}")
        else:
            st.info(f"画像ファイルが見つかりませんでした: {img_path}")

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
        st.subheader("💬 神託（観測された神からのメッセージ）")
        v_user = st.session_state["v_user"]
        score = st.session_state["score"]
        contrib = W[k, :] * v_user
        order = np.argsort(contrib)[::-1]
        top_vid = vow_ids[order[0]]
        top_vow_title = vow_title.get(top_vid, top_vid)

        oracle_text = f"{char_names[k]}が語る：\n\n"
        oracle_text += f"「{top_vow_title}」という誓願が、今のあなたに響いています。\n\n"

        r = df_innen[df_innen["VOW_ID_N"].astype(str) == str(top_vid)]
        if len(r) >= 1:
            r0 = r.iloc[0]
            oracle_text += f"十二因縁の「{str(r0[col_innen])}」の段にいます。\n"
            oracle_text += f"この段で起きがちなこと：{str(r0[col_modern])}\n\n"
            oracle_text += f"介入点：{str(r0[col_intervene])}"

        st.markdown(render_glass_message(oracle_text), unsafe_allow_html=True)

    st.subheader("📊 観測分布（サンプリング）")
    hist = pd.DataFrame({"神": char_names, "count": st.session_state["counts"]}).sort_values("count", ascending=False)
    st.bar_chart(hist.set_index("神"))

    st.subheader("🧩 この神託が指している誓願（上位）")
    v_user = st.session_state["v_user"]
    contrib = W[k, :] * v_user
    order = np.argsort(contrib)[::-1]

    rows = []
    for idx in order[:4]:
        vid = vow_ids[idx]
        rows.append({
            "VOW_ID": vid,
            "TITLE": vow_title.get(vid, vid),
            "need": float(v_user[idx]),
            "compat": float(W[k, idx]),
            "contrib": float(contrib[idx]),
        })
    df_top_vows = pd.DataFrame(rows)
    st.markdown(render_dataframe_as_html_table(df_top_vows), unsafe_allow_html=True)

    if len(df_quotes) > 0:
        st.subheader("📜 QUOTES神託（温度付きで選択）")
        quote_tau = st.slider("格言温度（高→ランダム / 低→上位固定）", 0.2, 2.5, 1.2, 0.1, key="quote_tau")

        if "last_quote_tau" not in st.session_state:
            st.session_state["last_quote_tau"] = quote_tau
            st.session_state["quote_seed_offset"] = 0

        if abs(st.session_state.get("last_quote_tau", quote_tau) - quote_tau) > 0.05:
            st.session_state["quote_seed_offset"] = st.session_state.get("quote_seed_offset", 0) + 1
            st.session_state["last_quote_tau"] = quote_tau

        quote_seed_base = (
            (user_text or "")
            + f"|quotes_temp|{quote_tau:.3f}|{seed}|offset_{st.session_state.get('quote_seed_offset', 0)}"
        )
        quote_seed = make_seed(quote_seed_base)

        qpick_temp = pick_quotes_by_temperature(
            df_quotes, lang="ja", k=3, tau=quote_tau, seed=quote_seed
        )

        if len(qpick_temp) > 0:
            for _, row in qpick_temp.iterrows():
                quote_text = str(row.get("QUOTE", "")).strip()
                source_text = str(row.get("SOURCE", "")).strip()
                if quote_text:
                    quote_display = f"「{quote_text}」"
                    if source_text and source_text != "nan":
                        quote_display += f"\n\n— {source_text}"
                    st.markdown(render_glass_message(quote_display), unsafe_allow_html=True)
        else:
            st.info("QUOTES神託が見つかりませんでした。")

    st.subheader("📜 十二因縁（診断）→ 誓願（介入）→ 神（語り手）")
    if len(r) >= 1:
        r0 = r.iloc[0]
        st.write(f"**今、強く出ている誓願**：{top_vow_title}")
        st.write(f"**対応する十二因縁**：{str(r0[col_innen])}")
        st.write(f"**現代語（起きがちなこと）**：{str(r0[col_modern])}")
        st.write(f"**介入点（つながりの理由）**：{str(r0[col_intervene])}")
    else:
        st.info("十二因縁シートに、上位誓願の対応行が見つかりませんでした。")

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
