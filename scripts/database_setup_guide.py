#!/usr/bin/env python3
"""
Database Setup Guide for Security Plus Training Tool
This script provides guidance for setting up a new database after MongoDB removal.
"""

def show_database_options():
    """Display available database options and setup instructions"""
    print("Security+ Training Tool - Database Setup Guide")
    print("=" * 50)
    print()
    print("MongoDB has been removed from this application.")
    print("Please choose one of the following database options:")
    print()
    
    print("1. PostgreSQL (Recommended for production)")
    print("   - Robust, feature-rich relational database")
    print("   - Excellent for complex queries and data integrity")
    print("   - Free tier available on: Railway, Supabase, Neon, ElephantSQL")
    print("   - Install: pip install psycopg2-binary")
    print()
    
    print("2. MySQL")
    print("   - Popular relational database")
    print("   - Good performance and reliability")
    print("   - Free tier available on: PlanetScale, Railway, Clever Cloud")
    print("   - Install: pip install PyMySQL")
    print()
    
    print("3. SQLite (Good for development/testing)")
    print("   - File-based database, no server required")
    print("   - Built into Python")
    print("   - Perfect for development and small applications")
    print("   - No installation needed")
    print()
    
    print("4. Cloud Database Services (Recommended for production)")
    print("   - Supabase (PostgreSQL): https://supabase.com")
    print("   - Railway (PostgreSQL/MySQL): https://railway.app")
    print("   - PlanetScale (MySQL): https://planetscale.com")
    print("   - Neon (PostgreSQL): https://neon.tech")
    print("   - ElephantSQL (PostgreSQL): https://www.elephantsql.com")
    print()

def show_implementation_steps():
    """Show steps to implement the chosen database"""
    print("Implementation Steps:")
    print("=" * 20)
    print()
    print("1. Choose your database and get connection details")
    print("2. Update requirements.txt with appropriate database driver")
    print("3. Set environment variables:")
    print("   - DATABASE_URL=your_connection_string")
    print("   - DATABASE_NAME=security_plus_training")
    print()
    print("4. Implement database connection in database/connection.py")
    print("5. Implement database operations in database/question_manager.py")
    print("6. Create database tables/schema for questions")
    print("7. Test the connection and operations")
    print()

def show_example_implementations():
    """Show example implementations for different databases"""
    print("Example Implementations:")
    print("=" * 25)
    print()
    
    print("PostgreSQL with psycopg2:")
    print("-" * 30)
    print("""
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = None
    
    def connect(self):
        self.connection = psycopg2.connect(
            self.database_url,
            cursor_factory=RealDictCursor
        )
    
    def get_connection(self):
        if not self.connection:
            self.connect()
        return self.connection
""")
    
    print("SQLite with sqlite3:")
    print("-" * 20)
    print("""
import sqlite3

class DatabaseManager:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
    
    def get_connection(self):
        if not self.connection:
            self.connect()
        return self.connection
""")
    
    print("MySQL with PyMySQL:")
    print("-" * 20)
    print("""
import pymysql

class DatabaseManager:
    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = None
    
    def connect(self):
        # Parse database_url and connect
        self.connection = pymysql.connect(
            host='localhost',
            user='username',
            password='password',
            database='security_plus_training'
        )
""")

def show_schema_example():
    """Show example database schema for questions"""
    print("Example Database Schema:")
    print("=" * 25)
    print()
    print("SQL (PostgreSQL/MySQL):")
    print("-" * 20)
    print("""
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    explanation TEXT,
    correct_answer TEXT,
    options JSON,  -- For multiple choice questions
    tags JSON,     -- Array of tags
    reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_created_at ON questions(created_at);
""")
    
    print("SQLite:")
    print("-" * 10)
    print("""
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    explanation TEXT,
    correct_answer TEXT,
    options TEXT,  -- JSON string
    tags TEXT,     -- JSON string
    reference TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

def main():
    """Main function to display all guidance"""
    show_database_options()
    print()
    show_implementation_steps()
    print()
    show_example_implementations()
    print()
    show_schema_example()
    print()
    print("Next Steps:")
    print("=" * 15)
    print("1. Choose your preferred database")
    print("2. Set up the database (local or cloud)")
    print("3. Implement the database connection and operations")
    print("4. Test your implementation")
    print("5. Update the application to use your new database")
    print()
    print("For more help, check the documentation of your chosen database.")

if __name__ == "__main__":
    main()
