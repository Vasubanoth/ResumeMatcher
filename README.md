# ResumeIQ — AI Resume Screener & Job Matcher

> Paste a job description + your resume → get an AI-powered match score, skill gap analysis, and a rewritten professional summary. Built with Streamlit and Google Gemini (free tier).

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What it does

| Feature | Description |
|---|---|
| **Match Score** | 0–100 score showing how well your resume fits the job |
| **Skill Analysis** | Matched ✓, missing ✗, and bonus ★ skills pulled from the JD |
| **Category Scores** | Breakdown by skill category (e.g. Technical, Communication) |
| **Gap Analysis** | Ranked gaps (high / medium / low) with specific fixes |
| **Improvement Tips** | Actionable bullet suggestions to strengthen your application |
| **AI Rewrite** | Your professional summary rewritten to target the exact role |
| **PDF Upload** | Upload your resume as a PDF — text extracted automatically |

---

## Tech stack

- **Frontend** — [Streamlit](https://streamlit.io)
- **AI** — [Google Gemini 2.5 Flash](https://aistudio.google.com) (free tier)
- **PDF parsing** — [pdfplumber](https://github.com/jsvine/pdfplumber)
- **Deployment** — [Streamlit Cloud](https://share.streamlit.io) (free)

---

## Project structure

```
resumeiq/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md
```

---

## link to use: 
https://resumematcher-f3blnmvapjutlak9nthjno.streamlit.app/

### Reading the results

- **Score 70–100** 🟢 Strong match — apply confidently
- **Score 45–69** 🟡 Partial match — address the gaps before applying
- **Score 0–44** 🔴 Weak match — significant reskilling or wrong role

---

## Built by

**Vasu Banoth** — Data Science enthusiast | Python · SQL · LLM Automation  
Inspired by internship work at Mentrisea Edutech LLP building LLM pipelines and automated reporting systems.

---

## License

MIT — free to use, modify, and deploy.
