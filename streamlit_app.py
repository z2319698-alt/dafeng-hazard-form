import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

# 頁面設定
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

# 初始化記憶狀態 (Session State)
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"
if 'selected_hazards' not in st.session_state:
    st.session_state.selected_hazards = []

# CSS 美化
st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) {
        background-color: #333333 !important; padding: 15px; border-radius: 10px;
    }
    .rule-text-white { font-size: 18px; color: #FFFFFF; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #555555; }
    .hazard-notice { color: #FFEB3B !important; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 左側導覽列 ---
st.sidebar.title("📋 表單選單")
pages = [
    "1. 施工安全危害告知單", 
    "2. 承攬商工具箱會議紀錄表", 
    "3. 動火作業許可證", 
    "4. 特殊危害作業許可證"
]
for p in pages:
    if st.sidebar.button(p):
        st.session_state.current_page = p

# --- 危害資料庫 ---
HAZARD_DETAILS = {
    "墜落": "● [墜落防護]：1.8公尺以上作業務必確實佩戴安全帶及安全帽。",
    "感電": "● [電力安全]：電路維修需斷電掛牌，嚴禁帶電作業。",
    "物體飛落": "● [防飛落]：施工區域下方應設警戒線，高處工具應有繩索繫留。",
    "火災爆炸": "● [動火管制]：動火區域3公尺內需備妥滅火器，清理易燃物。",
    "交通事故": "● [交通安全]：場內行駛嚴禁超速，轉彎處需減速鳴笛。",
    "缺氧窒息": "● [侷限空間]：進入前務必進行氧氣測量，作業中需全程通訊。",
    "化學品接觸": "● [化學防護]：需確實佩戴防護面罩、耐酸鹼手套。",
    "捲入夾碎": "● [防捲夾]：操作旋轉設備嚴禁佩戴手套，維修前需確實停機。"
}

# --- 頁面 1：危害告知單 ---
if st.session_
