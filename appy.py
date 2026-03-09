import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. CORE ARCHITECTURE ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # FORCING TEMPERATURE 0.0 FOR RAW, COLD LORE DATA
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
except Exception:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE LORE-SYNC GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Formula 1, Sonic, Naruto, NBA):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t_raw = theme_input.strip()
                
                with st.spinner(f"DECODING {t_raw.upper()}..."):
                    try:
                        prompt = (f"Provide FACTUAL lore for '{t_raw}'. Match the quality of One Piece or F1. "
                                 f"1. Exact lore currency. 2. Iconic defense move (NOT Shield/Guard). "
                                 f"3. Iconic speed power (NOT Surge/Drive). 4. Iconic high-contrast HEX color. "
                                 f"RULE: NO generic names. NO theme name in items. "
                                 f"RETURN JSON ONLY: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                 f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                        res = model.generate_content(prompt)
                        raw_text = re.search(r'\{.*\}', res.text, re.DOTALL).group()
                        data = json.loads(raw_text)
                        
                        # ANTI-ECHO SCRUBBER: Kill theme name echoes and generic terms
                        forbidden = [t_raw.lower(), "shield", "guard", "surge", "drive", "power", "protection"]
                        for key in ['currency', 'shield_name', 'booster_name']:
                            val = data[key].lower()
                            for f in forbidden:
                                val = val.replace(f, "").strip()
                            data[key] = val.title() if (len(val) > 2) else "Titan Core"
                        
                        st.session_state.world_data = data
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.session_state.user_theme = t_raw
                        st.rerun()
                    except Exception:
                        # STABLE FALLBACK - NO UNTERMINATED STRINGS
                        st.session_state.world_data = {
                            "currency": "Credits", "color": "#00FFCC", 
                            "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", 
                            "shield_lore": "Universal atomic-level defense.", 
                            "booster_lore": "Localized space-time folding."
                        }
                        st.session_state.user_theme = t_raw
                        st.session_state.vibe_color = "#00FFCC"
                        st.rerun()
    st.stop()

# --- 3. THE TITAN UI (10PX DASHED PULSE) ---
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-pulse {{
        0% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 85px {active_color}, inset 0 0 45px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 32px !important;
        padding: 60px !important;
        border-radius: 40px !important;
        animation: titan-pulse 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 60px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & ELITE PROTOCOL ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{st.session_state.world_data.get('currency', 'GOLD').upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. THE HUB ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 40px {active_color}; font-size: 80px; text-align: center;'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(st.session_state.world_data.get('shield_name'))
        st.write(f"_{st.session_state.world_data.get('shield_lore')}_")
        if st.button(f"BUY (15 {st.session_state.world_data.get('currency')})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("ACTIVATED!")
    with col2:
        st.subheader(st.session_state.world_data.get('booster_name'))
        st.write(f"_{st.session_state.world_data.get('booster_lore')}_")
        if st.button(f"BUY (25 {st.session_state.world_data.get('currency')})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.sub_multiplier = 6; st.success("ELITE BOOST!")
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
