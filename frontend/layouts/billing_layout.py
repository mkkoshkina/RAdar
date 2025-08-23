from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Group

from frontend.data.remote_data import fetch_transaction_history, fetch_user_balance
from frontend.ui_kit.components.user_balance import user_balance
from frontend.ui_kit.styles import table_style, table_header_style, table_cell_style, primary_button_style, \
    text_style, input_style
from frontend.ui_kit.utils import format_timestamp
from frontend.utils.i18n import t


# Components
def deposit_form(lang: str = 'en'):
    return html.Div([
        dcc.Input(
            id="deposit-amount",
            type="number",
            placeholder=t("amount", lang),
            value="",
            style=input_style
        ),
        html.Button(
            t("deposit", lang),
            id="deposit-button",
            n_clicks=0,
            style=primary_button_style
        ),
    ], style={'display': 'flex', 'alignItems': 'center'})


def transaction_history_table(transactions, lang: str = 'en'):
    data = [{"id": txn["id"],
             "amount": txn["amount"],
             "timestamp": format_timestamp(txn["timestamp"])} for txn in transactions]
    if not data:
        return html.Div(t("no_transactions", lang), style=text_style)

    columns = [
        {"name": t("amount", lang), "id": "amount", "type": "numeric", "format": Format(group=Group.yes)},
        {"name": t("timestamp", lang), "id": "timestamp"}
    ]

    return dash_table.DataTable(
        columns=columns,
        data=data,
        style_table=table_style,
        style_cell=table_cell_style,
        style_header=table_header_style
    )


# Layout
def billing_layout(user_session, lang: str = 'en'):
    transactions = fetch_transaction_history(user_session=user_session)
    balance = fetch_user_balance(user_session)
    return html.Div([
        html.Div(user_balance(balance), id='current-balance-billing'),
        deposit_form(lang),
        html.Div(transaction_history_table(transactions, lang), id='transaction-history-table'),
    ])
