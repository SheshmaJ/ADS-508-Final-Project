import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
import os

app = dash.Dash(__name__)

# Load data 
df = pd.read_csv("dashboard/sample_prediction.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

RISK_MAP = {
    "High Priority":   "High",
    "Medium Priority": "Medium",
    "Low Priority":    "Low",
    "High":            "High",
    "Medium":          "Medium",
    "Low":             "Low",
}
df["risk_level"]  = df["risk_level"].map(RISK_MAP).fillna(df["risk_level"])
df["is_high_risk"] = (df["risk_level"] == "High").astype(int)

print(f"Loaded {len(df):,} rows | Risk levels: {df['risk_level'].unique()}")

# Load California counties GeoJSON for map boundaries
GEOJSON_LOCAL = "dashboard/ca_counties.geojson"
GEOJSON_URL   = (
    "https://raw.githubusercontent.com/codeforamerica/"
    "click_that_hood/master/public/data/california-counties.geojson"
)

ca_counties = None
try:
    if os.path.exists(GEOJSON_LOCAL):
        with open(GEOJSON_LOCAL) as f:
            ca_counties = json.load(f)
        print("County GeoJSON loaded from local file")
    else:
        ca_counties = requests.get(GEOJSON_URL, timeout=10).json()
        os.makedirs("dashboard", exist_ok=True)
        with open(GEOJSON_LOCAL, "w") as f:
            json.dump(ca_counties, f)
        print("County GeoJSON downloaded and saved locally")
except Exception as e:
    print(f"Could not load county GeoJSON: {e}")

# Define features to show in the importance bars, along with their "importance" scores
FEATURES = {
    "Dryness of Vegetation": (
        "fuel_moisture_risk", 2880, "",
        "How dry the vegetation is. Drier = higher fire risk."
    ),
    "Amount of Combustible Vegetation": (
        "biomass_tons_ha", 2607, "t/ha",
        "How much plant material exists. More vegetation = more fuel."
    ),
    "Tree Height": (
        "ht", 1599, "ft",
        "Average height of trees. Taller trees spread fire faster."
    ),
    "Tree Thickness": (
        "dia", 1579, "in",
        "Average trunk diameter. Thicker trees carry more fuel."
    ),
    "Fire History": (
        "fire_recurrence", 795, "x",
        "How often fires have occurred here. Higher = more fire-prone area."
    ),
}
IMPORTANCE_MAX = max(v[1] for v in FEATURES.values())

STATEWIDE_AVG = {
    col: df[col].mean()
    for label, (col, *_) in FEATURES.items()
    if col in df.columns
}

# Define some common styles for reuse
CARD  = {"background": "white", "borderRadius": 8,
         "border": "0.5px solid #eee", "padding": "10px"}
LABEL = {"fontSize": 10, "color": "#888", "marginBottom": 4,
         "lineHeight": 1.3}
VALUE = {"fontSize": 17, "fontWeight": 600}
SEC   = {"fontSize": 12, "fontWeight": 600, "marginBottom": 4}
HINT  = {"fontSize": 10, "color": "#aaa", "marginBottom": 6,
         "fontStyle": "italic"}

# layout
app.layout = html.Div([

    # left sidebar with filters and distribution charts
    html.Div([

        html.Div("🌿 Filters", style={**SEC, "fontSize": 14}),
        html.Div("Use filters to explore a specific region or risk level.",
                 style=HINT),

        html.Label("County", style=LABEL),
        dcc.Dropdown(
            id="county-filter",
            options=[{"label": "All Counties", "value": "All"}] +
                    [{"label": c, "value": c}
                     for c in sorted(df["county_name"].dropna().unique())],
            value="All", clearable=False,
            style={"fontSize": 12, "marginBottom": 10}
        ),

        html.Label("City", style=LABEL),
        dcc.Dropdown(
            id="city-filter",
            options=[{"label": "All Cities", "value": "All"}] +
                    [{"label": c, "value": c}
                     for c in sorted(df["city"].dropna().unique())],
            value="All", clearable=False,
            style={"fontSize": 12, "marginBottom": 10}
        ),

        html.Label("Risk Level", style=LABEL),
        dcc.Dropdown(
            id="risk-filter",
            options=[
                {"label": "All Risk Levels",             "value": "All"},
                {"label": "🔴 High - Trim Immediately",  "value": "High"},
                {"label": "🟡 Medium - Monitor Closely", "value": "Medium"},
                {"label": "🟢 Low - No Action Needed",   "value": "Low"},
            ],
            value="All", clearable=False,
            style={"fontSize": 12, "marginBottom": 14}
        ),

        html.Hr(style={"margin": "6px 0"}),

        html.Div("How Many Locations Are at Each Risk Level", style=SEC),
        html.Div("Longer bar = more locations at that risk level.",
                 style=HINT),
        html.Div(id="risk-dist-bars"),

        html.Hr(style={"margin": "6px 0"}),

        html.Div("🔥 Which Months Have the Highest Fire Risk", style=SEC),
        html.Div("Use this to plan seasonal trimming schedules.", style=HINT),
        html.Div(id="month-heatmap"),

    ], style={
        "width": "230px", "minWidth": "230px", "padding": "14px",
        "borderRight": "1px solid #eee", "background": "white",
        "display": "flex", "flexDirection": "column",
        "overflowY": "auto", "boxSizing": "border-box"
    }),

    # Main content area with title, summary, KPIs, map, and details panels
    html.Div([

        # Title bar
        html.Div([
            html.Span(
                "🌿 VEGETATION GROWTH RISK AND TRIMMING PRIORITY DASHBOARD",
                style={"fontSize": 20, "fontWeight": 600}
            ),
            html.Div(
                "Each dot on the map is a vegetation location. "
                "Red = urgent trimming needed · "
                "Yellow = monitor closely · Green = low priority. "
                "Select a county to highlight its boundary.",
                style={"fontSize": 11, "color": "#888", "marginTop": 3}
            ),
        ], style={
            "padding": "12px 16px",
            "borderBottom": "1px solid #eee",
            "background": "white"
        }),

        # Summary banner
        html.Div(id="summary-banner", style={
            "background": "#fff8e1",
            "padding": "8px 16px",
            "borderBottom": "1px solid #f0d060",
            "fontSize": 12, "color": "#555"
        }),

        # KPI row
        html.Div(id="kpi-row", style={
            "display": "grid",
            "gridTemplateColumns": "repeat(8, 1fr)",
            "gap": "6px", "padding": "10px 14px",
            "background": "#f7f7f5",
            "borderBottom": "1px solid #eee"
        }),

        # Map + panels
        html.Div([

            # Map + zoom slider
            html.Div([
                dcc.Graph(
                    id="map-chart",
                    style={"flex": 1, "minHeight": 0, "height": "100%"},
                    config={"displayModeBar": False}
                ),
                html.Div([
                    html.Span("Zoom", style={
                        "fontSize": 11, "color": "#888", "marginRight": 8
                    }),
                    dcc.Slider(
                        id="map-zoom-slider",
                        min=4, max=12, step=0.5, value=5,
                        marks={4: "State", 7: "Region",
                               10: "City",  12: "Street"},
                        tooltip={"always_visible": False,
                                 "placement": "top"},
                    ),
                ], style={
                    "display": "flex", "alignItems": "center",
                    "padding": "6px 16px",
                    "background": "white",
                    "borderTop": "0.5px solid #eee"
                })
            ], style={
                "flex": 2, "display": "flex", "flexDirection": "column",
                "minHeight": 0, "overflow": "hidden",
            }),

            # Middle panel — driving factors
            html.Div([
                html.Div("⚠️ What's Driving the Risk in This Area?",
                         style=SEC),
                html.Div(
                    "Compared to the statewide average. "
                    "Red = worse than average · Green = better than average.",
                    style=HINT
                ),
                html.Div(id="importance-bars",
                         style={"overflowY": "auto", "flex": 1}),
            ], style={
                "width": "300px", "minWidth": "300px", "padding": "14px",
                "overflowY": "auto", "borderLeft": "1px solid #eee",
                "background": "white", "boxSizing": "border-box",
                "alignSelf": "stretch", "display": "flex",
                "flexDirection": "column",
            }),

            # Right panel — top counties table
            html.Div([
                html.Div("📍 Locations That Need Immediate Attention",
                         style=SEC),
                html.Div(
                    "These areas have the highest fire risk scores "
                    "and should be prioritized for trimming.",
                    style=HINT
                ),
                dash_table.DataTable(
                    id="top-counties-table",
                    style_cell={
                        "fontSize": 11, "padding": "6px",
                        "textAlign": "left", "whiteSpace": "normal"
                    },
                    style_header={
                        "fontWeight": 600, "color": "#888",
                        "backgroundColor": "#f7f7f5", "fontSize": 11
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"},
                         "backgroundColor": "#fafafa"},
                        {"if": {
                            "filter_query":
                                "{Risk Score (out of 100)} >= 99",
                            "column_id": "Risk Score (out of 100)"
                         },
                         "color": "#E24B4A", "fontWeight": 600},
                    ]
                ),
            ], style={
                "width": "260px", "minWidth": "260px", "padding": "14px",
                "overflowY": "auto", "borderLeft": "1px solid #eee",
                "background": "white", "boxSizing": "border-box",
                "alignSelf": "stretch",
            }),

        ], style={
            "display": "flex", "flex": 1,
            "overflow": "hidden", "alignItems": "stretch",
        }),

    ], style={
        "flex": 1, "display": "flex", "flexDirection": "column",
        "overflow": "hidden"
    }),

], style={
    "display": "flex", "height": "100vh",
    "fontFamily": "'Segoe UI', sans-serif",
    "overflow": "hidden", "background": "#f7f7f5"
})


# Helper function to filter the dataframe based on selected county, city, and risk level
def filter_df(county, city, risk):
    dff = df.copy()
    if county != "All":
        dff = dff[dff["county_name"] == county]
    if city != "All":
        dff = dff[dff["city"] == city]
    if risk != "All":
        dff = dff[dff["risk_level"] == risk]
    return dff


def add_county_boundaries(fig, selected_county):
    """
    Add county boundary lines only — no fill inside.
    Selected county gets a slightly thicker, darker line.
    All others get a thin, light gray line.
    """
    if not ca_counties:
        return fig

    for feature in ca_counties["features"]:
        county_name = feature["properties"].get("name", "")
        is_selected = (selected_county != "All" and
                       county_name.lower() == selected_county.lower())

        # Always use no fill to avoid obscuring map details
        fill_color = "rgba(0, 0, 0, 0)"          

        if is_selected:
            line_color = "rgba(55, 138, 221, 0.9)"  
            line_width = 2.5
        else:
            line_color = "rgba(173, 216, 230, 0.8)"  
            line_width = 0.6

        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            polygons = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polygons = geom["coordinates"]
        else:
            continue

        for polygon in polygons:
            for ring in polygon:
                lons = [pt[0] for pt in ring]
                lats = [pt[1] for pt in ring]
                fig.add_trace(go.Scattermap(
                    lon=lons,
                    lat=lats,
                    mode="lines",
                    fill="toself",
                    fillcolor=fill_color,      
                    line=dict(
                        color=line_color,
                        width=line_width
                    ),
                    hoverinfo="text",
                    hovertext=county_name,
                    showlegend=False,
                    name=county_name,
                ))
    return fig


# Summary banner
@app.callback(
    Output("summary-banner", "children"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_banner(county, city, risk):
    dff = filter_df(county, city, risk)
    if len(dff) == 0:
        return "No data for selected filters."
    high_count = int(dff["is_high_risk"].sum())
    high_pct   = dff["is_high_risk"].mean() * 100
    top_county = dff.groupby("county_name")["risk_score"].mean().idxmax()
    area = "selected area" if (county != "All" or city != "All") \
           else "all monitored locations"
    return (
        f"📋 Summary: Out of {len(dff):,} locations in {area}, "
        f"{high_count:,} ({high_pct:.1f}%) require urgent trimming. "
    )


# KPIs row
@app.callback(
    Output("kpi-row", "children"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_kpis(county, city, risk):
    dff = filter_df(county, city, risk)
    weather_index = (
        dff["avg_temp"].mean() + dff["avg_wind"].mean()
        - dff["avg_rain"].mean()
    )
    kpis = [
        ("🌿 Average Risk\nScore (0–100)",
         f"{dff['trimming_priority_score'].mean():.1f}"),
        ("⚠️ Locations Needing\nUrgent Trimming",
         f"{int(dff['is_high_risk'].sum()):,}"),
        ("🌲 Vegetation\nDensity",
         f"{dff['biomass_tons_ha'].mean():.0f} t/ha"),
        ("🔥 Average\nFire Risk Level",
         f"{(dff['fire_recurrence'].mean() + dff['log_fire_size'].mean()):.2f}"),
        ("🔥 Avg. Fire\nOccurrences",
         f"{dff['fire_recurrence'].mean():.2f}"),
        ("🌤️ Weather-Related\nRisk Score",
         f"{weather_index:.2f}"),
        ("💧 Average\nDryness Level",
         f"{dff['fuel_moisture_risk'].mean():.2f}"),
        ("📍 % of Locations\nat High Risk",
         f"{dff['is_high_risk'].mean()*100:.1f}%"),
    ]
    return [
        html.Div([
            html.Div(label, style={**LABEL, "whiteSpace": "pre-line"}),
            html.Div(value, style=VALUE),
        ], style=CARD)
        for label, value in kpis
    ]


# Map chart
@app.callback(
    Output("map-chart", "figure"),
    Input("county-filter",   "value"),
    Input("city-filter",     "value"),
    Input("risk-filter",     "value"),
    Input("map-zoom-slider", "value")
)
def update_map(county, city, risk, zoom):
    dff = filter_df(county, city, risk)

    fig = px.scatter_map(
        dff, lat="latitude", lon="longitude", color="risk_level",
        hover_name="city",
        hover_data={
            "county_name": True,
            "risk_score":  True,
            "risk_level":  False,
            "latitude":    True,
            "longitude":   True,
        },
        labels={
            "county_name": "County",
            "risk_score":  "Risk Score",
        },
        zoom=zoom, opacity=0.85,
        color_discrete_map={
            "Low":    "#639922",
            "Medium": "#EF9F27",
            "High":   "#E24B4A",
        },
        category_orders={"risk_level": ["High", "Medium", "Low"]}
    )

    # Add county boundaries as line traces on top of the scatter points
    fig = add_county_boundaries(fig, county)

    fig.update_layout(
        map_style="open-street-map",
        map=dict(                          
            center=dict(lat=37.5, lon=-119.5),
            zoom=zoom,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            title=dict(text="Risk Level", font=dict(size=11)),
            orientation="v",
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#ddd", borderwidth=1,
            font=dict(size=11),
        ),
        paper_bgcolor="white",
        autosize=True,
    )

    newnames = {
        "High":   "🔴 Trim Now",
        "Medium": "🟡 Monitor Closely",
        "Low":    "🟢 No Action",
    }
    fig.for_each_trace(
        lambda t: t.update(name=newnames.get(t.name, t.name))
    )
    return fig


# Top counties table
@app.callback(
    Output("top-counties-table", "data"),
    Output("top-counties-table", "columns"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_table(county, city, risk):
    dff = filter_df(county, city, risk)
    top = (
        dff.groupby(["county_name", "city"])["risk_score"]
        .mean().reset_index()
        .sort_values("risk_score", ascending=False)
        .head(10).round(2)
    )
    top.columns = ["County", "City", "Risk Score (out of 100)"]
    columns = [{"name": c, "id": c} for c in top.columns]
    return top.to_dict("records"), columns


# Driving factors importance bars
@app.callback(
    Output("importance-bars", "children"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_importance_bars(county, city, risk):
    dff = filter_df(county, city, risk)
    area_label = (
        city   if city   != "All" else
        county if county != "All" else
        "This Area"
    )
    items = []

    for label, (col, score, unit, description) in FEATURES.items():
        if col not in dff.columns:
            continue

        local_avg  = dff[col].mean()
        state_avg  = STATEWIDE_AVG.get(col, local_avg)
        pct_diff   = ((local_avg - state_avg) / state_avg * 100
                      if state_avg != 0 else 0)
        is_higher  = local_avg > state_avg
        bar_color  = "#E24B4A" if is_higher else "#639922"
        diff_color = "#E24B4A" if is_higher else "#639922"

        if abs(pct_diff) < 5:
            situation = "Similar to the state average."
        elif is_higher:
            situation = (
                f"{area_label} is {abs(pct_diff):.0f}% above average — "
                f"higher risk than most areas."
            )
        else:
            situation = (
                f"{area_label} is {abs(pct_diff):.0f}% below average — "
                f"lower risk than most areas."
            )

        items.append(html.Div([
            html.Div(label, style={
                "fontSize": 11, "fontWeight": 600,
                "color": "#333", "marginBottom": 2
            }),
            html.Div(description, style={
                "fontSize": 10, "color": "#aaa",
                "marginBottom": 4, "fontStyle": "italic"
            }),
            html.Div([
                html.Div([
                    html.Span("This area: ",
                              style={"fontSize": 10, "color": "#888"}),
                    html.Span(f"{local_avg:.1f}{unit}",
                              style={"fontSize": 11, "fontWeight": 600,
                                     "color": bar_color}),
                ]),
                html.Div([
                    html.Span("State avg: ",
                              style={"fontSize": 10, "color": "#888"}),
                    html.Span(f"{state_avg:.1f}{unit}",
                              style={"fontSize": 10, "color": "#888"}),
                ]),
            ], style={
                "display": "flex", "justifyContent": "space-between",
                "marginBottom": 3
            }),
            html.Div(style={
                "position": "relative", "height": 8,
                "background": "#eee", "borderRadius": 4,
                "marginBottom": 2,
            }, children=[
                html.Div(style={
                    "width": f"{min((local_avg / max(local_avg, state_avg)) * 100, 100):.1f}%",
                    "height": "100%", "background": bar_color,
                    "borderRadius": 4, "opacity": 0.85,
                }),
            ]),
            html.Div([
                html.Span("▲ " if is_higher else "▼ ",
                          style={"color": diff_color, "fontSize": 10}),
                html.Span(situation,
                          style={"fontSize": 10, "color": diff_color,
                                 "fontWeight": 500}),
            ], style={"marginBottom": 10}),
        ]))

    return items


# Risk level distribution bars
@app.callback(
    Output("risk-dist-bars", "children"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_risk_dist(county, city, risk):
    dff = filter_df(county, city, risk)
    total = max(len(dff), 1)
    bars = [
        ("🔴 High — Trim Now",
         (dff["risk_level"] == "High").sum() / total * 100,
         int((dff["risk_level"] == "High").sum()),
         "#E24B4A"),
        ("🟡 Medium — Monitor",
         (dff["risk_level"] == "Medium").sum() / total * 100,
         int((dff["risk_level"] == "Medium").sum()),
         "#EF9F27"),
        ("🟢 Low — No Action",
         (dff["risk_level"] == "Low").sum() / total * 100,
         int((dff["risk_level"] == "Low").sum()),
         "#639922"),
    ]
    return [
        html.Div([
            html.Div([
                html.Div(style={
                    "width": f"{pct:.1f}%", "height": "7px",
                    "background": color, "borderRadius": 4
                })
            ], style={"height": 7, "background": "#eee",
                      "borderRadius": 4, "marginBottom": 4}),
            html.Div(
                f"{label}: {pct:.1f}% ({count:,} locations)",
                style={"fontSize": 11, "color": "#555"}
            )
        ], style={"marginBottom": 10})
        for label, pct, count, color in bars
    ]


# Monthly heatmap
@app.callback(
    Output("month-heatmap", "children"),
    Input("county-filter", "value"),
    Input("city-filter",   "value"),
    Input("risk-filter",   "value")
)
def update_month_heatmap(county, city, risk):
    dff = filter_df(county, city, risk)

    all_months = pd.DataFrame({
        "fire_month":      list(range(1, 13)),
        "fire_month_name": ["Jan","Feb","Mar","Apr","May","Jun",
                            "Jul","Aug","Sep","Oct","Nov","Dec"]
    })
    monthly = (
        dff.groupby(["fire_month", "fire_month_name"])["risk_score"]
        .mean().reset_index()
    )
    monthly = all_months.merge(
        monthly, on=["fire_month", "fire_month_name"], how="left"
    ).fillna(0)

    cells = []
    for _, row in monthly.iterrows():
        score   = row["risk_score"]
        bg      = ("#E24B4A" if score > 65
                   else "#EF9F27" if score > 35
                   else "#639922")
        opacity = 0.25 + (score / 100) * 0.75 if score > 0 else 0.15
        cells.append(
            html.Div([
                html.Div(row["fire_month_name"], style={
                    "fontSize": 9, "color": "white",
                    "fontWeight": 500, "lineHeight": 1
                }),
                html.Div(f"{score:.0f}", style={
                    "fontSize": 11, "color": "white",
                    "fontWeight": 600, "marginTop": 2
                }),
            ], style={
                "background": bg, "opacity": opacity,
                "borderRadius": 4, "padding": "5px 3px",
                "textAlign": "center", "cursor": "default",
            },
            title=f"{row['fire_month_name']}: avg risk score {score:.1f}")
        )

    legend = html.Div([
        html.Span([
            html.Span(style={
                "width": 8, "height": 8, "borderRadius": 2,
                "background": c, "display": "inline-block",
                "marginRight": 3
            }),
            html.Span(lbl, style={"fontSize": 10, "color": "#555"})
        ], style={"marginRight": 8})
        for c, lbl in [
            ("#639922", "Low"),
            ("#EF9F27", "Medium"),
            ("#E24B4A", "High")
        ]
    ], style={"display": "flex", "alignItems": "center", "marginTop": 6})

    return html.Div([
        html.Div(cells, style={
            "display": "grid",
            "gridTemplateColumns": "repeat(4, 1fr)",
            "gap": 4, "marginBottom": 4,
        }),
        legend
    ])


# Run the app
if __name__ == "__main__":
    app.run(debug=True)