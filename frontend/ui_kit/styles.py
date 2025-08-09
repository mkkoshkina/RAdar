# Enhanced Theme Colors
theme_colors = {
    'primary': '#2563eb',
    'primary_light': '#3b82f6', 
    'primary_dark': '#1d4ed8',
    'secondary': '#5c4033',        # Keep brown for accents
    'background': '#faf8f6',
    'background_gray': '#e2e3e5',
    'background_light_gray':  '#f8f9fa',
    'surface': '#ffffff',
    'accent': '#d4a373',           # Golden-brown accent
    'text': '#1f1f1f',             # Almost black - primary text
    'text_medium': '#374151',      # Dark gray - secondary text  
    'text_light': '#6b7280',       # Medium gray - muted text
    'success': '#059669',
    'error': '#dc2626',
    'warning': '#d97706',
    'info': '#0284c7',
    'border': 'rgba(92, 64, 51, 0.15)',
    'border_light': '#e5e7eb',
    'shadow': '0 4px 10px rgba(0, 0, 0, 0.05)'
}

# Base Font Styles
font_styles = {
    'base': '"Montserrat", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    'heading': '"Montserrat", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    'text': '"Montserrat", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif'
}

# Base Style
base_style = {
    'textAlign': 'left',
    'borderRadius': '8px',
    'margin': '15px 0',
    'fontFamily': font_styles['base']
}
# Enhanced Card Style
card_style = {
    'backgroundColor': theme_colors['surface'],
    'padding': '24px',
    'margin': '16px 0',
    'borderRadius': '12px',
    'boxShadow': theme_colors['shadow'],
    'border': f'1px solid {theme_colors["border"]}',
    'transition': 'all 0.3s ease'
}

# Table Styles
table_style = {
    **base_style,
    'overflowX': 'auto',
    'border': '1px solid #dee2e6',
    'borderRadius': '0.375rem',
    'boxShadow': f'1px solid {theme_colors["border"]}',
    'marginTop': '1rem',
}

table_header_style = {
    'color': theme_colors['surface'],
    'backgroundColor': theme_colors['primary'],
    'fontWeight': 'bold',
    'padding': '1rem',
    'borderBottom': f'2px solid {theme_colors["border"]}',
}

table_cell_style = {
    'backgroundColor': theme_colors['background'],
    'color': theme_colors['text'],
    'padding': '0.75rem',
    'borderBottom': f'1px solid {theme_colors["border_light"]}',
    'textAlign': 'left',
    'fontSize': '0.9rem',
}

# Base Button Style
button_base = {
    'border': 'none',
    'borderRadius': '5px',
    'fontSize': '18px',
    'margin': '10px',
    'cursor': 'pointer',
    'outline': 'none',
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

dropdown_style = {
    'outline': 'none',
    'boxSizing': 'border-box',
    'fontFamily': font_styles['base'],
    'fontSize': '16px',
    'color': theme_colors['text'],
    'backgroundColor': theme_colors['background'],
    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
}

# Text and Heading Styles
text_style = {
    'fontSize': '16px',
    'lineHeight': '1.6',
    'color': theme_colors['text'],
    'fontFamily': font_styles['text'],
}

# Modern heading styles
heading1_style = {
    'fontSize': '2.5rem',
    'fontWeight': '600',
    'color': theme_colors['text'],
    'marginBottom': '1rem',
    'lineHeight': '1.2'
}

heading2_style = {
    'fontSize': '2rem',
    'fontWeight': '500',
    'color': theme_colors['text'],
    'marginBottom': '0.75rem',
    'lineHeight': '1.3'
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

# Navigation Styles
navigation_style = {
    'padding': '20px 15px',
    'backgroundColor': theme_colors['accent'],
    'fontSize': '18px',
    'textAlign': 'center',
    'fontWeight': 'bold',
    'color': 'white',
    'boxShadow': '0 2px 4px 0 rgba(0,0,0,.2)',
}

link_style = {
    'color': 'white',
    'textDecoration': 'none',
    'padding': '5px 15px',
    'fontWeight': '500',
    'display': 'inline-block',
    'transition': 'color 0.3s',
}

navigation_separator_style = {
    'color': 'rgba(255, 255, 255, 0.7)',
    'padding': '0 10px',
}

# User Balance and Error Message Styles
user_balance_style = {
    **base_style,
    'color': theme_colors['secondary'],
    'backgroundColor': theme_colors['background_light_gray'],
    'padding': '10px 20px',
    'borderRadius': '5px',
    'fontWeight': 'bold',
    'boxShadow': 'inset 0 1px 3px rgba(0,0,0,.3)',
    'fontSize': '20px',
}

error_message_style = {
    **base_style,
    'padding': '12px',
    'border': f"1px solid {theme_colors['error']}",
    'color': theme_colors['error'],
    'backgroundColor': theme_colors['background_light_gray'],
    'borderRadius': '5px',
    'fontWeight': 'bold',
    'display': 'flex',
    'alignItems': 'center',
    'gap': '10px',
}

upload_style = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '2px',
    'borderStyle': 'dashed',
    'borderRadius': '8px',
    'textAlign': 'center',
    'margin': '10px 0',
    'borderColor': theme_colors['primary_light'],
    'backgroundColor': theme_colors['background_gray'],
}

# Page Content
page_content_style = {'margin': '20px'}
