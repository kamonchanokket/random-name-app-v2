from Flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_v13_creative_final"

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

def render_page(page, **kwargs):
    data = load_data()
    available = [n for n in data["members"].keys() if n not in data["assignments"]]
    return render_template_string(
        HTML_TEMPLATE, 
        page=page, 
        members=data["members"], 
        assignments=data["assignments"],
        exclusions=data["exclusions"],
        available_names=sorted(available),
        **kwargs
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Buddy - นครนายก นาใจ 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background: radial-gradient(circle at top right, #1e293b, #020617); color: #f8fafc; min-height: 100vh; }
        .glass-card { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(249, 115, 22, 0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(234, 88, 12, 0.3); }
        select, input { background: rgba(2, 6, 23, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #f8fafc !important; }
        select:focus, input:focus { border-color: #f97316 !important; outline: none; }
        select option { background-color: #020617; color: #f8fafc; }
    </style>
</head>
<body class="pb-10">
    <div class="max-w-md mx-auto p-6 pt-12">
        <div class="text-center mb-10">
            <h1 class="text-4xl font-black text-white italic tracking-tighter uppercase">NAKHON NAYOK <span class="text-orange-500">2026</span></h1>
            <div class="h-1 w-20 bg-orange-500 mx-auto mt-2 rounded-full"></div>
            <p class="text-slate-500 text-[10px] tracking-[0.4em] uppercase mt-3 font-bold underline decoration-orange-500/30">Secret Buddy เสื้อที่มึงไม่อยากใส่</p>
        </div>

        <div class="flex mb-8 bg-slate-900/50 p-1.5 rounded-2xl border border-white/5 shadow-inner">
            <a href="/" class="flex-1 text-center py-3 rounded-xl text-xs font-black uppercase tracking-widest {{ 'bg-orange-600 text-white shadow-lg' if page == 'index' else 'text-slate-500 hover:text-slate-300' }}">🎁 จับคู่คนที่จะแกง</a>
            <a href="/admin" class="flex-1 text-center py-3 rounded-xl text-xs font-black uppercase tracking-widest {{ 'bg-orange-600 text-white shadow-lg' if page == 'admin' or page == 'login' else 'text-slate-500 hover:text-slate-300' }}">⚙️ แดนแอดมิน</a>
        </div>

        <div class="glass-card rounded-[3rem] p-10 relative overflow-hidden">
            {% if page == 'login' %}
                <form action="/admin_login" method="POST" class="text-center space-y-6">
                    <div class="bg-orange-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-orange-500/20">
                        <i data-lucide="lock" class="text-orange-500 w-8 h-8"></i>
                    </div>
                    <input type="password" name="pw" placeholder="รหัสลับแอดมิน" class="w-full rounded-2xl py-4 text-center text-white text-lg">
                    <button type="submit" class="w-full py-4 btn-primary rounded-2xl font-black text-white uppercase tracking-widest">Access System</button>
                </form>

            {% elif page == 'admin' %}
                <div class="space-y-8">
                    <section>
                        <h3 class="text-orange-400 text-[10px] font-black mb-4 uppercase tracking-widest flex items-center gap-2"><i data-lucide="user-plus" class="w-3 h-3"></i> 👹 เติมเชื้อเพลิงแกง (เพิ่มคน)</h3>
                        <form action="/add_member" method="POST" class="space-y-3">
                            <input type="text" name="name" required placeholder="ชื่อเล่นเพื่อน" class="w-full rounded-xl px-4 py-3 text-sm text-white">
                            <div class="flex gap-2">
                                <input type="text" name="pin" required placeholder="PIN" class="flex-1 rounded-xl px-4 py-3 text-sm text-white">
                                <input type="text" name="size" required placeholder="อก (เช่น 40-42)" class="flex-1 rounded-xl px-4 py-3 text-sm text-white">
                            </div>
                            <button type="submit" class="w-full bg-slate-100 text-slate-900 py-3 rounded-xl font-black text-xs uppercase hover:bg-white">ปั้นเหยื่อ</button>
                        </form>
                    </section>

                    <section class="pt-6 border-t border-white/5">
                        <h3 class="text-rose-400 text-[10px] font-black mb-4 uppercase tracking-widest flex items-center gap-2"><i data-lucide="heart-off" class="w-3 h-3"></i> 💔 ล็อคแฟน (ห้ามแกงกันเอง)</h3>
                        <form action="/add_exclusion" method="POST" class="flex gap-2">
                            <select name="p1" required class="flex-1 rounded-xl px-2 py-2 text-xs text-white cursor-pointer">
                                {% for name in members.keys() %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                            </select>
                            <span class="flex items-center text-slate-500 font-bold">❌</span>
                            <select name="p2" required class="flex-1 rounded-xl px-2 py-2 text-xs text-white cursor-pointer">
                                {% for name in members.keys() %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                            </select>
                            <button type="submit" class="bg-rose-600 px-4 rounded-xl text-white font-bold hover:bg-rose-500">+</button>
                        </form>
                        <div class="mt-3 flex flex-wrap gap-2">
                            {% for p1, p2 in exclusions %}
                            <div class="bg-rose-500/10 border border-rose-500/20 px-3 py-1 rounded-full text-[9px] text-rose-300 flex items-center gap-2 font-mono">
                                {{ p1 }} - {{ p2 }} <a href="/del_exclusion/{{ loop.index0 }}" class="font-black text-rose-500">×</a>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <section class="pt-6 border-t border-white/5 overflow-hidden">
                        <h3 class="text-emerald-400 text-[10px] font-black mb-4 uppercase tracking-widest text-center flex items-center gap-2 justify-center"><i data-lucide="file-text" class="w-3 h-3"></i> ☠️ โพยจับคู่ (ลับมากมึง)</h3>
                        <div class="space-y-1 max-h-48 overflow-y-auto pr-1">
                            {% for giver, receiver in assignments.items() %}
                            <div class="text-[9px] text-slate-500 flex justify-between bg-slate-900/30 p-2.5 rounded-lg border border-white/5 font-mono">
                                <span>{{ giver }}</span>
                                <span class="text-orange-500 font-bold">➔</span>
                                <span class="text-white">{{ receiver }} (อก {{ members[receiver].size }})</span>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <div class="pt-4 flex justify-between items-center border-t border-white/5">
                        <a href="/logout" class="text-[9px] text-slate-500 underline font-bold uppercase italic hover:text-white">Logout แอดมิน</a>
                        <a href="/reset" class="text-[9px] text-rose-500 font-bold uppercase hover:text-rose-300" onclick="return confirm('ล้างข้อมูลการสุ่มใหม่หมด?')">Reset System</a>
                    </div>
                </div>

            {% else %}
                <div class="text-center space-y-8">
                    <div class="bg-orange-500/10 w-20 h-20 rounded-[2rem] flex items-center justify-center mx-auto border border-orange-500/20 shadow-inner">
                        <i data-lucide="sparkles" class="text-orange-500 w-10 h-10"></i>
                    </div>
                    
                    <form action="/draw" method="POST" class="space-y-5">
                        <div class="text-left space-y-2">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest ml-4">1. มึงคือใครในแก๊ง?</label>
                            <select name="user_name" required class="w-full rounded-2xl p-5 text-white font-black text-lg appearance-none shadow-xl cursor-pointer">
                                <option value="">-- WHERE ARE YOU? --</option>
                                {% for name in available_names %}
                                    <option value="{{ name }}">{{ name }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="text-left space-y-2">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest ml-4">2. รหัสลับ (PIN)</label>
                            <input type="password" name="user_pin" required placeholder="••••" class="w-full rounded-2xl p-5 text-center text-white text-2xl tracking-[1em] shadow-xl">
                        </div>

                        <button type="submit" class="w-full py-5 mt-4 rounded-2xl font-black text-xl btn-primary text-white shadow-2xl uppercase tracking-widest italic animate-pulse">
                            🔥 สุ่มหาเหยื่อ!
                        </button>
                    </form>
                    <p class="text-slate-600 text-[9px] font-bold uppercase tracking-widest underline decoration-orange-500/20">Nakhon Nayok Na Jai 2026</p>
                </div>
            {% endif %}
        </div>
    </div>

    {% if result %}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-slate-950/98 backdrop-blur-2xl">
        <div class="glass-card w-full max-w-sm p-12 rounded-[4rem] border-2 border-orange-500/30 text-center space-y-8 animate-in zoom-in duration-500 shadow-[0_0_100px_rgba(234,88,12,0.3)]">
            <div>
                <p class="text-orange-500 text-[10px] font-black tracking-[0.3em] uppercase mb-4 italic">You Got Buddy!</p>
                <p class="text-slate-500 text-[10px] uppercase font-bold mb-2 tracking-widest">มึงเตรียมโดนแกง...</p>
                <h2 class="text-6xl font-black text-white tracking-tighter italic">{{ result }}</h2>
            </div>
            
            <div class="py-6 px-4 bg-emerald-500/10 border border-emerald-500/20 rounded-[2rem]">
                <p class="text-emerald-400 text-[10px] uppercase font-black mb-2 tracking-widest italic">ทรงอกของเหยื่อ</p>
                <p class="text-3xl font-black text-white italic tracking-widest font-mono">{{ result_size }}</p>
            </div>

            <p class="text-slate-500 text-[9px] italic leading-relaxed">แคปหน้าจอไว้ ห้ามบอกใครเด็ดขาด!<br>ไปหาชุดที่มันเห็นแล้วต้องร้องไห้มาซะ</p>

            <button onclick="window.location='/'" class="bg-orange-600 w-full py-4 rounded-2xl text-white font-black uppercase text-xs tracking-[0.2em] shadow-lg shadow-orange-900/40 hover:bg-orange-500 transition-colors">จำใส่สมองแล้ว</button>
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
    if not session.get("is_admin"): return render_page('login')
    return render_page('admin')

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))
    return "<script>alert('รหัสแอดมินผิดว่ะมึง!'); window.location='/admin';</script>"

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
        data["exclusions"] = [p for p in data["exclusions"] if name not in p]
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/add_exclusion", methods=["POST"])
def add_exclusion():
    p1 = request.form.get("p1")
    p2 = request.form.get("p2")
    if p1 and p2 and p1 != p2:
        data = load_data()
        if [p1, p2] not in data["exclusions"] and [p2, p1] not in data["exclusions"]:
            data["exclusions"].append([p1, p2])
            save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_exclusion/<int:index>")
def del_exclusion(index):
    data = load_data()
    if 0 <= index < len(data["exclusions"]):
        data["exclusions"].pop(index)
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    input_pin = request.form.get("user_pin", "").strip()
    data = load_data()
    
    if user not in data["members"] or data["members"][user]["pin"] != input_pin:
        return "<script>alert('ชื่อหรือ PIN ไม่ถูกว่ะมึง ลองใหม่!'); window.location='/';</script>"

    if user in data["assignments"]:
        res_name = data["assignments"][user]
        return render_page('index', result=res_name, result_size=data["members"][res_name]["size"])

    all_names = list(data["members"].keys())
    already_chosen = list(data["assignments"].values())
    
    candidates = [n for n in all_names if n != user and n not in already_chosen]
    
    for p1, p2 in data["exclusions"]:
        if user == p1 and p2 in candidates: candidates.remove(p2)
        if user == p2 and p1 in candidates: candidates.remove(p1)
    
    if not candidates:
        return "<script>alert('ไม่เหลือคนให้สุ่มแล้วจ้า ติดเงื่อนไขแฟนหรือเปล่า? ลองติดต่อแอดมิน'); window.location='/';</script>"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)