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
    "🌌 The observable universe is just 4% of all matter. The rest? Completely invisible dark energy we can't explain.",
    "⚡ Every atom in your body was forged inside a dying star. You are literally made of stardust.",
    "🧠 Your brain generates enough electricity to power a small LED bulb. You are a walking power source.",
    "🌀 Time moves faster on top of mountains than at sea level. GPS satellites have to correct for this every single day.",
    "🔮 Quantum particles can be in two places at once — until you look at them. Reality literally changes when observed.",
    "💀 The universe is 13.8 billion years old. Humans have existed for 0.0015% of that time.",
    "🌊 There are more possible chess games than atoms in the observable universe. Infinity is closer than you think.",
    "🧬 Your DNA, if uncoiled, would stretch from Earth to the Sun and back — 600 times.",
    "🕳️ A black hole the mass of Earth would be the size of a marble. That marble would destroy everything.",
    "💫 The Milky Way galaxy is on a collision course with Andromeda. In 4 billion years — they merge.",
    "🌡️ Space is not empty. It has a temperature: -270.45°C. Almost absolute zero but not quite.",
    "⏰ If the history of Earth was compressed into 24 hours, humans appear at 11:59:58 PM.",
    "🔬 There are more bacteria in your gut right now than stars in the Milky Way.",
    "🌍 The Earth's magnetic poles are slowly drifting. North is moving toward Siberia as you read this.",
    "💥 The sun loses 4 million tons of mass every single second converting it to pure energy.",
    "🧲 If you removed all the empty space from every human on Earth, we'd fit in a sugar cube.",
    "🌙 The Moon is slowly drifting away from Earth — 3.8cm per year. One day it will escape.",
    "⚛️ Protons are made of quarks. Quarks are held together by gluons. If you tried to pull them apart — new quarks appear from nothing.",
    "🕊️ Pigeons can detect magnetic fields. They literally have a compass built into their biology.",
    "🌿 Trees communicate through underground fungal networks. Forests are talking right now.",
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
]

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
        if st.button("⚡ WAIT... HOW DOES THIS WORK??", key="how_toggle"):
            st.session_state.how_open = not st.session_state.how_open

        if st.session_state.how_open:
            st.markdown("""
            <div class="how-expand">
                <div class="how-step">
                    <span class="how-step-icon">🌌</span>
                    <div class="how-step-title">STEP 1 — PICK YOUR UNIVERSE</div>
                    <div class="how-step-desc">MINECRAFT. NARUTO. NIKE. YOUR WEIRD CUSTOM WORLD NOBODY ELSE GETS. THE AI BUILDS IT. INSTANTLY. 🔥 COLORS. CURRENCY. ABILITIES. ALL OF IT.</div>
                </div>
                <div class="how-step">
                    <span class="how-step-icon">⏱</span>
                    <div class="how-step-title">STEP 2 — DO 30 SECONDS OF WORK</div>
                    <div class="how-step-desc">LITERALLY 30 SECONDS. STUDY. READ. DO ONE THING. THAT'S IT. YOU GET PAID IN YOUR UNIVERSE'S CURRENCY. 💰 YES. FOR REAL.</div>
                </div>
                <div class="how-step">
                    <span class="how-step-icon">📸</span>
                    <div class="how-step-title">STEP 3 — PROVE IT</div>
                    <div class="how-step-desc">SCREENSHOT. PHOTO. NOTES. ANYTHING. UPLOAD IT TO THE TRIBUNAL ⚖️ AND COLLECT YOUR COINS. NO PROOF = NO COINS. SIMPLE.</div>
                </div>
                <div class="how-step">
                    <span class="how-step-icon">🏆</span>
                    <div class="how-step-title">STEP 4 — GO CRAZY</div>
                    <div class="how-step-desc">BUY ABILITIES. WIN BATTLES. HATCH MONSTERS. UNLOCK ACHIEVEMENTS. DISCOVER SECRETS ABOUT THE UNIVERSE THAT WILL BREAK YOUR BRAIN. 🤯 ALL FROM STUDYING.</div>
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
        theme_input = st.text_input("🌌 Your Universe", placeholder="Minecraft, Naruto, F1, Dark Souls Ninja, Medieval Space War...", key="gw_theme")

        st.markdown("""
        <p class="default-hint">💡 Leave empty for default universe: <strong>INFINITE POWER</strong></p>
        <p class="default-hint">✨ Go broad or ultra-specific — <strong>"Naruto meets Cyberpunk"</strong>, <strong>"Medieval Space War"</strong>, <strong>"Stealth Assassin Nike"</strong> — the more detail you give, the better the AI builds your world.</p>
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
    if st.button("🚀 MISSION HUB",  key="nav_hub"):      st.session_state.view = "main";     st.rerun()
    if st.button("⚔️ BATTLE",       key="nav_battle"):   st.session_state.view = "battle";   st.rerun()
    if st.button("🛒 ARSENAL",      key="nav_shop"):     st.session_state.view = "shop";     st.rerun()
    if st.button("🔮 SECRETS",      key="nav_secrets"):  st.session_state.view = "secrets";  st.rerun()
    if st.button("💬 FEEDBACK",     key="nav_feedback"): st.session_state.view = "feedback"; st.rerun()

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
# BATTLE SCREEN — locked per battle, one reward only, universe-specific style
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("battle_state") == "ready" or st.session_state.view == "battle":

    # Freeze monster + style at battle start so re-renders don't re-roll
    if "current_battle" not in st.session_state or st.session_state.current_battle is None:
        battle_style = wd.get("battle_style", "random")
        if battle_style == "random":
            battle_style = random.choice(["shooter","turnbased","reaction","survival","rhythm","rpgclick","trivia"])
        monster_roll = random.randint(1,100)
        if monster_roll > 90:
            mon = {"name":f"Legendary {st.session_state.user_theme} Titan", "hp":7,"reward":20,"rarity":"Legendary"}
        elif monster_roll > 70:
            mon = {"name":f"Epic {st.session_state.user_theme} Warlord",   "hp":5,"reward":12,"rarity":"Epic"}
        elif monster_roll > 40:
            mon = {"name":f"Rare {st.session_state.user_theme} Hunter",    "hp":4,"reward":8, "rarity":"Rare"}
        else:
            mon = {"name":f"{st.session_state.user_theme} Scout",          "hp":3,"reward":5, "rarity":"Common"}
        st.session_state.current_battle = {
            "style": battle_style, "monster": mon,
            "reward_paid": False,   # LOCK — only pay once
            "hp_remaining": mon["hp"],
            "player_hp": 5,
            "turn": 0,
            "shooter_hits": 0,
            "shooter_targets": random.sample(range(9), 3),  # 3 targets in 9-grid
            "shooter_clicks": set(),
            "trivia_answered": False,
        }

    cb     = st.session_state.current_battle
    mon    = cb["monster"]
    bstyle = cb["style"]
    rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
    rc = rarity_colors.get(mon["rarity"],"#ffffff")

    # HP bar helper
    def hp_bar(current, maximum, color):
        pct = max(0, current / maximum)
        filled = int(pct * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"<span style='color:{color};font-family:Space Mono,monospace;font-size:13px'>{bar} {current}/{maximum}</span>"

    st.markdown(f"""<div class='monster-card'>
        <div style='font-size:11px;color:{rc};letter-spacing:3px;font-family:Space Mono,monospace'>{mon["rarity"].upper()} ENCOUNTER · {bstyle.upper()} BATTLE</div>
        <div style='font-family:Bebas Neue,sans-serif;font-size:34px;color:{C};margin:8px 0'>{mon["name"].upper()}</div>
        <div style='margin:6px 0'>Enemy HP: {hp_bar(cb["hp_remaining"], mon["hp"], "#ff4444")}</div>
        <div style='margin:6px 0'>Your HP:  {hp_bar(cb["player_hp"], 5, "#44ff88")}</div>
        <div style='font-size:12px;color:#ffffff;margin-top:8px'>Win reward: <span style='color:{C};font-weight:bold'>{mon["reward"]} {currency}</span>{"  ·  <span style='color:#aaaaaa;font-size:11px'>Reward already claimed</span>" if cb["reward_paid"] else ""}</div>
    </div>""", unsafe_allow_html=True)

    _, bcol, _ = st.columns([1,2,1])
    with bcol:

        # ── TURN-BASED (Anime, RPG, Fantasy) ──────────────────────────────
        if bstyle == "turnbased":
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>⚔️ TURN-BASED COMBAT · Choose your move</p>", unsafe_allow_html=True)
            move1 = wd.get("shield_name","DEFEND")[:18]
            move2 = wd.get("booster_name","STRIKE")[:18]
            a1, a2, a3 = st.columns(3)
            outcome = None
            with a1:
                if st.button(f"⚔️ {move1}", key="tb_attack"):
                    dmg = random.randint(1,3)
                    cb["hp_remaining"] = max(0, cb["hp_remaining"] - dmg)
                    enemy_dmg = random.randint(0,2)
                    cb["player_hp"] = max(0, cb["player_hp"] - enemy_dmg)
                    cb["turn"] += 1
                    outcome = ("hit", dmg, enemy_dmg)
            with a2:
                if st.button(f"⚡ {move2}", key="tb_boost"):
                    dmg = random.randint(2,4)
                    cb["hp_remaining"] = max(0, cb["hp_remaining"] - dmg)
                    enemy_dmg = random.randint(1,3)
                    cb["player_hp"] = max(0, cb["player_hp"] - enemy_dmg)
                    cb["turn"] += 1
                    outcome = ("boost", dmg, enemy_dmg)
            with a3:
                if st.button("🛡️ DEFEND", key="tb_defend"):
                    cb["player_hp"] = min(5, cb["player_hp"] + 1)
                    enemy_dmg = random.randint(0,1)
                    cb["player_hp"] = max(0, cb["player_hp"] - enemy_dmg)
                    cb["turn"] += 1
                    outcome = ("defend", 0, enemy_dmg)
            if outcome:
                otype, dealt, took = outcome
                msg = f"⚔️ Dealt **{dealt}** damage" if otype != "defend" else "🛡️ You blocked and recovered HP"
                if took > 0: msg += f" · Enemy struck back for **{took}**"
                st.info(msg)
                if cb["hp_remaining"] <= 0:
                    if not cb["reward_paid"]:
                        st.session_state.gold += mon["reward"]
                        st.session_state.battles_won += 1
                        cb["reward_paid"] = True
                    st.session_state.battles_fought += 1
                    st.session_state.incubator_eggs += 1
                    st.session_state.current_battle = None
                    st.session_state.battle_state = None
                    st.success(f"🏆 ENEMY DEFEATED! +{mon['reward']} {currency}!")
                    time.sleep(1); st.rerun()
                elif cb["player_hp"] <= 0:
                    st.session_state.battles_fought += 1
                    st.session_state.current_battle = None
                    st.session_state.battle_state = None
                    st.error("💀 YOU FELL IN BATTLE. No reward. Try again next mission.")
                    time.sleep(1); st.rerun()
                else:
                    st.rerun()

        # ── SHOOTER (FPS games) ───────────────────────────────────────────
        elif bstyle == "shooter":
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>🎯 SHOOTER — Tap the 🎯 targets, avoid the 💨 decoys</p>", unsafe_allow_html=True)
            targets = cb["shooter_targets"]
            clicks  = cb["shooter_clicks"]
            grid = st.columns(3)
            for i in range(9):
                col = grid[i % 3]
                with col:
                    if i in clicks:
                        st.markdown(f"<div style='text-align:center;font-size:24px;padding:8px'>✅</div>", unsafe_allow_html=True)
                    else:
                        label = "🎯" if i in targets else "💨"
                        if st.button(label, key=f"shoot_{i}"):
                            cb["shooter_clicks"].add(i)
                            if i in targets:
                                cb["hp_remaining"] = max(0, cb["hp_remaining"] - 1)
                            else:
                                cb["player_hp"] = max(0, cb["player_hp"] - 1)
                            st.rerun()
            hits = len(clicks & set(targets))
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:12px'>Hits: {hits}/{len(targets)}</p>", unsafe_allow_html=True)
            if cb["hp_remaining"] <= 0:
                if not cb["reward_paid"]:
                    st.session_state.gold += mon["reward"]
                    st.session_state.battles_won += 1
                    cb["reward_paid"] = True
                st.session_state.battles_fought += 1
                st.session_state.incubator_eggs += 1
                st.session_state.current_battle = None
                st.session_state.battle_state = None
                st.success(f"🏆 ALL TARGETS DOWN! +{mon['reward']} {currency}!")
                time.sleep(1); st.rerun()
            elif cb["player_hp"] <= 0:
                st.session_state.battles_fought += 1
                st.session_state.current_battle = None
                st.session_state.battle_state = None
                st.error("💀 TOO MANY MISSES. You got eliminated.")
                time.sleep(1); st.rerun()

        # ── RPG CLICK (Minecraft, Terraria, sandbox) ──────────────────────
        elif bstyle == "rpgclick":
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>⛏️ RPG COMBAT — Mine the enemy's HP down to zero!</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;color:#aaaaaa;font-size:12px'>Each click deals 1 damage · Enemy hits back randomly</p>", unsafe_allow_html=True)
            if st.button(f"⛏️ ATTACK  ({cb['hp_remaining']} HP left)", key="rpg_click"):
                cb["hp_remaining"] = max(0, cb["hp_remaining"] - 1)
                if random.random() > 0.6:
                    cb["player_hp"] = max(0, cb["player_hp"] - 1)
                if cb["hp_remaining"] <= 0:
                    if not cb["reward_paid"]:
                        st.session_state.gold += mon["reward"]
                        st.session_state.battles_won += 1
                        cb["reward_paid"] = True
                    st.session_state.battles_fought += 1
                    st.session_state.incubator_eggs += 1
                    st.session_state.current_battle = None
                    st.session_state.battle_state = None
                    st.success(f"🏆 DEFEATED! +{mon['reward']} {currency}!")
                    time.sleep(1); st.rerun()
                elif cb["player_hp"] <= 0:
                    st.session_state.battles_fought += 1
                    st.session_state.current_battle = None
                    st.session_state.battle_state = None
                    st.error("💀 YOU DIED. Respawn next mission.")
                    time.sleep(1); st.rerun()
                else:
                    st.rerun()

        # ── REACTION (Sports, Racing) ──────────────────────────────────────
        elif bstyle in ("reaction","racing"):
            label = "🏎️ OVERTAKE!" if bstyle == "racing" else "⚡ GO!"
            desc  = "🏎️ RACING — Hit OVERTAKE at exactly the right moment!" if bstyle == "racing" else "⚡ REACTION — Hit GO the instant you see the signal!"
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>{desc}</p>", unsafe_allow_html=True)
            # Fake delay signal using turn count
            if cb["turn"] == 0:
                st.markdown(f"<p style='text-align:center;font-size:40px'>🔴</p>", unsafe_allow_html=True)
                if st.button("WAIT FOR GREEN...", key="react_wait"):
                    cb["turn"] = 1
                    st.rerun()
            elif cb["turn"] == 1:
                st.markdown(f"<p style='text-align:center;font-size:40px'>🟡</p>", unsafe_allow_html=True)
                if st.button("ALMOST...", key="react_almost"):
                    cb["turn"] = 2
                    st.rerun()
            else:
                st.markdown(f"<p style='text-align:center;font-size:40px'>🟢</p>", unsafe_allow_html=True)
                if st.button(label, key="react_go"):
                    won = random.random() > 0.35
                    if won and not cb["reward_paid"]:
                        st.session_state.gold += mon["reward"]
                        st.session_state.battles_won += 1
                        cb["reward_paid"] = True
                    st.session_state.battles_fought += 1
                    st.session_state.incubator_eggs += 1
                    st.session_state.current_battle = None
                    st.session_state.battle_state = None
                    if won: st.success(f"🏆 PERFECT TIMING! +{mon['reward']} {currency}!")
                    else:   st.error("💀 TOO LATE! You missed the window.")
                    time.sleep(1); st.rerun()

        # ── SURVIVAL (Horror) ─────────────────────────────────────────────
        elif bstyle == "survival":
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>😰 SURVIVAL — Make the right call or get caught!</p>", unsafe_allow_html=True)
            actions = [("🏃 SPRINT", 0.55), ("🕳️ HIDE", 0.65), ("🪟 WINDOW", 0.45), ("🔇 SILENT WALK", 0.70)]
            random.shuffle(actions)
            cols = st.columns(2)
            for idx, (act_label, win_chance) in enumerate(actions):
                with cols[idx % 2]:
                    if st.button(act_label, key=f"surv_{idx}"):
                        won = random.random() < win_chance
                        if won and not cb["reward_paid"]:
                            st.session_state.gold += mon["reward"]
                            st.session_state.battles_won += 1
                            cb["reward_paid"] = True
                        st.session_state.battles_fought += 1
                        st.session_state.incubator_eggs += 1
                        st.session_state.current_battle = None
                        st.session_state.battle_state = None
                        if won: st.success(f"🏆 YOU ESCAPED! +{mon['reward']} {currency}!")
                        else:   st.error("💀 CAUGHT. You didn't make it out.")
                        time.sleep(1); st.rerun()

        # ── RHYTHM (Music, Fashion, K-pop) ───────────────────────────────
        elif bstyle == "rhythm":
            sequence = ["🎵","🥁","🎸","🎵","🥁"]
            if "rhythm_seq" not in cb: cb["rhythm_seq"] = 0
            step = cb["rhythm_seq"]
            total = len(sequence)
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>🎵 RHYTHM BATTLE — Hit the beats in order! ({step}/{total})</p>", unsafe_allow_html=True)
            st.progress(step / total)
            beat_cols = st.columns(total)
            for i, beat in enumerate(sequence):
                with beat_cols[i]:
                    if i < step:
                        st.markdown(f"<div style='text-align:center;font-size:28px;opacity:0.4'>{beat}</div>", unsafe_allow_html=True)
                    elif i == step:
                        if st.button(beat, key=f"beat_{i}_{step}"):
                            cb["rhythm_seq"] = step + 1
                            st.rerun()
                    else:
                        st.markdown(f"<div style='text-align:center;font-size:28px;opacity:0.2'>⬜</div>", unsafe_allow_html=True)
            if step >= total:
                if not cb["reward_paid"]:
                    st.session_state.gold += mon["reward"]
                    st.session_state.battles_won += 1
                    cb["reward_paid"] = True
                st.session_state.battles_fought += 1
                st.session_state.incubator_eggs += 1
                st.session_state.current_battle = None
                st.session_state.battle_state = None
                st.success(f"🎵 PERFECT COMBO! +{mon['reward']} {currency}!")
                time.sleep(1); st.rerun()

        # ── TRIVIA (Academic, school themes) ─────────────────────────────
        elif bstyle == "trivia":
            trivia_q = [
                ("What is 7 × 8?", ["54","56","58","64"], 1),
                ("What planet is closest to the Sun?", ["Venus","Earth","Mercury","Mars"], 2),
                ("What is H2O?", ["Oxygen","Hydrogen","Water","Salt"], 2),
                ("What is 144 ÷ 12?", ["11","12","13","14"], 1),
                ("Who wrote Romeo and Juliet?", ["Dickens","Shakespeare","Tolstoy","Austen"], 1),
            ]
            if "trivia_q" not in cb:
                q = random.choice(trivia_q)
                cb["trivia_q"] = q
                cb["trivia_answered"] = False
            q, opts, correct_idx = cb["trivia_q"]
            st.markdown(f"<div class='monster-card'><p style='color:#ffffff;font-family:Space Mono,monospace;font-size:14px;text-align:center'>{q}</p></div>", unsafe_allow_html=True)
            if not cb["trivia_answered"]:
                opt_cols = st.columns(2)
                for i, opt in enumerate(opts):
                    with opt_cols[i % 2]:
                        if st.button(opt, key=f"trivia_{i}"):
                            cb["trivia_answered"] = True
                            won = (i == correct_idx)
                            if won and not cb["reward_paid"]:
                                st.session_state.gold += mon["reward"]
                                st.session_state.battles_won += 1
                                cb["reward_paid"] = True
                            st.session_state.battles_fought += 1
                            st.session_state.incubator_eggs += 1
                            st.session_state.current_battle = None
                            st.session_state.battle_state = None
                            if won: st.success(f"🏆 CORRECT! +{mon['reward']} {currency}!")
                            else:   st.error(f"💀 WRONG! Answer was: {opts[correct_idx]}")
                            time.sleep(1); st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
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

# ── SECRETS ───────────────────────────────────────────────────────────────────
if view == "secrets":
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
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#ffffff;font-size:12px'>Stripe payments coming soon. Get ready.</p>", unsafe_allow_html=True)

    p_col, e_col = st.columns(2)
    with p_col:
        st.markdown(f"""<div class='shop-card'>
            <div style='text-align:center;margin-bottom:16px'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:{C}'>⚡ PREMIUM</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:48px;color:{TEXT}'>$5<span style='font-size:18px;color:#ffffff'>/mo</span></div>
                <div style='background:rgba(255,165,0,0.2);border:1px solid orange;border-radius:8px;padding:4px 12px;display:inline-block;font-family:Space Mono,monospace;font-size:10px;color:orange;letter-spacing:2px'>COMING SOON</div>
            </div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:{TEXT};line-height:2'>
                ✅ 2× XP on every mission<br>
                ✅ Rare+ ability upgrades<br>
                ✅ Extended mission timer options<br>
                ✅ Custom universe themes<br>
                ✅ Priority AI universe generation<br>
                ✅ Exclusive Premium badge
            </div>
        </div>""", unsafe_allow_html=True)

    with e_col:
        st.markdown(f"""<div class='shop-card' style='border-color:#FFD700'>
            <div style='text-align:center;margin-bottom:16px'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#FFD700'>💀 ELITE</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:48px;color:{TEXT}'>$10<span style='font-size:18px;color:#ffffff'>/mo</span></div>
                <div style='background:rgba(255,215,0,0.2);border:1px solid #FFD700;border-radius:8px;padding:4px 12px;display:inline-block;font-family:Space Mono,monospace;font-size:10px;color:#FFD700;letter-spacing:2px'>COMING SOON</div>
            </div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:{TEXT};line-height:2'>
                ✅ 3× XP on every mission<br>
                ✅ ALL ability tiers unlocked<br>
                ✅ Full maximum customization<br>
                ✅ Exclusive Elite 💀 badge<br>
                ✅ Cashback on milestone rewards<br>
                ✅ Legendary egg rate doubled<br>
                ✅ Private universe vaults
            </div>
        </div>""", unsafe_allow_html=True)

# ── FEEDBACK ──────────────────────────────────────────────────────────────────
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
                st.success("✅ Micro session done!"); time.sleep(1); st.rerun()
        with tc3:
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
            earned = st.session_state.pending_gold
            st.session_state.gold  += earned
            st.session_state.xp   += int(earned * 10)
            st.session_state.level  = 1 + st.session_state.xp // 100
            st.session_state.total_missions += 1
            st.session_state.needs_verification = False
            st.session_state.pending_gold = 0.0

            # Unlock a secret
            secret = random.choice(UNIVERSE_SECRETS)
            if "secret_queue" not in st.session_state:
                st.session_state.secret_queue = []
            st.session_state.secret_queue.append(secret)
            st.session_state.secrets_seen = len(st.session_state.secret_queue)
            st.session_state.show_secret = secret

            # Queue battle if GRINDER or OBSESSED
            if MODE in ("grinder","obsessed"):
                st.session_state.battle_state = "ready"

            # Earn egg
            st.session_state.incubator_eggs += 1

            st.balloons()
            st.success(f"✅ VERIFIED. +{earned:.1f} {currency} added. 🔮 Secret unlocked!")
            time.sleep(1); st.rerun()
