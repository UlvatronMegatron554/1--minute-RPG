import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # TEMPERATURE 0.0 FOR MAXIMUM FACTUAL ACCURACY
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
except:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'xp': 0, 'gold': 10.0, 'level': 1, 
        'world_data': {}, 'user_theme': "Default", 'view': 'main',
        'pending_gold': 0.0, 'pending_xp': 0, 'needs_verification': False,
        'vibe_color': "#FFD700", 'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. THE FORGE ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Formula 1, Sonic, NBA):")
        
        if st.button("🔥 AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip()
                
                with st.spinner(f"EXTRACTING LORE..."):
                    try:
                        prompt = (f"Identify the lore of '{t}'. "
                                 f"1. What is the EXACT currency in '{t}'? "
                                 f"2. What is a FAMOUS defensive move/item in '{t}'? "
                                 f"3. What is a FAMOUS speed move/item in '{t}'? "
                                 f"RULE: NEVER use the word '{t}' in names. "
                                 f"Return ONLY JSON: {{'currency': 'exact name', 'unit': 'unit', 'color': 'HEX', "
                                 f"'shield_name': 'lore power', 'booster_name': 'lore power', "
                                 f"'shield_lore': 'Deep lore fact', 'booster_lore': 'Deep lore fact'}}")
                        
                        res = model.generate_content(prompt)
                        match = re.search(r'\{.*\}', res.text, re.DOTALL)
                        if match:
                            data = json.loads(match.group())
                            st.session_state.world_data = data
                            st.session_state.user_theme = t
                            st.session_state.vibe_color = data.get('color', "#FFD700")
                            st.rerun()
                    except:
                        st.error("Lore Extraction Failed. Try again.")
    st.stop()

# --- 3. UI (10PX DASHED GLOW) ---
w = st.session_state.world_data
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 65px {active_color}, inset 0 0 30px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 28px !important;
        padding: 55px !important;
        border-radius: 35px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & HUB ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{w.get('currency', 'Points').upper()}", f"{st.session_state.gold:.2f}")
    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 25px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(w.get('shield_name'))
        st.write(f"_{w.get('shield_lore')}_")
        if st.button(f"CLAIM (15 {w.get('currency')})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("Activated!")
    with col2:
        st.subheader(w.get('booster_name'))
        st.write(f"_{w.get('booster_lore')}_")
        if st.button(f"CLAIM (25 {w.get('currency')})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.success("Activated!")
else:
    mins = st.select_slider("Burst Time:", options=[1, 3, 5])
    if st.button("START MISSION"):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1); bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold = mins * 1.0
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    if st.file_uploader("Upload proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
