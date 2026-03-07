import streamlit as st
import google.generativeai as genai
import time, json, re, random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    # INCREASED CREATIVITY SETTINGS
    generation_config = {
        "temperature": 0.9, # Higher temperature = more creative/less boring
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 500,
    }
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
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

# --- 2. THE TITAN FORGE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. One Piece, Ancient Rome, Cyberpunk):")
        
        if st.button("🔥 AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip() if theme_input.strip() else "Titan"
                
                with st.spinner(f"EXTRACTING LORE FOR {t.upper()}..."):
                    try:
                        # THE "NO-BORING-ZONE" PROMPT
                        prompt = (f"Act as a God-Tier RPG Worldbuilder. Forge a world for '{t}'. "
                                 f"STRICT RULE: DO NOT use the words 'Essence', 'Aegis', 'Shield', or 'Guard' if specific lore exists. "
                                 f"If the theme is One Piece, you MUST use 'Berries', 'Haki', 'Devil Fruits'. "
                                 f"If the theme is Rome, use 'Denarii' and 'Gladius'. "
                                 f"Be infinitely creative and lore-accurate. "
                                 f"Return ONLY JSON: {{'currency': 'lore currency', 'unit': 'lore unit', 'color': 'hex', "
                                 f"'shield_name': 'unique lore defense', 'booster_name': 'unique lore speed', "
                                 f"'shield_lore': 'Lore-heavy description', 'booster_lore': 'Lore-heavy description', "
                                 f"'evo_1': 'rank 1', 'evo_2': 'rank 2', 'evo_3': 'rank 3'}}")
                        
                        res = model.generate_content(prompt)
                        match = re.search(r'\{.*\}', res.text, re.DOTALL)
                        if match:
                            st.session_state.world_data = json.loads(match.group())
                            st.session_state.user_theme = t
                            st.session_state.vibe_color = st.session_state.world_data.get('color', "#FFD700")
                            st.rerun()
                    except:
                        # BETTER DYNAMIC BACKUP
                        st.session_state.world_data = {
                            "currency": "Gold Berries" if "piece" in t.lower() else "Gold",
                            "unit": "Beli" if "piece" in t.lower() else "Unit",
                            "color": "#FF4500" if "piece" in t.lower() else "#00FFCC",
                            "shield_name": "Armament Haki" if "piece" in t.lower() else f"{t} Guard",
                            "booster_name": "Gear Second" if "piece" in t.lower() else f"{t} Surge",
                            "shield_lore": "Absolute spiritual defense.", 
                            "booster_lore": "Pumping blood for extreme speed.",
                            "evo_1": "Novice", "evo_2": "Warrior", "evo_3": "Legend"
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = st.session_state.world_data["color"]
                        st.rerun()
    st.stop()

# --- 3. DYNAMIC UI (THE 10PX DASHED TITAN GLOW) ---
w = st.session_state.world_data
active_color = st.session_state.vibe_color if st.session_state.sub_tier != "Elite" else "#FFFFFF"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
        50% {{ box-shadow: 0 0 60px {active_color}, inset 0 0 30px {active_color}; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 20px {active_color}; border-color: {active_color}; }}
    }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 950 !important;
        font-size: 28px !important;
        padding: 50px !important;
        border-radius: 30px !important;
        animation: titan-glow 2s infinite ease-in-out !important;
        width: 100%;
        margin-bottom: 40px;
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
    mins = st.select_slider("Select Burst Time:", options=[1, 3, 5])
    if st.button("START MISSION", disabled=st.session_state.needs_verification):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1); bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold = mins * 1.0
        st.session_state.pending_xp = (mins * 25) * st.session_state.xp_multiplier * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    with st.expander("⚖️ TRIBUNAL", expanded=True):
        f = st.file_uploader("Upload proof:")
        if f and st.button("JUDGE"):
            st.session_state.gold += st.session_state.pending_gold
            st.session_state.xp += st.session_state.pending_xp
            st.session_state.needs_verification = False; st.balloons(); st.rerun()
