from dash import dcc, html

from frontend.ui_kit.styles import link_style, navigation_style, navigation_separator_style


def navigation_bar(user_session):
    # Build links for center section
    links = [dcc.Link('Home', href='/home', style=link_style)]

    if user_session and user_session.get('is_authenticated'):
        links += [
            html.Span(' | ', style=navigation_separator_style),
            dcc.Link('Prediction', href='/prediction', style=link_style),
            html.Span(' | ', style=navigation_separator_style),
            dcc.Link('Billing', href='/billing', style=link_style),
            html.Span(' | ', style=navigation_separator_style),
            dcc.Link('Info', href='/info', style=link_style)
        ]
        if user_session.get('is_superuser'):
            links += [
                html.Span(' | ', style=navigation_separator_style),
                dcc.Link('Admin', href='/admin', style=link_style)
            ]
    else:
        links += [
            html.Span(' | ', style=navigation_separator_style),
            dcc.Link('Info', href='/info', style=link_style)
        ]

    return html.Div(
        [
            # Left empty space
            html.Div(style={'flex': '1'}),
            
            # Center links
            html.Div(
                links,
                style={
                    'display': 'flex', 
                    'alignItems': 'center', 
                    'justifyContent': 'center',
                    'flex': '0 0 auto'  # Don't grow or shrink, auto width
                }
            ),
            
            # Right logo section
            html.Div(
                html.Img(
                    src='/assets/logo.png',
                    style={
                        'height': '70px',      # Fixed height
                        'maxHeight': '60px',   # Ensure it doesn't exceed
                        'objectFit': 'contain',
                        'display': 'block'
                    }
                ),
                style={
                    'flex': '1',
                    'display': 'flex',
                    'justifyContent': 'flex-end',  # Align logo to the right
                    'alignItems': 'center'
                }
            )
        ],
        style={
        **navigation_style,
        'display': 'flex',
        'alignItems': 'center',
        'height': '80px',          # Increased from 60px
        'minHeight': '80px',       # Increased from 60px
        'padding': '0 20px',
        'boxSizing': 'border-box'
                }
    )
