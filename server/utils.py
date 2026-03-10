import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Decode the token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # The Java backend used email as the subject ('sub')
            current_user = User.query.filter_by(email=data['sub']).first()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
                
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['sub']).first()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
            if current_user.role != 'ROLE_ADMIN':
                return jsonify({'error': 'Access denied. Admin role required.'}), 403
                
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def generate_token(user, secret_key):
    # Match the JWT structure from Java (sub = email, role = role) // plus standard claims
    payload = {
        'sub': user.email,
        'role': user.role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10) # 10 hours expiration
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')
