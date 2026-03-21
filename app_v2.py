import streamlit as st
import pandas as pd
import random
import requests
import time

# --- 1. ข้อมูลหลัก (Logic เดิมแน่นปั๊ก!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: URL Google Sheets (ใส่ของตัวเองนะจ๊ะ)
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. THE ULTIMATE UI (CSS) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="🏊‍♂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; color: white; }
    .stApp { background-color: #0d1117; }

    /* Centered Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 20px;
        padding: 5px 20px;
        border: 1px solid #30363d;
        width: fit-content;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab"] { height: 50px; color: #8b949e; font-weight: 600; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background-color: transparent !important; color: #f97316 !important; border-bottom: 2px solid #f97316 !important; }

    /* Victim Card & Name */
    .victim-reveal { text-align: center; padding: 20px 10px; }
    .victim-name { font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; text-shadow: 0 0 20px rgba(252, 231, 188, 0.3); }
    .victim-box { background-color: #1a1515; border: 1px solid #3d3030; border-radius: 20px; padding: 25px; margin-top: 10px; }

    /* Input สไตล์ Modern */
    .stTextInput input { background-color: #f0f2f6 !important; color: #0d1117 !important; border-radius: 10px !important; }
    .stButton>button { background: linear-gradient(90deg, #f97316, #d946ef) !important; border: none !important; border-radius: 15px !important; height: 3.5rem !important; font-weight: 800 !important; }
    
    /* Summary Badge */
    .summary-badge { background: rgba(249, 115, 22, 0.05); border: 1px solid #f97316; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & SESSION LOGIC ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        return dict(zip(df_a['Giver'], df_a['Receiver'])), df_a['Receiver'].tolist(), list(zip(df_e['P1'], df_e['P2']))
    except: return {}, [], []

history, already_picked, exclusion_list = load_data()

if 'my_user' not in st.session_state:
    st.session_state.my_user = None

# --- 4. RENDER ---
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)

tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

# --- TAB: DRAW ---
with tab_draw:
    if st.session_state.my_user is None:
        st.markdown('<div style="text-align:center; padding:20px;"><h2 style="color:#94a3b8;">มึงคือใครในแก๊ง?</h2></div>', unsafe_allow_html=True)
        u_name = st.selectbox("", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())), label_visibility="collapsed")
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.my_user = u_name
                st.rerun()
    else:
        # ระบบล็อคชื่อ (Dropdown หายไปแล้วตามข้อ 1)
        me = st.session_state.my_user
        st.markdown(f"<p style='text-align:center; color:#f97316;'>ล็อคระบบในชื่อ: <b>{me}</b></p>", unsafe_allow_html=True)
        
        if me in history:
            target = history[me]
            size = INITIAL_MEMBERS.get(target, "N/A")
            st.markdown(f"""
                <div class="victim-reveal">
                    <p style="color:#8b949e; letter-spacing:2px;">เตรียมชุดให้เพื่อนคนนี้...</p>
                    <div class="victim-name">{target}</div>
                    <div class="victim-box">
                        <p style="color:#f97316; font-weight:600; margin-bottom:5px;">อย่าลืมไปหาชุดมาให้เพื่อนคนนี้ใส่!</p>
                        <p style="color:#8b949e; font-size:0.9rem;">คัดมาเเบบที่ใส่เเล้วลงสระได้เเต่หน้าต้องร้องไห้</p>
                        <p style="color:white; margin-top:15px; font-weight:700; font-size:1.5rem;">ไซส์เสื้อ: {size}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; padding:40px;"><h1 style="font-size:5rem;">🎁</h1><p>พร้อมจะหาเหยื่อหรือยัง?</p></div>', unsafe_allow_html=True)
            if st.button("สุ่มหาเหยื่อเดียวนี้!"):
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
        
        st.markdown("---")
        # Logout Admin-Only
        with st.expander("🛠️ Admin Logout (เฉพาะแอดมินเท่านั้น)"):
            lo_pw = st.text_input("กรอกรหัสแอดมินเพื่อ Logout", type="password", key="lo_pw")
            if st.button("Logout"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.my_user = None
                    st.rerun()
                else:
                    st.error("รหัสไม่ถูกต้องจ่ะแม่!")

# --- TAB: ADMIN ---
with tab_admin:
    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    admin_pw = st.text_input("รหัสผ่านแอดมิน", type="password", key="admin_main_pw")
    
    if admin_pw == ADMIN_PASSWORD:
        # ข้อ 2: Summary 0/18
        count = len(history)
        total = len(INITIAL_MEMBERS)
        st.markdown(f"""
            <div class="summary-badge">
                <span style="color:#8b949e;">ความคืบหน้าการจับฉลาก</span><br>
                <span style="font-size:2rem; font-weight:800; color:#f97316;">{count} / {total}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### ❌ ตั้งค่าคู่ห้าม (แฟนกัน)")
        c1, c2 = st.columns(2)
        ex1 = c1.selectbox("คนที่ 1", sorted(INITIAL_MEMBERS.keys()), key="ex1")
        ex2 = c2.selectbox("คนที่ 2", sorted(INITIAL_MEMBERS.keys()), key="ex2")
        if st.button("บันทึกคู่ห้าม"):
            requests.get(f"{SCRIPT_URL}?giver={ex1}&receiver={ex2}&mode=excl")
            st.success("บันทึกคู่ห้ามเรียบร้อยจ้า")
            st.cache_data.clear()
        
        st.write("---")
        if st.checkbox("แอบดูโพยลับทั้งหมด"):
            st.dataframe(pd.DataFrame([{"Giver": k, "Receiver": v} for k, v in history.items()]))
    st.markdown('</div>', unsafe_allow_html=True)