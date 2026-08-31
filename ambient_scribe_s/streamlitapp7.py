
import streamlit as st
import speech_recognition as sr
import requests
import json
import uuid
import os
import math
from datetime import datetime
import io
import pandas as pd
import altair as alt
from html import escape

# ============================================================
# 1. CONFIGURATION & CLINICAL THEME
# ============================================================
st.set_page_config(page_title="MScribe | Clinical Scribe", layout="wide", page_icon="MS", menu_items=None)

COFORGE_API_KEY = "cba973db-581e-4b1a-a0d7-bff9f7dbb01d" 
COFORGE_ENDPOINT = "https://quasarmarket.coforge.com/qag/llmrouter-api/v2/chat/completions"
DB_FILE = "clinical_records.json"

# ============================================================
# CSS - POWER BI STYLE DASHBOARD
# ============================================================
st.markdown("""
<style>
    :root { --bg:#F6F8FA; --surface:#FFFFFF; --surface-secondary:#F8FAFC; --border:#E2E8F0; --border-strong:#CBD5E1; --text-primary:#17212B; --text-secondary:#64748B; --text-muted:#94A3B8; --primary:#0F766E; --primary-hover:#0D9488; --primary-light:#CCFBF1; --success:#15803D; --success-light:#DCFCE7; --warning:#B45309; --warning-light:#FEF3C7; --danger:#B91C1C; --danger-light:#FEE2E2; --info:#2563EB; --info-light:#DBEAFE; --purple:#7C3AED; --purple-light:#EDE9FE; }
    #MainMenu, header, footer { visibility: hidden; height: 0 !important; }
    .stApp { background: var(--bg) !important; font-family: Inter, system-ui, -apple-system, sans-serif; }
    .block-container { max-width: 100%; padding: 0.75rem 1.75rem 0.35rem !important; }
    .stMarkdown, .stText, label, h1, h2, h3, p { color: var(--text-primary) !important; }
    .stButton>button { background-color: var(--primary) !important; border: 1px solid var(--primary) !important; border-radius: 6px !important; min-height: 2rem !important; padding: 0.25rem 0.75rem !important; font-weight: 600 !important; }
    .stButton>button p, .stButton>button span { color: white !important; -webkit-text-fill-color: white !important; }
    .stButton>button:hover { background-color: var(--primary-hover) !important; border-color: var(--primary-hover) !important; }

    /* Input fields */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"] {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 5px !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="base-input"] { background-color: transparent !important; }

    input, textarea { color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important; caret-color: var(--text-primary) !important; }
    div[data-baseweb="select"] span { color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important; }

    /* Branding & Dashboard elements */
    .brand-title { color: var(--primary) !important; font-size: 26px; line-height: 1.05; font-weight: 750; margin: 0; }
    .brand-sub { color: var(--text-secondary) !important; font-size: 13px; margin: 2px 0 7px; }
    .page-heading { font-size: 24px; line-height: 1.1; font-weight: 700; margin: 0; }
    .page-kicker { color: var(--text-secondary) !important; font-size: 12px; margin: 2px 0 0; }
    .system-status { color: var(--success) !important; background: var(--success-light); border-radius: 999px; padding: 4px 9px; font-size: 11px; font-weight: 700; white-space: nowrap; }
    .toolbar-label, .shell-section-label { color: var(--text-muted) !important; font-size: 10px; font-weight: 750; letter-spacing: 1px; margin: 10px 0 3px; }
    .section-title { color: var(--text-primary); font-size: 16px; font-weight: 700; margin-top: 2px; }
    .section-subtitle { color: var(--text-secondary); font-size: 11px; margin: 0 0 5px; }
    .section-gap { height: 8px; }
    .kpi-context { color: var(--text-muted); font-size: 10px; margin-top: 3px; }
    .overview-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; border: 1px solid var(--border); border-radius: 7px; background: var(--surface); padding: 15px 12px; }
    .overview-grid div { border-left: 2px solid var(--border-strong); padding-left: 8px; }
    .overview-grid small, .patient-cell small, .insight-chip small, .shell-user small { display: block; color: var(--text-secondary); font-size: 10px; }
    .overview-grid b { display: block; font-size: 23px; margin-top: 5px; }
    .amber-text { color: var(--warning); } .green-text { color: var(--success); } .blue-text { color: var(--info); }
    .patient-table-header, .patient-cell { display: grid; }
    .patient-table-header { grid-template-columns: 2.2fr 1.15fr 1.7fr 1.55fr 1.05fr 1.15fr; color: var(--text-muted); font-size: 10px; font-weight: 750; letter-spacing: .7px; text-transform: uppercase; padding: 4px 8px; border-bottom: 1px solid var(--border-strong); }
    .patient-cell { gap: 2px; padding-top: 4px; } .patient-cell b { font-size: 12px; } .table-meta { display: block; color: var(--text-secondary); font-size: 11px; padding-top: 8px; } .doctor-text { color: var(--info); }
    .table-row-rule { border-bottom: 1px solid var(--border); margin: 2px 0; } .pagination-label { color: var(--text-secondary); font-size: 11px; text-align: center; padding-top: 7px; }
    .shell-logo { color: #F8FAFC !important; font-size: 24px; font-weight: 800; letter-spacing: -.6px; margin: 4px 0 0; } .shell-logo span { color: #5EEAD4 !important; }
    .shell-subtitle { color: #94A3B8 !important; font-size: 10px; line-height: 1.4; margin-bottom: 24px; }
    .shell-section-label { color: #94A3B8 !important; margin: 12px 0 5px; } .shell-divider { border-top: 1px solid #334155; margin: 16px 0 5px; }
    .nav-active-marker { background: #2DD4BF; height: 28px; width: 3px; position: absolute; left: 0; margin-top: -35px; }
    .shell-user { display: flex; align-items: center; gap: 8px; border-top: 1px solid #334155; padding-top: 13px; margin-top: 28px; color: #E5E7EB !important; font-size: 11px; } .user-avatar { background: #0F766E; border-radius: 50%; padding: 7px; font-size: 10px; }
    .clinical-graph { position: relative; overflow: hidden; margin: 8px 0 12px; background: #0F172A; border: 1px solid #1E293B; border-radius: 7px; }
    .graph-node { position: absolute; transform: translateX(-50%); max-width: 30%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; border-radius: 999px; padding: 7px 10px; color: white; font-size: 10px; font-weight: 700; text-align: center; z-index: 2; box-shadow: 0 0 0 3px rgba(15,23,42,.65); transition: transform .15s ease; } .graph-node:hover { transform: translateX(-50%) scale(1.06); }
    .patient-node { background: var(--primary); left: 50% !important; } .diagnosis-node { background: #7C3AED; } .symptom-node { background: #B45309; } .risk-node { background: #C2410C; }
    .graph-edge { position: absolute; height: 1px; transform-origin: left center; background: #64748B; opacity: .65; z-index: 1; }
    .insight-chip { display: inline-flex; align-items: center; gap: 7px; margin: 3px 4px 3px 0; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface-secondary); } .insight-chip b { font-size: 11px; } .insight-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--purple); } .insight-diagnosis .insight-dot { background: var(--danger); } .insight-symptom .insight-dot { background: var(--warning); } .insight-risk .insight-dot { background: #C2410C; }
    .insight-heading { color: var(--text-secondary); font-size: 10px; font-weight: 750; letter-spacing: .7px; text-transform: uppercase; margin: 9px 0 4px; }
    .workflow-steps { display: flex; gap: 0; margin: 14px 0 10px; color: var(--text-muted); font-size: 11px; } .workflow-steps span, .workflow-steps b { padding: 7px 16px; border-bottom: 2px solid var(--border); } .workflow-steps b { color: var(--primary); border-color: var(--primary); }
    .recording-prompt { color: var(--text-secondary); background: var(--surface-secondary); border: 1px dashed var(--border-strong); border-radius: 6px; padding: 15px; text-align: center; font-size: 12px; }
    .audit-note { color: var(--text-secondary); font-size: 11px; padding-bottom: 6px; }
    @media (max-width: 1100px) { .patient-table-header, [data-testid="stHorizontalBlock"]:has(.patient-cell) { min-width: 800px; } .block-container { padding-left: 1rem !important; padding-right: 1rem !important; } }

    /* Power BI Style KPI Cards */
    .kpi-card { background: var(--surface); padding: 9px 13px 8px; min-height: 68px; border-radius: 7px; border-top: 3px solid var(--primary); box-shadow: 0 1px 3px rgba(15,23,42,0.06); text-align: left; }
    .kpi-title { color: var(--text-secondary) !important; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; }
    .kpi-value { color: var(--text-primary) !important; font-size: 26px; line-height: 1.05; font-weight: 750; margin-top: 3px; }

    /* Dashboard containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--surface) !important;
        border-radius: 7px !important;
        box-shadow: 0 1px 3px rgba(15,23,42,0.06);
        padding: 7px 10px !important;
        border: 1px solid var(--border);
    }
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stVerticalBlockBorderWrapper"]) { gap: 0.35rem; }
    div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }
    div[data-testid="stButton"] { margin: 0; }
    .status-pill { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 10px; font-weight: 750; letter-spacing: 0.35px; }
    .status-pending { color: var(--warning); background: var(--warning-light); }
    .status-approved { color: var(--success); background: var(--success-light); }
    .records-row:hover { background: var(--surface-secondary); }
    hr { margin: 3px 0 6px !important; border-color: var(--border) !important; }
    [data-testid="stCaptionContainer"] { color: var(--text-secondary) !important; margin: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.65rem; }
    [data-testid="stVerticalBlock"] { gap: 0.45rem; }
    [data-testid="stSidebar"] { background: #111827 !important; }
    [data-testid="stSidebar"] * { color: #E5E7EB !important; }
    [data-testid="stSidebar"] .stButton>button { background: transparent !important; border-color: transparent !important; text-align: left !important; }
    [data-testid="stSidebar"] .stButton>button:hover { background: #164E63 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. DATABASE INITIALIZATION & STATE MANAGEMENT
# ============================================================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("records", [])
    return []

def save_db(records):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"records": records}, f, indent=4)

if "records" not in st.session_state: st.session_state.records = load_db()
if "page" not in st.session_state: st.session_state.page = "dashboard"
if "current_record" not in st.session_state: st.session_state.current_record = None
if "search_input" not in st.session_state: st.session_state.search_input = ""
if "dash_page" not in st.session_state: st.session_state.dash_page = 1
if "live_chunks" not in st.session_state: st.session_state.live_chunks = []
if "audio_key_counter" not in st.session_state: st.session_state.audio_key_counter = 0
if "chart_selected_date" not in st.session_state: st.session_state.chart_selected_date = None
if "chart_cases_page" not in st.session_state: st.session_state.chart_cases_page = 1

master_insights_list = [
    "None", "Diabetes (Type 2)", "Hypertension", "Hyperlipidemia",
    "Asthma", "Osteoarthritis", "Obesity", "Smoking History",
    "Alcohol Use", "Anxiety", "Depression", "Fever",
    "Chronic Cough", "Fatigue", "Headache", "Chest Pain", "Nausea", "Color Blindness"
]

def get_detected_insights(transcript_text):
    transcript_lower = transcript_text.lower()
    detected = set()
    keyword_map = {
        "diabetes": "Diabetes (Type 2)", "hypertension": "Hypertension", "high bp": "Hypertension",
        "cholesterol": "Hyperlipidemia", "asthma": "Asthma", "arthritis": "Osteoarthritis",
        "obesity": "Obesity", "smok": "Smoking History", "alcohol": "Alcohol Use",
        "anxiety": "Anxiety", "depression": "Depression", "fever": "Fever", "cough": "Chronic Cough",
        "fatigue": "Fatigue", "headache": "Headache", "chest pain": "Chest Pain", "nausea": "Nausea",
        "color blind": "Color Blindness"
    }
    for kw, condition in keyword_map.items():
        if kw in transcript_lower: detected.add(condition)
    return list(detected)

def call_clinical_llm(pat_name, pat_age, pat_gender, doctor_str, transcript):
    system_prompt = f"""You are an expert physician assistant. You will receive a raw, unpunctuated voice transcript.
    TASK 1: STRICT DIARIZATION (NO HALLUCINATIONS)
    Reconstruct the raw transcript into a readable dialogue.
    CRITICAL RULES:
    1. DO NOT invent, hallucinate, or add any automated questions. You must ONLY use the exact words provided.
    2. If it's a monologue, assign all text to the patient.
    3. Label lines as "{doctor_str}:" or "Patient ({pat_name}):"
    Start exactly with "--- DIARIZED TRANSCRIPT ---".

    TASK 2: CLINICAL NOTE
    Generate a strict, formal medical intake note.
    YOU MUST USE EXACTLY THESE BOLD HEADINGS (include the asterisks **):
    - **PATIENT INFORMATION**
    - **MAJOR DIAGNOSIS / ISSUES**
    - **PREVIOUS ALLERGIES**
    - **SYMPTOMS SHOWN**
    - **VITALS CHECKED**
    - **CLINICAL ASSESSMENT**
    - **MEDICATIONS PRESCRIBED**
    - **PLAN & RECOMMENDATIONS**

    Start this section exactly with "--- CLINICAL NOTE ---".
    If a section's details are missing, write 'Not discussed/checked'. For **MAJOR DIAGNOSIS / ISSUES**, write 'Awaiting manual input.' if no diagnosis is stated."""

    try:
        headers = {"Content-Type": "application/json", "X-API-KEY": COFORGE_API_KEY}
        body = {"model": "gpt-4o", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Patient: {pat_name} ({pat_age}, {pat_gender})\nTranscript: {transcript}"}], "temperature": 0.2}
        resp = requests.post(COFORGE_ENDPOINT, headers=headers, json=body, timeout=40)
        diarized_transcript = ""
        summary = ""
        transcript_data = []

        if resp.status_code == 200:
            data = resp.json()
            response_text = data["choices"][0]["message"]["content"]
            if "--- CLINICAL NOTE ---" in response_text:
                parts = response_text.split("--- CLINICAL NOTE ---")
                diarized_transcript = parts[0].replace("--- DIARIZED TRANSCRIPT ---", "").strip()
                summary = parts[1].strip()
            else:
                diarized_transcript = transcript
                summary = response_text

            for line in diarized_transcript.split('\n'):
                if line.strip():
                    if ':' in line:
                        speaker, text = line.split(':', 1)
                        transcript_data.append({"Speaker": speaker.strip(), "Text": text.strip()})
                    else:
                        transcript_data.append({"Speaker": "Unknown", "Text": line.strip()})
        else:
            transcript_data = [{"Speaker": "Unknown", "Text": transcript}]
            diarized_transcript = transcript
            summary = f"API Error: {resp.status_code}"
    except Exception as e:
        transcript_data = [{"Speaker": "Unknown", "Text": transcript}]
        diarized_transcript = transcript
        summary = f"Request failed: {str(e)}"
    return diarized_transcript, summary, transcript_data


# ============================================================
# REUSABLE ENTERPRISE UI COMPONENTS
# ============================================================
def render_sidebar(active_page):
    with st.sidebar:
        st.markdown('<div class="shell-logo">MS<span>cribe</span></div><div class="shell-subtitle">Clinical Intelligence Platform</div>', unsafe_allow_html=True)
        st.markdown('<div class="shell-section-label">WORKSPACE</div>', unsafe_allow_html=True)
        navigation = [("dashboard", "Overview"), ("new_consult", "Consultations"), ("review", "Clinical Review"), ("dashboard", "Analytics")]
        for page_key, label in navigation:
            active = (active_page == page_key and not (label == "Analytics" and active_page == "dashboard"))
            if st.button(label, key=f"nav_{label.lower().replace(' ', '_')}", use_container_width=True, type="secondary"):
                if page_key == "review" and st.session_state.current_record is None:
                    st.session_state.page = "dashboard"
                else:
                    st.session_state.page = page_key
                st.rerun()
            if active:
                st.markdown('<div class="nav-active-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="shell-divider"></div><div class="shell-section-label">UTILITY</div>', unsafe_allow_html=True)
        st.button("Settings", key="nav_settings", use_container_width=True, type="secondary")
        st.button("Help", key="nav_help", use_container_width=True, type="secondary")
        st.markdown('<div class="shell-user"><div class="user-avatar">MS</div><div><b>MScribe User</b><small>Clinical Operations</small></div></div>', unsafe_allow_html=True)


def render_header(title, subtitle, show_new=True):
    left, right = st.columns([7, 3], gap="large")
    with left:
        st.markdown(f'<div class="page-heading">{escape(title)}</div><div class="page-kicker">{escape(subtitle)}</div>', unsafe_allow_html=True)
    with right:
        status_col, action_col = st.columns([1, 2])
        status_col.markdown('<div class="system-status">System operational</div>', unsafe_allow_html=True)
        if show_new and action_col.button("New Consultation", key="header_new_consult", use_container_width=True):
            st.session_state.live_chunks = []
            st.session_state.audio_key_counter = 0
            st.session_state.page = "new_consult"
            st.rerun()


def render_kpi_card(label, value, accent, context):
    st.markdown(f'<div class="kpi-card" style="border-top-color:{accent};"><div class="kpi-title">{escape(label)}</div><div class="kpi-value">{value}</div><div class="kpi-context">{escape(context)}</div></div>', unsafe_allow_html=True)


def render_status_badge(status):
    css_class = "status-approved" if status == "Approved" else "status-pending"
    return f'<span class="status-pill {css_class}">{escape(status.upper())}</span>'


def render_patient_table(records, selected_date=None):
    if selected_date:
        records = [record for record in records if record.get("date") == selected_date or record.get("approval_date") == selected_date]
        st.caption(f"Cases for {selected_date} ({len(records)})")

    records_per_page = 3 if selected_date else 5
    total_pages = max(1, math.ceil(len(records) / records_per_page))
    page_state_key = "chart_cases_page" if selected_date else "dash_page"
    if st.session_state[page_state_key] > total_pages:
        st.session_state[page_state_key] = 1
    current_page = st.session_state[page_state_key]
    current_records = records[(current_page - 1) * records_per_page:current_page * records_per_page]

    st.markdown('<div class="patient-table-header"><span>Patient</span><span>ID</span><span>Doctor</span><span>Date</span><span>Status</span><span>Action</span></div>', unsafe_allow_html=True)
    for record in current_records:
        status = record.get("status", "Pending")
        date_text = record.get("date", "")
        if status == "Approved" and record.get("approval_date"):
            date_text = f"Approved {record['approval_date']}"
        row = st.container()
        with row:
            cols = st.columns([2.2, 1.15, 1.7, 1.55, 1.05, 1.15])
            cols[0].markdown(f'<div class="patient-cell"><b>{escape(record.get("name", ""))}</b><small>{escape(record.get("age", ""))}y · {escape(record.get("gender", ""))}</small></div>', unsafe_allow_html=True)
            cols[1].markdown(f'<span class="table-meta">{escape(record.get("id", ""))}</span>', unsafe_allow_html=True)
            cols[2].markdown(f'<span class="table-meta doctor-text">{escape(record.get("doctor", "N/A"))}</span>', unsafe_allow_html=True)
            cols[3].markdown(f'<span class="table-meta">{escape(date_text)}<br>{escape(record.get("time", ""))}</span>', unsafe_allow_html=True)
            cols[4].markdown(render_status_badge(status), unsafe_allow_html=True)
            if cols[5].button("Review" if status == "Pending" else "View", key=f"btn_{record.get('id', '')}", use_container_width=True):
                st.session_state.current_record = record
                st.session_state.page = "review"
                st.session_state.insight_count = 1
                st.session_state.detected_insights = get_detected_insights(record.get("transcript", ""))
                st.rerun()
        st.markdown('<div class="table-row-rule"></div>', unsafe_allow_html=True)

    if total_pages > 1:
        previous, page_info, next_page = st.columns([1, 2, 1])
        if previous.button("Previous", key=f"prev_cases_{selected_date}", disabled=current_page == 1, use_container_width=True):
            st.session_state[page_state_key] -= 1
            st.rerun()
        page_info.markdown(f'<div class="pagination-label">Page {current_page} of {total_pages}</div>', unsafe_allow_html=True)
        if next_page.button("Next", key=f"next_cases_{selected_date}", disabled=current_page == total_pages, use_container_width=True):
            st.session_state[page_state_key] += 1
            st.rerun()


def render_clinical_graph(patient_name, insights):
    nodes = [("PATIENT", "patient-node", 50, 10)]
    node_types = [("diabetes", "DIAGNOSIS", "diagnosis-node"), ("hypertension", "DIAGNOSIS", "diagnosis-node"), ("hyperlipidemia", "DIAGNOSIS", "diagnosis-node"), ("asthma", "DIAGNOSIS", "diagnosis-node"), ("arthritis", "DIAGNOSIS", "diagnosis-node"), ("obesity", "RISK FACTOR", "risk-node"), ("smoking", "RISK FACTOR", "risk-node"), ("alcohol", "RISK FACTOR", "risk-node")]
    for insight in insights:
        lowered = insight.lower()
        category, node_class = "SYMPTOM", "symptom-node"
        for keyword, candidate_category, candidate_class in node_types:
            if keyword in lowered:
                category, node_class = candidate_category, candidate_class
                break
        nodes.append((insight, node_class, 20 + ((len(nodes) - 1) % 3) * 30, 42 + ((len(nodes) - 1) // 3) * 34))
    edge_markup = "".join(f'<div class="graph-edge" style="left:50%;top:28px;width:{abs(x-50)}%;transform:rotate({(x-50)*0.65}deg);"></div>' for _, _, x, y in nodes[1:])
    node_markup = "".join(f'<div class="graph-node {node_class}" title="{escape(label)}" style="left:{x}%;top:{y}px;">{escape(label[:22])}</div>' for label, node_class, x, y in nodes)
    height = max(190, 130 + ((len(nodes) + 2) // 3) * 34)
    st.markdown(f'<div class="clinical-graph" style="height:{height}px;">{edge_markup}{node_markup}</div>', unsafe_allow_html=True)


def render_insight_chip(insight):
    lowered = insight.lower()
    category = "SYMPTOM"
    color_class = "insight-symptom"
    if any(value in lowered for value in ("diabetes", "hypertension", "cholesterol", "asthma", "arthritis")):
        category, color_class = "DIAGNOSIS", "insight-diagnosis"
    elif any(value in lowered for value in ("smok", "alcohol", "obesity")):
        category, color_class = "RISK FACTOR", "insight-risk"
    st.markdown(f'<div class="insight-chip {color_class}"><span class="insight-dot"></span><div><b>{escape(insight)}</b><small>{category} · detected</small></div></div>', unsafe_allow_html=True)


def render_transcript(record):
    with st.expander("Transcript Audit Trail", expanded=False):
        doc_name = record.get("doctor", "Doctor")
        patient_name = record.get("name", "Patient")
        if "transcript_data" in record and record["transcript_data"]:
            transcript_df = pd.DataFrame(record["transcript_data"])
        else:
            transcript_df = pd.DataFrame([{"Speaker": "Unknown", "Text": record.get("transcript", "No transcript found.")}])
        st.markdown(f'<div class="audit-note">Editable clinical conversation · {len(transcript_df)} entries</div>', unsafe_allow_html=True)
        return st.data_editor(transcript_df, use_container_width=True, num_rows="dynamic", hide_index=True, column_config={"Speaker": st.column_config.SelectboxColumn("Speaker", width="medium", options=[doc_name, f"Patient ({patient_name})", "Unknown"], required=True), "Text": st.column_config.TextColumn("Spoken Text", width="large")})

# ============================================================
# PAGE 1: DASHBOARD
# ============================================================
def show_dashboard():
    render_sidebar("dashboard")
    render_header("Clinical Operations", "Consultation and documentation overview")

    # --- FILTERING & SEARCH ---
    st.markdown('<div class="toolbar-label">RECORD DIRECTORY</div>', unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([5, 2, 3])
    with f_col1:
        search_query = st.text_input("Search patient or ID", placeholder="Search patient or ID").strip().lower()
    custom_dates = None
    with f_col2:
        date_filter = st.selectbox("Date", ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom Date Range"])
    with f_col3:
        status_filter = st.selectbox("Status", ["All Statuses", "Pending", "Approved"])
    if date_filter == "Custom Date Range":
        with f_col3:
            custom_dates = st.date_input("Custom Range", value=(datetime.now().date(), datetime.now().date()))

    filtered_records = []
    today = datetime.now().date()
    for record in st.session_state.records:
        if search_query and (search_query not in record["name"].lower() and search_query not in record["id"].lower()):
            continue
        if status_filter != "All Statuses" and record.get("status") != status_filter:
            continue
        try:
            rec_date = datetime.strptime(record["date"], "%d/%m/%Y").date()
        except ValueError:
            rec_date = today
        keep = True
        if date_filter == "Today": keep = (rec_date == today)
        elif date_filter == "Last 7 Days": keep = 0 <= (today - rec_date).days <= 7
        elif date_filter == "Last 30 Days": keep = 0 <= (today - rec_date).days <= 30
        elif date_filter == "Custom Date Range":
            if isinstance(custom_dates, tuple) and len(custom_dates) == 2:
                keep = custom_dates[0] <= rec_date <= custom_dates[1]
            elif isinstance(custom_dates, tuple) and len(custom_dates) == 1:
                keep = rec_date == custom_dates[0]
        if keep: filtered_records.append(record)

    # --- CALCULATE KPIs ---
    total = len(filtered_records)
    pending = sum(1 for r in filtered_records if r["status"] == "Pending")
    approved = sum(1 for r in filtered_records if r["status"] == "Approved")
    today_count = sum(1 for r in filtered_records if r.get("date", "") == today.strftime("%d/%m/%Y"))

    # --- RENDER KPI CARDS ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: render_kpi_card("Total Consultations", total, "#0F766E", "All recorded consults")
    with k2: render_kpi_card("Today's Volume", today_count, "#2563EB", "Created today")
    with k3: render_kpi_card("Pending Review", pending, "#B45309", "Requires attention")
    with k4: render_kpi_card("Approved Notes", approved, "#15803D", "Completed documentation")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # --- RENDER TIME SERIES GRAPH (True Event Snapshot Logic) ---
    selected_date = st.session_state.chart_selected_date
    chart_column, overview_column = st.columns([6.5, 3.5], gap="large")
    with chart_column:
        st.markdown('<div class="section-title">Consultation Activity</div><div class="section-subtitle">Daily consultation throughput and backlog</div>', unsafe_allow_html=True)
        if selected_date and st.button("Show all dates", key="clear_chart_filter"):
            st.session_state.chart_selected_date = None
            st.session_state.chart_cases_page = 1
            st.rerun()
        if total > 0:

            # Step 1: Collect every unique date that something happened (creation or approval)
            all_dates = set()
            for r in filtered_records:
                if 'date' in r: all_dates.add(r['date'])
                if 'approval_date' in r: all_dates.add(r['approval_date'])
                # Fallback for old records that were approved before we added approval_date
                elif r.get('status') == 'Approved': all_dates.add(r['date'])

            # Step 2: Sort dates chronologically
            sorted_dates = sorted(list(all_dates), key=lambda d: pd.to_datetime(d, format="%d/%m/%Y", errors='coerce'))

            chart_data = []
            cum_created = 0
            cum_approved = 0

            # Step 3: Walk through time day-by-day and calculate metrics
            for d in sorted_dates:
                # Count records created on this specific day
                created_today = sum(1 for r in filtered_records if r.get('date') == d)

                # Count records approved on this specific day
                approved_today = sum(1 for r in filtered_records if r.get('status') == 'Approved' and r.get('approval_date', r.get('date')) == d)

                cum_created += created_today
                cum_approved += approved_today

                # True backlog at the end of this day
                current_pending = cum_created - cum_approved

                chart_data.append({
                    'DateStr': d,
                    'DateObj': pd.to_datetime(d, format="%d/%m/%Y", errors='coerce'),
                    'New Consults': created_today,
                    'Approved Today': approved_today,
                    'Total Pending Backlog': current_pending
                })

            df_chart = pd.DataFrame(chart_data).dropna(subset=['DateObj'])

            if not df_chart.empty:
                melted_df = df_chart.melt(
                    id_vars=['DateStr', 'DateObj'],
                    value_vars=['New Consults', 'Approved Today', 'Total Pending Backlog'],
                    var_name='Metric',
                    value_name='Count'
                )

                color_scale = alt.Scale(
                    domain=['New Consults', 'Approved Today', 'Total Pending Backlog'],
                    range=['#2563EB', '#10B981', '#E11D48']
                )

                chart_point = alt.selection_point(name="chart_point", fields=["DateStr"], empty=False)
                line_chart = alt.Chart(melted_df).mark_line(point=True).add_params(chart_point).encode(
                    x=alt.X('DateStr:O', title='Date', sort=alt.EncodingSortField(field='DateObj', order='ascending'), axis=alt.Axis(labelAngle=-45, grid=False)),
                    y=alt.Y('Count:Q', title='Number of Records', axis=alt.Axis(tickMinStep=1)),
                    color=alt.Color('Metric:N', scale=color_scale, legend=alt.Legend(title="", orient="top", symbolType="circle")),
                    tooltip=[alt.Tooltip('DateStr:N', title='Date'), 'Metric:N', 'Count:Q']
                ).properties(height=220)

                chart_event = st.altair_chart(line_chart, use_container_width=True, on_select="rerun", key="dashboard_chart")
                selected_points = chart_event.selection.get("chart_point", [])
                if selected_points:
                    clicked_date = selected_points[0].get("DateStr")
                    if clicked_date != st.session_state.chart_selected_date:
                        st.session_state.chart_selected_date = clicked_date
                        st.session_state.chart_cases_page = 1
                        st.rerun()
            else:
                st.caption("Not enough valid date data to generate chart.")

    with overview_column:
        st.markdown('<div class="section-title">Clinical Overview</div><div class="section-subtitle">Current operating position</div>', unsafe_allow_html=True)
        approval_rate = round((approved / total) * 100) if total else 0
        st.markdown(f'<div class="overview-grid"><div><small>Pending review</small><b class="amber-text">{pending}</b></div><div><small>Approval rate</small><b class="green-text">{approval_rate}%</b></div><div><small>Today\'s consultations</small><b class="blue-text">{today_count}</b></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # --- PAGINATED DATA TABLE ---
    st.markdown('<div class="section-title">Patient Records</div><div class="section-subtitle">Clinical documentation queue</div>', unsafe_allow_html=True)
    if total > 0:
        render_patient_table(filtered_records, selected_date)
    else:
        st.info("No clinical records found.")

# ============================================================
# PAGE 2: NEW CONSULTATION
# ============================================================
def show_new_consultation():
    render_sidebar("new_consult")
    render_header("New Consultation", "Capture patient context and generate clinical documentation", show_new=False)
    st.markdown('<div class="workflow-steps"><b>01 Patient</b><span>02 Record</span><span>03 Generate</span><span>04 Review</span></div>', unsafe_allow_html=True)
    st.button("Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))

    with st.container(border=True):
        st.markdown('<div class="section-title">Patient Information</div><div class="section-subtitle">Enter the basic context for this consultation</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        pat_name = col1.text_input("Full Name (e.g. John Doe)")
        pat_age = col2.text_input("Age")
        pat_gender = col1.selectbox("Gender", ["Male", "Female", "Other"])
        doc_name = col2.text_input("Attending Doctor (e.g. Dr. Sarah Jenkins)")

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="section-title">Record Consultation</div><div class="section-subtitle">Capture the clinical conversation securely</div>', unsafe_allow_html=True)
        audio_file = st.audio_input("Record Audio", label_visibility="collapsed")

        st.markdown('<div class="recording-prompt">Audio input ready when you are</div>', unsafe_allow_html=True)
        generate_disabled = audio_file is None or not pat_name.strip()

        if st.button("Generate Clinical Note", type="primary", use_container_width=True, disabled=generate_disabled):
            if not pat_name.strip():
                st.error("Patient name is required!")
                return

            with st.spinner("Transcribing audio..."):
                recognizer = sr.Recognizer()
                try:
                    with sr.AudioFile(io.BytesIO(audio_file.read())) as source:
                        audio_data = recognizer.record(source)
                    transcript = recognizer.recognize_google(audio_data)
                except Exception as e:
                    transcript = ""
                    st.error(f"Error processing audio: {e}")

            with st.spinner("Analyzing context & generating summary..."):
                doctor_str = doc_name if doc_name else "Doctor"
                diarized_transcript, summary, transcript_data = call_clinical_llm(pat_name, pat_age, pat_gender, doctor_str, transcript)

            now = datetime.now()
            new_record = {
                "id": f"PT-{str(uuid.uuid4().int)[:4]}", "name": pat_name, "age": pat_age, "gender": pat_gender,
                "date": now.strftime("%d/%m/%Y"), "time": now.strftime("%H:%M"), "doctor": doctor_str,
                "status": "Pending", "transcript": diarized_transcript, "transcript_data": transcript_data, "summary": summary
            }

            st.session_state.records.insert(0, new_record)
            save_db(st.session_state.records)

            st.session_state.current_record = new_record
            st.session_state.insight_count = 1
            st.session_state.detected_insights = get_detected_insights(diarized_transcript)
            st.session_state.page = "review"
            st.rerun()

# ============================================================
# PAGE 3: REVIEW NOTE
# ============================================================
def show_review_note():
    render_sidebar("review")
    record = st.session_state.current_record

    top_back, top_title, top_status = st.columns([1, 6, 2])
    with top_back:
        if st.button("Back", key="review_back"):
            st.session_state.page = "dashboard"
            st.rerun()
    with top_title:
        st.markdown(f'<div class="page-heading">{escape(record.get("name", ""))}</div><div class="page-kicker">{escape(record.get("id", ""))} · {escape(record.get("age", ""))}y · {escape(record.get("gender", ""))} · {escape(record.get("doctor", "N/A"))}</div>', unsafe_allow_html=True)
    with top_status:
        st.markdown(render_status_badge(record.get("status", "Pending")), unsafe_allow_html=True)

    if "edit_summary" not in st.session_state or st.session_state.get('last_record_id') != record.get('id'):
        st.session_state.edit_summary = record.get('summary', '')
        st.session_state.last_record_id = record.get('id')

    col_left, col_right = st.columns([6, 4], gap="large")

    with col_left:
        st.markdown('<div class="section-title">Clinical Note</div><div class="section-subtitle">Structured documentation workspace</div>', unsafe_allow_html=True)
        st.text_area("Clinical note", key="edit_summary", height=510, label_visibility="collapsed")

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Clinical Intelligence</div><div class="section-subtitle">Detected relationships and insights</div>', unsafe_allow_html=True)
            insights = st.session_state.get("detected_insights", [])
            render_clinical_graph(record.get("name", "Patient"), insights)
            st.markdown('<div class="insight-heading">Detected Insights</div>', unsafe_allow_html=True)
            if insights:
                for insight in insights:
                    render_insight_chip(insight)
            else:
                st.caption("No insights detected in this transcript.")

            def add_insight_field():
                if st.session_state.insight_count < 6: st.session_state.insight_count += 1

            def push_to_summary():
                current_text = st.session_state.edit_summary
                target_heading = "- **MAJOR DIAGNOSIS / ISSUES**"
                fallback_heading1 = "- MAJOR DIAGNOSIS / ISSUES"
                fallback_heading2 = "**MAJOR DIAGNOSIS / ISSUES**"

                for i in range(st.session_state.insight_count):
                    val = st.session_state.get(f"insight_{i}", "")
                    if val and val != "None":
                        if "Awaiting manual input." in current_text: current_text = current_text.replace("Awaiting manual input.", f"• {val}")
                        elif target_heading in current_text: parts = current_text.split(target_heading, 1); current_text = parts[0] + target_heading + f"\n• {val}" + parts[1]
                        elif fallback_heading1 in current_text: parts = current_text.split(fallback_heading1, 1); current_text = parts[0] + fallback_heading1 + f"\n• {val}" + parts[1]
                        elif fallback_heading2 in current_text: parts = current_text.split(fallback_heading2, 1); current_text = parts[0] + fallback_heading2 + f"\n• {val}" + parts[1]
                        else: current_text = f"{target_heading}\n• {val}\n\n" + current_text
                st.session_state.edit_summary = current_text
                st.session_state.insight_count = 1

            st.markdown('<div class="insight-heading">Add Clinical Insight</div>', unsafe_allow_html=True)
            for i in range(st.session_state.insight_count):
                default_idx = 0
                if i < len(st.session_state.detected_insights):
                    auto_val = st.session_state.detected_insights[i]
                    if auto_val in master_insights_list: default_idx = master_insights_list.index(auto_val)
                st.selectbox(f"Insight {i+1}", master_insights_list, index=default_idx, key=f"insight_{i}", label_visibility="collapsed")

            c1, c2 = st.columns(2)
            c1.button("Add Clinical Insight", on_click=add_insight_field, use_container_width=True)
            c2.button("Push to Note", type="primary", on_click=push_to_summary, use_container_width=True)

    edited_df = render_transcript(record)

    st.write("---")

    def finalize_note():
        record['summary'] = st.session_state.edit_summary
        record['transcript_data'] = edited_df.to_dict('records')
        record['status'] = "Approved"
        # Stamp it with today's actual date when approved
        record['approval_date'] = datetime.now().strftime("%d/%m/%Y")
        for i, r in enumerate(st.session_state.records):
            if r['id'] == record['id']: st.session_state.records[i] = record; break
        save_db(st.session_state.records)
        st.session_state.page = "dashboard"

    def save_draft():
        record['summary'] = st.session_state.edit_summary
        record['transcript_data'] = edited_df.to_dict('records')
        for i, r in enumerate(st.session_state.records):
            if r['id'] == record['id']: st.session_state.records[i] = record; break
        save_db(st.session_state.records)
        st.success("Draft & Audit Trail Updated!")

    c1, c2, c3 = st.columns([7, 1.5, 1.5])
    if record.get('status') == "Pending":
        c2.button("Save Draft", on_click=save_draft, use_container_width=True)
        c3.button("Finalize Note", type="primary", on_click=finalize_note, use_container_width=True)
    else:
        c3.button("Update Record", type="primary", on_click=save_draft, use_container_width=True)

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "dashboard": show_dashboard()
elif st.session_state.page == "new_consult": show_new_consultation()
elif st.session_state.page == "review": show_review_note()