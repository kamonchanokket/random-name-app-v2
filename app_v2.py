import streamlit as st
import pandas as pd
import random
import requests

# --- 1. ข้อมูลรายชื่อและไซส์เสื้อ 18 คน (ห้ามหาย!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 2. CONFIG การเชื่อมต่อ (ใช้แค่ URL) ---
# 1. URL ของ Sheet ที่กด Publish to web เป็น CSV (สำหรับอ่าน)
CSV_URL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
# 2. URL ของ Apps Script ที่ได้จากขั้นตอนข้างบน (สำหรับเขียน)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxGIhUZBMzo3-hcPf5FX8oCs8i4wCLeYgwd1-XVCQx9AwkGjUn6B1OjZMS3YVyHODLH/exec"

# --- 3. UI STYLE (Modern Gen Y-Z) ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@400;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; background-color: #020617; color: white; }
    .stApp { background: radial-gradient(circle at top right, #1e293b, #020617); }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { background: linear-gradient(90deg, #f97316, #d946ef); color: white; font-weight: 800; border-radius: 15px; border: none; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC อ่าน/เขียน ---
def get_current_assignments():
    try:
        # อ่านข้อมูลจาก Sheet ตรงๆ ไม่ใช้ Key
        df = pd.read_csv(CSV_URL)
        return dict(zip(df['Giver'], df['Receiver']))
    except:
        return {}

def save_to_sheet(giver, receiver):
    # ส่งข้อมูลไปที่ Apps Script (ง่ายเหมือนเปิดเว็บ)
    requests.get(f"{SCRIPT_URL}?giver={giver}&receiver={receiver}")

# --- 5. MAIN APP ---
st.title("🚌 นครนายก นาใจ 2026")
assignments = get_current_assignments()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
user = st.selectbox("คุณคือใคร? (เลือกชื่อตัวเอง)", ["-- เลือกชื่อ --"] + sorted(list(INITIAL_MEMBERS.keys())))

if user != "-- เลือกชื่อ --":
    if user in assignments:
        target = assignments[user]
        st.balloons()
        st.success(f"สุ่มได้: {target}")
        st.info(f"ไซส์เสื้อ: {INITIAL_MEMBERS.get(target)}")
    else:
        if st.button("🚀 เริ่มสุ่มเหยื่อ!"):
            assigned = list(assignments.values())
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != user and n not in assigned]
            
            if candidates:
                res = random.choice(candidates)
                save_to_sheet(user, res)
                st.rerun()
            else:
                st.error("ไม่มีชื่อเหลือให้สุ่มแล้ว!")
st.markdown('</div>', unsafe_allow_html=True)

# --- แอดมินจัดการหลังบ้าน ---
with st.expander("🔑 สำหรับแอดมิน"):
    pw = st.text_input("รหัสผ่าน", type="password")
    if pw == "qwertyuiop[]asdfghjkl":
        st.write("ตารางสรุปผล:")
        st.table(pd.DataFrame([{"ผู้สุ่ม": k, "เหยื่อ": v} for k, v in assignments.items()]))