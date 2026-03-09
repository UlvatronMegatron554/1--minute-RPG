import streamlit as st
import anthropic
import time, json, re

# ─────────────────────────────────────────────────────────────────────────────
# TITAN OMNIVERSE v5.0 — INFINITE POWER GATEWAY EDITION
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="TITAN OMNIVERSE", page_icon="⚡", layout="wide")

SHIELD_EFFECT  = "Negates any debt that was earned."
BOOSTER_EFFECT = "Grants a 3× multiplier on all mission rewards."

DEFAULT_UNIVERSE_NAME = "INFINITE POWER"
DEFAULT_UNIVERSE = {
    "currency": "Titan Shards",
    "color": "#FFD700",
    "shield_name": "Infinite Barrier",
    "booster_name": "Limitless Surge",
    "description": "No limits. No boundaries. Pure unstoppable power.",
    "shield_effect": SHIELD_EFFECT,
    "booster_effect": BOOSTER_EFFECT,
}

def get_claude_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except Exception:
        return None

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

LORE_PROMPT = """You are an expert on every game, anime, sport, brand, show, movie, book, music genre, fashion brand, and cultural phenomenon that exists.

A user has chosen the universe: "{theme}"

Return ONLY a single raw JSON object with no explanation, no markdown, no code fences, nothing else.

Rules:
- "currency": The EXACT in-universe currency or most fitting value unit. Ultra-specific — never generic "Credits" or "Points" unless that franchise literally uses those words.
- "color": The single most ICONIC hex color for this universe — use the exact brand/logo/title screen color:
  Super Smash Bros=#E4000F, Mario=#E52521, Sonic=#0057A8, Minecraft=#5D9E35, Fortnite=#BEFF00, Roblox=#E8272A, Pokemon=#FFCB05, Valorant=#FF4655, One Piece=#E8372B, Naruto=#FF6600, Dragon Ball=#FF8C00, Demon Slayer=#22AA44, JJK=#6600CC, Bleach=#000000, F1=#FF1801, NBA=#EE6730, NFL=#013369, FIFA=#326B2E, Star Wars=#FFE81F, Marvel=#ED1D24, DC=#0476F2, Harry Potter=#740001, Skyrim=#C0C0C0, Elden Ring=#C8A951, GTA=#F4B000, Halo=#00B4D8, Dead by Daylight=#8B0000, Among Us=#C51111, Apex=#DA292A, Nike=#111111, Adidas=#000000, Supreme=#FF0000, Spotify=#1DB954, Netflix=#E50914.
  For anything else: use the dominant color from that franchise logo or title card.
- "shield_name": The most iconic DEFENSIVE item, armor, or technique. 100% specific.
- "booster_name": The most iconic SPEED or MOVEMENT ability. 100% specific.
- "description": One punchy sentence (max 12 words) capturing the soul of this universe.

Return exactly:
{{"currency": "...", "color": "#RRGGBB", "shield_name": "...", "booster_name": "...", "description": "..."}}"""

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

REQUIRED_KEYS = ["currency", "color", "shield_name", "booster_name", "description"]

def resolve_universe(theme):
    if not theme.strip():
        return DEFAULT_UNIVERSE.copy()
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

if "gold" not in st.session_state:
    st.session_state.update({
        "user_name": None, "gold": 10.0, "xp": 0, "level": 1,
        "world_data": {}, "user_theme": "",
        "view": "main", "pending_gold": 0.0, "needs_verification": False,
        "vibe_color": "#FFD700", "sub_tier": "Free", "sub_multiplier": 1,
        "total_missions": 0, "bg_color": "#050505",
        "feedback_list": [], "micro_timer_seconds": 30,
    })

# ─────────────────────────────────────────────────────────────────────────────
# 🌌 GATEWAY SCREEN v5.0 — INFINITE POWER EDITION
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_name is None:

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: #000008 !important;
        overflow-x: hidden;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
    .block-container { padding: 0 1rem !important; max-width: 100% !important; }

    /* ── ANIMATED RADIAL GLOW BACKGROUND — works within Streamlit ── */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 70% 50% at 10% 15%,  rgba(255,215,0,0.18) 0%, transparent 55%),
            radial-gradient(ellipse 55% 45% at 92% 8%,   rgba(255,60,60,0.14)  0%, transparent 55%),
            radial-gradient(ellipse 65% 45% at 50% 95%,  rgba(0,212,255,0.14)  0%, transparent 55%),
            radial-gradient(ellipse 45% 35% at 85% 65%,  rgba(155,89,182,0.12) 0%, transparent 55%),
            radial-gradient(ellipse 40% 30% at 15% 75%,  rgba(0,255,136,0.10)  0%, transparent 55%),
            #000008 !important;
        animation: bg-breathe 10s ease-in-out infinite alternate !important;
    }
    @keyframes bg-breathe {
        0%   { filter: brightness(1.0) saturate(1.0); }
        50%  { filter: brightness(1.15) saturate(1.2); }
        100% { filter: brightness(1.0) saturate(1.0); }
    }

    /* Grid overlay on page */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image:
            linear-gradient(rgba(255,215,0,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,215,0,0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none; z-index: 0;
    }

    /* Scan line — horizontal sweep */
    .scanline-wrap { width: 100%; height: 3px; overflow: hidden; margin-bottom: 8px; }
    .scanline {
        width: 50%; height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,215,0,0.9), transparent);
        animation: scan 2.5s linear infinite;
        box-shadow: 0 0 16px rgba(255,215,0,0.5);
    }
    @keyframes scan { 0% { transform: translateX(-100%); } 100% { transform: translateX(300%); } }

    /* Star field */
    .star-field {
        width: 100%; height: 80px; position: relative;
        background-image:
            radial-gradient(1.5px 1.5px at 8%  40%, rgba(255,255,255,0.95) 0%, transparent 100%),
            radial-gradient(1px   1px   at 20% 70%, rgba(255,255,255,0.80) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 35% 25%, rgba(255,255,255,0.90) 0%, transparent 100%),
            radial-gradient(1px   1px   at 52% 80%, rgba(255,255,255,0.75) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 67% 35%, rgba(255,255,255,0.95) 0%, transparent 100%),
            radial-gradient(1px   1px   at 80% 60%, rgba(255,255,255,0.80) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 93% 20%, rgba(255,255,255,0.90) 0%, transparent 100%),
            radial-gradient(2px   2px   at 15% 55%, rgba(255,215,0,1.0)    0%, transparent 100%),
            radial-gradient(2px   2px   at 72% 45%, rgba(0,212,255,1.0)    0%, transparent 100%),
            radial-gradient(2px   2px   at 44% 75%, rgba(255,100,100,1.0)  0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 58% 15%, rgba(255,255,255,0.85) 0%, transparent 100%),
            radial-gradient(1px   1px   at 3%  80%, rgba(255,255,255,0.70) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 88% 85%, rgba(255,255,255,0.90) 0%, transparent 100%);
        animation: twinkle 3.5s ease-in-out infinite alternate;
        margin-bottom: 12px;
    }
    @keyframes twinkle { 0% { opacity:0.4; } 100% { opacity:1.0; } }

    /* Badge */
    .top-badge {
        background: rgba(255,215,0,0.08);
        border: 1px solid rgba(255,215,0,0.35);
        border-radius: 99px; padding: 7px 22px;
        font-family: 'Space Mono', monospace;
        font-size: 11px; letter-spacing: 3px;
        color: #FFD700; text-transform: uppercase;
        text-align: center; margin: 0 auto 20px;
        display: table;
        animation: badge-glow 3s ease-in-out infinite alternate;
    }
    @keyframes badge-glow {
        0%   { box-shadow: 0 0 10px rgba(255,215,0,0.2); }
        100% { box-shadow: 0 0 35px rgba(255,215,0,0.55); }
    }

    /* Main title */
    .gw-main-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(72px, 14vw, 150px);
        text-align: center; letter-spacing: 8px; line-height: 0.88;
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 30%, #FF3C3C 65%, #CC00FF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: title-glow 4s ease-in-out infinite alternate;
        margin-bottom: 8px;
    }
    @keyframes title-glow {
        0%   { filter: drop-shadow(0 0 15px rgba(255,215,0,0.4)); }
        100% { filter: drop-shadow(0 0 55px rgba(255,140,0,0.7)); }
    }

    .gw-subtitle {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(11px, 1.8vw, 17px);
        text-align: center; letter-spacing: 5px;
        color: rgba(255,255,255,0.45);
        text-transform: uppercase; margin-bottom: 20px;
    }

    /* Feature pills */
    .features-row { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin: 12px 0 24px; }
    .feature-pill {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 99px; padding: 6px 14px;
        font-family: 'Space Mono', monospace;
        font-size: 11px; color: rgba(255,255,255,0.6);
        letter-spacing: 1px;
    }
    .feature-pill span { margin-right: 5px; }

    /* Stats */
    .stats-ticker { display:flex; gap:28px; justify-content:center; margin-bottom:24px; flex-wrap:wrap; }
    .stat-item { text-align:center; animation: stat-float 3s ease-in-out infinite alternate; }
    .stat-item:nth-child(2) { animation-delay:-1s; }
    .stat-item:nth-child(3) { animation-delay:-2s; }
    @keyframes stat-float { 0%{transform:translateY(0)} 100%{transform:translateY(-6px)} }
    .stat-num { font-family:'Bebas Neue',sans-serif; font-size:38px; color:#FFD700; line-height:1; }
    .stat-label { font-family:'Space Mono',monospace; font-size:9px; color:#555; letter-spacing:2px; text-transform:uppercase; }

    /* Divider */
    .gw-divider { width:100%; height:1px; background:linear-gradient(90deg,transparent,rgba(255,215,0,0.35),transparent); margin:4px 0 24px; }

    /* HOW IT WORKS — big, clear, impossible to miss */
    .how-it-works { width:100%; margin-top:28px; }
    .how-title {
        font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:4px;
        color:#FFD700; text-align:center; margin-bottom:16px;
        text-shadow: 0 0 20px rgba(255,215,0,0.5);
    }
    .how-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .how-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 16px; padding: 20px 18px;
        transition: all 0.3s;
    }
    .how-card:hover { background:rgba(255,215,0,0.08); border-color:rgba(255,215,0,0.4); }
    .how-icon { font-size:28px; margin-bottom:10px; display:block; }
    .how-card-title {
        font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:2px;
        color:#FFD700; margin-bottom:8px;
    }
    .how-card-desc {
        font-family:'Space Mono',monospace; font-size:12px;
        color:rgba(255,255,255,0.7); line-height:1.7;
    }

    /* Chips */
    .chip-section-label { font-family:'Space Mono',monospace; font-size:10px; color:#555; letter-spacing:2px; text-transform:uppercase; margin:14px 0 8px; }
    .chip-row { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:6px; }
    .chip {
        background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.18);
        border-radius:99px; padding:4px 12px; font-size:11px; color:#777;
        font-family:'Space Mono',monospace; letter-spacing:1px;
    }

    /* Hint */
    .default-hint { font-family:'Space Mono',monospace; font-size:10px; color:#444; font-style:italic; margin-top:6px; }
    .default-hint strong { color:#FFD700; }

    /* Streamlit input overrides */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,215,0,0.2) !important;
        border-radius: 10px !important; color: white !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 14px !important; padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(255,215,0,0.6) !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.15) !important;
    }
    .stTextInput label {
        font-family:'Space Mono',monospace !important; font-size:11px !important;
        letter-spacing:3px !important; color:#666 !important; text-transform:uppercase !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #FFD700, #FF8C00) !important;
        border: none !important; color: #000 !important;
        font-family:'Bebas Neue',sans-serif !important; font-size:24px !important;
        letter-spacing:4px !important; padding:18px !important;
        border-radius:14px !important; width:100% !important;
        box-shadow: 0 0 30px rgba(255,215,0,0.35) !important;
        transition: all 0.3s !important; margin-top:10px !important;
    }
    div.stButton > button:hover {
        transform:scale(1.02) !important;
        box-shadow:0 0 60px rgba(255,215,0,0.6) !important;
    }
    </style>

    <div class="scanline-wrap"><div class="scanline"></div></div>
    <div class="star-field"></div>
    <div class="top-badge">⚡ 30-Second RPG Study System · Any Universe · Zero Limits</div>
    <div class="gw-main-title">TITAN<br>OMNIVERSE</div>
    <div class="gw-subtitle">Infiniteverse · Study RPG · Unlock Your Power</div>
    <div class="features-row">
        <div class="feature-pill"><span>🎮</span>Pick ANY Universe</div>
        <div class="feature-pill"><span>⏱</span>30-Second Missions</div>
        <div class="feature-pill"><span>💰</span>Earn Real Rewards</div>
        <div class="feature-pill"><span>🔥</span>Study Like a Champion</div>
        <div class="feature-pill"><span>🌈</span>Fully Customizable</div>
        <div class="feature-pill"><span>⚡</span>Powered by AI</div>
    </div>
    <div class="stats-ticker">
        <div class="stat-item"><div class="stat-num">∞</div><div class="stat-label">Universes</div></div>
        <div class="stat-item"><div class="stat-num">30s</div><div class="stat-label">To Start</div></div>
        <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Free</div></div>
        <div class="stat-item"><div class="stat-num">0</div><div class="stat-label">Excuses</div></div>
    </div>
    <div class="gw-divider"></div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        name_input = st.text_input("⚡ Champion Name", placeholder="What are you called?", key="gw_name")
        theme_input = st.text_input(
            "🌌 Your Universe",
            placeholder="e.g. Minecraft, Naruto, F1, Nike, Ancient Rome, Germa 66...",
            key="gw_theme"
        )
        st.markdown("""
        <p class="default-hint">💡 Leave empty for default universe: <strong>INFINITE POWER</strong></p>
        <p class="default-hint" style="color:#555;margin-top:4px">
            ✨ Be as specific or creative as you want! Merge universes, invent custom worlds,
            or go deep — <strong style="color:#FFD700">"Germa 66 meets Halo"</strong>,
            <strong style="color:#FFD700">"Dark Souls Ninja"</strong>,
            <strong style="color:#FFD700">"Cyberpunk Basketball"</strong> — anything goes.
        </p>
        <div class="chip-section-label">⚡ Quick picks</div>
        <div class="chip-row">
            <span class="chip">Minecraft</span><span class="chip">Super Smash Bros</span>
            <span class="chip">One Piece</span><span class="chip">Formula 1</span>
            <span class="chip">Dead by Daylight</span><span class="chip">Pokemon</span>
            <span class="chip">Naruto</span><span class="chip">NBA</span>
            <span class="chip">Roblox</span><span class="chip">Harry Potter</span>
            <span class="chip">Valorant</span><span class="chip">Nike</span>
            <span class="chip">K-Pop</span><span class="chip">Ancient Rome</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name to begin.")
            else:
                theme_val    = theme_input.strip()
                display_name = theme_val if theme_val else DEFAULT_UNIVERSE_NAME
                with st.spinner(f"🌌 Loading {display_name.upper()}..."):
                    world_data = resolve_universe(theme_val)
                st.session_state.user_name  = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color", "#FFD700")
                st.session_state.user_theme = display_name
                st.rerun()

        st.markdown("""
        <div class="how-it-works">
            <div class="how-title">⚡ HOW IT WORKS</div>
            <div class="how-grid">
                <div class="how-card">
                    <span class="how-icon">🌌</span>
                    <div class="how-card-title">PICK YOUR UNIVERSE</div>
                    <div class="how-card-desc">Any game, anime, sport, brand, or custom world — the AI builds it for you instantly with the perfect colors, currency and abilities.</div>
                </div>
                <div class="how-card">
                    <span class="how-icon">⏱</span>
                    <div class="how-card-title">START A MISSION</div>
                    <div class="how-card-desc">30 seconds or 1 minute. Study, work, grind. Every second you put in earns you real in-universe currency.</div>
                </div>
                <div class="how-card">
                    <span class="how-icon">📸</span>
                    <div class="how-card-title">PROVE YOUR WORK</div>
                    <div class="how-card-desc">Upload proof to The Tribunal — a screenshot, photo, or notes. Real effort only. No shortcuts, no cheating.</div>
                </div>
                <div class="how-card">
                    <span class="how-icon">🏆</span>
                    <div class="how-card-title">LEVEL UP</div>
                    <div class="how-card-desc">Spend your earnings on abilities, unlock Elite status with TITAN10, and dominate your universe. Study = power.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
C        = st.session_state.vibe_color
wd       = st.session_state.world_data
currency = wd.get("currency", "Credits")
BG       = st.session_state.get("bg_color", "#050505")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important; color: white; font-family: 'Space Mono', monospace;
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
    border: 8px dashed {C} !important; background: #000 !important; color: white !important;
    font-family: 'Bebas Neue', sans-serif !important; font-size: 28px !important;
    letter-spacing: 4px !important; padding: 50px 30px !important; border-radius: 40px !important;
    animation: titan-pulse 2.5s infinite ease-in-out !important;
    width: 100%; text-transform: uppercase; transition: transform 0.3s; margin-bottom: 20px;
}}
div.stButton > button:hover {{ transform: scale(1.02); }}
.metric-card {{ background: rgba(20,20,20,0.95); border: 2px solid {C}; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 12px; }}
.shop-card   {{ border: 3px solid {C}; padding: 24px; border-radius: 18px; background: rgba(10,10,10,0.9); margin-bottom: 12px; }}
.feedback-card {{ background: rgba(20,20,20,0.9); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; margin: 6px 0; font-size: 13px; color: #ccc; }}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>⚡ TITAN HUB</h1>", unsafe_allow_html=True)
    st.write(f"**CHAMPION:** {st.session_state.user_name.upper()}")
    st.write(f"**UNIVERSE:** {st.session_state.user_theme}")
    st.write(f"**RANK:** {st.session_state.sub_tier.upper()}")
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C};margin:0'>{st.session_state.gold:.2f}</div>
        <div style='font-size:10px;color:#555;letter-spacing:2px'>{currency.upper()}</div>
    </div>""", unsafe_allow_html=True)

    st.write("---")
    st.markdown("**👑 ELITE ACTIVATION**")
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "TITAN10" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3
        st.success("ELITE STATUS SECURED!"); st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    if st.button("🚀 MISSION HUB",  key="nav_hub"):      st.session_state.view = "main";     st.rerun()
    if st.button("🛒 ARSENAL",      key="nav_shop"):     st.session_state.view = "shop";     st.rerun()
    if st.button("💬 FEEDBACK",     key="nav_feedback"): st.session_state.view = "feedback"; st.rerun()

    st.write("---")
    st.markdown("**🎨 BACKGROUND COLOR**")
    new_bg = st.color_picker("", value=st.session_state.get("bg_color","#050505"), key="bg_picker", label_visibility="collapsed")
    if new_bg != st.session_state.get("bg_color","#050505"):
        st.session_state.bg_color = new_bg; st.rerun()

    st.markdown("**🌈 THEME COLOR**")
    new_theme_color = st.color_picker("", value=st.session_state.vibe_color, key="theme_picker", label_visibility="collapsed")
    if new_theme_color != st.session_state.vibe_color:
        st.session_state.vibe_color = new_theme_color; st.rerun()

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
    st.markdown("**🚨 FULL RESET**")
    reset_input = st.text_input("Type RESET to confirm:", key="reset_confirm_input", placeholder="RESET")
    if st.button("🚨 RESET ALL PROGRESS", key="reset_btn"):
        if reset_input.strip().upper() == "RESET":
            st.session_state.clear(); st.rerun()
        else:
            st.error("Type RESET in the box first.")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};
           font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>
    {st.session_state.user_theme.upper()}
</h1>
<p style='text-align:center;font-size:16px;color:#666;margin-top:4px'>
    {wd.get("description","A realm of infinite power.")}
</p>""", unsafe_allow_html=True)
st.markdown("---")

# ── FEEDBACK VIEW ─────────────────────────────────────────────────────────────
if st.session_state.view == "feedback":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💬 FEEDBACK PORTAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        feedback_type = st.selectbox("TYPE", ["💡 Feature Idea","🐛 Bug Report","🔥 This is fire!","😤 Needs fixing","💭 General Thought"], key="fb_type")
        feedback_text = st.text_area("YOUR MESSAGE", placeholder="Be as detailed as you want.", height=120, key="fb_text")
        feedback_name = st.text_input("YOUR NAME (optional)", placeholder="Anonymous", key="fb_name")
        if st.button("🚀 SUBMIT FEEDBACK", key="submit_fb"):
            if feedback_text.strip():
                st.session_state.feedback_list.append({
                    "type": feedback_type, "message": feedback_text.strip(),
                    "name": feedback_name.strip() or "Anonymous",
                    "universe": st.session_state.user_theme,
                    "time": time.strftime("%Y-%m-%d %H:%M"),
                })
                st.success("✅ FEEDBACK RECEIVED. Thank you, Champion. 🔥"); st.balloons()
            else:
                st.error("Write something first!")
        if st.session_state.feedback_list:
            st.markdown("---")
            for fb in reversed(st.session_state.feedback_list):
                st.markdown(f"<div class='feedback-card'><span style='color:{C}'>{fb['type']}</span> · <span style='color:#555;font-size:11px'>{fb['time']} · {fb['name']}</span><br>{fb['message']}</div>", unsafe_allow_html=True)

# ── SHOP VIEW ─────────────────────────────────────────────────────────────────
elif st.session_state.view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>MULTIVERSE ARSENAL</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class='shop-card'>
            <div style='font-size:10px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚔️ DEFENSE ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 12px'>{wd.get('shield_name','Shield').upper()}</h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:4px'>{SHIELD_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#444'>Cost: <span style='color:{C};font-weight:bold'>15 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚔️ ACQUIRE · 15 {currency}", key="buy_shield"):
            if st.session_state.gold >= 15: st.session_state.gold -= 15; st.success(f"⚔️ {wd.get('shield_name')} activated!")
            else: st.error("Not enough currency.")
    with col2:
        st.markdown(f"""<div class='shop-card'>
            <div style='font-size:10px;color:#555;letter-spacing:2px;margin-bottom:6px'>⚡ SPEED ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 12px'>{wd.get('booster_name','Booster').upper()}</h3>
            <div style='background:rgba(255,255,255,0.04);border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#555;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:14px;color:#ddd;margin-top:4px'>{BOOSTER_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#444'>Cost: <span style='color:{C};font-weight:bold'>25 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚡ ACQUIRE · 25 {currency}", key="buy_booster"):
            if st.session_state.gold >= 25: st.session_state.gold -= 25; st.session_state.sub_multiplier = 3; st.success(f"⚡ {wd.get('booster_name')} engaged!")
            else: st.error("Not enough currency.")

# ── MISSION HUB ───────────────────────────────────────────────────────────────
else:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        reward   = 1.0 * st.session_state.sub_multiplier
        mult_tag = f" ×{st.session_state.sub_multiplier}" if st.session_state.sub_multiplier > 1 else ""
        st.markdown(f"""
        <div style='text-align:center;background:rgba(20,20,20,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;margin-bottom:20px'>
            <div style='font-size:11px;color:#444;letter-spacing:2px'>MISSION REWARD</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:52px;color:{C};margin:6px 0'>{reward:.1f} {currency}{mult_tag}</div>
            <div style='font-size:11px;color:#333'>per completed mission</div>
        </div>""", unsafe_allow_html=True)

        # Micro timer
        st.markdown(f"""
        <div style='background:rgba(20,20,20,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:20px;margin-bottom:16px;text-align:center'>
            <div style='font-size:10px;color:#555;letter-spacing:2px;margin-bottom:8px'>⏱ MICRO TIMER</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:48px;color:{C}'>{st.session_state.micro_timer_seconds}s</div>
            <div style='font-size:11px;color:#444'>+30s per tap · max 6 minutes</div>
        </div>""", unsafe_allow_html=True)

        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            if st.button("➕ ADD 30s", key="add_30"):
                if st.session_state.micro_timer_seconds < 360: st.session_state.micro_timer_seconds += 30; st.rerun()
                else: st.warning("Max 6 minutes!")
        with tc2:
            if st.button("▶ START", key="start_micro"):
                secs = st.session_state.micro_timer_seconds
                bar = st.progress(0); status = st.empty()
                for i in range(secs):
                    time.sleep(1); bar.progress((i+1)/secs)
                    status.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:{C};font-size:20px'>{secs-i-1}s remaining</p>", unsafe_allow_html=True)
                st.session_state.micro_timer_seconds = 30
                st.success("✅ Micro session complete!"); time.sleep(1); st.rerun()
        with tc3:
            if st.button("🔄 RESET", key="reset_micro"):
                st.session_state.micro_timer_seconds = 30; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
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
        uploaded = st.file_uploader("PROOF OF LABOR:", key="proof_upload")
        if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT", key="submit_proof"):
            earned = st.session_state.pending_gold
            st.session_state.gold += earned; st.session_state.total_missions += 1
            st.session_state.needs_verification = False; st.session_state.pending_gold = 0.0
            st.balloons(); st.success(f"✅ VERIFIED. +{earned:.1f} {currency} added.")
            time.sleep(1); st.rerun()
