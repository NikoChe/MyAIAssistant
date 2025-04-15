\echo '👷 Старт выполнения init.sql'

-- Таблица клиентов
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    username VARCHAR,
    initial_request TEXT
);

-- Таблица сессий
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    session_type VARCHAR NOT NULL,
    answers_json JSON NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Версии вопросов
CREATE TABLE IF NOT EXISTS question_versions (
    id TEXT PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Структура вопросов
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES question_versions(id),
    parent_id INTEGER REFERENCES questions(id),
    text TEXT NOT NULL,
    type TEXT DEFAULT 'text',
    required BOOLEAN DEFAULT TRUE,
    options JSON,
    "order" INTEGER DEFAULT 0
);

\echo '✅ init.sql выполнен полностью'
