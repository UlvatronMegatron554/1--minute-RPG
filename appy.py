import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. CORE SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

# Stability Lock for Model Version
MODEL_ID = 'gemini-1.5-flash'

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # TEMPERATURE 1.0 FOR PEAK CREATIVITY + SYSTEM INSTRUCTION
    model = genai.GenerativeModel(
        model_name=MODEL_ID,
        generation_config={"temperature": 1.0, "top_p": 0.95}
    )
except Exception:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'xp': 0, 'gold': 10.0, 'level': 1, 
        'world_data': {}, 'user_theme': "Default", 'view': 'main',
        'pending_gold': 0.0, 'pending_xp': 0, 'needs_verification': False,
        'vibe_color': "#FFD700", 'xp_multiplier': 1,
        'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE INFINITE FORGE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g., Formula 1, Sonic, NBA, Skyrim):")
        
        if st.button("🔥 AWAKEN"):
            if name_input and theme_input:
                st.session_state.user_name = name_input
                t = theme_input.strip()
                
                with st.spinner(f"EXTRACTING CANONICAL LORE FOR {t.upper()}..."):
                    try:
                        # THE PINNACLE PROMPT
                        prompt = (f"Act as an Infinite Lore Master. Analyze '{t}'. "
                                 f"STRICT RULES: "
                                 f"1. NEVER use the word '{t}' in item/ability names. "
                                 f"2. NO generic words (Shield, Guard, Surge, Essence, Power). "
                                 f"3. Find the EXACT canon currency and two iconic lore-based abilities. "
                                 f"4. Find the most iconic high-contrast HEX color for '{t}'. "
                                 f"Return ONLY JSON: {{'currency': 'name', 'color': 'HEX', "
                                 f"'shield_name': 'lore power', 'booster_name': 'lore power', "
                                 f"'shield_lore': 'Deep factual lore detail', 'booster_lore': 'Deep factual lore detail', "
                                 f"'evo_1': 'Rank 1', 'evo_2': 'Rank 2', 'evo_3': 'Rank 3'}}")
                        
                        res = model.generate_content(prompt)
                        data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                        
                        # ANTI-ECHO FILTER (Manual Override)
                        for key in ['currency', 'shield_name', 'booster_name']:
                            data[key] = data[key].replace(t, "").replace(t.title(), "").strip()
                            if not data[key]: data[key] = "Relic" # Safety fallback if name was only the theme
                        
                        st.session_state.world_data = data
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = data.get('color', "#FFD700")
                        st.rerun()
                    except Exception:
                        # EMERGENCY LORE RECOVERY (Non-Generic)
                        st.session_state.world_data = {
                            "currency": "Credits", "color": "#00FFCC",
                            "shield_name": "Kinetic Veil", "booster_name": "Phase Shift",
                            "shield_lore": "Molecular-level protection.", "booster_lore": "High-frequency translocation.",
                            "evo_1": "Novice", "evo_2": "Master", "evo_3": "Legend"
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = "#00FFCC"
                        st.rerun()
    st.stop()

# --- 3. THE TITAN UI (10PX DASHED GLOWING BORDERS) ---
# Applied ONLY to the gameplay buttons as requested.
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #080808; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 55px {active_color}, inset 0 0 25px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 26px !important;
        padding: 40px !important;
        border-radius: 20px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 30px;
        text-transform: uppercase;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.write(f"**RANK:** {st.session_state.sub_tier}")
    st.metric(f"{st.session_state.world_data.get('currency', 'GOLD').upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    st.subheader("💎 UPGRADE RANK")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. HUB & SHOP ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 20px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    st.header("🛒 LORE ABILITIES")
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
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.xp_multiplier = 2; st.success("ACTIVATED!")
else:
    mins = st.select_slider("Burst Time (Minutes):", options=[1, 3, 5])
    if st.button("START MISSION", disabled=st.session_state.needs_verification):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1); bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold = mins * 1.0
        st.session_state.pending_xp = (mins * 25) * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    with st.expander("⚖️ TRIBUNAL", expanded=True):
        f = st.file_uploader("Upload proof:")
        if f and st.button("JUDGE"):
            st.session_state.gold += st.session_state.pending_gold
            st.session_state.needs_verification = False; st.balloons(); st.rerun()
