from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = "nakhon_nayok_google_sheets_v11"

# --- ตั้งค่า Google Sheets ---
SHEET_NAME = "ชื่อ Google Sheet ของคุณ" # เปลี่ยนเป็นชื่อไฟล์ชีทที่คุณสร้าง
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    return sheet

def load_data_from_gs():
    try:
        sheet = get_sheet()
        # ดึงข้อมูลจาก Sheet1 (เก็บคู่สุ่ม) และ Sheet2 (เก็บคู่ห้าม)
        worksheet = sheet.get_worksheet(0) # แผ่นงานที่ 1: เก็บ Assignments
        ex_worksheet = sheet.get_worksheet(1) # แผ่นงานที่ 2: เก็บ Exclusions (ต้องสร้างรอไว้)
        
        all_vals = worksheet.get_all_records()
        assignments = {row['giver']: row['receiver'] for row in all_vals if row['receiver']}
        
        ex_vals = ex_worksheet.get_all_values()
        exclusions = ex_vals if ex_vals else []
        
        return {
            "names": list(INITIAL_MEMBERS.keys()),
            "assignments": assignments,
            "sizes": INITIAL_MEMBERS,
            "exclusions": exclusions
        }
    except Exception as e:
        print(f"Error loading: {e}")
        return {"names": list(INITIAL_MEMBERS.keys()), "assignments": {}, "sizes": INITIAL_MEMBERS, "exclusions": []}

def save_assignment_to_gs(giver, receiver):
    sheet = get_sheet().get_worksheet(0)
    # ค้นหาแถวที่มีชื่อ giver แล้วอัปเดตช่อง receiver
    cell = sheet.find(giver)
    sheet.update_cell(cell.row, 2, receiver)

# --- หน้าตาเว็บ (เหมือนเดิมแต่ปรับ Logic เล็กน้อย) ---
# (ใช้ HTML_TEMPLATE เดิมจากโค้ดที่คุณให้มาได้เลย แต่เพิ่มเงื่อนไขเช็ค session)
HTML_TEMPLATE = """
... (Copy จากโค้ดเดิมของคุณได้เลย) ...
"""

@app.route("/")
def index():
    # ระบบจำการเข้า: ถ้าคนนี้เคยสุ่มแล้วในเครื่องนี้ ให้เด้งไปหน้าผลลัพธ์เลย
    if "my_name" in session:
        data = load_data_from_gs()
        user = session["my_name"]
        if user in data["assignments"]:
            target = data["assignments"][user]
            return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target, result_size=data["sizes"].get(target, "ไม่ระบุ"))
    
    data = load_data_from_gs()
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index')

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    data = load_data_from_gs()
    
    # 1. ป้องกันการแอบสุ่มให้เพื่อน: บันทึกชื่อคนกดลงใน session
    session["my_name"] = user

    # 2. ถ้าเคยสุ่มไปแล้ว ให้ดึงผลเดิมจาก Google Sheet
    if user in data["assignments"]:
        target = data["assignments"][user]
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target, result_size=data["sizes"].get(target, "ไม่ระบุ"))

    # 3. Logic การสุ่ม (เหมือนเดิมแต่ดึงข้อมูลจาก Cloud)
    assigned_receivers = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned_receivers]
    
    for p1, p2 in data.get("exclusions", []):
        if user == p1 and p2 in candidates: candidates.remove(p2)
        if user == p2 and p1 in candidates: candidates.remove(p1)

    if not candidates:
        return "<script>alert('ไม่มีใครเหลือให้สุ่มแล้ว!'); window.location='/';</script>"

    target = random.choice(candidates)
    
    # 4. บันทึกลง Google Sheet
    try:
        save_assignment_to_gs(user, target)
    except:
        return "เกิดข้อผิดพลาดในการบันทึกลง Google Sheets"

    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target, result_size=data["sizes"].get(target, "ไม่ระบุ"))

@app.route("/admin")
def admin():
    if not session.get("is_admin"): return render_template_string(HTML_TEMPLATE, page='login')
    data = load_data_from_gs()
    return render_template_string(HTML_TEMPLATE, names=data["names"], sizes=data.get("sizes", {}), assignments=data.get("assignments", {}), exclusions=data.get("exclusions", []), page='admin')

# ... (Route อื่นๆ เช่น admin_login, logout, add_exclusion ให้ใช้ Logic ของ Google Sheets แบบเดียวกัน) ...

if __name__ == "__main__":
    app.run(debug=True)