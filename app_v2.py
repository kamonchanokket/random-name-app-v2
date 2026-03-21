import streamlit as st
import pandas as pd
import random
import requests
import time

# --- 1. ข้อมูลหลัก 18 คน (LOGIC เดิม ห้ามหาย!) ---
# ก๊อปปี้ INITIAL_MEMBERS จากโค้ดเดิมของคุณมาวางที่นี่
# เช่น: INITIAL_MEMBERS = { "นิ๊ค": "40-42", "พี่มิว": "44-46", ... }
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: URL ต่างๆ (แก้ URL ให้เป็นของคุณนะ)
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. MODERN UI DESIGN (CSS) ---
st.set_page_config(page_title="นครนายก Pool Villa 2026", page_icon="🏊‍♂️", layout="centered")

# CSS: เน้น Dark Mode, Neon Glow, Glassmorphism, Gradient ปุ่ม
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Kanit', sans-serif;
        color: #f1f5f9;
        background-color: #020617;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b 0%, #020617 100%);
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(20px);
        border-radius: 2rem;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.7);
        margin-bottom: 1.5rem;
    }

    /* Gradient Title */
    .neon-title {
        text-align: center;
        background: linear-gradient(135deg, #f97316 0%, #d946ef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        text-shadow: 0 0 30px rgba(217, 70, 239, 0.5);
    }

    /* Subtitle จากภาพ */
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Neon Icons */
    .neon-icon {
        color: #f97316;
        font-size: 3rem;
        text-shadow: 0 0 15px rgba(249, 115, 22, 0.7);
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Modern Selectbox */
    div[data-baseweb="select"] {
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Gradient Button จากรูป (Giver Page) */
    .stButton>button {
        width: 100%;
        border-radius: 18px;
        height: 3.8em;
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        font-weight: 800;
        font-size: 1.2rem;
        border: none;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.6);
    }
    
    /* Logout button ใน Sidebar */
    .sidebar .stButton>button {
        height: 2.5em;
        font-size: 0.9rem;
        background: #1e293b !important;
    }

    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (Fast Cache Logic) ---
@st.cache_data(ttl=60)
def load_data_turbo():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        history = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excls = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return history, picked, excls
    except:
        return {}, [], []

# โหลดข้อมูล
history, already_picked, exclusion_list = load_data_turbo()

# --- 4. SESSION MANAGEMENT (ล็อคตัวตน) ---
if 'my_user' not in st.session_state:
    st.session_state.my_user = None

# Header เสมอ
st.markdown('<div class="neon-title">นครนายก นาใจ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Secret Buddy Pool Villa 2026</div>', unsafe_allow_html=True)

# --- 5. MAIN LOGIC & UI SPLIT ---

if st.session_state.my_user is None:
    # --- หน้า Login (Identity Lock จาก UI เดิม) ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="neon-icon">🔒</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center;">ยืนยันตัวตนก่อน</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#94a3b8;">เลือกชื่อของคุณจากรายการเพื่อทำการล็อคเซสชัน</p>', unsafe_allow_html=True)
    
    u_select = st.selectbox("คุณคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
    
    if st.button("เข้าสู่ระบบ"):
        if u_select != "-- เลือกชื่อตัวเอง --":
            st.session_state.my_user = u_select
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    current_user = st.session_state.my_user
    st.write(f"สวัสดีคุณ: **{current_user}** 👋")

    # --- หน้า Dashboard ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # เช็คว่าเคยสุ่มหรือยัง (ดึงจากประวัติใน Sheet)
    if current_user in history:
        # กรณีสุ่มแล้ว: แสดงผล
        target = history[current_user]
        size = INITIAL_MEMBERS.get(target, "N/A")
        
        st.balloons()
        st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <p style="color: #94a3b8; font-size: 1.2rem; text-transform:uppercase; letter-spacing:1px;">เหยื่อของคุณคือ...</p>
                <h1 style="font-size: 5rem; font-weight: 800; color: #ffffff; margin: 15px 0;">{target}</h1>
                <div style="background: rgba(249, 115, 22, 0.1); color: #f97316; display: inline-block; padding: 10px 25px; border-radius: 50px; font-weight: 600; font-size:1.1rem; border: 1px solid rgba(249, 115, 22, 0.3);">
                    ไซส์เสื้อ: {size}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.info("⚠️ ผลการสุ่มถูกบันทึกใน Google Sheet แล้ว ไม่สามารถเปลี่ยนได้")
    
    else:
        # กรณีรอกดสุ่ม: แสดงไอคอนผีแบบรูป 10
        st.markdown('<div class="neon-icon">👻</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; font-size:1.2rem; color:#94a3b8;">คุณยังไม่ได้ทำการสุ่มเหยื่อ... พร้อมหรือยัง?</p>', unsafe_allow_html=True)
        
        # เพิ่มปุ่ม Logout จาก UI เดิม
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            if st.button("🔥 เริ่มสุ่มเดียวนี้!"):
                # Logic การสุ่ม (ไม่ซ้ำ, ไม่ใช่ตัวเอง, ไม่ใช่แฟน)
                candidates = [n for n in INITIAL_MEMBERS.keys() if n != current_user and n not in already_picked]
                
                # Logic ห้ามแฟนกันเจอกัน
                for p1, p2 in exclusion_list:
                    if current_user == p1 and p2 in candidates: candidates.remove(p2)
                    if current_user == p2 and p1 in candidates: candidates.remove(p1)
                
                if candidates:
                    with st.spinner('กำลังเฟ้นหาเหยื่อ...'):
                        time.sleep(1.5)
                        result = random.choice(candidates)
                        # เขียนข้อมูลลง Sheet ผ่าน Apps Script (No Key JSON!)
                        try:
                            requests.get(f"{SCRIPT_URL}?giver={current_user}&receiver={result}&mode=assign")
                            st.cache_data.clear() # เคลียร์แคชเพื่อโหลดข้อมูลใหม่
                            st.rerun()
                        except:
                            st.error("บันทึกประวัติไม่สำเร็จ! กรุณาลองใหม่")
                else:
                    st.error("ขออภัย! ไม่เหลือชื่อที่สุ่มได้ (หรือคุณติดกฎคู่ห้าม)")
                    
    st.markdown('</div>', unsafe_allow_html=True)

    # ปุ่มออกจากระบบแบบ UI เดิม
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# --- 6. ADMIN PANEL (จัดการคู่รัก จาก UI รูป 11) ---
with st.sidebar:
    st.markdown("### ⚙️ แอดมินจัดการแก๊ง")
    
    # ปิด Logic เก่าที่ให้ใครก็ได้ Add เพื่อน/คู่ห้าม
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        password_admin = st.text_input("รหัสผ่านแอดมิน", type="password")
        if st.button("เข้าสู่ระบบแอดมิน"):
            if password_admin == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        # เมื่อแอดมิน Login แล้ว
        st.markdown('<div style="text-align:center; font-weight:800; color:#f97316; font-size:1.5rem; margin-bottom:1rem;">ADMIN CONTROL</div>', unsafe_allow_html=True)
        
        # ส่วนจัดการคู่ห้าม (Anti-Fan Logic)
        st.markdown("---")
        st.subheader("❌ ตั้งค่าคู่ห้าม (แฟนกัน)")
        names_list = sorted(list(INITIAL_MEMBERS.keys()))
        col1, col2 = st.columns(2)
        exc1 = col1.selectbox("คนแรก", names_list, key="exc1")
        exc2 = col2.selectbox("คนที่สอง", names_list, key="exc2")
        if st.button("บันทึกคู่ห้ามลง Sheet"):
            try:
                # ยิงไปบอก Apps Script (mode=excl)
                requests.get(f"{SCRIPT_URL}?giver={exc1}&receiver={exc2}&mode=excl")
                st.success(f"ล็อกคู่ห้าม {exc1} กับ {exc2} แล้ว")
                st.cache_data.clear()
            except:
                st.error("บันทึกคู่ห้ามไม่สำเร็จ")

        st.markdown("---")
        # ดูผลสรุป
        if st.button("ดูผลสรุปทั้งหมด"):
            st.dataframe(pd.DataFrame([{"Giver": k, "Receiver": v, "Size": INITIAL_MEMBERS.get(v)} for k, v in history.items()]))

        if st.button("Logout Admin", type="secondary"):
            st.session_state.admin_logged_in = False
            st.rerun()