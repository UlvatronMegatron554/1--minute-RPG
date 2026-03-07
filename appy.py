import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import json
import re
import random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

MY_KEY = "AIzaSyCh42ZDXX3-kYyOHESq3RYoA4lgsq7uZ2s" # PASTE YOUR KEY HERE
genai.configure(api_key=MY_KEY)

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except:
    model = None

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'xp': 0, 'gold': 10.0, 'level': 1, 
        'world_data': {}, 'user_theme': "Default", 'view': 'main',
        'pending_gold': 0.0, 'pending_xp': 0, 'needs_verification': False,
        'evolution': "Novice", 'vibe_color': "#FFD700", 'xp_multiplier': 1,
        'reset_confirm_mode': False 
    })

# --- 2. PRE-START GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 20px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme:", placeholder="Leave blank for Default INFINITE POWER setting")
        
        c1, c2 = st.columns(2)
        if c1.button("🔥 AWAKEN"):
            if name_input:
                if not theme_input.strip():
                    st.session_state.world_data = {
                        "currency": "Power", "unit": "Burst", "color": "#FFD700",
                        "shield_name": "Titan Guard", "booster_name": "Infinite Surge",
                        "shield_lore": "This unbreakable shield crushes all doubt and wipes your debt clean.", 
                        "booster_lore": "Channel pure momentum to double your growth and reach the next rank.",
                        "evo_1": "Aspirant", "evo_2": "Titan", "evo_3": "Eternal"
                    }
                    st.session_state.user_name, st.session_state.user_theme = name_input, "Infinite Power"
                    st.session_state.vibe_color = "#FFD700"
                    st.rerun()
                else:
                    with st.spinner("Forging..."):
                        try:
                            prompt = f"Return ONLY JSON for RPG theme '{theme_input}'. Use 1 AMAZING sentence for lore. Keys: 'currency', 'unit', 'color', 'shield_name', 'booster_name', 'shield_lore', 'booster_lore', 'evo_1', 'evo_2', 'evo_3'."
                            res = model.generate_content(prompt)
                            match = re.search(r'\{.*\}', res.text, re.DOTALL)
                            if match:
                                st.session_state.world_data = json.loads(match.group())
                                st.session_state.user_name, st.session_state.user_theme = name_input, theme_input
                                st.session_state.vibe_color = st.session_state.world_data.get('color', "#FFD700")
                                st.rerun()
                        except:
                            st.error("Connection lag! Loading default...")
                            st.session_state.user_name = name_input
                            st.rerun()

        if c2.button("🎲 SURPRISE ME"):
            if name_input:
                lore = random.choice(["Pirate", "NBA", "Samurai", "Cyberpunk", "Space", "F1"])
                with st.spinner(f"Warping..."):
                    try:
                        prompt = f"Return ONLY JSON for theme '{lore}'. 1 amazing sentence per lore. Keys: 'currency', 'unit', 'color', 'shield_name', 'booster_name', 'shield_lore', 'booster_lore', 'evo_1', 'evo_2', 'evo_3'."
                        res = model.generate_content(prompt)
                        match = re.search(r'\{.*\}', res.text, re.DOTALL)
                        if match:
                            st.session_state.world_data = json.loads(match.group())
                            st.session_state.user_name, st.session_state.user_theme = name_input, lore
                            st.session_state.vibe_color = st.session_state.world_data.get('color', "#FFD700")
                            st.rerun()
                    except: st.error("Quota reached.")
    st.stop()

# --- 3. DYNAMIC UI (HYPER GLOW) ---
w = st.session_state.world_data
active_color = st.session_state.vibe_color
c_name = w.get('currency', 'Gold').upper()

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 10px {active_color}, inset 0 0 5px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 35px {active_color}, inset 0 0 20px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 10px {active_color}, inset 0 0 5px {active_color}; border-color: {active_color}; }}
    }}

    div.stButton > button {{
        border: 6px dashed {active_color} !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        padding: 20px !important;
        border-radius: 15px !important;
        animation: titan-glow 2.5s infinite ease-in-out !important;
    }}
    
    div.stButton > button:hover {{
        background-color: {active_color} !important;
        color: #000000 !important;
        animation: none !important;
        box-shadow: 0 0 60px {active_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{c_name}", f"{st.session_state.gold:.2f}")
    st.write(f"**RANK:** {st.session_state.evolution}")
    st.progress(st.session_state.xp / 100)
    st.write("---")
    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 ABILITY SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"):
        if st.session_state.reset_confirm_mode: st.session_state.clear(); st.rerun()
        else: st.session_state.reset_confirm_mode = True; st.rerun()
    if st.session_state.reset_confirm_mode: st.error("Click Reset again to confirm!")

# --- 5. SHOP & HUB ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 15px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    st.header("🛒 ABILITY SHOP")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(w.get('shield_name', 'Guardian'))
        st.write(f"*{w.get('shield_lore', 'A powerful protection ability.')}*")
        st.success("✨ ABILITY: REMOVES ALL DEBT")
        if st.button(f"CLAIM FOR 15 {c_name}", key="s"):
            if st.session_state.gold >= 15.0:
                st.session_state.gold -= 15.0; st.success("Debt Wiped!")
    with col2:
        st.subheader(w.get('booster_name', 'Surge'))
        st.write(f"*{w.get('booster_lore', 'A powerful momentum ability.')}*")
        st.success("🚀 ABILITY: DOUBLE XP SPEED")
        if st.button(f"CLAIM FOR 25 {c_name}", key="b"):
            if st.session_state.gold >= 25.0:
                st.session_state.gold -= 25.0; st.session_state.xp_multiplier = 2; st.success("Surge Active!")

else:
    st.write(f"### 🚀 START MISSION")
    mins = st.select_slider("Burst:", options=[1, 3, 5])
    if st.button("START", key="m", disabled=st.session_state.needs_verification):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1) # Test: 0.1
            bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold, st.session_state.pending_xp = mins * 1.0, (mins * 25) * st.session_state.xp_multiplier
        st.session_state.needs_verification = True; st.session_state.xp_multiplier = 1; st.rerun()

if st.session_state.needs_verification:
    with st.expander("⚖️ TRIBUNAL", expanded=True):
        f = st.file_uploader("Upload proof:", type=["png", "jpg", "jpeg"])
        if f and st.button("JUDGE"):
            st.session_state.gold += st.session_state.pending_gold; st.session_state.xp += st.session_state.pending_xp
            st.session_state.needs_verification = False; st.balloons(); time.sleep(1); st.rerun()

if st.session_state.xp >= 100:
    st.session_state.level += 1; st.session_state.xp -= 100; st.toast("🧬 LEVEL UP!"); st.rerun()