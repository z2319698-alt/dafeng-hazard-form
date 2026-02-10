import streamlit as st

st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

# 初始化權限狀態，防止直接跳過第一關
if 'auth_entry' not in st.session_state:
    st.session_state['auth_entry'] = False

st.markdown('<h1 style="text-align:center; color:#2E7D32;">大豐環保 (全興廠)</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">工安管理系統</h3>', unsafe_allow_html=True)

st.info("請從左側選單選擇作業表單。**請注意：必須先由承辦人開立『進場確認單』。**")
