def create_pdf_report(title, data_dict, canvas_key):
    # 使用 fpdf 基礎設定
    pdf = FPDF()
    pdf.add_page()
    
    # 使用 Helvetica (內建字型，保證不當機)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    # 填寫資料內容 (將標籤改為英文，內容過濾中文避免 Exception)
    pdf.set_font("Helvetica", size=12)
    # 建立一個中英文對照，讓 PDF 裡面的標籤是英文的
    label_map = {
        "Company": "Company",
        "Worker": "Worker Name",
        "Location": "Work Location",
        "Date": "Date"
    }
    
    for k, v in data_dict.items():
        # 強行把中文內容過濾成問號或空格，防止 FPDF 報錯
        safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
        label = label_map.get(k, k)
        pdf.cell(200, 10, txt=f"{label}: {safe_v}", ln=True)
    
    # --- 【重點：手寫簽名原樣呈現】 ---
    if canvas_key in st.session_state:
        canvas_data = st.session_state[canvas_key]
        if canvas_data is not None and canvas_data.image_data is not None:
            # 1. 將畫布數據轉為圖片
            from PIL import Image
            import numpy as np
            # 2. 處理透明背景
            img = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')
            # 3. 疊加在白色背景上 (PDF 不支援透明 PNG)
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            
            # 4. 轉存為位元組流
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='JPEG')
            
            # 5. 把你的手寫簽名「原樣」塞進 PDF
            pdf.ln(10)
            pdf.cell(200, 10, txt="Signature:", ln=True)
            pdf.image(img_byte_arr, x=10, w=80) # 控制簽名寬度為 80mm
            
    return pdf.output(dest='S')
