import streamlit as st
import pandas as pd
import random
import requests
from streamlit_javascript import st_javascript

# --- 1. CONFIG & DATA ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# แม่จ๋า แก้ URL 3 จุดนี้ให้เป็นของแม่นะจ๊ะ
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. THE FINAL UI (แก้ตามรูปที่แม่วงเป๊ะๆ) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Kanit', sans-serif; color: white; text-align: center; }}
    .stApp {{ background-color: #0d1117; }}

    /* Dropdown: พื้นดำสนิท ขอบส้ม ตัวขาว (ตามรูป 4dc68b) */
    div[data-baseweb="select"] {{ 
        background-color: #0d1117 !important; 
        border: 2px solid #f97316 !important; 
        border-radius: 12px !important; 
    }}
    div[data-baseweb="select"] * {{ color: #ffffff !important; font-weight: 600 !important; }}
    
    /* รายการเด้งลงมา (Listbox): พื้นดำ ตัวขาว (ตามรูป 4e37a2) */
    div[role="listbox"] {{ background-color: #0d1117 !important; border: 1px solid #30363d !important; }}
    div[role="listbox"] ul li {{ color: #ffffff !important; background-color: #0d1117 !important; }}
    div[role="listbox"] ul li:hover {{ background-color: #f97316 !important; }}

    /* ปุ่มหลักสุ่ม */
    .stButton>button {{
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; height: 3.5rem;
    }}

    .victim-name {{ font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; }}
    .victim-box {{ background-color: #161b22; border: 1px solid #30363d; border-radius: 20px; padding: 25px; margin: 20px auto; }}
    
    /* ปุ่ม Logout สีเทาจางๆ ล่างสุด (ตามรูป 4db442) */
    .logout-footer {{ color: #4b5563 !important; font-size: 0.8rem; margin-top: 50px; cursor: pointer; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PERSISTENT LOCK (ป้องกัน Refresh แล้วหลุด) ---
stored_name = st_javascript("localStorage.getItem('buddy_user');")

if 'user_auth' not in st.session_state:
    st.session_state.user_auth = stored_name if (stored_name and stored_name != "null") else None

def set_lock(name):
    st_javascript(f"localStorage.setItem('buddy_user', '{name}');")
    st.session_state.user_auth = name
    st.rerun()

def clear_lock():
    st_javascript("localStorage.removeItem('buddy_user');")
    st.session_state.user_auth = None
    st.rerun()

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=1)
def load_all_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        hist = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excl = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return hist, picked, excl
    except: return {}, [], []

history, already_picked, exclusion_list = load_all_data()

# --- 5. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

with tab_draw:
    me = st.session_state.user_auth
    
    # CASE 1: สุ่มไปแล้ว (ล็อคหน้าผลลัพธ์)
    if me and me in history:
        target = history[me]
        st.markdown(f"""
            <div class="victim-box">
                <p style="color:#8b949e;">เตรียมชุดให้เพื่อนคนนี้...</p>
                <div class="victim-name">{target}</div>
                <div style="background:#0d1117; padding:15px; border-radius:15px;">
                    <p style="color:#f97316; font-size:1.5rem; font-weight:800; margin:0;">ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, 'N/A')}</p>
                    <p style="color:#8b949e; font-size:0.9rem; margin-top:10px;">"คัดมาแบบที่ใส่แล้วต้องร้องไห้ แต่ต้องใส่ลงสระ!"</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="logout-footer">Admin Only: เปลี่ยนคนเล่น</div>', unsafe_allow_html=True)
        with st.expander("ปลดล็อคระบบ"):
            pw = st.text_input("รหัสผ่าน", type="password")
            if st.button("Logout"):
                if pw == ADMIN_PASSWORD: clear_lock()
                else: st.error("รหัสผิดจ่ะ")

    # CASE 2: ยังไม่ได้เลือกชื่อ
    elif not me:
        st.markdown('<div style="font-size:100px;">👻</div>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --": set_lock(u_name)

    # CASE 3: เลือกชื่อแล้วแต่ยังไม่สุ่ม
    else:
        st.markdown(f"<h3>สวัสดีจ๊ะคุณ {me} 👋</h3>", unsafe_allow_html=True)
        if st.button("🔥 เริ่มสุ่มหาเหยื่อเดียวนี้!"):
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != me and n not in already_picked]
            for p1, p2 in exclusion_list:
                if me == p1 and p2 in candidates: candidates.remove(p2)
                if me == p2 and p1 in candidates: candidates.remove(p1)
            
            if candidates:
                res = random.choice(candidates)
                requests.get(f"{SCRIPT_URL}?giver={me}&receiver={res}&mode=assign")
                st.cache_data.clear()
                st.rerun()
            else: st.error("ไม่มีชื่อเหลือให้สุ่มแล้ว!")

with tab_admin:
    admin_pw = st.text_input("รหัสผ่านแอดมิน", type="password", key="admin_key")
    if admin_pw == ADMIN_PASSWORD:
        # สถิติจำนวนครั้ง (ตาม REQ)
        st.markdown(f"### 📊 สถิติ: สุ่มแล้ว {len(history)} / {len(INITIAL_MEMBERS)} คน")
        
        # ตารางคู่รัก (ตาม REQ)
        st.write("📋 **รายชื่อคู่รัก (ห้ามสุ่มเจอกัน):**")
        if exclusion_list:
            st.table(pd.DataFrame(exclusion_list, columns=["ชื่อหลัก", "แฟน (ห้ามสุ่มเจอ)"]))
        
        if st.checkbox("ดูโพยลับ"):
            st.dataframe(pd.DataFrame([{"ผู้ให้":k, "ผู้รับ":v} for k, v in history.items()]))