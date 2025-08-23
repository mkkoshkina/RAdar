from dash import dcc, dash_table, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px
from statistics import quantiles
from scipy.stats import percentileofscore
import math
import random
import base64
import os
from pathlib import Path

from frontend.data.remote_data import fetch_user_balance, fetch_prediction_history
from frontend.ui_kit.components.user_balance import user_balance
from frontend.ui_kit.styles import table_style, table_header_style, table_cell_style, input_style, \
    dropdown_style, secondary_button_style, text_style, heading5_style, primary_button_style, \
    card_style, upload_style
from frontend.ui_kit.utils import format_timestamp
from frontend.utils.i18n import t

risk_colors = {
    'low': '#28a745',
    'lower than average': '#28a745',
    'average': '#28a745',
    'higher than average': '#ffc107', 
    'high': '#dc3545'
}


def compute_risk_label(risk_percentile, lang: str = 'en'):
    if risk_percentile <= 10:
        label = t('low', lang)
    elif 10 < risk_percentile <= 40:
        label = t('lower_than_average', lang)
    elif 40 < risk_percentile <= 60:
        label = t('average', lang)
    elif 60 < risk_percentile <= 90:
        label = t('higher_than_average', lang)
    elif 90 < risk_percentile:
        label = t('high', lang)
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


def genetic_upload_form(lang: str = 'en'):
    return html.Div([
        html.H3(t("upload_genetic_data", lang), style={'color': '#333', 'marginBottom': '15px'}),
        html.P(t("upload_genetic_data_desc", lang), 
               style={'color': '#666', 'marginBottom': '10px'}),
        
        html.Div([
            html.I(className="fas fa-coins", style={'marginRight': '5px', 'color': '#ffc107'}),
            html.Span(t("cost_per_analysis", lang), 
                     style={'color': '#666', 'fontSize': '14px', 'fontWeight': 'bold'})
        ], style={'marginBottom': '15px', 'padding': '8px', 'backgroundColor': '#fff3cd', 
                 'border': '1px solid #ffeaa7', 'borderRadius': '4px'}),
        
        dcc.Upload(
            id='upload-genetic-data',
            children=html.Div([
                html.Span(id='upload-icon', children="📁", style={'marginRight': '10px', 'fontSize': '16px'}),
                html.Span(id='upload-text', children=t("drag_and_drop", lang), style={})
            ]),
            style=upload_style,
            multiple=False
        ),
        
        html.Div(id='upload-status', style={'margin': '10px 0'}),
        
        html.Button(
            children=[
                html.Span("🧬", style={'marginRight': '8px', 'fontSize': '16px'}),
                t("analyze_button_text", lang)
            ],
            id='analyze-button', 
            className='btn-primary', 
            style=primary_button_style, 
            disabled=True
        ),
        
    ], className='card', style=card_style)


def create_error_display(error_message, lang: str = 'en'):
    
    if "BCFtools filtering failed" in error_message:
        error_type = t("error_invalid_vcf", lang)
        description = t("error_invalid_vcf_desc", lang)
        suggestions = [
            t("suggestion_vcf_format", lang),
            t("suggestion_file_corruption", lang),
            t("suggestion_redownload", lang)
        ]
    elif "PLINK conversion failed" in error_message:
        error_type = t("error_vcf_processing", lang)
        description = t("error_vcf_processing_desc", lang)
        suggestions = [
            t("suggestion_genotype_info", lang),
            t("suggestion_vcf_specs", lang),
            t("suggestion_chromosome_info", lang)
        ]
    elif "PLINK PRS calculation failed" in error_message:
        error_type = t("error_risk_calculation", lang)
        description = t("error_risk_calculation_desc", lang)
        suggestions = [
            t("suggestion_insufficient_variants", lang),
            t("suggestion_compatible_platform", lang),
            t("suggestion_known_platforms", lang)
        ]
    elif "Profile file not found" in error_message:
        error_type = t("error_analysis_output", lang)
        description = t("error_analysis_output_desc", lang)
        suggestions = [
            t("suggestion_system_error", lang),
            t("suggestion_contact_support", lang)
        ]
    elif "timeout" in error_message.lower() or "connection" in error_message.lower():
        error_type = t("error_connection", lang)
        description = t("error_connection_desc", lang)
        suggestions = [
            t("suggestion_check_connection", lang),
            t("suggestion_large_files", lang),
            t("suggestion_try_later", lang)
        ]
    else:
        error_type = t("error_analysis", lang)
        description = t("error_analysis_desc", lang)
        suggestions = [
            t("suggestion_valid_vcf", lang),
            t("suggestion_reputable_service", lang),
            t("suggestion_try_again", lang)
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
            html.H5(t("suggestions_fix_issue", lang), style={
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
            html.Summary(t("technical_details", lang), style={
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
            html.Button(t('try_again', lang), 
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


def create_risk_results(plink_data=None, error_message=None, lang: str = 'en'):
    if error_message:
        return create_error_display(error_message, lang)
    
    if plink_data:
        risk = plink_data.get('score', 0.0)
        sample_id = plink_data.get('id', 'Unknown')
        snps_used = plink_data.get('number_of_alleles_detected', 0)
        
        mean = 1.05
        std_dev = 0.94 
        
        np.random.seed(0)
        samples = np.random.normal(loc=mean, scale=std_dev, size=1000)
        risk_percentile = percentileofscore(samples, risk, kind='weak')
        risk_label = compute_risk_label(risk_percentile, lang)
        
        # Determine color based on percentile, not translated text
        if risk_percentile <= 10:
            color_key = 'low'
        elif 10 < risk_percentile <= 40:
            color_key = 'lower than average'
        elif 40 < risk_percentile <= 60:
            color_key = 'average'
        elif 60 < risk_percentile <= 90:
            color_key = 'higher than average'
        else:
            color_key = 'high'
    else:
        return html.Div([
            html.H4(t("no_uploaded_data", lang), style={'color': '#dc3545', 'margin': '0 0 10px 0'}),
            html.P(t("upload_data_to_analyze", lang), 
                   style={'color': '#666', 'margin': '0 0 10px 0'}) 
        ])

    return html.Div([
        html.Div([
            html.P(f"{t('number_alleles_detected', lang)} {snps_used}", 
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
                    t("your_risk_is", lang) + " ",
                    html.B(risk_label, style={'color': risk_colors[color_key]}),
                    t("higher_than", lang) + " ",
                    html.B(f"{math.floor(risk_percentile)}"),
                    t("of_people", lang)
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
            html.H5(t("recommendations", lang), style={'margin': '15px 0 10px 0'}),
            html.Ul([
                html.Li(t("recommendation_1", lang)),
                html.Li(t("recommendation_2", lang)),
                html.Li(t("recommendation_3", lang)),
                html.Li(t("recommendation_4", lang))
            ] if color_key in ['higher than average', 'high'] else [
                html.Li(t("recommendation_low_1", lang)),
                html.Li(t("recommendation_low_2", lang)),
                html.Li(t("recommendation_low_3", lang)),
                html.Li(t("recommendation_low_4", lang))
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

def create_variants_section(sample, lang: str = 'en'):
    csv_path = 'input/annotations/yet_another_final_PGS000195_metadata.csv'
    tsv_path = f'output/{sample}_final_prs_table.tsv'

    df_metadata = pd.read_csv(csv_path)
    df_snps = pd.read_csv(tsv_path, sep='\t')

    df = pd.merge(df_metadata, df_snps, left_on='rsID', right_on='rsid', how='inner')

    if 'Sources' in df.columns:
        df['Sources'] = df['Sources'].apply(format_links)

    df['effect_weight_display'] = df['effect_size']  
    
    df = df[['Sources','rsID','Chromosome','Position','Effect allele','Other allele','Effect weight','effect_weight_display','Odds ratio','Gene symbol','Ensembl gene ID','Gene description']]

    df_display = df[['Sources','rsID','Chromosome','Position','Effect allele','Other allele','Effect weight','Odds ratio','Gene symbol','Ensembl gene ID','Gene description']]

    fig = px.scatter(
        df,
        x='Position',
        y='effect_weight_display',
        color='effect_weight_display',
        color_continuous_scale='RdYlBu_r',  
        hover_data={'Chromosome': False, 'Position': True, 'effect_weight_display': True},
        labels={'effect_weight_display': 'Effect Weight'}
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
                html.H5(t("understanding_results", lang), style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li(t("understanding_variants", lang)),
                    html.Li(t("understanding_position", lang)),
                    html.Li([t("understanding_color", lang) + " ", html.B(t("color_strong", lang)), ", ", html.B(t("color_weak", lang))]),
                    html.Li(t("understanding_hover", lang)),
                    html.Li(t("understanding_table", lang)),
                    html.Li([html.B(t("understanding_links", lang))])
                ], style={'color': '#666', 'fontSize': '14px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px',
                'marginTop': '20px',
                'border': '1px solid #e9ecef'
            })
    ])


def snp_dandelion_plot(sample, lang: str = 'en'):
    tsv_path = f'output/{sample}_final_prs_table.tsv'
    try:
        df = pd.read_csv(tsv_path, sep='\t')
        df_sorted = df.sort_values('effect_size', ascending=False).head(3)
        df_sorted = df_sorted.copy()
        df_sorted['effect_size'] = df_sorted['effect_size'].round(4)
        
        top_rs_ids = df_sorted['rsid'].tolist()
        
        image_components = []
        
        for i, rs_id in enumerate(top_rs_ids):
            image_path = f'input/images/{rs_id}.png'
            annotation_path = f'input/annotations/snps_annotations/{rs_id}.tsv'
            
            snp_components = []
            
            snp_components.extend([
                html.H4(f"#{i+1}: {rs_id}", style={
                    'textAlign': 'center', 
                    'margin': '10px 0', 
                    'color': '#333',
                    'fontSize': '18px'
                }),
                html.P(f"Effect size: {df_sorted[df_sorted['rsid'] == rs_id]['effect_size'].iloc[0]}", style={
                    'textAlign': 'center', 
                    'margin': '5px 0 15px 0', 
                    'color': '#666',
                    'fontSize': '14px',
                    'fontWeight': 'bold'
                })
            ])
            
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    encoded_image = base64.b64encode(f.read()).decode('ascii')
                
                snp_components.append(
                    html.Img(
                        src=f'data:image/png;base64,{encoded_image}',
                        style={
                            'width': '100%', 
                            'maxWidth': '800px', 
                            'height': 'auto',
                            'border': '2px solid #ddd',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'
                        }
                    )
                )
            else:
                snp_components.append(
                    html.Div([
                        html.P(f"Image not found: {rs_id}.png", style={
                            'color': '#999', 
                            'fontStyle': 'italic',
                            'margin': '20px'
                        })
                    ], style={
                        'border': '2px dashed #ccc',
                        'borderRadius': '8px',
                        'padding': '40px',
                        'backgroundColor': '#f8f9fa',
                        'textAlign': 'center',
                        'marginBottom': '20px'
                    })
                )
            
            if os.path.exists(annotation_path):
                try:
                    annotation_df = pd.read_csv(annotation_path, sep='\t')
                    
                    if 'NCBI Gene Page' in annotation_df.columns:
                        annotation_df['NCBI Gene Page'] = annotation_df['NCBI Gene Page'].apply(
                            lambda x: f"[Link]({x})" if pd.notna(x) and str(x).startswith('http') else x
                        )
                    if 'Genomic Browser' in annotation_df.columns:
                        annotation_df['Genomic Browser'] = annotation_df['Genomic Browser'].apply(
                            lambda x: f"[Link]({x})" if pd.notna(x) and str(x).startswith('http') else x
                        )
                    
                    snp_components.extend([
                        html.H5(f"Gene Annotations for {rs_id}", style={
                            'textAlign': 'center',
                            'margin': '15px 0 10px 0',
                            'color': '#333',
                            'fontSize': '16px'
                        }),
                        dash_table.DataTable(
                            columns=[
                                {'name': col, 'id': col, 'presentation': 'markdown'} 
                                if col in ['NCBI Gene Page', 'Genomic Browser'] 
                                else {'name': col, 'id': col}
                                for col in annotation_df.columns
                            ],
                            data=annotation_df.to_dict('records'),
                            style_table={
                                'maxHeight': '300px',
                                'overflowY': 'auto',
                                'overflowX': 'auto',
                                'fontSize': '14px',
                                'border': '1px solid #ddd',
                                'marginBottom': '15px'
                            },
                            style_cell={
                                'textAlign': 'left',
                                'padding': '8px',
                                'fontFamily': 'Arial',
                                'fontSize': '12px',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'minWidth': '100px'
                            },
                            style_header={
                                'fontWeight': 'bold',
                                'backgroundColor': '#f8f9fa',
                                'fontSize': '13px',
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
                                }
                            ],
                            markdown_options={'link_target': '_blank'}
                        )
                    ])
                except Exception as e:
                    snp_components.append(
                        html.P(f"Error loading annotations for {rs_id}: {str(e)}", style={
                            'color': '#dc3545',
                            'fontStyle': 'italic',
                            'textAlign': 'center',
                            'margin': '10px 0'
                        })
                    )
            else:
                snp_components.append(
                    html.P(f"There are no protein-coding genes located within a 200 kb radius of this SNP: {rs_id}", style={
                        'color': '#666',
                        'fontStyle': 'italic',
                        'textAlign': 'center',
                        'margin': '10px 0'
                    })
                )
            
            image_component = html.Div(
                snp_components,
                style={
                    'width': '100%',
                    'maxWidth': '800px', 
                    'margin': '20px 0', 
                    'textAlign': 'center',
                    'padding': '20px',
                    'border': '1px solid #e0e0e0',
                    'borderRadius': '10px',
                    'backgroundColor': '#fafafa'
                }
            )
            
            image_components.append(image_component)
        
        return html.Div([
            html.H3(t("top_3_snps_title", lang), style={
                'textAlign': 'center', 
                'margin': '20px 0 10px 0', 
                'color': '#333'
            }),
            html.P(t("regions_centered", lang), style={
                'textAlign': 'center',
                'margin': '0 0 0px 0',
                'color': '#0066cc',
                'fontSize': '14px',
                'fontStyle': 'italic'
            }),
            html.Div(image_components, style={
                'display': 'flex', 
                'flexDirection': 'column',
                'alignItems': 'center',
                'gap': '0px'
            })
        ])
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading SNP plots: {str(e)}", 
                   style={'color': '#dc3545', 'fontStyle': 'italic', 'textAlign': 'center'})
        ])



def create_top_10_snps_section(sample, lang: str = 'en'):
    
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
            html.P(t("showing_top_10_snps", lang), 
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
                html.H5(t("understanding_results", lang), style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li(t("effect_size_contribution", lang)),
                    html.Li(t("genotype_explanation", lang)),
                    html.Li(t("allele_frequency_explanation", lang)),
                    html.Li(t("snps_part_of_prs", lang))
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

def create_drug_annotation_section(sample, lang: str = 'en'):
    csv_path = f'output/{sample}_intersection_with_drug_annotation.csv'
    
    try:
        if not Path(csv_path).exists():
            return html.Div([
                html.P(f"Drug annotation file not found: {csv_path}", 
                       style={'color': '#dc3545', 'fontStyle': 'italic'})
            ])
        
        df = pd.read_csv(csv_path)

        original_columns = ['CHROM', 'POS', 'ID_x', 'REF', 'ALT', 'sample', 'Gene', 'Drugs', 'Phenotype Categories']
        available_original_columns = [col for col in original_columns if col in df.columns]
        
        if not available_original_columns:
            return html.Div([
                html.P("Required columns not found in the drug annotation file.", 
                       style={'color': '#dc3545', 'fontStyle': 'italic'})
            ])
        
        df.rename(columns={"CHROM": "Chromosome", "POS": "Position", "ID_x": "SNP ID", "REF": "Reference Allele", "ALT": "Alternate Allele", 'sample': 'Sample'}, inplace=True)
        
        renamed_columns = ['Chromosome', 'Position', 'SNP ID', 'Reference Allele', 'Alternate Allele', 'Sample', 'Gene', 'Drugs', 'Phenotype Categories']
        available_columns = [col for col in renamed_columns if col in df.columns]
        
        df_filtered = df[available_columns].copy()
        
        df_filtered = df_filtered.dropna(how='all')
        df_filtered = df_filtered[df_filtered['Sample'].str.contains('1/0|0/1|1/1', na=False)]

        if df_filtered.empty:
            return html.Div([
                html.P("No drug annotation data available for display.", 
                       style={'color': '#666', 'fontStyle': 'italic'})
            ])
        
        return html.Div([
            html.P(t("showing_drug_interactions", lang).format(count=len(df_filtered)), 
                   style={'marginBottom': '15px', 'color': '#666'}),
            
            html.Div([
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
                        'border': '1px solid #ddd',
                        'minWidth': '100%'
                    },
                    style_cell={
                        'textAlign': 'left', 
                        'padding': '8px', 
                        'fontFamily': 'Arial', 
                        'fontSize': '13px',
                        'whiteSpace': 'nowrap',  # Changed from 'normal' to 'nowrap' to prevent text wrapping
                        'height': 'auto',
                        'minWidth': '120px',  # Increased minimum width
                        'maxWidth': 'none',   # Removed max width restriction
                    },
                    style_header={
                        'fontWeight': 'bold', 
                        'backgroundColor': '#f8f9fa', 
                        'fontSize': '14px',
                        'border': '1px solid #ddd',
                        'whiteSpace': 'nowrap'  # Prevent header text from wrapping
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
                )
            ], style={'overflowX': 'auto', 'width': '100%'}),  # Added container with horizontal scroll
            
            html.Div([
                html.H5(t("understanding_results", lang), style={'margin': '20px 0 10px 0', 'color': '#333'}),
                html.Ul([
                    html.Li(t("drug_section_explanation", lang)),
                    html.Li(t("sample_column_explanation", lang)),
                    html.Li(t("drugs_column_explanation", lang)),
                    html.Li(t("phenotype_column_explanation", lang)),
                    html.Li(t("filter_sort_explanation", lang))
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

def prediction_layout(user_session, lang: str = 'en'):
    balance = fetch_user_balance(user_session)
    predictions = fetch_prediction_history(user_session)
    
    return html.Div([
        html.H1(t("prediction_title", lang), 
                style={'textAlign': 'center', 'color': '#333', 'marginBottom': '30px'}),
        
        html.Div(user_balance(balance), id='current-balance-predictions'),
        
        genetic_upload_form(lang),
        
        html.Div([
            html.H3(t("risk_assessment_results", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='risk-results')
        ], className='card', style={**card_style, 'display': 'none'}, id='results-section'),
        
        html.Div([
            html.H3(t("prs_effect_weights", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='variants-section-content')  
        ], className='card', style={**card_style, 'display': 'none'}, id='variants-section'),


        html.Div([
            html.H3(t("genomic_regions", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='snp_dandelion-plot', style={'marginTop': '10px'})
        ], className='card', style={**card_style, 'display': 'none'}, id='snp_dandelion-section'),


        html.Div([
            html.H3(t("drug_efficacy", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='drug-annotation-content')
        ], className='card', style={**card_style, 'display': 'none'}, id='drug-annotation-section'),

        html.Div([
            html.H3(t("top_10_snps", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Div(id='top-10-snps-content')
        ], className='card', style={**card_style, 'display': 'none'}, id='top-10-snps-section'),

        html.Div([
            html.H3(t("pdf_report", lang), style={'color': '#333', 'marginBottom': '15px'}),
            html.Button(t("download_pdf_report", lang), id='download-pdf-button', className='btn-primary', 
            style=primary_button_style, disabled=True),
            dcc.Download(id='download-component')
        ], className='card', style={**card_style, 'display': 'none'}, id='pdf_report-section')

        
        
        # html.Div([
        #     html.H3("Analysis History", style={'color': '#333', 'marginBottom': '15px'}),
        #     html.Button('Clear History', id='clear-history-button', 
        #                style=secondary_button_style),
        #     html.Div(id='', style={'marginTop': '10px'}),
        #     #html.Div(prediction_history_table(predictions), id='prediction-history-table')
        # ], style=card_style)
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})