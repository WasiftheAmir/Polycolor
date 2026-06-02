import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACI Premio | Colour QC",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── STYLING (FORCED LIGHT THEME WITH SYSTEM FIXES) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #ffffff;
    --surface:   #f8f9fa;
    --border:    #e2e8f0;
    --accent:    #0ea5e9;
    --accent-hover: #0284c7;
    --pass:      #16a34a;
    --fail:      #dc2626;
    --text:      #0f172a;
    --subtext:   #64748b;
}

html, body, [class*="st-"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Hide Streamlit components */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1100px; }

/* Header Formatting */
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
    color: #0f172a;
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

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--subtext);
    margin-bottom: 0.75rem;
    margin-top: 2rem;
}

.card {
    background: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Banners */
.result-banner {
    border-radius: 12px;
    padding: 2rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 2rem 0;
}
.result-banner.pass { background: #f0fdf4; border: 1.5px solid var(--pass); }
.result-banner.fail { background: #fef2f2; border: 1.5px solid var(--fail); }
.result-label { font-family: 'Syne', sans-serif; font-size: 3.5rem; font-weight: 800; }
.result-label.pass { color: var(--pass); }
.result-label.fail { color: var(--fail); }

/* Axis Controls */
.axis-row {
    display: grid;
    grid-template-columns: 60px 1fr 100px 100px 80px;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--border);
}
.axis-name { font-family: 'DM Mono', monospace; color: var(--subtext); }
.axis-bar-wrap { position: relative; height: 6px; background: #e2e8f0; border-radius: 99px; }
.axis-bar-center { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #cbd5e1; }
.axis-bar-fill { position: absolute; top: 0; height: 100%; border-radius: 99px; }
.axis-val, .axis-tol { font-family: 'DM Mono', monospace; text-align: right; }

/* Swatches */
.swatch-wrap { display: flex; gap: 1.5rem; align-items: center; }
.swatch-box { width: 80px; height: 80px; border-radius: 10px; border: 1px solid var(--border); }
.swatch-label { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--subtext); text-transform: uppercase; }
.swatch-vals { font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #0f172a; }

/* Input Formatting Override */
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #0f172a !important;
}

/* GLOBAL BUTTON OVERRIDE FIX */
div[data-testid="stButton"] button {
    background-color: #0ea5e9 !important;
    border: none !important;
    border-radius: 8px !important;
    height: 3rem;
}
div[data-testid="stButton"] button:hover {
    background-color: #0284c7 !important;
}
div[data-testid="stButton"] button * {
    color: #ffffff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    background: transparent !important;
}

/* Inline Log Data Table Styling */
.log-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.log-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #64748b;
    padding: 0.6rem;
    border-bottom: 2px solid #e2e8f0;
    text-align: left;
}
.log-table td {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #0f172a;
    padding: 0.6rem;
    border-bottom: 1px solid #f1f5f9;
}
.badge { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 600; }
.badge.pass { background: #e6f4ea; color: #16a34a; }
.badge.fail { background: #fce8e6; color: #dc2626; }
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONNECTION ────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.readonly"]
SHEET_ID = "1u0d5uV9r7NE8JjYd-vcE0z8PRLnE3bjMf1eFVjcW-yg"
TAB_COLORS = "Color Visualization Index"
TAB_QC = "Color Tolerance Sheet"
LOG_SECTION_START = 15

@st.cache_resource(ttl=60)
def get_sheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_colors():
    client = get_sheet_client()
    all_rows = client.open_by_key(SHEET_ID).worksheet(TAB_COLORS).get_all_values()
    colors = {}
    for row in all_rows[3:]:  
        if len(row) >= 5 and row[1].strip():
            try:
                colors[row[1].strip()] = {"L": float(row[2]), "a": float(row[3]), "b": float(row[4])}
            except ValueError:
                continue
    return colors

@st.cache_data(ttl=60)
def load_tolerances():
    client = get_sheet_client()
    all_rows = client.open_by_key(SHEET_ID).worksheet(TAB_QC).get_all_values()
    tolerances = {}
    for row in all_rows[2:]:
        if not row or not row[0].strip() or "---" in row[0]:
            break  
        try:
            tolerances[row[0].strip()] = {"L": float(row[1]), "a": float(row[2]), "b": float(row[3])}
        except ValueError:
            continue
    return tolerances

def append_log(row_data: list):
    client = get_sheet_client()
    ws = client.open_by_key(SHEET_ID).worksheet(TAB_QC)
    all_rows = ws.get_all_values()
    next_row = len(all_rows) + 1
    for i in range(LOG_SECTION_START - 1, len(all_rows)):
        if i < len(all_rows) and not any(cell.strip() for cell in all_rows[i]):
            next_row = i + 1
            break
    ws.update(f"A{next_row}:M{next_row}", [row_data])

def load_recent_log():
    client = get_sheet_client()
    all_rows = client.open_by_key(SHEET_ID).worksheet(TAB_QC).get_all_values()
    log_rows = []
    in_log = False
    for row in all_rows:
        if row and row[0] == "Timestamp":
            in_log = True
            continue
        if in_log and any(cell.strip() for cell in row):
            log_rows.append(row)
    return log_rows[-10:]

def lab_to_rgb_hex(L, a, b):
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200
    f_inv = lambda t: t ** 3 if t > 0.206897 else (t - 16 / 116) / 7.787
    X, Y, Z = f_inv(fx) * 0.95047, f_inv(fy) * 1.00000, f_inv(fz) * 1.08883
    r =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b_ =  0.0557 * X - 0.2040 * Y + 1.0570 * Z
    gamma = lambda c: 12.92 * c if c <= 0.0031308 else 1.055 * (max(0, min(1, c)) ** (1 / 2.4)) - 0.055
    return f"#{int(gamma(r)*255):02x}{int(gamma(g)*255):02x}{int(gamma(b_)*255):02x}"

# ─── APPLICATION UI LAYOUT ──────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
  <div><div class="header-sub">ACI Premio Plastics · QC Division</div><h1 class="header-title">Colour <span>QC</span> System</h1></div>
  <div class="header-sub" style="text-align:right">CIE L*a*b* · Independent Axis Evaluation</div>
</div>
""", unsafe_allow_html=True)

try:
    colors = load_colors()
    tolerances = load_tolerances()
except Exception as e:
    st.error(f"Spreadsheet connection failed: {e}")
    st.stop()

st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
col_setup_1, col_setup_2 = st.columns([2, 1])
with col_setup_1:
    selected_color = st.selectbox("Target Colour Profile", list(colors.keys()))
with col_setup_2:
    location = st.selectbox("Testing Location", ["Office", "Factory", "Market"])

st.markdown('<div class="section-label">Sample Parameters</div>', unsafe_allow_html=True)
c_l, c_a, c_b = st.columns(3)
with c_l: sample_L = st.number_input("Sample L*", value=0.00, step=0.01, format="%.2f")
with c_a: sample_a = st.number_input("Sample a*", value=0.00, step=0.01, format="%.2f")
with c_b: sample_b = st.number_input("Sample b*", value=0.00, step=0.01, format="%.2f")

if selected_color:
    t, tol = colors[selected_color], tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})
    st.markdown(f"""
    <div class="card">
      <div class="swatch-wrap">
        <div><div class="swatch-label">Target Profile</div><div style="display:flex;gap:1rem;align-items:center"><div class="swatch-box" style="background:{lab_to_rgb_hex(t['L'], t['a'], t['b'])}"></div><div class="swatch-vals">L* {t['L']:.2f}<br>a* {t['a']:.2f}<br>b* {t['b']:.2f}</div></div></div>
        <div style="color:#cbd5e1;font-size:1.5rem;margin-top:1rem">→</div>
        <div><div class="swatch-label">Production Batch Sample</div><div style="display:flex;gap:1rem;align-items:center"><div class="swatch-box" style="background:{lab_to_rgb_hex(sample_L, sample_a, sample_b)}"></div><div class="swatch-vals">L* {sample_L:.2f}<br>a* {sample_a:.2f}<br>b* {sample_b:.2f}</div></div></div>
        <div style="margin-left:auto;text-align:right;"><div class="swatch-label">Active Threshold Limits</div><div class="swatch-vals">ΔL* ±{tol['L']:.2f}<br>Δa* ±{tol['a']:.2f}<br>Δb* ±{tol['b']:.2f}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
if st.button("Run Colour Evaluation & Log Data"):
    t, tol = colors[selected_color], tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})
    dL, da, db = round(sample_L - t["L"], 4), round(sample_a - t["a"], 4), round(sample_b - t["b"], 4)
    ok_L, ok_a, ok_b = abs(dL) <= tol["L"], abs(da) <= tol["a"], abs(db) <= tol["b"]
    verdict = "PASS" if (ok_L and ok_a and ok_b) else "FAIL"
    v_class = "pass" if verdict == "PASS" else "fail"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.markdown(f"""
    <div class="result-banner {v_class}">
      <div><div class="result-label {v_class}">{verdict}</div><div style="font-family:monospace;font-size:0.75rem;color:var(--{v_class});margin-top:0.4rem">{'All parameters stable' if verdict=='PASS' else 'Threshold boundaries exceeded'}</div></div>
      <div style="font-family:monospace;font-size:0.72rem;color:#64748b;text-align:right;line-height:2">{selected_color}<br>{location}<br>{now}</div>
    </div>
    """, unsafe_allow_html=True)

    # Deviation tracks rendering
    tracks_html = ""
    for ax, d_val, t_val, ok in [("L*", dL, tol["L"], ok_L), ("a*", da, tol["a"], ok_a), ("b*", db, tol["b"], ok_b)]:
        pct = min(abs(d_val) / (t_val * 2), 0.5) * 100
        l_pos = "50%" if d_val >= 0 else f"{50 - pct}%"
        tracks_html += f"""
        <div class="axis-row">
          <div class="axis-name">{ax}</div>
          <div class="axis-bar-wrap"><div class="axis-bar-center"></div><div class="axis-bar-fill" style="left:{l_pos};width:{pct}%;background:{'#16a34a' if ok else '#dc2626'}"></div></div>
          <div class="axis-val" style="color:{'#16a34a' if ok else '#dc2626'}">{"++" if d_val > 0 else ""}{d_val:.4f}</div>
          <div class="axis-tol">limit ±{t_val:.2f}</div>
          <div style="text-align:center;"><span class="badge {'pass' if ok else 'fail'}">{'OK' if ok else 'ERR'}</span></div>
        </div>"""
    st.markdown(f'<div class="card">{tracks_html}</div>', unsafe_allow_html=True)

    try:
        append_log([now, location, selected_color, t["L"], t["a"], t["b"], sample_L, sample_a, sample_b, dL, da, db, verdict])
        st.cache_data.clear()
        st.success("✓ Batch telemetry successfully committed to Google Sheet.")
    except Exception as err:
        st.error(f"Local write execution failure: {err}")

# --- SEPARATE UN-NESTED INLINE TABLE RENDER ---
st.markdown('<div class="section-label">Recent Laboratory Logs</div>', unsafe_allow_html=True)
try:
    recent_data = load_recent_log()
    if not recent_data:
        st.markdown('<div style="font-family:monospace;font-size:0.8rem;color:#64748b;">No verification records found.</div>', unsafe_allow_html=True)
    else:
        table_rows = ""
        for r in reversed(recent_data):
            if len(r) >= 13:
                table_rows += f"""
                <tr>
                  <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>
                  <td style="color:{'#16a34a' if float(r[9])>=0 else '#dc2626'}">{r[9]}</td>
                  <td style="color:{'#16a34a' if float(r[10])>=0 else '#dc2626'}">{r[10]}</td>
                  <td style="color:{'#16a34a' if float(r[11])>=0 else '#dc2626'}">{r[11]}</td>
                  <td><span class="badge {'pass' if r[12]=='PASS' else 'fail'}">{r[12]}</span></td>
                </tr>"""
        
        st.markdown(f"""
        <div class="card" style="overflow-x:auto; background:#ffffff;">
          <table class="log-table">
            <thead>
              <tr><th>Timestamp</th><th>Location</th><th>Colour Name</th><th>ΔL*</th><th>Δa*</th><th>Δb*</th><th>Verdict</th></tr>
            </thead>
            <tbody>
              {table_rows}
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)
except Exception as log_err:
    st.markdown('<div style="font-family:monospace;font-size:0.8rem;color:#64748b;">Awaiting first testing instance activation.</div>', unsafe_allow_html=True)
