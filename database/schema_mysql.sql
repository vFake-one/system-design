-- MySQL-oriented schema (optional migration target).
-- The assessed prototype uses SQLite. Review types before production use.

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30),
    role VARCHAR(30) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'caregiver', 'elderly', 'family'))
);

CREATE TABLE elderly_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
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
    consent_given TINYINT(1) NOT NULL DEFAULT 0,
    consent_date DATETIME,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    CONSTRAINT fk_elderly_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE caregiver_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elderly_id INT NOT NULL,
    caregiver_id INT NOT NULL,
    is_primary TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INT NULL,
    notes VARCHAR(255),
    CONSTRAINT fk_assign_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_assign_caregiver FOREIGN KEY (caregiver_id) REFERENCES users(id),
    CONSTRAINT fk_assign_by FOREIGN KEY (assigned_by) REFERENCES users(id)
);

CREATE TABLE family_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elderly_id INT NOT NULL,
    family_user_id INT NOT NULL,
    relationship VARCHAR(50),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_fam_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_fam_user FOREIGN KEY (family_user_id) REFERENCES users(id)
);

CREATE TABLE checkin_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elderly_id INT NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    window_start TIME NOT NULL,
    window_end TIME NOT NULL,
    days_of_week VARCHAR(20) NOT NULL DEFAULT '1,2,3,4,5,6,7',
    grace_minutes INT NOT NULL DEFAULT 60,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sched_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id)
);

CREATE TABLE checkin_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NULL,
    elderly_id INT NOT NULL,
    submitted_by INT NULL,
    status VARCHAR(20) NOT NULL,
    method VARCHAR(20),
    mood VARCHAR(20),
    needs_assistance TINYINT(1) NOT NULL DEFAULT 0,
    notes TEXT,
    due_at DATETIME NOT NULL,
    submitted_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rec_sched FOREIGN KEY (schedule_id) REFERENCES checkin_schedules(id),
    CONSTRAINT fk_rec_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_rec_user FOREIGN KEY (submitted_by) REFERENCES users(id)
);

CREATE INDEX idx_checkin_elderly_due ON checkin_records(elderly_id, due_at);

CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elderly_id INT NOT NULL,
    checkin_record_id INT NULL,
    alert_type VARCHAR(40) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    title VARCHAR(200) NOT NULL,
    reason TEXT NOT NULL,
    risk_score INT NULL,
    is_ai_flagged TINYINT(1) NOT NULL DEFAULT 0,
    assigned_to INT NULL,
    escalated_to INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME NULL,
    resolved_at DATETIME NULL,
    CONSTRAINT fk_alert_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_alert_record FOREIGN KEY (checkin_record_id) REFERENCES checkin_records(id),
    CONSTRAINT fk_alert_assigned FOREIGN KEY (assigned_to) REFERENCES users(id),
    CONSTRAINT fk_alert_escalated FOREIGN KEY (escalated_to) REFERENCES users(id)
);

CREATE TABLE alert_acknowledgements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT NOT NULL,
    user_id INT NOT NULL,
    notes TEXT,
    acknowledged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ack_alert FOREIGN KEY (alert_id) REFERENCES alerts(id),
    CONSTRAINT fk_ack_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE caregiver_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elderly_id INT NOT NULL,
    caregiver_id INT NOT NULL,
    visit_type VARCHAR(30) NOT NULL,
    visited_at DATETIME NOT NULL,
    duration_minutes INT NULL,
    observations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_visit_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_visit_caregiver FOREIGN KEY (caregiver_id) REFERENCES users(id)
);

CREATE TABLE followup_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT NULL,
    elderly_id INT NOT NULL,
    caregiver_id INT NOT NULL,
    action_type VARCHAR(40) NOT NULL,
    outcome VARCHAR(40) NOT NULL,
    description TEXT,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fu_alert FOREIGN KEY (alert_id) REFERENCES alerts(id),
    CONSTRAINT fk_fu_elderly FOREIGN KEY (elderly_id) REFERENCES elderly_profiles(id),
    CONSTRAINT fk_fu_caregiver FOREIGN KEY (caregiver_id) REFERENCES users(id)
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    link VARCHAR(255),
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_note_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(80) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(80) NOT NULL UNIQUE,
    value VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);
