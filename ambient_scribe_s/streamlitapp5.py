
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
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from aiortc.contrib.media import MediaRecorder

# ============================================================
# 1. CONFIGURATION & CLINICAL THEME
# ============================================================
st.set_page_config(page_title="MScribe | Clinical Scribe", layout="wide", page_icon="⚕️", menu_items=None)

try:
    COFORGE_API_KEY = st.secrets.get("COFORGE_API_KEY", os.getenv("COFORGE_API_KEY", ""))
except FileNotFoundError:
    COFORGE_API_KEY = os.getenv("COFORGE_API_KEY", "")
COFORGE_ENDPOINT = "https://quasarmarket.coforge.com/qag/llmrouter-api/v2/chat/completions"
DB_FILE = "clinical_records.json"

# ============================================================
# CSS - POWER BI STYLE DASHBOARD
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #F3F6F8 !important; }
    #MainMenu, header, footer { visibility: hidden; height: 0 !important; }
    .block-container { padding-top: 1rem !important; }
    .stMarkdown, .stText, label, h1, h2, h3, p { color: #1E293B !important; }
    .stButton>button { background-color: #0D9488 !important; border: none !important; border-radius: 6px !important; }
    .stButton>button p, .stButton>button span { color: white !important; -webkit-text-fill-color: white !important; }
    .stButton>button:hover { background-color: #0F766E !important; }

    /* Input fields */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="base-input"] { background-color: transparent !important; }

    input, textarea { color: #1E293B !important; -webkit-text-fill-color: #1E293B !important; caret-color: #1E293B !important; }
    div[data-baseweb="select"] span { color: #1E293B !important; -webkit-text-fill-color: #1E293B !important; }

    /* Branding & Dashboard elements */
    .brand-title { color: #0D9488 !important; font-size: 28px; font-weight: bold; margin-bottom: -15px; letter-spacing: -0.5px; }
    .brand-sub { color: #64748B !important; font-size: 16px; margin-bottom: 24px; }

    /* Power BI Style KPI Cards */
    .kpi-card { background-color: white; padding: 20px; border-radius: 8px; border-top: 4px solid #0D9488; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center;}
    .kpi-title { color: #64748B !important; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .kpi-value { color: #1E293B !important; font-size: 36px; font-weight: bold; margin-top: 8px; }

    /* Dashboard containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        padding: 15px;
        border: 1px solid #E2E8F0;
    }
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
if "recording_active" not in st.session_state: st.session_state.recording_active = False
if "recording_file_path" not in st.session_state: st.session_state.recording_file_path = None
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
# PAGE 1: DASHBOARD
# ============================================================
def show_dashboard():
    st.markdown('<div class="brand-title">MScribe</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Clinical Dashboard & Analytics</div>', unsafe_allow_html=True)

    header_col, action_col = st.columns([8, 2])
    with action_col:
        if st.button("New Consultation", use_container_width=True):
            st.session_state.live_chunks = []
            st.session_state.audio_key_counter = 0
            st.session_state.page = "new_consult"
            st.rerun()

    filter_col, search_col = st.columns([4, 6])
    with filter_col:
        date_filter = st.selectbox("Date Filter", ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom Date Range"])
    custom_dates = None
    if date_filter == "Custom Date Range":
        with filter_col:
            custom_dates = st.date_input("Custom Range", value=(datetime.now().date(), datetime.now().date()))
    with search_col:
        search_query = st.text_input("Search Patient Name or ID").strip().lower()

    filtered_records = []
    today = datetime.now().date()
    for record in st.session_state.records:
        if search_query and (search_query not in record["name"].lower() and search_query not in record["id"].lower()):
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
    k1.markdown(f'<div class="kpi-card" style="border-top-color: #0D9488;"><div class="kpi-title">Total Consults</div><div class="kpi-value">{total}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card" style="border-top-color: #64748B;"><div class="kpi-title">Today\'s Volume</div><div class="kpi-value">{today_count}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card" style="border-top-color: #F59E0B;"><div class="kpi-title">Pending Review</div><div class="kpi-value" style="color:#F59E0B;">{pending}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card" style="border-top-color: #10B981;"><div class="kpi-title">Approved Notes</div><div class="kpi-value" style="color:#10B981;">{approved}</div></div>', unsafe_allow_html=True)

    selected_date = st.session_state.chart_selected_date
    if selected_date:
        chart_col, table_col = st.columns([3, 7], gap="large")
    else:
        chart_col = st.container()
        table_col = st.container()

    with chart_col:
        with st.container(border=True):
            st.markdown("<p style='font-weight:600; color:#1E293B;'>Daily Consultation Activity</p>", unsafe_allow_html=True)
            if selected_date and st.button("Show all cases", key="clear_chart_filter", use_container_width=True):
                st.session_state.chart_selected_date = None
                st.session_state.chart_cases_page = 1
                st.rerun()
            if total > 0:
                date_events = set()
                for record in filtered_records:
                    if record.get('date'):
                        date_events.add(record['date'])
                    if record.get('status') == 'Approved' and record.get('approval_date'):
                        date_events.add(record['approval_date'])

                sorted_dates = sorted(
                    date_events,
                    key=lambda value: pd.to_datetime(value, format="%d/%m/%Y", errors='coerce')
                )
                if sorted_dates:
                    chart_rows = []
                    cumulative_created = 0
                    cumulative_approved = 0
                    for date_value in sorted_dates:
                        created_today = sum(1 for record in filtered_records if record.get('date') == date_value)
                        approved_today = sum(
                            1 for record in filtered_records
                            if record.get('status') == 'Approved'
                            and record.get('approval_date', record.get('date')) == date_value
                        )
                        cumulative_created += created_today
                        cumulative_approved += approved_today
                        chart_rows.append({
                            'DateObj': pd.to_datetime(date_value, format="%d/%m/%Y", errors='coerce'),
                            'DateKey': date_value,
                            'Day': pd.to_datetime(date_value, format="%d/%m/%Y").day,
                            'Total': created_today,
                            'Pending': cumulative_created - cumulative_approved,
                            'Approved': approved_today
                        })

                    agg_df = pd.DataFrame(chart_rows).dropna(subset=['DateObj'])
                    melted_df = agg_df.melt(id_vars=['DateObj', 'DateKey', 'Day'], value_vars=['Total', 'Pending', 'Approved'], var_name='Metric', value_name='Count')
                    color_scale = alt.Scale(domain=['Total', 'Approved', 'Pending'], range=['#2563EB', '#10B981', '#DC2626'])
                    chart_point = alt.selection_point(name="chart_point", fields=['DateKey'], empty=False)
                    line_chart = alt.Chart(melted_df).mark_line(point=True).add_params(chart_point).encode(
                        x=alt.X('Day:O', title='Day', sort=alt.SortField(field='DateObj', order='ascending'), axis=alt.Axis(labelAngle=0, grid=False)),
                        y=alt.Y('Count:Q', title='Number of Records', axis=alt.Axis(tickMinStep=1)),
                        color=alt.Color('Metric:N', scale=color_scale, legend=alt.Legend(title="", orient="top", symbolType="circle")),
                        tooltip=[alt.Tooltip('DateKey:N', title='Date'), 'Metric:N', 'Count:Q']
                    ).properties(height=280 if selected_date else 380)
                    chart_event = st.altair_chart(line_chart, use_container_width=True, on_select="rerun", key="dashboard_chart")
                    selected_points = chart_event.selection.get('chart_point', [])
                    if selected_points:
                        clicked_date = selected_points[0].get('DateKey')
                        if clicked_date != st.session_state.chart_selected_date:
                            st.session_state.chart_selected_date = clicked_date
                            st.session_state.chart_cases_page = 1
                            st.rerun()
                else:
                    st.caption("Not enough valid date data to generate chart.")

    with table_col:
        with st.container(border=True):
            st.markdown("<p style='font-weight:600; color:#1E293B;'>Patient Records Directory</p>", unsafe_allow_html=True)
            if total > 0:
                table_records = filtered_records
                if selected_date:
                    table_records = [r for r in table_records if r.get('date') == selected_date or r.get('approval_date') == selected_date]
                    st.caption(f"Cases for {selected_date} ({len(table_records)})")
                records_per_page = 3 if selected_date else 5
                total_pages = max(1, math.ceil(len(table_records) / records_per_page))
                if selected_date and st.session_state.chart_cases_page > total_pages:
                    st.session_state.chart_cases_page = 1
                page_key = 'chart_cases_page' if selected_date else 'dash_page'
                current_page = st.session_state[page_key]
                current_records = table_records[(current_page - 1) * records_per_page:current_page * records_per_page]
                columns = [3.2, 1.8, 1.4, 2.0] if selected_date else [3, 2, 2, 2]
                headers = st.columns(columns)
                for header, label in zip(headers, ['PATIENT & DOCTOR', 'DATE & TIME', 'STATUS', 'ACTIONS']):
                    header.markdown(f"<span style='color:#64748B; font-weight:bold; font-size:12px; border-bottom:1px solid #E2E8F0; display:block; padding-bottom:5px;'>{label}</span>", unsafe_allow_html=True)
                for record in current_records:
                    row_cols = st.columns(columns)
                    row_cols[0].markdown(f"<b>{record.get('name', '')}</b><br><span style='color:#64748B; font-size:13px;'>{record.get('id', '')} · {record.get('age', '')}y {record.get('gender', '')} · {record.get('doctor', 'N/A')}</span>", unsafe_allow_html=True)
                    row_cols[1].markdown(f"{record.get('date', '')}<br><span style='color:#64748B; font-size:13px;'>{record.get('time', '')}</span>", unsafe_allow_html=True)
                    status_color = '#DC2626' if record.get('status') == 'Pending' else '#10B981'
                    row_cols[2].markdown(f"<span style='color:{status_color}; font-weight:bold;'>{record.get('status', '').upper()}</span>", unsafe_allow_html=True)
                    if row_cols[3].button('Review Note' if record.get('status') == 'Pending' else 'View Record', key=f"btn_{record.get('id', '')}", use_container_width=True):
                        st.session_state.current_record = record
                        st.session_state.page = 'review'
                        st.session_state.insight_count = 1
                        st.session_state.detected_insights = get_detected_insights(record.get('transcript', ''))
                        st.rerun()
                if total_pages > 1:
                    previous, page_info, next_page = st.columns([2, 6, 2])
                    if previous.button('Previous', key=f'prev_cases_{selected_date}', disabled=current_page == 1, use_container_width=True):
                        st.session_state[page_key] -= 1
                        st.rerun()
                    page_info.markdown(f"<div style='text-align:center; color:#64748B; font-size:14px; margin-top:8px;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)
                    if next_page.button('Next', key=f'next_cases_{selected_date}', disabled=current_page == total_pages, use_container_width=True):
                        st.session_state[page_key] += 1
                        st.rerun()
            else:
                st.info("No clinical records found.")

# ============================================================
# PAGE 2: NEW CONSULTATION
# ============================================================
def show_new_consultation():
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    st.markdown("<h2 style='color: #1E293B;'>Start New Consultation</h2>", unsafe_allow_html=True)
    st.write("")

    with st.container(border=True):
        st.markdown("<h3 style='color:#1E293B;'>Patient Demographics</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        pat_name = col1.text_input("Full Name (e.g. John Doe)")
        pat_age = col2.text_input("Age")
        pat_gender = col1.selectbox("Gender", ["Male", "Female", "Other"])
        doc_name = col2.text_input("Attending Doctor (e.g. Dr. Sarah Jenkins)")

    st.write("")

    with st.container(border=True):
        st.markdown("<h3 style='color:#1E293B;'>🎙️ Record Consultation</h3>", unsafe_allow_html=True)
        start_col, stop_col, state_col = st.columns([1, 1, 3])
        with start_col:
            if st.button("Start", key="start_recording", use_container_width=True, disabled=st.session_state.recording_active):
                st.session_state.recording_file_path = None
                st.session_state.recording_active = True
                st.rerun()
        with stop_col:
            if st.button("Stop", key="stop_recording", use_container_width=True, disabled=not st.session_state.recording_active):
                st.session_state.recording_active = False
                st.rerun()
        with state_col:
            recording_status = "Recording active" if st.session_state.recording_active else "Ready to record"
            st.markdown(f"<div style='padding: 8px 0; color: #64748B; font-size: 13px;'>{recording_status}</div>", unsafe_allow_html=True)
        if st.session_state.recording_active and not st.session_state.recording_file_path:
            st.session_state.recording_file_path = os.path.join("uploads", f"consultation_{uuid.uuid4().hex}.wav")
        recording_path = st.session_state.recording_file_path or os.path.join("uploads", "consultation_preview.wav")
        os.makedirs(os.path.dirname(recording_path), exist_ok=True)
        webrtc_streamer(
            key="consultation_recorder",
            mode=WebRtcMode.SENDONLY,
            media_stream_constraints={"audio": True, "video": False},
            desired_playing_state=st.session_state.recording_active,
            in_recorder_factory=lambda: MediaRecorder(recording_path, format="wav"),
            media_toggle_controls=False,
        )

        st.write("")
        audio_file = None
        recording_is_ready = (
            not st.session_state.recording_active
            and st.session_state.recording_file_path
            and os.path.exists(st.session_state.recording_file_path)
            and os.path.getsize(st.session_state.recording_file_path) > 44
        )
        if recording_is_ready:
            audio_file = open(st.session_state.recording_file_path, "rb")
        generate_disabled = audio_file is None or not pat_name.strip()

        if st.button("✓ Generate Clinical Note", type="primary", use_container_width=True, disabled=generate_disabled):
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
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    record = st.session_state.current_record

    st.markdown(f"<h2 style='color: #1E293B;'>Clinical Review: {record.get('name','')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748B;'><b>ID:</b> {record.get('id','')} | <b>Demographics:</b> {record.get('age','')}y {record.get('gender','')} | <b>Attending:</b> {record.get('doctor', 'N/A')} | <b>Date:</b> {record.get('date','')}</p>", unsafe_allow_html=True)
    st.write("")

    if "edit_summary" not in st.session_state or st.session_state.get('last_record_id') != record.get('id'):
        st.session_state.edit_summary = record.get('summary', '')
        st.session_state.last_record_id = record.get('id')

    col_left, col_right = st.columns([5, 5], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("<h3 style='color: #1E293B;'>Structured Clinical Intake Summary</h3>", unsafe_allow_html=True)
            st.text_area("Summary", key="edit_summary", height=550, label_visibility="collapsed")

    with col_right:
        with st.container(border=True):
            st.markdown("<h3 style='color: #1E293B;'>Quick Inserts / Detected</h3>", unsafe_allow_html=True)

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

            for i in range(st.session_state.insight_count):
                default_idx = 0
                if i < len(st.session_state.detected_insights):
                    auto_val = st.session_state.detected_insights[i]
                    if auto_val in master_insights_list: default_idx = master_insights_list.index(auto_val)
                st.selectbox(f"Insight {i+1}", master_insights_list, index=default_idx, key=f"insight_{i}", label_visibility="collapsed")

            c1, c2 = st.columns(2)
            c1.button("➕ Add Field", on_click=add_insight_field, use_container_width=True)
            c2.button("✓ Push to Summary", type="primary", on_click=push_to_summary, use_container_width=True)

        st.write("")
        with st.container(border=True):
            st.markdown("<h3 style='color: #1E293B;'>Transcript Audit Trail</h3>", unsafe_allow_html=True)
            doc_name_str = record.get('doctor', 'Doctor')
            pat_name_str = record.get('name', 'Patient')

            if "transcript_data" in record and record["transcript_data"]: df = pd.DataFrame(record["transcript_data"])
            else: df = pd.DataFrame([{"Speaker": "Unknown", "Text": record.get("transcript", "No transcript found.")}])

            edited_df = st.data_editor(
                df, use_container_width=True, num_rows="dynamic", hide_index=True,
                column_config={"Speaker": st.column_config.SelectboxColumn("Speaker", width="medium", options=[doc_name_str, f"Patient ({pat_name_str})", "Unknown"], required=True), "Text": st.column_config.TextColumn("Spoken Text", width="large")}
            )

    st.write("---")

    def finalize_note():
        record['summary'] = st.session_state.edit_summary
        record['transcript_data'] = edited_df.to_dict('records')
        record['status'] = "Approved"
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
        c3.button("✓ Finalize Note", type="primary", on_click=finalize_note, use_container_width=True)
    else:
        c3.button("Update Record", type="primary", on_click=save_draft, use_container_width=True)

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "dashboard": show_dashboard()
elif st.session_state.page == "new_consult": show_new_consultation()
elif st.session_state.page == "review": show_review_note()