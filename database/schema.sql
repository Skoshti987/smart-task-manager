-- Smart Task Manager Database Schema
-- PostgreSQL Database Schema

-- Create database (uncomment if needed)
-- CREATE DATABASE smart_task_db;
-- CREATE DATABASE smart_task_db_dev;

-- Use the database
-- \c smart_task_db;

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at 
    BEFORE UPDATE ON tasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LFvOe'), -- password: admin123
('john_doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LFvOe'), -- password: admin123
('jane_smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LFvOe'); -- password: admin123

-- Insert sample tasks for testing (optional)
INSERT INTO tasks (title, description, priority, status, due_date, user_id) VALUES
('Complete project documentation', 'Write comprehensive documentation for the Smart Task Manager project', 'high', 'in_progress', CURRENT_TIMESTAMP + INTERVAL '3 days', 1),
('Review pull requests', 'Review and merge pending pull requests from team members', 'medium', 'pending', CURRENT_TIMESTAMP + INTERVAL '1 day', 1),
('Update dependencies', 'Update all npm and pip dependencies to latest stable versions', 'low', 'completed', CURRENT_TIMESTAMP - INTERVAL '2 days', 1),
('Fix login bug', 'Investigate and fix the login authentication issue reported by users', 'high', 'pending', CURRENT_TIMESTAMP + INTERVAL '1 day', 2),
('Prepare presentation', 'Create slides for the upcoming team meeting presentation', 'medium', 'pending', CURRENT_TIMESTAMP + INTERVAL '5 days', 2),
('Code review', 'Review the new analytics module implementation', 'medium', 'completed', CURRENT_TIMESTAMP - INTERVAL '1 day', 3),
('Database optimization', 'Optimize database queries for better performance', 'high', 'in_progress', CURRENT_TIMESTAMP + INTERVAL '2 days', 3),
('User testing', 'Conduct user testing sessions for the new features', 'low', 'pending', CURRENT_TIMESTAMP + INTERVAL '7 days', 3);

-- Create views for common queries
CREATE VIEW task_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status = 'pending' THEN 1 END) as pending_tasks,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as in_progress_tasks,
    COUNT(CASE WHEN t.due_date < CURRENT_TIMESTAMP AND t.status != 'completed' THEN 1 END) as overdue_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'completed' THEN 1 END) * 100.0 / NULLIF(COUNT(t.id), 0)), 2
    ) as completion_percentage
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.username;

CREATE VIEW priority_analysis AS
SELECT 
    u.id as user_id,
    u.username,
    t.priority,
    COUNT(t.id) as total_by_priority,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_by_priority,
    COUNT(CASE WHEN t.status = 'pending' THEN 1 END) as pending_by_priority,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as in_progress_by_priority
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.username, t.priority
ORDER BY u.id, t.priority;

-- Create function to get productivity score
CREATE OR REPLACE FUNCTION calculate_productivity_score(p_user_id INTEGER)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_total_tasks INTEGER;
    v_completed_tasks INTEGER;
    v_high_priority_tasks INTEGER;
    v_high_priority_completed INTEGER;
    v_overdue_tasks INTEGER;
    v_completion_score DECIMAL(5,2);
    v_high_priority_bonus DECIMAL(5,2);
    v_overdue_penalty DECIMAL(5,2);
    v_final_score DECIMAL(5,2);
BEGIN
    -- Get basic metrics
    SELECT COUNT(t.id), COUNT(CASE WHEN t.status = 'completed' THEN 1 END)
    INTO v_total_tasks, v_completed_tasks
    FROM tasks t
    WHERE t.user_id = p_user_id;
    
    -- Get high priority metrics
    SELECT COUNT(t.id), COUNT(CASE WHEN t.status = 'completed' THEN 1 END)
    INTO v_high_priority_tasks, v_high_priority_completed
    FROM tasks t
    WHERE t.user_id = p_user_id AND t.priority = 'high';
    
    -- Get overdue tasks count
    SELECT COUNT(t.id)
    INTO v_overdue_tasks
    FROM tasks t
    WHERE t.user_id = p_user_id 
    AND t.status != 'completed' 
    AND t.due_date < CURRENT_TIMESTAMP;
    
    -- Calculate base completion score
    IF v_total_tasks > 0 THEN
        v_completion_score := (v_completed_tasks * 100.0 / v_total_tasks);
    ELSE
        v_completion_score := 0;
    END IF;
    
    -- Calculate high priority bonus (max 20 points)
    IF v_high_priority_tasks > 0 THEN
        v_high_priority_bonus := LEAST((v_high_priority_completed * 100.0 / v_high_priority_tasks), 20);
    ELSE
        v_high_priority_bonus := 0;
    END IF;
    
    -- Calculate overdue penalty (5 points per overdue task, max 30 points)
    v_overdue_penalty := LEAST(v_overdue_tasks * 5, 30);
    
    -- Calculate final score
    v_final_score := v_completion_score + v_high_priority_bonus - v_overdue_penalty;
    v_final_score := GREATEST(0, LEAST(100, v_final_score));
    
    RETURN ROUND(v_final_score, 2);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;

-- Create indexes for views
CREATE INDEX idx_task_summary_user_id ON task_summary(user_id);
CREATE INDEX idx_priority_analysis_user_id ON priority_analysis(user_id);

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts for the Smart Task Manager application';
COMMENT ON TABLE tasks IS 'Tasks created and managed by users';
COMMENT ON COLUMN tasks.priority IS 'Task priority level: low, medium, or high';
COMMENT ON COLUMN tasks.status IS 'Task status: pending, in_progress, or completed';
COMMENT ON COLUMN tasks.due_date IS 'Optional due date for task completion';
COMMENT ON VIEW task_summary IS 'Summary view showing task statistics per user';
COMMENT ON VIEW priority_analysis IS 'Analysis view showing task breakdown by priority per user';
COMMENT ON FUNCTION calculate_productivity_score IS 'Calculates productivity score based on completion rate, priority handling, and overdue tasks';

-- Sample queries for testing
/*
-- Get all users and their task summary
SELECT * FROM task_summary;

-- Get priority analysis for a specific user
SELECT * FROM priority_analysis WHERE user_id = 1;

-- Calculate productivity score for a user
SELECT calculate_productivity_score(1) as productivity_score;

-- Get overdue tasks
SELECT t.*, u.username 
FROM tasks t 
JOIN users u ON t.user_id = u.id 
WHERE t.due_date < CURRENT_TIMESTAMP AND t.status != 'completed';

-- Get tasks due in the next 7 days
SELECT t.*, u.username 
FROM tasks t 
JOIN users u ON t.user_id = u.id 
WHERE t.due_date BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '7 days'
AND t.status != 'completed'
ORDER BY t.due_date;
*/
