import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.express as px

# --------------------------
# Supabase client setup
# --------------------------
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["anon_key"]  # read-only anon key
supabase = create_client(url, key)

# --------------------------
# Load data from your views
# --------------------------
@st.cache_data
def load_data():
    # vw_sales_progression
    data_progress = supabase.table("vw_sales_progression").select("*").execute()
    df_progress = pd.DataFrame(data_progress.data)

    # vw_final_attendance
    data_summary = supabase.table("vw_final_attendance").select("*").execute()
    df_summary = pd.DataFrame(data_summary.data)

    return df_progress, df_summary

df_progress, df_summary = load_data()

# --------------------------
# Colors and Page Config
# --------------------------
PRIMARY_COLOR = "#9c83fd"     # Lilac
ACCENT_COLOR = "#EC4899"      # Hot pink
BACKGROUND_COLOR = "#110f49"  # Dark background for high contrast
SIDEBAR_COLOR = "#1c1d2c"     # Dark grey sidebar
TEXT_COLOR = "#F9FAFB"        # Light text
HIGHLIGHT_COLOR = "#F59E0B"   # Bright yellow-orange

st.set_page_config(
    page_title="Roller Disco Dashboard",
    layout="wide",
    page_icon="🪩"
)

# --------------------------
# Styling
# --------------------------
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        }}
        .stSidebar {{
            background-color: {SIDEBAR_COLOR};
            color: {TEXT_COLOR};
        }}
        h1, h2, h3, h4 {{
            color: {PRIMARY_COLOR} !important;
        }}
        .stDataFrame div {{
            color: {TEXT_COLOR} !important;
            font-weight: 600;
        }}
        .css-1lcbmhc p, .css-1v0mbdj {{
            color: {TEXT_COLOR} !important;
            font-weight: 600;
        }}
        a {{
            color: {ACCENT_COLOR};
            font-weight: 600;
        }}
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Helper: mobile-friendly figure
# --------------------------
def mobile_friendly_fig(fig, wide_mode=True):
    # layout updates (same as before)
    fig.update_layout(
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        font_color=TEXT_COLOR,
        title_font_size=22,
        title_y=0.95,
        legend_font_size=14,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        xaxis_tickangle=-45,
        xaxis_tickfont_size=12,
        yaxis_tickfont_size=12,
        margin=dict(l=40, r=40, t=140, b=60),
        hovermode="x unified",
        width=1200 if wide_mode else None,
        autosize=True,  # allow Plotly to pick correct Y-axis
        height=None,  # remove fixed height
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        )
    )

    # only update line & marker for scatter traces
    for trace in fig.data:
        if trace.type == "scatter":
            trace.update(line=dict(width=3), marker=dict(size=8))
        elif trace.type == "bar":
            trace.update(marker=dict(line=dict(width=0)))  # optional: remove bar outlines

    return fig



# --------------------------
# Layout
# --------------------------
st.title("🪩 Roller Disco Ticket Dashboard")

# --------------------------
# Sidebar
# --------------------------
years = sorted(df_progress["year"].unique().tolist())
years.insert(0, "Overall")
year_selected = st.sidebar.selectbox("Select Year", years)

chart_mode = st.sidebar.radio("Comparison Mode", ["Absolute Tickets", "Percentage of Capacity"], index=0)
x_axis_mode = st.sidebar.radio("X-axis", ["Days Before Event", "Days Since On Sale"], index=0)
x_column = "days_before_event" if x_axis_mode == "Days Before Event" else "days_since_on_sale"

# --------------------------
# Data filtering
# --------------------------
if year_selected != "Overall":
    filtered = df_progress[df_progress["year"] == year_selected].copy()
    summary = df_summary[df_summary["year"] == year_selected].copy()
else:
    filtered = df_progress.copy()
    summary = df_summary.copy()

# --------------------------
# Single Year Chart
# --------------------------
if year_selected != "Overall":
    st.subheader(f"📈 Sales Progression — {year_selected}")
    df_plot = filtered.copy()

    if chart_mode == "Percentage of Capacity":
        df_caps = summary.copy()
        df_caps["od_capacity"] = df_caps["od_sold"] + df_caps["od_guestlist"]
        df_caps["lnd_capacity"] = df_caps["lnd_sold"] + df_caps["lnd_guestlist"]
        df_plot = df_plot.merge(df_caps[["year", "od_capacity", "lnd_capacity"]], on="year", how="left")

        def calc_percentage(row):
            return row["sold"] / row["od_capacity"] * 100 if row["slot"].lower() == "open disco" else row["sold"] / row["lnd_capacity"] * 100

        df_plot["sold_percentage"] = df_plot.apply(calc_percentage, axis=1)
        y_column = "sold_percentage"
        y_label = "% of Capacity"
    else:
        y_column = "sold"
        y_label = "Tickets Sold"

    fig = px.line(
        df_plot,
        x=x_column,
        y=y_column,
        color="slot",
        markers=True,
        title=f"{year_selected} Ticket Sales by Slot",
        labels={x_column: x_axis_mode, y_column: y_label, "slot": "Slot"},
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR]
    )
    if x_column == "days_before_event":
        fig.update_xaxes(autorange="reversed")
    fig = mobile_friendly_fig(fig, wide_mode=False)
    st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Multi-Year Comparison
# --------------------------
if year_selected == "Overall":
    st.subheader("📊 Multi-Year Comparison")
    for slot in ["Open Disco", "Late Night Disco"]:
        df_slot = df_progress[df_progress["slot"] == slot].copy()
        df_caps = df_summary.copy()
        if chart_mode == "Percentage of Capacity":
            df_caps["capacity"] = df_caps["od_sold"] + df_caps["od_guestlist"] if slot.lower() == "open disco" else df_caps["lnd_sold"] + df_caps["lnd_guestlist"]
            df_slot = df_slot.merge(df_caps[["year", "capacity"]], on="year", how="left")
            df_slot["sold_percentage"] = df_slot["sold"] / df_slot["capacity"] * 100
            y_column = "sold_percentage"
            y_label = "% of Capacity"
        else:
            y_column = "sold"
            y_label = "Tickets Sold"

        fig_multi = px.line(
            df_slot,
            x=x_column,
            y=y_column,
            color="year",
            markers=True,
            title=f"{slot} Ticket Sales Across Years",
            labels={x_column: x_axis_mode, y_column: y_label, "year": "Year"},
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        if x_column == "days_before_event":
            fig_multi.update_xaxes(autorange="reversed")
        fig_multi = mobile_friendly_fig(fig_multi, wide_mode=False)
        if chart_mode == "Absolute Tickets":
            fig_multi.update_yaxes(rangemode="tozero")  # start at 0
        fig_multi.update_layout(autosize=True)  # let Plotly pick the correct max Y
        st.plotly_chart(fig_multi, use_container_width=True)

# --------------------------
# Key Takeaways
# --------------------------
if year_selected != "Overall":
    st.subheader(f"📊 Key Takeaways — {year_selected}")


    def get_col(df, col_name):
        if col_name in df.columns:
            val = df[col_name].iloc[0]
            return int(val) if pd.notna(val) else 0
        else:
            return 0


    # Open Disco
    od_sold = get_col(summary, "od_sold")
    od_scanned = get_col(summary, "od_scanned")
    od_guestlist = get_col(summary, "od_guestlist")
    od_abendkasse = get_col(summary, "od_ak")

    # Late Night Disco
    lnd_sold = get_col(summary, "lnd_sold")
    lnd_scanned = get_col(summary, "lnd_scanned")
    lnd_guestlist = get_col(summary, "lnd_guestlist")
    lnd_abendkasse = get_col(summary, "lnd_ak")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 🪩 Open Disco")
        st.markdown(f"**Sold:** {od_sold}")
        st.markdown(f"**Guestlist:** {od_guestlist}")
        st.markdown(f"**Abendkasse:** {od_abendkasse}")
        st.markdown(f"**Scanned:** {od_scanned}/{od_sold + od_guestlist}")

    with col2:
        st.markdown(f"### 🌙 Late Night Disco")
        st.markdown(f"**Sold:** {lnd_sold}")
        st.markdown(f"**Guestlist:** {lnd_guestlist}")
        st.markdown(f"**Abendkasse:** {lnd_abendkasse}")
        st.markdown(f"**Scanned:** {lnd_scanned}/{lnd_sold + lnd_guestlist}")

    # Spectators
    if "spectators" in filtered.columns:
        with st.expander("Show Spectator Numbers"):
            fig2 = px.bar(
                filtered,
                x="update_date",
                y="spectators",
                title="Spectator Ticket Sales Over Time",
                color_discrete_sequence=[HIGHLIGHT_COLOR]
            )
            fig2 = mobile_friendly_fig(fig2, wide_mode=False)
            st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Built with 💜 by Kat / Space Quads")
