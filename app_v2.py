from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = "nakhon_nayok_v2026_pro"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "1234"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"members": {}, "assignments": {}, "exclusions": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- UI TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAKHON NAYOK 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background: #020617; color: #f8fafc; min-height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(249, 115, 22, 0.2); }
        .btn-burn { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); box-shadow: 0 10px 20px -5px rgba(234, 88, 12, 0.4); }
    </style>
</head>
<body class="p-4 flex flex-col items-center justify-center">
    <div class="w-full max-w-md">
        <header class="text-center mb-8 mt-10">
            <h1 class="text-4xl font-black italic text-white uppercase tracking-tighter">NAKHON NAYOK <span class="text-orange-500">2026</span></h1>
            <p class="text-[10px] text-slate-500 font-bold tracking-[0.3em] uppercase mt-2">Secret Buddy & Special Gift</p>
        </header>

        <div class="glass rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden">
            {% if page == 'admin' %}
                <!-- หน้าแอดมิน -->
                <h2 class="text-orange-500 font-black mb-6 uppercase tracking-widest text-xs flex items-center gap-2"><i data-lucide="settings"></i> แดนแอดมิน (ความลับ)</h2>
                
                <form action="/add_member" method="POST" class="space-y-3 mb-8">
                    <input type="text" name="name" placeholder="ชื่อเล่นเพื่อน" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-orange-500 outline-none">
                    <input type="text" name="size" placeholder="อก (เช่น 42)" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-orange-500 outline-none">
                    <button type="submit" class="w-full btn-burn py-3 rounded-xl font-black text-xs uppercase tracking-widest">ปั้นเหยื่อ</button>
                </form>

                <div class="space-y-4">
                    <h3 class="text-slate-400 text-[10px] font-black uppercase tracking-widest border-b border-slate-800 pb-2">📋 รายชื่อและลิงก์สุ่ม</h3>
                    <div class="space-y-2 max-h-64 overflow-y-auto pr-2">
                        {% for name, info in members.items() %}
                        <div class="bg-slate-900/50 p-3 rounded-xl border border-white/5">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm font-bold">{{ name }} <span class="text-[10px] text-slate-500 font-normal">(อก: {{ info.size }})</span></span>
                                <a href="/del_member/{{ name }}" class="text-rose-500"><i data-lucide="trash-2" class="w-4 h-4"></i></a>
                            </div>
                            <div class="flex gap-1">
                                <input type="text" readonly value="{{ base_url }}/draw/{{ info.token }}" id="link-{{ name }}" class="flex-1 bg-black/40 text-[9px] p-2 rounded border border-white/5 text-slate-400 font-mono">
                                <button onclick="copyLink('link-{{ name }}')" class="bg-slate-700 px-3 rounded text-[9px] font-bold hover:bg-slate-600">COPY</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="mt-8 pt-4 border-t border-slate-800 flex justify-between">
                    <a href="/logout" class="text-[10px] text-slate-500 underline uppercase">Logout</a>
                    <a href="/reset" class="text-[10px] text-rose-500 font-bold uppercase" onclick="return confirm('ล้างข้อมูลการสุ่มใหม่หมด?')">Reset All</a>
                </div>

            {% elif page == 'draw_home' %}
                <!-- หน้าที่เพื่อนเห็นตอนกดลิงก์ตัวเอง -->
                <div class="text-center space-y-6">
                    <div class="bg-orange-500/10 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto border border-orange-500/20">
                        <i data-lucide="sparkles" class="text-orange-500 w-10 h-10"></i>
                    </div>
                    <div>
                        <p class="text-slate-500 text-[10px] uppercase font-bold tracking-widest">ยินดีต้อนรับเหยื่อรายที่...</p>
                        <h2 class="text-4xl font-black text-white italic tracking-tighter mt-1">{{ user_name }}</h2>
                    </div>

                    {% if result %}
                        <div class="py-10 px-4 bg-orange-600 rounded-[2rem] shadow-[0_0_50px_rgba(234,88,12,0.3)] animate-bounce">
                            <p class="text-white/70 text-[10px] uppercase font-black mb-2 tracking-widest">มึงเตรียมโดนแกง...</p>
                            <h3 class="text-5xl font-black text-white italic tracking-tighter">{{ result }}</h3>
                            <div class="mt-4 bg-black/20 py-2 rounded-xl border border-white/10">
                                <p class="text-[9px] text-white/50 uppercase font-bold">ทรงอกของเหยื่อ</p>
                                <p class="text-xl font-black text-white">{{ result_size }}</p>
                            </div>
                        </div>
                        <p class="text-[9px] text-slate-500 italic">จำใส่สมองไว้ แล้วไปหาชุดมาแกงมันซะ!</p>
                    {% else %}
                        <form action="/process_draw/{{ token }}" method="POST">
                            <button type="submit" class="w-full py-6 btn-burn rounded-3xl font-black text-xl text-white uppercase italic tracking-widest animate-pulse">
                                🔥 สุ่มหาเหยื่อ!
                            </button>
                        </form>
                        <p class="text-[9px] text-slate-500">กดสุ่มแล้วเปลี่ยนใจไม่ได้นะจ๊ะ</p>
                    {% endif %}
                </div>

            {% elif page == 'login' %}
                <form action="/admin_login" method="POST" class="text-center space-y-4">
                    <i data-lucide="lock" class="mx-auto text-orange-500 mb-2"></i>
                    <input type="password" name="pw" placeholder="ADMIN PIN" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 text-center text-white focus:border-orange-500 outline-none">
                    <button type="submit" class="w-full btn-burn py-4 rounded-xl font-black text-white uppercase tracking-widest">ENTER</button>
                </form>
            {% endif %}
        </div>
    </div>

    <script>
        lucide.createIcons();
        function copyLink(id) {
            var copyText = document.getElementById(id);
            copyText.select();
            document.execCommand("copy");
            alert("ก๊อปลิงก์แล้ว ส่งให้เพื่อนได้เลย!");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return redirect(url_for("admin"))

@app.route("/admin")
def admin():
    if not session.get("is_admin"): return render_template_string(HTML_TEMPLATE, page='login')
    data = load_data()
    return render_template_string(HTML_TEMPLATE, page='admin', members=data["members"], base_url=request.url_root.rstrip('/'))

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin"))

@app.route("/add_member", methods=["POST"])
def add_member():
    name = request.form.get("name", "").strip()
    size = request.form.get("size", "").strip()
    if name and size:
        data = load_data()
        token = secrets.token_urlsafe(8)
        data["members"][name] = {"size": size, "token": token}
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

@app.route("/draw/<token>")
def draw_page(token):
    data = load_data()
    user_name = next((k for k, v in data["members"].items() if v["token"] == token), None)
    if not user_name: return "Link ไม่ถูกต้องว่ะมึง!", 404
    
    result = data["assignments"].get(user_name)
    result_size = data["members"][result]["size"] if result else None
    
    return render_template_string(HTML_TEMPLATE, page='draw_home', user_name=user_name, token=token, result=result, result_size=result_size)

@app.route("/process_draw/<token>", methods=["POST"])
def process_draw(token):
    data = load_data()
    user_name = next((k for k, v in data["members"].items() if v["token"] == token), None)
    if not user_name or user_name in data["assignments"]: return redirect(url_for("draw_page", token=token))

    all_names = list(data["members"].keys())
    already_chosen = list(data["assignments"].values())
    candidates = [n for n in all_names if n != user_name and n not in already_chosen]
    
    if not candidates: return "ไม่เหลือเหยื่อให้แกงแล้วว่ะ ติดต่อแอดมินด่วน!", 400

    target = random.choice(candidates)
    data["assignments"][user_name] = target
    save_data(data)
    return redirect(url_for("draw_page", token=token))

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)