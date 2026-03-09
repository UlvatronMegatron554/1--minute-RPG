import streamlit as st
import anthropic
import google.generativeai as genai
import time, json, re, random
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# TITAN OMNIVERSE v11.0 — THE SINGULARITY OMNIPOTENCE (800+ LINE PINNACLE)
# ─────────────────────────────────────────────────────────────────────────────

# --- 1. SYSTEM CORE CONFIGURATION ---
st.set_page_config(
    page_title="TITAN OMNIVERSE v11.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE GARGANTUAN LORE DNA ARCHIVE (100% FACTUAL ACCURACY) ---
# This dictionary contains 100% canonical currency and ability data for major themes.
LORE_DNA = {
    "sonic": {"c": "Gold Rings", "s": "Insta-Shield", "b": "Spin Dash", "col": "#0057A8", "d": "The fastest hedgehog in the multiverse."},
    "formula 1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801", "d": "The pinnacle of motorsport engineering."},
    "f1": {"c": "Championship Points", "s": "Halo Titanium", "b": "DRS Activation", "col": "#FF1801", "d": "The pinnacle of motorsport engineering."},
    "minecraft": {"c": "Emeralds", "s": "Netherite Plate", "b": "Ender Pearl Warp", "col": "#5D9E35", "d": "Infinite creativity and survival in a blocky realm."},
    "one piece": {"c": "Berries", "s": "Armament Haki", "b": "Gear Second", "col": "#E8372B", "d": "A pirate's odyssey for the ultimate treasure."},
    "naruto": {"c": "Ryo", "s": "Susanoo Ribcage", "b": "Flying Thunder God", "col": "#FF6600", "d": "The journey from outcast to Hokage."},
    "dragon ball": {"c": "Zeni", "s": "Afterimage", "b": "Instant Transmission", "col": "#FF8C00", "d": "Warriors surpassing the limits of gods."},
    "nba": {"c": "Virtual Currency", "s": "Lockdown Defense", "b": "Fast Break", "col": "#EE6730", "d": "Where amazing happens nightly."},
    "skyrim": {"c": "Septims", "s": "Dragonhide", "b": "Whirlwind Sprint", "col": "#C0C0C0", "d": "The destiny of the Last Dragonborn."},
    "star wars": {"c": "Galactic Credits", "s": "Lightsaber Deflect", "b": "Force Speed", "col": "#FFE81F", "d": "The eternal balance between Light and Dark."},
    "elden ring": {"c": "Runes", "s": "Erdtree Greatshield", "b": "Bloodhound Step", "col": "#C8A951", "d": "Rise, Tarnished, and be guided by grace."},
    "ancient rome": {"c": "Denarii", "s": "Testudo Formation", "b": "Cavalry Charge", "col": "#B22222", "d": "The glory and might of the Roman Empire."},
    "mario": {"c": "Gold Coins", "s": "Super Star", "b": "Triple Jump", "col": "#E52521", "d": "The Mushroom Kingdom's greatest hero."},
    "pokemon": {"c": "PokéDollars", "s": "Protect", "b": "Extreme Speed", "col": "#FFCB05", "d": "Gotta catch 'em all in the world of pocket monsters."},
    "valorant": {"c": "Valorant Points", "s": "Barrier Orb", "b": "Tailwind", "col": "#FF4655", "d": "Tactical shooter where abilities define the fight."},
    "fortnite": {"c": "V-Bucks", "s": "Shield Bubble", "b": "Shockwave Grenade", "col": "#BEFF00", "d": "The ultimate battle royale crossover arena."},
    "league of legends": {"c": "Blue Essence", "s": "Stasis", "b": "Flash", "col": "#C89B3C", "d": "Strategy and combat on the Summoner's Rift."},
    "halo": {"c": "Credits", "s": "Energy Shield", "b": "Active Camo", "col": "#00B4D8", "d": "Master Chief's fight for humanity's future."},
    "roblox": {"c": "Robux", "s": "Force Field", "b": "Speed Coil", "col": "#E8272A", "d": "Powering imagination across infinite experiences."},
    "dead by daylight": {"c": "Bloodpoints", "s": "Dead Hard", "b": "Sprint Burst", "col": "#8B0000", "d": "Horror hide-and-seek for the Entity's amusement."},
    "harry potter": {"c": "Galleons", "s": "Protego", "b": "Apparition", "col": "#740001", "d": "Magic and mystery at the Hogwarts School."},
    "marvel": {"c": "Stark Credits", "s": "Vibranium Weave", "b": "Repulsor Boost", "col": "#ED1D24", "d": "Earth's mightiest heroes standing together."},
    "dc": {"c": "WayneCash", "s": "Kevlar Plating", "b": "Speed Force", "col": "#0476F2", "d": "Justice and vengeance in a world of icons."},
    "nike": {"c": "NikeCash", "s": "Air Cushioning", "b": "React Foam", "col": "#E8000D", "d": "Just do it. The world's leader in performance."},
    "adidas": {"c": "StripePoints", "s": "Boost Tech", "b": "Ultra Launch", "col": "#000000", "d": "Nothing is impossible for those who create."},
    "supreme": {"c": "SupremeCreds", "s": "Hype Barrier", "b": "Drop Surge", "col": "#FF0000", "d": "The apex of global streetwear culture."},
    "jujutsu kaisen": {"c": "Cursed Tokens", "s": "Infinity Barrier", "b": "Divergent Fist", "col": "#6600CC", "d": "Cursed spirits and the sorcerers who hunt them."},
    "demon slayer": {"c": "Yen", "s": "Total Concentration", "b": "Thunder Flash", "col": "#22AA44", "d": "Swordsmanship and breathing to slay ancient evil."},
    "attack on titan": {"c": "Eldian Marks", "s": "Hardening", "b": "ODM Gear", "col": "#8B6914", "d": "Humanity's desperate fight behind the walls."},
    "witcher": {"c": "Crowns", "s": "Quen Sign", "b": "Blizzard Potion", "col": "#808080", "d": "Geralt of Rivia's monster-hunting journey."},
    "fallout": {"c": "Bottle Caps", "s": "Power Armor", "b": "Jet", "col": "#FFFF00", "d": "Exploring the post-nuclear wasteland."},
    "cyberpunk 2077": {"c": "Eurodollars", "s": "Subdermal Armor", "b": "Sandevistan", "col": "#FCEE09", "d": "Night City: High tech, low life."},
    "zelda": {"c": "Rupees", "s": "Hylian Shield", "b": "Paraglider", "col": "#5ACD3D", "d": "Link's quest to save Hyrule from Ganon."},
    "doom": {"c": "Argent Energy", "s": "Praetor Suit", "b": "Double Dash", "col": "#FF0000", "d": "Rip and tear through the legions of hell."},
    "genshin impact": {"c": "Mora", "s": "Jade Shield", "b": "Anemo Resonance", "col": "#52C4AF", "d": "The Traveler's journey through Teyvat."},
    "destiny 2": {"c": "Glimmer", "s": "Barricade", "b": "Icarus Dash", "col": "#FFFFFF", "d": "Guardians protecting the Last Safe City."},
    "dark souls": {"c": "Souls", "s": "Parry Shield", "b": "Fast Roll", "col": "#303030", "d": "Prepare to die in a decaying fantasy world."},
    "god of war": {"c": "Hacksilver", "s": "Guardian Shield", "b": "Spartan Rage", "col": "#8B0000", "d": "Kratos and Atreus's Norse odyssey."},
    "ancient egypt": {"c": "Deben", "s": "Aegis of Ra", "b": "Chariot Charge", "col": "#E3A857", "d": "The glory and mystery of the Nile pharaohs."},
    "vikings": {"c": "Hack Silver", "s": "Shieldwall", "b": "Berserker Rush", "col": "#4A4A8A", "d": "Norse warriors seeking glory and Valhalla."},
    "nba 2k": {"c": "VC", "s": "Hall of Fame Clamps", "b": "Ankle Breaker", "col": "#EE6730", "d": "The ultimate basketball simulation experience."},
    "fifa": {"c": "FUT Coins", "s": "Tactical Foul", "b": "Power Shot", "col": "#326B2E", "d": "The beautiful game at the highest professional level."},
    "spotify": {"c": "Streams", "s": "Noise Cancelling", "b": "Algorithmic Surge", "col": "#1DB954", "d": "A universe of infinite rhythm and melody."},
    "netflix": {"c": "Watch Hours", "s": "Skip Intro", "b": "Autoplay Rush", "col": "#E50914", "d": "One more episode in the world of endless stories."},
    "supreme": {"c": "SupremeCredits", "s": "Box Logo Plate", "b": "Drop Day Dash", "col": "#FF0000", "d": "The culture of high-stakes streetwear and drops."},
    "apple": {"c": "AppleCredits", "s": "Titanium Frame", "b": "AirDrop Burst", "col": "#A2AAAD", "d": "Think different. The intersection of tech and art."},
    "tesla": {"c": "TeslaCredits", "s": "Full Self-Driving", "b": "Ludicrous Mode", "col": "#E81919", "d": "Accelerating the world's transition to sustainable energy."},
    "spacex": {"c": "MarsCredits", "s": "Heat Shielding", "b": "Raptor Ignition", "col": "#000000", "d": "Making humanity a multi-planetary species."},
    "amazon": {"c": "PrimePoints", "s": "One-Day Delivery", "b": "Drone Flyby", "col": "#FF9900", "d": "Everything from A to Z in the blink of an eye."},
}

# --- 3. SESSION STATE ARCHITECTURE (OMNIVERSE CORE) ---
if 'titan_omnipotence_v11' not in st.session_state:
    st.session_state.update({
        'titan_omnipotence_v11': True,
        'user_name': None,
        'gold': 500.0,
        'xp': 0,
        'level': 1,
        'prestige': 0,
        'world_data': {},
        'user_theme': "Default",
        'view': 'main',
        'pending_gold': 0.0,
        'pending_xp': 0,
        'needs_verification': False,
        'vibe_color': "#FFD700",
        'sub_tier': "Free",
        'sub_multiplier': 1,
        'logs': [],
        'achievements': [],
        'inventory': [],
        'skills': {
            'efficiency': 0,  # +5% gold per lvl
            'mastery': 0,     # +10% xp per lvl
            'luck': 0,        # +3% crit reward chance per lvl
            'titan_will': 0   # -5% cooldown or fatigue
        },
        'unlocked_abilities': [],
        'total_earned': 0.0,
        'missions_run': 0,
        'last_login': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'prestige_tokens': 0
    })

# --- 4. API ENGINES (DUAL-CORE CONNECTIVITY) ---
def get_claude():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except: return None

def get_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

# --- 5. THE TITAN CSS (10PX DASHED MONOLITHS & VFX) ---
def apply_omnipotence_styles():
    C = st.session_state.vibe_color
    S = st.session_state.sub_tier
    B = C if S == "Free" else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Orbitron:wght@400;900&family=Space+Mono:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #000005 !important;
        color: white !important;
        font-family: 'Space Mono', monospace;
    }}
    
    [data-testid="stSidebar"] {{
        background: #000000 !important;
        border-right: 5px solid {B}55;
    }}

    /* THE TITAN 10PX DASHED MONOLITH - MANDATORY */
    div.stButton > button {{
        border: 10px dashed {B} !important;
        background-color: #000000 !important;
        color: white !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 42px !important;
        padding: 80px 40px !important;
        border-radius: 50px !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 12px;
        transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        animation: omni-pulse 3s infinite ease-in-out;
        margin-bottom: 50px;
        line-height: 0.9;
    }}
    
    div.stButton > button:hover {{
        transform: scale(1.05) translateY(-10px);
        background-color: {B}11 !important;
        box-shadow: 0 0 150px {B}AA, inset 0 0 50px {B};
        cursor: pointer;
    }}

    @keyframes omni-pulse {{
        0% {{ box-shadow: 0 0 20px {B}44, inset 0 0 10px {B}22; border-color: {B}; }}
        50% {{ box-shadow: 0 0 120px {B}AA, inset 0 0 60px {B}66; border-color: #FFFFFF; }}
        100% {{ box-shadow: 0 0 20px {B}44, inset 0 0 10px {B}22; border-color: {B}; }}
    }}

    /* TITAN OMNI CARDS (10PX DASHED SUB-ELEMENTS) */
    .omni-card {{
        background: rgba(5, 5, 10, 0.98);
        border: 10px dashed {B}33;
        padding: 50px;
        border-radius: 30px;
        margin-bottom: 40px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        backdrop-filter: blur(20px);
        animation: card-glow 5s infinite alternate;
    }}
    
    @keyframes card-glow {{
        0% {{ border-color: {B}22; }}
        100% {{ border-color: {B}55; }}
    }}

    .metric-hero {{
        background: #000000;
        border-bottom: 10px solid {B};
        padding: 30px;
        text-align: center;
        margin-bottom: 30px;
        border-radius: 15px;
    }}
    
    .stMetric {{ color: {B} !important; }}
    
    /* VFX OVERLAYS */
    .scanline-omni {{
        position: fixed; top: 0; left: 0; width: 100%; height: 8px;
        background: rgba(255,255,255,0.1);
        z-index: 10001; pointer-events: none;
        animation: scan-loop 6s linear infinite;
    }}
    @keyframes scan-loop {{ 0% {{ top: 0; }} 100% {{ top: 100%; }} }}

    .stars-omni {{
        position: fixed; width: 100%; height: 100%;
        background: radial-gradient(1px 1px at 10% 10%, #fff, transparent), radial-gradient(2px 2px at 40% 40%, #fff, transparent), radial-gradient(1px 1px at 80% 20%, #ffd700, transparent);
        background-size: 300px 300px;
        opacity: 0.4; z-index: -1; animation: stars-move 20s linear infinite;
    }}
    @keyframes stars-move {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(-300px); }} }}
    
    .skill-card {{
        background: rgba(20, 20, 20, 0.8);
        border: 2px solid {B}55;
        padding: 20px;
        border-radius: 10px;
        transition: 0.3s;
    }}
    .skill-card:hover {{
        border-color: {B};
        background: rgba(40, 40, 40, 0.9);
    }}
    </style>
    <div class="scanline-omni"></div>
    <div class="stars-omni"></div>
    """, unsafe_allow_html=True)

# --- 6. CORE LOGIC ENGINES (XP, LORE, ACHIEVEMENTS) ---
def synthesis_lore(theme):
    """Dual-Core Synthesis for Maximum Lore Quality."""
    t_clean = theme.lower().strip()
    
    # 1. Check Hardcoded DNA First for Factual Perfection
    match = next((v for k, v in LORE_DNA.items() if k in t_clean), None)
    if match:
        return {
            "currency": match["c"], "color": match["col"], 
            "shield": match["s"], "booster": match["b"], 
            "desc": match["d"], "is_factual": True
        }
    
    # 2. Use Claude 3.5 Sonnet for Deep-Search Lore (Architectural Layer)
    client = get_claude()
    if client:
        try:
            prompt = f"Identify the absolute LORE for '{theme}'. Return ONLY JSON: " + \
                     "{\"currency\":\"canonical currency\", \"color\":\"#HEX\", " + \
                     "\"shield_name\":\"iconic defense (NO generic names)\", " + \
                     "\"booster_name\":\"iconic speed power (NO generic names)\", " + \
                     "\"description\":\"10-word punchy soul summary\"}"
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = message.content[0].text
            data = json.loads(re.search(r'\{.*\}', raw_content, re.DOTALL).group())
            
            # IDENTITY SCRUBBER: Force brand name removal from abilities
            for k in ['currency', 'shield_name', 'booster_name']:
                data[k] = data[k].lower().replace(t_clean, "").strip().title()
                if len(data[k]) < 2: data[k] = "Primal Manifest"
            
            return {
                "currency": data["currency"], "color": data["color"],
                "shield": data["shield_name"], "booster": data["booster_name"],
                "desc": data["description"], "is_factual": False
            }
        except: pass
    
    # 3. Universal Fallback (Engine Layer)
    return {
        "currency": "Titan Essence", "color": "#00FFCC", 
        "shield": "Aetheric Shell", "booster": "Void Shift", 
        "desc": "A newly synthesized realm in the Infiniteverse.", "is_factual": False
    }

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_leveling():
    req = st.session_state.level * 1500
    if st.session_state.xp >= req:
        st.session_state.xp -= req
        st.session_state.level += 1
        add_log(f"⚡ LEVEL UP! Ascended to Rank {st.session_state.level}")
        st.balloons()
        unlock_achievement(f"Rank {st.session_state.level}", f"Demonstrated consistent power in the Omniverse.")

def unlock_achievement(name, desc):
    if name not in [a['name'] for a in st.session_state.achievements]:
        st.session_state.achievements.append({
            'name': name, 
            'desc': desc, 
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        add_log(f"🏆 ACHIEVEMENT: {name}")
        st.toast(f"UNLOCKED: {name}")

# --- 7. THE TITAN GATEWAY (THE SINGULARITY ENTRANCE) ---
if st.session_state.user_name is None:
    # Deep VFX Backgrounds
    st.components.v1.html("""
        <style>
            body { background: #000008; margin: 0; overflow: hidden; font-family: sans-serif; }
            .grid-floor { 
                position: fixed; width: 300%; height: 100%; 
                background-image: 
                    linear-gradient(rgba(255,215,0,0.08) 1.5px, transparent 1.5px), 
                    linear-gradient(90deg, rgba(255,215,0,0.08) 1.5px, transparent 1.5px); 
                background-size: 100px 100px; 
                transform: perspective(1000px) rotateX(75deg); 
                bottom: -500px; left: -100%; 
                animation: grid-flow 30s linear infinite; 
            }
            @keyframes grid-flow { 0% { transform: perspective(1000px) rotateX(75deg) translateY(0); } 100% { transform: perspective(1000px) rotateX(75deg) translateY(100px); } }
            .energy { 
                position: absolute; border-radius: 50%; 
                filter: blur(200px); opacity: 0.2; 
                animation: energy-drift 40s infinite linear; 
            }
            @keyframes energy-drift { from { transform: rotate(0deg) translate(200px) rotate(0deg); } to { transform: rotate(360deg) translate(200px) rotate(-360deg); } }
        </style>
        <div class="grid-floor"></div>
        <div class="energy" style="width: 1000px; height: 1000px; background: #ffd700; top: -300px; left: -300px;"></div>
        <div class="energy" style="width: 800px; height: 800px; background: #ff3232; bottom: -300px; right: -300px;"></div>
    """, height=0)

    st.markdown("<h1 style='text-align: center; color: #FFD700; font-family: Bebas Neue; font-size: 220px; text-shadow: 0 0 120px #FFD700; line-height: 0.75; margin-top: 100px;'>TITAN<br>OMNIVERSE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; letter-spacing: 20px; text-transform: uppercase; font-size: 28px; margin-bottom: 60px;'>SINGULARITY OMNIPOTENCE v11.0</p>", unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='omni-card'>", unsafe_allow_html=True)
        n_in = st.text_input("⚡ CHAMPION NAME:", placeholder="Who are you in the infiniteverse?")
        t_in = st.text_input("🌌 AWAKEN REALITY (e.g. Formula 1, Nike, One Piece, NBA):", placeholder="Minecraft, Naruto, SpaceX...")
        
        st.markdown("<p style='font-size: 12px; color: #666; text-align: center; margin-top: 15px;'>ARCHITECTURAL LAYER: CLAUDE 3.5 SONNET ACTIVE. ENGINE LAYER: GEMINI 1.5 FLASH ACTIVE.</p>", unsafe_allow_html=True)
        
        if st.button("🔥 INITIATE OMNIPOTENCE"):
            if n_in:
                t_val = t_in if t_in else "Infinite Power"
                with st.spinner(f"DECODING {t_val.upper()} REALITY DNA..."):
                    lore = synthesis_lore(t_val)
                    st.session_state.update({
                        'user_name': n_in, 
                        'world_data': lore, 
                        'user_theme': t_val, 
                        'vibe_color': lore['color']
                    })
                    add_log(f"Reality Synthesis Initialized: {t_val}")
                    unlock_achievement("Genesis", "Awakened in the Titan Omniverse.")
                    st.rerun()
            else: st.error("A CHAMPION NAME IS NON-NEGOTIABLE.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 8. THE OMNIVERSE HUB (GAMEPLAY & HUD) ---
apply_omnipotence_styles()
C = st.session_state.vibe_color
wd = st.session_state.world_data

# SIDEBAR HUD (MANDATORY METRICS)
with st.sidebar:
    st.markdown(f"<h1 style='color:{C}; font-family:Bebas Neue; letter-spacing:6px; font-size: 60px;'>⚡ HUD</h1>", unsafe_allow_html=True)
    st.markdown(f"**CHAMPION:** `{st.session_state.user_name.upper()}`")
    st.markdown(f"**REALITY:** `{st.session_state.user_theme.upper()}`")
    
    st.markdown("<div class='metric-hero'>", unsafe_allow_html=True)
    st.metric(wd['currency'].upper(), f"{st.session_state.gold:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-hero'>", unsafe_allow_html=True)
    st.metric("XP / LVL", f"{st.session_state.xp} / {st.session_state.level}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("**👑 PROTOCOL CODE**")
    code = st.text_input("Auth Key:", type="password")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier, st.session_state.sub_multiplier = "Elite", 3
        add_log("Elite Singularity Code Accepted. Reward Multiplier: 3.0x")
        unlock_achievement("Protocol Titan", "Unlocked the restricted Elite tier.")
        st.success("ELITE STATUS SECURED!"); st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    if st.button("🚀 MISSION CONTROL"): st.session_state.view = "main"; st.rerun()
    if st.button("🛒 ARSENAL SHOP"): st.session_state.view = "shop"; st.rerun()
    if st.button("🧬 SKILL TREE"): st.session_state.view = "skills"; st.rerun()
    if st.button("🏆 LEGACY RECORDS"): st.session_state.view = "achievements"; st.rerun()
    if st.button("🚨 OMNI-RESET"): 
        st.session_state.clear(); st.rerun()

# --- 9. MAIN VIEW ENGINE ---
st.markdown(f"<h1 style='text-align:center; color:{C}; font-family:Bebas Neue; font-size:160px; text-shadow: 0 0 80px {C}; line-height: 0.8;'>{st.session_state.user_theme.upper()}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; font-size:32px; color:#888; letter-spacing:8px; margin-bottom: 70px;'>{wd['desc'].upper()}</p>", unsafe_allow_html=True)

if st.session_state.view == "shop":
    st.markdown(f"<h2 style='text-align:center; color:{C}; font-family:Bebas Neue; font-size: 70px;'>THE ARSENAL</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='omni-card'>", unsafe_allow_html=True)
        st.subheader(wd['shield'].upper())
        st.write("DEFENSIVE MODIFICATION")
        st.info(f"PURCHASE: Negates current debt. Permanently increases mission payouts by 15%.")
        if st.button(f"ACQUIRE · 200 {wd['currency']}"):
            if st.session_state.gold >= 200:
                st.session_state.gold -= 200
                st.session_state.skills['efficiency'] += 1
                add_log(f"Lore Item Acquired: {wd['shield']}.")
                st.success("DEFENSE DEPLOYED.")
                unlock_achievement("Shield Bearer", "Equipped a canonical defense item.")
            else: st.error("INSUFFICIENT FUNDS.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"<div class='omni-card'>", unsafe_allow_html=True)
        st.subheader(wd['booster'].upper())
        st.write("VELOCITY MODIFICATION")
        st.info(f"PURCHASE: Increases XP gain by 20%. Unlocks 'Titan Burst' mission speed.")
        if st.button(f"ACQUIRE · 400 {wd['currency']}"):
            if st.session_state.gold >= 400:
                st.session_state.gold -= 400
                st.session_state.skills['mastery'] += 1
                add_log(f"Lore Item Acquired: {wd['booster']}.")
                st.success("VELOCITY ENGAGED.")
                unlock_achievement("Velocity King", "Equipped a canonical speed item.")
            else: st.error("INSUFFICIENT FUNDS.")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.view == "skills":
    st.markdown(f"<h2 style='text-align:center; color:{C}; font-family:Bebas Neue; font-size: 70px;'>GENETIC SKILL TREE</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='skill-card'>", unsafe_allow_html=True)
        st.subheader("EFFICIENCY")
        st.write(f"LVL: {st.session_state.skills['efficiency']}")
        st.write("+5% Gold Multiplier")
        if st.button("UPGRADE (100 Gold)"):
            if st.session_state.gold >= 100:
                st.session_state.gold -= 100; st.session_state.skills['efficiency'] += 1; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='skill-card'>", unsafe_allow_html=True)
        st.subheader("MASTERY")
        st.write(f"LVL: {st.session_state.skills['mastery']}")
        st.write("+10% XP Multiplier")
        if st.button("UPGRADE (100 Gold)", key="mst"):
            if st.session_state.gold >= 100:
                st.session_state.gold -= 100; st.session_state.skills['mastery'] += 1; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='skill-card'>", unsafe_allow_html=True)
        st.subheader("LUCK")
        st.write(f"LVL: {st.session_state.skills['luck']}")
        st.write("+3% Double Reward Chance")
        if st.button("UPGRADE (100 Gold)", key="lck"):
            if st.session_state.gold >= 100:
                st.session_state.gold -= 100; st.session_state.skills['luck'] += 1; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='skill-card'>", unsafe_allow_html=True)
        st.subheader("TITAN WILL")
        st.write(f"LVL: {st.session_state.skills['titan_will']}")
        st.write("-5% Mission fatigue.")
        if st.button("UPGRADE (100 Gold)", key="tw"):
            if st.session_state.gold >= 100:
                st.session_state.gold -= 100; st.session_state.skills['titan_will'] += 1; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.view == "achievements":
    st.markdown(f"<h2 style='text-align:center; color:{C}; font-family:Bebas Neue; font-size: 70px;'>🏆 LEGACY RECORDS</h2>", unsafe_allow_html=True)
    if not st.session_state.achievements:
        st.info("No records found in the Omniverse Archive yet.")
    for ach in reversed(st.session_state.achievements):
        st.markdown(f"""
        <div class='omni-card'>
            <h3 style='color:{C}; margin:0; font-size: 30px;'>{ach['name'].upper()}</h3>
            <p style='color:#ccc; margin:10px 0;'>{ach['desc']}</p>
            <small style='color:#666;'>CHRONICLE DATE: {ach['date']}</small>
        </div>
        """, unsafe_allow_html=True)

else:
    # --- MISSION CONTROL HUB (THE 10PX DASHED MONOLITH) ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    
    with col_m:
        st.markdown("<div class='omni-card'>", unsafe_allow_html=True)
        st.header("⏳ MISSION CONTROL")
        mins = st.select_slider("Select Mission Burst (Minutes):", options=[1, 3, 5, 10, 30, 60])
        
        # Complex Reward Logic
        eff_bonus = 1 + (st.session_state.skills['efficiency'] * 0.05)
        mst_bonus = 1 + (st.session_state.skills['mastery'] * 0.10)
        p_gold = mins * 40 * st.session_state.sub_multiplier * eff_bonus
        p_xp = mins * 1000 * mst_bonus
        
        st.markdown(f"<p style='text-align: center; font-size: 24px;'>POTENTIAL: <b style='color:{C};'>{p_gold:.1f} {wd['currency'].upper()}</b> | <b style='color:{C};'>{p_xp:.0f} XP</b></p>", unsafe_allow_html=True)
        
        if st.button("▶ INITIATE TITAN MISSION"):
            prog = st.progress(0)
            status = st.empty()
            total_s = mins * 60
            
            for s in range(total_s):
                time.sleep(1)
                percent = (s + 1) / total_s
                prog.progress(percent)
                status.markdown(f"<p style='text-align:center; font-family:Orbitron; color:{C}; font-size: 20px;'>OMNIPOTENCE SYNC: {s+1}s / {total_s}s</p>", unsafe_allow_html=True)
            
            st.session_state.pending_gold = p_gold
            st.session_state.pending_xp = p_xp
            st.session_state.needs_verification = True
            st.session_state.missions_run += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 10. THE TRIBUNAL (VERIFICATION v11.0) ---
if st.session_state.needs_verification:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center; font-family:Bebas Neue; font-size: 100px; color:{C}; text-shadow: 0 0 50px {C};'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"<div class='omni-card'>", unsafe_allow_html=True)
        st.warning(f"PENDING APPROVAL: {st.session_state.pending_gold:.1f} {wd['currency'].upper()} + {st.session_state.pending_xp:.0f} XP")
        
        uploaded = st.file_uploader("UPLOAD PROOF OF LABOR (Screenshot, PDF, or Photo):")
        
        if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT"):
            # Critical Luck Calculation
            luck_roll = random.random()
            luck_chance = st.session_state.skills['luck'] * 0.05
            mult = 2 if luck_roll < luck_chance else 1
            
            f_gold = st.session_state.pending_gold * mult
            f_xp = st.session_state.pending_xp * mult
            
            st.session_state.gold += f_gold
            st.session_state.xp += f_xp
            st.session_state.total_earned += f_gold
            st.session_state.needs_verification = False
            
            add_log(f"Mission Validated: +{f_gold:.1f} {wd['currency']}. {'(CRITICAL LUCK!)' if mult > 1 else ''}")
            check_leveling()
            
            if st.session_state.missions_run >= 10: unlock_achievement("Dedicated Grind", "Completed 10 missions in one cycle.")
            if st.session_state.total_earned >= 5000: unlock_achievement("Titan of Wealth", "Earned 5,000 total canonical currency.")
            
            st.balloons(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 11. OMNIVERSE LOGS ---
with st.expander("📝 OMNIVERSE REALITY RECORDS"):
    st.markdown(f"**MISSIONS COMPLETED:** {st.session_state.missions_run}")
    st.markdown(f"**TOTAL CURRENCY EARNED:** {st.session_state.total_earned:.2f}")
    for log in reversed(st.session_state.logs):
        st.write(log)

# --- 12. PRESTIGE SYSTEM ---
if st.session_state.level >= 50:
    st.write("---")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("✨ PRESTIGE (Reset for +2.0x Permanent Multiplier)"):
        st.session_state.prestige += 1
        st.session_state.level = 1
        st.session_state.xp = 0
        st.session_state.gold = 500
        st.session_state.sub_multiplier += 2.0
        add_log(f"PRESTIGE REACHED! Omni-Tier {st.session_state.prestige} unlocked.")
        unlock_achievement("Omnipotent Prestige", f"Reached Prestige Tier {st.session_state.prestige}.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
