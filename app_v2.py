import streamlit as st
import pandas as pd
import random
import requests

# --- 1. ข้อมูล 18 คนและไซส์เสื้อ (LOGIC ห้ามหาย!) ---
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว", "พี่มิว": "44 - 46 นิ้ว", "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL", "แมน": "50 - 52 นิ้วมั้ง 3XL", "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว", "วาย": "44-46", "แพร": "44-46", "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว", "บอส": "44 - 46 นิ้ว", "นุ่น": "44-46",
    "จิน": "46-48", "อู๋": "44 - 46 นิ้ว", "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว", "กี้": "40 นิ้ว"
}

# --- 2. CONFIG การเชื่อมต่อ (ใช้ URL จาก Apps Script ของคุณ) ---
# URL Sheet ที่ Publish เป็น CSV (ต้องแก้ gid ให้ตรงกับแต่ละ Tab)
CSV_ASSIGN = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=0"
CSV_EXCL = "https://docs.google.com/spreadsheets/d/16ehsojCaRyoD81BFOBqOIGKPpZzTp8oRAOy8cqmG1DI/export?format=csv&gid=1434640984"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-iLPmTTnwL88lxuo9D8l_gwOZTTaxLdDJwOLdiSgzEpSXUdDx_OBGyuygugH88eDt/exec"

st.set_page_config(page_title="นครนายก นาใจ 2026", page_icon="🚌")

# --- 3. LOGIC อ่าน/เขียน ข้อมูล ---
def load_data():
    try:
        df_a = pd.read_csv(CSV_ASSIGN)
        df_e = pd.read_csv(CSV_EXCL)
        assigns = dict(zip(df_a['Giver'], df_a['Receiver']))
        excls = list(zip(df_e['P1'], df_e['P2']))
        return assigns, excls
    except:
        return {}, []

def save_to_sheet(giver, receiver, mode="assign"):
    # ส่งไปที่ Apps Script (ถ้าเป็น assign บันทึกคู่สุ่ม, ถ้าเป็น excl บันทึกคู่ห้าม)
    requests.get(f"{SCRIPT_URL}?giver={giver}&receiver={receiver}&mode={mode}")

# --- 4. MAIN UI ---
st.title("🚌 นครนายก นาใจ 2026")
current_assigns, exclusion_list = load_data()

tab1, tab2 = st.tabs(["🎯 สุ่มเหยื่อ", "🔑 แอดมินจัดการ"])

with tab1:
    user = st.selectbox("เลือกชื่อของคุณ", ["-- เลือกชื่อ --"] + sorted(list(INITIAL_MEMBERS.keys())))
    
    if user != "-- เลือกชื่อ --":
        if user in current_assigns:
            target = current_assigns[user]
            st.success(f"คุณสุ่มได้: {target} (Size: {INITIAL_MEMBERS.get(target)})")
        else:
            if st.button("🔥 เริ่มสุ่มเหยื่อ!"):
                already_picked = list(current_assigns.values())
                # กรอง: ไม่ใช่ตัวเอง และยังไม่ถูกใครสุ่ม
                candidates = [n for n in INITIAL_MEMBERS.keys() if n != user and n not in already_picked]
                
                # --- LOGIC คู่ห้าม (แฟนกันห้ามสุ่มเจอกัน) ---
                for p1, p2 in exclusion_list:
                    if user == p1 and p2 in candidates: candidates.remove(p2)
                    if user == p2 and p1 in candidates: candidates.remove(p1)
                
                if candidates:
                    result = random.choice(candidates)
                    save_to_sheet(user, result, mode="assign")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("ไม่เหลือใครให้สุ่มแล้ว หรือติดกฎคู่ห้าม!")

with tab2:
    if st.text_input("รหัสผ่านแอดมิน", type="password") == "qwertyuiop[]asdfghjkl":
        st.subheader("❌ ตั้งค่าคู่ห้าม (แฟนกัน)")
        c1, c2 = st.columns(2)
        fan1 = c1.selectbox("คนแรก", INITIAL_MEMBERS.keys(), key="f1")
        fan2 = c2.selectbox("คนที่สอง", INITIAL_MEMBERS.keys(), key="f2")
        if st.button("บันทึกคู่ห้าม"):
            save_to_sheet(fan1, fan2, mode="excl")
            st.success("บันทึกคู่ห้ามลง Sheet แล้ว!")
            st.rerun()
            
        st.write("---")
        st.write("ผลการสุ่มปัจจุบัน:")
        st.table(pd.DataFrame([{"Giver": k, "Receiver": v} for k, v in current_assigns.items()]))