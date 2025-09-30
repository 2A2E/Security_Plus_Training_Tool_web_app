#!/usr/bin/env python3
"""
Script to set up the database schema in Supabase
This script creates the questions table and sets up the necessary structure.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_schema_sql():
    """Generate the SQL schema for the questions table"""
    return """
-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    explanation TEXT,
    correct_answer TEXT,
    correct_answers TEXT, -- JSON array for multiple correct answers
    options TEXT, -- JSON array for multiple choice options
    tags TEXT, -- JSON array of tags
    reference VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_question_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_questions_updated_at ON questions;
CREATE TRIGGER update_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for better security
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for authenticated users
-- For now, we'll allow all operations (you can restrict this later)
CREATE POLICY "Allow all operations on questions" ON questions
    FOR ALL USING (true);

-- Insert some sample questions for testing
INSERT INTO questions (question_text, question_type, category, difficulty, explanation, correct_answer, options, tags, reference) VALUES
(
    'Which of the following is the primary purpose of a firewall?',
    'multiple_choice',
    'Technologies and Tools',
    'Beginner',
    'A firewall''s primary purpose is to control and monitor network traffic between different network segments, acting as a barrier between trusted and untrusted networks.',
    '1',
    '["To encrypt data in transit", "To control network traffic and access", "To authenticate users", "To store backup data"]',
    '["firewall", "network-security", "access-control"]',
    'CompTIA Security+ SY0-601 Study Guide'
),
(
    'What type of attack involves sending malicious code through a web application to execute on a user''s browser?',
    'multiple_choice',
    'Threats, Attacks, and Vulnerabilities',
    'Intermediate',
    'Cross-Site Scripting (XSS) attacks involve injecting malicious scripts into web applications that are then executed in the victim''s browser.',
    '1',
    '["SQL Injection", "Cross-Site Scripting (XSS)", "Buffer Overflow", "Man-in-the-Middle"]',
    '["xss", "web-security", "injection-attacks"]',
    'OWASP Top 10'
),
(
    'Two-factor authentication (2FA) requires exactly two different types of authentication factors.',
    'true_false',
    'Identity and Access Management',
    'Beginner',
    'Two-factor authentication requires two different types of authentication factors from the three categories: something you know, something you have, or something you are.',
    'true',
    '[]',
    '["2fa", "authentication", "multi-factor"]',
    'NIST SP 800-63B'
),
(
    'The process of converting plaintext to ciphertext is called _____.',
    'fill_in_blank',
    'Cryptography and PKI',
    'Beginner',
    'Encryption is the process of converting readable plaintext into unreadable ciphertext using an algorithm and key.',
    'encryption',
    '["encryption", "encrypting"]',
    '["encryption", "cryptography", "terminology"]',
    'CompTIA Security+ SY0-601'
)
ON CONFLICT DO NOTHING;
"""

def show_setup_instructions():
    """Display instructions for setting up the schema"""
    print("Supabase Schema Setup Instructions")
    print("=" * 40)
    print()
    print("To set up the database schema in Supabase:")
    print()
    print("1. Go to your Supabase dashboard:")
    print("   https://supabase.com/dashboard")
    print()
    print("2. Select your project: security+")
    print()
    print("3. Go to the SQL Editor (left sidebar)")
    print()
    print("4. Click 'New Query'")
    print()
    print("5. Copy and paste the following SQL:")
    print()
    print("-" * 50)
    print(create_schema_sql())
    print("-" * 50)
    print()
    print("6. Click 'Run' to execute the SQL")
    print()
    print("7. Verify the table was created by going to:")
    print("   Table Editor > questions")
    print()
    print("The schema includes:")
    print("- questions table with all necessary fields")
    print("- Indexes for better performance")
    print("- Automatic timestamp updates")
    print("- Row Level Security (RLS) enabled")
    print("- Sample questions for testing")
    print()

def test_connection():
    """Test the Supabase connection"""
    print("Testing Supabase Connection...")
    print("=" * 30)
    
    try:
        from database.connection import db_manager
        
        print(f"Supabase URL: {db_manager.supabase_url}")
        print(f"Database Name: {db_manager.database_name}")
        
        # Test connection
        client = db_manager.get_client()
        print("✓ Supabase client created successfully")
        
        # Test table access
        try:
            result = client.table('questions').select('id').limit(1).execute()
            print("✓ Successfully connected to questions table")
            print(f"✓ Found {len(result.data)} sample questions")
        except Exception as e:
            print(f"⚠️  Questions table not found or empty: {e}")
            print("   This is normal if you haven't run the schema setup yet.")
        
        print("\n✓ Supabase connection test completed!")
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Supabase URL and API key")
        print("2. Make sure your Supabase project is active")
        print("3. Verify your internet connection")
        return False
    
    return True

def main():
    """Main function"""
    print("Security+ Training Tool - Supabase Setup")
    print("=" * 45)
    print()
    
    # Test connection first
    if test_connection():
        print()
        show_setup_instructions()
        
        print("\nNext Steps:")
        print("=" * 15)
        print("1. Run the SQL schema in your Supabase dashboard")
        print("2. Test the application: python run.py")
        print("3. Check API endpoints: /api/questions, /api/categories, etc.")
    else:
        print("\nPlease fix the connection issues before proceeding.")

if __name__ == "__main__":
    main()
