import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import math

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACI Premio | Colour QC",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── STYLING (LIGHT THEMING & CUSTOM SKY BLUE ACCENTS) ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #ffffff;
    --surface:   #f8f9fa;
    --border:    #e2e8f0;
    --accent:    #0ea5e9; /* Sky Blue */
    --accent-hover: #0284c7;
    --pass:      #16a34a;
    --fail:      #dc2626;
    --text:      #0f172a;
    --subtext:   #64748b;
}

html, body, [class*="st-"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1100px; }

/* ── HEADER ── */
.header-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2.5rem;
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
    line-height: 1;
    margin: 0;
}
.header-title span { color: var(--accent); }
.header-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--subtext);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--subtext);
    margin-bottom: 0.75rem;
    margin-top: 2rem;
}

/* ── CARDS ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
}

/* ── RESULT BANNER ── */
.result-banner {
    border-radius: 12px;
    padding: 2rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 2rem 0;
}
.result-banner.pass {
    background: #f0fdf4;
    border: 1.5px solid var(--pass);
}
.result-banner.fail {
    background: #fef2f2;
    border: 1.5px solid var(--fail);
}
.result-label {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
}
.result-label.pass { color: var(--pass); }
.result-label.fail { color: var(--fail); }
.result-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--subtext);
    text-align: right;
    line-height: 2;
}

/* ── AXIS BREAKDOWN ── */
.axis-row {
    display: grid;
    grid-template-columns: 60px 1fr 100px 100px 80px;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--border);
}
.axis-row:last-child { border-bottom: none; }
.axis-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: var(--subtext);
}
.axis-bar-wrap {
    position: relative;
    height: 6px;
    background: #e2e8f0;
    border-radius: 99px;
    overflow: visible;
}
.axis-bar-center {
    position: absolute;
    left: 50%;
    top: 0;
    width: 1px;
    height: 100%;
    background: #cbd5e1;
}
.axis-bar-fill {
    position: absolute;
    top: 0;
    height: 100%;
    border-radius: 99px;
}
.axis-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    text-align: right;
}
.axis-tol {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--subtext);
    text-align: right;
}
.axis-status {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    text-align: center;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
}
.axis-status.ok {
    background: #e6f4ea;
    color: var(--pass);
}
.axis-status.fail {
    background: #fce8e6;
    color: var(--fail);
}

/* ── SWATCH ── */
.swatch-wrap {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}
.swatch-box {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    border: 1px solid var(--border);
    flex-shrink: 0;
}
.swatch-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--subtext);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.swatch-vals {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: var(--text);
    line-height: 1.8;
}

/* ── INPUTS ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ── BUTTON OVERHAUL (FIXES VISIBILITY AND BACKGROUNDS) ── */
div[data-testid="stButton"] > button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100%;
    transition: background-color 0.15s ease;
}
div[data-testid="stButton"] > button:hover {
    background: var(--accent-hover) !important;
}
/* Explicitly control the text nested inside the button paragraph wrapper */
div[data-testid="stButton"] button p {
    background: transparent !important;
    color: #ffffff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── LOG TABLE ── */
.log-table { width: 100%; border-collapse: collapse; }
.log-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--subtext);
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
}
.log-table td {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--text);
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid #f1f5f9;
}
.log-table tr:last-child td { border-bottom: none; }
.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 500;
}
.badge.pass { background: #e6f4ea; color: var(--pass); }
.badge.fail { background: #fce8e6; color: var(--fail); }

/* ── STATUS CHIP ── */
.status-chip {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    background: #e0f2fe;
    color: var(--accent);
    border: 1px solid #bae6fd;
    margin-bottom: 2rem;
}

hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─── GOOGLE SHEETS CONNECTION ────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]
SHEET_ID = "1u0d5uV9r7NE8JjYd-vcE0z8PRLnE3bjMf1eFVjcW-yg"
TAB_COLORS   = "Color Visualization Index"
TAB_QC       = "Color Tolerance Sheet"

LOG_SECTION_START = 15  # Point to row 15 where the clean log framework begins


@st.cache_resource(ttl=60)
def get_sheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_data(ttl=60)
def load_colors():
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_COLORS)
    all_rows = ws.get_all_values()
    colors = {}
    for row in all_rows[3:]:  
        if len(row) >= 5 and row[1].strip():
            name = row[1].strip()
            try:
                L = float(row[2])
                a = float(row[3])
                b = float(row[4])
                colors[name] = {"L": L, "a": a, "b": b}
            except (ValueError, IndexError):
                continue
    return colors


@st.cache_data(ttl=60)
def load_tolerances():
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_QC)
    all_rows = ws.get_all_values()
    tolerances = {}
    for row in all_rows[2:]:
        if not row or not row[0].strip() or "--- QC TEST LOG ---" in row[0]:
            break  
        try:
            name = row[0].strip()
            tol_L = float(row[1])
            tol_a = float(row[2])
            tol_b = float(row[3])
            tolerances[name] = {"L": tol_L, "a": tol_a, "b": tol_b}
        except (ValueError, IndexError):
            continue
    return tolerances


def get_next_log_row():
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_QC)
    all_rows = ws.get_all_values()
    for i in range(LOG_SECTION_START, len(all_rows)):
        if not any(cell.strip() for cell in all_rows[i]):
            return i + 1  
    return len(all_rows) + 1


def append_log(row_data: list):
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_QC)
    next_row = get_next_log_row()
    ws.update(f"A{next_row}:M{next_row}", [row_data])


def setup_tab3():
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_QC)
    all_rows = ws.get_all_values()

    if all_rows and len(all_rows) >= 15 and all_rows[14] and all_rows[14][0] == "Timestamp":
        return

    colors = load_colors()

    ws.update("A1", [["COLOR TOLERANCE TABLE"]])
    ws.update("A2:D2", [["Color Name", "ΔL* Tolerance (±)", "Δa* Tolerance (±)", "Δb* Tolerance (±)"]])

    tol_rows = []
    for name in colors:
        tol_rows.append([name, 1.5, 1.5, 1.5])  

    ws.update(f"A3:D{2 + len(tol_rows)}", tol_rows)

    # Force cleaner placement on row 14 and 15 to clear layout shift offsets
    ws.update("A14", [["--- QC TEST LOG ---"]])
    ws.update("A15:M15", [[
        "Timestamp", "Location", "Color Name",
        "Target L*", "Target a*", "Target b*",
        "Sample L*", "Sample a*", "Sample b*",
        "ΔL*", "Δa*", "Δb*",
        "Result"
    ]])


def load_recent_log(n=15):
    client = get_sheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(TAB_QC)
    all_rows = ws.get_all_values()
    log_rows = []
    in_log = False
    for row in all_rows:
        if row and row[0] == "Timestamp":
            in_log = True
            continue
        if in_log and any(cell.strip() for cell in row):
            log_rows.append(row)
    return log_rows[-n:] if len(log_rows) > n else log_rows


# ─── LAB → sRGB CONVERSION ──────────────────────────────────────────────────────
def lab_to_rgb_hex(L, a, b):
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    def f_inv(t):
        return t ** 3 if t > 0.206897 else (t - 16 / 116) / 7.787

    X = f_inv(fx) * 0.95047
    Y = f_inv(fy) * 1.00000
    Z = f_inv(fz) * 1.08883

    r =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b_ =  0.0557 * X - 0.2040 * Y + 1.0570 * Z

    def gamma(c):
        c = max(0, min(1, c))
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    r, g, b_ = gamma(r), gamma(g), gamma(b_)
    ri, gi, bi = int(r * 255), int(g * 255), int(b_ * 255)
    return f"#{ri:02x}{gi:02x}{bi:02x}"


# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
  <div>
    <div class="header-sub">ACI Premio Plastics · QC Division</div>
    <h1 class="header-title">Colour <span>QC</span> System</h1>
  </div>
  <div class="header-sub" style="text-align:right">
    CIE L*a*b* · Per-Axis Tolerance<br>
    Independent Axis Evaluation
  </div>
</div>
""", unsafe_allow_html=True)


# ─── INIT SHEET ─────────────────────────────────────────────────────────────────
try:
    with st.spinner("Connecting to Google Sheets..."):
        setup_tab3()
        colors    = load_colors()
        tolerances = load_tolerances()
    st.markdown('<div class="status-chip">● CONNECTED TO GOOGLE SHEETS</div>', unsafe_allow_html=True)
except Exception as e:
    st.error(f"⚠️ Could not connect to Google Sheets: {e}")
    st.stop()


# ─── INPUT SECTION ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Test Configuration</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    color_names = list(colors.keys())
    selected_color = st.selectbox("Target Colour", color_names, key="color_select")

with col2:
    location = st.selectbox("Location", ["Office", "Factory", "Market"], key="location_select")

st.markdown('<div class="section-label">Sample L*a*b* Values</div>', unsafe_allow_html=True)

col_l, col_a, col_b = st.columns(3)
with col_l:
    sample_L = st.number_input("Sample L*", value=0.00, step=0.01, format="%.2f")
with col_a:
    sample_a = st.number_input("Sample a*", value=0.00, step=0.01, format="%.2f")
with col_b:
    sample_b = st.number_input("Sample b*", value=0.00, step=0.01, format="%.2f")


# ─── LIVE PREVIEW ───────────────────────────────────────────────────────────────
if selected_color:
    target = colors[selected_color]
    tol    = tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})
    target_hex = lab_to_rgb_hex(target["L"], target["a"], target["b"])
    sample_hex = lab_to_rgb_hex(sample_L, sample_a, sample_b)

    st.markdown('<div class="section-label">Colour Preview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
      <div class="swatch-wrap">
        <div>
          <div class="swatch-label">Target — {selected_color}</div>
          <div style="display:flex;gap:1rem;align-items:center">
            <div class="swatch-box" style="background:{target_hex}"></div>
            <div class="swatch-vals" style="color:var(--text)">L* {target['L']:.2f}<br>a* {target['a']:.2f}<br>b* {target['b']:.2f}</div>
          </div>
        </div>
        <div style="color:#cbd5e1;font-size:2rem;padding:0 1rem;margin-top:1.5rem">→</div>
        <div>
          <div class="swatch-label">Sample (entered values)</div>
          <div style="display:flex;gap:1rem;align-items:center">
            <div class="swatch-box" style="background:{sample_hex}"></div>
            <div class="swatch-vals" style="color:var(--text)">L* {sample_L:.2f}<br>a* {sample_a:.2f}<br>b* {sample_b:.2f}</div>
          </div>
        </div>
        <div style="margin-left:auto;text-align:right">
          <div class="swatch-label">Active Tolerances</div>
          <div class="swatch-vals" style="color:var(--text)">
            ΔL* ±{tol['L']:.2f}<br>
            Δa* ±{tol['a']:.2f}<br>
            Δb* ±{tol['b']:.2f}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── RUN TEST BUTTON ────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
run = st.button("▶  Run Colour Test & Log Result")

if run:
    target = colors[selected_color]
    tol    = tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})

    dL = round(sample_L - target["L"], 4)
    da = round(sample_a - target["a"], 4)
    db = round(sample_b - target["b"], 4)

    ok_L = abs(dL) <= tol["L"]
    ok_a = abs(da) <= tol["a"]
    ok_b = abs(db) <= tol["b"]
    overall = "PASS" if (ok_L and ok_a and ok_b) else "FAIL"
    result_class = "pass" if overall == "PASS" else "fail"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fail_axes = [ax for ax, ok in [("L*", ok_L), ("a*", ok_a), ("b*", ok_b)] if not ok]
    fail_note = f"Axes exceeded: {', '.join(fail_axes)}" if fail_axes else "All axes within tolerance"

    st.markdown(f"""
    <div class="result-banner {result_class}">
      <div>
        <div class="result-label {result_class}">{overall}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:{'#16a34a' if overall=='PASS' else '#dc2626'};margin-top:0.4rem">
          {fail_note}
        </div>
      </div>
      <div class="result-meta">
        {selected_color}<br>
        {location}<br>
        {now}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Axis Breakdown ──
    st.markdown('<div class="section-label">Axis Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    def bar_html(delta, tol_val, ok):
        pct = min(abs(delta) / (tol_val * 2), 0.5) * 100  
        left_pos = "50%" if delta >= 0 else f"{50 - pct}%"
        color = "#16a34a" if ok else "#dc2626"
        sign = "+" if delta > 0 else ""
        status_cls = "ok" if ok else "fail"
        status_txt = "OK" if ok else "FAIL"
        return f"""
        <div class="axis-bar-wrap">
          <div class="axis-bar-center"></div>
          <div class="axis-bar-fill" style="left:{left_pos};width:{pct}%;background:{color}"></div>
        </div>
        """, f"{sign}{delta:.4f}", status_cls, status_txt

    for axis_name, delta, tol_val, ok in [
        ("L*", dL, tol["L"], ok_L),
        ("a*", da, tol["a"], ok_a),
        ("b*", db, tol["b"], ok_b),
    ]:
        bar, val_str, status_cls, status_txt = bar_html(delta, tol_val, ok)
        st.markdown(f"""
        <div class="axis-row">
          <div class="axis-name">{axis_name}</div>
          {bar}
          <div class="axis-val" style="color:{'#16a34a' if ok else '#dc2626'}">{val_str}</div>
          <div class="axis-tol">tol ±{tol_val:.2f}</div>
          <div class="axis-status {status_cls}">{status_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    try:
        log_row = [
            now, location, selected_color,
            target["L"], target["a"], target["b"],
            sample_L, sample_a, sample_b,
            dL, da, db,
            overall
        ]
        append_log(log_row)
        st.cache_data.clear() # Corrected method call to erase data cache smoothly
        st.success("✓ Result logged to Google Sheets")
    except Exception as e:
        st.warning(f"Result calculated but could not write to sheet: {e}")


# ─── RECENT LOG ─────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Recent Test Log</div>', unsafe_allow_html=True)

try:
    log_rows = load_recent_log(15)
    if not log_rows:
        st.markdown('<div style="color:#888;font-family:DM Mono,monospace;font-size:0.8rem">No tests logged yet.</div>', unsafe_allow_html=True)
    else:
        rows_html = ""
        for row in reversed(log_rows):
            if len(row) < 13:
                continue
            ts, loc, cname = row[0], row[1], row[2]
            dL_v, da_v, db_v, res = row[9], row[10], row[11], row[12]
            badge_cls = "pass" if res == "PASS" else "fail"
            rows_html += f"""
            <tr>
              <td>{ts}</td>
              <td>{loc}</td>
              <td>{cname}</td>
              <td>{dL_v}</td>
              <td>{da_v}</td>
              <td>{db_v}</td>
              <td><span class="badge {badge_cls}">{res}</span></td>
            </tr>
            """
        
        st.markdown(f"""
        <div class="card" style="overflow-x:auto">
          <table class="log-table">
            <thead>
              <tr>
                <th>Timestamp</th><th>Location</th><th>Colour</th>
                <th>ΔL*</th><th>Δa*</th><th>Δb*</th><th>Result</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Could not load log: {e}")
