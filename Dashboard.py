import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px


# ================================================================
# 1. Read the LOAN dataset
# ================================================================

df = pd.read_csv("clean_loan_data.csv")

# ================================================================
# 2. Initialize Dash app
# ================================================================
app = Dash(__name__)
app.title = "Loan Dashboard"

income_min = int(df["Income"].min())
income_max = int(df["Income"].max())

# ================================================================
# 3. Layout
# ================================================================
app.layout = html.Div([
    html.H1(" Loan Dashboard", style={"textAlign": "center"}),

    # === KPI CARDS ===
    html.Div([
        html.Div(id="kpi-total", style={
            "width": "32%", "display": "inline-block",
            "backgroundColor": "#FF8C42", "padding": "12px",  # balanced bold orange
            "margin": "4px", "borderRadius": "6px", "textAlign": "center"
        }),
        html.Div(id="kpi-avg-income", style={
            "width": "32%", "display": "inline-block",
            "backgroundColor": "#FFD93D", "padding": "12px",  # golden yellow
            "margin": "4px", "borderRadius": "6px", "textAlign": "center"
        }),
        html.Div(id="kpi-approval", style={
            "width": "32%", "display": "inline-block",
            "backgroundColor": "#6A4C93", "padding": "12px",  # soft bold purple
            "margin": "4px", "borderRadius": "6px", "textAlign": "center"
        }),
    ], style={"marginBottom": "12px"}),

    # === Filters row ===
    html.Div([
        html.Div([
            html.Label("Loan Status:"),
            dcc.Dropdown(
                id="status-dropdown",
                options=[{"label": "All", "value": "ALL"}] +
                        [{"label": s, "value": s} for s in sorted(df["Loan_Status"].unique())],
                value="ALL",
                clearable=False
            )
        ], style={"width": "32%", "display": "inline-block", "padding": "6px"}),

        html.Div([
            html.Label("Gender:"),
            dcc.Dropdown(
                id="gender-dropdown",
                options=[{"label": "All", "value": "ALL"}] +
                        [{"label": g, "value": g} for g in sorted(df["Gender"].unique())],
                value="ALL",
                clearable=False
            )
        ], style={"width": "32%", "display": "inline-block", "padding": "6px"}),

        html.Div([
            html.Label("Income Range:"),
            dcc.RangeSlider(
                id="income-slider",
                min=income_min,
                max=income_max,
                step=1000,
                value=[income_min, income_max],
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], style={"width": "32%", "display": "inline-block", "padding": "18px 6px 6px 6px"})
    ], style={"marginBottom": "18px"}),

    # === Row 1 (Funnel, Bar Credit) ===
    html.Div([
        dcc.Graph(id="funnel-chart", style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(id="bar-credit", style={"width": "48%", "display": "inline-block"}),
    ]),

    # === Row 2 (Line, Pie) ===
    html.Div([
        dcc.Graph(id="income-loan-line", style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(id="pie-status", style={"width": "48%", "display": "inline-block"}),
    ]),

    # === Row 3 (Histogram, Scatter, Insights) ===
    html.Div([
        dcc.Graph(id="loan-hist", style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(id="scatter-income-loan", style={"width": "48%", "display": "inline-block"}),
        html.Div(id="insights-box", style={
            "width": "48%", "display": "inline-block",
            "verticalAlign": "top", "padding": "12px",
            "backgroundColor": "#D6EFFF", "borderRadius": "6px", "marginLeft": "6px"  # soft bold light blue
        }),
    ]),

    html.H3("Filtered Loan Dataset"),
    dash_table.DataTable(
        id="data-table",
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=15,
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#6A4C93", "color": "white", "fontWeight": "bold"},
        style_data={"backgroundColor": "#7cb4e6", "color": "white", "border": "1px solid #ddd"}
    )
])

# ================================================================
# 4. Callback
# ================================================================
@app.callback(
    Output("funnel-chart", "figure"),
    Output("bar-credit", "figure"),
    Output("income-loan-line", "figure"),
    Output("pie-status", "figure"),
    Output("loan-hist", "figure"),
    Output("scatter-income-loan", "figure"),
    Output("data-table", "data"),
    Output("kpi-total", "children"),
    Output("kpi-avg-income", "children"),
    Output("kpi-approval", "children"),
    Output("insights-box", "children"),
    Input("status-dropdown", "value"),
    Input("gender-dropdown", "value"),
    Input("income-slider", "value")
)
def update_dashboard(selected_status, selected_gender, income_range):
    dff = df.copy()
    if selected_status != "ALL":
        dff = dff[dff["Loan_Status"] == selected_status]
    if selected_gender != "ALL":
        dff = dff[dff["Gender"] == selected_gender]
    dff = dff[(dff["Income"] >= income_range[0]) & (dff["Income"] <= income_range[1])]

    # --- Funnel chart ---
    funnel_df = dff["Loan_Status"].value_counts().reset_index()
    funnel_df.columns = ["Loan_Status", "Count"]
    funnel_fig = px.funnel(funnel_df, x="Count", y="Loan_Status",
                           title="Loan Status Funnel",
                           color_discrete_sequence=["#FF8C42", "#FFD93D", "#6A4C93"])

    # --- Bar Credit ---
    bar_credit = px.bar(dff.groupby(["Credit_History", "Loan_Status"], as_index=False).size().rename(columns={"size":"Count"}),
                        x="Credit_History", y="Count", color="Loan_Status",
                        title="Credit History by Loan Status",
                        color_discrete_sequence=["#FF8C42", "#FFD93D", "#6A4C93"])

    # --- Line ---
    line_fig = px.line(dff.sort_values("Income"), x="Income", y="Loan_Amount",
                       title="Loan Amount by Income", markers=True,
                       color_discrete_sequence=["#FF6B6B"])

    # --- Pie ---
    pie_fig = px.pie(dff, names="Credit_History", title="Credit History Distribution",
                     color_discrete_sequence=["#FF8C42", "#FFD93D", "#6A4C93"])

    # --- Histogram ---
    loan_hist = px.histogram(dff, x="Loan_Amount", nbins=25, title="Loan Amount Distribution",
                             opacity=0.75, color_discrete_sequence=["#6AB04C"])

    # --- Scatter ---
    scatter_fig = px.scatter(dff, x="Income", y="Loan_Amount", color="Loan_Status",
                             title="Income vs Loan Amount", opacity=0.7,
                             color_discrete_sequence=["#FF8C42", "#FFD93D", "#6A4C93"])

    # --- Table ---
    table_data = dff.to_dict("records")

    # --- KPIs ---
    total_kpi = html.Div([html.H4("Total Applicants"), html.H2(f"{len(dff)}")], style={"margin": "0"})
    avg_income = dff["Income"].mean() if len(dff) > 0 else 0
    avg_income_kpi = html.Div([html.H4("Average Income"), html.H2(f"{avg_income:,.0f}")], style={"margin": "0"})
    approval_rate = (dff["Loan_Status"].eq("Approved").mean() * 100) if len(dff) > 0 else 0
    approval_kpi = html.Div([html.H4("Approval Rate"), html.H2(f"{approval_rate:.1f}%")], style={"margin": "0"})

    # --- Insights ---
    insights_html = html.Div([
        html.P(f"• Applicants: {len(dff)}"),
        html.P(f"• Avg income: {avg_income:,.0f}"),
        html.P(f"• Approval rate: {approval_rate:.1f}%")
    ], style={"backgroundColor": "#D6EFFF", "padding": "12px", "borderRadius": "6px"})

    return funnel_fig, bar_credit, line_fig, pie_fig, loan_hist, scatter_fig, table_data, total_kpi, avg_income_kpi, approval_kpi, insights_html

# ================================================================
# 5. Run the app
# ================================================================
if __name__ == "__main__":
    app.run(debug=True)
