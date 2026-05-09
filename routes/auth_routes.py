from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'error': 'All fields are required'}), 400
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            if request.is_json:
                return jsonify({'error': 'Invalid email format'}), 400
            flash('Invalid email format', 'error')
            return render_template('register.html')
        
        if not validate_password(password):
            if request.is_json:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'error': 'Username already exists'}), 400
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already exists'}), 400
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Registration failed', 'details': str(e)}), 500
        flash('Registration failed. Please try again.', 'error')
        return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Username and password are required'}), 400
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            if request.is_json:
                return jsonify({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }), 200
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'error')
            return render_template('login.html')
            
    except Exception as e:
        if request.is_json:
            return jsonify({'error': 'Login failed', 'details': str(e)}), 500
        flash('Login failed. Please try again.', 'error')
        return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    if request.is_json:
        return jsonify({'message': 'Logged out successfully'}), 200
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/current-user')
@login_required
def current_user_info():
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email
        }
    })
