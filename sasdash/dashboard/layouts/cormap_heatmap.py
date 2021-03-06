from __future__ import print_function, division

import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from .style import GRAPH_GLOBAL_CONFIG, INLINE_LABEL_STYLE
from ..base import dash_app

from sasdash.datamodel import warehouse

_PLOT_OPTIONS = [{
    'label': 'Adj Pr(>C) value',
    'value': 'adj Pr(>C)',
}, {
    'label': 'C value',
    'value': 'C',
}]

_DEFAULT_LAYOUT = html.Div(children=[
    dcc.Graph(
        id='cormap-heatmap-graph',
        figure={'data': ()},
        config=GRAPH_GLOBAL_CONFIG,
    ),
    html.Label('Plot type'),
    dcc.RadioItems(
        id='cormap-heatmap-plot-type',
        options=_PLOT_OPTIONS,
        value='adj Pr(>C)',
        labelStyle=INLINE_LABEL_STYLE,
    ),
])


def get_cormap_heatmap():
    return _DEFAULT_LAYOUT


_DEFAULT_FIGURE_LAYOUT = {
    'height': 550,
    'hovermode': 'closest',
    'title': 'CorMap Heatmap',
    'xaxis': dict(title='Frames', scaleanchor='y', constrain='domain'),
    'yaxis': dict(title='Frames', autorange='reversed'),
}


@dash_app.callback(
    Output('cormap-heatmap-graph', 'figure'),
    [
        Input('cormap-heatmap-plot-type', 'value'),
        Input('page-info', 'children'),
    ],
)
def _update_figure(plot_type, info_json):
    info = json.loads(info_json)
    info_tuple = info['project'], info['experiment'], info['run']
    cormap_heatmap = warehouse.get_cormap_heatmap(*info_tuple, plot_type)

    if plot_type == 'C':
        colorscale = 'Jet'
        colorbar = dict()
    else:
        p_threshold = 0.01  # default
        colorscale = (
            (0.0, "#D55E00"),  # orange
            (p_threshold, "#D55E00"),
            (p_threshold, "#009E73"),  # green
            (1.0 - 1e-8, "#009E73"),
            (1.0, "#0072B2"),  # blue
        )
        colorbar = dict(
            tickmode='array',
            tickvals=(0, (p_threshold + 1.0) / 2.0, 1.0),
            ticktext=(
                'adj Pr(>C) < 0.01',
                '0.01 <= adj Pr(>C) < 1',
                'adj Pr(>C) == 1',
            ),
        )
    return {
        'data': [{
            'type': 'heatmap',
            'z': cormap_heatmap,
            'colorscale': colorscale,
            'colorbar': colorbar,
        }],
        'layout': _DEFAULT_FIGURE_LAYOUT,
    } # yapf: disable
