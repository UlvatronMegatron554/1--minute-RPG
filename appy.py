import streamlit as st
import google.generativeai as genai
import time, json, re, random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'xp': 0, 'gold': 10.0, 'level': 1, 
        'world_data': {}, 'user_theme': "Default", 'view': 'main',
        'pending_gold': 0.0, 'pending_xp': 0, 'needs_verification': False,
        'evolution': "Novice", 'vibe_color': "#FFD700", 'xp_multiplier': 1,
        'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE INFINITE FORGE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 40px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Ancient Rome, Cyberpunk, One Piece):")
        
        if st.button("🔥 AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip() if theme_input.strip() else "Titan Power"
                
                with st.spinner(f"FORGING {t.upper()}..."):
                    try:
                        # THE LORE-COMMAND PROMPT (Aggressive Creativity)
                        prompt = (f"Act as a Master Worldbuilder for theme '{t}'. "
                                 f"DO NOT use generic names. If the theme is real or fictional, use the EXACT currency and power names. "
                                 f"Example: Rome = Denarii, One Piece = Berries, Naruto = Ryo. "
                                 f"Return ONLY JSON: {{'currency': 'real lore currency', 'unit': 'lore unit', 'color': 'hex', "
                                 f"'shield_name': 'lore defense power', 'booster_name': 'lore speed power', "
                                 f"'shield_lore': '1 sentence lore', 'booster_lore': '1 sentence lore', "
                                 f"'evo_1': 'rank 1', 'evo_2': 'rank 2', 'evo_3': 'rank 3'}}")
                        
                        res = model.generate_content(prompt)
                        match = re.search(r'\{.*\}', res.text, re.DOTALL)
                        if match:
                            st.session_state.world_data = json.loads(match.group())
                            st.session_state.user_theme = t
                            st.session_state.vibe_color = st.session_state.world_data.get('color', "#FFD700")
                            st.rerun()
                    except:
                        # DYNAMIC BACKUP (If AI is Busy, it still uses your theme name)
                        st.session_state.world_data = {
                            "currency": f"{t} Credits", "unit": "Unit", "color": "#00FFCC",
                            "shield_name": f"{t} Barrier", "booster_name": f"{t} Overdrive",
                            "shield_lore": "Forged from the heart of this realm.", 
                            "booster_lore": "Maximum velocity engaged.",
                            "evo_1": "Novice", "evo_2": "Titan", "evo_3": "Eternal"
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = "#00FFCC"
                        st.rerun()
    st.stop()

# --- 3. DYNAMIC UI (MAX TITAN GLOW - 10PX DASHED) ---
w = st.session_state.world_data
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 60px {active_color}, inset 0 0 30px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 15px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 28px !important;
        padding: 45px !important;
        border-radius: 25px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 35px;
        text-transform: uppercase;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.write(f"**RANK:** {st.session_state.sub_tier}")
    st.metric(f"{w.get('currency', 'Gold').upper()}", f"{st.session_state.gold:.2f}")
    st.write(f"**XP MULTI:** {st.session_state.sub_multiplier}x")
    
    st.write("---")
    st.subheader("💎 UPGRADE RANK")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS ACTIVATED!")
        st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. SHOP & HUB ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 25px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    st.header("🛒 ABILITY SHOP")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(w.get('shield_name', 'Guardian'))
        st.write(f"_{w.get('shield_lore', 'The ultimate defense.')}_")
        st.success("✨ ABILITY: REMOVES ALL DEBT")
        if st.button(f"CLAIM (15 {w.get('currency', 'Gold')})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("Debt Wiped!")
    with col2:
        st.subheader(w.get('booster_name', 'Surge'))
        st.write(f"_{w.get('booster_lore', 'The ultimate speed.')}_")
        st.success("🚀 ABILITY: DOUBLE XP SPEED")
        if st.button(f"CLAIM (25 {w.get('currency', 'Gold')})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.xp_multiplier = 2; st.success("Surge Active!")

else:
    mins = st.select_slider("Burst Time:", options=
