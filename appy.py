import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. THE ARCHITECT'S CORE ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # FORCING 0.0 TEMPERATURE FOR RAW FACTUAL DATA
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
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
                
                with st.spinner(f"DECODING {t.upper()} REALITY..."):
                    try:
                        # THE ABSOLUTE PROMPT: NO GUESSING, NO GENERIC NAMES
                        prompt = (f"Identify the canonical lore for '{t}'. "
                                 f"1. What is the EXACT currency used in '{t}'? "
                                 f"2. What is a FAMOUS defensive item or power in '{t}'? (NOT 'Shield', NOT 'Guard'). "
                                 f"3. What is a FAMOUS speed item or power in '{t}'? (NOT 'Surge', NOT 'Drive'). "
                                 f"4. What is the most iconic high-contrast HEX color for '{t}'? "
                                 f"STRICT RULE: Do NOT use the word '{t}' in any names. "
                                 f"RETURN JSON ONLY: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                 f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                        
                        res = model.generate_content(prompt)
                        data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                        
                        # THE LORE SCRUBBER: Kill any generic drift or echoes
                        forbidden = [t.lower(), "shield", "guard", "surge", "drive", "essence"]
                        for key in ['currency', 'shield_name', 'booster_name']:
                            val = data[key].lower()
                            for f in forbidden:
                                val = val.replace(f, "").strip()
                            data[key] = val.title() if val else "Primal Core"
                        
                        st.session_state.world_data = data
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.rerun()
                    except:
                        # TITAN FALLBACK
                        st.session_state.world_data = {
                            "currency": "Credits", "color": "#00FFCC", 
                            "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", 
                            "shield_lore": "Universal defense.", "booster_lore": "Universal speed."
                        }
                        st.session_state.user_theme = t
                        st.rerun()
    st.stop()

# --- 3. THE TITAN UI (10PX DASHED GLOW) ---
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 75px {active_color}, inset 0 0 35px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 30px !important;
        padding: 55px !important;
        border-radius: 35px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 50px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & ELITE SURPRISE ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{st.session_state.world_data['currency'].upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. THE INFINITEVERSE ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 30px {active_color}; font-size: 60px;'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

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
