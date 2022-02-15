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
from datetime import datetime
import plotly.io as pio
import plotly
import matplotlib.pyplot as plt
import joblib
from statsmodels.tsa.arima.model import ARIMA
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

    df2 = df2[df2['Date'] >= datetime(2021, 9, 21, 0, 0, 0, 0).date()]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(title=f"{title} ({ticker})")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })
    # fig = px(df2, x="Date", y="Open", title=f"{title} ({ticker})")
    fig.add_trace(go.Bar(name="Volume", x=df2['Date'], y=df2['Volume'], opacity=0.5), secondary_y=False)

    fig.add_trace(go.Candlestick(name="Price",
                                 x=df2['Date'],
                                 open=df2['Open'],
                                 high=df2['High'],
                                 low=df2['Low'],
                                 close=df2['Close'],
                                 line=dict(width=1)
                                 ),
                                 secondary_y=True)
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            dict(values=["2021-11-25", "2021-12-24", "2022-01-17"]),  # hide holidays
        ]
    )

    return fig



def createHistCrypto(currency, title):
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hcrypto"
    try:
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    df = getData(table)
    df2 = df[df["Currency"] == currency]
    df2.sort_values(by=['Date'], inplace=True)

    df2 = df2[df2['Date'] >= datetime(2021, 9, 21, 0, 0, 0, 0).date()]


    pio.templates.default = "plotly_dark"

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = px(df2, x="Date", y="Open", title=f"{title} ({ticker})")
    fig.add_trace(go.Bar(name="Volume", x=df2['Date'], y=df2['Volume'], opacity=0.5), secondary_y=False)
    fig.update_layout(title=f"{title} ({currency})")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })
    fig.add_trace(go.Candlestick(name="Price",
                                 x=df2['Date'],
                                 open=df2['Open'],
                                 high=df2['High'],
                                 low=df2['Low'],
                                 close=df2['Close'],
                                 line=dict(width=1)
                                 ),
                                 secondary_y=True)
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            dict(values=["2021-11-25", "2021-12-24", "2022-01-17"])  # hide holidays
        ]
    )
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
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    cursor = conn1.cursor()
    query = f"SELECT * FROM {table}"
    hst_df = pd.read_sql(query, conn1)

    apple_df = hst_df[hst_df['Ticker'] == 'AAPL']
    apple_df = apple_df.drop(columns='Ticker')
    apple_df['Date'] = pd.to_datetime(apple_df['Date'], format='%Y-%m-%d')
    apple_df.sort_values('Date', inplace=True)
    apple_df = apple_df[apple_df['Date'] >= '2021-01-01']
    apple_df.reset_index(drop=True, inplace=True)

    m_df = apple_df.drop(columns=['Date', 'Open', 'Close', 'Low', 'Volume'])

    ar_test_data = m_df.iloc[-15:]
    ar_train_data = m_df.iloc[:-15]

    try:
        arima_mdl = load(r'starima.model')
    except Exception as e:
        print(e)

    new_dates = [m_df.index[-1] + x for x in range(1, 21)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)
    arima_df = pd.concat([m_df, df_pred])
    arima_df['predictions'] = arima_mdl.predict(start=ar_train_data.shape[0], end=arima_df.shape[0])


    # Plotting
    plot_df = arima_df.iloc[ar_train_data.shape[0]:ar_train_data.shape[0] + 5]

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=plot_df['High'],
                             mode='lines+markers',
                             name='High'))
    fig.add_trace(go.Scatter(y=plot_df['predictions'],
                             mode='lines+markers',
                             name='Predictions'))
    fig.update_layout(
        title="AAPL Arima Model Predictions",
        xaxis_title="",
        yaxis_title="Price",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


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
    apple_df.sort_values('Date', inplace=True)
    apple_df = apple_df[apple_df['Date'] >= '2021-01-01']
    apple_df.reset_index(drop=True, inplace=True)

    m_df = apple_df.drop(columns=['Date', 'Open', 'Close', 'Low', 'Volume'])

    ar_test_data = m_df.iloc[-15:]
    ar_train_data = m_df.iloc[:-15]

    try:
        res = load(r'stautoreg.model')
    except Exception as e:
        print(e)

    new_dates = [m_df.index[-1] + x for x in range(1, 21)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)

    ar_df = pd.concat([m_df, df_pred])

    # start at the end of original data, go til the end of this new dataframe
    ar_df['predictions'] = res.predict(start=ar_train_data.shape[0], end=ar_df.shape[0])

    # Plotting
    plot_df = ar_df.iloc[ar_train_data.shape[0]:ar_train_data.shape[0] + 5]

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=plot_df['High'],
                             mode='lines+markers',
                             name='High'))
    fig.add_trace(go.Scatter(y=plot_df['predictions'],
                             mode='lines+markers',
                             name='Predictions'))

    fig.update_layout(
        title="AAPL Autoregressive Model Predictions",
        xaxis_title="",
        yaxis_title="Price",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createFigAutoRegCrypto():
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hcrypto"
    try:
        # print(f"server {server}, username {username}, password {password}, database {database}")
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    cursor = conn1.cursor()
    query = f"SELECT * FROM {table}"
    hcr_df = pd.read_sql(query, conn)

    btc_df = hcr_df[hcr_df['Currency'] == 'BTC']
    btc_df = btc_df.drop(columns='Currency')
    btc_df['Date'] = pd.to_datetime(btc_df['Date'], format='%Y-%m-%d')
    btc_df.sort_values('Date', inplace=True)
    btc_df.reset_index(drop=True, inplace=True)

    m_df = btc_df.drop(columns=['Date', 'Open', 'Close', 'Low', 'Volume', 'Market Cap'])

    ar_train_data = m_df.iloc[:-15]
    ar_test_data = m_df.iloc[-15:]

    try:
        res = load(r'crautoreg.model')
    except Exception as e:
        print(e)

    new_dates = [m_df.index[-1] + x for x in range(1, 11)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)

    ar_df = pd.concat([m_df, df_pred])

    # start at the end of original data, go til the end of this new dataframe
    ar_df['predictions'] = res.predict(start=ar_train_data.shape[0], end=ar_df.shape[0])

    # High contrast plot of price versus predictions for future highs
    plot_df = ar_df.iloc[ar_train_data.shape[0]:ar_train_data.shape[0] + 5]

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=plot_df['High'],
                             mode='lines+markers',
                             name='High'))
    fig.add_trace(go.Scatter(y=plot_df['predictions'],
                             mode='lines+markers',
                             name='Predictions'))

    fig.update_layout(
        title="BTC Autoregressive Model Predictions",
        xaxis_title="",
        yaxis_title="Price",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createFigArimaCrypto():
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    table = "dbo.hcrypto"
    try:
        # print(f"server {server}, username {username}, password {password}, database {database}")
        conn1 = pymssql.connect(server, username, password, database)
    except Exception as e:
        print(e)

    cursor = conn1.cursor()
    query = f"SELECT * FROM {table}"
    hcr_df = pd.read_sql(query, conn)

    btc_df = hcr_df[hcr_df['Currency'] == 'BTC']
    btc_df = btc_df.drop(columns='Currency')
    btc_df['Date'] = pd.to_datetime(btc_df['Date'], format='%Y-%m-%d')
    btc_df.sort_values('Date', inplace=True)
    btc_df.reset_index(drop=True, inplace=True)

    m_df = btc_df.drop(columns=['Date', 'Open', 'Close', 'Low', 'Volume', 'Market Cap'])

    ar_test_data = m_df.iloc[-15:]
    ar_train_data = m_df.iloc[:-15]

    try:
        arima_mdl = load(r'crarima.model')
    except Exception as e:
        print(e)

    new_dates = [m_df.index[-1] + x for x in range(1, 11)]
    df_pred = pd.DataFrame(index=new_dates, columns=m_df.columns)
    arima_df = pd.concat([m_df, df_pred])
    arima_df['predictions'] = arima_mdl.predict(start=ar_train_data.shape[0], end=arima_df.shape[0])


    # Plotting
    plot_df = arima_df.iloc[ar_train_data.shape[0]:ar_train_data.shape[0] + 5]

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=plot_df['High'],
                             mode='lines+markers',
                             name='High'))
    fig.add_trace(go.Scatter(y=plot_df['predictions'],
                             mode='lines+markers',
                             name='Predictions'))
    fig.update_layout(
        title="BTC Arima Model Predictions",
        xaxis_title="",
        yaxis_title="Price",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig

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
    "width": "17rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
    "overflow-y": "scroll"
}
# The styles for the main contnet position it to the rigth of the sidebar and add some padding
CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}
HOMELINK_STYLE = {
    "width": "17rem",
    "font-size": "3rem"
}


submenu_1 = [
    html.Li(
        # use Row and Col components to postion the chevrons
        dbc.Row(
            [
                dbc.Col("Finance Industry"),
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
            dbc.NavLink("Live Stock Data", href="/page-1/1"),
            dbc.NavLink("Historical Stock Data", href="/page-1/2"),
            dbc.NavLink("Industry Data", href="/page-1/3")
        ],
        id="submenu-1-collapse",
    ),
]

submenu_2 = [
    html.Li(
        # use Row and Col components to postion the chevrons
        dbc.Row(
            [
                dbc.Col("Manufacturing Industry"),
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
            dbc.NavLink("Live Stock Data", href="/page-2/1"),
            dbc.NavLink("Historical Stock Data", href="/page-2/2"),
            dbc.NavLink("Industry Data", href="/page-2/3")
        ],
        id="submenu-2-collapse",
    ),
]

submenu_3 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Information Industry"),
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
            dbc.NavLink("Live Stock Data", href="/page-3/1"),
            dbc.NavLink("Historical Stock Data", href="/page-3/2"),
            dbc.NavLink("Industry Data", href="/page-3/3")
        ],
        id="submenu-3-collapse",
    ),
]

submenu_4 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Retail Industry"),
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
            dbc.NavLink("Live Stock Data", href="/page-4/1"),
            dbc.NavLink("Historical Stock Data", href="/page-4/2"),
            dbc.NavLink("Industry Data", href="/page-4/3")
        ],
        id="submenu-4-collapse",
    ),
]

submenu_5 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Cryptocurrencies"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-5",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Historial Crypto Data", href="/page-5/1"),
            dbc.NavLink("Crypto vs. Stocks", href="/page-5/2"),
        ],
        id="submenu-5-collapse",
    ),
]

submenu_6 = [
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
        id="submenu-6",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Stocks", href="/page-6/1"),
            dbc.NavLink("Cryptocurrency", href="/page-6/2"),
        ],
        id="submenu-6-collapse",
    ),
]
home_button = html.Div(
    dbc.NavLink("Home", href="/"),
    style=HOMELINK_STYLE,
)
sidebar = html.Div(
    [
        home_button,
        html.Hr(),
        html.P(
            "Subtitle (TBD)", className="lead"
        ),
        dbc.Nav(submenu_1 + submenu_2 + submenu_3 + submenu_4 + submenu_5 + submenu_6, vertical=True),
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


for i in range(1, 7):
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


def historicalCryptoGraphs(title, currencies, names):
    return html.Div(children=[
        html.H1(children=title, style={"textAlign": "center"}),
        html.Table(children=[
            html.Tbody(
                children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createHistCrypto(currencies[0], names[0])
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createHistCrypto(currencies[1], names[1])
                            )
                        )
                    ],
                    ),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createHistCrypto(currencies[2], names[2])
                            )
                        ),
                        html.Td(
                            dcc.Graph(
                                figure=createHistCrypto(currencies[3], names[3])
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

    if pathname == "/":
        return html.Div([
            html.H1(children="Stocks vs. Cryptocurrencies", style={"textAlign": "center", "marginBottom": "50px"}),
            html.P("This dashboard visualizes live streaming data on 16 differents stocks in 4 different industries, as well as historical data for those stocks and 4 different cryptocurrencies. It also directly compares the performances of stocks and crypto and takes a look at machine learning predictions for each. Use the sidebar on the left to explore!"),
            html.P(children="Our group:", style={"marginTop": "50px"}),
            html.Ul([
                html.Li(html.A(children='Connor Buxton', href='https://www.linkedin.com/in/connor-buxton-748103181/', target='_blank')),
                html.Li(html.A(children='Ben Hines', href='https://www.linkedin.com/in/ben-hines-426286225/', target='_blank')),
                html.Li(html.A(children='Sargis Abrahamyan', href='https://www.linkedin.com/in/sargis-abrahamyan-1333571a0/', target='_blank')),
                html.Li(html.A(children='Lucas Stefanic', href='https://www.linkedin.com/in/lucas-stefanic-661404212/', target='_blank'))
            ])
        ], style={"font-size": "1.5em"}
        )

    if pathname == "/page-1/1":
        return html.Div([
            html.Div(id='finance-live'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-1/2":
        return historicalStockGraphs('Finance', ['V', 'JPM', 'BAC', 'MA'],
                                     ['VISA', 'JPMorgan Chase', 'Bank of America', 'Mastercard'])

    if pathname == "/page-1/3":
        return html.P("Page 1.3")

    if pathname == "/page-2/1":
        return html.Div([
            html.Div(id='manufacturing-live'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-2/2":
        return historicalStockGraphs('Manufacturing', ['AAPL', 'MSFT', 'MGPI', 'KWR'],
                                     ['Apple', 'Microsoft', 'MGP Ingredients Inc', 'Quaker Chemical Corp'])

    if pathname == "/page-2/3":
        return html.P("Page 2.3")

    if pathname == "/page-3/1":
        return html.Div([
            html.Div(id='information-live'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-3/2":
        return historicalStockGraphs('Information', ['CMCSA', 'VZ', 'T', 'TMUS'],
                                     ['Comcast', 'Verizon', 'AT&T', 'T-Mobile'])

    if pathname == "/page-3/3":
        return html.P("Page 3.3")

    if pathname == "/page-4/1":
        return html.Div([
            html.Div(id='retail-live'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,
                n_intervals=0
            )
        ])

    if pathname == "/page-4/2":
        return historicalStockGraphs('Retail', ['AMZN', 'WMT', 'HD', 'COST'],
                                     ['Amazon', 'Walmart', 'Home Depot', 'Costco'])

    if pathname == "/page-4/3":
        return html.P("Page 4.3")

    if pathname == "/page-5/1":
        return historicalCryptoGraphs('Cryptocurrencies', ['BTC', 'DOGE', 'ETH', 'LTC'],
                                      ['Bitcoin', 'Dogecoin', 'Ethereum', 'Litecoin'])

    if pathname == "/page-5/2":
        return html.P("Crypto vs. Stocks")

    if pathname == "/page-6/1":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"textAlign": "center"}),
            html.Hr(),
            html.Div(
                html.Table(children=[
                    html.Tbody(children=[
                        html.Tr(children=[
                            html.Td(
                                html.H4(children='', style={"textAlign": "center"}),
                            ),
                            html.Td(
                                html.H4(children='', style={"textAlign": "center"}),
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

    if pathname == "/page-6/2":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"textAlign": "center"}),
            html.Hr(),
            html.Div(
                html.Table(children=[
                    html.Tbody(children=[
                        html.Tr(children=[
                            html.Td(
                                html.H4(children='', style={"textAlign": "center"}),
                            ),
                            html.Td(
                                html.H4(children='', style={"textAlign": "center"}),
                            )
                        ]),
                        html.Tr(children=[
                            html.Td(
                                dcc.Graph(
                                    id="ml1 id",
                                    figure=createFigAutoRegCrypto()
                                ),
                            ),
                            html.Td(
                                dcc.Graph(
                                    id="ml1 id",
                                    figure=createFigArimaCrypto()
                                ),
                            )
                        ])

                    ]),

                ], style={"width": "100%", "tableLayout": "fixed"})
            )
        ])

    return dbc.Jumbotron(
        [
            html.H1("404: Not Found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)