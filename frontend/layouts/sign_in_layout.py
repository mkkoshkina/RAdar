from dash import dcc, html

from frontend.ui_kit.styles import text_style, heading2_style, primary_button_style, secondary_button_style, input_style
from frontend.utils.i18n import t

# Updated Input Style for Consistency
updated_input_style = {**input_style, 'marginBottom': '15px', 'width': '100%'}


# Components
def sign_in_form(lang: str = 'en'):
    return html.Div([
        dcc.Input(id="sign-in-email", type="email", placeholder=t("email", lang), autoFocus=True, style=updated_input_style),
        dcc.Input(id="sign-in-password", type="password", placeholder=t("password", lang), style=updated_input_style),
        html.Div([
            html.Button(t("sign_in", lang), id={'type': 'auth-button', 'action': 'sign-in'}, n_clicks=0,
                        style=primary_button_style),
            html.Button(t("sign_up_page", lang), id={'type': 'nav-button', 'index': 'sign-up'}, n_clicks=0,
                        style=secondary_button_style)
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})


# Layout
def sign_in_layout(lang: str = 'en'):
    return html.Div([
        html.H2(t("sign_in", lang), style=heading2_style),
        sign_in_form(lang),
        html.Div(id="sign-in-status", style=text_style)
    ], style={'maxWidth': '500px', 'margin': '0 auto', 'padding': '20px'})
