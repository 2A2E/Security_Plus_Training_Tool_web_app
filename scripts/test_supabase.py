#!/usr/bin/env python3
"""
Simple test script for Supabase integration
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    print("Testing Supabase Integration...")
    print("=" * 35)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from database.connection import db_manager
        from database.question_manager import question_manager
        print("   ✓ Imports successful")
        
        # Test connection
        print("2. Testing connection...")
        client = db_manager.get_client()
        print("   ✓ Supabase client created")
        
        # Test table access
        print("3. Testing table access...")
        try:
            result = client.table('questions').select('id').limit(1).execute()
            print("   ✓ Questions table accessible")
            print(f"   ✓ Found {len(result.data)} questions")
        except Exception as e:
            print(f"   ⚠️  Questions table not found: {e}")
            print("   This is normal if you haven't created the table yet.")
        
        # Test question manager
        print("4. Testing question manager...")
        if question_manager:
            count = question_manager.get_question_count()
            print(f"   ✓ Question manager working, count: {count}")
        else:
            print("   ⚠️  Question manager not available")
        
        print("\n✓ Supabase integration test completed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nTo fix this:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Make sure you're in the correct directory")
        return False
        
    except Exception as e:
        print(f"✗ Connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Supabase URL and API key")
        print("2. Make sure your Supabase project is active")
        print("3. Verify your internet connection")
        return False

if __name__ == "__main__":
    test_supabase_connection()
