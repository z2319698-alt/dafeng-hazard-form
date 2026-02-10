import streamlit as st

st.title("🚧 01. 施工進場確認單")

with st.form("entry_form"):
    comp = st.text_input("預定施工廠商")
    loc = st.selectbox("施工地點", ["粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
    submit = st.form_submit_with_button("核准進場")

if submit:
    if comp:
        st.session_state['auth_entry'] = True
        st.session_state['company'] = comp  # 這裡存入後，02頁面就能自動抓到廠商名
        st.session_state['location'] = loc
        st.success(f"✅ 已核准 {comp} 進場。現在請點擊左側選單前往『02. 施工安全危害告知單』")
    else:
        st.error("請輸入廠商名稱")
