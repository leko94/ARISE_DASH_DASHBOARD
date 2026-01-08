import pandas as pd
from dash import Dash, html, dcc
import plotly.graph_objects as go

# -------------------------------------------------
# LOAD EXCEL DATA
# -------------------------------------------------
df = pd.read_excel("Stokvel.xlsx")

# Members: A2:A12
members = df.iloc[0:12, 0]

# Totals per member: M2:M12
totals = df.iloc[0:12, 12]

# Total accumulated money
total_money = totals.sum()

# -------------------------------------------------
# GAUGE FIGURE
# -------------------------------------------------
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_money,
    number={"prefix": "ZAR "},
    title={"text": "Total Amount Accumulated"},
    gauge={
        "axis": {"range": [0, total_money * 1.2]},
        "bar": {"color": "#2E7D32"},
        "steps": [
            {"range": [0, total_money * 0.5], "color": "#E8F5E9"},
            {"range": [total_money * 0.5, total_money], "color": "#A5D6A7"}
        ]
    }
))

# -------------------------------------------------
# BAR CHART
# -------------------------------------------------
bar_fig = go.Figure(
    data=[
        go.Bar(
            x=members,
            y=totals,
            text=[f"ZAR {v:,.2f}" for v in totals],
            textposition="auto",
            marker_color="#1565C0"
        )
    ]
)

bar_fig.update_layout(
    title="Member Contributions (January – November)",
    xaxis_title="Stokvel Members",
    yaxis_title="Total Contribution (ZAR)",
    yaxis_tickprefix="ZAR ",
    height=500
)

# -------------------------------------------------
# DASH APP SETUP
# -------------------------------------------------
app = Dash(__name__)
server = app.server  # REQUIRED FOR GUNICORN

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
app.layout = html.Div([

    # HEADER STRIP
    html.Div([
        html.Img(
            src="/assets/logoekhishishini.jpeg",
            style={
                "height": "60px",
                "margin-right": "20px"
            }
        ),
        html.H1(
            "Ekhishini Dashboard Report",
            style={"margin": "0"}
        )
    ], style={
        "display": "flex",
        "align-items": "center",
        "padding": "12px",
        "border-bottom": "2px solid #e0e0e0",
        "background-color": "#fafafa"
    }),

    # CONTENT AREA
    html.Div([

        html.Div([
            dcc.Graph(figure=gauge_fig)
        ], style={
            "width": "35%",
            "display": "inline-block",
            "vertical-align": "top"
        }),

        html.Div([
            dcc.Graph(figure=bar_fig)
        ], style={
            "width": "65%",
            "display": "inline-block"
        })

    ], style={"padding": "20px"})
])

# -------------------------------------------------
# LOCAL RUN (OPTIONAL)
# -------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=False)

