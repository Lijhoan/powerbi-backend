import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db, User
from src.models.report import Report
from src.models.comment import Comment, CommentLike
from src.models.reaction import Reaction

# Import blueprints
from src.routes.auth import auth_bp
from src.routes.powerbi import powerbi_bp
from src.routes.comments import comments_bp
from src.routes.reactions import reactions_bp
from src.routes.user import user_bp 
def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'your-super-secret-jwt-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, origins=['http://localhost:3000', 'https://your-frontend-domain.com'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(powerbi_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(reactions_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api') 
    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        seed_database()
    
    # Serve frontend files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'PowerBI Backend API is running'}, 200
    
    return app

def seed_database():
    """Seed database with initial data"""
    try:
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                is_admin=True,
                email='admin@example.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        
        # Create regular user if not exists
        regular_user = User.query.filter_by(username='user').first()
        if not regular_user:
            regular_user = User(
                username='user',
                is_admin=False,
                email='user@example.com'
            )
            regular_user.set_password('user123')
            db.session.add(regular_user)
        
        # Create default report if not exists
        default_report = Report.query.filter_by(powerbi_report_id='default-report').first()
        if not default_report:
            default_report = Report(
                name='Dashboard Principal',
                description='Dashboard principal de la aplicación',
                powerbi_report_id='default-report',
                powerbi_workspace_id='default-workspace'
            )
            db.session.add(default_report)
        
        db.session.commit()
        
        # Add sample comments if none exist
        if Comment.query.count() == 0:
            sample_comments = [
                Comment(
                    user_id=regular_user.id if regular_user else 2,
                    report_id=default_report.id if default_report else 1,
                    content='Excelente análisis de ventas. Los datos del Q4 muestran una tendencia muy positiva.',
                    likes=5
                ),
                Comment(
                    user_id=admin_user.id if admin_user else 1,
                    report_id=default_report.id if default_report else 1,
                    content='Gracias por el feedback. Hemos actualizado el dashboard con métricas adicionales.',
                    likes=3
                )
            ]
            
            for comment in sample_comments:
                db.session.add(comment)
        
        # Add sample reactions if none exist
        if Reaction.query.count() == 0:
            sample_reactions = [
                Reaction(
                    user_id=regular_user.id if regular_user else 2,
                    report_id=default_report.id if default_report else 1,
                    reaction_type='me_interesa'
                ),
                Reaction(
                    user_id=admin_user.id if admin_user else 1,
                    report_id=default_report.id if default_report else 1,
                    reaction_type='aporta'
                )
            ]
            
            for reaction in sample_reactions:
                db.session.add(reaction)
        
        db.session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

