import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib import font_manager
import io
import textwrap

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Coach Kung: CS Calculator", page_icon="🏃‍♂️")

# --- ฟังก์ชันเสริม: วาดรูป JPG (แก้ไขให้เป็น A4 เป๊ะ) ---
def create_image_card(student_name, test_date, cs, dp, runner_type, zones_df, advice_text):
    # 1. ตั้งค่ากระดาษ A4 (8.27 x 11.69 นิ้ว)
    fig, ax = plt.subplots(figsize=(8.27, 11.69)) # A4 Size
    
    # ล็อกพื้นที่ให้เต็มแผ่น ไม่ให้มีขอบขาวเกินจำเป็น
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.axis('off') # ปิดแกน

    # 2. โหลดฟอนต์ไทย
    try:
        # ปรับขนาดฟอนต์ให้เหมาะกับ A4
        title_font = font_manager.FontProperties(fname='THSarabunNew.ttf', size=28, weight='bold')
        header_font = font_manager.FontProperties(fname='THSarabunNew.ttf', size=22, weight='bold')
        normal_font = font_manager.FontProperties(fname='THSarabunNew.ttf', size=18)
        small_font = font_manager.FontProperties(fname='THSarabunNew.ttf', size=14)
    except:
        st.warning("⚠️ ไม่พบฟอนต์ THSarabunNew.ttf")
        return None

    # 3. วาดส่วนหัว (Header) - ขยับตำแหน่งให้สวยงามบน A4
    plt.text(0.5, 0.92, "รายงานผลการทดสอบ: Critical Speed Profile", ha='center', fontproperties=title_font, color='#2c3e50')
    plt.text(0.5, 0.88, f"นักกีฬา: {student_name} | วันที่: {str(test_date)}", ha='center', fontproperties=header_font, color='#7f8c8d')
    plt.plot([0.1, 0.9], [0.86, 0.86], color='#bdc3c7', lw=2)

    # 4. วาดค่า Metrics
    plt.text(0.1, 0.82, "1. Physiological Metrics (ค่าสมรรถภาพ)", fontproperties=header_font, color='#2980b9')
    metrics_text = (
        f"• Critical Speed (CS): {cs:.2f} m/s\n"
        f"• Anaerobic Capacity (D'): {dp:.0f} m\n"
        f"• Runner Type: {runner_type}"
    )
    plt.text(0.12, 0.73, metrics_text, fontproperties=normal_font, va='top', linespacing=1.6)

    # 5. วาดตารางโซนซ้อม
    plt.text(0.1, 0.63, "2. Training Zones (โซนซ้อม)", fontproperties=header_font, color='#2980b9')
    
    cell_text = []
    for i, row in zones_df.iterrows():
        cell_text.append([row['Zone'], row['Intensity'], row['Pace Range (min/km)'], row['Objective']])
    
    col_labels = ["Zone", "Intensity", "Pace", "Objective"]
    
    # สร้างตาราง (ปรับตำแหน่งให้พอดี A4)
    table = plt.table(cellText=cell_text, colLabels=col_labels, 
                      loc='center', cellLoc='left', colLoc='center',
                      bbox=[0.1, 0.32, 0.8, 0.28]) # [left, bottom, width, height]
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    
    # ปรับฟอนต์ตาราง
    for key, cell in table.get_celld().items():
        cell.set_text_props(fontproperties=small_font)
        cell.set_edgecolor('#bdc3c7')
        if key[0] == 0:
            cell.set_text_props(fontproperties=header_font, color='white')
            cell.set_facecolor('#2980b9')
            cell.set_height(0.04)

    # 6. วาดคำแนะนำโค้ช
    plt.text(0.1, 0.25, "3. Coach's Advice (คำแนะนำ)", fontproperties=header_font, color='#2980b9')
    
    wrapper = textwrap.TextWrapper(width=65) # บีบข้อความให้แคบลงนิดนึงสำหรับ A4 แนวตั้ง
    wrapped_advice = wrapper.fill(text=advice_text)
    plt.text(0.12, 0.21, wrapped_advice, fontproperties=normal_font, va='top', linespacing=1.4)

    # 7. Footer
    plt.text(0.9, 0.03, "Designed by Coach Kung", ha='right', fontproperties=small_font, color='#95a5a6', style='italic')

    # 8. Save ลง Buffer (สำคัญ: ลบ bbox_inches='tight' ออก เพื่อรักษาขนาด A4)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='jpg', dpi=150) # ลบ bbox_inches ออกแล้ว
    img_buffer.seek(0)
    return img_buffer


# --- 2. ฟังก์ชันสร้าง PDF (เพิ่ม Footer) ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df, advice_text):
    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, "Designed by Coach Kung", align="R")

    pdf = PDF(orientation="P", unit="mm", format="A4")
    
    try:
        pdf.add_font('Thai', '', 'THSarabunNew.ttf')
    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf")
        return None

    pdf.add_page()

    # Header
    pdf.set_font('Thai', '', 22)
    pdf.cell(0, 12, text=f"รายงานผลการทดสอบ: Critical Speed Profile", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Thai', '', 16)
    pdf.cell(0, 10, text=f"นักกีฬา: {student_name} | วันที่: {test_date}", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Metrics
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="1. Physiological Metrics (ค่าสมรรถภาพ)", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Thai', '', 16)
    pdf.ln(2)
    pdf.cell(0, 8, text=f"Critical Speed (CS): {cs:.2f} m/s", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Anaerobic Capacity (D'): {dp:.1f} m", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Runner Type: {runner_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Zones Table
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="2. Personalized Training Zones (โซนซ้อม)", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font_size(14)
    pdf.set_fill_color(240, 240, 240)
    w_cols = [35, 25, 45, 85]
    headers = ["Zone", "Intensity", "Pace Range", "Objective"]
    
    for i, h in enumerate(headers):
        pdf.cell(w_cols[i], 8, h, border=1, fill=True, align='C')
    pdf.ln()

    for index, row in zones_df.iterrows():
        pdf.cell(w_cols[0], 8, str(row['Zone']), border=1)
        pdf.cell(w_cols[1], 8, str(row['Intensity']), border=1, align='C')
        pdf.cell(w_cols[2], 8, str(row['Pace Range (min/km)']), border=1, align='C')
        pdf.cell(w_cols[3], 8, str(row['Objective']), border=1, new_x="LMARGIN", new_y="NEXT")

    # Coach Advice
    pdf.ln(8)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="Coach's Recommendation (คำแนะนำการฝึกซ้อม):", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Thai', '', 14)
    pdf.multi_cell(0, 7, text=advice_text)

    return pdf.output()

# --- 3. ฟังก์ชัน Logic คำแนะนำ ---
def get_coach_advice(runner_type, cs_pace, dp):
    if "Diesel" in runner_type:
        return (
            f"📌 วิเคราะห์: คุณเป็นนักวิ่งสายอึด (Diesel) มีเครื่องยนต์ Aerobic ที่แข็งแกร่ง ยืนระยะได้ดีมาก "
            f"แต่มีถังพลังงานสำรอง (D') น้อย ({dp:.0f}m) ทำให้เร่งความเร็วฉับพลัน (Surge) หรือสปรินต์หน้าเส้นได้ไม่ดีนัก\n\n"
            f"🏋️ แผนการซ้อม: จุดอ่อนคือ Speed & Power ควรเสริมคอร์ทระยะสั้นที่เร็วและแรง "
            f"(เช่น 200m-400m @Zone 6) พักยาวๆ เพื่อขยายขนาดถัง D' ให้ใหญ่ขึ้น และซ้อม Hill Repeats เพื่อสร้างกำลังขา\n\n"
            f"🏁 กลยุทธ์วันแข่ง: ห้ามกระชาก! คุณต้องวิ่งแบบ Even Pace (ความเร็วคงที่) เหมือนเครื่องจักร "
            f"อย่าหลงไปแข่งสปรินต์กับใครช่วงต้นเกม รักษาความเร็วระดับ Threshold ไว้ แล้วใช้ความอึดบดคู่แข่งช่วงท้าย"
        )
    elif "Turbo" in runner_type:
        return (
            f"📌 วิเคราะห์: คุณเป็นนักวิ่งสายสปีด (Turbo) มีถังพลังงานสำรอง (D') ใหญ่มาก ({dp:.0f}m) "
            f"มีความเร็วต้นจัดจ้านและลูกฮึดหน้าเส้นที่น่ากลัว แต่ฐาน Aerobic (CS) อาจยังไม่กว้างพอ ทำให้หมดแรงไวถ้ายืดระยะ\n\n"
            f"🏋️ แผนการซ้อม: ต้องอุดรอยรั่วเรื่องความอึด เน้นซ้อม Tempo และ Threshold (Zone 3-4) "
            f"แช่ยาวๆ 20-40 นาที เพื่อดันเพดาน CS ให้สูงขึ้น และลดปริมาณการซ้อม Speed ลง เพราะคุณมีของดีอยู่แล้ว\n\n"
            f"🏁 กลยุทธ์วันแข่ง: ใจเย็นๆ ช่วงต้นเกม! คุณจะรู้สึกว่าวิ่งเร็วแล้วไม่เหนื่อย (เพราะใช้ถัง D' วิ่ง) "
            f"แต่ถ้าเพลินจนถังหมด คุณจะชนกำแพงทันที ให้คุม Pace ช่วงแรกให้ช้ากว่าที่รู้สึกสบายเล็กน้อย แล้วเก็บ D' ไว้ระเบิดพลังแซงช่วง 800 เมตรสุดท้าย"
        )
    else:
        return (
            f"📌 วิเคราะห์: คุณเป็นนักวิ่งสมดุล (Hybrid) มีความยืดหยุ่นสูง ปรับตัวได้ดีทั้งเกมเร็วและเกมอึด "
            f"ค่า D' ของคุณ ({dp:.0f}m) อยู่ในเกณฑ์มาตรฐาน ทำให้สามารถวางแผนการซ้อมได้หลากหลายที่สุด\n\n"
            f"🏋️ แผนการซ้อม: ใช้ระบบ Periodization ช่วงต้นฤดูกาลเน้นสร้างฐาน (Zone 2-3) "
            f"ช่วงกลางเน้น Threshold (Zone 4) และช่วงท้ายก่อนแข่งค่อยเติม Speed (Zone 5-6) ตามระยะที่จะลงแข่ง\n\n"
            f"🏁 กลยุทธ์วันแข่ง: คุณเลือกเล่นได้ตามสถานการณ์ สามารถเกาะกลุ่มนำไปเรื่อยๆ (Drafting) "
            f"แล้วหาจังหวะฉีกหนีเมื่อคู่แข่งเริ่มล้า หรือจะวิ่งคุมโซนตัวเองเพื่อทำ New PB ก็ทำได้ดีทั้งคู่"
        )

# --- 4. ส่วนแสดงผลเว็บ ---
st.title("🏃‍♂️ Critical Speed Calculator")
st.caption("Designed by Coach Kung | Science-Based Training")
st.markdown("---")

# Sidebar
st.sidebar.header("📝 ข้อมูลนักกีฬา")
student_name = st.sidebar.text_input("ชื่อนักกีฬา", "(ตัวอย่าง)")
test_date = st.sidebar.date_input("วันที่ทดสอบ")

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 1. Short Test")
short_opt = st.sidebar.selectbox("เวลา (Short):", ("3 นาที (180 วินาที)", "4 นาที (240 วินาที)", "5 นาที (300 วินาที)"))
t1 = {"3 นาที (180 วินาที)": 180, "4 นาที (240 วินาที)": 240, "5 นาที (300 วินาที)": 300}[short_opt]
d1 = st.sidebar.number_input("ระยะทาง Short (m)", min_value=0, value=900, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 2. Long Test")
long_opt = st.sidebar.selectbox("เวลา (Long):", ("10 นาที (600 วินาที)", "12 นาที (720 วินาที)", "15 นาที (900 วินาที)", "20 นาที (1200 วินาที)"))
t2 = {"10 นาที (600 วินาที)": 600, "12 นาที (720 วินาที)": 720, "15 นาที (900 วินาที)": 900, "20 นาที (1200 วินาที)": 1200}[long_opt]
d2 = st.sidebar.number_input("ระยะทาง Long (m)", min_value=0, value=3150, step=10)

calculate_btn = st.sidebar.button("🚀 คำนวณผลลัพธ์")

def get_pace(speed_ms):
    if speed_ms <= 0: return "-"
    sec_per_km = 1000 / speed_ms
    return f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d}"

if calculate_btn:
    try:
        # Calc
        cs = (d2 - d1) / (t2 - t1)
        dp = d2 - (cs * t2)
        cs_pace = get_pace(cs)

        # Type
        runner_type = "Hybrid (สมดุล)"
        if dp < 150: runner_type = "Diesel (Aerobic Engine)"
        elif dp > 250: runner_type = "Turbo (Anaerobic Power)"
        
        # Advice
        advice_text = get_coach_advice(runner_type, cs_pace, dp)

        # Display
        st.subheader(f"📊 ผลวิเคราะห์: {student_name}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Critical Speed", f"{cs:.2f} m/s", f"Pace {cs_pace}")
        col2.metric("Anaerobic Cap (D')", f"{dp:.0f} m", "ถังสำรอง")
        col3.metric("Type", runner_type.split()[0])

        st.info(advice_text)

        # Zones
        st.subheader("🎯 โซนซ้อมแนะนำ")
        zones_data = [
            ["Zone 1 Recovery", "< 70%", f"> {get_pace(cs*0.70)}", "Active Rest"],
            ["Zone 2 Easy", "70-80%", f"{get_pace(cs*0.70)} - {get_pace(cs*0.80)}", "Aerobic Base"],
            ["Zone 3 Steady", "80-90%", f"{get_pace(cs*0.80)} - {get_pace(cs*0.90)}", "Marathon Pace"],
            ["Zone 4 Threshold", "90-100%", f"{get_pace(cs*0.90)} - {get_pace(cs*1.00)}", "Tempo Run"],
            ["⚠️ CS Line", "100%", f"📍 {cs_pace}", "Red Line"],
            ["Zone 5 VO2max", "100-110%", f"{get_pace(cs*1.00)} - {get_pace(cs*1.10)}", "Interval"],
            ["Zone 6 Anaerobic", "> 110%", f"< {get_pace(cs*1.10)}", "Speed Work"]
        ]
        df_zones = pd.DataFrame(zones_data, columns=["Zone", "Intensity", "Pace Range (min/km)", "Objective"])
        st.table(df_zones)
        
        st.markdown("---")
        st.subheader("💾 บันทึกผลลัพธ์")
        
        col_pdf, col_jpg = st.columns(2)

        # 1. PDF Button
        pdf_bytes = create_pdf(student_name, test_date, cs, dp, runner_type, df_zones, advice_text)
        if pdf_bytes:
            col_pdf.download_button(
                label="📄 ดาวน์โหลดรายงาน PDF",
                data=bytes(pdf_bytes),
                file_name=f"Report_{student_name}.pdf",
                mime="application/pdf"
            )
            
        # 2. JPG Button (Fixed A4 Size)
        jpg_bytes = create_image_card(student_name, test_date, cs, dp, runner_type, df_zones, advice_text)
        if jpg_bytes:
            col_jpg.download_button(
                label="🖼️ ดาวน์โหลดรูปภาพ JPG",
                data=jpg_bytes,
                file_name=f"Card_{student_name}.jpg",
                mime="image/jpeg"
            )

    except ZeroDivisionError:
        st.error("Error: เวลาทดสอบต้องไม่เท่ากัน")
else:
    st.info("👈 กรุณากรอกข้อมูลที่แถบด้านซ้าย แล้วกดปุ่ม 'คำนวณผลลัพธ์'")
