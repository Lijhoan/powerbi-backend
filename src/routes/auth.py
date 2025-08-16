from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from src.models.user import User, db
from src.utils.schemas import LoginSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        # Validate input data
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        username = data['username']
        password = data['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'message': 'Credenciales inválidas'}), 401
            
    except ValidationError as e:
        return jsonify({'message': 'Datos de entrada inválidos', 'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor'}), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Refresh JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Create new access token
        new_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al renovar token'}), 500

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener información del usuario'}), 500

