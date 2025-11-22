# --- แก้ไขส่วน Import ด้านบนสุดของไฟล์ ---
from fpdf import FPDF # ต้องมั่นใจว่าลง pip install fpdf2 แล้ว

# --- แก้ไขฟังก์ชัน create_pdf ใหม่ทั้งหมด ---
def create_pdf(student_name, test_date, cs, dp, runner_type, zones_df):
    # สร้าง PDF แนวตั้ง (P), หน่วย mm, ขนาด A4
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # 1. ลงทะเบียนฟอนต์ภาษาไทย (สำคัญมาก!)
    # ต้องมีไฟล์ THSarabunNew.ttf ในโฟลเดอร์เดียวกัน
    try:
        pdf.add_font('Thai', '', 'THSarabunNew.ttf')
        pdf.set_font('Thai', '', 16)
        has_font = True
    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf กรุณาหาโหลดและนำมาวางไว้ข้างๆ app.py")
        return None # จบการทำงานถ้าไม่มีฟอนต์

    # 2. ส่วนหัวรายงาน (Header)
    pdf.set_font_size(22)
    pdf.cell(0, 12, text=f"รายงานผลการทดสอบ: Critical Speed Profile", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font_size(16)
    pdf.cell(0, 10, text=f"นักกีฬา: {student_name} | วันที่: {test_date}", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5) # เว้นบรรทัด

    # 3. ส่วนแสดงค่า Metrics (พื้นหลังสี)
    pdf.set_fill_color(230, 240, 255) # ฟ้าอ่อน
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="1. Physiological Metrics (ค่าสมรรถภาพ)", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Thai', '', 16)
    pdf.ln(2)
    pdf.cell(0, 8, text=f"Critical Speed (CS): {cs:.2f} m/s", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Anaerobic Capacity (D'): {dp:.1f} m", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Runner Type: {runner_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 4. ตารางโซนซ้อม (Table)
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="2. Personalized Training Zones (โซนซ้อม)", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # หัวตาราง
    pdf.set_font_size(14)
    pdf.set_fill_color(240, 240, 240) # เทาอ่อน
    
    # กำหนดความกว้างคอลัมน์
    w_zone = 40
    w_int = 25
    w_pace = 45
    w_obj = 80
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

    # 5. คำแนะนำโค้ช
    pdf.ln(8)
    pdf.set_font('Thai', '', 18)
    pdf.cell(0, 10, text="Coach's Insight (คำแนะนำ):", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Thai', '', 14)
    advice = f"นักวิ่งประเภท {runner_type} มีถังพลังงานสำรอง (D') อยู่ที่ {dp:.0f} เมตร ควรระวังการใช้ความเร็วช่วงต้นเกม อย่าให้เกิน Threshold นานเกินไป เพราะจะทำให้แบตเตอรี่หมดเร็ว"
    
    # ใช้ multi_cell สำหรับข้อความยาวๆ ให้ตัดบรรทัดอัตโนมัติ
    pdf.multi_cell(0, 8, text=advice)

    # ส่งค่ากลับเป็น bytes เพื่อให้ปุ่ม download รับไปใช้
    return pdf.output()
