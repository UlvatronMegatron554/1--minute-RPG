import streamlit as st
import google.generativeai as genai
import time, json, re, random

# ─────────────────────────────────────────────────────────────────────────────
# TITAN OMNIVERSE v2.0 — Single File Edition
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="TITAN OMNIVERSE", page_icon="⚡", layout="wide")

MODEL_ID = "gemini-1.5-flash"

# ── Model init ────────────────────────────────────────────────────────────────
def get_model():
    try:
        key = st.secrets["GEMINI_KEY"]
        genai.configure(api_key=key)
        return genai.GenerativeModel(
            MODEL_ID,
            generation_config={"temperature": 0.7, "max_output_tokens": 512}
        )
    except Exception:
        return None

# ── Bulletproof JSON extractor ────────────────────────────────────────────────
def extract_json(raw_text):
    if not raw_text:
        return None
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    # Attempt 1: direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    # Attempt 2: find first {...} block
    match = re.search(r"\{.*?\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    # Attempt 3: fix single quotes
    try:
        return json.loads(cleaned.replace("'", '"'))
    except Exception:
        pass
    # Attempt 4: regex key extraction
    result = {}
    for key in ["currency", "color", "shield_name", "booster_name",
                "shield_lore", "booster_lore", "description"]:
        m = re.search(rf'["\']?{key}["\']?\s*:\s*["\']([^"\']+)["\']', cleaned, re.IGNORECASE)
        if m:
            result[key] = m.group(1)
    return result if len(result) >= 4 else None

# ── Prompt ────────────────────────────────────────────────────────────────────
# KEY DESIGN:
# - shield_name / booster_name = ultra-specific item FROM that universe
# - shield_effect / booster_effect = ALWAYS fixed (we inject these ourselves)
# - color = the SINGLE most recognizable color tied to that IP/brand/topic
# - currency = the most logical reward/value unit for that universe

LORE_PROMPT = """You are a universe lore encoder. Return ONLY a raw JSON object. No markdown, no code fences, no explanation whatsoever.

UNIVERSE: "{theme}"

RULES:
1. "currency" = the most well-known in-universe coin, reward, or value unit. Examples: Minecraft→"Emeralds", Mario→"Coins", F1→"Championship Points", Nike→"NikeCash", NBA→"VC", Naruto→"Ryo", Dune→"Solaris". Be creative and specific — never use generic words like "Credits" or "Points" unless that universe literally uses them.
2. "color" = the single most ICONIC hex color for this universe. Be exact and precise:
   - Super Smash Bros = #E4000F (bright Nintendo red from the logo/title screen)
   - Mario = #E52521 (Mario's red)
   - Sonic = #0057A8 (Sega blue)
   - Minecraft = #5D9E35 (grass green)
   - Fortnite = #BEFF00 (neon yellow-green)
   - One Piece = #E8372B (Luffy's red vest)
   - Dragon Ball = #FF8C00 (orange gi)
   - Naruto = #FF6600 (orange jumpsuit)
   - F1 = #FF1801 (Formula 1 red)
   - NBA = #EE6730 (NBA orange)
   - Pokemon = #FFCB05 (Pikachu yellow)
   - Harry Potter = #740001 (Gryffindor red)
   - Star Wars = #FFE81F (crawl yellow)
   - Valorant = #FF4655 (Valorant red)
   - Halo = #008000 (Master Chief green)
   - Dead by Daylight = #8B0000 (blood red)
   - Roblox = #E8272A (Roblox red)
   - For anything else: pick the dominant brand/title/logo color, not a character color.
3. "shield_name" = the most iconic DEFENSIVE item, armor, technique, or concept from this universe. Must be specific — not generic.
4. "booster_name" = the most iconic SPEED or MOVEMENT ability, item, or technique. Must be specific — not generic.
5. "description" = one punchy sentence capturing the soul of this universe.

Return exactly:
{{"currency": "...", "color": "#RRGGBB", "shield_name": "...", "booster_name": "...", "description": "..."}}

Examples:
- "Minecraft": {{"currency": "Emeralds", "color": "#5D9E35", "shield_name": "Protection IV Netherite Chestplate", "booster_name": "Ender Pearl Warp", "description": "A boundless world of blocks where creativity and survival collide."}}
- "Super Smash Bros": {{"currency": "KO Points", "color": "#E4000F", "shield_name": "Perfect Shield", "booster_name": "Wavedash", "description": "The ultimate crossover battle arena where gaming legends clash."}}
- "Formula 1": {{"currency": "Championship Points", "color": "#FF1801", "shield_name": "Halo Titanium", "booster_name": "DRS Activation", "description": "The pinnacle of motorsport where speed, strategy and nerve collide."}}
- "One Piece": {{"currency": "Berries", "color": "#E8372B", "shield_name": "Armament Haki", "booster_name": "Gear Second", "description": "A pirate's odyssey across infinite oceans in search of the ultimate treasure."}}

Now return ONLY the JSON for "{theme}":"""

# ── Hardcoded fallbacks for when AI is unavailable ────────────────────────────
# Covers the most popular universes with pixel-perfect data.
HARD_FALLBACKS = {
    "super smash bros": {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"The ultimate crossover arena where every gaming legend settles the score."},
    "smash bros":       {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"The ultimate crossover arena where every gaming legend settles the score."},
    "mario":            {"currency":"Coins","color":"#E52521","shield_name":"Super Star","booster_name":"Cape Feather","description":"The mushroom kingdom's greatest hero leaps through worlds beyond imagination."},
    "sonic":            {"currency":"Gold Rings","color":"#0057A8","shield_name":"Insta-Shield","booster_name":"Spin Dash","description":"The fastest thing alive races through worlds at the speed of sound."},
    "minecraft":        {"currency":"Emeralds","color":"#5D9E35","shield_name":"Protection IV Netherite Chestplate","booster_name":"Ender Pearl Warp","description":"A boundless world of blocks where creativity and survival collide."},
    "fortnite":         {"currency":"V-Bucks","color":"#BEFF00","shield_name":"Shield Bubble","booster_name":"Shockwave Grenade","description":"100 players drop in. Only one walks out."},
    "roblox":           {"currency":"Robux","color":"#E8272A","shield_name":"Force Field","booster_name":"Speed Coil","description":"An infinite universe of user-built worlds with no limits."},
    "pokemon":          {"currency":"PokéDollars","color":"#FFCB05","shield_name":"Protect","booster_name":"Extreme Speed","description":"Catch, train, and battle creatures across a world of endless adventure."},
    "valorant":         {"currency":"VP","color":"#FF4655","shield_name":"Sage Barrier","booster_name":"Jett Updraft","description":"Precise gunplay meets deadly abilities in a high-stakes tactical shooter."},
    "dead by daylight":  {"currency":"Bloodpoints","color":"#8B0000","shield_name":"Dead Hard","booster_name":"Sprint Burst","description":"A nightmare realm where survivors and killers play an eternal game of death."},
    "one piece":        {"currency":"Berries","color":"#E8372B","shield_name":"Armament Haki","booster_name":"Gear Second","description":"A pirate's odyssey across infinite oceans in search of the ultimate treasure."},
    "naruto":           {"currency":"Ryo","color":"#FF6600","shield_name":"Susanoo","booster_name":"Body Flicker","description":"The path of the ninja — from outcast to the strongest in the village."},
    "dragon ball":      {"currency":"Zeni","color":"#FF8C00","shield_name":"Barrier Blast","booster_name":"Instant Transmission","description":"Warriors transcend limits in an endless quest for power and battle."},
    "demon slayer":     {"currency":"Yen","color":"#22AA44","shield_name":"Total Concentration","booster_name":"Thunder Breathing","description":"Demon hunters clash with ancient evil using breathing techniques and pure will."},
    "attack on titan":  {"currency":"Eldian Marks","color":"#8B6914","shield_name":"Hardening Crystal","booster_name":"ODM Gear Swing","description":"Humanity's last survivors fight back against giants behind crumbling walls."},
    "f1":               {"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed, strategy and nerve collide."},
    "formula 1":        {"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed, strategy and nerve collide."},
    "nba":              {"currency":"VC","color":"#EE6730","shield_name":"Lockdown Defense","booster_name":"Fast Break","description":"The greatest basketball league on Earth where legends are born every night."},
    "nfl":              {"currency":"Fan Tokens","color":"#013369","shield_name":"Blitz Package","booster_name":"Hail Mary","description":"America's most electrifying sport played by the world's greatest athletes."},
    "harry potter":     {"currency":"Galleons","color":"#740001","shield_name":"Protego Totalum","booster_name":"Apparition","description":"A world of magic, mystery, and courage hidden behind ordinary life."},
    "star wars":        {"currency":"Credits","color":"#FFE81F","shield_name":"Lightsaber Deflect","booster_name":"Force Speed","description":"A galaxy far, far away locked in eternal war between light and dark."},
    "marvel":           {"currency":"Stark Credits","color":"#ED1D24","shield_name":"Vibranium Shield","booster_name":"Repulsor Boost","description":"Earth's mightiest heroes stand between humanity and total annihilation."},
    "skyrim":           {"currency":"Septims","color":"#C0C0C0","shield_name":"Dragonhide","booster_name":"Whirlwind Sprint","description":"The Dragonborn's destiny unfolds across a frozen land of ancient power."},
    "elden ring":       {"currency":"Runes","color":"#C8A951","shield_name":"Erdtree Greatshield","booster_name":"Bloodhound Step","description":"A shattered world of demigods, death, and the pursuit of the Elden Ring."},
    "gta":              {"currency":"GTA$","color":"#F4B000","shield_name":"Body Armor","booster_name":"Rocket Boost","description":"Life on the streets where power, money, and chaos rule everything."},
    "nike":             {"currency":"NikeCash","color":"#111111","shield_name":"Air Max Cushion","booster_name":"React Foam Burst","description":"Just Do It — where athletic performance meets street culture."},
    "adidas":           {"currency":"Stripes Points","color":"#000000","shield_name":"Boost Sole","booster_name":"Ultraboost Launch","description":"Impossible is Nothing — three stripes that define sport and culture."},
    "music":            {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancelling","booster_name":"Drop Surge","description":"A universe built on rhythm, bars, and raw cultural resonance."},
    "kpop":             {"currency":"Fancash","color":"#FF6699","shield_name":"Fan Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and undeniable charisma."},
    "ancient rome":     {"currency":"Denarii","color":"#B22222","shield_name":"Testudo Formation","booster_name":"Cavalry Charge","description":"The eternal city's iron legions built the greatest empire the world has ever seen."},
    "vikings":          {"currency":"Silver Hack","color":"#4A4A8A","shield_name":"Shieldwall","booster_name":"Berserker Rush","description":"Norse warriors who crossed uncharted seas and carved history with axes."},
}

def get_smart_fallback(theme):
    t = theme.lower().strip()
    # Exact match first
    if t in HARD_FALLBACKS:
        return HARD_FALLBACKS[t]
    # Partial match
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key:
            return data
    # Generic domain match
    if any(w in t for w in ("game","gaming","rpg","fps","moba")):
        return {"currency":"Gold","color":"#FFD700","shield_name":"Barrier Shield","booster_name":"Phase Dash","description":"An infinite digital universe where skill and legend are born."}
    if any(w in t for w in ("anime","manga")):
        return {"currency":"Ryo","color":"#FF4500","shield_name":"Armament Haki","booster_name":"Body Flicker","description":"A world of extraordinary power, honour, and relentless destiny."}
    if any(w in t for w in ("sport","league","cup","championship","team")):
        return {"currency":"Trophy Points","color":"#FFD700","shield_name":"Iron Defense","booster_name":"Turbo Sprint","description":"The ultimate competitive arena where legends are made."}
    if any(w in t for w in ("fashion","brand","wear","style","cloth","retail","shop")):
        return {"currency":"Style Credits","color":"#FF69B4","shield_name":"Signature Drip","booster_name":"Trend Surge","description":"Where identity becomes art and every fit tells a story."}
    # Last resort
    return {"currency":"Titan Shards","color":"#00FFCC","shield_name":"Kinetic Barrier","booster_name":"Void Dash","description":"A realm of boundless power and infinite possibility."}

# ── Main resolver ─────────────────────────────────────────────────────────────
REQUIRED_KEYS = ["currency", "color", "shield_name", "booster_name", "description"]

# Fixed effect descriptions — these NEVER change regardless of universe
SHIELD_EFFECT = "Negates any debt that was earned."
BOOSTER_EFFECT = "Grants a 3× multiplier on all mission rewards."

def resolve_universe(theme, model):
    data = None

    # 1. Try AI
    if model is not None:
        try:
            prompt = LORE_PROMPT.format(theme=theme)
            response = model.generate_content(prompt)
            raw = response.text.strip() if response.text else ""
            parsed = extract_json(raw)
            if parsed and all(k in parsed for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", parsed.get("color", "")):
                    parsed["color"] = "#FFD700"
                data = parsed
        except Exception:
            pass

    # 2. Fallback if AI failed
    if not data:
        data = get_smart_fallback(theme)

    # 3. ALWAYS inject fixed effect descriptions (never let AI override these)
    data["shield_effect"] = SHIELD_EFFECT
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
        background: #050505 !important; color: white;
        font-family: 'Space Mono', monospace;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent !important; }
    #MainMenu, footer { visibility: hidden; }
    .gw-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(60px, 12vw, 120px);
        text-align: center;
        background: linear-gradient(135deg, #FFD700, #FF8C00, #FF3C3C);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; letter-spacing: 6px; line-height: 1;
    }
    .gw-sub {
        text-align: center; font-size: 12px; color: #555;
        letter-spacing: 3px; text-transform: uppercase; margin-bottom: 36px;
    }
    .gw-card {
        background: rgba(12,12,12,0.97);
        border: 1px solid rgba(255,215,0,0.12);
        border-radius: 20px; padding: 40px;
    }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
    .chip {
        background: rgba(255,215,0,0.07); border: 1px solid rgba(255,215,0,0.18);
        border-radius: 99px; padding: 4px 12px;
        font-size: 11px; color: #777; letter-spacing: 1px;
    }
    div.stButton > button {
        border: 3px solid #FFD700 !important;
        background: #000 !important; color: white !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 20px !important; letter-spacing: 3px !important;
        padding: 16px !important; border-radius: 12px !important;
        width: 100%; transition: all 0.3s;
    }
    div.stButton > button:hover { background: rgba(255,215,0,0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="gw-title">INFINITEVERSE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gw-sub">⚡ Choose any universe. Any world. Zero limits.</p>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="gw-card">', unsafe_allow_html=True)

        name_input = st.text_input("YOUR CHAMPION NAME", placeholder="What are you called?", key="gw_name")
        theme_input = st.text_input(
            "YOUR UNIVERSE",
            placeholder="Minecraft · One Piece · F1 · Dead by Daylight · Vogue · anything...",
            key="gw_theme"
        )

        examples = ["Minecraft","One Piece","Formula 1","Dead by Daylight",
                    "Harry Potter","NBA","Roblox","Dune","Streetwear","Ancient Rome",
                    "K-Pop","Valorant","Vikings","Nike"]
        st.markdown(
            '<div class="chip-row">' +
            "".join(f'<span class="chip">{e}</span>' for e in examples) +
            '</div><br>',
            unsafe_allow_html=True
        )

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name.")
            elif not theme_input.strip():
                st.error("Choose a universe — anything works.")
            else:
                with st.spinner(f"🌐 Loading {theme_input.upper()} lore..."):
                    world_data = resolve_universe(theme_input.strip(), get_model())
                st.session_state.user_name = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color", "#FFD700")
                st.session_state.user_theme = theme_input.strip()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP (post-gateway)
# ─────────────────────────────────────────────────────────────────────────────
C = st.session_state.vibe_color  # active theme color shorthand

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {{
    background: #050505 !important; color: white; font-family: 'Space Mono', monospace;
}}
[data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent !important; }}
[data-testid="stSidebar"] {{ background: #080808 !important; }}
#MainMenu, footer {{ visibility: hidden; }}

@keyframes titan-pulse {{
    0%   {{ box-shadow: 0 0 20px {C}, inset 0 0 10px {C}; border-color: {C}; }}
    50%  {{ box-shadow: 0 0 80px {C}, inset 0 0 40px {C}; border-color: #FFF; }}
    100% {{ box-shadow: 0 0 20px {C}, inset 0 0 10px {C}; border-color: {C}; }}
}}
div.stButton > button {{
    border: 8px dashed {C} !important;
    background: #000 !important; color: white !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 28px !important; letter-spacing: 4px !important;
    padding: 50px 30px !important; border-radius: 40px !important;
    animation: titan-pulse 2.5s infinite ease-in-out !important;
    width: 100%; text-transform: uppercase; transition: transform 0.3s; margin-bottom: 20px;
}}
div.stButton > button:hover {{ transform: scale(1.02); }}
.metric-card {{
    background: rgba(20,20,20,0.95); border: 2px solid {C};
    padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 12px;
}}
.shop-card {{
    border: 3px solid {C}; padding: 24px;
    border-radius: 18px; background: rgba(10,10,10,0.9); margin-bottom: 12px;
}}
</style>
""", unsafe_allow_html=True)

wd = st.session_state.world_data
currency = wd.get("currency", "Credits")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>⚡ TITAN HUB</h1>", unsafe_allow_html=True)
    st.write(f"**CHAMPION:** {st.session_state.user_name.upper()}")
    st.write(f"**UNIVERSE:** {st.session_state.user_theme}")
    st.write(f"**RANK:** {st.session_state.sub_tier.upper()}")

    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C};margin:0'>{st.session_state.gold:.2f}</div>
        <div style='font-size:10px;color:#555;letter-spacing:2px'>{currency.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.markdown("**👑 ELITE ACTIVATION**")
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"
        st.session_state.sub_multiplier = 3
        st.success("ELITE STATUS SECURED!")
        st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    if st.button("🚀 MISSION HUB", key="nav_hub"): st.session_state.view = "main"; st.rerun()
    if st.button("🛒 ARSENAL", key="nav_shop"): st.session_state.view = "shop"; st.rerun()

    st.write("---")
    st.markdown("**🌐 SWITCH UNIVERSE**")
    new_theme = st.text_input("New universe:", placeholder="Try anything...", key="switch_theme")
    if st.button("🔄 WARP", key="warp_btn"):
        if new_theme.strip():
            with st.spinner(f"Warping to {new_theme}..."):
                world_data = resolve_universe(new_theme.strip(), get_model())
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
            <div style='font-size:11px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚔️ DEFENSE ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 10px'>
                {wd.get('shield_name','Shield').upper()}
            </h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};
                        padding:10px 12px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:2px'>Negates any debt that was earned.</div>
            </div>
            <div style='font-size:12px;color:#444;margin-bottom:14px'>Cost: <span style='color:{C}'>15 {currency}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"⚔️ ACQUIRE SHIELD · 15 {currency}", key="buy_shield"):
            if st.session_state.gold >= 15:
                st.session_state.gold -= 15
                st.success(f"⚔️ {wd.get('shield_name')} activated!")
            else:
                st.error("Not enough currency.")

    with col2:
        st.markdown(f"""
        <div class='shop-card'>
            <div style='font-size:11px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚡ SPEED ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 10px'>
                {wd.get('booster_name','Booster').upper()}
            </h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};
                        padding:10px 12px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:2px'>Grants a 3× multiplier on all mission rewards.</div>
            </div>
            <div style='font-size:12px;color:#444;margin-bottom:14px'>Cost: <span style='color:{C}'>25 {currency}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"⚡ ACQUIRE BOOSTER · 25 {currency}", key="buy_booster"):
            if st.session_state.gold >= 25:
                st.session_state.gold -= 25
                st.session_state.sub_multiplier = 3
                st.success(f"⚡ {wd.get('booster_name')} engaged!")
            else:
                st.error("Not enough currency.")

# ── MISSION HUB VIEW ──────────────────────────────────────────────────────────
else:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        reward = 1.0 * st.session_state.sub_multiplier
        mult_tag = f" ×{st.session_state.sub_multiplier}" if st.session_state.sub_multiplier > 1 else ""

        st.markdown(f"""
        <div style='text-align:center;background:rgba(20,20,20,0.8);
                    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
                    padding:20px;margin-bottom:20px'>
            <div style='font-size:11px;color:#444;letter-spacing:2px'>MISSION REWARD</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:52px;color:{C}'>{reward:.1f} {currency}{mult_tag}</div>
            <div style='font-size:11px;color:#333'>per completed 1-minute mission</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("▶  START 1-MINUTE MISSION", key="start_mission"):
            bar = st.progress(0)
            status = st.empty()
            for i in range(60):
                time.sleep(1)
                bar.progress((i + 1) / 60)
                status.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#666'>SYNCHRONIZING: {i+1}s / 60s</p>", unsafe_allow_html=True)
            st.session_state.pending_gold = reward
            st.session_state.needs_verification = True
            st.rerun()

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
            st.session_state.gold += earned
            st.session_state.total_missions += 1
            st.session_state.needs_verification = False
            st.session_state.pending_gold = 0.0
            st.balloons()
            st.success(f"✅ VERIFIED. +{earned:.1f} {currency} added to your balance.")
            time.sleep(1)
            st.rerun()
