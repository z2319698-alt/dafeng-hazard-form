import streamlit as st
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF
from PIL import Image
import numpy as np

# --- 【關鍵鎖定：權限攔截】 ---
# 如果 01 頁面沒核准，直接封鎖此頁面
if not st.session_state.get('auth_entry', False):
    st.error("⚠️ 存取拒絕：請先由承辦人員開立『進場確認單』。")
    st.info("請聯絡承辦人至 [01_entry_confirmation] 填寫核准資訊。")
    st.stop()

# --- 【後台連線：PDF 生成與 Drive 上傳】 ---
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
    if not service: return None
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except:
        return None

def create_pdf_report(title, data_dict, canvas_result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    
    for k, v in data_dict.items():
        safe_k = str(k).encode('latin-1', 'replace').decode('latin-1')
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=f"{safe_k}: {safe_v}")
    
    if canvas_result is not None and canvas_result.image_data is not None:
        img_array = canvas_result.image_data.astype('uint8')
        if np.any(img_array[:, :, 3] > 0):
            img = Image.fromarray(img_array, 'RGBA')
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='JPEG')
            pdf.ln(10)
            pdf.image(img_byte_arr, x=10, w=100)
    return pdf.output(dest='S')

# --- 【介面樣式設定】 ---
st.markdown("""
    <style>
    .factory-header { font-
