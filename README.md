# Multimodal Construction Intelligence Platform

Skill Wallet Capstone Project 1: an AI decision-support app for construction sites, built with Streamlit and Google Gemini.

## Features
- **Site Safety & PPE Audit**: upload a site photo and get a safety score (0-100), PPE checklist (helmet, vest, boots, harness) and hazards with severity and remedies. Downloadable JSON report.
- **Crack Diagnostics**: classifies the defect (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), estimates crack width, causes, repairs and urgency.
- **Planning & Valuation**: budget, capex incurred, current asset value and steel/cement needs in INR (Lakh/Crore) by structure type, city tier and completion %. Includes a Pollinations AI rendering link.
- **Site Assistant & Weather Advisory**: weather-specific safety protocols (wind, rain, heat) and a multi-turn engineering chatbot.

## How it works
- Every AI response follows a strict **JSON data contract**, parsed and rendered in the UI.
- **Demo mode**: with no API key the app returns realistic sample outputs, so it always runs.
- **Live mode**: add a Gemini API key in the sidebar (or `GEMINI_API_KEY` in Streamlit secrets). If a live call fails, the app falls back to demo output.

## Tech stack
Python 3.9+, Streamlit, Pillow, google-generativeai (Gemini), Pollinations AI, JSON contracts.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push to a public GitHub repo, then create an app at [share.streamlit.io](https://share.streamlit.io) with branch `main` and main file `app.py`.

## Known limitations
- Demo mode outputs are sample data, not real analysis.
- The valuation model uses simplified average per-sq-ft rates and is indicative only.
- AI safety and structural findings must be verified by a qualified engineer.
- Chat history lives in the browser session only; no database is used.
