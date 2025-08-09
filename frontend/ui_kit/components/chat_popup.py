from dash import html, dcc

def chat_popup():
    return html.Div(
        id='chat-popup-container',
        children=[
            html.Div(
                id='chat-popup-header',
                children=[
                    html.Span("Chat", style={'fontWeight': 'bold'}),
                    html.Button("×", id='chat-popup-close', n_clicks=0, style={
                        'background': 'none', 'border': 'none', 'fontSize': '20px', 'float': 'right', 'cursor': 'pointer'
                    }),
                ],
                style={'padding': '8px', 'background': '#007bff', 'color': 'white', 'borderTopLeftRadius': '10px', 'borderTopRightRadius': '10px'}
            ),
            dcc.Textarea(id='chat-history', value='', style={'width': '100%', 'height': 150, 'resize': 'none'}, readOnly=True),
            html.Div([
                dcc.Input(id='chat-input', type='text', placeholder='Type your message...', style={'width': '70%'}),
                html.Button('Send', id='chat-send-btn', n_clicks=0, style={'marginLeft': '5px'})
            ], style={'padding': '8px'})
        ],
        style={
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'width': '300px',
            'boxShadow': '0 4px 16px rgba(0,0,0,0.2)',
            'borderRadius': '10px',
            'background': 'white',
            'zIndex': 9999,
            'display': 'none',  # Initially hidden
        }
    )