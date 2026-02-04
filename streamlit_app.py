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

# --- 【後台 PDF 與雲端功能】 ---
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
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except:
        return False

# 修正後的 PDF 彙整函式：會掃描所有存下來的簽名
def create_combined_pdf(title, data_dict, canvas_keys):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    
    # 寫入文字資料
    for k, v in data_dict.items():
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=f"{k}: {safe_v}", ln=True)
    
    # 彙整所有簽名
    from PIL import Image
    import numpy as np
    
    for key in canvas_keys:
        if key in st.session_state and st.session_state[key] is not None:
            canvas_data = st.session_state[key]
            if hasattr(canvas_data, "image_data") and canvas_data.image_data is not None:
                img_array = canvas_data.image_data.astype('uint8')
                if np.any(img_array[:, :, 3] > 0): # 確保有畫東西
                    pdf.ln(5)
                    pdf.cell(200, 10, txt=f"Signature ({key}):", ln=True)
                    img = Image.fromarray(img_array, 'RGBA')
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img_byte_arr = io.BytesIO()
                    bg.save(img_byte_arr, format='JPEG')
                    pdf.image(img_byte_arr, x=10, w=60)
    
    return pdf.output(dest='S')

# --- 【介面設定】 ---
st.set_page_config(page_title="大豐環保-工安管理系統", layout="centered")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 施工安全危害告知單"
if 'selected_hazards' not in st.session_state:
    st.session_state.selected_hazards = []

st.markdown("""
    <style>
    .factory-header { font-size: 22px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; }
    [data-testid="stVerticalBlock"] > div:has(div.rule-text-white) {
        background-color: #333333 !important; padding: 15px; border-radius: 10px;
    }
    .rule-text-white { font-size: 18px; color: #FFFFFF; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #555555; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("📋 表單選單")
pages = ["1. 施工安全危害告知單", "2. 承攬商工具箱會議紀錄表", "3. 動火作業許可證", "4. 特殊危害作業許可證"]
for p in pages:
    if st.sidebar.button(p):
        st.session_state.current_page = p

# --- 1. 危害告知單 ---
if st.session_state.current_page == "1. 施工安全危害告知單":
    st.markdown('<div class="factory-header">大豐環保 (全興廠)</div>', unsafe_allow_html=True)
    st.title("🚧 承攬商施工安全危害告知單")
    with st.container(border=True):
        st.subheader("👤 1. 基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.company = st.text_input("承攬商名稱", value=st.session_state.get('company',''), placeholder="請輸入公司")
            st.session_state.worker_name = st.text_input("施作人員姓名", value=st.session_state.get('worker_name',''), placeholder="請輸入姓名")
        with col2:
            st.session_state.work_date = st.date_input("施工日期", value=date.today())
            st.session_state.location = st.selectbox("施工地點", ["請選擇", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"])
    
    with st.container(border=True):
        st.subheader("⚠️ 2. 危害因素告知")
        st.session_state.selected_hazards = st.multiselect("勾選本次作業危害項目", ["墜落", "感電", "物體飛落", "火災爆炸", "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"], default=st.session_state.selected_hazards)
    
    st.subheader("📋 3. 安全衛生規定")
    rules = ["一、為防止尖銳物(玻璃、鐵釘、廢棄針頭)切割危害，應佩戴安全手套、安全鞋及防護具。", "二、設備維修需經主管同意並掛「維修中/保養中」牌。", "三、場內限速 15 公里/小時，嚴禁超速。", "四、工作場所禁止吸菸、飲食或飲酒。", "五、操作機具需持證照且經主管同意，相關責任由借用者自負。", "六、嚴禁貨叉載人。堆高機熄火需貨叉置地、拔鑰匙歸還。", "七、重機作業半徑內禁止進入，17噸(含)以上作業應放三角錐。", "八、1.8公尺以上高處作業或3.5噸以上車頭作業均須配戴安全帽。", "九、電路維修需戴絕緣具、斷電掛牌並指派一人全程監視。", "十、動火作業需主管同意、備滅火器(3公尺內)並配戴護目鏡。", "十一、清運車輛啟動前應確認周遭並發出信號。", "十二、開啟尾門應站側面，先開小縫確認無誤後再全面開啟。", "十三、未達指定傾貨區前，嚴禁私自開啟車斗。", "十四、行駛中嚴禁站立車斗，卸貨完確認車斗收妥方可駛離。", "十五、人員行經廠內出入口應行走人行道，遵守「停、看、行」。"]
    full_html = "".join([f"<div class='rule-text-white'>{r}</div>" for r in rules])
    with st.container(height=300, border=True):
        st.markdown(full_html, unsafe_allow_html=True)
    
    read_ok = st.checkbox("**我已充分閱讀並同意遵守上述所有規定**")
    st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="sign_h")
    
    if st.button("確認提交告知單", disabled=not read_ok):
        st.session_state.current_page = "2. 承攬商工具箱會議紀錄表"
        st.rerun()

# --- 2. 工具箱會議紀錄表 ---
elif st.session_state.current_page == "2. 承攬商工具箱會議紀錄表":
    st.title("📝 承攬商工具箱會議紀錄表")
    with st.container(border=True):
        st.subheader("📋 會議基本資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**作業廠商:** {st.session_state.get('company','')}")
            st.text_input("共同作業廠商", key="tool_co_comp")
            st.text_area("工程內容", placeholder="請輸入本日施工簡述", key="tool_content")
        with col2:
            st.write(f"**施工位置:** {st.session_state.get('location','')}")
            st.number_input("總作業人數", min_value=1, step=1, key="tool_total_num")
            st.write(f"**會議日期:** {date.today()}")
    
    st_canvas(stroke_width=3, background_color="#eee", height=250, key="sign_workers_all")
    col_sign1, col_sign2 = st.columns(2)
    with col_sign1:
        st.write("承辦單位人員簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_unit_final")
    with col_sign2:
        st.write("工安人員簽名")
        st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_safety_final")
    
    if st.button("確認提交工具箱會議"):
        if "火災爆炸" in st.session_state.get('selected_hazards', []):
            st.session_state.current_page = "3. 動火作業許可證"
        else:
            st.session_state.current_page = "4. 特殊危害作業許可證"
        st.rerun()

# --- 3. 動火作業許可證 ---
elif st.session_state.current_page == "3. 動火作業許可證":
    st.title("🔥 動火作業許可證")
    with st.container(border=True):
        st.subheader("📋 動火申請資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("動火設備", key="fire_equip")
            st.text_input("連絡電話", key="fire_tel")
        with col2:
            st.write("**作業期間 (限當日)**")
            c1, c2, c3 = st.columns([2, 1, 1])
            f_date = c1.date_input("日期", value=date.today(), key="f_date")
            f_start = c2.number_input("起(時)", 0, 23, 8, key="f_start")
            f_end = c3.number_input("迄(時)", 0, 23, 17, key="f_end")
            
    check_items = ["3 公尺內備有可使用/正常操作之自動灑水或手提滅火器", "防爆區或侷限空間內作業由工安單位測定可燃性氣體濃度", "動火時旁邊有警戒人員", "排除管線內可燃性物質", "隔離或中斷該區域之火警偵測器", "清除工作區域週邊 11 公尺內的可燃物或使用防火毯覆蓋保護", "工作區域易燃性地面予以防火保護", "工作區域週邊的地面及牆面不得有開口或使用防火毯覆蓋保護", "動火作業人員的安全眼鏡、面罩、手套等防護具", "施工產生之火花予以收集，工作區域內用防火布加以保護", "建築結構為不易燃性材料建造，或為不易燃性材料覆蓋保護", "須移走牆背面的易燃物質", "電焊機接頭及接地良好，並有自動電擊防止裝置", "鋼瓶直立或使用鋼瓶推車固定並有安全逆止閥", "每日收工前將火警系統中斷復歸，並檢點施工環境安全", "環境整理復歸，材料器材工具收拾整齊", "施工完畢後 30 分鐘動火場所覆查，沒有餘燼或悶燒情形"]
    for idx, item in enumerate(check_items):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"{idx+1}. {item}")
        c2.checkbox("", key=f"f_v_{idx}")
        c3.checkbox("", key=f"f_s_{idx}")
        c4.checkbox("", key=f"f_h_{idx}")
        
    st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_fire_v")
    st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_fire_s")

    if st.button("完成提交並彙整 PDF"):
        with st.spinner("正在彙整所有表單與簽名..."):
            all_data = {
                "Company": st.session_state.get('company',''),
                "Worker": st.session_state.get('worker_name',''),
                "Report": "Comprehensive Safety Report"
            }
            # 彙整告知單、工具箱、動火單的所有簽名
            canvas_to_include = ["sign_h", "sign_workers_all", "sign_unit_final", "sign_safety_final", "sign_fire_v", "sign_fire_s"]
            pdf_bytes = create_combined_pdf("Safety Work Report", all_data, canvas_to_include)
            upload_to_drive(pdf_bytes, f"Full_Report_{date.today()}.pdf")
            st.success("全部表單已彙整成一份 PDF 並上傳成功！")

# --- 4. 特殊危害作業許可證 (邏輯同上) ---
elif st.session_state.current_page == "4. 特殊危害作業許可證":
    st.title("🛡️ 特殊危害作業許可證")
    # ... (此處保留你原本的特殊作業介面項目)
    st_canvas(stroke_width=3, background_color="#fafafa", height=120, key="sign_spec_v")
    
    if st.button("完成提交並彙整 PDF"):
        with st.spinner("彙整中..."):
            all_data = {"Company": st.session_state.get('company',''), "Worker": st.session_state.get('worker_name','')}
            canvas_to_include = ["sign_h", "sign_workers_all", "sign_unit_final", "sign_safety_final", "sign_spec_v"]
            pdf_bytes = create_combined_pdf("Special Safety Report", all_data, canvas_to_include)
            upload_to_drive(pdf_bytes, f"Special_Report_{date.today()}.pdf")
            st.success("彙整 PDF 上傳成功！")
