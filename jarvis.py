import sys
import os

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

import tkinter as tk
from tkinter import ttk
import datetime
import threading
import math
import platform
import webbrowser
import subprocess
import re as _re
import urllib.request
import json

try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id if len(voices) > 0 else voices[0].id)
    engine.setProperty('rate', 165)
    engine.setProperty('volume', 1.0)
    HAS_TTS = True
except Exception:
    HAS_TTS = False

try:
    import speech_recognition as sr  # type: ignore[reportMissingImports]
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import wikipedia
    import wikipedia.exceptions
    HAS_WIKI = True
except ImportError:
    HAS_WIKI = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from PIL import Image, ImageTk, ImageGrab, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except ImportError:
    HAS_SBC = False

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw import AudioUtilities, IAudioEndpointVolume
    devices   = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    _vol_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
    HAS_PYCAW = True
except Exception:
    HAS_PYCAW = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

OS = platform.system()
WAKE_WORDS = ["hey lucky", "hey lucky", "hey liky", "hey lucy"]

BG         = "#0a0404"
BG1        = "#0f0505"
BG2        = "#160606"
BG3        = "#1c0808"
BORDER     = "#3a0f0f"
BORDER2    = "#5a1a0a"

RED        = "#ff2020"
RED_DIM    = "#8a0808"
RED_LO     = "#1a0404"
RED_GLOW   = "#ff4444"

ORANGE     = "#ff6a00"
ORANGE_DIM = "#8a3800"
ORANGE_LO  = "#1a0800"
ORANGE_MID = "#cc5500"

GOLD       = "#ffb300"
GOLD_DIM   = "#7a5500"
GOLD_LO    = "#1a1000"
GOLD_PALE  = "#ffd060"

AMBER      = "#ff8c00"
AMBER_DIM  = "#6a3a00"
AMBER_LO   = "#150900"

WHITE      = "#ffe8d0"
TEXT       = "#cc9980"
TEXT_DIM   = "#6a3a28"
TEXT_LO    = "#2a1410"

ARC_BLUE   = "#00aaff"
ARC_LO     = "#001a33"
ARC_DIM    = "#004477"

# ── SPEAK ──
_speak_lock = threading.Lock()
def speak(audio):
    if not HAS_TTS:
        return
    def _run():
        with _speak_lock:
            engine.say(audio)
            engine.runAndWait()
    threading.Thread(target=_run, daemon=True).start()

# ── ROOT ──
root = tk.Tk()
root.title("Lucky  v6.0")
root.geometry("1440x880")
root.configure(bg=BG)
root.resizable(True, True)

start_time = datetime.datetime.now()

FONT_MONO   = ("Courier", 10)
FONT_MONO_S = ("Courier", 9)
FONT_SM     = ("Courier", 8)
FONT_BOLD8  = ("Courier", 8,  "bold")
FONT_BOLD9  = ("Courier", 9,  "bold")
FONT_BOLD10 = ("Courier", 10, "bold")
FONT_BOLD12 = ("Courier", 12, "bold")
FONT_BOLD16 = ("Courier", 16, "bold")
FONT_BOLD22 = ("Courier", 22, "bold")
FONT_BOLD28 = ("Courier", 28, "bold")

# ═══════════════════════════════════════════
# 3D INTERFACE HELPERS
# ═══════════════════════════════════════════
def create_gradient(width, height, color1, color2, vertical=True):
    """Create a smooth gradient image from color1 to color2."""
    if not HAS_PIL:
        return None
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    for i in range(height if vertical else width):
        ratio = i / (height if vertical else width)
        r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
        g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
        b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
        if vertical:
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, height)], fill=(r, g, b))
    return ImageTk.PhotoImage(img)

class RoundedPanel(tk.Canvas):
    """A panel with rounded corners, gradient fill, bevel, and shadow."""
    def __init__(self, parent, title="", accent=ORANGE, radius=12, **kwargs):
        bg = kwargs.pop('bg', BG1)
        super().__init__(parent, bg=BG, highlightthickness=0, bd=0, **kwargs)
        self.accent = accent
        self.radius = radius
        self.title = title
        self.content = tk.Frame(self, bg=BG1)
        self._create_window = None
        self._grad_img = None
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event):
        w, h = event.width, event.height
        self.delete("panel")
        # Shadow
        self.create_rounded_rect(4, 4, w-2, h-2, self.radius, fill=TEXT_LO, outline="")
        # Main panel gradient
        grad = create_gradient(w-2, h-2, BG1, BG2)
        if grad:
            self._grad_img = grad
            self.create_rounded_rect(1, 1, w-3, h-3, self.radius, fill=BG1, outline="")
            self.create_rectangle(1, 1, w-3, h-3, fill=BG1, outline="")
            self.create_image(1, 1, image=grad, anchor='nw')
        # Bevel highlights
        self.create_rounded_rect(1, 1, w-3, h-3, self.radius, fill=None, outline=BG2, width=1)
        self.create_rounded_rect(2, 2, w-4, h-4, self.radius, fill=None, outline=self.accent, width=1)
        self.create_rounded_rect(0, 0, w-1, h-1, self.radius, fill=None, outline=BORDER2, width=1)
        # Title bar
        self.create_text(12, 12, text=f"◉  {self.title}", anchor='w', font=FONT_BOLD8, fill=self.accent)
        # Redraw content window on top
        if self._create_window:
            self.coords(self._create_window, 4, 20)
            self.itemconfig(self._create_window, width=max(10, w-8), height=max(10, h-24))
        else:
            self._create_window = self.create_window(4, 20, window=self.content, anchor='nw',
                                                     width=max(10, w-8), height=max(10, h-24))
        self.tag_lower("panel")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                  x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                  x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                  x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        self.create_polygon(points, smooth=True, **kwargs)

class GlowButton(tk.Canvas):
    def __init__(self, parent, text, command=None, accent=ORANGE, bg=BG2, height=30, **kwargs):
        super().__init__(parent, height=height, bg=BG, highlightthickness=0)
        self.text = text
        self.command = command
        self.accent = accent
        self.bg = bg
        self._grad_img = None
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._draw(hover=False)

    def _draw(self, hover):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        # Shadow
        self.create_rounded_rect(2, 2, w-2, h-2, 6, fill=TEXT_LO, outline="")
        # Main button gradient
        grad = create_gradient(w-4, h-4, self.bg, self.accent if hover else BG1)
        if grad:
            self._grad_img = grad
            self.create_image(2, 2, image=grad, anchor='nw')
        # Border
        self.create_rounded_rect(1, 1, w-3, h-3, 6, outline=self.accent, width=1)
        self.create_rounded_rect(0, 0, w-1, h-1, 6, outline=BORDER2, width=1)
        # Text
        self.create_text(w//2, h//2, text=self.text, font=FONT_BOLD9,
                         fill=self.accent if not hover else WHITE)

    def _on_enter(self, e):
        self._draw(hover=True)

    def _on_leave(self, e):
        self._draw(hover=False)

    def _on_click(self, e):
        if self.command:
            self.command()

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                  x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                  x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                  x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        self.create_polygon(points, smooth=True, **kwargs)

# ── HEADER ──
header = tk.Frame(root, bg=BG1, height=72)
header.pack(fill=tk.X, side=tk.TOP)
header.pack_propagate(False)
tk.Frame(root, bg=RED_DIM, height=1).pack(fill=tk.X)

logo_area = tk.Frame(header, bg=BG1)
logo_area.pack(side=tk.LEFT, padx=14, pady=8)

logo_canvas = tk.Canvas(logo_area, width=54, height=54, bg=BG1, highlightthickness=0)
logo_canvas.pack(side=tk.LEFT)

logo_angle = [0]

def draw_logo():
    c = logo_canvas
    c.delete("all")
    cx, cy = 27, 27
    # Outer rotating ring
    for i in range(12):
        angle = logo_angle[0] + i * 30
        rad = math.radians(angle)
        x1 = cx + 22 * math.cos(rad)
        y1 = cy - 22 * math.sin(rad)
        x2 = cx + 26 * math.cos(rad)
        y2 = cy - 26 * math.sin(rad)
        col = RED if i % 2 == 0 else ORANGE
        c.create_line(x1, y1, x2, y2, fill=col, width=2)
    # Inner arc reactor with pulsing
    pulse = 2 + (math.sin(logo_angle[0] * 0.1) + 1) / 2 * 6
    c.create_oval(cx-14, cy-14, cx+14, cy+14, fill=ARC_LO, outline=ARC_DIM, width=2)
    c.create_oval(cx-10, cy-10, cx+10, cy+10, fill=ARC_LO, outline=ARC_BLUE, width=1)
    c.create_oval(cx-pulse, cy-pulse, cx+pulse, cy+pulse, fill=ARC_BLUE, outline="")
    # Corner rivets
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle + logo_angle[0])
        dx = cx + 23 * math.cos(rad)
        dy = cy - 23 * math.sin(rad)
        c.create_oval(dx-2, dy-2, dx+2, dy+2, fill=GOLD, outline="")
    logo_angle[0] = (logo_angle[0] + 3) % 360
    root.after(50, draw_logo)

title_frame = tk.Frame(logo_area, bg=BG1)
title_frame.pack(side=tk.LEFT, padx=12)
tk.Label(title_frame, text="J.A.R.V.I.S",
         font=("Courier", 28, "bold"), bg=BG1, fg=ORANGE).pack(anchor="w")
tk.Label(title_frame, text="IRON MAN NEURAL INTERFACE  //  v6.0",
         font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(anchor="w")

# ── Status dots ──
dots_f = tk.Frame(header, bg=BG1)
dots_f.pack(side=tk.LEFT, padx=24, pady=10)
for label, color in [
    ("VOICE",   ORANGE if HAS_TTS    else RED),
    ("SPEECH",  GOLD   if HAS_SR     else RED),
    ("MONITOR", ORANGE if HAS_PSUTIL else GOLD),
    ("AUDIO",   GOLD   if HAS_PYCAW  else RED_DIM),
]:
    r = tk.Frame(dots_f, bg=BG1)
    r.pack(anchor="w", pady=1)
    dc = tk.Canvas(r, width=10, height=10, bg=BG1, highlightthickness=0)
    dc.pack(side=tk.LEFT)
    dc.create_oval(1, 1, 9, 9, fill=color,  outline=BG1, width=1)
    dc.create_oval(3, 3, 7, 7, fill=WHITE,  outline="")
    tk.Label(r, text=f" {label}", font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(side=tk.LEFT)

# ── Clock (right side) ──
clock_f = tk.Frame(header, bg=BG1)
clock_f.pack(side=tk.RIGHT, padx=20, pady=6)
hud_time_var   = tk.StringVar(value="--:--:--")
hud_date_var   = tk.StringVar(value="--- -- ----")
hud_uptime_var = tk.StringVar(value="UP 00:00")
tk.Label(clock_f, textvariable=hud_time_var,
         font=("Courier", 28, "bold"), bg=BG1, fg=ORANGE).pack(anchor="e")
tk.Label(clock_f, textvariable=hud_date_var,
         font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(anchor="e")
tk.Label(clock_f, textvariable=hud_uptime_var,
         font=FONT_SM, bg=BG1, fg=GOLD_DIM).pack(anchor="e")

# ── Status strip ──
status_strip = tk.Frame(root, bg=BG2, height=22)
status_strip.pack(fill=tk.X)
status_strip.pack_propagate(False)
tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)

status_mode_var = tk.StringVar(value="STANDBY")
mode_lbl = tk.Label(status_strip, textvariable=status_mode_var,
                    font=FONT_BOLD8, bg=RED_LO, fg=ORANGE, padx=10, width=12)
mode_lbl.pack(side=tk.LEFT)
tk.Frame(status_strip, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

status_msg_var = tk.StringVar(value="SYSTEM ONLINE  //  ARC REACTOR STABLE  //  MARK VI READY")
tk.Label(status_strip, textvariable=status_msg_var,
         font=FONT_SM, bg=BG2, fg=TEXT_DIM, padx=8).pack(side=tk.LEFT)

tk.Label(status_strip, text="◉  STARK INDUSTRIES AI CORE  ◉  ALL SYSTEMS NOMINAL  ◉",
         font=FONT_SM, bg=BG2, fg=TEXT_LO).pack(side=tk.RIGHT, padx=6)

def set_status(mode, color, msg):
    bg_lo = {
        ORANGE: ORANGE_LO, RED:  RED_LO, GOLD:  GOLD_LO,
        ARC_BLUE: ARC_LO,  AMBER: AMBER_LO
    }.get(color, BG2)
    root.after(0, lambda: status_mode_var.set(mode))
    root.after(0, lambda: status_msg_var.set(msg))
    root.after(0, lambda: mode_lbl.config(fg=color, bg=bg_lo))

# ── 3D PANEL FACTORY ──
def make_widget(parent, row, col, rowspan=1, colspan=1, title="", accent=ORANGE):
    panel = RoundedPanel(parent, title=title, accent=accent, bg=BG1)
    panel.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
               sticky="nsew", padx=1, pady=1)
    return panel.content

body = tk.Frame(root, bg=BORDER)
body.pack(fill=tk.BOTH, expand=True)
body.columnconfigure(0, weight=3)
body.columnconfigure(1, weight=2)
body.columnconfigure(2, weight=2)
body.rowconfigure(0, weight=3)
body.rowconfigure(1, weight=2)

log_c = make_widget(body, 0, 0, rowspan=2, title="◉  OPERATION LOG", accent=ORANGE)

output_area = tk.Text(
    log_c, bg=BG1, fg=TEXT, font=FONT_MONO_S,
    state=tk.DISABLED, bd=0, relief=tk.FLAT,
    padx=10, pady=6, spacing1=2, spacing3=2,
    selectbackground=ORANGE_LO, wrap=tk.WORD,
    insertbackground=ORANGE)
output_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
log_scroll = tk.Scrollbar(log_c, command=output_area.yview,
                           bg=BG1, troughcolor=BG, width=4, relief=tk.FLAT)
log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
output_area.config(yscrollcommand=log_scroll.set)

for tag, fg, bg in [
    ("ts",     TEXT_LO,   None),
    ("user",   GOLD,      GOLD_LO),
    ("info",   ORANGE,    ORANGE_LO),
    ("result", TEXT,      BG2),
    ("warn",   RED,       RED_LO),
    ("system", TEXT_DIM,  None),
    ("head",   ORANGE,    None),
    ("arc",    ARC_BLUE,  ARC_LO),
]:
    kw = dict(foreground=fg)
    if bg: kw["background"] = bg
    output_area.tag_config(tag, **kw)

def log(text, tag="system"):
    def _do():
        output_area.config(state=tk.NORMAL)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        output_area.insert(tk.END, f" {ts}  ", "ts")
        output_area.insert(tk.END, f"{text}\n", tag)
        output_area.see(tk.END)
        output_area.config(state=tk.DISABLED)
    root.after(0, _do)

weather_c = make_widget(body, 0, 1, title="◉  WEATHER & ENVIRONMENT", accent=GOLD)

inner_clock_f = tk.Frame(weather_c, bg=BG1)
inner_clock_f.pack(fill=tk.X, padx=8, pady=(6, 2))

panel_time_var = tk.StringVar(value="--:--")
panel_date_var = tk.StringVar(value="LOADING...")
tk.Label(inner_clock_f, textvariable=panel_time_var,
         font=("Courier", 32, "bold"), bg=BG1, fg=GOLD).pack(anchor="center")
tk.Label(inner_clock_f, textvariable=panel_date_var,
         font=FONT_BOLD9, bg=BG1, fg=TEXT_DIM).pack(anchor="center")

tk.Frame(weather_c, bg=BORDER, height=1).pack(fill=tk.X, padx=8, pady=4)

wx_canvas = tk.Canvas(weather_c, width=280, height=80,
                       bg=BG1, highlightthickness=0)
wx_canvas.pack(padx=8, pady=2)

wx_temp_var = tk.StringVar(value="FETCHING WEATHER...")
wx_desc_var = tk.StringVar(value="")
wx_loc_var  = tk.StringVar(value="")

wx_temp_lbl = tk.Label(weather_c, textvariable=wx_temp_var,
                        font=FONT_BOLD10, bg=BG1, fg=ORANGE)
wx_temp_lbl.pack(anchor="center")
tk.Label(weather_c, textvariable=wx_desc_var,
         font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(anchor="center")
tk.Label(weather_c, textvariable=wx_loc_var,
         font=FONT_SM, bg=BG1, fg=TEXT_LO).pack(anchor="center")

wx_extra_var = tk.StringVar(value="")
tk.Label(weather_c, textvariable=wx_extra_var,
         font=FONT_SM, bg=BG1, fg=GOLD_DIM).pack(anchor="center")

def draw_weather_art(condition=""):
    wx_canvas.delete("all")
    c = wx_canvas
    cond = condition.lower()

    if "clear" in cond or "sunny" in cond:
        cx, cy = 50, 40
        c.create_oval(cx-18, cy-18, cx+18, cy+18, fill=GOLD, outline=ORANGE, width=2)
        for a in range(0, 360, 45):
            r1, r2 = 22, 32
            rad = math.radians(a)
            x1 = cx + r1*math.cos(rad); y1 = cy - r1*math.sin(rad)
            x2 = cx + r2*math.cos(rad); y2 = cy - r2*math.sin(rad)
            c.create_line(x1, y1, x2, y2, fill=GOLD, width=2)
        c.create_text(140, 25, text="CLEAR SKIES", font=FONT_BOLD9, fill=GOLD, anchor="center")
        c.create_text(140, 45, text="OPTIMAL FLIGHT CONDITIONS", font=FONT_SM, fill=TEXT_DIM, anchor="center")
        c.create_text(140, 62, text="◉ ARC REACTOR AT 100%", font=FONT_SM, fill=ORANGE, anchor="center")

    elif "cloud" in cond or "overcast" in cond:
        for ox, oy, r in [(45,45,14),(60,38,18),(78,42,14),(90,47,12)]:
            c.create_oval(ox-r,oy-r,ox+r,oy+r, fill=TEXT_DIM, outline="")
        c.create_text(180, 30, text="CLOUDY", font=FONT_BOLD9, fill=TEXT, anchor="center")
        c.create_text(180, 48, text="REDUCED VISIBILITY", font=FONT_SM, fill=TEXT_DIM, anchor="center")
        c.create_text(180, 64, text="◉ SUIT SENSORS COMPENSATING", font=FONT_SM, fill=ORANGE, anchor="center")

    elif "rain" in cond or "drizzle" in cond:
        for ox, oy, r in [(45,35,13),(60,28,17),(77,32,13),(88,37,11)]:
            c.create_oval(ox-r,oy-r,ox+r,oy+r, fill=TEXT_DIM, outline="")
        for i in range(8):
            rx = 30 + i*10; ry = 52
            c.create_line(rx, ry, rx-4, ry+12, fill=ARC_BLUE, width=2)
        c.create_text(180, 35, text="RAIN", font=FONT_BOLD9, fill=ARC_BLUE, anchor="center")
        c.create_text(180, 52, text="PRECIPITATION DETECTED", font=FONT_SM, fill=TEXT_DIM, anchor="center")
        c.create_text(180, 68, text="◉ SUIT SEALED & WEATHERPROOF", font=FONT_SM, fill=ORANGE, anchor="center")

    elif "snow" in cond:
        for i in range(10):
            sx = 20+i*13; sy = 50 + (i%3)*8
            c.create_text(sx, sy, text="❄", font=("Courier",8), fill=ARC_BLUE)
        c.create_text(180, 30, text="SNOW", font=FONT_BOLD9, fill=ARC_BLUE, anchor="center")
        c.create_text(180, 48, text="LOW TEMPERATURE ALERT", font=FONT_SM, fill=TEXT_DIM, anchor="center")
        c.create_text(180, 64, text="◉ HEATING SYSTEMS ACTIVE", font=FONT_SM, fill=ORANGE, anchor="center")

    elif "thunder" in cond or "storm" in cond:
        pts = [40,20, 55,20, 45,38, 58,38, 38,65, 50,42, 38,42, 48,22]
        c.create_polygon(pts, fill=GOLD, outline=ORANGE)
        c.create_text(175, 30, text="THUNDERSTORM", font=FONT_BOLD9, fill=GOLD, anchor="center")
        c.create_text(175, 48, text="SEVERE WEATHER ALERT", font=FONT_SM, fill=RED, anchor="center")
        c.create_text(175, 64, text="◉ SEEKING SHELTER ADVISED", font=FONT_SM, fill=ORANGE, anchor="center")

    elif "mist" in cond or "fog" in cond or "haze" in cond:
        for y in [25,38,51,64]:
            c.create_line(10, y, 120, y, fill=TEXT_DIM, width=2, dash=(6,4))
        c.create_text(185, 35, text="MIST / FOG", font=FONT_BOLD9, fill=TEXT_DIM, anchor="center")
        c.create_text(185, 52, text="LOW VISIBILITY", font=FONT_SM, fill=TEXT_DIM, anchor="center")
        c.create_text(185, 68, text="◉ RADAR ONLINE", font=FONT_SM, fill=ORANGE, anchor="center")

    else:
        c.create_oval(30,20,70,60, fill=ARC_LO, outline=ARC_BLUE, width=2)
        c.create_oval(40,30,60,50, fill=ARC_BLUE, outline="")
        c.create_text(175, 40, text="CHECKING CONDITIONS...", font=FONT_BOLD9, fill=TEXT_DIM, anchor="center")

_weather_cache = {}

def fetch_weather():
    try:
        url = "https://wttr.in/?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/6.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        current  = data["current_condition"][0]
        area     = data["nearest_area"][0]
        temp_c   = int(current["temp_C"])
        temp_f   = int(current["temp_F"])
        desc     = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_kph = current["windspeedKmph"]
        feels_c  = current["FeelsLikeC"]
        city     = area["areaName"][0]["value"]
        country  = area["country"][0]["value"]
        _weather_cache.update({
            "temp_c": temp_c, "temp_f": temp_f, "desc": desc,
            "humidity": humidity, "wind_kph": wind_kph,
            "feels_c": feels_c, "city": city, "country": country
        })
        root.after(0, lambda: wx_temp_var.set(f"  {temp_c}°C  /  {temp_f}°F"))
        root.after(0, lambda: wx_desc_var.set(desc.upper()))
        root.after(0, lambda: wx_loc_var.set(f"{city}, {country}"))
        root.after(0, lambda: wx_extra_var.set(
            f"FEELS {feels_c}°C  ·  HUMIDITY {humidity}%  ·  WIND {wind_kph} KM/H"
        ))
        root.after(0, lambda d=desc: draw_weather_art(d))
        log(f"Weather updated: {temp_c}°C  {desc}  —  {city}", "arc")
    except Exception as e:
        root.after(0, lambda: wx_temp_var.set("WEATHER UNAVAILABLE"))
        root.after(0, lambda: wx_desc_var.set("CHECK NETWORK CONNECTION"))
        root.after(0, lambda: draw_weather_art(""))

def refresh_weather():
    threading.Thread(target=fetch_weather, daemon=True).start()
    root.after(600_000, refresh_weather)

# ── NETWORK STATUS ──
net_c = make_widget(body, 1, 1, title="◉  NETWORK STATUS", accent=ARC_BLUE)

net_canvas = tk.Canvas(net_c, width=60, height=60, bg=BG1, highlightthickness=0)
net_canvas.pack(side=tk.LEFT, padx=8, pady=6)

def draw_net_icon(up=True):
    c = net_canvas; c.delete("all")
    col = ARC_BLUE if up else RED
    cx, cy = 30, 30
    for i, r in enumerate([26, 18, 10]):
        c.create_arc(cx-r, cy-r, cx+r, cy+r, start=30, extent=120,
                     outline=col if (i < 2 if up else False) else RED_DIM,
                     width=2, style="arc")
    c.create_oval(cx-3, cy-3, cx+3, cy+3, fill=col, outline="")

net_info_f = tk.Frame(net_c, bg=BG1)
net_info_f.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
net_text = tk.Text(net_info_f, bg=BG1, fg=TEXT_DIM, font=FONT_SM,
                   state=tk.DISABLED, bd=0, relief=tk.FLAT,
                   padx=4, pady=4, wrap=tk.WORD)
net_text.pack(fill=tk.BOTH, expand=True)

def refresh_network():
    if not HAS_PSUTIL:
        return
    lines = []
    up_found = False
    for iface, stat in psutil.net_if_stats().items():
        if stat.isup:
            up_found = True
            ips = [a.address for a in psutil.net_if_addrs().get(iface, [])
                   if ":" not in a.address]
            lines.append(f" ◉ {iface}: UP  {', '.join(ips) if ips else 'no IP'}")
    io = psutil.net_io_counters()
    lines.append(f" ↑ SENT: {io.bytes_sent//1024**2} MB")
    lines.append(f" ↓ RECV: {io.bytes_recv//1024**2} MB")
    root.after(0, lambda: draw_net_icon(up_found))
    net_text.config(state=tk.NORMAL)
    net_text.delete("1.0", tk.END)
    for l in lines:
        net_text.insert(tk.END, l + "\n")
    net_text.config(state=tk.DISABLED)
    root.after(5000, refresh_network)

# ── VOICE CONTROL ──
voice_c = make_widget(body, 0, 2, title="◉  VOICE CONTROL", accent=ORANGE)

radar_canvas = tk.Canvas(voice_c, width=140, height=140,
                          bg=BG1, highlightthickness=0)
radar_canvas.pack(pady=6)

radar_angle  = [0]
radar_active = [False]

def draw_radar():
    radar_canvas.delete("all")
    cx, cy, r = 70, 70, 58
    # Perspective ellipse
    radar_canvas.create_oval(cx-20, cy-58, cx+20, cy+58, outline=RED_DIM, width=1, dash=(2,2))
    radar_canvas.create_oval(cx-40, cy-45, cx+40, cy+45, outline=RED_DIM, width=1)
    # Concentric rings
    for i in range(1, 5):
        rr = r * i // 4
        radar_canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, outline=RED_DIM if i < 4 else RED, width=1)
    # Crosshairs
    radar_canvas.create_line(cx-r, cy, cx+r, cy, fill=BORDER, width=1)
    radar_canvas.create_line(cx, cy-r, cx, cy+r, fill=BORDER, width=1)
    radar_canvas.create_line(cx-r, cy, cx+r, cy, fill=TEXT_LO, width=1)
    if radar_active[0]:
        a = radar_angle[0]
        for arc_i in range(10):
            alpha = a - arc_i * 7
            radar_canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                                     start=alpha, extent=7,
                                     outline="", fill=ORANGE_LO if arc_i > 0 else ORANGE_DIM,
                                     style=tk.PIESLICE)
        rad = math.radians(a)
        x2 = cx + r * math.cos(rad)
        y2 = cy - r * math.sin(rad)
        radar_canvas.create_line(cx, cy, x2, y2, fill=ORANGE, width=2)
        radar_angle[0] = (radar_angle[0] + 5) % 360
    # Core
    radar_canvas.create_oval(cx-10, cy-10, cx+10, cy+10, fill=ARC_LO, outline=ARC_DIM, width=2)
    radar_canvas.create_oval(cx-5,  cy-5,  cx+5,  cy+5,  fill=ARC_BLUE, outline="")
    root.after(50, draw_radar)

voice_status_var = tk.StringVar(value="STANDBY")
voice_status_lbl = tk.Label(voice_c, textvariable=voice_status_var,
                              font=FONT_BOLD9, bg=BG1, fg=TEXT_DIM)
voice_status_lbl.pack()

def set_voice_status(text, color):
    root.after(0, lambda: voice_status_var.set(text))
    root.after(0, lambda: voice_status_lbl.config(fg=color))

mic_btn = GlowButton(voice_c, text="◉  SPEAK NOW", command=lambda: start_voice_thread(),
                     accent=ORANGE, height=30)
mic_btn.pack(fill=tk.X, padx=8, pady=2)

wake_on  = [True]
wake_btn = GlowButton(voice_c, text="◉  WAKE WORD: ON",
                      accent=RED_GLOW, height=30)
wake_btn.pack(fill=tk.X, padx=8, pady=2)

def toggle_wake():
    wake_on[0] = not wake_on[0]
    if wake_on[0]:
        wake_btn.text   = "◉  WAKE WORD: ON "
        wake_btn.accent = RED_GLOW
        log("Wake word listener ENABLED.", "info")
    else:
        wake_btn.text   = "◉  WAKE WORD: OFF"
        wake_btn.accent = TEXT_DIM
        log("Wake word listener PAUSED.", "warn")
    wake_btn._draw(hover=False)
wake_btn.command = toggle_wake

tk.Label(voice_c, text='SAY  "HEY JARVIS"  TO ACTIVATE',
         font=FONT_SM, bg=BG1, fg=TEXT_LO).pack(pady=2)

ww_frame = tk.Frame(voice_c, bg=BG1)
ww_frame.pack(fill=tk.X, padx=10, pady=4)
tk.Label(ww_frame, text="WAKE WORDS:", font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(anchor="w")
for ww in ["Hey JARVIS", "JARVIS", "Hey Davis"]:
    wr = tk.Frame(ww_frame, bg=BG1)
    wr.pack(fill=tk.X)
    wc = tk.Canvas(wr, width=8, height=8, bg=BG1, highlightthickness=0)
    wc.pack(side=tk.LEFT, pady=2)
    wc.create_oval(1,1,7,7,outline=ORANGE_DIM, width=1)
    wc.create_oval(3,3,5,5,fill=ORANGE_DIM,    outline="")
    tk.Label(wr, text=f"  {ww}", font=FONT_SM, bg=BG1, fg=TEXT_DIM).pack(side=tk.LEFT)


def send_text_cmd():
    val = cmd_entry.get().strip()
    if not val:
        return
    cmd_entry.delete(0, tk.END)
    log(f"◉ INPUT › {val}", "user")
    process_query(val)

# ── COMMAND INPUT ──
inp_c = make_widget(body, 1, 2, title="◉  COMMAND INPUT", accent=GOLD)

tk.Label(inp_c, text="ENTER COMMAND:", font=FONT_SM, bg=BG1,
         fg=TEXT_DIM, anchor="w").pack(fill=tk.X, padx=8, pady=(5, 1))

cmd_entry = tk.Entry(inp_c, bg=BG3, fg=GOLD, font=FONT_MONO_S,
                     insertbackground=GOLD, relief=tk.FLAT, bd=0,
                     highlightthickness=1, highlightbackground=BORDER2,
                     highlightcolor=GOLD)
cmd_entry.pack(fill=tk.X, padx=8, pady=(0, 3), ipady=5)
cmd_entry.bind("<Return>", lambda e: send_text_cmd())

exec_btn = GlowButton(inp_c, text="◉  EXECUTE COMMAND", command=send_text_cmd,
                      accent=GOLD, height=30)
exec_btn.pack(fill=tk.X, padx=8, pady=(0, 4))

tk.Frame(inp_c, bg=BORDER, height=1).pack(fill=tk.X, padx=8)
tk.Label(inp_c, text="QUICK ACCESS:", font=FONT_SM, bg=BG1,
         fg=TEXT_LO, anchor="w").pack(fill=tk.X, padx=8, pady=(4, 1))

for s in ["battery", "system info", "screenshot", "time", "help", "network", "top processes"]:
    def _make_sugg(ss):
        bf = tk.Frame(inp_c, bg=BG1)
        bf.pack(fill=tk.X, padx=8)
        bc = tk.Canvas(bf, width=8, height=8, bg=BG1, highlightthickness=0)
        bc.pack(side=tk.LEFT, pady=2, padx=(0, 2))
        bc.create_oval(1,1,7,7, outline=RED_DIM, width=1)
        bc.create_oval(3,3,5,5, fill=RED_DIM, outline="")
        b = tk.Button(bf, text=ss, font=FONT_SM,
                      bg=BG1, fg=TEXT_DIM,
                      activebackground=BG2, activeforeground=GOLD,
                      bd=0, relief=tk.FLAT, anchor="w",
                      padx=4, pady=2, cursor="hand2",
                      command=lambda x=ss: quick_cmd(x))
        b.pack(side=tk.LEFT, fill=tk.X, expand=True)
        b.bind("<Enter>", lambda e, bb=b, f=bf: (bb.config(fg=GOLD, bg=BG2), f.config(bg=BG2)))
        b.bind("<Leave>", lambda e, bb=b, f=bf: (bb.config(fg=TEXT_DIM, bg=BG1), f.config(bg=BG1)))
    _make_sugg(s)

# ── BOTTOM BAR ──
tk.Frame(root, bg=BORDER2, height=1).pack(fill=tk.X)
bottom = tk.Frame(root, bg=BG1, height=20)
bottom.pack(fill=tk.X, side=tk.BOTTOM)
bottom.pack_propagate(False)
tk.Label(bottom,
         text=(f"OS:{OS}  psutil:{'✔' if HAS_PSUTIL else '✘'}  "
               f"voice:{'✔' if HAS_TTS else '✘'}  "
               f"SR:{'✔' if HAS_SR else '✘'}  "
               f"pycaw:{'✔' if HAS_PYCAW else '✘'}  "
               f"brightness:{'✔' if HAS_SBC else '✘'}"),
         font=FONT_SM, bg=BG1, fg=TEXT_LO, padx=12).pack(side=tk.LEFT)
tk.Label(bottom, text="JARVIS v6.0  //  STARK INDUSTRIES  //  IRON MAN INTERFACE",
         font=FONT_SM, bg=BG1, fg=TEXT_LO, padx=12).pack(side=tk.RIGHT)

# ═══════════════════════════════════════════
# LAPTOP CONTROL FUNCTIONS
# ═══════════════════════════════════════════
def get_battery_info():
    if not HAS_PSUTIL: return "psutil not installed."
    bat = psutil.sensors_battery()
    if bat is None: return "No battery detected."
    plug = "Plugged in ⚡" if bat.power_plugged else "On battery 🔋"
    secs = bat.secsleft
    if secs == psutil.POWER_TIME_UNLIMITED: tl = "Charging"
    elif secs == psutil.POWER_TIME_UNKNOWN: tl = "Unknown"
    else:
        h, m = divmod(secs // 60, 60)
        tl = f"{h}h {m}m remaining"
    return f"Battery: {bat.percent:.0f}%  |  {plug}  |  {tl}"

def set_volume(level):
    level = max(0, min(100, int(level)))
    if OS == "Windows":
        if HAS_PYCAW:
            _vol_ctrl.SetMasterVolumeLevelScalar(level / 100, None)
            return f"Volume set to {level}%"
        subprocess.run(["nircmd","setsysvolume",str(int(level*655.35))],capture_output=True)
        return f"Volume set to {level}%"
    elif OS == "Linux":
        subprocess.run(["amixer","-q","sset","Master",f"{level}%"],capture_output=True)
        return f"Volume set to {level}%"
    elif OS == "Darwin":
        subprocess.run(["osascript","-e",f"set volume output volume {level}"],capture_output=True)
        return f"Volume set to {level}%"
    return "Volume control unavailable."

def get_volume():
    if OS == "Windows" and HAS_PYCAW:
        return f"Current volume: {int(_vol_ctrl.GetMasterVolumeLevelScalar()*100)}%"
    return "Volume check unavailable."

def mute_volume():
    if OS == "Windows" and HAS_PYCAW:
        _vol_ctrl.SetMute(1, None); return "Muted."
    elif OS == "Linux":
        subprocess.run(["amixer","-q","sset","Master","mute"],capture_output=True); return "Muted."
    elif OS == "Darwin":
        subprocess.run(["osascript","-e","set volume output muted true"],capture_output=True); return "Muted."
    return "Mute unavailable."

def unmute_volume():
    if OS == "Windows" and HAS_PYCAW:
        _vol_ctrl.SetMute(0, None); return "Unmuted."
    elif OS == "Linux":
        subprocess.run(["amixer","-q","sset","Master","unmute"],capture_output=True); return "Unmuted."
    elif OS == "Darwin":
        subprocess.run(["osascript","-e","set volume output muted false"],capture_output=True); return "Unmuted."
    return "Unmute unavailable."

def set_brightness(level):
    level = max(0, min(100, int(level)))
    if HAS_SBC:
        try: sbc.set_brightness(level); return f"Brightness set to {level}%"
        except Exception as e: return f"Brightness error: {e}"
    if OS == "Windows":
        ps = (f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
              f".WmiSetBrightness(1,{level})")
        subprocess.run(["powershell","-Command",ps],capture_output=True)
        return f"Brightness set to {level}%"
    return "Install screen-brightness-control."

def get_brightness():
    if HAS_SBC:
        try: return f"Brightness: {sbc.get_brightness()[0]}%"
        except Exception as e: return f"Error: {e}"
    return "Install screen-brightness-control."

def take_screenshot():
    folder = os.path.join(os.path.expanduser("~"), "Pictures", "JARVIS_Screenshots")
    os.makedirs(folder, exist_ok=True)
    fname = datetime.datetime.now().strftime("shot_%Y%m%d_%H%M%S.png")
    path  = os.path.join(folder, fname)
    if HAS_PIL:
        ImageGrab.grab().save(path); return f"Screenshot saved → {path}"
    if OS == "Windows":
        ps = (f"Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
              f"$b=New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::"
              f"PrimaryScreen.Bounds.Width,[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);"
              f"$g=[System.Drawing.Graphics]::FromImage($b);"
              f"$g.CopyFromScreen(0,0,0,0,$b.Size);$b.Save('{path}')")
        subprocess.run(["powershell","-Command",ps],capture_output=True)
        return f"Screenshot saved → {path}"
    elif OS == "Linux":
        subprocess.run(["scrot",path],capture_output=True); return f"Screenshot → {path}"
    elif OS == "Darwin":
        subprocess.run(["screencapture",path],capture_output=True); return f"Screenshot → {path}"
    return "Screenshot failed."

def get_system_info():
    lines = [f"OS      : {platform.system()} {platform.release()} ({platform.machine()})"]
    if HAS_PSUTIL:
        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        bat  = psutil.sensors_battery()
        lines += [
            f"CPU     : {cpu}%  ({psutil.cpu_count()} cores)",
            f"RAM     : {ram.percent}%  ({ram.used//1024**3}/{ram.total//1024**3} GB)",
            f"Disk    : {disk.percent}%  ({disk.used//1024**3}/{disk.total//1024**3} GB)",
        ]
        if bat:
            lines.append(f"Battery : {bat.percent:.0f}%  "
                         f"{'⚡ Charging' if bat.power_plugged else '🔋 Discharging'}")
    if _weather_cache:
        lines.append(f"Weather : {_weather_cache.get('temp_c','?')}°C  "
                     f"{_weather_cache.get('desc','?')}  "
                     f"@ {_weather_cache.get('city','?')}")
    return "\n".join(lines)

def get_network_info():
    if not HAS_PSUTIL: return "psutil not installed."
    lines = []
    for iface, stat in psutil.net_if_stats().items():
        if stat.isup:
            ips = [a.address for a in psutil.net_if_addrs().get(iface, [])
                   if ":" not in a.address]
            lines.append(f"  {iface}: UP  {', '.join(ips) if ips else 'no IP'}")
    io = psutil.net_io_counters()
    lines.append(f"  Sent: {io.bytes_sent//1024**2} MB  |  Recv: {io.bytes_recv//1024**2} MB")
    return "Network:\n" + ("\n".join(lines) if lines else "  No active interfaces")

def list_top_processes():
    if not HAS_PSUTIL: return "psutil not installed."
    procs = sorted(psutil.process_iter(['name','cpu_percent','memory_percent']),
                   key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:6]
    lines = ["Top processes by CPU:"]
    for p in procs:
        lines.append(f"  {p.info['name'][:22]:<22}  "
                     f"CPU:{p.info['cpu_percent']:5.1f}%  "
                     f"RAM:{p.info['memory_percent']:.1f}%")
    return "\n".join(lines)

def kill_process(name):
    if not HAS_PSUTIL: return "psutil not installed."
    killed = []
    for p in psutil.process_iter(['name']):
        if name.lower() in (p.info['name'] or "").lower():
            p.kill(); killed.append(p.info['name'])
    return f"Killed: {', '.join(killed)}" if killed else f"No process '{name}' found."

def system_sleep():
    if OS == "Windows": subprocess.run(["rundll32.exe","powrprof.dll,SetSuspendState","0","1","0"])
    elif OS == "Linux":  subprocess.run(["systemctl","suspend"])
    elif OS == "Darwin": subprocess.run(["pmset","sleepnow"])
    return "Sleeping..."

def system_lock():
    if OS == "Windows": subprocess.run(["rundll32.exe","user32.dll,LockWorkStation"])
    elif OS == "Linux":  subprocess.run(["xdg-screensaver","lock"])
    return "Locked."

def system_shutdown_os():
    log("⚠ SHUTDOWN in 30s. Type 'cancel shutdown' to abort.", "warn")
    speak("Warning. Shutting down in 30 seconds.")
    if OS == "Windows": subprocess.run(["shutdown","/s","/t","30"])
    else:               subprocess.run(["shutdown","-h","+0.5"])
    return "Shutdown scheduled."

def cancel_shutdown():
    if OS == "Windows": subprocess.run(["shutdown","/a"],capture_output=True)
    else:               subprocess.run(["shutdown","-c"],capture_output=True)
    return "Shutdown cancelled."

def system_restart():
    log("⚠ RESTART in 30s.", "warn")
    speak("Warning. Restarting in 30 seconds.")
    if OS == "Windows": subprocess.run(["shutdown","/r","/t","30"])
    else:               subprocess.run(["shutdown","-r","+0.5"])
    return "Restart scheduled."

APP_MAP = {
    "notepad":"notepad.exe","calculator":"calc.exe","paint":"mspaint.exe",
    "task manager":"taskmgr.exe","file explorer":"explorer.exe","control panel":"control.exe",
    "cmd":"cmd.exe","powershell":"powershell.exe","word":"winword.exe","excel":"excel.exe",
    "chrome":"chrome.exe","firefox":"firefox.exe","edge":"msedge.exe",
    "vlc":"vlc.exe","spotify":"spotify.exe","discord":"discord.exe",
    "vscode":"code.exe","vs code":"code.exe",
}

def open_app(name):
    name = name.strip().lower()
    if OS == "Windows":
        exe = APP_MAP.get(name)
        if exe:
            try: subprocess.Popen(exe); return f"Launching {name}..."
            except FileNotFoundError: return f"{name} not found."
        return f"Unknown app '{name}'."
    elif OS == "Linux":  subprocess.Popen([name]); return f"Launching {name}..."
    elif OS == "Darwin": subprocess.Popen(["open","-a",name]); return f"Launching {name}..."
    return "Unsupported OS."

def safe_calculate(expr):
    allowed = set("0123456789+-*/(). ")
    if all(c in allowed for c in expr): return eval(expr)
    raise ValueError("Unsafe expression")

def get_weather_cmd():
    if _weather_cache:
        return (f"Weather: {_weather_cache['temp_c']}°C / {_weather_cache['temp_f']}°F  "
                f"— {_weather_cache['desc']}  @ {_weather_cache['city']}, "
                f"{_weather_cache['country']}\n"
                f"  Feels like {_weather_cache['feels_c']}°C  "
                f"Humidity {_weather_cache['humidity']}%  "
                f"Wind {_weather_cache['wind_kph']} km/h")
    return "Weather data not yet loaded. Fetching..."

def _laptop_control(q):
    if any(x in q for x in ["battery","power status","charge level"]):
        return True, get_battery_info()
    if "volume" in q:
        m = _re.search(r'\b(\d{1,3})\b', q)
        if m: return True, set_volume(int(m.group(1)))
        if "mute" in q:   return True, mute_volume()
        if "unmute" in q: return True, unmute_volume()
        if any(x in q for x in ["up","increase","louder"]): return True, set_volume(70)
        if any(x in q for x in ["down","decrease","lower"]): return True, set_volume(30)
        return True, get_volume()
    if q == "mute":   return True, mute_volume()
    if q == "unmute": return True, unmute_volume()
    if "brightness" in q:
        m = _re.search(r'\b(\d{1,3})\b', q)
        if m: return True, set_brightness(int(m.group(1)))
        if any(x in q for x in ["up","increase","max"]): return True, set_brightness(100)
        if any(x in q for x in ["down","decrease","dim"]): return True, set_brightness(30)
        return True, get_brightness()
    if any(x in q for x in ["screenshot","screen capture","capture screen"]):
        return True, take_screenshot()
    if any(x in q for x in ["system info","system status","hardware info",
                              "cpu usage","ram usage","disk usage","pc info"]):
        return True, get_system_info()
    if any(x in q for x in ["network","wifi","ip address","network info"]):
        return True, get_network_info()
    if any(x in q for x in ["top processes","running processes","task list","processes"]):
        return True, list_top_processes()
    if q.startswith("kill "): return True, kill_process(q.replace("kill","").strip())
    if any(x in q for x in ["sleep","hibernate"]): return True, system_sleep()
    if any(x in q for x in ["lock pc","lock screen","lock computer","lock workstation"]):
        return True, system_lock()
    if "cancel shutdown" in q or "abort shutdown" in q: return True, cancel_shutdown()
    if any(x in q for x in ["shutdown pc","shutdown computer","turn off pc","power off"]):
        return True, system_shutdown_os()
    if any(x in q for x in ["restart pc","restart computer","reboot"]): return True, system_restart()
    if any(x in q for x in ["weather","temperature","forecast","climate"]):
        return True, get_weather_cmd()
    if q.startswith("open ") and not any(x in q for x in ["youtube","google","http"]):
        app_name = q.replace("open","").strip()
        result   = open_app(app_name)
        if result and "Unknown" not in result: return True, result
    if q.startswith("launch ") or q.startswith("start "):
        app_name = q.replace("launch","").replace("start","").strip()
        return True, open_app(app_name)
    return False, ""

# ── MAIN PROCESSOR ──
def _process_worker(query):
    query = query.strip().lower()
    if not query or query == "none":
        log("No input detected.", "warn"); return

    set_status("PROCESSING", AMBER, "ARC REACTOR ANALYZING INPUT...")
    radar_active[0] = True

    handled, resp = _laptop_control(query)
    if handled:
        for line in (resp or "").split("\n"):
            if line.strip(): log(line, "result")
        speak((resp or "Done.").split("\n")[0])
        set_status("STANDBY", ORANGE, "ARC REACTOR STABLE  //  MARK VI READY")
        radar_active[0] = False
        return

    if "wikipedia" in query:
        topic = query.replace("wikipedia","").strip()
        speak(f"Searching Wikipedia for {topic}")
        if HAS_WIKI:
            try:
                result = wikipedia.summary(topic, sentences=2)
                log(result, "result"); speak(result)
            except wikipedia.exceptions.DisambiguationError:
                log("Too many results — be more specific.", "warn"); speak("Too many results.")
            except wikipedia.exceptions.PageError:
                log("No Wikipedia page found.", "warn"); speak("No page found.")
        else:
            log("Install wikipedia: pip install wikipedia", "warn")
    elif "open youtube" in query:
        speak("Opening YouTube.")
        webbrowser.open("https://youtube.com")
        log("Launching YouTube →", "info")
    elif "open google" in query:
        speak("Opening Google.")
        webbrowser.open("https://google.com")
        log("Launching Google →", "info")
    elif "time" in query:
        now = datetime.datetime.now()
        t   = now.strftime("%I:%M %p").lstrip("0")
        log(f"Current time: {now.strftime('%H:%M:%S')}", "result")
        speak(f"The time is {t}.")
    elif "date" in query:
        d = datetime.datetime.now().strftime("%A, %B %d %Y")
        log(f"Today: {d}", "result"); speak(f"Today is {d}.")
    elif "calculate" in query:
        try:
            expr   = query.replace("calculate","").strip()
            result = safe_calculate(expr)
            log(f"∑  {expr} = {result}", "result")
            speak(f"The result is {result}.")
        except Exception:
            log("Calculation error.", "warn"); speak("I could not calculate that.")
    elif "help" in query:
        lines = [
            "── COMMANDS ─────────────────────────────────",
            "  battery · system info · network info · weather",
            "  screenshot · volume [0-100] · mute · unmute",
            "  brightness [0-100] · sleep · lock screen",
            "  restart pc · shutdown pc · cancel shutdown",
            "  open [app] · open youtube · open google",
            "  wikipedia [topic] · calculate [expr]",
            "  time · date · top processes · kill [proc]",
        ]
        for l in lines: log(l, "head")
        speak("Command list displayed.")
    elif "exit" in query or "quit" in query:
        log("Lucky powering down. Goodbye, sir.", "warn")
        speak("Powering down. Goodbye sir.")
        root.after(2000, root.quit)
        return
    else:
        log(f'Unknown command: "{query}"', "warn")
        speak(f"I did not understand: {query}. Say help for command list.")

    set_status("STANDBY", ORANGE, "ARC REACTOR STABLE  //  MARK VI READY")
    radar_active[0] = False

def process_query(query):
    threading.Thread(target=_process_worker, args=(query,), daemon=True).start()

def quick_cmd(cmd):
    log(f"◉ CMD › {cmd}", "user")
    process_query(cmd)

def send_text_cmd():
    val = cmd_entry.get().strip()
    if not val: return
    cmd_entry.delete(0, tk.END)
    log(f"◉ INPUT › {val}", "user")
    process_query(val)

# ── VOICE RECOGNITION ──
def takeCommand():
    if not HAS_SR:
        log("speech_recognition not installed.", "warn"); return "none"
    r = sr.Recognizer()
    with sr.Microphone() as source:
        set_status("LISTENING", ARC_BLUE, "MICROPHONE ACTIVE  //  SPEAK NOW...")
        set_voice_status("LISTENING", ARC_BLUE)
        radar_active[0] = True
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=6)
        except Exception:
            set_voice_status("STANDBY", TEXT_DIM)
            radar_active[0] = False
            return "none"
    try:
        set_status("PROCESSING", AMBER, "RECOGNIZING SPEECH...")
        q = r.recognize_google(audio, language="en-in")
        log(f"VOICE › {q}", "user")
        return q.lower()
    except Exception:
        log("Could not understand audio.", "warn"); return "none"
    finally:
        set_status("STANDBY", ORANGE, "ARC REACTOR STABLE  //  MARK VI READY")
        set_voice_status("STANDBY", TEXT_DIM)
        radar_active[0] = False

def run_voice_command():
    q = takeCommand()
    if q != "none": process_query(q)

def start_voice_thread():
    threading.Thread(target=run_voice_command, daemon=True).start()

# ── WAKE WORD ──
_wake_active = [False]

def _listen_for_wake():
    if not HAS_SR: return
    r = sr.Recognizer()
    r.energy_threshold         = 300
    r.dynamic_energy_threshold = True
    log("Wake word listener started — say 'Hey Lucky'", "arc")
    while _wake_active[0]:
        if not wake_on[0]:
            threading.Event().wait(1); continue
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                try:
                    audio = r.listen(source, timeout=3, phrase_time_limit=4)
                except sr.WaitTimeoutError:
                    continue
            try:
                heard = r.recognize_google(audio, language="en-in").lower()
            except (sr.UnknownValueError, sr.RequestError):
                continue
            if any(ww in heard for ww in WAKE_WORDS):
                log(f"◉ Wake word detected: \"{heard}\"", "arc")
                set_status("WAKE", RED, "WAKE WORD DETECTED — LISTENING...")
                set_voice_status("WAKE DETECTED!", RED_GLOW)
                speak("Yes sir?")
                radar_active[0] = True
                try:
                    with sr.Microphone() as src2:
                        set_status("LISTENING", ARC_BLUE, "AWAITING COMMAND...")
                        try:
                            cmd_audio = r.listen(src2, timeout=5, phrase_time_limit=7)
                        except sr.WaitTimeoutError:
                            log("No command heard.", "warn")
                            set_status("STANDBY", ORANGE, "ARC REACTOR STABLE  //  MARK VI READY")
                            radar_active[0] = False; continue
                    cmd = r.recognize_google(cmd_audio, language="en-in").lower()
                    log(f"VOICE › {cmd}", "user")
                    process_query(cmd)
                except Exception as e:
                    log(f"Mic error: {e}", "warn")
                radar_active[0] = False
                set_status("STANDBY", ORANGE, "ARC REACTOR STABLE  //  MARK VI READY")
                set_voice_status("STANDBY", TEXT_DIM)
        except Exception:
            threading.Event().wait(1)

def start_wake_listener():
    if _wake_active[0]: return
    _wake_active[0] = True
    threading.Thread(target=_listen_for_wake, daemon=True).start()

# ── CLOCK TICK ──
def tick():
    now     = datetime.datetime.now()
    elapsed = int((now - start_time).total_seconds())
    m, s    = divmod(elapsed, 60)
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%a  %d %b %Y").upper()
    hud_time_var.set(time_str)
    hud_date_var.set(date_str)
    hud_uptime_var.set(f"UP  {m:02d}:{s:02d}")
    panel_time_var.set(now.strftime("%H:%M"))
    panel_date_var.set(date_str)
    root.after(1000, tick)

def wishMe():
    h = datetime.datetime.now().hour
    g = "Good morning sir" if h < 12 else "Good afternoon sir" if h < 18 else "Good evening sir"
    msg = f"{g}. Lucky version six point zero, Iron Man interface, online."
    log(msg, "info"); speak(msg)

# ═══════════════════════════════════════════
# STARTUP LOG
# ═══════════════════════════════════════════
log("◉" * 54, "head")
log("  Lucky  v6.0  — ", "head")
log("◉" * 54, "head")
log(f"  OS        : {OS}", "system")
log(f"  psutil    : {'✔' if HAS_PSUTIL  else '✘  pip install psutil'}", "system")
log(f"  voice TTS : {'✔' if HAS_TTS     else '✘  pip install pyttsx3'}", "system")
log(f"  speech SR : {'✔' if HAS_SR      else '✘  pip install SpeechRecognition'}", "system")
log(f"  Pillow    : {'✔' if HAS_PIL     else '✘  pip install Pillow'}", "system")
log(f"  pycaw     : {'✔' if HAS_PYCAW   else '✘  pip install pycaw  (Windows vol)'}", "system")
log(f"  brightness: {'✔' if HAS_SBC     else '✘  pip install screen-brightness-control'}", "system")
log("─" * 54, "system")
log("  COMMANDS: battery · system info · weather", "head")
log("  screenshot · volume [n] · brightness [n]", "arc")
log("  network · top processes · open [app]", "arc")
log("  sleep · lock · restart · shutdown · help", "arc")
log("◉" * 54, "head")

# ─── BOOT SEQUENCE ───
root.after(50,   draw_logo)
root.after(50,   draw_radar)
root.after(400,  tick)
root.after(500,  refresh_network)
root.after(600,  lambda: draw_weather_art(""))
root.after(800,  refresh_weather)
root.after(1200, wishMe)
root.after(1500, start_wake_listener)

# Apply gradient to root background after initial sizing
def apply_root_gradient():
    w, h = root.winfo_width(), root.winfo_height()
    grad = create_gradient(w, h, BG, BG1)
    if grad:
        root._grad_img = grad
        root.bg_label = tk.Label(root, image=grad, bg=BG)
        root.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        root.bg_label.lower()

root.after(100, apply_root_gradient)

root.mainloop()