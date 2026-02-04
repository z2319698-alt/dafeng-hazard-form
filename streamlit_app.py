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
    """透過 secrets.toml 取得 Google Drive 連線權限"""
    try:
        # 讀取 Secrets
        info = dict(st.secrets["gcp_service_account"])
        # 處理私鑰換行符號的終極防護
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception as e:
        st.error(f"⚠️ 金鑰連線失敗，請檢查 Secrets 格式: {e}")
        return None

def upload_to_drive(file_content, file_name):
    """將生成的 PDF 上傳至指定的 Google Drive 資料夾"""
    service = get_drive_service()
    if not service: return None
    
    # 你提供的 Google Drive 資料夾 ID
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
        st.error(f"❌ 上傳 Google Drive 失敗: {e}")
        return None

# --- 2. 頁面設定 ---
st.set_page_config(page_title="大豐環保安全作業管理系統", layout="wide")
st.title("🛡️ 大豐環保安全作業管理系統")

# 定義分頁
tab1, tab2, tab3 = st.tabs(["📋 1. 環境檢查", "🏗️ 2. 施工申請", "🔥 3. 動火作業許可"])

# --- Tab 1: 環境檢查 (保留完整欄位) ---
with tab1:
    st.header("每日環境安全檢查")
    with st.form("env_form"):
        col1, col2 = st.columns(2)
        with col1:
            check_date = st.date_input("檢查日期", date.today())
            area = st.selectbox("檢查區域", ["一廠", "二廠", "辦公室", "戶外場地"])
        with col2:
            inspector = st.text_input("檢查人員")
        
        st.write("**檢查項目：**")
        env_1 = st.checkbox("地面是否有積水或油漬？")
        env_2 = st.checkbox("消防栓/滅火器是否無遮擋？")
        env_3 = st.checkbox("電線是否有裸露或過載？")
        
        if st.form_submit_state("提交環境檢查"):
            st.success("環境檢查已紀錄（目前僅介面顯示）")

# --- Tab 2: 施工申請 (保留完整欄位) ---
with tab2:
    st.header("施工安全申請")
    with st.form("work_form"):
        c1, c2 = st.columns(2)
        with c1:
            work_co = st.text_input("施工單位")
            work_name = st.text_input("工程名稱")
        with c2:
            work_leader = st.text_input("現場負責人")
            work_type = st.multiselect("作業類型", ["高處作業", "吊掛作業", "電氣作業", "其他"])
        
        if st.form_submit_state("提交施工申請"):
            st.success("施工申請已發送（目前僅介面顯示）")

# --- Tab 3: 動火作業許可 (最完整的功能含 PDF) ---
with tab3:
    st.header("🔥 動火作業許可證申請")
    
    # 填寫資料區
    with st.container():
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            f_company = st.text_input("施工廠商名稱", key="fire_co_full")
            f_location = st.text_input("具體動火地點", key="fire_loc_full")
        with f_col2:
            f_worker = st.text_input("作業負責人", key="fire_work_full")
            f_type = st.selectbox("動火工具", ["電焊機", "氣割工具", "砂輪機", "噴燈", "其他"], key="fire_type_full")

    st.subheader("✅ 動火安全檢查項目 (須全部勾選)")
    chk_col1, chk_col2 = st.columns(2)
    with chk_col1:
        f_chk1 = st.checkbox("動火地點 10 公尺內已清除易燃物")
        f_chk2 = st.checkbox("附近備有足夠且合格之滅火器")
    with chk_col2:
        f_chk3 = st.checkbox("已派駐現場防火監護人")
        f_chk4 = st.checkbox("高處作業已設置防火毯遮擋火花")

    st.write("---")
    st.write("✍️ **作業負責人手寫簽名：**")
    f_canvas = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="fire_sign_canvas",
    )

    if st.button("🚀 確認提交並上傳雲端 PDF"):
        if not f_company or not f_worker:
            st.error("請完整填寫『施工廠商』與『負責人』！")
        elif not (f_chk1 and f_chk2 and f_chk3 and f_chk4):
            st.warning("所有安全檢查項目必須勾選，確保作業安全！")
        else:
            with st.spinner("正在產生 PDF 並同步上傳至 Google Drive..."):
                # 1. 建立 PDF 物件
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="DAFENG ENVIRONMENTAL PROTECTION", ln=True, align='C')
                pdf.cell(200, 10, txt="Hot Work Permit", ln=True, align='C')
                pdf.ln(10)
                
                # 2. 寫入表單內容 (目前 FPDF 預設不支援中文，先用英文標籤避免亂碼)
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
                pdf.cell(200, 10, txt=f"Company: {f_company}", ln=True)
                pdf.cell(200, 10, txt=f"Location: {f_location}", ln=True)
                pdf.cell(200, 10, txt=f"Responsible: {f_worker}", ln=True)
                pdf.cell(200, 10, txt=f"Tool Type: {f_type}", ln=True)
                pdf.ln(5)
                pdf.cell(200, 10, txt="Safety Checks: Passed", ln=True)
                
                # 3. 處理簽名 (將畫布轉圖片)
                if f_canvas.image_data is not None:
                    from PIL import Image
                    img = Image.fromarray(f_canvas.image_data.astype('uint8'), 'RGBA')
                    # 轉為 RGB
                    white_bg = Image.new("RGB", img.size, (255, 255, 255))
                    white_bg.paste(img, mask=img.split()[3])
                    img_byte_arr = io.BytesIO()
                    white_bg.save(img_byte_arr, format='JPEG')
                    pdf.ln(5)
                    pdf.cell(200, 10, txt="Signature:", ln=True)
                    pdf.image(img_byte_arr, x=10, y=pdf.get_y(), w=50)

                # 4. 輸出與上傳
                pdf_bytes = pdf.output()
                file_name = f"HotWork_{date.today()}_{f_company}.pdf"
                drive_id = upload_to_drive(pdf_bytes, file_name)
                
                if drive_id:
                    st.success(f"✅ 提交成功！檔案已存入 Google Drive")
                    st.info(f"檔案 ID: {drive_id}")
                    st.balloons()
