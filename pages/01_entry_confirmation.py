import streamlit as st
from datetime import date

# 1. 頁面基本設定
st.set_page_config(page_title="01 進場確認單 - 大豐環保", layout="centered")

# --- 自定義樣式 ---
st.markdown("""
    <style>
    .admin-header { font-size: 26px; color: #1565C0; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #1565C0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1565C0; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 標題與引導
st.markdown('<div class="admin-header">🚧 第一階段：行政發包與進場申請</div>', unsafe_allow_html=True)
st.write("此頁面由**廠內承辦人員**填寫，完成後方可開啟承攬商簽署介面。")

# 3. 進場確認表單
with st.form("entry_confirmation_form"):
    st.subheader("📝 施工基本資訊")
    
    col1, col2 = st.columns(2)
    with col1:
        vendor_name = st.text_input("承攬廠商全銜", placeholder="請輸入公司名稱")
        work_location = st.selectbox("施工地點", [
            "請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施", "行政辦公區"
        ])
    with col2:
        entry_date = st.date_input("預計施工日期", value=date.today())
        entry_time = st.time_input("預計進場時間")

    st.divider()
    
    st.subheader("⚙️ 施工內容審核")
    work_project = st.text_input("施工項目名稱", placeholder="例如：二樓空壓機濾網更換")
    work_description = st.text_area("具體施工內容簡述", placeholder="請簡述作業流程...")
    
    # 高風險作業勾選
    st.write("**⚠️ 高風險作業類別 (複選)：**")
    hazards = st.columns(3)
    is_fire = hazards[0].checkbox("動火作業")
    is_high = hazards[1].checkbox("高處作業")
    is_confined = hazards[2].checkbox("侷限空間")
    
    st.divider()
    
    # 附件確認清單
    st.subheader("📋 附件核對 (承辦人確認)")
    c1, c2 = st.columns(2)
    check_doc1 = c1.checkbox("已提供施工人員名冊")
    check_doc2 = c2.checkbox("已確認勞保投保證明")
    check_doc3 = c1.checkbox("特種作業證照核對完畢")
    check_doc4 = c2.checkbox("機具合格證(如吊車/堆高機)")

    # 提交按鈕 - 已修正函數名稱
    submit_btn = st.form_submit_button("核准進場並發佈任務")

# 4. 提交後的邏輯處理
if submit_btn:
    if vendor_name == "" or work_location == "請選擇" or work_project == "":
        st.error("❌ 請填寫必要的『廠商名稱』、『地點』與『施工項目』！")
    elif not (check_doc1 and check_doc2):
        st.warning("⚠️ 勞保證明與人員名冊為必要附件，請核對後再提交。")
    else:
        # --- 核心邏輯：將資料存入 Session State ---
        st.session_state['auth_entry'] = True
        st.session_state['company'] = vendor_name
        st.session_state['location'] = work_location
        st.session_state['project_name'] = work_project
        st.session_state['is_fire_work'] = is_fire 
        
        st.success(f"✅ 進場確認單已成功送出！")
        st.info(f"廠商 **{vendor_name}** 現在可以前往左側選單之『02 施工安全危害告知單』進行簽署。")
        st.balloons()
