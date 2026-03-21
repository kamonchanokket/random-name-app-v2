import streamlit as st
import pandas as pd
import random
import requests

# --- 1. ข้อมูลหลัก (Logic เริ่ดห้ามหาย!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: URL Google Sheets (อย่าลืมเช็คของตัวเองนะจ๊ะแม่)
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. THE ULTIMATE UI (CSS) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; color: white; text-align: center; }
    .stApp { background-color: #0d1117; }

    /* ปรับแต่ง Tabs ให้ Center และเส้นขีดเดียว (ข้อ 1 & 3) */
    .stTabs [data-baseweb="tab-list"] {
        display: flex; justify-content: center; background-color: transparent;
        border-bottom: 1px solid #30363d; gap: 30px; margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: transparent; border: none; color: #8b949e; font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #f97316 !important; border-bottom: 3px solid #f97316 !important;
    }

    /* กล่องข้อความและ Input (ข้อ 5) - ขาวสะอาดตาตัวหนังสือดำ */
    .stSelectbox div[data-baseweb="select"], .stTextInput input {
        background-color: #ffffff !important; color: #000000 !important;
        border-radius: 12px !important; font-weight: 600 !important; height: 45px;
    }
    label { color: #f97316 !important; font-size: 1.2rem !important; font-weight: 800 !important; }

    /* Mascot & Victim Reveal (ข้อ 2) */
    .ghost-box { font-size: 100px; margin: 10px 0; }
    .victim-name { font-size: 5.5rem; font-weight: 800; color: #fce7bc; text-shadow: 0 0 25px rgba(252, 231, 188, 0.4); margin: 10px 0; }
    .victim-box { background-color: #1a1515; border: 1px solid #3d3030; border-radius: 25px; padding: 30px; max-width: 550px; margin: 20px auto; }

    /* ปุ่ม Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; max-width: 320px;
        height: 3.5rem; font-size: 1.2rem;
    }
    
    /* Logout Style (ข้อ 4) - ตัวเล็กๆ เทาๆ ไม่แย่งซีน */
    .logout-section { margin-top: 60px; opacity: 0.5; font-size: 0.8rem; }
    .logout-section:hover { opacity: 1; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOAD ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        return dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str))), df_a['Receiver'].astype(str).tolist(), list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
    except: return {}, [], []

history, already_picked, exclusion_list = load_data()

# Session States
if 'my_user' not in st.session_state: st.session_state.my_user = None
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False

# --- 4. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem; margin-top:10px;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)

tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

# --- TAB: DRAW (หน้าสุ่ม) ---
with tab_draw:
    if st.session_state.my_user is None:
        st.markdown('<div class="ghost-box">👻</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#fce7bc;">เลือกชื่อตัวเองด่วน!</h3>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.my_user = u_name
                st.rerun()
    else:
        me = st.session_state.my_user
        if me in history:
            target = history[me]
            size = INITIAL_MEMBERS.get(target, "N/A")
            st.markdown(f"""
                <div class="victim-reveal">
                    <p style="color:#8b949e; letter-spacing:3px;">เหยื่อของคุณคือ...</p>
                    <div class="victim-name">{target}</div>
                    <div class="victim-box">
                        <p style="color:#f97316; font-size:1.5rem; font-weight:800;">ไซส์เสื้อ: {size}</p>
                        <hr style="border: 0.5px solid #3d3030; margin: 20px 0;">
                        <p style="color:#fce7bc; font-style:italic;">"คัดมาแบบที่ใส่แล้วต้องร้องไห้ แต่ต้องใส่ทั้งคืนนะจ้ะ!"</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="ghost-box">😜</div>', unsafe_allow_html=True)
            st.write(f"สวัสดีจ๊ะ **{me}** พร้อมจะแกงเพื่อนหรือยัง?")
            if st.button("สุ่มหาเหยื่อเดี๋ยวนี้!"):
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
        
        # Logout Admin-Only (ข้อ 4)
        st.markdown('<div class="logout-section">', unsafe_allow_html=True)
        with st.expander("Admin Logout (ล็อคชื่อไว้แล้วเพื่อความปลอดภัย)"):
            lo_pw = st.text_input("ใส่รหัสแอดมินเพื่อ Logout", type="password", key="lo_pw")
            if st.button("ยืนยัน Logout"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.my_user = None
                    st.rerun()
                else:
                    st.error("รหัสผิดจ่ะแม่!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: ADMIN (หน้าจัดการ) ---
with tab_admin:
    if not st.session_state.admin_authenticated:
        st.markdown('<div style="padding:40px;">', unsafe_allow_html=True)
        ad_input = st.text_input("รหัสผ่านแอดมิน (ตาดีๆ นะแม่นะ)", type="password")
        if st.button("เข้าสู่ระบบแอดมิน"):
            if ad_input == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("รหัสผิดจ่ะแม่!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        count = len(history)
        total = len(INITIAL_MEMBERS)
        st.markdown(f"""
            <div style="background:rgba(249,115,22,0.1); padding:20px; border-radius:20px; border:1px solid #f97316; margin-bottom:20px;">
                <h3 style="margin:0; color:#8b949e;">ความคืบหน้าการจับสลาก</h3>
                <h1 style="margin:0; color:#f97316; font-size:3rem;">{count} / {total} คน</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### ❌ ตั้งค่าคู่รักต้องห้าม")
        c1, c2 = st.columns(2)
        ex1 = c1.selectbox("คนที่ 1", sorted(INITIAL_MEMBERS.keys()), key="ex1")
        ex2 = c2.selectbox("คนที่ 2", sorted(INITIAL_MEMBERS.keys()), key="ex2")
        if st.button("บันทึกคู่ห้าม"):
            requests.get(f"{SCRIPT_URL}?giver={ex1}&receiver={ex2}&mode=excl")
            st.success(f"ล็อค {ex1} กับ {ex2} เรียบร้อย!")
            st.cache_data.clear()
            st.rerun()
            
        # ข้อ 6: ตารางลิสต์คู่ห้าม
        if exclusion_list:
            st.write("---")
            st.write("### 📋 รายชื่อคู่ห้ามที่บันทึกไว้")
            ex_df = pd.DataFrame(exclusion_list, columns=["ห้ามคนนี้", "สุ่มเจอคนนี้"])
            st.table(ex_df)

        st.write("---")
        if st.checkbox("แอบดูโพยลับ (ระวังคนข้างหลัง!)"):
            st.dataframe(pd.DataFrame([{"ผู้ให้": k, "ผู้รับ": v} for k, v in history.items()]))
            
        if st.button("ออกจากระบบแอดมิน"):
            st.session_state.admin_authenticated = False
            st.rerun()