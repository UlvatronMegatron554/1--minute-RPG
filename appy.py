import streamlit as st
import google.generativeai as genai
import time, json, re, random

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
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

# --- 2. THE INFINITE FORGE GATEWAY ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 50px #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme (e.g. Star Wars, Rome, Naruto, Minecraft):")
        
        if st.button("🔥 AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip() if theme_input.strip() else "Titan"
                
                with st.spinner(f"EXTRACTING LORE FOR {t.upper()}..."):
                    try:
                        # THE LORE-HUNTER PROMPT (No hardcoding)
                        prompt = (f"Act as a Master Lore-Expert. Create a world for theme '{t}'. "
                                 f"STRICT: Use only factual lore currency and powers. "
                                 f"If the theme is a specific game/movie, find its real items. "
                                 f"DO NOT use the word '{t}' in the names. "
                                 f"Return ONLY JSON: {{'currency': 'lore item', 'unit': 'lore unit', 'color': 'hex', "
                                 f"'shield_name': 'lore power', 'booster_name': 'lore power', "
                                 f"'shield_lore': 'Deep lore fact', 'booster_lore': 'Deep lore fact', "
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
                        # THE ADAPTIVE BACKUP (No One Piece bias)
                        lore_seeds = {
                            "space": {"c": "Credits", "s": "Ion Shield", "b": "Warp Drive", "h": "#00FFFF"},
                            "fantasy": {"c": "Gold Pieces", "s": "Magic Barrier", "b": "Haste Cloud", "h": "#9933FF"},
                            "mine": {"c": "Emeralds", "s": "Diamond Armor", "b": "Ender Pearl", "h": "#00FF00"},
                            "star": {"c": "Galactic Credits", "s": "Force Field", "b": "Hyperdrive", "h": "#00CCFF"},
                            "piece": {"c": "Berries", "s": "Haki Aura", "b": "Gear Second", "h": "#FF4500"},
                            "rome": {"c": "Denarii", "s": "Testudo", "b": "Chariot Charge", "h": "#B22222"},
                            "nba": {"c": "VC", "s": "Lockdown D", "b": "Fast Break", "h": "#EE6730"}
                        }
                        # Keyword matching to find the right theme
                        matched = next((v for k, v in lore_seeds.items() if k in t.lower()), None)
                        if not matched: matched = {"c": f"{t} Shards", "s": f"{t} Veil", "b": f"{t} Blink", "h": "#FFD700"}
                        
                        st.session_state.world_data = {
                            "currency": matched["c"], "unit": "Unit", "color": matched["h"],
                            "shield_name": matched["s"], "booster_name": matched["b"],
                            "shield_lore": f"A specialized defense from the {t} realm.", 
                            "booster_lore": f"Maximum velocity tuned to {t}.",
                            "evo_1": "Novice", "evo_2": "Master", "evo_3": "Legend"
                        }
                        st.session_state.user_theme = t
                        st.session_state.vibe_color = matched["h"]
                        st.rerun()
    st.stop()

# --- 3. DYNAMIC UI (10PX DASHED TITAN GLOW) ---
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
        text-transform: uppercase;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.write(f"**RANK:** {st.session_state.sub_tier}")
    st.metric(f"{w.get('currency', 'Gold').upper()}", f"{st.session_state.gold:.2f}")
    
    st.write("---")
    code = st.text_input("Activation Code:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        st.success("👑 ELITE STATUS ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

# --- 5. MAIN HUB ---
st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 25px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    st.header("🛒 ABILITY SHOP")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(w.get('shield_name'))
        st.write(f"_{w.get('shield_lore')}_")
        st.success("✨ REMOVES DEBT")
        if st.button(f"CLAIM (15 {w.get('currency')})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("Debt Wiped!")
    with col2:
        st.subheader(w.get('booster_name'))
        st.write(f"_{w.get('booster_lore')}_")
        st.success("🚀 DOUBLE XP")
        if st.button(f"CLAIM (25 {w.get('currency')})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.xp_multiplier = 2; st.success("Surge Active!")

else:
    mins = st.select_slider("Burst Time:", options=[1, 3, 5])
    if st.button("START MISSION", disabled=st.session_state.needs_verification):
        bar = st.progress(0)
        for i in range(mins * 60):
            time.sleep(1); bar.progress((i+1)/(mins*60))
        st.session_state.pending_gold, st.session_state.pending_xp = mins * 1.0, (mins * 25) * st.session_state.sub_multiplier
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    if st.file_uploader("Upload proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
