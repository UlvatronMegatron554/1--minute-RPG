import streamlit as st
import google.generativeai as genai
import time, json, re, random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # CRANKING TEMPERATURE TO 1.0 FOR MAXIMUM CREATIVITY
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 1.0})
except:
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

# --- 2. THE INFINITE FORGE ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Sonic, F1, Minecraft, Naruto):")
        
        if st.button("🔥 AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip() if theme_input.strip() else "Titan"
                
                with st.spinner(f"DECODING {t.upper()} LORE..."):
                    try:
                        # THE "ULTIMATE LORE" PROMPT
                        prompt = (f"Act as a Master Worldbuilder for '{t}'. "
                                 f"STRICT RULE: Do NOT use the word '{t}' in item names. "
                                 f"STRICT RULE: Do NOT use generic words like 'Shield' or 'Surge'. "
                                 f"Find the actual canon currency and unique defensive/speed powers. "
                                 f"Return ONLY JSON: {{'currency': 'real lore name', 'unit': 'unit', 'color': 'hex', "
                                 f"'shield_name': 'lore power', 'booster_name': 'lore power', "
                                 f"'shield_lore': 'Deep factual lore fact', 'booster_lore': 'Deep factual lore fact', "
                                 f"'evo_1': 'rank 1', 'evo_2': 'rank 2', 'evo_3': 'rank 3'}}")
                        
                        res = model.generate_content(prompt)
                        match = re.search(r'\{.*\}', res.text, re.DOTALL)
                        if match:
                            data = json.loads(match.group())
                            st.session_state.world_data = data
                            st.session_state.user_theme = t
                            st.session_state.vibe_color = data.get('color', "#FFD700")
                            st.rerun()
                    except:
                        # DYNAMIC BACKUP (Keyword Based)
                        st.session_state.world_data = {
                            "currency": "Rings" if "sonic" in t.lower() else "Credits",
                            "unit": "Gold", "color": "#0000FF" if "sonic" in t.lower() else "#FF1801",
                            "shield_name": "Insta-Shield" if "sonic" in t.lower() else "Kinetic Barrier",
                            "booster_name": "Spin Dash" if "sonic" in t.lower() else "Overdrive",
                            "shield_lore": "Forged from the heart of this realm.", 
                            "booster_lore": "Maximum velocity engaged.",
                            "evo_1": "Novice", "evo_2": "Master", "evo_3": "Legend"
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = st.session_state.world_data["color"]
                        st.rerun()
    st.stop()

# --- 3. DYNAMIC UI (10PX DASHED TITAN GLOW) ---
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
    st.metric(f"{w.get('currency', 'Gold').upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    st.subheader("💎 UPGRADE RANK")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. SHOP & HUB ---
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
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.xp_multiplier = 2; st.success("Activated!")
else:
    mins = st.select_slider("Burst Time:", options=[1, 3, 5])
    if st.button("START MISSION"):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1); bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold, st.session_state.pending_xp = mins * 1.0, (mins * 25) * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    if st.file_uploader("Proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
