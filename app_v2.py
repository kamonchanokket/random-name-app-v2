import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIG & DATA ---
SHEET_ID = "16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI" 
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"  # รหัสเดิมจากไฟล์ v10 ของคุณ

# URL สำหรับดึงข้อมูลจาก Tab ต่างๆ (ต้องระบุ gid ให้ถูกต้อง)
CSV_URL_RESULTS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
EXCLUSION_GID = "1434640984#gid=1434640984"
CSV_URL_EXCLUSIONS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={EXCLUSION_GID}"

MEMBER_DETAILS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 2. UI STYLE ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; background-color: #020617; color: white; }
    .stApp { background: radial-gradient(circle at top right, #1e293b, #020617); }
    .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(20px); border-radius: 2.5rem; padding: 2.5rem; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.5em;
        background: linear-gradient(135deg, #f97316 0%, #d946ef 100%);
        color: white !important; font-weight: 800; font-size: 1.2rem; border: none;
    }
    .admin-card { background: rgba(255, 255, 255, 0.05); border-radius: 1.5rem; padding: 1.5rem; margin-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA FETCHING ---
def load_sheet_data(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

# ดึงข้อมูลล่าสุด
df_results = load_sheet_data(CSV_URL_RESULTS)
df_exclusions = load_sheet_data(CSV_URL_EXCLUSIONS)

current_assignments = dict(zip(df_results['Giver'], df_results['Receiver'])) if not df_results.empty else {}
exclusion_list = list(zip(df_exclusions['P1'], df_exclusions['P2'])) if not df_exclusions.empty else []

# --- 4. MAIN APP ---
st.markdown('<h1 style="text-align: center; color: white; font-size: 3rem; font-weight: 800;">นครนายก <span style="color:#f97316">นาใจ</span></h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎯 สุ่มหาเหยื่อ", "🔑 จัดการแก๊ง"])

# --- TAB 1: หน้าสุ่มสำหรับสมาชิก ---
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if 'my_identity' not in st.session_state:
        st.subheader("🚌 ยืนยันตัวตน")
        user = st.selectbox("คุณคือใคร?", ["-- เลือกชื่อ --"] + sorted(list(MEMBER_DETAILS.keys())))
        if user != "-- เลือกชื่อ --" and st.button("จิ้มเล้ยยยย"):
            st.session_state.my_identity = user
            st.rerun()
    else:
        me = st.session_state.my_identity
        st.write(f"ฮายยยยเพื่อน: **{me}**")
        
        # Logic เช็คว่าสุ่มไปหรือยัง
        if me in current_assignments:
            target = current_assignments[me]
            st.balloons()
            st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: 2px dashed #f97316; border-radius: 20px;">
                    <p style="color: #94a3b8; margin:0;">เหยื่อของคุณคือ...</p>
                    <h1 style="font-size: 4rem; color: white; margin: 10px 0;">{target}</h1>
                    <span style="background: #f97316; padding: 5px 15px; border-radius: 10px; font-weight: bold;">Size: {MEMBER_DETAILS.get(target)}</span>
                </div>
            """, unsafe_allow_html=True)
            st.info("🔒 ล็อกผลแล้ว ห้ามแอบดูคนอื่นนะจ๊ะ")
        else:
            if st.button("🔥 เริ่มสุ่มเหยื่อ!"):
                already_picked = list(current_assignments.values())
                candidates = [n for n in MEMBER_DETAILS.keys() if n != me and n not in already_picked]
                
                # Dynamic Exclusion Logic
                for p1, p2 in exclusion_list:
                    if me == p1 and p2 in candidates: candidates.remove(p2)
                    if me == p2 and p1 in candidates: candidates.remove(p1)
                
                if not candidates:
                    st.error("ไม่มีใครให้สุ่มแล้ว (ติดคู่ห้าม)")
                else:
                    with st.spinner('กำลังสุ่ม...'):
                        time.sleep(1)
                        st.session_state.temp_res = random.choice(candidates)
                        st.rerun()

        if 'temp_res' in st.session_state:
            res = st.session_state.temp_res
            st.success(f"คนที่โดนมึงแกง: {res} (Size: {MEMBER_DETAILS.get(res)})")
            st.warning("⚠️ แคปจอและไปหาชุดให้เพื่อนด้วยหละ")
            if st.button("บรัยยยส์ ขอบคุณที่มาจุ่ม"):
                del st.session_state.temp_res
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: หน้า ADMIN PANEL ---
with tab2:
    if 'is_admin' not in st.session_state:
        pw = st.text_input("กรอกรหัสผ่านแอดมิน", type="password")
        if st.button("ยืนยันรหัสผ่าน"):
            if pw == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("รหัสผิดนะจ๊ะ!")
    else:
        st.write("### 🛠️ ระบบจัดการหลังบ้าน")
        
        # แสดงสถิติการสุ่ม
        col1, col2 = st.columns(2)
        col1.metric("สุ่มไปแล้ว", f"{len(current_assignments)} / {len(MEMBER_DETAILS)}")
        col2.metric("คู่ห้ามปัจจุบัน", f"{len(exclusion_list)} คู่")

        # แสดงรายการคู่ห้ามที่ดึงมาจาก Sheet
        with st.expander("👀 ดูรายชื่อคู่ห้าม (จาก Google Sheet)"):
            if exclusion_list:
                for p1, p2 in exclusion_list:
                    st.text(f"❌ {p1} ห้ามคู่กับ {p2}")
            else:
                st.write("ยังไม่มีคู่ห้ามในระบบ")

        # ปุ่มจัดการ
        st.write("---")
        st.warning("สำหรับการเพิ่ม/ลบชื่อคู่ห้าม ให้ไปจัดการที่หน้า Tab 'Exclusions' ใน Google Sheet โดยตรง")
        
        if st.button("ออกจากระบบแอดมิน"):
            del st.session_state.is_admin
            st.rerun()

# ปุ่ม Logout ของสมาชิก
if 'my_identity' in st.session_state:
    if st.sidebar.button("ออกจากระบบผู้ใช้"):
        st.session_state.clear()
        st.rerun()