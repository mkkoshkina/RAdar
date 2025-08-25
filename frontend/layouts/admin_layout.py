from dash import html, dash_table
from dash.dash_table.Format import Format, Group

from frontend.ui_kit.styles import table_style, table_header_style, table_cell_style, secondary_button_style, \
    text_style
from frontend.utils.i18n import t


# Components
def users_report(data, lang: str = 'en'):
    if not data:
        return html.Div(t("no_users_info", lang), style=text_style)

    columns = [
        {'name': t('active_users', lang), 'id': 'active_users', 'type': 'numeric'},
    ]

    data_array = [data]
    return dash_table.DataTable(columns=columns, data=data_array, style_table=table_style,
                                style_cell=table_cell_style,
                                style_header=table_header_style)


def predictions_report(data, lang: str = 'en'):
    if not data:
        return html.Div(t("no_predictions_info", lang), style=text_style)

    columns = [
        {'name': t('model_name', lang), 'id': 'model_name'},
        {'name': t('total_predictions', lang), 'id': 'total_prediction_batches', 'type': 'numeric',
         'format': Format(group=Group.yes)}
    ]
    return dash_table.DataTable(columns=columns, data=data, style_table=table_style,
                                style_cell=table_cell_style,
                                style_header=table_header_style)


def credits_report(data, lang: str = 'en'):
    if not data:
        return html.Div(t("no_credits_info", lang), style=text_style)

    columns = [
        {'name': t('total_credits_purchased', lang), 'id': 'total_credits_purchased', 'type': 'numeric'},
        {'name': t('total_credits_spent', lang), 'id': 'total_credits_spent', 'type': 'numeric'}
    ]

    data_array = [data]
    return dash_table.DataTable(columns=columns, data=data_array, style_table=table_style,
                                style_cell=table_cell_style,
                                style_header=table_header_style)


# Layout
def admin_layout(lang: str = 'en'):
    return html.Div(id='admin-page', children=[
        html.Div(id='users-report-div', children=users_report({}, lang)),
        html.Div(id='predictions-report-div', children=predictions_report([], lang)),
        html.Div(id='credits-report-div', children=credits_report({}, lang)),
        html.Button(t("refresh_data", lang), id="refresh-button", n_clicks=0,
                    style={**secondary_button_style, 'display': 'block', 'margin': '0 auto', 'marginTop': '20px'}),
    ])
