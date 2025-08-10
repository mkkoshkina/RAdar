from dash import dcc, html
from frontend.ui_kit.styles import (
    primary_button_style, text_style, secondary_button_style, 
    card_style, theme_colors, heading1_style, heading2_style
)

INFO_MD = """
# Understanding Your Polygenic Risk Score (PGS)

Your genetic analysis has been completed using validated polygenic risk scores from PGS Catalog (**PGS000194/PGS000195**). This score represents your genetic predisposition to developing rheumatoid arthritis compared to the general population.

**Important:** Your genetic risk is probability-based, not predictive. Even high genetic risk does not mean you will definitely develop rheumatoid arthritis, and low risk does not guarantee you won't.

---

## LOW GENETIC RISK (0–20th percentile)

Your genetic predisposition to rheumatoid arthritis is lower than that of 80% of the population. While this suggests a reduced inherited susceptibility, environmental and lifestyle factors still play an important role in overall disease risk. Standard health monitoring and preventive care remain appropriate to maintain long-term joint and general health.

**Recommended Actions**

**For healthcare providers:**  
Standard age-appropriate medical surveillance should be maintained, with documentation of the patient’s PGS status in their medical records. It is important to monitor for symptom development over time and to apply the usual rheumatoid arthritis clinical assessment if symptoms appear.

**For patients:**  
Lifestyle management is a key component. Complete smoking cessation remains the most important modifiable risk factor. Maintaining a healthy weight within a BMI range of 18.5–24.9 is recommended, alongside regular dental care and treatment of any periodontal disease. A balanced diet rich in omega-3 fatty acids can help support overall health and potentially reduce inflammation.

Patients should remain aware of potential early symptoms of RA, such as morning joint stiffness lasting more than 30 minutes, symmetric pain or swelling in the hands or feet, and joint symptoms that persist for more than six weeks. If these symptoms develop, they should promptly contact their healthcare provider. Routine follow-up through standard preventive care visits is advised to ensure timely detection and intervention if needed.

---

## MODERATE GENETIC RISK (20–80th percentile)

Your genetic risk is within the typical population range, meaning your genetic predisposition is similar to that of most people. Nonetheless, enhanced prevention strategies can be beneficial, and closer attention to early symptoms is warranted.

**For healthcare providers:**  
Management should include clinical monitoring with a detailed family history assessment and baseline serological testing (RF, anti-CCP, CRP) if symptoms develop. If joint symptoms are present, the EULAR/ACR arthralgia risk criteria should be applied, and rheumatology referral considered for persistent arthralgia lasting more than six weeks. Documentation is important: record the patient’s PGS status, note modifiable risk factors, and establish a clear symptom monitoring protocol.

**For patients:**  
Enhanced prevention is key. Complete smoking cessation, ideally with professional support, is critical. Maintaining a BMI below 25, receiving professional periodontal care every six months, practicing stress management techniques, and following an anti-inflammatory Mediterranean-style diet can help reduce risk. Patients should actively monitor symptoms, keeping a diary if joint issues arise, and seek prompt evaluation for morning stiffness lasting more than 45 minutes or for any joint swelling or symmetric pain. Annual wellness visits should include discussion of joint health.

---

## HIGH GENETIC RISK (80–100th percentile)

Your genetic risk is significantly above average, meaning your genetic predisposition to rheumatoid arthritis is higher than that of 80% of the population. This level of risk warrants intensive prevention and close monitoring strategies, as early intervention can help prevent or delay disease onset. It is important to note that most people with a high genetic risk still never develop rheumatoid arthritis.

**For healthcare providers:**  
Specialized monitoring is recommended, including a rheumatology consultation within six months, a baseline comprehensive assessment with joint examination, and baseline serological testing (anti-CCP, RF, CRP, ESR). If symptoms are present, consider ultrasound, MRI evaluation and develop an individualized monitoring schedule. Maintain clinical vigilance with urgent evaluation for any joint symptoms lasting longer than two weeks, a low threshold for rheumatology referral, and application of EULAR/ACR arthralgia risk stratification criteria. Participation in research initiatives such as the STOP-RA or PRAIRI studies may also be considered. Documentation should include a comprehensive risk factor assessment, a clear monitoring and escalation plan, and records of patient education.

**For patients:**  
Maximum risk reduction is essential. Complete smoking cessation with medical support is a top priority. Additional preventive measures include professional nutrition consultation for weight management, comprehensive periodontal care, stress management (with professional counseling if needed), and participation in joint-protective physical activity programs. Patients should maintain heightened symptom awareness and seek immediate medical attention for morning stiffness lasting more than one hour, any joint swelling, symmetric joint pain, difficulty making a fist, or fatigue associated with joint symptoms.

---

### Key Takeaways

- Your genetic risk is one piece of the puzzle — lifestyle and environmental factors are equally important  
- Prevention works — smoking cessation and lifestyle modification can significantly reduce risk regardless of genetics  
- Early detection saves joints — prompt evaluation of symptoms leads to better outcomes  
- You have control — many factors influencing RA development are modifiable  
- Stay informed — RA prevention and treatment continue to improve

**Remember:** This genetic information empowers you to take proactive steps for your joint health. Work with your healthcare team to develop a personalized prevention and monitoring strategy that's right for you.
"""

def info_layout(user_session=None):
    # Enhanced styles for this page
    hero_section_style = {
        'background': f'linear-gradient(135deg, {theme_colors["primary"]} 0%, {theme_colors["primary_dark"]} 100%)',
        'color': 'white',
        'padding': '40px 20px',
        'borderRadius': '12px',
        'marginBottom': '30px',
        'textAlign': 'center',
        'boxShadow': '0 8px 32px rgba(37, 99, 235, 0.2)'
    }
    
    risk_card_style = {
        **card_style,
        'margin': '20px 0',
        'padding': '30px',
        'borderLeft': f'6px solid {theme_colors["primary"]}',
        'transition': 'all 0.3s ease',
    }
    
    low_risk_style = {
        **risk_card_style,
        'borderLeftColor': '#10b981',  # Green
        'backgroundColor': '#f0fdf4'
    }
    
    moderate_risk_style = {
        **risk_card_style,
        'borderLeftColor': '#f59e0b',  # Orange
        'backgroundColor': '#fffbeb'
    }
    
    high_risk_style = {
        **risk_card_style,
        'borderLeftColor': '#ef4444',  # Red
        'backgroundColor': '#fef2f2'
    }
    
    section_header_style = {
        'fontSize': '1.5rem',
        'fontWeight': '600',
        'color': theme_colors['text'],
        'marginBottom': '15px',
        'display': 'flex',
        'alignItems': 'center',
        'gap': '10px'
    }
    
    subsection_style = {
        'marginBottom': '20px',
        'padding': '15px',
        'backgroundColor': 'rgba(255, 255, 255, 0.7)',
        'borderRadius': '8px',
        'border': f'1px solid {theme_colors["border_light"]}'
    }
    
    key_points_style = {
        **card_style,
        'background': f'linear-gradient(45deg, {theme_colors["accent"]} 0%, #e6d3b7 100%)',
        'color': theme_colors['text'],
        'marginTop': '30px'
    }
    
    return html.Div([
        # Hero Section
        html.Div([
            html.H1("Understanding Your Polygenic Risk Score", 
                   style={'fontSize': '2.5rem', 'fontWeight': '700', 'marginBottom': '15px'}),
            html.P("Comprehensive genetic analysis using validated PGS Catalog scores (PGS000194/PGS000195)", 
                   style={'fontSize': '1.1rem', 'opacity': '0.9', 'marginBottom': '25px'}),
            html.Div([
                html.A(
                    html.Button([
                        html.I(className="fas fa-upload", style={'marginRight': '8px'}),
                        "Upload VCF File"
                    ], className='btn-primary', style={
                        **primary_button_style, 
                        'backgroundColor': 'white',
                        'color': theme_colors['primary'],
                        'fontWeight': '600',
                        'padding': '12px 24px',
                        'border': 'none',
                        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.15)',
                        'marginRight': '15px'
                    }, id="info-upload-cta"),
                    href="/analyze",
                ),
                html.A(
                    html.Button([
                        html.I(className="fas fa-home", style={'marginRight': '8px'}),
                        "Back to Home"
                    ], className='btn-secondary', style={
                        **secondary_button_style,
                        'backgroundColor': 'rgba(255, 255, 255, 0.2)',
                        'color': 'white',
                        'border': '2px solid white',
                        'fontWeight': '500',
                        'padding': '12px 24px'
                    }),
                    href="/",
                ),
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '10px'})
        ], style=hero_section_style),
        
        # Important Notice
        html.Div([
            html.Div([
                html.I(className="fas fa-info-circle", 
                      style={'color': theme_colors['info'], 'marginRight': '10px', 'fontSize': '1.2rem'}),
                html.Strong("Important: "),
                "Your genetic risk is probability-based, not predictive. Even high genetic risk does not mean you will definitely develop rheumatoid arthritis, and low risk does not guarantee you won't."
            ], style={
                'padding': '20px',
                'backgroundColor': '#e6f3ff',
                'border': f'1px solid {theme_colors["info"]}',
                'borderRadius': '8px',
                'marginBottom': '30px',
                'fontSize': '1.1rem',
                'display': 'flex',
                'alignItems': 'flex-start'
            })
        ]),
        
        # Low Risk Section
        html.Div([
            html.H2([
                html.Span("🟢", style={'marginRight': '10px', 'fontSize': '1.5rem'}),
                "LOW GENETIC RISK (0–20th percentile)"
            ], style=section_header_style),
            html.P("Your genetic predisposition to rheumatoid arthritis is lower than that of 80% of the population. While this suggests a reduced inherited susceptibility, environmental and lifestyle factors still play an important role in overall disease risk. Standard health monitoring and preventive care remain appropriate to maintain long-term joint and general health.", 
                   style={**text_style, 'marginBottom': '20px', 'fontSize': '1.05rem'}),
            
            html.Div([
                html.H4("👨‍⚕️ For Healthcare Providers:", style={'color': '#10b981', 'marginBottom': '10px'}),
                html.P("Standard age-appropriate medical surveillance should be maintained, with documentation of the patient's PGS status in their medical records. It is important to monitor for symptom development over time and to apply the usual rheumatoid arthritis clinical assessment if symptoms appear.", 
                       style=text_style)
            ], style=subsection_style),
            
            html.Div([
                html.H4("👤 For Patients:", style={'color': '#10b981', 'marginBottom': '10px'}),
                html.P("Lifestyle management is a key component. Complete smoking cessation remains the most important modifiable risk factor. Maintaining a healthy weight within a BMI range of 18.5–24.9 is recommended, alongside regular dental care and treatment of any periodontal disease. A balanced diet rich in omega-3 fatty acids can help support overall health and potentially reduce inflammation.", 
                       style=text_style),
                html.P("Patients should remain aware of potential early symptoms of RA, such as morning joint stiffness lasting more than 30 minutes, symmetric pain or swelling in the hands or feet, and joint symptoms that persist for more than six weeks. If these symptoms develop, they should promptly contact their healthcare provider. Routine follow-up through standard preventive care visits is advised to ensure timely detection and intervention if needed.", 
                       style=text_style)
            ], style=subsection_style)
        ], style=low_risk_style),
        
        # Moderate Risk Section
        html.Div([
            html.H2([
                html.Span("🟡", style={'marginRight': '10px', 'fontSize': '1.5rem'}),
                "MODERATE GENETIC RISK (20–80th percentile)"
            ], style=section_header_style),
            html.P("Your genetic risk is within the typical population range, meaning your genetic predisposition is similar to that of most people. Nonetheless, enhanced prevention strategies can be beneficial, and closer attention to early symptoms is warranted.", 
                   style={**text_style, 'marginBottom': '20px', 'fontSize': '1.05rem'}),
            
            html.Div([
                html.H4("👨‍⚕️ For Healthcare Providers:", style={'color': '#f59e0b', 'marginBottom': '10px'}),
                html.P("Management should include clinical monitoring with a detailed family history assessment and baseline serological testing (RF, anti-CCP, CRP) if symptoms develop. If joint symptoms are present, the EULAR/ACR arthralgia risk criteria should be applied, and rheumatology referral considered for persistent arthralgia lasting more than six weeks. Documentation is important: record the patient's PGS status, note modifiable risk factors, and establish a clear symptom monitoring protocol.", 
                       style=text_style)
            ], style=subsection_style),
            
            html.Div([
                html.H4("👤 For Patients:", style={'color': '#f59e0b', 'marginBottom': '10px'}),
                html.P("Enhanced prevention is key. Complete smoking cessation, ideally with professional support, is critical. Maintaining a BMI below 25, receiving professional periodontal care every six months, practicing stress management techniques, and following an anti-inflammatory Mediterranean-style diet can help reduce risk. Patients should actively monitor symptoms, keeping a diary if joint issues arise, and seek prompt evaluation for morning stiffness lasting more than 45 minutes or for any joint swelling or symmetric pain. Annual wellness visits should include discussion of joint health.", 
                       style=text_style)
            ], style=subsection_style)
        ], style=moderate_risk_style),
        
        # High Risk Section
        html.Div([
            html.H2([
                html.Span("🔴", style={'marginRight': '10px', 'fontSize': '1.5rem'}),
                "HIGH GENETIC RISK (80–100th percentile)"
            ], style=section_header_style),
            html.P("Your genetic risk is significantly above average, meaning your genetic predisposition to rheumatoid arthritis is higher than that of 80% of the population. This level of risk warrants intensive prevention and close monitoring strategies, as early intervention can help prevent or delay disease onset. It is important to note that most people with a high genetic risk still never develop rheumatoid arthritis.", 
                   style={**text_style, 'marginBottom': '20px', 'fontSize': '1.05rem'}),
            
            html.Div([
                html.H4("👨‍⚕️ For Healthcare Providers:", style={'color': '#ef4444', 'marginBottom': '10px'}),
                html.P("Specialized monitoring is recommended, including a rheumatology consultation within six months, a baseline comprehensive assessment with joint examination, and baseline serological testing (anti-CCP, RF, CRP, ESR). If symptoms are present, consider ultrasound, MRI evaluation and develop an individualized monitoring schedule. Maintain clinical vigilance with urgent evaluation for any joint symptoms lasting longer than two weeks, a low threshold for rheumatology referral, and application of EULAR/ACR arthralgia risk stratification criteria. Participation in research initiatives such as the STOP-RA or PRAIRI studies may also be considered. Documentation should include a comprehensive risk factor assessment, a clear monitoring and escalation plan, and records of patient education.", 
                       style=text_style)
            ], style=subsection_style),
            
            html.Div([
                html.H4("👤 For Patients:", style={'color': '#ef4444', 'marginBottom': '10px'}),
                html.P("Maximum risk reduction is essential. Complete smoking cessation with medical support is a top priority. Additional preventive measures include professional nutrition consultation for weight management, comprehensive periodontal care, stress management (with professional counseling if needed), and participation in joint-protective physical activity programs. Patients should maintain heightened symptom awareness and seek immediate medical attention for morning stiffness lasting more than one hour, any joint swelling, symmetric joint pain, difficulty making a fist, or fatigue associated with joint symptoms.", 
                       style=text_style)
            ], style=subsection_style)
        ], style=high_risk_style),
        
        # Key Takeaways Section
        html.Div([
            html.H2([
                html.I(className="fas fa-key", style={'marginRight': '10px', 'color': theme_colors['accent']}),
                "Key Takeaways"
            ], style={'fontSize': '1.8rem', 'fontWeight': '600', 'marginBottom': '20px', 'color': theme_colors['text']}),
            html.Ul([
                html.Li("Your genetic risk is one piece of the puzzle — lifestyle and environmental factors are equally important", style={'marginBottom': '8px'}),
                html.Li("Prevention works — smoking cessation and lifestyle modification can significantly reduce risk regardless of genetics", style={'marginBottom': '8px'}),
                html.Li("Early detection saves joints — prompt evaluation of symptoms leads to better outcomes", style={'marginBottom': '8px'}),
                html.Li("You have control — many factors influencing RA development are modifiable", style={'marginBottom': '8px'}),
                html.Li("Stay informed — RA prevention and treatment continue to improve", style={'marginBottom': '8px'})
            ], style={'fontSize': '1.1rem', 'lineHeight': '1.6', 'color': theme_colors['text']}),
            html.P([
                html.Strong("Remember: "),
                "This genetic information empowers you to take proactive steps for your joint health. Work with your healthcare team to develop a personalized prevention and monitoring strategy that's right for you."
            ], style={'fontSize': '1.1rem', 'marginTop': '20px', 'fontStyle': 'italic', 'color': theme_colors['text']})
        ], style=key_points_style)
        
    ], style={
        'maxWidth': '1000px', 
        'margin': '0 auto', 
        'padding': '20px',
        'fontFamily': 'Montserrat, sans-serif'
    })
