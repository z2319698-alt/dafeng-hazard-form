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

# --- 1. Google Drive 連線設定 ---
def get_drive_service():
    try:
        # 從 st.secrets 讀取 TOML 格式金鑰
        info = dict(st.secrets["gcp_service_account"])
        # 修正私鑰換行符號
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception as e:
        st.error(f"⚠️ 金鑰連線失敗: {e}")
        return None

def upload_to_drive(file_content, file_name):
    service = get_drive_service()
    if not service: return None
    
    # 這裡請確認你的 Google Drive 資料夾 ID 是否正確
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"❌ 上傳失敗: {e}")
        return None

# --- 2. PDF 生成邏輯 ---
def create_pdf(form_data, sig_canvas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="DAFENG Hazard Form - Hot Work Permit", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    for key, value in form_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    
    # 處理簽名圖片
    if sig_canvas is not None and sig_canvas.image_data is not None:
        from PIL import Image
        import numpy as np
        img_data = sig_canvas.image_data
        img = Image.fromarray(img_data.astype('uint8'), 'RGBA')
        # 轉為 RGB 才能存入 PDF
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        
        img_byte_arr = io.BytesIO()
        bg.save(img_byte_arr, format='JPEG')
        pdf.ln(5)
        pdf.cell(200, 10, txt="Signature:", ln=True)
        pdf.image(img_byte_arr, x=10, y=pdf.get_y(), w=50)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 3. Streamlit 介面 ---
st.title("大豐環保安全系統")

tab1, tab2, tab3 = st.tabs(["環境檢查", "施工申請", "動火作業許可"])

with tab3:
    st.header("🔥 動火作業許可證")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("施工廠商", key="fire_co")
        worker = st.text_input("作業負責人", key="fire_work")
    with col2:
        location = st.text_input("施工地點", key="fire_loc")
        target = st.text_input("動火對象", key="fire_obj")

    st.write("---")
    st.write("手寫簽名確認：")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="sign_fire",
    )

    if st.button("完成提交並上傳"):
        if not company or not worker:
            st.warning("請填寫廠商與負責人名稱")
        else:
            with st.spinner("正在處理中..."):
                data_summary = {
                    "Company": company,
                    "Responsible": worker,
                    "Location": location,
                    "Object": target,
                    "Date": str(date.today())
                }
                
                # 生成 PDF
                pdf_output = create_pdf(data_summary, canvas_result)
                
                # 上傳 Drive
                fname = f"Fire_{date.today()}_{company}.pdf"
                fid = upload_to_drive(pdf_output, fname)
                
                if fid:
                    st.success(f"✅ 上傳成功！檔案存放在 Google Drive (ID: {fid})")
                    st.balloons()
