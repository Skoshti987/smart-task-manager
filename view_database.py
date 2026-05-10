#!/usr/bin/env python3
"""
Script to view the contents of the Smart Task Manager database
"""

import sqlite3
import os

def view_database():
    """View the contents of the SQLite database"""
    db_path = os.path.join('instance', 'smart_task.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            print("Make sure the application has been run at least once.")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("SMART TASK MANAGER DATABASE CONTENTS")
        print("=" * 60)
        
        # Show tables
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"\n📋 Tables found: {[table[0] for table in tables]}")
            
            # Show users
            print("\n👥 USERS:")
            print("-" * 40)
            cursor.execute("SELECT id, username, email, created_at FROM users;")
            users = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error accessing tables: {e}")
            return
        
        if users:
            for user in users:
                print(f"ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Created: {user[3]}")
        else:
            print("No users found")
        
        # Show tasks
        print("\n📝 TASKS:")
        print("-" * 80)
        cursor.execute("SELECT id, title, description, priority, status, created_at, user_id FROM tasks;")
        tasks = cursor.fetchall()
        
        if tasks:
            for task in tasks:
                print(f"ID: {task[0]}")
                print(f"Title: {task[1]}")
                print(f"Description: {task[2] or 'No description'}")
                print(f"Priority: {task[3]} | Status: {task[4]}")
                print(f"Created: {task[5]} | User ID: {task[6]}")
                print("-" * 40)
        else:
            print("No tasks found")
        
        # Show statistics
        print("\n📊 STATISTICS:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status;")
        task_status = cursor.fetchall()
        
        cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority;")
        task_priority = cursor.fetchall()
        
        print(f"Total Users: {user_count}")
        print(f"Total Tasks: {task_count}")
        
        if task_status:
            print("\nTasks by Status:")
            for status, count in task_status:
                print(f"  {status}: {count}")
        
        if task_priority:
            print("\nTasks by Priority:")
            for priority, count in task_priority:
                print(f"  {priority}: {count}")
        
        print("\n" + "=" * 60)
        print(f"Database location: {os.path.abspath(db_path)}")
        print(f"Database size: {os.path.getsize(db_path)} bytes")
        print("=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    view_database()
