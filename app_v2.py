import streamlit as st
import pandas as pd
import random
import requests

# --- 1. CONFIG & DATA (Logic แน่นปึ้ก!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: ใส่ URL ของแม่ตรงนี้จ่ะ
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. THE ULTIMATE UI (แก้ปีกกาซ้อนกัน 2 ชั้นเพื่อกัน Syntax Error) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="st-"] {{ font-family: 'Kanit', sans-serif; color: white; text-align: center; }}
    .stApp {{ background-color: #0d1117; }}

    /* แก้ไขช่อง Input/Selectbox: พื้นขาว-ตัวดำเข้ม (QC เนี๊ยบ) */
    div[data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }}
    div[data-baseweb="select"] span {{
        color: #000000 !important; 
        font-weight: 800 !important;
    }}
    .stTextInput input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
    }}
    
    label {{ color: #f97316 !important; font-weight: 800 !important; font-size: 1.2rem !important; }}

    /* Tabs & Design */
    .stTabs [data-baseweb="tab-list"] {{ display: flex; justify-content: center; border-bottom: 1px solid #30363d; gap: 20px; }}
    .stTabs [aria-selected="true"] {{ color: #f97316 !important; border-bottom: 3px solid #f97316 !important; }}

    .victim-name {{ font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; }}
    .victim-box {{ background-color: #1a1515; border: 1px solid #3d3030; border-radius: 20px; padding: 25px; margin: 20px auto; max-width: 500px; }}

    .stButton>button {{
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; height: 3.5rem;
    }}
    
    .logout-footer {{ margin-top: 80px; padding-top: 15px; border-top: 1px solid #333; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOGIC (Anti-Refresh & Exclusion) ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        hist = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excl = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return hist, picked, excl
    except: return {}, [], []

history, already_picked, exclusion_list = load_data()

if 'user_auth' not in st.session_state: st.session_state.user_auth = None

# --- 4. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)

tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

with tab_draw:
    if st.session_state.user_auth is None:
        st.markdown('<div style="font-size:100px;">👻</div>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.user_auth = u_name
                st.rerun()
    else:
        me = st.session_state.user_auth
        if me in history:
            target = history[me]
            st.markdown(f"""
                <div class="victim-reveal">
                    <p style="color:#8b949e;">เตรียมชุดให้เพื่อนคนนี้...</p>
                    <div class="victim-name">{target}</div>
                    <div class="victim-box">
                        <p style="color:#f97316; font-size:1.5rem; font-weight:800;">ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, 'N/A')}</p>
                        <p style="color:#8b949e; font-size:0.9rem; margin-top:10px;">"คัดมาแบบที่ใส่แล้วหน้าต้องร้องไห้ แต่ต้องใส่ลงสระ!"</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
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
                else:
                    st.error("ไม่มีชื่อที่สุ่มได้ในตอนนี้!")

        st.markdown('<div class="logout-footer">', unsafe_allow_html=True)
        with st.expander("Admin Only: เปลี่ยนคนเล่น"):
            lo_pw = st.text_input("รหัสแอดมิน", type="password", key="lo_pw")
            if st.button("Logout"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.user_auth = None
                    st.rerun()
                else: st.error("รหัสไม่ถูกต้อง!")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_admin:
    pw = st.text_input("รหัสแอดมิน", type="password", key="admin_pw")
    if pw == ADMIN_PASSWORD:
        st.write(f"### สถิติ: {len(history)} / {len(INITIAL_MEMBERS)} คน")
        if exclusion_list:
            st.write("📋 **คู่รักต้องห้าม:**", pd.DataFrame(exclusion_list, columns=["ห้าม", "สุ่มเจอคนนี้"]))
        if st.checkbox("ดูโพยลับ"):
            st.dataframe(pd.DataFrame([{"ผู้ให้":k, "ผู้รับ":v} for k, v in history.items()]))