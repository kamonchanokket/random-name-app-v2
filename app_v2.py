from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_v6_fixed"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl" 

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"names": [], "assignments": {}, "exclusions": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>นครนายก นาใจ 2026 | Secret Buddy</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --brand-orange: #ff6b35;
            --brand-dark: #0f172a;
        }
        body { 
            font-family: 'Kanit', sans-serif; 
            background: radial-gradient(circle at top right, #1e293b, #020617);
            color: #f8fafc;
            min-height: 100vh;
        }
        .glass-card { 
            background: rgba(30, 41, 59, 0.7); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .btn-gradient {
            background: linear-gradient(135deg, #f97316 0%, #d946ef 100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn-gradient:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 20px -5px rgba(249, 115, 22, 0.5);
        }
        .animate-float {
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        select {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23f97316'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 1rem center;
            background-size: 1.2em;
        }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-md mx-auto relative">
        <div class="absolute -top-10 -left-10 w-32 h-32 bg-orange-500/20 blur-3xl rounded-full"></div>
        <div class="absolute -bottom-10 -right-10 w-32 h-32 bg-purple-500/20 blur-3xl rounded-full"></div>

        <header class="text-center mb-10 relative">
            <div class="inline-block p-2 px-4 bg-orange-500/10 border border-orange-500/20 rounded-full mb-4">
                <span class="text-orange-400 text-xs font-bold tracking-widest uppercase">Annual Trip 2026</span>
            </div>
            <h1 class="text-4xl font-extrabold tracking-tight text-white mb-2">
                นครนายก <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-pink-500">นาใจ</span>
            </h1>
            <p class="text-slate-400 text-sm font-light italic">"เสื้อที่มึงไม่อยากใส่... คือสิ่งที่คุณต้องสุ่มได้"</p>
        </header>

        <nav class="flex p-1.5 bg-slate-900/50 rounded-2xl border border-white/5 mb-8 shadow-inner">
            <a href="/" class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-all {{ 'bg-white/10 text-white shadow-lg' if page == 'index' else 'text-slate-500 hover:text-slate-300' }}">
                <i data-lucide="gift" class="w-4 h-4"></i> สุ่มชื่อ
            </a>
            <a href="/admin" class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-all {{ 'bg-white/10 text-white shadow-lg' if page in ['admin', 'login'] else 'text-slate-500 hover:text-slate-300' }}">
                <i data-lucide="settings" class="w-4 h-4"></i> จัดการแก๊ง
            </a>
        </nav>

        <main class="glass-card rounded-[2.5rem] p-8 relative overflow-hidden">
            
            {% if page == 'login' %}
                <div class="text-center space-y-6 py-4">
                    <div class="w-16 h-16 bg-orange-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-orange-500/30">
                        <i data-lucide="lock" class="text-orange-500 w-8 h-8"></i>
                    </div>
                    <h2 class="text-xl font-bold">Admin Only</h2>
                    <form action="/admin_login" method="POST" class="space-y-4">
                        <input type="password" name="pw" placeholder="ระบุรหัสลับ" class="w-full bg-slate-950/50 border border-slate-700 rounded-2xl py-4 px-6 text-center text-white focus:ring-2 ring-orange-500/50 outline-none transition-all">
                        <button type="submit" class="w-full py-4 btn-gradient rounded-2xl font-bold text-white uppercase tracking-wider">Unlock Access</button>
                    </form>
                </div>

            {% elif page == 'admin' %}
                <div class="space-y-8">
                    <section>
                        <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3">เพิ่มสมาชิกใหม่</label>
                        <form action="/add_name" method="POST" class="relative group">
                            <input type="text" name="new_name" placeholder="ใส่ชื่อเล่นเพื่อน..." class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl pl-6 pr-16 py-4 text-white focus:border-orange-500 outline-none transition-all">
                            <button type="submit" class="absolute right-2 top-2 bottom-2 px-4 bg-orange-600 rounded-xl text-white hover:bg-orange-500 transition-colors">
                                <i data-lucide="plus" class="w-5 h-5"></i>
                            </button>
                        </form>
                    </section>

                    <section>
                        <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 text-right">รายชื่อทั้งหมด ({{ names|length }})</label>
                        <div class="flex flex-wrap gap-2">
                            {% for name in names %}
                            <div class="group bg-slate-800/40 hover:bg-slate-700/60 border border-white/5 px-4 py-2 rounded-xl text-sm flex items-center gap-3 transition-all">
                                <span class="font-medium text-slate-200">{{ name }}</span>
                                <a href="/del_name/{{ name }}" class="opacity-0 group-hover:opacity-100 text-rose-500 hover:scale-125 transition-all">
                                    <i data-lucide="x-circle" class="w-4 h-4"></i>
                                </a>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <section class="p-5 bg-rose-500/5 rounded-3xl border border-rose-500/10">
                        <div class="flex items-center gap-2 mb-4">
                            <i data-lucide="shield-alert" class="w-4 h-4 text-rose-400"></i>
                            <h3 class="text-rose-400 text-xs font-bold uppercase tracking-widest">คู่ห้ามสุ่มโดนกัน</h3>
                        </div>
                        <form action="/add_exclusion" method="POST" class="grid grid-cols-1 gap-3 mb-4">
                            <div class="grid grid-cols-2 gap-2">
                                <select name="p1" class="bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                                <select name="p2" class="bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-slate-800 hover:bg-slate-700 text-white py-3 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-colors">ยืนยันเงื่อนไข</button>
                        </form>
                        <div class="space-y-2">
                            {% for pair in exclusions %}
                            <div class="flex justify-between items-center bg-slate-900/50 p-3 rounded-xl border border-white/5">
                                <span class="text-xs text-slate-400 font-medium">{{ pair[0] }} <span class="mx-2 text-rose-500">×</span> {{ pair[1] }}</span>
                                <a href="/del_exclusion/{{ loop.index0 }}" class="text-rose-500 p-1 hover:bg-rose-500/10 rounded-lg">
                                    <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                                </a>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <footer class="pt-6 border-t border-white/10 flex flex-col gap-4">
                        <a href="/logout" class="text-center text-[10px] text-slate-500 hover:text-slate-300 underline underline-offset-4 font-bold">LOGOUT ADMIN</a>
                        <a href="/reset" class="py-3 px-6 bg-rose-950/30 border border-rose-500/20 text-rose-500 rounded-xl text-[10px] font-bold text-center hover:bg-rose-500/20 transition-all" onclick="return confirm('สุ่มใหม่ทั้งหมดจริงนะ?')">RESET ALL ASSIGNMENTS</a>
                    </footer>
                </div>

            {% else %}
                <div class="text-center py-4">
                    <div class="animate-float mb-8">
                        <div class="w-24 h-24 bg-gradient-to-br from-orange-500 to-pink-500 rounded-[2rem] flex items-center justify-center mx-auto rotate-12 shadow-2xl">
                            <i data-lucide="shirt" class="text-white w-12 h-12 -rotate-12"></i>
                        </div>
                    </div>

                    <form action="/draw" method="POST" class="space-y-8">
                        <div class="space-y-4">
                            <label class="block text-xs font-bold text-orange-400 uppercase tracking-[0.3em]">ยืนยันตัวตนคนบาป</label>
                            <div class="relative">
                                <select name="user_name" class="w-full bg-slate-950 border border-slate-800 rounded-3xl p-6 text-xl font-bold text-white text-center outline-none focus:ring-2 ring-orange-500/50 transition-all cursor-pointer">
                                    <option value="">เลือกชื่อตัวเอง</option>
                                    {% for name in names | sort %}
                                        <option value="{{ name }}">{{ name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <div class="pt-4">
                            <button type="submit" class="w-full py-6 rounded-3xl font-black text-2xl btn-gradient text-white shadow-2xl uppercase tracking-tighter italic">
                                สุ่มหาเหยื่อ!
                            </button>
                            <p class="mt-4 text-slate-500 text-[10px] uppercase font-bold tracking-widest">กดครั้งเดียวรู้เรื่อง คนเดิมสุ่มใหม่ไม่ได้</p>
                        </div>
                    </form>
                </div>
            {% endif %}
        </main>
    </div>

    {% if result %}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/90 backdrop-blur-xl transition-all">
        <div class="glass-card w-full max-w-sm p-10 rounded-[3rem] border-2 border-orange-500/50 text-center space-y-8 shadow-[0_0_80px_-15px_rgba(249,115,22,0.4)]">
            <header>
                <span class="bg-orange-500 text-white px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest">Target Locked</span>
                <p class="text-slate-400 text-xs font-medium mt-4 italic">จัดหาเสื้อให้เพื่อนคนนี้...</p>
            </header>
            
            <h2 class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-slate-400 py-4 drop-shadow-lg">
                {{ result }}
            </h2>
            
            <div class="py-4 px-6 bg-white/5 rounded-2xl border border-white/5 space-y-2">
                <p class="text-orange-400 text-sm font-bold uppercase tracking-tight">Mission Objective:</p>
                <p class="text-slate-300 text-xs leading-relaxed">ไปหาชุดที่มันเห็นแล้วอยากจะเดินลงจากรถทัวร์ หรือชุดที่ใส่แล้วคนนึกว่ามาแก้บน!</p>
            </div>
            
            <button onclick="window.location='/'" class="w-full py-4 bg-slate-800 hover:bg-slate-700 rounded-2xl text-white text-xs font-bold uppercase tracking-widest transition-all">
                รับทราบ และปกปิดเป็นความลับ
            </button>
        </div>
    </div>
    {% endif %}

    <script>
        lucide.createIcons();
    </script>
</body>
</html>
"""

# ... [Routes ส่วนที่เหลือเหมือนเดิมทั้งหมด] ...

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index')

@app.route("/admin")
def admin():
    if not session.get("is_admin"): return render_template_string(HTML_TEMPLATE, page='login')
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], exclusions=data["exclusions"], page='admin')

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))
    return "<script>alert('รหัสผิด!'); window.location='/admin';</script>"

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/add_name", methods=["POST"])
def add_name():
    name = request.form.get("new_name", "").strip()
    if not name: return redirect(url_for("admin"))
    data = load_data()
    if name not in data["names"]:
        data["names"].append(name)
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_name/<name>")
def del_name(name):
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    if name in data["names"]:
        data["names"].remove(name)
        data["assignments"] = {k: v for k, v in data["assignments"].items() if k != name and v != name}
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/add_exclusion", methods=["POST"])
def add_exclusion():
    p1, p2 = request.form.get("p1"), request.form.get("p2")
    if p1 == p2: return "<script>alert('ชื่อซ้ำกัน!'); window.location='/admin';</script>"
    data = load_data()
    data["exclusions"].append([p1, p2])
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_exclusion/<int:idx>")
def del_exclusion(idx):
    data = load_data()
    if 0 <= idx < len(data["exclusions"]): data["exclusions"].pop(idx)
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    if not user: return "<script>alert('เลือกชื่อก่อน!'); window.location='/';</script>"
    
    data = load_data()
    if user in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=data["assignments"][user])

    assigned_receivers = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned_receivers]
    
    for p1, p2 in data["exclusions"]:
        if user == p1 and p2 in candidates: candidates.remove(p2)
        if user == p2 and p1 in candidates: candidates.remove(p1)

    if not candidates:
        return "<script>alert('ไม่มีใครเหลือให้สุ่มแล้ว หรือติดเงื่อนไขคู่ห้าม!'); window.location='/';</script>"

    target = random.choice(candidates)
    data["assignments"][user] = target
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target)

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)