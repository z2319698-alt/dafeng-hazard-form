import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from datetime import date

# 頁面設定
st.set_page_config(page_title="大豐環保-危害告知系統", layout="centered")

# 使用 CSS 美化標題與區塊
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #2E7D32;
        color: white;
    }
    .reportview-container .main .footer{
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚧 承攬商施工安全危害告知")
st.info("請施作人員確實填寫以下資訊，並完成安全告知簽名。")

# 建立連線 (預留給後續 Excel 使用)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 表單開始 ---
with st.container():
    st.subheader("1. 基本資訊")
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("承攬商名稱", placeholder="例如：XX工程有限公司")
        worker_name = st.text_input("施作人員姓名", placeholder="請輸入全名")
    with col2:
        work_date = st.date_input("施工日期", value=date.today())
        # 💡 這裡改成你要的下拉式選單
        location_options = ["請選擇地點", "粉碎課", "造粒課", "玻璃屋", "地磅室", "廠內周邊設施"]
        work_location = st.selectbox("施工地點", options=location_options)

    st.write("---")
    st.subheader("2. 危害因素告知")
    st.write("針對本次施工環境，已告知下列可能之危害因素：")
    
    # 危害因素改用多選按鈕
    hazards = [
        "墜落", "感電", "物體飛落", "火災爆炸", 
        "交通事故", "缺氧窒息", "化學品接觸", "捲入夾碎"
    ]
    selected_hazards = st.multiselect("勾選已告知項目", hazards)

    st.write("---")
    st.subheader("3. 受告知人簽名")
    st.caption("請在下方灰色區域手寫簽名：")
    
    # 簽名板
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=200,
        drawing_mode="freedraw",
        key="canvas",
    )

    st.write("---")
    
    # 提交按鈕
    if st.button("確認提交告知單"):
        if not company or not worker_name or work_location == "請選擇地點":
            st.error("⚠️ 請完整填寫公司、姓名並選擇施工地點！")
        elif not selected_hazards:
            st.warning("⚠️ 請至少勾選一項危害因素！")
        elif canvas_result.image_data is None:
            st.error("⚠️ 請完成簽名再提交！")
        else:
            # 這裡之後會補上寫入 Excel 的邏輯
            st.success(f"✅ 提交成功！{worker_name} 辛苦了。")
            st.balloons()

st.markdown("---")
st.caption("大豐環保科技股份有限公司 - 工安管理系統")
