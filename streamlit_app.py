import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

# --- 【後台連線工具：不影響介面】 ---
def get_drive_service():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception as e:
        return None

def upload_to_drive(file_content, file_name):
    service = get_drive_service()
    if not service: return None
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except:
        return None

def create_pdf_report(title, data_dict, canvas_key):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for k, v in data_dict.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    
    if canvas_key in st.session_state:
        canvas_data = st.session_state[canvas_key]
        if canvas_data is not None and canvas_data.image_data is not None:
            from PIL import Image
            import numpy as np
            img = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='JPEG')
            pdf.ln(5)
            pdf.image(img_byte_arr, x=10, w=60)
    return pdf.output()

# --- 你早上的介面設定 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"
if 'selected_hazards' not in st.session_state:
    st.session_state.selected_hazards = []

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

st.sidebar.title("📋 表單選單")
pages = ["1. 施工安全危害告知單", "2. 承攬商工具箱會議紀錄表", "3. 動火作業許可證", "4. 特殊危害作業許可證"]
for p in pages:
    if st.sidebar.button(p):
        st.session_state.current_page = p

if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
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
    rules = ["一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。", "二、設備維修需經主管同意並掛「維修中/保養中」牌。", "三、場內限速 15 公里/小時，嚴禁超速。", "四、工作場所禁止吸菸、飲食或飲酒。", "五、操作機具需持證照且經主管同意，相關責任由借用者自負。", "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。", "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。", "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。", "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。", "十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。", "十一、清運車輛啟動前應確認周遭並發出信號。", "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。", "十三、未達指定傾貨區前，嚴禁私自開啟車斗。", "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。", "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"]
    full_html = "".join([f"<div class='rule-text-white'>{r}</div>" for r in rules])
    with st.container(height=300, border=True):
        st.markdown(full_html, unsafe_allow_html=True)
    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
    st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="sign_h")
    if st.button("確認提交告知單", disabled=not read_ok):
        st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
        st.rerun()

elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.subheader("📋 會議基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**作業廠商:** {st.session_state.get('company','')}")
            st.text_input("共同作業廠商", key="tool_co_comp")
            st.text_area("工程內容", placeholder="請輸入本日施工簡述", key="tool_content")
        with col2:
            st.write(f"**施工位置:** {st.session_state.get('location','')}")
            st.number_input("總作業人數", min_value=1, step=1, key="tool_total_num")
            st.write(f"**會議日期:** {date.today()}")
    with st.container(border=True):
        st.subheader("✅ 宣導事項勾選")
        hazard_options = ["墜落", "跌倒", "火災", "中毒", "缺氧", "衝撞", "感電", "物體飛落", "切、割、夾、捲", "爆炸", "物體破裂", "物體倒塌"]
        cols = st.columns(4)
        for i, opt in enumerate(hazard_options):
            cols[i % 4].checkbox(opt, key=f"tool_haz_{opt}")
    st.subheader("✍️ 當日施工人員宣導確認簽名 (大空格)")
    st_canvas(stroke_width=3, background_color="#eee", height=250, key="sign_workers_all")
    col_sign1, col_sign2 = st.columns(2)
    with col_sign1:
        st.write("承辦單位人員簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_unit_final")
    with col_sign2:
        st.write("工安人員簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_safety_final")
    if st.button("確認提交工具箱會議"):
        if "火災爆炸" in st.session_state.get('selected_hazards', []):
            st.session_state.current_page = "3. 動火作業許可證"
        else:
            st.session_state.current_page = "4. 特殊危害作業許可證"
        st.rerun()

elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    with st.container(border=True):
        st.subheader("📋 動火申請資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("動火設備", key="fire_equip")
            st.text_input("連絡電話", key="fire_tel")
        with col2:
            st.write("**作業期間 (限當日)**")
            c1, c2, c3 = st.columns([2, 1, 1])
            f_date = c1.date_input("日期", value=date.today(), key="f_date")
            f_start = c2.number_input("起(時)", 0, 23, 8, key="f_start")
            f_end = c3.number_input("迄(時)", 0, 23, 17, key="f_end")
    st.subheader("✅ 動火檢查表")
    h_col1, h_col2, h_col3, h_col4 = st.columns([4, 1, 1, 1])
    h_col1.write("**檢查重點**")
    h_col2.write("承攬商")
    h_col3.write("監工")
    h_col4.write("環安")
    
    check_items = [
        "3 公尺內備有可使用/正常操作之自動灑水或手提滅火器", "防爆區或侷限空間內作業由工安單位測定可燃性氣體濃度",
        "動火時旁邊有警戒人員", "排除管線內可燃性物質", "隔離或中斷該區域之火警偵測器",
        "清除工作區域週邊 11 公尺內的可燃物或使用防火毯覆蓋保護", "工作區域易燃性地面予以防火保護",
        "工作區域週邊的地面及牆面不得有開口或使用防火毯覆蓋保護", "動火作業人員的安全眼鏡、面罩、手套等防護具",
        "施工產生之火花予以收集，工作區域內用防火布加以保護", "建築結構為不易燃性材料建造，或為不易燃性材料覆蓋保護",
        "須移走牆背面的易燃物質", "電焊機接頭及接地良好，並有自動電擊防止裝置",
        "鋼瓶直立或使用鋼瓶推車固定並有安全逆止閥", "每日收工前將火警系統中斷復歸，並檢點施工環境安全",
        "環境整理復歸，材料器材工具收拾整齊", "施工完畢後 30 分鐘動火場所覆查，沒有餘燼或悶燒情形"
    ]
    
    for idx, item in enumerate(check_items):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"{idx+1}. {item}")
        c2.checkbox("", key=f"f_v_{idx}", label_visibility="collapsed")
        c3.checkbox("", key=f"f_s_{idx}", label_visibility="collapsed")
        c4.checkbox("", key=f"f_h_{idx}", label_visibility="collapsed")
    st.divider()
    st.subheader("✍️ 簽名欄位")
    sig1, sig2 = st.columns(2)
    with sig1:
        st.write("施工單位簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_fire_v")
    with sig2:
        st.write("監工單位簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_fire_s")
    
    if st.button("完成動火許可提交"):
        with st.spinner("PDF 生成中並上傳雲端..."):
            data = {"Company": st.session_state.get('company',''), "Worker": st.session_state.get('worker_name',''), "Date": str(date.today())}
            pdf_bytes = create_pdf_report("Hot Work Permit", data, "sign_fire_v")
            upload_to_drive(pdf_bytes, f"Fire_{date.today()}_{data['Company']}.pdf")
            st.success("動火作業申請成功！")
            st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()

elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    with st.container(border=True):
        st.subheader("📋 特殊作業申請資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**作業類別**")
            type_cols = st.columns(2)
            spec_types = ["局限空間", "吊掛", "高架", "危險管路拆卸鑽孔", "送電作業"]
            selected_types = {t: type_cols[i % 2].checkbox(t, key=f"spec_type_{t}") for i, t in enumerate(spec_types)}
            st.text_input("連絡電話", key="spec_tel")
        with col2:
            st.number_input("施工人數", min_value=1, step=1, key="spec_workers")
            st.write("**作業期間 (限當日)**")
            sc1, sc2, sc3 = st.columns([2, 1, 1])
            s_date = sc1.date_input("日期", value=date.today(), key="s_date")
            s_start = sc2.number_input("起(時)", 0, 23, 8, key="s_start")
            s_end = sc3.number_input("迄(時)", 0, 23, 17, key="s_end")

    st.subheader("✅ 特殊危害作業檢查表")
    check_data = {
        "局限空間": ["指派安全警戒人員，隨時監視?", "氧氣濃度在19%以上?", "測定危害物濃度在容許值以下?", "備有空氣呼吸器、安全帶供戴用?", "告知勞工施工區域潛在危害?"],
        "吊掛": ["吊車具合格證且吊鉤有防脫裝置?", "吊索、吊帶無受損及變形?", "嚴禁吊物下方站人並設警戒區?", "指派指揮人員佩戴紅旗/哨子?"],
        "高架": ["1.8公尺以上確實佩戴安全帶?", "施工架設置護欄及掃腳板?", "下方設置警示區域及看板?"],
        "危險管路拆卸鑽孔": ["確實關閉來源閥門並掛牌?", "管內殘壓/殘液排空確認?", "配戴防護面罩/耐酸鹼手套?"],
        "送電作業": ["開關箱鎖定並掛維修告知牌?", "使用絕緣手套/絕緣墊?", "驗電筆確認無殘電?"]
    }

    has_checked_any = False
    for t_name, is_selected in selected_types.items():
        if is_selected:
            has_checked_any = True
            st.markdown(f"**📍 {t_name} 檢查項目**")
            for idx, item in enumerate(check_data.get(t_name, [])):
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                c1.write(f"- {item}")
                c2.checkbox("", key=f"s_v_{t_name}_{idx}", label_visibility="collapsed")
                c3.checkbox("", key=f"s_s_{t_name}_{idx}", label_visibility="collapsed")
                c4.checkbox("", key=f"s_h_{t_name}_{idx}", label_visibility="collapsed")

    if not has_checked_any: st.info("請先於上方勾選「作業類別」以顯示對應檢查表")

    st.divider()
    st.subheader("✍️ 簽名核可")
    ssig1, ssig2 = st.columns(2)
    with ssig1:
        st.write("施工單位簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_v")
    with ssig2:
        st.write("監工人員簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_s")

    if st.button("完成特殊危害許可提交"):
        with st.spinner("上傳雲端中..."):
            data = {"Company": st.session_state.get('company',''), "Worker": st.session_state.get('worker_name',''), "Date": str(date.today())}
            pdf_bytes = create_pdf_report("Special Work Permit", data, "sign_spec_v")
            upload_to_drive(pdf_bytes, f"Special_{date.today()}_{data['Company']}.pdf")
            st.success("特殊危害作業申請成功！")
            st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()
