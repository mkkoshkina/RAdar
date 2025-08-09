from dash import dcc, dash_table, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px
from statistics import quantiles
from scipy.stats import percentileofscore
import math
import random
from pathlib import Path

from frontend.data.remote_data import fetch_user_balance, fetch_prediction_history
from frontend.ui_kit.components.user_balance import user_balance
from frontend.ui_kit.styles import table_style, table_header_style, table_cell_style, input_style, \
    dropdown_style, secondary_button_style, text_style, heading5_style, primary_button_style
from frontend.ui_kit.utils import format_timestamp

card_style = {
    'backgroundColor': '#ffffff',
    'padding': '20px',
    'margin': '10px 0',
    'borderRadius': '8px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'border': '1px solid #e0e0e0'
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
    'borderColor': '#007bff',
    'backgroundColor': '#f8f9fa'
}

risk_colors = {
    'low': '#28a745',
    'lower than average': '#28a745',
    'average': '#28a745',
    'higher than average': '#ffc107', 
    'high': '#dc3545'
}


def compute_risk_label(risk_percentile):
    if risk_percentile <= 10:
        label = 'low'
    elif 10 < risk_percentile <= 40:
        label = 'lower than average'
    elif 40 < risk_percentile <= 60:
        label = 'average'
    elif 60 < risk_percentile <= 90:
        label = 'higher than average'
    elif 90 < risk_percentile:
        label = 'high'
    else:
        raise ValueError("Invalid risk percentile value")
    return label


def plot_normal_hist(risk, samples, risk_percentile):
    percentiles = quantiles(samples, n=10)
    hist = go.Histogram(
        x=samples,
        histnorm='probability density',
        name='Population average risk scores',
        opacity=0.6
    )
    risk_line = go.Scatter(
        x=[risk, risk],
        y=[0, 0.5],
        mode='lines',
        name='Your Risk',
        line=dict(color='firebrick', dash='dash')
    )
    annotation = dict(
        x=risk,
        y=0.5,
        text=f"<br>Percentile: {risk_percentile:.1f}%",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-40
    )

    histogram_fig = go.Figure(data=[hist, risk_line])
    histogram_fig.update_layout(
        xaxis_title='Risk Score Decile',
        yaxis_title='Density',
        bargap=0.05,
        height=600,
        width=900,
        xaxis=dict(
            tickmode='array',
            ticktext=np.arange(10, 100, 10),
            tickvals=percentiles,
            ticklen=5,
            ticks='outside'),
        yaxis=dict(range=[0, None],
                   ticklen=5,
                   ticks='outside'),
        annotations=[annotation]
    )

    return histogram_fig


def genetic_upload_form():
    return html.Div([
        html.H3("Upload Genetic Data", style={'color': '#333', 'marginBottom': '15px'}),
        html.P("Upload your sequencing data in VCF format", 
               style={'color': '#666', 'marginBottom': '10px'}),
        
        dcc.Upload(
            id='upload-genetic-data',
            children=html.Div([
                html.I(className="fas fa-upload", style={'marginRight': '10px'}),
                'Drag and Drop or Click to Select Genetic Data File'
            ]),
            style=upload_style,
            multiple=False
        ),
        
        html.Div(id='upload-status', style={'margin': '10px 0'}),
        
        html.Button('Analyze Rheumatoid Arthritis Risk', id='analyze-button', 
                   style=primary_button_style, disabled=True),
        
    ], style=card_style)


def create_error_display(error_message):
    
    if "BCFtools filtering failed" in error_message:
        error_type = "Invalid VCF Format"
        description = "The uploaded file appears to be corrupted or is not a valid VCF format."
        suggestions = [
            "Ensure your file is in VCF format (.vcf extension)",
            "Check that the file is not corrupted during upload",
            "Try re-downloading the original file from your genetic testing provider"
        ]
    elif "PLINK conversion failed" in error_message:
        error_type = "VCF Processing Error"
        description = "The VCF file could not be processed by PLINK. This may be due to incompatible format or missing required fields."
        suggestions = [
            "Ensure your VCF file contains proper genotype information",
            "Check that the file follows VCF 4.x specifications",
            "Verify that genetic variants have proper chromosome and position information"
        ]
    elif "PLINK PRS calculation failed" in error_message:
        error_type = "Risk Score Calculation Error"
        description = "Unable to calculate the polygenic risk score. This may be due to insufficient genetic variants matching our reference panel."
        suggestions = [
            "Your genetic data may not contain enough variants for reliable risk calculation",
            "Ensure your data is from a compatible genetic testing platform",
            "Try uploading data from 23andMe, AncestryDNA, or similar whole-genome platforms"
        ]
    elif "Profile file not found" in error_message:
        error_type = "Analysis Output Error"
        description = "The analysis completed but results could not be generated properly."
        suggestions = [
            "This appears to be a system error - please try uploading again",
            "If the problem persists, contact support"
        ]
    elif "timeout" in error_message.lower() or "connection" in error_message.lower():
        error_type = "Connection Error"
        description = "The analysis request timed out or lost connection to the processing server."
        suggestions = [
            "Check your internet connection and try again",
            "Large files may take longer to process - please wait a few minutes",
            "If the problem persists, try again later"
        ]
    else:
        error_type = "Analysis Error"
        description = "An unexpected error occurred during genetic data analysis."
        suggestions = [
            "Please check that your file is a valid VCF format",
            "Ensure the file is from a reputable genetic testing service",
            "Try uploading the file again"
        ]
    
    return html.Div([
        html.Div([
            html.I(className="fas fa-exclamation-triangle", 
                  style={'color': '#dc3545', 'fontSize': '24px', 'marginRight': '10px'}),
            html.H4(error_type, style={'color': '#dc3545', 'margin': '0', 'display': 'inline-block'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
        
        html.P(description, style={
            'color': '#666', 
            'fontSize': '16px', 
            'marginBottom': '15px',
            'lineHeight': '1.5'
        }),
        
        html.Div([
            html.H5("Suggestions to fix this issue:", style={
                'color': '#333', 
                'margin': '10px 0',
                'fontSize': '16px'
            }),
            html.Ul([
                html.Li(suggestion, style={'margin': '5px 0', 'color': '#555'}) 
                for suggestion in suggestions
            ], style={'paddingLeft': '20px'})
        ]),
        
        html.Details([
            html.Summary("Technical Details", style={
                'color': '#007bff', 
                'cursor': 'pointer',
                'margin': '15px 0 10px 0',
                'fontSize': '14px'
            }),
            html.Pre(error_message, style={
                'backgroundColor': '#f8f9fa',
                'padding': '10px',
                'borderRadius': '4px',
                'fontSize': '12px',
                'color': '#666',
                'overflowX': 'auto',
                'border': '1px solid #e9ecef'
            })
        ]),
        
        html.Div([
            html.Button('Try Again', 
                       id='error-try-again-button',
                       style={
                           **primary_button_style,
                           'marginTop': '15px'
                       })
        ])
        
    ], style={
        **card_style,
        'border': '2px solid #dc3545',
        'backgroundColor': '#fff5f5'
    })


def create_risk_results(plink_data=None, error_message=None):
    if error_message:
        return create_error_display(error_message)
    
    if plink_data:
        risk = plink_data.get('score', 0.0)
        sample_id = plink_data.get('id', 'Unknown')
        snps_used = plink_data.get('number_of_snps_used', 0)
        
        mean = 1.05
        std_dev = 0.94 
        
        np.random.seed(0)
        samples = np.random.normal(loc=mean, scale=std_dev, size=1000)
        risk_percentile = percentileofscore(samples, risk, kind='weak')
        risk_label = compute_risk_label(risk_percentile)
    else:
        return html.Div([
            html.H4(f"No uploaded data found", style={'color': '#dc3545', 'margin': '0 0 10px 0'}),
            html.P("Please upload your genetic data to analyze rheumatoid arthritis risk.", 
                   style={'color': '#666', 'margin': '0 0 10px 0'}) 
        ])

    return html.Div([
        html.Div([
            html.P(f"Analysis based on {snps_used} genetic variants", 
                   style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'})
        ]) if plink_data else "",

        html.Div([
            dcc.Graph(
                figure=plot_normal_hist(risk, samples, risk_percentile),
                config={'displayModeBar': False},
                style={'flex': '2', 'minWidth': '400px'}
            ),
            html.Div([
                html.P([
                    "Your risk is ",
                    html.B(risk_label, style={'color': risk_colors[risk_label]}),
                    ". It is higher than in ",
                    html.B(f"{math.floor(risk_percentile)}%"),
                    " of people."
                ], style={
                    'color': '#333',
                    'fontSize': '20px',
                    'lineHeight': '1.6',
                    'padding': '10px',
                    'border': '2px solid #ccc',
                    'borderRadius': '8px',
                    'backgroundColor': '#f9f9f9',
                    'boxShadow': '0px 0px 20px rgba(0,0,0,0.1)'
                })
            ], style={
                'flex': '1',
                'marginLeft': '10px',
                'display': 'flex',
                'alignItems': 'center',
                'zIndex': 10
            })
        ], style={'display': 'flex', 'flexDirection': 'row'}),

        html.Div([
            html.H5("Risk Factors Identified:", style={'margin': '15px 0 10px 0'}),
            html.Ul([
                html.Li("HLA-DRB1 gene variants associated with rheumatoid arthritis"),
                html.Li("PTPN22 polymorphisms linked to autoimmune conditions"),
                html.Li("IL-1 gene cluster variations affecting inflammation"),
                html.Li("COL1A1 variants related to cartilage integrity")
            ])
        ]) if risk_label in ['higher than average', 'high'] else "",

        html.Div([
            html.H5("Recommendations:", style={'margin': '15px 0 10px 0'}),
            html.Ul([
                html.Li("Consult with a rheumatologist for further evaluation"),
                html.Li("Consider regular joint health monitoring"),
                html.Li("Maintain healthy weight and regular exercise")
            ] if risk_label in ['higher than average', 'high'] else [
                html.Li("Maintain current healthy lifestyle"),
                html.Li("Regular exercise to maintain joint flexibility"),
                html.Li("Balanced diet rich in omega-3 fatty acids")
            ])
        ])
    ])


def create_variants_table(plink_data=None, error_message=None):

    if error_message:
        return html.Div()
    
    if plink_data:
        snps_total = plink_data.get('number_of_snps', 0)
        snps_used = plink_data.get('number_of_snps_used', 0)
        
        return html.Div([
            html.H5("Polygenic Risk Score Analysis Summary", style={'margin': '15px 0 10px 0'}),
            html.Div([
                html.P(f"Total SNPs found in your data: {snps_total:,}"),
                html.P(f"SNPs used in risk calculation: {snps_used:,}"),
                html.P(f"Coverage: {(snps_used/snps_total*100):.1f}%" if snps_total > 0 else "Coverage: N/A"),
                html.P("Risk score calculated using PGS002769 (Rheumatoid Arthritis)")
            ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ])
    
    variants_data = [
        {"Gene": "HLA-DRB1", "Variant": "rs2395029", "Risk Allele": "G", 
         "Your Genotype": random.choice(["GG", "GT", "TT"]), 
         "Effect": "Increased RA risk"},
        {"Gene": "PTPN22", "Variant": "rs2476601", "Risk Allele": "T", 
         "Your Genotype": random.choice(["TT", "TC", "CC"]), 
         "Effect": "Autoimmune susceptibility"},
        {"Gene": "IL1RN", "Variant": "rs419598", "Risk Allele": "T", 
         "Your Genotype": random.choice(["TT", "TC", "CC"]), 
         "Effect": "Inflammatory response"},
        {"Gene": "COL1A1", "Variant": "rs1800012", "Risk Allele": "T", 
         "Your Genotype": random.choice(["TT", "TC", "CC"]), 
         "Effect": "Cartilage structure"}
    ]
    
    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in variants_data[0].keys()],
        data=variants_data,
        style_table=table_style,
        style_cell=table_cell_style,
        style_header=table_header_style,
        style_data_conditional=[
            {
                'if': {'filter_query': '{Risk Allele} = {Your Genotype}'},
                'backgroundColor': '#ffe6e6',
                'color': 'black',
            }
        ]
    )

def create_variants_section():
    csv_path = Path(__file__).parent / "data" / "yet_another_final_PGS000195_metadata.csv"
    df = pd.read_csv(csv_path)
    fig = px.scatter(
        df,
        x='chr_position',
        y='effect_weight',
        hover_data={'chr_name': False, 'chr_position': True, 'effect_weight': True},
    )

    fig.update_traces(
        customdata=df.to_dict('records'),
        marker=dict(size=5, opacity=0.8, color='blue')
    )

    fig.update_layout(
        xaxis_title='Genomic Position',
        yaxis_title='Effect Weight',
        showlegend=False,
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white',
        margin=dict(t=40, b=30, l=50, r=10),
        height=500,
        width=800, 
        autosize=False
    )

    return html.Div([
        html.Div([
            dcc.Graph(
                id='prs-scatter',
                figure=fig,
                config={'displayModeBar': False, 'responsive': False},
                style={'width': '800px', 'height': '500px', 'flexShrink': 0}  
            ),
            html.Div([
                html.H4("Hovered Variant Info", style={'marginBottom': '8px', 'fontSize': '16px', 'color': '#333'}),
                dash_table.DataTable(
                    id='hover-info-table',
                    columns=[
                        {'name': col, 'id': col, 'presentation': 'markdown'} if col == 'LINK'
                        else {'name': col, 'id': col}
                        for col in df.columns if df[col].notna().any()
                    ],
                    data=[],
                    style_table={'maxHeight': '350px', 'overflowY': 'auto', 'fontSize': '16px'},
                    style_cell={'textAlign': 'left', 'padding': '2px', 'fontFamily': 'Arial', 'fontSize': '15px'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0', 'fontSize': '16px'},
                    markdown_options={'link_target': '_blank'},
                )
            ], id='hover-info-container')
        ], style={
            'position': 'relative',
            'width': '800px',
            'height': '650px'
        })
    ])


# def prediction_history_table(predictions):
#     if not predictions:
#         return html.Div("No analysis history available", style=text_style)

#     batches = {}
#     for prediction in predictions:
#         batch_key = (prediction["model_name"], prediction["timestamp"], prediction["cost"], prediction["id"])
#         if batch_key not in batches:
#             batches[batch_key] = []
#         batches[batch_key].extend(prediction.get('predictions', []))

#     batch_tables = []
#     for (model_name, timestamp, cost, _), preds in batches.items():
#         data = [
#             {
#                 "merchant_id": pred["features"]["merchant_id"],
#                 "cluster_id": pred["features"]["cluster_id"],
#                 "predicted_category_id": pred["target"]["category_id"],
#                 "predicted_category_label": pred["target"]["category_label"],
#             }
#             for pred in preds
#         ]

#         columns = [
#             {"name": "Merchant ID", "id": "merchant_id"},
#             {"name": "Cluster ID", "id": "cluster_id"},
#             {"name": "Predicted Category ID", "id": "predicted_category_id"},
#             {"name": "Predicted Category Label", "id": "predicted_category_label"},
#         ]

#         batch_info = html.Div([
#             html.H5(f"{model_name}, {format_timestamp(timestamp)}, Cost: {abs(cost)}", style=heading5_style),
#             dash_table.DataTable(
#                 columns=columns,
#                 data=data,
#                 style_table=table_style,
#                 style_cell=table_cell_style,
#                 style_header=table_header_style
#             )
#         ])

#         batch_tables.append(batch_info)

#     return html.Div(batch_tables)

def snp_dandelion_plot():
    return html.Div('Here be the SNP Dandelion Plot')

def top_10_snps():
    return html.Div('Here be the top_10_snps')


def prediction_layout(user_session):
    balance = fetch_user_balance(user_session)
    predictions = fetch_prediction_history(user_session)
    
    return html.Div([
        html.H1("Genetic Arthritis Risk Prediction", 
                style={'textAlign': 'center', 'color': '#333', 'marginBottom': '30px'}),
        
        html.Div(user_balance(balance), id='current-balance-predictions'),
        
        genetic_upload_form(),
        
        html.Div([
            html.H3("Risk Assessment Results", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='risk-results')
        ], style=card_style, id='results-section'),
        
        html.Div([
            html.H3("PRS Effect Weights Across Genome", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(create_variants_section())  
        ], style=card_style, id='variants-section'),

        html.Div([
            html.H3("snp_dandelion-plot", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='snp_dandelion-plot', style={'marginTop': '10px'})
        ], style=card_style, id='snp_dandelion-section'),



        # html.Div([
        #     html.H3("Analysis History", style={'color': '#333', 'marginBottom': '15px'}),
        #     html.Button('Clear History', id='clear-history-button', 
        #                style=secondary_button_style),
        #     html.Div(id='', style={'marginTop': '10px'}),
        #     #html.Div(prediction_history_table(predictions), id='prediction-history-table')
        # ], style=card_style)
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})