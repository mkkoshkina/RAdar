import dash
from dash import dcc, html
import uuid

# Store session ID globally for the chat session
chat_session_id = str(uuid.uuid4())

def create_chatbot_layout():
    return html.Div([
        # Chat display area
        html.Div(id="chat-display", children=[], style={
            'height': '250px',  # Reduced from 400px
            'overflow-y': 'auto', 
            'border': '1px solid #e0e0e0', 
            'padding': '10px',
            'margin': '10px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '5px',
            'fontSize': '13px',
            'lineHeight': '1.4'
        }),
        # Input container for better alignment
        html.Div([
            dcc.Input(
                id="chat-input",
                type="text",
                placeholder="Type your message here...",
                style={
                    'width': '75%', 
                    'padding': '8px', 
                    'border': '1px solid #ddd', 
                    'borderRadius': '4px',
                    'fontSize': '13px',
                    'outline': 'none',
                    'boxSizing': 'border-box'
                }
            ),
            html.Button("Send", id="send-button", style={
                'width': '22%', 
                'margin-left': '3%',
                'padding': '8px',
                'background': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease',
                'fontSize': '13px',
                'fontWeight': 'bold',
                'height': '36px'  # Match input height
            })
        ], style={
            'display': 'flex',
            'padding': '0 10px 10px 10px',
            'alignItems': 'center',
            'gap': '5px'
        }),
        # Store session ID and pending message
        html.Div(id="session-store", children=chat_session_id, style={'display': 'none'}),
        dcc.Store(id="chat-session-id", data=chat_session_id),
        dcc.Store(id="pending-message", data=None)  # Add this store for pending messages
    ], style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'})

def chat_popup():
    """Create the chat popup component"""
    return html.Div([
        html.Div(
            id="chat-popup-container",
            children=[
                # Header with better styling
                html.Div([
                    html.H4("Chat Assistant", style={
                        'margin': '0', 
                        'color': 'white',
                        'fontSize': '14px',
                        'fontWeight': 'bold'
                    }),
                    html.Button("×", id="chat-popup-close", 
                               style={
                                   'background': 'none', 
                                   'border': 'none', 
                                   'color': 'white', 
                                   'fontSize': '18px', 
                                   'cursor': 'pointer', 
                                   'float': 'right',
                                   'width': '25px',
                                   'height': '25px',
                                   'borderRadius': '50%',
                                   'display': 'flex',
                                   'alignItems': 'center',
                                   'justifyContent': 'center'
                               })
                ], style={
                    'background': '#007bff', 
                    'padding': '8px 12px', 
                    'color': 'white',
                    'borderRadius': '10px 10px 0 0',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center'
                }),
                # Chat content with proper flex layout
                html.Div([
                    create_chatbot_layout()
                ], style={
                    'flex': '1',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflow': 'hidden'
                })
            ],
            style={
                'position': 'fixed',
                'bottom': '120px',  # Adjusted position
                'right': '20px',
                'width': '350px',
                'height': '380px',  # Reduced from 500px
                'background': 'white',
                'border': '1px solid #ccc',
                'borderRadius': '10px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                'zIndex': 9999,
                'display': 'none',  # Hidden by default
                'overflow': 'hidden',
                'flexDirection': 'column'
            }
        )
    ])