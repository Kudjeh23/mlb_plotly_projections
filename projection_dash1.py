from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from dash import dcc, html, callback, dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Select

'''
pip install dash pandas plotly
'''

hitter_df = pd.read_csv('MLB 2025 Quick Projections - Hitters CSV.csv', sep=',')
hitter_df= hitter_df.sort_values(by="Team", ascending=True)
teams = hitter_df["Team"].drop_duplicates().tolist()
hitter_df= hitter_df.sort_values(by="wRC+", ascending=False)
hitter_df["Pct"] = (hitter_df["PA"]/hitter_df.groupby(["Year","Team"])["PA"].transform("sum")) * 100
# hitter_df["Pct"] = hitter_df["Pct"].apply(lambda x: "{:.2f}%".format(x))

pitcher_df = pd.read_csv('MLB 2025 Quick Projections - Pitchers CSV.csv', sep=',')
pitcher_df = pitcher_df.sort_values(by="FIP", ascending=True)
pitcher_df["Pct"] = (pitcher_df["IP"]/pitcher_df.groupby(["Year","Team"])["IP"].transform("sum")) * 100
# pitcher_df["Pct"] = pitcher_df["Pct"].apply(lambda x: "{:.2f}%".format(x))

# custom_scale = ["red", "lightcoral", "white", "lightgreen", "green"]
custom_scale = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# App layout
app.layout = dbc.Container([
    html.H1(children='YOY Team Changes', style={'text-align': 'center'}),
    html.Hr(),
    dbc.Select(
        id='dropdown',
        options=teams,
        value='CLE',
        # clearable=False
    ),
    dbc.Row([
        dbc.Col(
            dag.AgGrid(
                id="grid",
                columnDefs=[{"field": i} for i in hitter_df.columns],
                columnSize="sizeToFit")),
            ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph1'), width=6),
        dbc.Col(dcc.Graph(id='graph2'), width=6),
    ], style={"margin": "50px"}
        )
])

# Add controls to build the interaction
@callback(
    Output("graph1", "figure"),
    Output("grid", "rowData"),
    Output("graph2", "figure"),
    Input("dropdown", "value"))
def update_bar_chart(team):
    choice = hitter_df["Team"] == team
    choice2 = pitcher_df["Team"] == team
    fig = px.bar(hitter_df[choice], 
                 x="Year", 
                 y="Pct", 
                 color="wRC+", 
                 barmode="group",
                 color_continuous_scale=custom_scale,
                 range_color=[28, 172],
                 title=f"<b>{team} wRC+ by <br> Percent of Team's Plate Appearances <br> 2024 Actual vs. 2025 Steamer Proj </b>",
                 labels={"Pct": "Percentage of PAs"})
    fig.layout.title.x = 0.5
    fig.layout.title.xanchor = "center"
    fig.layout.barcornerradius = 10
    filtered_df = hitter_df[hitter_df["Team"] == team]
    fig2 = px.bar(pitcher_df[choice2],
                 x="Year",
                 y="Pct", 
                 color="FIP", 
                 barmode="group",
                 title=f"<b>{team} FIP by <br> Percent of Team's Innings Pitched <br> 2024 Actual vs. 2025 Steamer Proj </b>",
                 labels={"Pct": "Percentage of IPs"},
                 color_continuous_scale=custom_scale[::-1],
                 range_color=[2.5, 5.9])
    fig2.layout.title.x = 0.5
    fig2.layout.title.xanchor = "center"
    fig2.layout.barcornerradius = 10
    return fig, filtered_df.to_dict("records"), fig2

# Run the app
if __name__ == '__main__':
    app.run(debug=True)