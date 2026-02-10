import streamlit as st
from datetime import date

st.set_page_config(page_title="進場確認單")

st.title("🚧 01. 施工進場確認單 (管理單位)")

with st.form("entry_gate"):
    admin_comp = st.text_input("預定施工廠商")
    admin_loc = st.selectbox("施工區域", ["粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
    admin_project = st.text_input("施工項目內容")
    admin_date = st.date_input("核准進場日期", value=date.today())
    
    submit = st.form_submit_with_button("核准並開啟後續表單")

if submit:
    if admin_comp and admin_project:
        st.session_state['auth_entry'] = True
        st.session_state['company'] = admin_comp
        st.session_state['location'] = admin_loc
        st.session_state['project_name'] = admin_project
        st.success(f"✅ 已核准 {admin_comp} 進場。請告知廠商前往『02. 危害告知單』。")
    else:
        st.error("請填寫完整資訊")
