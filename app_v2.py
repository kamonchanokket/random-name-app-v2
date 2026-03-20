from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_v12_fixed"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "1234" # รหัสเข้าหน้า Admin

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"members": {}, "assignments": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# เพิ่ม Default values ให้กับฟังก์ชัน render เพื่อกัน Error ตัวแปรหาย
def render_page(page, **kwargs):
    data = load_data()
    # คำนวณรายชื่อที่เหลืออยู่เสมอ เพื่อให้หน้า Index มีข้อมูลตลอด
    available = [n for n in data["members"].keys() if n not in data["assignments"]]
    return render_template_string(
        HTML_TEMPLATE, 
        page=page, 
        members=data["members"], 
        assignments=data["assignments"],
        available_names=sorted(available),
        **kwargs
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Buddy - นครนายก นาใจ</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #020617; color: #f8fafc; }
        .glass-card { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); transition: all 0.2s; }
    </style>
</head>
<body class="min-h-screen pb-10">
    <div class="max-w-md mx-auto p-4 pt-10">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-black text-white italic tracking-tighter">NAKHON NAYOK <span class="text-orange-500">2026</span></h1>
            <p class="text-slate-500 text-[10px] tracking-[0.3em] uppercase mt-1">สุ่มชื่อพร้อมเช็คเลขอกเพื่อน</p>
        </div>

        <div class="flex mb-6 bg-slate-900/80 p-1 rounded-2xl border border-white/5 shadow-xl">
            <a href="/" class="flex-1 text-center py-3 rounded-xl text-sm font-bold {{ 'bg-orange-600 text-white shadow-lg' if page == 'index' else 'text-slate-500' }}">🎁 สุ่มชื่อ</a>
            <a href="/admin" class="flex-1 text-center py-3 rounded-xl text-sm font-bold {{ 'bg-orange-600 text-white shadow-lg' if page == 'admin' or page == 'login' else 'text-slate-500' }}">⚙️ แอดมิน</a>
        </div>

        <div class="glass-card rounded-[2.5rem] p-8 shadow-2xl border border-orange-500/20">
            {% if page == 'login' %}
                <form action="/admin_login" method="POST" class="text-center space-y-6">
                    <i data-lucide="lock" class="mx-auto text-orange-500 w-10 h-10"></i>
                    <input type="password" name="pw" placeholder="รหัสแอดมิน" class="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 text-center text-white outline-none focus:border-orange-500">
                    <button type="submit" class="w-full py-3 btn-primary rounded-xl font-bold text-white uppercase">เข้าสู่ระบบ</button>
                </form>

            {% elif page == 'admin' %}
                <div class="space-y-6">
                    <div>
                        <h3 class="text-orange-400 text-[10px] font-black mb-3 uppercase tracking-widest">เพิ่มสมาชิกใหม่</h3>
                        <form action="/add_member" method="POST" class="space-y-2 mb-4">
                            <input type="text" name="name" required placeholder="ชื่อเล่นเพื่อน" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white outline-none focus:border-orange-500">
                            <div class="flex gap-2">
                                <input type="text" name="pin" required placeholder="PIN (4 หลัก)" class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white outline-none focus:border-orange-500">
                                <input type="text" name="size" required placeholder="เลขอก (40-42)" class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white outline-none focus:border-orange-500">
                            </div>
                            <button type="submit" class="w-full bg-orange-600 py-2 rounded-xl font-bold text-white mt-2">ยืนยันเพิ่มรายชื่อ</button>
                        </form>
                        <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
                            {% for name, info in members.items() %}
                            <div class="bg-slate-800/40 border border-white/5 px-4 py-2 rounded-xl flex justify-between items-center text-[11px]">
                                <span><b class="text-white">{{ name }}</b> | PIN: {{ info.pin }} | อก: <span class="text-emerald-400">{{ info.size }}</span></span>
                                <a href="/del_member/{{ name }}" class="text-rose-500 font-bold text-lg px-2">×</a>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-6 border-t border-white/5">
                        <h3 class="text-emerald-400 text-[10px] font-black mb-3 uppercase tracking-widest text-center">สรุปใครคู่ใคร (ลับมาก)</h3>
                        <div class="space-y-1">
                            {% for giver, receiver in assignments.items() %}
                            <div class="text-[10px] text-slate-400 bg-slate-900/50 p-2 rounded-lg border border-white/5 flex justify-between">
                                <span>{{ giver }}</span>
                                <span class="text-orange-500">➔</span>
                                <span class="text-white font-bold">{{ receiver }} ({{ members[receiver].size }})</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-4 border-t border-white/5 flex justify-between">
                        <a href="/logout" class="text-[9px] text-slate-500 underline uppercase italic">Log out</a>
                        <a href="/reset" class="text-[9px] text-rose-500 font-bold uppercase" onclick="return confirm('ล้างข้อมูลสุ่มใหม่หมด?')">Reset Everything</a>
                    </div>
                </div>

            {% else %}
                <div class="text-center space-y-6">
                    <div class="w-16 h-16 bg-orange-600/10 rounded-3xl flex items-center justify-center mx-auto border border-orange-500/20">
                        <i data-lucide="gift" class="text-orange-500 w-8 h-8"></i>
                    </div>
                    
                    <form action="/draw" method="POST" class="space-y-4">
                        <div class="text-left">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest ml-1">1. มึงชื่ออะไร?</label>
                            <select name="user_name" required class="w-full mt-2 bg-slate-950 border border-slate-800 rounded-xl p-4 text-white font-bold outline-none focus:border-orange-500 appearance-none">
                                <option value="">-- เลือกชื่อตัวเอง --</option>
                                {% for name in available_names %}
                                    <option value="{{ name }}">{{ name }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="text-left">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest ml-1">2. ใส่รหัส PIN ที่แอดมินส่งให้</label>
                            <input type="password" name="user_pin" required placeholder="••••" class="w-full mt-2 bg-slate-950 border border-slate-800 rounded-xl p-4 text-center text-white text-xl tracking-widest outline-none focus:border-orange-500">
                        </div>

                        <button type="submit" class="w-full py-4 mt-2 rounded-xl font-black text-lg btn-primary text-white shadow-xl shadow-orange-900/20 uppercase tracking-widest">
                            สุ่มรายชื่อเพื่อน
                        </button>
                    </form>
                </div>
            {% endif %}
        </div>
    </div>

    {% if result %}
    <div id="resultModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/95 backdrop-blur-xl">
        <div class="glass-card w-full max-w-xs p-10 rounded-[3rem] border-2 border-orange-500/30 text-center space-y-6">
            <p class="text-orange-500 text-[10px] font-black tracking-widest uppercase">มึงต้องซื้อชุดให้...</p>
            <h2 class="text-5xl font-black text-white tracking-tighter">{{ result }}</h2>
            <div class="py-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
                <p class="text-emerald-400 text-[10px] uppercase font-black mb-1 italic">เลขหน้าอกของมัน</p>
                <p class="text-2xl font-black text-white italic tracking-widest">{{ result_size }}</p>
            </div>
            <button onclick="window.location='/'" class="bg-orange-600 w-full py-3 rounded-xl text-white font-bold text-xs uppercase shadow-lg shadow-orange-900/40">เข้าใจแล้ว</button>
        </div>
    </div>
    {% endif %}

    <script>lucide.createIcons();</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_page('index', result=None)

@app.route("/admin")
def admin():
    if not session.get("is_admin"): 
        return render_page('login')
    return render_page('admin')

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))
    return "<script>alert('รหัสแอดมินผิด!'); window.location='/admin';</script>"

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/add_member", methods=["POST"])
def add_member():
    name = request.form.get("name", "").strip()
    pin = request.form.get("pin", "").strip()
    size = request.form.get("size", "").strip()
    if name and pin and size:
        data = load_data()
        data["members"][name] = {"pin": pin, "size": size}
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_member/<name>")
def del_member(name):
    data = load_data()
    if name in data["members"]:
        del data["members"][name]
        if name in data["assignments"]: del data["assignments"][name]
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    input_pin = request.form.get("user_pin", "").strip()
    data = load_data()
    
    if user not in data["members"] or data["members"][user]["pin"] != input_pin:
        return "<script>alert('ชื่อหรือ PIN ไม่ถูกต้อง!'); window.location='/';</script>"

    if user in data["assignments"]:
        res_name = data["assignments"][user]
        return render_page('index', result=res_name, result_size=data["members"][res_name]["size"])

    all_names = list(data["members"].keys())
    already_chosen = list(data["assignments"].values())
    candidates = [n for n in all_names if n != user and n not in already_chosen]
    
    if not candidates:
        return "<script>alert('ไม่เหลือคนให้สุ่มแล้วจ้า!'); window.location='/';</script>"

    target = random.choice(candidates)
    data["assignments"][user] = target
    save_data(data)
    
    return render_page('index', result=target, result_size=data["members"][target]["size"])

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)