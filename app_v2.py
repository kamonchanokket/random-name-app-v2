import streamlit as st
import pandas as pd
import random
import requests
import time

# --- 1. CONFIG & DATA ---
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

# --- 2. THE FINAL UI (แก้ Dropdown และ Layout) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Kanit', sans-serif; color: white; text-align: center; }}
    .stApp {{ background-color: #0d1117; }}

    /* Dropdown: ขอบส้ม-พื้นดำ-ตัวขาว (ตามรูปแม่) */
    div[data-baseweb="select"] {{ 
        background-color: #161b22 !important; 
        border: 2px solid #f97316 !important; 
        border-radius: 12px !important; 
    }}
    div[data-baseweb="select"] * {{ color: #ffffff !important; font-weight: 600 !important; }}
    div[role="listbox"] {{ background-color: #161b22 !important; border: 1px solid #30363d !important; }}
    div[role="listbox"] ul li {{ color: #ffffff !important; background-color: #161b22 !important; }}
    div[role="listbox"] ul li:hover {{ background-color: #f97316 !important; }}

    /* ปุ่มหลักสุ่ม */
    .stButton>button {{
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; height: 3.5rem;
    }}

    /* สไตล์ Admin Table */
    .stDataFrame {{ background-color: #161b22 !important; border-radius: 10px; }}
    
    .victim-name {{ font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; }}
    .victim-box {{ background-color: #161b22; border: 1px solid #30363d; border-radius: 20px; padding: 25px; margin: 20px auto; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE (ดึงครบทุกอย่าง) ---
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

if 'user_auth' not in st.session_state: st.session_state.user_auth = None

# --- 4. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)

tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

with tab_draw:
    me = st.session_state.user_auth
    
    # ด่าน 1: ถ้าเคยสุ่มแล้ว ล็อคหน้าผลลัพธ์ทันที (เช็คจาก DB)
    if me and me in history:
        target = history[me]
        st.markdown(f"""
            <div class="victim-box">
                <p style="color:#8b949e;">คุณ ({me}) ได้สุ่มเหยื่อไปแล้ว</p>
                <div class="victim-name">{target}</div>
                <div style="background:#0d1117; padding:15px; border-radius:15px;">
                    <p style="color:#f97316; font-size:1.5rem; font-weight:800; margin:0;">ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, 'N/A')}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # ปุ่ม Logout (เทา)
        with st.expander("เปลี่ยนคนเล่น (รหัสแอดมิน)"):
            lo_pw = st.text_input("Admin Password", type="password", key="lo_pw")
            if st.button("Logout"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.user_auth = None
                    st.rerun()
                else: st.error("รหัสผิดจ่ะ")

    elif not me:
        st.markdown('<div style="font-size:100px;">👻</div>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.user_auth = u_name
                st.rerun()
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
            else: st.error("ไม่มีชื่อที่สุ่มได้!")

with tab_admin:
    pw = st.text_input("รหัสผ่านแอดมิน", type="password", key="admin_pw")
    if pw == ADMIN_PASSWORD:
        # --- [REQ] โชว์จำนวนครั้งสุ่มไปแล้ว ---
        total_members = len(INITIAL_MEMBERS)
        done_count = len(history)
        st.markdown(f"""
            <div style="background:#161b22; padding:20px; border-radius:15px; border-left:5px solid #f97316; margin-bottom:20px;">
                <h2 style="margin:0; color:#f97316;">สถิติแก๊ง</h2>
                <p style="font-size:1.5rem; margin:10px 0;">สุ่มไปแล้ว: <b>{done_count}</b> / {total_members} คน</p>
            </div>
        """, unsafe_allow_html=True)

        # --- [REQ] โชว์ตารางคู่รักห้ามสุ่ม ---
        st.write("📋 **รายชื่อคู่รัก (ห้ามสุ่มเจอกัน):**")
        if exclusion_list:
            ex_df = pd.DataFrame(exclusion_list, columns=["ชื่อหลัก", "ห้ามสุ่มเจอ"])
            st.table(ex_df)
        else:
            st.info("ยังไม่มีข้อมูลคู่รัก")

        # --- โพยลับ ---
        if st.checkbox("ดูโพยลับ (สุ่มใครไปบ้างแล้ว)"):
            if history:
                reveal_df = pd.DataFrame([{"ผู้ให้": k, "ผู้รับ": v} for k, v in history.items()])
                st.dataframe(reveal_df, use_container_width=True)
            else:
                st.write("ยังไม่มีใครเริ่มสุ่มจ่ะ")