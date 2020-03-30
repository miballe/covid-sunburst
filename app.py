import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


# --- Start --- Reading base data for the Sunburst
def get_industries_hierarchy() -> pd.DataFrame:
    ret_ind = pd.read_csv('industries-hrchy.csv')
    ret_ind = ret_ind.replace(np.nan, '', regex=True)
    return ret_ind


industry_sentiment = pd.read_json('covidsm_agg_sentiment_industry.json.zip', orient='records')
industries_hrchy = get_industries_hierarchy()
# --- End --- Reading base data for the Sunburst

# --- Start --- Load base Sunburst (no data)
fig_layout = dict(margin=dict(t=0, l=0, r=0, b=0), width=800, height=850)
fig_ind = go.Figure(data=[go.Sunburst(
        ids=['total'],
        labels=['total'],
        parents=[''],
        marker=dict(colors=[0], colorscale='RdBu', cmid=0),
        hovertemplate='<b>(%{id})</b> %{label} <br>- Sentiment score: %{color:.2f}'
    )],
    layout=fig_layout
)
# --- End --- Load base Sunburst (no data)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Graph(id='sunburst-with-slider', figure=fig_ind),
    dcc.Slider(
        id='day-slider',
        min=1,
        max=71,
        value=1,
        marks={i: '{}'.format(i) for i in range(71)}
    )
])


# --- Start --- Sunburst Callback
@app.callback(
    Output('sunburst-with-slider', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_date):
    # Line that filters by sentiment dataset by date
    filtered_hrchy = industries_hrchy.copy()  # Line that filters hierarchy to only items with sentiment
    # TODO: Fix the root item by adding data
    sentiment_avgs = industry_sentiment.groupby(['industry_code'], as_index=False).agg({'sentiment': 'mean'})
    ind_with_sentiment = sentiment_avgs['industry_code'].to_list()
    filtered_hrchy = industries_hrchy[industries_hrchy['ind_fcode'].isin(ind_with_sentiment)]
    filtered_hrchy = filtered_hrchy.merge(sentiment_avgs, left_on='ind_fcode', right_on='industry_code')

    return go.Figure(data=[go.Sunburst(
                            ids=filtered_hrchy['ind_fcode'],
                            labels=filtered_hrchy['name'],
                            parents=filtered_hrchy['parent'],
                            marker=dict(colors=filtered_hrchy['sentiment'], colorscale='RdBu', cmid=0),
                            hovertemplate='<b>(%{id})</b> %{label} <br>- Sentiment score: %{color:.2f}'
                        )],
                        layout=fig_layout
                    )
# --- End --- Sunburst Callback


if __name__ == '__main__':
    app.run_server(debug=True)
