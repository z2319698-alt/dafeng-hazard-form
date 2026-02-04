import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

# 頁面設定
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

# 初始化記憶狀態
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
pages = ["1. 施工安全危害告知單", "2. 承攬商工具箱會議紀錄表", "3. 動火作業許可證", "4. 特殊危害作業許可證"]
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
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知")
    
    with st.container(border=True):
        st.subheader("👤 1. 基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.company = st.text_input("承攬商名稱", placeholder="請輸入公司")
            st.session_state.worker_name = st.text_input("施作人員姓名", placeholder="請輸入姓名")
        with col2:
            st.session_state.work_date = st.date_input("施工日期", value=date.today())
            st.session_state.location = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])

    with st.container(border=True):
        st.subheader("⚠️ 2. 危害因素告知")
        st.session_state.selected_hazards = st.multiselect("勾選本次作業危害項目", list(HAZARD_DETAILS.keys()))

    st.subheader("📋 3. 安全衛生規定")
    # 將 15 條規定放入列表，避免字串斷裂
    rules = [
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
    for r in rules:
        full_html += f"<div class='rule-text-white'>{r}</div>"
    
    # 針對勾選項目的額外告知
    if st.session_state.selected_hazards:
        full_html += "<div class='rule-text-white hazard-notice' style='border-top: 2px solid #FFEB3B; padding-top: 10px;'>▼ 您勾選項目的特別注意事項：</div>"
        for h in st.session_state.selected_hazards:
            full_html += f"<div class='rule-text-white hazard-notice'>{HAZARD_DETAILS[h]}</div>"

    with st.container(height=380, border=True):
        st.markdown(full_html, unsafe_allow_html=True)

    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
    
    st.subheader("✍️ 4. 受告知人簽名")
    st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="sign_h")

    if st.button("確認提交告知單", disabled=not read_ok):
        if not st.session_state.company or st.session_state.location == "請選擇":
            st.error("❌ 請填寫完整基本資訊")
        else:
            st.success("✅ 告知單已送出，跳轉至工具箱會議紀錄...")
            st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
            st.rerun()

# --- 頁面 2：工具箱會議 (其餘頁面邏輯完全不動) ---
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.write(f"**廠商:** {st.session_state.get('company','')}")
        st.write(f"**施工位置:** {st.session_state.get('location','')}")
        st.info(f"今日危害告知項目: {', '.join(st.session_state.selected_hazards)}")
        st.text_input("工程內容", placeholder="請輸入本日施工簡述")
        st.multiselect("本日防護具檢查", ["安全帽", "安全鞋", "反光背心", "安全帶", "防護手套"])
    st.subheader("✍️ 會議簽到")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_t")
    if st.button("確認送出會議紀錄"):
        if "火災爆炸" in st.session_state.selected_hazards:
            st.session_state.current_page = "3. 動火作業許可證"
        elif any(x in st.session_state.selected_hazards for x in ["墜落", "感電", "缺氧窒息", "化學品接觸"]):
            st.session_state.current_page = "4. 特殊危害作業許可證"
        else:
            st.success("流程已完成！")
            st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()

# --- 頁面 3：動火作業 ---
elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    st.error("⚠ 此作業涉及火災爆炸風險，請完成核對")
    st.checkbox("3公尺內備有滅火器")
    st.checkbox("清除週邊11公尺內可燃物")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_f")
    if st.button("完成動火申請"):
        st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()

# --- 頁面 4：特殊危害 ---
elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    st.warning(f"涉及高風險項目: {st.session_state.selected_hazards}")
    st.checkbox("指派一人以上安全警戒人員")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_s")
    if st.button("完成特殊危害申請"):
        st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()
