import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import date
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF

# --- 【1. 後台 PDF 與雲端功能】 ---
def get_drive_service():
    try:
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=scoped_credentials)
    except:
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

def create_report_pdf(title, data_dict, canvas_key):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    for k, v in data_dict.items():
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=f"{k}: {safe_v}")
    
    if canvas_key in st.session_state and st.session_state[canvas_key] is not None:
        c_data = st.session_state[canvas_key]
        if hasattr(c_data, "image_data") and c_data.image_data is not None:
            from PIL import Image
            import numpy as np
            img_array = c_data.image_data.astype('uint8')
            if np.any(img_array[:, :, 3] > 0):
                img = Image.fromarray(img_array, 'RGBA')
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img_byte_arr = io.BytesIO()
                bg.save(img_byte_arr, format='JPEG')
                pdf.ln(10)
                pdf.image(img_byte_arr, x=10, w=80)
    return pdf.output(dest='S')

# --- 【2. 介面樣式】 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"

st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    .rule-text-white { font-size: 16px; color: #FFFFFF; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #555555; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) { background-color: #333333 !important; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 【3. 側邊欄導航】 ---
st.sidebar.title("📋 表單選單")
pages = ["1. 施工安全危害告知單", "2. 承攬商工具箱會議紀錄表", "3. 動火作業許可證", "4. 特殊危害作業許可證"]
for p in pages:
    if st.sidebar.button(p):
        st.session_state.current_page = p
        st.rerun()

# --- 【4. 頁面內容】 ---

# --- 頁面 1: 施工安全危害告知單 ---
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知單")
    with st.container(border=True):
        st.subheader("👤 1. 基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            comp = st.text_input("承攬商名稱", key="comp", value=st.session_state.get('comp',''))
            worker = st.text_input("施作人員姓名", key="worker", value=st.session_state.get('worker',''))
        with col2:
            st.date_input("施工日期", value=date.today())
            loc = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])

    with st.container(border=True):
        st.subheader("⚠️ 2. 危害因素告知")
        st.session_state.selected_hazards = st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"], default=st.session_state.get('selected_hazards', []))

    st.subheader("📋 3. 安全衛生規定")
    rules = ["一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。", "二、設備維修需經主管同意並掛「維修中/保養中」牌。", "三、場內限速 15 公里/小時，嚴禁超速。", "四、工作場所禁止吸菸、飲食或飲酒。", "五、操作機具需持證照且經主管同意，相關責任由借用者自負。", "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。", "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。", "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。", "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。", "十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。", "十一、清運車輛啟動前應確認周遭並發出信號。", "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。", "十三、未達指定傾貨區前，嚴禁私自開啟車斗。", "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。", "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"]
    full_html = "".join([f"<div class='rule-text-white'>{r}</div>" for r in rules])
    with st.container(height=300, border=True):
        st.markdown(full_html, unsafe_allow_html=True)
    
    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**", key="read_ok")
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_h")
    
    if st.button("確認提交告知單並存檔"):
        if not read_ok:
            st.warning("請勾選同意規定！")
        else:
            with st.spinner("PDF 生成並上傳中..."):
                data = {"Form": "Hazard Notice", "Company": comp, "Worker": worker, "Hazards": st.session_state.selected_hazards}
                pdf_bytes = create_report_pdf("Hazard Notice", data, "sign_h")
                fname = f"01_Hazard_{comp}_{date.today()}.pdf"
                if upload_to_drive(pdf_bytes, fname):
                    st.success(f"✅ 告知單存檔成功！檔名: {fname}")
                    st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
                    st.rerun()

# --- 頁面 2: 工具箱會議 ---
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.subheader("📋 會議基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**作業廠商:** {st.session_state.get('comp','')}")
            co_comp = st.text_input("共同作業廠商", key="co_comp")
            job_desc = st.text_area("工程內容", key="job_desc")
        with col2:
            st.number_input("總作業人數", min_value=1, step=1)
            st.write(f"**會議日期:** {date.today()}")

    st_canvas(stroke_width=3, background_color="#eee", height=200, key="sign_toolbox")
    
    if st.button("確認提交工具箱會議並存檔"):
        with st.spinner("上傳中..."):
            data = {"Form": "Toolbox Meeting", "Description": job_desc}
            pdf_bytes = create_report_pdf("Toolbox Meeting", data, "sign_toolbox")
            fname = f"02_Toolbox_{st.session_state.get('comp','')}_{date.today()}.pdf"
            if upload_to_drive(pdf_bytes, fname):
                st.success(f"✅ 工具箱會議存檔成功！")
                # 模糊比對分流邏輯
                haz = st.session_state.get('selected_hazards', [])
                if "火災爆炸" in haz:
                    st.session_state.current_page = "3. 動火作業許可證"
                elif any(x in haz for x in ["墜落", "感電", "缺氧窒息", "化學品接觸"]):
                    st.session_state.current_page = "4. 特殊危害作業許可證"
                else:
                    st.balloons()
                    st.session_state.current_page = "1. 施工安全危害告知單"
                st.rerun()

# --- 頁面 3: 動火作業許可證 ---
elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    # 完整 17 項檢查項目
    check_items = ["3 公尺內備有可使用/正常操作之自動灑水或手提滅火器", "防爆區或侷限空間內作業由工安單位測定可燃性氣體濃度", "動火時旁邊有警戒人員", "排除管線內可燃性物質", "隔離或中斷該區域之火警偵測器", "清除工作區域週邊 11 公尺內的可燃物或使用防火毯覆蓋保護", "工作區域易燃性地面予以防火保護", "工作區域週邊的地面及牆面不得有開口或使用防火毯覆蓋保護", "動火作業人員的安全眼鏡、面罩、手套等防護具", "施工產生之火花予以收集，工作區域內用防火布加以保護", "建築結構為不易燃性材料建造，或為不易燃性材料覆蓋保護", "須移走牆背面的易燃物質", "電焊機接頭及接地良好，並有自動電擊防止裝置", "鋼瓶直立或使用鋼瓶推車固定並有安全逆止閥", "每日收工前將火警系統中斷復歸，並檢點施工環境安全", "環境整理復歸，材料器材工具收拾整齊", "施工完畢後 30 分鐘動火場所覆查，沒有餘燼或悶燒情形"]
    for idx, item in enumerate(check_items):
        c1, c2 = st.columns([5, 1])
        c1.write(f"{idx+1}. {item}")
        c2.checkbox("OK", key=f"f_{idx}")

    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_fire")
    if st.button("完成提交動火許可"):
        with st.spinner("存檔中..."):
            pdf_bytes = create_report_pdf("Hot Work Permit", {"Result": "Checked"}, "sign_fire")
            upload_to_drive(pdf_bytes, f"03_Fire_{st.session_state.get('comp','')}.pdf")
            st.success("✅ 動火作業存檔成功！")
            # 檢查是否還需要特殊作業
            haz = st.session_state.get('selected_hazards', [])
            if any(x in haz for x in ["墜落", "感電", "缺氧窒息"]):
                st.session_state.current_page = "4. 特殊危害作業許可證"
            else:
                st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()

# --- 頁面 4: 特殊危害作業許可證 ---
elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    spec_types = ["局限空間", "吊掛", "高架", "危險管路拆卸鑽孔", "送電作業"]
    selected_spec = [t for t in spec_types if st.checkbox(t)]
    
    st_canvas(stroke_width=3, background_color="#eee", height=150, key="sign_spec")
    if st.button("完成提交特殊作業許可"):
        with st.spinner("存檔中..."):
            pdf_bytes = create_report_pdf("Special Work Permit", {"Types": selected_spec}, "sign_spec")
            upload_to_drive(pdf_bytes, f"04_Spec_{st.session_state.get('comp','')}.pdf")
            st.success("✅ 特殊作業存檔完成！全部表單已結束。")
            st.balloons()
            st.session_state.current_page = "1. 施工安全危害告知單"
            st.rerun()
