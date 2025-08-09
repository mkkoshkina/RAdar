# Theme Colors
theme_colors = {
    'primary': '#007bff',
    'secondary': '#343a40',
    'background': '#ffffff',
    'accent': '#ffc107',
    'text': '#495057',
    'success': '#28a745',
    'error': '#dc3545',
    'info': '#17a2b8'
}

# Base Font Styles
font_styles = {
    'base': '"Arial", sans-serif',
    'heading': '"Helvetica Neue", Arial, sans-serif',
    'text': '"Open Sans", sans-serif'
}

# Primary and Secondary Button Styles
primary_button_style = {**button_base, 'backgroundColor': theme_colors['primary'], 'color': '#ffffff',
                        'padding': '12px 18px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.12)'}
secondary_button_style = {**button_base, 'backgroundColor': theme_colors['accent'], 'color': '#ffffff',
                          'padding': '12px 18px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}

# Input and Dropdown Styles
input_style = {
    'padding': '12px',
    'border': f"2px solid {theme_colors['secondary']}",
    'borderRadius': '8px',
    'outline': 'none',
    'boxSizing': 'border-box',
    'fontFamily': font_styles['base'],
    'fontSize': '16px',
    'color': theme_colors['text'],
}

# Text and Heading Styles
text_style = {
    'fontSize': '16px',
    'lineHeight': '1.6',
    'color': theme_colors['text'],
    'fontFamily': font_styles['text'],
}

heading2_style = {
    'fontFamily': font_styles['heading'],
    'fontWeight': '600',
    'color': theme_colors['primary'],
    'textShadow': '0px 1px 2px rgba(0, 0, 0, 0.1)',
    'marginBottom': '15px',
    'paddingTop': '10px',
    'lineHeight': '1.4',
    'textTransform': 'uppercase',
    'letterSpacing': '1px',
}

heading5_style = {
    'fontFamily': font_styles['heading'],
    'fontWeight': '500',
    'color': theme_colors['secondary'],
    'marginBottom': '10px',
    'paddingTop': '5px',
    'lineHeight': '1.3',
    'fontSize': '14px',
    'textTransform': 'none',
    'letterSpacing': '0.5px',
}