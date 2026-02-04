import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

# --- 1. 後台功能：PDF 引擎與雲端上傳 ---
def get_drive_service():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception:
        return None

def upload_to_drive(file_content, file_name):
    service = get_drive_service()
    if not service: return False
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    try:
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except:
        return False

def quick_pdf(title, content_list, canvas_key):
    """通用單頁 PDF 生成器"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    
    # 寫入文字內容
    for line in content_list:
        safe_line = str(line).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=safe_line)
    
    # 寫入簽名
    if canvas_key in st.session_state and st.session_state[canvas_key] is not None:
        canvas_data = st.session_state[canvas_key]
        if hasattr(canvas_data, "image_data") and canvas_data.image_data is not None:
            from PIL import Image
            import numpy as np
            img_array = canvas_data.image_data.astype('uint8')
            if np.any(img_array[:, :, 3] > 0):
                img = Image.fromarray(img_array, 'RGBA')
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img_byte_arr = io.BytesIO()
                bg.save(img_byte_arr, format='JPEG')
                pdf.ln(10)
                pdf.image(img_byte_arr, x=10, w=70)
    return pdf.output(dest='S')

# --- 2. 介面設定 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"
if 'selected_hazards' not in st.session_state:
    st.session_state.selected_hazards = []

st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    .rule-text-white { font-size: 16px; color: #FFFFFF; margin-bottom: 8px; border-bottom: 1px solid #555; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) { background-color: #333 !important; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 頁面邏輯 ---

# 頁面 1: 危害告知單 (必填)
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知單")
    
    comp = st.text_input("承攬商名稱", key="main_comp")
    worker = st.text_input("施作人員姓名", key="main_worker")
    loc = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
    hazards = st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"])
    
    st.subheader("📋 安全衛生規定")
    with st.container(height=250):
        st.markdown("1. 佩戴安全防護具... (略)") # 規定文字維持
    
    read_ok = st.checkbox("我已同意遵守規定")
    st_canvas(stroke_width=3, background_color="#eee", height=120, key="sign_page1")
    
    if st.button("確認提交告知單並存檔"):
        st.session_state.selected_hazards = hazards
        # 立即存 PDF
        pdf_content = quick_pdf("Hazard Notice", [f"Company: {comp}", f"Worker: {worker}", f"Hazards: {hazards}"], "sign_page1")
        upload_to_drive(pdf_content, f"01_Hazard_{comp}_{date.today()}.pdf")
        
        st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
        st.rerun()

# 頁面 2: 工具箱會議 (必填)
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    co_comp = st.text_input("共同作業廠商")
    content = st.text_area("工程內容")
    
    st_canvas(stroke_width=3, background_color="#eee", height=200, key="sign_page2")
    
    if st.button("確認提交工具箱會議並存檔"):
        # 立即存 PDF
        pdf_content = quick_pdf("Toolbox Meeting", [f"Co-Comp: {co_comp}", f"Content: {content}"], "sign_page2")
        upload_to_drive(pdf_content, f"02_Toolbox_{st.session_state.get('main_comp','')}_{date.today()}.pdf")
        
        # 判斷下一步要去哪 (模糊比對)
        haz_list = st.session_state.selected_hazards
        if "火災爆炸" in haz_list:
            st.session_state.current_page = "3. 動火作業許可證"
        elif any(x in haz_list for x in ["墜落", "缺氧窒息", "感電"]):
            st.session_state.current_page = "4. 特殊危害作業許可證"
        else:
            st.success("表單已全部完成！")
            st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()

# 頁面 3: 動火作業
elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    # ... (你的檢查項目 17 項維持不變) ...
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_page3")
    
    if st.button("完成提交動火許可"):
        pdf_content = quick_pdf("Hot Work Permit", ["Status: Approved"], "sign_page3")
        upload_to_drive(pdf_content, f"03_Fire_{date.today()}.pdf")
        
        # 動火填完，檢查是否還要填特殊作業
        haz_list = st.session_state.selected_hazards
        if any(x in haz_list for x in ["墜落", "缺氧窒息", "感電"]):
            st.session_state.current_page = "4. 特殊危害作業許可證"
        else:
            st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()

# 頁面 4: 特殊危害
elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    # ... (介面維持不變) ...
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_page4")
    
    if st.button("完成提交特殊作業許可"):
        pdf_content = quick_pdf("Special Work Permit", ["Status: Approved"], "sign_page4")
        upload_to_drive(pdf_content, f"04_Special_{date.today()}.pdf")
        
        st.success("所有表單皆已存檔！")
        st.session_state.current_page = "1. 施工安全危害告知單"
        st.rerun()
