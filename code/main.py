from ast import In
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import plotly.express as px
import pandas as pd
import pymssql
from joblib import dump, load
from plotly.subplots import make_subplots
import plotly
import matplotlib.pyplot as plt
import joblib

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ar_model import AutoReg as ar
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

database = "group3-DB"
table = "dbo.rtstock"
username = "group3_user"
password = "K-qC4SoI_oUvepg"
server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"

conn = pymssql.connect(server, username, password, database)
# table = "dbo.hstock"


def getData(table):
    # try:
    #     conn = pymssql.connect(server, username, password, database)
    # except Exception as e:
    #     print(e)
    cursor = conn.cursor()
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)
    return df


def createFig(table, ticker, title):
    df = getData(table)
    df2 = df[df["Ticker"] == ticker]
    df2.sort_values(by=['Time'], inplace=True)
    fig = px.line(df2, x="Time", y="Current Price", title=f"{title} ({ticker})"
                  # labels={
                  #     "Timestamp": "Need to convert from timestamp to time",
                  #     "Open Price": "Current Price ($)"
                  #     },
                  )
    return fig


def createFigML():

    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hstock"
    try:
        # print(f"server {server}, username {username}, password {password}, database {database}")
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    cursor = conn1.cursor()
    query = f"SELECT * FROM {table}"
    hst_df = pd.read_sql(query, conn1)
    apple_df = hst_df[hst_df['Ticker'] == 'AAPL']
    apple_df = apple_df.drop(columns='Ticker')
    apple_df['Date'] = pd.to_datetime(apple_df['Date'], format='%Y-%m-%d')
    apple_df.reset_index(drop=True, inplace=True)

    m_df = apple_df.drop(columns=['Date', 'Open', 'Close', 'Low', 'Volume'])

    try:
        res2 = load(r'autoreg.model')
    except Exception as e:
        print(e)


    new_dates = [m_df.index[-1] + x for x in range(1, 11)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)

    ar_df = pd.concat([m_df, df_pred])

    # start at the end of original data, go til the end of this new dataframe
    ar_df['predictions'] = res2.predict(start=m_df.shape[0], end=ar_df.shape[0])
    # fig = ar_df[['High', 'predictions']].plot(marker='o')

    sub_fig = make_subplots(specs=[[{"secondary_y": False}]])

    # fig = px.line(ar_df, y='High', markers=True)
    fig1 = px.line(ar_df, y='High', markers=True)
    fig2 = px.line(ar_df, y='predictions', markers=True, color_discrete_sequence=px.colors.qualitative.Light24)
    sub_fig.add_traces(fig1.data + fig2.data)

    return sub_fig
# -----------------------------------------------------------------------


# link fontawesome to get the chevron icons
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
server = app.server

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
# The styles for the main contnet position it to the rigth of the sidebar and add some padding
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "overflow-x": "scroll"
}


submenu_1 = [
    html.Li(
        # use Row and Col components to postion the chevrons
        dbc.Row(
            [
                dbc.Col("Live Stock Data"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-1",
    ),
    # we use the collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Finance", href="/page-1/1"),
            dbc.NavLink("Manufacturing", href="/page-1/2"),
            dbc.NavLink("Information", href="/page-1/3"),
            dbc.NavLink("Retail", href="/page-1/4"),
        ],
        id="submenu-1-collapse",
    ),
]

submenu_2 = [
    html.Li(
        # use Row and Col components to postion the chevrons
        dbc.Row(
            [
                dbc.Col("Historical Stock Data"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-2",
    ),
    # we use the collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Page 2.1", href="/page-2/1"),
            dbc.NavLink("Page 2.2", href="/page-2/2"),
        ],
        id="submenu-2-collapse",
    ),
]

submenu_3 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Historical Crypto Data"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-3",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Page 3.1", href="/page-3/1"),
            dbc.NavLink("Page 3.2", href="/page-3/2"),
        ],
        id="submenu-3-collapse",
    ),
]


submenu_4 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Machine Learning"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-4",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Stocks", href="/page-4/1"),
            dbc.NavLink("Cryptocurrency", href="/page-4/2"),
        ],
        id="submenu-4-collapse",
    ),
]

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A sidebar with collapsable navigation links", className="lead"
        ),
        dbc.Nav(submenu_1 + submenu_2 + submenu_3 + submenu_4, vertical=True),
    ],
    style=SIDEBAR_STYLE,
    id="sidebar",
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this function is used to toggle the is_open property of each Collapse
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# this function applies the "open" class to rotate the chevron
def set_navitem_class(is_open):
    if is_open:
        return "open"
    return ""


for i in [1, 2, 3, 4]:
    app.callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [State(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    app.callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)


# dcc.Interval(
#     id='interval-component',
#     interval=60*1000,
#     n_intervals=0
# )
# @app.callback(Output('graph_id', 'figure'),Input('interval-component', 'n_intervals'))

# def UpdateData(n):
#     createGraph()


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1/1"]:
        return html.Div(children=[
            html.H1(children='Finance', style={"text-align": "center"}),
            html.Table(children=[
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="f1 id",
                            figure=createFig('rtstock', 'V', 'VISA')
                        ),
                    ),
                    html.Td(
                        dcc.Graph(
                            id="f2 id",
                            figure=createFig('rtstock', 'JPM', 'JPMorgan Chase')
                        )
                    )
                ],
                ),
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="f3 id",
                            figure=createFig('rtstock', 'BAC', 'Bank of America')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="f4 id",
                            figure=createFig('rtstock', 'MA', 'Mastercard ')
                        )
                    )
                ],
                ),
            ]
            ),
            ]
        ),

    elif pathname == "/page-1/2":
        return html.Div(children=[
            html.H1(children='Manufacturing', style={"text-align": "center"}),
            html.Table(children=[
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="m1 id",
                            figure=createFig('rtstock', 'AAPL', 'Apple')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="m2 id",
                            figure=createFig('rtstock', 'MSFT', 'Microsoft')
                        )
                    )
                ],
                ),
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="m3 id",
                            figure=createFig('rtstock', 'MGPI', 'MGP Ingredients Inc')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="m4 id",
                            figure=createFig('rtstock', 'KWR', 'Quaker Chemical Corp')
                        )
                    )
                ],
                ),
            ]
            ),
            ]
        ),

    elif pathname == "/page-1/3":
        return html.Div(children=[
            html.H1(children='Information', style={"text-align": "center"}),
            html.Table(children=[
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="i1 id",
                            figure=createFig('rtstock', 'CMCSA', 'Comcast')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="i2 id",
                            figure=createFig('rtstock', 'VZ', 'Verizon')
                        )
                    )
                ],
                ),
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="i3 id",
                            figure=createFig('rtstock', 'T', 'AT&T')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="i4 id",
                            figure=createFig('rtstock', 'TMUS', 'T-Mobile')
                        )
                    )
                ],
                ),
            ]
            ),
            ]
        ),
    elif pathname == "/page-1/4":
        return html.Div(children=[
            html.H1(children='Retail', style={"text-align": "center"}),
            html.Table(children=[
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="i1 id",
                            figure=createFig('rtstock', 'AMZN', 'Amazon')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="i2 id",
                            figure=createFig('rtstock', 'WMT', 'Walmart')
                        )
                    )
                ],
                ),
                html.Tr(children=[
                    html.Td(
                        dcc.Graph(
                            id="i3 id",
                            figure=createFig('rtstock', 'HD', 'Home Depot')
                        )
                    ),
                    html.Td(
                        dcc.Graph(
                            id="i4 id",
                            figure=createFig('rtstock', 'COST', 'Costco')
                        )
                    )
                ],
                ),
            ]
            ),
            ]
        ),

    elif pathname == "/page-2/1":
        return html.P("This is page 2.1")
    elif pathname == "/page-2/2":
        return html.P("This is page 2.2")
    elif pathname == "/page-3/1":
        return html.P("This is page 3.1")
    elif pathname == "/page-3/2":
        return html.P("This is page 3.2")
    elif pathname == "/page-4/1":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"text-align": "center"}),
            html.Hr(),
            html.H3(children='AutoReg Model', style={"text-align": "center"}),
            html.Div(
                        dcc.Graph(
                            id="ml1 id",
                            figure=createFigML()
                        )
                    )
                ],
        ),
    elif pathname == "/page-4/2":
        return html.P("This is page 4.2")
    return dbc.Jumbotron(
        [
            html.H1("404: Not Found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )


# @app.callback(Output('f1 id', 'figure'), Input('interval-component', 'n_intervals'))
# def update_fin(arg):
#     print(f"Update fins {arg}")
#

if __name__ == '__main__':
    app.run_server(debug=True)
