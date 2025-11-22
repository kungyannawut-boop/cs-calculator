import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Coach Kung: CS Calculator", page_icon="🏃‍♂️")

# --- 2. ฟังก์ชันสร้าง PDF (เพิ่ม Footer) ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df, advice_text):
    
    # สร้าง Custom Class เพื่อทำ Footer (สิ่งที่เพิ่มมาใหม่)
    class PDF(FPDF):
        def footer(self):
            # เลื่อนตำแหน่งไปที่ 1.5 cm จากขอบล่าง
            self.set_y(-15)
            # ใช้ฟอนต์ Arial ตัวเอียง ขนาด 8 (ดู Inter หน่อย)
            self.set_font("Arial", "I", 8)
            # พิมพ์ข้อความชิดขวา (align='R')
            self.cell(0, 10, "Designed by Coach Kung", align="R")

    # เรียกใช้ Class ใหม่ที่เราเพิ่งสร้าง
    pdf = PDF(orientation="P", unit="mm", format="A4")
    
    # ลงทะเบียนฟอนต์ภาษาไทย
    try:
        pdf.add_font('Thai', '', 'THSarabunNew.ttf')
    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf")
        return None

    pdf.add_page()

    # --- ส่วนเนื้อหา (เหมือนเดิม) ---
    
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
    
    # Table Header
    pdf.set_font_size(14)
    pdf.set_fill_color(240, 240, 240)
    w_cols = [35, 25, 45, 85]
    headers = ["Zone", "Intensity", "Pace Range", "Objective"]
    
    for i, h in enumerate(headers):
        pdf.cell(w_cols[i], 8, h, border=1, fill=True, align='C')
    pdf.ln()

    # Table Rows
    pdf.set_font_size(14)
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

# --- 3. ฟังก์ชันคำแนะนำโค้ช ---
def get_coach_advice(runner_type, cs_pace, dp):
    if "Diesel" in runner_type:
        return (
            f"📌 วิเคราะห์: เป็นนักวิ่งสายอึด (Diesel) มี Aerobic Base แข็งแกร่ง แต่ถัง D' น้อย ({dp:.0f}m) เร่งความเร็วได้ไม่ดีนัก\n"
            f"🏋️ แผนซ้อม: เสริมคอร์ทสั้น (Speed) เพื่อขยายถัง D' และซ้อม Hill Repeats\n"
            f"🏁 วันแข่ง: วิ่ง Even Pace ห้ามกระชาก รักษาความเร็ว Threshold ไว้แล้วบดช่วงท้าย"
        )
    elif "Turbo" in runner_type:
        return (
            f"📌 วิเคราะห์: เป็นนักวิ่งสายสปีด (Turbo) ถัง D' ใหญ่ ({dp:.0f}m) มีลูกฮึดดี แต่ฐาน Aerobic อาจยังไม่กว้างพอ\n"
            f"🏋️ แผนซ้อม: เน้น Tempo/Threshold แช่ยาวๆ เพื่อดันเพดาน CS ลดการซ้อม Speed ลง\n"
            f"🏁 วันแข่ง: ใจเย็นช่วงต้น! เก็บ D' ไว้ระเบิดพลัง 800m สุดท้าย อย่าเพลินจนถังหมด"
        )
    else:
        return (
            f"📌 วิเคราะห์: เป็นนักวิ่งสมดุล (Hybrid) D' มาตรฐาน ({dp:.0f}m) ปรับเปลี่ยนแผนได้หลากหลาย\n"
            f"🏋️ แผนซ้อม: Periodization ช่วงต้นเน้น Base ช่วงกลางเน้น Threshold ช่วงท้ายเติม Speed\n"
            f"🏁 วันแข่ง: เกาะกลุ่ม (Drafting) ได้ดี หาจังหวะฉีกหนีเมื่อคู่แข่งล้า"
        )

# --- 4. ส่วนแสดงผลเว็บ ---
st.title("🏃‍♂️ Critical Speed Calculator")
st.caption("Designed by Coach Kung | Science-Based Training")
st.markdown("---")

# Sidebar
st.sidebar.header("📝 ข้อมูลนักกีฬา")
student_name = st.sidebar.text_input("ชื่อนักกีฬา", "คุณกุ้ง (ตัวอย่าง)")
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
            ["Zone 1 Recovery", "< 70%", f"> {get_pace(cs*0.70)}", "คลายกรด / Active Rest"],
            ["Zone 2 Easy", "70-80%", f"{get_pace(cs*0.70)} - {get_pace(cs*0.80)}", "สร้างฐาน Aerobic"],
            ["Zone 3 Steady", "80-90%", f"{get_pace(cs*0.80)} - {get_pace(cs*0.90)}", "Marathon Pace"],
            ["Zone 4 Threshold", "90-100%", f"{get_pace(cs*0.90)} - {get_pace(cs*1.00)}", "Tempo / ดันเพดาน"],
            ["⚠️ CS Line", "100%", f"📍 {cs_pace}", "Red Line (ขีดจำกัดร่างกาย)"],
            ["Zone 5 VO2max", "100-110%", f"{get_pace(cs*1.00)} - {get_pace(cs*1.10)}", "Interval / กระตุ้นหัวใจ"],
            ["Zone 6 Anaerobic", "> 110%", f"< {get_pace(cs*1.10)}", "Speed / พัฒนาความเร็วสูงสุด"]
        ]
        df_zones = pd.DataFrame(zones_data, columns=["Zone", "Intensity", "Pace Range (min/km)", "Objective"])
        st.table(df_zones)
        
        # PDF
        st.markdown("---")
        st.subheader("📄 รายงานผล (PDF)")
        pdf_bytes = create_pdf(student_name, test_date, cs, dp, runner_type, df_zones, advice_text)
        
        if pdf_bytes:
            st.download_button(
                label="📥 ดาวน์โหลดรายงาน PDF (ภาษาไทย)",
                data=bytes(pdf_bytes),
                file_name=f"Report_{student_name}.pdf",
                mime="application/pdf"
            )

    except ZeroDivisionError:
        st.error("Error: เวลาทดสอบต้องไม่เท่ากัน")
