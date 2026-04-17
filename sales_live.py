import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
import requests

# -----------------------------
# CONFIG
# -----------------------------
REFRESH_RATE = 5  # seconds
SALE_INTERVAL = 30  # seconds

PRODUCTS = {
    "Electronics": [
        {"name": "Smartphone", "brand": "Samsung", "price": 25000},
        {"name": "Laptop", "brand": "Dell", "price": 60000},
        {"name": "Headphones", "brand": "Sony", "price": 3000},
    ],
    "Fashion": [
        {"name": "T-Shirt", "brand": "Nike", "price": 1200},
        {"name": "Jeans", "brand": "Levi's", "price": 2500},
        {"name": "Shoes", "brand": "Adidas", "price": 4000},
    ],
    "Home": [
        {"name": "Mixer", "brand": "Philips", "price": 3500},
        {"name": "Chair", "brand": "Ikea", "price": 1500},
        {"name": "Lamp", "brand": "Syska", "price": 800},
    ],
}

CITIES = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]

# Optional: Put your OpenWeather API key here
API_KEY = ""


# -----------------------------
# WEATHER FUNCTION
# -----------------------------
def get_weather(city):
    try:
        if API_KEY == "":
            return random.choice(["☀️ Heat", "🌧 Rain", "🌤 Normal"])
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        res = requests.get(url).json()
        condition = res["weather"][0]["main"]

        if condition in ["Rain", "Drizzle", "Thunderstorm"]:
            return "🌧 Rain"
        elif condition in ["Clear"]:
            return "☀️ Heat"
        else:
            return "🌤 Normal"
    except:
        return "🌤 Normal"


# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "sales_data" not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(
        columns=["Time", "Category", "Product", "Brand", "City", "Price", "Weather"]
    )

if "last_sale_time" not in st.session_state:
    st.session_state.last_sale_time = time.time()


# -----------------------------
# GENERATE FAKE SALE
# -----------------------------
def generate_sale():
    category = random.choice(list(PRODUCTS.keys()))
    product_info = random.choice(PRODUCTS[category])
    city = random.choice(CITIES)

    sale = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Category": category,
        "Product": product_info["name"],
        "Brand": product_info["brand"],
        "City": city,
        "Price": product_info["price"],
        "Weather": get_weather(city),
    }

    return sale


# -----------------------------
# AUTO SALE GENERATION
# -----------------------------
current_time = time.time()
if current_time - st.session_state.last_sale_time >= SALE_INTERVAL:
    new_sale = generate_sale()
    st.session_state.sales_data = pd.concat(
        [st.session_state.sales_data, pd.DataFrame([new_sale])],
        ignore_index=True
    )
    st.session_state.last_sale_time = current_time


# -----------------------------
# DASHBOARD UI
# -----------------------------
st.set_page_config(page_title="Live Revenue Pulse", layout="wide")

st.title("📊 Live Revenue Pulse Dashboard")

data = st.session_state.sales_data

# Metrics
total_revenue = data["Price"].sum()
order_count = len(data)

col1, col2 = st.columns(2)

col1.metric("💰 Total Revenue", f"₹{total_revenue:,}")
col2.metric("📦 Total Orders", order_count)

st.divider()

# Filters
st.sidebar.header("Filters")

selected_category = st.sidebar.selectbox(
    "Select Category", ["All"] + list(PRODUCTS.keys())
)

selected_city = st.sidebar.selectbox(
    "Select City", ["All"] + CITIES
)

filtered_data = data.copy()

if selected_category != "All":
    filtered_data = filtered_data[filtered_data["Category"] == selected_category]

if selected_city != "All":
    filtered_data = filtered_data[filtered_data["City"] == selected_city]

# Display table
st.subheader("🛒 Live Sales Feed")
st.dataframe(filtered_data, use_container_width=True)

# Charts
st.subheader("📈 Sales by Category")
if not data.empty:
    category_chart = data.groupby("Category")["Price"].sum()
    st.bar_chart(category_chart)

st.subheader("🏙 Sales by City")
if not data.empty:
    city_chart = data.groupby("City")["Price"].sum()
    st.bar_chart(city_chart)

# -----------------------------
# AUTO REFRESH
# -----------------------------
time.sleep(REFRESH_RATE)
st.rerun()