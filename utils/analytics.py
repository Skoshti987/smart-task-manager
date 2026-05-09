import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import Task

class TaskAnalytics:
    @staticmethod
    def get_basic_analytics(user_id):
        try:
            # Get all tasks for the user
            tasks = Task.query.filter_by(user_id=user_id).all()
            
            if not tasks:
                return {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'pending_tasks': 0,
                    'in_progress_tasks': 0,
                    'completion_percentage': 0,
                    'overdue_tasks': 0
                }
            
            # Convert to DataFrame for analysis
            task_data = []
            for task in tasks:
                task_data.append({
                    'id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'status': task.status,
                    'created_at': task.created_at,
                    'updated_at': task.updated_at,
                    'due_date': task.due_date
                })
            
            df = pd.DataFrame(task_data)
            
            # Basic counts
            total_tasks = len(df)
            completed_tasks = len(df[df['status'] == 'completed'])
            pending_tasks = len(df[df['status'] == 'pending'])
            in_progress_tasks = len(df[df['status'] == 'in_progress'])
            
            # Completion percentage
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Overdue tasks
            current_time = datetime.utcnow()
            overdue_count = 0
            if 'due_date' in df.columns:
                overdue_tasks = df[
                    (df['status'] != 'completed') & 
                    (df['due_date'].notna()) & 
                    (pd.to_datetime(df['due_date']) < current_time)
                ]
                overdue_count = len(overdue_tasks)
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completion_percentage': round(completion_percentage, 2),
                'overdue_tasks': overdue_count
            }
            
        except Exception as e:
            print(f"Error in get_basic_analytics: {e}")
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'pending_tasks': 0,
                'in_progress_tasks': 0,
                'completion_percentage': 0,
                'overdue_tasks': 0
            }
    
    @staticmethod
    def get_priority_analytics(user_id):
        try:
            tasks = Task.query.filter_by(user_id=user_id).all()
            
            if not tasks:
                return {
                    'high_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0},
                    'medium_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0},
                    'low_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0}
                }
            
            task_data = []
            for task in tasks:
                task_data.append({
                    'priority': task.priority,
                    'status': task.status
                })
            
            df = pd.DataFrame(task_data)
            
            priorities = ['high', 'medium', 'low']
            result = {}
            
            for priority in priorities:
                priority_tasks = df[df['priority'] == priority]
                result[f'{priority}_priority'] = {
                    'total': len(priority_tasks),
                    'completed': len(priority_tasks[priority_tasks['status'] == 'completed']),
                    'pending': len(priority_tasks[priority_tasks['status'] == 'pending']),
                    'in_progress': len(priority_tasks[priority_tasks['status'] == 'in_progress'])
                }
            
            return result
            
        except Exception as e:
            print(f"Error in get_priority_analytics: {e}")
            return {
                'high_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0},
                'medium_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0},
                'low_priority': {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0}
            }
    
    @staticmethod
    def get_time_analytics(user_id, days=30):
        try:
            # Get tasks from the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            tasks = Task.query.filter(
                Task.user_id == user_id,
                Task.created_at >= start_date
            ).all()
            
            if not tasks:
                return {
                    'tasks_created': 0,
                    'tasks_completed': 0,
                    'daily_average': 0,
                    'completion_trend': []
                }
            
            task_data = []
            for task in tasks:
                task_data.append({
                    'created_at': task.created_at,
                    'status': task.status,
                    'updated_at': task.updated_at
                })
            
            df = pd.DataFrame(task_data)
            
            # Convert dates
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            
            # Tasks created in period
            tasks_created = len(df)
            
            # Tasks completed in period
            completed_in_period = df[df['status'] == 'completed']
            tasks_completed = len(completed_in_period)
            
            # Daily average
            daily_average = tasks_created / days if days > 0 else 0
            
            # Completion trend (last 7 days)
            completion_trend = []
            for i in range(7):
                date = datetime.utcnow() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                completed_on_date = len(completed_in_period[
                    completed_in_period['updated_at'].dt.date == date.date()
                ])
                
                completion_trend.append({
                    'date': date_str,
                    'completed': completed_on_date
                })
            
            return {
                'tasks_created': tasks_created,
                'tasks_completed': tasks_completed,
                'daily_average': round(daily_average, 2),
                'completion_trend': list(reversed(completion_trend))
            }
            
        except Exception as e:
            print(f"Error in get_time_analytics: {e}")
            return {
                'tasks_created': 0,
                'tasks_completed': 0,
                'daily_average': 0,
                'completion_trend': []
            }
    
    @staticmethod
    def get_productivity_score(user_id):
        try:
            basic_analytics = TaskAnalytics.get_basic_analytics(user_id)
            priority_analytics = TaskAnalytics.get_priority_analytics(user_id)
            
            total_tasks = basic_analytics['total_tasks']
            if total_tasks == 0:
                return 0
            
            # Base score from completion percentage
            completion_score = basic_analytics['completion_percentage']
            
            # Bonus for completing high priority tasks
            high_priority_total = priority_analytics['high_priority']['total']
            high_priority_completed = priority_analytics['high_priority']['completed']
            high_priority_bonus = 0
            
            if high_priority_total > 0:
                high_priority_completion = (high_priority_completed / high_priority_total) * 100
                high_priority_bonus = min(high_priority_completion, 20)  # Max 20 points bonus
            
            # Penalty for overdue tasks
            overdue_penalty = min(basic_analytics['overdue_tasks'] * 5, 30)  # Max 30 points penalty
            
            # Calculate final score
            final_score = completion_score + high_priority_bonus - overdue_penalty
            final_score = max(0, min(100, final_score))  # Keep between 0 and 100
            
            return round(final_score, 2)
            
        except Exception as e:
            print(f"Error in get_productivity_score: {e}")
            return 0
