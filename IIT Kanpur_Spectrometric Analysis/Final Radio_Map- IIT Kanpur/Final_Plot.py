import dash
import dash_leaflet as dl
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
import seaborn as sns
import numpy as np

#Enter location of the csv file containing all locations (with Latitude and Longitude)
locations_df = pd.read_csv(r'D:\Project-Simulation of the nightsky\TinySA\Interactive_dash_plots\final_csv\locations.csv')

app = dash.Dash(__name__)
server = app.server
markers = [
    dl.Marker(id=f"marker-{index}", position=[row["Latitude"], row["Longitude"]], children=[
        dl.Tooltip(row["Location"])
    ])
    for index, row in locations_df.iterrows()
]
app.layout = html.Div([
    html.Div([
        dl.Map(center=[26.5123, 80.2321], zoom=15, children=[
            dl.TileLayer(
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                maxZoom=18
            ),
            dl.LayerGroup(markers, id="markers")
        ], style={'height': '100vh', 'width': '50vw', 'position': 'fixed'}),
    ], style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top'}),
    
    html.Div([
        html.Div(id="graph-container", style={'width': '100%', 'padding-top': '0px', 'margin-top': '0px'})
    ], style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top'})
])
@app.callback(
    Output('graph-container', 'children'),
    [Input(f"marker-{index}", 'n_clicks') for index in range(len(locations_df))]
)
def update_graph(*args):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dcc.Graph()

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = int(button_id.split('-')[1])
    location = locations_df.iloc[index]
    location_name = location['Location']
    
    # Loading CSV (of each location as per 'Location' column of locations.csv file)
    csv_running_df = pd.read_csv(f"D:/Project-Simulation of the nightsky/TinySA/Interactive_dash_plots/final_csv/{location_name}.csv")
    csv_running_df['Magnitude (Log Mag dB)'] = pd.to_numeric(csv_running_df['Magnitude (Log Mag dB)'], errors='coerce')
    csv_running_df.dropna(inplace=True)

    #### PLOTLY LINE CHART  ####
    fig_plotly = go.Figure(data=[go.Scatter(x=csv_running_df['Frequency (Hz)'], y=csv_running_df['Magnitude (Log Mag dB)'], mode='lines', line=dict(width=0.5, color='blue'))])
    fig_plotly.update_layout(title=f'{location_name} - Frequency vs Magnitude', xaxis_title='Frequency (Hz)', yaxis_title='Magnitude (Log Mag dB)', 
                              plot_bgcolor='rgba(135, 206, 235, 0.5)', paper_bgcolor='rgba(231, 84, 128, 0.1)')

    ### STATS BOX ###
    stats = csv_running_df['Magnitude (Log Mag dB)'].describe()
    stat_box = html.Div([
        html.P(f"Count: {stats['count']:.2f}"),
        html.P(f"Mean: {stats['mean']:.2f}"),
        html.P(f"Standard Deviation: {stats['std']:.2f}"),
        html.P(f"Minimum: {stats['min']:.2f}"),
        html.P(f"25%: {stats['25%']:.2f}"),
        html.P(f"50%: {stats['50%']:.2f}"),
        html.P(f"75%: {stats['75%']:.2f}"),
        html.P(f"Maximum: {stats['max']:.2f}")
    ], style={'padding': '10px', 'backgroundColor': 'lightgray', 'margin': '10px'})

    #### k-MEANS CLUSTERING GRAPH ####
    scaler = StandardScaler()
    csv_running_df_scaled = scaler.fit_transform(csv_running_df[['Frequency (Hz)', 'Magnitude (Log Mag dB)']])
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(csv_running_df_scaled)
    labels = kmeans.labels_
    fig_kmeans = px.scatter(x=csv_running_df['Frequency (Hz)'], y=csv_running_df['Magnitude (Log Mag dB)'], color=labels, title='K-Means Clustering with 3 Clusters', labels={"x": "Frequency (Hz)", "y": "Magnitude (Log Mag dB)"})

    #### DENSITY PLOT - HISTOGRAM AND CURVE ###
    mean_value = csv_running_df['Magnitude (Log Mag dB)'].mean()
    fig_density = go.Figure()
    fig_density.add_trace(go.Histogram(x=csv_running_df['Magnitude (Log Mag dB)'], nbinsx=30, histnorm='density', name='Histogram'))
    kde_x = np.linspace(csv_running_df['Magnitude (Log Mag dB)'].min(), csv_running_df['Magnitude (Log Mag dB)'].max(), 200)
    kde_y = sns.kdeplot(csv_running_df['Magnitude (Log Mag dB)'], bw_adjust=1).get_lines()[0].get_data()
    fig_density.add_trace(go.Scatter(x=kde_x, y=kde_y[1], mode='lines', name='Density Curve'))
    fig_density.add_vline(x=mean_value, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_value:.2f}", annotation_position="top left")

    fig_density.update_layout(title=f'{location_name} - Density Plot with Mean and Curve', xaxis_title='Magnitude (Log Mag dB)', yaxis_title='Density', 
                              plot_bgcolor='rgba(135, 206, 235, 0.5)', paper_bgcolor='rgba(231, 84, 128, 0.1)')


    #### MANAGING ALL PLOTS ####
    graphs = html.Div([
        dcc.Graph(figure=fig_plotly, style={'height': '400px'}),
        stat_box,
        dcc.Graph(figure=fig_kmeans, style={'height': '400px'}),
        dcc.Graph(figure=fig_density, style={'height': '400px'})
    ], style={'display': 'grid', 'grid-template-columns': '1fr', 'gap': '20px', 'padding-top': '0px', 'margin-top': '0px'})

    return graphs

if __name__ == '__main__':
    app.run_server(port=8052)


