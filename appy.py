import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. THE TITAN NEXUS SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # FORCING TEMPERATURE 0.0 FOR ABSOLUTE FACTUAL ACCURACY
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
except:
    model = None

# --- 2. THE MASTER LORE DNA (HARD-CODED TRUTH) ---
LORE_DNA = {
    "sonic": {"c": "Gold Rings", "s": "Insta-Shield", "b": "Spin Dash", "col": "#0000FF"},
    "formula 1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801"},
    "f1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801"},
    "minecraft": {"c": "Emeralds", "s": "Netherite Plate", "b": "Ender Pearl Warp", "col": "#00AA00"},
    "one piece": {"c": "Berries", "s": "Armament Haki", "b": "Gear Second", "col": "#FF4500"},
    "naruto": {"c": "Ryo", "s": "Susanoo Ribs", "b": "Body Flicker", "col": "#FF9900"},
    "nba": {"c": "VC", "s": "Lockdown Defense", "b": "Fast Break", "col": "#EE6730"},
    "ancient rome": {"c": "Denarii", "s": "Testudo Formation", "b": "Chariot Charge", "col": "#B22222"},
    "skyrim": {"c": "Septims", "s": "Dragonhide", "b": "Whirlwind Sprint", "col": "#C0C0C0"},
    "star wars": {"c": "Galactic Credits", "s": "Lightsaber Deflect", "b": "Force Speed", "col": "#00CCFF"},
    "batman": {"c": "WayneTech Credits", "s": "Kevlar Batsuit", "b": "Grapnel Gun", "col": "#1A1A1B"}
}

if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 3. THE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme:")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t_low = theme_input.lower().strip()
                
                # STEP 1: CHECK HARD-CODED LORE DNA
                matched = next((v for k, v in LORE_DNA.items() if k in t_low), None)
                if matched:
                    st.session_state.world_data = {
                        "currency": matched["c"], "shield_name": matched["s"], "booster_name": matched["b"],
                        "color": matched["col"], "shield_lore": "Factual Lore.", "booster_lore": "Factual Lore."
                    }
                    st.session_state.vibe_color = matched["col"]
                    st.session_state.user_theme = theme_input
                    st.rerun()
                else:
                    # STEP 2: AI EXTRACTION (FOR NEW WORLDS ONLY)
                    with st.spinner("SCANNING MULTIVERSE..."):
                        try:
                            prompt = (f"Identify factual lore for '{theme_input}'. "
                                     f"1. Canonical currency. 2. Defense item. 3. Speed item. 4. Iconic HEX color. "
                                     f"RULE: NO generic names. NO theme name in items. "
                                     f"JSON ONLY: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                     f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                            res = model.generate_content(prompt)
                            data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                            st.session_state.world_data = data
                            st.session_state.vibe_color = data.get('color', "#FFD700")
                            st.session_state.user_theme = theme_input
                            st.rerun()
                        except:
                            st.session_state.world_data = {"currency": "Credits", "color": "#00FFCC", "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", "shield_lore": "Safe-mode.", "booster_lore": "Safe-mode."}
                            st.session_state.user_theme = theme_input
                            st.rerun()
    st.stop()

# --- 4. THE TITAN UI (10PX DASHED PULSE) ---
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

# --- 5. SIDEBAR & ELITE ---
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

st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 40px {active_color}; font-size: 80px; text-align: center;'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

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
