import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Coach Kung: CS Calculator", page_icon="🏃‍♂️")

# --- 2. ฟังก์ชันสร้าง PDF (รองรับภาษาไทย fpdf2) ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df):
    # สร้าง PDF แนวตั้ง (P), หน่วย mm, ขนาด A4
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # ลงทะเบียนฟอนต์ภาษาไทย (ต้องมีไฟล์ .ttf อยู่ข้างๆ app.py)
    try:
        pdf.add_font('Thai', '', 'THSarabunNew.ttf')
        pdf.set_font('Thai', '', 16)
    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf (PDF จะแสดงผลภาษาไทยไม่ได้)")
        return None

    # ส่วนหัวรายงาน
    pdf.set_font_size(22)
    pdf.cell(0, 12, text=f"รายงานผลการทดสอบ: Critical Speed Profile", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font_size(16)
    pdf.cell(0, 10, text=f"นักกีฬา: {student_name} | วันที่: {test_date}", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ส่วนแสดงค่า Metrics
    pdf.set_fill_color(230, 240, 255) # ฟ้าอ่อน
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="1. Physiological Metrics (ค่าสมรรถภาพ)", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Thai', '', 16)
    pdf.ln(2)
    pdf.cell(0, 8, text=f"Critical Speed (CS): {cs:.2f} m/s", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Anaerobic Capacity (D'): {dp:.1f} m", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Runner Type: {runner_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ตารางโซนซ้อม
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="2. Personalized Training Zones (โซนซ้อม)", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # หัวตาราง
    pdf.set_font_size(14)
    pdf.set_fill_color(240, 240, 240)
    
    w_zone, w_int, w_pace, w_obj = 40, 25, 45, 80
    h_row = 8

    pdf.cell(w_zone, h_row, "Zone", border=1, fill=True, align='C')
    pdf.cell(w_int, h_row, "Intensity", border=1, fill=True, align='C')
    pdf.cell(w_pace, h_row, "Pace Range", border=1, fill=True, align='C')
    pdf.cell(w_obj, h_row, "Objective", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")

    # ข้อมูลในตาราง
    pdf.set_font_size(14)
    for index, row in zones_df.iterrows():
        pdf.cell(w_zone, h_row, str(row['Zone']), border=1)
        pdf.cell(w_int, h_row, str(row['Intensity']), border=1, align='C')
        pdf.cell(w_pace, h_row, str(row['Pace Range (min/km)']), border=1, align='C')
        pdf.cell(w_obj, h_row, str(row['Objective']), border=1, new_x="LMARGIN", new_y="NEXT")

    # คำแนะนำโค้ช
    pdf.ln(8)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="Coach's Insight (คำแนะนำ):", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Thai', '', 14)
    advice = f"นักวิ่งประเภท {runner_type} (D' = {dp:.0f} m) ควรระวังการคุม Pace ในช่วงต้นมาราธอน อย่าให้เกิน Threshold นานเกินไป"
    pdf.multi_cell(0, 8, text=advice)

    # ส่งข้อมูลกลับเพื่อเตรียมดาวน์โหลด
    return pdf.output()

# --- 3. ส่วนแสดงผลเว็บ (User Interface) ---
st.title("🏃‍♂️ Critical Speed Calculator")
st.caption("Designed by Coach Kung | Science-Based Training")
st.markdown("---")

# Sidebar Input
st.sidebar.header("📝 ข้อมูลนักกีฬา & การทดสอบ")
student_name = st.sidebar.text_input("ชื่อนักกีฬา", "คุณกุ้ง (ตัวอย่าง)")
test_date = st.sidebar.date_input("วันที่ทดสอบ")

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 1. ผลทดสอบระยะสั้น (Short)")
short_opt = st.sidebar.selectbox("เลือกเวลา:", ("3 นาที (180 วินาที)", "4 นาที (240 วินาที)", "5 นาที (300 วินาที)"))
short_map = {"3 นาที (180 วินาที)": 180, "4 นาที (240 วินาที)": 240, "5 นาที (300 วินาที)": 300}
t1 = short_map[short_opt]
d1 = st.sidebar.number_input("ระยะทาง (เมตร)", min_value=0, value=900, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 2. ผลทดสอบระยะยาว (Long)")
long_opt = st.sidebar.selectbox("เลือกเวลา:", ("10 นาที (600 วินาที)", "12 นาที (720 วินาที)", "15 นาที (900 วินาที)", "20 นาที (1200 วินาที)"))
long_map = {"10 นาที (600 วินาที)": 600, "12 นาที (720 วินาที)": 720, "15 นาที (900 วินาที)": 900, "20 นาที (1200 วินาที)": 1200}
t2 = long_map[long_opt]
d2 = st.sidebar.number_input("ระยะทาง (เมตร)", min_value=0, value=3150, step=10)

calculate_btn = st.sidebar.button("🚀 คำนวณผลลัพธ์")

def get_pace(speed_ms):
    if speed_ms <= 0: return "-"
    sec_per_km = 1000 / speed_ms
    return f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d}"

if calculate_btn:
    try:
        # คำนวณ CS / D'
        cs = (d2 - d1) / (t2 - t1)
        dp = d2 - (cs * t2)
        cs_pace = get_pace(cs)

        # แสดงผลหน้าเว็บ
        st.subheader(f"📊 ผลวิเคราะห์: {student_name}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Critical Speed", f"{cs:.2f} m/s", f"Pace {cs_pace}")
        col2.metric("Anaerobic Cap (D')", f"{dp:.0f} m", "ถังสำรอง")
        
        runner_type = "Hybrid"
        if dp < 150: runner_type = "Diesel (Aerobic)"
        elif dp > 250: runner_type = "Turbo (Anaerobic)"
        col3.metric("Type", runner_type)

        st.markdown("---")
        st.subheader("🎯 โซนซ้อมแนะนำ")
        
        zones_data = [
            ["Zone 1 Recovery", "< 70%", f"> {get_pace(cs*0.70)}", "คลายกรด"],
            ["Zone 2 Easy", "70-80%", f"{get_pace(cs*0.70)} - {get_pace(cs*0.80)}", "Aerobic Base"],
            ["Zone 3 Steady", "80-90%", f"{get_pace(cs*0.80)} - {get_pace(cs*0.90)}", "Marathon Pace"],
            ["Zone 4 Threshold", "90-100%", f"{get_pace(cs*0.90)} - {get_pace(cs*1.00)}", "Tempo"],
            ["⚠️ CS Line", "100%", f"📍 {cs_pace}", "Red Line"],
            ["Zone 5 VO2max", "100-110%", f"{get_pace(cs*1.00)} - {get_pace(cs*1.10)}", "Interval"],
            ["Zone 6 Anaerobic", "> 110%", f"< {get_pace(cs*1.10)}", "Speed"]
        ]
        df_zones = pd.DataFrame(zones_data, columns=["Zone", "Intensity", "Pace Range (min/km)", "Objective"])
        st.table(df_zones)
        
        # --- ส่วนสร้างปุ่ม Download PDF (ตามที่ขอครับ) ---
        st.markdown("---")
        st.subheader("📄 รายงานผล")
        
        # สร้างข้อมูล PDF
        pdf_bytes = create_pdf(student_name, test_date, cs, dp, runner_type, df_zones)
        
        if pdf_bytes:
            # ปุ่ม Download อยู่ตรงนี้ครับ
            st.download_button(
                label="📥 ดาวน์โหลดรายงาน PDF (ภาษาไทย)",
                data=bytes(pdf_bytes),
                file_name=f"Report_{student_name}.pdf",
                mime="application/pdf"
            )

    except ZeroDivisionError:
        st.error("Error: เวลาทดสอบต้องไม่เท่ากัน")
st.info("👈 กรุณากรอกข้อมูลที่แถบด้านซ้าย แล้วกดปุ่ม 'คำนวณผลลัพธ์'")
