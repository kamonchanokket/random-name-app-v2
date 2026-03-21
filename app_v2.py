import streamlit as st
import pandas as pd
import random
import requests

# --- 1. ข้อมูลหลัก 18 คน (แหล่งอ้างอิงความถูกต้อง) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 2. CONFIG (เปลี่ยน URL เป็นของคุณ) ---
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"

def load_all_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN).dropna(subset=['Giver', 'Receiver'])
        df_e = pd.read_csv(CSV_EXCL).dropna(subset=['P1', 'P2'])
        history = dict(zip(df_a['Giver'].astype(str), df_a['Receiver'].astype(str)))
        picked_list = df_a['Receiver'].astype(str).tolist()
        excls = list(zip(df_e['P1'].astype(str), df_e['P2'].astype(str)))
        return history, picked_list, excls
    except:
        return {}, [], []

# --- 3. SESSION INITIALIZATION (ระบบจำตัวตน) ---
if 'my_identity' not in st.session_state:
    st.session_state.my_identity = None

# --- 4. UI SETUP ---
st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌")
st.title("🚌 นครนายก นาใจ 2026")

history, already_picked, exclusion_list = load_all_data()

# --- 5. LOGIC: การเลือกตัวตน ---
if st.session_state.my_identity is None:
    # หน้าแรก: ให้เลือกชื่อตัวเองเพื่อ Lock Session
    user_select = st.selectbox("คุณคือใคร? (เลือกแล้วเปลี่ยนไม่ได้ในเซสชันนี้)", ["-- เลือกชื่อ --"] + sorted(list(INITIAL_MEMBERS.keys())))
    if st.button("ยืนยันตัวตน"):
        if user_select != "-- เลือกชื่อ --":
            st.session_state.my_identity = user_select
            st.rerun()
else:
    # เมื่อยืนยันตัวตนแล้ว จะล็อคชื่อนั้นไว้เลย
    current_user = st.session_state.my_identity
    st.write(f"สวัสดีคุณ **{current_user}** 👋")
    
    # ปุ่ม Logout เผื่อเข้าผิดคน (แต่อาจจะลบออกก็ได้ถ้ากลัวเพื่อนแอบกด)
    if st.sidebar.button("ไม่ใช่ฉัน? (ออกจากระบบ)"):
        st.session_state.my_identity = None
        st.rerun()

    st.markdown("---")

    # เช็คว่าเคยสุ่มหรือยัง
    if current_user in history:
        target = history[current_user]
        size = INITIAL_MEMBERS.get(target, "ไม่พบข้อมูลไซส์")
        st.balloons()
        st.success(f"คุณสุ่มได้: **{target}**")
        st.info(f"ไซส์เสื้อของ {target} คือ: {size}")
    else:
        if st.button("🔥 เริ่มสุ่มเหยื่อ!"):
            candidates = [n for n in INITIAL_MEMBERS.keys() if n != current_user and n not in already_picked]
            
            # Logic คู่ห้าม (แฟน)
            for p1, p2 in exclusion_list:
                if current_user == p1 and p2 in candidates: candidates.remove(p2)
                if current_user == p2 and p1 in candidates: candidates.remove(p1)
            
            if candidates:
                result = random.choice(candidates)
                # โชว์สดทันที
                st.balloons()
                st.success(f"สุ่มเสร็จแล้ว! คุณได้: **{result}**")
                st.info(f"ไซส์เสื้อคือ: {INITIAL_MEMBERS[result]}")
                # บันทึกเงียบๆ
                requests.get(f"{SCRIPT_URL}?giver={current_user}&receiver={result}&mode=assign")
                # บังคับ rerun เพื่อให้ระบบจำสถานะจาก Sheet ในครั้งหน้า
                st.cache_data.clear() 
            else:
                st.error("ไม่เหลือใครให้สุ่มแล้ว หรือติดกฎคู่ห้าม!")

# --- 6. ADMIN VIEW ---
with st.expander("🔑 แอดมิน"):
    if st.text_input("Password", type="password") == "qwertyuiop[]asdfghjkl":
        st.table(pd.DataFrame([{"ผู้สุ่ม": k, "เหยื่อ": v} for k, v in history.items()]))
