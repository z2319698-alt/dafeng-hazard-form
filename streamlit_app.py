import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

st.set_page_config(page_title="大豐環保-危害告知系統", layout="centered")

st.title("🚧 承攬商施工安全危害告知")
st.write("---")

# 建立與 Google Sheets 的連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 填寫表單內容
col1, col2 = st.columns(2)
with col1:
    company = st.text_input("承攬商名稱")
    worker_name = st.text_input("施作人員姓名")
with col2:
    work_date = st.date_input("施工日期", value=date.today())
    work_location = st.text_input("施工地點")

hazard_items = st.multiselect(
    "告知危害因素",
    ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸"]
)

# 簽名區
st.write("### ✍️ 告知人/受告知人簽名")
canvas_result = st_canvas(
    stroke_width=3,
    stroke_color="#000000",
    background_color="#eeeeee",
    height=200,
    drawing_mode="freedraw",
    key="canvas",
)

if st.button("提交資料", type="primary"):
    if not worker_name or not company:
        st.error("❌ 請填寫公司名稱與姓名！")
    elif canvas_result.image_data is None:
        st.error("❌ 請完成簽名後再提交！")
    else:
        st.success("✅ 告知單提交成功！(後續連動 Excel 邏輯)")
        st.balloons()
