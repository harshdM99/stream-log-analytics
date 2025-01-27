import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from cassandra.cluster import Cluster
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
import pandas as pd
import configparser
import datetime 

# Configuration
config = configparser.ConfigParser()
config.read('config.py')

USERNAME = config['CREDENTIALS']['Username']
PASSWD = config['CREDENTIALS']['Password']
CERT = config['CREDENTIALS']['Cert']
KEYSPACE = config['KEYSPACES']['Keyspace']
TABLE = config['KEYSPACES']['Table']

# Setup Cassandra connection
ssl_context = SSLContext(PROTOCOL_TLSv1_2)
ssl_context.load_verify_locations(CERT)
ssl_context.verify_mode = CERT_REQUIRED
auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWD)

cluster = Cluster(['cassandra.us-east-1.amazonaws.com'], ssl_context=ssl_context, auth_provider=auth_provider, port=9142)
session = cluster.connect()
session.set_keyspace(KEYSPACE)

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time Log Analytics Dashboard"),
    dcc.Graph(id='latency-trend'),          # Line chart for latency trend
    dcc.Graph(id='request-time-series'),    # Time series for request counts
    dcc.Graph(id='method-bar-chart'),       # Bar chart for HTTP method counts
    dcc.Graph(id='url-bar-chart'),          # Bar chart for most accessed URLs
    dcc.Graph(id='error-pie-chart'),        # Pie chart for error responses
    html.Div(id='live-update-table'),       # Table for recent logs
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # 10 seconds
        n_intervals=0
    )
])

# Helper function to fetch data from Cassandra
def fetch_data():
    now = datetime.datetime.now(datetime.timezone.utc)
    current_minute_bucket = now.strftime("%Y-%m-%d-%H-%M")  # Current minute
    # TODO: REMOVE LATER
    # current_minute_bucket = "2025-01-23-02-54"
    
    query = f"""
    SELECT * FROM log_analytics.logs_table
    WHERE time_bucket = '{current_minute_bucket}'
    ORDER BY time DESC
    """
    print("TRIGGER : QUERYING CASSANDRA")
    rows = session.execute(query)
    data = pd.DataFrame(rows.current_rows)

    return data

# Callback to update visualizations
@app.callback(
    [Output('latency-trend', 'figure'),
     Output('request-time-series', 'figure'),
     Output('method-bar-chart', 'figure'),
     Output('url-bar-chart', 'figure'),
     Output('error-pie-chart', 'figure'),
     Output('live-update-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n_intervals):
    # Fetch the latest data
    df = fetch_data()

    try:
        # Ensure columns have the correct data types
        df['time'] = pd.to_datetime(df['time'])
        df['latency'] = pd.to_numeric(df['latency'], errors='coerce')

        # Latency Trend
        latency_fig = px.line(
            df,
            x='time',
            y='latency',
            title="Latency Trend Over Time"
        )

        # Time Series for Requests
        df['time_minute'] = df['time'].dt.floor('T')  # Round to minute
        requests_over_time = df.groupby(['time_minute', 'method']).size().reset_index(name='count')
        time_series_fig = px.line(
            requests_over_time,
            x='time_minute',
            y='count',
            color='method',
            title="Requests Over Time by HTTP Method"
        )

        # HTTP Method Count
        method_fig = px.bar(
            df['method'].value_counts().reset_index(),
            x='method',
        y='count',
        title="HTTP Method Count",
        labels={'index': 'HTTP Method', 'method': 'Count'}
        )

        # Top Accessed URLs
        url_count = df['url'].value_counts().reset_index()
        url_count.columns = ['url', 'count']
        url_bar_fig = px.bar(
            url_count.head(10),
            x='url',
            y='count',
            title="Top 10 Most Accessed URLs"
        )

        # Error Responses
        error_counts = df[df['response'].astype(int) >= 400]['response'].value_counts().reset_index()
        error_counts.columns = ['response', 'count']
        error_pie_fig = px.pie(
            error_counts,
            names='response',
            values='count',
            title="Error Response Code Distribution"
        )

        # Recent Logs Table
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([
                html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(len(df), 10))
            ])
        ])
    
    except Exception as e:
        print("Failed due to : ", e)
    
    return latency_fig, time_series_fig, method_fig, url_bar_fig, error_pie_fig, table


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
