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

# --- 權限攔截 ---
if not st.session_state.get('auth_entry', False):
    st.error("⚠️ 存取拒絕：請先由承辦人員開立『進場確認單』。")
    st.stop()

# --- 1. 後台函數 (Drive & PDF) ---
def upload_to_drive(file_content, file_name):
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=credentials.with_scopes(['https://www.googleapis.com/auth/drive.file']))
        
        folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except: return None

def create_pdf(title, data, canvas_data):
    pdf = FPDF()
    pdf.add_page()
    # 注意：若要支援中文，需上傳字體檔並用 pdf.add_font()，目前先用預設避免報錯
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    for k, v in data.items():
        pdf.multi_cell(0, 10, txt=f"{k}: {v}")

    if canvas_data is not None and canvas_data.image_data is not None:
        img_array = canvas_data.image_data.astype('uint8')
        if np.any(img_array[:, :, 3] > 0):
            img = Image.fromarray(img_array, 'RGBA')
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='JPEG')
            pdf.ln(10)
            pdf.image(img_byte_arr, x=10, w=100)
    return pdf.output(dest='S')

# --- 2. 介面呈現 ---
st.title("🚧 02 承攬商施工安全危害告知單")
comp = st.session_state.get('company', '')
loc = st.session_state.get('location', '')

st.info(f"✅ 已授權廠商：**{comp}** | 施工地點：**{loc}**")

with st.container(border=True):
    worker = st.text_input("施作人員姓名", key="worker_name")
    hazards = st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息"])

st.subheader("📋 安全衛生規定 (15條)")
rules = ["一、為防止尖銳物危害...", "二、設備維修需掛牌..."] # 此處可自行補完
st.markdown(f"<div style='background:#333;color:white;padding:15px;border-radius:5px;'>{'<br>'.join(rules)}</div>", unsafe_allow_html=True)

read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
canvas_result = st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_hazard")

if st.button("確認提交並存檔 PDF"):
    if not read_ok or canvas_result.image_data is None:
        st.warning("⚠️ 請勾選同意並完成簽名！")
    else:
        with st.spinner("PDF 生成中並上傳至 Google Drive..."):
            p_data = {"Company": comp, "Location": loc, "Worker": worker, "Date": str(date.today())}
            pdf_bytes = create_pdf("Hazard Communication Form", p_data, canvas_result)
            fname = f"Hazard_{comp}_{date.today()}.pdf"
            if upload_to_drive(pdf_bytes, fname):
                st.success(f"✅ 存檔成功！檔名：{fname}")
            else:
                st.error("❌ 上傳失敗，請檢查雲端權限設定。")
