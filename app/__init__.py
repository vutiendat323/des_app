import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Handle reverse proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    try:
        # Initialize extensions
        db.init_app(app)
        bcrypt.init_app(app)
        
        # Initialize login manager
        login_manager.init_app(app)
        login_manager.login_view = 'routes.login'
        login_manager.login_message_category = 'info'
        
        # Initialize SocketIO
        socketio.init_app(
            app,
            cors_allowed_origins=app.config['CORS_ORIGINS'],
            logger=True,
            engineio_logger=True
        )
        
        # Define user loader
        from .models import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Create database tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        
        # Register blueprints
        from .routes import routes
        app.register_blueprint(routes)
        
        logger.info("Application initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise