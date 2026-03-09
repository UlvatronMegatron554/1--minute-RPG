import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. THE SINGULARITY SETUP ---
st.set_page_config(page_title="TITAN OMNIVERSE", page_icon="⚡", layout="wide")

# Stability Model Lock
MODEL_ID = 'gemini-1.5-flash'

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # TEMPERATURE 0.0 FOR RAW, COLD LORE DATA - NO HALLUCINATIONS
    model = genai.GenerativeModel(MODEL_ID, generation_config={"temperature": 0.0})
except Exception:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE LORE-FORCE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ TITAN OMNIVERSE</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Formula 1, Sonic, Naruto, Rome):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t_raw = theme_input.strip()
                
                with st.spinner(f"INTERCEPTING {t_raw.upper()} REALITY..."):
                    try:
                        # THE OMNIVERSE PROMPT: COMMANDING ABSOLUTE LORE
                        prompt = (f"Act as a Factual Archivist for '{t_raw}'. "
                                 f"1. Factual lore currency. "
                                 f"2. Factual iconic defense power (NOT 'Shield' or 'Guard'). "
                                 f"3. Factual iconic speed power (NOT 'Surge' or 'Drive'). "
                                 f"4. The most iconic high-contrast HEX color. "
                                 f"RULES: Do NOT use the word '{t_raw}' in names. JSON ONLY: "
                                 f"{{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', "
                                 f"'booster_name': 'name', 'shield_lore': 'Deep fact', 'booster_lore': 'Deep fact'}}")
                        
                        res = model.generate_content(prompt)
                        data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                        
                        # THE TITAN SCRUBBER: Kill any generic drift or echoes
                        forbidden = [t_raw.lower(), "shield", "guard", "surge", "drive", "essence", "power"]
                        for key in ['currency', 'shield_name', 'booster_name']:
                            val = data[key].lower()
                            for f in forbidden:
                                val = val.replace(f, "").strip()
                            data[key] = val.title() if (len(val) > 2) else "Core Aura"
                        
                        st.session_state.world_data = data
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.session_state.user_theme = t_raw
                        st.rerun()
                    except Exception:
                        # ABSOLUTE STABLE FALLBACK
