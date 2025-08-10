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
    dropdown_style, secondary_button_style, text_style, heading5_style, primary_button_style, \
    card_style, upload_style
from frontend.ui_kit.utils import format_timestamp

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
        
        html.Button('Analyze Rheumatoid Arthritis Risk', id='analyze-button', className='btn-primary', 
                   style=primary_button_style, disabled=True),
        
    ], className='card', style=card_style)


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
                       id='error-try-again-button', className='btn-primary',
                       style={
                           **primary_button_style,
                           'marginTop': '15px'
                       })
        ])
        
    ], className='card', style={
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
        snps_used = plink_data.get('number_of_alleles_detected', 0)
        
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
            html.P(f"Number of alleles detected: {snps_used}", 
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
                html.Li("Maintain healthy weight and regular exercise"),
                html.Li("Avoid smoking")
            ] if risk_label in ['higher than average', 'high'] else [
                html.Li("Maintain current healthy lifestyle"),
                html.Li("Regular exercise to maintain joint flexibility"),
                html.Li("Balanced diet rich in omega-3 fatty acids"),
                html.Li("Avoid smoking")
            ])
        ])
    ])


def create_variants_table(plink_data=None, error_message=None):

    if error_message:
        return html.Div()
    
    if plink_data:
        snps_total = plink_data.get('number_of_alleles_observed', 0)
        snps_used = plink_data.get('number_of_alleles_detected', 0)
        
        return html.Div([
            html.H5("Polygenic Risk Score Analysis Summary", style={'margin': '15px 0 10px 0'}),
            html.Div([
                html.P(f"Total SNPs found in your data: {snps_total:,}"),
                html.P(f"SNPs used in risk calculation: {snps_used:,}"),
                html.P(f"Coverage: {(snps_used/snps_total*100):.1f}%" if snps_total > 0 else "Coverage: N/A"),
                html.P("Risk score calculated using PGS000195 (Rheumatoid Arthritis)")
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

def format_links(link_str):
    if pd.isna(link_str) or link_str.strip() == '':
        return ''
    links = link_str.split(';')
    formatted_links = []
    for i, url in enumerate(links):
        if not url.startswith('http'):
            url = 'https://' + url
        formatted_links.append(f"[{i+1}]({url})")
    return ' '.join(formatted_links)

def create_variants_section(sample):
    csv_path = 'input/annotations/yet_another_final_PGS000195_metadata.csv'
    tsv_path = f'output/{sample}_final_prs_table.tsv'

    df = pd.read_csv(csv_path)
    df_snps = pd.read_csv(tsv_path, sep='\t')

    df['is_in_sample'] = df['rsID'].isin(df_snps['rsid'])
    df['color'] = df['is_in_sample'].map({True: 'red', False: 'blue'})

    if 'Sources' in df.columns:
        df['Sources'] = df['Sources'].apply(format_links)

    df = df[['Sources','rsID','Chromosome','Position','Effect allele','Other allele','Effect weight','Odds ratio','Gene symbol','Ensembl gene ID','Gene description','color','is_in_sample']]

    df_display = df[['Sources','rsID','Chromosome','Position','Effect allele','Other allele','Effect weight','Odds ratio','Gene symbol','Ensembl gene ID','Gene description']]

    fig = px.scatter(
        df,
        x='Position',
        y='Effect weight',
        color='color',
        color_discrete_map={'red': 'red', 'blue': 'blue'},
        hover_data={'Chromosome': False, 'Position': True, 'Effect weight': True, 'color': False, 'is_in_sample': False},
    )

    fig.update_traces(
        customdata=df.to_dict('records'),
        marker=dict(size=5, opacity=0.8)
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
                html.H4("Variant Info", style={'marginBottom': '8px', 'fontSize': '16px', 'color': '#333'}),
                dash_table.DataTable(
                    id='hover-info-table',
                    columns=[
                        {'name': col, 'id': col, 'presentation': 'markdown'} if col == 'Sources'
                        else {'name': col, 'id': col}
                        for col in df_display.columns if df_display[col].notna().any()
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
        }),

        html.Div([
                html.H5("Understanding the Results:", style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li("This section shows the genetic variants associated with rheumatoid arthritis, each point represents a mutation"),
                    html.Li("The x-axis shows the genomic position of the variant, y-axis shows the effect size of the variant on rheumatoid arthritis risk"),
                    html.Li(["Red points indicate variants present in", html.B(" your genetic data")]),
                    html.Li("If you hover over a point, you will see more information about the variant"),
                    html.Li("The table below the plot shows detailed information about the variants, such as the gene name and symbol, chromosome, position and etc."),
                    html.Li([html.B("You can click on the links in the Sources column to learn more about each variant")])
                ], style={'color': '#666', 'fontSize': '14px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px',
                'marginTop': '20px',
                'border': '1px solid #e9ecef'
            })
    ])


def snp_dandelion_plot():
    return html.Div('Here be the SNP Dandelion Plot')

def create_top_10_snps_section(sample):
    
    tsv_path = f'output/{sample}_final_prs_table.tsv'
    
    try:
        if not tsv_path:
            return html.Div([
                html.P(f"Top 10 SNPs file not found for sample: {sample}", 
                       style={'color': '#dc3545', 'fontStyle': 'italic'})
            ])

        df = pd.read_csv(tsv_path, sep='\t')
        
        df_sorted = df.sort_values('effect_size', ascending=False).head(10)
        df_sorted = df_sorted.copy()
        df_sorted['effect_size'] = df_sorted['effect_size'].round(4)
        display_columns = {
            'rsid': 'SNP ID',
            'ref': 'Reference Allele',
            'effect_allele': 'Effect Allele', 
            'effect_size': 'Effect Size',
            'ALT_FREQS': 'Allele Frequency',
            'genotype': 'Your Genotype'
        }
        
        df_display = df_sorted.rename(columns=display_columns)
    
        return html.Div([
            html.P(f"Showing top 10 SNPs with highest effect sizes from your genetic analysis", 
                   style={'marginBottom': '15px', 'color': '#666'}),
            
            dash_table.DataTable(
                columns=[
                    {'name': col, 'id': col, 'type': 'numeric', 'format': {'specifier': '.4f'}} 
                    if col == 'Effect Size' else {'name': col, 'id': col}
                    for col in df_display.columns
                ],
                data=df_display.to_dict('records'),
                style_table={
                    'maxHeight': '400px', 
                    'overflowY': 'auto', 
                    'fontSize': '14px',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'textAlign': 'left', 
                    'padding': '10px', 
                    'fontFamily': 'Arial', 
                    'fontSize': '13px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px'
                },
                style_header={
                    'fontWeight': 'bold', 
                    'backgroundColor': '#f8f9fa', 
                    'fontSize': '14px',
                    'border': '1px solid #ddd',
                    'textAlign': 'center'
                },
                style_data={
                    'border': '1px solid #ddd'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    },
                    {
                        'if': {'column_id': 'Effect Size'},
                        'textAlign': 'right',
                        'fontWeight': 'bold',
                        'color': '#0066cc'
                    }
                ],
                sort_action="native"
            ),
            
            html.Div([
                html.H5("Understanding the Results:", style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li("Higher effect sizes indicate stronger contribution to rheumatoid arthritis risk"),
                    html.Li("Your genotype shows how many copies of the effect allele you carry (0, 1, or 2)"),
                    html.Li("Allele frequency represents how common this variant is in the population"),
                    html.Li("These SNPs are part of the polygenic risk score calculation")
                ], style={'color': '#666', 'fontSize': '14px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px',
                'marginTop': '20px',
                'border': '1px solid #e9ecef'
            })
        ])
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading top 10 SNPs: {str(e)}", 
                   style={'color': '#dc3545', 'fontStyle': 'italic'})
        ])

# def create_variants_table(plink_data=None, error_message=None):

#     if error_message:
#         return html.Div()
    
#     if plink_data:
#         snps_total = plink_data.get('number_of_alleles_observed', 0)
#         snps_used = plink_data.get('number_of_alleles_detected', 0)
        
#         return html.Div([
#             html.H5("Polygenic Risk Score Analysis Summary", style={'margin': '15px 0 10px 0'}),
#             html.Div([
#                 html.P(f"Total SNPs found in your data: {snps_total:,}"),
#                 html.P(f"SNPs used in risk calculation: {snps_used:,}"),
#                 html.P(f"Coverage: {(snps_used/snps_total*100):.1f}%" if snps_total > 0 else "Coverage: N/A"),
#                 html.P("Risk score calculated using PGS002769 (Rheumatoid Arthritis)")
#             ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
#         ])
    
#     variants_data = [
#         {"Gene": "HLA-DRB1", "Variant": "rs2395029", "Risk Allele": "G", 
#          "Your Genotype": random.choice(["GG", "GT", "TT"]), 
#          "Effect": "Increased RA risk"},
#         {"Gene": "PTPN22", "Variant": "rs2476601", "Risk Allele": "T", 
#          "Your Genotype": random.choice(["TT", "TC", "CC"]), 
#          "Effect": "Autoimmune susceptibility"},
#         {"Gene": "IL1RN", "Variant": "rs419598", "Risk Allele": "T", 
#          "Your Genotype": random.choice(["TT", "TC", "CC"]), 
#          "Effect": "Inflammatory response"},
#         {"Gene": "COL1A1", "Variant": "rs1800012", "Risk Allele": "T", 
#          "Your Genotype": random.choice(["TT", "TC", "CC"]), 
#          "Effect": "Cartilage structure"}
#     ]
    
#     return dash_table.DataTable(
#         columns=[{"name": col, "id": col} for col in variants_data[0].keys()],
#         data=variants_data,
#         style_table=table_style,
#         style_cell=table_cell_style,
#         style_header=table_header_style,
#         style_data_conditional=[
#             {
#                 'if': {'filter_query': '{Risk Allele} = {Your Genotype}'},
#                 'backgroundColor': '#ffe6e6',
#                 'color': 'black',
#             }
#         ]
#     )

def create_drug_annotation_section(sample):
    csv_path = f'output/{sample}_intersection_with_drug_annotation.csv'
    
    try:
        if not Path(csv_path).exists():
            return html.Div([
                html.P(f"Drug annotation file not found: {csv_path}", 
                       style={'color': '#dc3545', 'fontStyle': 'italic'})
            ])
        
        df = pd.read_csv(csv_path)

        required_columns = ['CHROM', 'POS', 'ID_x', 'REF', 'ALT', 'sample', 'Gene', 'Drugs', 'Phenotype Categories']
        df.rename(columns={"CHROM": "Chromosome", "POS": "Position", "ID_x": "SNP ID", "REF": "Reference Allele", "ALT": "Alternate Allele"}, inplace=True)
        available_columns = [col for col in required_columns if col in df.columns]
        
        if not available_columns:
            return html.Div([
                html.P("Required columns not found in the drug annotation file.", 
                       style={'color': '#dc3545', 'fontStyle': 'italic'})
            ])
        
        df_filtered = df[available_columns].copy()
        
        df_filtered = df_filtered.dropna(how='all')
        df_filtered = df_filtered[df_filtered['sample'].str.contains('1/0|0/1|1/1', na=False)]

        if df_filtered.empty:
            return html.Div([
                html.P("No drug annotation data available for display.", 
                       style={'color': '#666', 'fontStyle': 'italic'})
            ])
        
        return html.Div([
            html.P(f"Showing {len(df_filtered)} drug-gene interactions from your genetic data", 
                   style={'marginBottom': '15px', 'color': '#666'}),
            
            dash_table.DataTable(
                columns=[
                    {'name': col, 'id': col} for col in df_filtered.columns
                ],
                data=df_filtered.to_dict('records'),
                style_table={
                    'maxHeight': '400px', 
                    'overflowY': 'auto',
                    'overflowX': 'auto',
                    'fontSize': '14px',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'textAlign': 'left', 
                    'padding': '8px', 
                    'fontFamily': 'Arial', 
                    'fontSize': '13px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                    'maxWidth': '200px',
                },
                style_header={
                    'fontWeight': 'bold', 
                    'backgroundColor': '#f8f9fa', 
                    'fontSize': '14px',
                    'border': '1px solid #ddd'
                },
                style_data={
                    'border': '1px solid #ddd'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                page_size=20,  
                sort_action="native", 
                filter_action="native" 
            ),
            
            html.Div([
                html.H5("Understanding the Results:", style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li("This section shows genetic variants found in your data associated with drug efficacy and toxicity"),
                    html.Li("The column sample shows your genotype for each variant. 1/1 - both alleles are present, 1/0 or 0/1 - one allele is present"),
                    html.Li("The column Drugs shows the drugs that may be affected by these variants"),
                    html.Li("The column Phenotype Categories shows the type of effect the variant has on drug response"),
                    html.Li("You can fillter and sort the table to find specific variants or drugs")
                ], style={'color': '#666', 'fontSize': '14px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px',
                'marginTop': '20px',
                'border': '1px solid #e9ecef'
            })
        ])
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading drug annotation data: {str(e)}", 
                   style={'color': '#dc3545', 'fontStyle': 'italic'})
        ])

def prediction_layout(user_session):
    balance = fetch_user_balance(user_session)
    predictions = fetch_prediction_history(user_session)
    
    return html.Div([
        html.H1("Rheumatoid Arthritis Polygenic Risk Score Prediction", 
                style={'textAlign': 'center', 'color': '#333', 'marginBottom': '30px'}),
        
        html.Div(user_balance(balance), id='current-balance-predictions'),
        
        genetic_upload_form(),
        
        html.Div([
            html.H3("Your Polygenic Risk Assessment Results", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='risk-results')
        ], className='card', style={**card_style, 'display': 'none'}, id='results-section'),
        
        html.Div([
            html.H3("PRS Effect Weights Across Genome", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='variants-section-content')  
        ], className='card', style={**card_style, 'display': 'none'}, id='variants-section'),

        html.Div([
            html.H3("snp_dandelion-plot", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='snp_dandelion-plot', style={'marginTop': '10px'})
        ], className='card', style={**card_style, 'display': 'none'}, id='snp_dandelion-section'),

        html.Div([
            html.H3("Mutations Responsible For Drug Efficacy and Toxicity", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='drug-annotation-content')
        ], className='card', style={**card_style, 'display': 'none'}, id='drug-annotation-section'),

        html.Div([
            html.H3("Top 10 Most Influential SNPs", style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='top-10-snps-content')
        ], className='card', style={**card_style, 'display': 'none'}, id='top-10-snps-section'),

        html.Div([
            html.H3("PDF report", style={'color': '#333', 'marginBottom': '15px'}),
            html.Button('Download PDF Report', id='download-pdf-button', className='btn-primary', 
            style=primary_button_style, disabled=True),
        ], className='card', style={**card_style, 'display': 'none'}, id='pdf_report-section')

        
        
        # html.Div([
        #     html.H3("Analysis History", style={'color': '#333', 'marginBottom': '15px'}),
        #     html.Button('Clear History', id='clear-history-button', 
        #                style=secondary_button_style),
        #     html.Div(id='', style={'marginTop': '10px'}),
        #     #html.Div(prediction_history_table(predictions), id='prediction-history-table')
        # ], style=card_style)
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})