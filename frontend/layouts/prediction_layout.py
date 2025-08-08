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