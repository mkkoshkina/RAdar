import base64
import os
import tempfile
import warnings
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io

# Suppress pandas FutureWarnings related to groupby operations
warnings.filterwarnings("ignore", category=FutureWarning, message=".*grouping with a length-1 list-like.*")

from frontend.layouts.prediction_layout import (
    plot_normal_hist, 
    compute_risk_label, 
    risk_colors
)
from statistics import quantiles
from scipy.stats import percentileofscore
import numpy as np


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#007bff')
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#007bff')
        )
        
    def generate_pdf_report(self, plink_data, sample_id):
        try:
            risk = plink_data.get('score', 0.0)
            snps_used = plink_data.get('number_of_alleles_detected', 0)
            snps_total = plink_data.get('number_of_alleles_observed', 0)
            
            mean = 1.05
            std_dev = 0.94
            np.random.seed(0)
            samples = np.random.normal(loc=mean, scale=std_dev, size=1000)
            risk_percentile = percentileofscore(samples, risk, kind='weak')
            risk_label = compute_risk_label(risk_percentile)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
                story = []
                
                # Title
                story.append(Paragraph("Rheumatoid Arthritis Risk Assessment Report", self.title_style))
                story.append(Spacer(1, 12))
                
                # Basic info
                story.append(Paragraph(f"<b>Sample ID:</b> {sample_id}", self.styles['Normal']))
                story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Risk summary
                story.append(Paragraph("Risk Assessment Summary", self.heading_style))
                risk_color = risk_colors.get(risk_label, '#333333')
                story.append(Paragraph(f"<b>Your risk is {risk_label}. It is higher than {int(risk_percentile)}% of people.</b>", self.styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Summary table
                summary_data = [
                    ['Risk Score', f'{risk:.4f}'],
                    ['Total SNPs in your data', f'{snps_total:,}'],
                    ['SNPs used in calculation', f'{snps_used:,}'],
                    ['Coverage', f'{(snps_used/snps_total*100):.1f}%' if snps_total > 0 else 'N/A']
                ]
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 20))
                
                # Risk distribution plot
                try:
                    risk_plot_img = self._generate_risk_plot(risk, samples, risk_percentile)
                    if risk_plot_img:
                        story.append(Paragraph("Risk Distribution", self.heading_style))
                        story.append(Paragraph("This chart shows where your risk score falls within the population distribution.", self.styles['Normal']))
                        story.append(Spacer(1, 12))
                        story.append(risk_plot_img)
                        story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error adding risk plot: {str(e)}")
                
                # Scatter plot
                try:
                    scatter_plot_img = self._generate_scatter_plot(sample_id)
                    if scatter_plot_img:
                        story.append(Paragraph("PRS Effect Weights Across Genome", self.heading_style))
                        story.append(Paragraph("This scatter plot shows the effect weights of genetic variants across the genome. Red points indicate variants present in your genetic data.", self.styles['Normal']))
                        story.append(Spacer(1, 12))
                        story.append(scatter_plot_img)
                        story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error adding scatter plot: {str(e)}")
                
                # Top SNPs table
                try:
                    top_snps_data = self._get_top_snps_data(sample_id)
                    if top_snps_data:
                        story.append(Paragraph("Top 10 Most Influential SNPs", self.heading_style))
                        story.append(Paragraph("These are the genetic variants with the highest effect sizes in your risk calculation.", self.styles['Normal']))
                        story.append(Spacer(1, 12))
                        
                        snp_table_data = [['SNP ID', 'Reference Allele', 'Effect Allele', 'Effect Size', 'Your Genotype']]
                        for snp in top_snps_data[:10]:  # Limit to 10 for space
                            snp_table_data.append([
                                snp.get('rsid', 'N/A'),
                                snp.get('ref', 'N/A'),
                                snp.get('effect_allele', 'N/A'),
                                f"{snp.get('effect_size', 0):.4f}",
                                snp.get('genotype', 'N/A')
                            ])
                        
                        snp_table = Table(snp_table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                        snp_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(snp_table)
                        story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error adding SNPs table: {str(e)}")
                
                # Drug interactions table
                try:
                    drug_data = self._get_drug_annotation_data(sample_id)
                    if drug_data:
                        story.append(Paragraph("Drug-Gene Interactions", self.heading_style))
                        story.append(Paragraph("These genetic variants may affect drug efficacy and toxicity.", self.styles['Normal']))
                        story.append(Spacer(1, 12))
                        
                        drug_table_data = [['SNP ID', 'Gene', 'Drugs', 'Your Genotype']]
                        for drug in drug_data[:5]:  # Limit to 5 for space
                            drug_table_data.append([
                                drug.get('ID_x', 'N/A'),
                                drug.get('Gene', 'N/A'),
                                drug.get('Drugs', 'N/A')[:30] + '...' if len(str(drug.get('Drugs', 'N/A'))) > 30 else drug.get('Drugs', 'N/A'),
                                drug.get('sample', 'N/A')
                            ])
                        
                        drug_table = Table(drug_table_data, colWidths=[1.2*inch, 1*inch, 2*inch, 1*inch])
                        drug_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(drug_table)
                        story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error adding drug table: {str(e)}")
                
                # Recommendations
                story.append(Paragraph("Recommendations", self.heading_style))
                if risk_label in ['higher than average', 'high']:
                    recommendations = [
                        "• Consult with a rheumatologist for further evaluation",
                        "• Consider regular joint health monitoring",
                        "• Maintain healthy weight and regular exercise",
                        "• Avoid smoking"
                    ]
                else:
                    recommendations = [
                        "• Maintain current healthy lifestyle",
                        "• Regular exercise to maintain joint flexibility",
                        "• Balanced diet rich in omega-3 fatty acids",
                        "• Avoid smoking"
                    ]
                
                for rec in recommendations:
                    story.append(Paragraph(rec, self.styles['Normal']))
                
                story.append(Spacer(1, 20))
                
                story.append(Paragraph("This report is for informational purposes only and should not replace professional medical advice.", self.styles['Italic']))
                story.append(Paragraph("Generated by RAdar - Rheumatoid Arthritis Risk Assessment System", self.styles['Italic']))
                
                doc.build(story)
                
                with open(tmp_file.name, 'rb') as f:
                    pdf_content = f.read()
                
                os.unlink(tmp_file.name)
                
                return base64.b64encode(pdf_content).decode('utf-8')
                
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            return None
    
    def _generate_risk_plot(self, risk, samples, risk_percentile):
        try:
            # Check if kaleido is available for image export
            try:
                import kaleido
            except ImportError:
                print("Warning: kaleido package not available. Skipping risk plot generation.")
                return None
            
            fig = plot_normal_hist(risk, samples, risk_percentile)
            
            img_bytes = pio.to_image(fig, format="png", width=600, height=400)
            
            img_buffer = io.BytesIO(img_bytes)
            img = Image(img_buffer, width=5*inch, height=3.3*inch)
            return img
        except Exception as e:
            print(f"Error generating risk plot: {str(e)}")
            return None
    
    def _generate_scatter_plot(self, sample_id):
        try:
            # Check if kaleido is available for image export
            try:
                import kaleido
            except ImportError:
                print("Warning: kaleido package not available. Skipping scatter plot generation.")
                return None
                
            import plotly.express as px
            
            csv_path = 'input/annotations/yet_another_final_PGS000195_metadata.csv'
            tsv_path = f'output/{sample_id}_final_prs_table.tsv'
            
            if not (Path(csv_path).exists() and Path(tsv_path).exists()):
                return None
            
            df = pd.read_csv(csv_path)
            df_snps = pd.read_csv(tsv_path, sep='\t')
            
            df['is_in_sample'] = df['rsID'].isin(df_snps['rsid'])
            df['color'] = df['is_in_sample'].map({True: 'red', False: 'blue'})
            
            fig = px.scatter(
                df,
                x='Position',
                y='Effect weight',
                color='color',
                color_discrete_map={'red': 'red', 'blue': 'blue'},
                title='PRS Effect Weights Across Genome'
            )
            
            fig.update_layout(
                xaxis_title='Genomic Position',
                yaxis_title='Effect Weight',
                showlegend=False,
                xaxis=dict(showticklabels=False),
                plot_bgcolor='white',
                width=600,
                height=400
            )
            
            img_bytes = pio.to_image(fig, format="png", width=600, height=400)
            
            img_buffer = io.BytesIO(img_bytes)
            img = Image(img_buffer, width=5*inch, height=3.3*inch)
            return img
            
        except Exception as e:
            print(f"Error generating scatter plot: {str(e)}")
            return None
    
    def _get_top_snps_data(self, sample_id):
        try:
            tsv_path = f'output/{sample_id}_final_prs_table.tsv'
            if not Path(tsv_path).exists():
                return []
            
            df = pd.read_csv(tsv_path, sep='\t')
            df_sorted = df.sort_values('effect_size', ascending=False).head(10)
            df_sorted = df_sorted.copy()
            df_sorted['effect_size'] = df_sorted['effect_size'].round(4)
            
            return df_sorted.to_dict('records')
            
        except Exception as e:
            print(f"Error getting top SNPs data: {str(e)}")
            return []
    
    def _get_drug_annotation_data(self, sample_id):
        try:
            csv_path = f'output/{sample_id}_intersection_with_drug_annotation.csv'
            if not Path(csv_path).exists():
                return []
            
            df = pd.read_csv(csv_path)
            df_filtered = df[df['sample'].str.contains('1/0|0/1|1/1', na=False)]
            
            return df_filtered.head(10).to_dict('records') 
            
        except Exception as e:
            print(f"Error getting drug annotation data: {str(e)}")
            return []


pdf_generator = PDFReportGenerator()
