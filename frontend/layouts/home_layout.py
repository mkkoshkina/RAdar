from dash import dcc, html

from frontend.ui_kit.styles import (
    primary_button_style,
    secondary_button_style,
    text_style,
)


# ------- Local styles (kept minimal to match existing UI kit) -------
page_container_style = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "16px",
}

hero_style = {
    "backgroundColor": "#ffffff",
    "padding": "24px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.06)",
    "border": "1px solid #eaeaea",
    "textAlign": "center",
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


def _markdown_content(app_name: str) -> str:
    return f"""
**🧬 {app_name} – Genetic Risk Calculator for Rheumatoid Arthritis**

{app_name} is a clinical decision-support tool designed to assess an individual’s polygenic risk for developing rheumatoid arthritis (RA), using validated Polygenic Risk Scores (PRS).

By uploading a patient’s genetic data file in VCF, the platform cross-references known single nucleotide polymorphisms (SNPs) associated with RA risk against curated scientific databases. The resulting PRS can be integrated into the broader context of clinical evaluation, supporting risk stratification, early intervention planning, and personalized prevention strategies.

---

### 📚 Genomic evidence sources
[PGS Catalog PGS000195](https://www.pgscatalog.org/score/PGS000195/), [PGS Catalog PGS000194](https://www.pgscatalog.org/score/PGS000194/), and peer-reviewed RA-specific literature. These datasets encompass both general genetic susceptibility loci and variants linked to seropositive and seronegative RA phenotypes.

### ⚖️ Clinical relevance
Polygenic risk models have demonstrated utility in multiple specialties — cardiology, oncology, endocrinology — and are now being translated into rheumatology. Potential applications in RA include:

- Identifying high-risk individuals before symptom onset, enabling targeted monitoring;
- Guiding lifestyle or pharmacologic prevention strategies in predisposed patients;
- Refining patient selection for clinical trials focused on disease modification;
- Complementing traditional biomarkers (e.g., ACCP, RF) in risk assessment.

### ⚠️ Important
The PRS is an adjunctive tool, not a diagnostic test. It should be interpreted in the context of the patient’s clinical picture, family history, and other biomarkers. It does not replace physician judgment and is not intended as a standalone determinant for treatment initiation.

### 🛡 Data protection
- All files are processed locally or on encrypted, secure servers.
- No genetic data is stored after analysis — automatic deletion is enforced.

### 📄 Supported data formats
- VCF — MyHeritage, Ancestry, Atlas, WES/WGS

### 🔹 Clinical use case
**SNP2Risk-RA** can be incorporated into preventive rheumatology workflows as part of risk-based patient management, supporting earlier detection, improved counseling, and proactive care pathways.
"""


# ------- Components -------

def hero_section(app_name: str):
    return html.Div([
        html.H1("Welcome", style={"margin": 0, "fontSize": "28px", "fontWeight": 700}),
        html.P(
            "Upload a VCF file to calculate polygenic risk for rheumatoid arthritis.",
            style={**text_style, "margin": "6px 0 16px 0"},
        ),
        html.Div(
            [
                dcc.Link(

                    html.Button("Upload VCF & Analyze", id="home-upload-cta", n_clicks=0,
                                className='btn-primary', style=primary_button_style),
                    href="/analyze",
                ),
                dcc.Link(
                    html.Button("View Information", id="home-docs-cta", n_clicks=0, className='btn-primary', style=secondary_button_style),
                    href="/info",
                ),
            ],
            style=btn_row_style,
        ),
    ], style=hero_style)


def info_cards(app_name: str):
    return html.Div([
        html.Div([
            html.Div("About the tool", style=heading_style),
            dcc.Markdown(_markdown_content(app_name), style=text_style),
        ], style=card_style),
        html.Div([
            html.Div("How it works", style=heading_style),
            html.Div([
                html.Div("1. Upload VCF (unzipped)", style=text_style),
                html.Div("2. SNP matching vs curated panels", style=text_style),
                html.Div("3. PRS aggregation with validated weights", style=text_style),
                html.Div("4. Report preview & export", style=text_style),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px"}),
            html.Div("Supported: hg19 / hg38 (auto-detect when possible)", style={**text_style, "marginTop": "8px", "opacity": 0.9}),
        ], style=card_style),
        html.Div([
            html.Div("Quick start", style=heading_style),
            html.Div([
                html.Div("• Go to Analyze and upload your .vcf", style=text_style),
                html.Div("• Review matched SNPs and coverage", style=text_style),
                html.Div("• See overall PRS and interpretation bands", style=text_style),
                html.Div("• Export PDF summary for the chart/metrics", style=text_style),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px"}),
        ], style=card_style),
    ], style=cards_wrap_style)


# ------- Layout -------

def home_layout(user_session=None, app_name: str = "SNP2Risk-RA"):
    return html.Div([
        hero_section(app_name),
        info_cards(app_name),
    ], style=page_container_style)
