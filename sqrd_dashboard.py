import psycopg2
from urllib.parse import urlparse

# Your connection string
conn_str = "postgresql://postgres:Argarate5988@db.bfkzcighzjorhsshlwuc.supabase.co:5432/postgres"

# Parse the URL
url = urlparse(conn_str)
conn = psycopg2.connect(
    dbname=url.path[1:],      # removes leading /
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode='require'         # required by Supabase
)

cursor = conn.cursor()
cursor.execute("SELECT NOW();")  # test connection
print(cursor.fetchone())
