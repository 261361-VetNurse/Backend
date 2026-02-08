-- ====================================================================
-- Pet Medication Diary - MySQL Database Schema (IMPROVED)
-- Migration from MongoDB to MySQL 8.0+
-- Date: February 8, 2026
-- 
-- IMPROVEMENTS:
-- 1. Added user_id to medicines table (denormalization for performance)
-- 2. Added user_id, pet_id to notification tables (avoid complex JOINs)
-- 3. Added indexes for common query patterns
-- 4. Added triggers for automatic user_id propagation
-- ====================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables
DROP TABLE IF EXISTS appointments_notification;
DROP TABLE IF EXISTS medicines_notification;
DROP TABLE IF EXISTS pets_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS jwt_tokens;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- ====================================================================
-- 1. USERS TABLE
-- ====================================================================
CREATE TABLE users (
    user_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    
    -- Line Authentication
    line_id VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    picture_url TEXT,
    
    -- User Information
    fname VARCHAR(255) NOT NULL,
    lname VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'owner',
    is_registered BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Contact Information
    phone VARCHAR(20),
    email VARCHAR(255),
    
    -- Address Information
    address_line1 TEXT,
    address_line2 TEXT,
    subdistrict VARCHAR(100),
    district VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Thailand',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_line_id (line_id),
    INDEX idx_email (email),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User accounts with Line Authentication';

-- ====================================================================
-- 2. JWT_TOKENS TABLE
-- ====================================================================
CREATE TABLE jwt_tokens (
    token_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    access_token TEXT NOT NULL,
    key_id VARCHAR(255),
    token_type VARCHAR(50) DEFAULT 'Bearer',
    expires_at TIMESTAMP NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Constraints (1:1 relationship with users)
    UNIQUE KEY uk_user_id (user_id),
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='JWT tokens for user authentication (1 User : 1 JWT)';

-- ====================================================================
-- 3. PETS TABLE
-- ====================================================================
CREATE TABLE pets (
    pet_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Pet Information
    name VARCHAR(255) NOT NULL,
    species VARCHAR(100),
    breed VARCHAR(255),
    color VARCHAR(100),
    gender VARCHAR(20),
    birth_date DATE,
    weight_kg DECIMAL(6, 2),
    
    -- Medical Information
    allergies JSON COMMENT 'Array of allergy strings: ["penicillin", "chicken"]',
    infecund BOOLEAN DEFAULT FALSE COMMENT 'ทำหมัน/ตอนแล้ว',
    
    -- Media
    profile_image TEXT,
    
    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    in_medical BOOLEAN DEFAULT FALSE COMMENT 'กำลังอยู่ในระหว่างการรักษา',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_name (name),
    INDEX idx_user_deleted (user_id, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pet profiles owned by users (1 User : N Pets)';

-- ====================================================================
-- 4. MEDICINES TABLE (IMPROVED: Added user_id)
-- ====================================================================
CREATE TABLE medicines (
    medicine_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'Denormalized from pets.user_id for performance',
    pet_id BIGINT UNSIGNED NOT NULL,
    
    -- Medicine Information
    name VARCHAR(255) NOT NULL,
    properties TEXT COMMENT 'Medicine properties/description',
    dosage VARCHAR(100) COMMENT 'e.g., "1 tablet", "5ml"',
    
    -- Schedule Information
    frequency VARCHAR(50) NOT NULL COMMENT '-1=daily, 0-6=weekdays, comma-separated like "0,2,4"',
    status VARCHAR(20) DEFAULT 'TAKE' COMMENT 'TAKE=active, STOP=stopped',
    reminder_time JSON NOT NULL COMMENT 'Array of time strings: ["08:00", "20:00"]',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- History & Media
    notes JSON COMMENT 'Array of notes (max 3): ["note1", "note2", "note3"]',
    image_urls JSON COMMENT 'Array of image URLs',
    
    -- Status
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (status IN ('TAKE', 'STOP')),
    CHECK (start_date <= end_date),
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_pet_id (pet_id),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_user_status (user_id, status, is_deleted),
    INDEX idx_pet_status (pet_id, status, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Medication schedules for pets (1 Pet : N Medicines)';

-- ====================================================================
-- 5. MEDICINES_NOTIFICATION TABLE (IMPROVED: Added user_id, pet_id)
-- ====================================================================
CREATE TABLE medicines_notification (
    notification_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'For fast user-based queries',
    pet_id BIGINT UNSIGNED NOT NULL COMMENT 'For fast pet-based queries',
    medicine_id BIGINT UNSIGNED NOT NULL,
    
    -- Notification Information
    title VARCHAR(500) NOT NULL COMMENT 'e.g., "Time to give Amoxicillin to Lucky"',
    notification_at TIMESTAMP NOT NULL COMMENT 'Scheduled notification time',
    
    -- Status Tracking
    sending_status VARCHAR(50) DEFAULT 'not_sent' COMMENT 'not_sent, sent, failed',
    status VARCHAR(50) DEFAULT 'pending' COMMENT 'pending, sent, failed, canceled',
    sending_count INT DEFAULT 0 COMMENT 'Number of send attempts',
    istaken BOOLEAN DEFAULT FALSE COMMENT 'User marked as taken',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (sending_status IN ('not_sent', 'sent', 'failed')),
    CHECK (status IN ('pending', 'sent', 'failed', 'canceled')),
    
    -- Indexes (CRITICAL for notification scheduler)
    INDEX idx_user_id (user_id),
    INDEX idx_pet_id (pet_id),
    INDEX idx_medicine_id (medicine_id),
    INDEX idx_notification_at (notification_at),
    INDEX idx_istaken (istaken),
    INDEX idx_sending_status (sending_status),
    INDEX idx_medicine_date (medicine_id, notification_at),
    INDEX idx_user_date_taken (user_id, notification_at, istaken),
    INDEX idx_scheduler (notification_at, sending_status, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Medication reminder notifications (1 Medicine : N Notifications)';

-- ====================================================================
-- 6. APPOINTMENTS TABLE (IMPROVED: Added user_id)
-- ====================================================================
CREATE TABLE appointments (
    appointment_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'Denormalized from pets.user_id for performance',
    pet_id BIGINT UNSIGNED NOT NULL,
    
    -- Appointment Information
    location VARCHAR(500) NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    note TEXT,
    status VARCHAR(50) DEFAULT 'Upcoming',
    
    -- Status
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (status IN ('Upcoming', 'Completed', 'Canceled')),
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_pet_id (pet_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_user_status (user_id, status, is_deleted),
    INDEX idx_pet_status (pet_id, status, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Veterinary appointments for pets (1 Pet : N Appointments)';

-- ====================================================================
-- 7. APPOINTMENTS_NOTIFICATION TABLE (IMPROVED: Added user_id, pet_id)
-- ====================================================================
CREATE TABLE appointments_notification (
    notification_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'For fast user-based queries',
    pet_id BIGINT UNSIGNED NOT NULL COMMENT 'For fast pet-based queries',
    appointment_id BIGINT UNSIGNED NOT NULL,
    
    -- Notification Information
    title VARCHAR(500) NOT NULL COMMENT 'e.g., "Reminder: Appointment at ABC Clinic for Lucky"',
    notification_at TIMESTAMP NOT NULL COMMENT 'Created immediately after appointment',
    
    -- Status Tracking
    sending_status VARCHAR(50) DEFAULT 'not_sent',
    status VARCHAR(50) DEFAULT 'pending',
    sending_count INT DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (sending_status IN ('not_sent', 'sent', 'failed')),
    CHECK (status IN ('pending', 'sent', 'failed', 'canceled')),
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_pet_id (pet_id),
    INDEX idx_appointment_id (appointment_id),
    INDEX idx_notification_at (notification_at),
    INDEX idx_sending_status (sending_status),
    INDEX idx_status (status),
    INDEX idx_user_date (user_id, notification_at),
    INDEX idx_scheduler (notification_at, sending_status, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Appointment reminder notifications (1 Appointment : N Notifications)';

-- ====================================================================
-- 8. PETS_RECORDS TABLE
-- ====================================================================
CREATE TABLE pets_records (
    record_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id BIGINT UNSIGNED NOT NULL,
    
    -- Record Information
    note TEXT NOT NULL,
    images JSON COMMENT 'Array of image URLs',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_pet_id (pet_id),
    INDEX idx_created_at (created_at),
    INDEX idx_pet_date (pet_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Health and behavior records for pets (1 Pet : N Records)';

-- ====================================================================
-- TRIGGERS: Auto-populate user_id (Denormalization)
-- ====================================================================

-- Trigger: Auto-set user_id when inserting medicine
DELIMITER $$
CREATE TRIGGER trg_medicines_before_insert
BEFORE INSERT ON medicines
FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL OR NEW.user_id = 0 THEN
        SELECT user_id INTO NEW.user_id
        FROM pets
        WHERE pet_id = NEW.pet_id;
    END IF;
END$$

-- Trigger: Auto-set user_id when inserting appointment
CREATE TRIGGER trg_appointments_before_insert
BEFORE INSERT ON appointments
FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL OR NEW.user_id = 0 THEN
        SELECT user_id INTO NEW.user_id
        FROM pets
        WHERE pet_id = NEW.pet_id;
    END IF;
END$$

DELIMITER ;

-- ====================================================================
-- VIEWS FOR COMMON QUERIES
-- ====================================================================

-- View: Medicine notifications with full details
CREATE OR REPLACE VIEW v_medicines_notifications_full AS
SELECT 
    mn.notification_id,
    mn.user_id,
    mn.pet_id,
    mn.medicine_id,
    mn.title,
    mn.notification_at,
    mn.sending_status,
    mn.status,
    mn.istaken,
    m.name AS medicine_name,
    m.dosage,
    m.frequency,
    p.name AS pet_name,
    p.species,
    u.fname,
    u.lname,
    u.line_id,
    u.display_name
FROM medicines_notification mn
JOIN medicines m ON mn.medicine_id = m.medicine_id
JOIN pets p ON mn.pet_id = p.pet_id
JOIN users u ON mn.user_id = u.user_id
WHERE m.is_deleted = FALSE AND p.is_deleted = FALSE AND u.is_deleted = FALSE;

-- View: Appointment notifications with full details
CREATE OR REPLACE VIEW v_appointments_notifications_full AS
SELECT 
    an.notification_id,
    an.user_id,
    an.pet_id,
    an.appointment_id,
    an.title,
    an.notification_at,
    an.sending_status,
    an.status,
    a.location,
    a.appointment_date,
    a.note AS appointment_note,
    a.status AS appointment_status,
    p.name AS pet_name,
    p.species,
    u.fname,
    u.lname,
    u.line_id,
    u.display_name
FROM appointments_notification an
JOIN appointments a ON an.appointment_id = a.appointment_id
JOIN pets p ON an.pet_id = p.pet_id
JOIN users u ON an.user_id = u.user_id
WHERE a.is_deleted = FALSE AND p.is_deleted = FALSE AND u.is_deleted = FALSE;

-- View: User dashboard summary
CREATE OR REPLACE VIEW v_user_dashboard AS
SELECT 
    u.user_id,
    u.fname,
    u.lname,
    u.line_id,
    u.display_name,
    COUNT(DISTINCT p.pet_id) AS total_pets,
    COUNT(DISTINCT CASE WHEN m.status = 'TAKE' AND m.is_deleted = FALSE THEN m.medicine_id END) AS total_active_medicines,
    COUNT(DISTINCT CASE WHEN a.status = 'Upcoming' AND a.is_deleted = FALSE THEN a.appointment_id END) AS total_upcoming_appointments,
    COUNT(DISTINCT CASE WHEN mn.istaken = FALSE AND mn.notification_at >= NOW() THEN mn.notification_id END) AS pending_medicine_notifications
FROM users u
LEFT JOIN pets p ON u.user_id = p.user_id AND p.is_deleted = FALSE
LEFT JOIN medicines m ON p.pet_id = m.pet_id
LEFT JOIN appointments a ON p.pet_id = a.pet_id
LEFT JOIN medicines_notification mn ON m.medicine_id = mn.medicine_id
WHERE u.is_deleted = FALSE
GROUP BY u.user_id, u.fname, u.lname, u.line_id, u.display_name;

-- View: Active medicines with next notification
CREATE OR REPLACE VIEW v_active_medicines_with_next_notification AS
SELECT 
    m.medicine_id,
    m.user_id,
    m.pet_id,
    m.name AS medicine_name,
    m.dosage,
    m.frequency,
    m.status,
    m.start_date,
    m.end_date,
    p.name AS pet_name,
    MIN(CASE WHEN mn.istaken = FALSE AND mn.notification_at >= NOW() 
        THEN mn.notification_at END) AS next_notification_at,
    COUNT(CASE WHEN mn.istaken = FALSE AND mn.notification_at >= NOW() 
        THEN 1 END) AS pending_notifications_count
FROM medicines m
JOIN pets p ON m.pet_id = p.pet_id
LEFT JOIN medicines_notification mn ON m.medicine_id = mn.medicine_id
WHERE m.status = 'TAKE' AND m.is_deleted = FALSE AND p.is_deleted = FALSE
GROUP BY m.medicine_id, m.user_id, m.pet_id, m.name, m.dosage, 
         m.frequency, m.status, m.start_date, m.end_date, p.name;

-- ====================================================================
-- SAMPLE DATA INSERT (Optional - for testing)
-- ====================================================================

-- Insert test user
INSERT INTO users (line_id, display_name, fname, lname, phone, email)
VALUES ('U1234567890abcdef', 'John Doe', 'John', 'Doe', '0812345678', 'john@example.com');

-- Insert test pet
INSERT INTO pets (user_id, name, species, breed, gender, birth_date, weight_kg, allergies, infecund)
VALUES (
    1, 
    'Lucky', 
    'Dog', 
    'Golden Retriever', 
    'male', 
    '2020-05-15', 
    25.5,
    JSON_ARRAY('penicillin', 'chicken'),
    FALSE
);

-- Insert test medicine (user_id will be auto-populated by trigger)
INSERT INTO medicines (pet_id, name, dosage, frequency, status, reminder_time, start_date, end_date, notes)
VALUES (
    1,
    'Amoxicillin',
    '1 tablet',
    '-1',
    'TAKE',
    JSON_ARRAY('08:00', '20:00'),
    CURDATE(),
    DATE_ADD(CURDATE(), INTERVAL 7 DAY),
    JSON_ARRAY('Prescribed by Dr. Smith', 'Take with food')
);

-- Insert test appointment (user_id will be auto-populated by trigger)
INSERT INTO appointments (pet_id, location, appointment_date, status, note)
VALUES (
    1,
    'ABC Veterinary Clinic',
    DATE_ADD(NOW(), INTERVAL 7 DAY),
    'Upcoming',
    'Annual checkup and vaccination'
);

-- ====================================================================
-- USEFUL QUERIES FOR MIGRATION
-- ====================================================================

-- Query 1: Get all pending medicine notifications for a user (with LINE info)
-- SELECT * FROM v_medicines_notifications_full 
-- WHERE user_id = 1 AND istaken = FALSE AND notification_at >= NOW()
-- ORDER BY notification_at ASC;

-- Query 2: Get medicines that need notification generation today
-- SELECT m.*, p.name as pet_name, p.user_id
-- FROM medicines m
-- JOIN pets p ON m.pet_id = p.pet_id
-- WHERE m.status = 'TAKE' 
--   AND m.is_deleted = FALSE
--   AND m.end_date >= CURDATE()
--   AND m.start_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY);

-- Query 3: Get user's pets with active medicines count
-- SELECT p.*, COUNT(m.medicine_id) as active_medicines_count
-- FROM pets p
-- LEFT JOIN medicines m ON p.pet_id = m.pet_id AND m.status = 'TAKE' AND m.is_deleted = FALSE
-- WHERE p.user_id = 1 AND p.is_deleted = FALSE
-- GROUP BY p.pet_id;

-- Query 4: Get notifications to send (for notification service)
-- SELECT user_id, line_id, notification_id, title, notification_at
-- FROM v_medicines_notifications_full
-- WHERE sending_status = 'not_sent'
--   AND notification_at <= NOW()
--   AND status = 'pending'
-- ORDER BY notification_at ASC
-- LIMIT 100;

-- ====================================================================
-- MIGRATION NOTES
-- ====================================================================
-- 
-- IMPORTANT CHANGES FROM YOUR ORIGINAL SCHEMA:
-- 
-- 1. Added user_id to medicines table
--    - Avoids JOIN with pets table in common queries
--    - Auto-populated by trigger
-- 
-- 2. Added user_id, pet_id to notification tables
--    - Critical for notification scheduler performance
--    - Enables direct user-based queries without JOINs
--    - Matches MongoDB schema structure
-- 
-- 3. Added comprehensive indexes
--    - Composite indexes for common query patterns
--    - Scheduler-specific indexes
-- 
-- 4. Added triggers for automatic denormalization
--    - Maintains data consistency
--    - Transparent to application code
-- 
-- 5. Enhanced views for common operations
--    - Simplifies application queries
--    - Maintains MongoDB-like document structure
--
-- ====================================================================
