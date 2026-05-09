from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from config_dev import config
from extensions import db, login_manager, socketio
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp
    from routes.analytics_routes import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Join user-specific room for real-time updates
            room = f'user_{current_user.id}'
            join_room(room)
            emit('connected', {'message': f'Connected as {current_user.username}'})
        else:
            emit('error', {'message': 'Authentication required'})
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            room = f'user_{current_user.id}'
            leave_room(room)
            print(f'User {current_user.username} disconnected')
    
    @socketio.on('join_user_room')
    def handle_join_user_room():
        if current_user.is_authenticated:
            room = f'user_{current_user.id}'
            join_room(room)
            emit('joined_room', {'room': room})
        else:
            emit('error', {'message': 'Authentication required'})
    
    @socketio.on('leave_user_room')
    def handle_leave_user_room():
        if current_user.is_authenticated:
            room = f'user_{current_user.id}'
            leave_room(room)
            emit('left_room', {'room': room})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return redirect(url_for('auth.login'))
    
    # Context processors
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    # Create database tables
    with app.app_context():
        from models import User, Task
        
        # Import models to ensure they are registered with SQLAlchemy
        db.create_all()
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    socketio.run(
        app,
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=5000
    )
