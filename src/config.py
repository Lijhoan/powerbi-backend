import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-secret-key'
    
    # Database config
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    
    # Power BI config
    POWERBI_CLIENT_ID = os.environ.get('POWERBI_CLIENT_ID')
    POWERBI_CLIENT_SECRET = os.environ.get('POWERBI_CLIENT_SECRET')
    POWERBI_TENANT_ID = os.environ.get('POWERBI_TENANT_ID')
    POWERBI_WORKSPACE_ID = os.environ.get('POWERBI_WORKSPACE_ID')
    
    # CORS config
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

