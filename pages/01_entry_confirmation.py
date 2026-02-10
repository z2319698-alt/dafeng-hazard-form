import streamlit as st
from datetime import date

st.set_page_config(page_title="01 進場確認單")

st.title("🚧 施工進場確認單")
st.subheader("管理單位 / 承辦人填寫區")

with st.form("admin_gate"):
    c1, c2 = st.columns(2)
    with c1:
        v_name = st.text_input("預定施工廠商", placeholder="例如：某某工程行")
        v_loc = st.selectbox("施工區域", ["粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
    with c2:
        v_date = st.date_input("核准進場日期", value=date.today())
        v_project = st.text_input("施工項目", placeholder="例如：天車維修")

    submitted = st.form_submit_with_button("核准進場並發佈告知單")

if submitted:
    if v_name and v_project:
        st.session_state['auth_entry'] = True
        st.session_state['company'] = v_name
        st.session_state['location'] = v_loc
        st.session_state['entry_date'] = v_date
        st.session_state['project_name'] = v_project
        st.success(f"🎉 核准成功！已開啟 {v_name} 的簽署權限。")
        st.balloons()
    else:
        st.error("❌ 請完整填寫廠商名稱與施工項目。")
