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

# --- 【後台連線：修正 PDF 報錯且不改動介面】 ---
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
    # 使用 Helvetica 確保不當機，簽名會原樣手寫呈現
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    
    for k, v in data_dict.items():
        # 過濾中文避免 Exception，保留英文標籤
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=f"{k}: {safe_v}", ln=True)
    
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
            pdf.ln(10)
            pdf.cell(200, 10, txt="Signature:", ln=True)
            pdf.image(img_byte_arr, x=10, w=80)
    return pdf.output(dest='S')

# --- 你原本的介面設定 (完全保留) ---
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
    rules = ["一、為防止尖銳物切割危害，應佩戴安全手套。", "二、設備維修需掛牌。", "三、場內限速 15 公里。", "四、工作場所禁止吸菸。", "五、操作機具需持證照。"]
    full_html = "".join([f"<div class='rule-text-white'>{r}</div>" for r in rules])
    with st.container(height=200, border=True):
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
        st.write(f"**作業廠商:** {st.session_state.get('company','')}")
        st.text_area("工程內容", key="tool_content")
    
    st_canvas(stroke_width=3, background_color="#eee", height=200, key="sign_workers_all")
    
    if st.button("確認提交工具箱會議"):
        if "火災爆炸" in st.session_state.get('selected_hazards', []):
            st.session_state.current_page = "3. 動火作業許可證"
        else:
            st.session_state.current_page = "4. 特殊危害作業許可證"
        st.rerun()

elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    st.text_input("動火設備", key="fire_equip")
    st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_fire_v")
    
    if st.button("完成動火許可提交"):
        with st.spinner("上傳雲端中..."):
            data = {"Company": st.session_state.get('company',''), "Worker": st.session_state.get('worker_name','')}
            pdf_bytes = create_pdf_report("Hot Work Permit", data, "sign_fire_v")
            upload_to_drive(pdf_bytes, f"Fire_{date.today()}.pdf")
            st.success("動火作業申請成功！")
            st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()

elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    st.checkbox("高架作業", key="spec_type_1")
    st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_v")
    
    if st.button("完成特殊危害許可提交"):
        with st.spinner("上傳雲端中..."):
            data = {"Company": st.session_state.get('company',''), "Worker": st.session_state.get('worker_name','')}
            pdf_bytes = create_pdf_report("Special Work Permit", data, "sign_spec_v")
            upload_to_drive(pdf_bytes, f"Special_{date.today()}.pdf")
            st.success("特殊危害作業申請成功！")
            st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()
