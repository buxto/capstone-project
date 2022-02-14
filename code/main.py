from ast import In
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import plotly.express as px
import pandas as pd
import pymssql
from joblib import dump, load
from plotly.subplots import make_subplots
import plotly.graph_objs as go
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


def createHistStock(ticker, title):
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hstock"
    try:
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    df = getData(table)
    df2 = df[df["Ticker"] == ticker]
    df2.sort_values(by=['Date'], inplace=True)
    fig = px.line(df2, x="Date", y="Open", title=f"{title} ({ticker})")

    return fig


def createHistCryptoStock(currency, title):
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hcrypto"
    try:
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    df = getData(table)
    df2 = df[df["Currency"] == currency]
    df2.sort_values(by=['Date'], inplace=True)
    fig = px.line(df2, x="Date", y="Open", title=f"{title} ({currency})")

    return fig

def createFig(table, ticker, title):
    df = getData(table)
    df2 = df[df["Ticker"] == ticker]
    df2.sort_values(by=['Time'], inplace=True)
    fig = px.line(df2, x="Time", y="Current Price", title=f"{title} ({ticker})")
    return fig


def createFigArima():
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
        arima_mdl = load(r'arima.model')
    except Exception as e:
        print(e)

    new_dates = [m_df.index[-1] + x for x in range(1, 11)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)
    ar_df = pd.concat([m_df, df_pred])
    ar_df['predictions'] = arima_mdl.predict(start=m_df.shape[0], end=ar_df.shape[0])

    # Plotting
    sub_fig = make_subplots(specs=[[{"secondary_y": False}]])

    # fig = px.line(ar_df, y='High', markers=True)
    fig1 = px.line(ar_df, y='High', markers=True)
    fig2 = px.line(ar_df, y='predictions', markers=True, color_discrete_sequence=px.colors.qualitative.Light24)
    sub_fig.add_traces(fig1.data + fig2.data)

    return sub_fig


def createFigAutoReg():
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

    # Plotting
    sub_fig = make_subplots(specs=[[{"secondary_y": False}]])

    # fig = px.line(ar_df, y='High', markers=True)
    fig1 = px.line(ar_df, y='High', markers=True)
    fig2 = px.line(ar_df, y='predictions', markers=True, color_discrete_sequence=px.colors.qualitative.Light24)
    sub_fig.add_traces(fig1.data + fig2.data)

    return sub_fig


# -----------------------------------------------------------------------


# link fontawesome to get the chevron icons
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA], suppress_callback_exceptions=True)
server = app.server

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
}
# The styles for the main contnet position it to the rigth of the sidebar and add some padding
CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
    "overflowX": "scroll"
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
            dbc.NavLink("Finance", href="/page-2/1"),
            dbc.NavLink("Manufacturing", href="/page-2/2"),
            dbc.NavLink("Information", href="/page-2/3"),
            dbc.NavLink("Retail", href="/page-2/4"),
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
            dbc.NavLink("Crypto Stocks", href="/page-3/1"),
            # dbc.NavLink("Page 3.2", href="/page-3/2"),
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
        html.H2("Title(TDB)", className="display-4"),
        html.Hr(),
        html.P(
            "Subtitle (TBD)", className="lead"
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


for i in range(1, 5):
    app.callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [State(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    app.callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)


@app.callback(Output('finance-live', 'children'), Input('interval-component', 'n_intervals'))
def update_finance(n):
    return [
        html.H1(children='Finance', style={"textAlign": "center"}),
        html.Table(
            children=[
                html.Tbody(children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'V', 'VISA')
                            ),
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'JPM', 'JPMorgan Chase')
                            )
                        )
                    ]),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'BAC', 'Bank of America')
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'MA', 'Mastercard')
                            )
                        )
                    ])
                ])

            ],
            style={"width": "100%", "tableLayout": "fixed"}
        )
    ]


@app.callback(Output('manufacturing-live', 'children'), Input('interval-component', 'n_intervals'))
def update_manufacturing(n):
    return [
        html.H1(children='Manufacturing', style={"textAlign": "center"}),
        html.Table(
            children=[
                html.Tbody(children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'AAPL', 'Apple')
                            ),
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'MSFT', 'Microsoft')
                            )
                        )
                    ]),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'MGPI', 'MGP Ingredients Inc')
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'KWR', 'Quaker Chemical Corp')
                            )
                        )
                    ])

                ])

            ],
            style={"width": "100%", "tableLayout": "fixed"}
        )
    ]


@app.callback(Output('information-live', 'children'), Input('interval-component', 'n_intervals'))
def update_information(n):
    return [
        html.H1(children='Information', style={"textAlign": "center"}),
        html.Table(
            children=[
                html.Tbody(children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'CMCSA', 'Comcast')
                            ),
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'VZ', 'Verizon')
                            )
                        )
                    ]),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'T', 'AT&T')
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'TMUS', 'T-Mobile')
                            )
                        )
                    ])
                ])

            ],
            style={"width": "100%", "tableLayout": "fixed"}
        )
    ]


@app.callback(Output('retail-live', 'children'), Input('interval-component', 'n_intervals'))
def update_retail(n):
    return [
        html.H1(children='Retail', style={"textAlign": "center"}),
        html.Table(
            children=[
                html.Tbody(children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'AMZN', 'Amazon')
                            ),
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'WMT', 'Walmart')
                            )
                        )
                    ]),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'HD', 'Home Depot')
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createFig('rtstock', 'COST', 'Costco')
                            )
                        )
                    ])
                ])

            ],
            style={"width": "100%", "tableLayout": "fixed"}
        )
    ]


def historicalStockGraphs(industry, tickers, names):
    return html.Div(children=[
            html.H1(children=industry, style={"textAlign": "center"}),
            html.Table(children=[
                html.Tbody(
                    children=[
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    figure=createHistStock(tickers[0], names[0])
                                )
                            ),
                            html.Td(
                                dcc.Graph(
                                    figure=createHistStock(tickers[1], names[1])
                                )
                            )
                        ],
                        ),
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    figure=createHistStock(tickers[2], names[2])
                                )
                            ),
                            html.Td(
                                dcc.Graph(
                                    figure=createHistStock(tickers[3], names[3])
                                )
                            )
                        ],
                        ),
                    ],
                ),

            ], style={"width": "100%", "tableLayout": "fixed"}
            ),
        ]
        )


def historicalCryptoGraphs(industry, tickers, names):
    return html.Div(children=[
            html.H1(children=industry, style={"textAlign": "center"}),
            html.Table(children=[
                html.Tbody(
                    children=[
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    figure=createHistCryptoStock(tickers[0], names[0])
                                )
                            ),
                            html.Td(
                                dcc.Graph(
                                    figure=createHistCryptoStock(tickers[1], names[1])
                                )
                            )
                        ],
                        ),
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    figure=createHistCryptoStock(tickers[2], names[2])
                                )
                            ),
                            html.Td(
                                dcc.Graph(
                                    figure=createHistCryptoStock(tickers[3], names[3])
                                )
                            )
                        ],
                        ),
                    ],
                ),

            ], style={"width": "100%", "tableLayout": "fixed"}
            ),
        ]
        )



@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1/1"]:
        return html.Div([
            html.Div(id='finance-live'),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-1/2":
        return html.Div([
            html.Div(id='manufacturing-live'),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-1/3":
        return html.Div([
            html.Div(id='information-live'),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-1/4":
        return html.Div([
            html.Div(id='retail-live'),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,
                n_intervals=0
            )
        ])

    elif pathname == "/page-2/1":
        return historicalStockGraphs('Finance', ['V', 'JPM', 'BAC', 'MA'], ['VISA', 'JPMorgan Chase', 'Bank of America', 'Mastercard'])
    elif pathname == "/page-2/2":
        return historicalStockGraphs('Manufacturing', ['AAPL', 'MSFT', 'MGPI', 'KWR'], ['Apple', 'Microsoft', 'MGP Ingredients Inc', 'Quaker Chemical Corp'])
    elif pathname == "/page-2/3":
        return historicalStockGraphs('Information', ['CMCSA', 'VZ', 'T', 'TMUS'], ['Comcast', 'Verizon', 'AT&T', 'T-Mobile'])
    elif pathname == "/page-2/4":
        return historicalStockGraphs('Retail', ['AMZN', 'WMT', 'HD', 'COST'], ['Amazon', 'Walmart', 'Home Depot', 'Costco'])
    elif pathname == "/page-3/1":
        return historicalCryptoGraphs('Historical Crypto Stocks', ['BTC', 'ETH', 'LTC', 'DOGE'], ['Bitcoin', 'Ethereum', 'Litecoin', 'Dogecoin'])
    # elif pathname == "/page-3/2":
    #     return html.P("This is page 3.2")
    elif pathname == "/page-4/1":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"textAlign": "center"}),
            html.Hr(),
            html.Div(
                html.Table(children=[
                    html.Tbody(children=[
                        html.Tr(children=[
                            html.Td(
                                html.H4(children='AutoReg Model', style={"textAlign": "center"}),
                            ),
                            html.Td(
                                html.H4(children='Arima Model', style={"textAlign": "center"}),
                            )
                        ]),
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    id="ml1 id",
                                    figure=createFigAutoReg()
                                ),
                            ),
                            html.Td(
                                dcc.Graph(
                                    id="ml1 id",
                                    figure=createFigArima()
                                ),
                            )
                        ])

                    ]),

                ], style={"width": "100%", "tableLayout": "fixed"})
            )
        ])

    elif pathname == "/page-4/2":
        return html.P("This is page 4.2")
    return dbc.Jumbotron(
        [
            html.H1("404: Not Found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)
