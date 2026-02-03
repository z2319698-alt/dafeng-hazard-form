import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

# 頁面設定
st.set_page_config(page_title="大豐環保-危害告知系統", layout="centered")

# CSS 美化
st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: -10px; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) {
        background-color: #333333 !important;
        padding: 15px;
        border-radius: 10px;
    }
    .rule-text-white {
        font-size: 18px !important;
        font-weight: 400;
        line-height: 1.7;
        color: #FFFFFF !important;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #555555;
    }
    .hazard-notice {
        color: #FFEB3B !important; /* 危害注意事項用黃色區分 */
        font-weight: bold !important;
    }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; font-size: 18px !important; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 定義各項危害的注意事項資料庫 ---
HAZARD_DETAILS = {
    "墜落": "● [墜落防護]：1.8公尺以上作業務必確實佩戴安全帶及安全帽，並掛載於穩固錨點。",
    "感電": "● [電力安全]：電路維修需斷電掛牌，嚴禁帶電作業，工具需有絕緣防護。",
    "物體飛落": "● [防飛落]：施工區域下方應設警戒線或三角錐，禁止人員進入，高處工具應有繩索繫留。",
    "火災爆炸": "● [動火管制]：動火區域3公尺內需備妥滅火器，清理易燃物，並派人監火。",
    "交通事故": "● [交通安全]：場內行駛嚴禁超速，轉彎處需減速鳴笛，並行走指定人行道。",
    "缺氧窒息": "● [侷限空間]：進入前務必進行氧氣測量，作業中需全程通訊且有一人在外監督。",
    "化學品接觸": "● [化學防護]：需確實佩戴防護面罩、耐酸鹼手套，若噴濺應立即以清水沖洗並就醫。",
    "捲入夾碎": "● [防捲夾]：操作旋轉設備嚴禁佩戴手套或長袖寬鬆衣物，維修前需確實停機並LOCK OUT。"
}

# --- 標題區 ---
st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
st.title("🚧 承攬商施工安全危害告知")

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
    hazards = list(HAZARD_DETAILS.keys())
    selected_hazards = st.multiselect("勾選本次作業相關危害項目", hazards)

# --- 3. 安全衛生規定區 ---
st.subheader("📋 3. 安全衛生規定與專屬危害須知")
st.caption("請向下滾動閱讀完畢：")

# 組合 15 條通用規定
rules_list = [
    "一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。",
    "二、設備維修需經主管同意並掛「維修中/保養中」牌。",
    "三、場內限速 15 公里/小時，嚴禁超速。",
    "四、工作場所禁止吸菸、飲食或飲酒。",
    "五、操作機具需持證照且經主管同意，相關責任由借用者自負。",
    "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。",
    "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。",
    "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。",
    "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。",
    "十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。",
    "十一、清運車輛啟動前應確認周遭並發出信號。",
    "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。",
    "十三、未達指定傾貨區前，嚴禁私自開啟車斗。",
    "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。",
    "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"
]

full_html = ""
for r in rules_list:
    full_html += f"<div class='rule-text-white'>{r}</div>"

# 💡 動態增加勾選的危害注意事項
if selected_hazards:
    full_html += "<div class='rule-text-white' style='color:#FFEB3B !important; font-weight:bold; border-bottom:2px solid #FFEB3B;'>▼ 以下為您勾選項目的特別注意事項：</div>"
    for h in selected_hazards:
        detail = HAZARD_DETAILS.get(h, "")
        full_html += f"<div class='rule-text-white hazard-notice'>{detail}</div>"

# 顯示滾動視窗
with st.container(height=400, border=True):
    st.markdown(full_html, unsafe_allow_html=True)

st.markdown("####")
read_confirmed = st.checkbox("**我已充分閱讀並同意遵守上述通用規定及專屬危害須知**")

# --- 4. 簽名區 ---
st.subheader("✍️ 4. 受告知人簽名")
canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, drawing_mode="freedraw", key="canvas")

# --- 提交邏輯 ---
if st.button("確認提交告知單", type="primary", disabled=not read_confirmed):
    if not company or not worker_name or work_location == "請選擇地點":
        st.error("❌ 請填寫基本資訊！")
    elif not selected_hazards:
        st.warning("❌ 請至少勾選一項危害因素！")
    elif canvas_result.image_data is None:
        st.error("❌ 請完成簽名！")
    else:
        st.success("✅ 提交成功！")
        st.balloons()

if not read_confirmed:
    st.warning("👈 請勾選「我已閱讀並同意」方可提交。")
