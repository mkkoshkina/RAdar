import dash
from dash import dcc, html

from frontend.callbacks.callbacks import register_callbacks  # Remove the 's' from callbacks
from frontend.ui_kit.styles import page_content_style
from frontend.ui_kit.components.chat_popup import chat_popup

app = dash.Dash(__name__, suppress_callback_exceptions=True, title="RAdar: Rheumatoid Arthritis Predictor", assets_folder="assets")
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=5 * 60 * 1000),
    dcc.Store(id='user-session', storage_type='session'),

    dcc.Store(id='sign-in-session-update', storage_type='session'),
    dcc.Store(id='sign-up-session-update', storage_type='session'),

    html.Div(id='nav-bar'),
    html.Div(id='page-content', style=page_content_style),
    html.Button(
        "💬", id="open-chat-popup", n_clicks=0,  # Added chat emoji
        style={
            'position': 'fixed',
            'bottom': '120px',
            'right': '40px',
            'zIndex': 9998,
            'background': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '50%',
            'width': '60px',
            'height': '60px',
            'fontSize': '24px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.2)',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease'  # Added smooth transition
        }
    ),
    dcc.Store(id='chat-popup-visible', data=False),  # Add this to store popup state

    chat_popup(),
])

# Add external CSS for hover effects
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            #open-chat-popup:hover {
                background: #0056b3 !important;
                transform: scale(1.05) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            }
            
            #open-chat-popup:active {
                transform: scale(0.95) !important;
            }
            
            #send-button:hover {
                background: #0056b3 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            }
            
            #send-button:active {
                transform: translateY(0px) !important;
                background: #004494 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    register_callbacks(app)
    app.run(debug=True, host='0.0.0.0', port=9000)