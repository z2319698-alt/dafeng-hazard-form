import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

# 頁面設定
st.set_page_config(page_title="大豐環保-危害告知系統", layout="centered")

# CSS 美化：調整顏色與視覺層次
st.markdown("""
    <style>
    /* 調整規定文字：顏色改為深灰，增加字體平滑度 */
    .rule-text {
        font-size: 18px !important;
        font-weight: 400;
        line-height: 1.7;
        color: #555555;  /* 柔和的深灰色 */
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #f0f0f0; /* 增加細線分隔 */
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3.5em;
        font-size: 18px !important;
        background-color: #4CAF50;
        color: white;
    }
    /* 讓勾選框文字也明顯一點 */
    .stCheckbox label {
        font-size: 18px !important;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚧 承攬商施工安全危害告知")
st.info("請施作人員確實填寫資訊，閱讀安全守則並簽名。")

# --- 1. 基本資訊區 ---
with st.container(border=True):
    st.subheader("👤 1. 基本資訊")
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("承攬商名稱", placeholder="請輸入公司名稱")
        worker_name = st.text_input("施作人員姓名", placeholder="請輸入全名")
    with col2:
        work_date = st.date_input("施工日期", value=date.today())
        location_options = ["請選擇地點", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"]
        work_location = st.selectbox("施工地點", options=location_options)

# --- 2. 危害因素區 ---
with st.container(border=True):
    st.subheader("⚠️ 2. 危害因素告知")
    hazards = ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"]
    selected_hazards = st.multiselect("勾選本次作業相關危害項目", hazards)

# --- 3. 安全衛生規定區 ---
st.subheader("📋 3. 安全衛生規定 / Safety Rules")
st.caption("請向下滾動閱讀完畢：")

# 使用 HTML 包裝，顏色已調淡
rules_html = """
<div class='rule-text'>一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。</div>
<div class='rule-text'>二、設備維修需經主管同意並掛「維修中/保養中」牌。</div>
<div class='rule-text'>三、場內限速 15 公里/小時，嚴禁超速。</div>
<div class='rule-text'>四、工作場所禁止吸菸、飲食或飲酒。</div>
<div class='rule-text'>五、操作機具需持證照且經主管同意，相關責任由借用者自負。</div>
<div class='rule-text'>六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。</div>
<div class='rule-text'>七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。</div>
<div class='rule-text'>八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。</div>
<div class='rule-text'>九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。</div>
<div class='rule-text'>十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。</div>
<div class='rule-text'>十一、清運車輛啟動前應確認周遭並發出信號。</div>
<div class='rule-text'>十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。</div>
<div class='rule-text'>十三、未達指定傾貨區前，嚴禁私自開啟車斗。</div>
<div class='rule-text'>十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。</div>
<div class='rule-text'>十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。</div>
"""

with st.container(height=350, border=True):
    st.markdown(rules_html, unsafe_allow_html=True)

st.markdown("####")
read_confirmed = st.checkbox("**我已充分閱讀並同意遵守上述安全衛生規定**")

# --- 4. 簽名區 ---
st.subheader("✍️ 4. 受告知人簽名")
canvas_result = st_canvas(
    stroke_width=3,
    stroke_color="#000",
    background_color="#eee",
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)

st.write("---")

# --- 提交邏輯 ---
if st.button("確認提交告知單", type="primary", disabled=not read_confirmed):
    if not company or not worker_name or work_location == "請選擇地點":
        st.error("❌ 請填寫基本資訊！")
    elif not selected_hazards:
        st.warning("❌ 請勾選危害因素！")
    elif canvas_result.image_data is None:
        st.error("❌ 請完成簽名！")
    else:
        st.success(f"✅ 提交成功！")
        st.balloons()

if not read_confirmed:
    st.warning("👈 請先閱讀規定並勾選同意。")

st.markdown("---")
st.caption("大豐環保科技股份有限公司 - 工安管理系統")
