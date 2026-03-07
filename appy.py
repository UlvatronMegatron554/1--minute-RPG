import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import json
import re
import random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
except:
    st.warning("Awaiting API Key... Please set 'GEMINI_KEY' in Streamlit Secrets.")
    MY_KEY = None

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
        'sub_tier': "Free", 'sub_multiplier': 1
    })

# --- 2. PRE-START GATEWAY (INFINITEVERSE RESTORED) ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 20px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme:", placeholder="e.g. Cyberpunk, Ancient Egypt, Space")
        
        c1, c2 = st.columns(2)
        if c1.button("🔥 AWAKEN"):
            if name_input:
                if not theme_input.strip():
                    st.session_state.world_data = {
                        "currency": "Power", "unit": "Burst", "color": "#FFD700",
                        "shield_name": "Titan Guard", "booster_name": "Infinite Surge",
                        "shield_lore": "A divine barrier that channels your will into absolute reality.", 
                        "booster_lore": "An explosion of focus that propels you toward your ultimate rank.",
                        "evo_1": "Aspirant", "evo_2": "Titan", "evo_3": "Eternal"
                    }
                    st.session_state.user_name, st.session_state.user_theme = name_input, "Infinite Power"
                    st.session_state.vibe_color = "#FFD700"
                    st.rerun()
                else:
                    with st.spinner("Forging World..."):
                        try:
                            prompt = f"Return ONLY JSON for RPG theme '{theme_input}'. Keys: 'currency', 'unit', 'color' (hex), 'shield_name', 'booster_name', 'shield_lore', 'booster_lore', 'evo_1', 'evo_2', 'evo_3'."
                            res = model.generate_content(prompt)
                            match = re.search(r'\{.*\}', res.text, re.DOTALL)
                            if match:
                                st.session_state.world_data = json.loads(match.group())
                                st.session_state.user_name, st.session_state.user_theme = name_input, theme_input
                                st.session_state.vibe_color = st.session_state.world_data.get('color', "#FFD700")
                                st.rerun()
                        except: st.error("AI Busy. Try again in 5s.")
        
        if c2.button("🎲 SURPRISE ME"):
            if name_input:
                lore = random.choice(["Pirate", "Samurai", "Cyberpunk", "Galactic", "F1 Racing"])
                st.session_state.user_name = name_input
                st.session_state.user_theme = lore
                # Triggering world forge...
                st.rerun()
    st.stop()

# --- 3. DYNAMIC UI (ELITE GOD-MODE) ---
w = st.session_state.world_data
active_color = st.session_state.vibe_color
if st.session_state.sub_tier == "Elite":
    active_color = "#FFFFFF" # God-Mode White

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 10px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 40px {active_color}, inset 0 0 10px #FFD700; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 10px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 5px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        animation: titan-glow 3s infinite ease-in-out !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (STRICT STATE LOGIC) ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.write(f"**RANK:** {st.session_state.sub_tier}")
    st.metric(f"{w.get('currency', 'Gold').upper()}", f"{st.session_state.gold:.2f}")
    st.write(f"**XP MULTIPLIER:** {st.session_state.sub_multiplier}x")
    st.progress(st.session_state.xp / 100)
    
    st.write("---")
    st.subheader("💎 UPGRADE RANK")
    code = st.text_input("Activation Code:", type="password")
    
    # Logic checking to ensure multiplier stays active
    if code == "TITAN5" and st.session_state.sub_tier != "Premium":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Premium", 2
        st.rerun()
    elif code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.rerun()

    st.write("---")
    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 15px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    st.header("🛒 ABILITY SHOP")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(w.get('shield_name', 'Guardian'))
        st.write(f"_{w.get('shield_lore', 'Legendary defense.')}_")
        if st.button("BUY (15 Gold)"):
            if st.session_state.gold >= 15:
                st.session_state.gold -= 15; st.success("Debt Wiped!")
    with col2:
        st.subheader(w.get('booster_name', 'Surge'))
        st.write(f"_{w.get('booster_lore', 'Legendary speed.')}_")
        if st.button("BUY (25 Gold)"):
            if st.session_state.gold >= 25:
                st.session_state.gold -= 25; st.session_state.xp_multiplier = 2; st.success("Surge Active!")

else:
    mins = st.select_slider("Mission Duration:", options=[1, 3, 5])
    if st.button("START MISSION", disabled=st.session_state.needs_verification):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1) # Live speed
            bar.progress((i+1)/(mins*60))
        
        st.session_state.pending_gold = mins * 1.0
        # Formula: (Mins * 25) * Shop Boost * Subscription Rank
        st.session_state.pending_xp = (mins * 25) * st.session_state.xp_multiplier * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    with st.expander("⚖️ TRIBUNAL", expanded=True):
        f = st.file_uploader("Upload proof:", type=["png", "jpg", "jpeg"])
        if f and st.button("JUDGE"):
            st.session_state.gold += st.session_state.pending_gold
            st.session_state.xp += st.session_state.pending_xp
            st.session_state.needs_verification = False; st.balloons(); st.rerun()

if st.session_state.xp >= 100:
    st.session_state.level += 1; st.session_state.xp -= 100; st.toast("🧬 LEVEL UP!"); st.rerun()
