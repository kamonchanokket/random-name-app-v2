import streamlit as st
import pandas as pd
import random
import requests

# --- 1. CONFIG & DATA SOURCE (Logic เริ่ดห้ามขาด ห้ามหาย!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# CONFIG: URL Google Sheets (แก้ให้เป็นของคุณนะจ๊ะแม่)
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# --- 2. CSS เนี๊ยบระดับ QC (ขาว-ดำ 100% Contrast ตามใจแม่) ---
st.set_page_config(page_title="นครนายก นาใจ V.Final Pro", page_icon="👻", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    
    /* สไตล์หลัก */
    html, body, [class*="st-"] {{ font-family: 'Kanit', sans-serif; color: white; text-align: center; }}
    .stApp {{ background-color: #0d1117; }}

    /* >>> บังคับแก้ช่อง Input/Selectbox ทั้งแอปให้เป็นพื้นขาว-ตัวดำเข้ม (QC เนี๊ยบ) <<< */
    div[data-baseweb="select"] div[data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #ced4da !important;
    }}
    div[data-baseweb="select"] span {{
        color: #000000 !important; /* ตัวหนังสือดำเข้ม */
        font-weight: 700 !important;
    }}
    .stTextInput input, .stSelectbox input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }}
    /* แก้ไขลาเบล */
    label {{ color: #f97316 !important; font-weight: 800 !important; font-size: 1.2rem !important; margin-bottom: 5px !important; }}

    /* Tabs Style */
    .stTabs [data-baseweb="tab-list"] {{ display: flex; justify-content: center; border-bottom: 1px solid #30363d; gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; background-color: transparent; border: none; color: #8b949e; }}
    .stTabs [aria-selected="true"] {{ color: #f97316 !important; border-bottom: 3px solid #f97316 !important; }}

    /* Victim Card Style */
    .victim-reveal {{ text-align: center; padding: 20px 10px; }}
    .victim-name {{ font-size: 5rem; font-weight: 800; color: #fce7bc; margin: 15px 0; text-shadow: 0 0 20px rgba(252, 231, 188, 0.3); }}
    .victim-box {{ background-color: #1a1515; border: 1px solid #3d3030; border-radius: 20px; padding: 25px; margin: 20px auto; max-width: 500px; }}

    /* ปุ่ม Gradient */
    .stButton>button {{
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important; border-radius: 15px !important;
        color: white !important; font-weight: 800 !important; width: 100%; max-width: 320px; height: 3.5rem; font-size: 1.2rem;
    }
    
    /* Logout Section (ข้อ 4 เดิม) */
    .logout-footer {{ margin-top: 100px; padding-top: 15px; border-top: 1px solid #30363d; }}
    .logout-text {{ color: #4b5563; font-size: 0.8rem; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PERSISTENT DATA CHECK (Logic Guardian & Anti-Refresh Lock) ---
@st.cache_data(ttl=1) # โหลดแทบจะ Realtime กันเหนียว
def get_verified_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        hist = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excls = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return hist, picked, excls
    except: return {}, [], []

history, already_picked, exclusion_list = get_verified_data()

# Session for Identity
if 'verified_user' not in st.session_state: st.session_state.verified_user = None

# --- 4. RENDER MAIN APP ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem; margin-top:15px; margin-bottom:0;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#8b949e; font-size:1rem; margin-bottom:20px;">Secret Buddy "เสื้อที่มึงไม่อยากใส่แต่ต้องใส่"</p>', unsafe_allow_html=True)

tab_draw, tab_admin = st.tabs(["✨ จับคู่เดี๋ยวนี้", "🛠️ จัดการแก๊ง"])

# --- TAB: DRAW (สุ่มหาเหยื่อ) ---
with tab_draw:
    # ด่านแรก: ยืนยันตัวตน (Persistent Check)
    if st.session_state.verified_user is None:
        st.markdown('<div style="font-size:100px; margin-top:10px;">👻</div>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.verified_user = u_name
                st.rerun()
    else:
        # ล็อค Session เรียบร้อย
        me = st.session_state.verified_user
        
        # เช็คว่าชื่อ me เคยสุ่มไปยัง (จาก Database จริง)
        if me in history:
            # กรณีสุ่มแล้ว: โชว์ผลทันที ล็อคหน้านี้ไว้ (กันแอบดูเพื่อน)
            target = history[me]
            size = INITIAL_MEMBERS.get(target, "ไม่ทราบไซส์")
            st.balloons()
            st.markdown(f"""
                <div class="victim-reveal">
                    <p style="color:#8b949e;">เตรียมชุดให้เพื่อนคนนี้...</p>
                    <div class="victim-name">{target}</div>
                    <div class="victim-box">
                        <p style="color:#f97316; font-weight:800; font-size:1.5rem;">ไซส์เสื้อ: {size}</p>
                        <p style="color:#8b949e; font-size:0.9rem; margin-top:10px;">"คัดมาแบบที่มันเห็นแล้วต้องร้องไห้ แต่ต้องใส่ลงสระ!"</p>
                        <p style="color:#4b5563; font-size:0.8rem; margin-top:15px;">(ล็อคระบบในชื่อ {me})</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # กรณีรอสุ่ม
            st.markdown(f"<h3>สวัสดีจ๊ะคุณ {me} 👋</h3>", unsafe_allow_html=True)
            if st.button("🔥 เริ่มสุ่มหาเหยื่อเดียวนี้!"):
                # Logic การสุ่ม (ไม่ซ้ำ, ไม่ใช่ตัวเอง, ไม่ใช่แฟน)
                candidates = [n for n in INITIAL_MEMBERS.keys() if n != me and n not in already_picked]
                
                # Logic คู่ห้าม (Exclusion)
                for p1, p2 in exclusion_list:
                    if me == p1 and p2 in candidates: candidates.remove(p2)
                    if me == p2 and p1 in candidates: candidates.remove(p1)
                
                if candidates:
                    with st.spinner('กำลังเฟ้นหาเหยื่อ...'):
                        res = random.choice(candidates)
                        # เขียนข้อมูลลง Sheet ผ่าน Apps Script (No Key JSON!)
                        requests.get(f"{SCRIPT_URL}?giver={me}&receiver={res}&mode=assign")
                        st.cache_data.clear() # ล้าง Cache เพื่อดึงข้อมูลใหม่
                        st.rerun()
                else:
                    st.error("ขออภัย! ไม่เหลือชื่อที่สุ่มได้ (หรือคุณติดกฎคู่ห้าม)")

        # ส่วน Logout (ข้อ 2: แก้ปุ่มเนี๊ยบ Admin Only)
        st.markdown('<div class="logout-footer">', unsafe_allow_html=True)
        st.markdown('<p class="logout-text">ระบบล็อคชื่อไว้แล้ว หากต้องการเปลี่ยนกรุณาติดต่อแอดมิน</p>', unsafe_allow_html=True)
        with st.expander("🛠️ Admin Logout"):
            lo_pw = st.text_input("รหัสแอดมิน", type="password", key="lo_pw")
            if st.button("ยืนยัน Logout"):
                if lo_pw == ADMIN_PASSWORD:
                    st.session_state.verified_user = None
                    st.rerun()
                else:
                    st.error("รหัสไม่ถูกต้องจ่ะแม่!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: ADMIN (จัดการแก๊ง) ---
with tab_admin:
    st.markdown('<div style="text-align:center; padding:20px;">', unsafe_allow_html=True)
    admin_pw = st.text_input("รหัสผ่านแอดมิน", type="password", key="admin_page_pw")
    if admin_pw == ADMIN_PASSWORD:
        st.write(f"### สถิติล่าสุด: สุ่มไปแล้ว {len(history)} / {len(INITIAL_MEMBERS)} คน")
        
        st.write("---")
        st.write("### 🚫 ตั้งค่าคู่รักต้องห้าม (แฟนกัน)")
        c1, c2 = st.columns(2)
        ex1 = c1.selectbox("คนที่ 1", sorted(INITIAL_MEMBERS.keys()), key="ex1")
        ex2 = c2.selectbox("คนที่ 2", sorted(INITIAL_MEMBERS.keys()), key="ex2")
        if st.button("ล็อคคู่ห้าม"):
            requests.get(f"{SCRIPT_URL}?giver={ex1}&receiver={ex2}&mode=excl")
            st.success(f"บันทึกคู่ห้าม {ex1} กับ {ex2} แล้วจ้า")
            st.cache_data.clear()
            st.rerun()
            
        # ตารางคู่ห้าม (ข้อ 6 เดิม)
        if exclusion_list:
            st.write("📋 **รายชื่อคู่รักต้องห้ามปัจจุบัน**", pd.DataFrame(exclusion_list, columns=["ห้ามคนนี้", "สุ่มเจอคนนี้"]))

        st.write("---")
        if st.checkbox("แอบดูโพยลับ (ระวังคนข้างหลัง!)"):
            st.dataframe(pd.DataFrame([{"ใครให้": k, "ใครรับ": v} for k, v in history.items()]))