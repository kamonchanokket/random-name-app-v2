import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- 1. CONFIG & INITIAL DATA (รายชื่อ 18 คนและไซส์เสื้อ ห้ามลบ!) ---
# ใส่ URL ของ Google Sheet ที่แชร์แบบ "Anyone with the link can Edit" ตรงนี้
SHEET_URL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/edit#gid=0"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"

# ข้อมูลตั้งต้นที่อยู่ในระบบ (ไม่ต้องคีย์ใหม่)
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 2. UI STYLE (Modern Glassmorphism) ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Kanit', sans-serif; background-color: #020617; color: white; }
    .stApp { background: radial-gradient(circle at top right, #1e293b, #020617); }
    .glass-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
        border-radius: 2rem; padding: 2.5rem; border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em;
        background: linear-gradient(90deg, #f97316, #d946ef);
        color: white !important; font-weight: 800; border: none;
    }
    .status-badge { background: #f97316; padding: 5px 15px; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNECTION & DATA FETCHING ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_data():
    try:
        # อ่านข้อมูลจาก Tab 'Assignments' และ 'Exclusions' ตามที่คุณมี
        df_assign = conn.read(spreadsheet=SHEET_URL, worksheet="Assignments")
        df_excl = conn.read(spreadsheet=SHEET_URL, worksheet="Exclusions")
        return df_assign, df_excl
    except:
        # กรณี Sheet ยังว่างเปล่าให้สร้าง DataFrame เปล่าที่มีหัวตารางตามที่คุณกำหนด
        return pd.DataFrame(columns=['Giver', 'Receiver']), pd.DataFrame(columns=['P1', 'P2'])

df_assign, df_excl = get_all_data()

# แปลงข้อมูลจาก Sheet เป็น Dictionary และ List เพื่อใช้ใน Logic
current_assignments = dict(zip(df_assign['Giver'].dropna(), df_assign['Receiver'].dropna()))
exclusion_pairs = list(zip(df_excl['P1'].dropna(), df_excl['P2'].dropna()))

# --- 4. MAIN APP LOGIC ---
st.markdown('<h1 style="text-align: center; background: linear-gradient(to right, #f97316, #d946ef); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 800; margin-bottom:1rem;">นครนายก นาใจ</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎯 สุ่มเหยื่อ", "🔑 แอดมินจัดการ"])

# --- TAB 1: หน้าสำหรับสมาชิกสุ่มเหยื่อ ---
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if 'my_user' not in st.session_state:
        st.subheader("🚌 ยืนยันตัวตนก่อนสุ่ม")
        all_names = sorted(list(INITIAL_MEMBERS.keys()))
        u_name = st.selectbox("เลือกชื่อของคุณ", ["-- เลือกชื่อ --"] + all_names)
        if u_name != "-- เลือกชื่อ --" and st.button("เข้าสู่ระบบ"):
            st.session_state.my_user = u_name
            st.rerun()
    else:
        me = st.session_state.my_user
        st.write(f"สวัสดีคุณ: **{me}**")
        
        # ล็อกผล: ถ้าใน Google Sheet มีชื่อเราเป็น Giver แล้ว ให้แสดงผลเดิมทันที
        if me in current_assignments:
            target = current_assignments[me]
            st.balloons()
            st.markdown(f"""
                <div style="text-align: center; padding: 2rem; border: 2px solid #f97316; border-radius: 20px; background: rgba(249,115,22,0.1);">
                    <p style="color: #94a3b8; margin:0;">เหยื่อของคุณคือ...</p>
                    <h1 style="font-size: 4.5rem; color: white; margin: 10px 0;">{target}</h1>
                    <div style="margin-top:10px;"><span class="status-badge">SIZE: {INITIAL_MEMBERS.get(target)}</span></div>
                </div>
            """, unsafe_allow_html=True)
            st.info("🔒 ผลการสุ่มถูกบันทึกใน Google Sheet แล้ว ไม่สามารถเปลี่ยนได้")
        else:
            if st.button("🔥 เริ่มสุ่มเหยื่อ!"):
                # รายชื่อคนที่ถูกสุ่มไปแล้ว
                assigned_receivers = list(current_assignments.values())
                # รายชื่อคนที่มีสิทธิ์ถูกสุ่ม (ไม่ใช่ตัวเอง และยังไม่ถูกใครสุ่ม)
                candidates = [n for n in INITIAL_MEMBERS.keys() if n != me and n not in assigned_receivers]
                
                # Anti-Fan Logic (กรองคู่ห้ามสุ่มเจอกันจาก Tab Exclusions)
                for p1, p2 in exclusion_pairs:
                    if me == p1 and p2 in candidates: candidates.remove(p2)
                    if me == p2 and p1 in candidates: candidates.remove(p1)
                
                if not candidates:
                    st.error("ไม่เหลือใครให้คุณสุ่มแล้ว หรืออาจติดกฎคู่ห้าม กรุณาติดต่อแอดมิน")
                else:
                    with st.spinner('กำลังเฟ้นหาเหยื่อ...'):
                        time.sleep(1.5)
                        target = random.choice(candidates)
                        # บันทึกผลลง Google Sheet ทันที
                        new_data = pd.DataFrame([{"Giver": me, "Receiver": target}])
                        updated_assign = pd.concat([df_assign, new_data], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="Assignments", data=updated_assign)
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: หน้าสำหรับแอดมินจัดการระบบ ---
with tab2:
    admin_pw = st.text_input("กรอกรหัสผ่านแอดมิน", type="password")
    if admin_pw == ADMIN_PASSWORD:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # 1. แสดงสรุปผลการสุ่ม (Summary)
        st.subheader("📊 สรุปความคืบหน้า")
        col1, col2 = st.columns(2)
        col1.metric("สุ่มไปแล้ว", f"{len(current_assignments)} คน")
        col2.metric("คงเหลือ", f"{len(INITIAL_MEMBERS) - len(current_assignments)} คน")
        
        st.write("**ตารางรายชื่อผู้ที่สุ่มแล้ว:**")
        st.dataframe(df_assign, use_container_width=True)

        # 2. จัดการคู่ห้าม (Exclusions)
        st.write("---")
        st.subheader("❌ ตั้งค่าคู่ห้าม (Anti-Fan)")
        all_m = sorted(list(INITIAL_MEMBERS.keys()))
        c1, c2 = st.columns(2)
        p1_ex = c1.selectbox("คนแรก", all_m, key="p1_admin")
        p2_ex = c2.selectbox("คนที่สอง", all_m, key="p2_admin")
        
        if st.button("บันทึกคู่ห้ามลง Google Sheet"):
            if p1_ex != p2_ex:
                new_exclusion = pd.DataFrame([{"P1": p1_ex, "P2": p2_ex}])
                updated_excl = pd.concat([df_excl, new_exclusion], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, worksheet="Exclusions", data=updated_excl)
                st.success(f"บันทึกกฎ: {p1_ex} ห้ามคู่กับ {p2_ex} แล้ว!")
                st.rerun()
            else:
                st.warning("กรุณาเลือกชื่อที่ต่างกัน")

        # 3. เพิ่มสมาชิกใหม่ (นอกเหนือจาก 18 คนหลัก)
        st.write("---")
        st.subheader("➕ เพิ่มสมาชิกใหม่/แก้ไขไซส์")
        new_name = st.text_input("ชื่อเล่น")
        new_size = st.text_input("ไซส์เสื้อ")
        if st.button("เพิ่มเพื่อนเข้ากองสุ่ม"):
            if new_name:
                INITIAL_MEMBERS[new_name] = new_size
                st.success(f"เพิ่มคุณ {new_name} เรียบร้อย (ข้อมูลจะอยู่เฉพาะในรอบการใช้งานนี้)")
        
        # 4. ปุ่มล้างข้อมูลการสุ่ม (Reset)
        st.write("---")
        if st.button("🚨 ล้างข้อมูลการสุ่มทั้งหมด (Reset Assignments)", type="primary"):
            # ลบข้อมูลใน Tab Assignments ให้เหลือแต่หัวตาราง
            reset_df = pd.DataFrame(columns=['Giver', 'Receiver'])
            conn.update(spreadsheet=SHEET_URL, worksheet="Assignments", data=reset_df)
            st.warning("ล้างข้อมูลการสุ่มใน Google Sheet เรียบร้อยแล้ว")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# ปุ่ม Logout สำหรับสมาชิก
if 'my_user' in st.session_state:
    if st.sidebar.button("ออกจากระบบผู้ใช้"):
        st.session_state.clear()
        st.rerun()