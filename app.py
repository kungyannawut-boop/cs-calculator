import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Coach Gung: CS Calculator", page_icon="🏃‍♂️")

# --- ฟังก์ชันสร้าง PDF (หัวใจสำคัญ) ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df):
    pdf = FPDF()
    pdf.add_page()
    
    # ⚠️ พยายามโหลดฟอนต์ไทย (ต้องมีไฟล์ THSarabunNew.ttf อยู่ในโฟลเดอร์)
    # ถ้าไม่มีไฟล์ จะใช้ Arial (ภาษาไทยจะอ่านไม่ออก ต้องใช้ Eng)
    has_thai_font = True
    try:
        pdf.add_font('Thai', '', 'THSarabunNew.ttf', uni=True)
        pdf.set_font('Thai', '', 16)
    except:
        has_thai_font = False
        pdf.set_font('Arial', '', 12)
        st.warning("⚠️ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf ในระบบ -> PDF จะแสดงผลภาษาไทยไม่ได้ (แนะนำให้อัปโหลดไฟล์ฟอนต์)")

    # --- 1. หัวกระดาษ ---
    pdf.set_font_size(20)
    if has_thai_font:
        pdf.cell(0, 10, f"รายงานผลการทดสอบ: Critical Speed Profile", ln=True, align='C')
        pdf.set_font_size(16)
        pdf.cell(0, 10, f"นักกีฬา: {student_name} | วันที่: {test_date}", ln=True, align='C')
    else:
        pdf.cell(0, 10, f"CRITICAL SPEED REPORT", ln=True, align='C')
        pdf.set_font_size(12)
        pdf.cell(0, 10, f"Athlete: {student_name} | Date: {str(test_date)}", ln=True, align='C')
    
    pdf.ln(10) # เว้นบรรทัด

    # --- 2. ข้อมูลหลัก (Metrics) ---
    pdf.set_fill_color(200, 220, 255) # สีพื้นหลังฟ้าอ่อน
    pdf.cell(0, 10, "1. Physiological Metrics (ค่าสมรรถภาพ)", ln=True, fill=True)
    pdf.ln(2)
    
    metrics_text = f"Critical Speed (CS): {cs:.2f} m/s"
    dp_text = f"Anaerobic Capacity (D'): {dp:.1f} m"
    type_text = f"Runner Type: {runner_type}"
    
    pdf.cell(0, 8, metrics_text, ln=True)
    pdf.cell(0, 8, dp_text, ln=True)
    pdf.cell(0, 8, type_text, ln=True)
    pdf.ln(5)

    # --- 3. ตารางโซนซ้อม ---
    pdf.cell(0, 10, "2. Personalized Training Zones (โซนซ้อม)", ln=True, fill=True)
    pdf.ln(2)

    # หัวตาราง
    pdf.set_font_size(14 if has_thai_font else 10)
    pdf.set_fill_color(240, 240, 240)
    col_width = [40, 30, 50, 70] # ความกว้างคอลัมน์
    headers = ["Zone", "Intensity", "Pace Range", "Objective"]
    
    for i in range(4):
        pdf.cell(col_width[i], 8, headers[i], border=1, fill=True, align='C')
    pdf.ln()

    # ข้อมูลในตาราง
    pdf.set_font_size(12 if has_thai_font else 10)
    for index, row in zones_df.iterrows():
        # แปลงข้อมูลเป็น String เพื่อความชัวร์
        pdf.cell(col_width[0], 8, str(row['Zone']), border=1)
        pdf.cell(col_width[1], 8, str(row['Intensity']), border=1, align='C')
        pdf.cell(col_width[2], 8, str(row['Pace Range (min/km)']), border=1, align='C')
        # ช่องสุดท้ายอาจยาว ตัดคำหน่อย
        obj_text = str(row['Objective'])[:35] 
        pdf.cell(col_width[3], 8, obj_text, border=1)
        pdf.ln()

    # --- 4. โค้ชแนะนำ ---
    pdf.ln(10)
    pdf.set_font_size(16 if has_thai_font else 12)
    pdf.cell(0, 10, "Coach's Insight:", ln=True)
    pdf.set_font_size(12 if has_thai_font else 10)
    advice = f"นักวิ่งประเภท {runner_type} ควรระวัง Pace ช่วงต้นของการแข่งขัน อย่าให้เกิน Threshold นานเกินไป"
    pdf.multi_cell(0, 8, advice)

    return pdf.output(dest='S').encode('latin-1')

# --- ส่วนโปรแกรมหลัก (เหมือนเดิม) ---
st.title("🏃‍♂️ Critical Speed Calculator")
st.sidebar.header("📝 ข้อมูลนักกีฬา")
student_name = st.sidebar.text_input("ชื่อนักกีฬา", "User Gung")
test_date = st.sidebar.date_input("วันที่ทดสอบ")

st.sidebar.markdown("---")
short_duration_option = st.sidebar.selectbox("Short Test Time:", ("3 นาที (180s)", "4 นาที (240s)", "5 นาที (300s)"))
short_map = {"3 นาที (180s)": 180, "4 นาที (240s)": 240, "5 นาที (300s)": 300}
t1 = short_map[short_duration_option]
d1 = st.sidebar.number_input("Distance Short (m)", 900)

long_duration_option = st.sidebar.selectbox("Long Test Time:", ("12 นาที (720s)", "15 นาที (900s)", "20 นาที (1200s)"))
long_map = {"12 นาที (720s)": 720, "15 นาที (900s)": 900, "20 นาที (1200s)": 1200}
t2 = long_map[long_duration_option]
d2 = st.sidebar.number_input("Distance Long (m)", 3150)

calculate_btn = st.sidebar.button("🚀 คำนวณผลลัพธ์")

def get_pace(speed_ms):
    if speed_ms <= 0: return "-"
    sec_per_km = 1000 / speed_ms
    return f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d}"

if calculate_btn:
    try:
        cs = (d2 - d1) / (t2 - t1)
        dp = d2 - (cs * t2)
        cs_pace = get_pace(cs)
        
        st.success(f"✅ คำนวณสำเร็จ! (CS: {cs_pace} / D': {dp:.0f}m)")
        
        runner_type = "Hybrid"
        if dp < 150: runner_type = "Diesel"
        elif dp > 250: runner_type = "Turbo"

        # สร้าง Dataframe สำหรับแสดงผลและทำ PDF
        zones_data = [
            ["Z1 Recovery", "<70%", f">{get_pace(cs*0.70)}", "Active Rest"],
            ["Z2 Easy", "70-80%", f"{get_pace(cs*0.70)}-{get_pace(cs*0.80)}", "Aerobic Base"],
            ["Z3 Steady", "80-90%", f"{get_pace(cs*0.80)}-{get_pace(cs*0.90)}", "Marathon Pace"],
            ["Z4 Threshold", "90-100%", f"{get_pace(cs*0.90)}-{get_pace(cs*1.00)}", "Tempo Run"],
            ["Z5 VO2max", "100-110%", f"{get_pace(cs*1.00)}-{get_pace(cs*1.10)}", "Interval"],
            ["Z6 Speed", ">110%", f"<{get_pace(cs*1.10)}", "Anaerobic"]
        ]
        df_zones = pd.DataFrame(zones_data, columns=["Zone", "Intensity", "Pace Range (min/km)", "Objective"])
        st.table(df_zones)

        # --- ส่วนสร้างปุ่ม Download PDF ---
        st.markdown("---")
        st.subheader("📄 Download Report")
        
        # สร้าง PDF
        pdf_bytes = create_pdf(student_name, test_date, cs, dp, runner_type, df_zones)
        
        st.download_button(
            label="📥 ดาวน์โหลดรายงานเป็น PDF",
            data=pdf_bytes,
            file_name=f"Report_{student_name}.pdf",
            mime="application/pdf"
        )

    except ZeroDivisionError:
        st.error("Error: เวลาทดสอบซ้ำกัน")
