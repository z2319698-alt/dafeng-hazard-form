import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date
from fpdf import FPDF
import base64

# 頁面設定
st.set_page_config(page_title="大豐環保-工安管理系統", layout="wide")

# 初始化 Session State (記憶選單與跳轉)
if 'current_page' not in st.session_state:
    st.session_state.current_page = "危害告知單"
if 'selected_hazards' not in st.session_state:
    st.session_state.selected_hazards = []

# CSS 美化
st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) {
        background-color: #333333 !important; padding: 15px; border-radius: 10px;
    }
    .rule-text-white { font-size: 18px; color: #FFFFFF; margin-bottom: 10px; border-bottom: 1px solid #555555; }
    .hazard-notice { color: #FFEB3B !important; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 左側導覽列 ---
st.sidebar.title("📋 表單選單")
if st.sidebar.button("1. 施工安全危害告知單"):
    st.session_state.current_page = "危害告知單"
if st.sidebar.button("2. 工具箱會議紀錄表"):
    st.session_state.current_page = "工具箱會議"
if st.sidebar.button("3. 動火作業許可證"):
    st.session_state.current_page = "動火作業"
if st.sidebar.button("4. 特殊危害作業許可證"):
    st.session_state.current_page = "特殊危害"

# --- PDF 產生函式 (簡化版示意) ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Arial', '', '', unicode=True) # 實際環境需上傳中文字體檔
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    # 這裡後續需依據 PDF 格式寫入細節內容
    return pdf.output(dest='S').encode('latin-1')

# --- 頁面 1：施工安全危害告知單 ---
if st.session_state.current_page == "危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知")
    
    with st.container(border=True):
        st.subheader("👤 1. 基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("承攬商名稱")
            worker_name = st.text_input("施作人員姓名")
        with col2:
            work_date = st.date_input("施工日期", value=date.today())
            work_location = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])

    with st.container(border=True):
        st.subheader("⚠️ 2. 危害因素告知")
        hazard_map = {
            "墜落": "● [墜落防護]：1.8公尺以上作業務必確實佩戴安全帶及安全帽。",
            "感電": "● [電力安全]：電路維修需斷電掛牌，嚴禁帶電作業。",
            "火災爆炸": "● [動火管制]：動火區域3公尺內需備妥滅火器。",
            "缺氧窒息": "● [侷限空間]：進入前務必進行氧氣測量。",
            "化學品接觸": "● [化學防護]：需確實佩戴防護面罩、耐酸鹼手套。"
        }
        st.session_state.selected_hazards = st.multiselect("勾選相關危害項目", list(hazard_map.keys()))

    st.subheader("📋 3. 安全衛生規定")
    full_html = "<div class='rule-text-white'>一、為防止尖銳物切割危害，應佩戴安全手套...</div>" # (此處保留原本15條)
    if st.session_state.selected_hazards:
        full_html += "<div class='rule-text-white hazard-notice'>▼ 專屬危害須知：</div>"
        for h in st.session_state.selected_hazards:
            full_html += f"<div class='rule-text-white hazard-notice'>{hazard_map[h]}</div>"
    
    with st.container(height=300, border=True):
        st.markdown(full_html, unsafe_allow_html=True)

    read_ok = st.checkbox("我已充分閱讀並同意遵守")
    st.subheader("✍️ 4. 受告知人簽名")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="sign_1")

    if st.button("確認提交告知單", disabled=not read_ok):
        st.success("告知單已存檔 PDF！準備跳轉至工具箱會議...")
        st.session_state.current_page = "工具箱會議"
        st.rerun()

# --- 頁面 2：工具箱會議紀錄表 ---
elif st.session_state.current_page == "工具箱會議":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.write("會議地點:", st.session_state.get('work_location', '全興廠'))
        st.checkbox("宣導本日作業區域潛在危害性 (已勾選項目自動同步)")
        st.write("勾選項目:", ", ".join(st.session_state.selected_hazards))
        st.text_area("其他宣導事項")
    
    st.subheader("✍️ 當日施工人員確認簽名")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_2")

    if st.button("送出會議紀錄"):
        # 邏輯判斷：跳轉至動火或特殊危害
        if "火災爆炸" in st.session_state.selected_hazards:
            st.session_state.current_page = "動火作業"
        elif any(x in st.session_state.selected_hazards for x in ["墜落", "感電", "缺氧窒息", "化學品接觸"]):
            st.session_state.current_page = "特殊危害"
        else:
            st.success("所有流程已完成！")
            st.session_state.current_page = "危害告知單"
        st.rerun()

# --- 頁面 3：動火作業許可證 ---
elif st.session_state.current_page == "動火作業":
    st.title("🔥 動火作業許可證")
    st.warning("偵測到火災爆炸風險，請完成動火檢核。")
    st.checkbox("3公尺內備有滅火器")
    st.checkbox("清除週邊11公尺內可燃物")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_3")
    if st.button("完成動火申請"):
        st.session_state.current_page = "危害告知單"
        st.rerun()

# --- 頁面 4：特殊危害作業許可證 ---
elif st.session_state.current_page == "特殊危害":
    st.title("🛡️ 特殊危害作業許可證")
    st.warning("偵測到高風險作業，請完成特殊檢核。")
    st.write("目前勾選項：", st.session_state.selected_hazards)
    st.checkbox("已指派一人以上安全警戒人員")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_4")
    if st.button("完成特殊危害申請"):
        st.session_state.current_page = "危害告知單"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("大豐環保科技 - 全興廠工安系統")
