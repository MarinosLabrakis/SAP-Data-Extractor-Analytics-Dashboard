"""Plotly Dash dashboard — KPIs, vendor scorecard, aging, anomalies."""
from __future__ import annotations
import asyncio
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from ..services.analytics_service import AnalyticsService
from ..ai.anomaly import score as anomaly_score


def _kpi_card(title: str, value: str | int | float) -> dbc.Card:
    return dbc.Card(dbc.CardBody([
        html.Div(title, className="text-muted small"),
        html.H3(f"{value:,}" if isinstance(value, (int, float)) else value, className="mb-0"),
    ]))


def build_layout():
    svc = AnalyticsService()
    kpis      = asyncio.run(svc.kpis())
    scorecard = asyncio.run(svc.vendor_scorecard())
    aging     = asyncio.run(svc.aging())
    df_inv    = asyncio.run(svc.load_invoices_df())

    df_inv = df_inv.assign(days_to_due=(df_inv.get("due_date") - df_inv.get("invoice_date"))
                           .dt.days if not df_inv.empty else 0)
    scored = anomaly_score(df_inv) if not df_inv.empty else df_inv

    aging_chart = (px.histogram(aging, x="bucket", y="amount_eur",
                                title="Aging (EUR by bucket)", color="bucket")
                   if not aging.empty else px.scatter(title="No data"))

    top_chart = (px.bar(scorecard.head(10), x="vendor_id", y="total_eur",
                        title="Top 10 Vendors by Spend (EUR)")
                 if not scorecard.empty else px.scatter(title="No data"))

    return dbc.Container([
        html.H2("SAP P2P Analytics", className="mt-4"),
        html.Div("Side-by-side analytics on SAP S/4HANA Procure-to-Pay data",
                 className="text-muted mb-4"),
        dbc.Row([
            dbc.Col(_kpi_card("Open Invoices",    kpis["open_invoices"]),    md=3),
            dbc.Col(_kpi_card("Overdue Invoices", kpis["overdue_invoices"]), md=3),
            dbc.Col(_kpi_card("Total Open (EUR)", round(kpis["total_open_eur"], 2)), md=3),
            dbc.Col(_kpi_card("Vendors",          kpis["vendor_count"]),     md=3),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=top_chart),   md=6),
            dbc.Col(dcc.Graph(figure=aging_chart), md=6),
        ], className="mt-4"),
        html.H4("Vendor Scorecard", className="mt-4"),
        dash_table.DataTable(
            data=scorecard.to_dict("records") if not scorecard.empty else [],
            columns=[{"name": c, "id": c} for c in scorecard.columns] if not scorecard.empty else [],
            page_size=10, style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#0FAAFF", "color": "white", "fontWeight": "bold"},
        ),
        html.H4("Top Anomalous Invoices", className="mt-4"),
        dash_table.DataTable(
            data=(scored.nsmallest(10, "anomaly_score")[
                  ["invoice_id", "vendor_id", "amount_eur", "status", "anomaly_score"]
                  ].to_dict("records") if "anomaly_score" in scored.columns else []),
            columns=[{"name": c, "id": c} for c in
                     ["invoice_id", "vendor_id", "amount_eur", "status", "anomaly_score"]],
            style_header={"backgroundColor": "#0FAAFF", "color": "white", "fontWeight": "bold"},
        ),
    ], fluid=True)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="SAP P2P Analytics")
app.layout = build_layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
