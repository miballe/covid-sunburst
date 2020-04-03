import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

global_ndays_range = 20

# --- Start --- Reading base data for the Sunburst
industry_sentiment = pd.read_json('covidsm_agg_sentiment_industry.json.zip', orient='records')
industry_sentiment['published_at_date'] = pd.to_datetime(industry_sentiment['published_at_date'], unit='ms')
global_start_day = industry_sentiment['published_at_date'].max() - pd.DateOffset(days=global_ndays_range)
industries_hrchy = pd.read_csv('industries-hrchy.csv')
industries_hrchy = industries_hrchy.replace(np.nan, '', regex=True)
# --- End --- Reading base data for the Sunburst


# --- Start --- Load base Sunburst (no data)
fig_layout = dict(margin=dict(t=0, l=0, r=0, b=0), width=800, height=850)
fig_ind = go.Figure(data=[go.Sunburst(
        ids=['total'],
        labels=['All Industries'],
        parents=[''],
        marker=dict(colors=[0], colorscale='RdBu', cmid=0),
        hovertemplate='<b>(%{id})</b> %{label} <br>- Sentiment score: %{color:.2f}'
    )],
    layout=fig_layout
)
# --- End --- Load base Sunburst (no data)


slider_dates = pd.Series(industry_sentiment[industry_sentiment['published_at_date'] >= global_start_day]['published_at_date'].unique()).sort_values(ignore_index=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Graph(id='sunburst-with-slider', figure=fig_ind),
    dcc.Slider(
        id='day-slider',
        min=1,
        max=global_ndays_range,
        value=1,
        # marks={0: {'label': '{}'.format(slider_dates.iloc[dayix].strftime('%Y-%b-%d')),
        #        'style': {'transform': 'rotate(45deg)'}} for dayix in slider_dates.index}
        marks={ixday: {'label': '{}'.format(slider_dates.iloc[ixday].strftime('%d-%b')),
                       'style': {'transform': 'rotate(-45deg)', 'margin-top': 10, 'margin-left': -20}
                      } for ixday in slider_dates.index}
    )
])


# --- Start --- Sunburst Callback
@app.callback(
    Output('sunburst-with-slider', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_date):
    end_date = global_start_day + pd.DateOffset(days=selected_date)
    start_date = end_date + pd.DateOffset(days=-5)
    filtered_sentiment = industry_sentiment[(industry_sentiment['published_at_date'] >= start_date) & (industry_sentiment['published_at_date'] <= end_date)]
    # filtered_hrchy = industries_hrchy.copy()
    sentiment_avgs = filtered_sentiment.groupby(['industry_code'], as_index=False).agg({'sentiment': 'mean'})
    ind_with_sentiment = sentiment_avgs['industry_code'].to_list()
    filtered_hrchy = industries_hrchy[industries_hrchy['ind_fcode'].isin(ind_with_sentiment)]
    filtered_hrchy = filtered_hrchy.merge(sentiment_avgs, left_on='ind_fcode', right_on='industry_code')
    root_item_list = ['indroot', 'All Industries', '', 'indroot', filtered_hrchy[filtered_hrchy['parent'] == 'indroot']['sentiment'].mean()]
    root_item_df = pd.DataFrame([root_item_list], columns=['ind_fcode', 'name', 'parent', 'industry_code', 'sentiment'])
    filtered_hrchy = filtered_hrchy.append(root_item_df, ignore_index=True)

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
