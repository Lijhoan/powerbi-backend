from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from src.models.user import User, db
from src.models.comment import Comment, CommentLike
from src.models.report import Report
from src.utils.schemas import CommentSchema

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/comments', methods=['GET'])
def get_comments():
    """Get comments for a report"""
    try:
        report_id = request.args.get('report_id', 1, type=int)  # Default to report 1
        current_user_id = None
        
        # Try to get current user if authenticated
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except:
            pass
        
        # Get comments for the report
        comments = Comment.query.filter_by(
            report_id=report_id, 
            is_active=True
        ).order_by(Comment.created_at.desc()).all()
        
        # Convert to dict with user liked status
        comments_data = [comment.to_dict(current_user_id) for comment in comments]
        
        return jsonify(comments_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener comentarios'}), 500

@comments_bp.route('/comments', methods=['POST'])
@jwt_required()
def create_comment():
    """Create a new comment"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Validate input data
        schema = CommentSchema()
        data = schema.load(request.get_json())
        
        # Check if report exists (optional, can create default report)
        report_id = data['report_id']
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
        
        # Create new comment
        comment = Comment(
            user_id=current_user_id,
            report_id=report_id,
            content=data['contenido']
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify(comment.to_dict(current_user_id)), 201
        
    except ValidationError as e:
        return jsonify({'message': 'Datos de entrada inválidos', 'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear comentario'}), 500

@comments_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def toggle_comment_like(comment_id):
    """Toggle like on a comment"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Check if comment exists
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'message': 'Comentario no encontrado'}), 404
        
        # Check if user already liked this comment
        existing_like = CommentLike.query.filter_by(
            user_id=current_user_id,
            comment_id=comment_id
        ).first()
        
        if existing_like:
            # Remove like
            db.session.delete(existing_like)
            comment.likes = max(0, comment.likes - 1)
            action = 'removed'
        else:
            # Add like
            new_like = CommentLike(
                user_id=current_user_id,
                comment_id=comment_id
            )
            db.session.add(new_like)
            comment.likes += 1
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes': comment.likes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al procesar like'}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (only by owner or admin)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Check if comment exists
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'message': 'Comentario no encontrado'}), 404
        
        # Check if user can delete this comment
        if comment.user_id != current_user_id and not user.is_admin:
            return jsonify({'message': 'No tienes permisos para eliminar este comentario'}), 403
        
        # Soft delete
        comment.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Comentario eliminado'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar comentario'}), 500

