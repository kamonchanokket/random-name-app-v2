import streamlit as st
import pandas as pd
import random
import requests
import time

# --- 1. ข้อมูลหลัก (Logic เดิมห้ามหาย!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: อย่าลืมแก้ URL ให้เป็นของคุณนะจ๊ะ
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"

# --- 2. แก้ไข UI ตามจุดที่แจ้ง (เลข 1 และ 2) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; color: white; }
    .stApp { background-color: #0d1117; }

    /* แก้เลข 2: ปรับสี Selectbox ให้อ่านง่าย (ตัวหนังสือขาว พื้นหลังเข้ม) */
    div[data-baseweb="select"] > div {
        background-color: #1c2128 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }
    /* สีตัวหนังสือในรายการ Dropdown */
    div[data-baseweb="popover"] li {
        background-color: #1c2128 !important;
        color: white !important;
    }
    /* ซ่อนเลข 1 (ส่วนเกิน) และปรับแต่งช่องว่าง */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 15px;
        padding: 5px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] { height: 50px; color: #8b949e; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #21262d !important; color: #f97316 !important; }

    .glass-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 20px; padding: 30px; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important;
        border-radius: 15px !important;
        height: 3.5rem !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        hist = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excls = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return hist, picked, excls
    except: return {}, [], []

history, already_picked, exclusion_list = load_data()

# --- 4. SESSION IDENTITY LOGIC (กันแอบดูเพื่อน) ---
if 'my_user' not in st.session_state:
    st.session_state.my_user = None

st.markdown('<h1 style="text-align:center; font-weight:800; color:white; margin-bottom:0;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#8b949e; font-size:0.9rem;">Secret Buddy "เสื้อที่มึงไม่อยากใส่แต่ต้องใส่"</p>', unsafe_allow_html=True)

# แถบเมนู Tab 2 อันตามที่ชอบ
tab_draw, tab_admin = st.tabs(["🎁 จับคู่คนที่เราจะแกง", "⚙️ จัดการแก๊ง"])

with tab_draw:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # ด่านที่ 1: ยืนยันตัวตน (ล็อคชื่อ)
    if st.session_state.my_user is None:
        st.markdown('<h1 style="text-align:center;">👻</h1>', unsafe_allow_html=True)
        st.write("มึงคือใครในแก๊ง?")
        u_name = st.selectbox("เลือกชื่อตัวเองเพื่อล็อคเซสชัน", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())), label_visibility="collapsed")
        
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.my_user = u_name
                st.rerun()
            else:
                st.error("เลือกชื่อก่อนจ่ะแม่!")
    
    # ด่านที่ 2: เมื่อล็อคชื่อแล้ว (แก้ปัญหาแอบดูเพื่อน)
    else:
        me = st.session_state.my_user
        st.markdown(f"<p style='text-align:right; color:#f97316; font-size:0.8rem;'>ล็อคระบบในชื่อ: <b>{me}</b></p>", unsafe_allow_html=True)
        
        if me in history:
            # กรณีสุ่มไปแล้ว: โชว์ผลของตัวเองทันที ล็อคหน้าจอนี้ไว้
            target = history[me]
            st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <p style="color:#8b949e; margin-bottom:5px;">เหยื่อของมึงคือ...</p>
                    <h1 style="font-size:4.5rem; color:white; margin:0;">{target}</h1>
                    <div style="background:rgba(249,115,22,0.1); padding:10px; border-radius:10px; color:#f97316; border:1px solid #f97316; display:inline-block; margin-top:15px;">
                        ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, "N/A")}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # กรณีรอสุ่ม
            st.markdown('<h1 style="text-align:center;">🎲</h1>', unsafe_allow_html=True)
            st.write("กดปุ่มเพื่อเฟ้นหาเหยื่อของมึง!")
            if st.button("สุ่มหาเหยื่อเดียวนี้!"):
                # Logic สุ่ม: ห้ามตัวเอง, ห้ามซ้ำ, ห้ามแฟน
                candidates = [n for n in INITIAL_MEMBERS.keys() if n != me and n not in already_picked]
                for p1, p2 in exclusion_list:
                    if me == p1 and p2 in candidates: candidates.remove(p2)
                    if me == p2 and p1 in candidates: candidates.remove(p1)
                
                if candidates:
                    res = random.choice(candidates)
                    requests.get(f"{SCRIPT_URL}?giver={me}&receiver={res}&mode=assign")
                    st.balloons()
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("ไม่เหลือใครให้มึงสุ่มแล้ว (หรือมึงติดกฎคู่ห้าม)")

        if st.button("Logout / เปลี่ยนคนเล่น", type="secondary"):
            st.session_state.my_user = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab_admin:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    admin_pw = st.text_input("รหัสผ่านแอดมิน", type="password")
    if admin_pw == "qwertyuiop[]asdfghjkl":
        st.write("### ❌ ตั้งค่าคู่ห้าม (แฟนกัน)")
        col1, col2 = st.columns(2)
        ex1 = col1.selectbox("คนที่ 1", sorted(INITIAL_MEMBERS.keys()), key="ex1")
        ex2 = col2.selectbox("คนที่ 2", sorted(INITIAL_MEMBERS.keys()), key="ex2")
        if st.button("ล็อคคู่ห้าม"):
            requests.get(f"{SCRIPT_URL}?giver={ex1}&receiver={ex2}&mode=excl")
            st.success("บันทึกคู่ห้ามเรียบร้อยจ้า")
            st.cache_data.clear()
        
        st.write("---")
        if st.checkbox("ดูโพยลับทั้งหมด"):
            st.dataframe(pd.DataFrame([{"Giver": k, "Receiver": v} for k, v in history.items()]))
    st.markdown('</div>', unsafe_allow_html=True)