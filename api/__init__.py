from flask import Flask
from config import config_by_name

# Import extensions
from .extensions import db, ma, migrate

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    
    # Register Blueprints for API resources
    from .resources.user_resource import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # A simple route to check if the app is running
    @app.route('/health')
    def health_check():
        return "API is running!", 200
        
    # This context is needed for Flask-Migrate and to create tables
    with app.app_context():
        # You can create all tables here if not using migrations
        # db.create_all()
        pass

    return app