-- PostgreSQL schema for Learning Failure Lab

CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('STUDENT','TEACHER','ADMIN')),
  full_name VARCHAR(120) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE topics (
  id UUID PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE questions (
  id UUID PRIMARY KEY,
  topic_id UUID NOT NULL REFERENCES topics(id),
  content TEXT NOT NULL,
  difficulty SMALLINT NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE question_options (
  id UUID PRIMARY KEY,
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL DEFAULT FALSE,
  error_type VARCHAR(30),
  error_note TEXT,
  CONSTRAINT option_error_type_chk CHECK (
    error_type IS NULL OR error_type IN ('MISCONCEPTION','CONFUSION','LOGIC_GAP','RANDOM_GUESS','OVERCONFIDENCE')
  )
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  topic_id UUID NOT NULL REFERENCES topics(id),
  status VARCHAR(20) NOT NULL CHECK (status IN ('IN_PROGRESS','SUBMITTED')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  submitted_at TIMESTAMPTZ
);

CREATE TABLE attempts (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES questions(id),
  selected_option_id UUID NOT NULL REFERENCES question_options(id),
  is_correct BOOLEAN NOT NULL,
  latency_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (session_id, question_id)
);

CREATE TABLE error_events (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  topic_id UUID NOT NULL REFERENCES topics(id),
  question_id UUID NOT NULL REFERENCES questions(id),
  error_type VARCHAR(30) NOT NULL CHECK (error_type IN ('MISCONCEPTION','CONFUSION','LOGIC_GAP','RANDOM_GUESS','OVERCONFIDENCE')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  token_hash TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  actor_user_id UUID REFERENCES users(id),
  action VARCHAR(80) NOT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id UUID,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_questions_topic ON questions(topic_id);
CREATE INDEX idx_attempts_session ON attempts(session_id);
CREATE INDEX idx_error_events_user_time ON error_events(user_id, created_at DESC);
CREATE INDEX idx_sessions_user_time ON sessions(user_id, started_at DESC);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
