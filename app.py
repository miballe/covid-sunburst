import numpy as np
import pandas as pd
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


def industries_hierarchy() -> pd.DataFrame:
    ret_ind = pd.read_csv('industries-hrchy.csv')
    ret_ind = ret_ind.replace(np.nan, '', regex=True)
    return ret_ind


industries_hrchy = industries_hierarchy()
# Replace with real-data calculation
industries_hrchy['value'] = [random.gauss(1, 1) for i in range(industries_hrchy.shape[0])]
# End replacement
industries_hrchy['value'] = industries_hrchy['value'] / (max(abs(industries_hrchy['value'].min()), industries_hrchy['value'].max()) + 0.25)
industry_sentiment = pd.read_json('covidsm_agg_sentiment_industry.json.zip', orient='records')

fig_layout = dict(margin=dict(t=0, l=0, r=0, b=0), width=800, height=850)

fig_ind = go.Figure(data=[go.Sunburst(
        ids=industries_hrchy['ind_fcode'],
        labels=industries_hrchy['name'],
        parents=industries_hrchy['parent'],
        # values=industries_hrchy['values']
        marker=dict(
            colors=industries_hrchy['value'],
            colorscale='RdBu',
            cmid=0
        ),
        hovertemplate='<b>(%{id})</b> %{label} - Sentiment: %{color:.2f}'
    )],
    layout=fig_layout
)

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


@app.callback(
    Output('sunburst-with-slider', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_date):
    # filtered_df = industry_sentiment[industry_sentiment['published_at_date'] == selected_date]

    # fig_ind_layout = dict(margin=dict(t=0, l=0, r=0, b=0), width=600, height=650)

    return go.Figure(data=[go.Sunburst(
                            ids=industries_hrchy['ind_fcode'],
                            labels=industries_hrchy['name'],
                            parents=industries_hrchy['parent'],
                            # values=industries_hrchy['values']
                            marker=dict(
                                colors=industries_hrchy['value'],
                                colorscale='RdBu',
                                cmid=0
                            ),
                            hovertemplate='<b>(%{id})</b> %{label} - Sentiment: %{color:.2f}'
                        )],
                        layout=fig_layout
                    )


if __name__ == '__main__':
    app.run_server(debug=True)
