from dash import dcc, html



# Components
def sign_in_form():
    return html.Div([
        dcc.Input(id="sign-in-email", type="email", placeholder="Email", autoFocus=True),
        dcc.Input(id="sign-in-password", type="password", placeholder="Password"),
        html.Div([
            html.Button("Sign In", id={'type': 'auth-button', 'action': 'sign-in'}, n_clicks=0),
            html.Button("Sign Up Page", id={'type': 'nav-button', 'index': 'sign-up'}, n_clicks=0)
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})


# Layout
def sign_in_layout():
    return html.Div([
        html.H2("Sign In"),
        sign_in_form(),
        html.Div(id="sign-in-status")
    ], style={'maxWidth': '500px', 'margin': '0 auto', 'padding': '20px'})
