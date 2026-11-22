"""Presentation: everything the player SEES. No data logic in this file.

Functions here only receive ready-made values (the dicts from logic.py)
and draw them. Styling, animations and the swipe card all live here.

Built with substantial AI assistance (see README, "AI use").
"""
import html
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------
BG = "#0E1218"
PANEL = "#161C25"
LINE = "rgba(255,255,255,0.08)"
TEXT = "#E9EEF3"
MUTED = "#8C98A8"
AMBER = "#F2B53A"   # floodlights / accent
SACK = "#E5484D"    # red card
BACK = "#2BB3A3"    # keep faith
WIN = "#3DC47E"
DRAW = "#6B7686"
LOSS = "#E5484D"

LEAGUES = {
    "PL": "Premier League",
    "LL": "LaLiga",
    "BL": "Bundesliga",
    "SA": "Serie A",
    "L1": "Ligue 1",
}

# Club-style colour pairs for the generated crests (background, text)
CREST_COLOURS = [
    ("#C8102E", "#FFFFFF"), ("#034694", "#FFFFFF"), ("#6CABDD", "#1C2C5B"),
    ("#111111", "#FFFFFF"), ("#7A263A", "#9AD3EE"), ("#00843D", "#FFFFFF"),
    ("#FDE100", "#111111"), ("#1B2A4A", "#E4B53F"), ("#F18A00", "#111111"),
    ("#5B2C83", "#FFFFFF"), ("#E30613", "#FFE100"), ("#0B4EA2", "#FFD100"),
]

LOGO_FILE = Path("data/processed/team_logos.csv")  # optional: columns team, logo_url


# ---------------------------------------------------------------
# Global style
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600;700&display=swap');

:root {
  --bg: #0E1218; --panel: #161C25; --panel-2: #1C2430; --line: rgba(255,255,255,0.08);
  --text: #E9EEF3; --muted: #8C98A8; --amber: #F2B53A;
  --sack: #E5484D; --back: #2BB3A3; --win: #3DC47E; --draw: #6B7686; --loss: #E5484D;
  --display: 'Barlow Condensed', 'Arial Narrow', sans-serif;
  --body: 'Barlow', system-ui, sans-serif;
}

/* ---------- app frame ---------- */
.stApp {
  background:
    radial-gradient(1200px 500px at 50% -180px, rgba(242,181,58,0.10), transparent 60%),
    radial-gradient(800px 400px at 110% 10%, rgba(43,179,163,0.06), transparent 60%),
    var(--bg);
  font-family: var(--body);
}
.stMarkdown p, .stMarkdown li { font-family: var(--body); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"], .block-container { max-width: 760px; padding-top: 2.2rem; }
[data-testid="stSidebar"] { background: #0B0F14; border-right: 1px solid var(--line); }
[data-testid="stSidebarNav"] a span { font-family: var(--display); font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
footer { visibility: hidden; }

/* ---------- header ---------- */
.sb-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.sb-wordmark { font-family: var(--display); font-weight: 800; font-size: 30px; letter-spacing: .04em; line-height: 1; color: var(--text); }
.sb-wordmark .or { color: var(--muted); font-weight: 600; font-size: 20px; margin: 0 6px; vertical-align: 3px; }
.sb-wordmark .s { color: var(--sack); } .sb-wordmark .b { color: var(--back); }
.sb-score { font-family: var(--display); font-weight: 700; letter-spacing: .08em; font-size: 14px; color: var(--muted);
  border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; background: rgba(255,255,255,0.03); }
.sb-score b { color: var(--amber); font-size: 18px; margin-left: 6px; }
.sb-progress { display: flex; gap: 6px; margin: 16px 0 6px; }
.sb-seg { flex: 1; height: 5px; border-radius: 3px; background: rgba(255,255,255,0.08); overflow: hidden; }
.sb-seg.done { background: rgba(242,181,58,0.55); }
.sb-seg.now { background: rgba(255,255,255,0.08); position: relative; }
.sb-seg.now::after { content: ""; position: absolute; inset: 0; background: var(--amber); transform-origin: left; animation: sb-fill 1.1s ease-out forwards; }
.sb-caption { font-family: var(--display); font-weight: 600; letter-spacing: .14em; text-transform: uppercase; font-size: 12px; color: var(--muted); }

/* ---------- swipe card ---------- */
.sb-stage { position: relative; padding: 18px 6px 6px; overflow: hidden; }
.sb-card {
  --club: #444; position: relative; margin: 0 auto; max-width: 440px; border-radius: 22px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--club) 38%, transparent) 0%, transparent 46%),
    linear-gradient(180deg, #1B2330, #141A23);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 24px 60px -20px rgba(0,0,0,0.75), inset 0 1px 0 rgba(255,255,255,0.06);
  padding: 22px 22px 20px; user-select: none; touch-action: pan-y; cursor: grab;
  animation: sb-deal .55s cubic-bezier(.2,.9,.25,1.15) both;
}
.sb-card:active { cursor: grabbing; }
.sb-card.sb-snap { transition: transform .35s cubic-bezier(.2,1.4,.4,1); }
.sb-card.sb-fly { transition: transform .42s cubic-bezier(.5,0,.75,0), opacity .42s; opacity: 0; }
.sb-card.sb-static { cursor: default; animation: none; }

.sb-card-top { display: flex; align-items: center; gap: 16px; }
.sb-crest { flex: 0 0 auto; width: 74px; height: 84px; display: grid; place-items: center;
  clip-path: polygon(50% 0, 100% 12%, 100% 58%, 50% 100%, 0 58%, 0 12%);
  font-family: var(--display); font-weight: 800; font-size: 25px; letter-spacing: .04em;
  box-shadow: inset 0 -10px 20px rgba(0,0,0,0.25); }
.sb-crest-img { flex: 0 0 auto; width: 78px; height: 78px; object-fit: contain; filter: drop-shadow(0 6px 14px rgba(0,0,0,.5)); }
.sb-eyebrow { font-family: var(--display); font-weight: 700; letter-spacing: .14em; text-transform: uppercase; font-size: 12px; color: var(--muted); }
.sb-name { font-family: var(--display); font-weight: 800; font-size: 40px; line-height: 1; color: var(--text); margin: 4px 0 4px; text-transform: uppercase; }
.sb-sub { font-size: 14px; color: var(--muted); }

.sb-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 20px; }
.sb-stat { background: rgba(255,255,255,0.035); border: 1px solid var(--line); border-radius: 14px; padding: 12px 12px 10px; text-align: center; }
.sb-stat-val { font-family: var(--display); font-weight: 800; font-size: 34px; line-height: 1; color: var(--text); font-variant-numeric: tabular-nums; }
.sb-stat-val sup { font-size: 15px; margin-left: 1px; color: var(--muted); }
.sb-stat-val.danger { color: var(--sack); } .sb-stat-val.good { color: var(--win); }
.sb-stat-lbl { margin-top: 6px; font-family: var(--display); font-weight: 600; letter-spacing: .12em; text-transform: uppercase; font-size: 11px; color: var(--muted); }

.sb-form { margin-top: 18px; }
.sb-form-lbl { font-family: var(--display); font-weight: 600; letter-spacing: .14em; text-transform: uppercase; font-size: 11px; color: var(--muted); margin-bottom: 8px; }
.sb-pills { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; }
.sb-pill { display: grid; place-items: center; height: 30px; border-radius: 7px; font-family: var(--display); font-weight: 800; font-size: 15px; color: #0E1218; }
.sb-pill.W { background: var(--win); } .sb-pill.D { background: var(--draw); color: #E9EEF3; } .sb-pill.L { background: var(--loss); color: #fff; }

.sb-question { margin-top: 18px; padding-top: 14px; border-top: 1px dashed rgba(255,255,255,0.12); font-size: 15px; color: var(--text); text-align: center; }
.sb-question b { font-family: var(--display); letter-spacing: .04em; font-size: 17px; }

.sb-stamp { position: absolute; top: 26px; z-index: 3; font-family: var(--display); font-weight: 800; font-size: 40px; letter-spacing: .08em;
  padding: 2px 14px; border: 4px solid currentColor; border-radius: 10px; opacity: 0; pointer-events: none; }
.sb-stamp-sack { right: 22px; color: var(--sack); transform: rotate(12deg); }
.sb-stamp-back { left: 22px; color: var(--back); transform: rotate(-12deg); }
.sb-static .sb-stamp.on { opacity: .95; }

.sb-actions { display: flex; align-items: center; justify-content: center; gap: 18px; margin: 18px auto 4px; max-width: 440px; }
.sb-hint { flex: 1; text-align: center; font-size: 12px; color: var(--muted); letter-spacing: .04em; }
.sb-btn { font-family: var(--display); font-weight: 800; font-size: 18px; letter-spacing: .1em; border-radius: 999px; padding: 14px 22px; cursor: pointer;
  background: transparent; transition: transform .15s ease, box-shadow .2s ease, background .2s ease; }
.sb-btn:hover { transform: translateY(-2px) scale(1.04); }
.sb-btn:active { transform: scale(.96); }
.sb-btn-back { color: var(--back); border: 2px solid var(--back); }
.sb-btn-back:hover { background: rgba(43,179,163,0.12); box-shadow: 0 0 28px rgba(43,179,163,0.35); }
.sb-btn-sack { color: var(--sack); border: 2px solid var(--sack); }
.sb-btn-sack:hover { background: rgba(229,72,77,0.12); box-shadow: 0 0 28px rgba(229,72,77,0.35); }

/* ---------- reveal ---------- */
.sb-reveal { margin-top: 18px; border-radius: 22px; padding: 22px; border: 1px solid var(--line); background: linear-gradient(180deg, #1A212C, #141A23); animation: sb-rise .5s ease-out both; }
.sb-verdict { font-family: var(--display); font-weight: 800; font-size: 46px; line-height: 1; letter-spacing: .03em; animation: sb-pop .6s cubic-bezier(.2,1.6,.4,1) both; }
.sb-reveal.right .sb-verdict { color: var(--win); }
.sb-reveal.wrong .sb-verdict { color: var(--sack); }
.sb-verdict-sub { margin-top: 6px; color: var(--muted); font-size: 15px; }
.sb-bars { margin-top: 20px; display: grid; gap: 14px; }
.sb-bar-head { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin-bottom: 6px; }
.sb-bar-name { font-family: var(--display); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 15px; }
.sb-bar-name small { font-family: var(--body); text-transform: none; letter-spacing: 0; font-weight: 500; color: var(--muted); font-size: 13px; margin-left: 6px; }
.sb-bar-val { font-family: var(--display); font-weight: 800; font-size: 26px; font-variant-numeric: tabular-nums; }
.sb-bar-val small { font-size: 13px; color: var(--muted); margin-left: 3px; letter-spacing: .06em; }
.sb-track { height: 14px; border-radius: 8px; background: rgba(255,255,255,0.06); overflow: hidden; }
.sb-fill { height: 100%; width: var(--w); border-radius: 8px; animation: sb-grow 1.1s cubic-bezier(.2,.9,.2,1) both; }
.sb-fill.sack { background: linear-gradient(90deg, #a8262b, var(--sack)); }
.sb-fill.back { background: linear-gradient(90deg, #17766c, var(--back)); }
.sb-tag { display: inline-block; font-family: var(--display); font-weight: 700; font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
  padding: 2px 8px; border-radius: 999px; margin-left: 8px; vertical-align: 2px; }
.sb-tag.pick { border: 1px solid var(--amber); color: var(--amber); }
.sb-tag.best { background: var(--amber); color: #0E1218; }
.sb-footnote { margin-top: 14px; font-size: 12px; color: var(--muted); }

/* ---------- results list ---------- */
.sb-section { font-family: var(--display); font-weight: 700; letter-spacing: .14em; text-transform: uppercase; font-size: 13px; color: var(--muted); margin: 26px 0 10px; }
.sb-list { border: 1px solid var(--line); border-radius: 16px; overflow: hidden; background: rgba(255,255,255,0.02); }
.sb-row { display: grid; grid-template-columns: 44px 1fr 34px 64px 34px; align-items: center; gap: 8px; padding: 9px 14px; border-top: 1px solid var(--line); font-size: 15px; }
.sb-row:first-child { border-top: none; }
.sb-md { font-family: var(--display); font-weight: 700; color: var(--muted); font-size: 13px; letter-spacing: .06em; }
.sb-opp { color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sb-ha { font-family: var(--display); font-weight: 700; font-size: 12px; color: var(--muted); text-align: center; border: 1px solid var(--line); border-radius: 6px; padding: 1px 0; }
.sb-sc { font-family: var(--display); font-weight: 800; font-size: 18px; text-align: center; font-variant-numeric: tabular-nums; }
.sb-row .sb-pill { height: 26px; font-size: 14px; }

/* ---------- final ---------- */
.sb-final { text-align: center; padding: 20px 0 6px; animation: sb-rise .6s ease-out both; }
.sb-ring { --p: 0; width: 210px; height: 210px; margin: 10px auto 18px; border-radius: 50%; display: grid; place-items: center;
  background: conic-gradient(var(--amber) calc(var(--p) * 1%), rgba(255,255,255,0.07) 0); animation: sb-ring 1.4s cubic-bezier(.2,.9,.2,1) forwards; }
.sb-ring-inner { width: 172px; height: 172px; border-radius: 50%; background: var(--bg); display: grid; place-items: center; }
.sb-ring-num { font-family: var(--display); font-weight: 800; font-size: 72px; line-height: 1; }
.sb-ring-num small { font-size: 28px; color: var(--muted); }
.sb-tier { font-family: var(--display); font-weight: 800; font-size: 34px; text-transform: uppercase; letter-spacing: .03em; }
.sb-tier-sub { color: var(--muted); margin-top: 6px; font-size: 15px; }

/* ---------- home ---------- */
.sb-hero { text-align: center; padding: 30px 0 10px; }
.sb-hero h1 { font-family: var(--display) !important; font-weight: 800 !important; font-size: 76px !important; line-height: .92 !important; letter-spacing: .02em; margin: 0; padding: 0 !important; }
.sb-hero h1 .s { color: var(--sack); } .sb-hero h1 .b { color: var(--back); } .sb-hero h1 .or { color: var(--muted); font-size: 40px; vertical-align: 14px; margin: 0 8px; }
.sb-hero p { color: var(--muted); font-size: 18px; max-width: 520px; margin: 16px auto 0; }
.sb-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 30px 0 10px; }
.sb-step { border: 1px solid var(--line); border-radius: 16px; padding: 16px; background: rgba(255,255,255,0.025); }
.sb-step-n { font-family: var(--display); font-weight: 800; color: var(--amber); font-size: 14px; letter-spacing: .14em; }
.sb-step-t { font-family: var(--display); font-weight: 800; font-size: 22px; text-transform: uppercase; margin: 4px 0; }
.sb-step-d { color: var(--muted); font-size: 14px; }

/* ---------- Streamlit buttons ---------- */
.st-key-next_case, .st-key-play_again, .st-key-start,
.st-key-next_case > div, .st-key-play_again > div, .st-key-start > div { display: flex !important; justify-content: center !important; width: 100%; }
.st-key-next_case button, .st-key-play_again button, .st-key-start button {
  width: auto !important; min-width: 280px; border-radius: 999px; border: none; padding: 14px 28px;
  background: var(--amber); color: #0E1218; transition: transform .15s ease, box-shadow .2s ease;
}
.st-key-next_case button p, .st-key-play_again button p, .st-key-start button p {
  font-family: var(--display) !important; font-weight: 800; font-size: 19px; letter-spacing: .1em; text-transform: uppercase;
}
.st-key-next_case button:hover, .st-key-play_again button:hover, .st-key-start button:hover {
  transform: translateY(-2px); box-shadow: 0 10px 30px -8px rgba(242,181,58,0.6); color: #0E1218; border: none;
}

/* ---------- motion ---------- */
@keyframes sb-deal { from { opacity: 0; transform: translateY(26px) scale(.96) rotate(-1.5deg); } to { opacity: 1; transform: none; } }
@keyframes sb-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes sb-pop { from { opacity: 0; transform: scale(.6); } to { opacity: 1; transform: none; } }
@keyframes sb-grow { from { width: 0; } }
@keyframes sb-fill { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@property --p { syntax: '<number>'; inherits: false; initial-value: 0; }
@keyframes sb-ring { to { --p: var(--target); } }

@media (max-width: 560px) {
  .sb-name { font-size: 32px; } .sb-hero h1 { font-size: 54px !important; }
  .sb-steps { grid-template-columns: 1fr; } .sb-hint { display: none; }
  .sb-row { grid-template-columns: 38px 1fr 30px 56px 30px; padding: 8px 10px; }
}
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
"""


def load_style():
    """Call first on every page: page settings + global CSS."""
    st.set_page_config(page_title="Sack or Back", page_icon="⚽", layout="centered")
    # Blank lines would end the HTML block in markdown, so strip them out.
    css = "\n".join(line for line in CSS.splitlines() if line.strip())
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------
def _ordinal(n):
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _season_label(season):
    return f"20{season[:2]}/{season[2:]}"


def _teams_in_league(league, season):
    if league == "BL" or (league == "L1" and season >= "2324"):
        return 18
    return 20


def _abbreviation(team):
    words = [w for w in team.replace("'", "").split() if w]
    if len(words) == 1:
        return words[0][:3].upper()
    return (words[0][0] + words[-1][:2]).upper()


@st.cache_data
def _logo_urls():
    if LOGO_FILE.exists():
        logos = pd.read_csv(LOGO_FILE)
        return dict(zip(logos["team"], logos["logo_url"]))
    return {}


def _crest(team):
    url = _logo_urls().get(team)
    if isinstance(url, str) and url:
        return f'<img class="sb-crest-img" src="{html.escape(url)}" alt="">', "#3A4352"
    bg, fg = CREST_COLOURS[sum(ord(c) for c in team) % len(CREST_COLOURS)]
    badge = f'<div class="sb-crest" style="background:{bg};color:{fg}">{html.escape(_abbreviation(team))}</div>'
    return badge, bg


def _pills(last10):
    out = []
    for _, g in last10.iterrows():
        tip = f"vs {g['opponent']} {int(g['goals_for'])}–{int(g['goals_against'])}"
        out.append(f'<span class="sb-pill {g["result"]}" title="{html.escape(tip)}">{g["result"]}</span>')
    return "".join(out)


def _card_html(s, static=False, stamp=None):
    crest, club_colour = _crest(s["team"])
    n_teams = _teams_in_league(s["league"], s["season"])
    pos_class = "danger" if s["position"] > n_teams - 3 else ("good" if s["position"] <= 4 else "")
    stamp_sack = "on" if stamp == "sack" else ""
    stamp_back = "on" if stamp == "back" else ""
    return f"""
<div class="sb-stage">
  <div class="sb-card {'sb-static' if static else ''}" style="--club:{club_colour}">
    <div class="sb-stamp sb-stamp-back {stamp_back}">BACK</div>
    <div class="sb-stamp sb-stamp-sack {stamp_sack}">SACK</div>
    <div class="sb-card-top">
      {crest}
      <div>
        <div class="sb-eyebrow">{LEAGUES.get(s['league'], s['league'])} · {_season_label(s['season'])}</div>
        <div class="sb-name">{html.escape(s['team'])}</div>
        <div class="sb-sub">After matchday {s['round']}</div>
      </div>
    </div>
    <div class="sb-stats">
      <div class="sb-stat"><div class="sb-stat-val {pos_class}">{s['position']}<sup>{_ordinal(s['position'])}</sup></div><div class="sb-stat-lbl">Position</div></div>
      <div class="sb-stat"><div class="sb-stat-val">{s['points']}</div><div class="sb-stat-lbl">Points</div></div>
      <div class="sb-stat"><div class="sb-stat-val">{s['form']:.2f}</div><div class="sb-stat-lbl">PPG · last 5</div></div>
    </div>
    <div class="sb-form">
      <div class="sb-form-lbl">Last 10 results · oldest → newest</div>
      <div class="sb-pills">{_pills(s['last10'])}</div>
    </div>
    <div class="sb-question">The board meets tonight. <b>Does the coach stay?</b></div>
  </div>
</div>
"""


# ---------------------------------------------------------------
# Swipe card component (drag left = BACK, right = SACK)
# ---------------------------------------------------------------
SWIPE_JS = """
export default function (component) {
  const { data, setTriggerValue, parentElement } = component;
  if (parentElement.__sbCleanup) parentElement.__sbCleanup();

  parentElement.innerHTML = data.html + `
    <div class="sb-actions">
      <button class="sb-btn sb-btn-back" data-choice="back">← BACK</button>
      <div class="sb-hint">Swipe the card · or use ← →</div>
      <button class="sb-btn sb-btn-sack" data-choice="sack">SACK →</button>
    </div>`;

  const card = parentElement.querySelector('.sb-card');
  const stampSack = parentElement.querySelector('.sb-stamp-sack');
  const stampBack = parentElement.querySelector('.sb-stamp-back');
  const LIMIT = 110;
  let startX = 0, dx = 0, dragging = false, done = false;

  const place = (x) => {
    card.style.transform = `translateX(${x}px) rotate(${x / 16}deg)`;
    stampSack.style.opacity = Math.max(0, Math.min(1, x / LIMIT));
    stampBack.style.opacity = Math.max(0, Math.min(1, -x / LIMIT));
  };

  const decide = (choice) => {
    if (done) return;
    done = true;
    const dir = choice === 'sack' ? 1 : -1;
    (choice === 'sack' ? stampSack : stampBack).style.opacity = 1;
    card.style.animation = 'none';
    card.classList.remove('sb-snap');
    card.classList.add('sb-fly');
    requestAnimationFrame(() => {
      card.style.transform = `translateX(${dir * 760}px) rotate(${dir * 28}deg)`;
    });
    setTimeout(() => setTriggerValue('choice', choice), 430);
  };

  card.addEventListener('pointerdown', (e) => {
    if (done) return;
    dragging = true; dx = 0; startX = e.clientX;
    card.style.animation = 'none';
    card.classList.remove('sb-snap');
    card.setPointerCapture(e.pointerId);
  });
  card.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    dx = e.clientX - startX;
    place(dx);
  });
  const release = () => {
    if (!dragging) return;
    dragging = false;
    if (dx > LIMIT) decide('sack');
    else if (dx < -LIMIT) decide('back');
    else { card.classList.add('sb-snap'); place(0); }
  };
  card.addEventListener('pointerup', release);
  card.addEventListener('pointercancel', release);

  parentElement.querySelectorAll('[data-choice]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const choice = btn.dataset.choice;
      place(choice === 'sack' ? 60 : -60);
      setTimeout(() => decide(choice), 90);
    });
  });

  const onKey = (e) => {
    if (e.key === 'ArrowRight') decide('sack');
    if (e.key === 'ArrowLeft') decide('back');
  };
  document.addEventListener('keydown', onKey);

  const cleanup = () => document.removeEventListener('keydown', onKey);
  parentElement.__sbCleanup = cleanup;
  return cleanup;
}
"""

_swipe = st.components.v2.component("sack_or_back_swipe", js=SWIPE_JS, isolate_styles=False)


# ---------------------------------------------------------------
# Public functions used by the pages
# ---------------------------------------------------------------
def header(case_number, total, score):
    segments = "".join(
        f'<div class="sb-seg {"done" if n < case_number else "now" if n == case_number else ""}"></div>'
        for n in range(1, total + 1)
    )
    st.html(f"""
<div class="sb-top">
  <div class="sb-wordmark"><span class="s">SACK</span><span class="or">or</span><span class="b">BACK</span></div>
  <div class="sb-score">SCORE<b>{score}</b></div>
</div>
<div class="sb-progress">{segments}</div>
<div class="sb-caption">Case {case_number} of {total}</div>
""")


def swipe_card(s, key):
    """The decision card. Returns 'sack', 'back', or None if nothing happened yet."""
    result = _swipe(data={"html": _card_html(s)}, key=key, on_choice_change=lambda: None)
    return result.choice


def show_reveal(s, choice, result):
    """Verdict + both paths. Returns True when 'Next case' is clicked."""
    right = choice == result["better"]
    if right:
        verdict, sub = "RIGHT CALL", "The numbers back you up. Nice work in the boardroom."
    else:
        verdict, sub = "WRONG CALL", "The other path would have earned more points."

    def bar(option, title, note, value):
        tags = ""
        if option == choice:
            tags += '<span class="sb-tag pick">your pick</span>'
        if option == result["better"]:
            tags += '<span class="sb-tag best">better</span>'
        width = max(2, min(100, value / 3 * 100))
        return f"""
<div>
  <div class="sb-bar-head">
    <div class="sb-bar-name" style="color:var(--{option})">{title}<small>{note}</small>{tags}</div>
    <div class="sb-bar-val">{value:.2f}<small>PPG</small></div>
  </div>
  <div class="sb-track"><div class="sb-fill {option}" style="--w:{width:.1f}%"></div></div>
</div>"""

    st.html(_card_html(s, static=True, stamp=choice))
    st.html(f"""
<div class="sb-reveal {'right' if right else 'wrong'}">
  <div class="sb-verdict">{verdict}</div>
  <div class="sb-verdict-sub">{sub}</div>
  <div class="sb-bars">
    {bar("sack", "Sack", "what really happened", result["sack_ppg"])}
    {bar("back", "Back", "similar teams that kept their coach", result["back_ppg"])}
  </div>
  <div class="sb-footnote">Points per game over the next 10 matches. Max possible: 3.00.</div>
</div>
""")
    return st.button("Next case →", key="next_case")


def show_details(s):
    """Season chart + last 10 results, shown under the card."""
    n_teams = _teams_in_league(s["league"], s["season"])
    history = s["history"][["round", "position", "result", "opponent", "goals_for", "goals_against"]].copy()
    history["score"] = history["goals_for"].astype(int).astype(str) + "–" + history["goals_against"].astype(int).astype(str)

    st.html('<div class="sb-section">League position this season</div>')
    y_scale = alt.Scale(domain=[n_teams, 1], nice=False)
    zone = alt.Chart(pd.DataFrame({"y": [n_teams - 2.5], "y2": [n_teams + 0.5]})).mark_rect(
        color=SACK, opacity=0.10
    ).encode(y=alt.Y("y:Q", scale=y_scale), y2="y2:Q")
    zone_label = alt.Chart(pd.DataFrame({"y": [n_teams - 1]})).mark_text(
        text="RELEGATION ZONE", align="left", dx=6, color=SACK, opacity=0.7, fontSize=10, font="Barlow Condensed", fontWeight=700
    ).encode(y=alt.Y("y:Q", scale=y_scale), x=alt.value(0))
    line = alt.Chart(history).mark_line(color=AMBER, strokeWidth=2.5, interpolate="monotone").encode(
        x=alt.X("round:Q", title="Matchday", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("position:Q", title="Position", scale=y_scale, axis=alt.Axis(tickMinStep=1)),
    )
    dots = alt.Chart(history).mark_circle(size=70, opacity=1, stroke=BG, strokeWidth=1.5).encode(
        x="round:Q",
        y=alt.Y("position:Q", scale=y_scale),
        color=alt.Color("result:N", scale=alt.Scale(domain=["W", "D", "L"], range=[WIN, DRAW, LOSS]), legend=None),
        tooltip=[
            alt.Tooltip("round:Q", title="Matchday"),
            alt.Tooltip("opponent:N", title="Opponent"),
            alt.Tooltip("score:N", title="Score"),
            alt.Tooltip("position:Q", title="Position"),
        ],
    )
    chart = (
        (zone + zone_label + line + dots)
        .properties(height=240, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=MUTED, titleColor=MUTED, gridColor=LINE, domain=False, tickColor=LINE,
            labelFont="Barlow", titleFont="Barlow Condensed", titleFontWeight=700, labelFontSize=12, titleFontSize=12,
        )
    )
    st.altair_chart(chart, width="stretch")

    rows = []
    for _, g in s["last10"].iloc[::-1].iterrows():
        rows.append(f"""
<div class="sb-row">
  <div class="sb-md">MD {int(g['round'])}</div>
  <div class="sb-opp">{html.escape(str(g['opponent']))}</div>
  <div class="sb-ha">{'H' if g['home'] == 1 else 'A'}</div>
  <div class="sb-sc">{int(g['goals_for'])}–{int(g['goals_against'])}</div>
  <span class="sb-pill {g['result']}">{g['result']}</span>
</div>""")
    st.html('<div class="sb-section">Last 10 matches · newest first</div><div class="sb-list">' + "".join(rows) + "</div>")


def show_final(score, total):
    """Final screen. Returns True when 'Play again' is clicked."""
    tiers = {
        5: ("Director of the decade", "Perfect boardroom instincts. Every call was the right one."),
        4: ("Elite sporting director", "Clubs would hand you the keys tomorrow."),
        3: ("Solid board member", "Better than a coin flip, and better than plenty of real clubs."),
        2: ("Fan with opinions", "Strong feelings, mixed results."),
        1: ("Panic button presser", "The numbers disagreed with you more often than not."),
        0: ("Sack yourself", "Bold strategy. The data had other ideas."),
    }
    title, sub = tiers.get(score, tiers[0])
    pct = score / total * 100
    st.html(f"""
<div class="sb-final">
  <div class="sb-caption">Full time</div>
  <div class="sb-ring" style="--target:{pct:.0f}"><div class="sb-ring-inner">
    <div class="sb-ring-num">{score}<small>/{total}</small></div>
  </div></div>
  <div class="sb-tier">{title}</div>
  <div class="sb-tier-sub">{sub}</div>
</div>
""")
    return st.button("Play again", key="play_again")


def home():
    """Landing page. Returns True when 'Start playing' is clicked."""
    st.html("""
<div class="sb-hero">
  <div class="sb-caption">Top 5 leagues · 2021/22 to 2025/26</div>
  <h1><span class="s">SACK</span><span class="or">or</span><span class="b">BACK</span></h1>
  <p>You're the sporting director. The season is going wrong. Would you fire the coach, or stand by him?</p>
</div>
<div class="sb-steps">
  <div class="sb-step"><div class="sb-step-n">01</div><div class="sb-step-t">Read the room</div><div class="sb-step-d">A real club at a real moment of crisis: form, points, table.</div></div>
  <div class="sb-step"><div class="sb-step-n">02</div><div class="sb-step-t">Swipe</div><div class="sb-step-d">Left to back the coach. Right to sack him.</div></div>
  <div class="sb-step"><div class="sb-step-n">03</div><div class="sb-step-t">Face the data</div><div class="sb-step-d">See what really happened and what similar clubs did instead.</div></div>
</div>
""")
    return st.button("Start playing →", key="start")