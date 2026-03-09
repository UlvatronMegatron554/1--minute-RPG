import streamlit as st
import google.generativeai as genai
import json, re, time, random

# ─────────────────────────────────────────────────────────────────────────────
# INFINITEVERSE GATEWAY  v2.0
# Works for ANY universe: games, anime, sports, brands, books, fashion — anything.
# ─────────────────────────────────────────────────────────────────────────────

MODEL_ID = "gemini-1.5-flash"

# ── Model init ────────────────────────────────────────────────────────────────
def get_model():
    try:
        key = st.secrets["GEMINI_KEY"]
        genai.configure(api_key=key)
        # Temperature 0.7: creative enough for lore, stable enough to not hallucinate
        return genai.GenerativeModel(
            MODEL_ID,
            generation_config={"temperature": 0.7, "max_output_tokens": 512}
        )
    except Exception as e:
        return None

# ── THE BULLETPROOF JSON EXTRACTOR ───────────────────────────────────────────
# This is the core fix. Gemini often wraps JSON in markdown code blocks,
# adds preamble text, or uses single quotes. This handles ALL of it.
def extract_json(raw_text: str) -> dict | None:
    if not raw_text:
        return None

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()

    # Attempt 1: direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Attempt 2: find first {...} block
    match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Attempt 3: fix single quotes → double quotes
    try:
        fixed = cleaned.replace("'", '"')
        return json.loads(fixed)
    except Exception:
        pass

    # Attempt 4: manual key extraction (last resort regex)
    result = {}
    for key in ["currency", "color", "shield_name", "booster_name",
                "shield_lore", "booster_lore", "description"]:
        pattern = rf'["\']?{key}["\']?\s*:\s*["\']([^"\']+)["\']'
        m = re.search(pattern, cleaned, re.IGNORECASE)
        if m:
            result[key] = m.group(1)
    return result if len(result) >= 4 else None

# ── THE PROMPT — engineered to never fail ────────────────────────────────────
# Key design decisions:
# 1. Tells the model EXACTLY what format we need (no deviation)
# 2. Gives a concrete example so it knows the expected quality bar
# 3. Does NOT ask it to avoid words (the scrubber was breaking things)
# 4. Asks for a valid hex color explicitly
# 5. Keeps it short — fewer tokens = less chance of weird formatting

LORE_PROMPT = """You are a universe data encoder. Return ONLY a raw JSON object with no explanation, no markdown, no code fences.

For the universe: "{theme}"

Return exactly this structure:
{{
  "currency": "the canonical in-universe currency or reward (e.g. Rings, Berries, Bottle Caps)",
  "color": "#RRGGBB hex color most iconic to this universe",
  "shield_name": "the most iconic defensive ability, item or technique (2-4 words)",
  "booster_name": "the most iconic speed/movement ability or technique (2-4 words)",
  "shield_lore": "one sentence of authentic lore about this defense",
  "booster_lore": "one sentence of authentic lore about this movement ability",
  "description": "one punchy sentence describing this universe's essence"
}}

Example for "Minecraft":
{{"currency": "Emeralds", "color": "#00AA00", "shield_name": "Netherite Armor", "booster_name": "Ender Pearl Warp", "shield_lore": "Forged from ancient debris in the Nether, Netherite is virtually indestructible.", "booster_lore": "Teleportation via thrown ender pearls — instant relocation across dimensions.", "description": "A boundless world of blocks where creativity and survival collide."}}

Now return ONLY the JSON for "{theme}":"""

# ── SMART FALLBACKS — contextual, not generic ─────────────────────────────────
# These are keyword-based intelligent fallbacks, grouped by domain.
# Still covers ~95% of cases if AI fails, but far more contextual than before.

DOMAIN_FALLBACKS = {
    # Sports
    ("football", "soccer", "nfl", "nba", "mlb", "nhl", "basketball", "baseball", "tennis",
     "golf", "cricket", "rugby", "f1", "formula", "racing", "nascar", "mma", "ufc", "boxing"): {
        "currency": "Trophy Points", "color": "#FFD700",
        "shield_name": "Iron Defense", "booster_name": "Turbo Sprint",
        "shield_lore": "The ultimate defensive stance used by champions.", 
        "booster_lore": "Explosive acceleration that leaves opponents behind.",
        "description": "The ultimate competitive arena where legends are made."
    },
    # Anime / Manga
    ("anime", "manga", "one piece", "naruto", "bleach", "dragon ball", "attack on titan",
     "demon slayer", "jujutsu", "my hero", "hunter", "fullmetal", "sword art"): {
        "currency": "Ryo", "color": "#FF4500",
        "shield_name": "Armament Haki", "booster_name": "Body Flicker",
        "shield_lore": "Hardening of spirit into an impenetrable combat aura.",
        "booster_lore": "Movement so fast the human eye cannot track it.",
        "description": "A world of extraordinary power, honor, and destiny."
    },
    # Gaming
    ("minecraft", "roblox", "fortnite", "valorant", "league", "apex", "overwatch",
     "cod", "gta", "zelda", "mario", "pokemon", "skyrim", "elden", "souls", "game"): {
        "currency": "Gold Coins", "color": "#00AA00",
        "shield_name": "Barrier Shield", "booster_name": "Phase Dash",
        "shield_lore": "A protective barrier forged from the world's core energy.",
        "booster_lore": "Instant blink across space, leaving afterimages behind.",
        "description": "An infinite digital universe where skill reigns supreme."
    },
    # Fashion / Retail / Lifestyle
    ("fashion", "clothing", "style", "brand", "retail", "luxury", "streetwear",
     "nike", "adidas", "gucci", "supreme", "vans", "off-white"): {
        "currency": "Style Credits", "color": "#FF69B4",
        "shield_name": "Signature Drip", "booster_name": "Trend Surge",
        "shield_lore": "A curated aesthetic armor that commands any room.",
        "booster_lore": "Riding the cultural wave at peak momentum.",
        "description": "Where identity becomes art and every fit tells a story."
    },
    # Books / Fantasy / Sci-Fi
    ("book", "novel", "fantasy", "sci-fi", "scifi", "harry potter", "lord of the rings",
     "dune", "witcher", "tolkien", "marvel", "dc", "comics", "star wars"): {
        "currency": "Arcane Tokens", "color": "#9B59B6",
        "shield_name": "Arcane Ward", "booster_name": "Dimensional Step",
        "shield_lore": "An ancient ward woven from the fabric of pure magic.",
        "booster_lore": "A fold in space that collapses distance to nothing.",
        "description": "A realm where legends echo across time and worlds collide."
    },
}

# Last resort — generic but better than the old one
ULTIMATE_FALLBACK = {
    "currency": "Titan Shards", "color": "#00FFCC",
    "shield_name": "Kinetic Barrier", "booster_name": "Void Dash",
    "shield_lore": "A force field of concentrated kinetic energy.",
    "booster_lore": "A burst of velocity that bends local spacetime.",
    "description": "A realm of boundless power and infinite possibility."
}

def get_smart_fallback(theme: str) -> dict:
    t = theme.lower()
    for keywords, data in DOMAIN_FALLBACKS.items():
        if any(kw in t for kw in keywords):
            return data
    return ULTIMATE_FALLBACK

# ── MAIN FUNCTION: resolve_universe ──────────────────────────────────────────
# Call this with any theme string. Returns a guaranteed valid world_data dict.
def resolve_universe(theme: str, model) -> dict:
    """
    Resolves any theme string into a complete world_data dict.
    Tries AI first, falls back gracefully if anything fails.
    Returns a dict guaranteed to have all required keys.
    """
    REQUIRED_KEYS = ["currency", "color", "shield_name", "booster_name",
                     "shield_lore", "booster_lore", "description"]

    # --- Attempt AI resolution ---
    if model is not None:
        try:
            prompt = LORE_PROMPT.format(theme=theme)
            response = model.generate_content(prompt)
            raw = response.text.strip() if response.text else ""
            data = extract_json(raw)

            if data and all(k in data for k in REQUIRED_KEYS):
                # Validate color format — fix if model returned a name instead of hex
                color = data.get("color", "")
                if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
                    data["color"] = "#FFD700"  # safe gold default
                return data

        except Exception as e:
            pass  # Fall through to smart fallback

    # --- Smart domain fallback ---
    return get_smart_fallback(theme)


# ── GATEWAY UI COMPONENT ─────────────────────────────────────────────────────
# Drop-in replacement for the original gateway screen.
def render_gateway():
    """
    Renders the world selection screen.
    Sets st.session_state.user_name, world_data, vibe_color, user_theme on success.
    """
    active_color = "#FFD700"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        background: #050505 !important;
        color: white;
        font-family: 'Space Mono', monospace;
    }}
    .gateway-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(60px, 12vw, 120px);
        text-align: center;
        background: linear-gradient(135deg, #FFD700, #FF8C00, #FF3C3C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 6px;
        line-height: 1;
        text-shadow: none;
    }}
    .gateway-sub {{
        text-align: center;
        font-size: 13px;
        color: #555;
        letter-spacing: 3px;
        margin-bottom: 40px;
        text-transform: uppercase;
    }}
    .gateway-card {{
        background: rgba(15,15,15,0.95);
        border: 1px solid rgba(255,215,0,0.15);
        border-radius: 20px;
        padding: 40px;
    }}
    .hint-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }}
    .hint-chip {{
        background: rgba(255,215,0,0.08);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 99px;
        padding: 4px 12px;
        font-size: 11px;
        color: #888;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="gateway-title">INFINITEVERSE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gateway-sub">Choose any universe. Any world. No limits.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="gateway-card">', unsafe_allow_html=True)

        name_input = st.text_input(
            "YOUR CHAMPION NAME",
            placeholder="What are you called?",
            key="gw_name"
        )

        theme_input = st.text_input(
            "YOUR UNIVERSE",
            placeholder="Minecraft · One Piece · F1 · Dead by Daylight · Vogue · anything...",
            key="gw_theme"
        )

        # Example chips
        examples = ["Minecraft", "One Piece", "Formula 1", "Dead by Daylight",
                    "Harry Potter", "NBA", "Roblox", "Dune", "Streetwear", "Ancient Rome"]
        chips_html = '<div class="hint-row">' + "".join(
            f'<span class="hint-chip">{e}</span>' for e in examples
        ) + "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name.")
            elif not theme_input.strip():
                st.error("Choose a universe — anything works.")
            else:
                with st.spinner(f"🌐 Extracting {theme_input.upper()} lore data..."):
                    model = get_model()
                    world_data = resolve_universe(theme_input.strip(), model)

                st.session_state.user_name = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color", "#FFD700")
                st.session_state.user_theme = theme_input.strip()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
