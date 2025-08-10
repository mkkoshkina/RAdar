import json
import os
import base64
import math
import requests  # Add this import
from datetime import datetime
from json import JSONDecodeError

from dash import Output, Input, State, callback_context, ALL, dcc, html
from dash.exceptions import PreventUpdate

from frontend.data.local_data import authentificated_session
from frontend.data.remote_data import fetch_predictions_reports, fetch_users_report, fetch_credits_report
from frontend.data.remote_data import fetch_transaction_history, deposit_amount, send_prediction_request, \
    fetch_prediction_history, register_user, fetch_models, authenticate_user, fetch_user_balance, call_plink_prediction, \
    analyze_rheumatoid_arthritis_risk, get_genetic_analysis_cost
from frontend.layouts.admin_layout import admin_layout
from frontend.layouts.admin_layout import users_report, predictions_report, credits_report
from frontend.layouts.billing_layout import billing_layout
from frontend.layouts.billing_layout import transaction_history_table
from frontend.layouts.home_layout import home_layout
from frontend.layouts.info_layout import info_layout
from frontend.layouts.prediction_layout import prediction_layout, \
    snp_dandelion_plot, create_risk_results, create_variants_section, card_style, create_drug_annotation_section, create_top_10_snps_section
from frontend.layouts.sign_in_layout import sign_in_layout
from frontend.layouts.sign_up_layout import sign_up_layout
from frontend.ui_kit.components.error_message import error_message
from frontend.ui_kit.components.navigation import navigation_bar
from frontend.ui_kit.components.user_balance import user_balance

from frontend.data.remote_data import send_chat_message
import uuid


# Add this line to get API_URL
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

sign_page_last_click_timestamp = datetime.now()


def register_callbacks(_app):
    @_app.callback(
        Output('user-session', 'data'),
        [
            Input('sign-in-session-update', 'data'),
            Input('sign-up-session-update', 'data'),
        ],
        State('user-session', 'data')
    )
    def manage_session(sign_in_data, sign_up_data,
                       current_session):
        ctx = callback_context

        if not ctx.triggered:
            return current_session
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'sign-in-session-update' and sign_in_data:
            return sign_in_data
        elif trigger_id == 'sign-up-session-update' and sign_up_data:
            return sign_up_data

        return current_session

    @_app.callback(
        Output('url', 'pathname'),
        [Input({'type': 'nav-button', 'index': ALL}, 'n_clicks_timestamp'),
         Input('user-session', 'data')],
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def manage_navigation(n_clicks_timestamp, user_session, pathname):
        global sign_page_last_click_timestamp
        ctx = callback_context

        if user_session and user_session.get('is_authenticated', False) and pathname in ['/sign-in', '/sign-up']:
            return '/prediction'
        else:
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if not button_id:
                raise PreventUpdate

            try:
                button_index = json.loads(button_id.replace('\'', '"'))['index']
            except JSONDecodeError:
                raise PreventUpdate

            click_timestamp = max(n_clicks_timestamp) if n_clicks_timestamp else None

            if click_timestamp and (datetime.now() - sign_page_last_click_timestamp).total_seconds() > 1:
                sign_page_last_click_timestamp = datetime.now()
                if button_index == 'sign-up':
                    return '/sign-up'
                elif button_index == 'sign-in':
                    return '/sign-in'
            else:
                raise PreventUpdate

    @_app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('user-session', 'data')]
    )
    def manage_page_content(pathname, user_session):
        if pathname == '/home' or pathname == '/':
            return home_layout(user_session)
        
        elif pathname == '/info':
            return info_layout(user_session)
        
        elif pathname == '/analyze':
            # For now, redirect to prediction page or create analyze layout
            if user_session and user_session.get('is_authenticated'):
                return prediction_layout(user_session)
            else:
                return dcc.Location(id='url', href='/sign-in', refresh=True)
        
        elif pathname == '/docs':
            return "Documentation page will be implemented"
        
        elif user_session and user_session.get('is_authenticated'):
            if pathname == '/prediction':
                return prediction_layout(user_session)
            elif pathname == '/billing':
                return billing_layout(user_session)
            elif pathname == '/admin':
                if user_session.get('is_superuser'):
                    return admin_layout()
                else:
                    return "403 Access Denied"
            else:
                return "404 Page Not Found"
        
        # Non-authenticated user pages
        else:
            if pathname == '/sign-in':
                return sign_in_layout()
            elif pathname == '/sign-up':
                return sign_up_layout()
            else:
                return dcc.Location(id='url', href='/home', refresh=True)

    @_app.callback(
        Output('nav-bar', 'children'),
        [Input('user-session', 'data')]
    )
    def manage_navigation_bar(user_session):
        return navigation_bar(user_session)

    @_app.callback(
        [
            Output('sign-in-session-update', 'data'),
            Output('sign-in-status', 'children'),
        ],
        [
            Input({'type': 'auth-button', 'action': 'sign-in'}, 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('sign-in-email', 'value'),
            State('sign-in-password', 'value'),
        ],
        prevent_initial_call=True
    )
    def sign_in_callback(sign_in_clicks, _, sign_in_email, sign_in_password):
        if sign_in_clicks > 0:
            user_data, error = authenticate_user(sign_in_email, sign_in_password)
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Sign in successful"
            return None, error_message(error if error else "Invalid credentials")
        raise PreventUpdate

    @_app.callback(
        [
            Output('sign-up-session-update', 'data'),
            Output('sign-up-status', 'children'),
        ],
        [
            Input({'type': 'auth-button', 'action': 'sign-up'}, 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('sign-up-email', 'value'),
            State('sign-up-password', 'value'),
            State('sign-up-name', 'value'),
        ],
        prevent_initial_call=True
    )
    def sign_up_callback(sign_up_clicks, _, sign_up_email, sign_up_password, sign_up_name):
        if sign_up_clicks > 0:
            user_data, error = register_user(sign_up_email, sign_up_password, sign_up_name)
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Registration successful"

            return {}, error_message(error if error else "Registration failed")

        raise PreventUpdate

    @_app.callback(
        [Output('users-report-div', 'children'),
         Output('predictions-report-div', 'children'),
         Output('credits-report-div', 'children')],
        [Input('refresh-button', 'n_clicks')],
        State('user-session', 'data'),
    )
    def manage_admin_reports(_, user_session):
        try:
            users_report_data = fetch_users_report(user_session=user_session)
            predictions_report_data = fetch_predictions_reports(user_session=user_session)
            credits_report_data = fetch_credits_report(user_session=user_session)
            return (users_report(users_report_data),
                    predictions_report(predictions_report_data),
                    credits_report(credits_report_data))
        except Exception as e:
            return (error_message("Error fetching users report: " + str(e)),
                    error_message("Error fetching predictions report: " + str(e)),
                    error_message("Error fetching credits report: " + str(e)))

    @_app.callback(
        [
            Output('deposit-amount', 'value'),
            Output('transaction-history-table', 'children'),
            Output('current-balance-billing', 'children')
        ],
        [
            Input('deposit-button', 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('deposit-amount', 'value'),
        ]
    )
    def manage_deposit(deposit_clicks, user_session, _deposit_amount):
        if deposit_clicks > 0 and _deposit_amount and _deposit_amount > 0:
            transaction_info = deposit_amount(_deposit_amount, user_session=user_session)

            if transaction_info:
                balance = fetch_user_balance(user_session=user_session)
                transactions = fetch_transaction_history(user_session=user_session)
                return "", transaction_history_table(
                    transactions), user_balance(balance)

        raise PreventUpdate

    @_app.callback(
        [Output('model-dropdown', 'options'),
         Output('model-dropdown', 'value'),
         ],
        Input('model-dropdown', 'options'),
        State('user-session', 'data')
    )
    def manage_models(_, user_session):
        models = fetch_models(user_session)
        dropdown_options = [{'label': model['name'], 'value': model['name']} for model in models]
        return dropdown_options, dropdown_options[0]['value']

    @_app.callback(
        [
            Output('prediction-history-table', 'children'),
            Output('current-balance-predictions', 'children')
        ],
        [
            Input('predict-button', 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
        ]
    )
    # def manage_predictions(n_clicks, user_session):
    #     if n_clicks > 0 and user_session:
    #         predictions = fetch_prediction_history(user_session=user_session)
    #         balance = fetch_user_balance(user_session=user_session)
    #         return prediction_history_table(predictions), user_balance(balance)

    #     raise PreventUpdate

    # Immediate loading state when file is selected
    @_app.callback(
        [Output('upload-icon', 'className', allow_duplicate=True),
         Output('upload-text', 'children', allow_duplicate=True),
         Output('upload-text', 'style', allow_duplicate=True)],
        Input('upload-genetic-data', 'contents'),
        prevent_initial_call=True
    )
    def show_immediate_loading(contents):
        if contents is not None:
            return ("fas fa-spinner fa-spin", 
                   "Processing file, please wait...", 
                   {'color': '#2563eb', 'fontWeight': '600'})
        raise PreventUpdate

    @_app.callback(
        [Output('upload-status', 'children'),
         Output('analyze-button', 'disabled'),
         Output('upload-icon', 'className'),
         Output('upload-text', 'children'),
         Output('upload-text', 'style')],
        Input('upload-genetic-data', 'contents'),
        State('upload-genetic-data', 'filename')
    )
    def update_upload_status(contents, filename):
        if contents is None:
            return "", True, "fas fa-upload", "Drag and Drop or Click to Select Genetic Data File", {}
        
        try:
            # Show loading state immediately while processing
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            validation_errors = validate_vcf_file(filename, decoded)
            
            if validation_errors:
                error_list = "\\n".join([f"• {error}" for error in validation_errors])
                return (dcc.Markdown(
                    f"❌ **File validation failed:**\\n{error_list}", 
                    style={'color': '#dc3545'}
                ), True, "fas fa-exclamation-triangle", "Upload failed - please try again", 
                {'color': '#dc2626', 'fontWeight': '600'})
            
            file_size_mb = len(decoded) / (1024 * 1024)
            if file_size_mb > 100:
                return (dcc.Markdown(
                    f"⚠️ **Large file uploaded:** {filename} ({file_size_mb:.1f} MB)\\n"
                    f"Analysis may take several minutes to complete.", 
                    style={'color': '#ffc107'}
                ), False, "fas fa-check-circle", f"Ready to analyze {filename}",
                {'color': '#059669', 'fontWeight': '600'})
            
            return (dcc.Markdown(f"✅ **File uploaded:** {filename}", style={'color': '#28a745'}), 
                   False, "fas fa-check-circle", f"Ready to analyze {filename}",
                   {'color': '#059669', 'fontWeight': '600'})
            
        except Exception as e:
            return (dcc.Markdown(
                f"❌ **Error reading file:** {str(e)}", 
                style={'color': '#dc3545'}
            ), True, "fas fa-exclamation-triangle", "Upload failed - please try again",
            {'color': '#dc2626', 'fontWeight': '600'})

    # Loading state callback for analyze button
    @_app.callback(
        Output('analyze-button', 'children'),
        Input('analyze-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_analyze_button_loading(n_clicks):
        if n_clicks:
            return [
                html.I(className="fas fa-spinner fa-spin", style={'marginRight': '8px'}),
                'Analyzing... Please wait'
            ]
        return [
            html.I(className="fas fa-dna", style={'marginRight': '8px'}),
            'Analyze Rheumatoid Arthritis Risk'
        ]

    @_app.callback(
        [Output('risk-results', 'children'),
         Output('variants-section-content', 'children'),
         Output('current-balance-predictions', 'children', allow_duplicate=True),
         Output('results-section', 'style'),
         Output('variants-section', 'style'),
         Output('snp_dandelion-section', 'style'),
         Output('snp_dandelion-plot', 'children'),
         Output('drug-annotation-section', 'style'),
         Output('drug-annotation-content', 'children'),
         Output('top-10-snps-section', 'style'),
         Output('top-10-snps-content', 'children'),
         Output('pdf_report-section', 'style'),
         Output('user-session', 'data', allow_duplicate=True),
         Output('analyze-button', 'children', allow_duplicate=True)],
        Input('analyze-button', 'n_clicks'),
        [State('upload-genetic-data', 'contents'),
         State('upload-genetic-data', 'filename'),
         State('user-session', 'data')],
        prevent_initial_call=True
    )
    def analyze_genetic_risk(n_clicks, contents, filename, user_session):
        if not contents or not user_session:
            raise PreventUpdate
        
        # Reset button content after analysis
        reset_button_content = [
            html.I(className="fas fa-dna", style={'marginRight': '8px'}),
            'Analyze Rheumatoid Arthritis Risk'
        ]
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            validation_errors = validate_vcf_file(filename, decoded)
            if validation_errors:
                error_msg = f"File validation failed: {'; '.join(validation_errors)}"
                risk_results = create_risk_results(error_message=error_msg)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                hidden_style = {**card_style, 'display': 'none'}
                sample_name = filename.replace('.vcf', '') if filename.endswith('.vcf') else filename
                return risk_results, create_variants_section(sample_name), user_balance(balance), visible_style, visible_style, visible_style, "", hidden_style, "", hidden_style, "", visible_style, user_session, reset_button_content
            
            plink_result, error = analyze_rheumatoid_arthritis_risk(decoded, filename, user_session)
            
            if error:
                risk_results = create_risk_results(error_message=error)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                hidden_style = {**card_style, 'display': 'none'}
                sample_name = filename.replace('.vcf', '') if filename.endswith('.vcf') else filename
                return risk_results, create_variants_section(sample_name), user_balance(balance), visible_style, visible_style, visible_style, "", hidden_style, "", hidden_style, "", visible_style, user_session, reset_button_content
            
            if plink_result and plink_result.get('status') == 'success':
                plink_data = plink_result.get('results', [{}])[0] 
                risk_results = create_risk_results(plink_data)
                
                sample_name = filename.replace('.vcf', '') if filename.endswith('.vcf') else filename
                drug_annotation_content = create_drug_annotation_section(sample_name)
                top_10_snps_content = create_top_10_snps_section(sample_name)
                variants_section_content = create_variants_section(sample_name)
                snp_dandelion_content = snp_dandelion_plot(sample_name)
                
                # Store prediction data in session for PDF generation
                updated_session = user_session.copy()
                updated_session['latest_sample_id'] = sample_name
                updated_session['latest_plink_data'] = plink_data
            else:
                error_msg = plink_result.get('error', 'Unknown error')
                risk_results = create_risk_results(error_message=error_msg)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                hidden_style = {**card_style, 'display': 'none'}
                sample_name = filename.replace('.vcf', '') if filename.endswith('.vcf') else filename
                return risk_results, create_variants_section(sample_name), user_balance(balance), visible_style, visible_style, visible_style, "", hidden_style, "", hidden_style, "", visible_style, user_session, reset_button_content
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            risk_results = create_risk_results(error_message=error_msg)
            balance = fetch_user_balance(user_session=user_session)
            visible_style = {**card_style, 'display': 'block'}
            hidden_style = {**card_style, 'display': 'none'}
            sample_name = filename.replace('.vcf', '') if filename.endswith('.vcf') else filename
            return risk_results, create_variants_section(sample_name), user_balance(balance), visible_style, visible_style, visible_style, "", hidden_style, "", hidden_style, "", visible_style, user_session, reset_button_content
        
        balance = fetch_user_balance(user_session=user_session)
        visible_style = {**card_style, 'display': 'block'}
        
        return risk_results, variants_section_content, user_balance(balance), visible_style, visible_style, visible_style, snp_dandelion_content, visible_style, drug_annotation_content, visible_style, top_10_snps_content, visible_style, updated_session, reset_button_content

    @_app.callback(
        Output('prediction-history-table', 'children', allow_duplicate=True),
        Input('clear-history-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_analysis_history(n_clicks):
        if n_clicks:
            return "Analysis history cleared."
        raise PreventUpdate

    @_app.callback(
        [Output('upload-genetic-data', 'children', allow_duplicate=True),
         Output('upload-status', 'children', allow_duplicate=True),
         Output('analyze-button', 'disabled', allow_duplicate=True)],
        Input('error-try-again-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_upload_on_error(n_clicks):
        if n_clicks:
            return (
                html.Div([
                    html.I(id='upload-icon', className="fas fa-upload", style={'marginRight': '10px'}),
                    html.Span(id='upload-text', children='Drag and Drop or Click to Select Genetic Data File', style={})
                ]),
                "",
                True
            )
        raise PreventUpdate

    def validate_vcf_file(filename, file_content):
        errors = []
        
        if not filename.lower().endswith('.vcf'):
            errors.append("File must have .vcf extension")
        
        try:
            content_str = file_content.decode('utf-8', errors='replace')
            lines = content_str.split('\n')
            
            if not any(line.startswith('##fileformat=VCF') for line in lines[:10]):
                errors.append("File does not appear to be a valid VCF format (missing VCF header)")
            
            header_line = None
            for line in lines:
                if line.startswith('#CHROM'):
                    header_line = line
                    break
            
            if not header_line:
                errors.append("VCF file is missing required column headers")
            else:
                required_columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']
                for col in required_columns:
                    if col not in header_line:
                        errors.append(f"VCF file is missing required column: {col}")
            
        except Exception as e:
            errors.append(f"Could not read file content: {str(e)}")
        
        return errors

    @_app.callback(
        Output('hover-info-table', 'data'),
        Input('prs-scatter', 'hoverData')
    )
    def show_hovered_variant(hoverData):
        if hoverData is None:
            return []

        point_data = hoverData['points'][0]['customdata']
        # Format effect_weight to 2 decimals if it's a valid number and not NaN
        if isinstance(point_data, dict):
            val = point_data.get('effect_weight')
            try:
                f = float(val)
                if not math.isnan(f):
                    point_data['effect_weight'] = f"{f:.2f}"
            except (TypeError, ValueError):
                pass
        return [point_data]


    @_app.callback(
        Output('hover-info-container', 'style'),
        Input('prs-scatter', 'hoverData')
    )
    def toggle_hover_info_visibility(hoverData):
        base_style = {
                'position': 'absolute',
                'top': '480px',
                'left': '10px',
                'padding': '8px',
                'border': '2px solid #333',
                'borderRadius': '8px',
                'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
                'width': '1100px',
                'zIndex': 1000,
                'display': None
            }

        
        if hoverData is None:
            base_style['display'] = 'none'
        else:
            base_style['display'] = 'block'
            
        return base_style

    # CONSOLIDATED CHAT CALLBACKS
# Replace the existing chat popup toggle callback with this improved version:

    @_app.callback(
        Output('chat-popup-container', 'style'),
        [Input('open-chat-popup', 'n_clicks'),
        Input('chat-popup-close', 'n_clicks')],
        [State('chat-popup-container', 'style')],
        prevent_initial_call=True
    )
    def toggle_chat_popup(open_clicks, close_clicks, current_style):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Get the current style or use default
        style = current_style.copy() if current_style else {
            'position': 'fixed',
            'bottom': '190px',  # Updated position
            'right': '20px',
            'width': '350px',
            'height': '500px',
            'background': 'white',
            'border': '1px solid #ccc',
            'borderRadius': '10px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
            'zIndex': 9999,
            'display': 'none'
        }
        
        if button_id == 'open-chat-popup':
            # Toggle the display
            if style.get('display') == 'none':
                style['display'] = 'block'
            else:
                style['display'] = 'none'
        elif button_id == 'chat-popup-close':
            style['display'] = 'none'
        
        return style


    @_app.callback(
        Output('chat-session-id', 'data'),
        Input('chat-session-id', 'data')
    )
    def initialize_chat_session(current_session_id):
        if not current_session_id:
            return str(uuid.uuid4())
        return current_session_id

    # CONSOLIDATED CHAT MESSAGE CALLBACK (handles both chat-display.children and chat-input.value)
    # Callback 1: Handle immediate user message display and input clearing
    @_app.callback(
        [Output('chat-display', 'children'),
        Output('chat-input', 'value'),
        Output('pending-message', 'data')],  # Store pending message for bot response
        [Input('send-button', 'n_clicks'),
        Input('chat-input', 'n_submit')],  # Handle Enter key
        [State('chat-input', 'value'),
        State('chat-display', 'children')],
        prevent_initial_call=True
    )
    def handle_user_message(send_clicks, n_submit, user_message, chat_history):
        if not user_message or not user_message.strip():
            raise PreventUpdate
        
        # Initialize chat_history if it's None
        if chat_history is None:
            chat_history = []
        
        # Add user message immediately
        user_msg_div = html.Div([
            html.Strong("You: ", style={'color': '#333'}),
            html.Span(user_message.strip())
        ], style={
            'margin': '5px 0', 
            'padding': '8px',
            'backgroundColor': '#e3f2fd',
            'borderRadius': '8px',
            'wordWrap': 'break-word'
        })
        chat_history.append(user_msg_div)
        
        # Add "Bot is typing..." indicator
        typing_div = html.Div([
            html.Strong("Mr. Think-think: ", style={'color': '#1976d2'}),
            html.Span("typing...", style={'fontStyle': 'italic', 'color': '#999'})
        ], style={
            'margin': '5px 0', 
            'padding': '8px',
            'backgroundColor': '#f5f5f5',
            'borderRadius': '8px',
            'animation': 'pulse 1.5s infinite'
        })
        chat_history.append(typing_div)
        
        # Return updated history, clear input, and store message for bot processing
        return chat_history, "", user_message.strip()

    # Callback 2: Handle bot response (triggered by pending message)
    @_app.callback(
        Output('chat-display', 'children', allow_duplicate=True),
        Input('pending-message', 'data'),
        [State('chat-display', 'children'),
        State('chat-session-id', 'data'),
        State('session-store', 'children')],
        prevent_initial_call=True
    )
    def handle_bot_response(pending_message, chat_history, chat_session_id, session_store):
        if not pending_message:
            raise PreventUpdate
        
        # Use session_store as backup if chat_session_id is None
        session_id = chat_session_id or session_store or str(uuid.uuid4())
        
        if chat_history is None:
            chat_history = []
        
        try:
            # Get response from agent
            reply = send_chat_message(pending_message, session_id)
            
            # Remove "typing..." indicator (should be the last message)
            if chat_history and len(chat_history) > 0:
                # Check if last message contains "typing..."
                last_msg = chat_history[-1]
                if hasattr(last_msg, 'children') and len(last_msg.children) > 1:
                    if "typing..." in str(last_msg.children[1].children):
                        chat_history.pop()
            
            # Add bot response
            bot_msg_div = html.Div([
                html.Strong("Mr. Think-Think: ", style={'color': '#1976d2'}),
                html.Span(reply)
            ], style={
                'margin': '5px 0', 
                'padding': '8px',
                'backgroundColor': '#e8f5e8',
                'borderRadius': '8px',
                'wordWrap': 'break-word'
            })
            chat_history.append(bot_msg_div)
            
            return chat_history
            
        except Exception as e:
            # Remove "typing..." indicator if it exists
            if chat_history and len(chat_history) > 0:
                last_msg = chat_history[-1]
                if hasattr(last_msg, 'children') and len(last_msg.children) > 1:
                    if "typing..." in str(last_msg.children[1].children):
                        chat_history.pop()
            
            # Add error message
            error_div = html.Div([
                html.Strong("Error: ", style={'color': '#d32f2f'}),
                html.Span(str(e))
            ], style={
                'margin': '5px 0', 
                'padding': '8px',
                'backgroundColor': '#ffebee',
                'borderRadius': '8px',
                'color': '#d32f2f',
                'wordWrap': 'break-word'
            })
            chat_history.append(error_div)
            return chat_history

    @_app.callback(
        Output('download-pdf-button', 'disabled'),
        [Input('risk-results', 'children')],
        prevent_initial_call=True
    )
    def enable_pdf_download(risk_results):
        if risk_results and len(risk_results) > 0:
            return False
        return True

    @_app.callback(
        Output('download-component', 'data'),
        [Input('download-pdf-button', 'n_clicks')],
        [State('user-session', 'data')],
        prevent_initial_call=True
    )
    def download_pdf_report(n_clicks, user_session):
        if not n_clicks or not user_session:
            raise PreventUpdate
        
        try:
            from frontend.services.pdf_service import pdf_generator
            
            sample_id = user_session.get('latest_sample_id')
            plink_data = user_session.get('latest_plink_data')
            
            if not sample_id or not plink_data:
                print("No sample_id or plink_data found in session")
                raise PreventUpdate
            
            pdf_b64 = pdf_generator.generate_pdf_report(plink_data, sample_id)
            
            if pdf_b64:
                return {
                    'content': pdf_b64,
                    'filename': f'rheumatoid_arthritis_report_{sample_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                    'type': 'application/pdf',
                    'base64': True
                }
            else:
                print("PDF generation returned None")
                raise PreventUpdate
                
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise PreventUpdate
