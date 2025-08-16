from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from src.models.user import User, db
from src.models.reaction import Reaction
from src.models.report import Report
from src.utils.schemas import ReactionSchema

reactions_bp = Blueprint('reactions', __name__)

@reactions_bp.route('/reactions', methods=['GET'])
def get_reactions():
    """Get reaction statistics for a report"""
    try:
        report_id = request.args.get('report_id', 1, type=int)  # Default to report 1
        
        # Get reaction statistics
        stats = Reaction.get_reaction_stats(report_id)
        
        # If no reactions found, return default structure
        if not stats:
            stats = [
                {'tipo': 'me_interesa', 'count': 0},
                {'tipo': 'increible', 'count': 0},
                {'tipo': 'aporta', 'count': 0}
            ]
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener reacciones'}), 500

@reactions_bp.route('/reactions', methods=['POST'])
@jwt_required()
def create_reaction():
    """Create or update a reaction"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Validate input data
        schema = ReactionSchema()
        data = schema.load(request.get_json())
        
        report_id = data['report_id']
        reaction_type = data['tipo']
        
        # Check if report exists (optional, can create default report)
        report = Report.query.get(report_id)
        if not report:
            # Create default report if it doesn't exist
            report = Report(
                name='Dashboard Principal',
                description='Dashboard principal de la aplicación',
                powerbi_report_id='default-report',
                powerbi_workspace_id='default-workspace'
            )
            db.session.add(report)
            db.session.flush()  # Get the ID without committing
            report_id = report.id
        
        # Check if user already has this reaction for this report
        existing_reaction = Reaction.query.filter_by(
            user_id=current_user_id,
            report_id=report_id,
            reaction_type=reaction_type
        ).first()
        
        if existing_reaction:
            # Remove existing reaction (toggle off)
            db.session.delete(existing_reaction)
            action = 'removed'
        else:
            # Remove any other reaction from this user for this report
            other_reactions = Reaction.query.filter_by(
                user_id=current_user_id,
                report_id=report_id
            ).all()
            
            for reaction in other_reactions:
                db.session.delete(reaction)
            
            # Add new reaction
            new_reaction = Reaction(
                user_id=current_user_id,
                report_id=report_id,
                reaction_type=reaction_type
            )
            db.session.add(new_reaction)
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'message': 'Reacción registrada'
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Datos de entrada inválidos', 'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al procesar reacción'}), 500

@reactions_bp.route('/reactions/user', methods=['GET'])
@jwt_required()
def get_user_reactions():
    """Get current user's reactions for a report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        report_id = request.args.get('report_id', 1, type=int)
        
        # Get user's reactions for this report
        reactions = Reaction.query.filter_by(
            user_id=current_user_id,
            report_id=report_id
        ).all()
        
        return jsonify([reaction.to_dict() for reaction in reactions]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener reacciones del usuario'}), 500

