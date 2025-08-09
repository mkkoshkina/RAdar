# =========================
# Theme Colors — Blue + Warm Neutrals
# =========================
theme_colors = {
    'primary': '#2563eb',       # modern blue for primary actions
    'secondary': '#5c4033',     # warm rich brown
    'background': '#faf8f6',    # warm light beige background
    'accent': '#d4a373',        # golden-brown accent
    'text': '#4a3f35',          # deep warm brown text
    'success': '#2e7d32',       # deep green
    'error': '#c62828',         # muted red
    'info': '#0288d1'           # cyan-blue for info
}

# =========================
# Fonts
# =========================
font_styles = {
    'base': '"Inter", "Arial", sans-serif',
    'heading': '"Poppins", "Helvetica Neue", Arial, sans-serif',
    'text': '"Open Sans", sans-serif'
}

# =========================
# Base Style
# =========================
base_style = {
    'textAlign': 'left',
    'borderRadius': '10px',
    'margin': '15px 0',
    'fontFamily': font_styles['base'],
    'backgroundColor': theme_colors['background'],
    'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.05)'
}

# =========================
# Table Styles
# =========================
table_style = {
    **base_style,
    'overflowX': 'auto',
    'border': '1px solid rgba(92, 64, 51, 0.15)',  # warm border
    'borderRadius': '10px',
    'boxShadow': '0 8px 24px rgba(92, 64, 51, 0.10)',
    'marginTop': '1.5rem',
}

table_header_style = {
    'color': '#ffffff',
    'backgroundImage': 'linear-gradient(to right, #8d6e63, #d4a373)',  # brown gradient
    'fontWeight': '600',
    'padding': '1rem',
    'borderBottom': '2px solid rgba(0, 0, 0, 0.05)',
    'letterSpacing': '0.5px'
}

table_cell_style = {
    'backgroundColor': '#ffffff',
    'color': theme_colors['text'],
    'padding': '0.85rem 1rem',
    'borderBottom': '1px solid #e7e0db',
    'textAlign': 'left',
    'fontSize': '0.95rem',
}

# =========================
# Buttons
# =========================
button_base = {
    'border': 'none',
    'borderRadius': '8px',
    'fontSize': '16px',
    'margin': '10px',
    'cursor': 'pointer',
    'outline': 'none',
    'transition': 'all 0.25s ease',
}

primary_button_style = {
    **button_base,
    'backgroundImage': 'linear-gradient(90deg, #2563eb, #3b82f6)',  # blue gradient
    'color': '#ffffff',
    'padding': '12px 20px',
    'boxShadow': '0 6px 16px rgba(37, 99, 235, 0.28)'
}

secondary_button_style = {
    **button_base,
    'backgroundImage': 'linear-gradient(90deg, #5c4033, #8d6e63)',  # brown gradient
    'color': '#ffffff',
    'padding': '12px 20px',
    'boxShadow': '0 6px 16px rgba(92, 64, 51, 0.28)'
}

# =========================
# Inputs & Dropdowns
# =========================
input_style = {
    'padding': '12px',
    'border': f"1.5px solid {theme_colors['primary']}",   # subtle blue focus color
    'borderRadius': '10px',
    'outline': 'none',
    'boxSizing': 'border-box',
    'fontFamily': font_styles['base'],
    'fontSize': '15px',
    'color': theme_colors['text'],
    'boxShadow': '0 2px 8px rgba(37, 99, 235, 0.10)',
    'backgroundColor': '#ffffff',
}

dropdown_style = {
    **input_style,
    'boxShadow': '0 2px 8px rgba(92, 64, 51, 0.10)',  # slightly warmer shadow
}

# =========================
# Typography
# =========================
text_style = {
    'fontSize': '16px',
    'lineHeight': '1.6',
    'color': theme_colors['text'],
    'fontFamily': font_styles['text'],
}

heading2_style = {
    'fontFamily': font_styles['heading'],
    'fontWeight': '600',
    'color': theme_colors['secondary'],  # brown to balance blue UI
    'textShadow': '0px 2px 4px rgba(92, 64, 51, 0.15)',
    'marginBottom': '15px',
    'paddingTop': '10px',
    'lineHeight': '1.4',
    'letterSpacing': '0.8px',
    'textTransform': 'uppercase',
}

heading5_style = {
    'fontFamily': font_styles['heading'],
    'fontWeight': '500',
    'color': '#6b4f43',  # softer brown
    'marginBottom': '8px',
    'paddingTop': '4px',
    'lineHeight': '1.3',
    'fontSize': '14px',
    'letterSpacing': '0.4px',
}

# =========================
# Navigation & Links
# =========================
navigation_style = {
    'padding': '18px 15px',
    'backgroundImage': 'linear-gradient(to right, #1e3a8a, #2563eb)',  # blue nav
    'fontSize': '18px',
    'textAlign': 'center',
    'fontWeight': '600',
    'color': 'white',
    'boxShadow': '0 6px 14px rgba(0,0,0,.25)',
}

link_style = {
    'color': 'white',
    'textDecoration': 'none',
    'padding': '6px 15px',
    'fontWeight': '500',
    'display': 'inline-block',
    'transition': 'color 0.3s, transform 0.2s',
}

navigation_separator_style = {
    'color': 'rgba(255, 255, 255, 0.6)',
    'padding': '0 10px',
}

# =========================
# User Balance & Error
# =========================
user_balance_style = {
    **base_style,
    'color': theme_colors['secondary'],
    'backgroundColor': '#ecf3ff',  # cool card so the brown text pops
    'padding': '12px 22px',
    'borderRadius': '10px',
    'fontWeight': '600',
    'boxShadow': 'inset 0 1px 3px rgba(0,0,0,.06), 0 6px 16px rgba(37, 99, 235, 0.12)',
    'fontSize': '18px',
}

error_message_style = {
    **base_style,
    'padding': '12px',
    'border': f"1px solid {theme_colors['error']}",
    'color': theme_colors['error'],
    'backgroundColor': '#fde2e2',
    'borderRadius': '10px',
    'fontWeight': '500',
    'display': 'flex',
    'alignItems': 'center',
    'gap': '10px',
    'boxShadow': '0 6px 16px rgba(198, 40, 40, 0.18)'
}

# =========================
# Page Content
# =========================
page_content_style = {
    'margin': '20px'
}
