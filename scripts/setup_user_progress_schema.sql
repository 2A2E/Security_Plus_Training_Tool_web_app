-- User Progress Tracking Schema for Security+ Training Tool
-- Run this SQL in your Supabase SQL Editor

-- Create user_quiz_results table
CREATE TABLE IF NOT EXISTS user_quiz_results (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    quiz_id VARCHAR(255),
    quiz_type VARCHAR(50) NOT NULL, -- 'section_quiz', 'random_quiz', 'practice_test'
    section INTEGER,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    duration_seconds INTEGER,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_flashcard_progress table
CREATE TABLE IF NOT EXISTS user_flashcard_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    section INTEGER NOT NULL,
    cards_viewed INTEGER DEFAULT 1,
    session_id VARCHAR(255),
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_study_sessions table
CREATE TABLE IF NOT EXISTS user_study_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'quiz', 'flashcard', 'practice_test'
    section INTEGER,
    duration_seconds INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_quiz_results_user_id ON user_quiz_results(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_results_completed_at ON user_quiz_results(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_quiz_results_quiz_type ON user_quiz_results(quiz_type);
CREATE INDEX IF NOT EXISTS idx_user_quiz_results_section ON user_quiz_results(section);

CREATE INDEX IF NOT EXISTS idx_user_flashcard_progress_user_id ON user_flashcard_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_flashcard_progress_section ON user_flashcard_progress(section);
CREATE INDEX IF NOT EXISTS idx_user_flashcard_progress_viewed_at ON user_flashcard_progress(viewed_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_study_sessions_user_id ON user_study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_study_sessions_started_at ON user_study_sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_study_sessions_session_type ON user_study_sessions(session_type);

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE user_quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_flashcard_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_study_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for user_quiz_results
-- Users can only access their own quiz results
CREATE POLICY "Users can view their own quiz results" ON user_quiz_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own quiz results" ON user_quiz_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own quiz results" ON user_quiz_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own quiz results" ON user_quiz_results
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for user_flashcard_progress
-- Users can only access their own flashcard progress
CREATE POLICY "Users can view their own flashcard progress" ON user_flashcard_progress
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own flashcard progress" ON user_flashcard_progress
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own flashcard progress" ON user_flashcard_progress
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own flashcard progress" ON user_flashcard_progress
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for user_study_sessions
-- Users can only access their own study sessions
CREATE POLICY "Users can view their own study sessions" ON user_study_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own study sessions" ON user_study_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own study sessions" ON user_study_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own study sessions" ON user_study_sessions
    FOR DELETE USING (auth.uid() = user_id);

