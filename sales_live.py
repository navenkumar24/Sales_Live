import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
from datetime import datetime, timedelta
from collections import deque

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Live Revenue Pulse",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #080d14;
    --surface: #0e1825;
    --border: #1a2e45;
    --accent: #00ffe7;
    --accent2: #ff6b35;
    --accent3: #a259ff;
    --green: #39ff14;
    --yellow: #ffe600;
    --red: #ff3366;
    --text: #c8dff0;
    --dim: #4a6a8a;
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="block-container"] { padding: 1rem 2rem !important; }
.stMetric { background: transparent !important; }
div[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}
[data-testid="stMetricLabel"] > div {
    color: var(--dim) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] > div {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--dim);
    border-left: 3px solid var(--accent);
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── Hero Title ── */
.hero {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 0.25rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
    line-height: 1;
}
.hero-pulse {
    width: 10px; height: 10px;
    background: var(--green);
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 12px var(--green);
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 12px var(--green); }
    50% { opacity: 0.4; box-shadow: 0 0 4px var(--green); }
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.timestamp {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 0.08em;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* ── Weather Badge ── */
.weather-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.weather-badge {
    background: #0a1a2a;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    min-width: 140px;
}
.badge-city { color: #fff; font-weight: 700; }
.badge-temp { color: var(--accent); }
.badge-cond { color: var(--dim); font-size: 0.62rem; }
.badge-alert { color: var(--red); font-size: 0.6rem; letter-spacing: 0.1em; }

/* ── Feed Table ── */
.feed-row {
    display: grid;
    grid-template-columns: 90px 1fr 100px 110px 90px;
    gap: 0.5rem;
    align-items: center;
    padding: 0.55rem 0.8rem;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    transition: background 0.15s;
    border-left: 2px solid transparent;
}
.feed-row:hover { background: rgba(0,255,231,0.03); }
.feed-row.new {
    background: rgba(0,255,231,0.06);
    border-left-color: var(--accent);
    animation: slide-in 0.3s ease;
}
@keyframes slide-in {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
.feed-header {
    color: var(--dim);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.3rem;
}
.price-val { color: var(--green); }
.city-val  { color: var(--text); }
.cat-tag {
    background: rgba(162,89,255,0.15);
    border: 1px solid rgba(162,89,255,0.3);
    color: var(--accent3);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.6rem;
}
.brand-val { color: var(--accent2); }

/* ── Bar Charts (CSS) ── */
.bar-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.55rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.67rem;
}
.bar-label { width: 110px; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-track { flex: 1; background: var(--border); border-radius: 3px; height: 6px; }
.bar-fill  { height: 6px; border-radius: 3px; }
.bar-value { width: 60px; text-align: right; color: var(--dim); }

/* ── Ticker ── */
.ticker-wrap {
    background: var(--surface);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
    padding: 0.4rem 0;
    margin: 1rem 0;
}
.ticker-inner {
    display: flex;
    gap: 3rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: var(--dim);
    white-space: nowrap;
}
.ticker-item span { color: var(--accent); }

/* ── Heatmap Table ── */
.heatmap-wrap {
    overflow-x: auto;
    border-radius: 10px;
    border: 1px solid var(--border);
}
.heatmap-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
}
.heatmap-table th {
    background: #0a1520;
    color: var(--dim);
    padding: 0.5rem 0.7rem;
    text-align: right;
    font-weight: 700;
    letter-spacing: 0.08em;
    white-space: nowrap;
    border-bottom: 1px solid var(--border);
}
.heatmap-table th:first-child { text-align: left; }
.heatmap-table td {
    padding: 0.45rem 0.7rem;
    text-align: right;
    border-bottom: 1px solid rgba(26,46,69,0.5);
    color: #fff;
    white-space: nowrap;
}
.heatmap-table td:first-child {
    text-align: left;
    color: var(--text);
    font-weight: 700;
}
.heatmap-table tr:last-child td { border-bottom: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Streamlit overrides ── */
[data-testid="stDataFrame"] { background: var(--surface) !important; }
.stDataFrame > div { background: transparent !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA: PRODUCTS, BRANDS, CITIES
# ─────────────────────────────────────────────
PRODUCTS = {
    "Electronics": {
        "Apple":   [("iPhone 15 Pro", 1299), ("MacBook Air M3", 1499), ("AirPods Pro", 249), ("iPad Pro", 1099)],
        "Samsung": [("Galaxy S24 Ultra", 1199), ("Galaxy Tab S9", 799), ("Galaxy Buds2", 149), ("65\" QLED TV", 1299)],
        "Sony":    [("WH-1000XM5", 349), ("PlayStation 5", 499), ("Bravia XR 55\"", 1099), ("ZV-E10 Camera", 749)],
        "Dell":    [("XPS 15 Laptop", 1799), ("UltraSharp 27\"", 599), ("Inspiron 14", 699)],
        "LG":      [("OLED C3 65\"", 1799), ("UltraGear 27\"", 449), ("Gram 16 Laptop", 1299)],
    },
    "Fashion": {
        "Nike":    [("Air Max 270", 150), ("Dri-FIT Tee", 35), ("Windrunner Jacket", 110), ("React Infinity Run", 160)],
        "Adidas":  [("Ultraboost 23", 190), ("Originals Hoodie", 80), ("Stan Smith", 90), ("Tiro Track Suit", 70)],
        "Zara":    [("Linen Blazer", 89), ("Slim Chinos", 49), ("Knit Midi Dress", 69), ("Leather Sneakers", 99)],
        "H&M":     [("Oversized Tee", 19), ("Straight Jeans", 39), ("Puffer Jacket", 59), ("Ribbed Sweater", 29)],
        "Puma":    [("RS-X Sneakers", 110), ("Essentials Shorts", 30), ("Poly Training Tee", 25)],
    },
    "Home & Kitchen": {
        "Dyson":   [("V15 Detect Vacuum", 699), ("Airwrap Styler", 599), ("Pure Cool Fan", 449), ("Hot+Cool HP07", 549)],
        "Philips": [("Air Fryer XXL", 199), ("Espresso 3200", 799), ("Smart Blender", 149), ("Hue Starter Kit", 99)],
        "IKEA":    [("KALLAX Shelf", 149), ("MALM Bed Frame", 299), ("POÄNG Chair", 129), ("BESTA Storage", 199)],
        "Instant": [("Pot Duo 7-in-1", 89), ("Vortex Air Fryer", 79), ("Pot Pro", 119)],
        "Bosch":   [("Dishwasher Serie 6", 849), ("Washing Machine", 699), ("Fridge-Freezer", 999)],
    },
    "Sports & Fitness": {
        "Garmin":  [("Forerunner 265", 449), ("Fenix 7X", 899), ("Venu 3", 449), ("Edge 840 Cycling", 599)],
        "Fitbit":  [("Charge 6", 159), ("Sense 2", 249), ("Inspire 3", 99)],
        "Decathlon": [("Trekking Poles", 49), ("Yoga Mat Pro", 39), ("Road Bike 520", 899), ("Swim Goggles", 19)],
        "Peloton": [("Bike+", 2495), ("Tread", 2995), ("Row", 3195), ("Guide Camera", 295)],
        "Under Armour": [("HOVR Phantom 3", 140), ("Project Rock 5", 130), ("Rush Tights", 65)],
    },
    "Beauty & Personal Care": {
        "L'Oréal": [("Revitalift Serum", 39), ("True Match Foundation", 19), ("Elvive Shampoo", 12), ("Men Expert Cream", 17)],
        "The Ordinary": [("Niacinamide 10%", 10), ("Hyaluronic Acid", 9), ("Retinol 0.5%", 13), ("AHA 30% Peel", 14)],
        "Clinique": [("Moisture Surge 100H", 49), ("Even Better SPF20", 45), ("Dramatically Different+", 39)],
        "Mamaearth": [("Onion Hair Oil", 12), ("Vitamin C Face Wash", 9), ("Ubtan Face Pack", 11)],
        "Himalaya": [("Neem Face Wash", 7), ("Aloe Vera Gel", 8), ("Protein Shampoo", 10)],
    },
    "Books & Media": {
        "Penguin":  [("Atomic Habits", 18), ("Sapiens", 22), ("The Alchemist", 14), ("Rich Dad Poor Dad", 16)],
        "O'Reilly": [("Python Cookbook", 59), ("Designing ML Systems", 55), ("Clean Code", 42)],
        "Amazon":   [("Kindle Paperwhite", 139), ("Fire HD 10", 149), ("Echo Dot 5th Gen", 49)],
        "Marvel":   [("Avengers Omnibus", 99), ("X-Men Epic", 49), ("Daredevil Born Again", 29)],
    },
}

CITIES = [
    "Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Dubai", "Singapore", "London", "New York", "Tokyo",
    "Sydney", "Toronto", "Paris", "Berlin", "Bangkok",
]

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "sales_log" not in st.session_state:
    st.session_state.sales_log = []
if "total_revenue" not in st.session_state:
    st.session_state.total_revenue = 0.0
if "order_count" not in st.session_state:
    st.session_state.order_count = 0
if "prev_revenue" not in st.session_state:
    st.session_state.prev_revenue = 0.0
if "last_sale_time" not in st.session_state:
    st.session_state.last_sale_time = time.time()
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}
if "weather_ts" not in st.session_state:
    st.session_state.weather_ts = 0

# ─────────────────────────────────────────────
#  SALE GENERATOR
# ─────────────────────────────────────────────
def generate_sale():
    category = random.choice(list(PRODUCTS.keys()))
    brand    = random.choice(list(PRODUCTS[category].keys()))
    product, base_price = random.choice(PRODUCTS[category][brand])
    price    = round(base_price * random.uniform(0.85, 1.15), 2)
    city     = random.choice(CITIES)
    qty      = random.randint(1, 3)
    total    = round(price * qty, 2)
    return {
        "time":     datetime.now().strftime("%H:%M:%S"),
        "product":  product,
        "category": category,
        "brand":    brand,
        "price":    price,
        "qty":      qty,
        "total":    total,
        "city":     city,
    }

# ─────────────────────────────────────────────
#  WEATHER FETCH  (Open-Meteo – free, no key)
# ─────────────────────────────────────────────
CITY_COORDS = {
    "Chennai":   (13.08, 80.27), "Mumbai":    (19.07, 72.87),
    "Delhi":     (28.61, 77.20), "Bangalore": (12.97, 77.59),
    "Hyderabad": (17.38, 78.48), "Kolkata":   (22.57, 88.36),
    "Pune":      (18.52, 73.86), "Ahmedabad": (23.02, 72.57),
    "Jaipur":    (26.91, 75.79), "Surat":     (21.17, 72.83),
    "Dubai":     (25.20, 55.27), "Singapore": (1.35, 103.82),
    "London":    (51.51, -0.13), "New York":  (40.71, -74.01),
    "Tokyo":     (35.68, 139.69),"Sydney":    (-33.87, 151.21),
    "Toronto":   (43.65, -79.38),"Paris":     (48.86, 2.35),
    "Berlin":    (52.52, 13.40), "Bangkok":   (13.76, 100.50),
}
WMO_CODES = {
    0: ("Clear Sky", "☀️"), 1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"), 3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"), 51: ("Light Drizzle", "🌦️"),
    61: ("Light Rain", "🌧️"), 63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "⛈️"), 71: ("Light Snow", "🌨️"),
    80: ("Showers", "🌧️"), 95: ("Thunderstorm", "⛈️"),
}

@st.cache_data(ttl=300)
def fetch_weather_batch(cities):
    results = {}
    for city in cities:
        if city not in CITY_COORDS:
            continue
        lat, lon = CITY_COORDS[city]
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current_weather=true"
                f"&hourly=precipitation_probability"
                f"&forecast_days=1"
            )
            r = requests.get(url, timeout=4)
            if r.status_code == 200:
                d = r.json()
                cw = d.get("current_weather", {})
                code = cw.get("weathercode", 0)
                temp = cw.get("temperature", 0)
                desc, icon = WMO_CODES.get(code, ("Unknown", "🌡️"))
                rain_alert  = code in (61, 63, 65, 80, 95)
                heat_alert  = temp > 35
                results[city] = {
                    "temp": temp, "desc": desc, "icon": icon,
                    "rain": rain_alert, "heat": heat_alert, "code": code
                }
        except Exception:
            pass
    return results

# ─────────────────────────────────────────────
#  HEATMAP HELPER  (pure HTML/CSS, no matplotlib)
# ─────────────────────────────────────────────
def val_to_color(val, min_val, max_val):
    """Map a value to a CSS rgba color on a dark-orange-red scale."""
    if max_val == min_val:
        ratio = 0.0
    else:
        ratio = (val - min_val) / (max_val - min_val)
    if val == 0:
        return "background:rgba(10,20,32,0.6); color:#1a2e45;"
    # dark teal → amber → red-orange
    r = int(10  + ratio * 245)
    g = int(180 - ratio * 150)
    b = int(100 - ratio * 90)
    alpha = 0.25 + ratio * 0.65
    text_color = "#fff" if ratio > 0.25 else "#4a6a8a"
    return f"background:rgba({r},{g},{b},{alpha:.2f}); color:{text_color};"

def render_heatmap(pivot_df):
    """Render a pivot table as a fully themed CSS heatmap — no matplotlib needed."""
    if pivot_df.empty:
        return "<p style='color:var(--dim);font-size:0.7rem;font-family:Space Mono,monospace'>No data yet…</p>"

    all_vals = pivot_df.values.flatten()
    min_val  = float(all_vals[all_vals > 0].min()) if (all_vals > 0).any() else 0
    max_val  = float(all_vals.max())

    # Header row
    html = '<div class="heatmap-wrap"><table class="heatmap-table"><thead><tr>'
    html += "<th>CATEGORY</th>"
    for brand in pivot_df.columns:
        html += f"<th>{brand}</th>"
    html += "</tr></thead><tbody>"

    for cat, row in pivot_df.iterrows():
        html += f"<tr><td>{cat}</td>"
        for val in row:
            style = val_to_color(val, min_val, max_val)
            display = f"₹{val:,.0f}" if val > 0 else "—"
            html += f'<td style="{style}">{display}</td>'
        html += "</tr>"

    html += "</tbody></table></div>"
    return html

# ─────────────────────────────────────────────
#  TICK: add ~2 sales per 5-second refresh
# ─────────────────────────────────────────────
now = time.time()
elapsed = now - st.session_state.last_sale_time
new_count = max(1, int(elapsed / 2))   # ~1 sale per 2 sec

st.session_state.prev_revenue = st.session_state.total_revenue
for _ in range(new_count):
    sale = generate_sale()
    st.session_state.sales_log.insert(0, sale)
    st.session_state.total_revenue += sale["total"]
    st.session_state.order_count   += 1

if len(st.session_state.sales_log) > 200:
    st.session_state.sales_log = st.session_state.sales_log[:200]

st.session_state.last_sale_time = now
df = pd.DataFrame(st.session_state.sales_log)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
col_title, col_ts = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div class="hero">
        <span class="hero-title">REVENUE PULSE</span>
        <span class="hero-pulse"></span>
    </div>
    <div class="hero-sub">Live Sales Intelligence Dashboard · Auto-Refresh 5s</div>
    """, unsafe_allow_html=True)
with col_ts:
    st.markdown(f"""
    <div style="text-align:right; padding-top:1.2rem;">
        <div class="timestamp">⟳ {datetime.now().strftime('%d %b %Y · %H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  KPI METRICS
# ─────────────────────────────────────────────
rev_delta = st.session_state.total_revenue - st.session_state.prev_revenue
avg_order = st.session_state.total_revenue / max(1, st.session_state.order_count)
recent_df = df.head(10) if len(df) >= 10 else df
recent_rev = recent_df["total"].sum() if len(recent_df) > 0 else 0
top_cat   = df["category"].value_counts().idxmax() if len(df) > 0 else "—"
top_brand = df["brand"].value_counts().idxmax()    if len(df) > 0 else "—"

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💰 Total Revenue",    f"₹{st.session_state.total_revenue:,.0f}", f"+₹{rev_delta:,.0f}")
m2.metric("📦 Total Orders",     f"{st.session_state.order_count:,}",        f"+{new_count} now")
m3.metric("🧾 Avg Order Value",  f"₹{avg_order:,.0f}",                       "per order")
m4.metric("🏆 Top Category",     top_cat,                                    "by volume")
m5.metric("⭐ Top Brand",         top_brand,                                  "by revenue")

# ─────────────────────────────────────────────
#  LIVE TICKER
# ─────────────────────────────────────────────
if len(df) > 0:
    ticker_items = " &nbsp;|&nbsp; ".join([
        f"<span>{r['brand']} {r['product']}</span> ₹{r['total']:,.0f} · {r['city']}"
        for r in st.session_state.sales_log[:12]
    ])
    st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker-inner">⚡ LIVE &nbsp;&nbsp; {ticker_items}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN LAYOUT: Feed | Charts | Weather
# ─────────────────────────────────────────────
left_col, mid_col, right_col = st.columns([2.4, 2.2, 2.0], gap="medium")

# ── LEFT: Live Feed ──────────────────────────
with left_col:
    st.markdown('<div class="section-header">Live Order Feed</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feed-row feed-header">
        <span>TIME</span><span>PRODUCT</span><span>PRICE</span><span>BRAND</span><span>CITY</span>
    </div>
    """, unsafe_allow_html=True)

    feed_html = ""
    for i, row in enumerate(st.session_state.sales_log[:18]):
        is_new = "new" if i < new_count else ""
        feed_html += f"""
        <div class="feed-row {is_new}">
            <span style="color:var(--dim)">{row['time']}</span>
            <span style="color:var(--text);font-size:0.64rem">{row['product'][:22]}</span>
            <span class="price-val">₹{row['total']:,.0f}</span>
            <span class="brand-val">{row['brand']}</span>
            <span class="city-val">{row['city']}</span>
        </div>"""
    st.markdown(feed_html, unsafe_allow_html=True)

# ── MIDDLE: Charts ───────────────────────────
with mid_col:
    # Revenue by Category
    st.markdown('<div class="section-header">Revenue by Category</div>', unsafe_allow_html=True)
    cat_rev = df.groupby("category")["total"].sum().sort_values(ascending=False) if len(df) > 0 else pd.Series()
    if len(cat_rev) > 0:
        max_v = cat_rev.max()
        colors = ["#00ffe7", "#a259ff", "#ff6b35", "#ffe600", "#39ff14", "#ff3366"]
        bars_html = ""
        for i, (cat, val) in enumerate(cat_rev.items()):
            pct = int((val / max_v) * 100)
            col = colors[i % len(colors)]
            bars_html += f"""
            <div class="bar-row">
                <span class="bar-label" title="{cat}">{cat}</span>
                <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{col}"></div></div>
                <span class="bar-value">₹{val:,.0f}</span>
            </div>"""
        st.markdown(f'<div class="card"><div class="card-title">Category Performance</div>{bars_html}</div>', unsafe_allow_html=True)

    # Top Brands
    st.markdown('<div class="section-header">Top Brands</div>', unsafe_allow_html=True)
    brand_rev = df.groupby("brand")["total"].sum().sort_values(ascending=False).head(8) if len(df) > 0 else pd.Series()
    if len(brand_rev) > 0:
        max_b = brand_rev.max()
        bars2 = ""
        for i, (b, v) in enumerate(brand_rev.items()):
            pct = int((v / max_b) * 100)
            col = colors[i % len(colors)]
            bars2 += f"""
            <div class="bar-row">
                <span class="bar-label" title="{b}">{b}</span>
                <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{col}"></div></div>
                <span class="bar-value">₹{v:,.0f}</span>
            </div>"""
        st.markdown(f'<div class="card"><div class="card-title">Brand Revenue</div>{bars2}</div>', unsafe_allow_html=True)

# ── RIGHT: Weather + City Revenue ────────────
with right_col:
    st.markdown('<div class="section-header">City Weather Alerts</div>', unsafe_allow_html=True)

    top_cities = df["city"].value_counts().head(8).index.tolist() if len(df) > 0 else CITIES[:6]
    weather_data = fetch_weather_batch(tuple(top_cities))

    if weather_data:
        badges = ""
        for city in top_cities:
            if city not in weather_data:
                continue
            w = weather_data[city]
            alert = ""
            if w["rain"]:
                alert = '<span class="badge-alert">⚠ RAIN IMPACT</span>'
            elif w["heat"]:
                alert = '<span class="badge-alert">🔥 HEAT IMPACT</span>'
            badges += f"""
            <div class="weather-badge">
                <span>{w['icon']}</span>
                <div>
                    <div class="badge-city">{city}</div>
                    <div class="badge-temp">{w['temp']}°C</div>
                    <div class="badge-cond">{w['desc']}</div>
                    {alert}
                </div>
            </div>"""
        st.markdown(f'<div class="card"><div class="card-title">Live Conditions</div><div class="weather-grid">{badges}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><div class="card-title">Weather</div><span style="color:var(--dim);font-size:0.7rem;font-family:\'Space Mono\',monospace">Fetching data…</span></div>', unsafe_allow_html=True)

    # City Revenue
    st.markdown('<div class="section-header">Top Cities by Revenue</div>', unsafe_allow_html=True)
    city_rev = df.groupby("city")["total"].sum().sort_values(ascending=False).head(8) if len(df) > 0 else pd.Series()
    if len(city_rev) > 0:
        max_c = city_rev.max()
        city_bars = ""
        for i, (city, val) in enumerate(city_rev.items()):
            pct = int((val / max_c) * 100)
            flag = ""
            if city in weather_data:
                if weather_data[city]["rain"]:   flag = " 🌧"
                elif weather_data[city]["heat"]:  flag = " 🔥"
            city_bars += f"""
            <div class="bar-row">
                <span class="bar-label">{city}{flag}</span>
                <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:#00ffe7"></div></div>
                <span class="bar-value">₹{val:,.0f}</span>
            </div>"""
        st.markdown(f'<div class="card"><div class="card-title">City Revenue (weather-tagged)</div>{city_bars}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BOTTOM ROW: Category × Brand heatmap (pure CSS — no matplotlib)
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Category Breakdown by Brand</div>', unsafe_allow_html=True)
if len(df) > 0:
    pivot = df.pivot_table(
        index="category", columns="brand", values="total",
        aggfunc="sum", fill_value=0
    )
    top_brands = df.groupby("brand")["total"].sum().nlargest(10).index
    pivot = pivot[[c for c in top_brands if c in pivot.columns]]
    st.markdown(render_heatmap(pivot), unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  AUTO REFRESH
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:1.5rem; font-family:'Space Mono',monospace;
            font-size:0.6rem; color:#1a2e45; letter-spacing:0.15em;">
    AUTO-REFRESH EVERY 5 SECONDS · POWERED BY OPEN-METEO
</div>
""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
