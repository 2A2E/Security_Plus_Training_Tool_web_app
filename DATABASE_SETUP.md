# Database Setup Guide - Security+ Training Tool

**⚠️ IMPORTANT: MongoDB has been removed from this application.**

This guide explains how to set up a new database for the Security+ Training Tool after the MongoDB removal.

## Overview

The application previously used **MongoDB** as a non-relational database, but due to connection issues, MongoDB has been removed. You now need to choose and implement a new database solution.

## Available Database Options

### 1. PostgreSQL (Recommended for Production)
- **Pros**: Robust, feature-rich, excellent for complex queries
- **Cons**: Requires more setup than SQLite
- **Cloud Options**: Supabase, Railway, Neon, ElephantSQL
- **Installation**: `pip install psycopg2-binary`

### 2. MySQL
- **Pros**: Popular, good performance, widely supported
- **Cons**: Requires server setup
- **Cloud Options**: PlanetScale, Railway, Clever Cloud
- **Installation**: `pip install PyMySQL`

### 3. SQLite (Recommended for Development)
- **Pros**: File-based, no server required, built into Python
- **Cons**: Not suitable for high-concurrency production use
- **Cloud Options**: Not applicable (file-based)
- **Installation**: Built into Python

### 4. Cloud Database Services
- **Supabase** (PostgreSQL): https://supabase.com
- **Railway** (PostgreSQL/MySQL): https://railway.app
- **PlanetScale** (MySQL): https://planetscale.com
- **Neon** (PostgreSQL): https://neon.tech
- **ElephantSQL** (PostgreSQL): https://www.elephantsql.com

## Quick Setup Guide

### Step 1: Choose Your Database
Select one of the options above based on your needs:
- **Development/Testing**: SQLite
- **Production**: PostgreSQL or MySQL
- **Cloud**: Any of the cloud services listed

### Step 2: Update Dependencies
Edit `requirements.txt` and uncomment the appropriate database driver:

```txt
# For PostgreSQL
psycopg2-binary==2.9.7

# For MySQL
PyMySQL==1.1.0

# For SQLite (built-in, no additional package needed)
```

### Step 3: Set Environment Variables
Create a `.env` file based on `env_example.txt`:

```bash
# For PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_NAME=security_plus_training

# For MySQL
DATABASE_URL=mysql://username:password@host:port/database
DATABASE_NAME=security_plus_training

# For SQLite
DATABASE_URL=sqlite:///path/to/database.db
DATABASE_NAME=security_plus_training
```

### Step 4: Implement Database Connection
Update `database/connection.py` with your chosen database implementation.

### Step 5: Implement Database Operations
Update `database/question_manager.py` with your chosen database operations.

### Step 6: Create Database Schema
Create the necessary tables/collections for storing questions.

## Example Implementations

### PostgreSQL Implementation
```python
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
```

### SQLite Implementation
```python
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
```

## Database Schema

### PostgreSQL/MySQL Schema
```sql
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
```

### SQLite Schema
```sql
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
```

## Testing Your Database

After implementing your database:

1. Run the application: `python run.py`
2. Test API endpoints:
   - `GET /api/questions`
   - `GET /api/categories`
   - `GET /api/tags`
   - `GET /api/stats`

## Migration from MongoDB

If you had data in MongoDB that you need to migrate:

1. Export your MongoDB data to JSON
2. Create a migration script to convert JSON to your new database format
3. Import the converted data into your new database

## Getting Help

1. Run the database setup guide: `python scripts/database_setup_guide.py`
2. Check the documentation for your chosen database
3. Review the example implementations in this file
4. Test your implementation step by step

## Next Steps

1. Choose your database
2. Implement the connection and operations
3. Test thoroughly
4. Deploy your application

Remember: The application will show appropriate error messages until you implement your chosen database solution.