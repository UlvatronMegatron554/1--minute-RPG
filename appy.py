import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. CORE SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # TEMPERATURE 0.0 FOR RAW, COLD LORE DATA - NO GUESSING
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
except:
    model = None

# --- 2. THE SOURCE OF TRUTH (LORE DNA) ---
LORE_DNA = {
    "sonic": {"c": "Gold Rings", "s": "Insta-Shield", "b": "Spin Dash", "col": "#0000FF"},
    "formula 1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801"},
    "f1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801"},
    "minecraft": {"c": "Emeralds", "s": "Netherite Plate", "b": "Ender Pearl Warp", "col": "#00AA00"},
    "one piece": {"c": "Berries", "s": "Armament Haki", "b": "Gear Second", "col": "#FF4500"},
    "nba": {"c": "VC", "s": "Lockdown Defense", "b": "Fast Break", "col": "#EE6730"},
    "ancient rome": {"c": "Denarii", "s": "Testudo Formation", "b": "Chariot Charge", "col": "#B22222"},
    "skyrim": {"c": "Septims", "s": "Dragonhide", "b": "Whirlwind Sprint", "col": "#C0C0C0"}
}

if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 3. THE INFINITE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Sonic, F1, Ancient Rome, Skyrim):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t_low = theme_input.lower().strip()
                
                # Check DNA first for 100% accuracy
                matched = next((v for k, v in LORE_DNA.items() if k in t_low), None)
                if matched:
                    st.session_state.world_data = {
                        "currency": matched["c"], "shield_name": matched["s"], "booster_name": matched["b"],
                        "color": matched["col"], "shield_lore": "Canonical lore protection.", "booster_lore": "Canonical lore speed."
                    }
                    st.session_state.vibe_color = matched["col"]
                    st.session_state.user_theme = theme_input
                    st.rerun()
                else:
                    with st.spinner(f"DECODING {t_low.upper()} REALITY..."):
                        try:
                            prompt = (f"Identify factual lore for '{theme_input}'. Match the quality of One Piece or Formula 1. "
                                     f"1. Factual currency used. 2. Factual defense item. 3. Factual speed power. 4. Iconic HEX color. "
                                     f"STRICT RULE: NO generic names (Shield, Guard, Surge). NO theme name in items. "
                                     f"RETURN JSON ONLY: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                     f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                            res = model.generate_content(prompt)
                            data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                            
                            # THE SCRUBBER: Manually strip theme name if AI cheats
                            for key in ['currency', 'shield_name', 'booster_name']:
                                data[key] = data[key].lower().replace(t_low, "").strip().title()
                            
                            st.session_state.world_data = data
                            st.session_state.vibe_color = data.get('color', "#FFD700")
                            st.session_state.user_theme = theme_input
                            st.rerun()
                        except:
                            st.session_state.world_data = {"currency": "Credits", "color": "#00FFCC", "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", "shield_lore": "Advanced defense.", "booster_lore": "Advanced speed."}
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
        color: white !
