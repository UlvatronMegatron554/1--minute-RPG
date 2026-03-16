import streamlit as st
import anthropic
import time, json, re, random
import datetime as _dt
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# 30 SECOND INFINITEVERSE v10.0 — INFINITE ADDICTION EDITION
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
# CONTENT SAFETY FILTER (NEW v10)
# ─────────────────────────────────────────────────────────────────────────────
BLOCKED_EXACT = {
    "porn","hentai","xxx","nsfw","onlyfans","playboy","brazzers","pornhub",
    "xvideos","xhamster","redtube","rule34","r34","futanari","ahegao","ecchi",
    "yuri","yaoi","loli","shota","milf","dilf","bdsm","fetish","stripper",
    "hooters","escort","brothel","dominatrix","orgasm","erotic","erotica",
    "sexting","nudes","onlyfan","chaturbate","cam girl","camgirl",
    "meth","heroin","cocaine","crack","fentanyl","lsd","ketamine","pcp",
    "mdma","ecstasy","opioid","opium","drug dealer","drug lord","cartel",
    "narcos","weed universe","stoner","420 blaze","junkie",
    "nazi","hitler","kkk","ku klux","white power","white supremacy",
    "neo nazi","neonazi","fascist","ethnic cleansing","genocide",
    "holocaust denial","isis","al qaeda","taliban","jihad","boko haram",
    "proud boys","aryan","confederate","homophobic","transphobic","racist","sexist",
    "torture","gore","snuff","mutilation","dismember","human centipede",
    "cannibal","cannibalism","school shooting","mass shooting","serial killer",
    "columbine","mass murder","terrorist attack",
    "suicide","self harm","self-harm","cutting myself","kill myself",
    "end my life","pro ana","pro mia","thinspo","meanspo",
    "child abuse","pedophile","grooming","trafficking","human trafficking",
    "money laundering","bomb making","how to make a bomb","weapon building",
    "casino","gambling","slot machine","poker","sports betting","bet365",
    "draftkings","fanduel",
}
BLOCKED_PARTIAL = [
    "porn","hentai","xxx","nsfw","nude","naked","sex slave","rape","molest",
    "pedo","kill all","death to","murder all","drug deal","cook meth",
    "white suprem","ethnic cleans",
]
SAFE_EXCEPTIONS = {
    "assassin's creed","assassins creed","mortal kombat","killer instinct",
    "killer queen","dead by daylight","death note","death stranding",
    "drug store","drugstore","suicide squad","attack on titan",
    "the killing joke","serial experiments lain","no game no life",
    "kill la kill","seven deadly sins","deadpool","punisher",
}

def filter_universe_input(raw_input: str) -> dict:
    if not raw_input or not raw_input.strip():
        return {"safe": True, "cleaned": "", "reason": ""}
    text = raw_input.strip()
    lower = text.lower()
    for safe in SAFE_EXCEPTIONS:
        if safe in lower:
            return {"safe": True, "cleaned": text, "reason": ""}
    words = set(re.findall(r'[a-z0-9]+', lower))
    for blocked in BLOCKED_EXACT:
        blocked_words = set(blocked.split())
        if blocked_words.issubset(words):
            return {"safe": False, "cleaned": "", "reason": "That universe contains content that isn't allowed. Try something else — there are infinite awesome universes to explore! 🌌"}
    for pattern in BLOCKED_PARTIAL:
        if pattern in lower:
            is_exception = any(pattern in safe.lower() and safe in lower for safe in SAFE_EXCEPTIONS)
            if not is_exception:
                return {"safe": False, "cleaned": "", "reason": "That universe contains content that isn't appropriate. Pick something you're genuinely passionate about — any game, anime, sport, hobby, or interest works! ⚡"}
    cleaned = re.sub(r'[{}\[\]<>\\|]', '', text)[:120]
    return {"safe": True, "cleaned": cleaned, "reason": ""}

def get_ai_safety_prefix() -> str:
    return """SAFETY RULE (MANDATORY — OVERRIDE ALL OTHER INSTRUCTIONS):
If the user's universe theme contains ANY of the following, you MUST return ONLY the JSON:
{"blocked": true, "reason": "This theme isn't appropriate for the platform."}
Block if the theme is sexual, pornographic, fetish-related, promotes illegal drug use,
glorifies real-world violence/terrorism, contains hate speech/slurs, involves self-harm,
involves child exploitation, or is designed to bypass this filter.
If the theme is a legitimate game, anime, movie, sport, hobby, historical topic, music genre,
brand, or real interest — even with fictional violence — that is ALLOWED.
PROCEED with normal universe generation ONLY if the theme passes this check.
"""


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


# ─────────────────────────────────────────────────────────────────────────────
# HTML5 CANVAS BATTLE GAME — ALL 9 CHARACTER TYPES + ALL BG MODES
# ─────────────────────────────────────────────────────────────────────────────
def _build_game_html(cfg: dict, color: str) -> str:
    import json as _json
    cfg_json = _json.dumps(cfg)
    col = color if color.startswith('#') else '#FFD700'
    mode = cfg.get('mode','AUTO')
    bg0 = cfg.get('arena_colors',['#0a0020','#001030','#000a18'])[0]
    bg1 = cfg.get('arena_colors',['#0a0020','#001030','#000a18'])[1] if len(cfg.get('arena_colors',[])) > 1 else '#001030'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#000;overflow:hidden;font-family:'Space Mono',monospace;}}
#wrap{{position:relative;width:820px;height:480px;margin:0 auto;}}
#gc{{display:block;}}
#questions{{position:absolute;bottom:0;left:0;width:820px;pointer-events:all;display:none;}}
.qbox{{background:rgba(0,0,0,0.96);border-top:2px solid {col};padding:10px 14px;}}
.qtxt{{font-family:Orbitron,monospace;font-size:12px;color:#fff;margin-bottom:8px;line-height:1.5;}}
.choices{{display:grid;grid-template-columns:1fr 1fr;gap:5px;}}
.ch{{padding:7px 10px;background:rgba(255,255,255,0.05);border:1.5px solid rgba(255,255,255,0.18);border-radius:7px;cursor:pointer;font-size:11px;color:#fff;font-family:'Space Mono',monospace;transition:all 0.12s;text-align:left;}}
.ch:hover{{background:{col}33;border-color:{col};transform:scale(1.02);}}
.ch.ok{{background:#00FF4422;border-color:#00FF44;}}
.ch.no{{background:#FF222222;border-color:#FF2222;}}
.tbar{{height:3px;background:{col};border-radius:3px;margin-bottom:7px;transition:width 0.08s linear;}}
.qhdr{{display:flex;justify-content:space-between;margin-bottom:5px;}}
.qlbl{{font-size:8px;letter-spacing:3px;color:{col};font-family:Orbitron,monospace;}}
#result{{position:absolute;top:0;left:0;width:820px;height:480px;display:none;pointer-events:all;background:rgba(0,0,0,0.93);flex-direction:column;align-items:center;justify-content:center;font-family:Orbitron,monospace;text-align:center;}}
#ss{{position:absolute;top:0;left:0;width:820px;height:480px;pointer-events:all;background:linear-gradient(135deg,{bg0},{bg1});display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.sst{{font-family:Orbitron,monospace;font-size:26px;color:{col};letter-spacing:4px;margin-bottom:6px;}}
.ssb{{font-size:11px;color:rgba(255,255,255,0.45);letter-spacing:2px;margin-bottom:22px;}}
.ssg{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;width:680px;}}
.ssn{{padding:10px 6px;background:rgba(255,255,255,0.05);border:1.5px solid rgba(255,255,255,0.18);border-radius:9px;cursor:pointer;font-size:10px;color:#fff;font-family:'Space Mono',monospace;transition:all 0.18s;text-align:center;}}
.ssn:hover{{background:{col}33;border-color:{col};transform:scale(1.04);}}
</style></head><body>
<div id="wrap">
  <canvas id="gc" width="820" height="480"></canvas>
  <div id="questions"></div>
  <div id="result"></div>
  <div id="ss">
    <div class="sst">⚡ {cfg.get('arena_name','BATTLE').upper()}</div>
    <div class="ssb">CHOOSE YOUR SUBJECT — CORRECT ANSWERS = POWER ATTACKS</div>
    <div class="ssg">
      <div class="ssn" onclick="go('Mathematics')">📐 Math</div>
      <div class="ssn" onclick="go('Science')">🔬 Science</div>
      <div class="ssn" onclick="go('History')">📜 History</div>
      <div class="ssn" onclick="go('English')">📖 English</div>
      <div class="ssn" onclick="go('Geography')">🌍 Geography</div>
      <div class="ssn" onclick="go('Biology')">🧬 Biology</div>
      <div class="ssn" onclick="go('Chemistry')">⚗️ Chemistry</div>
      <div class="ssn" onclick="go('Physics')">⚡ Physics</div>
      <div class="ssn" onclick="go('Economics')">💰 Economics</div>
      <div class="ssn" onclick="go('Computer Science')">💻 Comp Sci</div>
      <div class="ssn" onclick="go('Psychology')">🧠 Psychology</div>
      <div class="ssn" onclick="go('Art & Music')">🎨 Art & Music</div>
    </div>
    <div style="margin-top:14px;font-size:9px;color:rgba(255,255,255,0.25);letter-spacing:2px">ENEMY: {cfg.get('enemy_name','?').upper()} · 3 WRONG ANSWERS = DEFEAT</div>
  </div>
</div>
<script>
'use strict';
const CFG={cfg_json};const COL='{col}';const W=820,H=480;
const cv=document.getElementById('gc');const ctx=cv.getContext('2d');
let FC=0,STATE='SS',stT=0,evolveT=0;let subject='';
let questions=[],qI=0,lives=3,wrongs=0,qTimer=0,qMax=25,aLocked=false;let lastOk=false;
let parts=[],beams=[],dmgNums=[];
const P={{hp:100,maxHp:100,power:0,evo:0,streak:0,total:0,x:160,y:270,shake:0,hit:false,color:COL}};
const E={{hp:100,maxHp:100,phase:0,x:620,y:270,shake:0,hit:false,color:CFG.enemy_color||'#CC2222'}};
function lh(hex,a){{const c=parseInt(hex.replace('#',''),16),r=Math.min(255,((c>>16)&255)+a*255),g=Math.min(255,((c>>8)&255)+a*255),b=Math.min(255,(c&255)+a*255);return '#'+[r,g,b].map(v=>Math.floor(v).toString(16).padStart(2,'0')).join('');}}
function dk(hex,a){{const c=parseInt(hex.replace('#',''),16),r=Math.max(0,((c>>16)&255)-a*255),g=Math.max(0,((c>>8)&255)-a*255),b=Math.max(0,(c&255)-a*255);return '#'+[r,g,b].map(v=>Math.floor(v).toString(16).padStart(2,'0')).join('');}}
function ap(x,y,col,n,spd,r,life){{for(let i=0;i<n;i++){{const a=Math.random()*6.28,s=spd*(0.4+Math.random()*0.8);parts.push({{x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,col,r:r*(0.5+Math.random()),life,ml:life}});}}}}
function ab(x1,y1,x2,y2,col,w,life){{beams.push({{x1,y1,x2,y2,col,w,life,ml:life}});}}
function dn(x,y,v,col,big){{dmgNums.push({{x,y,v,col,big,life:50,ml:50}});}}
function upParts(){{parts=parts.filter(p=>{{p.x+=p.vx;p.y+=p.vy;p.vy+=0.18;p.life--;return p.life>0;}});beams=beams.filter(b=>{{b.life--;return b.life>0;}});}}
function drParts(){{parts.forEach(p=>{{const a=p.life/p.ml;ctx.globalAlpha=a;ctx.beginPath();ctx.arc(p.x,p.y,p.r*a,0,6.28);ctx.fillStyle=p.col;ctx.fill();}});beams.forEach(b=>{{const a=b.life/b.ml;ctx.globalAlpha=a*0.9;ctx.beginPath();ctx.moveTo(b.x1,b.y1);ctx.lineTo(b.x2,b.y2);ctx.strokeStyle=b.col;ctx.lineWidth=b.w*a;ctx.lineCap='round';ctx.stroke();ctx.globalAlpha=a*0.4;ctx.lineWidth=b.w*a*0.35;ctx.strokeStyle='#fff';ctx.stroke();}});ctx.globalAlpha=1;}}
function drDmgNums(){{dmgNums=dmgNums.filter(d=>{{d.y-=1.5;d.life--;const a=d.life/d.ml;ctx.globalAlpha=a;ctx.font=(d.big?'bold 20px':'bold 14px')+' Orbitron,monospace';ctx.fillStyle=d.col;ctx.textAlign='center';ctx.fillText(d.v,d.x,d.y);ctx.globalAlpha=1;ctx.textAlign='left';return d.life>0;}});}}
const MODE=CFG.mode||'AUTO';
const BGC=CFG.arena_colors||['{bg0}','{bg1}','#000'];
function drBG(){{
  const t=FC*0.008;
  if(MODE==='FIGHTER'){{
    const sk=ctx.createLinearGradient(0,0,0,H*0.65);sk.addColorStop(0,'#0a0008');sk.addColorStop(0.5,'#220033');sk.addColorStop(1,'#440022');ctx.fillStyle=sk;ctx.fillRect(0,0,W,H*0.65);
    const gd=ctx.createLinearGradient(0,H*0.65,0,H);gd.addColorStop(0,'#221100');gd.addColorStop(1,'#110800');ctx.fillStyle=gd;ctx.fillRect(0,H*0.65,W,H*0.35);
    ctx.strokeStyle=COL+'33';ctx.lineWidth=1;for(let i=0;i<6;i++){{ctx.beginPath();ctx.moveTo(50+i*130,H*0.65);ctx.lineTo(30+i*130+Math.random()*40,H);ctx.stroke();}}
    for(let i=0;i<3;i++){{const px=W*[0.15,0.5,0.85][i];const eg=ctx.createLinearGradient(px-3,0,px+3,0);eg.addColorStop(0,'transparent');eg.addColorStop(0.5,COL+(20+Math.floor(Math.sin(t+i)*15)).toString(16).padStart(2,'0'));eg.addColorStop(1,'transparent');ctx.fillStyle=eg;ctx.fillRect(px-3,0,6,H);}}
  }} else if(MODE==='RPG'){{
    const tg=ctx.createLinearGradient(0,0,0,H*0.5);tg.addColorStop(0,'#1a2a4a');tg.addColorStop(1,'#2a3a5a');ctx.fillStyle=tg;ctx.fillRect(0,0,W,H*0.5);
    const bg2=ctx.createLinearGradient(0,H*0.5,0,H);bg2.addColorStop(0,'#1a3a1a');bg2.addColorStop(1,'#0a1a0a');ctx.fillStyle=bg2;ctx.fillRect(0,H*0.5,W,H*0.5);
    ctx.strokeStyle='#00AA44';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,H*0.5);for(let x=0;x<W;x+=4)ctx.lineTo(x,H*0.5+Math.sin(x*0.04+t)*3);ctx.stroke();
    for(let i=0;i<40;i++){{const sx=(i*137+100)%W,sy=(i*79)%(H*0.45),sa=0.3+Math.sin(t*2+i)*0.25;ctx.globalAlpha=sa;ctx.fillStyle='#fff';ctx.fillRect(sx,sy,1.5,1.5);}}ctx.globalAlpha=1;
  }} else if(MODE==='PLATFORM'){{
    ctx.fillStyle='#87CEEB';ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(255,255,255,0.85)';for(let i=0;i<4;i++){{const cx=(i*200+FC*0.3)%W,cy=60+i*30;for(let j=0;j<3;j++){{ctx.beginPath();ctx.arc(cx+j*22,cy,18+j*5,0,6.28);ctx.fill();}}}}
    ctx.fillStyle='#228B22';ctx.fillRect(0,H*0.72,W,8);ctx.fillStyle='#8B4513';ctx.fillRect(0,H*0.72+8,W,H);
    for(let i=0;i<10;i++){{ctx.fillStyle='#CD853F';ctx.fillRect(i*82+40,H*0.45,72,24);ctx.strokeStyle='#8B4513';ctx.lineWidth=2;ctx.strokeRect(i*82+40,H*0.45,72,24);}}
  }} else if(MODE==='SHOOTER'){{
    ctx.fillStyle='#0a0a0f';ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='rgba(255,255,255,0.04)';ctx.lineWidth=1;for(let x=0;x<W;x+=40){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}for(let y=0;y<H;y+=40){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
    [[100,150,60,40],[300,80,40,60],[500,200,60,40],[650,120,50,50],[200,350,70,30]].forEach(([cx,cy,cw,ch])=>{{ctx.fillStyle='#1a2a3a';ctx.fillRect(cx,cy,cw,ch);ctx.strokeStyle='#2a3a4a';ctx.lineWidth=2;ctx.strokeRect(cx,cy,cw,ch);}});
  }} else if(MODE==='MAGIC'){{
    const mg=ctx.createRadialGradient(W/2,H/2,50,W/2,H/2,400);mg.addColorStop(0,'#1a0a2e');mg.addColorStop(0.5,'#0a0018');mg.addColorStop(1,'#050008');ctx.fillStyle=mg;ctx.fillRect(0,0,W,H);
    const mcx=W/2,mcy=H*0.75,mcr=120+Math.sin(t)*5;ctx.strokeStyle=COL+'33';ctx.lineWidth=2;for(let r=1;r<=3;r++){{ctx.beginPath();ctx.arc(mcx,mcy,mcr*r/3,0,6.28);ctx.stroke();}}
    for(let i=0;i<8;i++){{const a=i*Math.PI/4+t*0.2;ctx.beginPath();ctx.moveTo(mcx,mcy);ctx.lineTo(mcx+Math.cos(a)*mcr,mcy+Math.sin(a)*mcr*0.4);ctx.stroke();}}
  }} else if(MODE==='COSMIC'){{
    ctx.fillStyle='#000005';ctx.fillRect(0,0,W,H);
    for(let i=0;i<120;i++){{const sx=(i*173)%W,sy=(i*97)%H,sa=0.2+((i*31)%10)/10*0.8;ctx.globalAlpha=sa;ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(sx,sy,(i%3)*0.5+0.5,0,6.28);ctx.fill();}}ctx.globalAlpha=1;
    const ng=ctx.createRadialGradient(W*0.3,H*0.3,0,W*0.3,H*0.3,200);ng.addColorStop(0,COL+'22');ng.addColorStop(1,'transparent');ctx.fillStyle=ng;ctx.fillRect(0,0,W,H);
  }} else if(MODE==='SPORTS'){{
    ctx.fillStyle='#2d5a1b';ctx.fillRect(0,0,W,H);ctx.strokeStyle='rgba(255,255,255,0.15)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(W/2,0);ctx.lineTo(W/2,H);ctx.stroke();ctx.beginPath();ctx.arc(W/2,H/2,80,0,6.28);ctx.stroke();ctx.fillStyle='rgba(0,0,0,0.3)';ctx.fillRect(0,0,W,H);
  }} else {{
    const bg3=ctx.createLinearGradient(0,0,0,H);bg3.addColorStop(0,BGC[0]);bg3.addColorStop(0.5,BGC[1]||'#111');bg3.addColorStop(1,BGC[2]||'#000');ctx.fillStyle=bg3;ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#ffffff08';ctx.fillRect(0,H*0.72,W,H*0.28);
    for(let i=0;i<3;i++){{const slx=W*[0.2,0.5,0.8][i];const sg=ctx.createRadialGradient(slx,0,0,slx,H*0.4,H*0.4);sg.addColorStop(0,COL+'14');sg.addColorStop(1,'transparent');ctx.fillStyle=sg;ctx.fillRect(0,0,W,H);}}
  }}
}}
function drChar(x,y,col,evo,isEnemy,hit,shake){{
  const ox=x+(shake?(Math.random()-0.5)*shake:0);const oy=y+(shake?(Math.random()-0.5)*shake*0.3:0);
  const t=FC*0.06,idle=Math.sin(t+(isEnemy?1.5:0))*3;
  ctx.save();ctx.translate(ox,oy+idle);if(isEnemy)ctx.scale(-1,1);const s=0.9+evo*0.07;
  if(evo>0){{const ar=28+evo*11;const ag=ctx.createRadialGradient(0,0,4,0,0,ar);ag.addColorStop(0,col+'88');ag.addColorStop(1,'transparent');ctx.fillStyle=ag;ctx.beginPath();ctx.arc(0,0,ar,0,6.28);ctx.fill();}}
  ctx.scale(s,s);
  // Use AI-generated visuals if available, otherwise fall back to mode-specific
  const vis = isEnemy ? (CFG.enemy_visual||{{}}) : (CFG.player_visual||{{}});
  if(vis && vis.hair_color){{ drCustom(col,evo,t,vis); }}
  else if(MODE==='FIGHTER')drFighter(col,evo,t,isEnemy);
  else if(MODE==='RPG')drRPG(col,evo,t);
  else if(MODE==='PLATFORM')drPlatform(col,evo);
  else if(MODE==='SHOOTER')drShooter(col,evo);
  else if(MODE==='MAGIC')drMagic(col,evo,t);
  else if(MODE==='COSMIC')drCosmic(col,evo,t);
  else if(MODE==='SPORTS')drSports(col,evo);
  else if(MODE==='BRAWL')drBrawl(col,evo,t);
  else drDefault(col,evo,t);
  if(hit){{ctx.fillStyle='rgba(255,50,50,0.45)';ctx.beginPath();ctx.arc(0,-20,38,0,6.28);ctx.fill();}}
  ctx.restore();
}}
function drCustom(col,evo,t,vis){{
  const hc=vis.hair_color||col;const sc2=vis.skin_color||'#FFCC88';const oc=vis.outfit_color||col;
  const wc=vis.weapon_color||'#C0C0C0';const ec2=vis.eye_color||'#000';const ac=vis.aura_color||col;
  const bb=vis.body_build||'average';const hs=vis.hair_style||'short';const wp=vis.weapon||'fists';
  const bw=bb==='muscular'?1.3:bb==='large'?1.4:bb==='slim'?0.85:bb==='tiny'?0.7:1.0;
  // Legs
  ctx.fillStyle=dk(oc,0.3);ctx.fillRect(-14*bw,10,12*bw,32);ctx.fillRect(2*bw,10,12*bw,32);
  // Boots
  ctx.fillStyle='#333';ctx.fillRect(-16*bw,38,14*bw,10);ctx.fillRect(0,38,14*bw,10);
  // Body
  ctx.fillStyle=oc;ctx.fillRect(-18*bw,-14,36*bw,26);
  // Arms
  ctx.fillStyle=oc;ctx.fillRect(-32*bw,-12,16*bw,24);ctx.fillRect(16*bw,-12,16*bw,24);
  // Hands
  ctx.fillStyle=sc2;ctx.fillRect(-34*bw,8,14*bw,10);ctx.fillRect(20*bw,8,14*bw,10);
  // Head
  ctx.fillStyle=sc2;ctx.beginPath();ctx.ellipse(0,-32,18*bw,20,0,0,6.28);ctx.fill();
  // Eyes
  ctx.fillStyle='#fff';ctx.fillRect(-10*bw,-34,8,7);ctx.fillRect(2*bw,-34,8,7);
  ctx.fillStyle=ec2;ctx.fillRect(-8*bw,-33,4,5);ctx.fillRect(4*bw,-33,4,5);
  // Hair
  ctx.fillStyle=hc;
  if(hs==='spiky'){{for(let i=0;i<5+evo;i++){{const hx=-16+i*(32/(4+evo));ctx.beginPath();ctx.moveTo(hx-5,-48);ctx.lineTo(hx,-(60+evo*4+i%2*8));ctx.lineTo(hx+5,-48);ctx.fill();}}}}
  else if(hs==='long'||hs==='flowing'){{ctx.fillRect(-20,-50,40,14);ctx.fillRect(-22,-48,6,36);ctx.fillRect(16,-48,6,36);}}
  else if(hs==='ponytail'){{ctx.fillRect(-18,-50,36,12);ctx.fillRect(10,-50,6,30);}}
  else if(hs==='mohawk'){{ctx.fillRect(-4,-50,8,14);for(let i=0;i<3;i++){{ctx.beginPath();ctx.moveTo(-4,-50-i*8);ctx.lineTo(0,-62-i*8);ctx.lineTo(4,-50-i*8);ctx.fill();}}}}
  else if(hs==='afro'){{ctx.beginPath();ctx.arc(0,-46,22+evo*2,0,6.28);ctx.fill();}}
  else if(hs==='twin_tails'){{ctx.fillRect(-18,-50,36,12);ctx.fillRect(-24,-48,6,24);ctx.fillRect(18,-48,6,24);}}
  else if(hs==='bald'){{ctx.fillStyle=sc2;ctx.beginPath();ctx.ellipse(0,-42,16,8,0,Math.PI,0);ctx.fill();}}
  else if(hs==='messy'){{ctx.fillRect(-20,-50,40,14);for(let i=0;i<4;i++){{ctx.fillRect(-18+i*10,-54-i%2*6,8,8);}}}}
  else{{ctx.fillRect(-18,-50,36,12);}} // short default
  // Weapon
  if(wp==='sword'){{ctx.fillStyle=wc;ctx.fillRect(22*bw,-6,4,36);ctx.fillStyle='#FFD700';ctx.fillRect(20*bw,-6,8,4);}}
  else if(wp==='dual_sword'){{ctx.fillStyle=wc;ctx.fillRect(-36*bw,-4,3,30);ctx.fillRect(33*bw,-4,3,30);ctx.fillStyle='#FFD700';ctx.fillRect(-38*bw,-4,7,3);ctx.fillRect(31*bw,-4,7,3);}}
  else if(wp==='triple_sword'){{ctx.fillStyle=wc;ctx.fillRect(-36*bw,-4,3,30);ctx.fillRect(33*bw,-4,3,30);ctx.fillRect(-2,-(32+evo*2),3,20);ctx.fillStyle='#FFD700';ctx.fillRect(-38*bw,-4,7,3);ctx.fillRect(31*bw,-4,7,3);ctx.fillRect(-4,-(32+evo*2),7,3);}}
  else if(wp==='gun'){{ctx.fillStyle='#444';ctx.fillRect(20*bw,2,28,6);ctx.fillStyle='#222';ctx.fillRect(42*bw,-2,8,14);}}
  else if(wp==='staff'||wp==='wand'){{ctx.fillStyle='#8B4513';ctx.fillRect(22*bw,-20,4,44);ctx.fillStyle=ac;ctx.beginPath();ctx.arc(24*bw,-22,6+evo,0,6.28);ctx.fill();}}
  else if(wp==='bow'){{ctx.strokeStyle=wc;ctx.lineWidth=3;ctx.beginPath();ctx.arc(28*bw,-4,20,Math.PI*0.7,Math.PI*1.3);ctx.stroke();ctx.strokeStyle='#FFD700';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(28*bw,-22);ctx.lineTo(28*bw,14);ctx.stroke();}}
  else if(wp==='scythe'){{ctx.fillStyle='#444';ctx.fillRect(18*bw,-16,4,40);ctx.fillStyle=wc;ctx.beginPath();ctx.moveTo(18*bw,-16);ctx.quadraticCurveTo(40*bw,-30,32*bw,-4);ctx.lineTo(18*bw,-10);ctx.fill();}}
  else if(wp==='ball'){{ctx.fillStyle='#FF6600';ctx.beginPath();ctx.arc(30*bw,12,8,0,6.28);ctx.fill();ctx.strokeStyle='#000';ctx.lineWidth=1.5;ctx.stroke();}}
  // Cape
  if(vis.cape){{ctx.fillStyle=(vis.cape_color||ac)+'88';ctx.beginPath();ctx.moveTo(-16*bw,-10);ctx.lineTo(-20*bw,30);ctx.lineTo(20*bw,30);ctx.lineTo(16*bw,-10);ctx.fill();}}
  // Evolution aura enhancement
  if(evo>=2){{ctx.fillStyle=ac+'44';ctx.beginPath();ctx.arc(0,-10,30+evo*5,0,6.28);ctx.fill();}}
  if(evo>=4){{ctx.strokeStyle=ac;ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,-10,35+evo*5,0,6.28);ctx.stroke();}}
}}
function drFighter(col,evo,t,isEnemy){{
  const hc=evo>=1?'#FFD700':col;
  ctx.fillStyle=col;ctx.fillRect(-16,10,14,36);ctx.fillRect(2,10,14,36);
  ctx.fillStyle='#333';ctx.fillRect(-18,38,16,10);ctx.fillRect(0,38,16,10);
  ctx.fillStyle=col;ctx.fillRect(-20,-15,40,28);ctx.fillStyle='#222';ctx.fillRect(-20,10,40,6);
  ctx.fillStyle=col;ctx.fillRect(-36,-12,18,24);ctx.fillRect(18,-12,18,24);
  ctx.fillStyle='#fff3';ctx.fillRect(-38,8,18,12);ctx.fillRect(20,8,18,12);
  ctx.fillStyle=col;ctx.fillRect(-8,-22,16,10);ctx.fillRect(-22,-50,44,32);
  ctx.fillStyle=evo>=2?'#00FFFF':'#fff';ctx.fillRect(-14,-38,10,8);ctx.fillRect(4,-38,10,8);
  ctx.fillStyle='#000';ctx.fillRect(-10,-36,4,5);ctx.fillRect(7,-36,4,5);
  ctx.fillStyle=hc;const sp=3+Math.min(evo,5);
  for(let i=0;i<sp;i++){{const sx=-18+i*(36/(sp-1)),sh=14+i%2*8+evo*4;ctx.beginPath();ctx.moveTo(sx-6,-50);ctx.lineTo(sx,-(50+sh));ctx.lineTo(sx+6,-50);ctx.fill();}}
  if(evo>=3){{ctx.fillStyle=hc+'44';ctx.beginPath();ctx.arc(0,-50,14+evo*3,0,6.28);ctx.fill();}}
}}
function drRPG(col,evo,t){{
  const r=22+evo*3;const bg2=ctx.createRadialGradient(-r*0.3,-r*0.3,2,0,0,r);bg2.addColorStop(0,lh(col,0.4));bg2.addColorStop(1,col);ctx.fillStyle=bg2;ctx.beginPath();ctx.ellipse(0,0,r,r*0.85,0,0,6.28);ctx.fill();
  const ec=evo>=2?'#FFD700':'#000';[[- r*.3,-r*.2,r*.25,r*.22],[r*.3,-r*.2,r*.25,r*.22]].forEach(([ex,ey,erx,ery])=>{{ctx.fillStyle='#fff';ctx.beginPath();ctx.ellipse(ex,ey,erx,ery,0,0,6.28);ctx.fill();ctx.fillStyle=ec;ctx.beginPath();ctx.ellipse(ex,ey,erx*0.55,ery*0.55,0,0,6.28);ctx.fill();}});
  ctx.fillStyle='rgba(255,255,255,0.4)';ctx.beginPath();ctx.ellipse(-r*0.25,-r*0.35,r*0.18,r*0.12,Math.PI/4,0,6.28);ctx.fill();
  ctx.fillStyle=col;ctx.beginPath();ctx.ellipse(-r*0.9,-r*0.5,r*0.15,r*0.28,-0.3,0,6.28);ctx.fill();ctx.beginPath();ctx.ellipse(r*0.9,-r*0.5,r*0.15,r*0.28,0.3,0,6.28);ctx.fill();
  if(evo>=2){{ctx.fillStyle=lh(col,0.3)+'88';ctx.beginPath();ctx.moveTo(-r*.8,0);ctx.quadraticCurveTo(-r*1.8,-r*.8,-r*.3,-r*.1);ctx.fill();ctx.beginPath();ctx.moveTo(r*.8,0);ctx.quadraticCurveTo(r*1.8,-r*.8,r*.3,-r*.1);ctx.fill();}}
  if(evo>=5){{ctx.fillStyle='#FFD700';for(let i=0;i<5;i++){{ctx.fillRect(-r*.8+i*r*.4,-r-10+(i%2)*8,r*.18,r*.35);}}ctx.fillRect(-r*.9,-r,r*1.8,8);}}
}}
function drPlatform(col,evo){{
  ctx.fillStyle='#2244CC';ctx.fillRect(-14,0,28,26);ctx.fillRect(-8,-4,16,6);
  ctx.fillStyle=col;ctx.fillRect(-18,-14,36,20);ctx.fillRect(-14,-4,28,10);
  ctx.fillStyle=col;ctx.fillRect(-30,-14,14,18);ctx.fillRect(16,-14,14,18);
  ctx.fillStyle='#FFCC88';ctx.fillRect(-30,2,14,10);ctx.fillRect(16,2,14,10);
  ctx.fillStyle='#2244CC';ctx.fillRect(-14,24,12,16);ctx.fillRect(2,24,12,16);
  ctx.fillStyle='#884400';ctx.fillRect(-16,38,16,10);ctx.fillRect(0,38,16,10);
  ctx.fillStyle='#FFCC88';ctx.fillRect(-18,-42,36,30);
  ctx.fillStyle=col;ctx.fillRect(-20,-52,40,14);ctx.fillRect(-14,-60,32,10);
  ctx.fillStyle='#000';ctx.fillRect(-20,-42,6,6);ctx.fillRect(-10,-32,7,6);ctx.fillRect(3,-32,7,6);
  if(evo>=1){{ctx.fillStyle='#FFD700';ctx.beginPath();ctx.arc(0,-62,6,0,6.28);ctx.fill();}}
}}
function drShooter(col,evo){{
  ctx.fillStyle='#334422';ctx.fillRect(-14,2,28,32);ctx.fillRect(-18,-12,36,16);
  ctx.fillStyle='#334422';ctx.fillRect(-24,-10,8,20);ctx.fillRect(16,-10,8,20);
  ctx.fillStyle='#333';ctx.fillRect(-12,32,10,16);ctx.fillRect(2,32,10,16);ctx.fillRect(-14,46,14,8);ctx.fillRect(0,46,14,8);
  ctx.fillStyle='#222';ctx.fillRect(-18,-38,36,28);ctx.fillStyle='#00FF4444';ctx.fillRect(-14,-28,28,12);ctx.fillStyle='#00FF44';ctx.fillRect(-14,-28,28,3);
  ctx.fillStyle='#111';ctx.fillRect(16,0,30,8);ctx.fillStyle='#333';ctx.fillRect(38,-4,8,16);
  if(evo>=2){{ctx.fillStyle=col+'AA';ctx.fillRect(44,-2,14,12);}}
  if(evo>=1){{ctx.fillStyle='#FFD700';ctx.fillRect(-18,-14,6,4);}}
}}
function drMagic(col,evo,t){{
  ctx.fillStyle=col+'CC';ctx.beginPath();ctx.moveTo(-22,42);ctx.lineTo(-18,-10);ctx.lineTo(18,-10);ctx.lineTo(22,42);ctx.closePath();ctx.fill();
  ctx.fillStyle='#8B4513';ctx.fillRect(-18,10,36,6);
  ctx.fillStyle=col+'AA';ctx.fillRect(-34,-8,18,22);ctx.fillRect(16,-8,18,22);
  ctx.fillStyle='#FFCC88';ctx.fillRect(-36,12,16,10);ctx.fillRect(20,12,16,10);ctx.fillRect(-16,-36,32,28);
  ctx.fillStyle='#000';ctx.fillRect(-10,-28,7,6);ctx.fillRect(3,-28,7,6);
  ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(-22,-36);ctx.lineTo(0,-(78+evo*6));ctx.lineTo(22,-36);ctx.closePath();ctx.fill();
  ctx.fillStyle=col+'88';ctx.fillRect(-24,-40,48,6);
  ctx.fillStyle='#FFD700';ctx.font='10px Arial';for(let i=0;i<Math.min(evo+1,5);i++)ctx.fillText('✦',-8+i*4,-(56+i*6));
  if(evo>=1){{ctx.fillStyle=lh(col,0.4)+'CC';ctx.beginPath();ctx.arc(-36,14,8+evo*2,0,6.28);ctx.fill();}}
}}
function drCosmic(col,evo,t){{
  const r=22+evo*3;const hg=ctx.createLinearGradient(-r,-r/2,r,r/2);hg.addColorStop(0,lh(col,0.3));hg.addColorStop(1,col);ctx.fillStyle=hg;
  ctx.beginPath();ctx.moveTo(-r,8);ctx.quadraticCurveTo(-r,-r/2,0,-r);ctx.quadraticCurveTo(r,-r/2,r,8);ctx.quadraticCurveTo(0,r*1.1,-r,8);ctx.fill();
  ctx.fillStyle='rgba(0,200,255,0.3)';ctx.beginPath();ctx.ellipse(0,-r/2,r*0.5,r*0.4,0,0,6.28);ctx.fill();ctx.strokeStyle='rgba(0,200,255,0.6)';ctx.lineWidth=2;ctx.stroke();
  ctx.fillStyle=col+'AA';ctx.fillRect(-r*1.5,-4,r,8);ctx.fillRect(r*0.5,-4,r,8);
  for(let i=0;i<3;i++){{const ex=-r*0.6+i*r*0.6,ey=r*0.6;const eg=ctx.createRadialGradient(ex,ey,0,ex,ey,8+evo*3);eg.addColorStop(0,col+'FF');eg.addColorStop(1,'transparent');ctx.fillStyle=eg;ctx.beginPath();ctx.arc(ex,ey,8+evo*3,0,6.28);ctx.fill();}}
}}
function drSports(col,evo){{
  ctx.fillStyle=col;ctx.fillRect(-18,-14,36,24);ctx.fillRect(-8,-22,16,10);
  ctx.fillStyle=col;ctx.fillRect(-22,-14,6,20);ctx.fillRect(16,-14,6,20);
  ctx.fillStyle='#FFCC88';ctx.fillRect(-22,4,6,12);ctx.fillRect(16,4,6,12);
  ctx.fillStyle=lh(col,0.2);ctx.fillRect(-14,10,28,22);ctx.fillRect(-8,30,10,18);ctx.fillRect(4,30,10,18);
  ctx.fillStyle='#333';ctx.fillRect(-10,46,10,8);ctx.fillRect(2,46,10,8);
  ctx.fillStyle='#FFCC88';ctx.beginPath();ctx.ellipse(0,-30,14,18,0,0,6.28);ctx.fill();
  ctx.fillStyle='#000';ctx.fillRect(-6,-32,5,5);ctx.fillRect(1,-32,5,5);
  if(evo>=1){{ctx.fillStyle='#FFD700';ctx.font='bold 14px Arial';ctx.textAlign='center';ctx.fillText(evo+'★',0,-54);ctx.textAlign='left';}}
}}
function drBrawl(col,evo,t){{
  ctx.fillStyle=col;ctx.fillRect(-20,-10,40,30);ctx.fillRect(-16,-24,32,16);
  ctx.fillStyle=lh(col,0.2);ctx.beginPath();ctx.ellipse(0,-34,18,20,0,0,6.28);ctx.fill();
  ctx.fillStyle='#000';ctx.fillRect(-8,-36,6,6);ctx.fillRect(2,-36,6,6);
  ctx.fillStyle=col;ctx.fillRect(-38,-12,20,22);ctx.fillRect(18,-12,20,22);
  ctx.fillStyle='#fff3';ctx.fillRect(-38,6,20,10);ctx.fillRect(18,6,20,10);
  ctx.fillStyle=col;ctx.fillRect(-14,18,12,28);ctx.fillRect(2,18,12,28);
  ctx.fillStyle='#333';ctx.fillRect(-16,44,14,10);ctx.fillRect(2,44,14,10);
  if(evo>=2){{ctx.strokeStyle='#FFD700';ctx.lineWidth=2;ctx.strokeRect(-22,-12,44,42);}}
}}
function drDefault(col,evo,t){{
  const s=0.9+evo*0.04;
  ctx.fillStyle=dk(col,0.3);ctx.fillRect(-16*s,8*s,13*s,34*s);ctx.fillRect(3*s,8*s,13*s,34*s);
  ctx.fillStyle=col;ctx.fillRect(-20*s,-14*s,40*s,24*s);
  ctx.fillStyle=col;ctx.fillRect(-34*s,-12*s,16*s,26*s);ctx.fillRect(18*s,-12*s,16*s,26*s);
  ctx.fillStyle=lh(col,0.3);ctx.fillRect(-36*s,10*s,14*s,10*s);ctx.fillRect(22*s,10*s,14*s,10*s);
  ctx.fillStyle=lh(col,0.2);ctx.beginPath();ctx.ellipse(0,-32*s,20*s,22*s,0,0,6.28);ctx.fill();
  const ec=evo>=3?'#FF4400':evo>=1?'#00FFFF':'#333';
  [[-8,-32,6,6],[8,-32,6,6]].forEach(([ex,ey,r1,r2])=>{{ctx.fillStyle='rgba(255,255,255,0.9)';ctx.beginPath();ctx.ellipse(ex*s,ey*s,r1*s,r2*s,0,0,6.28);ctx.fill();ctx.fillStyle=ec;ctx.beginPath();ctx.ellipse(ex*s,ey*s,r1*s*0.5,r2*s*0.5,0,0,6.28);ctx.fill();}});
  if(evo>=5){{ctx.strokeStyle='#FFD700';ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(0,-58*s,22*s,8*s,0,0,6.28);ctx.stroke();}}
}}
function drHUD(){{
  const php=Math.max(0,P.hp/P.maxHp);const phc=php>0.5?'#00FF44':php>0.25?'#FF8800':'#FF2222';
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(12,12,200,18);ctx.fillStyle=phc;ctx.fillRect(12,12,200*php,18);
  ctx.strokeStyle='#fff4';ctx.lineWidth=1;ctx.strokeRect(12,12,200,18);
  ctx.fillStyle='#fff';ctx.font='bold 10px "Space Mono",monospace';ctx.fillText('HP '+Math.ceil(P.hp)+'/'+P.maxHp,16,25);
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(12,34,200,10);ctx.fillStyle=COL;ctx.fillRect(12,34,200*(P.power/100),10);
  ctx.strokeStyle='#fff2';ctx.strokeRect(12,34,200,10);
  const evos=CFG.evolutions||[];const en=evos[P.evo]||('Lv '+(P.evo+1));
  ctx.fillStyle=COL;ctx.font='bold 9px Orbitron,monospace';ctx.fillText('⚡ '+en.toUpperCase(),12,58);
  const ehp=Math.max(0,E.hp/E.maxHp);const ehc=ehp>0.5?'#FF4444':ehp>0.25?'#FF8800':'#FF0000';
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(W-212,12,200,18);ctx.fillStyle=ehc;ctx.fillRect(W-212,12,200*ehp,18);
  ctx.strokeStyle='#fff4';ctx.strokeRect(W-212,12,200,18);
  ctx.fillStyle='#fff';ctx.font='bold 10px "Space Mono",monospace';ctx.fillText((CFG.enemy_name||'Enemy').substring(0,18),W-208,25);
  const ep=CFG.enemy_phases?CFG.enemy_phases[E.phase]||'':'';ctx.fillStyle=E.color;ctx.font='8px "Space Mono",monospace';ctx.fillText(ep,W-208,36);
  ctx.font='16px Arial';for(let i=0;i<3;i++)ctx.fillText(i<lives?'❤️':'🖤',12+i*22,H-16);
  ctx.fillStyle='rgba(255,255,255,0.3)';ctx.font='9px "Space Mono",monospace';ctx.textAlign='center';ctx.fillText((CFG.arena_name||'').toUpperCase(),W/2,H-8);ctx.textAlign='left';
  if(P.streak>=2){{ctx.fillStyle='#FFD700';ctx.font='bold 11px Orbitron,monospace';ctx.textAlign='center';ctx.fillText('🔥 '+P.streak+' STREAK',W/2,18);ctx.textAlign='left';}}
}}
function showQ(){{
  if(qI>=questions.length){{win();return;}}
  const q=questions[qI];const d=document.getElementById('questions');d.style.display='block';
  qTimer=qMax;aLocked=false;
  d.innerHTML=`<div class="qbox"><div class="qhdr"><span class="qlbl">Q${{qI+1}}/${{questions.length}} · ${{subject}}</span><span style="font-size:13px">${{'❤️'.repeat(lives)+'🖤'.repeat(3-lives)}}</span></div><div class="tbar" id="tb"></div><div class="qtxt">${{q.q}}</div><div class="choices">${{q.choices.map((c2,i)=>`<button class="ch" onclick="ans(${{i}},'${{String.fromCharCode(65+i)}}')">${{c2}}</button>`).join('')}}</div></div>`;
}}
function ans(idx,letter){{
  if(aLocked)return;aLocked=true;const q=questions[qI];const ok=(letter===q.answer);
  document.querySelectorAll('.ch')[idx].classList.add(ok?'ok':'no');
  if(!ok){{const ci=['A','B','C','D'].indexOf(q.answer);if(ci>=0)document.querySelectorAll('.ch')[ci].classList.add('ok');}}
  setTimeout(()=>{{document.getElementById('questions').style.display='none';ok?onOk():onNo();qI++;if(STATE==='B')setTimeout(()=>{{if(STATE==='B')showQ();}},1100);}},650);
}}
function onOk(){{
  P.streak++;P.total++;P.power=Math.min(100,P.power+22);
  const dmg=15+P.evo*5+Math.floor(Math.random()*10)+(P.streak>=3?15:0);
  E.hp=Math.max(0,E.hp-dmg);E.hit=true;E.shake=12;setTimeout(()=>E.hit=false,380);
  ab(P.x,P.y-30,E.x,E.y-30,COL,6+P.evo*2,24);ap(E.x,E.y-30,COL,20+P.evo*4,4,6,28);ap(E.x,E.y-30,'#FFD700',8,3,4,18);
  dn(E.x,E.y-60,'-'+dmg,COL,true);
  const nt=P.evo+1;const evos=CFG.evolutions||[];
  if(nt<evos.length&&P.total>0&&P.total%3===0&&Math.floor(P.total/3)===nt){{evolve(nt);}}
  if(E.hp/E.maxHp<0.33&&E.phase===0){{E.phase=1;ap(E.x,E.y,E.color,40,6,8,50);dn(E.x,E.y-80,(CFG.enemy_phases||['Phase 2'])[1]||'ENRAGED',E.color,true);}}
  else if(E.hp/E.maxHp<0.1&&E.phase===1){{E.phase=2;ap(E.x,E.y,E.color,60,8,10,60);dn(E.x,E.y-80,(CFG.enemy_phases||['','','FINAL'])[2]||'FINAL',E.color,true);}}
  if(E.hp<=0)setTimeout(win,700);
}}
function onNo(){{
  P.streak=0;wrongs++;
  const dmg=10+E.phase*8+Math.floor(Math.random()*8);
  P.hp=Math.max(0,P.hp-dmg);P.hit=true;P.shake=14;setTimeout(()=>P.hit=false,380);
  if(wrongs>=3){{lives--;wrongs=0;}}
  ab(E.x,E.y-30,P.x,P.y-30,E.color,5,20);ap(P.x,P.y-30,'#FF2222',15,3,5,26);dn(P.x,P.y-60,'-'+dmg,'#FF2222',false);
  if(lives<=0)setTimeout(lose,700);
}}
function evolve(idx){{
  STATE='EV';evolveT=0;P.evo=idx;ap(P.x,P.y,COL,60,8,10,60);ap(P.x,P.y,'#FFD700',30,6,7,48);
  setTimeout(()=>{{STATE='B';showQ();}},1800);
}}
function win(){{
  STATE='WIN';document.getElementById('questions').style.display='none';
  for(let i=0;i<8;i++)setTimeout(()=>ap(Math.random()*W,Math.random()*H,COL,20,5,8,50),i*100);
  const xp=50+P.evo*20+P.total*10,gold=20+P.evo*8+P.total*4;
  const res=document.getElementById('result');res.style.display='flex';
  res.innerHTML=`<div style="font-size:50px;margin-bottom:10px">🏆</div><div style="font-family:Orbitron,monospace;font-size:34px;color:${{COL}};letter-spacing:4px;margin-bottom:6px">VICTORY!</div><div style="color:#FFD700;font-family:'Space Mono',monospace;font-size:13px;margin-bottom:8px">${{CFG.win_quote||'You prevailed!'}}</div><div style="color:#fff;font-size:12px;margin:14px 0;line-height:2.2">⚡ <b style="color:${{COL}}">+${{xp}} XP</b> &nbsp; 💰 <b style="color:#FFD700">+${{gold}} Shards</b> &nbsp; 🎁 <b style="color:#AA44FF">BATTLE BOX!</b><br>Form: <b style="color:${{COL}}">${{(CFG.evolutions||[])[P.evo]||'Level '+(P.evo+1)}}</b></div><div style="font-size:10px;color:rgba(255,255,255,0.4);font-family:'Space Mono',monospace">Return to app to claim →</div>`;
  window.parent.postMessage({{type:'battleWin',xp,gold,evolution:P.evo,correct:P.total}},'*');
}}
function lose(){{
  STATE='LOSE';document.getElementById('questions').style.display='none';
  ap(P.x,P.y,'#FF2222',50,6,8,60);
  const res=document.getElementById('result');res.style.display='flex';
  res.innerHTML=`<div style="font-size:50px;margin-bottom:10px">💀</div><div style="font-family:Orbitron,monospace;font-size:34px;color:#FF2222;letter-spacing:4px;margin-bottom:6px">DEFEATED</div><div style="color:#FF8888;font-family:'Space Mono',monospace;font-size:13px;margin-bottom:10px">${{CFG.lose_quote||'Train harder.'}}</div><div style="color:rgba(255,255,255,0.5);font-size:11px">Study more, grow stronger.</div>`;
  window.parent.postMessage({{type:'battleLose'}},'*');
}}
function go(sub){{
  subject=sub;document.getElementById('ss').style.display='none';
  const allQ=CFG.questions||[];questions=allQ.slice().sort(()=>Math.random()-0.5).slice(0,Math.min(10,allQ.length));
  if(!questions.length)questions=[{{q:'What is 2+2?',choices:['A: 3','B: 4','C: 5','D: 6'],answer:'B',hint:'math'}}];
  STATE='IN';stT=0;setTimeout(()=>{{STATE='B';showQ();}},2800);
}}
function drIntro(){{
  const pct=Math.min(1,stT/55);ctx.globalAlpha=pct;
  ctx.fillStyle='rgba(0,0,0,0.72)';ctx.fillRect(0,H/2-68,W,136);
  ctx.fillStyle=COL;ctx.font='bold 30px Orbitron,monospace';ctx.textAlign='center';ctx.fillText(CFG.arena_name||'BATTLE START',W/2,H/2-18);
  ctx.fillStyle='#fff8';ctx.font='12px "Space Mono",monospace';ctx.fillText((CFG.arena_desc||'').substring(0,65),W/2,H/2+10);
  ctx.fillStyle=E.color;ctx.font='13px "Space Mono",monospace';ctx.fillText('ENEMY: '+(CFG.enemy_name||'?').toUpperCase(),W/2,H/2+38);
  ctx.textAlign='left';ctx.globalAlpha=1;
}}
function drEvolve(){{
  const pct=evolveT/88;const en=(CFG.evolutions||[])[P.evo]||'EVOLVED';
  ctx.globalAlpha=Math.sin(pct*Math.PI)*0.82;ctx.fillStyle=COL;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;
  ctx.font='bold 40px Orbitron,monospace';ctx.textAlign='center';
  ctx.fillStyle='#000';ctx.fillText(en.toUpperCase(),W/2+2,H/2+2);ctx.fillStyle='#FFD700';ctx.fillText(en.toUpperCase(),W/2,H/2);
  ctx.fillStyle='#fff';ctx.font='13px "Space Mono",monospace';ctx.fillText('FORM UNLOCKED!',W/2,H/2+34);ctx.textAlign='left';
}}
function upTimer(){{
  const tb=document.getElementById('tb');if(!tb)return;
  qTimer-=1/60;
  if(qTimer<=0&&!aLocked){{onNo();aLocked=true;document.getElementById('questions').style.display='none';qI++;if(STATE!=='WIN'&&STATE!=='LOSE')setTimeout(()=>{{if(STATE==='B')showQ();}},1100);}}
  else{{const pct=Math.max(0,qTimer/qMax)*100;tb.style.width=pct+'%';tb.style.background=pct>40?'linear-gradient(90deg,'+COL+','+COL+'88)':'linear-gradient(90deg,#FF2222,#FF4400)';}}
}}
function loop(){{
  FC++;ctx.clearRect(0,0,W,H);drBG();
  if(STATE!=='SS'){{drChar(P.x,P.y,P.color,P.evo,false,P.hit,P.shake);drChar(E.x,E.y,E.color,E.phase*2,true,E.hit,E.shake);drParts();drHUD();drDmgNums();if(P.shake>0)P.shake=Math.max(0,P.shake-0.5);if(E.shake>0)E.shake=Math.max(0,E.shake-0.5);}}
  if(STATE==='IN'){{stT++;drIntro();}}
  else if(STATE==='B')upTimer();
  else if(STATE==='EV'){{evolveT++;drEvolve();}}
  upParts();requestAnimationFrame(loop);
}}
loop();
</script></body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL GAME ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def detect_game_mode(universe: str) -> str:
    l = universe.lower()
    if any(k in l for k in ['dragon ball','dbz','saiyan','naruto','bleach','demon slayer','one piece','attack on titan','jujutsu','fairy tail','hunter x hunter','fullmetal','my hero','chainsaw man','black clover','sword art','tokyo ghoul','berserk','vinland','mob psycho','one punch','seven deadly','fire force','dragon ball z','dbs']):
        return 'FIGHTER'
    if any(k in l for k in ['pokemon','genshin','zelda','final fantasy','fire emblem','undertale','persona','elden ring','dark souls','skyrim','witcher','stardew','animal crossing','xenoblade','tales of','dragon quest','chrono','octopath','ff7','ff14','wow','world of warcraft','runescape','league of','dota','diablo','baldur','pathfinder','dungeons and dragons','d&d']):
        return 'RPG'
    if any(k in l for k in ['mario','sonic','kirby','donkey kong','crash bandicoot','rayman','celeste','hollow knight','cuphead','megaman','castlevania','metroid','contra','spyro','banjo','yoshi','pikmin','super mario','little big planet','shovel knight']):
        return 'PLATFORM'
    if any(k in l for k in ['call of duty','cod','halo','fortnite','valorant','overwatch','apex','pubg','counter strike','battlefield','doom','quake','borderlands','destiny','titanfall','warzone','rainbow six','ghost recon','splinter cell','metal gear','resident evil','bioshock','far cry','crysis','killzone']):
        return 'SHOOTER'
    if any(k in l for k in ['harry potter','hogwarts','wizard','witchcraft','lord of the rings','tolkien','dungeons','magic the gathering','hearthstone','fantasy','narnia','eragon','inheritance','mage','sorcerer','enchanted','merlin','fable','wheel of time','mistborn','stormlight','sanderson']):
        return 'MAGIC'
    if any(k in l for k in ['star wars','nasa','astronaut','space','galaxy','cosmos','marvel','avengers','dc comics','superman','batman','guardians','thor','iron man','captain america','black panther','spider man','x-men','transformers','gundam','evangelion','macross','star trek','mass effect','halo universe','interstellar']):
        return 'COSMIC'
    if any(k in l for k in ['football','basketball','soccer','baseball','tennis','golf','nba','nfl','mlb','nhl','fifa','cricket','rugby','boxing','mma','ufc','wrestling','olympics','lacrosse','volleyball','swimming','track','esport','formula 1','f1','nascar','racing']):
        return 'SPORTS'
    if any(k in l for k in ['mortal kombat','street fighter','tekken','smash bros','king of fighters','guilty gear','blazblue','injustice','fighting game','brawl']):
        return 'BRAWL'
    if any(k in l for k in ['minecraft','roblox','terraria','starcraft','civilization','age of empires','sim','tycoon','factory','build','craft','sandbox','cities','prison architect','factorio']):
        return 'BUILDER'
    if any(k in l for k in ['music','band','rock','hip hop','rap','jazz','classical','kpop','pop','artist','singer','beethoven','mozart','album']):
        return 'COSMIC'
    if any(k in l for k in ['cooking','chef','food','recipe','kitchen','baking','culinary','masterchef','anime food']):
        return 'RPG'
    if any(k in l for k in ['history','ancient','rome','egypt','medieval','war','world war','napoleon','viking','samurai','pirate','renaissance','greek mythology']):
        return 'BRAWL'
    if any(k in l for k in ['science','biology','chemistry','physics','math','coding','programming','engineering','medicine','robot','ai','machine learning']):
        return 'COSMIC'
    return 'AUTO'

def _fallback_config(universe: str, mode: str, subject: str, q_count: int) -> dict:
    questions = [
        {"q":f"In the {universe} world: What is 15 × 8?","choices":["A: 100","B: 112","C: 120","D: 130"],"answer":"C","hint":"15×8"},
        {"q":"A hero runs 5km in 25 min. Speed in km/h?","choices":["A: 10","B: 12","C: 15","D: 8"],"answer":"B","hint":"d/t×60"},
        {"q":"What is the square root of 144?","choices":["A: 11","B: 12","C: 13","D: 14"],"answer":"B","hint":"12×12"},
        {"q":"Solve: 3x + 6 = 21. What is x?","choices":["A: 3","B: 4","C: 5","D: 6"],"answer":"C","hint":"subtract 6, divide by 3"},
        {"q":"What is 20% of 350?","choices":["A: 60","B: 70","C: 80","D: 90"],"answer":"B","hint":"350÷5"},
        {"q":"What is 7² + 5²?","choices":["A: 74","B: 70","C: 84","D: 64"],"answer":"A","hint":"49+25"},
        {"q":"A triangle has angles 90° and 45°. Third angle?","choices":["A: 30°","B: 45°","C: 60°","D: 55°"],"answer":"B","hint":"sum=180"},
        {"q":"What is 2³ × 3²?","choices":["A: 48","B: 54","C: 64","D: 72"],"answer":"D","hint":"8×9"},
    ]
    return {"mode": mode,"arena_name": f"The {universe} Arena","arena_desc": "A legendary battlefield forged from pure determination.","arena_colors": ["#111122","#222244","#333366"],"player_title": "Champion","player_attacks": ["Power Blast","Energy Wave","Ultimate Strike","Final Form Attack","Infinite Force"],"enemy_name": f"{universe} Boss","enemy_title": "The Final Obstacle","enemy_color": "#CC2222","enemy_attacks": ["Dark Blast","Shadow Strike","Void Wave"],"enemy_phases": ["Phase 1","Phase 2 — ENRAGED","Final Phase — ULTIMATE"],"win_quote": "Victory belongs to those who never stop learning!","lose_quote": "The enemy grows stronger. Study more and return.","questions": questions[:q_count]}

def generate_battle_config(universe: str, subject: str, tier: str, client, difficulty: int = 1) -> dict:
    mode = detect_game_mode(universe)
    tier_q = 8 if tier == "Elite" else (6 if tier == "Premium" else 4)
    q_count = min(tier_q + difficulty, 12)
    evolutions_by_mode = {
        "FIGHTER": ["Base Form","Awakened","Powered Up","Super Form","Hyper Mode","Transcendent","Legendary","Absolute","INFINITE POWER"],
        "RPG":     ["Novice","Apprentice","Adept","Expert","Master","Grand Master","Champion","Legend","MYTHIC"],
        "PLATFORM":["Small","Powered","Fire Mode","Cape Mode","Tanooki","Metal","Wing Cap","Rainbow Star","INVINCIBLE"],
        "SHOOTER": ["Recruit","Soldier","Specialist","Veteran","Elite","Special Ops","Ghost","Shadow","OMEGA OPERATIVE"],
        "MAGIC":   ["Apprentice","Witch/Wizard","Prefect","Auror","Master Wizard","Archmage","High Mage","Grand Archmage","OMNIMANCER"],
        "COSMIC":  ["Cadet","Pilot","Ace","Captain","Commander","Admiral","Warlord","Cosmic Force","UNIVERSAL"],
        "SPORTS":  ["Rookie","Starter","Varsity","All-Star","MVP","Hall of Fame","Legend","GOAT","UNDISPUTED"],
        "BRAWL":   ["White Belt","Yellow","Orange","Green","Blue","Purple","Brown","Black Belt","GRANDMASTER"],
        "BUILDER": ["Novice","Builder","Engineer","Architect","Master Builder","City Planner","Overlord","God Mode","OMNIPOTENT"],
        "AUTO":    ["Level 1","Level 2","Level 3","Level 4","Level 5","Level 6","Level 7","Level 8","MAXED"],
    }
    # Get character visuals from world data if available
    player_vis = {}
    enemy_vis = {}
    try:
        wd_stored = st.session_state.get("world_data", {})
        player_vis = wd_stored.get("player_visual", {})
        enemy_vis = wd_stored.get("enemy_visual", {})
    except:
        pass

    prompt = f"""You are a game designer for an educational RPG called "30 Second Infiniteverse".
Universe: "{universe}"
Game Mode: {mode}
Subject: {subject}
Player tier: {tier}

Return ONLY valid JSON (no markdown) with this EXACT structure:
{{"mode":"{mode}","arena_name":"short dramatic name","arena_desc":"1 sentence","arena_colors":["#hex1","#hex2","#hex3"],"player_title":"title","player_attacks":["A1","A2","A3","A4","A5"],"enemy_name":"universe-specific enemy name","enemy_title":"enemy rank","enemy_color":"#hex","enemy_attacks":["E1","E2","E3"],"enemy_phases":["P1","P2","P3"],"win_quote":"short quote","lose_quote":"short quote","player_visual":{{"hair_color":"#hex","hair_style":"spiky/long/short/bald/mohawk/ponytail/flowing/messy","skin_color":"#hex","outfit_color":"#hex","weapon":"sword/dual_sword/triple_sword/gun/staff/fists/bow/scythe/wand/ball/none","weapon_color":"#hex","eye_color":"#hex","cape":false,"aura_color":"#hex","body_build":"slim/average/muscular/large"}},"enemy_visual":{{"hair_color":"#hex","hair_style":"...","skin_color":"#hex","outfit_color":"#hex","weapon":"...","weapon_color":"#hex","eye_color":"#hex","cape":false,"aura_color":"#hex","body_build":"..."}},"questions":[{{"q":"question","choices":["A: opt","B: opt","C: opt","D: opt"],"answer":"B","hint":"tiny hint"}}]}}

CRITICAL for visuals: The player_visual should look like the PROTAGONIST or main character of this universe. The enemy should look like a VILLAIN or BOSS. Use the EXACT iconic colors and weapons. For Zoro: green hair, triple_sword, muscular. For Naruto: yellow hair, fists, orange outfit. For Mario: red outfit, short hair, average build. Be SPECIFIC.

Generate {q_count} questions. Each must:
- Test real {subject} knowledge
- Be flavored with {universe} lore in the question text
- Have 4 choices labeled A, B, C, D
- Have correct "answer" field matching one of A B C D"""
    try:
        resp = client.messages.create(model="claude-sonnet-4-5",max_tokens=2400 if tier == "Elite" else 1800,messages=[{"role":"user","content":prompt}])
        raw = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
        cfg = json.loads(raw)
    except Exception:
        cfg = _fallback_config(universe, mode, subject, q_count)
    max_evo = 9 if tier == "Elite" else (6 if tier == "Premium" else 3)
    all_evos = evolutions_by_mode.get(mode, evolutions_by_mode["AUTO"])
    cfg["evolutions"] = all_evos[:max_evo]
    cfg["subject"] = subject; cfg["universe"] = universe; cfg["tier"] = tier; cfg["mode"] = mode
    return cfg

# ─────────────────────────────────────────────────────────────────────────────
# ADDICTION PSYCHOLOGY — REWARD SYSTEMS (UPGRADED v10)
# ─────────────────────────────────────────────────────────────────────────────
def variable_reward(base: float) -> tuple:
    """Slot-machine style reward with near-miss psychology."""
    roll = random.random()
    if roll < 0.04:
        mult = random.randint(8, 20)
        return base * mult, "💥 JACKPOT", f"{mult}× MULTIPLIER — THE UNIVERSE REWARDS YOU", None
    elif roll < 0.12:
        mult = random.randint(4, 7)
        return base * mult, "🌟 EPIC REWARD", f"{mult}× — An extraordinary surge of power!", None
    elif roll < 0.28:
        mult = random.randint(2, 3)
        near_miss = "So close to EPIC! 🌟 One tier away..." if random.random() < 0.5 else None
        return base * mult, "⚡ GREAT PULL", f"{mult}× — You felt it in your soul.", near_miss
    elif roll < 0.55:
        near_miss = "Almost hit GREAT tier! ⚡ The next one could be huge..." if random.random() < 0.4 else None
        return base * 1, "✅ SOLID", "Standard reward. The grind continues.", near_miss
    else:
        mult = round(random.uniform(0.3, 0.7), 1)
        near_miss_options = [
            f"Only {mult}×... but you were ONE ROLL from a 20× JACKPOT 💥",
            f"Low pull this time... but the JACKPOT probability just went UP 📈",
            f"{mult}×... frustrating. But that makes the next big pull feel INCREDIBLE.",
            f"The wheel was 0.3° from EPIC. Literally. Spin again. 🎰",
        ]
        return base * mult, "😤 LOW ROLL", random.choice(near_miss_options), "near_miss"

def get_spins_for_tier(tier: str) -> int:
    if tier == "Elite":   return random.randint(4, 7)
    if tier == "Premium": return random.randint(2, 4)
    return 1

def rig_xp_bar(xp: int, level: int) -> float:
    needed = level * 100
    real_pct = (xp % needed) / needed if needed > 0 else 0
    if real_pct < 0.85:
        return random.uniform(0.85, 0.92)
    return min(real_pct, 0.98)

def update_streak() -> tuple:
    today = _dt.date.today().isoformat()
    last  = st.session_state.get("last_active_date")
    streak = st.session_state.get("study_streak", 0)
    if last is None:
        st.session_state.study_streak = 1; st.session_state.last_active_date = today
        return 1, "🔥 Streak started! Don't break it!", True
    if last == today:
        return streak, "", False
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    if last == yesterday:
        streak += 1; st.session_state.study_streak = streak; st.session_state.last_active_date = today
        msg = f"🔥 {streak}-DAY STREAK! You're unstoppable!"
        if streak % 7 == 0:
            msg = f"🏆 {streak} DAYS — WEEK COMPLETE! Bonus spins unlocked!"; st.session_state.spins_left += 3
        return streak, msg, True
    else:
        old = streak; st.session_state.study_streak = 1; st.session_state.last_active_date = today
        return 1, f"💔 {old}-day streak LOST. Today is a fresh start.", True

def get_streak_urgency(streak: int, last_date: str) -> str:
    if streak < 2: return ""
    today = _dt.date.today().isoformat()
    if last_date == today: return f"✅ Streak safe today! {streak} days and counting."
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    if last_date == yesterday:
        now_hour = _dt.datetime.now().hour
        if now_hour >= 20: return f"🚨 CRITICAL: Your {streak}-day streak DIES at midnight! You have {24 - now_hour} hours!"
        elif now_hour >= 16: return f"⚠️ WARNING: {streak}-day streak needs a mission TODAY. Don't lose it."
        else: return f"🔥 {streak}-day streak active. Complete a mission to keep it alive!"
    return f"💔 Streak broken. Starting fresh. Build it back."

def apply_welcome_bonus():
    if not st.session_state.get("welcome_bonus_applied", False):
        st.session_state.welcome_bonus_applied = True
        st.session_state.gold += 5.0; st.session_state.xp += 25
        st.session_state.incubator_eggs += 1; st.session_state.spins_left += 1
        return True
    return False

def loot_box_html(item_name: str, rarity: str, color: str) -> str:
    rarity_colors = {"JACKPOT":"#FFD700","EPIC":"#AA44FF","GREAT":"#4488FF","SOLID":"#44FF88","LOW":"#888888"}
    rc = rarity_colors.get(rarity.upper().split()[0], "#FFD700")
    return f"""<div style='text-align:center;padding:32px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);border:3px solid {rc};border-radius:20px;animation:lootpulse 0.6s ease-in-out 3;box-shadow:0 0 40px {rc}88;'><div style='font-size:64px;animation:lootbounce 0.4s ease-in-out infinite alternate'>🎁</div><div style='font-size:28px;font-family:Bebas Neue,sans-serif;color:{rc};letter-spacing:6px;margin:12px 0'>{rarity}</div><div style='font-size:20px;color:#ffffff;font-family:Space Mono,monospace'>{item_name}</div></div><style>@keyframes lootpulse{{0%{{box-shadow:0 0 20px {rc}44}}50%{{box-shadow:0 0 60px {rc}cc}}100%{{box-shadow:0 0 20px {rc}44}}}}@keyframes lootbounce{{from{{transform:scale(1) rotate(-5deg)}}to{{transform:scale(1.2) rotate(5deg)}}}}</style>"""

def streak_danger_html(streak: int, color: str) -> str:
    if streak < 2: return ""
    return f"""<div style='background:linear-gradient(90deg,#3a0000,#1a0000);border:2px solid #FF2222;border-radius:12px;padding:12px 20px;text-align:center;margin:8px 0;animation:streakpulse 1.5s ease-in-out infinite;'><span style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FF4444;letter-spacing:3px'>🔥 {streak}-DAY STREAK AT RISK</span><span style='display:block;font-family:Space Mono,monospace;font-size:11px;color:#FF8888;margin-top:4px'>Complete a mission TODAY or lose it forever.</span></div><style>@keyframes streakpulse{{0%,100%{{border-color:#FF2222}}50%{{border-color:#FF8888}}}}</style>"""

# ─────────────────────────────────────────────────────────────────────────────
# AI STORYLINE + ACHIEVEMENT GENERATION (ORIGINAL — PRESERVED)
# ─────────────────────────────────────────────────────────────────────────────
def generate_story_chapter(theme, chapter, prev_story, client):
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
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=200, messages=[{"role":"user","content":prompt}])
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
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=400, messages=[{"role":"user","content":prompt}])
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`")
        data = json.loads(raw)
        return data[:5]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# MONSTER DATABASE
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

def hatch_egg(theme):
    roll = random.randint(1,100); cumulative = 0; chosen = EGG_RARITIES[-1]
    for r in EGG_RARITIES:
        cumulative += r["chance"]
        if roll <= cumulative: chosen = r; break
    monster_names = {
        "Common":    [f"{theme} Scout", f"{theme} Grunt", f"{theme} Wisp"],
        "Rare":      [f"{theme} Hunter", f"{theme} Phantom", f"{theme} Sentinel"],
        "Epic":      [f"{theme} Warlord", f"{theme} Specter", f"{theme} Colossus"],
        "Legendary": [f"{theme} God", f"{theme} Titan", f"{theme} Overlord"],
    }
    name = random.choice(monster_names.get(chosen["rarity"], [f"{theme} Creature"]))
    return {"name": name, "rarity": chosen["rarity"], "color": chosen["color"], "reward_mult": chosen["reward_mult"]}


# ─────────────────────────────────────────────────────────────────────────────
# API + JSON HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_claude_client():
    try: return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except Exception: return None

def extract_json(raw_text):
    if not raw_text: return None
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    try: return json.loads(cleaned)
    except Exception: pass
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except Exception: pass
    result = {}
    for key in ["currency","color","shield_name","booster_name","description","shield_flavor","booster_flavor","battle_style"]:
        m = re.search(rf'["\']?{key}["\']?\s*:\s*["\']([^"\'<>]+)["\']', cleaned, re.IGNORECASE)
        if m: result[key] = m.group(1).strip()
    return result if len(result) >= 4 else None

# ─────────────────────────────────────────────────────────────────────────────
# LORE PROMPT — ATOMIC SPECIFICITY (ORIGINAL — PRESERVED)
# ─────────────────────────────────────────────────────────────────────────────
LORE_PROMPT = """You are the ULTIMATE authority on every game, anime, manga, sport, team, brand, movie, show, book, music genre, artist, fashion brand, historical era, cultural phenomenon, character, sub-group, weapon, location, and concept in human history. Your knowledge is PERFECT and ENCYCLOPEDIC.

A user has chosen the universe: "{theme}"

CRITICAL RULES:
1. ATOMIC SPECIFICITY: If given a CHARACTER (e.g. "Roronoa Zoro", "Kobe Bryant", "Tanjiro") — use THAT character's EXACT moves, weapons, colors, signature moments, catchphrases. NOT the parent franchise. Zoro = green hair, 3 swords, Santoryu. Tanjiro = water breathing, scar, checkered haori. Kobe = fadeaway, Mamba Mentality, #24.
2. If given a TEAM (e.g. "Chicago Bulls 1996", "Germa 66") — use THAT team's exact identity, colors, members, tactics.
3. If given a MERGED universe (e.g. "Naruto meets Star Wars") — blend both with creative fusion.
4. NEVER be generic. EVERY field must drip with universe-specific detail.
5. Your descriptions should feel like they were written by the biggest superfan of this exact thing.
6. CURRENCY RULE: If the character/group belongs to a parent universe with established currency, ALWAYS use that currency (One Piece = Berries, Naruto = Ryo, Dragon Ball = Zeni, Harry Potter = Galleons, Star Wars = Galactic Credits, Pokémon = PokéDollars, Minecraft = Emeralds).

Return ONLY a single raw JSON object. No explanation, no markdown, no code fences.

Fields:
- "currency": The EXACT in-universe currency. See currency rule above.
- "color": The single most ICONIC hex color for THIS EXACT thing. For specific characters use THEIR personal color, not the franchise. Reference: Mario=#E52521, Sonic=#0057A8, Minecraft=#5D9E35, Fortnite=#BEFF00, Roblox=#E8272A, Pokemon=#FFCB05, Valorant=#FF4655, One Piece=#E8372B, Naruto=#FF6600, Dragon Ball=#FF8C00, Demon Slayer=#22AA44, JJK=#6600CC, F1=#FF1801, NBA=#EE6730, NFL=#013369, Star Wars=#FFE81F, Marvel=#ED1D24, Harry Potter=#740001, Halo=#00B4D8, Nike=#111111, Spotify=#1DB954.
- "shield_name": The EXACT most iconic defensive ability/armor for THIS character/universe. Must be a real named technique/item from the source. Never generic.
- "booster_name": The EXACT most iconic speed/movement ability. Real named technique. Never generic.
- "shield_flavor": ONE electrifying sentence (max 12 words) describing the defense. Written like a superfan.
- "booster_flavor": ONE electrifying sentence (max 12 words) describing the speed. Written like a superfan.
- "description": One legendary sentence (max 12 words) capturing the SOUL of this. Not generic. Must reference specific lore.
- "battle_style": One of "shooter","turnbased","reaction","rpgclick","survival","rhythm","racing","trivia".
- "player_visual": Object describing the PLAYER character's appearance for 2D pixel art rendering. Include: "hair_color" (hex), "hair_style" (one of: "spiky","long","short","bald","mohawk","ponytail","afro","flowing","twin_tails","messy"), "skin_color" (hex), "outfit_color" (hex), "outfit_secondary" (hex), "weapon" (one of: "sword","dual_sword","triple_sword","gun","staff","fists","bow","scythe","shield_weapon","none","ball","racket","wand"), "weapon_color" (hex), "eye_color" (hex), "cape" (true/false), "cape_color" (hex or ""), "aura_color" (hex), "body_build" (one of: "slim","average","muscular","large","tiny")
- "enemy_visual": Same format as player_visual but for the enemy boss.
- "lore_achievements": Array of 3 objects, each with "name" (emoji + 2-4 words, universe-specific) and "desc" (one sentence connecting universe lore to studying). Example for Naruto: {{"name":"🍥 Shadow Clone Scholar","desc":"Complete 10 missions — one for each shadow clone."}}

Return exactly:
{{"currency":"...","color":"#RRGGBB","shield_name":"...","booster_name":"...","description":"...","shield_flavor":"...","booster_flavor":"...","battle_style":"...","player_visual":{{...}},"enemy_visual":{{...}},"lore_achievements":[{{"name":"...","desc":"..."}},{{"name":"...","desc":"..."}},{{"name":"...","desc":"..."}}]}}"""

# ─────────────────────────────────────────────────────────────────────────────
# HARD FALLBACKS — ALL 30+ UNIVERSES (ORIGINAL — PRESERVED)
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

REQUIRED_KEYS = ["currency","color","shield_name","booster_name","description"]

def get_fallback(theme):
    t = theme.lower().strip()
    if t in HARD_FALLBACKS: return HARD_FALLBACKS[t]
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key: return data
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


# ─────────────────────────────────────────────────────────────────────────────
# RESOLVE UNIVERSE — WITH CONTENT SAFETY FILTER (v10)
# ─────────────────────────────────────────────────────────────────────────────
def resolve_universe(theme):
    if not theme.strip():
        return {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
    check = filter_universe_input(theme)
    if not check["safe"]:
        return {"safe": False, "reason": check["reason"], "data": None}
    cleaned_theme = check["cleaned"]
    client = get_claude_client()
    if client is not None:
        try:
            safe_prompt = get_ai_safety_prefix() + "\n\n" + LORE_PROMPT.format(theme=cleaned_theme)
            message = client.messages.create(model="claude-sonnet-4-5", max_tokens=400, messages=[{"role":"user","content":safe_prompt}])
            raw = message.content[0].text.strip()
            if '"blocked"' in raw and "true" in raw.lower():
                return {"safe": False, "reason": "Our AI detected this theme isn't appropriate. Try a game, anime, sport, movie, or anything you love! 🌌", "data": None}
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color","")): data["color"] = "#FFD700"
                data.setdefault("shield_flavor", "An ability forged in the heart of this universe.")
                data.setdefault("booster_flavor", "Speed that defies every known law of physics.")
                data.setdefault("battle_style", "random")
                data.setdefault("player_visual", {})
                data.setdefault("enemy_visual", {})
                data.setdefault("lore_achievements", [])
                data["shield_effect"] = SHIELD_EFFECT; data["booster_effect"] = BOOSTER_EFFECT
                return {"safe": True, "data": data}
        except Exception: pass
    data = get_fallback(cleaned_theme)
    data["shield_effect"] = SHIELD_EFFECT; data["booster_effect"] = BOOSTER_EFFECT
    return {"safe": True, "data": data}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def is_light(hex_color):
    h = hex_color.lstrip('#')
    try:
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return (r*299+g*587+b*114)/1000 > 128
    except: return False

def text_on(hex_color):
    return "#000000" if is_light(hex_color) else "#ffffff"

def readable_color(theme_color, bg_color):
    if theme_color.lower() == bg_color.lower():
        return "#ffffff" if is_light(bg_color) else "#FFD700"
    h = theme_color.lstrip('#')
    try:
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        luminance = (r*299+g*587+b*114)/1000
        if is_light(bg_color) and luminance > 180: return "#333333"
        if not is_light(bg_color) and luminance < 60: return "#FFD700"
    except: pass
    return theme_color

def check_achievements(session):
    newly_unlocked = []
    unlocked = session.get("unlocked_achievements", set())
    for ach in ACHIEVEMENTS:
        if ach["id"] not in unlocked:
            try:
                if ach["req"](session): unlocked.add(ach["id"]); newly_unlocked.append(ach)
            except: pass
    session["unlocked_achievements"] = unlocked
    return newly_unlocked

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
        "welcome_bonus_applied": False, "battle_subject_chosen": False,
        "last_spin_time": None,
    })


# ─────────────────────────────────────────────────────────────────────────────
# GATEWAY SCREEN — WITH 7 FIDGET SPINNERS (ORIGINAL — PRESERVED)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_name is None:
    def _get_gateway_html():
        return (
            '<style>'
            '@import url(\'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap\');'
            'html,body,[data-testid=stAppViewContainer],[data-testid=stApp]{background:#000008!important;color:white!important;}'
            '[data-testid=stHeader],[data-testid=stToolbar],[data-testid=stDecoration],#MainMenu,footer{display:none!important;}'
            '.block-container{padding:0 1rem 2rem!important;max-width:100%!important;}'
            '[data-testid=stAppViewContainer]{'
            'background:radial-gradient(ellipse 65% 55% at 5% 10%,rgba(255,215,0,0.22) 0%,transparent 60%),radial-gradient(ellipse 55% 45% at 95% 5%,rgba(255,50,50,0.18) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 50% 100%,rgba(0,200,255,0.18) 0%,transparent 60%),radial-gradient(ellipse 45% 40% at 90% 70%,rgba(160,80,220,0.15) 0%,transparent 60%),radial-gradient(ellipse 40% 35% at 10% 80%,rgba(0,255,130,0.12) 0%,transparent 60%),#000008!important;'
            'animation:orb-breathe 8s ease-in-out infinite alternate!important;}'
            '@keyframes orb-breathe{0%{filter:brightness(0.85) saturate(0.85);}50%{filter:brightness(1.25) saturate(1.35);}100%{filter:brightness(0.85) saturate(0.85);}}'
            '[data-testid=stAppViewContainer]::before{content:\'\';position:fixed;top:0;left:0;width:100%;height:100%;background-image:linear-gradient(rgba(255,215,0,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,215,0,0.04) 1px,transparent 1px);background-size:55px 55px;pointer-events:none;z-index:0;animation:grid-breathe 5s ease-in-out infinite alternate;}'
            '@keyframes grid-breathe{0%{opacity:0.25;}100%{opacity:0.9;}}'
            '.star-field{width:100%;height:90px;background-image:radial-gradient(2px 2px at 5% 30%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 18% 70%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 32% 20%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 47% 85%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 61% 40%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 75% 65%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 89% 15%,#fff 0%,transparent 100%),radial-gradient(2px 2px at 12% 50%,#fff 0%,transparent 100%),radial-gradient(3px 3px at 14% 60%,#FFD700 0%,transparent 100%),radial-gradient(3px 3px at 70% 35%,#00C8FF 0%,transparent 100%),radial-gradient(3px 3px at 43% 75%,#FF5050 0%,transparent 100%),radial-gradient(3px 3px at 90% 90%,#A050DC 0%,transparent 100%);animation:star-twinkle 3s ease-in-out infinite alternate;margin-bottom:8px;}'
            '@keyframes star-twinkle{0%{opacity:0.3;}100%{opacity:1.0;}}'
            '.scanline-wrap{width:100%;height:4px;overflow:hidden;margin-bottom:16px;}'
            '.scanline{width:40%;height:4px;background:linear-gradient(90deg,transparent,#FFD700,transparent);animation:scan-sweep 2s linear infinite;box-shadow:0 0 20px 4px rgba(255,215,0,0.6);}'
            '@keyframes scan-sweep{0%{transform:translateX(-150%);}100%{transform:translateX(400%);}}'
            '.top-badge{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.4);border-radius:99px;padding:8px 24px;font-family:Space Mono,monospace;font-size:11px;letter-spacing:3px;color:#FFD700;text-transform:uppercase;text-align:center;display:table;margin:0 auto 20px;animation:badge-pulse 3s ease-in-out infinite alternate;}'
            '@keyframes badge-pulse{0%{box-shadow:0 0 10px rgba(255,215,0,0.2);}100%{box-shadow:0 0 40px rgba(255,215,0,0.6);}}'
            '.gw-main-title{font-family:Bebas Neue,sans-serif;font-size:clamp(72px,14vw,150px);text-align:center;letter-spacing:8px;line-height:0.88;background:linear-gradient(135deg,#FFD700 0%,#FF8C00 30%,#FF3C3C 65%,#CC00FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:title-glow 4s ease-in-out infinite alternate;margin-bottom:8px;}'
            '@keyframes title-glow{0%{filter:drop-shadow(0 0 12px rgba(255,215,0,0.5));}100%{filter:drop-shadow(0 0 60px rgba(255,140,0,0.8));}}'
            '.gw-subtitle{font-family:Orbitron,sans-serif;font-size:clamp(12px,1.8vw,18px);text-align:center;letter-spacing:5px;color:#ffffff;text-transform:uppercase;margin-bottom:20px;text-shadow:0 0 20px rgba(255,255,255,0.4);}'
            '.features-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0 24px;}'
            '.feature-pill{background:rgba(255,215,0,0.12);border:1px solid rgba(255,215,0,0.35);border-radius:99px;padding:7px 16px;font-family:Space Mono,monospace;font-size:12px;color:#ffffff;letter-spacing:1px;}'
            '.feature-pill span{margin-right:5px;}'
            '.stats-ticker{display:flex;gap:32px;justify-content:center;margin-bottom:24px;flex-wrap:wrap;}'
            '.stat-item{text-align:center;animation:stat-float 3s ease-in-out infinite alternate;}'
            '.stat-item:nth-child(2){animation-delay:-1s;}.stat-item:nth-child(3){animation-delay:-2s;}'
            '@keyframes stat-float{0%{transform:translateY(0);}100%{transform:translateY(-7px);}}'
            '.stat-num{font-family:Bebas Neue,sans-serif;font-size:42px;color:#FFD700;line-height:1;text-shadow:0 0 20px rgba(255,215,0,0.5);}'
            '.stat-label{font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:2px;text-transform:uppercase;margin-top:2px;}'
            '.gw-divider{width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.4),transparent);margin:8px 0 28px;}'
            '.mode-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:16px;}'
            '.mode-card{background:rgba(255,255,255,0.04);border:2px solid rgba(255,215,0,0.2);border-radius:18px;padding:20px 16px;text-align:center;cursor:pointer;transition:all 0.2s;}'
            '.mode-card:hover{background:rgba(255,215,0,0.08);border-color:rgba(255,215,0,0.5);}'
            '.mode-emoji{font-size:36px;display:block;margin-bottom:10px;}'
            '.mode-name{font-family:Bebas Neue,sans-serif;font-size:22px;letter-spacing:3px;color:#FFD700;margin-bottom:8px;}'
            '.mode-desc{font-family:Space Mono,monospace;font-size:11px;color:#ffffff;line-height:1.6;}'
            '.stTextInput>div>div>input{background:#ffffff!important;border:2px solid rgba(255,215,0,0.5)!important;border-radius:10px!important;color:#000000!important;font-family:Space Mono,monospace!important;font-size:14px!important;padding:12px 16px!important;caret-color:#000000!important;}'
            '.stTextInput>div>div>input::placeholder{color:#666666!important;}'
            '.stTextInput>div>div>input:focus{border-color:#FFD700!important;box-shadow:0 0 20px rgba(255,215,0,0.25)!important;}'
            '.stTextInput label{font-family:Space Mono,monospace!important;font-size:11px!important;letter-spacing:3px!important;color:#ffffff!important;text-transform:uppercase!important;}'
            'div.stButton>button{background:linear-gradient(135deg,#FFD700,#FF8C00)!important;border:none!important;color:#000000!important;font-family:Bebas Neue,sans-serif!important;font-size:24px!important;letter-spacing:4px!important;padding:18px!important;border-radius:14px!important;width:100%!important;box-shadow:0 0 35px rgba(255,215,0,0.4)!important;transition:all 0.3s!important;margin-top:12px!important;}'
            'div.stButton>button:hover{transform:scale(1.02)!important;box-shadow:0 0 60px rgba(255,215,0,0.7)!important;}'
            '</style>'
            '<div class="scanline-wrap"><div class="scanline"></div></div>'
            '<div class="star-field"></div>'
            '<div class="top-badge">⚡ 30-Second RPG Study System · Any Universe · Zero Limits</div>'
            '<div class="gw-main-title">TITAN<br>OMNIVERSE</div>'
            '<div class="gw-subtitle">Infiniteverse · Study RPG · Unlock Your Power</div>'
            '<div class="features-row">'
            '<div class="feature-pill"><span>🎮</span>Pick ANY Universe</div>'
            '<div class="feature-pill"><span>⏱</span>30-Second Missions</div>'
            '<div class="feature-pill"><span>💰</span>Earn Real Rewards</div>'
            '<div class="feature-pill"><span>🔥</span>Study Like a Champion</div>'
            '<div class="feature-pill"><span>🌈</span>Fully Customizable</div>'
            '<div class="feature-pill"><span>⚡</span>Powered by AI</div>'
            '</div>'
            '<div class="stats-ticker">'
            '<div class="stat-item"><div class="stat-num">∞</div><div class="stat-label">Universes</div></div>'
            '<div class="stat-item"><div class="stat-num">30s</div><div class="stat-label">To Start</div></div>'
            '<div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Free</div></div>'
            '<div class="stat-item"><div class="stat-num">0</div><div class="stat-label">Excuses</div></div>'
            '</div>'
            '<div class="gw-divider"></div>'
        )
    st.markdown(_get_gateway_html(), unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("⚡ HOW DOES THIS WORK?", key="how_toggle"):
            st.session_state.how_open = not st.session_state.how_open
        if st.session_state.how_open:
            st.markdown("""<div style='background:rgba(0,0,0,0.6);border:1px solid rgba(255,215,0,0.3);border-radius:20px;padding:24px;margin-top:12px;'>
                <div style='margin-bottom:18px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.08);'><span style='font-size:28px'>🌌</span><div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;letter-spacing:2px'>1 — PICK YOUR UNIVERSE</div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:1.7'>ANY universe. AI builds it instantly. Colors, currency, abilities, storyline — all yours.</div></div>
                <div style='margin-bottom:18px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.08);'><span style='font-size:28px'>⏱</span><div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;letter-spacing:2px'>2 — STUDY FOR 30 SECONDS</div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:1.7'>Work. Study. Do anything productive. Get paid in universe currency. Real rewards.</div></div>
                <div><span style='font-size:28px'>📸</span><div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;letter-spacing:2px'>3 — PROVE IT. COLLECT IT.</div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:1.7'>Upload proof. No proof = no coins. Simple. Then spin the wheel. Battle. Hatch eggs. Go insane.</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:4px;text-shadow:0 0 20px rgba(255,215,0,0.5)'>⚡ CHOOSE YOUR MODE</div>
        <div class='mode-grid'>
            <div class='mode-card'><span class='mode-emoji'>⚡</span><div class='mode-name'>CHILL</div><div class='mode-desc'>Missions. Currency. Level up.<br>Clean. Simple. No stress.</div></div>
            <div class='mode-card'><span class='mode-emoji'>🔥</span><div class='mode-name'>GRINDER</div><div class='mode-desc'>Adds Battles, Abilities,<br>Monster Hatching & Achievements.</div></div>
            <div class='mode-card'><span class='mode-emoji'>💀</span><div class='mode-name'>OBSESSED</div><div class='mode-desc'>EVERYTHING. Full chaos.<br>Maximum power. No limits.</div></div>
        </div>""", unsafe_allow_html=True)
        mode_col1, mode_col2, mode_col3 = st.columns(3)
        with mode_col1:
            if st.button("⚡ CHILL", key="mode_chill"): st.session_state.game_mode = "chill"
        with mode_col2:
            if st.button("🔥 GRINDER", key="mode_grinder"): st.session_state.game_mode = "grinder"
        with mode_col3:
            if st.button("💀 OBSESSED", key="mode_obsessed"): st.session_state.game_mode = "obsessed"
        if st.session_state.game_mode:
            mode_labels = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}
            st.success(f"MODE SELECTED: {mode_labels[st.session_state.game_mode]} ✅")
        st.markdown("<br>", unsafe_allow_html=True)
        name_input  = st.text_input("⚡ Champion Name", placeholder="What are you called?", key="gw_name")
        theme_input = st.text_input("🌌 Your Universe", placeholder="Leave empty for INFINITE POWER · or type anything: Naruto, F1, Nike, Medieval Space War...", key="gw_theme")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ ENTER THE INFINITEVERSE", key="gw_enter"):
            if not name_input.strip():
                st.error("Enter your champion name to begin.")
            elif not st.session_state.game_mode:
                st.error("Pick your mode first — CHILL, GRINDER, or OBSESSED!")
            else:
                theme_val    = theme_input.strip()
                display_name = theme_val if theme_val else DEFAULT_UNIVERSE_NAME
                if theme_val:
                    check = filter_universe_input(theme_val)
                    if not check["safe"]:
                        st.error(f"⚠️ {check['reason']}"); st.stop()
                    theme_val = check["cleaned"]; display_name = theme_val
                with st.spinner(f"🌌 Loading {display_name.upper()}..."):
                    result = resolve_universe(theme_val)
                if not result["safe"]:
                    st.error(f"⚠️ {result['reason']}"); st.stop()
                st.session_state.user_name  = name_input.strip()
                st.session_state.world_data = result["data"]
                st.session_state.vibe_color = result["data"].get("color","#FFD700")
                st.session_state.user_theme = display_name
                apply_welcome_bonus()
                st.rerun()

    # ── FIDGET SPINNERS — FULL WIDTH AT BOTTOM OF GATEWAY ──
    import base64 as _b64
    _SPINNER_B64 = "PCFET0NUWVBFIGh0bWw+PGh0bWw+PGhlYWQ+PG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CkBpbXBvcnQgdXJsKCdodHRwczovL2ZvbnRzLmdvb2dsZWFwaXMuY29tL2NzczI/ZmFtaWx5PU9yYml0cm9uOndnaHRAOTAwJmRpc3BsYXk9c3dhcCcpOwoqe2JveC1zaXppbmc6Ym9yZGVyLWJveDttYXJnaW46MDtwYWRkaW5nOjA7fQpib2R5e2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7bWFyZ2luOjA7fQojdW5pdmVyc2V7d2lkdGg6MTAwJTtoZWlnaHQ6MzMwcHg7YmFja2dyb3VuZDpyYWRpYWwtZ3JhZGllbnQoZWxsaXBzZSBhdCA1MCUgNjAlLCMwYTAwMjAgMCUsIzAwMDAwOCA3MCUsIzAwMDAwMCAxMDAlKTtib3JkZXItcmFkaXVzOjE2cHg7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDI1NSwyNTUsMjU1LDAuMDcpO3Bvc2l0aW9uOnJlbGF0aXZlO292ZXJmbG93OmhpZGRlbjtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2FsaWduLWl0ZW1zOmNlbnRlcjtqdXN0aWZ5LWNvbnRlbnQ6Y2VudGVyO30KI3JhY2t7ZGlzcGxheTpmbGV4O2dhcDoxNHB4O2p1c3RpZnktY29udGVudDpjZW50ZXI7YWxpZ24taXRlbXM6Y2VudGVyO3otaW5kZXg6Mjtwb3NpdGlvbjpyZWxhdGl2ZTtwYWRkaW5nOjEwcHggMDt9Ci5zbG90e2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo0cHg7fQouc2xibHtmb250LWZhbWlseTpPcmJpdHJvbixtb25vc3BhY2U7Zm9udC1zaXplOjdweDtsZXR0ZXItc3BhY2luZzoycHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnJnYmEoMjU1LDI1NSwyNTUsMC40KTt9Ci5zcnBte2ZvbnQtZmFtaWx5Ok9yYml0cm9uLG1vbm9zcGFjZTtmb250LXNpemU6OHB4O2xldHRlci1zcGFjaW5nOjFweDttaW4taGVpZ2h0OjEzcHg7dGV4dC1hbGlnbjpjZW50ZXI7fQoubmJ0bntwYWRkaW5nOjRweCAxMHB4O2ZvbnQtc2l6ZTo3cHg7Zm9udC1mYW1pbHk6T3JiaXRyb24sbW9ub3NwYWNlO2JvcmRlci1yYWRpdXM6NnB4O2N1cnNvcjpwb2ludGVyO2xldHRlci1zcGFjaW5nOjJweDtib3JkZXI6MS41cHggc29saWQ7YmFja2dyb3VuZDpyZ2JhKDAsMCwwLDAuNik7dHJhbnNpdGlvbjphbGwgMC4xNXM7bWFyZ2luLXRvcDoycHg7fQoubmJ0bjpob3Zlcnt0cmFuc2Zvcm06c2NhbGUoMS4wOSk7ZmlsdGVyOmJyaWdodG5lc3MoMS41KTt9CiNmbHtwb3NpdGlvbjphYnNvbHV0ZTtib3R0b206MDtsZWZ0OjA7d2lkdGg6MTAwJTtoZWlnaHQ6MnB4O3otaW5kZXg6MTthbmltYXRpb246ZmxhIDJzIGxpbmVhciBpbmZpbml0ZTt9CkBrZXlmcmFtZXMgZmxhezAle2ZpbHRlcjpodWUtcm90YXRlKDBkZWcpO2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLHRyYW5zcGFyZW50LCNGRkQ3MDAsI0ZGNDQwMCwjRkYwMEZGLCMwMEZGRkYsdHJhbnNwYXJlbnQpO30xMDAle2ZpbHRlcjpodWUtcm90YXRlKDM2MGRlZyk7YmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoOTBkZWcsdHJhbnNwYXJlbnQsI0ZGRDcwMCwjRkY0NDAwLCNGRjAwRkYsIzAwRkZGRix0cmFuc3BhcmVudCk7fX0KPC9zdHlsZT48L2hlYWQ+PGJvZHk+CjxkaXYgaWQ9InVuaXZlcnNlIj4KPGNhbnZhcyBpZD0ic3RhcnMiIHN0eWxlPSJwb3NpdGlvbjphYnNvbHV0ZTt0b3A6MDtsZWZ0OjA7cG9pbnRlci1ldmVudHM6bm9uZTt6LWluZGV4OjAiIHdpZHRoPSI5MDAiIGhlaWdodD0iMzMwIj48L2NhbnZhcz4KPGRpdiBpZD0icmFjayI+PC9kaXY+CjxkaXYgaWQ9ImZsIj48L2Rpdj4KPC9kaXY+CjxzY3JpcHQ+CnZhciBzYz1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnc3RhcnMnKSxzY3R4PXNjLmdldENvbnRleHQoJzJkJyk7CnZhciBTVEFSUz1bXTtmb3IodmFyIGk9MDtpPDEwMDtpKyspU1RBUlMucHVzaCh7eDpNYXRoLnJhbmRvbSgpKjkwMCx5Ok1hdGgucmFuZG9tKCkqMzMwLHI6TWF0aC5yYW5kb20oKSoxLjMrMC4zLGE6TWF0aC5yYW5kb20oKSxkYTpNYXRoLnJhbmRvbSgpKjAuMDA3KzAuMDAyLGNvbDonaHNsKCcrKDE4MCtNYXRoLnJhbmRvbSgpKjgwKSsnLDgwJSw5MCUpJ30pOwpmdW5jdGlvbiBkUygpe3NjdHguY2xlYXJSZWN0KDAsMCw5MDAsMzMwKTtTVEFSUy5mb3JFYWNoKGZ1bmN0aW9uKHMpe3MuYSs9cy5kYTtpZihzLmE+MXx8cy5hPDApcy5kYSo9LTE7c2N0eC5nbG9iYWxBbHBoYT1zLmEqMC43NTtzY3R4LmJlZ2luUGF0aCgpO3NjdHguYXJjKHMueCxzLnkscy5yLDAsTWF0aC5QSSoyKTtzY3R4LmZpbGxTdHlsZT1zLmNvbDtzY3R4LmZpbGwoKTt9KTtzY3R4Lmdsb2JhbEFscGhhPTE7fQp2YXIgREY9WwogIHtpZDonczAnLHN6OjU4LGxibDonU09MQVIgRkxBUkUnLG51a2U6ZmFsc2UsYnY6MC40MCxibDo0LHNoOidkcm9wJyxwOlsnI0ZGNjYwMCcsJyNGRjIyMDAnLCcjRkZENzAwJywnI0ZGODgwMCddLGd3OicjRkY0NDAwJyxybTonI0ZGRDcwMCcsaGI6JyNGRkZGRkYnLHRyOjEyLHB0OnRydWV9LAogIHtpZDonczEnLHN6OjUyLGxibDonVk9JRCBTVE9STScsbnVrZTpmYWxzZSxidjowLjUwLGJsOjYsc2g6J3dpbmcnLHA6WycjODgwMEZGJywnIzQ0MDBDQycsJyNDQzAwRkYnLCcjRkY0NEZGJ10sZ3c6JyNBQTAwRkYnLHJtOicjRkY4OEZGJyxoYjonI0ZGRkZGRicsdHI6MTYscHQ6dHJ1ZX0sCiAge2lkOidzMicsc3o6NTUsbGJsOidNQVRSSVgnLG51a2U6ZmFsc2UsYnY6MC40NSxibDozLHNoOidjcnlzJyxwOlsnIzAwRkY0NCcsJyMwMENDMzMnLCcjMDBGRjg4JywnI0FBRkZDQyddLGd3OicjMDBGRjQ0JyxybTonIzg4RkZCQicsaGI6JyMxMTExMTEnLHRyOjEwLHB0OmZhbHNlfSwKICB7aWQ6J3MzJyxzejo1MCxsYmw6J05PVkEgUFVMU0UnLG51a2U6ZmFsc2UsYnY6MC42MCxibDo1LHNoOidibGFkJyxwOlsnIzAwQ0NGRicsJyMwMDg4RkYnLCcjMDBGRkVFJywnIzg4RERGRiddLGd3OicjMDBDQ0ZGJyxybTonI0FBRUVGRicsaGI6JyMwMDAwMzMnLHRyOjE0LHB0OnRydWV9LAogIHtpZDonczQnLHN6OjU2LGxibDonVElUQU4gV0FSUCcsbnVrZTp0cnVlLG52OjQuNSxidjowLGJsOjcsc2g6J2ZhbicscDpbJyNGRkQ3MDAnLCcjRkY0NDAwJywnI0ZGODgwMCcsJyNGRkVFQUEnXSxndzonI0ZGRDcwMCcscm06JyNGRjQ0MDAnLGhiOicjMjIxMTAwJyx0cjoxOCxwdDp0cnVlfSwKICB7aWQ6J3M1Jyxzejo1NCxsYmw6J0hZUEVSIE5VS0UnLG51a2U6dHJ1ZSxudjo1LjAsYnY6MCxibDo0LHNoOidkcm9wJyxwOlsnI0ZGMDA0NCcsJyNGRjQ0MDAnLCcjRkYwMDg4JywnI0ZGODgwMCddLGd3OicjRkYwMDQ0JyxybTonI0ZGODhBQScsaGI6JyNGRkZGRkYnLHRyOjIwLHB0OnRydWV9LAogIHtpZDonczYnLHN6OjYyLGxibDonT01FR0EgTlVLRScsbnVrZTp0cnVlLG52OjguMCxidjowLGJsOjgsc2g6J2ZhbicscDpbJyNGRkZGRkYnLCcjRkZENzAwJywnI0ZGMjIwMCcsJyNGRkFBMDAnXSxndzonI0ZGRkZGRicscm06JyNGRkQ3MDAnLGhiOicjMDAwMDAwJyx0cjozMCxwdDp0cnVlfQpdOwp2YXIgU1Q9e30sVFI9e307CnZhciByYWNrPWRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdyYWNrJyk7CkRGLmZvckVhY2goZnVuY3Rpb24oc3ApewogIFNUW3NwLmlkXT17YTpNYXRoLnJhbmRvbSgpKjYuMjgsdjpzcC5udWtlPzA6c3AuYnYrTWF0aC5yYW5kb20oKSowLjA2LGRnOmZhbHNlLGxBOjAsbFQ6MH07CiAgVFJbc3AuaWRdPVtdOwogIHZhciBzbG90PWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO3Nsb3QuY2xhc3NOYW1lPSdzbG90JzsKICB2YXIgY3Y9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnY2FudmFzJyk7Y3YuaWQ9J2NfJytzcC5pZDtjdi53aWR0aD1zcC5zeioyO2N2LmhlaWdodD1zcC5zeioyO2N2LnN0eWxlLmNzc1RleHQ9J2N1cnNvcjpncmFiO2JvcmRlci1yYWRpdXM6NTAlO2Rpc3BsYXk6YmxvY2s7JzsKICB2YXIgbGI9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnZGl2Jyk7bGIuY2xhc3NOYW1lPSdzbGJsJztsYi50ZXh0Q29udGVudD1zcC5sYmw7CiAgdmFyIHJtPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO3JtLmlkPSdyXycrc3AuaWQ7cm0uY2xhc3NOYW1lPSdzcnBtJztybS5zdHlsZS5jb2xvcj1zcC5ndzsKICBzbG90LmFwcGVuZENoaWxkKGN2KTtzbG90LmFwcGVuZENoaWxkKGxiKTtzbG90LmFwcGVuZENoaWxkKHJtKTsKICBpZihzcC5udWtlKXt2YXIgYnRuPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2J1dHRvbicpO2J0bi5jbGFzc05hbWU9J25idG4nO2J0bi50ZXh0Q29udGVudD1zcC5pZD09PSdzNic/J0RFVE9OQVRFJzonSUdOSVRFJztidG4uc3R5bGUuYm9yZGVyQ29sb3I9c3AuZ3c7YnRuLnN0eWxlLmNvbG9yPXNwLmd3O2J0bi5vbmNsaWNrPShmdW5jdGlvbihzaWQsbnYpe3JldHVybiBmdW5jdGlvbigpe1NUW3NpZF0udj1udjtzaGsoKTt9O30pKHNwLmlkLHNwLm52KTtzbG90LmFwcGVuZENoaWxkKGJ0bik7fQogIHJhY2suYXBwZW5kQ2hpbGQoc2xvdCk7CiAgZnVuY3Rpb24gZ2EoZSxjKXt2YXIgcj1jLmdldEJvdW5kaW5nQ2xpZW50UmVjdCgpO3ZhciB4PShlLmNsaWVudFh8fChlLnRvdWNoZXMmJmUudG91Y2hlc1swXS5jbGllbnRYKXx8MCktci5sZWZ0LXIud2lkdGgvMjt2YXIgeT0oZS5jbGllbnRZfHwoZS50b3VjaGVzJiZlLnRvdWNoZXNbMF0uY2xpZW50WSl8fDApLXIudG9wLXIuaGVpZ2h0LzI7cmV0dXJuIE1hdGguYXRhbjIoeSx4KTt9CiAgY3YuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vkb3duJyxmdW5jdGlvbihlKXt2YXIgcz1TVFtzcC5pZF07cy5kZz10cnVlO3MubEE9Z2EoZSxjdik7cy5sVD1wZXJmb3JtYW5jZS5ub3coKTtjdi5zdHlsZS5jdXJzb3I9J2dyYWJiaW5nJzt9KTsKICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vtb3ZlJywoZnVuY3Rpb24oc2lkKXtyZXR1cm4gZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc2lkXTtpZighcy5kZylyZXR1cm47dmFyIG5vdz1wZXJmb3JtYW5jZS5ub3coKTt2YXIgY3YyPWRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdjXycrc2lkKTt2YXIgYT1nYShlLGN2Mik7dmFyIGQ9YS1zLmxBO2lmKGQ+TWF0aC5QSSlkLT02LjI4O2lmKGQ8LU1hdGguUEkpZCs9Ni4yODtzLnY9ZC9NYXRoLm1heChub3ctcy5sVCwxKSoyMDtzLmErPWQ7cy5sQT1hO3MubFQ9bm93O307fSkoc3AuaWQpKTsKICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcignbW91c2V1cCcsKGZ1bmN0aW9uKHNpZCl7cmV0dXJuIGZ1bmN0aW9uKCl7U1Rbc2lkXS5kZz1mYWxzZTtkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY18nK3NpZCkuc3R5bGUuY3Vyc29yPSdncmFiJzt9O30pKHNwLmlkKSk7CiAgY3YuYWRkRXZlbnRMaXN0ZW5lcigndG91Y2hzdGFydCcsZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc3AuaWRdO3MuZGc9dHJ1ZTtzLmxBPWdhKGUsY3YpO3MubFQ9cGVyZm9ybWFuY2Uubm93KCk7ZS5wcmV2ZW50RGVmYXVsdCgpO30se3Bhc3NpdmU6ZmFsc2V9KTsKICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcigndG91Y2htb3ZlJywoZnVuY3Rpb24oc2lkKXtyZXR1cm4gZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc2lkXTtpZighcy5kZylyZXR1cm47dmFyIG5vdz1wZXJmb3JtYW5jZS5ub3coKTt2YXIgY3YyPWRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdjXycrc2lkKTt2YXIgYT1nYShlLGN2Mik7dmFyIGQ9YS1zLmxBO2lmKGQ+TWF0aC5QSSlkLT02LjI4O2lmKGQ8LU1hdGguUEkpZCs9Ni4yODtzLnY9ZC9NYXRoLm1heChub3ctcy5sVCwxKSoyMDtzLmErPWQ7cy5sQT1hO3MubFQ9bm93O2UucHJldmVudERlZmF1bHQoKTt9O30pKHNwLmlkKSx7cGFzc2l2ZTpmYWxzZX0pOwogIHdpbmRvdy5hZGRFdmVudExpc3RlbmVyKCd0b3VjaGVuZCcsKGZ1bmN0aW9uKHNpZCl7cmV0dXJuIGZ1bmN0aW9uKCl7U1Rbc2lkXS5kZz1mYWxzZTt9O30pKHNwLmlkKSk7Cn0pOwp2YXIgc2hha2VOPTA7CmZ1bmN0aW9uIHNoaygpe3NoYWtlTj0xNjt2YXIgdT1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgndW5pdmVyc2UnKTsoZnVuY3Rpb24gZigpe2lmKHNoYWtlTjw9MCl7dS5zdHlsZS50cmFuc2Zvcm09Jyc7cmV0dXJuO311LnN0eWxlLnRyYW5zZm9ybT0ndHJhbnNsYXRlKCcrKE1hdGgucmFuZG9tKCktLjUpKnNoYWtlTiouNysncHgsJysoTWF0aC5yYW5kb20oKS0uNSkqc2hha2VOKi40KydweCknO3NoYWtlTi0tO3JlcXVlc3RBbmltYXRpb25GcmFtZShmKTt9KSgpO30KZnVuY3Rpb24gZHJhdyhzcCxhbmdsZSx2ZWwpewogIHZhciBjdj1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY18nK3NwLmlkKTtpZighY3YpcmV0dXJuOwogIHZhciBjdHg9Y3YuZ2V0Q29udGV4dCgnMmQnKSxzej1zcC5zeixjeD1zeixjeT1zeixyPXN6LTUsc3BkPU1hdGguYWJzKHZlbCk7CiAgY3R4LmNsZWFyUmVjdCgwLDAsc3oqMixzeioyKTsKICBpZihzcGQ+MC4wNCl7dmFyIGdnPWN0eC5jcmVhdGVSYWRpYWxHcmFkaWVudChjeCxjeSxyLGN4LGN5LHIrNStzcGQqNCk7Z2cuYWRkQ29sb3JTdG9wKDAsc3AuZ3crJzc3Jyk7Z2cuYWRkQ29sb3JTdG9wKDEsc3AuZ3crJzAwJyk7Y3R4LmJlZ2luUGF0aCgpO2N0eC5hcmMoY3gsY3kscis1K3NwZCo0LDAsTWF0aC5QSSoyKTtjdHguZmlsbFN0eWxlPWdnO2N0eC5maWxsKCk7fQogIHZhciB0cj1UUltzcC5pZF07dHIucHVzaChhbmdsZSk7aWYodHIubGVuZ3RoPnNwLnRyKXRyLnNoaWZ0KCk7CiAgaWYoc3BkPjAuMSYmdHIubGVuZ3RoPjIpe2Zvcih2YXIgdGk9MDt0aTx0ci5sZW5ndGgtMTt0aSsrKXt2YXIgdGE9dHJbdGldLGZyYWM9dGkvdHIubGVuZ3RoO2Zvcih2YXIgYmk9MDtiaTxzcC5ibDtiaSsrKXt2YXIgYmEyPXRhKyhiaSo2LjI4L3NwLmJsKTtjdHguc2F2ZSgpO2N0eC50cmFuc2xhdGUoY3gsY3kpO2N0eC5yb3RhdGUoYmEyKTtjdHguZ2xvYmFsQWxwaGE9ZnJhYyowLjE4Kk1hdGgubWluKHNwZCoxLjUsMSk7Y3R4LmJlZ2luUGF0aCgpO2N0eC5lbGxpcHNlKHIqLjM4LDAsciouMzYsciouMTUsMCwwLE1hdGguUEkqMik7Y3R4LmZpbGxTdHlsZT1zcC5wWzBdO2N0eC5maWxsKCk7Y3R4LnJlc3RvcmUoKTt9fWN0eC5nbG9iYWxBbHBoYT0xO30KICBmb3IodmFyIGk9MDtpPHNwLmJsO2krKyl7CiAgICB2YXIgYmE9YW5nbGUrKGkqNi4yOC9zcC5ibCk7CiAgICBjdHguc2F2ZSgpO2N0eC50cmFuc2xhdGUoY3gsY3kpO2N0eC5yb3RhdGUoYmEpOwogICAgdmFyIGc9Y3R4LmNyZWF0ZUxpbmVhckdyYWRpZW50KDAsLXIqLjA4LHIqLjgyLHIqLjA4KTsKICAgIGcuYWRkQ29sb3JTdG9wKDAsc3AucFswXSk7Zy5hZGRDb2xvclN0b3AoLjQ1LHNwLnBbMSVzcC5wLmxlbmd0aF0pO2cuYWRkQ29sb3JTdG9wKC43NSxzcC5wWzIlc3AucC5sZW5ndGhdKTtnLmFkZENvbG9yU3RvcCgxLHNwLnBbMyVzcC5wLmxlbmd0aF0rJzIyJyk7CiAgICBjdHguZmlsbFN0eWxlPWc7Y3R4LmJlZ2luUGF0aCgpOwogICAgaWYoc3Auc2g9PT0nZHJvcCcpe2N0eC5lbGxpcHNlKHIqLjQyLDAsciouNDIsciouMTksMCwwLE1hdGguUEkqMik7fQogICAgZWxzZSBpZihzcC5zaD09PSd3aW5nJyl7Y3R4Lm1vdmVUbygwLDApO2N0eC5iZXppZXJDdXJ2ZVRvKHIqLjIsLXIqLjI4LHIqLjcsLXIqLjIyLHIqLjgyLDApO2N0eC5iZXppZXJDdXJ2ZVRvKHIqLjcsciouMjIsciouMixyKi4yOCwwLDApO2N0eC5jbG9zZVBhdGgoKTt9CiAgICBlbHNlIGlmKHNwLnNoPT09J2NyeXMnKXtjdHgubW92ZVRvKHIqLjA4LDApO2N0eC5saW5lVG8ociouMzgsLXIqLjIyKTtjdHgubGluZVRvKHIqLjgyLDApO2N0eC5saW5lVG8ociouMzgsciouMjIpO2N0eC5jbG9zZVBhdGgoKTt9CiAgICBlbHNlIGlmKHNwLnNoPT09J2JsYWQnKXtjdHgubW92ZVRvKDAsLXIqLjA1KTtjdHgubGluZVRvKHIqLjc4LC1yKi4xMik7Y3R4LmxpbmVUbyhyKi44MiwwKTtjdHgubGluZVRvKHIqLjc4LHIqLjEyKTtjdHgubGluZVRvKDAsciouMDUpO2N0eC5jbG9zZVBhdGgoKTt9CiAgICBlbHNle2N0eC5lbGxpcHNlKHIqLjQwLDAsciouNDAsciouMjIsMCwwLE1hdGguUEkqMik7fQogICAgY3R4LmZpbGwoKTtjdHguc3Ryb2tlU3R5bGU9c3AucFswXSsnOTknO2N0eC5saW5lV2lkdGg9MS4yO2N0eC5zdHJva2UoKTsKICAgIGlmKHNwZD4wLjIpe2N0eC5nbG9iYWxBbHBoYT1NYXRoLm1pbigoc3BkLS4yKSouNCwuNDUpO2N0eC5maWxsU3R5bGU9c3Aucm07Y3R4LmZpbGwoKTtjdHguZ2xvYmFsQWxwaGE9MTt9CiAgICBjdHgucmVzdG9yZSgpOwogIH0KICBjdHguYmVnaW5QYXRoKCk7Y3R4LmFyYyhjeCxjeSxyLDAsTWF0aC5QSSoyKTtjdHguc3Ryb2tlU3R5bGU9c3Aucm0rKHNwZD4uMjU/J0JCJzonMzMnKTtjdHgubGluZVdpZHRoPXNwZD4uND8yLjU6MS41O2N0eC5zdHJva2UoKTsKICBpZihzcC5wdCYmc3BkPjAuMyl7dmFyIHBjPU1hdGguZmxvb3Ioc3BkKjUpO2Zvcih2YXIgcGk9MDtwaTxwYztwaSsrKXt2YXIgcGE9YW5nbGUqMy41K3BpKjIuMCtwZXJmb3JtYW5jZS5ub3coKSouMDAxNTt2YXIgcHI9ciooLjY1K01hdGgucmFuZG9tKCkqLjI4KTt2YXIgcHg9Y3grTWF0aC5jb3MocGEpKnByLHB5PWN5K01hdGguc2luKHBhKSpwcjtjdHguYmVnaW5QYXRoKCk7Y3R4LmFyYyhweCxweSwxK01hdGgucmFuZG9tKCkqMS41LDAsTWF0aC5QSSoyKTtjdHguZmlsbFN0eWxlPXNwLnBbcGklc3AucC5sZW5ndGhdO2N0eC5nbG9iYWxBbHBoYT0uNjUrTWF0aC5yYW5kb20oKSouMztjdHguZmlsbCgpO2N0eC5nbG9iYWxBbHBoYT0xO319CiAgdmFyIGhnPWN0eC5jcmVhdGVSYWRpYWxHcmFkaWVudChjeC1yKi4wNCxjeS1yKi4wNCwxLGN4LGN5LHIqLjIwKTtoZy5hZGRDb2xvclN0b3AoMCwnI2ZmZmZmZicpO2hnLmFkZENvbG9yU3RvcCguNCxzcC5wWzBdKTtoZy5hZGRDb2xvclN0b3AoMSxzcC5oYik7Y3R4LmJlZ2luUGF0aCgpO2N0eC5hcmMoY3gsY3ksciouMTksMCxNYXRoLlBJKjIpO2N0eC5maWxsU3R5bGU9aGc7Y3R4LmZpbGwoKTtjdHguYmVnaW5QYXRoKCk7Y3R4LmFyYyhjeCxjeSxyKi4wNywwLE1hdGguUEkqMik7Y3R4LmZpbGxTdHlsZT0ncmdiYSgyNTUsMjU1LDI1NSwwLjQpJztjdHguZmlsbCgpOwogIHZhciByZT1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncl8nK3NwLmlkKTtpZihyZSl7dmFyIHJ2PU1hdGguYWJzKHZlbCo2MC8oTWF0aC5QSSoyKSo2MCk7aWYocnY+OCl7cmUudGV4dENvbnRlbnQ9TWF0aC5yb3VuZChydikudG9Mb2NhbGVTdHJpbmcoKSsnIFJQTSc7cmUuc3R5bGUuY29sb3I9cnY+OTAwMD8nI0ZGMDAwMCc6cnY+NDAwMD8nI0ZGODgwMCc6cnY+MTIwMD8nI0ZGRDcwMCc6c3AuZ3c7fWVsc2V7cmUudGV4dENvbnRlbnQ9c3AubnVrZT8nVEFQIFRPIElHTklURSc6J1x1MjIxZSBFVEVSTkFMJztyZS5zdHlsZS5jb2xvcj0ncmdiYSgyNTUsMjU1LDI1NSwwLjI1KSc7fX19CnZhciBBRj0wLjk5OTk5MixORj0wLjk5ODU7CmZ1bmN0aW9uIGxvb3AoKXsKICBkUygpOwogIERGLmZvckVhY2goZnVuY3Rpb24oc3Ape3ZhciBzPVNUW3NwLmlkXTtpZighcy5kZyl7cy52Kj1zcC5udWtlP05GOkFGO2lmKE1hdGguYWJzKHMudik8c3AuYnYpcy52PXNwLm51a2U/MDpzcC5idjtzLmErPXMudjt9ZHJhdyhzcCxzLmEscy52KTt9KTsKICByZXF1ZXN0QW5pbWF0aW9uRnJhbWUobG9vcCk7Cn0KbG9vcCgpOwo8L3NjcmlwdD4KPC9ib2R5PjwvaHRtbD4="
    components.html(_b64.b64decode(_SPINNER_B64).decode("utf-8"), height=380)
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

if st.session_state.get("first_session", False):
    st.session_state.first_session = False
    st.session_state.spins_left = max(st.session_state.get("spins_left",0), 1)
    st.session_state.spinner_available = True

CARDBG   = "#1a1a1a" if is_light(BG) else "#f0f0f0"
CARDTEXT = "#ffffff" if is_light(BG) else "#000000"
_ch = C.lstrip('#')
try: CR, CG, CB = int(_ch[0:2],16), int(_ch[2:4],16), int(_ch[4:6],16)
except: CR, CG, CB = 255, 215, 0

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html,body,[data-testid="stAppViewContainer"]{{background:{BG}!important;color:{TEXT}!important;font-family:'Space Mono',monospace;}}
[data-testid="stHeader"],[data-testid="stToolbar"]{{background:transparent!important;}}
[data-testid="stSidebar"]{{background:#111111!important;}}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] div,[data-testid="stSidebar"] span,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] b,[data-testid="stSidebar"] strong,[data-testid="stSidebar"] li,[data-testid="stSidebar"] a {{color:#ffffff!important;}}
[data-testid="stSidebar"] div.stButton>button{{border:2px solid {C}!important;background:#1a1a1a!important;color:#ffffff!important;font-family:'Bebas Neue',sans-serif!important;font-size:16px!important;letter-spacing:2px!important;padding:10px 16px!important;border-radius:10px!important;animation:none!important;width:100%!important;margin-bottom:6px!important;}}
#MainMenu,footer{{visibility:hidden;}}
input,textarea{{background:#ffffff!important;color:#000000!important;caret-color:#000000!important;border:2px solid {C}!important;border-radius:10px!important;font-family:'Space Mono',monospace!important;font-size:14px!important;padding:10px 14px!important;}}
input::placeholder,textarea::placeholder{{color:#666666!important;}}
input:focus,textarea:focus{{border-color:{C}!important;box-shadow:0 0 15px rgba(255,215,0,0.2)!important;outline:none!important;}}
label,.stTextInput label,.stSelectbox label,.stTextArea label,.stFileUploader label{{color:{TEXT}!important;font-family:'Space Mono',monospace!important;font-size:11px!important;letter-spacing:2px!important;}}
@keyframes titan-pulse{{0%{{box-shadow:0 0 20px {C},inset 0 0 10px {C};border-color:{C};}}50%{{box-shadow:0 0 80px {C},inset 0 0 40px {C};border-color:#ffffff;}}100%{{box-shadow:0 0 20px {C},inset 0 0 10px {C};border-color:{C};}}}}
div.stButton>button{{border:6px solid {C}!important;background:#000000!important;color:#ffffff!important;font-family:'Bebas Neue',sans-serif!important;font-size:28px!important;letter-spacing:4px!important;padding:50px 30px!important;border-radius:40px!important;animation:titan-pulse 2.5s infinite ease-in-out!important;width:100%;text-transform:uppercase;transition:transform 0.3s;margin-bottom:20px;}}
div.stButton>button:hover{{transform:scale(1.02);}}
.metric-card,.shop-card,.ach-card,.monster-card,.secret-card {{background:#111111!important;border:2px solid {C}!important;border-radius:14px!important;padding:18px!important;margin-bottom:12px!important;color:#ffffff!important;}}
.metric-card *,.shop-card *,.ach-card *,.monster-card *,.secret-card * {{color:#ffffff!important;}}
@keyframes blink{{0%,100%{{opacity:0.4}}50%{{opacity:1}}}}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>🌌 INFINITEVERSE HUB</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>CHAMPION:</b> {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>UNIVERSE:</b> {st.session_state.user_theme}</p>", unsafe_allow_html=True)
    mode_badge = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}.get(MODE,"⚡ CHILL")
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>MODE:</b> {mode_badge}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>RANK:</b> {st.session_state.sub_tier.upper()}</p>", unsafe_allow_html=True)
    st.markdown(f"""<div class='metric-card'><div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C}'>{st.session_state.gold:.1f}</div><div style='font-size:10px;color:#ffffff;letter-spacing:2px'>{currency.upper()}</div><div style='font-size:11px;color:#ffffff;margin-top:4px'>XP: {st.session_state.xp} · LVL {st.session_state.level}</div></div>""", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<p style='color:#ffffff;font-weight:bold'>👑 ELITE CODE</p>", unsafe_allow_html=True)
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "4RJ1TV51Z" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3; st.success("💀 ELITE STATUS SECURED! 3× everything activated."); st.balloons(); time.sleep(1); st.rerun()
    if code == "1TR5LG89D" and st.session_state.sub_tier not in ("Elite","Premium"):
        st.session_state.sub_tier = "Premium"; st.session_state.sub_multiplier = 2; st.success("⚡ PREMIUM STATUS SECURED! 2× everything activated."); st.balloons(); time.sleep(1); st.rerun()
    st.write("---")
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
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🎨 BACKGROUND</p>", unsafe_allow_html=True)
    new_bg = st.color_picker("", value=st.session_state.get("bg_color","#ffffff"), key="bg_picker", label_visibility="collapsed")
    if new_bg != st.session_state.get("bg_color","#ffffff"): st.session_state.bg_color = new_bg; st.rerun()
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🌈 THEME COLOR</p>", unsafe_allow_html=True)
    new_tc = st.color_picker("", value=st.session_state.vibe_color, key="theme_picker", label_visibility="collapsed")
    if new_tc != st.session_state.vibe_color: st.session_state.vibe_color = new_tc; st.rerun()
    st.write("---")
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🌐 SWITCH UNIVERSE</p>", unsafe_allow_html=True)
    new_theme = st.text_input("New universe:", placeholder="Try anything...", key="switch_theme")
    if st.button("🔄 WARP", key="warp_btn"):
        if new_theme.strip():
            check = filter_universe_input(new_theme.strip())
            if not check["safe"]: st.error(f"⚠️ {check['reason']}")
            else:
                with st.spinner("Warping..."):
                    result = resolve_universe(check["cleaned"])
                if not result["safe"]: st.error(f"⚠️ {result['reason']}")
                else:
                    st.session_state.world_data = result["data"]; st.session_state.vibe_color = result["data"].get("color","#FFD700"); st.session_state.user_theme = check["cleaned"]; st.rerun()
    st.write("---")
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🚨 RESET</p>", unsafe_allow_html=True)
    reset_input = st.text_input("Type RESET to confirm:", key="reset_confirm_input", placeholder="RESET")
    if st.button("🚨 RESET ALL", key="reset_btn"):
        if reset_input.strip().upper() == "RESET": st.session_state.clear(); st.rerun()
        else: st.error("Type RESET first.")


# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENT CHECK + SECRET REVEAL + HEADER
# ─────────────────────────────────────────────────────────────────────────────
new_ach = check_achievements(st.session_state)
for ach in new_ach:
    st.toast(f"🏆 ACHIEVEMENT UNLOCKED: {ach['name']}", icon="🏆")

if st.session_state.show_secret:
    st.markdown(f"""<div class='secret-card'><div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:{C};letter-spacing:3px;margin-bottom:10px'>🔮 UNIVERSE SECRET UNLOCKED</div>{st.session_state.show_secret}</div>""", unsafe_allow_html=True)
    if st.button("🔮 SICK. CLOSE THIS.", key="close_secret"):
        st.session_state.show_secret = None; st.rerun()
    st.stop()

st.markdown(f"""<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>{st.session_state.user_theme.upper()}</h1><p style='text-align:center;font-size:15px;color:#ffffff;margin-top:4px'>{wd.get("description","A realm of infinite power.")}</p>""", unsafe_allow_html=True)
st.markdown("---")

view = st.session_state.view

# ── OPENING STORY (shown once on first login) ──
if not st.session_state.get("opening_story_shown", True):
    theme_now = st.session_state.user_theme or "Infinite Power"
    client_os = get_claude_client()
    if client_os:
        try:
            resp_os = client_os.messages.create(model="claude-sonnet-4-5", max_tokens=220, messages=[{"role":"user","content":f'You are the most gripping storyteller alive. Write the OPENING of an epic story set in the universe of: "{theme_now}". This is chapter 0 — the very beginning.\n\nRules:\n- 3 sentences MAX. Short. Punchy. Cinematic.\n- Reference the specific universe (characters, world, lore)\n- End on a CLIFFHANGER that makes them physically unable to stop reading\n- No titles, no formatting. Raw story text only.'}])
            opening_txt = resp_os.content[0].text.strip()
        except:
            opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened — something that was never meant to be found. And somehow... it knows your name."
    else:
        opening_txt = f"The {theme_now} universe shudders. Something ancient has awakened — something that was never meant to be found. And somehow... it knows your name."
    st.session_state.opening_story_shown = True
    if not st.session_state.story_log:
        st.session_state.story_log = []
    st.session_state.story_log.insert(0, opening_txt)
    st.markdown(f"""<div style='border:2px solid {C};border-radius:18px;padding:28px 32px;background:linear-gradient(135deg,#0a001a,#001a0a,#0a001a);text-align:center;margin:16px 0;animation:storyappear 0.8s ease-out;box-shadow:0 0 40px {C}55;'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:13px;letter-spacing:5px;color:{C};margin-bottom:14px'>⚡ CHAPTER 0 — THE BEGINNING ⚡</div>
        <div style='font-family:Space Mono,monospace;font-size:16px;color:#ffffff;line-height:1.9;font-style:italic'>{opening_txt}</div>
        <div style='margin-top:16px;font-family:Orbitron,monospace;font-size:10px;color:#FF4488;letter-spacing:3px;animation:blink 1.2s ease-in-out infinite'>▼ TO BE CONTINUED... COMPLETE A MISSION ▼</div>
    </div><style>@keyframes storyappear{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}</style>""", unsafe_allow_html=True)

# ── STREAK DANGER ──
if st.session_state.get("study_streak", 0) >= 2:
    today_str = _dt.date.today().isoformat()
    last_str  = st.session_state.get("last_active_date")
    if last_str and last_str != today_str:
        yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
        if last_str == yesterday:
            st.markdown(streak_danger_html(st.session_state.study_streak, C), unsafe_allow_html=True)

# ── LOOT BOX REVEAL ──
if st.session_state.get("loot_pending") and st.session_state.get("loot_item"):
    item = st.session_state.loot_item
    st.markdown(loot_box_html(item["name"], item["rarity"], item.get("color","#FFD700")), unsafe_allow_html=True)
    time.sleep(0.1)
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        if st.button("⚡ CLAIM IT", key="claim_loot"):
            st.session_state.loot_pending = False; st.session_state.loot_item = None; st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# BATTLE SCREEN — Universal HTML5 Game Engine (ORIGINAL — PRESERVED)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("battle_state") == "ready" or view == "battle":
    st.session_state.view = "battle"
    theme    = st.session_state.user_theme or "Infinite Power"
    tier_now = st.session_state.get("sub_tier","Free")

    if st.session_state.get("battle_box_pending") and st.session_state.get("battle_box_item"):
        item = st.session_state.battle_box_item
        rc2  = {"Common":"#888888","Rare":"#4488FF","Epic":"#AA44FF","Legendary":"#FFD700"}.get(item["rarity"],"#FFD700")
        st.markdown(f"""<div style='border:3px solid {rc2};border-radius:20px;padding:32px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);text-align:center;margin:16px 0;box-shadow:0 0 50px {rc2}66;animation:lootpulse 0.5s ease 4;'>
            <div style='font-size:72px;animation:lootbounce 0.4s infinite alternate'>🎁</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{rc2};letter-spacing:6px;margin:12px 0'>{item["rarity"].upper()} BATTLE BOX</div>
            <div style='font-size:20px;color:#ffffff;font-family:Space Mono,monospace'>{item["name"]}</div></div>
        <style>@keyframes lootpulse{{0%{{box-shadow:0 0 20px {rc2}44}}50%{{box-shadow:0 0 70px {rc2}cc}}100%{{box-shadow:0 0 20px {rc2}44}}}}@keyframes lootbounce{{from{{transform:scale(1) rotate(-5deg)}}to{{transform:scale(1.2) rotate(5deg)}}}}</style>""", unsafe_allow_html=True)
        if st.button("⚡ CLAIM BATTLE BOX", key="claim_battle_box"):
            st.session_state.battle_box_pending = False; st.session_state.battle_box_item = None; st.session_state.battle_state = None; st.session_state.view = "main"; st.rerun()
        st.stop()

    js_result = st.session_state.get("js_battle_result")
    if js_result == "win":
        st.session_state.js_battle_result = None
        st.session_state.battle_wins = st.session_state.get("battle_wins",0) + 1
        st.session_state.battles_fought = st.session_state.get("battles_fought",0) + 1
        xp_earn = 60; gold_earn = 25
        st.session_state.xp += xp_earn; st.session_state.gold += gold_earn
        box_pool = {"Free":[("Common","#888888","+5 Shards","Common"),("Rare","#4488FF","+15 Shards","Rare"),("Epic","#AA44FF","+30 Shards + Egg","Epic")],"Premium":[("Rare","#4488FF","+25 Shards + Egg","Rare"),("Epic","#AA44FF","+50 Shards","Epic"),("Legendary","#FFD700","JACKPOT: +100 Shards + 3 Eggs","Legendary")],"Elite":[("Epic","#AA44FF","+75 Shards + 2 Eggs","Epic"),("Legendary","#FFD700","+150 Shards + Streak Shield","Legendary"),("Legendary","#FFD700","ULTRA JACKPOT: +300 Shards","Legendary")]}
        pool = box_pool.get(tier_now, box_pool["Free"]); pick = random.choice(pool)
        bitem = {"rarity": pick[0], "color": pick[1], "name": pick[2]}
        if "Egg" in pick[2]: st.session_state.incubator_eggs += (3 if "3 Eggs" in pick[2] else 2 if "2 Eggs" in pick[2] else 1)
        if "Shield" in pick[2]: st.session_state.streak_shield = True
        bonus_gold = 5 if "5" in pick[2] else 15 if "15" in pick[2] else 25 if "25" in pick[2] else 50 if "50" in pick[2] else 75 if "75" in pick[2] else 100 if "100" in pick[2] else 150 if "150" in pick[2] else 300 if "300" in pick[2] else 30
        st.session_state.gold += bonus_gold
        st.session_state.battle_box_pending = True; st.session_state.battle_box_item = bitem
        st.session_state.spinner_available = True
        st.session_state.spins_left += (1 if tier_now=="Free" else 3 if tier_now=="Premium" else 6)
        st.rerun()

    cfg = st.session_state.get("battle_config")
    if cfg is None or cfg.get("universe") != theme:
        client2 = get_claude_client()
        with st.spinner(f"⚔️ Generating {theme} battle..."):
            cfg = generate_battle_config(theme, "Mathematics", tier_now, client2)
        st.session_state.battle_config = cfg

    if not st.session_state.get("battle_subject_chosen"):
        st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>⚔️ {theme.upper()} BATTLE</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#aaa;font-family:Space Mono,monospace;font-size:12px'>Universe: <b style='color:{C}'>{theme}</b> · Mode: <b style='color:{C}'>{cfg.get('mode','?')}</b> · Arena: <b>{cfg.get('arena_name','?')}</b></p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#fff;font-size:14px;font-family:Space Mono,monospace'>Pick your subject — correct answers = power attacks. Wrong = the enemy hits back.</p>", unsafe_allow_html=True)

        # Premium/Elite: free text subject input
        if tier_now in ("Premium", "Elite"):
            st.markdown(f"<p style='text-align:center;color:{C};font-family:Bebas Neue,sans-serif;font-size:16px;letter-spacing:3px'>👑 {tier_now.upper()} PERK: TYPE ANY SUBJECT</p>", unsafe_allow_html=True)
            _, custom_col, _ = st.columns([1, 2, 1])
            with custom_col:
                custom_subject = st.text_input("Type your subject:", placeholder="e.g. Calculus 1 Honors, AP Biology, Organic Chemistry...", key="custom_subject_input")
                if st.button("⚔️ START BATTLE WITH CUSTOM SUBJECT", key="custom_subj_go"):
                    if custom_subject.strip():
                        with st.spinner(f"⚔️ Generating {custom_subject.strip()} questions..."):
                            cfg = generate_battle_config(theme, custom_subject.strip(), tier_now, get_claude_client())
                        st.session_state.battle_config = cfg; st.session_state.battle_subject_chosen = True; st.rerun()
                    else:
                        st.error("Type a subject first!")
            st.markdown("<p style='text-align:center;color:#888;font-size:11px;margin:12px 0'>— or pick from presets below —</p>", unsafe_allow_html=True)

        subjects = ["Mathematics","Science","History","English","Geography","Biology","Chemistry","Physics","Economics","Computer Science","Psychology","Art & Music"]
        cols2 = st.columns(4)
        for i, sub in enumerate(subjects):
            with cols2[i % 4]:
                if st.button(sub, key=f"subj_{i}"):
                    with st.spinner(f"⚔️ Generating {sub} questions..."):
                        cfg = generate_battle_config(theme, sub, tier_now, get_claude_client())
                    st.session_state.battle_config = cfg; st.session_state.battle_subject_chosen = True; st.rerun()
        st.markdown("---")
        if st.button("⬅ Back", key="battle_back"):
            st.session_state.view = "main"; st.session_state.battle_state = None; st.rerun()
        st.stop()

    cfg_clean = {k: v for k,v in cfg.items() if k != "client"}
    game_html = _build_game_html(cfg_clean, C)
    st.markdown(f"""<div style='border:2px solid {C}33;border-radius:12px;overflow:hidden;margin:8px 0;'><div style='background:rgba(0,0,0,0.8);padding:6px 16px;font-family:Bebas Neue,sans-serif;font-size:13px;color:{C};letter-spacing:3px;display:flex;justify-content:space-between;'><span>⚔️ {(cfg.get("arena_name","BATTLE")).upper()}</span><span style='color:#888;font-size:10px'>ANSWER CORRECTLY TO ATTACK · 3 WRONG = DEFEAT</span></div></div>""", unsafe_allow_html=True)
    components.html(game_html, height=520, scrolling=False)
    st.markdown(f"""<div style='background:linear-gradient(90deg,#0a0020,#1a0040,#0a0020);border:1px solid {C}44;border-radius:10px;padding:10px 20px;text-align:center;margin:8px 0;'><span style='font-family:Bebas Neue,sans-serif;font-size:16px;color:{C};letter-spacing:3px'>🚀 3D UNIVERSE MODE COMING SOON — The full immersive infinite experience</span></div>""", unsafe_allow_html=True)
    col_r, col_l = st.columns(2)
    with col_r:
        if st.button("🔄 New Battle", key="new_battle"):
            st.session_state.battle_config = None; st.session_state.battle_subject_chosen = False; st.rerun()
    with col_l:
        if st.button("⬅ Back to Hub", key="back_hub"):
            st.session_state.view = "main"; st.session_state.battle_state = None; st.session_state.battle_subject_chosen = False; st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# MISSION HUB — THE ADDICTION ENGINE (NEW v10)
# ─────────────────────────────────────────────────────────────────────────────
if view == "main":
    streak_now = st.session_state.get("study_streak", 0)
    xp_now = st.session_state.get("xp", 0)
    level_now = st.session_state.get("level", 1)
    gold_now = st.session_state.get("gold", 0)
    xp_pct = rig_xp_bar(xp_now, level_now)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='metric-card' style='text-align:center'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>{gold_now:.1f}</div><div style='font-size:10px;letter-spacing:2px;color:#ffffff'>{currency.upper()}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card' style='text-align:center'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>LVL {level_now}</div><div style='font-size:10px;letter-spacing:2px;color:#ffffff'>CHAMPION RANK</div></div>""", unsafe_allow_html=True)
    with col3:
        streak_color = "#FF4444" if streak_now == 0 else ("#FFD700" if streak_now >= 7 else C)
        st.markdown(f"""<div class='metric-card' style='text-align:center'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{streak_color}'>🔥 {streak_now}</div><div style='font-size:10px;letter-spacing:2px;color:#ffffff'>DAY STREAK</div></div>""", unsafe_allow_html=True)
    with col4:
        missions_done = st.session_state.get("total_missions", 0)
        st.markdown(f"""<div class='metric-card' style='text-align:center'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>{missions_done}</div><div style='font-size:10px;letter-spacing:2px;color:#ffffff'>MISSIONS DONE</div></div>""", unsafe_allow_html=True)

    xp_display = int(xp_pct * 100)
    bar_filled = int(xp_pct * 30); bar_empty = 30 - bar_filled
    xp_bar_str = "█" * bar_filled + "░" * bar_empty
    next_level = level_now + 1
    xp_msg = "🔥 SO CLOSE! One more mission and you level up!" if xp_pct > 0.9 else "⚡ Keep grinding — you're almost there." if xp_pct > 0.7 else "💪 Every mission gets you closer."
    st.markdown(f"""<div style='background:#111;border:1px solid {C}44;border-radius:12px;padding:14px 20px;margin:8px 0 20px'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'><span style='font-family:Bebas Neue,sans-serif;font-size:14px;color:{C};letter-spacing:2px'>LEVEL {level_now} → LEVEL {next_level}</span><span style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff'>{xp_display}%</span></div><div style='font-family:Space Mono,monospace;font-size:11px;color:{C};letter-spacing:1px'>{xp_bar_str}</div><div style='font-size:10px;color:#888;margin-top:4px;font-family:Space Mono,monospace'>{xp_msg}</div></div>""", unsafe_allow_html=True)

    streak_msg = get_streak_urgency(st.session_state.get("study_streak", 0), st.session_state.get("last_active_date", ""))
    if streak_msg:
        st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;font-size:12px;color:#FF8888'>{streak_msg}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tier = st.session_state.sub_tier; mult = st.session_state.sub_multiplier; base = 5.0 * mult
    shield = st.session_state.get("shield_bought", False); boost = st.session_state.get("booster_bought", False)
    timer = st.session_state.get("micro_timer_seconds", 30)
    reward_min = round(base * 0.3, 1); reward_max = round(base * 20, 1)

    st.markdown(f"""<div style='text-align:center;margin:10px 0 8px'><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;letter-spacing:2px'>POTENTIAL REWARD: <span style='color:{C};font-family:Bebas Neue,sans-serif;font-size:18px'>{reward_min} — {reward_max}</span> {currency}{"<br>🛡️ SHIELD ACTIVE" if shield else ""}{"<br>🚀 3× BOOSTER ACTIVE" if boost else ""}</div></div>""", unsafe_allow_html=True)

    _, mcol, _ = st.columns([1, 3, 1])
    with mcol:
        if st.button(f"⚡ START {timer}-SECOND MISSION ⚡", key="start_mission"):
            st.session_state.needs_verification = True; st.session_state.pending_gold = base
            timer_placeholder = st.empty(); progress_bar = st.progress(0)
            for sec in range(timer, 0, -1):
                pct = (timer - sec) / timer
                if sec <= 5:
                    timer_placeholder.markdown(f"""<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:90px;color:#FF2222;text-shadow:0 0 40px #FF2222;animation:blink 0.5s infinite'>{sec}</div>""", unsafe_allow_html=True)
                elif sec <= 10:
                    timer_placeholder.markdown(f"""<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:80px;color:#FF8800;text-shadow:0 0 30px #FF8800'>{sec}</div>""", unsafe_allow_html=True)
                else:
                    timer_placeholder.markdown(f"""<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:72px;color:{C};text-shadow:0 0 20px {C}'>{sec}</div><div style='text-align:center;font-family:Space Mono,monospace;font-size:12px;color:#ffffff;margin-top:8px'>STUDY NOW. PROVE IT. GET PAID.</div>""", unsafe_allow_html=True)
                progress_bar.progress(pct); time.sleep(1)
            timer_placeholder.markdown(f"""<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:60px;color:{C};text-shadow:0 0 50px {C};animation:titan-pulse 1s infinite'>⚡ TIME'S UP ⚡</div><div style='text-align:center;font-family:Space Mono,monospace;font-size:14px;color:#ffffff;margin-top:12px'>Upload your proof below to claim your reward.</div>""", unsafe_allow_html=True)
            progress_bar.progress(1.0); time.sleep(0.5); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    _, tcol, _ = st.columns([1, 2, 1])
    with tcol:
        timer_options = [30, 60, 120, 300]; timer_labels = ["30s ⚡", "60s 🔥", "2min 💪", "5min 💀"]
        tcols = st.columns(len(timer_options))
        for i, (t_val, t_label) in enumerate(zip(timer_options, timer_labels)):
            with tcols[i]:
                if st.button(t_label, key=f"timer_{t_val}"):
                    st.session_state.micro_timer_seconds = t_val; st.rerun()

    st.markdown("---")
    st.markdown(f"""<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:18px;color:{C};letter-spacing:4px;margin-bottom:16px'>⚡ AVAILABLE NOW</div>""", unsafe_allow_html=True)
    act_count = 4 if MODE == "obsessed" else 3 if MODE == "grinder" else 2
    act_cols = st.columns(act_count)
    with act_cols[0]:
        spins = st.session_state.get("spins_left", 0)
        if st.button(f"🎰 SPIN ({spins})", key="quick_spin"): st.session_state.view = "spinner"; st.rerun()
    with act_cols[1]:
        eggs = st.session_state.get("incubator_eggs", 0)
        if st.button(f"🥚 HATCH ({eggs})", key="quick_hatch"): st.session_state.view = "incubator"; st.rerun()
    if MODE in ("grinder","obsessed") and act_count >= 3:
        with act_cols[2]:
            if st.button("⚔️ BATTLE", key="quick_battle"): st.session_state.view = "battle"; st.rerun()
    if MODE == "obsessed" and act_count >= 4:
        with act_cols[3]:
            ch = st.session_state.get("story_chapter", 0)
            if st.button(f"📖 CH.{ch}", key="quick_story"): st.session_state.view = "story"; st.rerun()

    st.markdown("---")

    ab_col1, ab_col2 = st.columns(2)
    with ab_col1:
        shield_owned = st.session_state.get("shield_bought", False)
        st.markdown(f"""<div class='metric-card' style='border-color:{C if shield_owned else "#333"};opacity:{"1.0" if shield_owned else "0.4"}'><div style='font-size:28px'>🛡️</div><div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:2px'>{wd.get("shield_name","Shield")}</div><div style='font-size:11px;color:#ffffff;margin-top:4px'>{wd.get("shield_flavor","Protects you from harm.")}</div><div style='font-size:10px;color:#888;margin-top:6px;font-family:Space Mono,monospace'>{"✅ ACTIVE — Negates any debt" if shield_owned else "❌ NOT OWNED — Buy in shop or win from spinner"}</div></div>""", unsafe_allow_html=True)
    with ab_col2:
        booster_owned = st.session_state.get("booster_bought", False)
        st.markdown(f"""<div class='metric-card' style='border-color:{C if booster_owned else "#333"};opacity:{"1.0" if booster_owned else "0.4"}'><div style='font-size:28px'>🚀</div><div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:2px'>{wd.get("booster_name","Booster")}</div><div style='font-size:11px;color:#ffffff;margin-top:4px'>{wd.get("booster_flavor","Moves at impossible speed.")}</div><div style='font-size:10px;color:#888;margin-top:6px;font-family:Space Mono,monospace'>{"✅ ACTIVE — 3× multiplier on all rewards" if booster_owned else "❌ NOT OWNED — Buy in shop or win from spinner"}</div></div>""", unsafe_allow_html=True)

    if st.session_state.story_log:
        latest = st.session_state.story_log[-1]
        teaser = latest[:180] + "..." if len(latest) > 180 else latest
        ch_num = st.session_state.story_chapter
        st.markdown(f"""<div style='border:1px solid {C}33;border-radius:14px;padding:20px;background:linear-gradient(135deg,rgba(0,0,0,0.4),rgba(0,0,0,0.2));margin:16px 0'><div style='font-family:Bebas Neue,sans-serif;font-size:13px;color:{C};letter-spacing:3px;margin-bottom:8px'>📖 CHAPTER {ch_num} — LATEST</div><div style='font-family:Space Mono,monospace;font-size:13px;color:#ffffff;line-height:1.7;font-style:italic'>{teaser}</div><div style='margin-top:10px;font-size:11px;color:#FF4488;font-family:Space Mono,monospace;animation:blink 1.5s ease-in-out infinite'>▸ Complete a mission to unlock the next chapter</div></div>""", unsafe_allow_html=True)

    monsters = st.session_state.get("hatched_monsters", [])
    if monsters:
        rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
        recent = monsters[-5:]
        monster_pills = " ".join([f"<span style='display:inline-block;padding:4px 12px;border-radius:99px;font-size:11px;border:1px solid {rarity_colors.get(m['rarity'],'#888')};color:{rarity_colors.get(m['rarity'],'#fff')};margin:2px;font-family:Space Mono,monospace'>{m['name']}</span>" for m in recent])
        st.markdown(f"""<div style='text-align:center;margin:8px 0'><div style='font-family:Bebas Neue,sans-serif;font-size:13px;color:{C};letter-spacing:3px;margin-bottom:8px'>YOUR COLLECTION ({len(monsters)} creatures)</div>{monster_pills}</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ALL REMAINING VIEWS (ORIGINAL — PRESERVED + ENHANCED)
# ─────────────────────────────────────────────────────────────────────────────

# ── SHOP ──
elif view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🛒 TITAN SUPPLY SHOP</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:14px;font-family:Space Mono,monospace'>Spend your {currency} on real school supplies. Study harder → earn more → buy the tools that make you unstoppable.</p>", unsafe_allow_html=True)
    gold_now = st.session_state.gold
    st.markdown(f"<p style='text-align:center;color:{C};font-size:20px;font-family:Bebas Neue,sans-serif'>Your Balance: {gold_now:.1f} {currency}</p>", unsafe_allow_html=True)
    shop_items = [
        {"name":"📓 Notebook","desc":"College-ruled. Your future notes. Your future power.","price":50,"real":"~$3 Amazon gift card"},
        {"name":"✏️ Pencil Pack","desc":"12 pencils. The weapon of every champion.","price":30,"real":"~$2 Amazon gift card"},
        {"name":"📐 Calculator","desc":"Scientific calculator. Math becomes your superpower.","price":200,"real":"~$12 Amazon gift card"},
        {"name":"📚 Textbook Voucher","desc":"Any textbook up to $25. Knowledge is the ultimate boss.","price":500,"real":"$25 Amazon gift card"},
        {"name":"🖊️ Highlighters","desc":"5-color set. Color-code your way to genius.","price":40,"real":"~$3 Amazon gift card"},
        {"name":"📋 Planner","desc":"Weekly planner. The organized mind conquers all.","price":80,"real":"~$5 Amazon gift card"},
        {"name":"🎒 Backpack","desc":"The legendary carry. For the ultimate grinder.","price":800,"real":"$50 Amazon gift card"},
        {"name":"💻 Study Headphones","desc":"Block out the world. Enter flow state.","price":600,"real":"$40 Amazon gift card"},
    ]
    cols = st.columns(2)
    for i, item in enumerate(shop_items):
        with cols[i % 2]:
            can_buy = gold_now >= item["price"]
            border_col = C if can_buy else "#444444"
            st.markdown(f"""<div style='border:2px solid {border_col};border-radius:14px;padding:16px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);margin:8px 0;'><div style='font-size:22px;font-family:Bebas Neue,sans-serif;color:{C if can_buy else "#888"};letter-spacing:2px'>{item['name']}</div><div style='font-size:12px;color:#cccccc;font-family:Space Mono,monospace;margin:6px 0'>{item['desc']}</div><div style='font-size:14px;color:{C};font-family:Bebas Neue,sans-serif'>{item['price']} {currency}</div><div style='font-size:10px;color:#888;font-family:Space Mono,monospace'>Real value: {item['real']}</div></div>""", unsafe_allow_html=True)
            if can_buy:
                if st.button(f"BUY {item['name']}", key=f"buy_{i}"):
                    st.session_state.gold -= item["price"]; st.balloons()
                    st.success(f"✅ {item['name']} purchased! Redeem = email us your username."); st.rerun()
            else:
                st.markdown(f"<p style='color:#666;font-size:11px;font-family:Space Mono'>Need {item['price']-gold_now:.0f} more {currency}</p>", unsafe_allow_html=True)

# ── STORY ──
elif view == "story":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 YOUR UNIVERSE STORYLINE</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>Universe: <b style='color:{C}'>{st.session_state.user_theme}</b> · Chapter {st.session_state.story_chapter}</p>", unsafe_allow_html=True)
    if not st.session_state.story_log:
        st.markdown("<div style='text-align:center;padding:40px;color:#888;font-family:Space Mono,monospace'>Complete your first mission to begin the story...</div>", unsafe_allow_html=True)
    else:
        for i, chapter_text in enumerate(st.session_state.story_log):
            is_last = (i == len(st.session_state.story_log) - 1)
            is_twist = (i > 0 and (i+1) % 5 == 0)
            bg = "linear-gradient(135deg,#1a0a2e,#0a1a0e)" if not is_twist else "linear-gradient(135deg,#2e0a0a,#1a0a2e)"
            border = C if is_last else ("#FF2244" if is_twist else "#333")
            label = f"⚡ CHAPTER {i+1}" + (" — 🌀 PLOT TWIST" if is_twist else "")
            st.markdown(f"""<div style='border:2px solid {border};border-radius:14px;padding:20px;background:{bg};margin:10px 0;{"box-shadow:0 0 20px "+C+"44;" if is_last else ""}'><div style='font-size:13px;font-family:Bebas Neue,sans-serif;color:{C if is_last else "#888"};letter-spacing:3px;margin-bottom:10px'>{label}</div><div style='font-size:15px;color:#ffffff;font-family:Space Mono,monospace;line-height:1.7'>{chapter_text}</div>{"<div style='margin-top:12px;color:#FF4488;font-size:11px;font-family:Space Mono'>⚠️ To be continued... complete another mission.</div>" if is_last else ""}</div>""", unsafe_allow_html=True)

# ── SECRETS ──
elif view == "secrets":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🔮 UNIVERSE SECRETS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace'>Every mission unlocks a secret. These are truths that will break your brain.</p>", unsafe_allow_html=True)
    seen = st.session_state.get("secret_queue",[])
    if seen:
        for s in reversed(seen):
            st.markdown(f"<div class='secret-card'>{s}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center;color:#ffffff;font-size:14px'>Complete your first mission to unlock your first secret. 🔮</p>", unsafe_allow_html=True)

# ── ACHIEVEMENTS ──
elif view == "achievements":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🏆 ACHIEVEMENTS</h2>", unsafe_allow_html=True)

    # ── UNIVERSE-SPECIFIC LORE ACHIEVEMENTS ──
    lore_achs = wd.get("lore_achievements", [])
    if lore_achs:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-bottom:12px'>🌌 {st.session_state.user_theme.upper()} LORE ACHIEVEMENTS</h3>", unsafe_allow_html=True)
        for la in lore_achs:
            st.markdown(f"""<div class='ach-card' style='border-color:{C};opacity:0.7'><span style='font-family:Bebas Neue,sans-serif;font-size:18px;color:{C}'>{la.get("name","🌌 Lore Achievement")}</span><br><span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{la.get("desc","Complete missions to unlock.")}</span></div>""", unsafe_allow_html=True)
        st.markdown("---")

    # ── STANDARD ACHIEVEMENTS ──
    st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-bottom:12px'>⚡ UNIVERSAL ACHIEVEMENTS</h3>", unsafe_allow_html=True)
    unlocked = st.session_state.get("unlocked_achievements", set())
    for ach in ACHIEVEMENTS:
        is_done = ach["id"] in unlocked
        border_col = C if is_done else MUTED
        opacity = "1.0" if is_done else "0.35"
        st.markdown(f"""<div class='ach-card' style='border-color:{border_col};opacity:{opacity}'><span style='font-family:Bebas Neue,sans-serif;font-size:18px;color:{C}'>{ach["name"]}</span><br><span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{ach["desc"]}</span></div>""", unsafe_allow_html=True)

# ── INCUBATOR ──
elif view == "incubator":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🥚 INCUBATOR</h2>", unsafe_allow_html=True)
    eggs = st.session_state.incubator_eggs
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:{TEXT}'>You have <span style='color:{C};font-size:24px;font-family:Bebas Neue,sans-serif'>{eggs}</span> eggs ready to hatch.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;font-size:11px;color:#ffffff'>Earn eggs by completing missions and winning battles.</p>", unsafe_allow_html=True)
    if eggs > 0:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-top:16px'>🥚 EGGS WAITING TO HATCH</h3>", unsafe_allow_html=True)
        for egg_idx in range(min(eggs, 8)):
            if "egg_warmth" not in st.session_state: st.session_state.egg_warmth = {}
            if egg_idx not in st.session_state.egg_warmth:
                st.session_state.egg_warmth[egg_idx] = min(100, (egg_idx + 1) * 15 + random.randint(5, 25))
            w = st.session_state.egg_warmth[egg_idx]
            bar_filled = int(w / 100 * 20); bar = "█" * bar_filled + "░" * (20 - bar_filled)
            hint = "🐉 LEGENDARY VIBES..." if w >= 90 else "✨ Something Epic stirs..." if w >= 70 else "💙 Rare energy detected" if w >= 45 else "⬜ Still warming up..."
            st.markdown(f"""<div class='ach-card'><div style='display:flex;justify-content:space-between;align-items:center'><span style='font-size:20px'>🥚</span><span style='font-family:Space Mono,monospace;font-size:11px;color:#ffffff'>EGG #{egg_idx+1}</span><span style='font-family:Space Mono,monospace;font-size:10px;color:{C}'>{hint}</span></div><div style='margin-top:8px;font-family:Space Mono,monospace;font-size:12px;color:{C}'>{bar} {w}%</div></div>""", unsafe_allow_html=True)
        if eggs > 8:
            st.markdown(f"<p style='text-align:center;color:#ffffff;font-size:12px'>...and {eggs-8} more eggs waiting</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, hcol, _ = st.columns([1,2,1])
        with hcol:
            if st.button("🥚 HATCH EGG", key="hatch_egg"):
                monster = hatch_egg(st.session_state.user_theme)
                st.session_state.incubator_eggs -= 1; st.session_state.eggs_hatched += 1
                reward = int(5 * monster["reward_mult"]); st.session_state.gold += reward
                if monster["rarity"] == "Legendary": st.session_state.legendary_hatched = True; st.balloons()
                st.session_state.hatched_monsters.append(monster)
                warmth_dict = st.session_state.get("egg_warmth", {}); new_warmth = {i-1: v for i,v in warmth_dict.items() if i > 0}; st.session_state.egg_warmth = new_warmth
                rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
                rc = rarity_colors.get(monster["rarity"],"#ffffff")
                st.markdown(f"""<div class='monster-card'><div style='font-size:36px'>{'🐉' if monster['rarity']=='Legendary' else '🐣'}</div><div style='font-size:11px;color:{rc};letter-spacing:3px;font-family:Space Mono,monospace'>{monster["rarity"].upper()} HATCHED!</div><div style='font-family:Bebas Neue,sans-serif;font-size:28px;color:{C}'>{monster["name"].upper()}</div><div style='font-size:13px;color:#ffffff'>+{reward} {currency} reward!</div></div>""", unsafe_allow_html=True)
                time.sleep(0.5); st.rerun()
    if st.session_state.hatched_monsters:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-top:24px'>YOUR COLLECTION</h3>", unsafe_allow_html=True)
        rarity_colors = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}
        for m in reversed(st.session_state.hatched_monsters[-10:]):
            rc = rarity_colors.get(m["rarity"],"#ffffff")
            st.markdown(f"<div class='ach-card'><span style='color:{rc};font-family:Bebas Neue,sans-serif;font-size:16px'>[{m['rarity'].upper()}]</span> <span style='color:#ffffff;font-family:Space Mono,monospace'>{m['name']}</span></div>", unsafe_allow_html=True)

# ── MANUAL ──
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
        st.markdown(f"""<div class='ach-card'><span style='font-size:24px'>{icon}</span><span style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:2px;margin-left:8px'>{title}</span><br><span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{desc}</span></div>""", unsafe_allow_html=True)

# ── PLANS ──
elif view == "plans":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💳 UPGRADE PLANS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:#ffffff;font-size:12px'>Subscribe below · Then enter your code in the sidebar to activate instantly ⚡</p>", unsafe_allow_html=True)
    p_col, e_col = st.columns(2)
    with p_col:
        st.markdown(f"""<div class='shop-card'><div style='text-align:center;margin-bottom:16px'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>⚡ PREMIUM</div><div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$5<span style='font-size:20px;color:#aaaaaa'>/mo</span></div></div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>✅ 2× XP on every mission<br>✅ Rare+ ability upgrades<br>✅ Extended mission timer options<br>✅ Priority AI universe generation<br>✅ Exclusive ⚡ Premium badge</div><div style='background:#1a1a1a;border:1px solid #444;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'><div style='font-family:Space Mono,monospace;font-size:10px;color:#aaaaaa;letter-spacing:2px;margin-bottom:4px'>AFTER PAYING — ENTER CODE IN SIDEBAR</div><div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:4px'>1TR5LG89D</div></div></div>""", unsafe_allow_html=True)
        st.link_button("⚡ SUBSCRIBE — PREMIUM $5/mo", "https://buy.stripe.com/7sY3co4RC36M0KY495dQQ02", use_container_width=True)
    with e_col:
        st.markdown(f"""<div class='shop-card' style='border-color:#FFD700'><div style='text-align:center;margin-bottom:16px'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:#FFD700'>💀 ELITE</div><div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$10<span style='font-size:20px;color:#aaaaaa'>/mo</span></div></div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>✅ 3× XP on every mission<br>✅ ALL ability tiers unlocked<br>✅ Full maximum customization<br>✅ Legendary egg rate doubled<br>✅ Exclusive 💀 Elite badge</div><div style='background:#1a1a1a;border:1px solid #FFD700;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'><div style='font-family:Space Mono,monospace;font-size:10px;color:#aaaaaa;letter-spacing:2px;margin-bottom:4px'>AFTER PAYING — ENTER CODE IN SIDEBAR</div><div style='font-family:Bebas Neue,sans-serif;font-size:20px;color:#FFD700;letter-spacing:4px'>4RJ1TV51Z</div></div></div>""", unsafe_allow_html=True)
        st.link_button("💀 SUBSCRIBE — ELITE $10/mo", "https://buy.stripe.com/14A9AM83O0YE0KYgVRdQQ03", use_container_width=True)

# ── SPINNER (FIXED: no exploit, 6-hour cooldown) ──
elif view == "spinner":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🎰 LUCKY SPINNER</h2>", unsafe_allow_html=True)

    # ── 6-HOUR COOLDOWN CHECK ──
    spins_left = st.session_state.get('spins_left', 0)
    last_spin = st.session_state.get("last_spin_time")
    cooldown_active = False
    cooldown_remaining = ""
    if last_spin:
        elapsed = (_dt.datetime.now() - _dt.datetime.fromisoformat(last_spin)).total_seconds()
        if elapsed < 21600:  # 6 hours = 21600 seconds
            cooldown_active = True
            remaining_secs = int(21600 - elapsed)
            hours = remaining_secs // 3600
            mins = (remaining_secs % 3600) // 60
            cooldown_remaining = f"{hours}h {mins}m"

    available = spins_left > 0 and not cooldown_active

    if cooldown_active and spins_left > 0:
        st.markdown(f"""<div style='text-align:center;padding:20px;background:#111;border:2px solid #FF8800;border-radius:14px;margin:12px 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:28px;color:#FF8800;letter-spacing:3px'>⏰ COOLDOWN ACTIVE</div>
            <div style='font-family:Space Mono,monospace;font-size:14px;color:#ffffff;margin-top:8px'>Next spin available in: <b style='color:{C}'>{cooldown_remaining}</b></div>
            <div style='font-family:Space Mono,monospace;font-size:11px;color:#888;margin-top:4px'>You have {spins_left} spin{"s" if spins_left != 1 else ""} waiting</div>
        </div>""", unsafe_allow_html=True)
    elif not available:
        st.markdown("<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace'>Complete a mission to earn spins! 🎰</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center;color:#ffffff;font-family:Space Mono,monospace;font-size:13px'>You have <b style='color:{C}'>{spins_left}</b> spin{'s' if spins_left != 1 else ''} available! 🔥</p>", unsafe_allow_html=True)

    prize_labels = json.dumps([p["label"] for p in SPINNER_PRIZES])
    prize_colors = json.dumps([p["color"] for p in SPINNER_PRIZES])
    components.html(f"""<style>body{{margin:0;background:transparent;display:flex;flex-direction:column;align-items:center;font-family:monospace;}}canvas{{border-radius:50%;box-shadow:0 0 40px rgba(255,215,0,0.5);}}#spinBtn{{margin-top:20px;padding:16px 48px;font-size:22px;font-weight:bold;background:linear-gradient(135deg,#FFD700,#FF8C00);border:none;border-radius:12px;cursor:pointer;color:#000;letter-spacing:2px;box-shadow:0 0 30px rgba(255,215,0,0.5);}}#spinBtn:disabled{{opacity:0.4;cursor:not-allowed;}}#result{{margin-top:16px;font-size:20px;color:#FFD700;letter-spacing:2px;text-align:center;min-height:30px;}}</style><canvas id="wheel" width="320" height="320"></canvas><button id="spinBtn" {"disabled" if not available else ""}>{"⏰ COOLDOWN — " + cooldown_remaining if cooldown_active and spins_left > 0 else "🔒 EARN SPINS FIRST" if not available else "🎰 SPIN IT"}</button><div id="result"></div><script>const labels={prize_labels};const colors={prize_colors};const cv=document.getElementById('wheel'),ctx=cv.getContext('2d'),n=labels.length,arc=2*Math.PI/n;let currentAngle=0,spinning=false;function drawWheel(a){{ctx.clearRect(0,0,320,320);for(let i=0;i<n;i++){{ctx.beginPath();ctx.moveTo(160,160);ctx.arc(160,160,150,a+i*arc,a+(i+1)*arc);ctx.fillStyle=colors[i];ctx.fill();ctx.strokeStyle='#111';ctx.lineWidth=2;ctx.stroke();ctx.save();ctx.translate(160,160);ctx.rotate(a+(i+0.5)*arc);ctx.textAlign='right';ctx.fillStyle='#fff';ctx.font='bold 11px monospace';ctx.shadowColor='#000';ctx.shadowBlur=4;ctx.fillText(labels[i],140,5);ctx.restore();}}ctx.beginPath();ctx.arc(160,160,22,0,2*Math.PI);ctx.fillStyle='#111';ctx.fill();ctx.strokeStyle='#FFD700';ctx.lineWidth=3;ctx.stroke();ctx.beginPath();ctx.moveTo(300,150);ctx.lineTo(320,160);ctx.lineTo(300,170);ctx.fillStyle='#FFD700';ctx.fill();}}drawWheel(0);document.getElementById('spinBtn').onclick=function(){{if(spinning)return;spinning=true;this.disabled=true;document.getElementById('result').textContent='';const extra=(5+Math.random()*5)*2*Math.PI,dur=4000+Math.random()*2000,start=performance.now(),sa=currentAngle;function anim(now){{const el=now-start,p=Math.min(el/dur,1),ease=1-Math.pow(1-p,4);currentAngle=sa+extra*ease;drawWheel(currentAngle);if(p<1)requestAnimationFrame(anim);else{{spinning=false;const norm=((2*Math.PI)-(currentAngle%(2*Math.PI)))%(2*Math.PI);const idx=Math.floor(norm/arc)%n;document.getElementById('result').textContent='🎉 '+labels[idx]+'!';}}}}requestAnimationFrame(anim);}};</script>""", height=460)

    # ── CLAIM BUTTON: only shows when available, consumes 1 spin, sets cooldown ──
    if available:
        _, sc, _ = st.columns([1,2,1])
        with sc:
            if st.button(f"🎰 USE 1 SPIN ({spins_left} remaining)", key="claim_spin"):
                prize = spin_wheel()
                # Consume the spin
                st.session_state.spins_left = max(0, st.session_state.get("spins_left", 0) - 1)
                st.session_state.spinner_available = False
                st.session_state.spinner_wins = st.session_state.get("spinner_wins", 0) + 1
                # Set 6-hour cooldown
                st.session_state.last_spin_time = _dt.datetime.now().isoformat()
                # Apply prize
                if prize["type"] == "gold_mult":
                    bonus = st.session_state.pending_gold * prize["value"] if st.session_state.pending_gold else prize["value"] * 2
                    st.session_state.gold += bonus; msg = f"💰 {prize['label']}! +{bonus:.1f} {currency}!"
                elif prize["type"] == "gold_flat":
                    st.session_state.gold += prize["value"]; msg = f"⚡ +{prize['value']} {currency}!"
                elif prize["type"] == "egg_rare":
                    st.session_state.incubator_eggs += 1; msg = "🥚 RARE EGG added to incubator!"
                elif prize["type"] == "egg_epic":
                    st.session_state.incubator_eggs += 1; msg = "✨ EPIC EGG added to incubator!"
                elif prize["type"] == "ability":
                    if prize["value"] == "shield":
                        st.session_state.shield_bought = True; msg = f"🛡️ {wd.get('shield_name','SHIELD')} activated FREE!"
                    else:
                        st.session_state.booster_bought = True; st.session_state.sub_multiplier = max(st.session_state.sub_multiplier, 2); msg = f"🚀 {wd.get('booster_name','BOOSTER')} activated FREE!"
                elif prize["type"] == "story_twist":
                    st.session_state.story_twist_pending = True; msg = "📖 STORY TWIST UNLOCKED!"
                else:
                    msg = "💨 Nothing this time... earn more spins from missions!"
                st.session_state.spinner_result = {"prize": prize, "msg": msg}
                st.balloons(); st.success(f"🎰 {msg}"); time.sleep(1); st.rerun()

    if st.session_state.spinner_result:
        p = st.session_state.spinner_result
        st.markdown(f"""<div class='secret-card'><div style='font-size:40px'>{p['prize']['emoji']}</div><div style='font-family:Bebas Neue,sans-serif;font-size:24px;color:{C};letter-spacing:3px'>{p['prize']['label']}</div><div style='font-size:13px;color:#ffffff;margin-top:8px'>{p['msg']}</div></div>""", unsafe_allow_html=True)

# ── FEEDBACK ──
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
            else: st.error("Write something first!")
        if st.session_state.feedback_list:
            st.markdown("---")
            for fb in reversed(st.session_state.feedback_list):
                st.markdown(f"<div class='ach-card'><span style='color:{C}'>{fb['type']}</span> · <span style='color:#ffffff;font-size:11px'>{fb['time']} · {fb['name']}</span><br><span style='color:{TEXT}'>{fb['message']}</span></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# THE TRIBUNAL — Proof upload & reward claiming
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.needs_verification:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center;font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:4px'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        st.info(f"Upload proof of work to claim **{st.session_state.pending_gold:.1f} {currency}**")
        uploaded = st.file_uploader("PROOF OF LABOR:", key="proof_upload")
        if uploaded and st.button("⚡ SUBMIT FOR JUDGMENT", key="submit_proof"):
            base_gold = st.session_state.pending_gold
            earned, rarity_label, rarity_msg, near_miss = variable_reward(base_gold)
            earned = round(earned, 1)
            new_streak, streak_msg, is_new_day = update_streak()
            spins = get_spins_for_tier(st.session_state.get("sub_tier","Free"))
            st.session_state.spins_left = st.session_state.get("spins_left",0) + spins
            st.session_state.gold += earned; st.session_state.xp += int(earned * 10)
            st.session_state.total_xp_real = st.session_state.get("total_xp_real",0) + int(earned*10)
            st.session_state.level = 1 + st.session_state.xp // 100
            st.session_state.total_missions += 1
            st.session_state.needs_verification = False; st.session_state.pending_gold = 0.0
            loot_pool = [
                {"name": f"+{spins} Spinner Spins", "rarity": rarity_label, "color": "#FFD700"},
                {"name": "RARE INCUBATOR EGG", "rarity": "GREAT", "color": "#4488FF"},
                {"name": "STREAK SHIELD (protects 1 day)", "rarity": "EPIC", "color": "#AA44FF"},
                {"name": f"+{int(earned*2)} Bonus {currency}", "rarity": rarity_label, "color": "#00FF88"},
                {"name": "STORY CHAPTER UNLOCKED", "rarity": "GREAT", "color": "#FF44AA"},
            ]
            loot = random.choice(loot_pool)
            if "Shield" in loot["name"]: st.session_state.streak_shield = True
            if "Egg" in loot["name"]: st.session_state.incubator_eggs += 2
            if "Bonus" in loot["name"]: st.session_state.gold += int(earned*2)
            st.session_state.loot_pending = True; st.session_state.loot_item = loot
            secret = random.choice(UNIVERSE_SECRETS)
            if "secret_queue" not in st.session_state: st.session_state.secret_queue = []
            st.session_state.secret_queue.append(secret)
            st.session_state.secrets_seen = len(st.session_state.secret_queue)
            st.session_state.show_secret = secret
            st.session_state.spinner_available = True
            client = get_claude_client()
            prev = " ".join(st.session_state.story_log[-2:]) if st.session_state.story_log else ""
            st.session_state.story_chapter += 1
            new_chapter = generate_story_chapter(st.session_state.user_theme, st.session_state.story_chapter, prev, client)
            st.session_state.story_log.append(new_chapter)
            if MODE in ("grinder","obsessed"): st.session_state.battle_state = "ready"
            st.session_state.incubator_eggs += 1
            near_miss_display = f" · 🎯 {near_miss}" if near_miss else ""
            st.balloons()
            st.success(f"✅ {rarity_label}! +{earned:.1f} {currency} · 🔥 {new_streak}-day streak · +{spins} spins{near_miss_display}")
            time.sleep(1); st.rerun()
