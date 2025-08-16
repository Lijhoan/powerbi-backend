import requests
import json
from datetime import datetime, timedelta
from flask import current_app

class PowerBIService:
    
    @staticmethod
    def get_access_token():
        """Get access token for Power BI API"""
        try:
            tenant_id = current_app.config['POWERBI_TENANT_ID']
            client_id = current_app.config['POWERBI_CLIENT_ID']
            client_secret = current_app.config['POWERBI_CLIENT_SECRET']
            
            if not all([tenant_id, client_id, client_secret]):
                # Return mock token for development
                return "mock-powerbi-access-token"
            
            url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default'
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                current_app.logger.error(f"Failed to get Power BI token: {response.text}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error getting Power BI token: {str(e)}")
            return None
    
    @staticmethod
    def generate_embed_token(report_id=None, user_permissions=None):
        """Generate embed token for Power BI report"""
        try:
            access_token = PowerBIService.get_access_token()
            
            if not access_token or access_token == "mock-powerbi-access-token":
                # Return mock data for development
                return {
                    'embedUrl': 'https://app.powerbi.com/reportEmbed?reportId=sample-report&autoAuth=true&ctid=sample-tenant',
                    'accessToken': 'mock-powerbi-embed-token',
                    'expiration': (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
                }
            
            workspace_id = current_app.config['POWERBI_WORKSPACE_ID']
            
            # If no specific report_id provided, use default from config or mock
            if not report_id:
                report_id = 'default-report-id'
            
            # Get embed URL
            embed_url = f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={workspace_id}"
            
            # Generate embed token
            embed_token_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Token request body
            token_request = {
                'accessLevel': 'View',
                'allowSaveAs': False
            }
            
            response = requests.post(embed_token_url, headers=headers, json=token_request)
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'embedUrl': embed_url,
                    'accessToken': token_data.get('token'),
                    'expiration': token_data.get('expiration')
                }
            else:
                current_app.logger.error(f"Failed to generate embed token: {response.text}")
                # Return mock data as fallback
                return {
                    'embedUrl': embed_url,
                    'accessToken': 'mock-powerbi-embed-token',
                    'expiration': (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
                }
                
        except Exception as e:
            current_app.logger.error(f"Error generating embed token: {str(e)}")
            # Return mock data as fallback
            return {
                'embedUrl': 'https://app.powerbi.com/reportEmbed?reportId=sample-report&autoAuth=true&ctid=sample-tenant',
                'accessToken': 'mock-powerbi-embed-token',
                'expiration': (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
            }
    
    @staticmethod
    def get_reports_list():
        """Get list of available reports"""
        try:
            access_token = PowerBIService.get_access_token()
            
            if not access_token or access_token == "mock-powerbi-access-token":
                # Return mock data for development
                return [
                    {
                        'id': 'sample-report-1',
                        'name': 'Dashboard Ventas',
                        'description': 'Análisis de ventas mensuales'
                    },
                    {
                        'id': 'sample-report-2',
                        'name': 'Reporte Financiero',
                        'description': 'Estado financiero y KPIs'
                    }
                ]
            
            workspace_id = current_app.config['POWERBI_WORKSPACE_ID']
            url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                reports_data = response.json()
                return reports_data.get('value', [])
            else:
                current_app.logger.error(f"Failed to get reports list: {response.text}")
                return []
                
        except Exception as e:
            current_app.logger.error(f"Error getting reports list: {str(e)}")
            return []

