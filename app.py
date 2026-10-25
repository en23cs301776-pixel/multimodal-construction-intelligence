"""Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1 - Streamlit app.

Runs in DEMO MODE (no API key needed) and switches to live Gemini analysis
when a key is provided in the sidebar or in Streamlit secrets (GEMINI_API_KEY).
"""
import json
import re
import urllib.parse

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")

st.markdown(
    """
<style>
.pill{display:inline-block;padding:2px 12px;border-radius:999px;font-weight:600;font-size:0.85rem;color:#fff}
.Low{background:#2e9e5b}.Medium{background:#d9a400}.High{background:#e8731a}.Critical{background:#d62839}
.banner{padding:14px 18px;border-radius:10px;background:linear-gradient(90deg,#1f3a5f,#2f6690);color:#fff;margin-bottom:12px}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------- helpers
def secret_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def pill(level):
    return f'<span class="pill {level}">{level}</span>'


def inr(x):
    if x >= 1e7:
        return f"₹{x / 1e7:.2f} Cr"
    if x >= 1e5:
        return f"₹{x / 1e5:.2f} Lakh"
    return f"₹{x:,.0f}"


def parse_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def ask_gemini(prompt, image=None):
    import google.generativeai as genai

    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel(st.session_state.model_name)
    parts = [prompt] + ([image] if image is not None else [])
    return model.generate_content(parts).text


def live_mode():
    return bool(st.session_state.api_key)


def analyse(prompt, image, demo_result):
    """Return (result_dict, used_live_ai). Falls back to demo on any failure."""
    if not live_mode():
        return demo_result, False
    try:
        return parse_json(ask_gemini(prompt, image)), True
    except Exception as e:  # network, quota, bad JSON, bad model name...
        st.warning(f"Live AI call failed ({type(e).__name__}); showing demo output instead.")
        return demo_result, False


def json_download(label, data, name):
    st.download_button(label, json.dumps(data, indent=2), file_name=name, mime="application/json")


# ----------------------------------------------------------------- state
st.session_state.setdefault("api_key", secret_key())
st.session_state.setdefault("model_name", "gemini-2.5-flash")
st.session_state.setdefault("chat", [])

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🏗️ ConstructIQ")
    key = st.text_input("Google Gemini API key", type="password", value=st.session_state.api_key,
                        help="Leave empty to use demonstration mode.")
    st.session_state.api_key = key.strip()
    st.session_state.model_name = st.text_input("Gemini model", value=st.session_state.model_name)
    if live_mode():
        st.success("Live AI mode")
    else:
        st.info("Demo mode: realistic sample outputs, no API key needed.")
    st.markdown(
        """
**Architecture**
1. Streamlit UI (tabs per module)
2. Multimodal LLM (Gemini) for image analysis
3. JSON data contracts for every AI response
4. Rule-based planning & valuation engine
5. Weather-aware advisory + site chatbot

**Modules**
- Epic 2: PPE safety and crack diagnostics
- Epic 3: Planning and valuation
- Epic 5: Assistant and weather advisory
"""
    )

st.markdown(
    '<div class="banner"><h2 style="margin:0">Multimodal Construction Intelligence Platform</h2>'
    "Site safety · structural diagnostics · cost planning · real estate valuation</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🦺 Site Safety & PPE Audit", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Site Assistant & Weather"]
)

# ----------------------------------------------------------------- tab 1
PPE_PROMPT = """You are a construction safety inspector (OSHA and IS 456 aware). Analyse this site photo.
Return ONLY valid JSON, no markdown, with this schema:
{"safety_score": int 0-100, "overall_status": "Compliant|Needs Attention|Non-Compliant",
 "ppe_detection": {"helmet": bool, "high_vis_vest": bool, "safety_boots": bool, "safety_harness": bool},
 "hazards": [{"hazard": str, "severity": "Low|Medium|High|Critical", "remedy": str}]}"""

with tab1:
    st.subheader("Site Safety & PPE Audit")
    up = st.file_uploader("Upload a construction site photo", type=["jpg", "jpeg", "png"], key="ppe")
    if up:
        img = Image.open(up).convert("RGB")
        st.image(img, width=420)
        if st.button("Run safety audit", type="primary"):
            seed = len(up.getvalue())
            score = 48 + seed % 40
            demo = {
                "safety_score": score,
                "overall_status": "Compliant" if score >= 80 else "Needs Attention" if score >= 60 else "Non-Compliant",
                "ppe_detection": {"helmet": True, "high_vis_vest": seed % 2 == 0, "safety_boots": True,
                                  "safety_harness": False},
                "hazards": [
                    {"hazard": "Worker at height without safety harness", "severity": "Critical",
                     "remedy": "Stop work at height until harness and anchor points are in place."},
                    {"hazard": "Loose material stacked near edge", "severity": "Medium",
                     "remedy": "Relocate and secure materials; install toe boards."},
                    {"hazard": "Poor housekeeping on walkways", "severity": "Low",
                     "remedy": "Clear debris daily and mark walkways."},
                ],
            }
            with st.spinner("Analysing site photo..."):
                res, live = analyse(PPE_PROMPT, img, demo)
            st.session_state["ppe_result"] = (res, live)
    if "ppe_result" in st.session_state and up:
        res, live = st.session_state["ppe_result"]
        st.caption("Source: live Gemini analysis" if live else "Source: demonstration mode")
        c1, c2, c3 = st.columns(3)
        c1.metric("Safety score", f"{res.get('safety_score', 0)}/100")
        c2.metric("Status", res.get("overall_status", "-"))
        c3.metric("Hazards found", len(res.get("hazards", [])))
        st.progress(min(max(int(res.get("safety_score", 0)), 0), 100) / 100)
        st.markdown("**PPE checklist**")
        for k, v in res.get("ppe_detection", {}).items():
            st.write(("✅ " if v else "❌ ") + k.replace("_", " ").title())
        st.markdown("**Identified hazards**")
        for h in res.get("hazards", []):
            st.markdown(f"{pill(h.get('severity', 'Low'))} **{h.get('hazard')}**<br>↳ {h.get('remedy')}",
                        unsafe_allow_html=True)
        json_download("⬇ Download JSON report", res, "safety_report.json")

# ----------------------------------------------------------------- tab 2
CRACK_PROMPT = """You are a structural engineer. Analyse this concrete/wall surface photo.
Return ONLY valid JSON, no markdown:
{"defect_type": "Hairline|Settlement|Structural Shear|Thermal Expansion|Spalling",
 "crack_width_mm": float, "severity": "Low|Medium|High|Critical",
 "probable_causes": [str], "recommended_repairs": [str], "urgency": str}"""

with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    up2 = st.file_uploader("Upload a concrete / wall surface photo", type=["jpg", "jpeg", "png"], key="crack")
    if up2:
        img2 = Image.open(up2).convert("RGB")
        st.image(img2, width=420)
        if st.button("Diagnose defect", type="primary"):
            demo = {
                "defect_type": "Settlement",
                "crack_width_mm": round(1.5 + len(up2.getvalue()) % 30 / 10, 1),
                "severity": "High",
                "probable_causes": ["Differential foundation settlement", "Poor soil compaction",
                                    "Water ingress weakening sub-base"],
                "recommended_repairs": ["Epoxy injection along the crack", "Structural re-grouting",
                                        "Install crack gauges to monitor movement"],
                "urgency": "Inspect within 7 days; restrict loading nearby.",
            }
            with st.spinner("Diagnosing..."):
                res, live = analyse(CRACK_PROMPT, img2, demo)
            st.session_state["crack_result"] = (res, live)
    if "crack_result" in st.session_state and up2:
        res, live = st.session_state["crack_result"]
        st.caption("Source: live Gemini analysis" if live else "Source: demonstration mode")
        c1, c2, c3 = st.columns(3)
        c1.metric("Defect type", res.get("defect_type", "-"))
        c2.metric("Crack width", f"{res.get('crack_width_mm', '-')} mm")
        c3.markdown("Severity<br>" + pill(res.get("severity", "Low")), unsafe_allow_html=True)
        st.markdown("**Probable causes**")
        for x in res.get("probable_causes", []):
            st.write("• " + x)
        st.markdown("**Recommended repairs**")
        for x in res.get("recommended_repairs", []):
            st.write("• " + x)
        st.warning("Urgency: " + str(res.get("urgency", "-")))
        json_download("⬇ Download JSON report", res, "crack_report.json")

# ----------------------------------------------------------------- tab 3
COST = {"Residential": 1800, "Commercial": 2400, "Industrial": 2000}      # ₹ / sq ft build cost
VALUE = {"Residential": 7500, "Commercial": 9500, "Industrial": 5000}     # ₹ / sq ft market value
TIER_COST = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.85}
TIER_VALUE = {"Tier 1": 1.8, "Tier 2": 1.0, "Tier 3": 0.6}

with tab3:
    st.subheader("Project Planning & Real Estate Valuation (INR)")
    a, b = st.columns(2)
    stype = a.selectbox("Structure type", list(COST))
    tier = b.selectbox("Location tier", list(TIER_COST))
    area = a.number_input("Built-up area (sq ft)", min_value=200, max_value=500000, value=2000, step=100)
    pct = b.slider("Completion (%)", 0, 100, 40)

    budget = area * COST[stype] * TIER_COST[tier]
    spent = budget * pct / 100
    full_value = area * VALUE[stype] * TIER_VALUE[tier]
    value_now = full_value * (0.35 + 0.65 * pct / 100)  # land/plot share + built share
    steel_t = area * 4.0 / 1000
    cement_bags = area * 0.42

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total project budget", inr(budget))
    m2.metric("Capex incurred", inr(spent))
    m3.metric("Current asset value", inr(value_now))
    m4.metric("Value on completion", inr(full_value))
    st.progress(pct / 100, text=f"Milestone progress: {pct}%")
    n1, n2 = st.columns(2)
    n1.metric("Steel requirement", f"{steel_t:,.1f} tonnes")
    n2.metric("Cement requirement", f"{cement_bags:,.0f} bags")
    st.caption("Simplified model using average per-sq-ft rates; not a substitute for a quantity surveyor.")

    st.markdown("**Conceptual architectural rendering (Pollinations AI)**")
    style = st.text_input("Describe the building", f"modern {stype.lower()} building, glass facade, daylight")
    if st.button("Generate rendering"):
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(style + ", architectural render")
        try:
            st.image(url, width=520)
        except Exception:
            pass
        st.markdown(f"[Open rendering in new tab]({url})")

# ----------------------------------------------------------------- tab 4
WEATHER = {
    "Normal": ["Standard site protocols apply.", "Daily toolbox talk before shift."],
    "High Wind": ["Suspend crane and hoisting operations above safe wind limits.",
                  "Secure scaffolding sheets, formwork and loose materials.",
                  "Restrict work at height."],
    "Heavy Rain": ["Switch off and isolate temporary electrical supply; electrical hazard risk.",
                   "Cover fresh concrete; delay pours and protect curing.",
                   "Pump out excavations; watch for slippery surfaces."],
    "Extreme Heat": ["Enforce hydration and shaded rest breaks.",
                     "Pour concrete early morning; use wet curing to avoid plastic shrinkage cracks.",
                     "Monitor workers for heat stress."],
}

DEMO_CHAT = [
    (r"crack", "Hairline cracks under 0.3 mm are usually cosmetic. Anything wider, or growing, needs a structural check and epoxy injection."),
    (r"helmet|ppe|harness|vest", "Minimum PPE: helmet, high-vis vest, safety boots; add a harness above 1.8 m and gloves/eye protection where relevant."),
    (r"cement|concrete|cur", "Cure concrete for at least 7 days (14 for blended cement). Keep it moist and shaded in hot weather."),
    (r"cost|budget|price", "Use the Planning tab for a budget estimate. Keep 8-10% contingency for price swings in steel and cement."),
    (r"rain|wind|heat|weather", "Pick the current weather above for site-specific protocols."),
]

with tab4:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    w = st.selectbox("Today's weather condition", list(WEATHER))
    for line in WEATHER[w]:
        (st.success if w == "Normal" else st.warning)(line)

    st.markdown("**Construction engineering assistant**")
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    q = st.chat_input("Ask about safety, materials, cracks, scheduling...")
    if q:
        st.session_state.chat.append({"role": "user", "content": q})
        reply = None
        if live_mode():
            try:
                hist = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.chat[-6:])
                reply = ask_gemini("You are a concise senior construction engineer in India. "
                                   f"Site weather: {w}.\n{hist}\nassistant:")
            except Exception:
                reply = None
        if reply is None:
            reply = next((r for p, r in DEMO_CHAT if re.search(p, q, re.I)),
                         "Good question. Share more detail (material, stage, location) and I'll give a specific recommendation.")
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()
