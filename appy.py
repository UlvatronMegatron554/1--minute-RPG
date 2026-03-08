import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

# FIX: Explicitly using the stable model name to prevent 'NotFound' error
MODEL_NAME = 'gemini-1.5-flash'

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    model = None

# --- 2. THE MASTER LORE DATABASE (THE DNA) ---
LORE_DB = {
    "formula 1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "h": "#FF1801"},
    "f1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "h": "#FF1801"},
    "sonic": {"c": "Gold Rings", "s": "Insta-Shield", "b": "Spin Dash", "h": "#0000FF"},
    "minecraft": {"c": "Emeralds", "s": "Netherite Plating", "b": "Ender Pearl Warp", "h": "#00AA00"},
    "one piece": {"c": "Berries", "s": "Armament Haki", "b": "Gear Second", "h": "#FF4500"},
    "naruto": {"c": "Ryo", "s": "Susanoo Ribs", "b": "Body Flicker", "h": "#FF9900"},
    "nba": {"c": "VC", "s": "Lockdown Defense", "b": "Fast Break", "h": "#EE6730"},
    "ancient rome": {"c": "Denarii", "s": "Testudo Formation", "b": "Chariot Charge", "h": "#B22222"},
    "skyrim": {"c": "Septims", "s": "Dragonhide", "b": "Whirlwind Sprint", "h": "#C0C0C0"},
    "star wars": {"c": "Galactic Credits", "s": "Lightsaber Deflect", "b": "Force Speed", "h": "#00CCFF"},
    "cyberpunk": {"c": "Eddies", "s": "Subdermal Armor", "b": "Sandevistan", "h": "#FFFF00"},
    "dragon ball": {"c": "Zeni", "s": "Afterimage", "b": "Kaioken", "h": "#FF8C00"},
    "harry potter": {"c": "Galleons", "s": "Protego Totalum", "b": "Apparition", "h": "#740001"},
    "batman": {"c": "WayneTech Credits", "s": "Kevlar Batsuit", "b": "Grapnel Gun", "h": "#1A1A1B"},
    "elden ring": {"c": "Runes", "s": "Ironjar Aromatic", "b": "Bloodhound Step", "h": "#FFD700"},
    "pokemon": {"c": "PokéDollars", "s": "Protect", "b": "Extreme Speed", "h": "#FF0000"},
    "witcher": {"c": "Crowns", "s": "Quen Sign", "b": "Blizzard Potion", "h": "#808080"},
    "marvel": {"c": "Stark Credits", "s": "Vibranium Weave", "b": "Repulsor Flight", "h": "#AF0202"},
    "ancient egypt": {"c": "Deben", "s": "Bronze Aspis", "b": "Chariot Blitz", "h": "#E5C100"},
    "fallout": {"c": "Bottle Caps", "s": "Power Armor", "b": "Jet Injector", "h": "#FFFF00"},
    "lord of the rings": {"c": "Silver Pennies", "s": "Mithril Shirt", "b": "Shadowfax Gallop", "h": "#4B5320"}
}

# --- INITIALIZE STATE ---
if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 'vibe_color': "#FFD700"
    })

# --- 3. GATEWAY (NO GLOWING BOXES HERE) ---
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>⚡ 1-MINUTE RPG</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Champion Name:")
        theme_input = st.text_input("World Theme:")
        if st.button("AWAKEN"):
            if name_input:
                st.session_state.user_name = name_input
                t = theme_input.strip().lower()
                
                # Check Local Database First
                matched_key = next((k for k in LORE_DB if k in t), None)
                if matched_key:
                    d = LORE_DB[matched_key]
                    st.session_state.world_data = {
                        "currency": d["c"], "shield_name": d["s"], "booster_name": d["b"], 
                        "color": d["h"], "shield_lore": "Factual Lore.", "booster_lore": "Factual Lore."
                    }
                    st.session_state.user_theme = theme_input
                    st.session_state.vibe_color = d["h"]
                    st.rerun()
                else:
                    # AI Fallback
                    with st.spinner("ANALYZING MULTIVERSE..."):
                        try:
                            prompt = f"Identify lore for '{t}'. Match the quality of Sonic (Rings/Spin Dash). No generic names. Return ONLY JSON: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', 'booster_name': 'name', 'shield_lore': 'fact', 'booster_lore': 'fact'}}"
                            res = model.generate_content(prompt)
                            match = re.search(r'\{.*\}', res.text, re.DOTALL)
                            if match:
                                data = json.loads(match.group())
                                st.session_state.world_data = data
                                st.session_state.user_theme = theme_input
                                st.session_state.vibe_color = data.get('color', "#FFD700")
                                st.rerun()
                        except Exception:
                            # Emergency Backup if AI completely fails
                            st.session_state.world_data = {"currency": "Gold", "color": "#FFD700", "shield_name": "Defense", "booster_name": "Speed", "shield_lore": "Safe-mode engaged.", "booster_lore": "Safe-mode engaged."}
                            st.session_state.user_theme = theme_input
                            st.rerun()
    st.stop()

# --- 4. THE TITAN UI (10PX DASHED) ---
active_color = st.session_state.vibe_color
st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        padding: 40px !important;
        animation: glow 2s infinite ease-in-out;
    }}
    @keyframes glow {{
        0% {{ box-shadow: 0 0 10px {active_color}; }}
        50% {{ box-shadow: 0 0 40px {active_color}; }}
        100% {{ box-shadow: 0 0 10px {active_color}; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & HUB ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{st.session_state.world_data.get('currency', 'Points').upper()}", f"{st.session_state.gold:.2f}")
    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

st.markdown(f"<h1 style='color:{active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(st.session_state.world_data['shield_name'])
        st.write(st.session_state.world_data['shield_lore'])
        if st.button(f"BUY (15 {st.session_state.world_data['currency']})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("Activated!")
    with col2:
        st.subheader(st.session_state.world_data['booster_name'])
        st.write(st.session_state.world_data['booster_lore'])
        if st.button(f"BUY (25 {st.session_state.world_data['currency']})"):
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
    if st.file_uploader("Proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
