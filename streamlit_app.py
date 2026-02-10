import streamlit as st

st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

st.markdown("""
    <style>
    .factory-header { font-size: 24px; color: #2E7D32; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="factory-header">大豐環保 (全興廠) 工安管理系統</div>', unsafe_allow_html=True)

st.info("請從左側選單選擇作業表單。請注意：必須先由承辦人開立『進場確認單』。")

# 初始化 session_state
if 'auth_entry' not in st.session_state:
    st.session_state['auth_entry'] = False
