import webbrowser
import json
import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

TASKS_FILE = os.path.expanduser("~/Desktop/Claude Code/practice/tasks.json")
NOTES_FILE = os.path.expanduser("~/Desktop/Claude Code/practice/dashboard_notes.json")

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def fetch_weather():
    try:
        url = "https://wttr.in/Burnaby,BC,Canada?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        temp_c = data["current_condition"][0]["temp_C"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        feels = data["current_condition"][0]["FeelsLikeC"]
        return {"temp": temp_c, "desc": desc, "feels": feels}
    except:
        return {"temp": "--", "desc": "Unavailable", "feels": "--"}

def fetch_quote():
    try:
        url = "https://zenquotes.io/api/today"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        return {"quote": data[0]["q"], "author": data[0]["a"]}
    except:
        return {"quote": "The best time to start was yesterday. The next best time is now.", "author": "Unknown"}

def fetch_word():
    try:
        url = "https://random-word-api.herokuapp.com/word"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            word = json.loads(r.read())[0]
        url2 = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        req2 = urllib.request.Request(url2, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req2, timeout=5) as r2:
            data = json.loads(r2.read())
        definition = data[0]["meanings"][0]["definitions"][0]["definition"]
        return {"word": word, "definition": definition}
    except:
        return {"word": "resilience", "definition": "The capacity to recover quickly from difficulties."}

weather = {"temp": "--", "desc": "Loading...", "feels": "--"}
quote = {"quote": "The best time to start was yesterday. The next best time is now.", "author": "Unknown"}
word = {"word": "resilience", "definition": "The capacity to recover quickly from difficulties."}
tasks = load_json(TASKS_FILE, [])
notes = load_json(NOTES_FILE, {"focus": "", "scratchpad": ""})

import threading
def load_data():
    global weather, quote, word
    weather = fetch_weather()
    quote = fetch_quote()
    word = fetch_word()
    print("Dashboard data loaded.")
threading.Thread(target=load_data, daemon=True).start()

def build_html():
    tasks_json = json.dumps(tasks)
    return f"""<!DOCTYPE html>
<html>
<head>
<title>Brandon's Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0a0a; color: #e0e0e0; font-family: 'Arial', sans-serif; min-height: 100vh; padding: 30px; }}
  h2 {{ color: #4a9eff; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; max-width: 1100px; margin: 0 auto; }}
  .card {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 20px; }}
  .card.wide {{ grid-column: span 2; }}
  .card.full {{ grid-column: span 3; }}
  #greeting {{ font-size: 26px; font-weight: bold; color: white; margin-bottom: 6px; }}
  #datetime {{ font-size: 14px; color: #888; }}
  .weather-temp {{ font-size: 42px; font-weight: bold; color: white; }}
  .weather-desc {{ color: #888; margin-top: 4px; }}
  .weather-feels {{ color: #555; font-size: 13px; margin-top: 4px; }}
  .quote-text {{ font-size: 15px; color: #ccc; line-height: 1.6; font-style: italic; }}
  .quote-author {{ color: #4a9eff; margin-top: 10px; font-size: 13px; }}
  .word {{ font-size: 22px; font-weight: bold; color: white; margin-bottom: 6px; }}
  .definition {{ color: #888; font-size: 14px; line-height: 1.5; }}
  input[type=text], textarea {{ background: #1a1a1a; border: 1px solid #2a2a2a; color: #e0e0e0; border-radius: 8px; padding: 10px; font-size: 14px; width: 100%; outline: none; }}
  input[type=text]:focus, textarea:focus {{ border-color: #4a9eff; }}
  textarea {{ resize: none; height: 100px; }}
  .add-row {{ display: flex; gap: 8px; margin-bottom: 14px; }}
  .add-row input {{ flex: 1; }}
  button {{ background: #4a9eff; color: white; border: none; border-radius: 8px; padding: 10px 16px; cursor: pointer; font-size: 14px; }}
  button:hover {{ background: #3a8eef; }}
  ul {{ list-style: none; }}
  li {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #1a1a1a; }}
  li:last-child {{ border-bottom: none; }}
  li span {{ cursor: pointer; flex: 1; font-size: 14px; }}
  li.done span {{ text-decoration: line-through; color: #444; }}
  .del {{ background: #1a1a1a; color: #555; padding: 4px 10px; font-size: 12px; border-radius: 6px; }}
  .del:hover {{ background: #e53935; color: white; }}
  #focus-input {{ font-size: 16px; }}
</style>
</head>
<body>
<div class="grid">

  <div class="card wide">
    <div id="greeting">Good day, Brandon!</div>
    <div id="datetime">Loading...</div>
  </div>

  <div class="card">
    <h2>Weather — Burnaby, BC</h2>
    <div class="weather-temp">{weather['temp']}°C</div>
    <div class="weather-desc">{weather['desc']}</div>
    <div class="weather-feels">Feels like {weather['feels']}°C</div>
  </div>

  <div class="card wide">
    <h2>Quote of the Day</h2>
    <div class="quote-text">"{quote['quote']}"</div>
    <div class="quote-author">— {quote['author']}</div>
  </div>

  <div class="card">
    <h2>Word of the Day</h2>
    <div class="word">{word['word']}</div>
    <div class="definition">{word['definition']}</div>
  </div>

  <div class="card full">
    <h2>Daily Focus — What's your one big thing today?</h2>
    <input type="text" id="focus-input" placeholder="Type your main focus for today..." value="{notes['focus']}" oninput="saveNotes()" />
  </div>

  <div class="card wide">
    <h2>To-Do List</h2>
    <div class="add-row">
      <input type="text" id="task-input" placeholder="Add a task..." />
      <button onclick="addTask()">Add</button>
    </div>
    <ul id="task-list"></ul>
  </div>

  <div class="card">
    <h2>Quick Notes</h2>
    <textarea id="scratchpad" placeholder="Jot anything here..." oninput="saveNotes()">{notes['scratchpad']}</textarea>
  </div>

</div>
<script>
  let tasks = {tasks_json};

  function updateTime() {{
    const now = new Date();
    const hour = now.getHours();
    let greet = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
    document.getElementById('greeting').textContent = greet + ", Brandon!";
    document.getElementById('datetime').textContent = now.toLocaleDateString('en-CA', {{weekday:'long', year:'numeric', month:'long', day:'numeric'}}) + ' · ' + now.toLocaleTimeString();
  }}
  setInterval(updateTime, 1000);
  updateTime();

  function render() {{
    const list = document.getElementById('task-list');
    list.innerHTML = '';
    tasks.forEach((t, i) => {{
      const li = document.createElement('li');
      if (t.done) li.classList.add('done');
      li.innerHTML = `<span onclick="toggle(${{i}})">${{t.text}}</span><button class="del" onclick="del(${{i}})">✕</button>`;
      list.appendChild(li);
    }});
  }}

  function addTask() {{
    const input = document.getElementById('task-input');
    const text = input.value.trim();
    if (!text) return;
    tasks.push({{text, done: false}});
    input.value = '';
    sync();
  }}

  function toggle(i) {{ tasks[i].done = !tasks[i].done; sync(); }}
  function del(i) {{ tasks.splice(i, 1); sync(); }}

  function sync() {{
    fetch('/save-tasks', {{method:'POST', body: JSON.stringify(tasks)}});
    render();
  }}

  function saveNotes() {{
    const focus = document.getElementById('focus-input').value;
    const scratchpad = document.getElementById('scratchpad').value;
    fetch('/save-notes', {{method:'POST', body: JSON.stringify({{focus, scratchpad}})}});
  }}

  document.getElementById('task-input').addEventListener('keydown', e => {{ if (e.key === 'Enter') addTask(); }});
  render();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(build_html().encode())

    def do_POST(self):
        global tasks, notes
        length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(length))
        if self.path == "/save-tasks":
            tasks = data
            save_json(TASKS_FILE, tasks)
        elif self.path == "/save-notes":
            notes = data
            save_json(NOTES_FILE, notes)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

PORT = int(os.environ.get("PORT", 8766))
IS_LOCAL = PORT == 8766

if IS_LOCAL:
    print("Opening dashboard... (press Ctrl+C to quit)")
    webbrowser.open(f"http://localhost:{PORT}")

HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
