-- Todo Application Database Schema
-- PostgreSQL 14+
-- This schema is managed by SQLAlchemy + Alembic in production

-- ============================================================================
-- Users Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for email lookups (login queries)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- Tasks Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT DEFAULT '',
  is_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for user lookups (list tasks for user)
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Index for sorting by creation date
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- ============================================================================
-- Constraints & Relationships
-- ============================================================================

-- Foreign key constraint (enforced by REFERENCES above)
-- Tasks.user_id must reference a valid Users.id
-- ON DELETE CASCADE: When user is deleted, delete their tasks

-- Unique constraint on email (enforced by UNIQUE above)
-- Prevents duplicate user registrations

-- ============================================================================
-- Initial Data (Optional - for testing)
-- ============================================================================

-- DO NOT include in production; handled by application during registration
-- Example:
-- INSERT INTO users (email, hashed_password) VALUES
--   ('test@example.com', '$2b$12$...');
--
-- INSERT INTO tasks (user_id, title, description, is_completed) VALUES
--   (1, 'Buy groceries', 'Milk, eggs, bread', FALSE),
--   (1, 'Complete project', 'Finish the todo app', FALSE);

-- ============================================================================
-- Notes
-- ============================================================================

-- 1. All timestamps are in UTC
-- 2. Passwords are hashed with bcrypt (min 60 chars)
-- 3. Soft deletes NOT used (hard delete on removal)
-- 4. No audit log (out of scope for MVP)
-- 5. Tasks ordered by created_at DESC (newest first)
-- 6. user_id is immutable (cannot reassign tasks)
-- 7. updated_at is managed by application (trigger not used)
