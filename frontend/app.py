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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            /* Chat button hover effects */
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
            
            /* Upload loading animation */
            .fa-spin {
                animation: fa-spin 1.5s infinite linear;
                color: #2563eb;
            }
            
            @keyframes fa-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Smooth transitions for upload states */
            #upload-icon {
                transition: all 0.3s ease;
            }
            
            #upload-text {
                transition: all 0.3s ease;
            }
            
            /* Upload area hover effect */
            div[id="upload-genetic-data"]:hover {
                border-color: #2563eb !important;
                background-color: #f0f7ff !important;
                cursor: pointer;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(37, 99, 235, 0.1);
            }
            
            /* Success state styling */
            .fa-check-circle {
                color: #059669 !important;
            }
            
            /* Error state styling */
            .fa-exclamation-triangle {
                color: #dc2626 !important;
            }
            
            /* Upload text color changes based on state */
            #upload-text.success {
                color: #059669;
                font-weight: 600;
            }
            
            #upload-text.error {
                color: #dc2626;
                font-weight: 600;
            }
            
            #upload-text.loading {
                color: #2563eb;
                font-weight: 600;
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
    app.run(debug=False, host='0.0.0.0', port=9000)