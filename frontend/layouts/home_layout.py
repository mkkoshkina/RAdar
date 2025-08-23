from dash import dcc, html

from frontend.ui_kit.styles import (
    primary_button_style,
    secondary_button_style,
    text_style,
    theme_colors,
)

    

# ------- Local styles (kept minimal to match existing UI kit) -------
page_container_style = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "16px",
}

hero_style = {
    'background': f'linear-gradient(135deg, {theme_colors["primary"]} 0%, {theme_colors["primary_dark"]} 100%)',
    'color': 'white',
    'padding': '50px 30px',
    'borderRadius': '12px',
    'textAlign': 'center',
    'boxShadow': '0 8px 32px rgba(37, 99, 235, 0.2)',
    'marginBottom': '24px'
}

cards_wrap_style = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
    "gap": "16px",
}

card_style = {
    "backgroundColor": "#ffffff",
    "padding": "16px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
    "border": "1px solid #efefef",
}

heading_style = {
    "fontSize": "20px",
    "fontWeight": 600,
    "margin": "0 0 8px 0",
}

subheading_style = {
    "fontSize": "16px",
    "fontWeight": 500,
    "margin": "12px 0 8px 0",
}

btn_row_style = {
    "display": "flex",
    "gap": "12px",
    "flexWrap": "wrap",
    "justifyContent": "center",
}


def _markdown_content(app_name: str, lang: str = 'en') -> str:
    return f"""
**🧬 {app_name} – {t("tool_description_title", lang)}**

{app_name} {t("tool_description", lang)}

{t("tool_description_detail", lang)}

---

### 📚 {t("genomic_evidence_sources", lang)}
[PGS Catalog PGS000195](https://www.pgscatalog.org/score/PGS000195/), [PGS Catalog PGS000194](https://www.pgscatalog.org/score/PGS000194/), {t("genomic_evidence_detail", lang)}

### ⚖️ {t("clinical_relevance", lang)}
{t("clinical_relevance_intro", lang)}

- {t("clinical_app_1", lang)}
- {t("clinical_app_2", lang)}
- {t("clinical_app_3", lang)}
- {t("clinical_app_4", lang)}

### ⚠️ {t("important_notice", lang)}
{t("important_disclaimer", lang)}

### 🛡 {t("data_protection", lang)}
- {t("data_protection_1", lang)}
- {t("data_protection_2", lang)}

### 📄 {t("supported_data_formats", lang)}
- {t("supported_formats_detail", lang)}

### 🔹 {t("clinical_use_case", lang)}
**{app_name}** {t("clinical_use_case_detail", lang)}
"""


# ------- Components -------

from frontend.utils.i18n import t

lang_btn_style = {
    "backgroundColor": "#2563eb",
    "color": "white",
    "border": "none",
    "borderRadius": "6px",
    "padding": "8px 18px",
    "fontWeight": "600",
    "fontSize": "1rem",
    "marginRight": "8px",
    "boxShadow": "0 2px 8px rgba(37,99,235,0.12)",
    "cursor": "pointer",
    "transition": "background 0.2s"
}

def hero_section(app_name: str, lang: str = 'en'):
    return html.Div([
        html.Div([
            html.Button("EN", id="lang-en", n_clicks=0, style=lang_btn_style),
            html.Button("RU", id="lang-ru", n_clicks=0, style={**lang_btn_style, "marginRight": "0"})
        ], style={"display": "flex", "justifyContent": "flex-end", "marginBottom": "16px"}),
        html.H1(t("welcome", lang), style={
            'margin': '0 0 15px 0', 
            'fontSize': '2.8rem', 
            'fontWeight': '700',
            'textShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),
        html.P(
            t("upload_info", lang),
            style={
                'fontSize': '1.2rem',
                'margin': '0 0 30px 0',
                'opacity': '0.95',
                'maxWidth': '600px',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'lineHeight': '1.5'
            },
        ),
        html.Div(
            [
                dcc.Link(
                    html.Button([
                        html.Span("📁", style={'marginRight': '10px', 'fontSize': '16px'}),
                        t("upload_cta", lang)
                    ], id="home-upload-cta", n_clicks=0,
                       className='btn-primary', style={
                        **primary_button_style,
                        'backgroundColor': 'white',
                        'color': theme_colors['primary'],
                        'fontWeight': '600',
                        'padding': '14px 28px',
                        'fontSize': '1.1rem',
                        'border': 'none',
                        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.15)',
                        'marginRight': '15px',
                        'transition': 'all 0.3s ease'
                    }),
                    href="/analyze",
                ),
                dcc.Link(
                    html.Button([
                        html.Span("ℹ️", style={'marginRight': '10px', 'fontSize': '16px'}),
                        t("view_info", lang)
                    ], id="home-docs-cta", n_clicks=0, 
                       className='btn-primary', style={
                        **secondary_button_style,
                        'backgroundColor': 'rgba(255, 255, 255, 0.2)',
                        'color': 'white',
                        'border': '2px solid white',
                        'fontWeight': '500',
                        'padding': '14px 28px',
                        'fontSize': '1.1rem',
                        'transition': 'all 0.3s ease'
                    }),
                    href="/info",
                ),
            ],
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'flexWrap': 'wrap',
                'gap': '15px'
            },
        ),
    ], style=hero_style)


def info_cards(app_name: str, lang: str = 'en'):
    return html.Div([
        html.Div([
            html.Div(t("about_tool", lang), style=heading_style),
            dcc.Markdown(_markdown_content(app_name, lang), style=text_style),
        ], style=card_style),
        html.Div([
            html.Div(t("how_it_works", lang), style=heading_style),
            html.Div([
                html.Div(t("step1", lang), style=text_style),
                html.Div(t("step2", lang), style=text_style),
                html.Div(t("step3", lang), style=text_style),
                html.Div(t("step4", lang), style=text_style),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px"}),
            html.Div(t("supported_grch37", lang), style={**text_style, "marginTop": "8px", "opacity": 0.9}),
        ], style=card_style),
        html.Div([
            html.Div(t("quick_start", lang), style=heading_style),
            html.Div([
                html.Div(t("qs1", lang), style=text_style),
                html.Div(t("qs2", lang), style=text_style),
                html.Div(t("qs3", lang), style=text_style),
                html.Div(t("qs4", lang), style=text_style),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px"}),
        ], style=card_style),
    ], style=cards_wrap_style)


# ------- Layout -------

def home_layout(user_session=None, app_name: str = "RAdar", lang: str = 'en'):
    return html.Div([
        hero_section(app_name, lang),
        info_cards(app_name, lang),
    ], style=page_container_style)
