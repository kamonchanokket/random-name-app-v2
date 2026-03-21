import streamlit as st
import pandas as pd
import random
import requests

# --- 1. CONFIG & INITIAL DATA ---
# รายชื่อ 18 คนและไซส์เสื้อ (แหล่งข้อมูลเดียวที่เชื่อถือได้)
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- ต้องแก้ URL 3 จุดนี้ให้เป็นของคุณ ---
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"


# --- 2. MODERN UI DESIGN (CSS) ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; }
    .stApp { background: radial-gradient(circle at top right, #1e293b, #020617); color: white; }
    
    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 20px;
        text-align: center;
    }
    
    /* Custom Button */
    .stButton>button {
        background: linear-gradient(90deg, #f97316, #d946ef);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(249, 115, 22, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (Fast Cache) ---
@st.cache_data(ttl=60)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        history = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked = df_a['Receiver'].astype(str).tolist()
        excls = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return history, picked, excls
    except:
        return {}, [], []

# --- 4. APP LOGIC ---
if 'my_user' not in st.session_state:
    st.session_state.my_user = None

history, already_picked, exclusion_list = load_data()

st.markdown('<h1 style="text-align:center; font-weight:800;">🚌 นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)

if st.session_state.my_user is None:
    # --- LOGIN PAGE ---
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("ยินดีต้อนรับ! กรุณายืนยันตัวตน")
        u_select = st.selectbox("เลือกชื่อของคุณ", ["-- โปรดเลือก --"] + sorted(list(INITIAL_MEMBERS.keys())))
        if st.button("เข้าสู่ระบบ"):
            if u_select != "-- โปรดเลือก --":
                st.session_state.my_user = u_select
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- DASHBOARD PAGE ---
    current_user = st.session_state.my_user
    st.markdown(f'<p style="text-align:right;">สวัสดี, <b>{current_user}</b> | <small><a href="javascript:window.location.reload()" style="color:#94a3b8; text-decoration:none;">รีเฟรช</a></small></p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if current_user in history:
        # เคยสุ่มไปแล้ว: ดึงจาก History ใน Sheet มาแมตช์กับ Size ในโค้ด
        target = history[current_user]
        size = INITIAL_MEMBERS.get(target, "ไม่ทราบไซส์")
        st.balloons()
        st.markdown(f"<h3>เหยื่อของคุณคือ</h3>")
        st.markdown(f"<h1 style='font-size:4rem; color:#f97316; margin:0;'>{target}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.5rem; opacity:0.8;'>ไซส์เสื้อ: {size}</p>", unsafe_allow_html=True)
    else:
        # ยังไม่เคยสุ่ม: แสดงปุ่มสุ่ม
        st.write("คุณยังไม่ได้ทำการสุ่มเหยื่อ...")
        if st.button("🔥 เริ่มการสุ่มตอนนี้!"):
            # 1. กรองคนที่ไม่ใช่ตัวเอง และยังไม่ถูกใครสุ่ม
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != current_user and n not in already_picked]
            
            # 2. กรองคู่ห้าม (Anti-Fan)
            for p1, p2 in exclusion_list:
                if current_user == p1 and p2 in candidates: candidates.remove(p2)
                if current_user == p2 and p1 in candidates: candidates.remove(p1)
            
            if candidates:
                result = random.choice(candidates)
                # บันทึกเงียบๆ ลง Sheet
                requests.get(f"{SCRIPT_URL}?giver={current_user}&receiver={result}&mode=assign")
                # เคลียร์แคชเพื่อให้โหลดข้อมูลใหม่ทันที
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("ขออภัย! ไม่เหลือรายชื่อที่สุ่มได้ (หรือคุณติดกฎคู่ห้าม)")
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.my_user = None
        st.rerun()

# --- 5. ADMIN PANEL (คู่ห้าม) ---
with st.sidebar:
    st.markdown("### 🛠️ ระบบจัดการ")
    if st.text_input("Admin Password", type="password") == "qwertyuiop[]asdfghjkl":
        st.markdown("---")
        st.write("❌ **เพิ่มคู่ห้าม (แฟนกัน)**")
        f1 = st.selectbox("คนแรก", sorted(INITIAL_MEMBERS.keys()), key="f1")
        f2 = st.selectbox("คนที่สอง", sorted(INITIAL_MEMBERS.keys()), key="f2")
        if st.button("บันทึกคู่ห้าม"):
            requests.get(f"{SCRIPT_URL}?giver={f1}&receiver={f2}&mode=excl")
            st.success("บันทึกคู่ห้ามสำเร็จ!")
            st.cache_data.clear()
        
        if st.button("ดูรายชื่อทั้งหมด"):
            st.write(history)