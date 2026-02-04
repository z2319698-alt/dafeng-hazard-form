import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

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
    if not service: return False
    folder_id = '1EHPRmig_vFpRS8cgz-8FsG88_LhT_JY5' 
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/pdf')
    try:
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except:
        return False

def create_pdf_report(title, data_dict, canvas_key):
    """
    修正編碼問題：使用 latin-1 替換法，避免中文導致當機。
    注意：這會在 PDF 裡把中文顯示為問號，但程式不會崩潰。
    若要完美顯示中文，需上傳字體檔並使用 pdf.add_font()。
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    
    for k, v in data_dict.items():
        # 關鍵修正：將中文安全轉換，避免拋出 EncodingException
        safe_text = f"{k}: {v}".encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=safe_text)
    
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
                pdf.image(img_byte_arr, x=10, w=60)
    return pdf.output(dest='S')

# --- 【介面樣式設定】 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"

st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) { background-color: #333333 !important; padding: 15px; border-radius: 10px; }
    .rule-text-white { font-size: 16px; color: #FFFFFF; margin-bottom: 12px; border-bottom: 1px solid #555555; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 【分流邏輯導航】 ---
# 1. 危害告知單
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知單")
    
    with st.container(border=True):
        st.subheader("👤 1. 基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            comp = st.text_input("承攬商名稱", key="comp_val")
            worker = st.text_input("施作人員姓名", key="worker_val")
        with col2:
            st.date_input("施工日期", value=date.today())
            loc = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
            st.session_state.location = loc

    st.subheader("📋 3. 安全衛生規定")
    rules = ["一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。", "二、設備維修需經主管同意並掛「維修中/保養中」牌。", "三、場內限速 15 公里/小時，嚴禁超速。", "四、工作場所禁止吸菸、飲食或飲酒。", "五、操作機具需持證照且經主管同意，相關責任由借用者自負。", "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。", "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。", "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。", "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。", "十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。", "十一、清運車輛啟動前應確認周遭並發出信號。", "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。", "十三、未達指定傾貨區前，嚴禁私自開啟車斗。", "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。", "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"]
    full_html = "".join([f"<div class='rule-text-white'>{r}</div>" for r in rules])
    with st.container(height=300, border=True):
        st.markdown(full_html, unsafe_allow_html=True)
    
    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_h")
    
    if st.button("確認提交告知單並存檔"):
        if not read_ok:
            st.warning("⚠️ 請勾選同意規定")
        else:
            with st.spinner("存檔中..."):
                st.session_state.company = comp
                st.session_state.worker_name = worker
                pdf_bytes = create_pdf_report("Hazard Notice", {"Comp": comp, "Name": worker}, "sign_h")
                if upload_to_drive(pdf_bytes, f"01_Hazard_{comp}_{date.today()}.pdf"):
                    st.success("✅ 告知單已存檔至雲端資料夾！")
                    st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
                    st.rerun()

# 2. 工具箱會議
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.subheader("📋 會議基本資訊")
        st.write(f"**廠商:** {st.session_state.get('company','')} | **地點:** {st.session_state.get('location','')}")
        st.text_area("工程內容", key="tool_content")
    
    st.subheader("✅ 宣導事項 (勾選決定下一張單)")
    hazard_options = ["墜落", "中毒", "缺氧", "爆炸", "火災", "感電", "跌倒", "衝撞"]
    cols = st.columns(4)
    sel_haz = []
    for i, opt in enumerate(hazard_options):
        if cols[i % 4].checkbox(opt, key=f"t_haz_{opt}"):
            sel_haz.append(opt)

    st.write("施工人員簽名 (大空格)")
    st_canvas(stroke_width=3, background_color="#eee", height=200, key="sign_toolbox")
    
    if st.button("確認提交工具箱會議"):
        with st.spinner("存檔中..."):
            pdf_bytes = create_pdf_report("Toolbox", {"Comp": st.session_state.company}, "sign_toolbox")
            upload_to_drive(pdf
