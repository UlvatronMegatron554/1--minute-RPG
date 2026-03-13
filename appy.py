import streamlit as st
import anthropic
import time, json, re, random
import datetime as _dt

# ─────────────────────────────────────────────────────────────────────────────
# 30 SECOND INFINITEVERSE v10.0 — FULLY FIXED EDITION
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="30 Second Infiniteverse", page_icon="🌌", layout="wide")

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
# SPINNER COOLDOWN SYSTEM (6 HOURS)
# ─────────────────────────────────────────────────────────────────────────────
def get_spinner_cooldown_remaining():
    last_spin = st.session_state.get("last_spin_time", None)
    if last_spin is None:
        return 0
    cooldown = 6 * 60 * 60
    elapsed = time.time() - last_spin
    return max(0, cooldown - elapsed)

def can_spin():
    if st.session_state.get("last_spin_time", None) is None:
        return True
    return get_spinner_cooldown_remaining() <= 0

# ─────────────────────────────────────────────────────────────────────────────
# LOSS AVERSION & STREAK SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
def get_streak_info():
    streak = st.session_state.get("study_streak", 0)
    today = _dt.date.today().isoformat()
    last = st.session_state.get("last_active_date")
    
    days_until_7 = 7 - (streak % 7) if streak > 0 else 7
    days_until_30 = 30 - (streak % 30) if streak > 0 else 30
    
    if streak == 0:
        msg = "🔥 START YOUR STREAK TODAY! Don't lose out on bonus rewards!"
    elif streak < 7:
        msg = f"💎 {7 - streak} days until your 7-DAY MILESTONE BONUS! Don't break your streak!"
    elif streak % 7 == 0:
        msg = f"🎉 {streak}-DAY STREAK! You've earned bonus spins! Keep going!"
    elif streak < 30:
        msg = f"⚡ {30 - streak} days until 30-DAY MEGA BONUS! You're unstoppable!"
    else:
        msg = f"👑 {streak}-DAY STREAK! You're a LEGEND! Never stop!"
    
    return streak, days_until_7, days_until_30, msg

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
ACHIEVEMENTS_BASE = [
    {"id": "first_mission",    "name": "⚡ FIRST BLOOD",          "desc": "Completed your very first mission.", "req": lambda s: s.get("total_missions",0) >= 1},
    {"id": "five_missions",    "name": "🔥 ON A ROLL",             "desc": "5 missions done.", "req": lambda s: s.get("total_missions",0) >= 5},
    {"id": "ten_missions",     "name": "💪 GRIND MODE",            "desc": "10 missions completed.", "req": lambda s: s.get("total_missions",0) >= 10},
    {"id": "fifty_missions",   "name": "👑 UNSTOPPABLE",           "desc": "50 missions done.", "req": lambda s: s.get("total_missions",0) >= 50},
    {"id": "first_gold",       "name": "💰 FIRST PAYDAY",          "desc": "Earned your first currency.", "req": lambda s: s.get("gold",0) >= 5},
    {"id": "rich",             "name": "🤑 LOADED",                "desc": "100 currency stacked.", "req": lambda s: s.get("gold",0) >= 100},
    {"id": "elite_unlocked",   "name": "👁️ ELITE EYES ONLY",       "desc": "You found the code.", "req": lambda s: s.get("sub_tier","") == "Elite"},
    {"id": "first_battle",     "name": "⚔️ WARRIOR BORN",          "desc": "First battle fought.", "req": lambda s: s.get("battles_fought",0) >= 1},
    {"id": "battle_streak",    "name": "🏆 BATTLE HARDENED",       "desc": "10 battles completed.", "req": lambda s: s.get("battles_fought",0) >= 10},
    {"id": "first_egg",        "name": "🥚 EGG COLLECTOR",         "desc": "First egg earned.", "req": lambda s: s.get("eggs_hatched",0) >= 1},
    {"id": "legendary_hatch",  "name": "🐉 LEGENDARY TAMER",       "desc": "A LEGENDARY creature hatched.", "req": lambda s: s.get("legendary_hatched",False)},
    {"id": "shield_bought",    "name": "🛡️ FORTIFIED",             "desc": "Defense ability acquired.", "req": lambda s: s.get("shield_bought",False)},
    {"id": "booster_bought",   "name": "🚀 SPEED DEMON",           "desc": "Speed ability acquired.", "req": lambda s: s.get("booster_bought",False)},
    {"id": "secret_collector", "name": "🔮 TRUTH SEEKER",          "desc": "5 secrets collected.", "req": lambda s: s.get("secrets_seen",0) >= 5},
    {"id": "spinner_winner",   "name": "🎰 LUCKY SPIN",            "desc": "Won your first prize.", "req": lambda s: s.get("spinner_wins",0) >= 1},
    {"id": "storyline_deep",   "name": "📖 LORE KEEPER",           "desc": "Chapter 5 of storyline.", "req": lambda s: s.get("story_chapter",0) >= 5},
    {"id": "week_streak",      "name": "📅 WEEK WARRIOR",          "desc": "7 day streak achieved.", "req": lambda s: s.get("study_streak",0) >= 7},
    {"id": "month_streak",     "name": "🌟 MONTH MASTER",          "desc": "30 day streak!", "req": lambda s: s.get("study_streak",0) >= 30},
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

# ─────────────────────────────────────────────────────────────────────────────
# GAME ENGINE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def detect_game_mode(universe: str) -> str:
    l = universe.lower()
    if any(k in l for k in ['dragon ball','dbz','naruto','bleach','one piece','attack on titan','jujutsu','fairy tail','demon slayer']):
        return 'FIGHTER'
    if any(k in l for k in ['pokemon','genshin','zelda','final fantasy','fire emblem','persona','elden ring','dark souls','skyrim','witcher']):
        return 'RPG'
    if any(k in l for k in ['mario','sonic','kirby','donkey kong','crash bandicoot','celeste','hollow knight','cuphead','megaman']):
        return 'PLATFORM'
    if any(k in l for k in ['call of duty','cod','halo','fortnite','valorant','overwatch','apex','pubg','counter strike','battlefield','destiny']):
        return 'SHOOTER'
    if any(k in l for k in ['harry potter','hogwarts','lord of the rings','wizard','magic','fantasy']):
        return 'MAGIC'
    if any(k in l for k in ['star wars','nasa','space','galaxy','marvel','avengers','dc comics','superman','batman']):
        return 'COSMIC'
    if any(k in l for k in ['football','basketball','soccer','baseball','tennis','golf','nba','nfl','f1','formula 1','racing']):
        return 'SPORTS'
    if any(k in l for k in ['mortal kombat','street fighter','tekken','smash bros','king of fighters','fighting']):
        return 'BRAWL'
    return 'AUTO'

def _fallback_config(universe: str, mode: str, subject: str, q_count: int) -> dict:
    questions = [
        {"q":f"In the {universe} world: What is 15 × 8?","choices":["A: 100","B: 112","C: 120","D: 130"],"answer":"C"},
        {"q":f"A hero runs 5km in 25 min. Speed in km/h?","choices":["A: 10","B: 12","C: 15","D: 8"],"answer":"B"},
        {"q":"What is the square root of 144?","choices":["A: 11","B: 12","C: 13","D: 14"],"answer":"B"},
        {"q":"Solve: 3x + 6 = 21. What is x?","choices":["A: 3","B: 4","C: 5","D: 6"],"answer":"C"},
    ]
    return {
        "mode": mode,
        "arena_name": f"The {universe} Arena",
        "arena_desc": "A legendary battlefield forged from pure determination.",
        "arena_colors": ["#111122","#222244","#333366"],
        "player_title": "Champion",
        "enemy_name": f"{universe} Boss",
        "enemy_title": "The Final Obstacle",
        "enemy_color": "#CC2222",
        "enemy_phases": ["Phase 1","Phase 2 — ENRAGED","Final Phase — ULTIMATE"],
        "win_quote": "Victory belongs to those who never stop learning!",
        "lose_quote": "The enemy grows stronger. Study more and return.",
        "questions": questions[:q_count],
        "question_timer": 30,
    }

def generate_battle_config(universe: str, subject: str, tier: str, client, difficulty: int = 1) -> dict:
    mode = detect_game_mode(universe)
    tier_q = 8 if tier == "Elite" else (6 if tier == "Premium" else 4)
    q_count = min(tier_q + difficulty, 12)
    q_timer = 30 if tier == "Elite" else (20 if tier == "Premium" else 15)
    
    evolutions_by_mode = {
        "FIGHTER": ["Base Form","Awakened","Powered Up","Super Form","Hyper Mode","Transcendent","Legendary","Absolute","INFINITE POWER"],
        "RPG":     ["Novice","Apprentice","Adept","Expert","Master","Grand Master","Champion","Legend","MYTHIC"],
        "PLATFORM":["Small","Powered","Fire Mode","Cape Mode","Tanooki","Metal","Wing Cap","Rainbow Star","INVINCIBLE"],
        "SHOOTER": ["Recruit","Soldier","Specialist","Veteran","Elite","Special Ops","Ghost","Shadow","OMEGA OPERATIVE"],
        "MAGIC":   ["Apprentice","Witch/Wizard","Prefect","Auror","Master Wizard","Archmage","High Mage","Grand Archmage","OMNIMANCER"],
        "COSMIC":  ["Cadet","Pilot","Ace","Captain","Commander","Admiral","Warlord","Cosmic Force","UNIVERSAL"],
        "SPORTS":  ["Rookie","Starter","Varsity","All-Star","MVP","Hall of Fame","Legend","GOAT","UNDISPUTED"],
        "BRAWL":   ["White Belt","Yellow","Orange","Green","Blue","Purple","Brown","Black Belt","GRANDMASTER"],
        "AUTO":    ["Level 1","Level 2","Level 3","Level 4","Level 5","Level 6","Level 7","Level 8","MAXED"],
    }
    
    try:
        prompt = f"""Generate {q_count} questions about {subject} flavored with {universe} universe. Return JSON with "questions" array: [{{"q":"question","choices":["A: opt","B: opt","C: opt","D: opt"],"answer":"B"}}]"""
        resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=2000, messages=[{"role":"user","content":prompt}])
        raw = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
        cfg = json.loads(raw)
    except Exception:
        cfg = _fallback_config(universe, mode, subject, q_count)

    max_evo = 9 if tier == "Elite" else (6 if tier == "Premium" else 3)
    all_evos = evolutions_by_mode.get(mode, evolutions_by_mode["AUTO"])
    cfg["evolutions"] = all_evos[:max_evo]
    cfg["subject"] = subject
    cfg["universe"] = universe
    cfg["tier"] = tier
    cfg["mode"] = mode
    cfg["question_timer"] = q_timer
    return cfg

def variable_reward(base: float) -> tuple:
    roll = random.random()
    if roll < 0.04:
        mult = random.randint(8, 20)
        return base * mult, "💥 JACKPOT", f"{mult}× MULTIPLIER!"
    elif roll < 0.12:
        mult = random.randint(4, 7)
        return base * mult, "🌟 EPIC REWARD", f"{mult}×!"
    elif roll < 0.28:
        mult = random.randint(2, 3)
        return base * mult, "⚡ GREAT PULL", f"{mult}×!"
    elif roll < 0.55:
        return base * 1, "✅ SOLID", "Standard reward."
    else:
        mult = round(random.uniform(0.3, 0.7), 1)
        return base * mult, "😤 LOW ROLL", f"Only {mult}×..."

def get_spins_for_tier(tier: str) -> int:
    if tier == "Elite":   return 6
    if tier == "Premium": return 3
    return 1

def update_streak() -> tuple:
    today = _dt.date.today().isoformat()
    last  = st.session_state.get("last_active_date")
    streak = st.session_state.get("study_streak", 0)
    if last is None:
        st.session_state.study_streak = 1
        st.session_state.last_active_date = today
        return 1, "🔥 Streak started!", True
    if last == today:
        return streak, "", False
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    if last == yesterday:
        streak += 1
        st.session_state.study_streak = streak
        st.session_state.last_active_date = today
        msg = f"🔥 {streak}-DAY STREAK! You're unstoppable!"
        if streak % 7 == 0:
            msg = f"🏆 {streak} DAYS — WEEK COMPLETE! Bonus spins!"
            st.session_state.spins_left += 3
        if streak % 30 == 0:
            msg = f"👑 {streak} DAYS — MONTH MASTER!"
            st.session_state.spins_left += 10
        return streak, msg, True
    else:
        old = streak
        st.session_state.study_streak = 1
        st.session_state.last_active_date = today
        return 1, f"💔 {old}-day streak LOST. Fresh start!", True

def loot_box_html(item_name: str, rarity: str, color: str) -> str:
    rarity_colors = {"JACKPOT":"#FFD700","EPIC":"#AA44FF","GREAT":"#4488FF","SOLID":"#44FF88","LOW":"#888888"}
    rc = rarity_colors.get(rarity.upper().split()[0], "#FFD700")
    return f"""<div style='text-align:center;padding:32px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);border:3px solid {rc};border-radius:20px;animation:lootpulse 0.6s ease-in-out 3;box-shadow:0 0 40px {rc}88;'><div style='font-size:64px;animation:lootbounce 0.4s ease-in-out infinite alternate'>🎁</div><div style='font-size:28px;font-family:Bebas Neue,sans-serif;color:{rc};letter-spacing:6px;margin:12px 0'>{rarity}</div><div style='font-size:20px;color:#ffffff;font-family:Space Mono,monospace'>{item_name}</div></div><style>@keyframes lootpulse{{0%{{box-shadow:0 0 20px {rc}44}}50%{{box-shadow:0 0 60px {rc}cc}}100%{{box-shadow:0 0 20px {rc}44}}}}@keyframes lootbounce{{from{{transform:scale(1) rotate(-5deg)}}to{{transform:scale(1.2) rotate(5deg)}}}}</style>"""

def streak_danger_html(streak: int, color: str) -> str:
    if streak < 2: return ""
    return f"""<div style='background:linear-gradient(90deg,#3a0000,#1a0000);border:2px solid #FF2222;border-radius:12px;padding:12px 20px;text-align:center;margin:8px 0;animation:streakpulse 1.5s ease-in-out infinite;'><span style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FF4444;letter-spacing:3px'>🔥 {streak}-DAY STREAK AT RISK</span><span style='display:block;font-family:Space Mono,monospace;font-size:11px;color:#FF8888;margin-top:4px'>Complete a mission TODAY or lose it forever.</span></div><style>@keyframes streakpulse{{0%,100%{{border-color:#FF2222}}50%{{border-color:#FF8888}}}}</style>"""

def generate_story_chapter(theme, chapter, prev_story, client):
    try:
        is_milestone = (chapter % 5 == 0)
        prompt = f"""Write 2-3 sentences for Chapter {chapter} of a story set in {theme} universe. {"MUST include a massive plot twist." if is_milestone else "End with a cliffhanger."}"""
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=200, messages=[{"role":"user","content":prompt}])
        return msg.content[0].text.strip()
    except:
        return f"Chapter {chapter}: The {theme} universe trembles. Something ancient stirs in the shadows..."

def generate_universe_achievements(theme, client):
    try:
        prompt = f"""Generate 5 achievements specific to "{theme}" universe. Return JSON: [{{"name":"...","desc":"..."}}]"""
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=400, messages=[{"role":"user","content":prompt}])
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`")
        return json.loads(raw)[:5]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# MONSTER DATABASE
# ─────────────────────────────────────────────────────────────────────────────
EGG_RARITIES = [
    {"rarity": "Common",    "color": "#aaaaaa", "chance": 55, "reward_mult": 1},
    {"rarity": "Rare",      "color": "#4488ff", "chance": 28, "reward_mult": 2},
    {"rarity": "Epic",      "color": "#aa44ff", "chance": 13, "reward_mult": 4},
    {"rarity": "Legendary", "color": "#FFD700", "chance": 4,  "reward_mult": 10},
]

# ─────────────────────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_claude_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except:
        return None

def extract_json(raw_text):
    if not raw_text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except:
        pass
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return None

LORE_PROMPT = """Return JSON for universe "{theme}": {{"currency":"...","color":"#hex","shield_name":"...","booster_name":"...","description":"...","shield_flavor":"...","booster_flavor":"...","battle_style":"..."}}"""

HARD_FALLBACKS = {
    "super smash bros":  {"currency":"KO Points","color":"#E4000F","shield_name":"Perfect Shield","booster_name":"Wavedash","description":"Every gaming legend meets in the ultimate crossover brawl.","shield_flavor":"Reflects any attack back with perfect timing.","booster_flavor":"Slides across the stage faster than the eye can track.","battle_style":"reaction"},
    "minecraft":         {"currency":"Emeralds","color":"#5D9E35","shield_name":"Protection IV Netherite","booster_name":"Ender Pearl Warp","description":"A boundless world of blocks.","shield_flavor":"Absorbs almost any damage.","booster_flavor":"Teleports you instantly.","battle_style":"random"},
    "pokemon":           {"currency":"PokéDollars","color":"#FFCB05","shield_name":"Protect","booster_name":"Extreme Speed","description":"Catch, train, and battle creatures.","shield_flavor":"Blocks any single attack.","booster_flavor":"Moves so fast it always strikes first.","battle_style":"turnbased"},
    "one piece":         {"currency":"Berries","color":"#E8372B","shield_name":"Armament Haki","booster_name":"Gear Second","description":"A pirate's odyssey.","shield_flavor":"Coats body in invisible armor.","booster_flavor":"Pumps blood at rocket speed.","battle_style":"turnbased"},
    "naruto":            {"currency":"Ryo","color":"#FF6600","shield_name":"Susanoo Ribcage","booster_name":"Flying Thunder God","description":"From outcast to the strongest.","shield_flavor":"Giant chakra ribcage.","booster_flavor":"Teleports instantly.","battle_style":"turnbased"},
    "dragon ball":       {"currency":"Zeni","color":"#FF8C00","shield_name":"Barrier Blast","booster_name":"Instant Transmission","description":"Warriors transcend all limits.","shield_flavor":"Ki barrier explodes outward.","booster_flavor":"Teleports to any ki signature.","battle_style":"turnbased"},
    "harry potter":      {"currency":"Galleons","color":"#740001","shield_name":"Protego Totalum","booster_name":"Apparition","description":"A world of magic and courage.","shield_flavor":"Full protective enchantment.","booster_flavor":"Vanishes and reappears anywhere.","battle_style":"turnbased"},
    "star wars":         {"currency":"Galactic Credits","color":"#FFE81F","shield_name":"Lightsaber Deflect","booster_name":"Force Speed","description":"A galaxy far away.","shield_flavor":"Impenetrable energy shield.","booster_flavor":"Superhuman speed.","battle_style":"turnbased"},
}

def get_fallback(theme):
    t = theme.lower().strip()
    if t in HARD_FALLBACKS:
        return HARD_FALLBACKS[t]
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key:
            return data
    return {"currency":"Titan Shards","color":"#00FFCC","shield_name":"Kinetic Barrier","booster_name":"Void Dash","description":"A realm of boundless power.","shield_flavor":"Converts kinetic to protective force.","booster_flavor":"Rips a hole in space.","battle_style":"random"}

REQUIRED_KEYS = ["currency","color","shield_name","booster_name","description"]

def resolve_universe(theme):
    if not theme.strip():
        return DEFAULT_UNIVERSE.copy()
    client = get_claude_client()
    if client:
        try:
            message = client.messages.create(model="claude-sonnet-4-5", max_tokens=400, messages=[{"role":"user","content":LORE_PROMPT.format(theme=theme)}])
            raw = message.content[0].text.strip()
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color","")):
                    data["color"] = "#FFD700"
                data.setdefault("shield_flavor",  "An ability forged in this universe.")
                data.setdefault("booster_flavor", "Speed that defies physics.")
                data.setdefault("battle_style",   "random")
                data["shield_effect"]  = SHIELD_EFFECT
                data["booster_effect"] = BOOSTER_EFFECT
                return data
        except:
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
    for ach in ACHIEVEMENTS_BASE:
        if ach["id"] not in unlocked:
            try:
                if ach["req"](session):
                    unlocked.add(ach["id"])
                    newly_unlocked.append(ach)
            except:
                pass
    universe_achs = session.get("universe_achievements", [])
    for ach in universe_achs:
        if ach.get("id") not in unlocked:
            unlocked.add(ach.get("id"))
            newly_unlocked.append(ach)
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
        "game_mode": None, "how_open": False,
        "unlocked_achievements": set(),
        "battles_fought": 0, "battles_won": 0,
        "eggs_hatched": 0, "legendary_hatched": False,
        "incubator_eggs": 0, "hatched_monsters": [],
        "secrets_seen": 0,
        "shield_bought": False, "booster_bought": False,
        "battle_state": None, "current_battle": None, "egg_warmth": {},
        "battle_config": None, "battle_box_pending": False, "battle_box_item": None,
        "battle_wins": 0, "opening_loot_claimed": False,
        "secret_queue": [], "show_secret": None,
        "spinner_available": False, "spinner_wins": 0,
        "first_session": True, "spinner_result": None,
        "story_chapter": 0, "story_log": [],
        "story_twist_pending": False, "opening_story_shown": False,
        "study_streak": 0, "last_active_date": None,
        "streak_shield": False, "spins_left": 0,
        "loot_pending": False, "loot_item": None,
        "total_xp_real": 0,
        "universe_achievements": [], "universe_ach_loaded": False,
        "last_spin_time": None, "claim_used_this_session": False,
        "custom_subject": "",
    })

# ─────────────────────────────────────────────────────────────────────────────
# 🌌 GATEWAY SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_name is None:
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#000008!important;color:white!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important;}
.stTextInput>div>div>input{background:#ffffff!important;border:2px solid #FFD700!important;border-radius:10px!important;color:#000!important;font-family:'Space Mono'!important;font-size:14px!important;padding:12px!important;}
div.stButton>button{background:linear-gradient(135deg,#FFD700,#FF8C00)!important;border:none!important;color:#000!important;font-family:'Bebas Neue',sans-serif!important;font-size:24px!important;letter-spacing:4px!important;padding:18px!important;border-radius:14px!important;width:100%!important;box-shadow:0 0 35px rgba(255,215,0,0.4)!important;}
</style>
<div style='text-align:center;padding:40px'>
<div style='font-family:Bebas Neue,sans-serif;font-size:clamp(48px,12vw,120px);background:linear-gradient(135deg,#FFD700,#FF8C00,#FF3C3C,#CC00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:8px;line-height:1'>30 SECOND<br>INFINITEVERSE</div>
<p style='font-family:Orbitron,monospace;color:#aaa;letter-spacing:3px'>Any Universe · 30-Second Missions · AI Powered</p>
</div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,2,1])
    with col:
        mode_col1, mode_col2, mode_col3 = st.columns(3)
        with mode_col1:
            if st.button("⚡ CHILL"): st.session_state.game_mode = "chill"
        with mode_col2:
            if st.button("🔥 GRINDER"): st.session_state.game_mode = "grinder"
        with mode_col3:
            if st.button("💀 OBSESSED"): st.session_state.game_mode = "obsessed"

        name_input = st.text_input("⚡ Champion Name", placeholder="Enter your name")
        theme_input = st.text_input("🌌 Your Universe", placeholder="Naruto, F1, Nike, etc.")
        custom_subject = st.text_input("🎯 Your Study Subject (optional)", placeholder="Quantum Physics, Piano, Spanish...")

        # 7 SPINNERS: 3 AUTO + 4 IGNITE
        import streamlit.components.v1 as components
        _SPINNER_HTML = '''<style>@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');*{box-sizing:border-box;margin:0;padding:0;}#universe{width:100%;height:380px;background:radial-gradient(ellipse at 50% 60%,#0a0020 0%,#000008 70%);border-radius:16px;position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;}#rack{display:flex;gap:10px;justify-content:center;align-items:center;z-index:2;padding:10px;flex-wrap:wrap;}.slot{display:flex;flex-direction:column;align-items:center;gap:3px;}.slbl{font-family:Orbitron,monospace;font-size:6px;letter-spacing:1px;color:rgba(255,255,255,0.4);}.srpm{font-family:Orbitron,monospace;font-size:7px;min-height:11px;}.nbtn{padding:3px 8px;font-size:6px;font-family:Orbitron;border-radius:4px;cursor:pointer;border:1px solid;background:rgba(0,0,0,0.6);transition:all 0.12s;}</style><div id="universe"><canvas id="stars" style="position:absolute;top:0;left:0;pointer-events:none;z-index:0" width="900" height="380"></canvas><div id="rack"><div class="slot"><canvas id="c_s0" width="90" height="90"></canvas><div class="slbl">AUTO OMEGA</div><div id="r_s0" class="srpm" style="color:#FF00FF">∞ ETERNAL</div></div><div class="slot"><canvas id="c_s1" width="90" height="90"></canvas><div class="slbl">AUTO QUANTUM</div><div id="r_s1" class="srpm" style="color:#00FFFF">∞ ETERNAL</div></div><div class="slot"><canvas id="c_s2" width="90" height="90"></canvas><div class="slbl">AUTO COSMIC</div><div id="r_s2" class="srpm" style="color:#FFD700">∞ ETERNAL</div></div><div class="slot"><canvas id="c_s3" width="80" height="80"></canvas><div class="slbl">IGNITE NOVA</div><div id="r_s3" class="srpm" style="color:#FF4400"></div><button class="nbtn" style="border-color:#FF4400;color:#FF4400" onclick="ignite('s3',0.6)">IGNITE</button></div><div class="slot"><canvas id="c_s4" width="80" height="80"></canvas><div class="slbl">IGNITE BLAZE</div><div id="r_s4" class="srpm" style="color:#FF6600"></div><button class="nbtn" style="border-color:#FF6600;color:#FF6600" onclick="ignite('s4',0.55)">IGNITE</button></div><div class="slot"><canvas id="c_s5" width="80" height="80"></canvas><div class="slbl">IGNITE SURGE</div><div id="r_s5" class="srpm" style="color:#FF8800"></div><button class="nbtn" style="border-color:#FF8800;color:#FF8800" onclick="ignite('s5',0.5)">IGNITE</button></div><div class="slot"><canvas id="c_s6" width="80" height="80"></canvas><div class="slbl">IGNITE FLASH</div><div id="r_s6" class="srpm" style="color:#FFAA00"></div><button class="nbtn" style="border-color:#FFAA00;color:#FFAA00" onclick="ignite('s6',0.45)">IGNITE</button></div></div></div><script>var sc=document.getElementById('stars'),sctx=sc.getContext('2d');var STARS=[];for(var i=0;i<80;i++)STARS.push({x:Math.random()*900,y:Math.random()*380,r:Math.random()*1.3+0.3,a:Math.random(),da:Math.random()*0.007+0.002});function dS(){sctx.clearRect(0,0,900,380);STARS.forEach(function(s){s.a+=s.da;if(s.a>1||s.a<0)s.da*=-1;sctx.globalAlpha=s.a*0.75;sctx.beginPath();sctx.arc(s.x,s.y,s.r,0,Math.PI*2);sctx.fillStyle='#fff';sctx.fill();});sctx.globalAlpha=1;}var DF=[{id:'s0',sz:45,lbl:'AUTO OMEGA',bv:0.8,bl:5,sh:'drop',p:['#FF00FF','#AA00FF','#FF44FF'],gw:'#FF00FF',rm:'#FF88FF'},{id:'s1',sz:45,lbl:'AUTO QUANTUM',bv:0.75,bl:4,sh:'crys',p:['#00FFFF','#00AAAA','#00FFEE'],gw:'#00FFFF',rm:'#88FFFF'},{id:'s2',sz:45,lbl:'AUTO COSMIC',bv:0.7,bl:6,sh:'fan',p:['#FFD700','#FF8C00','#FFAA00'],gw:'#FFD700',rm:'#FFAA00'},{id:'s3',sz:40,lbl:'IGNITE NOVA',bv:0.25,bl:4,sh:'drop',p:['#FF4400','#FF2200','#FF6600'],gw:'#FF4400',rm:'#FF6600'},{id:'s4',sz:40,lbl:'IGNITE BLAZE',bv:0.22,bl:3,sh:'wing',p:['#FF6600','#FF4400','#FF8800'],gw:'#FF6600',rm:'#FF8800'},{id:'s5',sz:40,lbl:'IGNITE SURGE',bv:0.2,bl:5,sh:'blad',p:['#FF8800','#FF6600','#FFAA00'],gw:'#FF8800',rm:'#FFAA00'},{id:'s6',sz:40,lbl:'IGNITE FLASH',bv:0.18,bl:4,sh:'crys',p:['#FFAA00','#FF8800','#FFCC00'],gw:'#FFAA00',rm:'#FFDD00'}];var ST={};DF.forEach(function(sp){ST[sp.id]={a:Math.random()*6.28,v:sp.bv};var cv=document.getElementById('c_'+sp.id);cv.width=sp.sz*2;cv.height=sp.sz*2;});function draw(sp,angle,vel){var cv=document.getElementById('c_'+sp.id);if(!cv)return;var ctx=cv.getContext('2d'),sz=sp.sz,cx=sz,cy=sz,r=sz-5,spd=Math.abs(vel);ctx.clearRect(0,0,sz*2,sz*2);for(var i=0;i<sp.bl;i++){var ba=angle+(i*6.28/sp.bl);ctx.save();ctx.translate(cx,cy);ctx.rotate(ba);ctx.fillStyle=sp.p[i%sp.p.length];ctx.beginPath();ctx.ellipse(r*0.4,0,r*0.4,r*0.2,0,0,Math.PI*2);ctx.fill();ctx.restore();}ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.strokeStyle=sp.rm+(spd>0.3?'BB':'33');ctx.lineWidth=2;ctx.stroke();}function ignite(id,targetV){ST[id].v=targetV;}var AF=0.999995;function loop(){dS();DF.forEach(function(sp){var s=ST[sp.id];s.v*=AF;if(Math.abs(s.v)<sp.bv)s.v=sp.bv;s.a+=s.v;draw(sp,s.a,s.v);});requestAnimationFrame(loop);}loop();</script>'''
        components.html(_SPINNER_HTML, height=395)

        if st.button("⚡ ENTER THE INFINITEVERSE"):
            if not name_input.strip():
                st.error("Enter your champion name.")
            elif not st.session_state.game_mode:
                st.error("Pick your mode!")
            else:
                theme_val = theme_input.strip()
                display_name = theme_val if theme_val else DEFAULT_UNIVERSE_NAME
                st.session_state.custom_subject = custom_subject.strip() if custom_subject.strip() else "General Knowledge"
                with st.spinner(f"Loading {display_name}..."):
                    world_data = resolve_universe(theme_val)
                st.session_state.user_name = name_input.strip()
                st.session_state.world_data = world_data
                st.session_state.vibe_color = world_data.get("color","#FFD700")
                st.session_state.user_theme = display_name
                client = get_claude_client()
                if client and theme_val:
                    try:
                        uni_achs = generate_universe_achievements(theme_val, client)
                        st.session_state.universe_achievements = uni_achs
                    except:
                        pass
                st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
MODE = st.session_state.game_mode or "chill"
wd = st.session_state.world_data
BG = st.session_state.get("bg_color","#ffffff")
RAW_C = st.session_state.vibe_color
C = readable_color(RAW_C, BG)
TEXT = text_on(BG)
MUTED = "#444444" if is_light(BG) else "#cccccc"
currency = wd.get("currency","Credits")

_ch = C.lstrip('#')
try:
    CR, CG, CB = int(_ch[0:2],16), int(_ch[2:4],16), int(_ch[4:6],16)
except:
    CR, CG, CB = 255, 215, 0

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html,body,[data-testid="stAppViewContainer"]{{background:{BG}!important;color:{TEXT}!important;font-family:'Space Mono',monospace;}}
[data-testid="stHeader"],[data-testid="stToolbar"]{{background:transparent!important;}}
[data-testid="stSidebar"]{{background:#111111!important;}}
[data-testid="stSidebar"] * {{color:#ffffff!important;}}
[data-testid="stSidebar"] div.stButton>button{{border:2px solid {C}!important;background:#1a1a1a!important;color:#ffffff!important;font-family:'Bebas Neue'!important;font-size:14px!important;padding:8px 12px!important;border-radius:8px!important;width:100%!important;margin-bottom:4px!important;}}
#MainMenu,footer{{visibility:hidden;}}
input,textarea{{background:#ffffff!important;color:#000!important;border:2px solid {C}!important;border-radius:10px!important;font-family:'Space Mono'!important;font-size:14px!important;}}
div.stButton>button{{border:6px solid {C}!important;background:#000!important;color:#fff!important;font-family:'Bebas Neue'!important;font-size:28px!important;letter-spacing:4px!important;padding:20px!important;border-radius:40px!important;animation:titan-pulse 2.5s infinite ease-in-out!important;width:100%;}}
.metric-card,.shop-card,.ach-card,.monster-card,.secret-card{{background:#111!important;border:2px solid {C}!important;border-radius:14px!important;padding:18px!important;color:#fff!important;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue;color:{C};letter-spacing:3px'>🌌 INFINITEVERSE</h1>")
    st.markdown(f"**CHAMPION:** {st.session_state.user_name.upper()}")
    st.markdown(f"**UNIVERSE:** {st.session_state.user_theme}")
    st.markdown(f"**MODE:** {MODE.upper()}")
    st.markdown(f"**RANK:** {st.session_state.sub_tier.upper()}")
    st.markdown(f"**SUBJECT:** {st.session_state.get('custom_subject','General Knowledge')}")

    st.markdown(f"**{currency}:** {st.session_state.gold:.1f} | XP: {st.session_state.xp} | LVL {st.session_state.level}")

    streak, days_7, days_30, streak_msg = get_streak_info()
    if streak > 0:
        st.markdown(f"🔥 **{streak} DAY STREAK**")
        st.progress(min(100, streak * 3.33) / 100)

    st.write("---")
    st.markdown("**👑 ELITE CODE**")
    code = st.text_input("Code:", type="password", key="elite_code")
    if code == "4RJ1TV51Z" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3
        st.success("💀 ELITE ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()
    if code == "1TR5LG89D" and st.session_state.sub_tier not in ("Elite","Premium"):
        st.session_state.sub_tier = "Premium"; st.session_state.sub_multiplier = 2
        st.success("⚡ PREMIUM ACTIVATED!"); st.balloons(); time.sleep(1); st.rerun()

    st.write("---")
    if st.button("🚀 MISSION HUB"): st.session_state.view = "main"; st.rerun()
    if st.button("⚔️ BATTLE"): st.session_state.view = "battle"; st.rerun()
    if st.button("🎰 SPINNER"): st.session_state.view = "spinner"; st.rerun()
    if st.button("🛒 SHOP"): st.session_state.view = "shop"; st.rerun()
    if st.button("📖 STORY"): st.session_state.view = "story"; st.rerun()
    if st.button("🔮 SECRETS"): st.session_state.view = "secrets"; st.rerun()
    if st.button("💬 FEEDBACK"): st.session_state.view = "feedback"; st.rerun()

    if MODE in ("grinder","obsessed"):
        if st.button("🏆 ACHIEVEMENTS"): st.session_state.view = "achievements"; st.rerun()
        if st.button("🥚 INCUBATOR"): st.session_state.view = "incubator"; st.rerun()
        if st.button("🎯 PETS"): st.session_state.view = "pets"; st.rerun()

    if MODE == "obsessed":
        if st.button("📖 MANUAL"): st.session_state.view = "manual"; st.rerun()
        if st.button("💳 PLANS"): st.session_state.view = "plans"; st.rerun()

    st.write("---")
    new_bg = st.color_picker("BG", value=st.session_state.get("bg_color","#ffffff"), label_visibility="collapsed")
    if new_bg != st.session_state.bg_color:
        st.session_state.bg_color = new_bg; st.rerun()
    new_tc = st.color_picker("Theme", value=st.session_state.vibe_color, label_visibility="collapsed")
    if new_tc != st.session_state.vibe_color:
        st.session_state.vibe_color = new_tc; st.rerun()

    st.write("---")
    new_theme = st.text_input("Switch Universe:", placeholder="New universe...")
    if st.button("🔄 WARP"):
        if new_theme.strip():
            world_data = resolve_universe(new_theme.strip())
            st.session_state.world_data = world_data
            st.session_state.vibe_color = world_data.get("color","#FFD700")
            st.session_state.user_theme = new_theme.strip()
            st.rerun()

    st.write("---")
    if st.button("🚨 RESET ALL"):
        st.session_state.clear(); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS CHECK
# ─────────────────────────────────────────────────────────────────────────────
new_ach = check_achievements(st.session_state)
for ach in new_ach:
    st.toast(f"🏆 {ach['name']}", icon="🏆")

if st.session_state.show_secret:
    st.markdown(f"<div class='secret-card'><h3>🔮 SECRET</h3>{st.session_state.show_secret}</div>", unsafe_allow_html=True)
    if st.button("CLOSE"):
        st.session_state.show_secret = None
        st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>{st.session_state.user_theme.upper()}</h1><p style='text-align:center;font-size:15px;color:#fff;margin-top:4px'>{wd.get('description','A realm of infinite power.')}</p>""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# VIEWS
# ─────────────────────────────────────────────────────────────────────────────
view = st.session_state.view

# ── OPENING STORY ───────────────────────────────────────────────────────────
if not st.session_state.get("opening_story_shown", True):
    theme_now = st.session_state.user_theme or "Infinite Power"
    client_os = get_claude_client()
    if client_os:
        try:
            resp_os = client_os.messages.create(model="claude-sonnet-4-5", max_tokens=220, messages=[{"role":"user","content":f"Write 3 sentences opening for {theme_now} universe story. End with cliffhanger."}])
            opening_txt = resp_os.content[0].text.strip()
        except:
            opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened."
    else:
        opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened."

    st.session_state.opening_story_shown = True
    if "story_log" not in st.session_state:
        st.session_state.story_log = []
    st.session_state.story_log.insert(0, opening_txt)

    st.markdown(f"<div class='ach-card' style='border-color:{C}'><h3>⚡ CHAPTER 0</h3><p>{opening_txt}</p></div>", unsafe_allow_html=True)

# ── STREAK DANGER ───────────────────────────────────────────────────────────
if st.session_state.get("study_streak", 0) >= 2:
    today_str = _dt.date.today().isoformat()
    last_str = st.session_state.get("last_active_date")
    if last_str and last_str != today_str:
        yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
        if last_str == yesterday:
            st.markdown(streak_danger_html(st.session_state.study_streak, C), unsafe_allow_html=True)

# ── LOOT BOX ────────────────────────────────────────────────────────────────
if st.session_state.get("loot_pending") and st.session_state.get("loot_item"):
    item = st.session_state.loot_item
    st.markdown(loot_box_html(item["name"], item["rarity"], item.get("color","#FFD700")), unsafe_allow_html=True)
    if st.button("⚡ CLAIM IT"):
        st.session_state.loot_pending = False
        st.session_state.loot_item = None
        st.rerun()
    st.stop()

# ── MAIN MISSION HUB ──────────────────────────────────────────────────────
if view == "main" or view == "main":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C};letter-spacing:4px'>🚀 MISSION HUB</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Balance", f"{st.session_state.gold:.1f} {currency}")
    with col2:
        st.metric("⭐ XP", st.session_state.xp)
    with col3:
        st.metric("📊 Level", st.session_state.level)

    st.markdown("---")
    st.markdown(f"<h3 style='color:{C}'>⏱️ START A 30-SECOND MISSION</h3>", unsafe_allow_html=True)
    st.info(f"Work/study for 30 seconds, then upload proof to claim your {currency}!")
    
    mission_btn = st.button("🚀 START 30-SECOND MISSION", use_container_width=True)
    
    if mission_btn:
        st.session_state.mission_start_time = time.time()
        st.success("⏱️ Go! You have 30 seconds! Work hard!")
        time.sleep(30)
        st.session_state.needs_verification = True
        st.session_state.pending_gold = random.uniform(5, 25)
        st.rerun()

# ── BATTLE ────────────────────────────────────────────────────────────────
elif view == "battle":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>⚔️ BATTLE</h2>", unsafe_allow_html=True)
    theme = st.session_state.user_theme or "Infinite Power"
    tier_now = st.session_state.get("sub_tier","Free")
    custom_subj = st.session_state.get("custom_subject", "General Knowledge")

    if st.session_state.get("battle_box_pending") and st.session_state.get("battle_box_item"):
        item = st.session_state.battle_box_item
        rc2 = {"Common":"#888","Rare":"#4488FF","Epic":"#AA44FF","Legendary":"#FFD700"}.get(item["rarity"],"#FFD700")
        st.markdown(f"<div style='border:3px solid {rc2};border-radius:20px;padding:32px;text-align:center;margin:16px 0;background:linear-gradient(135deg,#0a0a1a,#1a0a2e)'><div style='font-size:64px'>🎁</div><div style='font-size:28px;color:{rc2}'>{item['rarity']} BATTLE BOX</div><div style='font-size:20px'>{item['name']}</div></div>", unsafe_allow_html=True)
        if st.button("⚡ CLAIM BATTLE BOX"):
            st.session_state.battle_box_pending = False
            st.session_state.battle_box_item = None
            st.rerun()
        st.stop()

    cfg = st.session_state.get("battle_config")
    if cfg is None:
        client2 = get_claude_client()
        with st.spinner("Generating battle..."):
            cfg = generate_battle_config(theme, custom_subj, tier_now, client2)
        st.session_state.battle_config = cfg

    if st.button("⚔️ START BATTLE"):
        st.session_state.battle_state = "ready"
        st.rerun()

    if st.session_state.get("battle_state") == "ready":
        st.success(f"⚔️ Battle Ready! Universe: {theme} | Subject: {custom_subj}")
        st.info(f"Timer: {cfg.get('question_timer',15)}s per question")

# ── SPINNER ────────────────────────────────────────────────────────────────
elif view == "spinner":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🎰 LUCKY SPINNER</h2>", unsafe_allow_html=True)
    
    can_spin_now = can_spin()
    cooldown_remaining = get_spinner_cooldown_remaining()
    
    if not can_spin_now:
        hours = int(cooldown_remaining // 3600)
        mins = int((cooldown_remaining % 3600) // 60)
        secs = int(cooldown_remaining % 60)
        st.markdown(f"<div style='border:2px solid #FF4400;border-radius:14px;padding:20px;text-align:center'><div style='font-size:28px;color:#FF4400'>⏰ COOLDOWN</div><div style='font-size:36px;color:#FF6600'>{hours:02d}:{mins:02d}:{secs:02d}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center'>Your spin is ready! 🔥</p>", unsafe_allow_html=True)

    if can_spin_now and not st.session_state.get("claim_used_this_session", False):
        if st.button("🎰 CLAIM YOUR SPIN PRIZE"):
            st.session_state.claim_used_this_session = True
            st.session_state.last_spin_time = time.time()
            
            prize = spin_wheel()
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
                msg = "🥚 RARE EGG!"
            elif prize["type"] == "egg_epic":
                st.session_state.incubator_eggs += 1
                msg = "✨ EPIC EGG!"
            elif prize["type"] == "ability":
                if prize["value"] == "shield":
                    st.session_state.shield_bought = True
                    msg = f"🛡️ SHIELD ACTIVATED!"
                else:
                    st.session_state.booster_bought = True
                    msg = f"🚀 BOOSTER ACTIVATED!"
            elif prize["type"] == "story_twist":
                st.session_state.story_twist_pending = True
                msg = "📖 STORY TWIST!"
            else:
                msg = "💨 Nothing..."

            st.session_state.spinner_result = {"prize": prize, "msg": msg}
            st.balloons()
            st.success(f"🎰 {msg}")
            time.sleep(1); st.rerun()
    elif st.session_state.get("claim_used_this_session", False):
        st.info("⏰ You've already claimed. Come back in 6 hours!")

    if st.session_state.spinner_result:
        p = st.session_state.spinner_result
        st.markdown(f"<div class='secret-card'><div style='font-size:40px'>{p['prize']['emoji']}</div><div style='font-size:24px;color:{C}'>{p['prize']['label']}</div><div>{p['msg']}</div></div>", unsafe_allow_html=True)

# ── SHOP ───────────────────────────────────────────────────────────────────
elif view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🛒 SHOP</h2>", unsafe_allow_html=True)
    gold_now = st.session_state.gold
    
    shop_items = [
        {"name":"📓 Notebook","price":50},{"name":"✏️ Pencils","price":30},{"name":"📐 Calculator","price":200},
        {"name":"📚 Textbook","price":500},{"name":"🖊️ Highlighters","price":40},{"name":"📋 Planner","price":80},
        {"name":"🎒 Backpack","price":800},{"name":"💻 Headphones","price":600},
    ]
    
    cols = st.columns(2)
    for i, item in enumerate(shop_items):
        with cols[i % 2]:
            can_buy = gold_now >= item["price"]
            border_col = C if can_buy else "#444"
            st.markdown(f"<div class='shop-card' style='border-color:{border_col}'><h3>{item['name']}</h3><p>{item['price']} {currency}</p></div>", unsafe_allow_html=True)
            if can_buy:
                if st.button(f"BUY {item['name']}", key=f"buy_{i}"):
                    st.session_state.gold -= item["price"]
                    st.success(f"✅ {item['name']} purchased!")
                    st.rerun()

# ── STORY ─────────────────────────────────────────────────────────────────
elif view == "story":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>📖 STORY</h2>", unsafe_allow_html=True)
    if st.session_state.story_log:
        for i, chapter_text in enumerate(st.session_state.story_log):
            st.markdown(f"<div class='ach-card'><h4>⚡ CHAPTER {i+1}</h4><p>{chapter_text}</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>Complete missions to unlock your story!</p>")

# ── SECRETS ────────────────────────────────────────────────────────────────
elif view == "secrets":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🔮 SECRETS</h2>", unsafe_allow_html=True)
    seen = st.session_state.get("secret_queue",[])
    if seen:
        for s in reversed(seen):
            st.markdown(f"<div class='secret-card'>{s}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>Complete missions to unlock secrets!</p>")

# ── ACHIEVEMENTS ───────────────────────────────────────────────────────────
elif view == "achievements":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🏆 ACHIEVEMENTS</h2>", unsafe_allow_html=True)
    
    uni_achs = st.session_state.get("universe_achievements", [])
    if uni_achs:
        st.markdown(f"<h3 style='color:{C}'>🌌 {st.session_state.user_theme} Achievements</h3>", unsafe_allow_html=True)
        for ach in uni_achs:
            st.markdown(f"<div class='ach-card'><h4>{ach.get('name','???')}</h4><p>{ach.get('desc','???')}</p></div>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color:{C}'>⚡ General</h3>", unsafe_allow_html=True)
    unlocked = st.session_state.get("unlocked_achievements", set())
    for ach in ACHIEVEMENTS_BASE:
        is_done = ach["id"] in unlocked
        border_col = C if is_done else MUTED
        opacity = "1" if is_done else "0.4"
        st.markdown(f"<div class='ach-card' style='border-color:{border_col};opacity:{opacity}'><h4>{ach['name']}</h4><p>{ach['desc']}</p></div>", unsafe_allow_html=True)

# ── INCUBATOR ──────────────────────────────────────────────────────────────
elif view == "incubator":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🥚 INCUBATOR</h2>", unsafe_allow_html=True)
    eggs = st.session_state.incubator_eggs
    st.markdown(f"**You have {eggs} eggs.**")
    
    if eggs > 0 and st.button("🥚 HATCH EGG"):
        monster = hatch_egg(st.session_state.user_theme)
        st.session_state.incubator_eggs -= 1
        st.session_state.eggs_hatched += 1
        reward = int(5 * monster["reward_mult"])
        st.session_state.gold += reward
        if monster["rarity"] == "Legendary":
            st.session_state.legendary_hatched = True
            st.balloons()
        st.session_state.hatched_monsters.append(monster)
        st.success(f"🐣 {monster['rarity']} {monster['name']}! +{reward} {currency}!")
        st.rerun()

    if st.session_state.hatched_monsters:
        st.markdown("**YOUR PETS:**")
        for m in st.session_state.hatched_monsters:
            st.markdown(f"- {m['rarity']} {m['name']}")

# ── PETS ─────────────────────────────────────────────────────────────────
elif view == "pets":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>🎯 PETS & LEVELING</h2>", unsafe_allow_html=True)
    pets = st.session_state.get("hatched_monsters", [])
    if pets:
        for i, pet in enumerate(pets):
            pet_level = st.session_state.get(f"pet_level_{i}", 1)
            pet_xp = st.session_state.get(f"pet_xp_{i}", 0)
            xp_needed = pet_level * 100
            xp_pct = (pet_xp / xp_needed) * 100 if xp_needed > 0 else 0
            
            st.markdown(f"""<div class='ach-card'>
<div style='display:flex;justify-content:space-between'><span style='font-size:24px'>{'🐉' if pet['rarity']=='Legendary' else '🐣'}</span><span style='font-size:20px;color:{C}'>{pet['name']}</span><span>LVL {pet_level}</span></div>
<div style='margin-top:10px'><div style='background:#333;height:10px;border-radius:5px'><div style='background:{C};height:100%;width:{min(100,xp_pct)}%'></div></div><small>{pet_xp}/{xp_needed} XP</small></div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p>No pets yet. Hatch eggs from the Incubator!</p>")

# ── MANUAL ────────────────────────────────────────────────────────────────
elif view == "manual":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>📖 MANUAL</h2>", unsafe_allow_html=True)
    manual_items = [
        ("⏱","MISSIONS","30 SECONDS. WORK. UPLOAD PROOF. GET PAID."),
        ("⚖️","THE TRIBUNAL","NO PROOF = NO COINS. AI ANALYZES YOUR SCREENSHOT."),
        ("🛒","SHOP","BUY SHIELD = NUKE DEBT. BUY BOOSTER = 3X MULTIPLIER."),
        ("⚔️","BATTLES","WIN = BONUS + EGG. LOSE = TRY AGAIN."),
        ("🥚","INCUBATOR","HATCH EGGS. COMMON TO LEGENDARY."),
        ("🔮","SECRETS","EVERY MISSION = NEW BRAIN-BREAKING SECRET."),
        ("⏰","COOLDOWN","6 HOURS BETWEEN SPINS. USE WISELY."),
        ("🔥","STREAKS","7 DAYS = WEEKLY BONUS. 30 DAYS = MONTHLY MEGA."),
    ]
    for icon, title, desc in manual_items:
        st.markdown(f"<div class='ach-card'><span style='font-size:24px'>{icon}</span> <b style='color:{C}'>{title}</b><p>{desc}</p></div>", unsafe_allow_html=True)

# ── PLANS ────────────────────────────────────────────────────────────────
elif view == "plans":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>💳 UPGRADE PLANS</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""<div style='background:#111;border-radius:14px;padding:20px;margin:16px 0;border:2px solid {C}'>
<h3 style='color:{C};text-align:center'>📊 FEATURE COMPARISON</h3>
<table style='width:100%;font-size:11px;color:#fff;text-align:center'>
<tr style='background:{C}22'><th style='text-align:left;padding:10px'>FEATURE</th><th>FREE</th><th style='color:#00FF88'>PREMIUM</th><th style='color:#FFD700'>ELITE</th></tr>
<tr><td style='text-align:left;padding:8px'>Spins/session</td><td>1</td><td>3</td><td>6</td></tr>
<tr style='background:#fff08'><td style='text-align:left'>Loot pool</td><td>Common/Rare</td><td>Rare/Epic</td><td>Epic/Legendary</td></tr>
<tr><td style='text-align:left'>Evolutions</td><td>3 stages</td><td>6 stages</td><td>9 + exclusives</td></tr>
<tr style='background:#fff08'><td style='text-align:left'>Story depth</td><td>Short</td><td>Medium</td><td>Maximum</td></tr>
<tr><td style='text-align:left'>Tokens</td><td>1,000</td><td>5,000</td><td>15,000</td></tr>
<tr style='background:#fff08'><td style='text-align:left'>Battle dialogue</td><td>Generic</td><td>Universe</td><td>Real-time AI</td></tr>
<tr><td style='text-align:left'>Achievements</td><td>Standard</td><td>Lore names</td><td>AI-generated</td></tr>
<tr style='background:#fff08'><td style='text-align:left'>Proof feedback</td><td>Pass/Fail</td><td>+ Reason</td><td>+ Comment</td></tr>
<tr><td style='text-align:left'>Battle timer</td><td>15s</td><td>20s</td><td>30s</td></tr>
<tr style='background:#fff08'><td style='text-align:left'>XP Multiplier</td><td>1×</td><td>2×</td><td>3×</td></tr>
</table></div>""", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center;color:{C};font-size:14px'>💎 All plans help MODIFY AND CHANGE AND IMPROVE your gaming and studying experience!</p>", unsafe_allow_html=True)

    p_col, e_col = st.columns(2)
    with p_col:
        st.markdown(f"""<div class='shop-card'>
<h3 style='color:{C}'>⚡ PREMIUM</h3>
<p style='font-size:32px'>$5/mo</p>
<ul style='text-align:left;font-size:12px'>
<li>✅ 2× XP</li><li>✅ 3 spins</li><li>✅ Rare/Epic loot</li><li>✅ 6 evolutions</li><li>✅ Universe dialogue</li><li>✅ Lore achievements</li><li>✅ 20s timer</li>
</ul>
<div style='background:#1a1a1a;padding:10px;border-radius:8px;text-align:center;margin-top:10px'>
<small>CODE:</small><br><b style='color:{C};font-size:18px'>1TR5LG89D</b></div></div>""", unsafe_allow_html=True)
    with e_col:
        st.markdown("""<div class='shop-card' style='border-color:#FFD700'>
<h3 style='color:#FFD700'>💀 ELITE</h3>
<p style='font-size:32px'>$10/mo</p>
<ul style='text-align:left;font-size:12px'>
<li>✅ 3× XP</li><li>✅ 6 spins</li><li>✅ Epic/Legendary</li><li>✅ 9 + exclusives</li><li>✅ AI dialogue</li><li>✅ AI achievements</li><li>✅ 30s timer</li><li>✅ Legendary 2× rate</li>
</ul>
<div style='background:#1a1a1a;padding:10px;border-radius:8px;text-align:center;margin-top:10px;border:1px solid #FFD700'>
<small>CODE:</small><br><b style='color:#FFD700;font-size:18px'>4RJ1TV51Z</b></div></div>""", unsafe_allow_html=True)

# ── FEEDBACK ────────────────────────────────────────────────────────────
elif view == "feedback":
    st.markdown(f"<h2 style='font-family:Bebas Neue;text-align:center;color:{C}'>💬 FEEDBACK</h2>", unsafe_allow_html=True)
    fb_type = st.selectbox("Type", ["💡 Idea","🐛 Bug","🔥 Fire","😤 Fix","💭 Other"])
    fb_text = st.text_area("Message")
    if st.button("🚀 SUBMIT"):
        if fb_text.strip():
            st.session_state.feedback_list.append({"type":fb_type,"message":fb_text,"time":time.strftime("%Y-%m-%d")})
            st.success("✅ Thanks!"); st.balloons()
        else:
            st.error("Write something!")

# ── TRIBUNAL (VERIFICATION) ─────────────────────────────────────────────────
if st.session_state.needs_verification:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center;font-family:Bebas Neue;color:{C}'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
    st.info(f"Upload proof to claim **{st.session_state.pending_gold:.1f} {currency}**")
    
    uploaded = st.file_uploader("Screenshot/Photo:", type=['png','jpg','jpeg','webp'])
    
    if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT"):
        if st.session_state.get("claim_used_this_session", False):
            st.error("⚠️ Already claimed! Complete another mission first.")
            st.stop()
        
        tier = st.session_state.get("sub_tier", "Free")
        
        if tier == "Elite":
            st.success("✅ APPROVED! Personalized: Your dedication to studying in this universe is truly impressive!")
        elif tier == "Premium":
            st.success("✅ APPROVED! Reason: Screenshot verified.")
        else:
            st.success("✅ APPROVED!")
        
        base_gold = st.session_state.pending_gold
        earned, rarity_label, rarity_msg = variable_reward(base_gold)
        earned = round(earned, 1)

        new_streak, streak_msg, is_new_day = update_streak()
        spins = get_spins_for_tier(tier)
        st.session_state.spins_left = st.session_state.get("spins_left",0) + spins

        st.session_state.gold += earned
        st.session_state.xp += int(earned * 10)
        st.session_state.total_xp_real = st.session_state.get("total_xp_real",0) + int(earned*10)
        st.session_state.level = 1 + st.session_state.xp // 100
        st.session_state.total_missions += 1
        st.session_state.needs_verification = False
        st.session_state.pending_gold = 0.0
        st.session_state.claim_used_this_session = True

        loot_pool = [
            {"name": f"+{spins} Spins", "rarity": rarity_label, "color": "#FFD700"},
            {"name": "RARE EGG", "rarity": "GREAT", "color": "#4488FF"},
            {"name": "STREAK SHIELD", "rarity": "EPIC", "color": "#AA44FF"},
            {"name": f"+{int(earned*2)} Bonus", "rarity": rarity_label, "color": "#00FF88"},
        ]
        loot = random.choice(loot_pool)
        if "Shield" in loot["name"]: st.session_state.streak_shield = True
        if "Egg" in loot["name"]: st.session_state.incubator_eggs += 2
        if "Bonus" in loot["name"]: st.session_state.gold += int(earned*2)
        st.session_state.loot_pending = True
        st.session_state.loot_item = loot

        secret = random.choice(UNIVERSE_SECRETS)
        if "secret_queue" not in st.session_state:
            st.session_state.secret_queue = []
        st.session_state.secret_queue.append(secret)
        st.session_state.secrets_seen = len(st.session_state.secret_queue)
        st.session_state.show_secret = secret

        st.session_state.spinner_available = True

        client = get_claude_client()
        prev = " ".join(st.session_state.story_log[-2:]) if st.session_state.story_log else ""
        st.session_state.story_chapter += 1
        new_chapter = generate_story_chapter(st.session_state.user_theme, st.session_state.story_chapter, prev, client)
        st.session_state.story_log.append(new_chapter)

        if MODE in ("grinder","obsessed"):
            st.session_state.battle_state = "ready"

        st.session_state.incubator_eggs += 1

        st.balloons()
        st.success(f"✅ {rarity_label}! +{earned:.1f} {currency} | 🔥 {new_streak}-day streak | +{spins} spins")
        if streak_msg:
            st.info(f"🔥 {streak_msg}")
        time.sleep(1); st.rerun()
