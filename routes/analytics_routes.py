from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.analytics import TaskAnalytics

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    try:
        # Get all types of analytics
        basic_analytics = TaskAnalytics.get_basic_analytics(current_user.id)
        priority_analytics = TaskAnalytics.get_priority_analytics(current_user.id)
        time_analytics = TaskAnalytics.get_time_analytics(current_user.id)
        productivity_score = TaskAnalytics.get_productivity_score(current_user.id)
        
        # Combine all analytics
        analytics_data = {
            'basic': basic_analytics,
            'priority': priority_analytics,
            'time': time_analytics,
            'productivity_score': productivity_score,
            'generated_at': TaskAnalytics._get_current_timestamp()
        }
        
        return jsonify({
            'analytics': analytics_data,
            'message': 'Analytics generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate analytics', 'details': str(e)}), 500

@analytics_bp.route('/analytics/basic', methods=['GET'])
@login_required
def get_basic_analytics():
    try:
        analytics = TaskAnalytics.get_basic_analytics(current_user.id)
        
        return jsonify({
            'analytics': analytics,
            'message': 'Basic analytics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve basic analytics', 'details': str(e)}), 500

@analytics_bp.route('/analytics/priority', methods=['GET'])
@login_required
def get_priority_analytics():
    try:
        analytics = TaskAnalytics.get_priority_analytics(current_user.id)
        
        return jsonify({
            'analytics': analytics,
            'message': 'Priority analytics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve priority analytics', 'details': str(e)}), 500

@analytics_bp.route('/analytics/time', methods=['GET'])
@login_required
def get_time_analytics():
    try:
        # Get days parameter from query string (default: 30 days)
        days = request.args.get('days', 30, type=int)
        days = max(1, min(365, days))  # Limit between 1 and 365 days
        
        analytics = TaskAnalytics.get_time_analytics(current_user.id, days)
        
        return jsonify({
            'analytics': analytics,
            'message': f'Time analytics for last {days} days retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve time analytics', 'details': str(e)}), 500

@analytics_bp.route('/analytics/productivity-score', methods=['GET'])
@login_required
def get_productivity_score():
    try:
        score = TaskAnalytics.get_productivity_score(current_user.id)
        
        # Determine performance level
        if score >= 80:
            level = 'Excellent'
            color = '#28a745'  # Green
        elif score >= 60:
            level = 'Good'
            color = '#ffc107'  # Yellow
        elif score >= 40:
            level = 'Average'
            color = '#fd7e14'  # Orange
        else:
            level = 'Needs Improvement'
            color = '#dc3545'  # Red
        
        return jsonify({
            'productivity_score': score,
            'performance_level': level,
            'color': color,
            'message': 'Productivity score calculated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to calculate productivity score', 'details': str(e)}), 500

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@login_required
def get_dashboard_analytics():
    try:
        # Get comprehensive analytics for dashboard
        basic_analytics = TaskAnalytics.get_basic_analytics(current_user.id)
        priority_analytics = TaskAnalytics.get_priority_analytics(current_user.id)
        productivity_score = TaskAnalytics.get_productivity_score(current_user.id)
        
        # Prepare dashboard data
        dashboard_data = {
            'summary_cards': [
                {
                    'title': 'Total Tasks',
                    'value': basic_analytics['total_tasks'],
                    'icon': 'tasks',
                    'color': '#007bff'
                },
                {
                    'title': 'Completed',
                    'value': basic_analytics['completed_tasks'],
                    'icon': 'check-circle',
                    'color': '#28a745'
                },
                {
                    'title': 'In Progress',
                    'value': basic_analytics['in_progress_tasks'],
                    'icon': 'clock',
                    'color': '#ffc107'
                },
                {
                    'title': 'Overdue',
                    'value': basic_analytics['overdue_tasks'],
                    'icon': 'exclamation-triangle',
                    'color': '#dc3545'
                }
            ],
            'completion_rate': {
                'percentage': basic_analytics['completion_percentage'],
                'completed': basic_analytics['completed_tasks'],
                'total': basic_analytics['total_tasks']
            },
            'priority_breakdown': {
                'high': priority_analytics['high_priority']['total'],
                'medium': priority_analytics['medium_priority']['total'],
                'low': priority_analytics['low_priority']['total']
            },
            'productivity_score': {
                'score': productivity_score,
                'level': TaskAnalytics._get_performance_level(productivity_score),
                'color': TaskAnalytics._get_performance_color(productivity_score)
            }
        }
        
        return jsonify({
            'dashboard': dashboard_data,
            'message': 'Dashboard analytics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve dashboard analytics', 'details': str(e)}), 500

# Helper methods for TaskAnalytics class
@staticmethod
def _get_current_timestamp():
    from datetime import datetime
    return datetime.utcnow().isoformat()

@staticmethod  
def _get_performance_level(score):
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    elif score >= 40:
        return 'Average'
    else:
        return 'Needs Improvement'

@staticmethod
def _get_performance_color(score):
    if score >= 80:
        return '#28a745'  # Green
    elif score >= 60:
        return '#ffc107'  # Yellow
    elif score >= 40:
        return '#fd7e14'  # Orange
    else:
        return '#dc3545'  # Red

# Add helper methods to TaskAnalytics class
TaskAnalytics._get_current_timestamp = _get_current_timestamp
TaskAnalytics._get_performance_level = _get_performance_level
TaskAnalytics._get_performance_color = _get_performance_color
