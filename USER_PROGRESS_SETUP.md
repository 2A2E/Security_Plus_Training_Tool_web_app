# User Progress Tracking Setup Guide

This guide explains how to set up the database tables for user progress tracking in Supabase.

## Overview

The profile and dashboard features require three new tables in Supabase:
- `user_quiz_results` - Stores quiz completion data
- `user_flashcard_progress` - Tracks flashcard views
- `user_study_sessions` - Tracks study time

## Setup Steps

### 1. Access Supabase SQL Editor

1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to SQL Editor (left sidebar)
4. Click "New Query"

### 2. Run the Schema SQL

Copy and paste the contents of `scripts/setup_user_progress_schema.sql` into the SQL Editor and click "Run".

Alternatively, you can run the SQL directly:

```sql
-- See scripts/setup_user_progress_schema.sql for the complete schema
```

### 3. Verify Tables Created

After running the SQL:

1. Go to Table Editor (left sidebar)
2. Verify these tables exist:
   - `user_quiz_results`
   - `user_flashcard_progress`
   - `user_study_sessions`

### 4. Verify Row Level Security (RLS)

The schema includes RLS policies that ensure users can only access their own data. These are automatically created when you run the SQL script.

## Features Enabled

Once the schema is set up, the following features will be available:

### Profile Page (`/profile`)
- Edit user information (first name, last name, experience level)
- View real-time statistics:
  - Total quizzes completed
  - Total flashcards viewed
  - Total practice tests completed
  - Average score
  - Total hours studied

### Dashboard Page (`/dashboard`)
- Overview statistics cards
- Recent quiz results table
- Section-wise progress breakdown
- Performance trends (last 30 days)
- Quick action buttons

### Automatic Progress Tracking
- Quiz results are automatically saved when quizzes are completed
- Flashcard views are tracked when users view flashcards
- Study sessions are tracked with duration

## Testing

After setup, you can test by:

1. Logging in as a user
2. Completing a quiz
3. Viewing flashcards
4. Checking the dashboard and profile pages to see your progress

## Troubleshooting

### Tables not created
- Make sure you're running the SQL in the correct Supabase project
- Check for any SQL errors in the Supabase logs

### RLS policies blocking access
- Verify RLS policies were created correctly
- Ensure users are authenticated (logged in)
- Check that `auth.uid()` matches the `user_id` in the tables

### No data showing
- Complete a quiz or view flashcards while logged in
- Check that the user_id in session matches the user_id in Supabase auth.users table
- Verify data was inserted by checking the tables directly in Supabase

## Schema Details

### user_quiz_results
Stores quiz completion data with:
- Quiz type (section_quiz, random_quiz, practice_test)
- Section number (for section quizzes)
- Score and percentage
- Duration

### user_flashcard_progress
Tracks flashcard views:
- Section number
- Cards viewed count
- Session ID

### user_study_sessions
Tracks study time:
- Session type (quiz, flashcard, practice_test)
- Duration in seconds
- Start and end timestamps

All tables include proper indexes for performance and RLS policies for security.

