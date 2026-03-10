import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.orders import orders_bp

def create_app():
    app = Flask(__name__)
    
    # Configure Database (SQLite) and Secret Key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopsphere.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'mysupersecretkeythatisverysecureandlongenough' # Use a standard static key for easy testing just like in dev
    
    # Configure CORS (allow all origins, matching the Java SecurityConfig)
    CORS(app)
    
    # Initialize DB
    db.init_app(app)
    
    with app.app_context():
        # Create tables automatically based on SQLAlchemy models (like spring.jpa.hibernate.ddl-auto=update)
        db.create_all()

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')

    # Global Exception Handler (matches the Java @ControllerAdvice layout)
    @app.errorhandler(Exception)
    def handle_exception(e):
        # We can expand this to check for specific error classes if needed (e.g. SQLAlchemy Errors)
        print(f"Global Error caught: {e}")
        # Always return JSON rather than HTML template crash
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Run the server on port 8080 to match the frontend expectations
    app.run(host='0.0.0.0', port=8080, debug=True)
