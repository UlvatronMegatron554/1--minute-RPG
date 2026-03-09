import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. CORE ARCHITECTURE ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
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

# --- 2. THE LORE-SYNC GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Formula 1, Sonic, NBA, Skyrim):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t = theme_input.strip()
                
                with st.spinner(f"DECODING {t.upper()} REALITY..."):
                    try:
                        prompt = (f"Identify the LORE for '{t}'. Match the quality of One Piece or Formula 1. "
                                 f"1. Factual currency used. 2. Factual defense item (NOT Shield/Guard). "
                                 f"3. Factual speed power (NOT Surge/Drive). 4. Iconic high-contrast HEX color. "
                                 f"STRICT RULE: NO generic names. NO theme name in items. "
                                 f"RETURN JSON ONLY: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                 f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                        res = model.generate_content(prompt)
                        data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                        
                        # ANTI-ECHO SCRUBBER: Kill theme name echoes and generic terms
                        forbidden = [t.lower(), "shield", "guard", "surge", "drive"]
                        for key in ['currency', 'shield_name', 'booster_name']:
                            val = data[key].lower()
                            for f in forbidden:
                                val = val.replace(f, "").strip()
                            data[key] = val.title() if (val and len(val) > 2) else "Core Power"
                        
                        st.session_state.world_data = data
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.rerun()
                    except:
                        st.session_state.world_data = {"currency": "Credits", "color": "#00
