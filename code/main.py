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


database = "group3-DB"
table = "dbo.rtstock"
username = "group3_user"
password = "K-qC4SoI_oUvepg"
server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"

conn = pymssql.connect(server, username, password, database)


def getData(table):
    server = "gen10-data-fundamentals-21-11-sql-server.database.windows.net"
    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor()
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)
    return df


def createHistStock(ticker, title):

    table = "dbo.hstock"

    df = getData(table)
    df2 = df[df["Ticker"] == ticker]
    df2.sort_values(by=['Date'], inplace=True)

    df2 = df2[df2['Date'] >= datetime(2021, 9, 21, 0, 0, 0, 0).date()]
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_layout(
        {
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)'
        },
        title=f"{title} ({ticker})",
        yaxis_title='Volume',

    )

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
    fig.update_yaxes(title_text="Price ($)", secondary_y=True)
    return fig


def createHistCrypto(currency, title):

    table = "dbo.hcrypto"

    df = getData(table)
    df2 = df[df["Currency"] == currency]
    df2.sort_values(by=['Date'], inplace=True)

    df2 = df2[df2['Date'] >= datetime(2021, 9, 21, 0, 0, 0, 0).date()]


    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(name="Volume", x=df2['Date'], y=df2['Volume'], opacity=0.5), secondary_y=False)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'
        },
        title=f"{title} ({currency})",
        yaxis_title='Volume',
    )
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
    fig.update_yaxes(title_text="Price ($)", secondary_y=True)
    return fig


def createFig(table, ticker, title):
    df = getData(table)
    df2 = df[df["Ticker"] == ticker]
    df2.sort_values(by=['Time'], inplace=True)
    fig = px.line(df2, x="Time", y="Current Price", title=f"{title} ({ticker})")

    return fig


def createFigArima():

    table = "dbo.hstock"

    hst_df = getData(table)

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
        title="AAPL ARIMA Model Predictions",
        xaxis_title="Date Index",
        yaxis_title="Price ($)",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createFigAutoReg():

    table = "dbo.hstock"

    hst_df = getData(table)

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
        xaxis_title="Date Index",
        yaxis_title="Price ($)",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createFigAutoRegCrypto():

    table = "dbo.hcrypto"

    hcr_df = getData(table)

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
        xaxis_title="Date Index",
        yaxis_title="Price ($)",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createFigArimaCrypto():

    table = "dbo.hcrypto"

    hcr_df = getData(table)

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
        title="BTC ARIMA Model Predictions",
        xaxis_title="Date Index",
        yaxis_title="Price ($)",
        legend_title="",
        font=dict(
            size=18,
        )
    )
    return fig


def createIndustryGraph(table, x_axis, title, data):

    df = getData(table)
    df["Number_of_Establishments"] = pd.to_numeric(df["Number_of_Establishments"])
    df["Sales_Shipment_or_Revenue"] = pd.to_numeric(df["Sales_Shipment_or_Revenue"])

    df2 = df[df["NAICS_Code_Meaning"].isin(data)]

    fig = px.bar(df2, y="NAICS_Code_Meaning", x=x_axis, title=f"{title}", orientation='h',
                 labels={
                     "NAICS_Code_Meaning": "Industry",
                     "Number_of_Establishments": "Number of Establishments",
                     "Sales_Shipment_or_Revenue": "Sales Shipment or Revenue ($1000)"
                 },
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
    "width": "20rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
    "overflowY": "scroll"
}
# The styles for the main contnet position it to the rigth of the sidebar and add some padding
CONTENT_STYLE = {
    "marginLeft": "21rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}
HOMELINK_STYLE = {
    "width": "17rem",
    "fontSize": "2.7rem",
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

submenu_7 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Industry Data"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-7",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("General", href="/page-7/1"),
            dbc.NavLink("Subcategories", href="/page-7/2"),
        ],
        id="submenu-7-collapse",
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

        dbc.Nav(submenu_1 + submenu_2 + submenu_3 + submenu_4 + submenu_5 + submenu_6 + submenu_7, vertical=True),
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


for i in range(1, 8):
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
        html.H4(children="Live data", style={"textAlign": "center"}),
        html.Hr(),
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
        html.H4(children="Live data", style={"textAlign": "center"}),
        html.Hr(),
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
        html.H4(children="Live data", style={"textAlign": "center"}),
        html.Hr(),
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
        html.H4(children="Live data", style={"textAlign": "center"}),
        html.Hr(),
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
        html.H4(children="Since September 21, 2021", style={"textAlign": "center"}),
        html.Hr(),
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
        html.H4(children="Since September 21, 2021", style={"textAlign": "center"}),
        html.Hr(),
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


def industryData(table, data):
    return html.Div(children=[
        html.H1(children="Industry Data", style={"textAlign": "center"}),
        html.Hr(),
        html.Table(children=[
            html.Tbody(
                children=[
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createIndustryGraph(table, "Number_of_Establishments", "Number of Establishments by Industry Group", data)
                            )
                        ),
                    ],
                    ),
                    html.Tr(children=[
                        html.Td(
                            dcc.Graph(
                                figure=createIndustryGraph(table, "Sales_Shipment_or_Revenue", "Sales Shipment or Revenue by Industry Group", data)
                            )
                        ),
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
            html.H1(children="Stocks vs. Cryptocurrencies", style={"textAlign": "center"}),
            html.Hr(),
            html.P(children="This dashboard visualizes live streaming data on 16 differents stocks in 4 different industries, as well as historical data for those stocks and 4 different cryptocurrencies. It also takes a look at machine learning predictions for stocks and crypto and shows economic data for the industries. Use the sidebar on the left to explore!", style={"marginTop": "50px"}),
            html.P(children="Our group:", style={"marginTop": "50px"}),
            html.Ul([
                html.Li(html.A(children='Connor Buxton', href='https://www.linkedin.com/in/connor-buxton-748103181/', target='_blank')),
                html.Li(html.A(children='Ben Hines', href='https://www.linkedin.com/in/ben-hines-426286225/', target='_blank')),
                html.Li(html.A(children='Sargis Abrahamyan', href='https://www.linkedin.com/in/sargis-abrahamyan-1333571a0/', target='_blank')),
                html.Li(html.A(children='Lucas Stefanic', href='https://www.linkedin.com/in/lucas-stefanic-661404212/', target='_blank'))
            ]),
            html.Footer([
                html.Div(["Data sources",
                html.Div(html.A(children='Alpha Vantage API', href='https://www.alphavantage.co', target='_blank')),
                html.Div(html.A(children='Finnhub Stock API', href='https://finnhub.io/', target='_blank')),
                html.Div(html.A(children='US Economic Census', href='https://data.census.gov/cedsci/table?q=ECNNAPCSIND2017.EC1700NAPCSINDPRD ', target='_blank')),
                ],

                style={
                    "position": "absolute",
                    "bottom": "0",
                    "right": "0",
                    "margin": "1rem",
                    "textAlign": "right",
                    "font-size": "1rem",
                }
            )])
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

    if pathname == "/page-5/1":
        return historicalCryptoGraphs('Cryptocurrencies', ['BTC', 'DOGE', 'ETH', 'LTC'],
                                      ['Bitcoin', 'Dogecoin', 'Ethereum', 'Litecoin'])

    if pathname == "/page-6/1":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"textAlign": "center"}),
            html.H4(children='Stocks', style={"textAlign": "center"}),
            html.Hr(),
            html.Div([
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

                ], style={"width": "100%", "tableLayout": "fixed"}),
                html.Div([
                    html.Li("Grid Search was used to locate parameters which increase accuracy"),
                    html.Li("Stock market and cryptocurrency data proved too volatile to provide the algorithms with a pattern to latch onto"),
                    html.Li("Attempted to experiment with order hyperparameters, but no significant change in results"),
                    ]
                )
            ]
            )
        ])

    if pathname == "/page-6/2":
        return html.Div(children=[
            html.H1(children='Machine Learning', style={"textAlign": "center"}),
            html.H4(children='Cryptocurrency', style={"textAlign": "center"}),
            html.Hr(),
            html.Div([
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

                ], style={"width": "100%", "tableLayout": "fixed"}),
                html.Div([
                    html.Li("Grid Search was used to locate parameters which increase accuracy"),
                    html.Li("Stock market and cryptocurrency data proved too volatile to provide the algorithms with a pattern to latch onto"),
                    html.Li("Attempted to experiment with order hyperparameters, but no significant change in results"),
                ])
                ]
            )
        ])
    if pathname == "/page-7/1":
        return industryData("dbo.census", ["Manufacturing", "Finance and insurance", "Retail trade", "Information"])
    if pathname == "/page-7/2":
        return industryData("dbo.census", ["Grain and oilseed milling", "Distilleries", "Electronic computer manufacturing", "Commercial banking", "Credit card issuing"])


    return dbc.Jumbotron(
        [
            html.H1("404: Not Found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)