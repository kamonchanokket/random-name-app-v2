import streamlit as st
import gspread
import random
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. SETTING & UI STYLE (HTML/CSS) ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Kanit', sans-serif;
        background-color: #020617;
    }
    
    /* สไตล์ Card แก้ว */
    .main-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 2.5rem;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }

    /* ปุ่ม Gradient แบบ Gen Z */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background: linear-gradient(135deg, #f97316 0%, #d946ef 100%);
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 25px -5px rgba(249, 115, 22, 0.5);
        color: white;
    }

    /* ตกแต่ง Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 15px;
        background-color: #0f172a;
        border: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS CONNECTION ---
def get_gs_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # ดึงค่าจาก Streamlit Secrets
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"⚠️ ลืมใส่ Secrets ในหน้า Settings หรือเปล่า?: {e}")
        return None

# --- 3. DATA & LOGIC ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 4. APP INTERFACE ---
st.markdown('<h1 style="text-align: center; color: white;">นครนายก <span style="color: #f97316;">นาใจ</span> 2026</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #94a3b8; font-style: italic;">"หาชุดที่ใส่แล้วโลกต้องจำ!"</p>', unsafe_allow_html=True)

# ระบบจำชื่อผู้ใช้ (Session State)
if 'my_name' not in st.session_state:
    st.session_state.my_name = None

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    if not st.session_state.my_name:
        st.write("👋 **ใครเอ่ย? เลือกชื่อตัวเองก่อนนะ**")
        selected_user = st.selectbox("", ["-- รายชื่อเพื่อน --"] + sorted(list(INITIAL_MEMBERS.keys())), label_visibility="collapsed")
        
        if selected_user != "-- รายชื่อเพื่อน --":
            if st.button("ยืนยันตัวตน"):
                st.session_state.my_name = selected_user
                st.rerun()
    else:
        st.success(f"ยินดีต้อนรับคุณ: **{st.session_state.my_name}**")
        
        if st.button("🚀 กดสุ่มหาเหยื่อ / ดูผลลัพธ์"):
            client = get_gs_client()
            if client:
                try:
                    # ชื่อไฟล์ Google Sheets
                    sheet = client.open("random-name-tracking") 
                    ws_assign = sheet.worksheet("Assignments")
                    ws_excl = sheet.worksheet("Exclusions")
                    
                    data = ws_assign.get_all_records()
                    assignments = {row['giver']: row['receiver'] for row in data if row.get('receiver')}
                    
                    # ถ้าเคยสุ่มไปแล้ว ให้โชว์ผลเดิม
                    if st.session_state.my_name in assignments:
                        target = assignments[st.session_state.my_name]
                        st.balloons()
                        st.markdown(f"""
                            <div style="text-align: center; padding: 2rem; background: rgba(249, 115, 22, 0.1); border-radius: 2rem; border: 2px dashed #f97316;">
                                <p style="color: #94a3b8;">เหยื่อของคุณคือ...</p>
                                <h1 style="color: white; font-size: 4rem; margin: 0;">{target}</h1>
                                <div style="display: inline-block; padding: 0.5rem 1.5rem; background: #f97316; color: white; border-radius: 1rem; font-weight: bold; margin-top: 1rem;">
                                    Size: {INITIAL_MEMBERS.get(target, '-')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        # กรองคนที่ไม่ใช่ตัวเอง และคนที่ยังไม่ถูกเลือก
                        assigned_receivers = list(assignments.values())
                        candidates = [n for n in INITIAL_MEMBERS.keys() if n != st.session_state.my_name and n not in assigned_receivers]
                        
                        # กรอง Exclusion Rules (คู่ห้าม)
                        exclusions = ws_excl.get_all_values()
                        for pair in exclusions:
                            if len(pair) >= 2:
                                p1, p2 = pair[0], pair[1]
                                if st.session_state.my_name == p1 and p2 in candidates: candidates.remove(p2)
                                if st.session_state.my_name == p2 and p1 in candidates: candidates.remove(p1)

                        if not candidates:
                            st.error("❌ ไม่มีใครเหลือให้คุณสุ่มแล้ว!")
                        else:
                            target = random.choice(candidates)
                            # บันทึกลง Google Sheets (หาช่องที่ชื่อเราอยู่ แล้วบันทึก Target ลงคอลัมน์ 2)
                            cell = ws_assign.find(st.session_state.my_name)
                            ws_assign.update_cell(cell.row, 2, target)
                            st.rerun() # รีหน้าเพื่อให้มันโชว์ผลลัพธ์จาก Block ข้างบน
                            
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ไม่ใช่ฉัน? (ล้างข้อมูลเครื่องนี้)", type="secondary"):
            st.session_state.my_name = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #475569; font-size: 0.7rem;">BUILD WITH ❤️ FOR NAKHON NAYOK 2026</p>', unsafe_allow_html=True)