# -*- coding: utf-8 -*-
"""量子神託 QR閲覧専用アプリ。PC側 app_qubo_chat_QR_fixed.py の oracle パラメータに対応。"""
import base64
import json
import zlib
from pathlib import Path
from html import escape

import streamlit as st

st.set_page_config(page_title="量子神託｜共有された神託", page_icon="🔮", layout="centered")
st.markdown("""
<style>
.stApp {background:linear-gradient(160deg,#080d20,#161126);color:#f5f3ff}
.block-container {max-width:850px;padding-top:2rem}
.oracle {padding:1.15rem;background:#182437;border:1px solid #344765;
 border-radius:14px;white-space:pre-wrap;line-height:1.9;color:#fafaff}
</style>
""", unsafe_allow_html=True)

MAX_TOKEN_LEN = 16000

def decode_oracle(token: str) -> dict:
    if not token or len(token) > MAX_TOKEN_LEN:
        raise ValueError("QRデータの長さが不正です")
    compressed = base64.urlsafe_b64decode(token + ("=" * (-len(token) % 4)))
    # 展開サイズ上限。外部入力なので過大なデータは扱わない。
    inflater = zlib.decompressobj()
    raw = inflater.decompress(compressed, 100_001)
    if len(raw) > 100_000 or inflater.unconsumed_tail or not inflater.eof:
        raise ValueError("QRデータが大きすぎるか破損しています")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("QRデータの形式が正しくありません")
    return payload


def show_message(value: str):
    st.markdown('<div class="oracle">' + escape(value) + '</div>', unsafe_allow_html=True)

st.title("🔮 共有された量子神託")
raw_token = st.query_params.get("oracle", "")
if not raw_token:
    st.info("PCの量子神託会話版で生成したQRコードを読み取ると、ここに神託が表示されます。")
    st.stop()

try:
    shared = decode_oracle(str(raw_token))
except Exception:
    st.error("QRデータを読み取れませんでした。PCの会話版でQRコードを再生成してください。")
    st.stop()

name = str(shared.get("god_name") or "観測された神")
st.header("⛩️ " + name)
image_name = Path(str(shared.get("image_file") or "")).name
if image_name:
    image_path = Path(__file__).resolve().parent / "assets" / "images" / "characters" / image_name
    if image_path.is_file() and image_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        st.image(str(image_path), width=320)
    else:
        st.warning("神の画像が公開先に見つかりません。画像ファイル名: " + image_name)
else:
    st.warning("QRデータに神の画像ファイル名がありません。")

vow = str(shared.get("vow_title") or "")
if vow:
    st.subheader("🧩 誓願")
    st.write(vow)

oracle = str(shared.get("oracle_text") or "")
if oracle:
    st.subheader("💬 神託")
    show_message(oracle)

quote = str(shared.get("quote_text") or "")
if quote:
    st.subheader("📜 格言")
    source = str(shared.get("quote_source") or "")
    show_message("「" + quote + "」" + (("\n— " + source) if source else ""))

when = str(shared.get("timestamp") or "")
if when:
    st.caption("観測日時: " + when)
st.caption("QRのURLに観測結果を含める方式です。個人的な内容を含む場合、URLの共有先にご注意ください。")
