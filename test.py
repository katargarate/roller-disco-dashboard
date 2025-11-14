import streamlit as st
import psycopg2
from urllib.parse import urlparse

# --- Step 1: Your connection string ---
conn_str = "postgresql://postgres:Argarate5988@db.bfkzcighzjorhsshlwuc.supabase.co:5432/postgres"

# --- Step 2: Parse the connection string ---
url = urlparse(conn_str)
conn = psycopg2.connect(
    dbname=url.path[1:],   # remove leading '/'
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode='require'      # Supabase requires SSL
)

# --- Step 3: Create a cursor ---
cursor = conn.cursor()

# --- Step 4: Test query ---
cursor.execute("SELECT NOW();")
current_time = cursor.fetchone()[0]

st.title("Supabase Connection Test")
st.write(f"Database current time: {current_time}")

# --- Optional: query your table ---
cursor.execute("SELECT * FROM your_table;")
rows = cursor.fetchall()
st.write(rows)

# --- Step 5: Close connection (optional) ---
cursor.close()
conn.close()
