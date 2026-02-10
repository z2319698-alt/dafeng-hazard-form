import streamlit as st
# ... 保持你原本的所有 import ...

# --- 加入這段鎖定邏輯 ---
if not st.session_state.get('auth_entry', False):
    st.error("⚠️ 存取拒絕：請先由承辦人員開立『進場確認單』。")
    st.stop() 
# ----------------------

# ... 接著放你原本的所有代碼 (def create_pdf_report 等等) ...
