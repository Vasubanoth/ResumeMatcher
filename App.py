import streamlit as st
import google.generativeai as genai
import pdfplumber
import io
import json
import re
import os

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── API KEY (from Streamlit secrets or env, never shown to user) ────────────
def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")

API_KEY = get_api_key()

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #0f1117 !important;
    color: #e8eaf0 !important;
}

#MainMenu, footer, header[data-testid="stHeader"],
div[data-testid="stDecoration"] { display: none !important; }

.block-container { padding: 2rem 2.5rem !important; max-width: 1400px !important; }

.app-header {
    display: flex; align-items: center; gap: 16px;
    padding-bottom: 24px; border-bottom: 1px solid #2a2d3a; margin-bottom: 32px;
}
.app-logo { font-size: 28px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
.app-logo span { color: #7c6dff; }
.app-badge {
    background: #1e1f2e; border: 1px solid #3a3d52; color: #7078a0;
    font-family: 'Space Mono', monospace; font-size: 10px;
    letter-spacing: 0.1em; text-transform: uppercase; padding: 4px 10px; border-radius: 4px;
}

.panel-title {
    font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #7c6dff; margin-bottom: 20px;
    padding-bottom: 10px; border-bottom: 1px solid #2a2d3a;
}

.field-label { font-size: 13px; font-weight: 600; color: #c8cad8; margin-bottom: 4px; display: block; margin-top: 14px; }
.field-hint  { font-size: 11px; color: #4e5270; margin-bottom: 6px; display: block; }

div[data-testid="stTextArea"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stRadio"] label { display: none !important; }

div[data-testid="stTextArea"] textarea {
    background: #1a1c28 !important; border: 1.5px solid #2c2f45 !important;
    border-radius: 8px !important; color: #dde0f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13.5px !important; line-height: 1.65 !important; padding: 12px 14px !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #7c6dff !important; box-shadow: 0 0 0 3px rgba(124,109,255,0.15) !important;
}
div[data-testid="stTextArea"] textarea::placeholder { color: #353858 !important; }

div[data-testid="stTextInput"] input {
    background: #1a1c28 !important; border: 1.5px solid #2c2f45 !important;
    border-radius: 8px !important; color: #dde0f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13.5px !important; padding: 10px 14px !important; height: 44px !important;
}
div[data-testid="stTextInput"] input:focus { border-color: #7c6dff !important; }
div[data-testid="stTextInput"] input::placeholder { color: #353858 !important; }

div[data-testid="stFileUploader"] > div {
    background: #1a1c28 !important; border: 1.5px dashed #2c2f45 !important; border-radius: 8px !important;
}
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span { color: #7078a0 !important; font-size: 13px !important; }
div[data-testid="stFileUploadDropzone"] button {
    background: #252840 !important; color: #c8cad8 !important;
    border: 1px solid #3a3d52 !important; border-radius: 6px !important; font-size: 12px !important;
}

div[data-testid="stRadio"] > div { display: flex; gap: 8px; flex-direction: row !important; }
div[data-testid="stRadio"] label {
    display: flex !important; align-items: center;
    background: #1a1c28; border: 1.5px solid #2c2f45; border-radius: 6px;
    padding: 6px 14px; cursor: pointer; font-size: 12px !important;
    font-weight: 600 !important; color: #7078a0 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    border-color: #7c6dff !important; background: #1e1f38 !important; color: #a09aff !important;
}
div[data-testid="stRadio"] input { margin-right: 6px; accent-color: #7c6dff; }

.stButton button {
    background: linear-gradient(135deg, #7c6dff 0%, #9b59f5 100%) !important;
    color: #ffffff !important; border: none !important; border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 14px !important; padding: 14px 28px !important; width: 100% !important; margin-top: 8px !important;
}
.stButton button:hover:not(:disabled) { opacity: 0.88 !important; }
.stButton button:disabled { opacity: 0.3 !important; }

.score-card {
    background: #161820; border: 1px solid #2a2d3a; border-radius: 12px;
    padding: 22px 24px; display: flex; align-items: center; gap: 22px; margin-bottom: 22px;
}
.score-circle {
    width: 86px; height: 86px; border-radius: 50%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    flex-shrink: 0; border: 3px solid;
}
.score-num { font-family: 'Space Mono', monospace; font-size: 26px; font-weight: 700; line-height: 1; }
.score-lbl { font-size: 9px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.55; margin-top: 2px; }
.score-verdict { font-size: 17px; font-weight: 700; color: #e8eaf0; margin-bottom: 5px; }
.score-summary { font-size: 12.5px; color: #7078a0; line-height: 1.6; }

.rst { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    color: #4a4e68; margin: 18px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #1e2030; }

.chip-grid { display: flex; flex-wrap: wrap; gap: 5px; }
.chip { font-family: 'Space Mono', monospace; font-size: 11px; padding: 3px 9px; border-radius: 4px; border: 1px solid; }
.chip-match { background: #081a10; color: #4ade80; border-color: #143824; }
.chip-miss  { background: #1e0e0e; color: #f87171; border-color: #3a1616; }
.chip-bonus { background: #120e22; color: #a78bfa; border-color: #241850; }

.skill-row { margin-bottom: 13px; }
.skill-hdr { display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; color: #b0b4cc; margin-bottom: 5px; }
.skill-hdr span:last-child { font-family: 'Space Mono', monospace; color: #4a4e68; font-size: 11px; }
.skill-track { height: 5px; background: #1a1c28; border-radius: 3px; overflow: hidden; }
.skill-fill  { height: 100%; border-radius: 3px; }

.gap-item { padding: 12px 14px; border-radius: 8px; margin-bottom: 9px; border: 1px solid; }
.gap-high   { background: #160a0a; border-color: #3a1414; }
.gap-medium { background: #16120a; border-color: #3a2c10; }
.gap-low    { background: #081410; border-color: #103020; }
.gap-issue  { font-size: 13px; font-weight: 600; color: #dde0f0; margin-bottom: 4px; }
.gap-fix    { font-size: 12px; color: #606480; line-height: 1.55; }

.sug-item {
    background: #131524; border: 1px solid #1e2240; border-left: 3px solid #7c6dff;
    padding: 11px 13px; margin-bottom: 8px; border-radius: 0 8px 8px 0;
    font-size: 13px; line-height: 1.6; color: #b0b4cc;
}

.rw-box {
    background: #0a0b12; border: 1px solid #1e2030; color: #b0b4cc;
    padding: 18px 20px; border-radius: 8px;
    font-family: 'Space Mono', monospace; font-size: 12px; line-height: 1.8; white-space: pre-wrap;
}

div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 600 !important; color: #4a4e68 !important;
    padding: 8px 16px !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #a09aff !important; }
div[data-testid="stTabs"] [data-testid="stTabsContent"] {
    background: #161820 !important; border: 1px solid #2a2d3a !important;
    border-radius: 0 8px 8px 8px !important; padding: 18px !important;
}

div[data-testid="stExpander"] {
    background: #1a1c28 !important; border: 1px solid #2a2d3a !important; border-radius: 8px !important;
}
div[data-testid="stExpander"] summary { color: #7078a0 !important; font-size: 12px !important; }
.stCaption p { color: #4a4e68 !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-logo">Resume<span>IQ</span></div>
    <div class="app-badge">AI-Powered · Gemini 2.5 Flash</div>
</div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("⚠️ API key not configured. Add `GEMINI_API_KEY` to Streamlit secrets.")
    st.stop()


# ─── PDF EXTRACTION ───────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_file) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
            for table in page.extract_tables():
                for row in table:
                    row_text = " | ".join(c or "" for c in row if c)
                    if row_text.strip():
                        parts.append(row_text)
    return "\n\n".join(parts)


# ─── CLAUDE ANALYSIS ──────────────────────────────────────────────────────────
def analyse_resume(job_desc: str, resume_text: str, role_level: str) -> dict:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are an expert technical recruiter and career coach. Analyse the resume against the job description and return ONLY a valid JSON object (no markdown, no extra text, no code fences).

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}

{f'CANDIDATE LEVEL: {role_level}' if role_level else ''}

Return this exact JSON structure:
{{
  "score": <integer 0-100>,
  "verdict": "<3-6 word headline about fit>",
  "summary": "<2-3 sentence overall assessment>",
  "matched_skills": ["<skill>", ...],
  "missing_skills": ["<skill>", ...],
  "bonus_skills": ["<skill exceeding requirements>", ...],
  "skill_categories": [
    {{ "name": "<category>", "score": <0-100>, "color": "<hex>" }}
  ],
  "gaps": [
    {{ "severity": "high|medium|low", "issue": "<gap>", "fix": "<how to address>" }}
  ],
  "suggestions": ["<actionable improvement>", ...],
  "rewritten_summary": "<rewrite candidate professional summary targeting this role, 3-4 sentences>"
}}

skill_categories: 3-5 role-relevant categories. Use colors: #4ade80 strong, #facc15 medium, #f87171 weak.
matched_skills and missing_skills must come directly from JD requirements."""

    response = model.generate_content(prompt)
    clean = re.sub(r"```(?:json)?|```", "", response.text).strip()
    return json.loads(clean)


# ─── RENDER RESULTS ───────────────────────────────────────────────────────────
def render_results(r: dict):
    score = max(0, min(100, r.get("score", 0)))
    if score >= 70:
        rc, rb = "#4ade80", "#081a10"
    elif score >= 45:
        rc, rb = "#facc15", "#16120a"
    else:
        rc, rb = "#f87171", "#160a0a"

    st.markdown(f"""
    <div class="score-card">
        <div class="score-circle" style="border-color:{rc};background:{rb}">
            <div class="score-num" style="color:{rc}">{score}</div>
            <div class="score-lbl" style="color:{rc}">/ 100</div>
        </div>
        <div style="flex:1">
            <div class="score-verdict">{r.get('verdict','Analysis complete')}</div>
            <div class="score-summary">{r.get('summary','')}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["📊  Skills", "🔍  Gaps", "💡  Improve", "✍️  Rewrite"])

    with t1:
        for cat in r.get("skill_categories", []):
            p = max(0, min(100, cat.get("score", 0)))
            c = cat.get("color", "#7c6dff")
            st.markdown(f'<div class="skill-row"><div class="skill-hdr"><span>{cat["name"]}</span><span>{p}/100</span></div><div class="skill-track"><div class="skill-fill" style="width:{p}%;background:{c}"></div></div></div>', unsafe_allow_html=True)

        for label, key, cls in [("✓ Matched", "matched_skills", "chip-match"), ("✗ Missing", "missing_skills", "chip-miss"), ("★ Bonus", "bonus_skills", "chip-bonus")]:
            items = r.get(key, [])
            if items:
                chips = "".join(f'<span class="chip {cls}">{s}</span>' for s in items)
                st.markdown(f'<div class="rst">{label}</div><div class="chip-grid">{chips}</div>', unsafe_allow_html=True)

    with t2:
        gaps = r.get("gaps", [])
        icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        if gaps:
            for g in gaps:
                sev = g.get("severity", "medium")
                st.markdown(f'<div class="gap-item gap-{sev}"><div class="gap-issue">{icons.get(sev,"•")} {g.get("issue","")}</div><div class="gap-fix">{g.get("fix","")}</div></div>', unsafe_allow_html=True)
        else:
            st.success("No significant gaps found.")

    with t3:
        sugs = r.get("suggestions", [])
        if sugs:
            for s in sugs:
                st.markdown(f'<div class="sug-item">{s}</div>', unsafe_allow_html=True)
        else:
            st.info("No suggestions at this time.")

    with t4:
        rw = r.get("rewritten_summary", "")
        st.markdown(f'<div class="rst">AI-rewritten professional summary</div><div class="rw-box">{rw}</div>', unsafe_allow_html=True)
        st.caption("Tailored to this job description — copy and edit as needed.")
        if rw:
            st.code(rw, language=None)


# ─── LAYOUT ───────────────────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    st.markdown('<div class="panel-title">01 · Your Details</div>', unsafe_allow_html=True)

    st.markdown('<span class="field-label">Job Description</span><span class="field-hint">Paste the full job posting — responsibilities, requirements, nice-to-haves</span>', unsafe_allow_html=True)
    job_desc = st.text_area("jd", height=200, placeholder="e.g. We are looking for a Data Analyst with 2+ years of SQL, Python and dashboard experience...", label_visibility="collapsed")

    st.markdown('<span class="field-label">Your Resume / CV</span>', unsafe_allow_html=True)
    mode = st.radio("mode", ["📎  Upload PDF", "📝  Paste text"], horizontal=True, label_visibility="collapsed")

    resume_text = ""
    if mode == "📎  Upload PDF":
        st.markdown('<span class="field-hint">Upload your resume as a PDF</span>', unsafe_allow_html=True)
        f = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
        if f:
            with st.spinner("Extracting text…"):
                try:
                    resume_text = extract_text_from_pdf(f)
                    st.success(f"✓ Extracted {len(resume_text.split()):,} words from **{f.name}**")
                    with st.expander("Preview extracted text"):
                        st.text(resume_text[:1500] + ("…" if len(resume_text) > 1500 else ""))
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
    else:
        st.markdown('<span class="field-hint">Paste your resume text — experience, skills, education, projects</span>', unsafe_allow_html=True)
        resume_text = st.text_area("resume", height=220,
            placeholder="e.g. Data Analyst Intern @ Mentrisea Edutech\n• Built LLM pipelines with Gemini 2.0 Pro...",
            label_visibility="collapsed")

    st.markdown('<span class="field-label">Role Level <span style="font-weight:400;color:#4e5270">(optional)</span></span>', unsafe_allow_html=True)
    role_level = st.text_input("lvl", placeholder="e.g. Entry-level, 2 YOE, Senior…", label_visibility="collapsed")

    ready = len(job_desc.strip()) > 50 and len(resume_text.strip()) > 50
    btn = st.button("✦  Screen My Resume", disabled=not ready, use_container_width=True)
    if not ready:
        st.caption("Add job description and resume (50+ chars each) to enable screening.")

with col_r:
    st.markdown('<div class="panel-title">02 · AI Analysis</div>', unsafe_allow_html=True)

    if "result" not in st.session_state:
        st.session_state.result = None
    if "err" not in st.session_state:
        st.session_state.err = None

    if btn and ready:
        st.session_state.result = None
        st.session_state.err = None
        with st.spinner("Gemini is reading your resume…"):
            try:
                st.session_state.result = analyse_resume(job_desc, resume_text, role_level)
            except json.JSONDecodeError as e:
                st.session_state.err = f"Parse error — try again. ({e})"
            except Exception as e:
                err_str = str(e)
                if "API_KEY" in err_str or "credentials" in err_str.lower():
                    st.session_state.err = "Invalid API key. Check your GEMINI_API_KEY in Streamlit secrets."
                elif "quota" in err_str.lower() or "429" in err_str:
                    st.session_state.err = "Rate limit hit — wait a moment and retry. (Free tier: 10 req/min)"
                else:
                    st.session_state.err = err_str

    if st.session_state.err:
        st.error(st.session_state.err)
    elif st.session_state.result:
        render_results(st.session_state.result)
    else:
        st.markdown("""
        <div style="padding:80px 0;text-align:center">
            <div style="font-size:44px;opacity:0.08;margin-bottom:16px">◈</div>
            <div style="font-size:14px;font-weight:600;color:#2a2d3a;margin-bottom:8px">No analysis yet</div>
            <div style="font-size:12.5px;color:#22253a;max-width:260px;margin:0 auto;line-height:1.7">
                Fill in the job description and your resume on the left, then hit <strong style="color:#3a3d58">Screen My Resume</strong>.
            </div>
        </div>""", unsafe_allow_html=True)
