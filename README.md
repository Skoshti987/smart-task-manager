# Smart Task Management System

A comprehensive full-stack web application for task management with real-time updates, analytics, and PostgreSQL database integration.

## Features

### Core Functionality
- **User Authentication**: Registration, login, and secure session management
- **Task Management**: Create, read, update, and delete tasks
- **Real-time Updates**: WebSocket integration for live task updates
- **Analytics Dashboard**: Comprehensive task analytics with charts and productivity scores
- **Priority Management**: High, medium, and low priority task classification
- **Due Date Tracking**: Task scheduling and overdue task notifications

### Technical Features
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with optimized queries and indexes
- **Frontend**: Bootstrap 5 with responsive design
- **Real-time Communication**: Socket.IO for WebSocket connections
- **Data Analytics**: Pandas and NumPy for statistical analysis
- **Security**: Password hashing, input validation, and CSRF protection

## Technology Stack

### Backend
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.0.5** - ORM
- **Flask-Login 0.6.3** - Authentication
- **Flask-SocketIO 5.3.6** - WebSocket support
- **psycopg2-binary** - PostgreSQL adapter
- **pandas 2.0.3** - Data analysis
- **numpy 1.24.3** - Numerical computing

### Frontend
- **Bootstrap 5.3.0** - UI framework
- **Font Awesome 6.4.0** - Icons
- **Chart.js** - Data visualization
- **Socket.IO Client** - Real-time communication

### Database
- **PostgreSQL** - Primary database
- **SQLite** - Development database
- **SQLAlchemy ORM** - Database abstraction

## Project Structure

```
smart-task-manager/
│
├── app.py                 # Main Flask application
├── config_dev.py          # Development configuration
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── extensions.py         # Flask extensions
├── run_dev.py            # Development server
│
├── models/               # Database models
│   └── __init__.py       # User and Task models
│
├── routes/               # API routes
│   ├── auth_routes.py    # Authentication endpoints
│   ├── task_routes.py    # Task management endpoints
│   └── analytics_routes.py # Analytics endpoints
│
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   └── dashboard.html   # Main dashboard
│
├── static/              # Static assets
│   ├── css/
│   │   └── style.css   # Custom styles
│   ├── js/
│   │   └── script.js   # JavaScript functionality
│   └── images/         # Image assets
│
├── utils/               # Utility functions
│   └── analytics.py     # Analytics calculations
│
└── database/            # Database files
    └── schema.sql      # Database schema
```

## Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (for production)
- Git (for cloning)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-task-manager.git
cd smart-task-manager
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application

#### Development Mode (Recommended)
```bash
python run_dev.py
```

#### Production Mode
```bash
# Set environment variables
export FLASK_CONFIG=production
export DATABASE_URL=postgresql://username:password@localhost/smart_task_db
export SECRET_KEY=your-production-secret-key

# Run with production server
gunicorn --worker-class eventlet -w 1 app:app
```

### 5. Access the Application
- **URL**: http://localhost:5000
- **Test Credentials**: admin/admin123

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/current-user` - Get current user info

### Tasks
- `POST /tasks/add-task` - Create new task
- `GET /tasks/tasks` - Get all tasks (with filters)
- `PUT /tasks/update-task/<id>` - Update task
- `DELETE /tasks/delete-task/<id>` - Delete task
- `GET /tasks/task/<id>` - Get specific task
- `POST /tasks/bulk-update` - Bulk update tasks

### Analytics
- `GET /analytics` - Get all analytics
- `GET /analytics/basic` - Get basic analytics
- `GET /analytics/priority` - Get priority analytics
- `GET /analytics/time` - Get time-based analytics
- `GET /analytics/productivity-score` - Get productivity score
- `GET /analytics/dashboard` - Get dashboard analytics

## WebSocket Events

### Client to Server
- `connect` - Establish connection
- `join_user_room` - Join user-specific room
- `leave_user_room` - Leave user-specific room

### Server to Client
- `task_added` - New task created
- `task_updated` - Task modified
- `task_deleted` - Task removed
- `tasks_bulk_updated` - Multiple tasks updated

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `created_at`

### Tasks Table
- `id` (Primary Key)
- `title`
- `description`
- `priority` (low, medium, high)
- `status` (pending, in_progress, completed)
- `created_at`
- `updated_at`
- `due_date`
- `user_id` (Foreign Key)

## Analytics Features

### Basic Analytics
- Total tasks count
- Completed tasks count
- Pending tasks count
- In-progress tasks count
- Completion percentage
- Overdue tasks count

### Priority Analytics
- Task distribution by priority
- Completion rates by priority level
- Priority-based performance metrics

### Time Analytics
- Tasks created in time period
- Daily task creation averages
- Completion trends over time
- Productivity patterns

### Productivity Score
- Calculated based on completion rate
- Bonus for high-priority task completion
- Penalty for overdue tasks
- Score range: 0-100

## Security Features

- Password hashing with Werkzeug
- Input validation and sanitization
- CSRF protection
- Secure session management
- SQL injection prevention through ORM
- XSS protection with template escaping

## Performance Optimizations

- Database indexes on frequently queried columns
- Optimized database queries
- Efficient WebSocket room management
- Client-side caching for static assets
- Lazy loading for large datasets

## GitHub Setup and Upload

### 1. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Smart Task Manager"
```

### 2. Create GitHub Repository
- Go to https://github.com and create new repository
- Name: `smart-task-manager`
- Choose Public/Private as needed
- Don't initialize with README (we already have one)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/yourusername/smart-task-manager.git
git branch -M main
git push -u origin main
```

## Database Setup (PostgreSQL)

### Development (SQLite)
- Automatic setup with `python run_dev.py`
- Database file: `smart_task.db`

### Production (PostgreSQL)
```bash
# Create database
createdb smart_task_db

# Import schema
psql -d smart_task_db -f database/schema.sql

# Set environment variable
export DATABASE_URL=postgresql://username:password@localhost/smart_task_db
```

## Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "app:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues

## Future Enhancements

- [ ] Mobile application
- [ ] Email notifications
- [ ] Task templates
- [ ] Team collaboration features
- [ ] Advanced reporting
- [ ] Integration with calendar applications
- [ ] File attachments for tasks
- [ ] Task dependencies
- [ ] Time tracking
- [ ] Kanban board view

## Quick Start Guide

```bash
# Clone and setup
git clone https://github.com/yourusername/smart-task-manager.git
cd smart-task-manager
pip install -r requirements.txt

# Run development server
python run_dev.py

# Access at http://localhost:5000
# Login: admin/admin123
```

## Project Highlights

This project demonstrates:

✅ **Full Stack Development** - Complete frontend and backend integration
✅ **Real-time Systems** - WebSocket implementation for live updates
✅ **Database Design** - PostgreSQL with optimized schema
✅ **API Architecture** - RESTful API design patterns
✅ **Python Data Analysis** - Pandas and NumPy integration
✅ **Modern Frontend** - Bootstrap 5 with responsive design
✅ **Security Best Practices** - Authentication and data protection
✅ **Production Ready** - Scalable architecture and deployment options

Perfect for:
- Internship portfolio projects
- Full-stack development demonstrations
- Database integration examples
- Real-time application showcases
- Academic assignments
