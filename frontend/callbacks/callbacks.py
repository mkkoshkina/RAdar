import json
import os
import base64
import math
from datetime import datetime
from json import JSONDecodeError

from dash import Output, Input, State, callback_context, ALL, dcc, html
from dash.exceptions import PreventUpdate

from frontend.data.local_data import authentificated_session
from frontend.data.remote_data import fetch_predictions_reports, fetch_users_report, fetch_credits_report
from frontend.data.remote_data import fetch_transaction_history, deposit_amount, send_prediction_request, \
    fetch_prediction_history, register_user, fetch_models, authenticate_user, fetch_user_balance, call_plink_prediction
from frontend.layouts.admin_layout import admin_layout
from frontend.layouts.admin_layout import users_report, predictions_report, credits_report
from frontend.layouts.billing_layout import billing_layout
from frontend.layouts.billing_layout import transaction_history_table
from frontend.layouts.prediction_layout import prediction_layout, \
    snp_dandelion_plot, create_risk_results, create_variants_section, card_style
from frontend.layouts.sign_in_layout import sign_in_layout
from frontend.layouts.sign_up_layout import sign_up_layout
from frontend.ui_kit.components.error_message import error_message
from frontend.ui_kit.components.navigation import navigation_bar
from frontend.ui_kit.components.user_balance import user_balance

from frontend.data.remote_data import send_chat_message

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
            return "Home page layout will be implemented"
        
        elif pathname == '/info':
            return "Info page layout will be implemented"
        
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


    @_app.callback(
        [Output('upload-status', 'children'),
         Output('analyze-button', 'disabled')],
        Input('upload-genetic-data', 'contents'),
        State('upload-genetic-data', 'filename')
    )
    def update_upload_status(contents, filename):
        if contents is None:
            return "", True
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            validation_errors = validate_vcf_file(filename, decoded)
            
            if validation_errors:
                error_list = "\\n".join([f"• {error}" for error in validation_errors])
                return dcc.Markdown(
                    f"❌ **File validation failed:**\\n{error_list}", 
                    style={'color': '#dc3545'}
                ), True
            
            file_size_mb = len(decoded) / (1024 * 1024)
            if file_size_mb > 100:
                return dcc.Markdown(
                    f"⚠️ **Large file uploaded:** {filename} ({file_size_mb:.1f} MB)\\n"
                    f"Analysis may take several minutes to complete.", 
                    style={'color': '#ffc107'}
                ), False
            
            return dcc.Markdown(f"✅ **File uploaded:** {filename}", style={'color': '#28a745'}), False
            
        except Exception as e:
            return dcc.Markdown(
                f"❌ **Error reading file:** {str(e)}", 
                style={'color': '#dc3545'}
            ), True

    @_app.callback(
        [Output('risk-results', 'children'),
         Output('variants-section', 'children'),
         Output('current-balance-predictions', 'children', allow_duplicate=True),
         Output('results-section', 'style'),
         Output('variants-section', 'style'),
         Output('snp_dandelion-section', 'style'),
         Output('pdf_report-section', 'style')],
        Input('analyze-button', 'n_clicks'),
        [State('upload-genetic-data', 'contents'),
         State('upload-genetic-data', 'filename'),
         State('user-session', 'data')],
        prevent_initial_call=True
    )
    def analyze_genetic_risk(n_clicks, contents, filename, user_session):
        if not contents or not user_session:
            raise PreventUpdate
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            validation_errors = validate_vcf_file(filename, decoded)
            if validation_errors:
                error_msg = f"File validation failed: {'; '.join(validation_errors)}"
                risk_results = create_risk_results(error_message=error_msg)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                return risk_results, create_variants_section(), user_balance(balance), visible_style, visible_style, visible_style, visible_style
            
            vcf_dir = 'input/vcf'
            os.makedirs(vcf_dir, exist_ok=True)
            
            vcf_path = os.path.join(vcf_dir, filename)
            with open(vcf_path, 'wb') as f:
                f.write(decoded)
            
            plink_result, error = call_plink_prediction(filename)
            
            if error:
                risk_results = create_risk_results(error_message=error)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                return risk_results, create_variants_section(), user_balance(balance), visible_style, visible_style, visible_style, visible_style
            
            if plink_result and plink_result.get('status') == 'success':
                plink_data = plink_result.get('results', [{}])[0] 
                risk_results = create_risk_results(plink_data)
            else:
                error_msg = plink_result.get('error', 'Unknown error')
                risk_results = create_risk_results(error_message=error_msg)
                balance = fetch_user_balance(user_session=user_session)
                visible_style = {**card_style, 'display': 'block'}
                return risk_results, create_variants_section(), user_balance(balance), visible_style, visible_style, visible_style, visible_style
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            risk_results = create_risk_results(error_message=error_msg)
            balance = fetch_user_balance(user_session=user_session)
            visible_style = {**card_style, 'display': 'block'}
            return risk_results, create_variants_section(), user_balance(balance), visible_style, visible_style, visible_style, visible_style
        
        balance = fetch_user_balance(user_session=user_session)
        visible_style = {**card_style, 'display': 'block'}
        
        return risk_results, create_variants_section(), user_balance(balance), visible_style, visible_style, visible_style, visible_style

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
                    html.I(className="fas fa-upload", style={'marginRight': '10px'}),
                    'Drag and Drop or Click to Select Genetic Data File'
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

    @app.callback(
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
        style = current_style or {}
        if button_id == 'open-chat-popup':
            style['display'] = 'block'
        elif button_id == 'chat-popup-close':
            style['display'] = 'none'
        return style

    @app.callback(
        Output('chat-history', 'value'),
        [Input('chat-send-btn', 'n_clicks')],
        [State('chat-input', 'value'),
        State('chat-history', 'value'),
        State('user-session', 'data')],
        prevent_initial_call=True
    )
    def update_chat(n_clicks, user_message, chat_history, user_session):
        if not user_message:
            raise PreventUpdate
        reply = send_chat_message(user_message, user_session)
        new_history = (chat_history or '') + f"\nYou: {user_message}\nBot: {reply}"
        return new_history
