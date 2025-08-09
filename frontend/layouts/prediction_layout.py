from dash import dcc, dash_table, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from statistics import quantiles

from pathlib import Path



risk_colors = {
    'low': '#28a745',
    'lower than average': '#28a745',
    'average': '#28a745',
    'higher than average': '#ffc107', 
    'high': '#dc3545'
}


def compute_risk_label(risk_percentile):
    if risk_percentile <= 10:
        label = 'low'
    elif 10 < risk_percentile <= 40:
        label = 'lower than average'
    elif 40 < risk_percentile <= 60:
        label = 'average'
    elif 60 < risk_percentile <= 90:
        label = 'higher than average'
    elif 90 < risk_percentile:
        label = 'high'
    else:
        raise ValueError("Invalid risk percentile value")
    return label

def plot_normal_hist(risk, samples, risk_percentile):
    percentiles = quantiles(samples, n=10)
    hist = go.Histogram(
        x=samples,
        histnorm='probability density',
        name='Population average risk scores',
        opacity=0.6
    )
    risk_line = go.Scatter(
        x=[risk, risk],
        y=[0, 0.5],
        mode='lines',
        name='Your Risk',
        line=dict(color='firebrick', dash='dash')
    )
    annotation = dict(
        x=risk,
        y=0.5,
        text=f"<br>Percentile: {risk_percentile:.1f}%",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-40
    )

    histogram_fig = go.Figure(data=[hist, risk_line])
    histogram_fig.update_layout(
        xaxis_title='Risk Score Decile',
        yaxis_title='Density',
        bargap=0.05,
        height=600,
        width=900,
        xaxis=dict(
            tickmode='array',
            ticktext=np.arange(10, 100, 10),
            tickvals=percentiles,
            ticklen=5,
            ticks='outside'),
        yaxis=dict(range=[0, None],
                   ticklen=5,
                   ticks='outside'),
        annotations=[annotation]
    )

    return histogram_fig