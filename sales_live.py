import streamlit as st
import pandas as pd
import random
import plotly.express as px
from datetime import datetime
import sqlite3
from passlib.hash import pbkdf2_sha256
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Enterprise Command Center PRO",
    layout="wide",
    page_icon="🚀"
)

# -----------------------------
# DB
# -----------------------------
conn = sqlite3.connect("command_center.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT,
        role TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS sales(
        time TEXT,
        product TEXT,
        price INTEGER,
        city TEXT,
        weather TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS hospital(
        time TEXT,
        patientid INTEGER,
        triage INTEGER,
        wait INTEGER,
        department TEXT
    )""")

    conn.commit()

init_db()

# -----------------------------
# DEFAULT USERS
# -----------------------------
def create_users():
    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ("admin", "admin123", "Admin"),
            ("manager", "manager123", "Manager"),
            ("doctor", "doctor123", "Doctor")
        ]
        for u, p, r in users:
            cursor.execute(
                "INSERT INTO users VALUES (?,?,?)",
                (u, pbkdf2_sha256.hash(p), r)
            )
        conn.commit()

create_users()

# -----------------------------
# LOGIN
# -----------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Enterprise Command Center PRO")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and pbkdf2_sha256.verify(password, user[1]):
            st.session_state.login = True
            st.session_state.user = username
            st.session_state.role = user[2]
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🚀 Control Panel")

st.sidebar.success(f"{st.session_state.user}")
st.sidebar.info(f"Role: {st.session_state.role}")

dashboard = st.sidebar.selectbox(
    "Dashboard",
    ["Revenue", "Hospital"]
)

refresh = st.sidebar.slider("Refresh (sec)", 5, 60, 10)

st_autorefresh(interval=refresh * 1000, key="auto")

# -----------------------------
# SAFE DB READ
# -----------------------------
def load_data(table):
    return pd.read_sql(f"SELECT * FROM {table}", conn)

# -----------------------------
# DATA
# -----------------------------
products = ["Laptop","Mobile","Tablet","Camera","Headphones","Watch"]
cities = ["Chennai","Mumbai","Delhi","Bangalore","Hyderabad"]
departments = ["Emergency","Cardiology","Orthopedic","Neurology","General"]

def weather():
    return random.choice(["Clear","Rain","Clouds","Heat"])

def sale():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000,50000),
        random.choice(cities),
        weather()
    )

def patient():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.randint(1000,9999),
        random.randint(1,5),
        random.randint(5,120),
        random.choice(departments)
    )

# -----------------------------
# REVENUE
# -----------------------------
if dashboard == "Revenue":

    st.title("📊 Revenue Dashboard PRO")

    cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?)", sale())
    conn.commit()

    df = load_data("sales")

    if not df.empty:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Revenue", f"₹{df['price'].sum():,}")
        col2.metric("Orders", len(df))
        col3.metric("Avg", f"₹{int(df['price'].mean())}")
        col4.metric("Cities", df['city'].nunique())

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            st.plotly_chart(px.bar(df, x="city", y="price", color="city"), use_container_width=True)

        with c2:
            st.plotly_chart(px.pie(df, names="product"), use_container_width=True)

        st.subheader("Live Data")
        st.dataframe(df.tail(10), use_container_width=True)

    else:
        st.warning("No sales data yet")

# -----------------------------
# HOSPITAL
# -----------------------------
if dashboard == "Hospital":

    st.title("🏥 Hospital Command Center PRO")

    cursor.execute("INSERT INTO hospital VALUES (?,?,?,?,?)", patient())
    conn.commit()

    df = load_data("hospital")

    if not df.empty:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("ER Load", len(df))
        col2.metric("Avg Wait", int(df["wait"].mean()))
        col3.metric("Critical", len(df[df["triage"] == 1]))
        col4.metric("Dept", df["department"].nunique())

        if len(df[df["triage"] == 1]) > 3:
            st.error("🚨 CRITICAL SURGE")

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            st.plotly_chart(px.bar(df, x="department", y="wait"), use_container_width=True)

        with c2:
            st.plotly_chart(px.histogram(df, x="triage"), use_container_width=True)

        st.subheader("Live Patients")
        st.dataframe(df.tail(10), use_container_width=True)

# -----------------------------
# EXPORT
# -----------------------------
st.sidebar.divider()

if st.sidebar.button("Export Sales"):
    load_data("sales").to_csv("sales.csv", index=False)
    st.sidebar.success("Exported")

if st.sidebar.button("Export Hospital"):
    load_data("hospital").to_csv("hospital.csv", index=False)
    st.sidebar.success("Exported")

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
