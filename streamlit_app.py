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

# --- 1. 危害告知單 (完全不動) ---
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.title("🚧 承攬商施工安全危害告知單")
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
        st.session_state.selected_hazards = st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"])
    st.subheader("📋 3. 安全衛生規定")
    rules = ["一、為防止尖銳物切割危害，應佩戴安全手套、安全鞋及防護具。", "二、設備維修需經主管同意並掛「維修中/保養中」牌。", "三、場內限速 15 公里/小時，嚴禁超速。", "四、工作場所禁止吸菸、飲食或飲酒。", "五、操作機具需持證照且經主管同意，相關責任由借用者自負。", "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。", "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。", "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。", "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。", "十、動火作業需主管同意、備滅火器並配戴護目鏡。", "十一、清運車輛啟動前應確認周遭並發出信號。", "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。", "十三、未達指定傾貨區前，嚴禁私自開啟車斗。", "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。", "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"]
    st.info("\n".join(rules))
    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
    st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="sign_h")
    if st.button("確認提交告知單", disabled=not read_ok):
        st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
        st.rerun()

# --- 2. 工具箱會議紀錄表 (完全不動) ---
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**作業廠商:** {st.session_state.get('company','')}")
            st.text_input("共同作業廠商", key="tool_co_comp")
            st.text_area("工程內容", key="tool_content")
        with col2:
            st.number_input("總作業人數", min_value=1, step=1, key="tool_total_num")
            st.write(f"**會議日期:** {date.today()}")
    hazard_options = ["墜落", "跌倒", "火災", "中毒", "缺氧", "衝撞", "感電", "物體飛落", "切、割、夾、捲", "爆炸", "物體破裂", "物體倒塌"]
    st.write("**宣導事項勾選**")
    cols = st.columns(4)
    for i, opt in enumerate(hazard_options):
        cols[i % 4].checkbox(opt, key=f"tool_haz_{opt}")
    st.subheader("✍️ 施工人員宣導確認簽名")
    st_canvas(stroke_width=3, background_color="#eee", height=250, key="sign_workers_all")
    c_s1, c_s2 = st.columns(2)
    c_s1.write("承辦單位簽名"); c_s2.write("工安人員簽名")
    st_canvas(stroke_width=3, background_color="#fafafa", height=100, key="sign_u")
    st_canvas(stroke_width=3, background_color="#fafafa", height=100, key="sign_s_f")
    if st.button("確認提交工具箱會議"):
        if "火災爆炸" in st.session_state.get('selected_hazards', []):
            st.session_state.current_page = "3. 動火作業許可證"
        else:
            st.session_state.current_page = "4. 特殊危害作業許可證"
        st.rerun()

# --- 3. 動火作業許可證 (完全不動) ---
elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("動火設備", key="fire_equip"); st.text_input("連絡電話", key="fire_tel")
        with col2:
            st.date_input("日期", value=date.today()); st.number_input("起(時)", 0, 23, 8); st.number_input("迄(時)", 0, 23, 17)
    st.write("**動火檢查表 (承攬/監工/環安)**")
    items = ["3公尺內有滅火器", "有警戒人員", "管線無可燃物", "周邊11公尺清空", "地面防火保護", "隔離偵測器"]
    for i, it in enumerate(items):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"{i+1}. {it}"); c2.checkbox("", key=f"f_v_{i}"); c3.checkbox("", key=f"f_s_{i}"); c4.checkbox("", key=f"f_h_{i}")
    st_canvas(stroke_width=3, background_color="#fafafa", height=100, key="sf_v")
    st_canvas(stroke_width=3, background_color="#fafafa", height=100, key="sf_s")
    if st.button("完成動火提交"):
        st.session_state.current_page = "1. 施工安全危害告知單"; st.rerun()

# --- 4. 特殊危害作業許可證 (重點修正區) ---
elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    
    with st.container(border=True):
        st.subheader("📋 申請資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**作業類別 (請勾選)**")
            spec_cat = {
                "局限空間": ["指派警戒人員隨時監視?", "氧氣濃度19%以上?", "測定危害物濃度?", "備有空氣呼吸器/安全帶?", "告知勞工潛在危害?"],
                "吊掛作業": ["吊車證照及防脫落裝置檢查?", "吊索/吊帶是否有損傷?", "嚴禁吊物下方站人?", "指揮人員佩戴哨子/紅旗?", "作業半徑設警示帶?"],
                "高架作業": ["1.8公尺以上確實佩戴安全帶?", "施工架設有護欄及掃腳板?", "下方設警示區域及看板?", "梯子是否有防滑及夾角限制?"],
                "危險管路": ["確實關閉來源閥門並掛牌?", "管內殘壓/殘液確認排空?", "配戴防護面罩/耐酸鹼手套?"],
                "送電作業": ["確實鎖定開關箱並掛維修牌?", "使用絕緣手套/絕緣墊?", "驗電筆確認無電後施工?"]
            }
            selected_cats = []
            for cat in spec_cat.keys():
                if st.checkbox(cat, key=f"sel_{cat}"):
                    selected_cats.append(cat)
            st.text_input("連絡電話", key="spec_tel_new")
        with col2:
            st.number_input("施工人數", min_value=1, step=1, key="spec_num_new")
            st.write("**作業期間 (限當日)**")
            sc1, sc2, sc3 = st.columns([2, 1, 1])
            s_date = sc1.date_input("日期", value=date.today(), key="sd")
            s_st = sc2.number_input("起", 0, 23, 8, key="ss"); s_et = sc3.number_input("迄", 0, 23, 17, key="se")

    if selected_cats:
        st.subheader("✅ 特殊危害作業檢查表 (連動內容)")
        h1, h2, h3, h4 = st.columns([4, 1, 1, 1])
        h1.write("**檢查重點**"); h2.write("承攬"); h3.write("監工"); h4.write("環安")

        for cat in selected_cats:
            st.markdown(f"**📍 {cat}項目**")
            for idx, item in enumerate(spec_cat[cat]):
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                c1.write(item)
                c2.checkbox("", key=f"sv_{cat}_{idx}", label_visibility="collapsed")
                c3.checkbox("", key=f"ss_{cat}_{idx}", label_visibility="collapsed")
                c4.checkbox("", key=f"sh_{cat}_{idx}", label_visibility="collapsed")
    else:
        st.warning("請先勾選上方「作業類別」以顯示檢查表")

    st.divider()
    st.subheader("✍️ 簽名核可")
    ss1, ss2 = st.columns(2)
    with ss1:
        st.write("施工單位簽名"); st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_v_n")
    with ss2:
        st.write("監工人員簽名"); st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_s_n")

    if st.button("完成特殊危害許可提交"):
        st.success("特殊危害作業申請成功！"); st.session_state.current_page = "1. 施工安全危害告知單"; st.rerun()
