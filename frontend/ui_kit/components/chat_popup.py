import dash
from dash import dcc, html
import uuid

# Store session ID globally for the chat session
chat_session_id = str(uuid.uuid4())

def create_chatbot_layout():
    return html.Div([
        html.Div(id="chat-display", children=[], style={
            'height': '400px', 
            'overflow-y': 'scroll', 
            'border': '1px solid #ccc', 
            'padding': '10px',
            'margin-bottom': '10px',
            'backgroundColor': '#f8f9fa'
        }),
        dcc.Input(
            id="chat-input",
            type="text",
            placeholder="Type your message here...",
            style={'width': '80%', 'padding': '8px', 'border': '1px solid #ddd', 'borderRadius': '4px'}
        ),
        html.Button("Send", id="send-button", style={
            'width': '18%', 
            'margin-left': '2%',
            'padding': '8px',
            'background': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer'
        }),
        # Store session ID in hidden divs
        html.Div(id="session-store", children=chat_session_id, style={'display': 'none'}),
        dcc.Store(id="chat-session-id", data=chat_session_id)
    ])

def chat_popup():
    """Create the chat popup component"""
    return html.Div([
        html.Div(
            id="chat-popup-container",
            children=[
                html.Div([
                    html.H4("Chat Assistant", style={'margin': '0', 'color': 'white'}),
                    html.Button("×", id="chat-popup-close", 
                               style={'background': 'none', 'border': 'none', 
                                     'color': 'white', 'fontSize': '20px', 
                                     'cursor': 'pointer', 'float': 'right'})
                ], style={'background': '#007bff', 'padding': '10px', 'color': 'white'}),
                create_chatbot_layout()
            ],
            style={
                'position': 'fixed',
                'bottom': '90px',
                'right': '20px',
                'width': '350px',
                'height': '500px',
                'background': 'white',
                'border': '1px solid #ccc',
                'borderRadius': '10px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                'zIndex': 9999,
                'display': 'none'  # Hidden by default
            }
        )
    ])