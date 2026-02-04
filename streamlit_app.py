import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

# --- 1. Google Drive 連線邏輯 ---
def get_drive_service():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception as e:
        st.error(f"⚠️ 連線失敗: {e}")
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
    except Exception as e:
        st.error(f"❌ 上傳失敗: {e}")
        return None

# --- 2. 介面與表單內容 ---
st.set_page_config(page_title="大豐環保安全系統", layout="centered")
st.title("🛡️ 大豐環保安全作業管理系統")

tab1, tab2, tab3 = st.tabs(["📋 環境檢查", "🏗️ 施工申請", "🔥 動火作業許可"])

with tab3:
    st.header("動火作業許可證申請")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("施工廠商", placeholder="請輸入廠商全名", key="co_f")
        location = st.text_input("施工地點", placeholder="例如：倉庫後方", key="loc_f")
    with col2:
        worker = st.text_input("作業負責人", placeholder="請輸入負責人姓名", key="work_f")
        hot_type = st.selectbox("動火類型", ["電焊", "氧乙炔切割", "砂輪機切削", "其他"], key="type_f")

    st.subheader("✅ 安全檢查項目")
    c1, c2 = st.columns(2)
    with c1:
        check1 = st.checkbox("清除周遭易燃物 (10公尺內)")
        check2 = st.checkbox("備妥滅火器且壓力正常")
    with c2:
        check3 = st.checkbox("派駐專人監護")
        check4 = st.checkbox("施工人員穿戴防護具")

    st.write("---")
    st.write("✍️ **作業負責人手寫簽名：**")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="sign_fire_final",
    )

    if st.button("確認提交並產生 PDF"):
        if not company or not worker:
            st.error("請填寫廠商與負責人名稱！")
        elif not (check1 and check2 and check3 and check4):
            st.warning("所有安全檢查項目皆須勾選才能提交！")
        else:
            with st.spinner("正在產生 PDF 並存入雲端..."):
                # --- PDF 修正寫法 ---
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="DAFENG Hot Work Permit", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
                pdf.cell(200, 10, txt=f"Company: {company}", ln=True)
                pdf.cell(200, 10, txt=f"Responsible: {worker}", ln=True)
                
                # 核心修正：output() 直接返回 bytes，不帶引數
                pdf_bytes = pdf.output() 
                
                fname = f"Fire_{date.today()}_{company}.pdf"
                fid = upload_to_drive(pdf_bytes, fname)
                
                if fid:
                    st.success(f"✅ 提交成功！檔案 ID: {fid}")
                    st.balloons()
