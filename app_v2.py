import streamlit as st
import pandas as pd
import random
import requests

# --- 1. CONFIG (Logic แน่นปึ้ก!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. CSS (แก้ Dropdown และ ปุ่ม Logout สีเทา) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Kanit', sans-serif; color: white; text-align: center; }}
    .stApp {{ background-color: #0d1117; }}

    /* แก้ Dropdown: พื้นขาว ตัวดำ (ทุกจุด!) */
    div[data-baseweb="select"] {{ background-color: #FFFFFF !important; border-radius: 12px !important; }}
    div[data-baseweb="select"] * {{ color: #000000 !important; font-weight: 800 !important; }}
    
    /* รายการที่เด้งลงมา */
    ul[role="listbox"] li {{ background-color: #FFFFFF !important; color: #000000 !important; font-weight: 700 !important; }}
    
    /* ช่อง Input ปกติ */
    .stTextInput input {{ background-color: #FFFFFF !important; color: #000000 !important; font-weight: 800 !important; }}
    label {{ color: #f97316 !important; font-weight: 800 !important; font-size: 1.2rem !important; }}

    /* ปุ่มหลัก (สุ่ม) */
    .stButton>button {{
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; height: 3.5rem;
    }}

    /* ปุ่ม Logout สีเทา (ตามสั่งแม่) */
    div.logout-container button {{
        background-color: transparent !important;
        color: #4b5563 !important;
        border: 1px solid #4b5563 !important;
        border-radius: 10px !important;
        font-size: 0.8rem !important;
        height: 2.5rem !important;
        width: auto !important;
        padding: 0 20px !important;
    }}
    div.logout-container button:hover {{ color: #f97316 !important; border-color: #f97316 !important; }}

    .victim-name {{ font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; }}
    .victim-box {{ background-color: #1a1515; border: 1px solid #3d3030; border-radius: 20px; padding: 25px; margin: 20px auto; max-width: 500px; }}
    .logout-footer {{ margin-top: 100px; padding-top: 20px; border-top: 1px solid #333; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOGIC (Anti-Refresh Lock) ---
@st.cache_data(ttl=1)
def fetch_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        hist = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excl = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return hist, picked, excl
    except: return {}, [], []

history, already_picked, exclusion_list = fetch_data()

if 'user_auth' not in st.session_state: st.session_state.user_auth = None

# --- 4. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

with tab_draw:
    current_user = st.session_state.user_auth
    
    # ด่าน 1: ถ้าเคยสุ่มแล้ว (เช็คจาก DB) ล็อคหน้าทันที!
    if current_user and current_user in history:
        target = history[current_user]
        st.markdown(f"""
            <div class="victim-reveal">
                <p style="color:#8b949e;">ล็อคระบบในชื่อ: {current_user}</p>
                <div class="victim-name">{target}</div>
                <div class="victim-box">
                    <p style="color:#f97316; font-size:1.5rem; font-weight:800;">ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, 'N/A')}</p>
                    <p style="color:#8b949e; font-size:0.9rem; margin-top:10px;">"คัดมาแบบที่ใส่แล้วหน้าต้องร้องไห้ แต่ต้องใส่ลงสระ!"</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ด่าน 2: เลือกชื่อ (ถ้ายังไม่เคยเลือก)
    elif not current_user:
        st.markdown('<div style="font-size:100px;">👻</div>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.user_auth = u_name
                st.rerun()
    
    # ด่าน 3: หน้ากดสุ่ม (ถ้าเลือกชื่อแล้วแต่ยังไม่สุ่ม)
    else:
        st.markdown(f"<h3>สวัสดีจ๊ะคุณ {current_user} 👋</h3>", unsafe_allow_html=True)
        if st.button("🔥 เริ่มสุ่มหาเหยื่อเดียวนี้!"):
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != current_user and n not in already_picked]
            for p1, p2 in exclusion_list:
                if current_user == p1 and p2 in candidates: candidates.remove(p2)
                if current_user == p2 and p1 in candidates: candidates.remove(p1)
            
            if candidates:
                res = random.choice(candidates)
                requests.get(f"{SCRIPT_URL}?giver={current_user}&receiver={res}&mode=assign")
                st.cache_data.clear()
                st.rerun()
            else: st.error("ไม่มีชื่อที่สุ่มได้!")

    # ปุ่ม Logout สีเทา (แยกส่วนชัดเจน ไม่ซ้อน!)
    if current_user:
        st.markdown('<div class="logout-footer">', unsafe_allow_html=True)
        st.write("ถ้าไม่ใช่คุณ หรือต้องการเปลี่ยนชื่อ (ต้องใส่รหัสแอดมิน)")
        with st.container():
            st.markdown('<div class="logout-container">', unsafe_allow_html=True)
            lo_pw = st.text_input("รหัสแอดมินเพื่อ Logout", type="password", key="lo_pw")
            if st.button("Logout เปลี่ยนคนเล่น"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.user_auth = None
                    st.rerun()
                else: st.error("รหัสผิดจ่ะแม่!")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_admin:
    pw = st.text_input("รหัสผ่านแอดมิน", type="password", key="admin_pw")
    if pw == ADMIN_PASSWORD:
        st.write(f"### สถิติ: {len(history)} / {len(INITIAL_MEMBERS)} คน")
        if st.checkbox("ดูโพยลับ"):
            st.dataframe(pd.DataFrame([{"ผู้ให้":k, "ผู้รับ":v} for k, v in history.items()]))