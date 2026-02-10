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

# --- 1. 權限攔截：沒開單不准進來 ---
if not st.session_state.get('auth_entry', False):
    st.error("⚠️ 存取拒絕：請先由承辦人員開立『進場確認單』。")
    st.info("請點擊左側選單的『01_entry_confirmation』進行開單。")
    st.stop()

# --- 2. 後台函數 (保持你原本的邏輯) ---
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
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except: return False

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

# --- 3. 介面樣式 ---
st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    .rule-box { background-color: #333333; padding: 15px; border-radius: 10px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頁面內容 ---
st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
st.title("🚧 02. 施工安全危害告知單")

# 自動帶入第 1 頁的資料
comp = st.session_state.get('company','')
loc = st.session_state.get('location','')
st.info(f"✅ 已授權廠商：{comp} | 地點：{loc}")

worker = st.text_input("施作人員姓名", key="in_worker")

with st.expander("📋 查看 15 條安全衛生規定"):
    rules = ["一、應佩戴安全手套、安全鞋...", "二、設備維修需掛牌...", " (此處自行補完) "]
    st.markdown("<br>".join(rules), unsafe_allow_html=True)

read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
canvas_result = st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_h")

if st.button("確認提交告知單並存檔"):
    if not read_ok or canvas_result.image_data is None:
        st.warning("⚠️ 請勾選同意並完成簽名！")
    else:
        with st.spinner("存檔至 Google Drive..."):
            pdf_bytes = create_pdf_report("Hazard Notice", {"Company": comp, "Worker": worker}, canvas_result)
            fname = f"01_Hazard_{comp}_{date.today()}.pdf"
            if upload_to_drive(pdf_bytes, fname):
                st.success(f"✅ 存檔完成：{fname}")
            else:
                st.error("❌ 上傳失敗，請檢查權限。")
