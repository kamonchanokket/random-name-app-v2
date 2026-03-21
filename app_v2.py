import streamlit as st
import pandas as pd
import random
import requests

# --- 1. CONFIG & LOGIC (ย้ำว่า Logic แน่นปึ้กเหมือนเดิม!) ---
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

# --- 2. CSS แก้ไขตามใจแม่ (ข้อ 2 & 3) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="👻", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; color: white; text-align: center; }
    .stApp { background-color: #0d1117; }

    /* ข้อ 3: แก้ Dropdown ให้ขาวเด่น ตัวหนังสือดำเข้ม */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="select"] * {
        color: #000000 !important; /* ตัวหนังสือดำปี๋ */
        font-weight: 700 !important;
    }
    input { color: #000000 !important; }

    /* ปรับแต่ง Tabs ให้สวยขีดเดียว */
    .stTabs [data-baseweb="tab-list"] {
        display: flex; justify-content: center; border-bottom: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        color: #f97316 !important; border-bottom: 3px solid #f97316 !important;
    }

    /* Victim Box */
    .victim-name { font-size: 5rem; font-weight: 800; color: #fce7bc; text-shadow: 0 0 20px rgba(252, 231, 188, 0.3); }
    .victim-box { background-color: #1a1515; border: 1px solid #3d3030; border-radius: 20px; padding: 25px; margin: 20px auto; }
    
    /* ข้อ 2: แก้ปุ่ม Logout ที่มันซ้อนกัน (ล้างของเก่า) */
    .stExpander { background-color: transparent !important; border: none !important; }
    .logout-btn-container { margin-top: 50px; padding: 10px; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA PERSISTENCE (ข้อ 1: แก้บั๊ค Refresh) ---
@st.cache_data(ttl=1) # ดึงสดทุกวินาทีเพื่อกันพลาด
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

# จัดการ Session ให้แม่
if 'user_auth' not in st.session_state: st.session_state.user_auth = None

# --- 4. RENDER ---
st.markdown('<h1 style="font-weight:800; font-size:3.5rem;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
tab_draw, tab_admin = st.tabs(["✨ สุ่มหาเหยื่อ", "🛠️ จัดการแก๊ง"])

with tab_draw:
    # ถ้ายังไม่ได้เลือกชื่อ หรือรีเฟรชมาแล้วชื่อยังไม่อยู่ใน DB
    if st.session_state.user_auth is None:
        st.markdown('<h2 style="font-size:80px;">👻</h2>', unsafe_allow_html=True)
        u_name = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("ยืนยันตัวตน"):
            if u_name != "-- เลือกชื่อตัวเอง --":
                st.session_state.user_auth = u_name
                st.rerun()
    else:
        me = st.session_state.user_auth
        # ข้อ 1: เช็คจาก DB เสมอ ต่อให้รีเฟรช ถ้าเคยสุ่มแล้วต้องเห็นคนเดิม
        if me in history:
            target = history[me]
            st.markdown(f"""
                <p style="color:#8b949e;">เหยื่อของคุณคือ...</p>
                <div class="victim-name">{target}</div>
                <div class="victim-box">
                    <p style="color:#f97316; font-weight:700;">ไซส์เสื้อ: {INITIAL_MEMBERS.get(target, 'N/A')}</p>
                    <p style="color:#fce7bc; font-size:0.9rem;">"คัดมาแบบที่ใส่แล้วต้องร้องไห้ แต่ต้องใส่ทั้งคืนนะจ้ะ!"</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h3>สวัสดีจ๊ะ **{me}**</h3>", unsafe_allow_html=True)
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
        
        # ข้อ 2: แก้ปุ่ม Logout แบบใหม่ ไม่ซ้อน ไม่รก
        st.markdown('<div class="logout-btn-container">', unsafe_allow_html=True)
        with st.expander("ตั้งค่าบัญชี (สำหรับ Logout)"):
            if st.button("ออกจากระบบชื่อนี้"):
                st.session_state.user_auth = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with tab_admin:
    # หน้า Admin เหมือนเดิมจ่ะแม่ เพิ่มปุ่มกดยืนยันชัดๆ
    pw = st.text_input("รหัสผ่านแอดมิน", type="password")
    if st.button("เข้าสู่ระบบแอดมิน") or pw == ADMIN_PASSWORD:
        if pw == ADMIN_PASSWORD:
            st.write(f"### สุ่มไปแล้ว {len(history)} / {len(INITIAL_MEMBERS)} คน")
            # ตารางคู่ห้าม (ข้อ 6 เดิม)
            if exclusion_list:
                st.write("📋 **คู่รักต้องห้าม:**")
                st.table(pd.DataFrame(exclusion_list, columns=["ห้าม", "เจอคนนี้"]))
            
            if st.checkbox("ดูโพยลับ"):
                st.dataframe(pd.DataFrame([{"ให้":k, "รับ":v} for k, v in history.items()]))
        else:
            st.error("รหัสผิดจ่ะแม่!")