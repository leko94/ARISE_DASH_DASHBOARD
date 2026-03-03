import os
import pandas as pd
from dash import Dash, html, dcc
import plotly.graph_objects as go


# -----------------------------
# CONFIG
# -----------------------------
EXCEL_FILE = os.getenv("EXCEL_FILE", "Stokvel03032026.xlsx")

# If your sheet isn't the first one, set SHEET_NAME, e.g. "Sheet1"
SHEET_NAME = os.getenv("Sheet1", None)

# Data ranges (0-indexed)
MEMBERS_ROWS = slice(0, 12)   # A2:A13 style equivalent in your original logic
MEMBERS_COL = 0              # Column A
TOTALS_COL = 12              # Column M


# -----------------------------
# LOAD DATA (SAFE)
# -----------------------------
def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Excel file not found: '{path}'. "
            f"Make sure it is included in your deployment and spelled correctly."
        )

    df_ = pd.read_excel(path, sheet_name=SHEET_NAME, engine="openpyxl")
    return df_


df = load_data(EXCEL_FILE)

members = df.iloc[MEMBERS_ROWS, MEMBERS_COL].astype(str).fillna("Unknown")
totals = pd.to_numeric(df.iloc[MEMBERS_ROWS, TOTALS_COL], errors="coerce").fillna(0)

total_money = float(totals.sum())
avg_contribution = float(totals.mean()) if len(totals) else 0.0
top_idx = int(totals.idxmax()) if len(totals) else 0
top_member = str(df.iloc[top_idx, MEMBERS_COL]) if len(totals) else "-"
top_amount = float(totals.max()) if len(totals) else 0.0


# -----------------------------
# PLOTLY GLOBAL LOOK
# -----------------------------
PLOTLY_TEMPLATE = "plotly_white"


def money(v: float) -> str:
    return f"ZAR {v:,.2f}"


# -----------------------------
# GAUGE FIGURE
# -----------------------------
gauge_max = max(total_money * 1.25, 1)  # avoid zero-range
gauge_fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=total_money,
        number={"prefix": "ZAR ", "valueformat": ",.2f"},
        title={"text": "Total Amount Accumulated"},
        gauge={
            "axis": {"range": [0, gauge_max]},
            "bar": {"color": "#1B5E20"},
            "steps": [
                {"range": [0, gauge_max * 0.5], "color": "#E8F5E9"},
                {"range": [gauge_max * 0.5, gauge_max * 0.85], "color": "#C8E6C9"},
                {"range": [gauge_max * 0.85, gauge_max], "color": "#A5D6A7"},
            ],
        },
    )
)
gauge_fig.update_layout(
    template=PLOTLY_TEMPLATE,
    margin=dict(l=20, r=20, t=60, b=20),
    height=320,
)


# -----------------------------
# BAR CHART
# -----------------------------
bar_fig = go.Figure(
    data=[
        go.Bar(
            x=members,
            y=totals,
            text=[money(v) for v in totals],
            textposition="outside",
        )
    ]
)
bar_fig.update_layout(
    template=PLOTLY_TEMPLATE,
    title="Member Contributions (January – November)",
    xaxis_title="Stokvel Members",
    yaxis_title="Total Contribution (ZAR)",
    yaxis_tickprefix="ZAR ",
    margin=dict(l=20, r=20, t=60, b=60),
    height=520,
)
bar_fig.update_yaxes(rangemode="tozero")


# -----------------------------
# DASH APP
# -----------------------------
app = Dash(__name__)
server = app.server  # REQUIRED FOR GUNICORN

# -----------------------------
# STYLES
# -----------------------------
PAGE_STYLE = {
    "minHeight": "100vh",
    "background": "linear-gradient(135deg, #f7f9fc 0%, #eef2f7 100%)",
    "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
}

HEADER_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "gap": "16px",
    "padding": "16px 20px",
    "backgroundColor": "rgba(255,255,255,0.9)",
    "backdropFilter": "blur(6px)",
    "borderBottom": "1px solid #e6e9ef",
    "position": "sticky",
    "top": "0",
    "zIndex": "10",
}

BRAND_STYLE = {"display": "flex", "alignItems": "center", "gap": "14px"}

TITLE_STYLE = {"margin": "0", "fontSize": "22px", "fontWeight": "800", "color": "#111827"}
SUBTITLE_STYLE = {"margin": "2px 0 0 0", "fontSize": "13px", "color": "#6B7280"}

CONTAINER_STYLE = {"maxWidth": "1200px", "margin": "0 auto", "padding": "18px 18px 28px"}

GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(12, 1fr)",
    "gap": "14px",
}

CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e6e9ef",
    "borderRadius": "16px",
    "boxShadow": "0 10px 20px rgba(17,24,39,0.06)",
    "padding": "14px 14px",
}

KPI_TITLE = {"margin": "0", "fontSize": "12px", "color": "#6B7280", "fontWeight": "700"}
KPI_VALUE = {"margin": "6px 0 0 0", "fontSize": "20px", "color": "#111827", "fontWeight": "900"}


def kpi_card(title: str, value: str):
    return html.Div(
        [
            html.P(title, style=KPI_TITLE),
            html.P(value, style=KPI_VALUE),
        ],
        style=CARD_STYLE,
    )


# -----------------------------
# LAYOUT
# -----------------------------
app.layout = html.Div(
    style=PAGE_STYLE,
    children=[
        # Header
        html.Div(
            style=HEADER_STYLE,
            children=[
                html.Div(
                    style=BRAND_STYLE,
                    children=[
                        html.Img(
                            src="/assets/logoekhishishini.jpeg",
                            style={"height": "52px", "width": "52px", "borderRadius": "12px", "objectFit": "cover"},
                        ),
                        html.Div(
                            children=[
                                html.H1("Ekhishini Dashboard Report", style=TITLE_STYLE),
                                html.P("Stokvel contribution overview", style=SUBTITLE_STYLE),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    style={"textAlign": "right"},
                    children=[
                        html.P("File:", style={"margin": "0", "fontSize": "12px", "color": "#6B7280", "fontWeight": "700"}),
                        html.P(EXCEL_FILE, style={"margin": "4px 0 0 0", "fontSize": "12px", "color": "#111827"}),
                    ],
                ),
            ],
        ),

        # Body
        html.Div(
            style=CONTAINER_STYLE,
            children=[
                # KPIs
                html.Div(
                    style=GRID_STYLE,
                    children=[
                        html.Div(kpi_card("Total Accumulated", money(total_money)), style={"gridColumn": "span 4"}),
                        html.Div(kpi_card("Average per Member", money(avg_contribution)), style={"gridColumn": "span 4"}),
                        html.Div(kpi_card("Top Contributor", f"{top_member} ({money(top_amount)})"), style={"gridColumn": "span 4"}),
                    ],
                ),

                html.Div(style={"height": "14px"}),

                # Charts grid
                html.Div(
                    style=GRID_STYLE,
                    children=[
                        html.Div(
                            style={**CARD_STYLE, "gridColumn": "span 5"},
                            children=[dcc.Graph(figure=gauge_fig, config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={**CARD_STYLE, "gridColumn": "span 7"},
                            children=[dcc.Graph(figure=bar_fig, config={"displayModeBar": False})],
                        ),
                    ],
                ),

                html.Div(style={"height": "14px"}),

                # Table
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Member Totals", style={"margin": "4px 0 12px 0", "fontSize": "16px", "fontWeight": "900"}),
                        html.Div(
                            style={"overflowX": "auto"},
                            children=[
                                html.Table(
                                    style={"width": "100%", "borderCollapse": "collapse"},
                                    children=[
                                        html.Thead(
                                            html.Tr(
                                                [
                                                    html.Th("Member", style={"textAlign": "left", "padding": "10px", "borderBottom": "1px solid #e6e9ef"}),
                                                    html.Th("Total (ZAR)", style={"textAlign": "right", "padding": "10px", "borderBottom": "1px solid #e6e9ef"}),
                                                ]
                                            )
                                        ),
                                        html.Tbody(
                                            [
                                                html.Tr(
                                                    [
                                                        html.Td(m, style={"padding": "10px", "borderBottom": "1px solid #f1f4f8"}),
                                                        html.Td(money(v), style={"padding": "10px", "textAlign": "right", "borderBottom": "1px solid #f1f4f8"}),
                                                    ]
                                                )
                                                for m, v in zip(members, totals)
                                            ]
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# -----------------------------
# LOCAL RUN
# -----------------------------
if __name__ == "__main__":
    app.run_server(debug=False)
