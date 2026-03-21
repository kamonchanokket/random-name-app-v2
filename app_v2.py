import streamlit as st
import pandas as pd
import random
import requests
import time

# --- 1. ข้อมูลหลัก (LOGIC เดิม) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# ต้องแก้ URL ให้เป็นของคุณ
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"

# --- 2. CUSTOM CSS (เพื่อหน้าตาแบบรูป 2 และ 11) ---
st.set_page_config(page_title="นครนายก นาใจ", page_icon="🚌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; color: white; }
    .stApp { background-color: #0a0e17; }

    /* ปรับแต่ง Tabs ให้เหมือนรูปเรฟ */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 15px;
        padding: 5px;
        gap: 10px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px;
        background-color: transparent;
        color: #8b949e;
        border: none;
        flex: 1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #f97316 !important; /* สีส้มตามรูป */
    }

    /* Glass Card */
    .main-card {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 25px;
        padding: 40px;
        text-align: center;
        margin-top: 20px;
    }

    /* ปุ่ม Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #f97316, #d946ef) !important;
        border: none !important;
        border-radius: 15px !important;
        height: 3.5rem !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & SESSION ---
@st.cache_data(ttl=10)
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        return dict(zip(df_a['Giver'], df_a['Receiver'])), df_a['Receiver'].tolist(), list(zip(df_e['P1'], df_e['P2']))
    except: return {}, [], []

history, already_picked, exclusion_list = load_data()

# --- 4. UI RENDER ---
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:3rem; margin-bottom:0;">นครนายก <span style="color:#f97316;">นาใจ</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#8b949e; font-style:italic; margin-bottom:20px;">"สุ่มหาเหยื่อ (พร้อมไซส์เสื้อ) ฉบับแอดมินไม่รู้โพย"</p>', unsafe_allow_html=True)

# สร้าง Tab 2 อันข้างบนตามรูป 2
tab_draw, tab_admin = st.tabs(["🎁 จับคู่คนที่เราจะแกง", "⚙️ จัดการแก๊ง"])

# --- TAB 1: สุ่มหาเหยื่อ ---
with tab_draw:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<h1 style="font-size:4rem;">👻</h1>', unsafe_allow_html=True)
    
    u_select = st.selectbox("มึงคือใครในแก๊ง?", ["-- เลือกชื่อตัวเอง --"] + sorted(list(INITIAL_MEMBERS.keys())))
    
    if st.button("สุ่มหาเหยื่อ!", key="btn_draw"):
        if u_select == "-- เลือกชื่อตัวเอง --":
            st.warning("เลือกชื่อตัวเองก่อนไอ้ชาย!")
        elif u_select in history:
            # ถ้าเคยสุ่มแล้ว ให้โชว์ผลเลย
            target = history[u_select]
            size = INITIAL_MEMBERS.get(target, "N/A")
            st.success(f"มึงเคยสุ่มไปแล้ว! เหยื่อคือ: {target} (ไซส์: {size})")
        else:
            # Logic การสุ่ม (ห้ามตัวเอง, ห้ามซ้ำ, ห้ามแฟน)
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != u_select and n not in already_picked]
            for p1, p2 in exclusion_list:
                if u_select == p1 and p2 in candidates: candidates.remove(p2)
                if u_select == p2 and p1 in candidates: candidates.remove(p1)
            
            if candidates:
                res = random.choice(candidates)
                requests.get(f"{SCRIPT_URL}?giver={u_select}&receiver={res}&mode=assign")
                st.balloons()
                st.markdown(f"<h3>เหยื่อของมึงคือ...</h3><h1 style='color:#f97316; font-size:4rem;'>{res}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p>ไซส์เสื้อ: {INITIAL_MEMBERS[res]}</p>", unsafe_allow_html=True)
                st.cache_data.clear()
            else:
                st.error("ไม่เหลือใครให้มึงสุ่มแล้ว (หรือมึงติดกฎคู่ห้าม)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: แอดมิน (ตามรูป 11) ---
with tab_admin:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🔒 แอดมินยืนยันตัวตน")
    pw = st.text_input("รหัสผ่าน", type="password")
    
    if pw == "qwertyuiop[]asdfghjkl":
        st.markdown("---")
        st.write("### ❌ คู่ที่ไม่ควรแกงกันเอง (คู่ห้าม)")
        c1, c2 = st.columns(2)
        ex1 = c1.selectbox("คนแรก", sorted(INITIAL_MEMBERS.keys()), key="ex1")
        ex2 = c2.selectbox("คนที่สอง", sorted(INITIAL_MEMBERS.keys()), key="ex2")
        if st.button("ห้ามสุ่มเจอกัน"):
            requests.get(f"{SCRIPT_URL}?giver={ex1}&receiver={ex2}&mode=excl")
            st.success(f"ล็อคแล้ว! {ex1} จะไม่สุ่มเจอ {ex2}")
            st.cache_data.clear()
        
        st.markdown("---")
        st.write("### 📜 ประวัติการสุ่ม (ความลับ)")
        if st.checkbox("แอบดูโพย"):
            st.write(pd.DataFrame([{"ผู้ให้": k, "ผู้รับ": v} for k, v in history.items()]))
    st.markdown('</div>', unsafe_allow_html=True)