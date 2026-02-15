-- ====================================================================
-- Pet Medication Diary - Sample Data Insert Script
-- Date: February 9, 2026
-- Description: Comprehensive sample data for testing and development
-- ====================================================================

-- Disable foreign key checks for easier insertion
SET FOREIGN_KEY_CHECKS = 0;

-- ====================================================================
-- 1. INSERT USERS (Pet Owners)
-- ====================================================================

INSERT INTO users (line_id, display_name, fname, lname, role, is_registered, phone, email, 
                   address_line1, address_line2, subdistrict, district, province, postal_code, country)
VALUES 
-- User 1: Somchai (Registered, complete profile)
('U1a2b3c4d5e6f7g8h9i0', 'Somchai K.', 'สมชาย', 'คำดี', 'owner', TRUE, '0812345678', 'somchai.k@gmail.com',
 '123/45 หมู่บ้านสวนสุข', 'ซอยรามคำแหง 24', 'หัวหมาก', 'บางกะปิ', 'กรุงเทพมหานคร', '10240', 'Thailand'),

-- User 2: Siriwan (Registered, complete profile)
('U2b3c4d5e6f7g8h9i0j1', 'Siriwan P.', 'ศิริวรรณ', 'พรหมมา', 'owner', TRUE, '0823456789', 'siriwan.p@hotmail.com',
 '456/78 คอนโดลุมพินี', 'ถนนพระราม 4', 'คลองเตย', 'คลองเตย', 'กรุงเทพมหานคร', '10110', 'Thailand'),

-- User 3: Nattapong (Registered, minimal info)
('U3c4d5e6f7g8h9i0j1k2', 'Nat N.', 'ณัฐพงษ์', 'นาคทอง', 'owner', TRUE, '0834567890', 'nattapong.n@outlook.com',
 NULL, NULL, NULL, NULL, NULL, NULL, 'Thailand'),

-- User 4: Pimchanok (New user, not fully registered)
('U4d5e6f7g8h9i0j1k2l3', 'Pim C.', 'พิมพ์ชนก', 'สุขสันต์', 'owner', FALSE, '0845678901', NULL,
 NULL, NULL, NULL, NULL, NULL, NULL, 'Thailand'),

-- User 5: Wanchai (Registered, complete profile)
('U5e6f7g8h9i0j1k2l3m4', 'Wanchai S.', 'วันชัย', 'สว่างแจ้ง', 'owner', TRUE, '0856789012', 'wanchai.s@yahoo.com',
 '789/12 บ้านเดี่ยว', 'ถนนเพชรบุรี', 'มักกะสัน', 'ราชเทวี', 'กรุงเทพมหานคร', '10400', 'Thailand');

-- ====================================================================
-- 2. INSERT PETS (Multiple pets for different owners)
-- ====================================================================

INSERT INTO pets (user_id, name, species, breed, color, gender, birth_date, weight_kg, 
                  allergies, infecund, profile_image, is_verified, in_medical)
VALUES 
-- Somchai's pets (user_id = 1)
(1, 'Lucky', 'Dog', 'Golden Retriever', 'Golden', 'male', '2020-05-15', 28.50, 
 JSON_ARRAY('penicillin', 'chicken'), FALSE, 'https://example.com/images/lucky.jpg', TRUE, FALSE),

(1, 'Mimi', 'Cat', 'Persian', 'White', 'female', '2021-03-20', 4.20, 
 JSON_ARRAY(), TRUE, 'https://example.com/images/mimi.jpg', TRUE, FALSE),

-- Siriwan's pets (user_id = 2)
(2, 'Max', 'Dog', 'Poodle', 'Brown', 'male', '2019-08-10', 6.80, 
 JSON_ARRAY('dairy'), TRUE, 'https://example.com/images/max.jpg', TRUE, TRUE),

(2, 'Bella', 'Cat', 'Siamese', 'Cream', 'female', '2022-01-05', 3.50, 
 JSON_ARRAY(), FALSE, 'https://example.com/images/bella.jpg', TRUE, FALSE),

(2, 'Coco', 'Dog', 'Chihuahua', 'Black', 'female', '2023-06-12', 2.10, 
 JSON_ARRAY('beef'), FALSE, 'https://example.com/images/coco.jpg', TRUE, FALSE),

-- Nattapong's pet (user_id = 3)
(3, 'Tiger', 'Cat', 'Bengal', 'Orange', 'male', '2020-11-25', 5.50, 
 JSON_ARRAY('fish'), FALSE, 'https://example.com/images/tiger.jpg', TRUE, FALSE),

-- Pimchanok's pet (user_id = 4)
(4, 'Brownie', 'Dog', 'Beagle', 'Brown', 'male', '2021-07-30', 12.00, 
 JSON_ARRAY(), FALSE, NULL, FALSE, FALSE),

-- Wanchai's pets (user_id = 5)
(5, 'Snow', 'Cat', 'Scottish Fold', 'White', 'female', '2022-09-18', 4.80, 
 JSON_ARRAY(), TRUE, 'https://example.com/images/snow.jpg', TRUE, FALSE),

(5, 'Rocky', 'Dog', 'Labrador', 'Black', 'male', '2018-12-01', 32.00, 
 JSON_ARRAY('corn'), FALSE, 'https://example.com/images/rocky.jpg', TRUE, FALSE);

-- ====================================================================
-- 3. INSERT MEDICINES (Medication schedules)
-- ====================================================================

INSERT INTO medicines (user_id, pet_id, name, properties, dosage, frequency, status, 
                       reminder_time, start_date, end_date, notes, image_urls)
VALUES 
-- Lucky's medicines (pet_id = 1)
(1, 1, 'Amoxicillin', 'Antibiotic for bacterial infections', '500mg tablet', '-1', 'TAKE',
 JSON_ARRAY('08:00', '20:00'), '2026-02-01', '2026-02-14', 
 JSON_ARRAY('Prescribed by Dr. Somkid', 'Take with food', 'Monitor for allergic reactions'),
 JSON_ARRAY('https://example.com/meds/amoxicillin.jpg')),

(1, 1, 'Heartgard Plus', 'Heartworm prevention', '1 chewable tablet', '0', 'TAKE',
 JSON_ARRAY('09:00'), '2026-01-06', '2026-12-31', 
 JSON_ARRAY('Give every Monday', 'Can be given with or without food'),
 JSON_ARRAY()),

-- Mimi's medicines (pet_id = 2)
(1, 2, 'Revolution', 'Flea and tick prevention', '1 pipette', '1', 'TAKE',
 JSON_ARRAY('10:00'), '2026-01-07', '2026-12-31', 
 JSON_ARRAY('Apply every Tuesday', 'Apply to skin between shoulder blades'),
 JSON_ARRAY('https://example.com/meds/revolution.jpg')),

-- Max's medicines (pet_id = 3) - Currently in medical treatment
(2, 3, 'Prednisone', 'Anti-inflammatory steroid', '5mg tablet', '-1', 'TAKE',
 JSON_ARRAY('07:00', '19:00'), '2026-02-05', '2026-02-19', 
 JSON_ARRAY('For skin allergy treatment', 'Reduce dosage gradually'),
 JSON_ARRAY()),

(2, 3, 'Apoquel', 'Allergy relief', '16mg tablet', '-1', 'TAKE',
 JSON_ARRAY('08:00'), '2026-02-01', '2026-03-01', 
 JSON_ARRAY('Long-term allergy management'),
 JSON_ARRAY()),

-- Bella's medicine (pet_id = 4)
(2, 4, 'Drontal', 'Deworming medication', '1 tablet', '0,3', 'TAKE',
 JSON_ARRAY('09:00'), '2026-02-03', '2026-02-17', 
 JSON_ARRAY('Give on Monday and Thursday', 'Fast for 2 hours before'),
 JSON_ARRAY()),

-- Coco's medicine (pet_id = 5)
(2, 5, 'Vitamin Supplement', 'Daily multivitamin', '1 tablet', '-1', 'TAKE',
 JSON_ARRAY('08:30'), '2026-01-15', '2026-06-15', 
 JSON_ARRAY('For growing puppy'),
 JSON_ARRAY()),

-- Tiger's medicine (pet_id = 6)
(3, 6, 'Metacam', 'Pain relief', '0.5ml oral suspension', '-1', 'STOP',
 JSON_ARRAY('08:00'), '2026-01-10', '2026-01-24', 
 JSON_ARRAY('Treatment completed', 'Was for post-surgery pain'),
 JSON_ARRAY()),

-- Rocky's medicine (pet_id = 9)
(5, 9, 'Glucosamine', 'Joint supplement', '1 tablet', '-1', 'TAKE',
 JSON_ARRAY('09:00'), '2026-01-01', '2026-12-31', 
 JSON_ARRAY('For senior dog joint health', 'Long-term supplement'),
 JSON_ARRAY());

-- ====================================================================
-- 4. INSERT APPOINTMENTS (Veterinary appointments)
-- ====================================================================

INSERT INTO appointments (user_id, pet_id, location, appointment_date, note, status)
VALUES 
-- Lucky's appointments (pet_id = 1)
(1, 1, 'ABC Veterinary Clinic, Sukhumvit 63', '2026-02-15 10:00:00', 
 'Annual checkup and vaccination (Rabies, DHPP)', 'Upcoming'),

(1, 1, 'ABC Veterinary Clinic, Sukhumvit 63', '2026-01-15 14:00:00', 
 'Follow-up for ear infection', 'Completed'),

-- Mimi's appointment (pet_id = 2)
(1, 2, 'Pet Hospital Bangkok, Rama 4', '2026-02-20 11:00:00', 
 'Dental cleaning and checkup', 'Upcoming'),

-- Max's appointments (pet_id = 3)
(2, 3, 'Thonglor Pet Hospital', '2026-02-12 09:00:00', 
 'Skin allergy follow-up, check treatment progress', 'Upcoming'),

(2, 3, 'Thonglor Pet Hospital', '2026-01-20 09:00:00', 
 'Initial consultation for skin allergy', 'Completed'),

-- Bella's appointment (pet_id = 4)
(2, 4, 'Thonglor Pet Hospital', '2026-03-01 15:00:00', 
 'Spaying surgery', 'Upcoming'),

-- Coco's appointment (pet_id = 5)
(2, 5, 'Thonglor Pet Hospital', '2026-02-18 10:30:00', 
 'Puppy vaccination (2nd dose)', 'Upcoming'),

-- Tiger's appointment (pet_id = 6)
(3, 6, 'Cat Clinic Silom', '2026-02-25 14:00:00', 
 'Annual health screening', 'Upcoming'),

-- Brownie's appointment (pet_id = 7)
(4, 7, 'Happy Pets Clinic', '2026-02-10 16:00:00', 
 'First visit and health check', 'Upcoming'),

-- Snow's appointment (pet_id = 8)
(5, 8, 'Feline Specialist Center', '2026-02-22 11:00:00', 
 'Vaccination booster', 'Upcoming'),

-- Rocky's appointments (pet_id = 9)
(5, 9, 'Senior Pet Care Center', '2026-02-14 10:00:00', 
 'Senior dog health screening (blood test, X-ray)', 'Upcoming'),

(5, 9, 'Senior Pet Care Center', '2026-01-10 10:00:00', 
 'Arthritis consultation', 'Completed');

-- ====================================================================
-- 5. INSERT MEDICINES NOTIFICATIONS
-- ====================================================================

INSERT INTO medicines_notification (user_id, pet_id, medicine_id, title, notification_at, 
                                    sending_status, status, sending_count, istaken)
VALUES 
-- Lucky's Amoxicillin notifications (medicine_id = 1)
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-09 08:00:00', 'not_sent', 'pending', 0, FALSE),
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-09 20:00:00', 'not_sent', 'pending', 0, FALSE),
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-10 08:00:00', 'not_sent', 'pending', 0, FALSE),
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-10 20:00:00', 'not_sent', 'pending', 0, FALSE),

-- Past notifications (already taken)
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-08 08:00:00', 'sent', 'sent', 1, TRUE),
(1, 1, 1, 'เวลาให้ยา Amoxicillin กับ Lucky', '2026-02-08 20:00:00', 'sent', 'sent', 1, TRUE),

-- Lucky's Heartgard Plus (medicine_id = 2)
(1, 1, 2, 'เวลาให้ยา Heartgard Plus กับ Lucky', '2026-02-10 09:00:00', 'not_sent', 'pending', 0, FALSE),

-- Mimi's Revolution (medicine_id = 3)
(1, 2, 3, 'เวลาให้ยา Revolution กับ Mimi', '2026-02-11 10:00:00', 'not_sent', 'pending', 0, FALSE),

-- Max's medicines (medicine_id = 4, 5)
(2, 3, 4, 'เวลาให้ยา Prednisone กับ Max', '2026-02-09 07:00:00', 'not_sent', 'pending', 0, FALSE),
(2, 3, 4, 'เวลาให้ยา Prednisone กับ Max', '2026-02-09 19:00:00', 'not_sent', 'pending', 0, FALSE),
(2, 3, 5, 'เวลาให้ยา Apoquel กับ Max', '2026-02-09 08:00:00', 'not_sent', 'pending', 0, FALSE),

-- Bella's Drontal (medicine_id = 6)
(2, 4, 6, 'เวลาให้ยา Drontal กับ Bella', '2026-02-10 09:00:00', 'not_sent', 'pending', 0, FALSE),

-- Coco's Vitamin (medicine_id = 7)
(2, 5, 7, 'เวลาให้ยา Vitamin Supplement กับ Coco', '2026-02-09 08:30:00', 'not_sent', 'pending', 0, FALSE),

-- Rocky's Glucosamine (medicine_id = 9)
(5, 9, 9, 'เวลาให้ยา Glucosamine กับ Rocky', '2026-02-09 09:00:00', 'not_sent', 'pending', 0, FALSE);

-- ====================================================================
-- 6. INSERT APPOINTMENTS NOTIFICATIONS
-- ====================================================================

INSERT INTO appointments_notification (user_id, pet_id, appointment_id, title, notification_at, 
                                       sending_status, status, sending_count)
VALUES 
-- Lucky's upcoming appointment (appointment_id = 1)
(1, 1, 1, 'แจ้งเตือน: นัดหมายที่ ABC Veterinary Clinic สำหรับ Lucky', '2026-02-14 10:00:00', 
 'not_sent', 'pending', 0),

-- Mimi's appointment (appointment_id = 3)
(1, 2, 3, 'แจ้งเตือน: นัดหมายที่ Pet Hospital Bangkok สำหรับ Mimi', '2026-02-19 11:00:00', 
 'not_sent', 'pending', 0),

-- Max's appointment (appointment_id = 4)
(2, 3, 4, 'แจ้งเตือน: นัดหมายที่ Thonglor Pet Hospital สำหรับ Max', '2026-02-11 09:00:00', 
 'not_sent', 'pending', 0),

-- Bella's appointment (appointment_id = 6)
(2, 4, 6, 'แจ้งเตือน: นัดหมายผ่าตัดทำหมันที่ Thonglor Pet Hospital สำหรับ Bella', '2026-02-28 15:00:00', 
 'not_sent', 'pending', 0),

-- Coco's appointment (appointment_id = 7)
(2, 5, 7, 'แจ้งเตือน: นัดหมายฉีดวัคซีนที่ Thonglor Pet Hospital สำหรับ Coco', '2026-02-17 10:30:00', 
 'not_sent', 'pending', 0),

-- Tiger's appointment (appointment_id = 8)
(3, 6, 8, 'แจ้งเตือน: นัดหมายที่ Cat Clinic Silom สำหรับ Tiger', '2026-02-24 14:00:00', 
 'not_sent', 'pending', 0),

-- Brownie's appointment (appointment_id = 9)
(4, 7, 9, 'แจ้งเตือน: นัดหมายที่ Happy Pets Clinic สำหรับ Brownie', '2026-02-09 16:00:00', 
 'not_sent', 'pending', 0),

-- Snow's appointment (appointment_id = 10)
(5, 8, 10, 'แจ้งเตือน: นัดหมายที่ Feline Specialist Center สำหรับ Snow', '2026-02-21 11:00:00', 
 'not_sent', 'pending', 0),

-- Rocky's appointment (appointment_id = 11)
(5, 9, 11, 'แจ้งเตือน: นัดหมายตรวจสุขภาพที่ Senior Pet Care Center สำหรับ Rocky', '2026-02-13 10:00:00', 
 'not_sent', 'pending', 0);

-- ====================================================================
-- 7. INSERT PETS RECORDS (Health and symptom records)
-- ====================================================================

INSERT INTO pets_records (pet_id, note, images, created_at)
VALUES 
-- Lucky's records (pet_id = 1)
(1, 'มีอาการเบื่อน้ำเบื่ออาหาร ดูเหมือนจะไม่ค่อยมีแรง อุณหภูมิร่างกาย 39.5°C', 
 JSON_ARRAY('https://example.com/records/lucky_sick_1.jpg'), '2026-01-14 18:30:00'),

(1, 'กินอาหารได้ปกติแล้ว มีแรงมากขึ้น หูยังแดงอยู่นิดหน่อย', 
 JSON_ARRAY(), '2026-01-16 09:00:00'),

(1, 'หายดีแล้ว กระฉับกระเฉง กินอาหารได้ดี', 
 JSON_ARRAY('https://example.com/records/lucky_recovered.jpg'), '2026-01-20 10:00:00'),

-- Mimi's records (pet_id = 2)
(2, 'ขนร่วงมากกว่าปกติ พบก้อนขนในอุจจาระ', 
 JSON_ARRAY('https://example.com/records/mimi_hairball.jpg'), '2026-02-01 14:00:00'),

(2, 'ให้ยาระบายก้อนขนแล้ว สังเกตว่าอาเจียนน้อยลง', 
 JSON_ARRAY(), '2026-02-05 11:00:00'),

-- Max's records (pet_id = 3)
(3, 'ผิวหนังแดง คันมาก เกาตัวบ่อย มีผื่นแดงบริเวณท้องและขา', 
 JSON_ARRAY('https://example.com/records/max_allergy_1.jpg', 'https://example.com/records/max_allergy_2.jpg'), 
 '2026-01-19 16:00:00'),

(3, 'ให้ยาแล้ว 5 วัน อาการดีขึ้นเล็กน้อย ยังคันอยู่แต่น้อยลง', 
 JSON_ARRAY('https://example.com/records/max_progress.jpg'), '2026-01-25 10:00:00'),

(3, 'ผื่นลดลงมาก แต่ยังมีรอยแดงบริเวณท้อง', 
 JSON_ARRAY(), '2026-02-05 09:00:00'),

-- Bella's record (pet_id = 4)
(4, 'เริ่มมีอาการเรียกร้องผสมพันธุ์ ร้องดัง กระสับกระส่าย', 
 JSON_ARRAY(), '2026-02-01 20:00:00'),

-- Coco's records (pet_id = 5)
(5, 'ฉีดวัคซีนเข็มแรก ตัวสั่นเล็กน้อยหลังฉีด น้ำหนัก 2.1 kg', 
 JSON_ARRAY('https://example.com/records/coco_vaccine1.jpg'), '2026-01-18 10:30:00'),

(5, 'สุขภาพดี กระฉับกระเฉง เล่นได้ดี น้ำหนักเพิ่มเป็น 2.3 kg', 
 JSON_ARRAY(), '2026-02-01 15:00:00'),

-- Tiger's record (pet_id = 6)
(6, 'ผ่าตัดเอาก้อนไขมันที่หลัง แผลหายดี ถอดไหมแล้ว', 
 JSON_ARRAY('https://example.com/records/tiger_surgery.jpg'), '2026-01-25 11:00:00'),

-- Rocky's records (pet_id = 9)
(9, 'เดินกระเผลก ขาหลังดูแข็ง ลุกยาก โดยเฉพาะตอนเช้า', 
 JSON_ARRAY('https://example.com/records/rocky_arthritis.jpg'), '2026-01-09 08:00:00'),

(9, 'ให้ยาบำรุงข้อต่อแล้ว 1 เดือน เดินดีขึ้นเล็กน้อย', 
 JSON_ARRAY(), '2026-02-08 10:00:00');

-- ====================================================================
-- 8. INSERT JWT TOKENS (Sample active tokens)
-- ====================================================================

INSERT INTO jwt_tokens (user_id, access_token, key_id, token_type, expires_at)
VALUES 
(1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.sample_token_1', 
 'key_somchai_001', 'Bearer', DATE_ADD(NOW(), INTERVAL 30 DAY)),

(2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyfQ.sample_token_2', 
 'key_siriwan_001', 'Bearer', DATE_ADD(NOW(), INTERVAL 30 DAY)),

(3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozfQ.sample_token_3', 
 'key_nattapong_001', 'Bearer', DATE_ADD(NOW(), INTERVAL 30 DAY)),

(5, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1fQ.sample_token_5', 
 'key_wanchai_001', 'Bearer', DATE_ADD(NOW(), INTERVAL 30 DAY));

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- ====================================================================
-- VERIFICATION QUERIES
-- ====================================================================

-- Check inserted data counts
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Pets', COUNT(*) FROM pets
UNION ALL
SELECT 'Medicines', COUNT(*) FROM medicines
UNION ALL
SELECT 'Appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'Medicines Notifications', COUNT(*) FROM medicines_notification
UNION ALL
SELECT 'Appointments Notifications', COUNT(*) FROM appointments_notification
UNION ALL
SELECT 'Pets Records', COUNT(*) FROM pets_records
UNION ALL
SELECT 'JWT Tokens', COUNT(*) FROM jwt_tokens;

-- ====================================================================
-- SUMMARY
-- ====================================================================
-- 
-- DATA INSERTED:
-- - 5 Users (4 registered, 1 new)
-- - 9 Pets (across different owners)
-- - 9 Medicines (active and stopped)
-- - 12 Appointments (upcoming and completed)
-- - 15 Medicine Notifications (pending and sent)
-- - 9 Appointment Notifications (pending)
-- - 13 Pet Health Records
-- - 4 JWT Tokens (active sessions)
--
-- REALISTIC SCENARIOS COVERED:
-- 1. Users with multiple pets
-- 2. Pets with ongoing medical treatment (Max)
-- 3. Daily and weekly medication schedules
-- 4. Past and future appointments
-- 5. Taken and pending notifications
-- 6. Health records with images
-- 7. Different pet species (dogs and cats)
-- 8. Various medication types and frequencies
-- 9. Completed and stopped medications
-- 10. Pets with and without allergies
--
-- ====================================================================
