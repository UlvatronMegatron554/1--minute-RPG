import streamlit as st
import anthropic
import time, json, re, random

# ─────────────────────────────────────────────────────────────────────────────
# TITAN OMNIVERSE v8.0 — INFINITE OBSESSION EDITION
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="TITAN OMNIVERSE", page_icon="⚡", layout="wide")

SHIELD_EFFECT  = "Negates any debt that was earned."
BOOSTER_EFFECT = "Grants a 3× multiplier on all mission rewards."
DEFAULT_UNIVERSE_NAME = "INFINITE POWER"
DEFAULT_UNIVERSE = {
    "currency": "Titan Shards", "color": "#FFD700",
    "shield_name": "Infinite Barrier", "booster_name": "Limitless Surge",
    "description": "No limits. No boundaries. Pure unstoppable power.",
    "shield_effect": SHIELD_EFFECT, "booster_effect": BOOSTER_EFFECT,
    "shield_flavor": "An unbreakable wall forged from pure limitless energy.",
    "booster_flavor": "Surges you forward at speeds that defy all known physics.",
    "battle_style": "random",
}

# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSE SECRETS DATABASE
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSE_SECRETS = [
    "🤯 WAIT WHAT: You cannot hum while holding your nose closed. Try it. You literally just tried it.",
    "💀 REALITY CHECK: The CIA once tried to weaponize cats as spies. They spent $20 million. The first cat was immediately hit by a taxi.",
    "🌌 EXISTENCE CRISIS: There are more possible iterations of a game of chess than atoms in the observable universe. Every game ever played is essentially unique.",
    "🧠 BRAIN BREAK: Your brain is constantly hallucinating. What you see right now is a 0.1 second old prediction. You have never seen the present moment.",
    "⚡ TIMELINE SHOCK: Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid. Let that sink in.",
    "🔮 PHYSICS IS LYING: If you removed all empty space from every atom in every human on Earth, all 8 billion of us would fit inside a sugar cube.",
    "💫 SCALE DESTROYER: A teaspoon of neutron star material weighs 10 billion tons. One teaspoon. 10 BILLION TONS.",
    "🕳️ TIME IS FAKE: According to Einstein, time literally slows down the faster you move. Astronauts on the ISS age slightly slower than us. Time travel is real.",
    "🧬 YOU ARE MOSTLY EMPTY: You are 99.9999999% empty space. The atoms that make you up are almost entirely nothing. You are basically a ghost.",
    "🌊 THE SUN IS DELAYED: The light hitting your face right now left the Sun 8 minutes ago. You are always seeing the past. The Sun could explode and you wouldn't know for 8 minutes.",
    "🔥 FIRE ISN'T A THING: Fire is not matter. It has no mass. It is a chemical reaction — pure energy made visible. You cannot touch fire. You can only touch heat.",
    "🌍 EARTH IS FAKE ROUND: Earth is not a sphere. It bulges at the equator and is flattened at the poles. It's technically an oblate spheroid. Maps have been lying to you.",
    "💥 YOUR MEMORY IS FICTION: Every time you remember something, you are not replaying it. You are reconstructing it. And every reconstruction changes it slightly. Your memories are edited every single time.",
    "🧲 IMPOSSIBLE MATERIAL: Aerogel is 99.8% air. It looks like frozen smoke. It can support 4,000 times its own weight. It insulates so well you can hold a blowtorch on one side and touch the other.",
    "⏰ BIOLOGICAL HORROR: You have a second brain in your gut. It has 100 million neurons. It makes decisions independently. Your gut literally thinks.",
    "🌀 MANDELA EFFECT EXPLAINED: Your brain fills in gaps in your vision. There is a blind spot in each eye where the optic nerve connects. You have never seen a complete image in your entire life.",
    "🔬 QUANTUM HORROR: Particles that have interacted remain connected FOREVER across any distance. Einstein called it spooky action at a distance. Changing one instantly affects the other. Nothing should be able to do this.",
    "🕊️ BIRDS ARE DINOSAURS: When you look at a bird, you are looking at a living dinosaur. Birds are the direct descendants of theropod dinosaurs. The T-Rex is more closely related to a chicken than to a Triceratops.",
    "🌿 TREES ARE ONE ORGANISM: The Pando aspen grove in Utah is a single organism connected by roots. It weighs 6 million kg. It is 80,000 years old. It is the largest and oldest living thing on Earth.",
    "🤖 YOU ARE PROGRAMMABLE: Scientists have successfully implanted false memories into mice. The mice acted on memories of things that never happened. Human memory works the same way. You may already have false memories.",
    "💀 DEATH PARADOX: The cells in your body are completely replaced every 7-10 years. You share zero atoms with the person you were a decade ago. Are you the same person? Philosophers have debated this for 2,000 years.",
    "⚡ SPEED OF THOUGHT: A nerve impulse travels at 268 mph. But conscious thought is much slower. Your brain makes decisions up to 10 SECONDS before you are consciously aware of making them. Free will might be an illusion.",
    "🌌 MULTIVERSE IS MATH: The equations of quantum mechanics don't predict ONE outcome. They predict ALL possible outcomes simultaneously. The many-worlds interpretation says every decision spawns a parallel universe. Every. Single. One.",
    "🧠 PLACEBO IS REAL MEDICINE: In clinical trials, placebo surgery — where surgeons cut open patients, do nothing, and sew them back up — has the same results as real surgery for certain conditions. Your belief literally heals you.",
    "🔮 NOTHING IS SOLID: The chair you are sitting on is not solid. The atoms repel each other electromagnetically creating the illusion of solidity. You are not touching anything. You never have. You never will.",
]

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS DATABASE
# ─────────────────────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "first_mission",    "name": "⚡ FIRST BLOOD",          "desc": "Completed your very first mission. The journey begins NOW.",          "req": lambda s: s.get("total_missions",0) >= 1},
    {"id": "five_missions",    "name": "🔥 ON A ROLL",             "desc": "5 missions done. You're already better than yesterday.",              "req": lambda s: s.get("total_missions",0) >= 5},
    {"id": "ten_missions",     "name": "💪 GRIND MODE ACTIVATED",  "desc": "10 missions. This is becoming a habit. A powerful one.",              "req": lambda s: s.get("total_missions",0) >= 10},
    {"id": "fifty_missions",   "name": "👑 UNSTOPPABLE",           "desc": "50 missions. You are literally built different at this point.",        "req": lambda s: s.get("total_missions",0) >= 50},
    {"id": "first_gold",       "name": "💰 FIRST PAYDAY",          "desc": "Earned your first currency. The grind pays off.",                     "req": lambda s: s.get("gold",0) >= 5},
    {"id": "rich",             "name": "🤑 LOADED",                "desc": "100 currency stacked. You are wealthy in this universe.",             "req": lambda s: s.get("gold",0) >= 100},
    {"id": "elite_unlocked",   "name": "👁️ ELITE EYES ONLY",       "desc": "You found the code. Not everyone gets here.",                         "req": lambda s: s.get("sub_tier","") == "Elite"},
    {"id": "first_battle",     "name": "⚔️ WARRIOR BORN",          "desc": "First battle fought. Win or lose — you showed up.",                   "req": lambda s: s.get("battles_fought",0) >= 1},
    {"id": "battle_streak",    "name": "🏆 BATTLE HARDENED",       "desc": "10 battles completed. You fear nothing in this universe.",            "req": lambda s: s.get("battles_fought",0) >= 10},
    {"id": "first_egg",        "name": "🥚 EGG COLLECTOR",         "desc": "First incubator egg earned. Something is growing in there...",        "req": lambda s: s.get("eggs_hatched",0) >= 1},
    {"id": "legendary_hatch",  "name": "🐉 LEGENDARY TAMER",       "desc": "A LEGENDARY creature hatched. This almost never happens.",            "req": lambda s: s.get("legendary_hatched",False)},
    {"id": "shield_bought",    "name": "🛡️ FORTIFIED",             "desc": "Defense ability acquired. Nothing can touch you now.",                "req": lambda s: s.get("shield_bought",False)},
    {"id": "booster_bought",   "name": "🚀 SPEED DEMON",           "desc": "Speed ability acquired. You move at a different frequency.",          "req": lambda s: s.get("booster_bought",False)},
    {"id": "secret_collector", "name": "🔮 TRUTH SEEKER",          "desc": "Collected 5 universe secrets. Your mind is expanding.",              "req": lambda s: s.get("secrets_seen",0) >= 5},
    {"id": "spinner_winner",   "name": "🎰 LUCKY SPIN",            "desc": "Won your first prize on the spinner. Fortune favours the bold.",      "req": lambda s: s.get("spinner_wins",0) >= 1},
    {"id": "storyline_deep",   "name": "📖 LORE KEEPER",           "desc": "Reached chapter 5 of your universe storyline. You are invested.",     "req": lambda s: s.get("story_chapter",0) >= 5},
]

# ─────────────────────────────────────────────────────────────────────────────
# SPINNER PRIZES
# ─────────────────────────────────────────────────────────────────────────────
SPINNER_PRIZES = [
    {"label": "2× GOLD",      "emoji": "💰", "color": "#FFD700", "type": "gold_mult",    "value": 2,   "weight": 25},
    {"label": "5 BONUS",      "emoji": "⚡", "color": "#00FF88", "type": "gold_flat",    "value": 5,   "weight": 20},
    {"label": "RARE EGG",     "emoji": "🥚", "color": "#4488ff", "type": "egg_rare",     "value": 1,   "weight": 15},
    {"label": "EPIC EGG",     "emoji": "✨", "color": "#aa44ff", "type": "egg_epic",     "value": 1,   "weight": 8},
    {"label": "SHIELD",       "emoji": "🛡️", "color": "#22CCFF", "type": "ability",      "value": "shield", "weight": 10},
    {"label": "BOOSTER",      "emoji": "🚀", "color": "#FF6600", "type": "ability",      "value": "booster","weight": 8},
    {"label": "STORY TWIST",  "emoji": "📖", "color": "#FF44AA", "type": "story_twist",  "value": 1,   "weight": 7},
    {"label": "NOTHING",      "emoji": "💨", "color": "#444444", "type": "nothing",      "value": 0,   "weight": 7},
]

def spin_wheel():
    weights = [p["weight"] for p in SPINNER_PRIZES]
    total = sum(weights)
    r = random.randint(1, total)
    cumulative = 0
    for prize in SPINNER_PRIZES:
        cumulative += prize["weight"]
        if r <= cumulative:
            return prize
    return SPINNER_PRIZES[-1]


import datetime as _dt

def variable_reward(base: float) -> tuple:
    """Slot-machine style reward. Unpredictability = dopamine."""
    roll = random.random()
    if roll < 0.04:   # 4% — JACKPOT
        mult = random.randint(8, 20)
        return base * mult, "💥 JACKPOT", f"{mult}× MULTIPLIER — THE UNIVERSE REWARDS YOU"
    elif roll < 0.12: # 8% — EPIC
        mult = random.randint(4, 7)
        return base * mult, "🌟 EPIC REWARD", f"{mult}× — An extraordinary surge of power!"
    elif roll < 0.28: # 16% — GREAT
        mult = random.randint(2, 3)
        return base * mult, "⚡ GREAT PULL", f"{mult}× — You felt it in your soul."
    elif roll < 0.55: # 27% — NORMAL
        return base * 1, "✅ SOLID", "Standard reward. The grind continues."
    else:             # 45% — LOW (keeps them hungry)
        mult = round(random.uniform(0.3, 0.7), 1)
        return base * mult, "😤 LOW ROLL", f"Only {mult}×... but the NEXT one could be 20×."

def get_spins_for_tier(tier: str) -> int:
    if tier == "Elite":   return random.randint(4, 7)
    if tier == "Premium": return random.randint(2, 4)
    return 1

def rig_xp_bar(xp: int, level: int) -> float:
    """Always show XP bar at 85-95% so they're always 'almost there'."""
    needed = level * 100
    real_pct = (xp % needed) / needed if needed > 0 else 0
    # If below 85%, fake it up to 85-92%
    if real_pct < 0.85:
        return random.uniform(0.85, 0.92)
    return min(real_pct, 0.98)

def update_streak() -> tuple:
    """Update daily streak. Returns (new_streak, message, is_new_day)."""
    today = _dt.date.today().isoformat()
    last  = st.session_state.get("last_active_date")
    streak = st.session_state.get("study_streak", 0)
    if last is None:
        st.session_state.study_streak = 1
        st.session_state.last_active_date = today
        return 1, "🔥 Streak started! Don't break it!", True
    if last == today:
        return streak, "", False   # already active today
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    if last == yesterday:
        streak += 1
        st.session_state.study_streak = streak
        st.session_state.last_active_date = today
        msg = f"🔥 {streak}-DAY STREAK! You're unstoppable!"
        if streak % 7 == 0:
            msg = f"🏆 {streak} DAYS — WEEK COMPLETE! Bonus spins unlocked!"
            st.session_state.spins_left += 3
        return streak, msg, True
    else:
        # Streak broken
        old = streak
        st.session_state.study_streak = 1
        st.session_state.last_active_date = today
        return 1, f"💔 {old}-day streak LOST. Today is a fresh start.", True

def loot_box_html(item_name: str, rarity: str, color: str) -> str:
    rarity_colors = {"JACKPOT":"#FFD700","EPIC":"#AA44FF","GREAT":"#4488FF","SOLID":"#44FF88","LOW":"#888888"}
    rc = rarity_colors.get(rarity.upper().split()[0], "#FFD700")
    return f"""
    <div style='text-align:center;padding:32px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);
        border:3px solid {rc};border-radius:20px;animation:lootpulse 0.6s ease-in-out 3;
        box-shadow:0 0 40px {rc}88;'>
        <div style='font-size:64px;animation:lootbounce 0.4s ease-in-out infinite alternate'>🎁</div>
        <div style='font-size:28px;font-family:Bebas Neue,sans-serif;color:{rc};
            letter-spacing:6px;margin:12px 0'>{rarity}</div>
        <div style='font-size:20px;color:#ffffff;font-family:Space Mono,monospace'>{item_name}</div>
    </div>
    <style>
    @keyframes lootpulse{{0%{{box-shadow:0 0 20px {rc}44}}50%{{box-shadow:0 0 60px {rc}cc}}100%{{box-shadow:0 0 20px {rc}44}}}}
    @keyframes lootbounce{{from{{transform:scale(1) rotate(-5deg)}}to{{transform:scale(1.2) rotate(5deg)}}}}
    </style>"""

def streak_danger_html(streak: int, color: str) -> str:
    if streak < 2: return ""
    return f"""<div style='background:linear-gradient(90deg,#3a0000,#1a0000);border:2px solid #FF2222;
        border-radius:12px;padding:12px 20px;text-align:center;margin:8px 0;
        animation:streakpulse 1.5s ease-in-out infinite;'>
        <span style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FF4444;letter-spacing:3px'>
        🔥 {streak}-DAY STREAK AT RISK</span>
        <span style='display:block;font-family:Space Mono,monospace;font-size:11px;color:#FF8888;margin-top:4px'>
        Complete a mission TODAY or lose it forever.</span></div>
    <style>@keyframes streakpulse{{0%,100%{{border-color:#FF2222}}50%{{border-color:#FF8888}}}}</style>"""


# ─────────────────────────────────────────────────────────────────────────────
# AI STORYLINE + ACHIEVEMENT GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_story_chapter(theme, chapter, prev_story, client):
    """Generate next chapter of the universe storyline."""
    try:
        is_milestone = (chapter % 5 == 0)
        prompt = f"""You are the most creative storyteller alive. The user is studying in the universe of: "{theme}"

They are on Chapter {chapter} of their universe storyline.
Previous story so far: {prev_story[-300:] if prev_story else "This is the beginning."}

{"This is a MILESTONE chapter — make it a MASSIVE plot twist or revelation. Something shocking that recontextualizes everything. Universe-specific. Jaw-dropping." if is_milestone else "Write the next short chapter (2-3 sentences max). Universe-specific. Gripping. Ends on a hook that makes you NEED to read the next one."}

Rules:
- Reference the specific universe deeply — characters, locations, lore
- Make it feel earned and connected to studying/working hard
- {"MILESTONE: End with a cliffhanger that changes EVERYTHING" if is_milestone else "End with a micro-cliffhanger"}
- Raw text only, no titles, no formatting

Write the chapter now:"""
        msg = client.messages.create(
            model="claude-sonnet-4-5", max_tokens=200,
            messages=[{"role":"user","content":prompt}]
        )
        return msg.content[0].text.strip()
    except:
        return f"Chapter {chapter}: The {theme} universe trembles. Something ancient stirs in the shadows. Your power grows — but so does the threat."

def generate_universe_achievements(theme, client):
    """Generate universe-specific achievements via AI."""
    try:
        prompt = f"""Generate 5 achievements specific to the universe "{theme}" AND studying/working hard.
Each achievement has: name (with emoji, max 4 words), desc (one punchy sentence, how it's earned).
Return ONLY raw JSON array, no markdown:
[{{"name":"...","desc":"..."}},{{"name":"...","desc":"..."}}]"""
        msg = client.messages.create(
            model="claude-sonnet-4-5", max_tokens=400,
            messages=[{"role":"user","content":prompt}]
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`")
        data = json.loads(raw)
        return data[:5]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# MONSTER DATABASE (per battle style)
# ─────────────────────────────────────────────────────────────────────────────
GENERIC_MONSTERS = [
    {"name": "Shadow Titan",    "hp": 3, "reward": 5,  "rarity": "Common"},
    {"name": "Void Stalker",    "hp": 4, "reward": 8,  "rarity": "Rare"},
    {"name": "Chaos Wraith",    "hp": 5, "reward": 12, "rarity": "Epic"},
    {"name": "Oblivion Lord",   "hp": 7, "reward": 20, "rarity": "Legendary"},
]

EGG_RARITIES = [
    {"rarity": "Common",    "color": "#aaaaaa", "chance": 55, "reward_mult": 1},
    {"rarity": "Rare",      "color": "#4488ff", "chance": 28, "reward_mult": 2},
    {"rarity": "Epic",      "color": "#aa44ff", "chance": 13, "reward_mult": 4},
    {"rarity": "Legendary", "color": "#FFD700", "chance": 4,  "reward_mult": 10},
]

# ─────────────────────────────────────────────────────────────────────────────
# API + JSON HELPERS
# ─────────────────────────────────────────────────────────────────────────────
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
    result = {}
    for key in ["currency","color","shield_name","booster_name","description","shield_flavor","booster_flavor","battle_style"]:
        m = re.search(rf'["\']?{key}["\']?\s*:\s*["\']([^"\'<>]+)["\']', cleaned, re.IGNORECASE)
        if m:
            result[key] = m.group(1).strip()
    return result if len(result) >= 4 else None

# ─────────────────────────────────────────────────────────────────────────────
# LORE PROMPT — ATOMIC SPECIFICITY
# ─────────────────────────────────────────────────────────────────────────────
LORE_PROMPT = """You are the world's most encyclopedic expert on every game, anime, manga, sport, team, brand, movie, show, book, music genre, artist, fashion brand, historical era, cultural phenomenon, character, sub-group, weapon, location, and concept that has ever existed.

A user has chosen the universe: "{theme}"

CRITICAL RULE: Go to the most ATOMIC level of specificity possible.
- If given a specific CHARACTER (e.g. "Vinsmoke Ichiji", "Roronoa Zoro", "Kobe Bryant") — use THAT character's exact moves, weapons, signature moments. NOT the parent franchise.
- If given a specific TEAM (e.g. "Chicago Bulls 1996", "Germa 66 Stealth Black") — use THAT team's exact identity, colors, and tactics.
- If given a specific WEAPON, LOCATION, ERA, SONG, ALBUM — zoom all the way in on THAT specific thing.
- If given a MERGED universe (e.g. "Germa 66 meets Halo") — blend both intelligently.
- NEVER give generic answers when something specific is provided.

Return ONLY a single raw JSON object. No explanation, no markdown, no code fences.

Fields:
- "currency": The EXACT in-universe currency. CRITICAL CURRENCY RULE: If the theme is ANY character, sub-group, or faction that belongs to a parent universe with an established currency, ALWAYS use the parent universe currency. Examples: ANY One Piece character/group (Luffy, Zoro, Germa 66, Vinsmoke Yonji, Big Mom Pirates, etc.) = Berries. ANY Naruto character = Ryo. ANY Dragon Ball character = Zeni. ANY Harry Potter character/house = Galleons. ANY Star Wars faction = Galactic Credits. Only use a custom sub-currency if the sub-group has a completely independent economy with NO connection to the parent universe.
- "color": The single most ICONIC hex color. For specific characters use THEIR color not the franchise color. Ichiji=red-gold of his Raid Suit, Zoro=forest green, Stealth Black Germa=deep black-gold. Reference colors: Super Smash Bros=#E4000F, Mario=#E52521, Sonic=#0057A8, Minecraft=#5D9E35, Fortnite=#BEFF00, Roblox=#E8272A, Pokemon=#FFCB05, Valorant=#FF4655, One Piece=#E8372B, Naruto=#FF6600, Dragon Ball=#FF8C00, Demon Slayer=#22AA44, JJK=#6600CC, F1=#FF1801, NBA=#EE6730, NFL=#013369, Star Wars=#FFE81F, Marvel=#ED1D24, DC=#0476F2, Harry Potter=#740001, Skyrim=#C0C0C0, Elden Ring=#C8A951, GTA=#F4B000, Halo=#00B4D8, Dead by Daylight=#8B0000, Nike=#111111, Spotify=#1DB954, Netflix=#E50914. For anything else use the dominant iconic color of that exact thing.
- "shield_name": The most iconic DEFENSIVE ability, armor, or technique specific to THIS exact universe/character. Never generic.
- "booster_name": The most iconic SPEED or MOVEMENT ability specific to THIS exact universe/character. Never generic.
- "shield_flavor": ONE fun hype sentence describing what this defense ability does. Universe-flavored. Max 12 words.
- "booster_flavor": ONE fun hype sentence describing what this speed ability does. Universe-flavored. Max 12 words.
- "description": One punchy sentence (max 12 words) capturing the soul of this universe/character/concept.
- "battle_style": One of: "shooter", "turnbased", "reaction", "rpgclick", "survival", "rhythm", "racing", "trivia" — pick the ONE that fits the universe's actual combat/gameplay style. Rules: FPS/tactical shooters(CoD,Valorant,Halo,Apex,Fortnite)=shooter. Anime/manga/fantasy RPG=turnbased. Sports/racing(NBA,NFL,F1,FIFA)=reaction for sports OR racing for F1/racing games. Horror(Dead by Daylight,Resident Evil,Outlast)=survival. Music/fashion/K-pop/Spotify=rhythm. Minecraft/Terraria/sandbox RPG=rpgclick. Quiz/trivia/school/academic themes=trivia. If user prompt explicitly requests a style, use that. Otherwise default to what fits the universe naturally.

Return exactly:
{{"currency":"...","color":"#RRGGBB","shield_name":"...","booster_name":"...","description":"...","shield_flavor":"...","booster_flavor":"...","battle_style":"..."}}"""

# ─────────────────────────────────────────────────────────────────────────────
# HARD FALLBACKS
# ─────────────────────────────────────────────────────────────────────────────
HARD_FALLBACKS = {
    "super smash bros":  {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"Every gaming legend meets in the ultimate crossover brawl.","shield_flavor":"Reflects any attack back with perfect timing.","booster_flavor":"Slides across the stage faster than the eye can track.","battle_style":"reaction"},
    "minecraft":         {"currency":"Emeralds","color":"#5D9E35","shield_name":"Protection IV Netherite Chestplate","booster_name":"Ender Pearl Warp","description":"A boundless world of blocks where creativity and survival collide.","shield_flavor":"Absorbs almost any damage with enchanted netherite armor.","booster_flavor":"Teleports you instantly wherever the pearl lands.","battle_style":"random"},
    "fortnite":          {"currency":"V-Bucks","color":"#BEFF00","shield_name":"Shield Bubble","booster_name":"Shockwave Grenade","description":"100 players drop in. Only one walks out.","shield_flavor":"Creates an impenetrable dome that blocks all incoming fire.","booster_flavor":"Launches you through the air at explosive speed.","battle_style":"shooter"},
    "roblox":            {"currency":"Robux","color":"#E8272A","shield_name":"Force Field","booster_name":"Speed Coil","description":"An infinite universe of user-built worlds with zero limits.","shield_flavor":"Wraps you in an untouchable glowing force bubble.","booster_flavor":"Multiplies your movement speed to inhuman levels instantly.","battle_style":"random"},
    "pokemon":           {"currency":"PokéDollars","color":"#FFCB05","shield_name":"Protect","booster_name":"Extreme Speed","description":"Catch, train, and battle creatures across endless adventure.","shield_flavor":"A perfect barrier that blocks any single incoming attack.","booster_flavor":"Moves so fast it always strikes first, no exceptions.","battle_style":"turnbased"},
    "valorant":          {"currency":"VP","color":"#FF4655","shield_name":"Sage Barrier Orb","booster_name":"Jett Updraft","description":"Precise gunplay meets deadly abilities in a tactical shooter.","shield_flavor":"Raises a solid ice wall that stops bullets cold.","booster_flavor":"Launches Jett upward on a burst of wind.","battle_style":"shooter"},
    "dead by daylight":  {"currency":"Bloodpoints","color":"#8B0000","shield_name":"Dead Hard","booster_name":"Sprint Burst","description":"Survivors and killers play an eternal game of death.","shield_flavor":"A burst of adrenaline that phases through a hit.","booster_flavor":"Explodes into a full sprint from a standing start.","battle_style":"survival"},
    "one piece":         {"currency":"Berries","color":"#E8372B","shield_name":"Armament Haki","booster_name":"Gear Second","description":"A pirate's odyssey chasing the ultimate treasure.","shield_flavor":"Coats your body in invisible armor that blocks Devil Fruits.","booster_flavor":"Pumps blood at rocket speed to move like lightning.","battle_style":"turnbased"},
    "naruto":            {"currency":"Ryo","color":"#FF6600","shield_name":"Susanoo Ribcage","booster_name":"Flying Thunder God","description":"From outcast to the strongest — the ninja's path.","shield_flavor":"A giant ribcage of chakra that absorbs catastrophic damage.","booster_flavor":"Teleports instantly to any marked location across any distance.","battle_style":"turnbased"},
    "dragon ball":       {"currency":"Zeni","color":"#FF8C00","shield_name":"Barrier Blast","booster_name":"Instant Transmission","description":"Warriors transcend all limits in an eternal quest for power.","shield_flavor":"A ki barrier that explodes outward destroying everything nearby.","booster_flavor":"Locks onto any ki signature and teleports there instantly.","battle_style":"turnbased"},
    "demon slayer":      {"currency":"Yen","color":"#22AA44","shield_name":"Total Concentration Breathing","booster_name":"Thunder Breathing First Form","description":"Demon hunters clash with ancient evil using breathing and will.","shield_flavor":"Fills every cell with oxygen giving superhuman endurance instantly.","booster_flavor":"A single lightning-fast slash that crosses any distance instantly.","battle_style":"turnbased"},
    "attack on titan":   {"currency":"Eldian Marks","color":"#8B6914","shield_name":"Hardening Crystal","booster_name":"ODM Gear Swing","description":"Humanity fights back against titans behind crumbling walls.","shield_flavor":"Crystallizes your titan skin into unbreakable diamond-hard armor.","booster_flavor":"Launches grappling hooks and swings at terrifying speed.","battle_style":"survival"},
    "jujutsu kaisen":    {"currency":"Cursed Tokens","color":"#6600CC","shield_name":"Infinity Barrier","booster_name":"Divergent Fist","description":"Cursed energy battles rage beneath everyday life.","shield_flavor":"Slows everything approaching you to an infinite standstill.","booster_flavor":"Cursed energy explodes out a split second after impact.","battle_style":"turnbased"},
    "bleach":            {"currency":"Spirit Coins","color":"#4A4A4A","shield_name":"Hierro Skin","booster_name":"Shunpo Flash Step","description":"Soul Reapers clash with Hollows in a war between life and death.","shield_flavor":"Steel-hard skin that makes blades feel like paper.","booster_flavor":"Moves so fast you leave afterimages across the battlefield.","battle_style":"turnbased"},
    "my hero academia":  {"currency":"Hero Credits","color":"#1DA462","shield_name":"Full Cowl Armor","booster_name":"One For All Smash","description":"Heroes and villains clash where quirks define destiny.","shield_flavor":"Channels One For All through every cell for full protection.","booster_flavor":"Concentrates every ounce of One For All into one devastating hit.","battle_style":"turnbased"},
    "f1":                {"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium Cockpit","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed and nerve collide.","shield_flavor":"A titanium halo that has saved drivers' lives at 300kph.","booster_flavor":"Opens the rear wing and adds 15kph of pure straight-line speed.","battle_style":"reaction"},
    "nba":               {"currency":"VC","color":"#EE6730","shield_name":"Lockdown Defender","booster_name":"Fast Break","description":"The greatest basketball league where legends are born nightly.","shield_flavor":"Shuts down any offensive player with suffocating on-ball pressure.","booster_flavor":"Pushes the pace before the defense can set up.","battle_style":"reaction"},
    "nfl":               {"currency":"Fan Tokens","color":"#013369","shield_name":"Blitz Package","booster_name":"Hail Mary","description":"America's most electrifying sport played by the world's greatest.","shield_flavor":"Sends every defender at the quarterback simultaneously.","booster_flavor":"A desperate 60-yard throw into the end zone at the buzzer.","battle_style":"reaction"},
    "harry potter":      {"currency":"Galleons","color":"#740001","shield_name":"Protego Totalum","booster_name":"Apparition","description":"A world of magic and courage hidden behind ordinary life.","shield_flavor":"Casts a full protective enchantment over an entire building.","booster_flavor":"Vanishes from one location and reappears anywhere instantly.","battle_style":"turnbased"},
    "star wars":         {"currency":"Galactic Credits","color":"#FFE81F","shield_name":"Lightsaber Deflect","booster_name":"Force Speed","description":"A galaxy far away locked in eternal war between light and dark.","shield_flavor":"Spins the lightsaber so fast it creates an impenetrable energy shield.","booster_flavor":"Channels the Force to move at superhuman blinding speed.","battle_style":"turnbased"},
    "marvel":            {"currency":"Stark Credits","color":"#ED1D24","shield_name":"Vibranium Shield","booster_name":"Repulsor Boost","description":"Earth's mightiest heroes stand against total annihilation.","shield_flavor":"Absorbs and redirects any kinetic energy thrown at it.","booster_flavor":"Fires repulsor blasts downward to launch you across the sky.","battle_style":"turnbased"},
    "halo":              {"currency":"CR","color":"#00B4D8","shield_name":"Energy Shield","booster_name":"Active Camo","description":"Master Chief stands as humanity's last line against the Covenant.","shield_flavor":"Regenerating energy shield absorbs hits and recovers automatically.","booster_flavor":"Turns completely invisible for a limited but deadly window.","battle_style":"shooter"},
    "call of duty":      {"currency":"CoD Points","color":"#FF6600","shield_name":"Trophy System","booster_name":"Tactical Sprint","description":"The world's most intense military shooter — no mercy in ranked.","shield_flavor":"Intercepts and destroys incoming grenades and projectiles automatically.","booster_flavor":"A full-speed burst sprint that covers ground in seconds.","battle_style":"shooter"},
    "apex legends":      {"currency":"Apex Coins","color":"#DA292A","shield_name":"Evo Shield","booster_name":"Pathfinder Grapple","description":"Legends compete in a brutal frontier battle royale.","shield_flavor":"Absorbs damage and evolves into a stronger shield automatically.","booster_flavor":"Launches a grappling hook that swings you anywhere instantly.","battle_style":"shooter"},
    "among us":          {"currency":"Stars","color":"#C51111","shield_name":"Emergency Meeting","booster_name":"Vent Escape","description":"Trust no one — the impostor walks among you right now.","shield_flavor":"Calls everyone together instantly buying you precious time.","booster_flavor":"Drops into a vent and reappears anywhere on the map.","battle_style":"survival"},
    "valorant":          {"currency":"VP","color":"#FF4655","shield_name":"Sage Barrier Orb","booster_name":"Jett Updraft","description":"Precise gunplay meets deadly abilities in a tactical shooter.","shield_flavor":"Raises a solid ice wall that stops bullets cold.","booster_flavor":"Launches upward on a burst of cutting wind.","battle_style":"shooter"},
    "elden ring":        {"currency":"Runes","color":"#C8A951","shield_name":"Erdtree Greatshield","booster_name":"Bloodhound Step","description":"A shattered world of demigods in pursuit of the Elden Ring.","shield_flavor":"A colossal golden shield blessed by the Erdtree itself.","booster_flavor":"A ghost-step dodge that leaves behind a phantom decoy.","battle_style":"turnbased"},
    "skyrim":            {"currency":"Septims","color":"#C0C0C0","shield_name":"Dragonhide Spell","booster_name":"Whirlwind Sprint Shout","description":"The Dragonborn's destiny unfolds across a frozen ancient land.","shield_flavor":"Encases your skin in magical dragon scales deflecting all blows.","booster_flavor":"A dragon shout that launches you forward at wind speed.","battle_style":"turnbased"},
    "gta":               {"currency":"GTA$","color":"#F4B000","shield_name":"Body Armor","booster_name":"Rocket Boost","description":"Power, money, and chaos rule the streets.","shield_flavor":"Military-grade body armor absorbing bullets like they are nothing.","booster_flavor":"Fires a rocket booster launching you forward at insane speed.","battle_style":"shooter"},
    "zelda":             {"currency":"Rupees","color":"#5ACD3D","shield_name":"Hylian Shield","booster_name":"Ocarina Serenade","description":"The hero of time journeys through Hyrule to defeat darkness.","shield_flavor":"The legendary shield that has never been destroyed in battle.","booster_flavor":"A magical song that warps you instantly to any location.","battle_style":"turnbased"},
    "overwatch":         {"currency":"Overwatch Coins","color":"#F99E1A","shield_name":"Reinhardt Barrier","booster_name":"Lucio Speed Boost","description":"Colorful heroes battle across a futuristic world in conflict.","shield_flavor":"A massive energy barrier protecting everyone standing behind it.","booster_flavor":"An area aura that permanently speeds up your entire team.","battle_style":"shooter"},
    "nike":              {"currency":"NikeCash","color":"#111111","shield_name":"Air Max Cushioning","booster_name":"ReactX Foam Propulsion","description":"Just Do It — where athletic performance meets street culture.","shield_flavor":"Absorbs impact forces like they never happened at all.","booster_flavor":"Stores and returns energy in every step for explosive speed.","battle_style":"reaction"},
    "spotify":           {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancelling","booster_name":"Algorithmic Surge","description":"Music for everyone — three million songs, infinite discovery.","shield_flavor":"Blocks out every distraction leaving only pure focus.","booster_flavor":"The algorithm finds your next obsession before you even search.","battle_style":"rhythm"},
    "netflix":           {"currency":"Watch Hours","color":"#E50914","shield_name":"Skip Intro","booster_name":"Autoplay Rush","description":"One more episode — the platform that redefined how we watch.","shield_flavor":"Skips straight past anything standing in your way.","booster_flavor":"Loads the next episode before you can even think to stop.","battle_style":"random"},
    "ancient rome":      {"currency":"Denarii","color":"#B22222","shield_name":"Testudo Formation","booster_name":"Cavalry Charge","description":"Iron legions built the greatest empire the world has ever seen.","shield_flavor":"Locks shields into an impenetrable tortoise of Roman steel.","booster_flavor":"A thundering wall of horses that crushes any battle line.","battle_style":"turnbased"},
    "k-pop":             {"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma.","shield_flavor":"Ten thousand lightsticks form a wall of pure fan power.","booster_flavor":"Drops the new single and breaks the entire internet instantly.","battle_style":"rhythm"},
    "kpop":              {"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma.","shield_flavor":"Ten thousand lightsticks form a wall of pure fan power.","booster_flavor":"Drops the new single and breaks the entire internet instantly.","battle_style":"rhythm"},
}

def get_fallback(theme):
    t = theme.lower().strip()
    if t in HARD_FALLBACKS:
        return HARD_FALLBACKS[t]
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key:
            return data
    if any(w in t for w in ("game","gaming","rpg","fps","moba","battle royale","shooter")):
        return {"currency":"Gold","color":"#FFD700","shield_name":"Barrier Field","booster_name":"Phase Dash","description":"An infinite digital universe where only the skilled survive.","shield_flavor":"An energy barrier that blocks any incoming attack cold.","booster_flavor":"Phases through reality itself leaving enemies completely confused.","battle_style":"shooter"}
    if any(w in t for w in ("anime","manga","shonen","seinen")):
        return {"currency":"Ryo","color":"#FF4500","shield_name":"Armament Aura","booster_name":"Body Flicker","description":"A world of extraordinary power, honour, and relentless destiny.","shield_flavor":"Coats your entire body in an invisible armored aura.","booster_flavor":"Moves so fast the human eye literally cannot follow.","battle_style":"turnbased"}
    if any(w in t for w in ("sport","league","cup","championship","team","fc","united")):
        return {"currency":"Trophy Points","color":"#FFD700","shield_name":"Iron Defense","booster_name":"Turbo Sprint","description":"The ultimate competitive arena where legends are made.","shield_flavor":"A defensive wall that has never once been broken through.","booster_flavor":"Explodes past every defender with pure explosive acceleration.","battle_style":"reaction"}
    if any(w in t for w in ("fashion","brand","wear","style","cloth","retail","drip")):
        return {"currency":"Style Credits","color":"#FF69B4","shield_name":"Signature Drip","booster_name":"Trend Surge","description":"Where identity becomes art and every fit tells a story.","shield_flavor":"Your fit is so clean it stops haters in their tracks.","booster_flavor":"Catches the trend wave before anyone else even sees it.","battle_style":"rhythm"}
    if any(w in t for w in ("music","rap","hip","pop","rock","edm","trap","drill")):
        return {"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancel","booster_name":"Drop Surge","description":"A universe built on rhythm, bars, and raw cultural resonance.","shield_flavor":"Cancels out all noise and lets only the beat through.","booster_flavor":"The drop hits and everything accelerates beyond all control.","battle_style":"rhythm"}
    if any(w in t for w in ("horror","scary","dark","terror","ghost","demon")):
        return {"currency":"Fear Points","color":"#8B0000","shield_name":"Ward Sigil","booster_name":"Shadow Sprint","description":"Fear is the only currency that matters in this realm.","shield_flavor":"An ancient sigil that keeps the darkness at bay temporarily.","booster_flavor":"Merges with shadows and moves unseen through pure terror.","battle_style":"survival"}
    return {"currency":"Titan Shards","color":"#00FFCC","shield_name":"Kinetic Barrier","booster_name":"Void Dash","description":"A realm of boundless power and infinite possibility.","shield_flavor":"Converts all incoming kinetic energy into pure protective force.","booster_flavor":"Rips a hole in space and steps through it instantly.","battle_style":"random"}

REQUIRED_KEYS = ["currency","color","shield_name","booster_name","description"]

def resolve_universe(theme):
    if not theme.strip():
        return DEFAULT_UNIVERSE.copy()
    client = get_claude_client()
    if client is not None:
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=400,
                messages=[{"role":"user","content":LORE_PROMPT.format(theme=theme)}]
            )
            raw  = message.content[0].text.strip()
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color","")):
                    data["color"] = "#FFD700"
                data.setdefault("shield_flavor",  "An ability forged in the heart of this universe.")
                data.setdefault("booster_flavor", "Speed that defies every known law of physics.")
                data.setdefault("battle_style",   "random")
                data["shield_effect"]  = SHIELD_EFFECT
                data["booster_effect"] = BOOSTER_EFFECT
                return data
        except Exception:
            pass
    data = get_fallback(theme)
    data["shield_effect"]  = SHIELD_EFFECT
    data["booster_effect"] = BOOSTER_EFFECT
    return data

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def is_light(hex_color):
    h = hex_color.lstrip('#')
    try:
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return (r*299+g*587+b*114)/1000 > 128
    except:
        return False

def text_on(hex_color):
    return "#000000" if is_light(hex_color) else "#ffffff"

def readable_color(theme_color, bg_color):
    """Return theme color if it's readable on bg, else return white or black."""
    if theme_color.lower() == bg_color.lower():
        return "#ffffff" if is_light(bg_color) else "#FFD700"
    h = theme_color.lstrip('#')
    try:
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        luminance = (r*299+g*587+b*114)/1000
        bg_light = is_light(bg_color)
        if bg_light and luminance > 180:
            return "#333333"
        if not bg_light and luminance < 60:
            return "#FFD700"
    except:
        pass
    return theme_color

def check_achievements(session):
    newly_unlocked = []
    unlocked = session.get("unlocked_achievements", set())
    for ach in ACHIEVEMENTS:
        if ach["id"] not in unlocked:
            try:
                if ach["req"](session):
                    unlocked.add(ach["id"])
                    newly_unlocked.append(ach)
            except:
                pass
    session["unlocked_achievements"] = unlocked
    return newly_unlocked

def hatch_egg(theme):
    roll = random.randint(1,100)
    cumulative = 0
    chosen = EGG_RARITIES[-1]
    for r in EGG_RARITIES:
        cumulative += r["chance"]
        if roll <= cumulative:
            chosen = r
            break
    monster_names = {
        "Common":    [f"{theme} Scout",    f"{theme} Grunt",     f"{theme} Wisp"],
        "Rare":      [f"{theme} Hunter",   f"{theme} Phantom",   f"{theme} Sentinel"],
        "Epic":      [f"{theme} Warlord",  f"{theme} Specter",   f"{theme} Colossus"],
        "Legendary": [f"{theme} God",      f"{theme} Titan",     f"{theme} Overlord"],
    }
    name = random.choice(monster_names.get(chosen["rarity"], [f"{theme} Creature"]))
    return {"name": name, "rarity": chosen["rarity"], "color": chosen["color"], "reward_mult": chosen["reward_mult"]}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
if "gold" not in st.session_state:
    st.session_state.update({
        "user_name": None, "gold": 10.0, "xp": 0, "level": 1,
        "world_data": {}, "user_theme": "",
        "view": "main", "pending_gold": 0.0, "needs_verification": False,
        "vibe_color": "#FFD700", "sub_tier": "Free", "sub_multiplier": 1,
        "total_missions": 0, "bg_color": "#ffffff",
        "feedback_list": [], "micro_timer_seconds": 30,
        "game_mode": None,
        "how_open": False,
        "unlocked_achievements": set(),
        "battles_fought": 0, "battles_won": 0,
        "eggs_hatched": 0, "legendary_hatched": False,
        "incubator_eggs": 0, "hatched_monsters": [],
        "secrets_seen": 0,
        "shield_bought": False, "booster_bought": False,
        "battle_state": None, "current_battle": None, "egg_warmth": {},
        "secret_queue": [],
        "show_secret": None,
        "spinner_available": False,
        "spinner_wins": 0,
        "first_session": True,
        "spinner_result": None,
        "story_chapter": 0,
        "story_log": [],
        "story_twist_pending": False,
        "opening_story_shown": False,
        "study_streak": 0,
        "last_active_date": None,
        "streak_shield": False,
        "spins_left": 0,
        "loot_pending": False,
        "loot_item": None,
        "total_xp_real": 0,
        "universe_achievements": [],
        "universe_ach_loaded": False,
    })

# ─────────────────────────────────────────────────────────────────────────────
# 🌌 GATEWAY SCREEN v8.0
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_name is None:

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap');
    html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#000008!important;color:white!important;}
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;}
    .block-container{padding:0 1rem 2rem!important;max-width:100%!important;}

    [data-testid="stAppViewContainer"]{
        background:
            radial-gradient(ellipse 65% 55% at 5% 10%, rgba(255,215,0,0.22) 0%,transparent 60%),
            radial-gradient(ellipse 55% 45% at 95% 5%, rgba(255,50,50,0.18) 0%,transparent 60%),
            radial-gradient(ellipse 60% 50% at 50% 100%,rgba(0,200,255,0.18) 0%,transparent 60%),
            radial-gradient(ellipse 45% 40% at 90% 70%, rgba(160,80,220,0.15) 0%,transparent 60%),
            radial-gradient(ellipse 40% 35% at 10% 80%, rgba(0,255,130,0.12) 0%,transparent 60%),
            #000008!important;
        animation:orb-breathe 8s ease-in-out infinite alternate!important;
    }
    @keyframes orb-breathe{0%{filter:brightness(0.85) saturate(0.85);}50%{filter:brightness(1.25) saturate(1.35);}100%{filter:brightness(0.85) saturate(0.85);}}

    [data-testid="stAppViewContainer"]::before{
        content:'';position:fixed;top:0;left:0;width:100%;height:100%;
        background-image:linear-gradient(rgba(255,215,0,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,215,0,0.04) 1px,transparent 1px);
        background-size:55px 55px;pointer-events:none;z-index:0;
        animation:grid-breathe 5s ease-in-out infinite alternate;
    }
    @keyframes grid-breathe{0%{opacity:0.25;}100%{opacity:0.9;}}

    .star-field{
        width:100%;height:90px;
        background-image:
            radial-gradient(2px 2px at 5% 30%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 18% 70%,#fff 0%,transparent 100%),
            radial-gradient(2px 2px at 32% 20%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 47% 85%,#fff 0%,transparent 100%),
            radial-gradient(2px 2px at 61% 40%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 75% 65%,#fff 0%,transparent 100%),
            radial-gradient(2px 2px at 89% 15%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 12% 50%,#fff 0%,transparent 100%),
            radial-gradient(3px 3px at 14% 60%,#FFD700 0%,transparent 100%),radial-gradient(3px 3px at 70% 35%,#00C8FF 0%,transparent 100%),
            radial-gradient(3px 3px at 43% 75%,#FF5050 0%,transparent 100%),radial-gradient(3px 3px at 90% 90%,#A050DC 0%,transparent 100%),
            radial-gradient(2px 2px at 55% 10%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 38% 45%,#fff 0%,transparent 100%);
        animation:star-twinkle 3s ease-in-out infinite alternate;margin-bottom:8px;
    }
    @keyframes star-twinkle{0%{opacity:0.3;}100%{opacity:1.0;}}

    .scanline-wrap{width:100%;height:4px;overflow:hidden;margin-bottom:16px;}
    .scanline{width:40%;height:4px;background:linear-gradient(90deg,transparent,#FFD700,transparent);animation:scan-sweep 2s linear infinite;box-shadow:0 0 20px 4px rgba(255,215,0,0.6);}
    @keyframes scan-sweep{0%{transform:translateX(-150%);}100%{transform:translateX(400%);}}

    .top-badge{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.4);border-radius:99px;padding:8px 24px;font-family:'Space Mono',monospace;font-size:11px;letter-spacing:3px;color:#FFD700;text-transform:uppercase;text-align:center;display:table;margin:0 auto 20px;animation:badge-pulse 3s ease-in-out infinite alternate;}
    @keyframes badge-pulse{0%{box-shadow:0 0 10px rgba(255,215,0,0.2);}100%{box-shadow:0 0 40px rgba(255,215,0,0.6);}}

    .gw-main-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(72px,14vw,150px);text-align:center;letter-spacing:8px;line-height:0.88;background:linear-gradient(135deg,#FFD700 0%,#FF8C00 30%,#FF3C3C 65%,#CC00FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:title-glow 4s ease-in-out infinite alternate;margin-bottom:8px;}
    @keyframes title-glow{0%{filter:drop-shadow(0 0 12px rgba(255,215,0,0.5));}100%{filter:drop-shadow(0 0 60px rgba(255,140,0,0.8));}}

    .gw-subtitle{font-family:'Orbitron',sans-serif;font-size:clamp(12px,1.8vw,18px);text-align:center;letter-spacing:5px;color:#ffffff;text-transform:uppercase;margin-bottom:20px;text-shadow:0 0 20px rgba(255,255,255,0.4);}

    .features-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0 24px;}
    .feature-pill{background:rgba(255,215,0,0.12);border:1px solid rgba(255,215,0,0.35);border-radius:99px;padding:7px 16px;font-family:'Space Mono',monospace;font-size:12px;color:#ffffff;letter-spacing:1px;}
    .feature-pill span{margin-right:5px;}

    .stats-ticker{display:flex;gap:32px;justify-content:center;margin-bottom:24px;flex-wrap:wrap;}
    .stat-item{text-align:center;animation:stat-float 3s ease-in-out infinite alternate;}
    .stat-item:nth-child(2){animation-delay:-1s;}.stat-item:nth-child(3){animation-delay:-2s;}
    @keyframes stat-float{0%{transform:translateY(0);}100%{transform:translateY(-7px);}}
    .stat-num{font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFD700;line-height:1;text-shadow:0 0 20px rgba(255,215,0,0.5);}
    .stat-label{font-family:'Space Mono',monospace;font-size:10px;color:#ffffff;letter-spacing:2px;text-transform:uppercase;margin-top:2px;}

    .gw-divider{width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.4),transparent);margin:8px 0 28px;}

    /* HOW IT WORKS expanded */
    .how-expand{background:rgba(0,0,0,0.6);border:1px solid rgba(255,215,0,0.3);border-radius:20px;padding:24px;margin-top:12px;}
    .how-step{margin-bottom:18px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.08);}
    .how-step:last-child{margin-bottom:0;padding-bottom:0;border-bottom:none;}
    .how-step-icon{font-size:28px;display:block;margin-bottom:6px;}
    .how-step-title{font-family:'Bebas Neue',sans-serif;font-size:22px;color:#FFD700;letter-spacing:2px;margin-bottom:4px;}
    .how-step-desc{font-family:'Space Mono',monospace;font-size:12px;color:#ffffff;line-height:1.7;}

    /* MODE CARDS */
    .mode-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:16px;}
    .mode-card{background:rgba(255,255,255,0.04);border:2px solid rgba(255,215,0,0.2);border-radius:18px;padding:20px 16px;text-align:center;cursor:pointer;transition:all 0.2s;}
    .mode-card:hover{background:rgba(255,215,0,0.08);border-color:rgba(255,215,0,0.5);}
    .mode-emoji{font-size:36px;display:block;margin-bottom:10px;}
    .mode-name{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:3px;color:#FFD700;margin-bottom:8px;}
    .mode-desc{font-family:'Space Mono',monospace;font-size:11px;color:#ffffff;line-height:1.6;}

    /* CHIPS */
    .chip-section-label{font-family:'Space Mono',monospace;font-size:10px;color:#ffffff;letter-spacing:2px;text-transform:uppercase;margin:16px 0 8px;}
    .chip-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;}
    .chip{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.25);border-radius:99px;padding:5px 13px;font-size:11px;color:#ffffff;font-family:'Space Mono',monospace;letter-spacing:1px;}

    .default-hint{font-family:'Space Mono',monospace;font-size:11px;color:#ffffff;margin-top:6px;line-height:1.7;}
    .default-hint strong{color:#FFD700;}

    /* INPUTS — black text on white */
    .stTextInput>div>div>input{background:#ffffff!important;border:2px solid rgba(255,215,0,0.5)!important;border-radius:10px!important;color:#000000!important;font-family:'Space Mono',monospace!important;font-size:14px!important;padding:12px 16px!important;caret-color:#000000!important;}
    .stTextInput>div>div>input::placeholder{color:#666666!important;}
    .stTextInput>div>div>input:focus{border-color:#FFD700!important;box-shadow:0 0 20px rgba(255,215,0,0.25)!important;}
    .stTextInput label{font-family:'Space Mono',monospace!important;font-size:11px!important;letter-spacing:3px!important;color:#ffffff!important;text-transform:uppercase!important;}

    div.stButton>button{background:linear-gradient(135deg,#FFD700,#FF8C00)!important;border:none!important;color:#000000!important;font-family:'Bebas Neue',sans-serif!important;font-size:24px!important;letter-spacing:4px!important;padding:18px!important;border-radius:14px!important;width:100%!important;box-shadow:0 0 35px rgba(255,215,0,0.4)!important;transition:all 0.3s!important;margin-top:12px!important;}
    div.stButton>button:hover{transform:scale(1.02)!important;box-shadow:0 0 60px rgba(255,215,0,0.7)!important;}
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
        # HOW IT WORKS toggle button
        if st.button("⚡ HOW DOES THIS WORK?", key="how_toggle"):
            st.session_state.how_open = not st.session_state.how_open

        if st.session_state.how_open:
            st.markdown("""
            <div class="how-expand">
                <div class="how-step">
                    <span class="how-step-icon">🌌</span>
                    <div class="how-step-title">1 — PICK YOUR UNIVERSE</div>
                    <div class="how-step-desc">ANY universe. AI builds it instantly. Colors, currency, abilities, storyline — all yours.</div>
                </div>
                <div class="how-step">
                    <span class="how-step-icon">⏱</span>
                    <div class="how-step-title">2 — STUDY FOR 30 SECONDS</div>
                    <div class="how-step-desc">Work. Study. Do anything productive. Get paid in universe currency. Real rewards.</div>
                </div>
                <div class="how-step">
                    <span class="how-step-icon">📸</span>
                    <div class="how-step-title">3 — PROVE IT. COLLECT IT.</div>
                    <div class="how-step-desc">Upload proof. No proof = no coins. Simple. Then spin the wheel. Battle. Hatch eggs. Go insane.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # MODE SELECTION
        st.markdown("""
        <div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:4px;text-shadow:0 0 20px rgba(255,215,0,0.5)'>⚡ CHOOSE YOUR MODE</div>
        <div class='mode-grid'>
            <div class='mode-card'>
                <span class='mode-emoji'>⚡</span>
                <div class='mode-name'>CHILL</div>
                <div class='mode-desc'>Missions. Currency. Level up.<br>Clean. Simple. No stress.</div>
            </div>
            <div class='mode-card'>
                <span class='mode-emoji'>🔥</span>
                <div class='mode-name'>GRINDER</div>
                <div class='mode-desc'>Adds Battles, Abilities,<br>Monster Hatching & Achievements.</div>
            </div>
            <div class='mode-card'>
                <span class='mode-emoji'>💀</span>
                <div class='mode-name'>OBSESSED</div>
                <div class='mode-desc'>EVERYTHING. Full chaos.<br>Maximum power. No limits.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        mode_col1, mode_col2, mode_col3 = st.columns(3)
        with mode_col1:
            if st.button("⚡ CHILL", key="mode_chill"):
                st.session_state.game_mode = "chill"
        with mode_col2:
            if st.button("🔥 GRINDER", key="mode_grinder"):
                st.session_state.game_mode = "grinder"
        with mode_col3:
            if st.button("💀 OBSESSED", key="mode_obsessed"):
                st.session_state.game_mode = "obsessed"

        if st.session_state.game_mode:
            mode_labels = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}
            st.success(f"MODE SELECTED: {mode_labels[st.session_state.game_mode]} ✅")

        st.markdown("<br>", unsafe_allow_html=True)

        name_input  = st.text_input("⚡ Champion Name", placeholder="What are you called?", key="gw_name")
        theme_input = st.text_input("🌌 Your Universe", placeholder="Leave empty for INFINITE POWER · or type anything: Naruto, F1, Nike, Medieval Space War...", key="gw_theme")

        # FIDGET SPINNERS — ULTRA HYPER MEGA EDITION
        import streamlit.components.v1 as components
        _SPINNER_HTML = '<style>\n@import url(\'https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap\');\n*{box-sizing:border-box;margin:0;padding:0;}\nbody{background:transparent;}\n#universe{width:100%;height:330px;background:radial-gradient(ellipse at 50% 60%,#0a0020 0%,#000008 70%,#000000 100%);border-radius:16px;border:1px solid rgba(255,255,255,0.07);position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;}\n#rack{display:flex;gap:14px;justify-content:center;align-items:center;z-index:2;position:relative;padding:10px 0;}\n.slot{display:flex;flex-direction:column;align-items:center;gap:4px;}\n.slbl{font-family:Orbitron,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.4);}\n.srpm{font-family:Orbitron,monospace;font-size:8px;letter-spacing:1px;min-height:13px;text-align:center;}\n.nbtn{padding:4px 10px;font-size:7px;font-family:Orbitron,monospace;border-radius:6px;cursor:pointer;letter-spacing:2px;border:1.5px solid;background:rgba(0,0,0,0.6);transition:all 0.15s;margin-top:2px;}\n.nbtn:hover{transform:scale(1.09);filter:brightness(1.5);}\n#fl{position:absolute;bottom:0;left:0;width:100%;height:2px;z-index:1;animation:fla 2s linear infinite;}\n@keyframes fla{0%{filter:hue-rotate(0deg);background:linear-gradient(90deg,transparent,#FFD700,#FF4400,#FF00FF,#00FFFF,transparent);}100%{filter:hue-rotate(360deg);background:linear-gradient(90deg,transparent,#FFD700,#FF4400,#FF00FF,#00FFFF,transparent);}}\n</style>\n<div id="universe">\n<canvas id="stars" style="position:absolute;top:0;left:0;pointer-events:none;z-index:0" width="900" height="330"></canvas>\n<div id="rack"></div>\n<div id="fl"></div>\n</div>\n<script>\nvar sc=document.getElementById(\'stars\'),sctx=sc.getContext(\'2d\');\nvar STARS=[];for(var i=0;i<100;i++)STARS.push({x:Math.random()*900,y:Math.random()*330,r:Math.random()*1.3+0.3,a:Math.random(),da:Math.random()*0.007+0.002,col:\'hsl(\'+(180+Math.random()*80)+\',80%,90%)\'});\nfunction dS(){sctx.clearRect(0,0,900,330);STARS.forEach(function(s){s.a+=s.da;if(s.a>1||s.a<0)s.da*=-1;sctx.globalAlpha=s.a*0.75;sctx.beginPath();sctx.arc(s.x,s.y,s.r,0,Math.PI*2);sctx.fillStyle=s.col;sctx.fill();});sctx.globalAlpha=1;}\nvar DF=[\n  {id:\'s0\',sz:72,lbl:\'SOLAR FLARE\',nuke:false,bv:0.34,bl:4,sh:\'drop\',p:[\'#FF6600\',\'#FF2200\',\'#FFD700\',\'#FF8800\'],gw:\'#FF4400\',rm:\'#FFD700\',hb:\'#FFF\',tr:12,pt:true},\n  {id:\'s1\',sz:62,lbl:\'VOID STORM\', nuke:false,bv:0.44,bl:6,sh:\'wing\',p:[\'#8800FF\',\'#4400CC\',\'#CC00FF\',\'#FF44FF\'],gw:\'#AA00FF\',rm:\'#FF88FF\',hb:\'#FFF\',tr:16,pt:true},\n  {id:\'s2\',sz:66,lbl:\'MATRIX\',     nuke:false,bv:0.38,bl:3,sh:\'crys\',p:[\'#00FF44\',\'#00CC33\',\'#00FF88\',\'#AAFFCC\'],gw:\'#00FF44\',rm:\'#88FFBB\',hb:\'#111\',tr:10,pt:false},\n  {id:\'s3\',sz:60,lbl:\'NOVA PULSE\', nuke:false,bv:0.58,bl:5,sh:\'blad\',p:[\'#00CCFF\',\'#0088FF\',\'#00FFEE\',\'#88DDFF\'],gw:\'#00CCFF\',rm:\'#AAEEFF\',hb:\'#003\',tr:14,pt:true},\n  {id:\'s4\',sz:70,lbl:\'TITAN WARP\', nuke:false,bv:0.30,bl:7,sh:\'fan\', p:[\'#FFD700\',\'#FF4400\',\'#FF8800\',\'#FFEEAA\'],gw:\'#FFD700\',rm:\'#FF4400\',hb:\'#210\',tr:18,pt:true},\n  {id:\'s5\',sz:65,lbl:\'HYPER NUKE\', nuke:true, nv:3.8, bv:0.14,bl:4,sh:\'drop\',p:[\'#FF0044\',\'#FF4400\',\'#FF0088\',\'#FF8800\'],gw:\'#FF0044\',rm:\'#F8A\',hb:\'#FFF\',tr:20,pt:true},\n  {id:\'s6\',sz:76,lbl:\'OMEGA NUKE\', nuke:true, nv:7.0, bv:0.08,bl:8,sh:\'fan\', p:[\'#FFF\',\'#FFD700\',\'#FF2200\',\'#FA0\'],gw:\'#FFF\',rm:\'#FFD700\',hb:\'#000\',tr:30,pt:true}\n];\nvar ST={},TR={};\nvar rack=document.getElementById(\'rack\');\nDF.forEach(function(sp){\n  ST[sp.id]={a:Math.random()*6.28,v:sp.bv+Math.random()*0.06,dg:false,lA:0,lT:0};\n  TR[sp.id]=[];\n  var slot=document.createElement(\'div\');slot.className=\'slot\';\n  var cv=document.createElement(\'canvas\');cv.id=\'c_\'+sp.id;cv.width=sp.sz*2;cv.height=sp.sz*2;cv.style.cssText=\'cursor:grab;border-radius:50%;display:block;\';\n  var lb=document.createElement(\'div\');lb.className=\'slbl\';lb.textContent=sp.lbl;\n  var rm=document.createElement(\'div\');rm.id=\'r_\'+sp.id;rm.className=\'srpm\';rm.style.color=sp.gw;\n  slot.appendChild(cv);slot.appendChild(lb);slot.appendChild(rm);\n  if(sp.nuke){var btn=document.createElement(\'button\');btn.className=\'nbtn\';btn.textContent=sp.id===\'s6\'?\'DETONATE\':\'IGNITE\';btn.style.borderColor=sp.gw;btn.style.color=sp.gw;btn.onclick=(function(sid,nv){return function(){ST[sid].v=nv;shk();};})(sp.id,sp.nv);slot.appendChild(btn);}\n  rack.appendChild(slot);\n  function ga(e,c){var r=c.getBoundingClientRect();var x=(e.clientX||(e.touches&&e.touches[0].clientX)||0)-r.left-r.width/2;var y=(e.clientY||(e.touches&&e.touches[0].clientY)||0)-r.top-r.height/2;return Math.atan2(y,x);}\n  cv.addEventListener(\'mousedown\',function(e){var s=ST[sp.id];s.dg=true;s.lA=ga(e,cv);s.lT=performance.now();cv.style.cursor=\'grabbing\';});\n  window.addEventListener(\'mousemove\',(function(sid){return function(e){var s=ST[sid];if(!s.dg)return;var now=performance.now();var cv2=document.getElementById(\'c_\'+sid);var a=ga(e,cv2);var d=a-s.lA;if(d>Math.PI)d-=6.28;if(d<-Math.PI)d+=6.28;s.v=d/Math.max(now-s.lT,1)*20;s.a+=d;s.lA=a;s.lT=now;};})(sp.id));\n  window.addEventListener(\'mouseup\',(function(sid){return function(){ST[sid].dg=false;document.getElementById(\'c_\'+sid).style.cursor=\'grab\';};})(sp.id));\n  cv.addEventListener(\'touchstart\',function(e){var s=ST[sp.id];s.dg=true;s.lA=ga(e,cv);s.lT=performance.now();e.preventDefault();},{passive:false});\n  window.addEventListener(\'touchmove\',(function(sid){return function(e){var s=ST[sid];if(!s.dg)return;var now=performance.now();var cv2=document.getElementById(\'c_\'+sid);var a=ga(e,cv2);var d=a-s.lA;if(d>Math.PI)d-=6.28;if(d<-Math.PI)d+=6.28;s.v=d/Math.max(now-s.lT,1)*20;s.a+=d;s.lA=a;s.lT=now;e.preventDefault();};})(sp.id),{passive:false});\n  window.addEventListener(\'touchend\',(function(sid){return function(){ST[sid].dg=false;};})(sp.id));\n});\nvar shakeN=0;\nfunction shk(){shakeN=16;var u=document.getElementById(\'universe\');(function f(){if(shakeN<=0){u.style.transform=\'\';return;}u.style.transform=\'translate(\'+(Math.random()-.5)*shakeN*.7+\'px,\'+(Math.random()-.5)*shakeN*.4+\'px)\';shakeN--;requestAnimationFrame(f);})();}\nfunction draw(sp,angle,vel){\n  var cv=document.getElementById(\'c_\'+sp.id);if(!cv)return;\n  var ctx=cv.getContext(\'2d\'),sz=sp.sz,cx=sz,cy=sz,r=sz-5,spd=Math.abs(vel);\n  ctx.clearRect(0,0,sz*2,sz*2);\n  if(spd>0.04){var gg=ctx.createRadialGradient(cx,cy,r,cx,cy,r+5+spd*4);gg.addColorStop(0,sp.gw+\'77\');gg.addColorStop(1,sp.gw+\'00\');ctx.beginPath();ctx.arc(cx,cy,r+5+spd*4,0,Math.PI*2);ctx.fillStyle=gg;ctx.fill();}\n  var tr=TR[sp.id];tr.push(angle);if(tr.length>sp.tr)tr.shift();\n  if(spd>0.1&&tr.length>2){for(var ti=0;ti<tr.length-1;ti++){var ta=tr[ti],frac=ti/tr.length;for(var bi=0;bi<sp.bl;bi++){var ba2=ta+(bi*6.28/sp.bl);ctx.save();ctx.translate(cx,cy);ctx.rotate(ba2);ctx.globalAlpha=frac*0.18*Math.min(spd*1.5,1);ctx.beginPath();ctx.ellipse(r*.38,0,r*.36,r*.15,0,0,Math.PI*2);ctx.fillStyle=sp.p[0];ctx.fill();ctx.restore();}}ctx.globalAlpha=1;}\n  for(var i=0;i<sp.bl;i++){\n    var ba=angle+(i*6.28/sp.bl);\n    ctx.save();ctx.translate(cx,cy);ctx.rotate(ba);\n    var g=ctx.createLinearGradient(0,-r*.08,r*.82,r*.08);\n    g.addColorStop(0,sp.p[0]);g.addColorStop(.45,sp.p[1%sp.p.length]);g.addColorStop(.75,sp.p[2%sp.p.length]);g.addColorStop(1,sp.p[3%sp.p.length]+\'22\');\n    ctx.fillStyle=g;ctx.beginPath();\n    if(sp.sh===\'drop\'){ctx.ellipse(r*.42,0,r*.42,r*.19,0,0,Math.PI*2);}\n    else if(sp.sh===\'wing\'){ctx.moveTo(0,0);ctx.bezierCurveTo(r*.2,-r*.28,r*.7,-r*.22,r*.82,0);ctx.bezierCurveTo(r*.7,r*.22,r*.2,r*.28,0,0);ctx.closePath();}\n    else if(sp.sh===\'crys\'){ctx.moveTo(r*.08,0);ctx.lineTo(r*.38,-r*.22);ctx.lineTo(r*.82,0);ctx.lineTo(r*.38,r*.22);ctx.closePath();}\n    else if(sp.sh===\'blad\'){ctx.moveTo(0,-r*.05);ctx.lineTo(r*.78,-r*.12);ctx.lineTo(r*.82,0);ctx.lineTo(r*.78,r*.12);ctx.lineTo(0,r*.05);ctx.closePath();}\n    else{ctx.ellipse(r*.40,0,r*.40,r*.22,0,0,Math.PI*2);}\n    ctx.fill();ctx.strokeStyle=sp.p[0]+\'99\';ctx.lineWidth=1.2;ctx.stroke();\n    if(spd>0.2){ctx.globalAlpha=Math.min((spd-.2)*.4,.45);ctx.fillStyle=sp.rm;ctx.fill();ctx.globalAlpha=1;}\n    ctx.restore();\n  }\n  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.strokeStyle=sp.rm+(spd>.25?\'BB\':\'33\');ctx.lineWidth=spd>.4?2.5:1.5;ctx.stroke();\n  if(sp.pt&&spd>0.3){var pc=Math.floor(spd*5);for(var pi=0;pi<pc;pi++){var pa=angle*3.5+pi*2.0+performance.now()*.0015;var pr=r*(.65+Math.random()*.28);var px=cx+Math.cos(pa)*pr,py=cy+Math.sin(pa)*pr;ctx.beginPath();ctx.arc(px,py,1+Math.random()*1.5,0,Math.PI*2);ctx.fillStyle=sp.p[pi%sp.p.length];ctx.globalAlpha=.65+Math.random()*.3;ctx.fill();ctx.globalAlpha=1;}}\n  var hg=ctx.createRadialGradient(cx-r*.04,cy-r*.04,1,cx,cy,r*.20);hg.addColorStop(0,\'#fff\');hg.addColorStop(.4,sp.p[0]);hg.addColorStop(1,sp.hb);ctx.beginPath();ctx.arc(cx,cy,r*.19,0,Math.PI*2);ctx.fillStyle=hg;ctx.fill();ctx.beginPath();ctx.arc(cx,cy,r*.07,0,Math.PI*2);ctx.fillStyle=\'#fff6\';ctx.fill();\n  var re=document.getElementById(\'r_\'+sp.id);if(re){var rv=Math.abs(vel*60/(Math.PI*2)*60);if(rv>8){re.textContent=Math.round(rv).toLocaleString()+\' RPM\';re.style.color=rv>9000?\'#F00\':rv>4000?\'#F80\':rv>1200?\'#FFD700\':sp.gw;}else{re.textContent=sp.nuke?\'TAP TO IGNITE\':\'\\u221e ETERNAL\';re.style.color=\'rgba(255,255,255,0.25)\';}}}\nvar AF=0.999992,NF=0.9985;\nfunction loop(){\n  dS();\n  DF.forEach(function(sp){var s=ST[sp.id];if(!s.dg){s.v*=sp.nuke?NF:AF;if(Math.abs(s.v)<sp.bv)s.v=sp.bv;s.a+=s.v;}draw(sp,s.a,s.v);});\n  requestAnimationFrame(loop);\n}\nloop();\n</script>'
        components.html(_SPINNER_HTML, height=345)


        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name to begin.")
            elif not st.session_state.game_mode:
                st.error("Pick your mode first — CHILL, GRINDER, or OBSESSED!")
            else:
                theme_val    = theme_input.strip()
                display_name = theme_val if theme_val else DEFAULT_UNIVERSE_NAME
                with st.spinner(f"🌌 Loading {display_name.upper()}..."):
                    world_data = resolve_universe(theme_val)
                st.session_state.user_name  = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color","#FFD700")
                st.session_state.user_theme = display_name
                st.rerun()

    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP SETUP
# ─────────────────────────────────────────────────────────────────────────────
MODE   = st.session_state.game_mode or "chill"
wd     = st.session_state.world_data
BG     = st.session_state.get("bg_color","#ffffff")
RAW_C  = st.session_state.vibe_color
C      = readable_color(RAW_C, BG)
TEXT   = text_on(BG)
MUTED  = "#444444" if is_light(BG) else "#cccccc"
currency = wd.get("currency","Credits")

# ── FREE SPIN ON FIRST LOAD ───────────────────────────────────────────────────
if st.session_state.get("first_session", False):
    st.session_state.first_session = False
    st.session_state.spins_left = max(st.session_state.get("spins_left",0), 1)
    st.session_state.spinner_available = True


# Card background: solid dark on light page, solid light on dark page
CARDBG   = "#1a1a1a" if is_light(BG) else "#f0f0f0"
CARDTEXT = "#ffffff" if is_light(BG) else "#000000"

# Extract RGB components of theme color for card backgrounds
_ch = C.lstrip('#')
try:
    CR, CG, CB = int(_ch[0:2],16), int(_ch[2:4],16), int(_ch[4:6],16)
except:
    CR, CG, CB = 255, 215, 0

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');

html,body,[data-testid="stAppViewContainer"]{{background:{BG}!important;color:{TEXT}!important;font-family:'Space Mono',monospace;}}
[data-testid="stHeader"],[data-testid="stToolbar"]{{background:transparent!important;}}

/* SIDEBAR — always dark, always white text, no exceptions */
[data-testid="stSidebar"]{{background:#111111!important;}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] b,
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a {{color:#ffffff!important;}}
/* Sidebar buttons — compact, white text on dark */
[data-testid="stSidebar"] div.stButton>button{{
    border:2px solid {C}!important;
    background:#1a1a1a!important;
    color:#ffffff!important;
    font-family:'Bebas Neue',sans-serif!important;
    font-size:16px!important;
    letter-spacing:2px!important;
    padding:10px 16px!important;
    border-radius:10px!important;
    animation:none!important;
    width:100%!important;
    margin-bottom:6px!important;
}}

#MainMenu,footer{{visibility:hidden;}}

input,textarea{{background:#ffffff!important;color:#000000!important;caret-color:#000000!important;border:2px solid {C}!important;border-radius:10px!important;font-family:'Space Mono',monospace!important;font-size:14px!important;padding:10px 14px!important;}}
input::placeholder,textarea::placeholder{{color:#666666!important;}}
input:focus,textarea:focus{{border-color:{C}!important;box-shadow:0 0 15px rgba(255,215,0,0.2)!important;outline:none!important;}}
label,.stTextInput label,.stSelectbox label,.stTextArea label,.stFileUploader label{{color:{TEXT}!important;font-family:'Space Mono',monospace!important;font-size:11px!important;letter-spacing:2px!important;}}

@keyframes titan-pulse{{
    0%  {{box-shadow:0 0 20px {C},inset 0 0 10px {C};border-color:{C};}}
    50% {{box-shadow:0 0 80px {C},inset 0 0 40px {C};border-color:#ffffff;}}
    100%{{box-shadow:0 0 20px {C},inset 0 0 10px {C};border-color:{C};}}
}}
div.stButton>button{{border:6px solid {C}!important;background:#000000!important;color:#ffffff!important;font-family:'Bebas Neue',sans-serif!important;font-size:28px!important;letter-spacing:4px!important;padding:50px 30px!important;border-radius:40px!important;animation:titan-pulse 2.5s infinite ease-in-out!important;width:100%;text-transform:uppercase;transition:transform 0.3s;margin-bottom:20px;}}
div.stButton>button:hover{{transform:scale(1.02);}}

/* CARDS — always #111 background, always white text. No exceptions. */
.metric-card,
.shop-card,
.ach-card,
.monster-card,
.secret-card {{
    background:#111111!important;
    border:2px solid {C}!important;
    border-radius:14px!important;
    padding:18px!important;
    margin-bottom:12px!important;
    color:#ffffff!important;
}}
.metric-card *,
.shop-card *,
.ach-card *,
.monster-card *,
.secret-card * {{
    color:#ffffff!important;
}}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>⚡ TITAN HUB</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>CHAMPION:</b> {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>UNIVERSE:</b> {st.session_state.user_theme}</p>", unsafe_allow_html=True)
    mode_badge = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}.get(MODE,"⚡ CHILL")
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>MODE:</b> {mode_badge}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>RANK:</b> {st.session_state.sub_tier.upper()}</p>", unsafe_allow_html=True)

    st.markdown(f"""<div class='metric-card'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C}'>{st.session_state.gold:.1f}</div>
        <div style='font-size:10px;color:#ffffff;letter-spacing:2px'>{currency.upper()}</div>
        <div style='font-size:11px;color:#ffffff;margin-top:4px'>XP: {st.session_state.xp} · LVL {st.session_state.level}</div>
    </div>""", unsafe_allow_html=True)

    st.write("---")
    st.markdown(f"<p style='color:#ffffff;font-weight:bold'>👑 ELITE CODE</p>", unsafe_allow_html=True)
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "4RJ1TV51Z" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3
        st.success("💀 ELITE STATUS SECURED! 3× everything activated."); st.balloons(); time.sleep(1); st.rerun()
    if code == "1TR5LG89D" and st.session_state.sub_tier not in ("Elite","Premium"):
        st.session_state.sub_tier = "Premium"; st.session_state.sub_multiplier = 2
        st.success("⚡ PREMIUM STATUS SECURED! 2× everything activated."); st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    # NAV TABS based on mode
    if st.button("🚀 MISSION HUB",  key="nav_hub"):      st.session_state.view = "main";       st.rerun()
    if st.button("⚔️ BATTLE",       key="nav_battle"):   st.session_state.view = "battle";     st.rerun()
    if st.button("🎰 SPINNER",      key="nav_spin"):     st.session_state.view = "spinner";    st.rerun()
    if st.button("🛒 SHOP",          key="nav_shop"):     st.session_state.view = "shop";       st.rerun()
    if st.button("📖 STORY",         key="nav_story"):    st.session_state.view = "story";      st.rerun()
    if st.button("🔮 SECRETS",      key="nav_secrets"):  st.session_state.view = "secrets";    st.rerun()
    if st.button("💬 FEEDBACK",     key="nav_feedback"): st.session_state.view = "feedback";   st.rerun()

    if MODE in ("grinder","obsessed"):
        if st.button("🏆 ACHIEVEMENTS", key="nav_ach"):  st.session_state.view = "achievements"; st.rerun()
        if st.button("🥚 INCUBATOR",    key="nav_inc"):  st.session_state.view = "incubator";    st.rerun()

    if MODE == "obsessed":
        if st.button("📖 MANUAL",   key="nav_manual"):  st.session_state.view = "manual";  st.rerun()
        if st.button("💳 PLANS",    key="nav_plans"):   st.session_state.view = "plans";   st.rerun()

    st.write("---")
    st.markdown(f"<p style='color:#ffffff;font-weight:bold'>🎨 BACKGROUND</p>", unsafe_allow_html=True)
    new_bg = st.color_picker("", value=st.session_state.get("bg_color","#ffffff"), key="bg_picker", label_visibility="collapsed")
    if new_bg != st.session_state.get("bg_color","#ffffff"):
        st.session_state.bg_color = new_bg; st.rerun()

    st.markdown(f"<p style='color:#ffffff;font-weight:bold'>🌈 THEME COLOR</p>", unsafe_allow_html=True)
    new_tc = st.color_picker("", value=st.session_state.vibe_color, key="theme_picker", label_visibility="collapsed")
    if new_tc != st.session_state.vibe_color:
        st.session_state.vibe_color = new_tc; st.rerun()

    st.write("---")
    st.markdown(f"<p style='color:#ffffff;font-weight:bold'>🌐 SWITCH UNIVERSE</p>", unsafe_allow_html=True)
    new_theme = st.text_input("New universe:", placeholder="Try anything...", key="switch_theme")
    if st.button("🔄 WARP", key="warp_btn"):
        if new_theme.strip():
            with st.spinner(f"Warping..."):
                world_data = resolve_universe(new_theme.strip())
            st.session_state.world_data = world_data
            st.session_state.vibe_color = world_data.get("color","#FFD700")
            st.session_state.user_theme = new_theme.strip()
            st.rerun()

    st.write("---")
    st.markdown(f"<p style='color:#ffffff;font-weight:bold'>🚨 RESET</p>", unsafe_allow_html=True)
    reset_input = st.text_input("Type RESET to confirm:", key="reset_confirm_input", placeholder="RESET")
    if st.button("🚨 RESET ALL", key="reset_btn"):
        if reset_input.strip().upper() == "RESET":
            st.session_state.clear(); st.rerun()
        else:
            st.error("Type RESET first.")

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENT CHECK + SECRET REVEAL
# ─────────────────────────────────────────────────────────────────────────────
new_ach = check_achievements(st.session_state)
for ach in new_ach:
    st.toast(f"🏆 ACHIEVEMENT UNLOCKED: {ach['name']}", icon="🏆")

if st.session_state.show_secret:
    st.markdown(f"""<div class='secret-card'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:{C};letter-spacing:3px;margin-bottom:10px'>🔮 UNIVERSE SECRET UNLOCKED</div>
        {st.session_state.show_secret}
    </div>""", unsafe_allow_html=True)
    if st.button("🔮 SICK. CLOSE THIS.", key="close_secret"):
        st.session_state.show_secret = None
        st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};
font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>
{st.session_state.user_theme.upper()}</h1>
<p style='text-align:center;font-size:15px;color:#ffffff;margin-top:4px'>{wd.get("description","A realm of infinite power.")}</p>
""", unsafe_allow_html=True)
st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# BATTLE SCREEN — Godot WebGL embedded + fallback turn-based
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("battle_state") == "ready" or st.session_state.view == "battle":

    # Freeze monster at battle start
    if "current_battle" not in st.session_state or st.session_state.current_battle is None:
        monster_roll = random.randint(1,100)
        if monster_roll > 90:
            mon = {"name":f"Legendary {st.session_state.user_theme} Titan","hp":7,"reward":20,"rarity":"Legendary"}
        elif monster_roll > 70:
            mon = {"name":f"Epic {st.session_state.user_theme} Warlord",  "hp":5,"reward":12,"rarity":"Epic"}
        elif monster_roll > 40:
            mon = {"name":f"Rare {st.session_state.user_theme} Hunter",   "hp":4,"reward":8, "rarity":"Rare"}
        else:
            mon = {"name":f"{st.session_state.user_theme} Scout",         "hp":3,"reward":5, "rarity":"Common"}
        st.session_state.current_battle = {
            "monster": mon, "reward_paid": False,
            "hp_remaining": mon["hp"], "player_hp": 5, "turn": 0,
        }

    cb  = st.session_state.current_battle
    mon = cb["monster"]
    rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
    rc  = rarity_colors.get(mon["rarity"],"#ffffff")

    # Build Godot URL with universe params
    theme_enc   = st.session_state.user_theme.replace(" ","%20")
    currency_enc= currency.replace(" ","%20")
    color_hex   = C.lstrip("#")
    shield_enc  = wd.get("shield_name","Shield").replace(" ","%20")
    booster_enc = wd.get("booster_name","Boost").replace(" ","%20")
    sflavor_enc = wd.get("shield_flavor","").replace(" ","%20")
    bflavor_enc = wd.get("booster_flavor","").replace(" ","%20")
    bstyle      = wd.get("battle_style","turnbased")
    reward_val  = mon["reward"]
    rarity_val  = mon["rarity"]

    godot_url = (
        f"https://celebrated-genie-79733a.netlify.app"
        f"?universe={theme_enc}&currency={currency_enc}&color={color_hex}"
        f"&shield={shield_enc}&booster={booster_enc}"
        f"&sflavor={sflavor_enc}&bflavor={bflavor_enc}"
        f"&style={bstyle}&reward={reward_val}&rarity={rarity_val}"
    )

    st.markdown(f"""<div class='monster-card'>
        <div style='font-size:11px;color:{rc};letter-spacing:3px;font-family:Space Mono,monospace'>{mon["rarity"].upper()} ENCOUNTER</div>
        <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:{C};margin:6px 0'>{mon["name"].upper()}</div>
        <div style='font-size:12px;color:#ffffff'>Defeat to earn <span style='color:{C};font-weight:bold'>{mon["reward"]} {currency}</span>{"  · <span style='color:#aaaaaa;font-size:11px'>Reward claimed ✓</span>" if cb["reward_paid"] else ""}</div>
    </div>""", unsafe_allow_html=True)

    # Embed Godot game
    import streamlit.components.v1 as components
    components.html(f"""
    <style>
    body{{margin:0;background:#000;display:flex;flex-direction:column;align-items:center;}}
    #game-frame{{width:100%;max-width:800px;height:480px;border:2px solid {C};border-radius:12px;background:#000;}}
    #loading{{font-family:Space Mono,monospace;color:{C};font-size:13px;text-align:center;padding:16px;}}
    </style>
    <div id="loading">⚔️ LOADING BATTLE... ONE MOMENT</div>
    <iframe id="game-frame"
        src="{godot_url}"
        frameborder="0"
        allowfullscreen
        allow="autoplay; fullscreen *; monetization; xr-spatial-tracking"
        style="display:none"
        onload="document.getElementById('loading').style.display='none';this.style.display='block'">
    </iframe>
    <script>
    // Listen for battle result from Godot
    window.addEventListener('message', function(e) {{
        if(e.data && e.data.type === 'battleResult') {{
            window.parent.postMessage(e.data, '*');
        }}
    }});
    </script>
    """, height=520)

    col1, col2 = st.columns(2)
    with col1:
        if not cb["reward_paid"]:
            if st.button("✅ I WON — CLAIM REWARD", key="claim_win"):
                st.session_state.gold += mon["reward"]
                st.session_state.battles_won += 1
                cb["reward_paid"] = True
                st.session_state.incubator_eggs += 1
                st.session_state.battles_fought += 1
                st.session_state.spinner_available = True
                st.success(f"🏆 +{mon['reward']} {currency} claimed!")
                time.sleep(0.5); st.rerun()
        else:
            st.success("✅ Reward already claimed!")
    with col2:
        if st.button("⏩ SKIP BATTLE", key="skip_battle"):
            st.session_state.current_battle = None
            st.session_state.battle_state = None
            st.session_state.view = "main"
            st.rerun()

    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# VIEWS
# ─────────────────────────────────────────────────────────────────────────────
view = st.session_state.view



# ── OPENING STORY (shown once, immediately on first login) ────────────────────
if not st.session_state.get("opening_story_shown", True):
    theme_now = st.session_state.user_theme or "Infinite Power"
    client_os = get_claude_client()
    if client_os:
        try:
            resp_os = client_os.messages.create(
                model="claude-sonnet-4-5", max_tokens=220,
                messages=[{"role":"user","content":f'''You are the most gripping storyteller alive. Write the OPENING of an epic story set in the universe of: "{theme_now}". This is chapter 0 — the very beginning.

Rules:
- 3 sentences MAX. Short. Punchy. Cinematic.
- Reference the specific universe (characters, world, lore)
- End on a CLIFFHANGER that makes them physically unable to stop reading
- No titles, no formatting. Raw story text only.'''}]
            )
            opening_txt = resp_os.content[0].text.strip()
        except:
            opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened — something that was never meant to be found. And somehow... it knows your name."
    else:
        opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened — something that was never meant to be found. And somehow... it knows your name."

    st.session_state.opening_story_shown = True
    if "story_log" not in st.session_state or not st.session_state.story_log:
        if "story_log" not in st.session_state:
            st.session_state.story_log = []
        st.session_state.story_log.insert(0, opening_txt)

    st.markdown(f"""
    <div style='border:2px solid {C};border-radius:18px;padding:28px 32px;
        background:linear-gradient(135deg,#0a001a,#001a0a,#0a001a);
        text-align:center;margin:16px 0;animation:storyappear 0.8s ease-out;
        box-shadow:0 0 40px {C}55;'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:13px;letter-spacing:5px;
            color:{C};margin-bottom:14px'>⚡ CHAPTER 0 — THE BEGINNING ⚡</div>
        <div style='font-family:Space Mono,monospace;font-size:16px;color:#ffffff;
            line-height:1.9;font-style:italic'>{opening_txt}</div>
        <div style='margin-top:16px;font-family:Orbitron,monospace;font-size:10px;
            color:#FF4488;letter-spacing:3px;animation:blink 1.2s ease-in-out infinite'>
            ▼ TO BE CONTINUED... COMPLETE A MISSION ▼</div>
    </div>
    <style>
    @keyframes storyappear{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
    @keyframes blink{{0%,100%{{opacity:0.3}}50%{{opacity:1}}}}
    </style>
    """, unsafe_allow_html=True)

# ── STREAK DANGER WARNING (shown on all views) ────────────────────
if st.session_state.get("study_streak", 0) >= 2:
    today_str = _dt.date.today().isoformat()
    last_str  = st.session_state.get("last_active_date")
    if last_str and last_str != today_str:
        yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
        if last_str == yesterday:
            st.markdown(streak_danger_html(st.session_state.study_streak, C), unsafe_allow_html=True)

# ── LOOT BOX REVEAL ───────────────────────────────────────────────
if st.session_state.get("loot_pending") and st.session_state.get("loot_item"):
    item = st.session_state.loot_item
    st.markdown(loot_box_html(item["name"], item["rarity"], item.get("color","#FFD700")), unsafe_allow_html=True)
    time.sleep(0.1)
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        if st.button("⚡ CLAIM IT", key="claim_loot"):
            st.session_state.loot_pending = False
            st.session_state.loot_item = None
            st.rerun()
    st.stop()

# ── SCHOOL SHOP ───────────────────────────────────────────────────────────────
if view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🛒 TITAN SUPPLY SHOP</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:14px;font-family:Space Mono,monospace'>Spend your {currency} on real school supplies. Study harder → earn more → buy the tools that make you unstoppable.</p>", unsafe_allow_html=True)

    gold_now = st.session_state.gold
    st.markdown(f"<p style='text-align:center;color:{C};font-size:20px;font-family:Bebas Neue,sans-serif'>Your Balance: {gold_now:.1f} {currency}</p>", unsafe_allow_html=True)

    shop_items = [
        {"name":"📓 Notebook",        "desc":"College-ruled. Your future notes. Your future power.",   "price":50,  "real":"~$3 Amazon gift card"},
        {"name":"✏️ Pencil Pack",      "desc":"12 pencils. The weapon of every champion.",               "price":30,  "real":"~$2 Amazon gift card"},
        {"name":"📐 Calculator",       "desc":"Scientific calculator. Math becomes your superpower.",   "price":200, "real":"~$12 Amazon gift card"},
        {"name":"📚 Textbook Voucher", "desc":"Any textbook up to $25. Knowledge is the ultimate boss.", "price":500, "real":"$25 Amazon gift card"},
        {"name":"🖊️ Highlighters",    "desc":"5-color set. Color-code your way to genius.",             "price":40,  "real":"~$3 Amazon gift card"},
        {"name":"📋 Planner",          "desc":"Weekly planner. The organized mind conquers all.",        "price":80,  "real":"~$5 Amazon gift card"},
        {"name":"🎒 Backpack",         "desc":"The legendary carry. For the ultimate grinder.",          "price":800, "real":"$50 Amazon gift card"},
        {"name":"💻 Study Headphones", "desc":"Block out the world. Enter flow state.",                 "price":600, "real":"$40 Amazon gift card"},
    ]

    cols = st.columns(2)
    for i, item in enumerate(shop_items):
        with cols[i % 2]:
            can_buy = gold_now >= item["price"]
            border_col = C if can_buy else "#444444"
            st.markdown(f"""<div style='border:2px solid {border_col};border-radius:14px;padding:16px;
                background:linear-gradient(135deg,#0a0a1a,#1a0a2e);margin:8px 0;'>
                <div style='font-size:22px;font-family:Bebas Neue,sans-serif;color:{C if can_buy else "#888"};letter-spacing:2px'>{item['name']}</div>
                <div style='font-size:12px;color:#cccccc;font-family:Space Mono,monospace;margin:6px 0'>{item['desc']}</div>
                <div style='font-size:14px;color:{C};font-family:Bebas Neue,sans-serif'>{item['price']} {currency}</div>
                <div style='font-size:10px;color:#888;font-family:Space Mono,monospace'>Real value: {item['real']}</div>
                </div>""", unsafe_allow_html=True)
            if can_buy:
                if st.button(f"BUY {item['name']}", key=f"buy_{i}"):
                    st.session_state.gold -= item["price"]
                    st.balloons()
                    st.success(f"✅ {item['name']} purchased! Redeem = email us your username. We'll send the gift card within 24h.")
                    st.info("📧 Redemption coming soon — will be automated. For now DM on Discord.")
                    st.rerun()
            else:
                st.markdown(f"<p style='color:#666;font-size:11px;font-family:Space Mono'>Need {item['price']-gold_now:.0f} more {currency}</p>", unsafe_allow_html=True)

# ── STORY VIEW ────────────────────────────────────────────────────────────────
elif view == "story":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 YOUR UNIVERSE STORYLINE</h2>", unsafe_allow_html=True)
    theme_display = st.session_state.user_theme or "Unknown Universe"
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>Universe: <b style='color:{C}'>{theme_display}</b> · Chapter {st.session_state.story_chapter}</p>", unsafe_allow_html=True)

    if not st.session_state.story_log:
        st.markdown(f"<div style='text-align:center;padding:40px;color:#888;font-family:Space Mono,monospace'>Complete your first mission to begin the story...</div>", unsafe_allow_html=True)
    else:
        for i, chapter_text in enumerate(st.session_state.story_log):
            is_last = (i == len(st.session_state.story_log) - 1)
            is_twist = (i > 0 and (i+1) % 5 == 0)
            bg = f"linear-gradient(135deg,#1a0a2e,#0a1a0e)" if not is_twist else f"linear-gradient(135deg,#2e0a0a,#1a0a2e)"
            border = C if is_last else ("#FF2244" if is_twist else "#333")
            label = f"⚡ CHAPTER {i+1}" + (" — 🌀 PLOT TWIST" if is_twist else "")
            st.markdown(f"""<div style='border:2px solid {border};border-radius:14px;padding:20px;
                background:{bg};margin:10px 0;{"box-shadow:0 0 20px "+C+"44;" if is_last else ""}'>
                <div style='font-size:13px;font-family:Bebas Neue,sans-serif;color:{C if is_last else "#888"};
                    letter-spacing:3px;margin-bottom:10px'>{label}</div>
                <div style='font-size:15px;color:#ffffff;font-family:Space Mono,monospace;line-height:1.7'>{chapter_text}</div>
                {"<div style=\"margin-top:12px;color:#FF4488;font-size:11px;font-family:Space Mono\">⚠️ To be continued... complete another mission.</div>" if is_last else ""}
                </div>""", unsafe_allow_html=True)

# ── SECRETS ───────────────────────────────────────────────────────────────────
elif view == "secrets":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🔮 UNIVERSE SECRETS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace'>Every mission unlocks a secret. These are truths that will break your brain.</p>", unsafe_allow_html=True)
    seen = st.session_state.get("secret_queue",[])
    if seen:
        for s in reversed(seen):
            st.markdown(f"<div class='secret-card'>{s}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:14px'>Complete your first mission to unlock your first secret. 🔮</p>", unsafe_allow_html=True)

# ── ACHIEVEMENTS ──────────────────────────────────────────────────────────────
elif view == "achievements":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🏆 ACHIEVEMENTS</h2>", unsafe_allow_html=True)
    unlocked = st.session_state.get("unlocked_achievements", set())
    for ach in ACHIEVEMENTS:
        is_done = ach["id"] in unlocked
        border_col = C if is_done else MUTED
        opacity = "1.0" if is_done else "0.35"
        st.markdown(f"""<div class='ach-card' style='border-color:{border_col};opacity:{opacity}'>
            <span style='font-family:Bebas Neue,sans-serif;font-size:18px;color:{C}'>{ach["name"]}</span><br>
            <span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{ach["desc"]}</span>
        </div>""", unsafe_allow_html=True)

# ── INCUBATOR ─────────────────────────────────────────────────────────────────
elif view == "incubator":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🥚 INCUBATOR</h2>", unsafe_allow_html=True)
    eggs = st.session_state.incubator_eggs
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:{TEXT}'>You have <span style='color:{C};font-size:24px;font-family:Bebas Neue,sans-serif'>{eggs}</span> eggs ready to hatch.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;font-size:11px;color:#ffffff'>Earn eggs by completing missions and winning battles.</p>", unsafe_allow_html=True)

    # Show egg progress bars for all eggs waiting
    if eggs > 0:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-top:16px'>🥚 EGGS WAITING TO HATCH</h3>", unsafe_allow_html=True)
        rarity_weights = [("Legendary 🐉", "#FFD700", 4), ("Epic ✨", "#aa44ff", 13), ("Rare 💙", "#4488ff", 28), ("Common ⬜", "#aaaaaa", 55)]
        for egg_idx in range(min(eggs, 8)):  # show max 8 eggs
            # Each egg has a "preheat" progress bar based on its index
            warmth = min(100, (egg_idx + 1) * 15 + random.randint(5, 25) if egg_idx not in st.session_state.get("egg_warmth",{}) else st.session_state.egg_warmth[egg_idx])
            if "egg_warmth" not in st.session_state:
                st.session_state.egg_warmth = {}
            if egg_idx not in st.session_state.egg_warmth:
                st.session_state.egg_warmth[egg_idx] = warmth
            w = st.session_state.egg_warmth[egg_idx]
            bar_filled = int(w / 100 * 20)
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            # Guess rarity hint based on warmth
            if w >= 90:   hint = "🐉 LEGENDARY VIBES..."
            elif w >= 70: hint = "✨ Something Epic stirs..."
            elif w >= 45: hint = "💙 Rare energy detected"
            else:         hint = "⬜ Still warming up..."
            st.markdown(f"""<div class='ach-card'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <span style='font-size:20px'>🥚</span>
                    <span style='font-family:Space Mono,monospace;font-size:11px;color:#ffffff'>EGG #{egg_idx+1}</span>
                    <span style='font-family:Space Mono,monospace;font-size:10px;color:{C}'>{hint}</span>
                </div>
                <div style='margin-top:8px;font-family:Space Mono,monospace;font-size:12px;color:{C}'>{bar} {w}%</div>
            </div>""", unsafe_allow_html=True)
        if eggs > 8:
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:12px'>...and {eggs-8} more eggs waiting</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        _, hcol, _ = st.columns([1,2,1])
        with hcol:
            if st.button("🥚 HATCH EGG", key="hatch_egg"):
                monster = hatch_egg(st.session_state.user_theme)
                st.session_state.incubator_eggs -= 1
                st.session_state.eggs_hatched += 1
                reward = int(5 * monster["reward_mult"])
                st.session_state.gold += reward
                if monster["rarity"] == "Legendary":
                    st.session_state.legendary_hatched = True
                    st.balloons()
                st.session_state.hatched_monsters.append(monster)
                # Remove first egg warmth slot and shift down
                warmth_dict = st.session_state.get("egg_warmth", {})
                new_warmth = {i-1: v for i,v in warmth_dict.items() if i > 0}
                st.session_state.egg_warmth = new_warmth
                rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
                rc = rarity_colors.get(monster["rarity"],"#ffffff")
                st.markdown(f"""<div class='monster-card'>
                    <div style='font-size:36px'>{'🐉' if monster['rarity']=='Legendary' else '🐣'}</div>
                    <div style='font-size:11px;color:{rc};letter-spacing:3px;font-family:Space Mono,monospace'>{monster["rarity"].upper()} HATCHED!</div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:28px;color:{C}'>{monster["name"].upper()}</div>
                    <div style='font-size:13px;color:#ffffff'>+{reward} {currency} reward!</div>
                </div>""", unsafe_allow_html=True)
                time.sleep(0.5); st.rerun()

    if st.session_state.hatched_monsters:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-top:24px'>YOUR COLLECTION</h3>", unsafe_allow_html=True)
        rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
        for m in reversed(st.session_state.hatched_monsters[-10:]):
            rc = rarity_colors.get(m["rarity"],"#ffffff")
            st.markdown(f"<div class='ach-card'><span style='color:{rc};font-family:Bebas Neue,sans-serif;font-size:16px'>[{m['rarity'].upper()}]</span> <span style='color:#ffffff;font-family:Space Mono,monospace'>{m['name']}</span></div>", unsafe_allow_html=True)

# ── MANUAL ────────────────────────────────────────────────────────────────────
elif view == "manual":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 CHEAT CODE MANUAL</h2>", unsafe_allow_html=True)
    manual_items = [
        ("⏱", "MISSIONS", "30 SECONDS. WORK. UPLOAD PROOF. BOOM — PAID. THAT'S THE WHOLE THING."),
        ("⚖️", "THE TRIBUNAL", "NO PROOF = NO COINS. SCREENSHOT IT. PHOTO IT. WRITE IT. JUST SHOW SOMETHING."),
        ("🛒", "ARSENAL", "BUY SHIELD = NUKE YOUR DEBT. BUY BOOSTER = 3X MULTIPLIER. BUY BOTH = UNSTOPPABLE."),
        ("⚔️", "BATTLES", "EVERY MISSION = A BATTLE UNLOCKS. WIN = BONUS COINS + AN EGG. LOSE = TRY AGAIN."),
        ("🥚", "INCUBATOR", "HATCH EGGS. COMMON TO LEGENDARY. LEGENDARY IS BASICALLY IMPOSSIBLE. BASICALLY."),
        ("🔮", "SECRETS", "AFTER EVERY MISSION YOU LEARN SOMETHING THAT WILL GENUINELY BREAK YOUR BRAIN."),
        ("👑", "PREMIUM & ELITE", "UNLOCK PREMIUM OR ELITE IN THE PLANS TAB. YOUR CODE ACTIVATES IN THE SIDEBAR."),
        ("🌌", "SWITCH UNIVERSE", "BORED? WARP TO ANOTHER UNIVERSE ANYTIME. THE AI REBUILDS EVERYTHING INSTANTLY."),
        ("💳", "PLANS", "PREMIUM AND ELITE TIERS COMING SOON. MORE XP. MORE POWER. MORE EVERYTHING."),
    ]
    for icon, title, desc in manual_items:
        st.markdown(f"""<div class='ach-card'>
            <span style='font-size:24px'>{icon}</span>
            <span style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:2px;margin-left:8px'>{title}</span><br>
            <span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{desc}</span>
        </div>""", unsafe_allow_html=True)

# ── PLANS ─────────────────────────────────────────────────────────────────────
elif view == "plans":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💳 UPGRADE PLANS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#ffffff;font-size:12px'>Subscribe below · Then enter your code in the sidebar to activate instantly ⚡</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    p_col, e_col = st.columns(2)
    with p_col:
        st.markdown(f"""<div class='shop-card'>
            <div style='text-align:center;margin-bottom:16px'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>⚡ PREMIUM</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$5<span style='font-size:20px;color:#aaaaaa'>/mo</span></div>
                <div style='font-family:Space Mono,monospace;font-size:11px;color:#aaaaaa;margin-top:4px'>Cancel anytime</div>
            </div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>
                ✅ 2× XP on every mission<br>
                ✅ Rare+ ability upgrades<br>
                ✅ Extended mission timer options<br>
                ✅ Priority AI universe generation<br>
                ✅ Exclusive ⚡ Premium badge
            </div>
            <div style='background:#1a1a1a;border:1px solid #444;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'>
                <div style='font-family:Space Mono,monospace;font-size:10px;color:#aaaaaa;letter-spacing:2px;margin-bottom:4px'>AFTER PAYING — ENTER CODE IN SIDEBAR</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:4px'>1TR5LG89D</div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.link_button("⚡ SUBSCRIBE — PREMIUM $5/mo", "https://buy.stripe.com/7sY3co4RC36M0KY495dQQ02", use_container_width=True)

    with e_col:
        st.markdown(f"""<div class='shop-card' style='border-color:#FFD700'>
            <div style='text-align:center;margin-bottom:16px'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:#FFD700'>💀 ELITE</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$10<span style='font-size:20px;color:#aaaaaa'>/mo</span></div>
                <div style='font-family:Space Mono,monospace;font-size:11px;color:#aaaaaa;margin-top:4px'>Cancel anytime</div>
            </div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>
                ✅ 3× XP on every mission<br>
                ✅ ALL ability tiers unlocked<br>
                ✅ Full maximum customization<br>
                ✅ Legendary egg rate doubled<br>
                ✅ Exclusive 💀 Elite badge
            </div>
            <div style='background:#1a1a1a;border:1px solid #FFD700;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'>
                <div style='font-family:Space Mono,monospace;font-size:10px;color:#aaaaaa;letter-spacing:2px;margin-bottom:4px'>AFTER PAYING — ENTER CODE IN SIDEBAR</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:#FFD700;letter-spacing:4px'>4RJ1TV51Z</div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.link_button("💀 SUBSCRIBE — ELITE $10/mo", "https://buy.stripe.com/14A9AM83O0YE0KYgVRdQQ03", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class='ach-card' style='text-align:center'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:18px;color:{C};letter-spacing:3px'>HOW IT WORKS</div>
        <div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2;margin-top:8px'>
            1️⃣ Click your plan above → complete Stripe checkout<br>
            2️⃣ Come back here → go to the sidebar<br>
            3️⃣ Enter your activation code → status unlocks instantly ⚡
        </div>
    </div>""", unsafe_allow_html=True)

# ── SPINNER ───────────────────────────────────────────────────────────────────
elif view == "spinner":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🎰 LUCKY SPINNER</h2>", unsafe_allow_html=True)
    available = st.session_state.get('spins_left', 0) > 0 or st.session_state.spinner_available
    spins_remaining = st.session_state.get('spins_left', 1 if st.session_state.spinner_available else 0)
    if not available:
        st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace'>Complete a mission to unlock your spin! 🎰</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>You earned a spin! Hit the button and see what you get. 🔥</p>", unsafe_allow_html=True)

    # Animated JS spinner wheel embedded
    prize_labels = [p["label"] for p in SPINNER_PRIZES]
    prize_colors = [p["color"] for p in SPINNER_PRIZES]
    labels_js = str(prize_labels).replace("'",'"')
    colors_js = str(prize_colors).replace("'",'"')
    import streamlit.components.v1 as components
    components.html(f"""
    <style>
        body{{margin:0;background:transparent;display:flex;flex-direction:column;align-items:center;font-family:'Space Mono',monospace;}}
        canvas{{border-radius:50%;box-shadow:0 0 40px rgba(255,215,0,0.5);}}
        #spinBtn{{margin-top:20px;padding:16px 48px;font-size:22px;font-family:'Space Mono',monospace;font-weight:bold;background:linear-gradient(135deg,#FFD700,#FF8C00);border:none;border-radius:12px;cursor:pointer;color:#000;letter-spacing:2px;box-shadow:0 0 30px rgba(255,215,0,0.5);}}
        #spinBtn:disabled{{opacity:0.4;cursor:not-allowed;}}
        #result{{margin-top:16px;font-size:20px;color:#FFD700;font-family:Space Mono,monospace;letter-spacing:2px;text-align:center;min-height:30px;}}
    </style>
    <canvas id="wheel" width="320" height="320"></canvas>
    <button id="spinBtn" {"disabled" if not available else ""}>{"🔒 COMPLETE A MISSION" if not available else "🎰 SPIN IT"}</button>
    <div id="result"></div>
    <script>
    const labels = {labels_js};
    const colors = {colors_js};
    const canvas = document.getElementById('wheel');
    const ctx = canvas.getContext('2d');
    const n = labels.length;
    const arc = 2 * Math.PI / n;
    let currentAngle = 0;
    let spinning = false;

    function drawWheel(angle) {{
        ctx.clearRect(0,0,320,320);
        for(let i=0;i<n;i++) {{
            ctx.beginPath();
            ctx.moveTo(160,160);
            ctx.arc(160,160,150,angle+i*arc,angle+(i+1)*arc);
            ctx.fillStyle = colors[i];
            ctx.fill();
            ctx.strokeStyle='#111';ctx.lineWidth=2;ctx.stroke();
            ctx.save();
            ctx.translate(160,160);
            ctx.rotate(angle+(i+0.5)*arc);
            ctx.textAlign='right';
            ctx.fillStyle='#fff';
            ctx.font='bold 11px Space Mono,monospace';
            ctx.shadowColor='#000';ctx.shadowBlur=4;
            ctx.fillText(labels[i],140,5);
            ctx.restore();
        }}
        // Center circle
        ctx.beginPath();
        ctx.arc(160,160,22,0,2*Math.PI);
        ctx.fillStyle='#111';ctx.fill();
        ctx.strokeStyle='#FFD700';ctx.lineWidth=3;ctx.stroke();
        // Pointer
        ctx.beginPath();
        ctx.moveTo(300,150);ctx.lineTo(320,160);ctx.lineTo(300,170);
        ctx.fillStyle='#FFD700';ctx.fill();
    }}

    drawWheel(0);

    document.getElementById('spinBtn').onclick = function() {{
        if(spinning) return;
        spinning = true;
        this.disabled = true;
        document.getElementById('result').textContent = '';
        const extraSpins = (5 + Math.random()*5) * 2 * Math.PI;
        const duration = 4000 + Math.random()*2000;
        const start = performance.now();
        const startAngle = currentAngle;
        function animate(now) {{
            const elapsed = now - start;
            const progress = Math.min(elapsed/duration,1);
            const ease = 1 - Math.pow(1-progress,4);
            currentAngle = startAngle + extraSpins * ease;
            drawWheel(currentAngle);
            if(progress < 1) {{
                requestAnimationFrame(animate);
            }} else {{
                spinning = false;
                // Find winning segment
                const normalized = ((2*Math.PI) - (currentAngle % (2*Math.PI))) % (2*Math.PI);
                const idx = Math.floor(normalized / arc) % n;
                document.getElementById('result').textContent = '🎉 ' + labels[idx] + '!';
                // Send result to Streamlit
                window.parent.postMessage({{type:'spinResult',prize:labels[idx]}}, '*');
            }}
        }}
        requestAnimationFrame(animate);
    }};
    </script>
    """, height=460)

    # Spin button in Streamlit (actual prize logic)
    if available:
        _, sc, _ = st.columns([1,2,1])
        with sc:
            if st.button("🎰 CLAIM YOUR SPIN PRIZE", key="claim_spin"):
                prize = spin_wheel()
                st.session_state.spinner_available = False
                st.session_state.spinner_wins += 1

                if prize["type"] == "gold_mult":
                    bonus = st.session_state.pending_gold * prize["value"] if st.session_state.pending_gold else prize["value"] * 2
                    st.session_state.gold += bonus
                    msg = f"💰 {prize['label']}! +{bonus:.1f} {currency}!"
                elif prize["type"] == "gold_flat":
                    st.session_state.gold += prize["value"]
                    msg = f"⚡ +{prize['value']} {currency}!"
                elif prize["type"] == "egg_rare":
                    st.session_state.incubator_eggs += 1
                    msg = f"🥚 RARE EGG added to incubator!"
                elif prize["type"] == "egg_epic":
                    st.session_state.incubator_eggs += 1
                    msg = f"✨ EPIC EGG added to incubator!"
                elif prize["type"] == "ability":
                    if prize["value"] == "shield":
                        st.session_state.shield_bought = True
                        msg = f"🛡️ {wd.get('shield_name','SHIELD')} activated FREE!"
                    else:
                        st.session_state.booster_bought = True
                        st.session_state.sub_multiplier = max(st.session_state.sub_multiplier, 2)
                        msg = f"🚀 {wd.get('booster_name','BOOSTER')} activated FREE!"
                elif prize["type"] == "story_twist":
                    st.session_state.story_twist_pending = True
                    msg = "📖 STORY TWIST UNLOCKED! Check your Storyline tab!"
                else:
                    msg = "💨 Nothing this time... spin again next mission!"

                st.session_state.spinner_result = {"prize": prize, "msg": msg}
                st.balloons()
                st.success(f"🎰 {msg}")
                time.sleep(1); st.rerun()

    if st.session_state.spinner_result:
        p = st.session_state.spinner_result
        st.markdown(f"""<div class='secret-card'>
            <div style='font-size:40px'>{p['prize']['emoji']}</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:24px;color:{C};letter-spacing:3px'>{p['prize']['label']}</div>
            <div style='font-size:13px;color:#ffffff;margin-top:8px'>{p['msg']}</div>
        </div>""", unsafe_allow_html=True)

# ── STORYLINE ─────────────────────────────────────────────────────────────────
elif view == "storyline":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 YOUR STORYLINE</h2>", unsafe_allow_html=True)
    chapter = st.session_state.story_chapter
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#ffffff;font-size:12px'>Chapter {chapter} · Universe: {st.session_state.user_theme}</p>", unsafe_allow_html=True)

    if not st.session_state.story_log:
        st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace'>Complete your first mission to begin your story. 📖</p>", unsafe_allow_html=True)
    else:
        # Show story twist badge if pending
        if st.session_state.story_twist_pending:
            st.markdown(f"""<div class='secret-card'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FF44AA;letter-spacing:3px'>🌀 STORY TWIST INCOMING</div>
                <div style='color:#ffffff;font-size:13px;margin-top:8px'>The spinner unlocked a surprise twist in your universe. Complete one more mission to reveal it.</div>
            </div>""", unsafe_allow_html=True)

        # Show all chapters in reverse
        for i, chapter_text in enumerate(reversed(st.session_state.story_log)):
            ch_num = len(st.session_state.story_log) - i
            is_milestone = (ch_num % 5 == 0)
            border = "#FFD700" if is_milestone else C
            badge = "⭐ MILESTONE CHAPTER" if is_milestone else f"Chapter {ch_num}"
            st.markdown(f"""<div class='ach-card' style='border-color:{border};{"border-width:3px;" if is_milestone else ""}'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:14px;color:{border};letter-spacing:2px;margin-bottom:6px'>{badge}</div>
                <div style='font-family:Space Mono,monospace;font-size:13px;color:#ffffff;line-height:1.8'>{chapter_text}</div>
            </div>""", unsafe_allow_html=True)


elif view == "feedback":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💬 FEEDBACK PORTAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        fb_type = st.selectbox("TYPE", ["💡 Feature Idea","🐛 Bug Report","🔥 This is fire!","😤 Needs fixing","💭 General Thought"], key="fb_type")
        fb_text = st.text_area("YOUR MESSAGE", placeholder="Be as detailed as you want.", height=120, key="fb_text")
        fb_name = st.text_input("YOUR NAME (optional)", placeholder="Anonymous", key="fb_name")
        if st.button("🚀 SUBMIT", key="submit_fb"):
            if fb_text.strip():
                st.session_state.feedback_list.append({"type":fb_type,"message":fb_text.strip(),"name":fb_name.strip() or "Anonymous","universe":st.session_state.user_theme,"time":time.strftime("%Y-%m-%d %H:%M")})
                st.success("✅ RECEIVED. Thank you, Champion. 🔥"); st.balloons()
            else:
                st.error("Write something first!")
        if st.session_state.feedback_list:
            st.markdown("---")
            for fb in reversed(st.session_state.feedback_list):
                st.markdown(f"<div class='ach-card'><span style='color:{C}'>{fb['type']}</span> · <span style='color:#ffffff;font-size:11px'>{fb['time']} · {fb['name']}</span><br><span style='color:{TEXT}'>{fb['message']}</span></div>", unsafe_allow_html=True)

# ── SHOP ──────────────────────────────────────────────────────────────────────
elif view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🛒 ARSENAL</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class='shop-card'>
            <div style='font-size:10px;color:#ffffff;letter-spacing:2px;margin-bottom:6px'>⚔️ DEFENSE ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 6px'>{wd.get('shield_name','Shield').upper()}</h3>
            <div style='font-size:12px;color:#ffffff;font-style:italic;margin-bottom:12px'>{wd.get('shield_flavor','An ability forged in the heart of this universe.')}</div>
            <div style='background:#111111;border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#ffffff;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:13px;color:{TEXT};margin-top:4px'>{SHIELD_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#ffffff'>Cost: <span style='color:{C};font-weight:bold'>15 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚔️ ACQUIRE · 15 {currency}", key="buy_shield"):
            if st.session_state.gold >= 15:
                st.session_state.gold -= 15; st.session_state.shield_bought = True
                st.success(f"⚔️ {wd.get('shield_name')} activated!")
            else: st.error("Not enough currency.")
    with col2:
        st.markdown(f"""<div class='shop-card'>
            <div style='font-size:10px;color:#ffffff;letter-spacing:2px;margin-bottom:6px'>⚡ SPEED ABILITY</div>
            <h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:2px;margin:0 0 6px'>{wd.get('booster_name','Booster').upper()}</h3>
            <div style='font-size:12px;color:#ffffff;font-style:italic;margin-bottom:12px'>{wd.get('booster_flavor','Speed that defies every known law of physics.')}</div>
            <div style='background:#111111;border-left:3px solid {C};padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:14px'>
                <div style='font-size:10px;color:#ffffff;letter-spacing:2px'>EFFECT</div>
                <div style='font-size:13px;color:{TEXT};margin-top:4px'>{BOOSTER_EFFECT}</div>
            </div>
            <div style='font-size:12px;color:#ffffff'>Cost: <span style='color:{C};font-weight:bold'>25 {currency}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"⚡ ACQUIRE · 25 {currency}", key="buy_booster"):
            if st.session_state.gold >= 25:
                st.session_state.gold -= 25; st.session_state.sub_multiplier = 3
                st.session_state.booster_bought = True
                st.success(f"⚡ {wd.get('booster_name')} engaged!")
            else: st.error("Not enough currency.")

# ── MISSION HUB ───────────────────────────────────────────────────────────────
else:
    _, col, _ = st.columns([1,2,1])
    with col:
        reward   = 1.0 * st.session_state.sub_multiplier
        mult_tag = f" ×{st.session_state.sub_multiplier}" if st.session_state.sub_multiplier > 1 else ""
        st.markdown(f"""<div style='text-align:center;background:#111111;border:1px solid rgba({CR},{CG},{CB},0.12);border-radius:16px;padding:24px;margin-bottom:20px'>
            <div style='font-size:11px;color:#ffffff;letter-spacing:2px'>MISSION REWARD</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:52px;color:{C};margin:6px 0'>{reward:.1f} {currency}{mult_tag}</div>
            <div style='font-size:11px;color:#ffffff'>per completed mission</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style='background:#111111;border:1px solid rgba({CR},{CG},{CB},0.08);border-radius:16px;padding:20px;margin-bottom:16px;text-align:center'>
            <div style='font-size:10px;color:#ffffff;letter-spacing:2px;margin-bottom:8px'>⏱ MICRO TIMER</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:48px;color:{C}'>{st.session_state.micro_timer_seconds}s</div>
            <div style='font-size:11px;color:#ffffff'>+30s per tap · max 6 minutes</div>
        </div>""", unsafe_allow_html=True)

        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            if st.button("➖ MINUS 30s", key="sub_30"):
                if st.session_state.micro_timer_seconds > 30: st.session_state.micro_timer_seconds -= 30; st.rerun()
                else: st.warning("Minimum 30 seconds!")
        with tc2:
            if st.button("➕ ADD 30s", key="add_30"):
                if st.session_state.micro_timer_seconds < 360: st.session_state.micro_timer_seconds += 30; st.rerun()
                else: st.warning("Max 6 minutes!")
        with tc3:
            if st.button("▶ START", key="start_micro"):
                secs = st.session_state.micro_timer_seconds
                bar = st.progress(0); status = st.empty()
                for i in range(secs):
                    time.sleep(1); bar.progress((i+1)/secs)
                    status.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:{C};font-size:20px'>{secs-i-1}s remaining</p>", unsafe_allow_html=True)
                st.session_state.micro_timer_seconds = 30
                st.success("✅ Micro session done!"); time.sleep(1); st.rerun()
        with tc4:
            if st.button("🔄 RESET", key="reset_micro"):
                st.session_state.micro_timer_seconds = 30; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶  START 1-MINUTE MISSION", key="start_mission"):
            bar = st.progress(0); status = st.empty()
            for i in range(60):
                time.sleep(1); bar.progress((i+1)/60)
                status.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#ffffff'>SYNCHRONIZING: {i+1}s / 60s</p>", unsafe_allow_html=True)
            st.session_state.pending_gold = reward
            st.session_state.needs_verification = True
            st.rerun()

# ── TRIBUNAL ──────────────────────────────────────────────────────────────────
if st.session_state.needs_verification:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center;font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:4px'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        st.info(f"Upload proof of work to claim **{st.session_state.pending_gold:.1f} {currency}**")
        uploaded = st.file_uploader("PROOF OF LABOR:", key="proof_upload")
        if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT", key="submit_proof"):
            base_gold = st.session_state.pending_gold
            # ── VARIABLE REWARD (slot machine) ──
            earned, rarity_label, rarity_msg = variable_reward(base_gold)
            earned = round(earned, 1)

            # ── STREAK ──
            new_streak, streak_msg, is_new_day = update_streak()

            # ── SPINS BY TIER ──
            spins = get_spins_for_tier(st.session_state.get("sub_tier","Free"))
            st.session_state.spins_left = st.session_state.get("spins_left",0) + spins

            st.session_state.gold  += earned
            st.session_state.xp   += int(earned * 10)
            st.session_state.total_xp_real = st.session_state.get("total_xp_real",0) + int(earned*10)
            st.session_state.level  = 1 + st.session_state.xp // 100
            st.session_state.total_missions += 1
            st.session_state.needs_verification = False
            st.session_state.pending_gold = 0.0

            # ── LOOT BOX ──
            loot_pool = [
                {"name": f"+{spins} Spinner Spins", "rarity": rarity_label, "color": "#FFD700"},
                {"name": "RARE INCUBATOR EGG", "rarity": "GREAT", "color": "#4488FF"},
                {"name": "STREAK SHIELD (protects 1 day)", "rarity": "EPIC", "color": "#AA44FF"},
                {"name": f"+{int(earned*2)} Bonus {currency}", "rarity": rarity_label, "color": "#00FF88"},
                {"name": "STORY CHAPTER UNLOCKED", "rarity": "GREAT", "color": "#FF44AA"},
            ]
            loot = random.choice(loot_pool)
            # Apply loot effect
            if "Streak Shield" in loot["name"]: st.session_state.streak_shield = True
            if "Egg" in loot["name"]: st.session_state.incubator_eggs += 2
            if "Bonus" in loot["name"]: st.session_state.gold += int(earned*2)
            st.session_state.loot_pending = True
            st.session_state.loot_item = loot

            # Unlock a secret
            secret = random.choice(UNIVERSE_SECRETS)
            if "secret_queue" not in st.session_state:
                st.session_state.secret_queue = []
            st.session_state.secret_queue.append(secret)
            st.session_state.secrets_seen = len(st.session_state.secret_queue)
            st.session_state.show_secret = secret

            # Unlock spinner
            st.session_state.spinner_available = True
            st.session_state.spinner_wins = st.session_state.get("spinner_wins",0)

            # Advance storyline
            client = get_claude_client()
            prev = " ".join(st.session_state.story_log[-2:]) if st.session_state.story_log else ""
            st.session_state.story_chapter += 1
            new_chapter = generate_story_chapter(
                st.session_state.user_theme,
                st.session_state.story_chapter,
                prev, client
            )
            st.session_state.story_log.append(new_chapter)

            # Queue battle if GRINDER or OBSESSED
            if MODE in ("grinder","obsessed"):
                st.session_state.battle_state = "ready"

            # Earn egg
            st.session_state.incubator_eggs += 1

            st.balloons()
            st.success(f"✅ {rarity_label}! +{earned:.1f} {currency} · 🔥 {new_streak}-day streak · +{spins} spins · Loot box incoming!")
            time.sleep(1); st.rerun()
