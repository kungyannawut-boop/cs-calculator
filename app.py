import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import matplotlib
matplotlib.use("Agg") # Backend สำหรับ Server
import matplotlib.pyplot as plt
from matplotlib import font_manager
import io
import os
import tempfile # ใช้สร้างไฟล์ชั่วคราวสำหรับรูปกราฟใน PDF

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Coach Kung: CS Calculator", page_icon="🏃‍♂️")

# --- ฟังก์ชันวาดกราฟ (ใช้ร่วมกันทั้ง Web และ PDF) ---
def plot_cs_regression(times, dists, cs, dp):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # 1. Plot จุดทดสอบจริง
    ax.scatter(times, dists, color='red', s=100, zorder=5, label='Test Data')
    
    # 2. Plot เส้น Linear Regression
    # สร้างจุด x สำหรับวาดเส้น (จาก 0 ถึง เวลามากสุด+นิดหน่อย)
    x_line = np.linspace(0, max(times)*1.15, 100)
    y_line = cs * x_line + dp
    
    ax.plot(x_line, y_line, color='blue', linestyle='--', linewidth=2, label=f'CS Slope ({cs:.2f} m/s)')
    
    # 3. ตกแต่งกราฟ
    ax.set_title("Critical Speed Regression Model (Distance vs Time)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Distance (meters)")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # แสดงสมการบนกราฟ
    ax.text(0.05, 0.95, f"Dist = ({cs:.2f} × Time) + {dp:.0f}", transform=ax.transAxes, 
            fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    return fig

# --- 2. ฟังก์ชันสร้าง PDF (เพิ่มกราฟ) ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df, advice_text, times, dists):
    
    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, "Designed by Coach Kung", align="R")

    pdf = PDF(orientation="P", unit="mm", format="A4")
    
    # Auto Path หาฟอนต์
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, 'THSarabunNew.ttf')

    try:
        pdf.add_font('Thai', '', font_path)
    except:
        st.error(f"❌ ไม่พบฟอนต์ที่: {font_path}")
        return None

    pdf.add_page()

    # Header
    pdf.set_font('Thai', '', 22)
    pdf.cell(0, 12, text=f"รายงานผลการทดสอบ: Critical Speed Profile (3-Point)", align='C', new_x="LMARGIN", new_y="NEXT")
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
    pdf.ln(2)

    # --- ✅ ส่วนเพิ่มกราฟลง PDF ---
    try:
        # สร้างกราฟจากฟังก์ชัน
        fig = plot_cs_regression(times, dists, cs, dp)
        
        # บันทึกกราฟลงไฟล์ชั่วคราว (Temp File)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, format='png', dpi=150)
            tmpfile_path = tmpfile.name
        
        # แทรกรูปจากไฟล์ชั่วคราวลง PDF
        # x=Center, w=120mm (กว้างประมาณครึ่งหน้า A4)
        pdf.image(tmpfile_path, x=45, w=120) 
        pdf.ln(5) # เว้นบรรทัดหลังรูป
        
        # ลบไฟล์ชั่วคราวทิ้งเพื่อคืนพื้นที่
        os.unlink(tmpfile_path)
        plt.close(fig)
        
    except Exception as e:
        st.warning(f"ไม่สามารถสร้างกราฟใน PDF ได้: {e}")
    # ---------------------------

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

    # Advice
    pdf.ln(8)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="Coach's Recommendation:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Thai', '', 14)
    pdf.multi_cell(0, 7, text=advice_text)

    return pdf.output()

# --- 3. คำแนะนำโค้ช ---
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

# --- 4. Main App ---
st.title("🏃‍♂️ CS Calculator (3-Point Protocol)")
st.caption("Designed by Coach Kung | Science-Based Training")
st.markdown("---")

# Sidebar
st.sidebar.header("📝 ข้อมูลนักกีฬา")
student_name = st.sidebar.text_input("ชื่อนักกีฬา", "(ตัวอย่าง)")
test_date = st.sidebar.date_input("วันที่ทดสอบ")

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ 1. Sprint Test (30s)")
t1 = 30 
st.sidebar.caption("เวลา: 30 วินาที (Anaerobic)")
d1 = st.sidebar.number_input("ระยะทาง 30s (m)", min_value=0, value=180, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 2. Middle Test (3min)")
mid_opt = st.sidebar.selectbox("เวลา (Mid):", ("3 นาที (180s)", "4 นาที (240s)"), index=0)
t2 = 180 if "3 นาที" in mid_opt else 240
d2 = st.sidebar.number_input(f"ระยะทาง {mid_opt} (m)", min_value=0, value=850, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader("🐢 3. Endurance Test (12min)")
long_opt = st.sidebar.selectbox("เวลา (Long):", ("12 นาที (720s)", "15 นาที (900s)", "20 นาที (1200s)"), index=0)
t3_map = {"12 นาที (720s)": 720, "15 นาที (900s)": 900, "20 นาที (1200s)": 1200}
t3 = t3_map[long_opt]
d3 = st.sidebar.number_input(f"ระยะทาง {long_opt} (m)", min_value=0, value=3100, step=10)

calculate_btn = st.sidebar.button("🚀 คำนวณผลลัพธ์ (3-Point)")

def get_pace(speed_ms):
    if speed_ms <= 0: return "-"
    sec_per_km = 1000 / speed_ms
    return f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d}"

if calculate_btn:
    try:
        # คำนวณ
        times = np.array([t1, t2, t3])      
        distances = np.array([d1, d2, d3])  
        
        slope, intercept = np.polyfit(times, distances, 1)
        cs = slope
        dp = intercept
        cs_pace = get_pace(cs)

        # Type
        runner_type = "Hybrid (สมดุล)"
        if dp < 150: runner_type = "Diesel (Aerobic Engine)"
        elif dp > 250: runner_type = "Turbo (Anaerobic Power)"
        
        advice_text = get_coach_advice(runner_type, cs_pace, dp)

        # --- Display Results ---
        st.subheader(f"📊 ผลวิเคราะห์ (3-Point): {student_name}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Critical Speed", f"{cs:.2f} m/s", f"Pace {cs_pace}")
        col2.metric("Anaerobic Cap (D')", f"{dp:.0f} m", "ถังสำรอง")
        col3.metric("Type", runner_type.split()[0])

        # --- ✅ เพิ่ม: แสดงกราฟบนหน้าเว็บ ---
        with st.expander("📈 ดูกราฟวิเคราะห์ (Linear Regression)", expanded=True):
            fig_web = plot_cs_regression(times, distances, cs, dp)
            st.pyplot(fig_web)
        # -----------------------------------

        st.info(advice_text)

        # Zones
        st.subheader("🎯 โซนซ้อมแนะนำ")
        zones_data = [
            ["Zone 1 Recovery", "< 70%", f"> {get_pace(cs*0.70)}", "คลายกรด / Active Rest"],
            ["Zone 2 Easy", "70-80%", f"{get_pace(cs*0.70)} - {get_pace(cs*0.80)}", "สร้างฐาน Aerobic / เก็บระยะ"],
            ["Zone 3 Steady", "80-90%", f"{get_pace(cs*0.80)} - {get_pace(cs*0.90)}", "ความทนทาน / Marathon Pace"],
            ["Zone 4 Threshold", "90-100%", f"{get_pace(cs*0.90)} - {get_pace(cs*1.00)}", "Tempo / ดันเพดานความเหนื่อย"],
            ["⚠️ CS Line", "100%", f"📍 {cs_pace}", "Red Line (ขีดจำกัดร่างกาย)"],
            ["Zone 5 VO2max", "100-110%", f"{get_pace(cs*1.00)} - {get_pace(cs*1.10)}", "Interval / กระตุ้นหัวใจ"],
            ["Zone 6 Anaerobic", "> 110%", f"< {get_pace(cs*1.10)}", "Speed / พัฒนาความเร็วสูงสุด"]
        ]
        df_zones = pd.DataFrame(zones_data, columns=["Zone", "Intensity", "Pace Range (min/km)", "Objective"])
        st.table(df_zones)
        
        # PDF
        st.markdown("---")
        st.subheader("📄 รายงานผล (PDF)")
        
        # ส่งค่า times, distances ไปให้ฟังก์ชันสร้าง PDF เพื่อวาดกราฟ
        pdf_bytes = create_pdf(student_name, test_date, cs, dp, runner_type, df_zones, advice_text, times, distances)
        
        if pdf_bytes:
            st.download_button(
                label="📥 ดาวน์โหลดรายงาน PDF (ภาษาไทย + กราฟ)",
                data=bytes(pdf_bytes),
                file_name=f"Report_{student_name}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👈 กรุณากรอกข้อมูลทั้ง 3 ระยะ แล้วกดปุ่ม 'คำนวณผลลัพธ์'")