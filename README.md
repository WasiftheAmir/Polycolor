# PolyColor — Colour QC System
**ACI Premio Plastics · QC Division**

PolyColor is an internal colour quality control web application built for ACI Premio Plastics. It allows QC staff, lab technicians, and engineers to evaluate production batch colour samples against established standard colour profiles using the CIE L\*a\*b\* colour space, log results in real time to a shared Google Sheet, and review recent test history — all from a mobile-friendly browser interface accessible on the factory floor, in the office, or in the field.

---

## What It Does

### Colour Evaluation
The core function of the app is to compare a production sample's colour values against a target standard and determine whether the sample is within acceptable deviation bounds.

The user selects a target colour profile from a dropdown (populated live from the master colour reference sheet), enters the L\*, a\*, and b\* values read from a colorimeter, and hits **Run**. The app computes the signed delta on each axis independently:

- **ΔL\*** — deviation in lightness
- **Δa\*** — deviation on the green–red axis
- **Δb\*** — deviation on the blue–yellow axis

Each axis is checked against its own tolerance limit, which is defined per colour in the tolerance reference sheet. A sample is only marked **PASS** if all three axes are simultaneously within their respective limits. If any single axis exceeds its tolerance, the result is a **FAIL**, and the specific failing axes are reported.

### Per-Axis Independent Tolerance System
Tolerances are not a single composite ΔE threshold — they are defined independently for each axis and for each colour. This design reflects the reality that different colours have different perceptual sensitivities: a pink colour's identity lives primarily in its a\* (red-green) value, while a gold's identity lives in b\* (yellow). Tolerances are stored in a dedicated Google Sheet tab and can be updated at any time without touching the application code.

### Live Colour Swatch Preview
As the user selects a target profile and enters sample values, the app renders approximate colour swatches for both the target and the sample using a CIE L\*a\*b\* → sRGB conversion. This gives the user an immediate visual reference before running the evaluation.

### Result Display
After running a test, the app displays:
- A large **PASS / FAIL** verdict banner with colour coding (green / red)
- The specific axes that failed, if any
- A per-axis deviation bar chart showing the magnitude and direction of each delta relative to its tolerance limit
- The colour name, testing location, and timestamp

### Automatic Logging to Google Sheets
Every test result is automatically appended to a dedicated **QC Log** tab in the connected Google Sheet. Each log entry records:

`Timestamp · Location · Colour Name · Target L\* · Target a\* · Target b\* · Sample L\* · Sample a\* · Sample b\* · ΔL\* · Δa\* · Δb\* · Result`

This creates a persistent, shareable audit trail of all colour evaluations across all locations and users with no manual data entry required.

### Recent Log View
The bottom of the app displays the 10 most recent test results in a formatted table, newest first, with verdict cells colour-coded green or red. This gives any user instant visibility into recent QC activity without opening the spreadsheet.

---

## Google Sheets Integration

The app connects to a central Google Sheet with the following tab structure:

| Tab | Purpose |
|---|---|
| `Color Visualization Index` | Master list of standard colour profiles with target L\*a\*b\* values |
| `Color Tolerance Sheet` | Per-colour, per-axis tolerance limits (editable without code changes) |
| `Comparison Log` | Auto-appended QC test log |
| `Raw Color Data` | Raw colorimeter export data (read-only reference) |

Authentication is handled via a Google Cloud service account. Credentials are stored securely in Streamlit's secrets manager and are never exposed in the codebase.

---

## Tech Stack

- **Frontend / App framework:** [Streamlit](https://streamlit.io)
- **Google Sheets integration:** `gspread` + `google-auth`
- **Colour space conversion:** CIE L\*a\*b\* → XYZ → sRGB (implemented natively, no external colour library)
- **Data handling:** `pandas`
- **Deployment:** Streamlit Community Cloud
- **Credentials:** Google Cloud service account via `st.secrets`

---

## Project Structure

```
polycolor/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
└── .streamlit/
    └── secrets.toml        # Service account credentials (not committed)
```

---

## Setup & Deployment

### 1. Google Cloud Service Account
- Create a project in [Google Cloud Console](https://console.cloud.google.com)
- Enable the **Google Sheets API** and **Google Drive API**
- Create a service account and download the JSON key
- Share the target Google Sheet with the service account's `client_email` as Editor

### 2. Streamlit Secrets
In Streamlit Community Cloud, add the contents of the service account JSON under **Advanced Settings → Secrets** using the following format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

### 3. Dependencies
```
streamlit>=1.32.0
gspread>=6.0.0
google-auth>=2.28.0
pandas
```

### 4. Deploy
Push the repo to GitHub and connect it to [Streamlit Community Cloud](https://share.streamlit.io). Select `app.py` as the entry point.

---

## Adding New Colours

1. Add a new row to the **Color Visualization Index** tab with the colour name and target L\*, a\*, b\* values
2. Add a corresponding row to the **Color Tolerance Sheet** tab with per-axis tolerance values
3. The dropdown in the app will reflect the new colour automatically on next load — no code changes required
