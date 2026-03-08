import streamlit as st
import google.generativeai as genai
import time, json, re

# --- 1. SETUP ---
st.set_page_config(page_title="1-MINUTE RPG", page_icon="⚡", layout="wide")

try:
    MY_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=MY_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = None

# --- 2. THE UNIVERSAL LORE ENGINE (THE ABSOLUTE FIX) ---
# I have added high-tier keywords. If the AI fails, the code SNIFFS these.
GENRE_MAP = {
    "sonic": {"c": "Rings", "s": "Insta-Shield", "b": "Spin Dash", "h": "#0000FF"},
    "formula": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "h": "#FF1801"},
    "f1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "h": "#FF1801"},
    "mario": {"c": "Gold Coins", "s": "Super Mushroom", "b": "Dash Panel", "h": "#E52521"},
    "gta": {"c": "Cash", "s": "Body Armor", "b": "Franklin's Ability", "h": "#008105"},
    "cod": {"c": "CP", "s": "Trophy System", "b": "Dead Silence", "h": "#2B2B2B"},
    "fighting": {"c": "Fight Money", "s": "Perfect Block", "b": "Drive Rush", "h": "#FF4500"},
    "space": {"c": "Credits", "s": "Deflector Shield", "b": "Hyperdrive", "h": "#00CCFF"},
    "dragon": {"c": "Zeni", "s": "Afterimage", "b": "Kaioken", "h": "#FF8C00"},
    "minecraft": {"c": "Emeralds", "s": "Netherite Plate", "b": "Ender Pearl", "h": "#00AA00"}
}

if 'gold' not in st.session_state:
    st.session_state.update({
        'user_name': None, 'gold': 10.0, 'world_data': {}, 'user_theme': "Default", 
        'view': 'main', 'pending_gold': 0.0, 'needs_verification': False, 'vibe_color': "#FFD700"
    })

# --- 3. THE GATEWAY ---
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
                
                # STEP 1: KEYWORD SNIFFING (INSTANT & FACTUAL)
                match = next((v for k, v in GENRE_MAP.items() if k in t), None)
                if match:
                    st.session_state.world_data = {
                        "currency": match["c"], "shield_name": match["s"], "booster_name": match["b"], 
                        "color": match["h"], "shield_lore": f"Canonical defense of the {t} realm.", 
                        "booster_lore": f"Maximum velocity tuned to {t} physics."
                    }
                    st.session_state.vibe_color = match["h"]
                    st.session_state.user_theme = theme_input
                    st.rerun()
                
                # STEP 2: AI FALLBACK (ONLY IF SNIFFING FAILS)
                else:
                    with st.spinner("SEARCHING MULTIVERSE..."):
                        try:
                            prompt = f"Lore for '{t}'. Factual currency/defense/speed. No generic names. No theme name in items. JSON: {{'currency': 'name', 'color': 'HEX', 'shield_name': 'name', 'booster_name': 'name', 'shield_lore': 'fact', 'booster_lore': 'fact'}}"
                            res = model.generate_content(prompt)
                            data = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
                            st.session_state.world_data = data
                            st.session_state.vibe_color = data.get('color', "#FFD700")
                            st.session_state.user_theme = theme_input
                            st.rerun()
                        except:
                            # STEP 3: SMART CATEGORY BACKUP (NO MORE 'SAFE MODE' TEXT)
                            st.session_state.world_data = {
                                "currency": "Credits", "shield_name": "Kinetic Veil", "booster_name": "Phase Shift", 
                                "color": "#00FFCC", "shield_lore": "Advanced energetic protection.", "booster_lore": "High-speed translocation."
                            }
                            st.session_state.vibe_color = "#00FFCC"
                            st.session_state.user_theme = theme_input
                            st.rerun()
    st.stop()

# --- 4. THE TITAN UI (10PX DASHED GLOW - LOCKED) ---
active_color = st.session_state.vibe_color
st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; }}
    div.stButton > button {{
        border: 10px dashed {active_color} !important;
        background-color: #000000 !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 26px !important;
        padding: 45px !important;
        border-radius: 20px !important;
        animation: titan-glow 2s infinite ease-in-out;
    }}
    @keyframes titan-glow {{
        0% {{ box-shadow: 0 0 15px {active_color}; }}
        50% {{ box-shadow: 0 0 50px {active_color}, inset 0 0 20px {active_color}; }}
        100% {{ box-shadow: 0 0 15px {active_color}; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. HUB & SHOP ---
with st.sidebar:
    st.title(f"⚡ {st.session_state.user_name.upper()}")
    st.metric(f"{st.session_state.world_data['currency'].upper()}", f"{st.session_state.gold:.2f}")
    if st.button("🚀 HUB"): st.session_state.view = 'main'; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = 'shop'; st.rerun()
    if st.button("🚨 RESET"): st.session_state.clear(); st.rerun()

st.markdown(f"<h1 style='color:{active_color}; text-shadow: 0 0 20px {active_color};'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)

if st.session_state.view == 'shop':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(st.session_state.world_data['shield_name'])
        st.info(st.session_state.world_data['shield_lore'])
        if st.button(f"BUY (15 {st.session_state.world_data['currency']})"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success("ACTIVATED!")
    with col2:
        st.subheader(st.session_state.world_data['booster_name'])
        st.info(st.session_state.world_data['booster_lore'])
        if st.button(f"BUY (25 {st.session_state.world_data['currency']})"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.success("ACTIVATED!")
else:
    if st.button("START 1-MINUTE MISSION"):
        bar = st.progress(0)
        for i in range(60):
            time.sleep(1); bar.progress((i+1)/60)
        st.session_state.pending_gold = 1.0
        st.session_state.needs_verification = True; st.rerun()

if st.session_state.needs_verification:
    if st.file_uploader("Upload proof:") and st.button("JUDGE"):
        st.session_state.gold += st.session_state.pending_gold
        st.session_state.needs_verification = False; st.balloons(); st.rerun()
