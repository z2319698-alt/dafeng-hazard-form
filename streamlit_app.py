import streamlit as st

# 1. 基礎設定
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

# 2. 初始化 Session State
if 'auth_entry' not in st.session_state:
    st.session_state['auth_entry'] = False

# 3. 顯示首頁內容
st.markdown('<h1 style="text-align:center; color:#2E7D32;">大豐環保 (全興廠)</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">工安管理系統</h3>', unsafe_allow_html=True)

st.divider()

st.info("""
👈 **請看左側選單開始操作：**
1. **01_entry_confirmation**: 承辦人員點擊此處「開立進場單」。
2. **02_hazard_form**: 廠商核准後，點擊此處進行「危害告知簽名」。
""")

if st.session_state['auth_entry']:
    st.success(f"✅ 當前已授權廠商：{st.session_state.get('company')}")
