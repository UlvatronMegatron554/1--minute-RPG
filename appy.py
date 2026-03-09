import streamlit as st
import anthropic
import time, json, re

# ─────────────────────────────────────────────────────────────────────────────
# TITAN OMNIVERSE v3.0 — Powered by Claude Sonnet
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="TITAN OMNIVERSE", page_icon="⚡", layout="wide")

# ── Fixed ability effect descriptions (NEVER change regardless of universe) ───
SHIELD_EFFECT  = "Negates any debt that was earned."
BOOSTER_EFFECT = "Grants a 3× multiplier on all mission rewards."

# ── Claude client ─────────────────────────────────────────────────────────────
def get_claude_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except Exception:
        return None

# ── Bulletproof JSON extractor ────────────────────────────────────────────────
def extract_json(raw_text):
    if not raw_text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    try:
        return json.loads(cleaned.replace("'", '"'))
    except Exception:
        pass
    result = {}
    for key in ["currency", "color", "shield_name", "booster_name", "description"]:
        m = re.search(rf'["\']?{key}["\']?\s*:\s*["\']([^"\'<>]+)["\']', cleaned, re.IGNORECASE)
        if m:
            result[key] = m.group(1).strip()
    return result if len(result) >= 4 else None

# ── The prompt ────────────────────────────────────────────────────────────────
LORE_PROMPT = """You are an expert on every game, anime, sport, brand, show, movie, book, music genre, fashion brand, and cultural phenomenon that exists.

A user has chosen the universe: "{theme}"

Return ONLY a single raw JSON object with no explanation, no markdown, no code fences, nothing else.

Rules:
- "currency": The EXACT in-universe currency or most fitting value unit. Ultra-specific — never generic "Credits" or "Points" unless that franchise literally uses those words. Examples: Minecraft=Emeralds, Mario=Coins, Naruto=Ryo, One Piece=Berries, F1=Championship Points, NBA=VC, Roblox=Robux, Fortnite=V-Bucks, Nike=NikeCash, Spotify=Streams.

- "color": The single most ICONIC hex color for this universe — use the exact brand/logo/title screen color:
  Super Smash Bros=#E4000F, Mario=#E52521, Sonic=#0057A8, Minecraft=#5D9E35, Fortnite=#BEFF00, Roblox=#E8272A, Pokemon=#FFCB05, Valorant=#FF4655, One Piece=#E8372B, Naruto=#FF6600, Dragon Ball=#FF8C00, Demon Slayer=#22AA44, JJK=#6600CC, Bleach=#000000, F1=#FF1801, NBA=#EE6730, NFL=#013369, FIFA=#326B2E, Star Wars=#FFE81F, Marvel=#ED1D24, DC=#0476F2, Harry Potter=#740001, Skyrim=#C0C0C0, Elden Ring=#C8A951, GTA=#F4B000, Halo=#00B4D8, Dead by Daylight=#8B0000, Among Us=#C51111, Apex=#DA292A, Nike=#111111, Adidas=#000000, Supreme=#FF0000, Spotify=#1DB954, Netflix=#E50914.
  For anything else: use the dominant color from that franchise logo or title card.

- "shield_name": The most iconic DEFENSIVE item, armor, or technique from this exact universe. 100% specific — never generic. Examples: Minecraft="Protection IV Netherite Chestplate", Naruto="Susanoo Ribcage", F1="Halo Titanium Cockpit", NBA="Lockdown Defender", Harry Potter="Protego Totalum", Nike="Air Max Cushioning".

- "booster_name": The most iconic SPEED or MOVEMENT ability from this exact universe. 100% specific. Examples: Minecraft="Ender Pearl Warp", Naruto="Flying Thunder God", F1="DRS Activation", NBA="Fast Break", Harry Potter="Apparition", Nike="ReactX Foam Propulsion".

- "description": One punchy sentence (max 12 words) capturing the soul of this universe.

Return exactly:
{{"currency": "...", "color": "#RRGGBB", "shield_name": "...", "booster_name": "...", "description": "..."}}"""

# ── Hardcoded safety net ──────────────────────────────────────────────────────
HARD_FALLBACKS = {
    "super smash bros":  {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"Every gaming legend meets in the ultimate crossover brawl."},
    "smash bros":        {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"Every gaming legend meets in the ultimate crossover brawl."},
    "mario":             {"currency":"Coins","color":"#E52521","shield_name":"Super Star Invincibility","booster_name":"Cape Feather Spin","description":"The mushroom kingdom's greatest hero leaps through worlds."},
    "sonic":             {"currency":"Gold Rings","color":"#0057A8","shield_name":"Insta-Shield","booster_name":"Spin Dash","description":"The fastest thing alive races at the speed of sound."},
    "minecraft":         {"currency":"Emeralds","color":"#5D9E35","shield_name":"Protection IV Netherite Chestplate","booster_name":"Ender Pearl Warp","description":"A boundless world of blocks where creativity and survival collide."},
    "fortnite":          {"currency":"V-Bucks","color":"#BEFF00","shield_name":"Shield Bubble","booster_name":"Shockwave Grenade","description":"100 players drop in. Only one walks out."},
    "roblox":            {"currency":"Robux","color":"#E8272A","shield_name":"Force Field","booster_name":"Speed Coil","description":"An infinite universe of user-built worlds with zero limits."},
    "pokemon":           {"currency":"PokéDollars","color":"#FFCB05","shield_name":"Protect","booster_name":"Extreme Speed","description":"Catch, train, and battle creatures across endless adventure."},
    "valorant":          {"currency":"VP","color":"#FF4655","shield_name":"Sage Barrier Orb","booster_name":"Jett Updraft","description":"Precise gunplay meets deadly abilities in a tactical shooter."},
    "dead by daylight":  {"currency":"Bloodpoints","color":"#8B0000","shield_name":"Dead Hard","booster_name":"Sprint Burst","description":"Survivors and killers play an eternal game of death."},
    "dbd":               {"currency":"Bloodpoints","color":"#8B0000","shield_name":"Dead Hard","booster_name":"Sprint Burst","description":"Survivors and killers play an eternal game of death."},
    "one piece":         {"currency":"Berries","color":"#E8372B","shield_name":"Armament Haki","booster_name":"Gear Second","description":"A pirate's odyssey chasing the ultimate treasure."},
    "naruto":            {"currency":"Ryo","color":"#FF6600","shield_name":"Susanoo Ribcage","booster_name":"Flying Thunder God","description":"From outcast to the strongest — the ninja's path."},
    "dragon ball":       {"currency":"Zeni","color":"#FF8C00","shield_name":"Barrier Blast","booster_name":"Instant Transmission","description":"Warriors transcend all limits in an eternal quest for power."},
    "demon slayer":      {"currency":"Yen","color":"#22AA44","shield_name":"Total Concentration Breathing","booster_name":"Thunder Breathing First Form","description":"Demon hunters clash with ancient evil using breathing and will."},
    "attack on titan":   {"currency":"Eldian Marks","color":"#8B6914","shield_name":"Hardening Crystal","booster_name":"ODM Gear Swing","description":"Humanity fights back against titans behind crumbling walls."},
    "jujutsu kaisen":    {"currency":"Cursed Tokens","color":"#6600CC","shield_name":"Infinity Barrier","booster_name":"Divergent Fist","description":"Cursed energy battles rage beneath everyday life."},
    "bleach":            {"currency":"Spirit Coins","color":"#000000","shield_name":"Hierro Skin","booster_name":"Shunpo Flash Step","description":"Soul Reapers clash with Hollows in a war between life and death."},
    "my hero academia":  {"currency":"Hero Credits","color":"#1DA462","shield_name":"Full Cowl Armor","booster_name":"One For All Smash","description":"Heroes and villains clash where quirks define destiny."},
    "f1":                {"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium Cockpit","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed and nerve collide."},
    "formula 1":         {"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium Cockpit","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed and nerve collide."},
    "nba":               {"currency":"VC","color":"#EE6730","shield_name":"Lockdown Defender","booster_name":"Fast Break","description":"The greatest basketball league where legends are born nightly."},
    "nfl":               {"currency":"Fan Tokens","color":"#013369","shield_name":"Blitz Package","booster_name":"Hail Mary","description":"America's most electrifying sport played by the world's greatest."},
    "fifa":              {"currency":"FUT Coins","color":"#326B2E","shield_name":"Tactical Foul","booster_name":"Through Ball Sprint","description":"The beautiful game at the highest level on every continent."},
    "soccer":            {"currency":"FUT Coins","color":"#326B2E","shield_name":"Tactical Foul","booster_name":"Through Ball Sprint","description":"90 minutes, one ball, infinite passion."},
    "harry potter":      {"currency":"Galleons","color":"#740001","shield_name":"Protego Totalum","booster_name":"Apparition","description":"A world of magic and courage hidden behind ordinary life."},
    "star wars":         {"currency":"Galactic Credits","color":"#FFE81F","shield_name":"Lightsaber Deflect","booster_name":"Force Speed","description":"A galaxy far away locked in eternal war between light and dark."},
    "marvel":            {"currency":"Stark Credits","color":"#ED1D24","shield_name":"Vibranium Shield","booster_name":"Repulsor Boost","description":"Earth's mightiest heroes stand against total annihilation."},
    "dc":                {"currency":"WayneCash","color":"#0476F2","shield_name":"Nth Metal Armor","booster_name":"Flash Speed Force","description":"Iconic heroes wage war for the soul of civilization."},
    "batman":            {"currency":"WayneCash","color":"#1A1A2E","shield_name":"Kevlar Batsuit","booster_name":"Grapnel Gun Swing","description":"The Dark Knight — vengeance wrapped in shadow and steel."},
    "skyrim":            {"currency":"Septims","color":"#C0C0C0","shield_name":"Dragonhide Spell","booster_name":"Whirlwind Sprint Shout","description":"The Dragonborn's destiny unfolds across a frozen ancient land."},
    "elden ring":        {"currency":"Runes","color":"#C8A951","shield_name":"Erdtree Greatshield","booster_name":"Bloodhound Step","description":"A shattered world of demigods in pursuit of the Elden Ring."},
    "gta":               {"currency":"GTA$","color":"#F4B000","shield_name":"Body Armor","booster_name":"Rocket Boost","description":"Power, money, and chaos rule the streets."},
    "halo":              {"currency":"CR","color":"#00B4D8","shield_name":"Energy Shield","booster_name":"Active Camo","description":"Master Chief stands as humanity's last line against the Covenant."},
    "apex legends":      {"currency":"Apex Coins","color":"#DA292A","shield_name":"Evo Shield","booster_name":"Pathfinder Grapple","description":"Legends compete in a brutal frontier battle royale."},
    "among us":          {"currency":"Stars","color":"#C51111","shield_name":"Emergency Meeting","booster_name":"Vent Escape","description":"Trust no one — the impostor walks among you right now."},
    "league of legends": {"currency":"Blue Essence","color":"#C89B3C","shield_name":"Locket of the Iron Solari","booster_name":"Ghost Summoner Spell","description":"Five champions. One nexus. Infinite ways to win or lose."},
    "call of duty":      {"currency":"CoD Points","color":"#FF6600","shield_name":"Trophy System","booster_name":"Tactical Sprint","description":"The world's most intense military shooter — no mercy in ranked."},
    "zelda":             {"currency":"Rupees","color":"#5ACD3D","shield_name":"Hylian Shield","booster_name":"Ocarina Serenade","description":"The hero of time journeys through Hyrule to defeat darkness."},
    "overwatch":         {"currency":"Overwatch Coins","color":"#F99E1A","shield_name":"Reinhardt Barrier","booster_name":"Lucio Speed Boost","description":"Colorful heroes battle across a futuristic world in conflict."},
    "nike":              {"currency":"NikeCash","color":"#111111","shield_name":"Air Max Cushioning","booster_name":"ReactX Foam Propulsion","description":"Just Do It — where athletic performance meets street culture."},
    "adidas":            {"currency":"StripePoints","color":"#000000","shield_name":"Boost Sole Absorption","booster_name":"Ultraboost Launch","description":"Impossible Is Nothing — three stripes defining sport and culture."},
    "supreme":           {"currency":"SupremeCreds","color":"#FF0000","shield_name":"Box Logo Drop","booster_name":"Hype Wave","description":"The most coveted box logo in streetwear — drop day is everything."},
    "spotify":           {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancelling","booster_name":"Algorithmic Surge","description":"Music for everyone — three million songs, infinite discovery."},
    "netflix":           {"currency":"Watch Hours","color":"#E50914","shield_name":"Skip Intro","booster_name":"Autoplay Rush","description":"One more episode — the platform that redefined how we watch."},
    "ancient rome":      {"currency":"Denarii","color":"#B22222","shield_name":"Testudo Formation","booster_name":"Cavalry Charge","description":"Iron legions built the greatest empire the world has ever seen."},
    "vikings":           {"currency":"Silver Hack","color":"#4A4A8A","shield_name":"Shieldwall","booster_name":"Berserker Rush","description":"Norse warriors carved history across uncharted seas with axes."},
    "kpop":              {"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma."},
    "k-pop":             {"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma."},
}

def get_fallback(theme):
    t = theme.lower().strip()
    if t in HARD_FALLBACKS:
        return HARD_FALLBACKS[t]
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key:
            return data
    if any(w in t for w in ("game","gaming","rpg","fps","moba","battle royale")):
        return {"currency":"Gold","color":"#FFD700","shield_name":"Barrier Field","booster_name":"Phase Dash","description":"An infinite digital universe where only the skilled survive."}
    if any(w in t for w in ("anime","manga","shonen","seinen")):
        return {"currency":"Ryo","color":"#FF4500","shield_name":"Armament Aura","booster_name":"Body Flicker","description":"A world of extraordinary power, honour, and relentless destiny."}
    if any(w in t for w in ("sport","league","cup","championship","team","fc","united")):
        return {"currency":"Trophy Points","color":"#FFD700","shield_name":"Iron Defense","booster_name":"Turbo Sprint","description":"The ultimate competitive arena where legends are made."}
    if any(w in t for w in ("fashion","brand","wear","style","cloth","retail","shop","drip")):
        return {"currency":"Style Credits","color":"#FF69B4","shield_name":"Signature Drip","booster_name":"Trend Surge","description":"Where identity becomes art and every fit tells a story."}
    if any(w in t for w in ("music","rap","hip","pop","rock","edm","trap","drill")):
        return {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancel","booster_name":"Drop Surge","description":"A universe built on rhythm, bars, and raw cultural resonance."}
    return {"currency":"Titan Shards","color":"#00FFCC","shield_name":"Kinetic Barrier","booster_name":"Void Dash","description":"A realm of boundless power and infinite possibility."}

# ── MAIN RESOLVER ─────────────────────────────────────────────────────────────
REQUIRED_KEYS = ["currency", "color", "shield_name", "booster_name", "description"]

def resolve_universe(theme):
    client = get_claude_client()
    if client is not None:
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                messages=[{"role": "user", "content": LORE_PROMPT.format(theme=theme)}]
            )
            raw  = message.content[0].text.strip()
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color", "")):
                    data["color"] = "#FFD700"
                data["shield_effect"]  = SHIELD_EFFECT
                data["booster_effect"] = BOOSTER_EFFECT
                return data
        except Exception:
            pass
    data = get_fallback(theme)
    data["shield_effect"]  = SHIELD_EFFECT
    data["booster_effect"] = BOOSTER_EFFECT
    return data

# ── Session State Init ─────────────────────────────────────────────────────────
if "gold" not in st.session_state:
    st.session_state.update({
        "user_name": None, "gold": 10.0, "xp": 0, "level": 1,
        "world_data": {}, "user_theme": "",
        "view": "main", "pending_gold": 0.0, "needs_verification": False,
        "vibe_color": "#FFD700", "sub_tier": "Free", "sub_multiplier": 1,
        "total_missions": 0,
    })

# ─────────────────────────────────────────────────────────────────────────────
# GATEWAY SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_name is None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background: #050505 !important; color: white; font-family: 'Space Mono', monospace;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent !important; }
    #MainMenu, footer { visibility: hidden; }
    .gw-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(60px, 12vw, 120px); text-align: center;
        background: linear-gradient(135deg, #FFD700, #FF8C00, #FF3C3C);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; letter-spacing: 6px; line-height: 1;
    }
    .gw-sub { text-align:center; font-size:12px; color:#555; letter-spacing:3px; text-transform:uppercase; margin-bottom:36px; }
    .gw-card { background:rgba(12,12,12,0.97); border:1px solid rgba(255,215,0,0.12); border-radius:20px; padding:40px; }
    .chip-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
    .chip { background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.18); border-radius:99px; padding:4px 12px; font-size:11px; color:#666; letter-spacing:1px; }
    div.stButton > button {
        border:3px solid #FFD700 !important; background:#000 !important; color:white !important;
        font-family:'Bebas Neue',sans-serif !important; font-size:20px !important;
        letter-spacing:3px !important; padding:16px !important; border-radius:12px !important;
        width:100%; transition:all 0.3s;
    }
    div.stButton > button:hover { background:rgba(255,215,0,0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="gw-title">INFINITEVERSE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gw-sub">⚡ Any universe. Any world. Zero limits.</p>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="gw-card">', unsafe_allow_html=True)
        name_input  = st.text_input("YOUR CHAMPION NAME", placeholder="What are you called?", key="gw_name")
        theme_input = st.text_input("YOUR UNIVERSE", placeholder="Minecraft · One Piece · F1 · Dead by Daylight · Nike · anything...", key="gw_theme")

        examples = ["Minecraft","Super Smash Bros","One Piece","Formula 1","Dead by Daylight",
                    "Pokemon","Naruto","NBA","Roblox","Harry Potter","Valorant","Nike","K-Pop","Ancient Rome"]
        st.markdown('<div class="chip-row">' + "".join(f'<span class="chip">{e}</span>' for e in examples) + '</div><br>', unsafe_allow_html=True)

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name.")
            elif not theme_input.strip():
                st.error("Choose a universe — anything works.")
            else:
                with st.spinner(f"🌐 Loading {theme_input.upper()} universe data..."):
                    world_data = resolve_universe(theme_input.strip())
                st.session_state.user_name  = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color", "#FFD700")
                st.session_state.user_theme = theme_input.strip()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
C        = st.session_state.vibe_color
wd       = st.session_state.world_data
currency = wd.get("currency", "Credits")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {{ background:#050505 !important; color:white; font-family:'Space Mono',monospace; }}
[data-testid="stHeader"], [data-testid="stToolbar"] {{ background:transparent !important; }}
[data-testid="stSidebar"] {{ background:#080808 !important; }}
#MainMenu, footer {{ visibility:hidden; }}
@keyframes titan-pulse {{
    0%   {{ box-shadow:0 0 20px {C},inset 0 0 10px {C}; border-color:{C}; }}
    50%  {{ box-shadow:0 0 80px {C},inset 0 0 40px {C}; border-color:#FFF; }}
    100% {{ box-shadow:0 0 20px {C},inset 0 0 10px {C}; border-color:{C}; }}
}}
div.stButton > button {{
    border:8px dashed {C} !important; background:#000 !important; color:white !important;
    font-family:'Bebas Neue',sans-serif !important; font-size:28px !important;
    letter-spacing:4px !important; padding:50px 30px !important; border-radius:40px !important;
    animation:titan-pulse 2.5s infinite ease-in-out !important;
    width:100%; text-transform:uppercase; transition:transform 0.3s; margin-bottom:20px;
}}
div.stButton > button:hover {{ transform:scale(1.02); }}
.metric-card {{ background:rgba(20,20,20,0.95); border:2px solid {C}; padding:18px; border-radius:14px; text-align:center; margin-bottom:12px; }}
.shop-card   {{ border:3px solid {C}; padding:24px; border-radius:18px; background:rgba(10,10,10,0.9); margin-bottom:12px; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>⚡ TITAN HUB</h1>", unsafe_allow_html=True)
    st.write(f"**CHAMPION:** {st.session_state.user_name.upper()}")
    st.write(f"**UNIVERSE:** {st.session_state.user_theme}")
    st.write(f"**RANK:** {st.session_state.sub_tier.upper()}")
    st.markdown(f"<div class='metric-card'><div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C};margin:0'>{st.session_state.gold:.2f}</div><div style='font-size:10px;color:#555;letter-spacing:2px'>{currency.upper()}</div></div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("**👑 ELITE ACTIVATION**")
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3
        st.success("ELITE STATUS SECURED!"); st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    if st.button("🚀 MISSION HUB", key="nav_hub"):  st.session_state.view = "main"; st.rerun()
    if st.button("🛒 ARSENAL",     key="nav_shop"):  st.session_state.view = "shop"; st.rerun()

    st.write("---")
    st.markdown("**🌐 SWITCH UNIVERSE**")
    new_theme = st.text_input("New universe:", placeholder="Try anything...", key="switch_theme")
    if st.button("🔄 WARP", key="warp_btn"):
        if new_theme.strip():
            with st.spinner(f"Warping to {new_theme}..."):
                world_data = resolve_universe(new_theme.strip())
            st.session_state.world_data = world_data
            st.session_state.vibe_color = world_data.get("color", "#FFD700")
            st.session_state.user_theme = new_theme.strip()
            st.rerun()

    st.write("---")
    if st.button("🚨 FULL RESET", key="reset_btn"):
        st.session_state.clear(); st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};
           font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>
    {st.session_state.user_theme.upper()}
</h1>
<p style='text-align:center;font-size:16px;color:#666;margin-top:4px'>{wd.get("description","A realm of infinite power.")}</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── SHOP VIEW ─────────────────────────────────────────────────────────────────
if st.session_state.view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>MULTIVERSE ARSENAL</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='shop-card'>
            <div style='font-size:10px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚔️ DEFENSE ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 12px'>{wd.get('shield_name','Shield').upper()}</h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:4px'>{SHIELD_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#444'>Cost: <span style='color:{C};font-weight:bold'>15 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚔️ ACQUIRE · 15 {currency}", key="buy_shield"):
            if st.session_state.gold >= 15:
                st.session_state.gold -= 15; st.success(f"⚔️ {wd.get('shield_name')} activated!")
            else:
                st.error("Not enough currency.")

    with col2:
        st.markdown(f"""
        <div class='shop-card'>
            <div style='font-size:10px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚡ SPEED ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 12px'>{wd.get('booster_name','Booster').upper()}</h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:4px'>{BOOSTER_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#444'>Cost: <span style='color:{C};font-weight:bold'>25 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚡ ACQUIRE · 25 {currency}", key="buy_booster"):
            if st.session_state.gold >= 25:
                st.session_state.gold -= 25; st.session_state.sub_multiplier = 3; st.success(f"⚡ {wd.get('booster_name')} engaged!")
            else:
                st.error("Not enough currency.")

# ── MISSION HUB VIEW ──────────────────────────────────────────────────────────
else:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        reward   = 1.0 * st.session_state.sub_multiplier
        mult_tag = f" ×{st.session_state.sub_multiplier}" if st.session_state.sub_multiplier > 1 else ""
        st.markdown(f"""
        <div style='text-align:center;background:rgba(20,20,20,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;margin-bottom:20px'>
            <div style='font-size:11px;color:#444;letter-spacing:2px'>MISSION REWARD</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:52px;color:{C};margin:6px 0'>{reward:.1f} {currency}{mult_tag}</div>
            <div style='font-size:11px;color:#333'>per completed 1-minute mission</div>
        </div>""", unsafe_allow_html=True)

        if st.button("▶  START 1-MINUTE MISSION", key="start_mission"):
            bar = st.progress(0); status = st.empty()
            for i in range(60):
                time.sleep(1); bar.progress((i+1)/60)
                status.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#555'>SYNCHRONIZING: {i+1}s / 60s</p>", unsafe_allow_html=True)
            st.session_state.pending_gold = reward; st.session_state.needs_verification = True; st.rerun()

# ── TRIBUNAL ──────────────────────────────────────────────────────────────────
if st.session_state.needs_verification:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center;font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:4px'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.info(f"Upload proof of work to claim **{st.session_state.pending_gold:.1f} {currency}**")
        uploaded = st.file_uploader("PROOF OF LABOR (screenshot, photo, notes):", key="proof_upload")
        if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT", key="submit_proof"):
            earned = st.session_state.pending_gold
            st.session_state.gold += earned; st.session_state.total_missions += 1
            st.session_state.needs_verification = False; st.session_state.pending_gold = 0.0
            st.balloons(); st.success(f"✅ VERIFIED. +{earned:.1f} {currency} added to your balance.")
            time.sleep(1); st.rerun()
