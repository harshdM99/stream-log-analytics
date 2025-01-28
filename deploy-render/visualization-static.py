import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from datetime import datetime, timezone

# Fetch data from local
# df = pd.read_csv("c:/Users/Work/Desktop/NEW PROJECTS 2024/data engg projs/log analytics/visualization/sample-data.csv")

# Fetch data from render server
df = pd.read_csv("sample-data.csv")

try:
    # Ensure columns have the correct data types
    df['time'] = pd.to_datetime(df['time'])
    cutoff_datetime = datetime(2025, 1, 23, 21, 0, tzinfo=timezone.utc)
    df = df[df['time'] >= cutoff_datetime]

    df['time_minute'] = df['time'].dt.floor('T')  # Round to minute
    df.set_index('time', inplace=True)
    latency_resampled = df['latency'].resample('T').mean()  # 'T' for 1 minute

    # Latency Trend
    latency_fig = px.line(
        latency_resampled,
        x=latency_resampled.index,
        y=latency_resampled,
        title="Latency Trend (Per-Minute Average)"
    )
    latency_fig.update_layout(
        xaxis_title="Time (minutes)",
        yaxis_title="Average Latency (ms)"
    )

    # Time Series for Requests
    requests_over_time = df.groupby(['time_minute', 'method']).size().reset_index(name='count')
    time_series_fig = px.line(
        requests_over_time,
        x='time_minute',
        y='count',
        color='method',
        title="Requests by Method Over Time"
    )
    time_series_fig.update_layout(
        xaxis_title="Time (minutes)",
        yaxis_title="Request Count"
    )

    # HTTP Method Count
    method_count = df['method'].value_counts().reset_index()
    method_count.columns = ['method', 'count']
    method_fig = px.bar(
        method_count,
        x='method',
        y='count',
        title="Distribution of HTTP Methods",
        color='method'
    )
    method_fig.update_layout(
        xaxis_title="HTTP Method",
        yaxis_title="Count"
    )

    # Top Accessed URLs
    url_count = df['url'].value_counts().reset_index()
    url_count.columns = ['url', 'count']
    url_bar_fig = px.bar(
        url_count.head(5),
        x='url',
        y='count',
        title="Top 5 Most Accessed URLs", 
        color='url'
    )
    url_bar_fig.update_layout(
        xaxis_title="URL",
        yaxis_title="Access Count"
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

except Exception as e:
    print("Failed due to: ", e)
    latency_fig = time_series_fig = method_fig = url_bar_fig = error_pie_fig = None
    table = html.Div("Error loading data.")

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    # Main title and note about static data
    html.H1("Real-Time Log Analytics Dashboard", style={
        'textAlign': 'center',
        'font-size': '2.5rem',
        'font-weight': 'bold',
        'margin-bottom': '20px',
        'color': '#333'  # Dark grey color for a professional look
    }),
    html.P("Note: This visualization is just for demonstration purpose based on a static file.", style={
        'textAlign': 'center',
        'font-size': '1rem',
        'color': '#555',  # Lighter grey for less emphasis
        'margin-bottom': '20px'
    }),

    # Links for architecture diagram and GitHub
    html.Div([
        html.A('View Architecture Diagram', href='https://github.com/harshdM99/stream-log-analytics/blob/master/log-project-architecture.png', target='_blank', style={
            'font-size': '1rem',
            'color': '#007bff',
            'text-decoration': 'none',
            'margin-right': '15px'
        }),
        html.A('Visit GitHub Project Page', href='https://github.com/harshdM99/stream-log-analytics/tree/master', target='_blank', style={
            'font-size': '1rem',
            'color': '#007bff',
            'text-decoration': 'none'
        })
    ], style={
        'textAlign': 'center',
        'margin-bottom': '30px',
        'font-weight': 'bold'
    }),

    # Side-by-side layout for the first set of graphs
    html.Div([
        dcc.Graph(figure=latency_fig, style={'flex': 1, 'max-width': '50%'}),
        dcc.Graph(figure=time_series_fig, style={'flex': 1, 'max-width': '50%'})
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}), 

    # Side-by-side layout for the second set of graphs
    html.Div([
        dcc.Graph(figure=method_fig, style={'flex': 1, 'max-width': '50%'}),
        dcc.Graph(figure=error_pie_fig, style={'flex': 1, 'max-width': '50%'})
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}), 

    dcc.Graph(figure=url_bar_fig),  # Pie chart for error responses
])

# Run on render
server = app.server

# Run the Dash app on local
# if __name__ == '__main__':
#     app.run_server(debug=True, host='0.0.0.0', port=8080)