import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # TEMPERATURE 1.0 FOR PEAK CREATIVITY - NO MORE GENERIC DRIFT
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 1.0})
except:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE INFINITE FORGE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Formula 1, Sonic, Ancient Rome, Skyrim):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t = theme_input.strip()
                
                with st.spinner(f"EXTRACTING CANONICAL LORE FOR {t.upper()}..."):
                    try:
                        # THE PINNACLE LORE PROMPT
                        prompt = (f"Act as a Master of Lore for '{t}'. "
                                 f"RULES: 1. NEVER use the word '{t}' in item names. "
                                 f"2. NO generic words like 'Shield' or 'Surge'. "
                                 f"3. Find the EXACT factual currency and two iconic lore-based powers. "
                                 f"4. Use the MOST ICONIC high-contrast HEX color for '{t}'. "
                                 f"Return ONLY JSON: {{'currency': 'name', 'color': 'HEX', "
                                 f"'shield_name': 'lore power', 'booster_name': 'lore power', "
                                 f"'shield_lore': 'Deep factual lore', 'booster_lore': 'Deep factual lore'}}")
                        
                        res = model.generate_content(prompt)
                        data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                        
                        # ANTI-ECHO SCRUBBER: Manually strip theme name if AI cheats
                        for key in ['currency', 'shield_name', 'booster_name']:
                            data[key] = data[key].lower().replace(t.lower(), "").strip().title()
                        
                        st.session_state.world_data = data
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.rerun()
                    except:
                        # HIGH-QUALITY DYNAMIC FALLBACK
                        st.session_state.world_data = {
                            "currency": "Credits", "color": "#00FFCC", 
                            "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", 
                            "shield_lore": "Forged in the heart of this realm.", 
                            "booster_lore": "Maximum velocity engaged."
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = "#00FFCC"
                        st.rerun()
    st.stop()

# --- 3. THE TITAN UI (10PX DASHED GLOW) ---
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 65px {active_color}, inset 0 0 30px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 28px !important;
        padding: 50px !important;
        border-radius: 25px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 40px;
        text-transform: uppercase;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & HUB ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{st.session_state.world_data['currency'].upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 25px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(st.session_state.world_data['shield_name'])
        st.write(f"_{st.session_state.world_data['shield_lore']}_")
        if st.button(f"BUY (15 {st.session_state.world_data['currency']})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("ACTIVATED!")
    with col2:
        st.subheader(st.session_state.world_data['booster_name'])
        st.write(f"_{st.session_state.world_data['booster_lore']}_")
        if st.button(f"BUY (25 {st.session_state.world_data['currency']})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.success("ACTIVATED!")
else:
    if st.button("START 1-MINUTE MISSION"):
        bar = st.progress(0)
        for i in range(60):
            time.sleep(1); bar.progress((i+1)/60)
        st.session_state.pending_gold = 1.0 * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    if st.file_uploader("Upload proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
