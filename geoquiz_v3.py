import streamlit as st
import pandas as pd
import re
import time
import requests
import plotly.express as px
from streamlit_plotly_events import plotly_events
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------------------------
# Continents (codés en dur — un pays ne change jamais de continent, pas besoin
# qu'Emma maintienne ça dans le Sheet, c'est réglé une fois pour toutes ici)
# ---------------------------------------------------------------------------
CONTINENT = {
    "ZAF":"Afrique","DZA":"Afrique","AGO":"Afrique","BEN":"Afrique","BWA":"Afrique",
    "BFA":"Afrique","BDI":"Afrique","CPV":"Afrique","CMR":"Afrique","COM":"Afrique",
    "COG":"Afrique","COD":"Afrique","CIV":"Afrique","DJI":"Afrique","EGY":"Afrique",
    "ERI":"Afrique","SWZ":"Afrique","ETH":"Afrique","GAB":"Afrique","GMB":"Afrique",
    "GHA":"Afrique","GIN":"Afrique","GNB":"Afrique","GNQ":"Afrique","KEN":"Afrique",
    "LSO":"Afrique","LBR":"Afrique","LBY":"Afrique","MDG":"Afrique","MWI":"Afrique",
    "MLI":"Afrique","MAR":"Afrique","MUS":"Afrique","MRT":"Afrique","MOZ":"Afrique",
    "NAM":"Afrique","NER":"Afrique","NGA":"Afrique","UGA":"Afrique","RWA":"Afrique",
    "STP":"Afrique","SEN":"Afrique","SYC":"Afrique","SLE":"Afrique","SOM":"Afrique",
    "SDN":"Afrique","SSD":"Afrique","TZA":"Afrique","TCD":"Afrique","TGO":"Afrique",
    "TUN":"Afrique","ZMB":"Afrique","ZWE":"Afrique","CAF":"Afrique",
    "AFG":"Asie","SAU":"Asie","ARM":"Asie","AZE":"Asie","BHR":"Asie","BGD":"Asie",
    "BTN":"Asie","MMR":"Asie","BRN":"Asie","KHM":"Asie","CHN":"Asie","CYP":"Asie",
    "PRK":"Asie","KOR":"Asie","ARE":"Asie","GEO":"Asie","IND":"Asie","IDN":"Asie",
    "IRQ":"Asie","IRN":"Asie","ISR":"Asie","JPN":"Asie","JOR":"Asie","KAZ":"Asie",
    "KGZ":"Asie","KWT":"Asie","LAO":"Asie","LBN":"Asie","MYS":"Asie","MDV":"Asie",
    "MNG":"Asie","NPL":"Asie","OMN":"Asie","UZB":"Asie","PAK":"Asie","PHL":"Asie",
    "QAT":"Asie","SGP":"Asie","LKA":"Asie","SYR":"Asie","TJK":"Asie","THA":"Asie",
    "TLS":"Asie","TKM":"Asie","TUR":"Asie","VNM":"Asie","YEM":"Asie",
    "ALB":"Europe","DEU":"Europe","AND":"Europe","AUT":"Europe","BEL":"Europe",
    "BLR":"Europe","BIH":"Europe","BGR":"Europe","HRV":"Europe","DNK":"Europe",
    "ESP":"Europe","EST":"Europe","FIN":"Europe","FRA":"Europe","GRC":"Europe",
    "HUN":"Europe","IRL":"Europe","ISL":"Europe","ITA":"Europe","LVA":"Europe",
    "LIE":"Europe","LTU":"Europe","LUX":"Europe","MKD":"Europe","MLT":"Europe",
    "MDA":"Europe","MCO":"Europe","MNE":"Europe","NOR":"Europe","NLD":"Europe",
    "POL":"Europe","PRT":"Europe","CZE":"Europe","ROU":"Europe","GBR":"Europe",
    "RUS":"Europe","SMR":"Europe","SRB":"Europe","SVK":"Europe","SVN":"Europe",
    "SWE":"Europe","CHE":"Europe","UKR":"Europe",
    "CAN":"Amérique","USA":"Amérique","MEX":"Amérique","ATG":"Amérique","BHS":"Amérique",
    "BRB":"Amérique","BLZ":"Amérique","CRI":"Amérique","CUB":"Amérique","DMA":"Amérique",
    "DOM":"Amérique","SLV":"Amérique","GRD":"Amérique","GTM":"Amérique","HTI":"Amérique",
    "HND":"Amérique","JAM":"Amérique","NIC":"Amérique","PAN":"Amérique","KNA":"Amérique",
    "LCA":"Amérique","VCT":"Amérique","TTO":"Amérique","ARG":"Amérique","BOL":"Amérique",
    "BRA":"Amérique","CHL":"Amérique","COL":"Amérique","ECU":"Amérique","GUY":"Amérique",
    "PRY":"Amérique","PER":"Amérique","SUR":"Amérique","URY":"Amérique","VEN":"Amérique",
    "AUS":"Océanie","FJI":"Océanie","KIR":"Océanie","MHL":"Océanie","FSM":"Océanie",
    "NRU":"Océanie","NZL":"Océanie","PLW":"Océanie","PNG":"Océanie","WSM":"Océanie",
    "SLB":"Océanie","TON":"Océanie","TUV":"Océanie","VUT":"Océanie",
}

# Coordonnées du centre de chaque pays (source: gavinr/world-countries-centroids,
# domaine public), utilisées pour placer un point cliquable par pays plutôt que
# de faire dépendre le clic du remplissage entier du polygone (ça évite le
# conflit avec le glisser/zoom de la carte, cf. plus bas).
CENTROIDS = {
    "AFG": (34.13, 66.59), "AGO": (-12.17, 17.65), "ALB": (41.14, 20.06),
    "AND": (42.55, 1.58), "ARE": (24.18, 54.28), "ARG": (-35.70, -64.53),
    "ARM": (40.18, 45.05), "ATG": (17.07, -61.79), "AUS": (-25.70, 134.02),
    "AUT": (47.63, 13.80), "AZE": (40.39, 48.63), "BDI": (-3.26, 29.89),
    "BEL": (50.62, 4.68), "BEN": (9.50, 2.31), "BFA": (12.11, -1.69),
    "BGD": (23.67, 90.43), "BGR": (42.82, 25.25), "BHR": (26.05, 50.54),
    "BHS": (24.72, -78.07), "BIH": (44.14, 17.83), "BLR": (53.47, 27.96),
    "BLZ": (17.24, -88.68), "BOL": (-16.73, -64.45), "BRA": (-11.52, -54.36),
    "BRB": (13.18, -59.56), "BRN": (4.54, 114.64), "BTN": (27.42, 90.47),
    "BWA": (-22.24, 23.86), "CAF": (6.33, 20.52), "CAN": (57.55, -98.42),
    "CHE": (46.74, 8.29), "CHL": (-37.83, -70.77), "CHN": (38.07, 104.69),
    "CIV": (7.54, -5.57), "CMR": (6.29, 12.95), "COD": (-3.34, 23.42),
    "COG": (-0.73, 14.88), "COL": (4.19, -72.64), "COM": (-11.66, 43.35),
    "CPV": (15.08, -23.63), "CRI": (9.86, -84.15), "CUB": (21.48, -79.70),
    "CYP": (35.12, 33.38), "CZE": (49.75, 15.38), "DEU": (51.08, 10.43),
    "DJI": (11.75, 42.61), "DMA": (15.43, -61.36), "DNK": (56.00, 9.38),
    "DOM": (18.78, -70.43), "DZA": (28.35, 2.66), "ECU": (-1.56, -78.46),
    "EGY": (26.61, 30.24), "ERI": (15.01, 39.27), "ESP": (28.30, -16.54),
    "EST": (58.65, 25.92), "ETH": (8.73, 39.91), "FIN": (65.02, 25.66),
    "FJI": (-17.82, 177.98), "FRA": (46.64, 2.19), "FSM": (6.88, 158.23),
    "GAB": (-0.63, 11.84), "GBR": (53.98, -2.85), "GEO": (42.18, 43.38),
    "GHA": (7.95, -1.22), "GIN": (10.26, -10.99), "GMB": (13.43, -15.38),
    "GNB": (11.98, -14.98), "GNQ": (1.60, 10.43), "GRC": (39.42, 23.11),
    "GRD": (12.11, -61.68), "GTM": (15.82, -90.31), "GUY": (4.68, -58.91),
    "HND": (14.74, -86.49), "HRV": (44.91, 16.63), "HTI": (18.88, -72.89),
    "HUN": (47.23, 19.40), "IDN": (0.16, 113.97), "IND": (23.59, 81.17),
    "IRL": (53.30, -8.24), "IRN": (32.91, 54.24), "IRQ": (33.11, 43.83),
    "ISL": (65.12, -19.06), "ISR": (31.51, 35.03), "ITA": (42.98, 12.76),
    "JAM": (18.12, -77.30), "JOR": (31.39, 36.96), "JPN": (36.77, 137.47),
    "KAZ": (47.64, 66.38), "KEN": (0.69, 37.95), "KGZ": (41.36, 74.18),
    "KHM": (12.70, 105.04), "KIR": (1.87, -157.39), "KNA": (17.31, -62.75),
    "KOR": (36.40, 127.76), "KWT": (29.28, 47.56), "LAO": (18.12, 103.76),
    "LBN": (33.91, 35.90), "LBR": (6.52, -9.26), "LBY": (27.20, 17.91),
    "LCA": (13.90, -60.97), "LIE": (47.15, 9.55), "LKA": (7.70, 80.67),
    "LSO": (-29.60, 28.24), "LTU": (55.29, 23.95), "LUX": (49.78, 6.10),
    "LVA": (56.81, 24.69), "MAR": (28.69, -8.82), "MCO": (43.75, 7.41),
    "MDA": (47.07, 28.39), "MDG": (-19.04, 46.68), "MDV": (-0.61, 73.10),
    "MEX": (23.87, -101.55), "MHL": (7.31, 168.72), "MKD": (41.59, 21.71),
    "MLI": (17.17, -4.35), "MLT": (35.89, 14.44), "MMR": (19.90, 97.09),
    "MNE": (42.74, 19.30), "MNG": (47.09, 103.40), "MOZ": (-17.53, 35.21),
    "MRT": (20.47, -10.50), "MUS": (-20.28, 57.56), "MWI": (-13.13, 34.23),
    "MYS": (3.67, 114.63), "NAM": (-21.91, 18.16), "NER": (17.08, 8.87),
    "NGA": (9.61, 8.15), "NIC": (12.89, -85.02), "NLD": (52.13, 5.55),
    "NOR": (64.98, 16.67), "NPL": (28.30, 84.13), "NRU": (-0.52, 166.93),
    "NZL": (-43.83, 170.69), "OMN": (20.72, 55.84), "PAK": (30.12, 69.09),
    "PAN": (8.44, -80.14), "PER": (-8.52, -74.11), "PHL": (15.59, 121.82),
    "PLW": (7.53, 134.58), "PNG": (-7.16, 144.83), "POL": (52.07, 19.44),
    "PRK": (40.19, 127.34), "PRT": (39.68, -7.93), "PRY": (-23.42, -58.39),
    "QAT": (25.32, 51.20), "ROU": (45.82, 25.09), "RUS": (59.04, 98.67),
    "RWA": (-2.01, 29.92), "SAU": (24.14, 44.60), "SDN": (15.67, 29.95),
    "SEN": (14.23, -14.61), "SGP": (1.35, 103.81), "SLB": (-9.61, 160.16),
    "SLE": (8.56, -11.79), "SLV": (13.76, -88.86), "SMR": (43.94, 12.46),
    "SOM": (6.52, 45.40), "SRB": (44.03, 20.86), "SSD": (7.66, 30.39),
    "STP": (0.23, 6.61), "SUR": (4.10, -55.86), "SVK": (48.70, 19.58),
    "SVN": (46.14, 14.89), "SWE": (62.73, 17.06), "SWZ": (-26.56, 31.51),
    "SYC": (-4.66, 55.47), "SYR": (35.10, 38.51), "TCD": (15.28, 18.43),
    "TGO": (8.66, 0.90), "THA": (13.66, 101.09), "TJK": (38.57, 70.94),
    "TKM": (39.06, 58.46), "TLS": (-8.81, 125.95), "TON": (-21.16, -175.20),
    "TTO": (10.42, -61.37), "TUN": (34.09, 9.66), "TUR": (38.93, 35.57),
    "TUV": (-8.51, 179.22), "TZA": (-6.36, 34.82), "UGA": (1.28, 32.34),
    "UKR": (48.66, 31.27), "URY": (-32.78, -56.02), "USA": (38.82, -96.33),
    "UZB": (41.49, 63.85), "VCT": (13.25, -61.19), "VEN": (7.15, -66.36),
    "VNM": (16.52, 105.91), "VUT": (-15.19, 166.85), "WSM": (-13.63, -172.44),
    "YEM": (16.00, 47.47), "ZAF": (-28.55, 24.75), "ZMB": (-13.16, 27.76),
    "ZWE": (-18.93, 29.72),
}

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT9uBtHmtYAEQTp9GqAcr9Q3bMIDDrCYl6iQtIx-6g7K8-ZiSAbpe6E3zI-s1PnqyoKNTGI5LLip83X/pub?gid=1570862950&single=true&output=csv"

DEMO_DATA = [
    {"pays": "France", "code_iso3": "FRA", "dirigeant": "Emmanuel Macron - President", "alias": "", "photo_url": ""},
    {"pays": "Etats-Unis", "code_iso3": "USA", "dirigeant": "Donald Trump - President", "alias": "", "photo_url": ""},
    {"pays": "Chine", "code_iso3": "CHN", "dirigeant": "Xi Jinping - President", "alias": "", "photo_url": ""},
    {"pays": "Allemagne", "code_iso3": "DEU", "dirigeant": "Friedrich Merz - Chancelier", "alias": "", "photo_url": ""},
    {"pays": "Japon", "code_iso3": "JPN", "dirigeant": "", "alias": "", "photo_url": ""},
]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wikipedia_photo(full_name: str) -> str:
    """Va chercher la photo d'un dirigeant sur Wikipedia (FR puis EN) a partir
    de son nom, pour eviter d'avoir 163 liens a maintenir a la main."""
    name = full_name.strip()
    if not name:
        return ""
    for lang in ("fr", "en"):
        try:
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
            resp = requests.get(url, timeout=4, headers={"User-Agent": "AtlasQuiz/1.0"})
            if resp.status_code == 200:
                thumb = resp.json().get("thumbnail", {}).get("source", "")
                if thumb:
                    return thumb
        except Exception:
            continue
    return ""


def strip_title(dirigeant_field: str) -> str:
    """'Friedrich Merz - Chancelier' -> 'Friedrich Merz'"""
    return re.split(r"\s+-\s+", dirigeant_field, maxsplit=1)[0].strip()


@st.cache_data(ttl=300)
def load_data():
    """
    RÈGLE DE FILTRAGE (silencieuse) : la ligne 2 du Sheet est une ligne
    d'explication des colonnes destinee a Emma. On la detecte en verifiant
    que code_iso3 fait exactement 3 lettres MAJUSCULES (un vrai code ISO3
    respecte toujours ce format, un texte d'explication non) et on l'exclut.
    """
    if SHEET_CSV_URL.startswith("REMPLACE_MOI"):
        return pd.DataFrame(DEMO_DATA), False
    try:
        df = pd.read_csv(SHEET_CSV_URL, dtype=str).fillna("")
        df = df[df["code_iso3"].str.fullmatch(r"[A-Z]{3}")]
        return df, True
    except Exception:
        return pd.DataFrame(DEMO_DATA), False


df, is_live = load_data()
df["continent"] = df["code_iso3"].map(CONTINENT).fillna("Autre")
df_lvl2 = df[df["dirigeant"].str.strip() != ""]  # pool niveau 2 : dirigeant renseigné uniquement

LEVEL_INFO = {
    1: {"label": "Niveau 1", "sub": "Repère le pays", "icon": "🗺️", "points": 10},
    2: {"label": "Niveau 2", "sub": "Trouve le/la dirigeant·e", "icon": "🎓", "points": 15},
}

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Atlas Quiz", page_icon="🗺️", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F0EBDD; }
    h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #1C2B3A; }
    .stButton>button {
        background-color: #1C2B3A; color: white; border-radius: 6px;
        border: none; font-weight: 600; padding: 8px 20px; width: 100%;
    }
    .stButton>button:hover { background-color: #C4523D; color: white; }
    .level-banner {
        background: #1C2B3A; color: #F0EBDD; border-radius: 10px;
        padding: 14px 18px; margin-bottom: 12px; display: flex;
        justify-content: space-between; align-items: center;
    }
    .level-banner .lvl-title { font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; }
    .level-banner .lvl-sub { font-size: 13px; opacity: 0.8; }
    .level-banner .manche { font-size: 13px; opacity: 0.9; text-align: right; }
    .prompt-box {
        background: #fff8ea; border: 1px solid #B8934A; border-radius: 8px;
        padding: 14px 18px; font-size: 17px; margin-bottom: 12px; color: #1C2B3A;
        text-align: center;
    }
    .score-badge {
        display: inline-block; background: #C4523D; color: white;
        padding: 4px 14px; border-radius: 999px; font-weight: 700;
        font-family: 'Fraunces', serif; font-size: 18px;
    }
    .leader-photo {
        display: block; margin: 0 auto 10px auto; width: 130px; height: 130px;
        object-fit: cover; border-radius: 8px; border: 3px solid #B8934A;
    }
    .demo-banner {
        background: #C4523D; color: white; padding: 6px 12px; border-radius: 6px;
        font-size: 13px; text-align: center; margin-bottom: 12px;
    }
    .recap-box {
        background: #3F6B4F; color: white; padding: 20px; border-radius: 10px;
        text-align: center; margin-top: 12px;
    }
    .recap-box .big { font-family: 'Fraunces', serif; font-size: 36px; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# État de session
# ---------------------------------------------------------------------------
defaults = {
    "score": 0, "level": 1, "feedback": None, "target": None,
    "manche": 1, "total_manches": None,  # None = illimité
    "game_over": False, "wrong_attempts": set(),
    "continent": "Monde entier", "chrono_sec": None,  # None = pas de chrono
    "round_start": None, "best_score": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def pick_target(level):
    pool = df if level == 1 else df_lvl2
    if st.session_state.continent != "Monde entier":
        pool = pool[pool["continent"] == st.session_state.continent]
    if pool.empty:  # filet de sécurité si un continent+niveau 2 n'a aucun pays rempli
        pool = df if level == 1 else df_lvl2
    return pool.sample(1).iloc[0]


if st.session_state.target is None:
    st.session_state.target = pick_target(st.session_state.level)

# ---------------------------------------------------------------------------
# Réglages (repliable, pour ne pas encombrer)
# ---------------------------------------------------------------------------
CONTINENTS = ["Monde entier", "Afrique", "Asie", "Europe", "Amérique", "Océanie"]
CHRONO_OPTIONS = ["Aucun", "10s", "20s", "30s"]

with st.expander("⚙️ Paramètres de la partie"):
    c1, c2 = st.columns(2)
    with c1:
        options = ["Illimité", "5", "10", "20"]
        current = "Illimité" if st.session_state.total_manches is None else str(st.session_state.total_manches)
        mode = st.radio("Nombre de manches", options, horizontal=True,
                         index=options.index(current) if current in options else 0)
        zone = st.selectbox("Zone géographique", CONTINENTS,
                             index=CONTINENTS.index(st.session_state.continent))
    with c2:
        chrono_current = "Aucun" if st.session_state.chrono_sec is None else f"{st.session_state.chrono_sec}s"
        chrono_choice = st.radio("Chrono par manche", CHRONO_OPTIONS, horizontal=True,
                                  index=CHRONO_OPTIONS.index(chrono_current) if chrono_current in CHRONO_OPTIONS else 0)

    if st.button("🔄 Nouvelle partie avec ces réglages"):
        st.session_state.total_manches = None if mode == "Illimité" else int(mode)
        st.session_state.continent = zone
        st.session_state.chrono_sec = None if chrono_choice == "Aucun" else int(chrono_choice.replace("s", ""))
        st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
        st.session_state.score = 0
        st.session_state.manche = 1
        st.session_state.game_over = False
        st.session_state.target = pick_target(st.session_state.level)
        st.session_state.feedback = None
        st.session_state.wrong_attempts = set()
        st.session_state.round_start = time.time()
        st.rerun()
# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.title("🗺️ Atlas Quiz")
with top_col2:
    best = max(st.session_state.best_score, st.session_state.score)
    st.markdown(
        f'<div style="text-align:right;padding-top:10px">'
        f'<span class="score-badge">{st.session_state.score} pts</span>'
        f'<div style="font-size:11px;color:#5a5142;margin-top:4px">🏆 record : {best} pts</div></div>',
        unsafe_allow_html=True,
    )

if not is_live:
    st.markdown(
        '<div class="demo-banner">⚠️ Mode démo — le Google Sheet n\'est pas encore branché</div>',
        unsafe_allow_html=True,
    )

level_choice = st.radio(
    "Niveau",
    [1, 2],
    format_func=lambda n: f"{LEVEL_INFO[n]['icon']} {LEVEL_INFO[n]['label']} — {LEVEL_INFO[n]['sub']}",
    horizontal=True,
    label_visibility="collapsed",
)
if level_choice != st.session_state.level:
    st.session_state.level = level_choice
    st.session_state.target = pick_target(level_choice)
    st.session_state.feedback = None
    st.session_state.wrong_attempts = set()
    st.session_state.round_start = time.time()
    st.rerun()

level = st.session_state.level
info = LEVEL_INFO[level]

if st.session_state.round_start is None:
    st.session_state.round_start = time.time()

remaining = None
if st.session_state.chrono_sec and st.session_state.feedback is None and not st.session_state.game_over:
    elapsed = time.time() - st.session_state.round_start
    remaining = max(0, st.session_state.chrono_sec - elapsed)
    st_autorefresh(interval=500, key=f"chrono_{st.session_state.manche}_{level}")
    if remaining <= 0:
        st.session_state.feedback = "timeout"

manche_txt = f"Manche {st.session_state.manche}" + (f" / {st.session_state.total_manches}" if st.session_state.total_manches else "")
chrono_txt = f" · ⏱️ {int(remaining)}s" if remaining is not None else ""
st.markdown(
    f'<div class="level-banner"><div><div class="lvl-title">{info["icon"]} {info["label"]}</div>'
    f'<div class="lvl-sub">{info["sub"]}</div></div><div class="manche">{manche_txt}{chrono_txt}</div></div>',
    unsafe_allow_html=True,
)

target = st.session_state.target

# ---------------------------------------------------------------------------
# Fin de partie
# ---------------------------------------------------------------------------
if st.session_state.game_over:
    st.markdown(
        f'<div class="recap-box"><div>Partie terminée !</div>'
        f'<div class="big">{st.session_state.score} pts</div>'
        f'<div>en {st.session_state.total_manches} manches</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("🔁 Rejouer"):
        st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
        st.session_state.score = 0
        st.session_state.manche = 1
        st.session_state.game_over = False
        st.session_state.target = pick_target(level)
        st.session_state.feedback = None
        st.session_state.wrong_attempts = set()
        st.session_state.round_start = time.time()
        st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# Consigne
# ---------------------------------------------------------------------------
if level == 1:
    st.markdown(f'<div class="prompt-box">Clique sur <b>{target["pays"]}</b></div>', unsafe_allow_html=True)
else:
    leader_name = strip_title(target["dirigeant"])
    photo = target["photo_url"] if target["photo_url"] else fetch_wikipedia_photo(leader_name)
    if photo:
        st.markdown(f'<img src="{photo}" class="leader-photo">', unsafe_allow_html=True)
    else:
        st.caption("(photo introuvable pour ce nom — vérifie l'orthographe dans le Sheet)")
    st.markdown(
        f'<div class="prompt-box">Clique sur le pays dirigé par <b>{target["dirigeant"]}</b></div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Carte
# ---------------------------------------------------------------------------
map_df = df.copy()
map_df["couleur"] = "#D8CFAE"
for iso3 in st.session_state.wrong_attempts:
    map_df.loc[map_df["code_iso3"] == iso3, "couleur"] = "#C4523D"
if st.session_state.feedback in ("revealed", "timeout"):
    map_df.loc[map_df["code_iso3"] == target["code_iso3"], "couleur"] = "#C4523D"
if st.session_state.feedback == "correct":
    map_df.loc[map_df["code_iso3"] == target["code_iso3"], "couleur"] = "#3F6B4F"

import plotly.graph_objects as go  # noqa: E402  (ajouté ici pour rester proche de son usage)

fig = px.choropleth(
    map_df,
    locations="code_iso3",
    locationmode="ISO-3",
    color="couleur",
    color_discrete_map="identity",
    projection="natural earth",
)
fig.update_traces(
    marker_line_color="#1C2B3A",
    marker_line_width=0.5,
    hoverinfo="skip",  # ce calque ne sert plus qu'à l'affichage des couleurs, plus au clic
)

# Calque de clic : un petit point au centre de chaque pays. C'est ce calque qui
# capte les clics, pas le remplissage du pays — ça règle le conflit avec le
# glisser/zoom de la carte (un polygone entier cliquable interceptait aussi les
# relâchers de glisser-déposer comme des clics, un point ponctuel non).
lats = [CENTROIDS.get(iso3, (None, None))[0] for iso3 in map_df["code_iso3"]]
lons = [CENTROIDS.get(iso3, (None, None))[1] for iso3 in map_df["code_iso3"]]
fig.add_trace(go.Scattergeo(
    lat=lats, lon=lons, mode="markers",
    marker=dict(size=22, color="rgba(0,0,0,0)", line=dict(width=0)),  # invisible mais cliquable
    hovertemplate=" <extra></extra>",
))

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="#F0EBDD",
    geo=dict(bgcolor="#F0EBDD", showframe=False, showcoastlines=True, coastlinecolor="#1C2B3A"),
    showlegend=False,
    height=420,
    dragmode="pan",  # glisser/zoom pleinement actifs à nouveau
)

clicked = plotly_events(fig, click_event=True, key=f"map_{level}_{target['code_iso3']}_{st.session_state.feedback}")

if clicked and st.session_state.feedback not in ("correct", "timeout"):
    point = clicked[0]
    if point.get("curveNumber") == 1:  # 0 = choropleth (ignoré), 1 = calque de points cliquables
        point_index = point.get("pointIndex", point.get("pointNumber"))
        clicked_row = map_df.iloc[point_index]
        if clicked_row["code_iso3"] == target["code_iso3"]:
            st.session_state.score += info["points"]
            st.session_state.feedback = "correct"
            st.rerun()
        else:
            st.session_state.wrong_attempts.add(clicked_row["code_iso3"])
            st.session_state.feedback = "wrong"
            st.rerun()

if st.session_state.feedback == "wrong":
    st.error("Pas ce pays-là — réessaie.")
elif st.session_state.feedback == "correct":
    st.success(f"Correct ! +{info['points']} pts")
elif st.session_state.feedback == "timeout":
    st.warning(f"⏱️ Temps écoulé ! C'était **{target['pays']}**" + (f" — {target['dirigeant']}" if level == 2 else ""))
elif st.session_state.feedback == "revealed":
    st.info(f"C'était **{target['pays']}**" + (f" — {target['dirigeant']}" if level == 2 else "") + " (pays surligné en rouge sur la carte)")


def go_next():
    st.session_state.manche += 1
    st.session_state.wrong_attempts = set()
    if st.session_state.total_manches and st.session_state.manche > st.session_state.total_manches:
        st.session_state.game_over = True
        st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
    else:
        st.session_state.target = pick_target(level)
        st.session_state.feedback = None
        st.session_state.round_start = time.time()


col1, col2 = st.columns(2)
with col1:
    if st.button("Pays suivant →" if st.session_state.feedback else "Passer →"):
        go_next()
        st.rerun()
with col2:
    if st.button("👁️ Révéler", disabled=st.session_state.feedback in ("correct", "timeout")):
        st.session_state.feedback = "revealed"
        st.rerun()

st.caption(f"{len(df)} pays chargés ({len(df_lvl2)} avec dirigeant renseigné)" + (" — Google Sheet en direct" if is_live else " — données de démo"))