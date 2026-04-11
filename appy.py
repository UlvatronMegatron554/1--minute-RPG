import streamlit as st
import anthropic
import time, json, re, random
import datetime as _dt
import streamlit.components.v1 as components
try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False
try:
    import replicate
    REPLICATE_AVAILABLE = True
except Exception:
    REPLICATE_AVAILABLE = False

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
    "🌊 THE SUN IS DELAYED: The light hitting your face right now left the Sun 8 minutes ago. You are always seeing the past.",
    "🔥 FIRE ISN'T A THING: Fire is not matter. It has no mass. It is a chemical reaction — pure energy made visible.",
    "🌍 EARTH IS FAKE ROUND: Earth is not a sphere. It bulges at the equator. Maps have been lying to you.",
    "💥 YOUR MEMORY IS FICTION: Every time you remember something, you are reconstructing it. Every reconstruction changes it slightly.",
    "🧲 IMPOSSIBLE MATERIAL: Aerogel is 99.8% air. It can support 4,000 times its own weight.",
    "⏰ BIOLOGICAL HORROR: You have a second brain in your gut. It has 100 million neurons. It makes decisions independently.",
    "🌀 MANDELA EFFECT EXPLAINED: Your brain fills in gaps in your vision. There is a blind spot in each eye. You have never seen a complete image.",
    "🔬 QUANTUM HORROR: Particles that have interacted remain connected FOREVER across any distance. Changing one instantly affects the other.",
    "🕊️ BIRDS ARE DINOSAURS: When you look at a bird, you are looking at a living dinosaur. Birds are the direct descendants of theropod dinosaurs.",
    "🌿 TREES ARE ONE ORGANISM: The Pando aspen grove in Utah is a single organism. It is 80,000 years old. It is the largest living thing on Earth.",
    "🤖 YOU ARE PROGRAMMABLE: Scientists have successfully implanted false memories into mice. Human memory works the same way.",
    "💀 DEATH PARADOX: The cells in your body are completely replaced every 7-10 years. Are you the same person you were a decade ago?",
    "⚡ SPEED OF THOUGHT: Your brain makes decisions up to 10 SECONDS before you are consciously aware of making them. Free will might be an illusion.",
    "🌌 MULTIVERSE IS MATH: The equations of quantum mechanics predict ALL possible outcomes simultaneously. Every decision spawns a parallel universe.",
    "🧠 PLACEBO IS REAL MEDICINE: Placebo surgery — where surgeons cut open patients, do nothing, and sew them back up — has the same results as real surgery for certain conditions.",
    "🔮 NOTHING IS SOLID: The chair you are sitting on is not solid. The atoms repel each other electromagnetically creating the illusion of solidity.",
]

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS DATABASE
# ─────────────────────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "first_mission",    "name": "⚡🌟 FIRST BLOOD",              "desc": "Completed your very first mission. The journey begins NOW.",          "req": lambda s: s.get("total_missions",0) >= 1},
    {"id": "five_missions",    "name": "🔥💪 ON A ROLL",                "desc": "5 missions done. You're already better than yesterday.",              "req": lambda s: s.get("total_missions",0) >= 5},
    {"id": "ten_missions",     "name": "⚡⚡ GRIND MODE ACTIVATED",     "desc": "10 missions. This is becoming a habit. A powerful one.",              "req": lambda s: s.get("total_missions",0) >= 10},
    {"id": "fifty_missions",   "name": "💀🔥👑 UNSTOPPABLE",           "desc": "50 missions. You are literally built different at this point.",        "req": lambda s: s.get("total_missions",0) >= 50},
    {"id": "first_gold",       "name": "💰⚡ FIRST PAYDAY",            "desc": "Earned your first currency. The grind pays off.",                     "req": lambda s: s.get("gold",0) >= 5},
    {"id": "rich",             "name": "💰💰💰 LOADED",               "desc": "100 currency stacked. You are wealthy in this universe.",             "req": lambda s: s.get("gold",0) >= 100},
    {"id": "elite_unlocked",   "name": "👁️🔮💀 ELITE EYES ONLY",      "desc": "You found the code. Not everyone gets here.",                         "req": lambda s: s.get("sub_tier","") == "Elite"},
    {"id": "first_battle",     "name": "⚔️🌀 WARRIOR BORN",           "desc": "First battle fought. Win or lose — you showed up.",                   "req": lambda s: s.get("battles_fought",0) >= 1},
    {"id": "battle_streak",    "name": "⚔️💀🏆 BATTLE HARDENED",      "desc": "10 battles completed. You fear nothing in this universe.",            "req": lambda s: s.get("battles_fought",0) >= 10},
    {"id": "first_egg",        "name": "🥚✨ EGG COLLECTOR",           "desc": "First incubator egg earned. Something is growing in there...",        "req": lambda s: s.get("eggs_hatched",0) >= 1},
    {"id": "legendary_hatch",  "name": "🐉🌟💥 LEGENDARY TAMER",      "desc": "A LEGENDARY creature hatched. This almost never happens.",            "req": lambda s: s.get("legendary_hatched",False)},
    {"id": "shield_bought",    "name": "🛡️⚡ FORTIFIED",              "desc": "Defense ability acquired. Nothing can touch you now.",                "req": lambda s: s.get("shield_bought",False)},
    {"id": "booster_bought",   "name": "🚀💨⚡ SPEED DEMON",          "desc": "Speed ability acquired. You move at a different frequency.",          "req": lambda s: s.get("booster_bought",False)},
    {"id": "secret_collector", "name": "🔮🌀👁️ TRUTH SEEKER",        "desc": "Collected 5 universe secrets. Your mind is expanding.",              "req": lambda s: s.get("secrets_seen",0) >= 5},
    {"id": "spinner_winner",   "name": "🎰⚡💰 LUCKY SPIN",           "desc": "Won your first prize on the spinner. Fortune favours the bold.",      "req": lambda s: s.get("spinner_wins",0) >= 1},
    {"id": "storyline_deep",   "name": "📖🌌✨ LORE KEEPER",          "desc": "Reached chapter 5 of your universe storyline. You are invested.",     "req": lambda s: s.get("story_chapter",0) >= 5},
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
# HTML5 CANVAS BATTLE GAME
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
</style></head><body>
<div id="wrap">
  <canvas id="gc" width="820" height="480"></canvas>
  <div id="questions"></div>
  <div id="result"></div>
</div>
<script>
'use strict';
const CFG={cfg_json};const COL='{col}';const W=820,H=480;
const cv=document.getElementById('gc');const ctx=cv.getContext('2d');
let FC=0,STATE='IN',stT=0,evolveT=0;let subject=CFG.subject||'General';
let questions=[],qI=0,lives=3,wrongs=0,qTimer=0,qMax=25,aLocked=false;
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
  }} else if(MODE==='RPG'){{
    const tg=ctx.createLinearGradient(0,0,0,H*0.5);tg.addColorStop(0,'#1a2a4a');tg.addColorStop(1,'#2a3a5a');ctx.fillStyle=tg;ctx.fillRect(0,0,W,H*0.5);
    const bg2=ctx.createLinearGradient(0,H*0.5,0,H);bg2.addColorStop(0,'#1a3a1a');bg2.addColorStop(1,'#0a1a0a');ctx.fillStyle=bg2;ctx.fillRect(0,H*0.5,W,H*0.5);
  }} else if(MODE==='PLATFORM'){{
    ctx.fillStyle='#87CEEB';ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#228B22';ctx.fillRect(0,H*0.72,W,8);ctx.fillStyle='#8B4513';ctx.fillRect(0,H*0.72+8,W,H);
  }} else if(MODE==='SHOOTER'){{
    ctx.fillStyle='#0a0a0f';ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='rgba(255,255,255,0.04)';ctx.lineWidth=1;for(let x=0;x<W;x+=40){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}for(let y=0;y<H;y+=40){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
  }} else if(MODE==='COSMIC'){{
    ctx.fillStyle='#000005';ctx.fillRect(0,0,W,H);
    for(let i=0;i<120;i++){{const sx=(i*173)%W,sy=(i*97)%H,sa=0.2+((i*31)%10)/10*0.8;ctx.globalAlpha=sa;ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(sx,sy,(i%3)*0.5+0.5,0,6.28);ctx.fill();}}ctx.globalAlpha=1;
  }} else {{
    const bg3=ctx.createLinearGradient(0,0,0,H);bg3.addColorStop(0,BGC[0]);bg3.addColorStop(0.5,BGC[1]||'#111');bg3.addColorStop(1,BGC[2]||'#000');ctx.fillStyle=bg3;ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#ffffff08';ctx.fillRect(0,H*0.72,W,H*0.28);
  }}
}}
function drChar(x,y,col,evo,isEnemy,hit,shake){{
  const ox=x+(shake?(Math.random()-0.5)*shake:0);const oy=y+(shake?(Math.random()-0.5)*shake*0.3:0);
  const t=FC*0.06,idle=Math.sin(t+(isEnemy?1.5:0))*3;
  ctx.save();ctx.translate(ox,oy+idle);if(isEnemy)ctx.scale(-1,1);const s=0.9+evo*0.07;
  if(evo>0){{const ar=28+evo*11;const ag=ctx.createRadialGradient(0,0,4,0,0,ar);ag.addColorStop(0,col+'88');ag.addColorStop(1,'transparent');ctx.fillStyle=ag;ctx.beginPath();ctx.arc(0,0,ar,0,6.28);ctx.fill();}}
  ctx.scale(s,s);
  const vis=isEnemy?(CFG.enemy_visual||{{}}):(CFG.player_visual||{{}});
  if(vis&&vis.hair_color){{drCustom(col,evo,t,vis);}}
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
  const oc2=vis.outfit_secondary||dk(oc,0.2);const wc=vis.weapon_color||'#C0C0C0';const ec2=vis.eye_color||'#000';const ac=vis.aura_color||col;
  const bb=vis.body_build||'average';const hs=vis.hair_style||'short';const wp=vis.weapon||'fists';
  const bw=bb==='muscular'?1.3:bb==='large'?1.4:bb==='slim'?0.85:bb==='tiny'?0.7:1.0;
  const _tier=vis.tier||'free';
  const _isFree=(_tier==='free');const _isPrem=(_tier==='premium');const _isElite=(_tier==='elite');
  // Shadow — Premium/Elite only
  if(!_isFree){{ctx.fillStyle='rgba(0,0,0,0.25)';ctx.beginPath();ctx.ellipse(0,48,22*bw,6,0,0,6.28);ctx.fill();}}
  ctx.fillStyle=dk(oc,0.3);ctx.fillRect(-14*bw,10,12*bw,32);ctx.fillRect(2*bw,10,12*bw,32);
  if(!_isFree){{ctx.fillStyle=dk(oc,0.15);ctx.fillRect(-12*bw,22,8*bw,4);ctx.fillRect(4*bw,22,8*bw,4);}}
  ctx.fillStyle='#333';ctx.fillRect(-16*bw,38,14*bw,10);ctx.fillRect(0,38,14*bw,10);
  if(_isElite){{ctx.fillStyle='#222';ctx.fillRect(-17*bw,46,16*bw,3);ctx.fillRect(-1,46,16*bw,3);}}
  // Body shading: Free=flat, Premium=linear gradient, Elite=full gradient+details
  if(_isFree){{ctx.fillStyle=oc;ctx.fillRect(-18*bw,-14,36*bw,26);}}
  else if(_isPrem){{const bg2=ctx.createLinearGradient(-18*bw,-14,18*bw,12);bg2.addColorStop(0,lh(oc,0.1));bg2.addColorStop(1,oc);ctx.fillStyle=bg2;ctx.fillRect(-18*bw,-14,36*bw,26);ctx.fillStyle=oc2;ctx.fillRect(-18*bw,8,36*bw,4);}}
  else{{const bGrad=ctx.createLinearGradient(-18*bw,-14,18*bw,12);bGrad.addColorStop(0,lh(oc,0.1));bGrad.addColorStop(0.5,oc);bGrad.addColorStop(1,dk(oc,0.15));ctx.fillStyle=bGrad;ctx.fillRect(-18*bw,-14,36*bw,26);ctx.fillStyle=oc2;ctx.fillRect(-18*bw,8,36*bw,4);ctx.fillRect(-12*bw,-14,24*bw,4);}}
  ctx.fillStyle=oc;ctx.fillRect(-32*bw,-12,16*bw,24);ctx.fillRect(16*bw,-12,16*bw,24);
  ctx.fillStyle=sc2;ctx.fillRect(-34*bw,8,14*bw,10);ctx.fillRect(20*bw,8,14*bw,10);
  if(!_isFree){{ctx.fillStyle=dk(sc2,0.1);ctx.fillRect(-34*bw,14,3,4);ctx.fillRect(-28*bw,14,3,4);ctx.fillRect(20*bw,14,3,4);ctx.fillRect(26*bw,14,3,4);}}
  // Head: Free=flat, Premium=gradient, Elite=radial gradient+ears+nose
  if(_isFree){{ctx.fillStyle=sc2;ctx.beginPath();ctx.ellipse(0,-32,18*bw,20,0,0,6.28);ctx.fill();}}
  else if(_isPrem){{const hg2=ctx.createLinearGradient(0,-50,0,-14);hg2.addColorStop(0,lh(sc2,0.1));hg2.addColorStop(1,sc2);ctx.fillStyle=hg2;ctx.beginPath();ctx.ellipse(0,-32,18*bw,20,0,0,6.28);ctx.fill();}}
  else{{const headGrad=ctx.createRadialGradient(-4,-34,2,0,-32,20);headGrad.addColorStop(0,lh(sc2,0.15));headGrad.addColorStop(1,sc2);ctx.fillStyle=headGrad;ctx.beginPath();ctx.ellipse(0,-32,18*bw,20,0,0,6.28);ctx.fill();ctx.fillStyle=sc2;ctx.fillRect(-20*bw,-34,4,8);ctx.fillRect(16*bw,-34,4,8);ctx.fillStyle=dk(sc2,0.08);ctx.fillRect(-1,-28,2,4);}}
  // Eyes: Free=dark blocks, Premium=whites+iris, Elite=full detail+shine
  if(_isFree){{ctx.fillStyle='#000';ctx.fillRect(-8*bw,-34,5,5);ctx.fillRect(3*bw,-34,5,5);}}
  else{{ctx.fillStyle='#fff';ctx.fillRect(-10*bw,-34,8,7);ctx.fillRect(2*bw,-34,8,7);ctx.fillStyle=ec2;ctx.fillRect(-8*bw,-33,5,5);ctx.fillRect(4*bw,-33,5,5);ctx.fillStyle='#000';ctx.fillRect(-7*bw,-32,3,3);ctx.fillRect(5*bw,-32,3,3);if(_isElite){{ctx.fillStyle='rgba(255,255,255,0.8)';ctx.fillRect(-7*bw,-33,2,2);ctx.fillRect(5*bw,-33,2,2);}}}}
  if(!_isFree){{ctx.fillStyle=dk(sc2,0.15);ctx.fillRect(-4,-22,8,2);}}// mouth
  if(_isElite){{ctx.fillStyle=dk(hc,0.3);ctx.fillRect(-11*bw,-37,9,2);ctx.fillRect(2*bw,-37,9,2);}}// eyebrows
  ctx.fillStyle=hc;
  if(hs==='spiky'){{for(let i=0;i<5+evo;i++){{const hx=-16+i*(32/(4+evo));ctx.beginPath();ctx.moveTo(hx-5,-48);ctx.lineTo(hx,-(60+evo*4+i%2*8));ctx.lineTo(hx+5,-48);ctx.fill();}}}}
  else if(hs==='long'||hs==='flowing'){{ctx.fillRect(-20,-50,40,14);ctx.fillRect(-22,-48,6,36);ctx.fillRect(16,-48,6,36);}}
  else if(hs==='mohawk'){{ctx.fillRect(-4,-50,8,14);for(let i=0;i<3;i++){{ctx.beginPath();ctx.moveTo(-4,-50-i*8);ctx.lineTo(0,-62-i*8);ctx.lineTo(4,-50-i*8);ctx.fill();}}}}
  else if(hs==='afro'){{ctx.beginPath();ctx.arc(0,-46,22+evo*2,0,6.28);ctx.fill();}}
  else{{ctx.fillRect(-18,-50,36,12);}}
  if(wp==='sword'){{ctx.fillStyle=wc;ctx.fillRect(22*bw,-6,4,36);ctx.fillStyle='#FFD700';ctx.fillRect(20*bw,-6,8,4);}}
  else if(wp==='dual_sword'){{ctx.fillStyle=wc;ctx.fillRect(-36*bw,-4,3,30);ctx.fillRect(33*bw,-4,3,30);ctx.fillStyle='#FFD700';ctx.fillRect(-38*bw,-4,7,3);ctx.fillRect(31*bw,-4,7,3);}}
  else if(wp==='triple_sword'){{ctx.fillStyle=wc;ctx.fillRect(-36*bw,-4,3,30);ctx.fillRect(33*bw,-4,3,30);ctx.fillRect(-2,-(32+evo*2),3,20);}}
  else if(wp==='gun'){{ctx.fillStyle='#444';ctx.fillRect(20*bw,2,28,6);}}
  else if(wp==='staff'||wp==='wand'){{ctx.fillStyle='#8B4513';ctx.fillRect(22*bw,-20,4,44);ctx.fillStyle=ac;ctx.beginPath();ctx.arc(24*bw,-22,6+evo,0,6.28);ctx.fill();}}
  // Cape: Elite only
  if(_isElite&&vis.cape){{ctx.fillStyle=(vis.cape_color||ac)+'88';ctx.beginPath();ctx.moveTo(-16*bw,-10);ctx.lineTo(-20*bw,30);ctx.lineTo(20*bw,30);ctx.lineTo(16*bw,-10);ctx.fill();ctx.fillStyle=(vis.cape_color||ac)+'44';ctx.beginPath();ctx.moveTo(-18*bw,-8);ctx.lineTo(-22*bw,32);ctx.lineTo(22*bw,32);ctx.lineTo(18*bw,-8);ctx.fill();}}
  // Aura: Free=none, Premium=subtle, Elite=layered
  if(_isPrem&&evo>=1){{ctx.fillStyle=ac+'22';ctx.beginPath();ctx.arc(0,-10,28+evo*4,0,6.28);ctx.fill();}}
  if(_isElite&&evo>=1){{ctx.fillStyle=ac+'33';ctx.beginPath();ctx.arc(0,-10,30+evo*5,0,6.28);ctx.fill();ctx.fillStyle=ac+'18';ctx.beginPath();ctx.arc(0,-10,40+evo*7,0,6.28);ctx.fill();if(evo>=3){{ctx.strokeStyle=ac+'88';ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,-10,35+evo*5,0,6.28);ctx.stroke();}}}}
}}
function drFighter(col,evo,t,isEnemy){{
  const hc=evo>=1?'#FFD700':col;
  ctx.fillStyle=col;ctx.fillRect(-16,10,14,36);ctx.fillRect(2,10,14,36);
  ctx.fillStyle='#333';ctx.fillRect(-18,38,16,10);ctx.fillRect(0,38,16,10);
  ctx.fillStyle=col;ctx.fillRect(-20,-15,40,28);ctx.fillStyle='#222';ctx.fillRect(-20,10,40,6);
  ctx.fillStyle=col;ctx.fillRect(-36,-12,18,24);ctx.fillRect(18,-12,18,24);
  ctx.fillStyle=col;ctx.fillRect(-8,-22,16,10);ctx.fillRect(-22,-50,44,32);
  ctx.fillStyle=evo>=2?'#00FFFF':'#fff';ctx.fillRect(-14,-38,10,8);ctx.fillRect(4,-38,10,8);
  ctx.fillStyle='#000';ctx.fillRect(-10,-36,4,5);ctx.fillRect(7,-36,4,5);
  ctx.fillStyle=hc;const sp=3+Math.min(evo,5);
  for(let i=0;i<sp;i++){{const sx=-18+i*(36/(sp-1)),sh=14+i%2*8+evo*4;ctx.beginPath();ctx.moveTo(sx-6,-50);ctx.lineTo(sx,-(50+sh));ctx.lineTo(sx+6,-50);ctx.fill();}}
}}
function drRPG(col,evo,t){{
  const r=22+evo*3;const bg2=ctx.createRadialGradient(-r*0.3,-r*0.3,2,0,0,r);bg2.addColorStop(0,lh(col,0.4));bg2.addColorStop(1,col);ctx.fillStyle=bg2;ctx.beginPath();ctx.ellipse(0,0,r,r*0.85,0,0,6.28);ctx.fill();
  const ec=evo>=2?'#FFD700':'#000';[[-r*.3,-r*.2,r*.25,r*.22],[r*.3,-r*.2,r*.25,r*.22]].forEach(([ex,ey,erx,ery])=>{{ctx.fillStyle='#fff';ctx.beginPath();ctx.ellipse(ex,ey,erx,ery,0,0,6.28);ctx.fill();ctx.fillStyle=ec;ctx.beginPath();ctx.ellipse(ex,ey,erx*0.55,ery*0.55,0,0,6.28);ctx.fill();}});
}}
function drPlatform(col,evo){{
  ctx.fillStyle='#2244CC';ctx.fillRect(-14,0,28,26);
  ctx.fillStyle=col;ctx.fillRect(-18,-14,36,20);
  ctx.fillStyle='#FFCC88';ctx.fillRect(-18,-42,36,30);
  ctx.fillStyle=col;ctx.fillRect(-20,-52,40,14);
  ctx.fillStyle='#000';ctx.fillRect(-10,-32,7,6);ctx.fillRect(3,-32,7,6);
}}
function drShooter(col,evo){{
  ctx.fillStyle='#334422';ctx.fillRect(-14,2,28,32);ctx.fillRect(-18,-12,36,16);
  ctx.fillStyle='#222';ctx.fillRect(-18,-38,36,28);ctx.fillStyle='#00FF44';ctx.fillRect(-14,-28,28,3);
  ctx.fillStyle='#111';ctx.fillRect(16,0,30,8);
}}
function drMagic(col,evo,t){{
  ctx.fillStyle=col+'CC';ctx.beginPath();ctx.moveTo(-22,42);ctx.lineTo(-18,-10);ctx.lineTo(18,-10);ctx.lineTo(22,42);ctx.closePath();ctx.fill();
  ctx.fillStyle='#FFCC88';ctx.fillRect(-16,-36,32,28);
  ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(-22,-36);ctx.lineTo(0,-(78+evo*6));ctx.lineTo(22,-36);ctx.closePath();ctx.fill();
}}
function drCosmic(col,evo,t){{
  const r=22+evo*3;const hg=ctx.createLinearGradient(-r,-r/2,r,r/2);hg.addColorStop(0,lh(col,0.3));hg.addColorStop(1,col);ctx.fillStyle=hg;
  ctx.beginPath();ctx.moveTo(-r,8);ctx.quadraticCurveTo(-r,-r/2,0,-r);ctx.quadraticCurveTo(r,-r/2,r,8);ctx.quadraticCurveTo(0,r*1.1,-r,8);ctx.fill();
}}
function drSports(col,evo){{
  ctx.fillStyle=col;ctx.fillRect(-18,-14,36,24);
  ctx.fillStyle='#FFCC88';ctx.beginPath();ctx.ellipse(0,-30,14,18,0,0,6.28);ctx.fill();
  ctx.fillStyle='#000';ctx.fillRect(-6,-32,5,5);ctx.fillRect(1,-32,5,5);
}}
function drBrawl(col,evo,t){{
  ctx.fillStyle=col;ctx.fillRect(-20,-10,40,30);ctx.fillRect(-16,-24,32,16);
  ctx.fillStyle=lh(col,0.2);ctx.beginPath();ctx.ellipse(0,-34,18,20,0,0,6.28);ctx.fill();
  ctx.fillStyle='#000';ctx.fillRect(-8,-36,6,6);ctx.fillRect(2,-36,6,6);
  ctx.fillStyle=col;ctx.fillRect(-38,-12,20,22);ctx.fillRect(18,-12,20,22);
}}
function drDefault(col,evo,t){{
  const s=0.9+evo*0.04;
  ctx.fillStyle=dk(col,0.3);ctx.fillRect(-16*s,8*s,13*s,34*s);ctx.fillRect(3*s,8*s,13*s,34*s);
  ctx.fillStyle=col;ctx.fillRect(-20*s,-14*s,40*s,24*s);
  ctx.fillStyle=lh(col,0.2);ctx.beginPath();ctx.ellipse(0,-32*s,20*s,22*s,0,0,6.28);ctx.fill();
  const ec=evo>=3?'#FF4400':evo>=1?'#00FFFF':'#333';
  [[-8,-32,6,6],[8,-32,6,6]].forEach(([ex,ey,r1,r2])=>{{ctx.fillStyle='rgba(255,255,255,0.9)';ctx.beginPath();ctx.ellipse(ex*s,ey*s,r1*s,r2*s,0,0,6.28);ctx.fill();ctx.fillStyle=ec;ctx.beginPath();ctx.ellipse(ex*s,ey*s,r1*s*0.5,r2*s*0.5,0,0,6.28);ctx.fill();}});
}}
function drHUD(){{
  const php=Math.max(0,P.hp/P.maxHp);const phc=php>0.5?'#00FF44':php>0.25?'#FF8800':'#FF2222';
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(12,12,200,18);ctx.fillStyle=phc;ctx.fillRect(12,12,200*php,18);
  ctx.strokeStyle='#fff4';ctx.lineWidth=1;ctx.strokeRect(12,12,200,18);
  ctx.fillStyle='#fff';ctx.font='bold 10px "Space Mono",monospace';ctx.fillText('HP '+Math.ceil(P.hp)+'/'+P.maxHp,16,25);
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(12,34,200,10);ctx.fillStyle=COL;ctx.fillRect(12,34,200*(P.power/100),10);
  const evos=CFG.evolutions||[];const en=evos[P.evo]||('Lv '+(P.evo+1));
  ctx.fillStyle=COL;ctx.font='bold 9px Orbitron,monospace';ctx.fillText('⚡ '+en.toUpperCase(),12,58);
  const ehp=Math.max(0,E.hp/E.maxHp);const ehc=ehp>0.5?'#FF4444':ehp>0.25?'#FF8800':'#FF0000';
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(W-212,12,200,18);ctx.fillStyle=ehc;ctx.fillRect(W-212,12,200*ehp,18);
  ctx.strokeStyle='#fff4';ctx.strokeRect(W-212,12,200,18);
  ctx.fillStyle='#fff';ctx.font='bold 10px "Space Mono",monospace';ctx.fillText((CFG.enemy_name||'Enemy').substring(0,18),W-208,25);
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
  ab(P.x,P.y-30,E.x,E.y-30,COL,6+P.evo*2,24);ap(E.x,E.y-30,COL,20+P.evo*4,4,6,28);
  dn(E.x,E.y-60,'-'+dmg,COL,true);
  const nt=P.evo+1;const evos=CFG.evolutions||[];
  if(nt<evos.length&&P.total>0&&P.total%3===0&&Math.floor(P.total/3)===nt){{evolve(nt);}}
  if(E.hp/E.maxHp<0.33&&E.phase===0){{E.phase=1;ap(E.x,E.y,E.color,40,6,8,50);}}
  else if(E.hp/E.maxHp<0.1&&E.phase===1){{E.phase=2;ap(E.x,E.y,E.color,60,8,10,60);}}
  if(E.hp<=0)setTimeout(win,700);
}}
function onNo(){{
  P.streak=0;wrongs++;
  const dmg=10+E.phase*8+Math.floor(Math.random()*8);
  P.hp=Math.max(0,P.hp-dmg);P.hit=true;P.shake=14;setTimeout(()=>P.hit=false,380);
  if(wrongs>=3){{lives--;wrongs=0;}}
  ab(E.x,E.y-30,P.x,P.y-30,E.color,5,20);ap(P.x,P.y-30,'#FF2222',15,3,5,26);
  dn(P.x,P.y-60,'-'+dmg,'#FF2222',false);
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
  res.innerHTML=`<div style="font-size:50px;margin-bottom:10px">🏆</div><div style="font-family:Orbitron,monospace;font-size:34px;color:${{COL}};letter-spacing:4px;margin-bottom:6px">VICTORY!</div><div style="color:#FFD700;font-family:'Space Mono',monospace;font-size:13px;margin-bottom:8px">${{CFG.win_quote||'You prevailed!'}}</div><div style="color:#fff;font-size:12px;margin:14px 0;line-height:2.2">⚡ <b style="color:${{COL}}">+${{xp}} XP</b> &nbsp; 💰 <b style="color:#FFD700">+${{gold}} Shards</b> &nbsp; 🎁 <b style="color:#AA44FF">BATTLE BOX!</b><br>Form: <b style="color:${{COL}}">${{(CFG.evolutions||[])[P.evo]||'Level '+(P.evo+1)}}</b></div>`;
  window.parent.postMessage({{type:'battleWin',xp,gold,evolution:P.evo,correct:P.total}},'*');
}}
function lose(){{
  STATE='LOSE';document.getElementById('questions').style.display='none';
  ap(P.x,P.y,'#FF2222',50,6,8,60);
  const res=document.getElementById('result');res.style.display='flex';
  res.innerHTML=`<div style="font-size:50px;margin-bottom:10px">💀</div><div style="font-family:Orbitron,monospace;font-size:34px;color:#FF2222;letter-spacing:4px;margin-bottom:6px">DEFEATED</div><div style="color:#FF8888;font-family:'Space Mono',monospace;font-size:13px;margin-bottom:10px">${{CFG.lose_quote||'Train harder.'}}</div>`;
  window.parent.postMessage({{type:'battleLose'}},'*');
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
var allQ=CFG.questions||[];questions=allQ.slice().sort(function(){{return Math.random()-0.5;}}).slice(0,Math.min(10,allQ.length));
if(!questions.length)questions=[{{q:'What is 2+2?',choices:['A: 3','B: 4','C: 5','D: 6'],answer:'B',hint:'math'}}];
setTimeout(function(){{STATE='B';showQ();}},2800);
loop();
if(autoLand >= 0) {{
  spinning = true;
  var targetAngle = (2*Math.PI) - (autoLand + 0.5) * arc;
  var extra = targetAngle + (6 + Math.random()*4) * 2 * Math.PI;
  var dur = 4000;
  var startT = performance.now(), startA = angle;
  (function autoAnim(now) {{
    var el = now - startT, p = Math.min(el/dur, 1);
    var ease = 1 - Math.pow(1-p, 4);
    angle = startA + extra * ease;
    draw(angle);
    if(p < 1) requestAnimationFrame(autoAnim);
    else {{
      spinning = false;
      var res = document.getElementById('result');
      res.textContent = emojis[autoLand] + ' ' + labels[autoLand];
      res.style.color = colors[autoLand];
      requestAnimationFrame(idle);
    }}
  }})(performance.now());
}}
</script></body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL GAME ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def detect_game_mode(universe: str) -> str:
    l = universe.lower()
    if any(k in l for k in ['dragon ball','dbz','saiyan','naruto','bleach','demon slayer','one piece','attack on titan','jujutsu','fairy tail','hunter x hunter','fullmetal','my hero','chainsaw man','black clover','sword art','tokyo ghoul','berserk','mob psycho','one punch','seven deadly','fire force']):
        return 'FIGHTER'
    if any(k in l for k in ['pokemon','genshin','zelda','final fantasy','fire emblem','undertale','persona','elden ring','dark souls','skyrim','witcher','stardew','animal crossing','xenoblade','tales of','dragon quest','chrono','ff7','wow','world of warcraft','runescape','league of','dota','diablo','baldur','d&d']):
        return 'RPG'
    if any(k in l for k in ['mario','sonic','kirby','donkey kong','crash bandicoot','rayman','celeste','hollow knight','cuphead','megaman','castlevania','metroid','spyro','yoshi','super mario','shovel knight']):
        return 'PLATFORM'
    if any(k in l for k in ['call of duty','cod','halo','fortnite','valorant','overwatch','apex','pubg','counter strike','battlefield','doom','borderlands','destiny','warzone','rainbow six','metal gear','resident evil','bioshock','far cry']):
        return 'SHOOTER'
    if any(k in l for k in ['harry potter','hogwarts','wizard','lord of the rings','tolkien','magic the gathering','hearthstone','fantasy','narnia','mage','sorcerer','merlin','fable','mistborn','sanderson']):
        return 'MAGIC'
    if any(k in l for k in ['star wars','nasa','astronaut','space','galaxy','cosmos','marvel','avengers','dc comics','superman','batman','guardians','thor','iron man','spider man','x-men','transformers','gundam','evangelion','star trek','mass effect']):
        return 'COSMIC'
    if any(k in l for k in ['football','basketball','soccer','baseball','tennis','golf','nba','nfl','mlb','nhl','fifa','cricket','rugby','boxing','mma','ufc','olympics','formula 1','f1','nascar','racing']):
        return 'SPORTS'
    if any(k in l for k in ['mortal kombat','street fighter','tekken','smash bros','king of fighters','guilty gear','injustice','fighting game','brawl']):
        return 'BRAWL'
    if any(k in l for k in ['minecraft','roblox','terraria','starcraft','civilization','age of empires','tycoon','factory','craft','sandbox','factorio']):
        return 'BUILDER'
    if any(k in l for k in ['music','band','rock','hip hop','rap','jazz','classical','kpop','pop','artist','singer']):
        return 'COSMIC'
    if any(k in l for k in ['history','ancient','rome','egypt','medieval','war','world war','napoleon','viking','samurai','pirate']):
        return 'BRAWL'
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
    return {"mode":mode,"arena_name":f"The {universe} Arena","arena_desc":"A legendary battlefield forged from pure determination.","arena_colors":["#111122","#222244","#333366"],"player_title":"Champion","player_attacks":["Power Blast","Energy Wave","Ultimate Strike","Final Form Attack","Infinite Force"],"enemy_name":f"{universe} Boss","enemy_title":"The Final Obstacle","enemy_color":"#CC2222","enemy_attacks":["Dark Blast","Shadow Strike","Void Wave"],"enemy_phases":["Phase 1","Phase 2 — ENRAGED","Final Phase — ULTIMATE"],"win_quote":"Victory belongs to those who never stop learning!","lose_quote":"The enemy grows stronger. Study more and return.","questions":questions[:q_count]}

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
    prompt = f"""You are a game designer for "30 Second Infiniteverse".
Universe: "{universe}" | Game Mode: {mode} | Subject: {subject} | Tier: {tier}

Return ONLY valid JSON (no markdown):
{{"mode":"{mode}","arena_name":"short name","arena_desc":"1 sentence","arena_colors":["#h1","#h2","#h3"],"player_title":"title","player_attacks":["A1","A2","A3","A4","A5"],"enemy_name":"enemy","enemy_title":"rank","enemy_color":"#hex","enemy_attacks":["E1","E2","E3"],"enemy_phases":["P1","P2","P3"],"win_quote":"quote","lose_quote":"quote","player_visual":{{"hair_color":"#hex","hair_style":"spiky/long/short/bald/mohawk/afro/flowing","skin_color":"#hex","outfit_color":"#hex","outfit_secondary":"#hex","weapon":"sword/dual_sword/triple_sword/gun/staff/fists/bow/scythe/wand/ball/none","weapon_color":"#hex","eye_color":"#hex","cape":false,"aura_color":"#hex","body_build":"slim/average/muscular/large"}},"enemy_visual":{{"hair_color":"#hex","hair_style":"...","skin_color":"#hex","outfit_color":"#hex","outfit_secondary":"#hex","weapon":"...","weapon_color":"#hex","eye_color":"#hex","cape":false,"aura_color":"#hex","body_build":"..."}},"questions":[{{"q":"question with {universe} flavor","choices":["A: opt","B: opt","C: opt","D: opt"],"answer":"B","hint":"hint"}}]}}

Player visual = PROTAGONIST of this universe. Enemy = VILLAIN/BOSS. Use iconic colors/weapons.

CHARACTER ART TIER — TIER IS: {tier}
- FREE tier: Generate player_visual and enemy_visual BUT mark them with "tier":"free" — simplified, decent but not detailed. Flat colors, basic outfit, simple weapon. Still recognizable but not elaborate.
- PREMIUM tier: Mark with "tier":"premium" — detailed and polished. Layered outfit colors, signature weapon, expressive features, good shading colors. Clearly better than Free.
- ELITE tier: Mark with "tier":"elite" — LEGENDARY quality. Every detail perfect. Iconic signature look, cape if the character has one, aura, exact weapon, exact color combos from the source material. Maximum expression and detail.

 — READ CAREFULLY:
Each question MUST be a real {subject} education question (actual math, science, history, etc.)
BUT written with {universe} lore as the creative wrapper. The LORE is the flavor, the EDUCATION is the substance.

GOOD EXAMPLE (Naruto + Math):
"Naruto ran 15km every day during his 3-year training arc. How many total kilometres did he run?"
Choices: A: 1,095km  B: 10,950km  C: 16,425km  D: 5,475km  Answer: C  (15×365×3)

GOOD EXAMPLE (Dragon Ball + Science):
"Goku's power level doubles every time he trains for 6 months. If he starts at 9,000, what's his power after 2 years?"
Choices: A: 36,000  B: 72,000  C: 144,000  D: 288,000  Answer: C  (doubles 4 times)

BAD EXAMPLE (pure lore trivia — DO NOT DO THIS):
"What is the name of Naruto's signature move?" — this tests pop culture, not education

Make every question:
- Genuinely solve-able with real {subject} knowledge/skill
- Beautifully written with lore context that makes it feel epic and motivated
- Progressively harder through the set
- Written with energy — make the student FEEL the universe while solving real problems"""
    try:
        resp = client.messages.create(model="claude-sonnet-4-5",max_tokens=2400 if tier=="Elite" else 1800,messages=[{"role":"user","content":prompt}])
        raw = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
        cfg = json.loads(raw)
    except Exception:
        cfg = _fallback_config(universe, mode, subject, q_count)
    max_evo = 9 if tier=="Elite" else (6 if tier=="Premium" else 3)
    all_evos = evolutions_by_mode.get(mode, evolutions_by_mode["AUTO"])
    cfg["evolutions"] = all_evos[:max_evo]
    cfg["subject"] = subject; cfg["universe"] = universe; cfg["tier"] = tier; cfg["mode"] = mode
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# ADDICTION PSYCHOLOGY — REWARD SYSTEMS
# ─────────────────────────────────────────────────────────────────────────────
def variable_reward(base: float) -> tuple:
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
    if real_pct < 0.85: return random.uniform(0.85, 0.92)
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
            weeks = streak // 7
            # ── MASSIVE WEEKLY REWARD ──────────────────────────────────────
            bonus_gold = 150 * weeks          # scales with how many weeks done
            bonus_spins = 5 + weeks           # more spins each week
            bonus_eggs = 2                    # always 2 eggs
            st.session_state.gold       += bonus_gold
            st.session_state.spins_left += bonus_spins
            st.session_state.incubator_eggs += bonus_eggs
            st.session_state.xp         += 500 * weeks
            st.session_state.level = 1 + st.session_state.xp // 100
            st.session_state["weekly_reward_pending"] = {
                "weeks": weeks, "gold": bonus_gold,
                "spins": bonus_spins, "eggs": bonus_eggs, "xp": 500 * weeks
            }
            msg = f"🏆 WEEK {weeks} COMPLETE — LEGENDARY REWARD INCOMING!"
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
# AI STORY + ACHIEVEMENT GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_story_chapter(theme, chapter, prev_story, client):
    try:
        is_milestone = (chapter % 5 == 0)
        prompt = f"""Universe: "{theme}". Chapter {chapter}.
Previous: {prev_story[-200:] if prev_story else "Beginning."}
STRICT RULES — VIOLATING ANY = FAILURE:
- MAXIMUM 3 sentences. If you write 4+ sentences you have FAILED.
- Each sentence MAX 25 words.
- {"TWIST: One shocking revelation that changes everything." if is_milestone else "CLIFFHANGER: End on something impossible and unresolved."}
- Use SPECIFIC {theme} character names, locations, powers.
- End with ... (three dots, mandatory)
- No titles. No labels. Raw text only."""

        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=350, messages=[{"role":"user","content":prompt}])
        text = msg.content[0].text.strip()
        # Ensure it always ends with ...
        if not text.endswith("..."):
            text = text.rstrip(".") + "..."
        return text
    except:
        return f"The {theme} universe holds its breath — something that should not exist has just opened its eyes, and it already knows your name..."

def generate_universe_achievements(theme, client):
    try:
        existing_count = len(st.session_state.get("universe_achievements", []))
        prompt = f"""Generate 10 NEW creative achievements for "{theme}" connected to studying.
These are achievements #{existing_count+1} through #{existing_count+10}.
CRITICAL: Each must have a DIFFERENT unlock condition — mix: currency earned, battles won, streaks, eggs hatched, story chapters, spinner wins, levels, secrets collected.
Each must reference specific {theme} lore.
Return ONLY raw JSON array: [{{"name":"emoji + 2-4 words","desc":"one sentence"}}]"""
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=1200, messages=[{"role":"user","content":prompt}])
        raw = re.sub(r"```(?:json)?", "", msg.content[0].text.strip()).strip().rstrip("`")
        return json.loads(raw)[:10]
    except:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# MONSTER + EGG SYSTEMS
# ─────────────────────────────────────────────────────────────────────────────
EGG_RARITIES = [
    {"rarity":"Common",    "color":"#aaaaaa","chance":55,"reward_mult":1},
    {"rarity":"Rare",      "color":"#4488ff","chance":28,"reward_mult":2},
    {"rarity":"Epic",      "color":"#aa44ff","chance":13,"reward_mult":4},
    {"rarity":"Legendary", "color":"#FFD700","chance":4, "reward_mult":10},
]

def hatch_egg(theme):
    roll = random.randint(1,100); cumulative = 0; chosen = EGG_RARITIES[-1]
    for r in EGG_RARITIES:
        cumulative += r["chance"]
        if roll <= cumulative: chosen = r; break
    names = {"Common":[f"{theme} Scout",f"{theme} Grunt"],"Rare":[f"{theme} Hunter",f"{theme} Phantom"],"Epic":[f"{theme} Warlord",f"{theme} Specter"],"Legendary":[f"{theme} God",f"{theme} Titan"]}
    name = random.choice(names.get(chosen["rarity"],[f"{theme} Creature"]))
    return {"name":name,"rarity":chosen["rarity"],"color":chosen["color"],"reward_mult":chosen["reward_mult"]}


# ─────────────────────────────────────────────────────────────────────────────
# API + JSON HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_claude_client():
    try: return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    except Exception: return None

# ─────────────────────────────────────────────────────────────────────────────
# SUPABASE — PERSISTENT DATABASE
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    if not SUPABASE_AVAILABLE: return None
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

def db_save(user_name: str, theme: str):
    """Save full session state to Supabase."""
    sb = get_supabase()
    if not sb or not user_name: return
    try:
        payload = {
            "user_name": user_name.lower().strip(),
            "theme": theme,
            "gold": float(st.session_state.get("gold", 0)),
            "xp": int(st.session_state.get("xp", 0)),
            "level": int(st.session_state.get("level", 1)),
            "total_missions": int(st.session_state.get("total_missions", 0)),
            "study_streak": int(st.session_state.get("study_streak", 0)),
            "last_active_date": st.session_state.get("last_active_date"),
            "battles_fought": int(st.session_state.get("battles_fought", 0)),
            "battles_won": int(st.session_state.get("battles_won", 0)),
            "eggs_hatched": int(st.session_state.get("eggs_hatched", 0)),
            "incubator_eggs": int(st.session_state.get("incubator_eggs", 0)),
            "spinner_wins": int(st.session_state.get("spinner_wins", 0)),
            "story_chapter": int(st.session_state.get("story_chapter", 0)),
            "story_log": json.dumps(st.session_state.get("story_log", [])),
            "secret_queue": json.dumps(st.session_state.get("secret_queue", [])),
            "unlocked_achievements": json.dumps(list(st.session_state.get("unlocked_achievements", set()))),
            "universe_achievements": json.dumps(st.session_state.get("universe_achievements", [])),
            "hatched_monsters": json.dumps(st.session_state.get("hatched_monsters", [])),
            "sub_tier": st.session_state.get("sub_tier", "Free"),
            "sub_multiplier": int(st.session_state.get("sub_multiplier", 1)),
            "shield_bought": bool(st.session_state.get("shield_bought", False)),
            "booster_bought": bool(st.session_state.get("booster_bought", False)),
            "legendary_hatched": bool(st.session_state.get("legendary_hatched", False)),
            "last_spin_time": st.session_state.get("last_spin_time"),
            "spins_left": int(st.session_state.get("spins_left", 0)),
            "game_mode": st.session_state.get("game_mode", "chill"),
            "vibe_color": st.session_state.get("vibe_color", "#FFD700"),
            "bg_color": st.session_state.get("bg_color", "#ffffff"),
            "micro_timer_seconds": int(st.session_state.get("micro_timer_seconds", 30)),
            "tribunal_due_time": st.session_state.get("tribunal_due_time"),
            "pending_gold": float(st.session_state.get("pending_gold", 0)),
            "pending_xp": int(st.session_state.get("pending_xp", 0)),
            "tribunal_missions_since": int(st.session_state.get("tribunal_missions_since", 0)),
            "needs_verification": bool(st.session_state.get("needs_verification", False)),
            "updated_at": _dt.datetime.utcnow().isoformat(),
            "password_hash": st.session_state.get("password_hash", ""),
            "leaderboard_visible": bool(st.session_state.get("leaderboard_visible", True)),
            "email": st.session_state.get("user_email", "").lower().strip().strip("_"),
        }
        # save_key = name_universe_mode (unique per combo)
        _mode  = st.session_state.get("game_mode", "chill") or "chill"
        _theme_key = (theme or "infinitepower").lower().strip().replace(" ","_")[:30]
        _save_key  = f"{user_name.lower().strip()}_{_theme_key}_{_mode}"
        payload["save_key"] = _save_key
        try:
            sb.table("players").upsert(payload, on_conflict="save_key").execute()
        except Exception:
            # Fallback: upsert on user_name for old saves without save_key
            sb.table("players").upsert(payload, on_conflict="user_name").execute()
    except Exception as e:
        pass  # Silent fail — never break the app for a DB issue

def db_load(user_name: str, theme: str = "", mode: str = "") -> dict | None:
    """Load session state from Supabase. Uses save_key if theme+mode provided, else falls back to user_name."""
    sb = get_supabase()
    if not sb or not user_name: return None
    try:
        if theme and mode:
            _theme_key = (theme or "infinitepower").lower().strip().replace(" ","_")[:30]
            _save_key  = f"{user_name.lower().strip()}_{_theme_key}_{mode}"
            res = sb.table("players").select("*").eq("save_key", _save_key).execute()
            if res.data: return res.data[0]
        # Fallback: load any save matching user_name (first one found)
        res = sb.table("players").select("*").eq("user_name", user_name.lower().strip()).execute()
        if not res.data: return None
        row = res.data[0]
        return row
    except Exception:
        return None

def db_apply(row: dict):
    """Apply a loaded DB row into session state."""
    st.session_state.gold              = float(row.get("gold", 10))
    st.session_state.xp               = int(row.get("xp", 0))
    st.session_state.level            = int(row.get("level", 1))
    st.session_state.total_missions   = int(row.get("total_missions", 0))
    st.session_state.study_streak     = int(row.get("study_streak", 0))
    st.session_state.last_active_date = row.get("last_active_date")
    st.session_state.battles_fought   = int(row.get("battles_fought", 0))
    st.session_state.battles_won      = int(row.get("battles_won", 0))
    st.session_state.eggs_hatched     = int(row.get("eggs_hatched", 0))
    st.session_state.incubator_eggs   = int(row.get("incubator_eggs", 0))
    st.session_state.spinner_wins     = int(row.get("spinner_wins", 0))
    st.session_state.story_chapter    = int(row.get("story_chapter", 0))
    st.session_state.sub_tier         = row.get("sub_tier", "Free")
    st.session_state.sub_multiplier   = int(row.get("sub_multiplier", 1))
    st.session_state.shield_bought    = bool(row.get("shield_bought", False))
    st.session_state.booster_bought   = bool(row.get("booster_bought", False))
    st.session_state.legendary_hatched= bool(row.get("legendary_hatched", False))
    st.session_state.last_spin_time   = row.get("last_spin_time")
    st.session_state.spins_left       = int(row.get("spins_left", 0))
    st.session_state.game_mode        = row.get("game_mode", "chill")
    # vibe_color is set by resolve_universe, not db_apply
    st.session_state.bg_color         = row.get("bg_color", "#ffffff")
    st.session_state.micro_timer_seconds = int(row.get("micro_timer_seconds", 30))
    try: st.session_state.story_log   = json.loads(row.get("story_log", "[]"))
    except: st.session_state.story_log = []
    try: st.session_state.secret_queue = json.loads(row.get("secret_queue", "[]"))
    except: st.session_state.secret_queue = []
    try: st.session_state.unlocked_achievements = set(json.loads(row.get("unlocked_achievements", "[]")))
    except: st.session_state.unlocked_achievements = set()
    try: st.session_state.universe_achievements = json.loads(row.get("universe_achievements", "[]"))
    except: st.session_state.universe_achievements = []
    try: st.session_state.hatched_monsters = json.loads(row.get("hatched_monsters", "[]"))
    except: st.session_state.hatched_monsters = []
    st.session_state.secrets_seen = len(st.session_state.secret_queue)
    st.session_state.opening_story_shown = len(st.session_state.story_log) > 0
    st.session_state.password_hash = row.get("password_hash", "")
    st.session_state.leaderboard_visible = bool(row.get("leaderboard_visible", True))
    st.session_state.user_email = row.get("email", "")
    st.session_state.tribunal_due_time = None
    st.session_state.pending_gold = 0.0
    st.session_state.pending_xp = 0
    st.session_state.tribunal_missions_since = 0
    st.session_state.tribunal_seconds_done = 0
    st.session_state.needs_verification = False

def db_get_leaderboard(limit: int = 10) -> list:
    """Get top players by total missions."""
    sb = get_supabase()
    if not sb: return []
    try:
        res = sb.table("players").select("user_name,total_missions,study_streak,level,theme,sub_tier").eq("leaderboard_visible", True).order("total_missions", desc=True).limit(limit).execute()
        return res.data or []
    except Exception:
        return []

def db_save_feedback(fb_type: str, message: str, name: str, universe: str):
    """Save user feedback to Supabase feedback table."""
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("feedback").insert({
            "fb_type": fb_type,
            "message": message,
            "name": name,
            "universe": universe,
            "submitted_at": _dt.datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass

def send_reset_email(to_email: str, name: str, token: str) -> bool:
    """Send password reset email via Gmail SMTP."""
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    try:
        gmail_user = st.secrets.get("GMAIL_USER", "")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD", "")
        if not gmail_user or not gmail_pass: return False
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🌌 30 Second Infiniteverse — Password Reset"
        msg["From"]    = gmail_user
        msg["To"]      = to_email
        html = f"""
        <div style="background:#000;padding:40px;font-family:'Space Mono',monospace;max-width:500px;margin:0 auto;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;color:#FFD700;letter-spacing:4px;text-align:center;margin-bottom:8px;">
                30 SECOND INFINITEVERSE
            </div>
            <div style="color:#ffffff;font-size:18px;text-align:center;margin-bottom:24px;">
                Password Reset Request
            </div>
            <div style="background:#111;border:2px solid #FFD700;border-radius:14px;padding:24px;margin-bottom:20px;">
                <p style="color:#ffffff;font-size:13px;line-height:1.8;">Hey <b style="color:#FFD700">{name}</b>,</p>
                <p style="color:#ffffff;font-size:13px;line-height:1.8;">Someone requested a password reset for your account.
                If that was you, use this code:</p>
                <div style="background:#000;border:3px solid #FFD700;border-radius:10px;padding:20px;text-align:center;margin:16px 0;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFD700;letter-spacing:8px;">{token}</div>
                    <div style="color:#888;font-size:11px;margin-top:8px;">Valid for 30 minutes</div>
                </div>
                <p style="color:#888;font-size:11px;line-height:1.8;">Enter this code in the app under "Forgot Password?" to reset your password.
                If you didn't request this, ignore this email — your account is safe.</p>
            </div>
            <div style="text-align:center;color:#555;font-size:10px;">30 Second Infiniteverse · Powered by AI</div>
        </div>"""
        msg.attach(MIMEText(html, "html"))
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
            s.login(gmail_user, gmail_pass)
            s.sendmail(gmail_user, to_email, msg.as_string())
        return True
    except Exception:
        return False

def db_save_image(key: str, url: str):
    """Cache a generated image URL in Supabase."""
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("images").upsert({"key": key, "url": url, "created_at": _dt.datetime.utcnow().isoformat()}, on_conflict="key").execute()
    except Exception:
        pass

def db_get_image(key: str) -> str | None:
    """Retrieve a cached image URL."""
    sb = get_supabase()
    if not sb: return None
    try:
        res = sb.table("images").select("url").eq("key", key).execute()
        if res.data: return res.data[0]["url"]
    except Exception:
        pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
# FLUX IMAGE GENERATION (via Replicate)
# ─────────────────────────────────────────────────────────────────────────────
def generate_image(prompt: str, cache_key: str = None, width: int = 768, height: int = 768) -> str | None:
    """Generate an image with FLUX. Returns URL or None. Uses cache if available."""
    # Check cache first
    if cache_key:
        cached = db_get_image(cache_key)
        if cached: return cached
    if not REPLICATE_AVAILABLE: return None
    try:
        import replicate as _rep
        api_token = st.secrets.get("REPLICATE_KEY", "")
        if not api_token: return None
        client = _rep.Client(api_token=api_token)
        output = client.run(
            "black-forest-labs/flux-schnell",
            input={"prompt": prompt, "width": width, "height": height, "num_outputs": 1, "output_format": "webp"}
        )
        url = str(output[0]) if output else None
        if url and cache_key:
            db_save_image(cache_key, url)
        return url
    except Exception:
        return None

def generate_universe_banner(theme: str, color: str) -> str | None:
    """Generate a cinematic banner for the universe gateway screen."""
    cache_key = f"banner_{theme.lower().replace(' ', '_')[:40]}"
    prompt = (
        f"Cinematic ultra-wide banner art for '{theme}' universe. "
        f"Epic landscape, dramatic lighting, dominant color {color}, "
        f"hyper-detailed, 8K, moody atmospheric, no text, no UI elements, "
        f"professional concept art, stunning composition"
    )
    return generate_image(prompt, cache_key, width=1024, height=384)

def generate_character_portrait(theme: str, vis: dict, is_enemy: bool = False) -> str | None:
    """Generate a character portrait for battle screen."""
    role = "villain boss enemy" if is_enemy else "hero protagonist player character"
    hair = vis.get("hair_color", "#000"), vis.get("hair_style", "short")
    outfit = vis.get("outfit_color", "#000")
    weapon = vis.get("weapon", "none")
    build = vis.get("body_build", "average")
    cache_key = f"char_{theme.lower().replace(' ','_')[:30]}_{'enemy' if is_enemy else 'player'}"
    prompt = (
        f"Full body character portrait of the {role} from '{theme}'. "
        f"{build} build, {hair[1]} {hair[0]} hair, {outfit} outfit, wielding {weapon}. "
        f"Anime/game art style, ultra detailed, dramatic lighting, transparent background, "
        f"professional illustration, no text"
    )
    return generate_image(prompt, cache_key, width=512, height=768)

def generate_achievement_badge(achievement_name: str, theme: str, color: str) -> str | None:
    """Generate a badge image for an achievement."""
    clean_name = re.sub(r'[^a-z0-9]', '_', achievement_name.lower())[:30]
    cache_key = f"badge_{clean_name}"
    prompt = (
        f"Circular achievement badge icon for '{achievement_name}' in the '{theme}' universe. "
        f"Glowing {color} accent, dark background, ornate border, emblematic symbol, "
        f"game UI art style, high detail, no text"
    )
    return generate_image(prompt, cache_key, width=256, height=256)

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
# LORE PROMPT
# ─────────────────────────────────────────────────────────────────────────────
LORE_PROMPT = """You are the ULTIMATE authority on every game, anime, manga, sport, team, brand, movie, show, book, music genre, artist, fashion brand, historical era, cultural phenomenon in human history.

Universe: "{theme}"

CRITICAL RULES:
1. ATOMIC SPECIFICITY: If given a CHARACTER — use THAT character's EXACT moves, weapons, colors. Zoro = green hair, 3 swords. Tanjiro = water breathing, checkered haori. Kobe = fadeaway, #24.
2. NEVER be generic. EVERY field must drip with universe-specific detail.
3. CURRENCY RULE: Use the exact in-universe currency (One Piece=Berries, Naruto=Ryo, Dragon Ball=Zeni, Harry Potter=Galleons, Star Wars=Galactic Credits, Pokemon=PokeDollars, Minecraft=Emeralds).

Return ONLY a single raw JSON object. No markdown.

Fields: "currency", "color" (most iconic hex), "shield_name" (exact defensive ability/armor), "booster_name" (exact speed ability), "shield_flavor" (12 words max), "booster_flavor" (12 words max), "description" (12 words max, captures the SOUL), "battle_style" (shooter/turnbased/reaction/rpgclick/survival/rhythm/racing/trivia), "player_visual" (hair_color, hair_style, skin_color, outfit_color, outfit_secondary, weapon, weapon_color, eye_color, cape, cape_color, aura_color, body_build), "enemy_visual" (same), "lore_achievements" (array of 10 objects with name+desc, DIFFERENT conditions — mix currency/battles/streaks/eggs/chapters/spinner/levels/secrets).

Return: {{"currency":"...","color":"#RRGGBB","shield_name":"...","booster_name":"...","description":"...","shield_flavor":"...","booster_flavor":"...","battle_style":"...","player_visual":{{...}},"enemy_visual":{{...}},"lore_achievements":[...]}}"""


# ─────────────────────────────────────────────────────────────────────────────
# HARD FALLBACKS
# ─────────────────────────────────────────────────────────────────────────────
HARD_FALLBACKS = {
    "minecraft":{"currency":"Emeralds","color":"#5D9E35","shield_name":"Protection IV Netherite Chestplate","booster_name":"Ender Pearl Warp","description":"A boundless world of blocks where creativity and survival collide.","shield_flavor":"Absorbs almost any damage with enchanted netherite armor.","booster_flavor":"Teleports you instantly wherever the pearl lands.","battle_style":"random"},
    "fortnite":{"currency":"V-Bucks","color":"#BEFF00","shield_name":"Shield Bubble","booster_name":"Shockwave Grenade","description":"100 players drop in. Only one walks out.","shield_flavor":"Creates an impenetrable dome that blocks all incoming fire.","booster_flavor":"Launches you through the air at explosive speed.","battle_style":"shooter"},
    "roblox":{"currency":"Robux","color":"#E8272A","shield_name":"Force Field","booster_name":"Speed Coil","description":"An infinite universe of user-built worlds with zero limits.","shield_flavor":"Wraps you in an untouchable glowing force bubble.","booster_flavor":"Multiplies your movement speed to inhuman levels instantly.","battle_style":"random"},
    "pokemon":{"currency":"PokeDollars","color":"#FFCB05","shield_name":"Protect","booster_name":"Extreme Speed","description":"Catch, train, and battle creatures across endless adventure.","shield_flavor":"A perfect barrier that blocks any single incoming attack.","booster_flavor":"Moves so fast it always strikes first, no exceptions.","battle_style":"turnbased"},
    "valorant":{"currency":"VP","color":"#FF4655","shield_name":"Sage Barrier Orb","booster_name":"Jett Updraft","description":"Precise gunplay meets deadly abilities in a tactical shooter.","shield_flavor":"Raises a solid ice wall that stops bullets cold.","booster_flavor":"Launches Jett upward on a burst of wind.","battle_style":"shooter"},
    "one piece":{"currency":"Berries","color":"#E8372B","shield_name":"Armament Haki","booster_name":"Gear Second","description":"A pirate's odyssey chasing the ultimate treasure.","shield_flavor":"Coats your body in invisible armor that blocks Devil Fruits.","booster_flavor":"Pumps blood at rocket speed to move like lightning.","battle_style":"turnbased"},
    "naruto":{"currency":"Ryo","color":"#FF6600","shield_name":"Susanoo Ribcage","booster_name":"Flying Thunder God","description":"From outcast to the strongest — the ninja's path.","shield_flavor":"A giant ribcage of chakra that absorbs catastrophic damage.","booster_flavor":"Teleports instantly to any marked location across any distance.","battle_style":"turnbased"},
    "dragon ball":{"currency":"Zeni","color":"#FF8C00","shield_name":"Barrier Blast","booster_name":"Instant Transmission","description":"Warriors transcend all limits in an eternal quest for power.","shield_flavor":"A ki barrier that explodes outward destroying everything nearby.","booster_flavor":"Locks onto any ki signature and teleports there instantly.","battle_style":"turnbased"},
    "demon slayer":{"currency":"Yen","color":"#22AA44","shield_name":"Total Concentration Breathing","booster_name":"Thunder Breathing First Form","description":"Demon hunters clash with ancient evil using breathing and will.","shield_flavor":"Fills every cell with oxygen giving superhuman endurance instantly.","booster_flavor":"A single lightning-fast slash that crosses any distance instantly.","battle_style":"turnbased"},
    "attack on titan":{"currency":"Eldian Marks","color":"#8B6914","shield_name":"Hardening Crystal","booster_name":"ODM Gear Swing","description":"Humanity fights back against titans behind crumbling walls.","shield_flavor":"Crystallizes your titan skin into unbreakable diamond-hard armor.","booster_flavor":"Launches grappling hooks and swings at terrifying speed.","battle_style":"survival"},
    "jujutsu kaisen":{"currency":"Cursed Tokens","color":"#6600CC","shield_name":"Infinity Barrier","booster_name":"Divergent Fist","description":"Cursed energy battles rage beneath everyday life.","shield_flavor":"Slows everything approaching you to an infinite standstill.","booster_flavor":"Cursed energy explodes out a split second after impact.","battle_style":"turnbased"},
    "my hero academia":{"currency":"Hero Credits","color":"#1DA462","shield_name":"Full Cowl Armor","booster_name":"One For All Smash","description":"Heroes and villains clash where quirks define destiny.","shield_flavor":"Channels One For All through every cell for full protection.","booster_flavor":"Concentrates every ounce of One For All into one devastating hit.","battle_style":"turnbased"},
    "f1":{"currency":"Championship Points","color":"#FF1801","shield_name":"Halo Titanium Cockpit","booster_name":"DRS Activation","description":"The pinnacle of motorsport where speed and nerve collide.","shield_flavor":"A titanium halo that has saved drivers' lives at 300kph.","booster_flavor":"Opens the rear wing and adds 15kph of pure straight-line speed.","battle_style":"reaction"},
    "nba":{"currency":"VC","color":"#EE6730","shield_name":"Lockdown Defender","booster_name":"Fast Break","description":"The greatest basketball league where legends are born nightly.","shield_flavor":"Shuts down any offensive player with suffocating on-ball pressure.","booster_flavor":"Pushes the pace before the defense can set up.","battle_style":"reaction"},
    "harry potter":{"currency":"Galleons","color":"#740001","shield_name":"Protego Totalum","booster_name":"Apparition","description":"A world of magic and courage hidden behind ordinary life.","shield_flavor":"Casts a full protective enchantment over an entire building.","booster_flavor":"Vanishes from one location and reappears anywhere instantly.","battle_style":"turnbased"},
    "star wars":{"currency":"Galactic Credits","color":"#FFE81F","shield_name":"Lightsaber Deflect","booster_name":"Force Speed","description":"A galaxy far away locked in eternal war between light and dark.","shield_flavor":"Spins the lightsaber so fast it creates an impenetrable energy shield.","booster_flavor":"Channels the Force to move at superhuman blinding speed.","battle_style":"turnbased"},
    "marvel":{"currency":"Stark Credits","color":"#ED1D24","shield_name":"Vibranium Shield","booster_name":"Repulsor Boost","description":"Earth's mightiest heroes stand against total annihilation.","shield_flavor":"Absorbs and redirects any kinetic energy thrown at it.","booster_flavor":"Fires repulsor blasts downward to launch you across the sky.","battle_style":"turnbased"},
    "halo":{"currency":"CR","color":"#00B4D8","shield_name":"Energy Shield","booster_name":"Active Camo","description":"Master Chief stands as humanity's last line against the Covenant.","shield_flavor":"Regenerating energy shield absorbs hits and recovers automatically.","booster_flavor":"Turns completely invisible for a limited but deadly window.","battle_style":"shooter"},
    "call of duty":{"currency":"CoD Points","color":"#FF6600","shield_name":"Trophy System","booster_name":"Tactical Sprint","description":"The world's most intense military shooter — no mercy in ranked.","shield_flavor":"Intercepts and destroys incoming grenades and projectiles automatically.","booster_flavor":"A full-speed burst sprint that covers ground in seconds.","battle_style":"shooter"},
    "apex legends":{"currency":"Apex Coins","color":"#DA292A","shield_name":"Evo Shield","booster_name":"Pathfinder Grapple","description":"Legends compete in a brutal frontier battle royale.","shield_flavor":"Absorbs damage and evolves into a stronger shield automatically.","booster_flavor":"Launches a grappling hook that swings you anywhere instantly.","battle_style":"shooter"},
    "elden ring":{"currency":"Runes","color":"#C8A951","shield_name":"Erdtree Greatshield","booster_name":"Bloodhound Step","description":"A shattered world of demigods in pursuit of the Elden Ring.","shield_flavor":"A colossal golden shield blessed by the Erdtree itself.","booster_flavor":"A ghost-step dodge that leaves behind a phantom decoy.","battle_style":"turnbased"},
    "zelda":{"currency":"Rupees","color":"#5ACD3D","shield_name":"Hylian Shield","booster_name":"Ocarina Serenade","description":"The hero of time journeys through Hyrule to defeat darkness.","shield_flavor":"The legendary shield that has never been destroyed in battle.","booster_flavor":"A magical song that warps you instantly to any location.","battle_style":"turnbased"},
    "overwatch":{"currency":"Overwatch Coins","color":"#F99E1A","shield_name":"Reinhardt Barrier","booster_name":"Lucio Speed Boost","description":"Colorful heroes battle across a futuristic world in conflict.","shield_flavor":"A massive energy barrier protecting everyone standing behind it.","booster_flavor":"An area aura that permanently speeds up your entire team.","battle_style":"shooter"},
    "nike":{"currency":"NikeCash","color":"#111111","shield_name":"Air Max Cushioning","booster_name":"ReactX Foam Propulsion","description":"Just Do It — where athletic performance meets street culture.","shield_flavor":"Absorbs impact forces like they never happened at all.","booster_flavor":"Stores and returns energy in every step for explosive speed.","battle_style":"reaction"},
    "spotify":{"currency":"Streams","color":"#1DB954","shield_name":"Noise Cancelling","booster_name":"Algorithmic Surge","description":"Music for everyone — three million songs, infinite discovery.","shield_flavor":"Blocks out every distraction leaving only pure focus.","booster_flavor":"The algorithm finds your next obsession before you even search.","battle_style":"rhythm"},
    "gta":{"currency":"GTA$","color":"#F4B000","shield_name":"Body Armor","booster_name":"Rocket Boost","description":"Power, money, and chaos rule the streets.","shield_flavor":"Military-grade body armor absorbing bullets like they are nothing.","booster_flavor":"Fires a rocket booster launching you forward at insane speed.","battle_style":"shooter"},
    "k-pop":{"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma.","shield_flavor":"Ten thousand lightsticks form a wall of pure fan power.","booster_flavor":"Drops the new single and breaks the entire internet instantly.","battle_style":"rhythm"},
    "kpop":{"currency":"Fancash","color":"#FF6699","shield_name":"Lightstick Shield","booster_name":"Comeback Drop","description":"The global phenomenon of precision performance and charisma.","shield_flavor":"Ten thousand lightsticks form a wall of pure fan power.","booster_flavor":"Drops the new single and breaks the entire internet instantly.","battle_style":"rhythm"},
}

REQUIRED_KEYS = ["currency","color","shield_name","booster_name","description"]

def get_fallback(theme):
    t = theme.lower().strip()
    if t in HARD_FALLBACKS: return HARD_FALLBACKS[t]
    for key, data in HARD_FALLBACKS.items():
        if key in t or t in key: return data
    return {"currency":"Titan Shards","color":"#00FFCC","shield_name":"Kinetic Barrier","booster_name":"Void Dash","description":"A realm of boundless power and infinite possibility.","shield_flavor":"Converts all incoming kinetic energy into pure protective force.","booster_flavor":"Rips a hole in space and steps through it instantly.","battle_style":"random"}


# ─────────────────────────────────────────────────────────────────────────────
# RESOLVE UNIVERSE
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
            message = client.messages.create(model="claude-sonnet-4-5", max_tokens=1800, messages=[{"role":"user","content":safe_prompt}])
            raw = message.content[0].text.strip()
            if '"blocked"' in raw and "true" in raw.lower():
                return {"safe": False, "reason": "Our AI detected this theme isn't appropriate. Try a game, anime, sport, movie, or anything you love! 🌌", "data": None}
            data = extract_json(raw)
            if data and all(k in data for k in REQUIRED_KEYS):
                if not re.match(r"^#[0-9A-Fa-f]{6}$", data.get("color","")): data["color"] = "#FFD700"
                data.setdefault("shield_flavor","An ability forged in the heart of this universe.")
                data.setdefault("booster_flavor","Speed that defies every known law of physics.")
                data.setdefault("battle_style","random")
                data.setdefault("player_visual",{})
                data.setdefault("enemy_visual",{})
                data.setdefault("lore_achievements",[])
                data["shield_effect"] = SHIELD_EFFECT; data["booster_effect"] = BOOSTER_EFFECT
                return {"safe": True, "data": data}
        except Exception: pass
    data = get_fallback(cleaned_theme)
    data["shield_effect"] = SHIELD_EFFECT; data["booster_effect"] = BOOSTER_EFFECT
    data["player_visual"] = {}; data["enemy_visual"] = {}
    ach_client = get_claude_client()
    if ach_client:
        data["lore_achievements"] = generate_universe_achievements(cleaned_theme, ach_client)
    if not data.get("lore_achievements"):
        curr = data.get("currency","Shards")
        actions = [
            {"name":f"⚡ First {cleaned_theme} Step","desc":f"Complete your very first mission in {cleaned_theme}."},
            {"name":f"💰 {cleaned_theme} Payday","desc":f"Earn {random.choice([25,50,100])} {curr} through pure grind."},
            {"name":f"⚔️ {cleaned_theme} Fighter","desc":f"Win {random.choice([1,3,5])} battles in the arena."},
            {"name":f"🔥 {cleaned_theme} Flame","desc":f"Hold a {random.choice([3,5,7])}-day study streak."},
            {"name":f"🥚 {cleaned_theme} Collector","desc":f"Hatch {random.choice([2,3,5])} eggs from the incubator."},
            {"name":f"🎰 {cleaned_theme} Gambler","desc":f"Win {random.choice([3,5,8])} spinner prizes."},
            {"name":f"💎 {cleaned_theme} Banker","desc":f"Stack {random.choice([150,250,500])} {curr} in your vault."},
            {"name":f"🐉 {cleaned_theme} Mythic","desc":f"Hatch a Legendary creature from the incubator."},
            {"name":f"📖 {cleaned_theme} Saga","desc":f"Reach Chapter {random.choice([5,8,10])} of your storyline."},
            {"name":f"👑 {cleaned_theme} Conqueror","desc":f"Win {random.choice([10,15,20])} battles total."},
        ]
        random.shuffle(actions)
        data["lore_achievements"] = actions[:10]
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
        "battle_wins": 0, "opening_loot_claimed": False, "unclaimed_boxes": 0,
        "secret_queue": [], "show_secret": None,
        "spinner_available": False, "spinner_wins": 0,
        "first_session": True, "spinner_result": None,
        "story_chapter": 0, "story_log": [],
        "story_twist_pending": False, "opening_story_shown": False,
        "study_streak": 0, "last_active_date": None,
        "streak_shield": False, "spins_left": 0,
        "loot_pending": False, "loot_item": None, "loot_log": [],
        "total_xp_real": 0,
        "universe_achievements": [], "universe_ach_loaded": False,
        "welcome_bonus_applied": False, "battle_subject_chosen": False,
        "last_spin_time": None, "spin_awarded_this_view": False,
        "last_auto_save": None, "password_hash": "", "leaderboard_visible": True, "user_email": "", "gw_page": 1, "ret_saves_found": None, "ret_pass_hash": "", "ret_name": "", "ret_single_save": None,
    })


# ─────────────────────────────────────────────────────────────────────────────
# GATEWAY SCREEN
# ─────────────────────────────────────────────────────────────────────────────
# ── AUTO-RELOAD ON REFRESH via query params ──────────────────────────────────
if st.session_state.user_name is None:
    _qp_name = st.query_params.get("u", "")
    _qp_theme = st.query_params.get("t", "")
    _qp_mode = st.query_params.get("m", "")
    if _qp_name:
        _auto_save = None
        _sb_auto = get_supabase()
        if _sb_auto:
            try:
                _r2 = _sb_auto.table("players").select("*").eq("user_name", _qp_name.lower().strip()).execute()
                if _r2.data: _auto_save = _r2.data[0]
            except: pass
        if _auto_save:
            _auto_theme = _auto_save.get("theme","") or DEFAULT_UNIVERSE_NAME
            with st.spinner(f"🌌 Loading {_auto_theme}..."):
                _auto_result = resolve_universe(_auto_theme)
            if not _auto_result or not _auto_result.get("safe"):
                _auto_result = {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
            _auto_data = _auto_result["data"]
            st.session_state.user_name  = _auto_save.get("user_name", _qp_name)
            st.session_state.game_mode  = _auto_save.get("game_mode","chill") or "chill"
            _asaved_color = _auto_save.get("vibe_color","")
            if _asaved_color and re.match(r'^#[0-9A-Fa-f]{6}$', _asaved_color):
                _auto_data["color"] = _asaved_color
            st.session_state.vibe_color = _auto_data.get("color","#FFD700")
            st.session_state.user_theme = _auto_theme
            st.session_state.world_data = _auto_data
            db_apply(_auto_save)
            st.session_state.vibe_color = _auto_data.get("color","#FFD700")
            st.session_state.user_theme = _auto_theme
            st.session_state.world_data = _auto_data
            st.rerun()
        elif _qp_theme:
            with st.spinner(f"🌌 Reloading {_qp_theme}..."):
                _fallback_result = resolve_universe(_qp_theme)
            if not _fallback_result or not _fallback_result.get("safe"):
                _fallback_result = {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
            _fb_data = _fallback_result["data"]
            st.session_state.user_name = _qp_name
            st.session_state.game_mode = _qp_mode or "chill"
            st.session_state.world_data = _fb_data
            st.session_state.vibe_color = _fb_data.get("color","#FFD700")
            st.session_state.user_theme = _qp_theme
            st.rerun()

if st.session_state.user_name is None:
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap');
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#000!important;color:white!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;}
.block-container{padding:0 1rem 2rem!important;max-width:100%!important;}
[data-testid="stAppViewContainer"]{background:#000!important;}
.star-field{display:none;}
.scanline-wrap{width:100%;height:4px;overflow:hidden;margin-bottom:16px;}
.scanline{width:40%;height:4px;background:linear-gradient(90deg,transparent,#FFD700,transparent);animation:scan-sweep 2s linear infinite;box-shadow:0 0 20px 4px rgba(255,215,0,0.6);}
@keyframes scan-sweep{0%{transform:translateX(-150%);}100%{transform:translateX(400%);}}
.top-badge{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.4);border-radius:99px;padding:8px 24px;font-family:Space Mono,monospace;font-size:11px;letter-spacing:3px;color:#FFD700;text-transform:uppercase;text-align:center;display:table;margin:0 auto 20px;animation:badge-pulse 3s ease-in-out infinite alternate;position:relative;z-index:5;}
@keyframes badge-pulse{0%{box-shadow:0 0 10px rgba(255,215,0,0.2);}100%{box-shadow:0 0 40px rgba(255,215,0,0.6);}}
.gw-main-title{font-family:Bebas Neue,sans-serif;font-size:clamp(72px,14vw,150px);text-align:center;letter-spacing:8px;line-height:0.88;color:#FFD700;animation:title-gold-breathe 4s ease-in-out infinite alternate;margin-bottom:8px;position:relative;z-index:5;}
@keyframes title-gold-breathe{0%{filter:drop-shadow(0 0 10px rgba(255,215,0,0.7)) drop-shadow(0 0 25px rgba(255,200,0,0.5)) drop-shadow(0 0 50px rgba(255,180,0,0.3));transform:scale(1.0);}
100%{filter:drop-shadow(0 0 22px rgba(255,235,100,1.0)) drop-shadow(0 0 55px rgba(255,215,0,0.9)) drop-shadow(0 0 110px rgba(255,200,0,0.6));transform:scale(1.018);}}
.gw-subtitle{font-family:Orbitron,sans-serif;font-size:clamp(12px,1.8vw,18px);text-align:center;letter-spacing:5px;color:#ffffff;text-transform:uppercase;margin-bottom:20px;text-shadow:0 0 20px rgba(255,255,255,0.4);position:relative;z-index:5;}
.features-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:12px 0 24px;position:relative;z-index:5;}
.feature-pill{background:rgba(255,215,0,0.12);border:1px solid rgba(255,215,0,0.35);border-radius:99px;padding:7px 16px;font-family:Space Mono,monospace;font-size:12px;color:#ffffff;letter-spacing:1px;}
.feature-pill span{margin-right:5px;}
.stats-ticker{display:flex;gap:32px;justify-content:center;margin-bottom:24px;flex-wrap:wrap;position:relative;z-index:5;}
.stat-item{text-align:center;animation:stat-float 3s ease-in-out infinite alternate;}
.stat-item:nth-child(2){animation-delay:-1s;}.stat-item:nth-child(3){animation-delay:-2s;}
@keyframes stat-float{0%{transform:translateY(0);}100%{transform:translateY(-7px);}}
.stat-num{font-family:Bebas Neue,sans-serif;font-size:42px;color:#FFD700;line-height:1;text-shadow:0 0 20px rgba(255,215,0,0.5);}
.stat-label{font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:2px;text-transform:uppercase;margin-top:2px;}
.gw-divider{width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.4),transparent);margin:8px 0 28px;position:relative;z-index:5;}
.mode-card{border-radius:22px;padding:24px 16px;text-align:center;cursor:pointer;transition:transform 0.3s,box-shadow 0.3s;min-height:220px;display:flex;flex-direction:column;justify-content:center;align-items:center;animation:card-breathe 5s ease-in-out infinite alternate;position:relative;z-index:5;}
.mode-card:nth-child(1){background:linear-gradient(160deg,#0a0020 0%,#150040 50%,#0d0030 100%);border:2px solid rgba(120,60,255,0.5);box-shadow:0 0 30px rgba(100,40,255,0.2),inset 0 0 40px rgba(80,0,200,0.1);}
.mode-card:nth-child(2){background:linear-gradient(160deg,#001020 0%,#002040 50%,#001530 100%);border:2px solid rgba(0,160,255,0.5);box-shadow:0 0 30px rgba(0,140,255,0.2),inset 0 0 40px rgba(0,80,200,0.1);}
.mode-card:nth-child(3){background:linear-gradient(160deg,#1a0010 0%,#300020 50%,#200015 100%);border:2px solid rgba(200,0,120,0.5);box-shadow:0 0 30px rgba(180,0,100,0.2),inset 0 0 40px rgba(160,0,80,0.1);}
.mode-card:hover{transform:translateY(-6px) scale(1.03);box-shadow:0 0 60px rgba(160,80,255,0.4),inset 0 0 60px rgba(100,40,255,0.15);}
@keyframes card-breathe{0%{box-shadow:0 0 20px rgba(100,40,255,0.15);}100%{box-shadow:0 0 50px rgba(100,40,255,0.35),0 8px 40px rgba(0,0,0,0.5);}}
.mode-emoji{font-size:36px;display:block;margin-bottom:10px;}
.mode-name{font-family:Bebas Neue,sans-serif;font-size:22px;letter-spacing:3px;color:#FFD700;margin-bottom:8px;}
.mode-desc{font-family:Space Mono,monospace;font-size:11px;color:#ffffff;line-height:1.6;}
.stTextInput>div>div>input{background:#ffffff!important;border:2px solid rgba(255,215,0,0.5)!important;border-radius:10px!important;color:#000000!important;font-family:Space Mono,monospace!important;font-size:14px!important;padding:12px 16px!important;caret-color:#000000!important;position:relative;z-index:5;}
.stTextInput>div>div>input::placeholder{color:#666666!important;}
.stTextInput>div>div>input:focus{border-color:#FFD700!important;box-shadow:0 0 20px rgba(255,215,0,0.25)!important;}
.stTextInput label{font-family:Space Mono,monospace!important;font-size:11px!important;letter-spacing:3px!important;color:#ffffff!important;text-transform:uppercase!important;position:relative;z-index:5;}
div.stButton>button{
  background:linear-gradient(135deg,#7B68EE,#FF00FF,#00FFFF)!important;
  background-size:300% 300%!important;
  border:none!important;
  color:#ffffff!important;
  font-family:Bebas Neue,sans-serif!important;
  font-size:24px!important;
  letter-spacing:4px!important;
  padding:18px!important;
  border-radius:14px!important;
  width:100%!important;
  text-shadow:0 0 12px rgba(255,255,255,0.9)!important;
  box-shadow:0 0 30px rgba(123,0,255,0.5),0 0 60px rgba(255,0,128,0.3),inset 0 0 20px rgba(255,255,255,0.08)!important;
  transition:all 0.3s!important;
  margin-top:12px!important;
  animation:btn-cosmic 5s ease-in-out infinite alternate,btn-glow-pulse 2s ease-in-out infinite alternate!important;
  position:relative;z-index:5;
}
@keyframes btn-cosmic{
  0%  {background-position:0% 50%;  box-shadow:0 0 30px rgba(123,0,255,0.6),0 0 60px rgba(255,0,128,0.3);}
  33% {background-position:100% 0%; box-shadow:0 0 40px rgba(255,0,128,0.7),0 0 80px rgba(255,100,0,0.4);}
  66% {background-position:50% 100%;box-shadow:0 0 35px rgba(0,200,255,0.6),0 0 70px rgba(0,255,150,0.3);}
  100%{background-position:0% 50%;  box-shadow:0 0 30px rgba(200,0,255,0.6),0 0 60px rgba(0,150,255,0.4);}
}
@keyframes btn-glow-pulse{
  0%  {filter:brightness(1.0) saturate(1.2);}
  100%{filter:brightness(1.35) saturate(1.6);}
}
div.stButton>button:hover{
  transform:scale(1.04) translateY(-2px)!important;
  filter:brightness(1.5) saturate(1.8)!important;
  box-shadow:0 0 70px rgba(255,0,200,0.9),0 0 130px rgba(0,200,255,0.5),inset 0 0 30px rgba(255,255,255,0.15)!important;
}
[data-testid="stExpander"]{position:relative;z-index:5;}
[data-testid="column"]{position:relative;z-index:5;}

</style>""", unsafe_allow_html=True)


    st.markdown("""
<div class="scanline-wrap"><div class="scanline"></div></div>
<div class="star-field"></div>
<div class="top-badge">⚡ 30-Second RPG Study System · Any Universe · Zero Limits</div>
<div class="gw-main-title">30 SECOND<br>INFINITEVERSE</div>
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

    components.html("""<canvas id="portalBg" style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;"></canvas>
<script>
(function(){
var cv=document.getElementById('portalBg');
if(!cv||cv._portalInit)return;
cv._portalInit=true;
var c=cv.getContext('2d');
function resize(){cv.width=window.innerWidth*2;cv.height=window.innerHeight*2;c.setTransform(2,0,0,2,0,0);}
resize();window.addEventListener('resize',resize);
var W,H,cx,cy,maxR;
function dims(){W=window.innerWidth;H=window.innerHeight;cx=W/2;cy=H/2;maxR=Math.min(W,H)*0.48;}
dims();
var rings=[];
for(var i=0;i<14;i++){var r=maxR*(0.15+i*0.063);rings.push({r:r,segments:6+i*4,width:1+Math.sin(i*0.7)*1.5+1.5,speed:0.0004+i*0.00008,dir:i%2===0?1:-1,hue:270+i*22,sat:65+i*2,gap:0.015+i*0.005});}
var sparks=[];
for(var i=0;i<120;i++){sparks.push({angle:Math.random()*6.2832,dist:40+Math.random()*(maxR-20),speed:0.001+Math.random()*0.003,dir:Math.random()>0.5?1:-1,size:0.5+Math.random()*2,hue:Math.random()*360,pulse:Math.random()*6.2832,pulseSpeed:0.02+Math.random()*0.04,trail:[]});}
var bolts=[];
for(var i=0;i<8;i++){bolts.push({fromRing:Math.floor(Math.random()*10),toRing:Math.floor(Math.random()*10)+2,angle:Math.random()*6.2832,life:0,maxLife:60+Math.random()*120,hue:250+Math.random()*80,active:false,nextSpawn:Math.floor(Math.random()*200)});}
var geometric=[];
for(var i=0;i<4;i++){geometric.push({sides:3+i,r:maxR*(0.25+i*0.18),speed:0.0002*(i%2===0?1:-1),hue:40+i*70,alpha:0.08+i*0.02});}
var pulseWaves=[],t=0;
function frame(){
  t++;dims();
  c.globalCompositeOperation='source-over';
  c.fillStyle='rgba(0,0,2,0.18)';c.fillRect(0,0,W,H);
  var dg=c.createRadialGradient(cx,cy,0,cx,cy,maxR*1.2);
  dg.addColorStop(0,'rgba(20,0,50,'+(0.04+Math.sin(t*0.002)*0.02)+')');
  dg.addColorStop(0.3,'rgba(10,0,30,'+(0.03+Math.sin(t*0.003)*0.015)+')');
  dg.addColorStop(0.6,'rgba(5,0,15,0.02)');dg.addColorStop(1,'rgba(0,0,0,0)');
  c.fillStyle=dg;c.fillRect(0,0,W,H);
  for(var i=geometric.length-1;i>=0;i--){
    var g=geometric[i];c.save();c.translate(cx,cy);c.rotate(t*g.speed);
    c.beginPath();
    for(var s=0;s<g.sides;s++){var a2=s*6.2832/g.sides-1.5708;var px=Math.cos(a2)*g.r,py=Math.sin(a2)*g.r;if(s===0)c.moveTo(px,py);else c.lineTo(px,py);}
    c.closePath();var gp=g.alpha*(0.6+Math.sin(t*0.003+i)*0.4);
    c.strokeStyle='hsla('+((g.hue+t*0.015)%360)+',50%,50%,'+gp+')';c.lineWidth=0.8;c.stroke();
    for(var s=0;s<g.sides;s++){var a2=s*6.2832/g.sides-1.5708;var px=Math.cos(a2)*g.r,py=Math.sin(a2)*g.r;c.beginPath();c.arc(px,py,2,0,6.2832);c.fillStyle='hsla('+((g.hue+t*0.015)%360)+',70%,70%,'+(gp*2)+')';c.fill();}
    c.restore();
  }
  for(var i=0;i<rings.length;i++){
    var ring=rings[i];var ba=t*ring.speed*ring.dir;
    var sA=(6.2832/ring.segments)*(1-ring.gap);var gA=(6.2832/ring.segments)*ring.gap;
    var rP=0.4+Math.sin(t*0.003+i*0.6)*0.35;
    for(var s=0;s<ring.segments;s++){
      var sAn=ba+s*(sA+gA);var sB=rP*(0.5+Math.sin(t*0.005+s*0.9+i*0.4)*0.5);var h2=(ring.hue+t*0.015+s*2)%360;
      c.beginPath();c.arc(cx,cy,ring.r,sAn,sAn+sA);c.strokeStyle='hsla('+h2+','+ring.sat+'%,55%,'+sB*0.65+')';c.lineWidth=ring.width;c.stroke();
      if(sB>0.5){c.beginPath();c.arc(cx,cy,ring.r,sAn,sAn+sA);c.strokeStyle='hsla('+h2+','+ring.sat+'%,75%,'+(sB-0.5)*0.35+')';c.lineWidth=ring.width+6;c.stroke();}
      if(sB>0.7&&ring.width>2){var mA=sAn+sA/2;var nx=cx+Math.cos(mA)*ring.r,ny=cy+Math.sin(mA)*ring.r;var ng=c.createRadialGradient(nx,ny,0,nx,ny,8);ng.addColorStop(0,'hsla('+h2+',80%,80%,'+(sB-0.7)*0.6+')');ng.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=ng;c.fillRect(nx-8,ny-8,16,16);}
    }
  }
  for(var i=0;i<sparks.length;i++){
    var sp=sparks[i];sp.angle+=sp.speed*sp.dir;sp.pulse+=sp.pulseSpeed;
    var sb=0.3+Math.sin(sp.pulse)*0.5;var sx=cx+Math.cos(sp.angle)*sp.dist,sy=cy+Math.sin(sp.angle)*sp.dist;
    sp.trail.push({x:sx,y:sy,a:sb});if(sp.trail.length>6)sp.trail.shift();
    for(var j=0;j<sp.trail.length;j++){var tr=sp.trail[j];var ta=tr.a*(j/sp.trail.length)*0.4;c.beginPath();c.arc(tr.x,tr.y,sp.size*(j/sp.trail.length),0,6.2832);c.fillStyle='hsla('+((sp.hue+t*0.02)%360)+',70%,65%,'+ta+')';c.fill();}
    c.beginPath();c.arc(sx,sy,sp.size,0,6.2832);c.fillStyle='hsla('+((sp.hue+t*0.02)%360)+',80%,70%,'+sb*0.7+')';c.fill();
  }
  for(var i=0;i<bolts.length;i++){
    var b=bolts[i];
    if(!b.active){b.nextSpawn--;if(b.nextSpawn<=0){b.active=true;b.life=0;b.angle=Math.random()*6.2832;b.fromRing=Math.floor(Math.random()*8);b.toRing=b.fromRing+2+Math.floor(Math.random()*4);if(b.toRing>=rings.length)b.toRing=rings.length-1;b.hue=250+Math.random()*80;}continue;}
    b.life++;if(b.life>b.maxLife){b.active=false;b.nextSpawn=80+Math.floor(Math.random()*300);continue;}
    var bA=b.life<10?b.life/10:b.life>b.maxLife-15?(b.maxLife-b.life)/15:1;bA*=0.4;
    var r1=rings[b.fromRing].r,r2=rings[Math.min(b.toRing,rings.length-1)].r;
    var bAn=b.angle+Math.sin(t*0.005)*0.1;var x1=cx+Math.cos(bAn)*r1;
    c.beginPath();c.moveTo(x1,cy+Math.sin(bAn)*r1);
    for(var s=1;s<=6;s++){var fr=s/6;var mR=r1+(r2-r1)*fr;var jt=(Math.random()-0.5)*12;c.lineTo(cx+Math.cos(bAn+jt*0.01)*mR+jt,cy+Math.sin(bAn+jt*0.01)*mR+jt*0.5);}
    c.strokeStyle='hsla('+b.hue+',80%,70%,'+bA+')';c.lineWidth=1.5;c.stroke();
    c.strokeStyle='hsla('+b.hue+',90%,90%,'+(bA*0.5)+')';c.lineWidth=4;c.stroke();
  }
  if(t%120<3){pulseWaves.push({r:30,maxR:maxR*1.1,speed:2.5,alpha:0.2,hue:(270+t*0.1)%360});}
  for(var i=pulseWaves.length-1;i>=0;i--){
    var pw=pulseWaves[i];pw.r+=pw.speed;pw.alpha*=0.985;
    if(pw.r>pw.maxR||pw.alpha<0.005){pulseWaves.splice(i,1);continue;}
    c.beginPath();c.arc(cx,cy,pw.r,0,6.2832);c.strokeStyle='hsla('+pw.hue+',70%,60%,'+pw.alpha+')';c.lineWidth=2;c.stroke();
  }
  var hR=28;c.save();c.translate(cx,cy);c.rotate(t*0.0008);
  for(var h=0;h<3;h++){var hr=hR*(1+h*0.5);var ha=(0.12-h*0.03)*(0.6+Math.sin(t*0.004+h)*0.4);c.beginPath();for(var i=0;i<6;i++){var a2=i*1.0472-0.5236+h*0.1;if(i===0)c.moveTo(Math.cos(a2)*hr,Math.sin(a2)*hr);else c.lineTo(Math.cos(a2)*hr,Math.sin(a2)*hr);}c.closePath();c.strokeStyle='hsla('+((40+h*30+t*0.01)%360)+',70%,60%,'+ha+')';c.lineWidth=1;c.stroke();}
  c.restore();
  var cg=c.createRadialGradient(cx,cy,0,cx,cy,50);
  cg.addColorStop(0,'rgba(255,255,255,'+(0.04+Math.sin(t*0.004)*0.02)+')');cg.addColorStop(0.3,'rgba(255,215,0,'+(0.03+Math.sin(t*0.005)*0.015)+')');cg.addColorStop(0.6,'rgba(120,0,255,'+(0.02+Math.sin(t*0.003)*0.01)+')');cg.addColorStop(1,'rgba(0,0,0,0)');
  c.fillStyle=cg;c.beginPath();c.arc(cx,cy,50,0,6.2832);c.fill();
  var oa=c.createRadialGradient(cx,cy,maxR*0.8,cx,cy,maxR*1.3);
  oa.addColorStop(0,'rgba(120,0,255,'+(0.015+Math.sin(t*0.002)*0.008)+')');oa.addColorStop(0.4,'rgba(255,0,180,'+(0.01+Math.sin(t*0.003)*0.005)+')');oa.addColorStop(0.7,'rgba(0,100,255,'+(0.008+Math.sin(t*0.004)*0.004)+')');oa.addColorStop(1,'rgba(0,0,0,0)');
  c.fillStyle=oa;c.beginPath();c.arc(cx,cy,maxR*1.3,0,6.2832);c.fill();
  requestAnimationFrame(frame);
}
c.fillStyle='#000';c.fillRect(0,0,W,H);
frame();
})();
</script>
""", height=800)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("⚡ HOW IT WORKS", key="info_toggle"):
            st.session_state.info_open = not st.session_state.get("info_open", False)
        if st.session_state.get("info_open", False):
            st.markdown("<div style='background:rgba(0,0,0,0.85);border:2px solid #FFD700;border-radius:20px;padding:28px;margin-top:12px;color:#fff;font-family:Space Mono,monospace;font-size:12px;line-height:2.2'>🌌 <b style='color:#FFD700'>Pick any universe</b> — AI builds it instantly.<br>⏱ <b style='color:#FFD700'>Study 30 seconds</b> — get paid.<br>📸 <b style='color:#FFD700'>Upload proof</b> — no proof = no coins.</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _gw_page = st.session_state.get("gw_page", 1)

        if _gw_page == 3:
            st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:18px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:8px'>⚡ CHOOSE YOUR MODE</div>", unsafe_allow_html=True)
            mode_col1, mode_col2, mode_col3 = st.columns(3)
            with mode_col1:
                st.markdown("""<div class='mode-card'><span class='mode-emoji'>⚡</span><div class='mode-name'>CHILL</div><div class='mode-desc'>Missions. Currency. Level up.</div></div>""", unsafe_allow_html=True)
                if st.button("⚡ CHILL", key="mode_chill", use_container_width=True):
                    st.session_state.game_mode = "chill"
            with mode_col2:
                st.markdown("""<div class='mode-card'><span class='mode-emoji'>🔥</span><div class='mode-name'>GRINDER</div><div class='mode-desc'>Adds Battles, Abilities, Monster Hatching.</div></div>""", unsafe_allow_html=True)
                if st.button("🔥 GRINDER", key="mode_grinder", use_container_width=True):
                    st.session_state.game_mode = "grinder"
            with mode_col3:
                st.markdown("""<div class='mode-card'><span class='mode-emoji'>💀</span><div class='mode-name'>OBSESSED</div><div class='mode-desc'>EVERYTHING. Full chaos. No limits.</div></div>""", unsafe_allow_html=True)
                if st.button("💀 OBSESSED", key="mode_obsessed", use_container_width=True):
                    st.session_state.game_mode = "obsessed"
            if st.session_state.game_mode:
                mode_labels = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}
                st.success(f"MODE: {mode_labels[st.session_state.game_mode]} ✅")

        if _gw_page == 1:
            st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:20px'>WHO ARE YOU?</div>", unsafe_allow_html=True)
            _c1, _c2 = st.columns(2)
            with _c1:
                if st.button("🌌 NEW PLAYER  Create my account", key="gw_new", use_container_width=True):
                    st.session_state.gw_page = 2; st.rerun()
            with _c2:
                if st.button("⚡ RETURNING PLAYER  Load my progress", key="gw_returning", use_container_width=True):
                    st.session_state.gw_page = 4; st.rerun()
            name_input = ""; email_input = ""; pass_input = ""; theme_input = ""
            st.stop()

        elif _gw_page == 2:
            st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:16px'>STEP 1 OF 2 — YOUR ACCOUNT</div>", unsafe_allow_html=True)
            email_input = st.text_input("📧 Email", placeholder="Your email — we never spam.", key="gw_email")
            pass_input  = st.text_input("🔑 Password", placeholder="Create a password", type="password", key="gw_pass")
            name_input = ""; theme_input = ""
            st.markdown("<br>", unsafe_allow_html=True)
            _nb1, _nb2 = st.columns([1, 4])
            with _nb1:
                if st.button("← Back", key="gw_back2"):
                    st.session_state.gw_page = 1; st.rerun()
            with _nb2:
                if st.button("NEXT ⚡", key="gw_next", use_container_width=True):
                    if not st.session_state.get("gw_email","").strip():
                        st.error("Enter your email.")
                    elif not st.session_state.get("gw_pass","").strip():
                        st.error("Enter a password.")
                    else:
                        st.session_state.gw_page = 3; st.rerun()
            st.stop()

        elif _gw_page == 3:
            email_input = st.session_state.get("gw_email", "")
            pass_input  = st.session_state.get("gw_pass", "")
            st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:16px'>STEP 2 OF 2 — YOUR UNIVERSE</div>", unsafe_allow_html=True)
            name_input  = st.text_input("⚡ Champion Name", placeholder="What are you called?", key="gw_name")
            theme_input = st.text_input("🌌 Your Universe", placeholder="Leave empty for INFINITE POWER · or type: Naruto, F1, Nike...", key="gw_theme")
            _bc, _ = st.columns([1,4])
            with _bc:
                if st.button("← Back", key="gw_back"):
                    st.session_state.gw_page = 2; st.rerun()

        elif _gw_page == 4:
            if st.session_state.get("ret_single_save") and not st.session_state.get("ret_saves_found"):
                _sv = st.session_state.ret_single_save
                _sv_theme = _sv.get("theme","") or DEFAULT_UNIVERSE_NAME
                _sv_name = _sv.get("user_name","")
                st.markdown(f"<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:8px'>WELCOME BACK, {_sv_name.upper()}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:12px;color:#888;text-align:center;margin-bottom:16px'>Universe: {_sv_theme.upper()}</div>", unsafe_allow_html=True)
                _ret_pass = st.text_input("🔑 Enter your password:", type="password", key="ret_pass_check")
                _rb1, _rb2 = st.columns([1, 4])
                with _rb1:
                    if st.button("← Back", key="gw_back_ret_pass"):
                        st.session_state.ret_single_save = None
                        st.session_state.gw_page = 4
                        st.rerun()
                with _rb2:
                    if st.button("⚡ ENTER", key="ret_pass_submit", use_container_width=True):
                        import hashlib as _hl_ret
                        if not _ret_pass.strip():
                            st.error("Enter your password.")
                        else:
                            _ret_hash = _hl_ret.sha256(_ret_pass.strip().encode()).hexdigest()
                            _stored_hash = _sv.get("password_hash", "")
                            if _stored_hash and _ret_hash != _stored_hash:
                                st.error("🔒 Wrong password.")
                            else:
                                with st.spinner(f"🌌 Loading {_sv_theme}..."):
                                    _result = resolve_universe(_sv_theme)
                                if not _result or not _result.get("safe"):
                                    _result = {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
                                _rdata = _result["data"]
                                _saved_color = _sv.get("vibe_color","")
                                if _saved_color and re.match(r"^#[0-9A-Fa-f]{6}$", _saved_color):
                                    _rdata["color"] = _saved_color
                                db_apply(_sv)
                                st.session_state.user_name = _sv_name
                                st.session_state.game_mode = _sv.get("game_mode","chill") or "chill"
                                st.session_state.world_data = _rdata
                                st.session_state.vibe_color = _rdata.get("color","#FFD700")
                                st.session_state.user_theme = _sv_theme
                                st.session_state.ret_single_save = None
                                st.query_params["u"] = _sv_name.lower()
                                st.query_params["t"] = _sv_theme
                                st.query_params["m"] = _sv.get("game_mode","chill") or "chill"
                                st.rerun()
                name_input = ""; email_input = ""; pass_input = ""; theme_input = ""
                st.stop()

            elif not st.session_state.get("ret_saves_found"):
                st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:8px'>WELCOME BACK, CHAMPION</div>", unsafe_allow_html=True)
                ret_email = st.text_input("📧 Your Email", placeholder="The email you signed up with", key="gw_ret_email")
                _rb1, _rb2 = st.columns([1, 4])
                with _rb1:
                    if st.button("← Back", key="gw_back_ret"):
                        st.session_state.gw_page = 1; st.rerun()
                with _rb2:
                    if st.button("🔍 FIND MY SAVES", key="gw_find_saves", use_container_width=True):
                        if not ret_email.strip():
                            st.error("Enter your email.")
                        else:
                            _clean_ret_email = ret_email.strip().lower().strip("_")
                            _sb = get_supabase()
                            _all_saves = []
                            if _sb:
                                try:
                                    _lr = _sb.table("players").select("*").execute()
                                    for _row in (_lr.data or []):
                                        _re = _row.get("email","").lower().strip().strip("_")
                                        if _re == _clean_ret_email:
                                            _all_saves.append(_row)
                                except: pass
                            if not _all_saves:
                                st.error("❌ No account found with that email.")
                            else:
                                if len(_all_saves) == 1:
                                    st.session_state.ret_single_save = _all_saves[0]
                                    st.rerun()
                                else:
                                    st.session_state.ret_saves_found = _all_saves
                                    st.session_state.ret_name = _all_saves[0].get("user_name","")
                                    st.rerun()

                with st.expander("🤔 Forgot your Champion Name?"):
                    _lookup_email = st.text_input("📧 Email:", key="lookup_email")
                    if st.button("🔎 FIND MY NAME", key="find_name_btn", use_container_width=True):
                        if not _lookup_email.strip():
                            st.error("Enter your email.")
                        else:
                            _sb2 = get_supabase()
                            _found = []
                            if _sb2:
                                try:
                                    _lr = _sb2.table("players").select("user_name,theme,game_mode,email").neq("email","").execute()
                                    _found = [r for r in (_lr.data or []) if r.get("email","").lower().strip().strip("_") == _lookup_email.strip().lower()]
                                except: pass
                            if not _found:
                                st.warning("❌ No account found.")
                            else:
                                for _f in _found:
                                    st.markdown(f"<div style='background:#0a0a0a;border:2px solid rgba(255,215,0,0.4);border-radius:12px;padding:12px;margin:4px 0;color:#fff;font-family:Space Mono,monospace;font-size:11px'>🌌 {(_f.get('theme','') or 'INFINITE POWER').upper()}<br>👤 <b style='color:#FFD700'>{_f.get('user_name','').upper()}</b></div>", unsafe_allow_html=True)

                with st.expander("🔑 Forgot your Password?"):
                    import secrets as _sec2, hashlib as _hl2r
                    _rp_email = st.text_input("Email:", key="ret_reset_email")
                    if st.button("Send Reset Code", key="ret_send_reset", use_container_width=True):
                        if not _rp_email.strip():
                            st.error("Enter your email.")
                        else:
                            _sbr0 = get_supabase()
                            _found_r = []
                            if _sbr0:
                                try:
                                    _lr0 = _sbr0.table("players").select("*").neq("email","").execute()
                                    _found_r = [r for r in (_lr0.data or []) if r.get("email","").lower().strip().strip("_") == _rp_email.strip().lower()]
                                except: pass
                            if not _found_r:
                                st.error("No account found.")
                            else:
                                _tok = _sec2.token_hex(3).upper()
                                _tok_hash = _hl2r.sha256(_tok.encode()).hexdigest()
                                _expiry_r = (_dt.datetime.utcnow() + _dt.timedelta(minutes=30)).isoformat()
                                _rp_name_found = _found_r[0].get("user_name","")
                                _sbr = get_supabase()
                                if _sbr:
                                    try: _sbr.table("players").update({"reset_token":_tok_hash,"reset_expiry":_expiry_r}).eq("user_name",_rp_name_found).execute()
                                    except: pass
                                if send_reset_email(_rp_email.strip(), _rp_name_found, _tok):
                                    st.success("✅ Code sent!")
                                    st.session_state.ret_reset_pending = _rp_name_found
                                else:
                                    st.error("Could not send email.")
                    if st.session_state.get("ret_reset_pending"):
                        _rc_code  = st.text_input("Reset Code:", key="ret_code_input")
                        _rc_pass  = st.text_input("New Password:", key="ret_new_pass", type="password")
                        _rc_pass2 = st.text_input("Confirm:", key="ret_new_pass2", type="password")
                        if st.button("Reset My Password", key="ret_do_reset", use_container_width=True):
                            import hashlib as _hl3r, datetime as _dtt2r
                            if not _rc_code.strip() or not _rc_pass.strip():
                                st.error("Fill in all fields.")
                            elif _rc_pass.strip() != _rc_pass2.strip():
                                st.error("Passwords do not match.")
                            else:
                                _c_hash = _hl3r.sha256(_rc_code.strip().upper().encode()).hexdigest()
                                _row_r  = db_load(st.session_state.ret_reset_pending)
                                if not _row_r or _row_r.get("reset_token","") != _c_hash:
                                    st.error("Wrong code.")
                                elif _row_r.get("reset_expiry","") < _dtt2r.datetime.utcnow().isoformat():
                                    st.error("Code expired.")
                                else:
                                    _new_h = _hl3r.sha256(_rc_pass.strip().encode()).hexdigest()
                                    _sbr2 = get_supabase()
                                    if _sbr2:
                                        try: _sbr2.table("players").update({"password_hash":_new_h,"reset_token":"","reset_expiry":""}).eq("user_name",st.session_state.ret_reset_pending.lower()).execute()
                                        except: pass
                                    st.session_state.ret_reset_pending = None
                                    st.success("Password reset!")

                name_input = ""; email_input = ""; pass_input = ""; theme_input = ""
                st.stop()

            else:
                _saves = st.session_state.ret_saves_found
                _ret_name = st.session_state.get("ret_name","")
                st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:#FFD700;text-align:center;letter-spacing:4px;margin-bottom:16px'>CHOOSE YOUR UNIVERSE</div>", unsafe_allow_html=True)
                mode_icons = {"chill":"⚡","grinder":"🔥","obsessed":"💀"}
                for i, _sv in enumerate(_saves):
                    _sv_theme = _sv.get("theme","") or "INFINITE POWER"
                    _sv_mode  = _sv.get("game_mode","chill") or "chill"
                    _sv_lv    = _sv.get("level",1)
                    _sv_miss  = _sv.get("total_missions",0)
                    _sv_str   = _sv.get("study_streak",0)
                    _sv_gold  = _sv.get("gold",0)
                    _icon     = mode_icons.get(_sv_mode,"⚡")
                    st.markdown(f"<div style='background:#0a0a1a;border:2px solid rgba(255,215,0,0.3);border-radius:16px;padding:18px 20px;margin-bottom:8px'><div style='font-family:Bebas Neue,sans-serif;font-size:24px;color:#FFD700;letter-spacing:3px'>{_icon} {_sv_theme.upper()}</div><div style='font-family:Space Mono,monospace;font-size:11px;color:#888;margin-top:4px'>{_sv_mode.upper()} · Lv {_sv_lv} · {_sv_miss} missions · 🔥 {_sv_str} streak · {_sv_gold:.0f} gold</div></div>", unsafe_allow_html=True)
                    if st.button(f"▶ ENTER — {_sv_theme.upper()}", key=f"enter_save_{i}_{_sv_theme[:10]}", use_container_width=True):
                        st.session_state.ret_single_save = _sv
                        st.session_state.ret_name = _sv.get("user_name","")
                        st.session_state.ret_saves_found = None
                        st.rerun()
                if st.button("← Back", key="gw_back_saves"):
                    st.session_state.ret_saves_found = None
                    st.session_state.gw_page = 4
                    st.rerun()
                name_input = ""; email_input = ""; pass_input = ""; theme_input = ""
                st.stop()

        else:
            name_input = ""; email_input = ""; pass_input = ""; theme_input = ""

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ ENTER THE INFINITEVERSE ⚡", key="gw_enter", use_container_width=True):
            if not name_input.strip():
                st.error("Enter your champion name to begin.")
            elif not pass_input.strip():
                st.error("Create a password to protect your account.")
            elif not email_input.strip() and st.session_state.get("gw_page", 1) != 4:
                st.error("Enter your email.")
            elif not st.session_state.game_mode:
                st.error("Choose CHILL, GRINDER, or OBSESSED to continue.")
            else:
                import hashlib as _hl
                clean_name  = name_input.strip()
                pass_hash   = _hl.sha256(pass_input.strip().encode()).hexdigest()
                theme_val   = theme_input.strip()
                display_name = theme_val if theme_val else DEFAULT_UNIVERSE_NAME
                existing = db_load(clean_name, theme_val.strip() if theme_val.strip() else "", st.session_state.game_mode or "")
                if not existing:
                    existing = db_load(clean_name)
                if existing:
                    stored_hash = existing.get("password_hash", "")
                    if stored_hash and stored_hash != pass_hash:
                        st.error("🔒 Wrong password or name already taken.")
                        st.stop()
                    elif stored_hash == pass_hash:
                        saved_theme = existing.get("theme", "") or DEFAULT_UNIVERSE_NAME
                        saved_mode  = existing.get("game_mode", "chill") or "chill"
                        with st.spinner(f"🌌 Welcome back, {clean_name}!"):
                            result = resolve_universe(saved_theme)
                        if not result["safe"]:
                            result = {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
                        _rdata2 = result["data"]
                        _sc2 = existing.get("vibe_color","")
                        if _sc2 and re.match(r"^#[0-9A-Fa-f]{6}$", _sc2):
                            _rdata2["color"] = _sc2
                        db_apply(existing)
                        st.session_state.user_name    = clean_name
                        st.session_state.password_hash = pass_hash
                        st.session_state.world_data   = _rdata2
                        st.session_state.vibe_color   = _rdata2.get("color", "#FFD700")
                        st.session_state.user_theme   = saved_theme
                        st.session_state.game_mode    = saved_mode
                        st.query_params["u"] = clean_name.lower()
                        st.query_params["t"] = saved_theme
                        st.query_params["m"] = saved_mode
                        st.session_state.gw_page = 1
                        st.toast(f"✅ Welcome back, {clean_name}!", icon="🌌")
                        st.rerun()
                    else:
                        saved_theme = existing.get("theme", "") or display_name
                        with st.spinner(f"🌌 Loading {saved_theme.upper()}..."):
                            result = resolve_universe(saved_theme)
                        if not result["safe"]:
                            result = {"safe": True, "data": DEFAULT_UNIVERSE.copy()}
                        db_apply(existing)
                        st.session_state.user_name    = clean_name
                        st.session_state.password_hash = pass_hash
                        st.session_state.world_data   = result["data"]
                        st.session_state.vibe_color   = result["data"].get("color", "#FFD700")
                        st.session_state.user_theme   = saved_theme
                        db_save(clean_name, saved_theme)
                        st.rerun()
                else:
                    if theme_val:
                        check = filter_universe_input(theme_val)
                        if not check["safe"]:
                            st.error(f"⚠️ {check['reason']}"); st.stop()
                        theme_val = check["cleaned"]; display_name = theme_val
                    with st.spinner(f"🌌 Loading {display_name.upper()}..."):
                        result = resolve_universe(theme_val)
                    if not result["safe"]:
                        st.error(f"⚠️ {result['reason']}"); st.stop()
                    st.session_state.user_name    = clean_name
                    st.session_state.password_hash = pass_hash
                    st.session_state.user_email   = email_input.strip() if email_input.strip() else ""
                    st.session_state.world_data   = result["data"]
                    st.session_state.vibe_color   = result["data"].get("color", "#FFD700")
                    st.session_state.user_theme   = display_name
                    st.session_state.universe_achievements = result["data"].get("lore_achievements", [])
                    st.session_state.universe_ach_loaded = True
                    apply_welcome_bonus()
                    db_save(clean_name, display_name)
                    st.query_params["u"] = clean_name.lower()
                    st.query_params["t"] = display_name
                    st.query_params["m"] = st.session_state.get("game_mode","chill") or "chill"
                    st.rerun()

    import base64 as _b64
    _SPINNER_B64 = "PCFET0NUWVBFIGh0bWw+PGh0bWw+PGhlYWQ+PG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CkBpbXBvcnQgdXJsKCdodHRwczovL2ZvbnRzLmdvb2dsZWFwaXMuY29tL2NzczI/ZmFtaWx5PU9yYml0cm9uOndnaHRANzAwJmRpc3BsYXk9c3dhcCcpOwoqe2JveC1zaXppbmc6Ym9yZGVyLWJveDttYXJnaW46MDtwYWRkaW5nOjA7fQpodG1sLGJvZHl7d2lkdGg6MTAwJTtiYWNrZ3JvdW5kOnRyYW5zcGFyZW50O292ZXJmbG93LXg6aGlkZGVuO292ZXJmbG93LXk6aGlkZGVuO30KI3Jvd3tkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246cm93O2p1c3RpZnktY29udGVudDpzcGFjZS1iZXR3ZWVuO2FsaWduLWl0ZW1zOmZsZXgtZW5kO3dpZHRoOjEwMCU7cGFkZGluZzoxMHB4IDZweCA2cHg7fQouc2xvdHtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6M3B4O2ZsZXg6MTttaW4td2lkdGg6MDt9Ci5zbGJse2ZvbnQtZmFtaWx5Ok9yYml0cm9uLG1vbm9zcGFjZTtmb250LXNpemU6N3B4O2xldHRlci1zcGFjaW5nOjFweDt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7Y29sb3I6cmdiYSgyNTUsMjU1LDI1NSwwLjM4KTt0ZXh0LWFsaWduOmNlbnRlcjt3aGl0ZS1zcGFjZTpub3dyYXA7b3ZlcmZsb3c6aGlkZGVuO3RleHQtb3ZlcmZsb3c6ZWxsaXBzaXM7bWF4LXdpZHRoOjEwMCU7fQouc3JwbXtmb250LWZhbWlseTpPcmJpdHJvbixtb25vc3BhY2U7Zm9udC1zaXplOjdweDtsZXR0ZXItc3BhY2luZzowLjhweDttaW4taGVpZ2h0OjExcHg7dGV4dC1hbGlnbjpjZW50ZXI7d2hpdGUtc3BhY2U6bm93cmFwO30KLm5idG57cGFkZGluZzo1cHggN3B4O2ZvbnQtc2l6ZTo3cHg7Zm9udC1mYW1pbHk6T3JiaXRyb24sbW9ub3NwYWNlO2JvcmRlci1yYWRpdXM6NXB4O2N1cnNvcjpwb2ludGVyO2xldHRlci1zcGFjaW5nOjFweDtib3JkZXI6MS41cHggc29saWQ7YmFja2dyb3VuZDpyZ2JhKDAsMCwwLDAuNyk7dHJhbnNpdGlvbjphbGwgMC4xMnM7bWFyZ2luLXRvcDoycHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO3doaXRlLXNwYWNlOm5vd3JhcDttYXgtd2lkdGg6MTAwJTt9Ci5uYnRuOmhvdmVye3RyYW5zZm9ybTpzY2FsZSgxLjEpO2ZpbHRlcjpicmlnaHRuZXNzKDEuNyk7fQoubmJ0bjphY3RpdmV7dHJhbnNmb3JtOnNjYWxlKDAuOSk7fQouZXRsYmx7Zm9udC1zaXplOjdweDtjb2xvcjpyZ2JhKDI1NSwyNTUsMjU1LDAuMTUpO2ZvbnQtZmFtaWx5Ok9yYml0cm9uLG1vbm9zcGFjZTt0ZXh0LWFsaWduOmNlbnRlcjttYXJnaW4tdG9wOjFweDt9Cjwvc3R5bGU+PC9oZWFkPjxib2R5Pgo8ZGl2IGlkPSJyb3ciPjwvZGl2Pgo8c2NyaXB0Pgp2YXIgREY9WwogIHtpZDonZjAnLHN6OjYwLGxibDonU09MQVIgRkxBUkUnLGlnOnRydWUsIG52OjUuMCxidjowLCAgIGJsOjQsc2g6J2Ryb3AnLHA6WycjRkY2NjAwJywnI0ZGMjIwMCcsJyNGRkQ3MDAnLCcjRkY4ODAwJ10sZ3c6JyNGRjQ0MDAnLHJtOicjRkZENzAwJyxoYjonI0ZGRicsdHI6MTAsYnRuOidJR05JVEUnfSwKICB7aWQ6J2YxJyxzejo2MCxsYmw6J1ZPSUQgU1RPUk0nLCBpZzpmYWxzZSwgICAgIGJ2OjAuNDgsYmw6NixzaDond2luZycscDpbJyM4ODAwRkYnLCcjNDQwMENDJywnI0NDMDBGRicsJyNGRjQ0RkYnXSxndzonI0FBMDBGRicscm06JyNGRjg4RkYnLGhiOicjRkZGJyx0cjoxMn0sCiAge2lkOidmMicsc3o6NjAsbGJsOidNQVRSSVggQ09SRScsaWc6ZmFsc2UsICAgICBidjowLjQzLGJsOjMsc2g6J2NyeXMnLHA6WycjMDBGRjQ0JywnIzAwQ0MzMycsJyMwMEZGODgnLCcjQUFGRkNDJ10sZ3c6JyMwMEZGNDQnLHJtOicjODhGRkJCJyxoYjonIzExMScsdHI6OX0sCiAge2lkOidmMycsc3o6NjQsbGJsOidOT1ZBIFBVTFNFJywgaWc6dHJ1ZSwgbnY6Ni41LGJ2OjAsICAgYmw6NSxzaDonYmxhZCcscDpbJyMwMENDRkYnLCcjMDA4OEZGJywnIzAwRkZFRScsJyM4OERERkYnXSxndzonIzAwQ0NGRicscm06JyNBQUVFRkYnLGhiOicjMDAzJyx0cjoxMixidG46J1dBUlAgRFJJVkUnfSwKICB7aWQ6J2Y0Jyxzejo2MCxsYmw6J1RJVEFOIFdBUlAnLCBpZzpmYWxzZSwgICAgIGJ2OjAuNTUsYmw6NyxzaDonZmFuJywgcDpbJyNGRkQ3MDAnLCcjRkY0NDAwJywnI0ZGODgwMCcsJyNGRkVFQUEnXSxndzonI0ZGRDcwMCcscm06JyNGRjQ0MDAnLGhiOicjMjEwJyx0cjoxNH0sCiAge2lkOidmNScsc3o6NjAsbGJsOidDSEFPUyBGTFVYJywgaWc6ZmFsc2UsICAgICBidjowLjQ0LGJsOjQsc2g6J2Ryb3AnLHA6WycjRkYwMDQ0JywnI0ZGNDQwMCcsJyNGRjAwODgnLCcjRkY4ODAwJ10sZ3c6JyNGRjAwNDQnLHJtOicjRkY4OEFBJyxoYjonI0ZGRicsdHI6MTB9LAogIHtpZDonZjYnLHN6OjY4LGxibDonU0lOR1VMQVJJVFknLGlnOnRydWUsIG52OjkuMCxidjowLCAgIGJsOjgsc2g6J2ZhbicsIHA6WycjRkZGJywnI0ZGRDcwMCcsJyNGRjIyMDAnLCcjRkZBQTAwJ10sZ3c6JyNGRkZGRkYnLHJtOicjRkZENzAwJyxoYjonIzAwMCcsdHI6MjIsYnRuOidPQkxJVEVSQVRFJ30sCl07CnZhciBTVD17fSxUUj17fTsKdmFyIHJvdz1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncm93Jyk7CkRGLmZvckVhY2goZnVuY3Rpb24oc3ApewogIFNUW3NwLmlkXT17YTpNYXRoLnJhbmRvbSgpKjYuMjgsdjpzcC5pZz8wOnNwLmJ2K01hdGgucmFuZG9tKCkqMC4wNixkZzpmYWxzZSxsQTowLGxUOjB9O1RSW3NwLmlkXT1bXTsKICB2YXIgc2xvdD1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtzbG90LmNsYXNzTmFtZT0nc2xvdCc7CiAgdmFyIGN2PWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2NhbnZhcycpO2N2LmlkPSdjXycrc3AuaWQ7Y3Yud2lkdGg9c3Auc3oqMjtjdi5oZWlnaHQ9c3Auc3oqMjtjdi5zdHlsZS5jc3NUZXh0PSdjdXJzb3I6Z3JhYjtib3JkZXItcmFkaXVzOjUwJTtkaXNwbGF5OmJsb2NrO21heC13aWR0aDoxMDAlOyc7CiAgdmFyIGxiPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO2xiLmNsYXNzTmFtZT0nc2xibCc7bGIudGV4dENvbnRlbnQ9c3AubGJsOwogIHZhciBybT1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtybS5pZD0ncl8nK3NwLmlkO3JtLmNsYXNzTmFtZT0nc3JwbSc7cm0uc3R5bGUuY29sb3I9c3AuZ3c7CiAgc2xvdC5hcHBlbmRDaGlsZChjdik7c2xvdC5hcHBlbmRDaGlsZChsYik7c2xvdC5hcHBlbmRDaGlsZChybSk7CiAgaWYoc3AuaWcpe3ZhciBidG49ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnYnV0dG9uJyk7YnRuLmNsYXNzTmFtZT0nbmJ0bic7YnRuLnRleHRDb250ZW50PXNwLmJ0bjtidG4uc3R5bGUuYm9yZGVyQ29sb3I9c3AuZ3c7YnRuLnN0eWxlLmNvbG9yPXNwLmd3O2J0bi5vbmNsaWNrPShmdW5jdGlvbihzaWQsbnYpe3JldHVybiBmdW5jdGlvbigpe1NUW3NpZF0udj1udjtzaGsoKTt9O30pKHNwLmlkLHNwLm52KTtzbG90LmFwcGVuZENoaWxkKGJ0bik7fQogIGVsc2V7dmFyIGVsPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO2VsLmNsYXNzTmFtZT0nZXRsYmwnO2VsLnRleHRDb250ZW50PSfiiJ4gQVVUTyc7ZWwuc3R5bGUuY29sb3I9c3AuZ3crJzQ0JztzbG90LmFwcGVuZENoaWxkKGVsKTt9CiAgcm93LmFwcGVuZENoaWxkKHNsb3QpOwogIGZ1bmN0aW9uIGdhKGUsYzIpe3ZhciByMj1jMi5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKTtyZXR1cm4gTWF0aC5hdGFuMigoZS5jbGllbnRZfHwoZS50b3VjaGVzJiZlLnRvdWNoZXNbMF0uY2xpZW50WSl8fDApLXIyLnRvcC1yMi5oZWlnaHQvMiwoZS5jbGllbnRYfHwoZS50b3VjaGVzJiZlLnRvdWNoZXNbMF0uY2xpZW50WCl8fDApLXIyLmxlZnQtcjIud2lkdGgvMik7fQogIGN2LmFkZEV2ZW50TGlzdGVuZXIoJ21vdXNlZG93bicsZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc3AuaWRdO3MuZGc9dHJ1ZTtzLmxBPWdhKGUsY3YpO3MubFQ9cGVyZm9ybWFuY2Uubm93KCk7Y3Yuc3R5bGUuY3Vyc29yPSdncmFiYmluZyc7fSk7CiAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoJ21vdXNlbW92ZScsKGZ1bmN0aW9uKHNpZCl7cmV0dXJuIGZ1bmN0aW9uKGUpe3ZhciBzPVNUW3NpZF07aWYoIXMuZGcpcmV0dXJuO3ZhciBub3c9cGVyZm9ybWFuY2Uubm93KCksYzI9ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2NfJytzaWQpO3ZhciBhPWdhKGUsYzIpLGQ9YS1zLmxBO2lmKGQ+TWF0aC5QSSlkLT02LjI4O2lmKGQ8LU1hdGguUEkpZCs9Ni4yODtzLnY9ZC9NYXRoLm1heChub3ctcy5sVCwxKSoyMDtzLmErPWQ7cy5sQT1hO3MubFQ9bm93O307fSkoc3AuaWQpKTsKICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcignbW91c2V1cCcsKGZ1bmN0aW9uKHNpZCl7cmV0dXJuIGZ1bmN0aW9uKCl7U1Rbc2lkXS5kZz1mYWxzZTtkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY18nK3NpZCkuc3R5bGUuY3Vyc29yPSdncmFiJzt9O30pKHNwLmlkKSk7CiAgY3YuYWRkRXZlbnRMaXN0ZW5lcigndG91Y2hzdGFydCcsZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc3AuaWRdO3MuZGc9dHJ1ZTtzLmxBPWdhKGUsY3YpO3MubFQ9cGVyZm9ybWFuY2Uubm93KCk7ZS5wcmV2ZW50RGVmYXVsdCgpO30se3Bhc3NpdmU6ZmFsc2V9KTsKICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcigndG91Y2htb3ZlJywoZnVuY3Rpb24oc2lkKXtyZXR1cm4gZnVuY3Rpb24oZSl7dmFyIHM9U1Rbc2lkXTtpZighcy5kZylyZXR1cm47dmFyIG5vdz1wZXJmb3JtYW5jZS5ub3coKSxjMj1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY18nK3NpZCk7dmFyIGE9Z2EoZSxjMiksZD1hLXMubEE7aWYoZD5NYXRoLlBJKWQtPTYuMjg7aWYoZDwtTWF0aC5QSSlkKz02LjI4O3Mudj1kL01hdGgubWF4KG5vdy1zLmxULDEpKjIwO3MuYSs9ZDtzLmxBPWE7cy5sVD1ub3c7ZS5wcmV2ZW50RGVmYXVsdCgpO307fSkoc3AuaWQpLHtwYXNzaXZlOmZhbHNlfSk7CiAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoJ3RvdWNoZW5kJywoZnVuY3Rpb24oc2lkKXtyZXR1cm4gZnVuY3Rpb24oKXtTVFtzaWRdLmRnPWZhbHNlO307fSkoc3AuaWQpKTsKfSk7CnZhciBzaGFrZU49MDsKZnVuY3Rpb24gc2hrKCl7c2hha2VOPTE0O3ZhciB1PWRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdyb3cnKTsoZnVuY3Rpb24gZigpe2lmKHNoYWtlTjw9MCl7dS5zdHlsZS50cmFuc2Zvcm09Jyc7cmV0dXJuO311LnN0eWxlLnRyYW5zZm9ybT0ndHJhbnNsYXRlKCcrKE1hdGgucmFuZG9tKCktLjUpKnNoYWtlTiouNisncHgsJysoTWF0aC5yYW5kb20oKS0uNSkqc2hha2VOKi4zKydweCknO3NoYWtlTi0tO3JlcXVlc3RBbmltYXRpb25GcmFtZShmKTt9KSgpO30KZnVuY3Rpb24gZHJhdyhzcCxhbmdsZSx2ZWwpewogIHZhciBjdj1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY18nK3NwLmlkKTtpZighY3YpcmV0dXJuOwogIHZhciBjdHg9Y3YuZ2V0Q29udGV4dCgnMmQnKSxzej1zcC5zeixjeD1zeixjeT1zeixyPXN6LTQsc3BkPU1hdGguYWJzKHZlbCk7CiAgY3R4LmNsZWFyUmVjdCgwLDAsc3oqMixzeioyKTsKICBpZihzcGQ+MC4wNSl7dmFyIGdnPWN0eC5jcmVhdGVSYWRpYWxHcmFkaWVudChjeCxjeSxyLGN4LGN5LHIrNCtzcGQqMyk7Z2cuYWRkQ29sb3JTdG9wKDAsc3AuZ3crJzY2Jyk7Z2cuYWRkQ29sb3JTdG9wKDEsc3AuZ3crJzAwJyk7Y3R4LmJlZ2luUGF0aCgpO2N0eC5hcmMoY3gsY3kscis0K3NwZCozLDAsTWF0aC5QSSoyKTtjdHguZmlsbFN0eWxlPWdnO2N0eC5maWxsKCk7fQogIHZhciB0cj1UUltzcC5pZF07dHIucHVzaChhbmdsZSk7aWYodHIubGVuZ3RoPnNwLnRyKXRyLnNoaWZ0KCk7CiAgaWYoc3BkPjAuMTImJnRyLmxlbmd0aD4yKXtmb3IodmFyIHRpPTA7dGk8dHIubGVuZ3RoLTE7dGkrKyl7dmFyIGZyYWM9dGkvdHIubGVuZ3RoO2Zvcih2YXIgYmk9MDtiaTxzcC5ibDtiaSsrKXt2YXIgYmEyPXRyW3RpXSsoYmkqNi4yOC9zcC5ibCk7Y3R4LnNhdmUoKTtjdHgudHJhbnNsYXRlKGN4LGN5KTtjdHgucm90YXRlKGJhMik7Y3R4Lmdsb2JhbEFscGhhPWZyYWMqMC4xNSpNYXRoLm1pbihzcGQqMS41LDEpO2N0eC5iZWdpblBhdGgoKTtjdHguZWxsaXBzZShyKi4zOCwwLHIqLjM0LHIqLjE0LDAsMCxNYXRoLlBJKjIpO2N0eC5maWxsU3R5bGU9c3AucFswXTtjdHguZmlsbCgpO2N0eC5yZXN0b3JlKCk7fX1jdHguZ2xvYmFsQWxwaGE9MTt9CiAgZm9yKHZhciBpPTA7aTxzcC5ibDtpKyspe3ZhciBiYT1hbmdsZSsoaSo2LjI4L3NwLmJsKTtjdHguc2F2ZSgpO2N0eC50cmFuc2xhdGUoY3gsY3kpO2N0eC5yb3RhdGUoYmEpO3ZhciBnPWN0eC5jcmVhdGVMaW5lYXJHcmFkaWVudCgwLC1yKi4wOCxyKi44MixyKi4wOCk7Zy5hZGRDb2xvclN0b3AoMCxzcC5wWzBdKTtnLmFkZENvbG9yU3RvcCguNDUsc3AucFsxJXNwLnAubGVuZ3RoXSk7Zy5hZGRDb2xvclN0b3AoLjc1LHNwLnBbMiVzcC5wLmxlbmd0aF0pO2cuYWRkQ29sb3JTdG9wKDEsc3AucFszJXNwLnAubGVuZ3RoXSsnMjInKTtjdHguZmlsbFN0eWxlPWc7Y3R4LmJlZ2luUGF0aCgpOwogIGlmKHNwLnNoPT09J2Ryb3AnKXtjdHguZWxsaXBzZShyKi40MiwwLHIqLjQyLHIqLjE5LDAsMCxNYXRoLlBJKjIpO31lbHNlIGlmKHNwLnNoPT09J3dpbmcnKXtjdHgubW92ZVRvKDAsMCk7Y3R4LmJlemllckN1cnZlVG8ociouMiwtciouMjgsciouNywtciouMjIsciouODIsMCk7Y3R4LmJlemllckN1cnZlVG8ociouNyxyKi4yMixyKi4yLHIqLjI4LDAsMCk7Y3R4LmNsb3NlUGF0aCgpO31lbHNlIGlmKHNwLnNoPT09J2NyeXMnKXtjdHgubW92ZVRvKHIqLjA4LDApO2N0eC5saW5lVG8ociouMzgsLXIqLjIyKTtjdHgubGluZVRvKHIqLjgyLDApO2N0eC5saW5lVG8ociouMzgsciouMjIpO2N0eC5jbG9zZVBhdGgoKTt9ZWxzZSBpZihzcC5zaD09PSdibGFkJyl7Y3R4Lm1vdmVUbygwLC1yKi4wNSk7Y3R4LmxpbmVUbyhyKi43OCwtciouMTIpO2N0eC5saW5lVG8ociouODIsMCk7Y3R4LmxpbmVUbyhyKi43OCxyKi4xMik7Y3R4LmxpbmVUbygwLHIqLjA1KTtjdHguY2xvc2VQYXRoKCk7fWVsc2V7Y3R4LmVsbGlwc2UociouNDAsMCxyKi40MCxyKi4yMiwwLDAsTWF0aC5QSSoyKTt9CiAgY3R4LmZpbGwoKTtjdHguc3Ryb2tlU3R5bGU9c3AucFswXSsnODgnO2N0eC5saW5lV2lkdGg9MTtjdHguc3Ryb2tlKCk7CiAgaWYoc3BkPjAuMil7Y3R4Lmdsb2JhbEFscGhhPU1hdGgubWluKChzcGQtLjIpKi40LC40KTtjdHguZmlsbFN0eWxlPXNwLnJtO2N0eC5maWxsKCk7Y3R4Lmdsb2JhbEFscGhhPTE7fWN0eC5yZXN0b3JlKCk7fQogIGN0eC5iZWdpblBhdGgoKTtjdHguYXJjKGN4LGN5LHIsMCxNYXRoLlBJKjIpO2N0eC5zdHJva2VTdHlsZT1zcC5ybSsoc3BkPi4yMj8nQkInOicyMicpO2N0eC5saW5lV2lkdGg9c3BkPi40PzI6MS4yO2N0eC5zdHJva2UoKTsKICBpZihzcGQ+MC4zKXt2YXIgcGM9TWF0aC5taW4oTWF0aC5mbG9vcihzcGQqNCksMTApO2Zvcih2YXIgcGk9MDtwaTxwYztwaSsrKXt2YXIgcGE9YW5nbGUqMy4yK3BpKjIuMCtwZXJmb3JtYW5jZS5ub3coKSouMDAxNTt2YXIgcHI9ciooLjYrTWF0aC5yYW5kb20oKSouMjgpO2N0eC5iZWdpblBhdGgoKTtjdHguYXJjKGN4K01hdGguY29zKHBhKSpwcixjeStNYXRoLnNpbihwYSkqcHIsMStNYXRoLnJhbmRvbSgpKjEuMywwLE1hdGguUEkqMik7Y3R4LmZpbGxTdHlsZT1zcC5wW3BpJXNwLnAubGVuZ3RoXTtjdHguZ2xvYmFsQWxwaGE9LjUrTWF0aC5yYW5kb20oKSouMztjdHguZmlsbCgpO2N0eC5nbG9iYWxBbHBoYT0xO319CiAgdmFyIGhnPWN0eC5jcmVhdGVSYWRpYWxHcmFkaWVudChjeC1yKi4wNCxjeS1yKi4wNCwxLGN4LGN5LHIqLjE4KTtoZy5hZGRDb2xvclN0b3AoMCwnI2ZmZicpO2hnLmFkZENvbG9yU3RvcCguNCxzcC5wWzBdKTtoZy5hZGRDb2xvclN0b3AoMSxzcC5oYik7Y3R4LmJlZ2luUGF0aCgpO2N0eC5hcmMoY3gsY3ksciouMTgsMCxNYXRoLlBJKjIpO2N0eC5maWxsU3R5bGU9aGc7Y3R4LmZpbGwoKTtjdHguYmVnaW5QYXRoKCk7Y3R4LmFyYyhjeCxjeSxyKi4wNiwwLE1hdGguUEkqMik7Y3R4LmZpbGxTdHlsZT0ncmdiYSgyNTUsMjU1LDI1NSwwLjQ1KSc7Y3R4LmZpbGwoKTsKICB2YXIgcmU9ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3JfJytzcC5pZCk7aWYocmUpe3ZhciBydj1NYXRoLmFicyh2ZWwqNjAvKE1hdGguUEkqMikqNjApO2lmKHJ2Pjgpe3JlLnRleHRDb250ZW50PU1hdGgucm91bmQocnYpLnRvTG9jYWxlU3RyaW5nKCkrJyBSUE0nO3JlLnN0eWxlLmNvbG9yPXJ2PjkwMDA/JyNGRjAwMDAnOnJ2PjQwMDA/JyNGRjg4MDAnOnJ2PjEyMDA/JyNGRkQ3MDAnOnNwLmd3O31lbHNle3JlLnRleHRDb250ZW50PXNwLmlnPydSRUFEWSc7cmUuc3R5bGUuY29sb3I9J3JnYmEoMjU1LDI1NSwyNTUsMC4xNiknO319Cn0KdmFyIEFGPTAuOTk5OTkzLE5GPTAuOTk4NjsKZnVuY3Rpb24gbG9vcCgpe0RGLmZvckVhY2goZnVuY3Rpb24oc3Ape3ZhciBzPVNUW3NwLmlkXTtpZighcy5kZyl7cy52Kj1zcC5pZz9ORjpBRjtpZihNYXRoLmFicyhzLnYpPHNwLmJ2KXMudj1zcC5pZz8wOnNwLmJ2O31zLmErPXMudjtkcmF3KHNwLHMuYSxzLnYpO30pO3JlcXVlc3RBbmltYXRpb25GcmFtZShsb29wKTt9Cmxvb3AoKTsKPC9zY3JpcHQ+PC9ib2R5PjwvaHRtbD4="
    try:
        components.html(_b64.b64decode(_SPINNER_B64).decode("utf-8"), height=500)
    except:
        pass
    st.stop()






# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP SETUP (runs when user IS logged in)
# ─────────────────────────────────────────────────────────────────────────────
wd       = st.session_state.world_data or DEFAULT_UNIVERSE
C        = st.session_state.vibe_color or wd.get("color", "#FFD700")
BG       = st.session_state.get("bg_color", "#ffffff")
TEXT     = readable_color(C, BG)
currency = wd.get("currency", "Titan Shards")
MODE     = st.session_state.get("game_mode", "chill") or "chill"
# ── Set query params for refresh survival ──
if st.session_state.user_name:
    st.query_params["u"] = st.session_state.user_name
    st.query_params["t"] = st.session_state.user_theme or ""
    st.query_params["m"] = MODE
# ── Main app background + text color ──
st.markdown(f"""<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: {BG} !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{
    display: none !important;
}}
.block-container {{ max-width: 1000px !important; }}
.metric-card {{
    background: linear-gradient(135deg, #0a0a1a, #1a0a2e);
    border: 2px solid {C}66;
    border-radius: 16px;
    padding: 20px;
    margin: 8px 0;
}}
.secret-card {{
    background: linear-gradient(135deg, #0a0a2e, #1a0020);
    border: 2px solid {C};
    border-radius: 16px;
    padding: 20px;
    margin: 8px 0;
    font-family: Space Mono, monospace;
    font-size: 14px;
    color: #ffffff;
    line-height: 1.8;
}}
.ach-card {{
    background: #111;
    border: 1px solid {C}44;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 6px 0;
    color: #ffffff;
}}
.monster-card {{
    background: linear-gradient(135deg, #0a001a, #1a0a2e);
    border: 2px solid {C};
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    margin: 12px 0;
}}
.shop-card {{
    background: linear-gradient(160deg, #0a0a1a 0%, #1a0a2e 50%, #0a0a1a 100%);
    border: 2px solid {C}55;
    border-radius: 20px;
    padding: 28px 20px;
}}
</style>""", unsafe_allow_html=True)

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown(f"<h1 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin:0'>🌌 INFINITEVERSE HUB</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>CHAMPION:</b> {st.session_state.user_name}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>UNIVERSE:</b> {st.session_state.user_theme}</p>", unsafe_allow_html=True)
    mode_badge = {"chill":"⚡ CHILL","grinder":"🔥 GRINDER","obsessed":"💀 OBSESSED"}.get(MODE,"⚡ CHILL")
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>MODE:</b> {mode_badge}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#ffffff;margin:3px 0'><b>RANK:</b> {st.session_state.sub_tier.upper()}</p>", unsafe_allow_html=True)
    _m_done   = st.session_state.get("total_missions", 0)
    _eggs     = st.session_state.get("incubator_eggs", 0)
    _boxes    = st.session_state.get("unclaimed_boxes", 0)
    _sp_left  = st.session_state.get("spins_left", 0)
    st.markdown(f"""<div class='metric-card'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:40px;color:{C}'>{st.session_state.gold:.1f}</div>
        <div style='font-size:10px;color:#ffffff;letter-spacing:2px'>{currency.upper()}</div>
        <div style='font-size:11px;color:#ffffff;margin-top:4px'>XP: {st.session_state.xp} · LVL {st.session_state.level}</div>
        <div style='margin-top:6px;padding-top:6px;border-top:1px solid {C}33;font-size:11px;color:#ffffff;letter-spacing:1px'>⚡ <b style='color:{C}'>{_m_done}</b> MISSIONS DONE</div>
        <div style='margin-top:6px;padding-top:6px;border-top:1px solid {C}22;display:flex;gap:12px;justify-content:space-between;font-size:11px'>
            <span>🎁 <b style='color:{C}'>{_boxes}</b> boxes</span>
            <span>🥚 <b style='color:{C}'>{_eggs}</b> eggs</span>
            <span>🎰 <b style='color:{C}'>{_sp_left}</b> spins</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<p style='color:#ffffff;font-weight:bold'>👑 ELITE CODE</p>", unsafe_allow_html=True)
    code = st.text_input("Protocol Code:", type="password", key="elite_code")
    if code == "4RJ1TV51Z" and st.session_state.sub_tier != "Elite":
        st.session_state.sub_tier = "Elite"; st.session_state.sub_multiplier = 3; st.success("💀 ELITE STATUS SECURED!"); st.balloons(); time.sleep(1); st.rerun()
    if code == "1TR5LG89D" and st.session_state.sub_tier not in ("Elite","Premium"):
        st.session_state.sub_tier = "Premium"; st.session_state.sub_multiplier = 2; st.success("⚡ PREMIUM STATUS SECURED!"); st.balloons(); time.sleep(1); st.rerun()
    st.write("---")
    if st.button("🚪 QUIT", key="nav_quit", use_container_width=True):
            db_save(st.session_state.user_name, st.session_state.user_theme)
            st.query_params.clear()
            for _k in list(st.session_state.keys()):
                del st.session_state[_k]
            st.rerun()
    if st.button("🚀 MISSION HUB",   key="nav_hub"):      st.session_state.view = "main";       st.rerun()
    if st.button("⚔️ BATTLE",        key="nav_battle"):   st.session_state.view = "battle";     st.rerun()
    if st.button("🎰 SPINNER",       key="nav_spin"):     st.session_state.view = "spinner";    st.session_state.spin_awarded_this_view = False; st.rerun()
    if st.button("🛒 SHOP",          key="nav_shop"):     st.session_state.view = "shop";       st.rerun()
    if st.button("📖 STORY",         key="nav_story"):    st.session_state.view = "story";      st.rerun()
    if st.button("🔮 SECRETS",       key="nav_secrets"):  st.session_state.view = "secrets";    st.rerun()
    if st.button("🛡️ ABILITIES",    key="nav_abilities"): st.session_state.view = "abilities";  st.rerun()
    if st.button("💬 FEEDBACK",      key="nav_feedback"): st.session_state.view = "feedback";   st.rerun()
    if st.button("🏆 LEADERBOARD",   key="nav_leader"):   st.session_state.view = "leaderboard"; st.rerun()
    if st.button("📦 MY BOXES",       key="nav_boxes"):   st.session_state.view = "boxes";      st.rerun()
    if MODE in ("grinder","obsessed"):
        if st.button("🏆 ACHIEVEMENTS", key="nav_ach"):  st.session_state.view = "achievements"; st.rerun()
        if st.button("🥚 INCUBATOR",    key="nav_inc"):  st.session_state.view = "incubator";    st.rerun()
    if MODE == "obsessed":
        if st.button("📖 MANUAL",    key="nav_manual"):  st.session_state.view = "manual";  st.rerun()
        if st.button("💳 PLANS",     key="nav_plans"):   st.session_state.view = "plans";   st.rerun()
    st.write("---")
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🎨 BACKGROUND</p>", unsafe_allow_html=True)
    new_bg = st.color_picker("", value=st.session_state.get("bg_color","#ffffff"), key="bg_picker", label_visibility="collapsed")
    if new_bg != st.session_state.get("bg_color","#ffffff"): st.session_state.bg_color = new_bg; st.rerun()
    st.markdown("<p style='color:#ffffff;font-weight:bold'>🌈 THEME COLOR</p>", unsafe_allow_html=True)
    new_tc = st.color_picker("", value=st.session_state.vibe_color, key="theme_picker", label_visibility="collapsed")
    if new_tc != st.session_state.vibe_color: st.session_state.vibe_color = new_tc; st.rerun()
    if st.button("💾 SAVE NOW", key="manual_save"):
        db_save(st.session_state.user_name, st.session_state.user_theme)
        st.success("✅ Saved!")
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

# ── AUTO-SAVE EVERY 3 MINUTES ─────────────────────────────────────────────────
if st.session_state.user_name:
    _now = _dt.datetime.now()
    _last = st.session_state.get("last_auto_save")
    _should_save = False
    if _last is None:
        _should_save = True
    else:
        try:
            _should_save = (_now - _dt.datetime.fromisoformat(_last)).total_seconds() > 180
        except Exception:
            _should_save = True
    if _should_save:
        db_save(st.session_state.user_name, st.session_state.user_theme)
        st.session_state.last_auto_save = _now.isoformat()
        if _last is not None:  # Don't show on first load
            st.toast("💾 Progress auto-saved!", icon="✅")
for ach in new_ach:
    st.toast(f"🏆 ACHIEVEMENT UNLOCKED: {ach['name']}", icon="🏆")

if st.session_state.show_secret:
    st.markdown(f"""<div class='secret-card'><div style='font-family:Bebas Neue,sans-serif;font-size:22px;color:{C};letter-spacing:3px;margin-bottom:10px'>🔮 UNIVERSE SECRET UNLOCKED</div>{st.session_state.show_secret}</div>""", unsafe_allow_html=True)
    if st.button("🔮 SICK. CLOSE THIS.", key="close_secret"):
        st.session_state.show_secret = None; st.rerun()
    st.stop()

# ── Try to show universe banner from FLUX ─────────────────────────────────
_banner_key = f"banner_{st.session_state.user_theme.lower().replace(' ','_')[:40]}"
_banner_url = db_get_image(_banner_key)
if _banner_url:
    st.markdown(f"<img src='{_banner_url}' style='width:100%;height:180px;object-fit:cover;border-radius:14px;margin-bottom:12px;box-shadow:0 0 30px {C}44'>", unsafe_allow_html=True)
st.markdown(f"""<h1 style='font-family:Bebas Neue,sans-serif;color:{C};text-shadow:0 0 40px {C};font-size:clamp(48px,10vw,100px);text-align:center;letter-spacing:6px;margin-bottom:0'>{st.session_state.user_theme.upper()}</h1><p style='text-align:center;font-size:15px;color:#ffffff;margin-top:4px'>{wd.get("description","A realm of infinite power.")}</p>""", unsafe_allow_html=True)
st.markdown("---")
# Generate banner in background if not cached (non-blocking)
if not _banner_url and st.session_state.user_theme and REPLICATE_AVAILABLE:
    import threading
    def _gen_banner():
        generate_universe_banner(st.session_state.user_theme, st.session_state.vibe_color)
    threading.Thread(target=_gen_banner, daemon=True).start()

view = st.session_state.view

# ── OPENING STORY ──
if not st.session_state.get("opening_story_shown", True):
    theme_now = st.session_state.user_theme or "Infinite Power"
    client_os = get_claude_client()
    if client_os:
        try:
            resp_os = client_os.messages.create(model="claude-sonnet-4-5", max_tokens=200, messages=[{"role":"user","content":f"""Universe: "{theme_now}". Opening chapter.
MAXIMUM 3 sentences. Each MAX 25 words.
Drop reader mid-action using specific {theme_now} characters and locations.
One detail that should be impossible in this universe.
End with ... (three dots).
Raw text only."""}])
            opening_txt = resp_os.content[0].text.strip()
            if not opening_txt.endswith("..."):
                opening_txt = opening_txt.rstrip(".") + "..."
        except:
            opening_txt = f"The last thing anyone expected was silence — not the silence of peace, but the silence of something so vast and so wrong that even the laws of {theme_now} had stopped breathing to listen..."
    else:
        opening_txt = f"The last thing anyone expected was silence — not the silence of peace, but the silence of something so vast and so wrong that even the laws of {theme_now} had stopped breathing to listen..."
    st.session_state.opening_story_shown = True
    if not st.session_state.story_log: st.session_state.story_log = []
    st.session_state.story_log.insert(0, opening_txt)


# ── STREAK DANGER ──
if st.session_state.get("study_streak",0) >= 2:
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
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        if st.button("⚡ CLAIM IT", key="claim_loot"):
            st.session_state.loot_pending = False; st.session_state.loot_item = None; st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# BATTLE SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("battle_state") == "ready" or view == "battle":
    st.session_state.view = "battle"
    theme    = st.session_state.user_theme or "Infinite Power"
    tier_now = st.session_state.get("sub_tier","Free")
    _battle_mode = st.session_state.get("game_mode","chill")
    if _battle_mode == "chill":
        st.markdown(f"""<div style='text-align:center;padding:40px;background:#0a0a1a;
            border:2px solid #FF8800;border-radius:20px;margin:20px 0'>
            <div style='font-size:48px'>⚔️</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#FF8800;
                letter-spacing:4px;margin:12px 0'>BATTLES LOCKED IN CHILL MODE</div>
            <div style='font-family:Space Mono,monospace;font-size:13px;color:#aaa;line-height:1.8'>
                Battles are available in 🔥 GRINDER and 💀 OBSESSED modes.<br>
                Create a new universe with one of those modes to unlock battles.
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("← Back to Mission Hub", key="battle_back_chill"):
            st.session_state.view = "main"; st.rerun()
        st.stop()

    if st.session_state.get("battle_box_pending") and st.session_state.get("battle_box_item"):
        item = st.session_state.battle_box_item
        rc2  = {"Common":"#888888","Rare":"#4488FF","Epic":"#AA44FF","Legendary":"#FFD700"}.get(item["rarity"],"#FFD700")
        st.markdown(f"""<div style='border:3px solid {rc2};border-radius:20px;padding:32px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);text-align:center;margin:16px 0;box-shadow:0 0 50px {rc2}66;'><div style='font-size:72px'>🎁</div><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{rc2};letter-spacing:6px;margin:12px 0'>{item["rarity"].upper()} BATTLE BOX</div><div style='font-size:20px;color:#ffffff;font-family:Space Mono,monospace'>{item["name"]}</div></div>""", unsafe_allow_html=True)
        if st.button("⚡ CLAIM BATTLE BOX", key="claim_battle_box"):
            st.session_state.battle_box_pending = False; st.session_state.battle_box_item = None; st.session_state.battle_state = None; st.session_state.view = "main"; st.rerun()
        st.stop()

    js_result = st.session_state.get("js_battle_result")
    if js_result == "win":
        st.session_state.js_battle_result = None
        st.session_state.battle_wins = st.session_state.get("battle_wins",0) + 1
        st.session_state.battles_fought = st.session_state.get("battles_fought",0) + 1
        st.session_state.xp += 60; st.session_state.gold += 25
        box_pool = {"Free":[("Common","#888888","+5 Shards","Common"),("Rare","#4488FF","+15 Shards","Rare")],"Premium":[("Rare","#4488FF","+25 Shards + Egg","Rare"),("Epic","#AA44FF","+50 Shards","Epic")],"Elite":[("Epic","#AA44FF","+75 Shards + 2 Eggs","Epic"),("Legendary","#FFD700","+150 Shards + Shield","Legendary")]}
        pool = box_pool.get(tier_now, box_pool["Free"]); pick = random.choice(pool)
        bitem = {"rarity": pick[0], "color": pick[1], "name": pick[2]}
        if "Egg" in pick[2]: st.session_state.incubator_eggs += (2 if "2 Eggs" in pick[2] else 1)
        if "Shield" in pick[2]: st.session_state.streak_shield = True
        st.session_state.gold += int(pick[3]) if len(pick) > 3 else 0
        st.session_state.battle_box_pending = True; st.session_state.battle_box_item = bitem
        if "loot_log" not in st.session_state: st.session_state.loot_log = []
        st.session_state.loot_log.append({"name": bitem["name"], "rarity": bitem["rarity"], "color": bitem.get("color","#FFD700"), "source": "Battle"})
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
        st.markdown(f"<p style='text-align:center;color:#aaa;font-family:Space Mono,monospace;font-size:12px'>Arena: <b>{cfg.get('arena_name','?')}</b> · Mode: <b style='color:{C}'>{cfg.get('mode','?')}</b></p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#fff;font-size:13px;font-family:Space Mono,monospace'>Pick your subject — correct answers = power attacks. Wrong = enemy hits back.</p>", unsafe_allow_html=True)

        if tier_now in ("Premium","Elite"):
            st.markdown(f"<p style='text-align:center;color:{C};font-family:Bebas Neue,sans-serif;font-size:16px;letter-spacing:3px'>👑 {tier_now.upper()}: TYPE ANY SUBJECT</p>", unsafe_allow_html=True)
            _, custom_col, _ = st.columns([1,2,1])
            with custom_col:
                custom_subject = st.text_input("Type your subject:", placeholder="e.g. Calculus 1, AP Biology, Organic Chemistry...", key="custom_subject_input")
                if st.button("⚔️ START WITH CUSTOM SUBJECT", key="custom_subj_go"):
                    if custom_subject.strip():
                        with st.spinner(f"⚔️ Generating {custom_subject.strip()} questions..."):
                            cfg = generate_battle_config(theme, custom_subject.strip(), tier_now, get_claude_client())
                        st.session_state.battle_config = cfg; st.session_state.battle_subject_chosen = True; st.rerun()
            st.markdown("<p style='text-align:center;color:#888;font-size:11px'>— or pick preset —</p>", unsafe_allow_html=True)

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

    cfg_clean = {k:v for k,v in cfg.items() if k != "client"}
    game_html = _build_game_html(cfg_clean, C)
    st.markdown(f"""<div style='border:2px solid {C}33;border-radius:12px;overflow:hidden;margin:8px 0;'><div style='background:rgba(0,0,0,0.8);padding:6px 16px;font-family:Bebas Neue,sans-serif;font-size:13px;color:{C};letter-spacing:3px;display:flex;justify-content:space-between;'><span>⚔️ {(cfg.get("arena_name","BATTLE")).upper()}</span><span style='color:#888;font-size:10px'>CORRECT = ATTACK · 3 WRONG = DEFEAT</span></div></div>""", unsafe_allow_html=True)
    components.html(game_html, height=520, scrolling=False)
    st.markdown(f"""<div style='background:linear-gradient(90deg,#0a0020,#1a0040,#0a0020);border:1px solid {C}44;border-radius:10px;padding:10px 20px;text-align:center;margin:8px 0;'><span style='font-family:Bebas Neue,sans-serif;font-size:16px;color:{C};letter-spacing:3px'>🚀 3D UNIVERSE MODE COMING SOON</span></div>""", unsafe_allow_html=True)
    col_r, col_l = st.columns(2)
    with col_r:
        if st.button("🔄 New Battle", key="new_battle"):
            st.session_state.battle_config = None; st.session_state.battle_subject_chosen = False; st.rerun()
    with col_l:
        if st.button("⬅ Back to Hub", key="back_hub"):
            st.session_state.view = "main"; st.session_state.battle_state = None; st.session_state.battle_subject_chosen = False; st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# MISSION HUB
# ─────────────────────────────────────────────────────────────────────────────
if view == "main":
    streak_now = st.session_state.get("study_streak",0)
    xp_now = st.session_state.get("xp",0)
    level_now = st.session_state.get("level",1)
    xp_pct = rig_xp_bar(xp_now, level_now)

    # ── STREAK BAR ──
    streak_color = "#FF4444" if streak_now == 0 else ("#FFD700" if streak_now >= 7 else C)
    streak_week = streak_now % 7
    streak_weeks_done = streak_now // 7
    streak_bar_str = "🔥" * streak_week + "⬜" * (7 - streak_week)
    week_label = f"WEEK {streak_weeks_done + 1}" if streak_weeks_done > 0 else "WEEK 1"
    streak_urgency = get_streak_urgency(streak_now, st.session_state.get("last_active_date",""))
    _sh = f"<div style='background:#111;border:2px solid {streak_color};border-radius:14px;padding:16px 20px;margin-bottom:20px'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'><span style='font-family:Bebas Neue,sans-serif;font-size:22px;color:{streak_color};letter-spacing:3px'>🔥 {streak_now}-DAY STREAK</span><span style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff'>{week_label} · Day {streak_week}/7</span></div><div style='font-size:22px;letter-spacing:6px;text-align:center;padding:6px 0'>{streak_bar_str}</div>"
    if streak_urgency: _sh += f"<div style='font-size:11px;color:#FF8888;margin-top:6px;font-family:Space Mono,monospace'>{streak_urgency}</div>"
    _sh += "</div>"
    st.markdown(_sh, unsafe_allow_html=True)

    missions_done = st.session_state.get("total_missions",0)  # used by sidebar counter

    # ── WEEKLY REWARD POPUP ──────────────────────────────────────────────────
    if st.session_state.get("weekly_reward_pending"):
        wr = st.session_state.weekly_reward_pending
        st.markdown(f"""<div style='background:linear-gradient(135deg,#1a0a00,#2a1500,#1a0a00);
            border:3px solid #FFD700;border-radius:20px;padding:28px;text-align:center;
            margin-bottom:20px;box-shadow:0 0 60px #FFD70088;
            animation:lootpulse 0.8s ease-in-out 5;'>
            <div style='font-size:56px;margin-bottom:4px'>🏆</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:38px;color:#FFD700;
                letter-spacing:5px;margin-bottom:6px'>WEEK {wr["weeks"]} COMPLETE!</div>
            <div style='font-family:Space Mono,monospace;font-size:13px;color:#ffffff;
                margin-bottom:18px;line-height:1.8'>
                You studied <b style='color:#FFD700'>7 days straight.</b><br>
                The universe has noticed. And it is <b style='color:#FF8800'>rewarding you massively.</b>
            </div>
            <div style='display:flex;justify-content:center;gap:24px;flex-wrap:wrap;margin-bottom:16px'>
                <div style='background:#FFD70022;border:2px solid #FFD700;border-radius:12px;
                    padding:14px 20px;min-width:100px'>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#FFD700'>+{wr["gold"]}</div>
                    <div style='font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:1px'>{currency}</div>
                </div>
                <div style='background:#AA44FF22;border:2px solid #AA44FF;border-radius:12px;
                    padding:14px 20px;min-width:100px'>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#AA44FF'>+{wr["xp"]}</div>
                    <div style='font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:1px'>XP</div>
                </div>
                <div style='background:#00CCFF22;border:2px solid #00CCFF;border-radius:12px;
                    padding:14px 20px;min-width:100px'>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#00CCFF'>+{wr["spins"]}</div>
                    <div style='font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:1px'>SPINS</div>
                </div>
                <div style='background:#00FF4422;border:2px solid #00FF44;border-radius:12px;
                    padding:14px 20px;min-width:100px'>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:32px;color:#00FF44'>+{wr["eggs"]}</div>
                    <div style='font-family:Space Mono,monospace;font-size:10px;color:#ffffff;letter-spacing:1px'>EGGS 🥚</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        _, cc, _ = st.columns([1,2,1])
        with cc:
            if st.button("⚡ CLAIM MY WEEK REWARD", key="claim_weekly"):
                st.session_state.weekly_reward_pending = None
                st.balloons()
                st.rerun()

    # ── XP BAR ──
    xp_display = int(xp_pct * 100)
    bar_filled = int(xp_pct * 30); bar_empty = 30 - bar_filled
    xp_bar_str = "█" * bar_filled + "░" * bar_empty
    xp_msg = "🔥 SO CLOSE! One more mission and you level up!" if xp_pct > 0.9 else "⚡ Keep grinding." if xp_pct > 0.7 else "💪 Every mission gets you closer."
    st.markdown(f"""<div style='background:#111;border:1px solid {C}44;border-radius:12px;padding:14px 20px;margin:8px 0 20px'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'><span style='font-family:Bebas Neue,sans-serif;font-size:14px;color:{C};letter-spacing:2px'>LEVEL {level_now} → LEVEL {level_now+1}</span><span style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff'>{xp_display}%</span></div><div style='font-family:Space Mono,monospace;font-size:11px;color:{C}'>{xp_bar_str}</div><div style='font-size:10px;color:#888;margin-top:4px;font-family:Space Mono,monospace'>{xp_msg}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MISSION TIMER + START BUTTON — neat, centered, balanced ──
    tier = st.session_state.sub_tier; mult = st.session_state.sub_multiplier; base = 5.0 * mult
    shield = st.session_state.get("shield_bought",False); boost = st.session_state.get("booster_bought",False)
    timer = st.session_state.get("micro_timer_seconds",30)
    reward_min = round(base*0.3,1); reward_max = round(base*20,1)

    _reward_parts = [f"<div style='font-family:Space Mono,monospace;font-size:10px;color:#888;letter-spacing:2px;margin-bottom:2px'>POTENTIAL REWARD</div>",
                     f"<div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:{C};line-height:1.1'>{reward_min} — {reward_max} {currency}</div>"]
    if shield:  _reward_parts.append("<div style='font-size:11px;color:#00FF44;margin-top:3px'>🛡️ SHIELD ACTIVE</div>")
    if boost:   _reward_parts.append("<div style='font-size:11px;color:#FF8800;margin-top:3px'>🚀 3× BOOSTER ACTIVE</div>")
    _reward_html = "".join(_reward_parts)
    st.markdown(f"<div style='text-align:center;margin:10px 0 12px;padding:12px;background:#111;border:1px solid {C}33;border-radius:12px'>{_reward_html}</div>", unsafe_allow_html=True)

    # ── LAYOUT CUSTOMIZER ────────────────────────────────────────────────────
    with st.expander("⚙️ Customize Button Layout", expanded=False):
        cz1, cz2 = st.columns(2)
        with cz1:
            st.slider("Text size", 9, 26, st.session_state.get("btn_font_size_slider", 13), step=1, key="btn_font_size_slider")
        with cz2:
            st.slider("Button height", 2, 32, st.session_state.get("btn_pad_slider", 4), step=2, key="btn_pad_slider")
        st.slider("Center button width  ← narrow | wide →", 1, 8, st.session_state.get("center_weight_slider", 2), step=1, key="center_weight_slider")

    _fs = st.session_state.get("btn_font_size_slider", 13)
    _pd = st.session_state.get("btn_pad_slider", 4)
    _cw = st.session_state.get("center_weight_slider", 2)

    # Target `p` inside button — that's where Streamlit actually puts the text
    st.markdown(f"""<style>
[data-testid="stMain"] div.stButton>button p{{font-size:{_fs}px!important;line-height:1.2!important;}}
[data-testid="stMain"] div.stButton>button{{padding:{_pd}px 12px!important;}}
</style>""", unsafe_allow_html=True)

    # ── START MISSION + ±30s ─────────────────────────────────────────────────
    _trib_passed = st.session_state.get("tribunal_verdict") == "pass"
    _custom_unlocked = st.session_state.get("custom_timer_unlocked", False)
    if _trib_passed and not _custom_unlocked:
        st.session_state.custom_timer_unlocked = True
        st.toast("🔓 Custom timer unlocked! Set any duration you want.", icon="⏱")
    _timer_running = st.session_state.get("timer_running", False)
    _timer_paused  = st.session_state.get("timer_paused", False)
    _timer_start   = st.session_state.get("timer_start")
    _timer_dur     = st.session_state.get("timer_duration", timer)
    _timer_rem_saved = st.session_state.get("timer_remaining_saved", _timer_dur)

    if _timer_running and _timer_start:
        _elapsed   = (_dt.datetime.now() - _dt.datetime.fromisoformat(_timer_start)).total_seconds()
        _remaining = max(0, _timer_dur - int(_elapsed))
        _pct       = min(1.0, _elapsed / _timer_dur)
        _bar_color = "#FF2222" if _remaining <= 5 else C
        st.progress(_pct)
        st.markdown(f"""<div style='text-align:center;background:#111;border:2px solid {_bar_color}66;border-radius:14px;padding:16px;margin:8px 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:{_bar_color};line-height:1'>{_remaining}s</div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:#888;letter-spacing:2px'>STUDY NOW — DON'T STOP</div>
        </div>""", unsafe_allow_html=True)
        _tc1, _tc2 = st.columns(2)
        with _tc1:
            if st.button("⏸ PAUSE TIMER", key="stop_timer", use_container_width=True):
                st.session_state.timer_running       = False
                st.session_state.timer_paused        = True
                st.session_state.timer_remaining_saved = _remaining
                st.rerun()
        with _tc2:
            if st.button("🔄 RESTART", key="restart_timer", use_container_width=True):
                st.session_state.timer_running  = False
                st.session_state.timer_paused   = False
                st.session_state.timer_start    = None
                st.rerun()
        if _remaining <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_paused  = False
            st.session_state.timer_start   = None
            st.rerun()
        else:
            time.sleep(1); st.rerun()

    elif _timer_paused:
        st.progress(1.0 - (_timer_rem_saved / max(_timer_dur,1)))
        st.markdown(f"""<div style='text-align:center;background:#111;border:2px solid #FF8800;border-radius:14px;padding:16px;margin:8px 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#FF8800;line-height:1'>{_timer_rem_saved}s</div>
            <div style='font-family:Space Mono,monospace;font-size:12px;color:#888;letter-spacing:2px'>⏸ PAUSED</div>
        </div>""", unsafe_allow_html=True)
        _tc1, _tc2 = st.columns(2)
        with _tc1:
            if st.button("▶ START TIMER", key="resume_timer", use_container_width=True):
                _offset = _dt.datetime.now() - _dt.timedelta(seconds=_timer_dur - _timer_rem_saved)
                st.session_state.timer_running = True
                st.session_state.timer_paused  = False
                st.session_state.timer_start   = _offset.isoformat()
                st.rerun()
        with _tc2:
            if st.button("🔄 RESTART", key="restart_timer", use_container_width=True):
                st.session_state.timer_running  = False
                st.session_state.timer_paused   = False
                st.session_state.timer_start    = None
                st.rerun()

    else:
        # ── TIMER IDLE — show controls ────────────────────────────────────
        # ── TIMER IDLE — show controls ────────────────────────────────────
        if st.session_state.get("custom_timer_unlocked", False):
            st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:10px;color:#FFD700;text-align:center;margin-bottom:4px;letter-spacing:1px'>🔓 CUSTOM TIMER UNLOCKED</div>", unsafe_allow_html=True)
            _custom_val = st.number_input("Set your timer (seconds):", min_value=30, max_value=3600, value=timer, step=30, key="custom_timer_input")
            st.session_state.micro_timer_seconds = _custom_val
            timer = _custom_val
        else:
            st.markdown(f"<div style='text-align:center;font-family:Bebas Neue,sans-serif;font-size:14px;color:#555;letter-spacing:2px;margin-bottom:4px'>TIMER: {timer}s &nbsp;·&nbsp; min 30s &nbsp;·&nbsp; max 5min · Pass tribunal to unlock custom</div>", unsafe_allow_html=True)
        st.markdown('<div class="mission-timer-row">', unsafe_allow_html=True)
        col_m, col_s, col_p = st.columns([1, _cw, 1])
        with col_m:
            if st.button("－30s", key="timer_minus", use_container_width=True):
                st.session_state.micro_timer_seconds = max(30, timer-30); st.rerun()
        with col_s:
            if st.button(f"⚡ START {timer}s MISSION ⚡", key="start_mission", use_container_width=True):
                st.session_state.needs_verification = True
                st.session_state.pending_gold  = base
                st.session_state.pending_xp    = st.session_state.get("pending_xp", 0) + int(base * 10)
                st.session_state.tribunal_missions_since = st.session_state.get("tribunal_missions_since", 0) + 1
                st.session_state.tribunal_seconds_done = st.session_state.get("tribunal_seconds_done", 0) + timer
                # Set tribunal due time on very first mission only
                if st.session_state.get("tribunal_seconds_done", 0) >= 240:
                    st.session_state.tribunal_due_time = _dt.datetime.now().isoformat()
                st.session_state.timer_running  = True
                st.session_state.timer_start    = _dt.datetime.now().isoformat()
                st.session_state.timer_duration = timer
                st.rerun()
        with col_p:
            if st.button("＋30s", key="timer_plus", use_container_width=True):
                st.session_state.micro_timer_seconds = min(300, timer+30); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)




# ─────────────────────────────────────────────────────────────────────────────
# ALL OTHER VIEWS
# ─────────────────────────────────────────────────────────────────────────────

elif view == "shop":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🛒 SUPPLY SHOP</h2>", unsafe_allow_html=True)
    gold_now = st.session_state.gold
    st.markdown(f"<p style='text-align:center;color:{C};font-size:20px;font-family:Bebas Neue,sans-serif'>Balance: {gold_now:.1f} {currency}</p>", unsafe_allow_html=True)
    shop_items = [
        {"name":"📓 Notebook","desc":"College-ruled. Your future notes.","price":50,"real":"~$3 Amazon gift card"},
        {"name":"✏️ Pencil Pack","desc":"12 pencils. The weapon of every champion.","price":30,"real":"~$2 Amazon gift card"},
        {"name":"📐 Calculator","desc":"Scientific calculator. Math becomes your superpower.","price":200,"real":"~$12 Amazon gift card"},
        {"name":"📚 Textbook Voucher","desc":"Any textbook up to $25.","price":500,"real":"$25 Amazon gift card"},
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
            st.markdown(f"""<div style='border:2px solid {border_col};border-radius:14px;padding:16px;background:linear-gradient(135deg,#0a0a1a,#1a0a2e);margin:8px 0;'><div style='font-size:22px;font-family:Bebas Neue,sans-serif;color:{C if can_buy else "#888"};letter-spacing:2px'>{item['name']}</div><div style='font-size:12px;color:#cccccc;font-family:Space Mono,monospace;margin:6px 0'>{item['desc']}</div><div style='font-size:14px;color:{C};font-family:Bebas Neue,sans-serif'>{item['price']} {currency}</div><div style='font-size:10px;color:#888;font-family:Space Mono,monospace'>{item['real']}</div></div>""", unsafe_allow_html=True)
            if can_buy:
                if st.button(f"BUY {item['name']}", key=f"buy_{i}"):
                    st.session_state.gold -= item["price"]; st.balloons(); st.success(f"✅ {item['name']} purchased!"); st.rerun()
            else:
                st.markdown(f"<p style='color:#666;font-size:11px;font-family:Space Mono'>Need {item['price']-gold_now:.0f} more {currency}</p>", unsafe_allow_html=True)

elif view == "story":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 YOUR UNIVERSE STORYLINE</h2>", unsafe_allow_html=True)
    if not st.session_state.story_log:
        st.markdown("<div style='text-align:center;padding:40px;color:#888;font-family:Space Mono,monospace'>Complete your first mission to begin the story...</div>", unsafe_allow_html=True)
    else:
        for i, chapter_text in enumerate(st.session_state.story_log):
            is_last = (i == len(st.session_state.story_log)-1)
            is_twist = (i > 0 and (i+1) % 5 == 0)
            border = C if is_last else ("#FF2244" if is_twist else "#333")
            label = f"⚡ CHAPTER {i+1}" + (" — 🌀 PLOT TWIST" if is_twist else "")
            st.markdown(f"""<div style='border:2px solid {border};border-radius:14px;padding:20px;background:{"linear-gradient(135deg,#2e0a0a,#1a0a2e)" if is_twist else "linear-gradient(135deg,#1a0a2e,#0a1a0e)"};margin:10px 0;{"box-shadow:0 0 20px "+C+"44;" if is_last else ""}'><div style='font-size:13px;font-family:Bebas Neue,sans-serif;color:{C if is_last else "#888"};letter-spacing:3px;margin-bottom:10px'>{label}</div><div style='font-size:15px;color:#ffffff;font-family:Space Mono,monospace;line-height:1.7'>{chapter_text}</div></div>""", unsafe_allow_html=True)

elif view == "secrets":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🔮 UNIVERSE SECRETS</h2>", unsafe_allow_html=True)
    seen = st.session_state.get("secret_queue",[])
    if seen:
        for s in reversed(seen):
            st.markdown(f"<div class='secret-card'>{s}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center;color:#ffffff;font-size:14px'>Complete your first mission to unlock your first secret. 🔮</p>", unsafe_allow_html=True)

elif view == "achievements":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🏆 {st.session_state.user_theme.upper()} ACHIEVEMENTS</h2>", unsafe_allow_html=True)
    all_achs = st.session_state.get("universe_achievements",[])
    if not all_achs: all_achs = wd.get("lore_achievements",[])
    if all_achs:
        for la in all_achs:
            st.markdown(f"""<div class='ach-card'><span style='font-family:Bebas Neue,sans-serif;font-size:18px;color:{C}'>{la.get("name","🌌 Achievement")}</span><br><span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{la.get("desc","Complete missions to unlock.")}</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center;color:#888;font-family:Space Mono,monospace'>Complete missions to generate achievements.</p>", unsafe_allow_html=True)

elif view == "incubator":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🥚 INCUBATOR</h2>", unsafe_allow_html=True)
    eggs = st.session_state.incubator_eggs
    st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;color:{TEXT}'>You have <span style='color:{C};font-size:24px;font-family:Bebas Neue,sans-serif'>{eggs}</span> eggs ready to hatch.</p>", unsafe_allow_html=True)
    if eggs > 0:
        for egg_idx in range(min(eggs,8)):
            if "egg_warmth" not in st.session_state: st.session_state.egg_warmth = {}
            if egg_idx not in st.session_state.egg_warmth:
                st.session_state.egg_warmth[egg_idx] = min(100,(egg_idx+1)*15+random.randint(5,25))
            w = st.session_state.egg_warmth[egg_idx]
            bar_filled = int(w/100*20); bar = "█"*bar_filled+"░"*(20-bar_filled)
            hint = "🐉 LEGENDARY VIBES..." if w>=90 else "✨ Epic stirs..." if w>=70 else "💙 Rare energy detected" if w>=45 else "⬜ Still warming..."
            st.markdown(f"""<div class='ach-card'><div style='display:flex;justify-content:space-between;align-items:center'><span style='font-size:20px'>🥚</span><span style='font-family:Space Mono,monospace;font-size:11px;color:#ffffff'>EGG #{egg_idx+1}</span><span style='font-family:Space Mono,monospace;font-size:10px;color:{C}'>{hint}</span></div><div style='margin-top:8px;font-family:Space Mono,monospace;font-size:12px;color:{C}'>{bar} {w}%</div></div>""", unsafe_allow_html=True)
        _, hcol, _ = st.columns([1,2,1])
        with hcol:
            if st.button("🥚 HATCH EGG", key="hatch_egg"):
                monster = hatch_egg(st.session_state.user_theme)
                st.session_state.incubator_eggs -= 1; st.session_state.eggs_hatched += 1
                reward = int(5*monster["reward_mult"]); st.session_state.gold += reward
                if monster["rarity"] == "Legendary": st.session_state.legendary_hatched = True; st.balloons()
                st.session_state.hatched_monsters.append(monster)
                new_warmth = {i-1:v for i,v in st.session_state.egg_warmth.items() if i>0}
                st.session_state.egg_warmth = new_warmth
                rc = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}.get(monster["rarity"],"#ffffff")
                st.markdown(f"""<div class='monster-card'><div style='font-size:36px'>{'🐉' if monster['rarity']=='Legendary' else '🐣'}</div><div style='font-size:11px;color:{rc};letter-spacing:3px;font-family:Space Mono,monospace'>{monster["rarity"].upper()} HATCHED!</div><div style='font-family:Bebas Neue,sans-serif;font-size:28px;color:{C}'>{monster["name"].upper()}</div><div style='font-size:13px;color:#ffffff'>+{reward} {currency}!</div></div>""", unsafe_allow_html=True)
                time.sleep(0.5); st.rerun()
    if st.session_state.hatched_monsters:
        st.markdown(f"<h3 style='font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:3px;margin-top:24px'>YOUR COLLECTION</h3>", unsafe_allow_html=True)
        for m in reversed(st.session_state.hatched_monsters[-10:]):
            rc = {"Common":"#aaaaaa","Rare":"#4488ff","Epic":"#aa44ff","Legendary":"#FFD700"}.get(m["rarity"],"#fff")
            st.markdown(f"<div class='ach-card'><span style='color:{rc};font-family:Bebas Neue,sans-serif;font-size:16px'>[{m['rarity'].upper()}]</span> <span style='color:#ffffff;font-family:Space Mono,monospace'>{m['name']}</span></div>", unsafe_allow_html=True)

elif view == "manual":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📖 CHEAT CODE MANUAL</h2>", unsafe_allow_html=True)
    for icon, title, desc in [("⏱","MISSIONS","30 SECONDS. WORK. UPLOAD PROOF. BOOM — PAID."),("⚖️","THE TRIBUNAL","NO PROOF = NO COINS. SCREENSHOT IT. PHOTO IT. WRITE IT."),("🛒","ARSENAL","BUY SHIELD = NUKE YOUR DEBT. BUY BOOSTER = 3X MULTIPLIER."),("⚔️","BATTLES","EVERY MISSION = A BATTLE UNLOCKS. WIN = BONUS COINS + AN EGG."),("🥚","INCUBATOR","HATCH EGGS. COMMON TO LEGENDARY."),("🔮","SECRETS","AFTER EVERY MISSION YOU LEARN SOMETHING BRAIN-BREAKING."),("👑","PREMIUM & ELITE","UNLOCK IN THE PLANS TAB. CODE ACTIVATES IN THE SIDEBAR."),("💳","PLANS","PREMIUM AND ELITE TIERS. MORE XP. MORE POWER. MORE EVERYTHING.")]:
        st.markdown(f"""<div class='ach-card'><span style='font-size:24px'>{icon}</span><span style='font-family:Bebas Neue,sans-serif;font-size:20px;color:{C};letter-spacing:2px;margin-left:8px'>{title}</span><br><span style='font-family:Space Mono,monospace;font-size:11px;color:{TEXT}'>{desc}</span></div>""", unsafe_allow_html=True)

elif view == "plans":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💳 UPGRADE PLANS</h2>", unsafe_allow_html=True)
    p_col, e_col = st.columns(2)
    with p_col:
        st.markdown(f"""<div class='shop-card'><div style='text-align:center;margin-bottom:16px'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:{C}'>⚡ PREMIUM</div><div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$5<span style='font-size:20px;color:#aaaaaa'>/mo</span></div></div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>✅ 2× XP &amp; currency on every mission<br>✅ 3 spins per session (Free=1)<br>✅ Rare + Epic loot pool<br>✅ 6 evolution stages in battle<br>✅ Universe-specific battle dialogue<br>✅ Lore-named achievements<br>✅ Medium story chapters<br>✅ Proof feedback + reason<br>✅ Type any subject in battle<br>✅ Priority AI generation</div><div style='background:#1a1a1a;border:1px solid #444;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'><div style='font-family:Space Mono,monospace;font-size:11px;color:#aaaaaa;letter-spacing:1px'>✅ After subscribing, your unique access code<br>will be sent to your email within minutes.</div></div></div>""", unsafe_allow_html=True)
        st.link_button("⚡ SUBSCRIBE — PREMIUM $5/mo", "https://buy.stripe.com/7sY3co4RC36M0KY495dQQ02", use_container_width=True)
    with e_col:
        st.markdown(f"""<div class='shop-card' style='border-color:#FFD700'><div style='text-align:center;margin-bottom:16px'><div style='font-family:Bebas Neue,sans-serif;font-size:36px;color:#FFD700'>💀 ELITE</div><div style='font-family:Bebas Neue,sans-serif;font-size:56px;color:#ffffff;line-height:1'>$10<span style='font-size:20px;color:#aaaaaa'>/mo</span></div></div><div style='font-family:Space Mono,monospace;font-size:12px;color:#ffffff;line-height:2.2;margin-bottom:20px'>✅ 3× XP &amp; currency on every mission<br>✅ 6 spins per session (Free=1)<br>✅ Epic + Legendary loot pool<br>✅ 9 evolution stages + exclusives<br>✅ Real-time Claude battle dialogue<br>✅ AI-generated custom achievements<br>✅ Maximum token story chapters<br>✅ Proof feedback + personalized comment<br>✅ Type any subject in battle<br>✅ Legendary egg rate doubled</div><div style='background:#1a1a1a;border:1px solid #FFD700;border-radius:10px;padding:12px;text-align:center;margin-bottom:12px'><div style='font-family:Space Mono,monospace;font-size:11px;color:#aaaaaa;letter-spacing:1px'>✅ After subscribing, your unique access code<br>will be sent to your email within minutes.</div></div></div>""", unsafe_allow_html=True)
        st.link_button("💀 SUBSCRIBE — ELITE $10/mo", "https://buy.stripe.com/14A9AM83O0YE0KYgVRdQQ03", use_container_width=True)

elif view == "spinner":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🎰 LUCKY SPINNER</h2>", unsafe_allow_html=True)

    spins_left    = st.session_state.get("spins_left", 0)
    last_spin_str = st.session_state.get("last_spin_time")

    cooldown_secs_left = 0
    if last_spin_str:
        try:
            elapsed = (_dt.datetime.now() - _dt.datetime.fromisoformat(last_spin_str)).total_seconds()
            cooldown_secs_left = max(0, int(21600 - elapsed))
        except Exception:
            cooldown_secs_left = 0

    on_cooldown = cooldown_secs_left > 0
    can_spin    = spins_left > 0 and not on_cooldown

    if on_cooldown:
        components.html(f"""<div style="text-align:center;padding:16px;background:#0a0808;border:2px solid #FF8800;border-radius:14px;">
            <div style="font-family:monospace;font-size:28px;color:#FF8800;letter-spacing:3px" id="lbl">NEXT SPIN IN: <span id="val">--:--:--</span></div>
            <div style="font-family:monospace;font-size:11px;color:#666;margin-top:6px">{spins_left} spin(s) banked - 6h cooldown</div>
        </div>
        <script>
        var r={cooldown_secs_left};
        (function tick(){{if(r<=0){{document.getElementById('val').textContent='READY NOW!';document.getElementById('lbl').style.color='#00FF44';return;}}var h=Math.floor(r/3600),m=Math.floor((r%3600)/60),s=r%60;document.getElementById('val').textContent=String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');r--;setTimeout(tick,1000);}})();
        </script>""", height=80)
    elif can_spin:
        st.markdown(f"""<div style='text-align:center;padding:14px;background:#080f08;border:2px solid #00FF44;border-radius:14px;margin:4px 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:#00FF44;letter-spacing:3px'>✅ {spins_left} SPIN(S) READY</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style='text-align:center;padding:14px;background:#0a0a0a;border:2px solid #333;border-radius:14px;margin:4px 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:#555;letter-spacing:3px'>🔒 COMPLETE A MISSION TO EARN SPINS</div>
        </div>""", unsafe_allow_html=True)

    prize_labels = json.dumps([p["label"] for p in SPINNER_PRIZES])
    prize_colors = json.dumps([p["color"] for p in SPINNER_PRIZES])
    prize_emojis = json.dumps([p["emoji"] for p in SPINNER_PRIZES])
    _land_idx = st.session_state.get("spinner_landing_index", -1)
    _is_animating = (_land_idx >= 0)

    components.html(f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;display:flex;flex-direction:column;align-items:center;padding:12px 0;font-family:monospace;}}
#wrap{{position:relative;width:420px;height:420px;}}
canvas{{border-radius:50%;box-shadow:0 0 50px rgba(255,215,0,0.4);display:block;}}
#pointer{{position:absolute;right:-14px;top:50%;transform:translateY(-50%);width:0;height:0;border-top:18px solid transparent;border-bottom:18px solid transparent;border-left:28px solid #FFD700;filter:drop-shadow(0 0 8px #FFD700);}}
#result{{margin-top:18px;font-size:24px;color:#FFD700;letter-spacing:2px;text-align:center;min-height:32px;font-weight:bold;opacity:0;transition:opacity 0.5s;}}
</style>
<div id="wrap">
  <canvas id="wh" width="420" height="420"></canvas>
  <div id="pointer"></div>
</div>
<div id="result"></div>
<script>
var labels={prize_labels}, colors={prize_colors}, emojis={prize_emojis};
var cv=document.getElementById('wh'), ctx=cv.getContext('2d');
var n=labels.length, arc=2*Math.PI/n;
var angle=0, spinning=false, idleSpeed=0.006;
var autoLand={_land_idx};

function draw(a){{
  ctx.clearRect(0,0,420,420);
  for(var i=0;i<n;i++){{
    ctx.beginPath(); ctx.moveTo(210,210);
    ctx.arc(210,210,193,a+i*arc,a+(i+1)*arc);
    ctx.fillStyle=colors[i]; ctx.fill();
    ctx.strokeStyle='#111'; ctx.lineWidth=2; ctx.stroke();
    ctx.save(); ctx.translate(210,210); ctx.rotate(a+(i+0.5)*arc);
    ctx.textAlign='right'; ctx.fillStyle='#fff';
    ctx.font='bold 13px monospace'; ctx.fillText(labels[i],182,5);
    ctx.restore();
  }}
  if(spinning){{
    ctx.beginPath(); ctx.arc(210,210,198,0,2*Math.PI);
    ctx.strokeStyle='rgba(255,215,0,0.5)'; ctx.lineWidth=6; ctx.stroke();
  }}
  ctx.beginPath(); ctx.arc(210,210,28,0,2*Math.PI);
  var hg=ctx.createRadialGradient(202,202,3,210,210,28);
  hg.addColorStop(0,'#fff'); hg.addColorStop(1,'#111');
  ctx.fillStyle=hg; ctx.fill();
  ctx.strokeStyle='#FFD700'; ctx.lineWidth=3; ctx.stroke();
}}

function doIdle(){{ if(spinning)return; angle+=idleSpeed; draw(angle); requestAnimationFrame(doIdle); }}

if(autoLand >= 0){{
  spinning = true;
  var desiredAngle = -((autoLand + 0.5) * arc);
  var needed = desiredAngle - angle;
  needed = ((needed % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
  var totalSpin = needed + 7 * 2 * Math.PI;
  var dur = 4500;
  var t0 = performance.now(), a0 = angle;
  (function spinAnim(now){{
    var elapsed = now - t0, p = Math.min(elapsed/dur, 1);
    var ease = 1 - Math.pow(1-p, 4);
    angle = a0 + totalSpin * ease;
    draw(angle);
    if(p < 1){{ requestAnimationFrame(spinAnim); }}
    else{{
      spinning = false;
      var res = document.getElementById('result');
      res.textContent = emojis[autoLand] + ' ' + labels[autoLand] + ' — YOURS!';
      res.style.color = colors[autoLand];
      res.style.opacity = '1';
      requestAnimationFrame(doIdle);
    }}
  }})(performance.now());
}} else {{
  doIdle();
}}
</script>""", height=540)

    if _is_animating:
        if st.button("🎁 CLAIM MY PRIZE", key="claim_spin_prize", use_container_width=True):
            st.session_state.spinner_landing_index = -1
            st.rerun()
    elif can_spin:
        if st.button("🎰 SPIN IT ⚡", key="python_spin_btn", use_container_width=True):
            _now_s = _dt.datetime.now()
            _last_s = st.session_state.get("last_spin_time")
            _spin_ok = True
            if _last_s:
                try:
                    if (_now_s - _dt.datetime.fromisoformat(_last_s)).total_seconds() < 21600:
                        _spin_ok = False
                except: pass
            if _spin_ok and st.session_state.get("spins_left", 0) > 0:
                _prize = random.choice(SPINNER_PRIZES)
                st.session_state.last_spin_time = _now_s.isoformat()
                st.session_state.spins_left = max(0, st.session_state.get("spins_left",1) - 1)
                st.session_state.spinner_wins = st.session_state.get("spinner_wins",0) + 1
                st.session_state.spinner_result = {"prize": _prize, "msg": f"You won: {_prize['label']}!"}
                st.session_state.spinner_landing_index = SPINNER_PRIZES.index(_prize)
                _pt = _prize.get("type", "nothing")
                if _pt == "gold_mult":
                    st.session_state.gold += st.session_state.gold * (_prize["value"] - 1)
                elif _pt == "gold_flat":
                    st.session_state.gold += float(_prize["value"])
                elif _pt == "egg_rare" or _pt == "egg_epic":
                    st.session_state.incubator_eggs += int(_prize["value"])
                elif _pt == "ability":
                    if _prize["value"] == "shield":
                        st.session_state.shield_bought = True
                    elif _prize["value"] == "booster":
                        st.session_state.booster_bought = True
                elif _pt == "story_twist":
                    st.session_state.story_twist_pending = True
                db_save(st.session_state.user_name, st.session_state.user_theme)
                st.rerun()
            else:
                st.error("Cooldown not finished!")
    elif spins_left > 0 and on_cooldown:
        st.button(f"🔒 COOLDOWN — {cooldown_secs_left//3600}h {(cooldown_secs_left%3600)//60}m", key="python_spin_btn_locked", disabled=True, use_container_width=True)
    else:
        st.button("🔒 NO SPINS — COMPLETE A MISSION", key="python_spin_btn_empty", disabled=True, use_container_width=True)

    if st.session_state.get("spinner_result") and not _is_animating:
        p  = st.session_state.spinner_result
        rc = p["prize"]["color"]
        st.markdown(f"""<div style='background:linear-gradient(135deg,#0a0a1a,#1a0a2e);
            border:3px solid {rc};border-radius:18px;padding:28px;text-align:center;
            margin-top:16px;box-shadow:0 0 50px {rc}55;'>
            <div style='font-size:56px;margin-bottom:8px'>{p["prize"]["emoji"]}</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:30px;color:{rc};
                        letter-spacing:4px;margin-bottom:8px'>{p["prize"]["label"]}</div>
            <div style='font-family:Space Mono,monospace;font-size:13px;color:#fff'>{p["msg"]}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("✅ DISMISS", key="dismiss_spin_result"):
            st.session_state.spinner_result = None
            st.rerun()

elif view == "abilities":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🛡️ YOUR ABILITIES</h2>", unsafe_allow_html=True)
    shield_owned  = st.session_state.get("shield_bought", False)
    booster_owned = st.session_state.get("booster_bought", False)
    tier_now_ab   = st.session_state.get("sub_tier", "Free")

    # SHIELD
    s_bc  = C if shield_owned else "#333"
    s_sc  = "#00FF44" if shield_owned else "#FF4444"
    s_st  = "✅ ACTIVE" if shield_owned else "❌ NOT OWNED"
    s_how = "Win from the 🎰 Spinner or complete a battle" if not shield_owned else ""
    s_study = f"<div style='margin-top:8px;padding:8px 10px;background:rgba(0,255,100,0.08);border-left:3px solid #00FF44;border-radius:4px;font-family:Space Mono,monospace;font-size:11px;color:#00FF88'>📚 STUDY BENEFIT: Negates any currency debt earned that session. Keeps your balance safe on bad runs.</div>"
    st.markdown(f"""<div class='metric-card' style='border-color:{s_bc}'>
        <div style='display:flex;align-items:flex-start;gap:16px'>
            <div style='font-size:48px'>🛡️</div>
            <div style='flex:1'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:{C};letter-spacing:3px'>{wd.get("shield_name","Shield")}</div>
                <div style='font-size:12px;color:#aaaaaa;margin:4px 0;font-style:italic'>{wd.get("shield_flavor","Protects from harm.")}</div>
                <div style='font-size:12px;color:{s_sc};font-family:Space Mono,monospace;margin-top:4px'>{s_st}{(" — "+s_how) if s_how else ""}</div>
                {s_study}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # BOOSTER
    b_bc  = C if booster_owned else "#333"
    b_sc  = "#00FF44" if booster_owned else "#FF4444"
    b_st  = "✅ ACTIVE — 3× CURRENCY ON EVERY MISSION" if booster_owned else "❌ NOT OWNED"
    b_how = "Win from the 🎰 Spinner or complete a battle" if not booster_owned else ""
    b_mult = f"+{int((st.session_state.sub_multiplier*3-1)*100)}% more" if booster_owned else "3× multiplier when activated"
    b_study = f"<div style='margin-top:8px;padding:8px 10px;background:rgba(255,140,0,0.08);border-left:3px solid #FF8800;border-radius:4px;font-family:Space Mono,monospace;font-size:11px;color:#FFAA44'>📚 STUDY BENEFIT: Every mission reward is tripled. Earn 3× currency, 3× XP progress, 3× closer to leveling up. Stack with Premium/Elite for maximum gain.</div>"
    st.markdown(f"""<div class='metric-card' style='border-color:{b_bc}'>
        <div style='display:flex;align-items:flex-start;gap:16px'>
            <div style='font-size:48px'>🚀</div>
            <div style='flex:1'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:26px;color:{C};letter-spacing:3px'>{wd.get("booster_name","Booster")}</div>
                <div style='font-size:12px;color:#aaaaaa;margin:4px 0;font-style:italic'>{wd.get("booster_flavor","Moves at impossible speed.")}</div>
                <div style='font-size:12px;color:{b_sc};font-family:Space Mono,monospace;margin-top:4px'>{b_st}{(" — "+b_how) if b_how else ""}</div>
                {b_study}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='text-align:center;padding:14px;background:#111;border:1px solid {C}22;border-radius:12px;margin-top:8px'>
        <div style='font-family:Space Mono,monospace;font-size:11px;color:#666'>Win abilities from the 🎰 Spinner · Or purchase Elite/Premium for permanent boosts</div>
    </div>""", unsafe_allow_html=True)

elif view == "boxes":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>📦 MY LOOT BOXES</h2>", unsafe_allow_html=True)
    loot_log = st.session_state.get("loot_log", [])
    if not loot_log:
        st.markdown(f"<div style='text-align:center;padding:40px;font-family:Space Mono,monospace;color:#555;font-size:13px'>No boxes yet. Complete missions and win battles to earn them!</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center;font-family:Space Mono,monospace;font-size:12px;color:#888'>{len(loot_log)} boxes earned total</p>", unsafe_allow_html=True)
        rarity_colors = {{"JACKPOT":"#FFD700","💥 JACKPOT":"#FFD700","EPIC":"#AA44FF","✨ EPIC":"#AA44FF","GREAT":"#4488FF","⚡ GREAT":"#4488FF","SOLID":"#44FF88","✅ SOLID":"#44FF88","LOW":"#888888","😤 LOW":"#888888","🌟 EPIC REWARD":"#AA44FF","Common":"#aaaaaa","Rare":"#4488FF","Legendary":"#FFD700"}}
        for box in reversed(loot_log[-50:]):
            rc = rarity_colors.get(box.get("rarity",""), box.get("color","#FFD700"))
            source_badge = f"<span style='font-size:9px;padding:2px 6px;background:{rc}22;border:1px solid {rc}44;border-radius:4px;color:{rc};margin-left:8px'>{box.get('source','Mission')}</span>"
            st.markdown(f"<div style='display:flex;align-items:center;padding:10px 14px;background:#111;border:1px solid {rc}44;border-radius:10px;margin-bottom:6px'><div style='font-size:22px;margin-right:12px'>🎁</div><div style='flex:1'><div style='font-family:Bebas Neue,sans-serif;font-size:15px;color:{rc};letter-spacing:2px'>{box.get('name','Prize')}{source_badge}</div><div style='font-family:Space Mono,monospace;font-size:10px;color:#666;margin-top:2px'>{box.get('rarity','')}</div></div></div>", unsafe_allow_html=True)

elif view == "leaderboard":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>🏆 GLOBAL LEADERBOARD</h2>", unsafe_allow_html=True)

    is_visible = st.session_state.get("leaderboard_visible", True)

    # ── Your leaderboard visibility status ───────────────────────────────────
    if is_visible:
        st.markdown(f"""<div style='background:#080f08;border:2px solid #00FF44;border-radius:12px;
            padding:14px 20px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center'>
            <div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:18px;color:#00FF44;letter-spacing:2px'>✅ YOU ARE ON THE LEADERBOARD</div>
                <div style='font-family:Space Mono,monospace;font-size:11px;color:#555;margin-top:3px'>Others can see your rank and progress</div>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🙈 HIDE ME FROM LEADERBOARD", key="lb_hide"):
            st.session_state.leaderboard_visible = False
            db_save(st.session_state.user_name, st.session_state.user_theme)
            st.success("✅ You're now hidden from the leaderboard. Focus on yourself! 💪")
            st.rerun()
    else:
        st.markdown(f"""<div style='background:#0a0808;border:2px solid #FF8800;border-radius:12px;
            padding:14px 20px;margin-bottom:8px'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:18px;color:#FF8800;letter-spacing:2px'>🙈 YOU ARE HIDDEN FROM THE LEADERBOARD</div>
            <div style='font-family:Space Mono,monospace;font-size:11px;color:#555;margin-top:3px'>Only you can see this. Others cannot see your name.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:11px;color:#888;margin-bottom:6px'>Type <b style='color:{C}'>Leaderboard</b> below to rejoin:</div>", unsafe_allow_html=True)
        rejoin_input = st.text_input("", placeholder="Type: Leaderboard", key="lb_rejoin_input", label_visibility="collapsed")
        if st.button("⚡ REJOIN LEADERBOARD", key="lb_rejoin"):
            if rejoin_input.strip() == "Leaderboard":
                st.session_state.leaderboard_visible = True
                db_save(st.session_state.user_name, st.session_state.user_theme)
                st.success("🏆 You're back on the leaderboard!")
                st.rerun()
            else:
                st.error("Type exactly: Leaderboard")

    st.markdown("---")

    # ── Leaderboard table ─────────────────────────────────────────────────────
    leaders = db_get_leaderboard(15)
    if not leaders:
        st.markdown("<p style='text-align:center;color:#888;font-family:Space Mono,monospace'>No players yet — complete a mission to appear here!</p>", unsafe_allow_html=True)
    else:
        medals = ["🥇","🥈","🥉"] + ["🏅"]*12
        for i, p in enumerate(leaders):
            is_you    = p["user_name"] == st.session_state.user_name.lower().strip()
            bg        = "#1a1a2a" if is_you else "#111"
            border    = C if is_you else "#333"
            name_col  = C if is_you else "#fff"
            tier_badge = {"Elite":"💀","Premium":"⚡","Free":""}.get(p.get("sub_tier","Free"),"")
            you_tag   = "&nbsp;&nbsp;← YOU" if is_you else ""
            missions  = p.get("total_missions", 0)
            streak    = p.get("study_streak", 0)
            level     = p.get("level", 1)
            uname     = p["user_name"].upper()
            st.markdown(
                f"<div style='border:2px solid {border};border-radius:12px;padding:12px 16px;"
                f"margin:6px 0;background:{bg};display:flex;justify-content:space-between;align-items:center'>"
                f"<span style='font-family:Bebas Neue,sans-serif;font-size:22px;color:{name_col}'>"
                f"{medals[i]} {uname} {tier_badge}</span>"
                f"<span style='font-family:Space Mono,monospace;font-size:11px;color:#888'>"
                f"{missions} missions &middot; {streak}🔥 streak &middot; Lv{level}{you_tag}</span>"
                f"</div>",
                unsafe_allow_html=True
            )


elif view == "feedback":
    st.markdown(f"<h2 style='font-family:Bebas Neue,sans-serif;text-align:center;color:{C};letter-spacing:4px'>💬 FEEDBACK PORTAL</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        fb_type = st.selectbox("TYPE", ["💡 Feature Idea","🐛 Bug Report","🔥 This is fire!","😤 Needs fixing","💭 General Thought"], key="fb_type")
        fb_text = st.text_area("YOUR MESSAGE", placeholder="Be as detailed as you want.", height=120, key="fb_text")
        fb_name = st.text_input("YOUR NAME (optional)", placeholder="Anonymous", key="fb_name")
        if st.button("🚀 SUBMIT", key="submit_fb"):
            if fb_text.strip():
                clean_name = fb_name.strip() or "Anonymous"
                st.session_state.feedback_list.append({"type":fb_type,"message":fb_text.strip(),"name":clean_name,"universe":st.session_state.user_theme,"time":time.strftime("%Y-%m-%d %H:%M")})
                db_save_feedback(fb_type, fb_text.strip(), clean_name, st.session_state.user_theme)
                st.success("✅ RECEIVED. Thank you, Champion. 🔥"); st.balloons()
            else: st.error("Write something first!")



if view == "main":
    # ─────────────────────────────────────────────────────────────────────────────
    # THE TRIBUNAL — only fires after 5 minutes
    # ─────────────────────────────────────────────────────────────────────────────
    _trib_due = st.session_state.get("tribunal_due_time")
    _trib_overdue = False
    if _trib_due:
        try:
            _trib_overdue = _dt.datetime.now() > _dt.datetime.fromisoformat(_trib_due)
        except:
            # Corrupted date — clear it
            st.session_state.tribunal_due_time = None
            _trib_overdue = False
    
    # Screenshot Proof progress bar — always visible
    if not _trib_overdue:
        _pg = st.session_state.get("pending_gold", 0)
        _px = st.session_state.get("pending_xp", 0)
        _nm = st.session_state.get("tribunal_missions_since", 0)
        try:
            _total_secs = 240
            _done_secs = st.session_state.get("tribunal_seconds_done", 0)
            _elapsed_pct = min(1.0, _done_secs / _total_secs)
            _remaining_secs = max(0, _total_secs - _done_secs)
            _mins = _remaining_secs // 60; _secs_r = _remaining_secs % 60
            _timer_label = f"{_mins}:{str(_secs_r).zfill(2)}"
        except:
            _elapsed_pct = 0.0; _timer_label = "4:00"
        _bar_fill = int(_elapsed_pct * 20)
        _bar_str  = "█" * _bar_fill + "░" * (20 - _bar_fill)
        _locked_text = f"+{_pg:.1f} {currency} · +{_px} XP LOCKED" if _pg > 0 else "Start a mission to begin earning"
        _mission_text = f"{_nm} mission{'s' if _nm!=1 else ''} done" if _nm > 0 else "No missions yet"
        _bar_fill = int(_elapsed_pct * 20)
        _bar_str  = "█" * _bar_fill + "░" * (20 - _bar_fill)
        st.markdown(f"""<div style='background:#080808;border:2px solid #FF8800;border-radius:14px;padding:16px 20px;margin:8px 0'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:18px;color:#FF8800;letter-spacing:3px'>
                    📸 SCREENSHOT PROOF — {_timer_label} LEFT
                </div>
                <div style='text-align:right;font-family:Space Mono,monospace;font-size:11px;color:#888'>
                    {_mission_text}
                </div>
            </div>
            <div style='font-family:Space Mono,monospace;font-size:13px;color:#FF8800;letter-spacing:2px;margin-bottom:6px'>{_bar_str} {int(_elapsed_pct*100)}%</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:16px;color:#FFD700'>{_locked_text}</div>
            <div style='font-family:Space Mono,monospace;font-size:10px;color:#555;margin-top:4px'>When bar hits 100% — upload a screenshot of your work to unlock all rewards</div>
        </div>""", unsafe_allow_html=True)
    
    _show_tribunal = False
    if st.session_state.needs_verification and st.session_state.get("tribunal_missions_since", 0) > 0:
        _trib_due_str = st.session_state.get("tribunal_due_time")
        if _trib_due_str:
            try:
                _show_tribunal = st.session_state.get("tribunal_seconds_done", 0) >= 240
            except:
                _show_tribunal = False
        if st.session_state.get("timer_running", False) or st.session_state.get("timer_paused", False):
            _show_tribunal = False
    if _show_tribunal:
        st.markdown("---")
        st.markdown(f"<h2 style='text-align:center;font-family:Bebas Neue,sans-serif;color:{C};letter-spacing:4px'>⚖️ THE TRIBUNAL</h2>", unsafe_allow_html=True)
        _, col, _ = st.columns([1,2,1])
        with col:
            st.info(f"Upload proof of work to claim **{st.session_state.pending_gold:.1f} {currency}** + a 🔮 Universe Secret + 📖 Story Chapter + 🎁 Loot Box")
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
                st.session_state.tribunal_seconds_done = 0
                st.session_state.tribunal_due_time = None
                st.session_state.tribunal_missions_since = 0
    
                total_m = st.session_state.total_missions
                current_achs = st.session_state.get("universe_achievements",[])
                if total_m % 10 == 0 and len(current_achs) < 300:
                    ach_client = get_claude_client()
                    if ach_client:
                        new_achs = generate_universe_achievements(st.session_state.user_theme, ach_client)
                        if new_achs:
                            st.session_state.universe_achievements = current_achs + new_achs
                            st.toast(f"🏆 {len(new_achs)} NEW ACHIEVEMENTS UNLOCKED!", icon="🏆")
    
                loot_pool = [
                    {"name":f"+{spins} Spinner Spins","rarity":rarity_label,"color":"#FFD700"},
                    {"name":"RARE INCUBATOR EGG","rarity":"GREAT","color":"#4488FF"},
                    {"name":"STREAK SHIELD (protects 1 day)","rarity":"EPIC","color":"#AA44FF"},
                    {"name":f"+{int(earned*2)} Bonus {currency}","rarity":rarity_label,"color":"#00FF88"},
                    {"name":"STORY CHAPTER UNLOCKED","rarity":"GREAT","color":"#FF44AA"},
                ]
                loot = random.choice(loot_pool)
                if "Shield" in loot["name"]: st.session_state.streak_shield = True
                if "Egg" in loot["name"]: st.session_state.incubator_eggs += 2
                if "Bonus" in loot["name"]: st.session_state.gold += int(earned*2)
                st.session_state.loot_pending = True; st.session_state.loot_item = loot
                # ── SAVE TO SUPABASE ──
                db_save(st.session_state.user_name, st.session_state.user_theme)
                if "loot_log" not in st.session_state: st.session_state.loot_log = []
                st.session_state.loot_log.append({"name": loot["name"], "rarity": loot["rarity"], "color": loot.get("color","#FFD700"), "source": "Mission"})
                st.session_state.unclaimed_boxes = st.session_state.get('unclaimed_boxes', 0) + 1
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
                time.sleep(1); st.rerun()    # ── MISSION TIMER — side buttons small, center button big ─────────────────
