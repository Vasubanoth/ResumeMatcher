import streamlit as st
import anthropic
import pdfplumber
import io
import json
import re

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700&display=swap');

:root {
    --ink: #0e0e0e;
    --paper: #f5f0e8;
    --paper2: #ede7d8;
    --accent: #c84b2f;
    --accent2: #1a6b3a;
    --accent3: #2645a8;
    --muted: #7a7060;
    --border: #c8bfaa;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--paper);
}

.stApp { background-color: var(--paper); }

/* Header */
.resumeiq-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 20px 0 16px 0;
    border-bottom: 1.5px solid var(--border);
    margin-bottom: 28px;
}
.resumeiq-logo {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 32px;
    color: var(--ink);
    letter-spacing: -0.5px;
}
.resumeiq-logo span { color: #c84b2f; font-style: italic; }
.resumeiq-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border-left: 1.5px solid var(--border);
    padding-left: 16px;
}

/* Section labels */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

/* Score card */
.score-card {
    background: var(--paper2);
    border: 1.5px solid var(--border);
    border-radius: 4px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.score-number {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 52px;
    line-height: 1;
    color: var(--ink);
}
.score-verdict {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 20px;
    color: var(--ink);
    margin: 6px 0 4px;
}
.score-summary { font-size: 13px; color: var(--muted); line-height: 1.6; }

/* Chips */
.chip-container { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.chip {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 2px;
}
.chip-match  { background: #d4edda; color: #1a6b3a; border: 1px solid #a8d5b5; }
.chip-miss   { background: #fde8e8; color: #c84b2f; border: 1px solid #f4b8b5; }
.chip-bonus  { background: #dce8fd; color: #2645a8; border: 1px solid #b0c8f8; }

/* Gap severity */
.gap-high   { border-left: 3px solid #c84b2f; padding-left: 10px; margin-bottom: 10px; }
.gap-medium { border-left: 3px solid #b85a00; padding-left: 10px; margin-bottom: 10px; }
.gap-low    { border-left: 3px solid #1a6b3a; padding-left: 10px; margin-bottom: 10px; }
.gap-issue  { font-weight: 600; font-size: 13px; color: var(--ink); }
.gap-fix    { font-size: 12px; color: var(--muted); margin-top: 2px; }

/* Suggestions */
.suggestion-item {
    background: var(--paper2);
    border-left: 3px solid #2645a8;
    padding: 10px 12px;
    margin-bottom: 8px;
    border-radius: 0 3px 3px 0;
    font-size: 13px;
    line-height: 1.5;
    color: var(--ink);
}

/* Rewrite box */
.rewrite-box {
    background: #0e0e0e;
    color: #f0ead8;
    padding: 18px 20px;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    line-height: 1.7;
    white-space: pre-wrap;
}

/* Progress bars custom */
.skill-row { margin-bottom: 12px; }
.skill-header { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
.skill-track { height: 6px; background: #e4ddc9; border-radius: 3px; overflow: hidden; }
.skill-fill  { height: 100%; border-radius: 3px; }

/* Streamlit overrides */
div[data-testid="stFileUploader"] { border: 1.5px dashed var(--border) !important; border-radius: 4px !important; background: var(--paper2) !important; }
div[data-testid="stTextArea"] textarea { background: var(--paper2) !important; border: 1.5px solid var(--border) !important; font-family: 'Syne', sans-serif !important; font-size: 13px !important; border-radius: 4px !important; }
div[data-testid="stTextInput"] input { background: var(--paper2) !important; border: 1.5px solid var(--border) !important; font-family: 'Syne', sans-serif !important; font-size: 13px !important; border-radius: 4px !important; }
.stButton button {
    background: #0e0e0e !important;
    color: #f5f0e8 !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 12px 28px !important;
    width: 100% !important;
    transition: background .15s !important;
}
.stButton button:hover { background: #2a2a2a !important; }
div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="resumeiq-header">
    <div class="resumeiq-logo">Resume<span>IQ</span></div>
    <div class="resumeiq-tagline">AI-Powered Resume Screener &amp; Job Matcher</div>
</div>
""", unsafe_allow_html=True)


# ─── PDF EXTRACTION ──────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF using pdfplumber."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            # Also extract any tables as structured text
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    row_text = " | ".join(cell or "" for cell in row if cell)
                    if row_text.strip():
                        text_parts.append(row_text)
    return "\n\n".join(text_parts)


# ─── CLAUDE ANALYSIS ─────────────────────────────────────────────────────────
def analyse_resume(api_key: str, job_desc: str, resume_text: str, role_level: str) -> dict:
    """Send resume + JD to Claude and parse structured JSON response."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert technical recruiter and career coach. Analyse the resume against the job description and return ONLY a valid JSON object (no markdown, no extra text, no code fences).

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}

{f'CANDIDATE LEVEL: {role_level}' if role_level else ''}

Return this exact JSON structure:
{{
  "score": <integer 0-100>,
  "verdict": "<3-6 word headline about fit, e.g. 'Strong technical match, soft skills gap'>",
  "summary": "<2-3 sentence overall assessment>",
  "matched_skills": ["<skill>", ...],
  "missing_skills": ["<skill>", ...],
  "bonus_skills": ["<skill that exceeds requirements>", ...],
  "skill_categories": [
    {{ "name": "<category>", "score": <0-100>, "color": "<hex>" }}
  ],
  "gaps": [
    {{ "severity": "high|medium|low", "issue": "<gap description>", "fix": "<how to address it>" }}
  ],
  "suggestions": [
    "<specific, actionable improvement suggestion>",
    ...
  ],
  "rewritten_summary": "<rewrite the candidate professional summary to better target this role, 3-4 sentences using their actual experience>"
}}

Be specific, honest, and constructive. skill_categories should have 3-5 categories relevant to this role. matched_skills and missing_skills come directly from the JD requirements."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    # Strip any accidental markdown fences
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(clean)


# ─── RESULT RENDERING ────────────────────────────────────────────────────────
def render_results(result: dict):
    score = max(0, min(100, result.get("score", 0)))
    ring_color = "#1a6b3a" if score >= 70 else "#b85a00" if score >= 45 else "#c84b2f"

    # Score card
    st.markdown(f"""
    <div class="score-card">
        <div style="display:flex;align-items:center;gap:28px">
            <div>
                <div class="score-number" style="color:{ring_color}">{score}</div>
                <div style="font-family:'DM Mono',monospace;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em">/ 100</div>
            </div>
            <div>
                <div class="score-verdict">{result.get('verdict','Analysis complete')}</div>
                <div class="score-summary">{result.get('summary','')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab_skills, tab_gaps, tab_improve, tab_rewrite = st.tabs(
        ["Skills", "Gaps", "Improve", "Rewrite"]
    )

    # ── SKILLS ──
    with tab_skills:
        cats = result.get("skill_categories", [])
        if cats:
            st.markdown('<div class="section-label">Category scores</div>', unsafe_allow_html=True)
            for cat in cats:
                pct = max(0, min(100, cat.get("score", 0)))
                color = cat.get("color", "#2645a8")
                st.markdown(f"""
                <div class="skill-row">
                    <div class="skill-header">
                        <span>{cat['name']}</span>
                        <span style="font-family:'DM Mono',monospace;color:var(--muted);font-size:11px">{pct}/100</span>
                    </div>
                    <div class="skill-track">
                        <div class="skill-fill" style="width:{pct}%;background:{color}"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])
        bonus   = result.get("bonus_skills", [])

        if matched:
            st.markdown('<div class="section-label" style="margin-top:16px">✓ Matched requirements</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="chip chip-match">{s}</span>' for s in matched)
            st.markdown(f'<div class="chip-container">{chips}</div>', unsafe_allow_html=True)

        if missing:
            st.markdown('<div class="section-label" style="margin-top:16px">✗ Missing / weak areas</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="chip chip-miss">{s}</span>' for s in missing)
            st.markdown(f'<div class="chip-container">{chips}</div>', unsafe_allow_html=True)

        if bonus:
            st.markdown('<div class="section-label" style="margin-top:16px">★ Exceeds requirements</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="chip chip-bonus">{s}</span>' for s in bonus)
            st.markdown(f'<div class="chip-container">{chips}</div>', unsafe_allow_html=True)

    # ── GAPS ──
    with tab_gaps:
        gaps = result.get("gaps", [])
        if gaps:
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            for g in gaps:
                sev = g.get("severity", "medium")
                st.markdown(f"""
                <div class="gap-{sev}">
                    <div class="gap-issue">{sev_icon.get(sev,'•')} {g.get('issue','')}</div>
                    <div class="gap-fix">{g.get('fix','')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No significant gaps found.")

    # ── IMPROVE ──
    with tab_improve:
        suggestions = result.get("suggestions", [])
        if suggestions:
            for s in suggestions:
                st.markdown(f'<div class="suggestion-item">{s}</div>', unsafe_allow_html=True)
        else:
            st.info("No suggestions at this time.")

    # ── REWRITE ──
    with tab_rewrite:
        rewrite = result.get("rewritten_summary", "")
        st.markdown('<div class="section-label">AI-rewritten professional summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rewrite-box">{rewrite}</div>', unsafe_allow_html=True)
        st.caption("Tailored to the job description above. Copy and edit as needed.")
        if rewrite:
            st.code(rewrite, language=None)


# ─── MAIN LAYOUT ─────────────────────────────────────────────────────────────
col_input, col_results = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<div class="section-label">Step 01 — Your details</div>', unsafe_allow_html=True)

    # API Key
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com"
    )

    # Job Description
    st.markdown("**Job Description**")
    job_desc = st.text_area(
        "Job Description",
        height=180,
        placeholder="Paste the full job posting here — responsibilities, requirements, nice-to-haves...",
        label_visibility="collapsed"
    )

    # Resume: toggle between PDF upload and paste
    st.markdown("**Resume / CV**")
    resume_mode = st.radio(
        "Input mode",
        ["Upload PDF", "Paste text"],
        horizontal=True,
        label_visibility="collapsed"
    )

    resume_text = ""

    if resume_mode == "Upload PDF":
        uploaded_file = st.file_uploader(
            "Upload your resume PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            with st.spinner("Extracting text from PDF…"):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    word_count = len(resume_text.split())
                    st.success(f"✓ Extracted {word_count:,} words from {uploaded_file.name}")
                    with st.expander("Preview extracted text"):
                        st.text(resume_text[:1500] + ("…" if len(resume_text) > 1500 else ""))
                except Exception as e:
                    st.error(f"Could not extract PDF text: {e}")
    else:
        resume_text = st.text_area(
            "Resume text",
            height=200,
            placeholder="Paste your resume text here — work experience, skills, education, projects…",
            label_visibility="collapsed"
        )

    # Optional level
    role_level = st.text_input(
        "Role level (optional)",
        placeholder="e.g. Entry-level, 2 YOE, Senior, Manager…"
    )

    # Validate and run
    ready = bool(
        api_key.startswith("sk-ant-") and
        len(job_desc.strip()) > 50 and
        len(resume_text.strip()) > 50
    )

    if not api_key:
        st.caption("Enter your Anthropic API key to continue.")
    elif not api_key.startswith("sk-ant-"):
        st.warning("API key should start with `sk-ant-`")

    screen_btn = st.button(
        "Screen My Resume →",
        disabled=not ready,
        use_container_width=True
    )

with col_results:
    st.markdown('<div class="section-label">Step 02 — AI analysis</div>', unsafe_allow_html=True)

    # Store results in session state so they persist
    if "result" not in st.session_state:
        st.session_state.result = None
    if "error" not in st.session_state:
        st.session_state.error = None

    if screen_btn and ready:
        st.session_state.result = None
        st.session_state.error = None
        with st.spinner("Claude is reading your resume and the job description…"):
            try:
                result = analyse_resume(api_key, job_desc, resume_text, role_level)
                st.session_state.result = result
            except json.JSONDecodeError as e:
                st.session_state.error = f"Could not parse Claude's response. Try again. ({e})"
            except anthropic.AuthenticationError:
                st.session_state.error = "Invalid API key. Check your key at console.anthropic.com."
            except anthropic.RateLimitError:
                st.session_state.error = "Rate limit hit. Wait a moment and try again."
            except Exception as e:
                st.session_state.error = str(e)

    if st.session_state.error:
        st.error(st.session_state.error)
    elif st.session_state.result:
        render_results(st.session_state.result)
    else:
        st.markdown("""
        <div style="padding:60px 20px;text-align:center;color:var(--muted)">
            <div style="font-family:'DM Serif Display',Georgia,serif;font-size:36px;font-style:italic;opacity:.2;color:#0e0e0e">∅</div>
            <p style="font-size:13px;margin-top:12px;max-width:260px;margin-left:auto;margin-right:auto">
                Fill in the job description and your resume on the left, then hit Screen.
            </p>
        </div>
        """, unsafe_allow_html=True)
