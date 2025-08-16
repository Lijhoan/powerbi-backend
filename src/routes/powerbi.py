from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
from src.models.report import Report
from src.services.powerbi_service import PowerBIService

powerbi_bp = Blueprint('powerbi', __name__)

@powerbi_bp.route('/powerbi/report-url', methods=['GET'])
@jwt_required()
def get_report_url():
    """Get Power BI embed URL and access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Get report_id from query parameters (optional)
        report_id = request.args.get('report_id')
        
        # Generate embed token
        embed_data = PowerBIService.generate_embed_token(
            report_id=report_id,
            user_permissions=user.to_dict()
        )
        
        return jsonify(embed_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener URL del reporte'}), 500

@powerbi_bp.route('/powerbi/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get list of available Power BI reports"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Get reports from database
        reports = Report.query.filter_by(is_active=True).all()
        
        # If no reports in database, get from Power BI API
        if not reports:
            powerbi_reports = PowerBIService.get_reports_list()
            return jsonify(powerbi_reports), 200
        
        # Return reports from database
        return jsonify([report.to_dict() for report in reports]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener lista de reportes'}), 500

@powerbi_bp.route('/powerbi/reports', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report entry (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Se requieren privilegios de administrador'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'powerbi_report_id', 'powerbi_workspace_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Campo requerido: {field}'}), 400
        
        # Create new report
        report = Report(
            name=data['name'],
            description=data.get('description', ''),
            powerbi_report_id=data['powerbi_report_id'],
            powerbi_workspace_id=data['powerbi_workspace_id']
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear reporte'}), 500

