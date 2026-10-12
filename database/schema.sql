-- SQLite schema for the Elderly Household Welfare Check-in System
-- Academic prototype. Does not store plain-text passwords.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30),
    role VARCHAR(30) NOT NULL CHECK (role IN ('admin', 'caregiver', 'elderly', 'family')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE TABLE IF NOT EXISTS elderly_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    full_name VARCHAR(120) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    address VARCHAR(255),
    phone VARCHAR(30),
    mobility_status VARCHAR(50),
    living_arrangement VARCHAR(50),
    emergency_contact_name VARCHAR(120),
    emergency_contact_phone VARCHAR(30),
    emergency_contact_relationship VARCHAR(50),
    secondary_contact_name VARCHAR(120),
    secondary_contact_phone VARCHAR(30),
    welfare_notes TEXT,
    consent_given BOOLEAN NOT NULL DEFAULT 0,
    consent_date DATETIME,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TABLE IF NOT EXISTS caregiver_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    caregiver_id INTEGER NOT NULL REFERENCES users(id),
    is_primary BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    notes VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS family_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    family_user_id INTEGER NOT NULL REFERENCES users(id),
    relationship VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS checkin_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly')),
    window_start TIME NOT NULL,
    window_end TIME NOT NULL,
    days_of_week VARCHAR(20) NOT NULL DEFAULT '1,2,3,4,5,6,7',
    grace_minutes INTEGER NOT NULL DEFAULT 60,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checkin_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER REFERENCES checkin_schedules(id),
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    submitted_by INTEGER REFERENCES users(id),
    status VARCHAR(20) NOT NULL,
    method VARCHAR(20),
    mood VARCHAR(20),
    needs_assistance BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT,
    due_at DATETIME NOT NULL,
    submitted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_checkin_elderly_due ON checkin_records(elderly_id, due_at);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    checkin_record_id INTEGER REFERENCES checkin_records(id),
    alert_type VARCHAR(40) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    title VARCHAR(200) NOT NULL,
    reason TEXT NOT NULL,
    risk_score INTEGER,
    is_ai_flagged BOOLEAN NOT NULL DEFAULT 0,
    assigned_to INTEGER REFERENCES users(id),
    escalated_to INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME,
    resolved_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_alerts_elderly_status ON alerts(elderly_id, status);

CREATE TABLE IF NOT EXISTS alert_acknowledgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL REFERENCES alerts(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    notes TEXT,
    acknowledged_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS caregiver_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    caregiver_id INTEGER NOT NULL REFERENCES users(id),
    visit_type VARCHAR(30) NOT NULL,
    visited_at DATETIME NOT NULL,
    duration_minutes INTEGER,
    observations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS followup_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER REFERENCES alerts(id),
    elderly_id INTEGER NOT NULL REFERENCES elderly_profiles(id),
    caregiver_id INTEGER NOT NULL REFERENCES users(id),
    action_type VARCHAR(40) NOT NULL,
    outcome VARCHAR(40) NOT NULL,
    description TEXT,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    message TEXT,
    link VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(80) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(80) NOT NULL UNIQUE,
    value VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);
