import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACI Premio PolyColor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── STYLING ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #ffffff;
    --surface:   #f8f9fa;
    --border:    #e2e8f0;
    --accent:    #0ea5e9;
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

#MainMenu, footer, header { visibility: hidden; }

/* ── RESPONSIVE CONTAINER ── */
.block-container {
    padding: 1.5rem 1.25rem 4rem 1.25rem !important;
    max-width: 700px !important;
}
@media (min-width: 768px) {
    .block-container {
        padding: 2rem 3rem 4rem 3rem !important;
        max-width: 1100px !important;
    }
}

/* ── HEADER ── */
.header-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.25rem;
    margin-bottom: 2rem;
}
@media (min-width: 600px) {
    .header-wrap {
        flex-direction: row;
        align-items: flex-end;
        justify-content: space-between;
    }
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0f172a;
    margin: 0;
    line-height: 1.1;
}
@media (min-width: 600px) {
    .header-title { font-size: 2rem; }
}
.header-title span { color: var(--accent); }
.header-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--subtext);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--subtext);
    margin-bottom: 0.6rem;
    margin-top: 1.75rem;
}

/* ── CARDS ── */
.card {
    background: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}
@media (min-width: 600px) {
    .card { padding: 1.5rem; }
}

/* ── SWATCH ── */
.swatch-wrap {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
@media (min-width: 500px) {
    .swatch-wrap {
        flex-direction: row;
        align-items: center;
        flex-wrap: wrap;
    }
}
.swatch-pair {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}
.swatch-box {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    border: 1px solid var(--border);
    flex-shrink: 0;
}
@media (min-width: 600px) {
    .swatch-box { width: 72px; height: 72px; }
}
.swatch-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--subtext);
    text-transform: uppercase;
    margin-bottom: 0.25rem;
    letter-spacing: 0.06em;
}
.swatch-vals {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #0f172a;
    line-height: 1.7;
}
.swatch-arrow {
    color: #cbd5e1;
    font-size: 1.25rem;
    display: none;
}
@media (min-width: 500px) {
    .swatch-arrow { display: block; }
}
.swatch-tol {
    margin-left: auto;
    text-align: right;
}
@media (max-width: 499px) {
    .swatch-tol {
        margin-left: 0;
        text-align: left;
        border-top: 1px solid var(--border);
        padding-top: 0.75rem;
        width: 100%;
    }
}

/* ── RESULT BANNER ── */
.result-banner {
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin: 1.5rem 0;
}
@media (min-width: 500px) {
    .result-banner {
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        padding: 2rem 2.5rem;
    }
}
.result-banner.pass { background: #f0fdf4; border: 1.5px solid var(--pass); }
.result-banner.fail { background: #fef2f2; border: 1.5px solid var(--fail); }
.result-label {
    font-family: 'Syne', sans-serif;
    font-size: 2.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
}
@media (min-width: 500px) {
    .result-label { font-size: 3.5rem; }
}
.result-label.pass { color: var(--pass); }
.result-label.fail { color: var(--fail); }
.result-note {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    margin-top: 0.3rem;
}
.result-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #64748b;
    line-height: 1.9;
}
@media (min-width: 500px) {
    .result-meta { text-align: right; }
}

/* ── AXIS ROWS ── */
.axis-row {
    display: grid;
    grid-template-columns: 36px 1fr 72px 60px;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
}
@media (min-width: 500px) {
    .axis-row {
        grid-template-columns: 48px 1fr 90px 80px 70px;
        gap: 1rem;
    }
}
.axis-row:last-child { border-bottom: none; }
.axis-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--subtext);
}
.axis-bar-wrap {
    position: relative;
    height: 6px;
    background: #e2e8f0;
    border-radius: 99px;
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
    font-size: 0.75rem;
    text-align: right;
}
.axis-tol {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--subtext);
    text-align: right;
    display: none;
}
@media (min-width: 500px) {
    .axis-tol { display: block; }
}
.badge {
    display: inline-block;
    padding: 0.18rem 0.45rem;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    text-align: center;
}
.badge.pass { background: #e6f4ea; color: #16a34a; }
.badge.fail { background: #fce8e6; color: #dc2626; }

/* ── INPUTS ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #0f172a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1rem !important;
    height: 2.75rem !important;
}

/* ── BUTTON ── */
div[data-testid="stButton"] button {
    background-color: #0ea5e9 !important;
    border: none !important;
    border-radius: 10px !important;
    height: 3.25rem !important;
    width: 100% !important;
    transition: background 0.15s;
}
div[data-testid="stButton"] button:hover {
    background-color: #0284c7 !important;
}
div[data-testid="stButton"] button * {
    color: #ffffff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    background: transparent !important;
}

/* ── LOG TABLE ── */
.log-table { width: 100%; border-collapse: collapse; }
.log-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #64748b;
    padding: 0.5rem 0.5rem;
    border-bottom: 2px solid #e2e8f0;
    text-align: left;
    white-space: nowrap;
}
.log-table td {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #0f172a;
    padding: 0.55rem 0.5rem;
    border-bottom: 1px solid #f1f5f9;
    white-space: nowrap;
}
.log-table tr:last-child td { border-bottom: none; }

hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ───────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]
SHEET_ID          = "1u0d5uV9r7NE8JjYd-vcE0z8PRLnE3bjMf1eFVjcW-yg"
TAB_COLORS        = "Color Visualization Index"
TAB_QC            = "Color Tolerance Sheet"
LOG_SECTION_START = 15

@st.cache_resource(ttl=60)
def get_sheet_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_colors():
    all_rows = get_sheet_client().open_by_key(SHEET_ID).worksheet(TAB_COLORS).get_all_values()
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
    all_rows = get_sheet_client().open_by_key(SHEET_ID).worksheet(TAB_QC).get_all_values()
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
    ws = get_sheet_client().open_by_key(SHEET_ID).worksheet(TAB_QC)
    all_rows = ws.get_all_values()
    next_row = len(all_rows) + 1
    for i in range(LOG_SECTION_START - 1, len(all_rows)):
        if not any(cell.strip() for cell in all_rows[i]):
            next_row = i + 1
            break
    ws.update(f"A{next_row}:M{next_row}", [row_data])

@st.cache_data(ttl=60)
def load_recent_log():
    all_rows = get_sheet_client().open_by_key(SHEET_ID).worksheet(TAB_QC).get_all_values()
    log_rows, in_log = [], False
    for row in all_rows:
        if row and row[0] == "Timestamp":
            in_log = True
            continue
        if in_log and any(cell.strip() for cell in row):
            log_rows.append(row)
    return log_rows[-10:]  # only last 10

def lab_to_rgb_hex(L, a, b):
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200
    f_inv = lambda t: t ** 3 if t > 0.206897 else (t - 16 / 116) / 7.787
    X, Y, Z = f_inv(fx) * 0.95047, f_inv(fy) * 1.0, f_inv(fz) * 1.08883
    r  =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g  = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b_ =  0.0557 * X - 0.2040 * Y + 1.0570 * Z
    gam = lambda c: 12.92 * c if c <= 0.0031308 else 1.055 * (max(0, min(1, c)) ** (1/2.4)) - 0.055
    return f"#{int(gam(r)*255):02x}{int(gam(g)*255):02x}{int(gam(b_)*255):02x}"

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
  <div>
    <div class="header-sub">ACI Premio Plastics · QC Division</div>
    <h1 class="header-title"> PolyColor </h1>
  </div>
  <div class="header-sub">CIE L*a*b* · Independent Axis Evaluation</div>
</div>
""", unsafe_allow_html=True)

# ─── LOAD DATA ──────────────────────────────────────────────────────────────────
try:
    colors     = load_colors()
    tolerances = load_tolerances()
except Exception as e:
    st.error(f"Spreadsheet connection failed: {e}")
    st.stop()

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)

selected_color = st.selectbox("Target Colour Profile", list(colors.keys()))
location       = st.selectbox("Testing Location", ["Office", "Factory", "Market"])

# ─── SAMPLE INPUT ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Sample L*a*b* Values</div>', unsafe_allow_html=True)

c_l, c_a, c_b = st.columns(3)
with c_l: sample_L = st.number_input("L*", value=0.00, step=0.01, format="%.2f")
with c_a: sample_a = st.number_input("a*", value=0.00, step=0.01, format="%.2f")
with c_b: sample_b = st.number_input("b*", value=0.00, step=0.01, format="%.2f")

# ─── SWATCH PREVIEW ─────────────────────────────────────────────────────────────
if selected_color:
    t   = colors[selected_color]
    tol = tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})
    t_hex = lab_to_rgb_hex(t["L"], t["a"], t["b"])
    s_hex = lab_to_rgb_hex(sample_L, sample_a, sample_b)

    st.markdown('<div class="section-label">Colour Preview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
      <div class="swatch-wrap">
        <div class="swatch-pair">
          <div class="swatch-box" style="background:{t_hex}"></div>
          <div>
            <div class="swatch-label">Target</div>
            <div class="swatch-vals">L* {t['L']:.2f}<br>a* {t['a']:.2f}<br>b* {t['b']:.2f}</div>
          </div>
        </div>
        <div class="swatch-arrow">→</div>
        <div class="swatch-pair">
          <div class="swatch-box" style="background:{s_hex}"></div>
          <div>
            <div class="swatch-label">Sample</div>
            <div class="swatch-vals">L* {sample_L:.2f}<br>a* {sample_a:.2f}<br>b* {sample_b:.2f}</div>
          </div>
        </div>
        <div class="swatch-tol">
          <div class="swatch-label">Tolerances</div>
          <div class="swatch-vals">ΔL* ±{tol['L']:.2f}<br>Δa* ±{tol['a']:.2f}<br>Δb* ±{tol['b']:.2f}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── RUN BUTTON ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

if st.button("▶  Run Colour Evaluation & Log Result"):
    t   = colors[selected_color]
    tol = tolerances.get(selected_color, {"L": 1.5, "a": 1.5, "b": 1.5})

    dL = round(sample_L - t["L"], 4)
    da = round(sample_a - t["a"], 4)
    db = round(sample_b - t["b"], 4)

    ok_L = abs(dL) <= tol["L"]
    ok_a = abs(da) <= tol["a"]
    ok_b = abs(db) <= tol["b"]

    verdict   = "PASS" if (ok_L and ok_a and ok_b) else "FAIL"
    v_class   = "pass" if verdict == "PASS" else "fail"
    fail_axes = [ax for ax, ok in [("L*", ok_L), ("a*", ok_a), ("b*", ok_b)] if not ok]
    fail_note = f"Axes exceeded: {', '.join(fail_axes)}" if fail_axes else "All axes within tolerance"
    now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Result banner
    st.markdown(f"""
    <div class="result-banner {v_class}">
      <div>
        <div class="result-label {v_class}">{verdict}</div>
        <div class="result-note" style="color:{'#16a34a' if verdict=='PASS' else '#dc2626'}">{fail_note}</div>
      </div>
      <div class="result-meta">{selected_color}<br>{location}<br>{now}</div>
    </div>
    """, unsafe_allow_html=True)

    # Axis breakdown
    st.markdown('<div class="section-label">Axis Breakdown</div>', unsafe_allow_html=True)
    tracks_html = ""
    for ax, d_val, t_val, ok in [("L*", dL, tol["L"], ok_L), ("a*", da, tol["a"], ok_a), ("b*", db, tol["b"], ok_b)]:
        pct   = min(abs(d_val) / (t_val * 2), 0.5) * 100
        l_pos = "50%" if d_val >= 0 else f"{50 - pct}%"
        color = "#16a34a" if ok else "#dc2626"
        sign  = "+" if d_val > 0 else ""
        tracks_html += f"""
        <div class="axis-row">
          <div class="axis-name">{ax}</div>
          <div class="axis-bar-wrap">
            <div class="axis-bar-center"></div>
            <div class="axis-bar-fill" style="left:{l_pos};width:{pct}%;background:{color}"></div>
          </div>
          <div class="axis-val" style="color:{color}">{sign}{d_val:.4f}</div>
          <div class="axis-tol">±{t_val:.2f}</div>
          <span class="badge {v_class if not ok else 'pass'}">{'OK' if ok else 'ERR'}</span>
        </div>"""
    st.markdown(f'<div class="card">{tracks_html}</div>', unsafe_allow_html=True)

    # Log to Sheets
    try:
        append_log([now, location, selected_color,
                    t["L"], t["a"], t["b"],
                    sample_L, sample_a, sample_b,
                    dL, da, db, verdict])
        load_recent_log.clear()
        st.success("✓ Result logged to Google Sheets.")
    except Exception as err:
        st.error(f"Logging failed: {err}")

# ─── RECENT LOG ─────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Recent Laboratory Logs</div>', unsafe_allow_html=True)

try:
    recent_data = load_recent_log()
    if not recent_data:
        st.markdown('<div style="font-family:monospace;font-size:0.8rem;color:#64748b;">No records yet.</div>', unsafe_allow_html=True)
    else:
        rows = []
        for r in reversed(recent_data):
            if len(r) >= 13:
                rows.append({
                    "Timestamp": r[0],
                    "Location":  r[1],
                    "Colour":    r[2],
                    "ΔL*":       float(r[9]),
                    "Δa*":       float(r[10]),
                    "Δb*":       float(r[11]),
                    "Verdict":   r[12],
                })

        df = pd.DataFrame(rows)

        def style_table(df):
            def row_style(row):
                is_pass = row["Verdict"] == "PASS"
                v_color = "#16a34a" if is_pass else "#dc2626"
                v_bg    = "#f0fdf4" if is_pass else "#fef2f2"
                styles  = [""] * len(row)
                styles[df.columns.get_loc("Verdict")] = f"color:{v_color};background:{v_bg};font-weight:600"
                return styles
            return df.style.apply(row_style, axis=1).format({
                "ΔL*": "{:+.4f}", "Δa*": "{:+.4f}", "Δb*": "{:+.4f}"
            })

        st.dataframe(style_table(df), use_container_width=True, hide_index=True)

except Exception:
    st.markdown('<div style="font-family:monospace;font-size:0.8rem;color:#64748b;">Awaiting first test.</div>', unsafe_allow_html=True)
