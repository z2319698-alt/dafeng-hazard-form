import streamlit as st
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from PIL import Image
import numpy as np
from fpdf import FPDF
# 假設你的 PDF 與 Drive 函數寫在 utils.py 或直接貼在各頁頂部

# --- 權限檢查 ---
if not st.session_state.get('auth_entry', False):
    st.error("⚠️ 存取拒絕：請先由承辦人員開立『進場確認單』。")
    st.stop()

st.title("🚧 02. 施工安全危害告知單")

# 自動帶入第一步的資料
comp = st.session_state.get('company', '')
loc = st.session_state.get('location', '')

st.write(f"**施工廠商：** {comp} | **施工地點：** {loc}")

# --- 15 條規範與簽名 (保留你原本的 UI) ---
with st.container(border=True):
    st.subheader("⚠️ 危害因素告知")
    st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"])

rules = ["一、為防止尖銳物危害...", "二、設備維修需掛牌...", " (此處省略至十五條) "]
full_html = "".join([f"<div style='color:white; background:#333; padding:10px;'>{r}</div>" for r in rules])
st.markdown(full_html, unsafe_allow_html=True)

read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
canvas_result = st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_h")

if st.button("確認提交告知單"):
    if read_ok and canvas_result.image_data is not None:
        # 這裡放入你原本的 PDF 生成與上傳 Drive 的邏輯
        st.success("✅ 告知單已存檔至雲端，請繼續前往工具箱會議。")
    else:
        st.warning("請確保已勾選同意並完成簽名。")
