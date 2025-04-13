-- Clients table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT,
    username TEXT,
    initial_request TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status TEXT DEFAULT 'pending', -- pending, confirmed, rejected
    topic TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Availability slots (optional pre-generated schedule)
CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    type TEXT, -- reminder_12h, reminder_6h, etc.
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Owner preferences table
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    name TEXT,
    work_start TIME DEFAULT '09:00',
    work_end TIME DEFAULT '18:00',
    slot_duration INTEGER DEFAULT 60,
    break_between INTEGER DEFAULT 15,
    slots_per_day_limit INTEGER DEFAULT 100,
    bookable_ratio INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW()
);
