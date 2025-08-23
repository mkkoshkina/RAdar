from dash import dcc, html

from frontend.ui_kit.styles import text_style, heading2_style, primary_button_style, secondary_button_style, input_style
from frontend.utils.i18n import t

# Updated Input Style for Consistency
updated_input_style = {**input_style, 'marginBottom': '15px', 'width': '100%'}


# Components
def sign_up_form(lang: str = 'en'):
    return html.Div([
        dcc.Input(id="sign-up-email", type="email", placeholder=t("email", lang), autoFocus=True, style=updated_input_style),
        dcc.Input(id="sign-up-password", type="password", placeholder=t("password", lang), style=updated_input_style),
        dcc.Input(id="sign-up-name", type="text", placeholder=t("name", lang), style=updated_input_style),
        html.Div([
            html.Button(t("sign_up", lang), id={'type': 'auth-button', 'action': 'sign-up'}, n_clicks=0,
                        style=primary_button_style),
            html.Button(t("sign_in_page", lang), id={'type': 'nav-button', 'index': 'sign-in'}, n_clicks=0,
                        style=secondary_button_style)
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})


# Layout
def sign_up_layout(lang: str = 'en'):
    return html.Div([
        html.H2(t("sign_up", lang), style=heading2_style),
        sign_up_form(lang),
        html.Div(id="sign-up-status", style=text_style)
    ], style={'maxWidth': '500px', 'margin': '0 auto', 'padding': '20px'})
