import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

# --- 【1. 後台功能：PDF 引擎與雲端上傳】 ---
def get_drive_service():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except Exception as e:
        st.error(f"雲端連線失敗: {e}")
        return None

def upload_to_drive(file_content, file_name):
    service = get_drive_service()
    if not service: return False
    # 這是你指定的 Google Drive 資料夾 ID
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    try:
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except Exception as e:
        st.error(f"檔案上傳失敗: {e}")
        return False

def create_single_pdf(title, data_dict, canvas_key):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    for k, v in data_dict.items():
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=f"{k}: {safe_v}", ln=True)
    
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
                pdf.image(img_byte_arr, x=10, w=80)
    return pdf.output(dest='S')

# --- 【2. 介面與導航邏輯】 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"

st.sidebar.title("📋 表單分頁選單")
st.sidebar.info(f"📍 目前位置：\n{st.session_state.current_page}")
pages = ["1. 施工安全危害告知單", "2. 承攬商工具箱會議紀錄表", "3. 動火作業許可證", "4. 特殊危害作業許可證"]
for p in pages:
    if st.sidebar.button(p):
        st.session_state.current_page = p
        st.rerun()

# --- 【3. 頁面內容】 ---

# 頁面 1
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.title("🚧 施工安全危害告知單")
    comp = st.text_input("承攬商名稱", key="c1")
    user = st.text_input("簽署人姓名", key="u1")
    hazards = st.multiselect("危害因素", ["墜落", "感電", "火災爆炸", "物體飛落", "缺氧窒息"])
    
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_1")
    
    if st.button("🚀 提交此表單並存檔"):
        if not comp or not user:
            st.warning("請填寫廠商名稱與姓名再送出！")
        else:
            with st.spinner("正在上傳至 Google Drive..."):
                st.session_state.selected_hazards = hazards
                data = {"Company": comp, "User": user, "Hazards": hazards}
                pdf_bytes = create_single_pdf("Hazard Notice", data, "sign_1")
                filename = f"01_Hazard_{comp}_{date.today()}.pdf"
                
                if upload_to_drive(pdf_bytes, filename):
                    st.success(f"✅ 已成功存檔！檔名：{filename}")
                    st.toast("告知單上傳成功！")
                    st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
                    st.button("點此進入下一頁：工具箱會議")
                else:
                    st.error("存檔失敗，請檢查網路或憑證設定。")

# 頁面 2
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 工具箱會議紀錄表")
    st.write(f"廠商：{st.session_state.get('c1', '未填寫')}")
    job_content = st.text_area("本次工程簡述")
    
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_2")
    
    if st.button("🚀 提交工具箱會議紀錄"):
        with st.spinner("上傳中..."):
            data = {"Content": job_content}
            pdf_bytes = create_single_pdf("Toolbox Meeting", data, "sign_2")
            filename = f"02_Toolbox_{date.today()}.pdf"
            
            if upload_to_drive(pdf_bytes, filename):
                st.success("✅ 工具箱會議存檔成功！")
                
                # 自動分流邏輯
                hazards = st.session_state.get('selected_hazards', [])
                if "火災爆炸" in hazards:
                    st.session_state.current_page = "3. 動火作業許可證"
                    st.info("⚠️ 偵測到『火災爆炸』因素，請繼續填寫動火許可證。")
                elif any(h in hazards for h in ["墜落", "缺氧窒息", "感電"]):
                    st.session_state.current_page = "4. 特殊危害作業許可證"
                    st.info("⚠️ 偵測到高風險因素，請繼續填寫特殊作業許可證。")
                else:
                    st.balloons()
                    st.success("恭喜！所有必填表單已完成。")
            st.rerun()

# 頁面 3 & 4 依此類推... (代碼邏輯相同，確保每個按鈕都有 st.success)
