from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import Task
from extensions import db
from datetime import datetime
from flask_socketio import emit

task_bp = Blueprint('tasks', __name__)

def validate_task_data(data):
    errors = []
    
    if not data.get('title', '').strip():
        errors.append('Title is required')
    
    if data.get('priority') and data['priority'] not in ['low', 'medium', 'high']:
        errors.append('Priority must be low, medium, or high')
    
    if data.get('status') and data['status'] not in ['pending', 'in_progress', 'completed']:
        errors.append('Status must be pending, in_progress, or completed')
    
    return errors

@task_bp.route('/add-task', methods=['POST'])
@login_required
def add_task():
    try:
        data = request.get_json()
        
        # Validate data
        errors = validate_task_data(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Create new task
        task = Task(
            title=data.get('title', '').strip(),
            description=data.get('description', '').strip(),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending'),
            user_id=current_user.id
        )
        
        # Handle due date if provided
        if data.get('due_date'):
            try:
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due date format. Use ISO format.'}), 400
        
        db.session.add(task)
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        from app import socketio
        socketio.emit('task_added', {
            'task': task.to_dict(),
            'user': current_user.username
        }, room=f'user_{current_user.id}')
        
        return jsonify({
            'message': 'Task added successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add task', 'details': str(e)}), 500

@task_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = Task.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(Task.status == status_filter)
        
        if priority_filter:
            query = query.filter(Task.priority == priority_filter)
        
        if search_query:
            query = query.filter(
                (Task.title.ilike(f'%{search_query}%')) |
                (Task.description.ilike(f'%{search_query}%'))
            )
        
        # Order by created date (newest first)
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'total': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch tasks', 'details': str(e)}), 500

@task_bp.route('/update-task/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Validate data
        errors = validate_task_data(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Update fields
        if 'title' in data:
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description'].strip()
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid due date format. Use ISO format.'}), 400
            else:
                task.due_date = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        from app import socketio
        socketio.emit('task_updated', {
            'task': task.to_dict(),
            'user': current_user.username
        }, room=f'user_{current_user.id}')
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update task', 'details': str(e)}), 500

@task_bp.route('/delete-task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task_data = task.to_dict()
        db.session.delete(task)
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        from app import socketio
        socketio.emit('task_deleted', {
            'task': task_data,
            'user': current_user.username
        }, room=f'user_{current_user.id}')
        
        return jsonify({
            'message': 'Task deleted successfully',
            'task_id': task_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete task', 'details': str(e)}), 500

@task_bp.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch task', 'details': str(e)}), 500

@task_bp.route('/tasks/bulk-update', methods=['POST'])
@login_required
def bulk_update_tasks():
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        updates = data.get('updates', {})
        
        if not task_ids:
            return jsonify({'error': 'No task IDs provided'}), 400
        
        # Validate updates
        if 'status' in updates and updates['status'] not in ['pending', 'in_progress', 'completed']:
            return jsonify({'error': 'Invalid status value'}), 400
        
        if 'priority' in updates and updates['priority'] not in ['low', 'medium', 'high']:
            return jsonify({'error': 'Invalid priority value'}), 400
        
        # Update tasks
        updated_tasks = []
        for task_id in task_ids:
            task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
            if task:
                if 'status' in updates:
                    task.status = updates['status']
                if 'priority' in updates:
                    task.priority = updates['priority']
                
                task.updated_at = datetime.utcnow()
                updated_tasks.append(task)
        
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        from app import socketio
        socketio.emit('tasks_bulk_updated', {
            'tasks': [task.to_dict() for task in updated_tasks],
            'user': current_user.username
        }, room=f'user_{current_user.id}')
        
        return jsonify({
            'message': f'{len(updated_tasks)} tasks updated successfully',
            'tasks': [task.to_dict() for task in updated_tasks]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to bulk update tasks', 'details': str(e)}), 500
