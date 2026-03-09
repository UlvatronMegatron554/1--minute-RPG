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
LORE_PROMPT = """You are a universe data encoder. Return ONLY a raw JSON object — no explanation, no markdown, no code fences, nothing else.

For the universe: "{theme}"

Return exactly this structure:
{{
  "currency": "the canonical in-universe currency or reward",
  "color": "#RRGGBB hex color most iconic to this universe",
  "shield_name": "the most iconic defensive ability or item (2-4 words)",
  "booster_name": "the most iconic speed or movement ability (2-4 words)",
  "shield_lore": "one sentence of authentic lore about this defense",
  "booster_lore": "one sentence of authentic lore about this movement ability",
  "description": "one punchy sentence describing this universe's essence"
}}

Example for "Minecraft":
{{"currency": "Emeralds", "color": "#00AA00", "shield_name": "Netherite Armor", "booster_name": "Ender Pearl Warp", "shield_lore": "Forged from ancient debris in the Nether, Netherite is virtually indestructible.", "booster_lore": "Teleportation via thrown ender pearls, instant relocation across the world.", "description": "A boundless world of blocks where creativity and survival collide."}}

Now return ONLY the JSON for "{theme}":"""

# ── Smart domain fallbacks ─────────────────────────────────────────────────────
DOMAIN_FALLBACKS = [
    (("football","soccer","nfl","nba","mlb","nhl","basketball","baseball","tennis",
      "golf","cricket","rugby","f1","formula","racing","nascar","mma","ufc","boxing","sports"),
     {"currency":"Trophy Points","color":"#FFD700","shield_name":"Iron Defense","booster_name":"Turbo Sprint",
      "shield_lore":"The ultimate defensive stance used by champions the world over.",
      "booster_lore":"Explosive acceleration that leaves every opponent behind.",
      "description":"The ultimate competitive arena where legends are made."}),

    (("anime","manga","one piece","naruto","bleach","dragon ball","attack on titan",
      "demon slayer","jujutsu","my hero","hunter","fullmetal","sword art","fairy tail"),
     {"currency":"Ryo","color":"#FF4500","shield_name":"Armament Haki","booster_name":"Body Flicker",
      "shield_lore":"Hardening of spirit into an impenetrable aura of combat energy.",
      "booster_lore":"Movement so fast the human eye cannot track its path.",
      "description":"A world of extraordinary power, honour, and relentless destiny."}),

    (("minecraft","roblox","fortnite","valorant","league","apex","overwatch","cod",
      "gta","zelda","mario","pokemon","skyrim","elden","souls","dead by daylight",
      "dbd","among us","fall guys","terraria","stardew","game","gaming"),
     {"currency":"Gold Coins","color":"#00AA00","shield_name":"Barrier Shield","booster_name":"Phase Dash",
      "shield_lore":"A protective barrier forged from the world's deepest energy reserves.",
      "booster_lore":"Instant blink across space, leaving only afterimages behind.",
      "description":"An infinite digital universe where skill and strategy reign supreme."}),

    (("fashion","clothing","style","brand","retail","luxury","streetwear",
      "nike","adidas","gucci","supreme","vans","off-white","zara","h&m"),
     {"currency":"Style Credits","color":"#FF69B4","shield_name":"Signature Drip","booster_name":"Trend Surge",
      "shield_lore":"A curated aesthetic armour that commands attention in any room.",
      "booster_lore":"Riding the cultural wave at peak momentum and maximum visibility.",
      "description":"Where identity becomes art and every fit tells a story."}),

    (("book","novel","fantasy","sci-fi","scifi","harry potter","lord of the rings",
      "dune","witcher","tolkien","marvel","dc","comics","star wars","batman","superman"),
     {"currency":"Arcane Tokens","color":"#9B59B6","shield_name":"Arcane Ward","booster_name":"Dimensional Step",
      "shield_lore":"An ancient ward woven from the very fabric of pure concentrated magic.",
      "booster_lore":"A fold in space that collapses impossible distances to nothing.",
      "description":"A realm where legends echo across time and worlds collide."}),

    (("music","rap","hiphop","hip-hop","pop","rock","jazz","edm","kpop","k-pop",
      "artist","band","album","concert","spotify","playlist"),
     {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancel","booster_name":"Drop Surge",
      "shield_lore":"Pure sonic energy condensed into an impenetrable audio shield.",
      "booster_lore":"The bass drop that launches you forward at the speed of sound.",
      "description":"A universe built on rhythm, bars, and cultural resonance."}),

    (("history","ancient","rome","egypt","greek","medieval","viking","samurai",
      "war","military","ww2","napoleon","empire","civilization"),
     {"currency":"Denarii","color":"#B22222","shield_name":"Testudo Formation","booster_name":"Cavalry Charge",
      "shield_lore":"Overlapping shields locked together into an impenetrable iron tortoise.",
      "booster_lore":"A thundering wall of horses and steel that breaks any battle line.",
      "description":"The rise and fall of civilisations written in blood and glory."}),
]

ULTIMATE_FALLBACK = {
    "currency": "Titan Shards", "color": "#00FFCC",
    "shield_name": "Kinetic Barrier", "booster_name": "Void Dash",
    "shield_lore": "A force field of concentrated kinetic energy.",
    "booster_lore": "A burst of velocity that bends local spacetime.",
    "description": "A realm of boundless power and infinite possibility."
}

def get_smart_fallback(theme):
    t = theme.lower()
    for keywords, data in DOMAIN_FALLBACKS:
        if any(kw in t for kw in keywords):
            return data
    return ULTIMATE_FALLBACK

# ── Main resolver ─────────────────────────────────────────────────────────────
REQUIRED_KEYS = ["currency", "color", "shield_name", "booster_name",
                 "shield_lore", "booster_lore", "description"]

def resolve_universe(theme, model):
    if model is not None:
        try:
            prompt = LORE_PROMPT.format(theme=theme)
            response = model.generate_content(prompt)
            raw = response.text.strip() if response.text else ""
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                # Validate hex color
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color", "")):
                    data["color"] = "#FFD700"
                return data
        except Exception:
            pass
    return get_smart_fallback(theme)

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
        st.markdown(f"<div class='shop-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px'>{wd.get('shield_name','Shield').upper()}</h3>", unsafe_allow_html=True)
        st.write(f"_{wd.get('shield_lore','Legendary protection.')}_")
        st.write("**EFFECT:** Negates incoming debt")
        if st.button(f"ACQUIRE · 15 {currency}", key="buy_shield"):
            if st.session_state.gold >= 15:
                st.session_state.gold -= 15
                st.success(f"⚔️ {wd.get('shield_name')} activated!")
            else:
                st.error("Not enough currency.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='shop-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px'>{wd.get('booster_name','Booster').upper()}</h3>", unsafe_allow_html=True)
        st.write(f"_{wd.get('booster_lore','Pure velocity unleashed.')}_")
        st.write("**EFFECT:** 3× reward multiplier")
        if st.button(f"ACQUIRE · 25 {currency}", key="buy_booster"):
            if st.session_state.gold >= 25:
                st.session_state.gold -= 25
                st.session_state.sub_multiplier = 3
                st.success(f"⚡ {wd.get('booster_name')} engaged!")
            else:
                st.error("Not enough currency.")
        st.markdown("</div>", unsafe_allow_html=True)

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
