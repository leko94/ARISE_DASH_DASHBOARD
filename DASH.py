
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Ekhishini Stokvel Dashboard",
    layout="wide"
)

# -----------------------------
# HEADER WITH LOGO (TOP STRIP)
# -----------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logoekhishishini.jpeg", width=120)

with col2:
    st.markdown(
        """
        <h1 style="margin-bottom:0;">Ekhishini Stokvel</h1>
        <p style="color:gray;">Financial Contributions Dashboard</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# -----------------------------
# LOAD EXCEL DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_excel("Stokvel.xlsx")

df = load_data()

# -----------------------------
# DATA PROCESSING
# -----------------------------
# Members: A2:A12
members = df.iloc[1:12, 0]

# Monthly contributions: B1:L1 (Jan–Nov)
monthly_columns = df.columns[1:12]

# Total per member: Column M
totals = df.iloc[1:12, 12]

# Total accumulated money (sum of M2:M12)
total_money = totals.sum()

# -----------------------------
# GAUGE: TOTAL MONEY IN
# -----------------------------
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_money,
    number={'prefix': "ZAR "},
    title={'text': "Total Amount Accumulated"},
    gauge={
        'axis': {'range': [0, total_money * 1.2]},
        'bar': {'color': "#2E8B57"},
        'steps': [
            {'range': [0, total_money * 0.5], 'color': "#E8F5E9"},
            {'range': [total_money * 0.5, total_money], 'color': "#A5D6A7"}
        ],
    }
))

# -----------------------------
# BAR CHART: MEMBER CONTRIBUTIONS
# -----------------------------
bar_fig = go.Figure()

bar_fig.add_trace(go.Bar(
    x=members,
    y=totals,
    text=[f"ZAR {v:,.2f}" for v in totals],
    textposition='auto',
    marker_color="#1E88E5"
))

bar_fig.update_layout(
    title="Member Contributions (January – November)",
    xaxis_title="Stokvel Members",
    yaxis_title="Total Contribution (ZAR)",
    yaxis_tickprefix="ZAR ",
    height=500
)

# -----------------------------
# DASHBOARD LAYOUT
# -----------------------------
left_col, right_col = st.columns([1, 2])

with left_col:
    st.plotly_chart(gauge_fig, use_container_width=True)

with right_col:
    st.plotly_chart(bar_fig, use_container_width=True)

