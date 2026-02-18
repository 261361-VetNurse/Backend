import datetime
import random

# Configuration
START_DATE = datetime.date(2025, 12, 1)
END_DATE = datetime.date(2026, 4, 30)
TODAY = datetime.date(2026, 2, 12)  # Assumed "Today" for status logic

# Helpers
def fmt_date(d):
    return d.strftime("%Y-%m-%d")

def fmt_datetime(d, t="00:00:00"):
    return f"{fmt_date(d)} {t}"

def random_date(start, end):
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

SQL_HEADER = """-- ====================================================================
-- Pet Medication Diary - High Volume Seed Data (Dec 2025 - Apr 2026)
-- Generated on: 2026-02-12
-- ====================================================================

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE appointments_notification;
TRUNCATE TABLE medicines_notification;
TRUNCATE TABLE pets_records;
TRUNCATE TABLE appointments;
TRUNCATE TABLE medicines;
TRUNCATE TABLE pets;
TRUNCATE TABLE jwt_tokens;
TRUNCATE TABLE users;

-- ====================================================================
-- 1. USERS
-- ====================================================================
INSERT INTO users (user_id, line_id, display_name, fname, lname, role, is_registered, phone, email, address_line1, subdistrict, district, province, postal_code) VALUES
(1, 'U1a2b3c4d5e6f7g8h9i0', 'Somchai K.', 'สมชาย', 'คำดี', 'owner', TRUE, '0812345678', 'somchai.k@gmail.com', '123/45 Happy Village', 'Hua Mak', 'Bang Kapi', 'Bangkok', '10240'),
(2, 'U2b3c4d5e6f7g8h9i0j1', 'Siriwan P.', 'ศิริวรรณ', 'พรหมมา', 'owner', TRUE, '0823456789', 'siriwan.p@hotmail.com', '456/78 Lumpini Condo', 'Khlong Toei', 'Khlong Toei', 'Bangkok', '10110');

-- ====================================================================
-- 2. PETS
-- ====================================================================
INSERT INTO pets (pet_id, user_id, name, species, breed, gender, birth_date, weight_kg, allergies, infecund, profile_image, is_verified, in_medical) VALUES
(1, 1, 'Lucky', 'Dog', 'Golden Retriever', 'male', '2020-05-15', 28.50, '["chicken"]', FALSE, 'https://images.unsplash.com/photo-1552053831-71594a27632d', TRUE, FALSE),
(2, 1, 'Mimi', 'Cat', 'Persian', 'female', '2021-03-20', 4.20, '[]', TRUE, 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba', TRUE, FALSE),
(3, 2, 'Max', 'Dog', 'Poodle', 'male', '2019-08-10', 6.80, '["dairy"]', TRUE, 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e', TRUE, TRUE),
(4, 2, 'Snow', 'Cat', 'Scottish Fold', 'female', '2022-01-10', 3.50, '[]', FALSE, 'https://images.unsplash.com/photo-1573865526739-10659fec78a5', TRUE, FALSE);

-- ====================================================================
-- 3. MEDICINES
-- ====================================================================
INSERT INTO medicines (medicine_id, user_id, pet_id, name, properties, dosage, frequency, status, reminder_time, start_date, end_date, notes) VALUES
-- Lucky (Pet 1)
(1, 1, 1, 'Amoxicillin', 'Antibiotic', '1 tablet', '-1', 'STOP', '["08:00", "20:00"]', '2025-12-01', '2025-12-20', '["Infection treated"]'),
(2, 1, 1, 'Heartgard Plus', 'Heartworm', '1 chewable', '0', 'TAKE', '["09:00"]', '2025-12-01', '2026-12-31', '["Weekly prevention"]'),
(3, 1, 1, 'Joint Supplement', 'Supplement', '1 tablet', '-1', 'TAKE', '["18:00"]', '2026-01-01', '2026-12-31', '["Daily joint support"]'),

-- Mimi (Pet 2)
(4, 1, 2, 'Multi-Vitamin', 'Supplement', '5ml', '-1', 'TAKE', '["08:00"]', '2025-12-01', '2026-04-30', '["General health"]'),
(5, 1, 2, 'Eye Drops', 'Eye Care', '2 drops', '-1', 'TAKE', '["09:00", "21:00"]', '2026-02-01', '2026-03-01', '["Conjunctivitis"]'),

-- Max (Pet 3) - High Volume Meds
(6, 2, 3, 'Insulin', 'Diabetes', '3 units', '-1', 'TAKE', '["07:00", "19:00"]', '2025-12-01', '2026-06-30', '["Diabetes management"]'),
(7, 2, 3, 'Prednisone', 'Steroid', '5mg', '-1', 'STOP', '["08:00"]', '2025-12-10', '2025-12-25', '["Allergy flare up"]'),

-- Snow (Pet 4)
(8, 2, 4, 'Flea Prevention', 'Spot-on', '1 tube', '0', 'TAKE', '["10:00"]', '2025-12-01', '2026-12-31', '["Weekly check"]');

-- ====================================================================
-- 4. APPOINTMENTS (Generated Randomly)
-- ====================================================================
INSERT INTO appointments (appointment_id, user_id, pet_id, location, appointment_date, note, status) VALUES
"""
print(SQL_HEADER)

appointments = []
appt_id = 1
clinics = ["ABC Clinic", "Thonglor Hospital", "Local Vet", "Pet Wellness Center"]
statuses = ["Completed", "Completed", "Canceled", "Upcoming"] # Weighted towards Completed for past

for pet_id, user_id in [(1,1), (2,1), (3,2), (4,2)]:
    # Generate ~1 appointment per month
    curr = START_DATE
    while curr < END_DATE:
        if random.random() > 0.3: # 70% chance of appt in a month
            appt_date = random_date(curr, curr + datetime.timedelta(days=28))
            time_str = f"{random.randint(9, 17)}:00:00"
            full_dt = fmt_datetime(appt_date, time_str)
            
            if appt_date < TODAY:
                status = random.choice(["Completed", "Completed", "Canceled"])
            else:
                status = "Upcoming"
                
            clinic = random.choice(clinics)
            note = random.choice(["Vaccination", "Checkup", "Follow-up", "Grooming", "Consultation"])
            
            appointments.append(f"({appt_id}, {user_id}, {pet_id}, '{clinic}', '{full_dt}', '{note}', '{status}')")
            appt_id += 1
        curr += datetime.timedelta(days=30)

print(",\n".join(appointments) + ";")


print("""
-- ====================================================================
-- 5. NOTIFICATIONS (Generated via Script - High Volume)
-- ====================================================================
INSERT INTO medicines_notification (user_id, pet_id, medicine_id, title, notification_at, sending_status, status, istaken) VALUES
""")

notifications = []

# Med Definitions: (id, user, pet, name, start, end, times, freq_days)
# freq_days: -1 = daily, [0] = monday
meds = [
    (1, 1, 1, 'Amoxicillin', datetime.date(2025, 12, 1), datetime.date(2025, 12, 20), ["08:00:00", "20:00:00"], -1),
    (2, 1, 1, 'Heartgard Plus', datetime.date(2025, 12, 1), datetime.date(2026, 4, 30), ["09:00:00"], [0]), # Weekly Mon
    (3, 1, 1, 'Joint Supplement', datetime.date(2026, 1, 1), datetime.date(2026, 4, 30), ["18:00:00"], -1),
    (4, 1, 2, 'Multi-Vitamin', datetime.date(2025, 12, 1), datetime.date(2026, 4, 30), ["08:00:00"], -1),
    (5, 1, 2, 'Eye Drops', datetime.date(2026, 2, 1), datetime.date(2026, 3, 1), ["09:00:00", "21:00:00"], -1),
    (6, 2, 3, 'Insulin', datetime.date(2025, 12, 1), datetime.date(2026, 4, 30), ["07:00:00", "19:00:00"], -1),
    (7, 2, 3, 'Prednisone', datetime.date(2025, 12, 10), datetime.date(2025, 12, 25), ["08:00:00"], -1),
    (8, 2, 4, 'Flea Prevention', datetime.date(2025, 12, 1), datetime.date(2026, 4, 30), ["10:00:00"], [0]),
]

for mid, uid, pid, name, start, end, times, freq in meds:
    curr = start
    while curr <= end and curr <= END_DATE:
        # Check frequency
        if freq == -1 or curr.weekday() in freq:
            for t in times:
                notif_dt = fmt_datetime(curr, t)
                
                # Logic
                if curr < TODAY:
                     sending_status = "'sent'"
                     status = "'sent'"
                     # 85% compliance rate
                     istaken = "TRUE" if random.random() < 0.85 else "FALSE"
                     if istaken == "FALSE":
                         # If missed in past, it stays missed (status=sent, istaken=false) -> logic handles "Missed" display
                         pass
                elif curr == TODAY:
                    # Depends on time
                    n_dt = datetime.datetime.combine(curr, datetime.time(int(t[:2]), int(t[3:5])))
                    now_dt = datetime.datetime.combine(TODAY, datetime.time(15, 30)) # assume 15:30
                    
                    if n_dt < now_dt:
                        # Past time today
                        sending_status = "'sent'"
                        status = "'sent'"
                        istaken = "TRUE" if random.random() < 0.9 else "FALSE"
                    else:
                        # Future time today
                        sending_status = "'not_sent'"
                        status = "'pending'"
                        istaken = "FALSE"
                else:
                    # Future date
                    sending_status = "'not_sent'"
                    status = "'pending'"
                    istaken = "FALSE"

                notifications.append(f"({uid}, {pid}, {mid}, 'Time to give {name}', '{notif_dt}', {sending_status}, {status}, {istaken})")
        curr += datetime.timedelta(days=1)

print(",\n".join(notifications) + ";")

print("""
-- ====================================================================
-- 6. APPOINTMENT NOTIFICATIONS (Simplified)
-- ====================================================================
-- Skipped for brevity in this high-volume script, assuming triggered by app logic or can add basic ones
INSERT INTO appointments_notification (user_id, pet_id, appointment_id, title, notification_at, sending_status, status) VALUES
(1, 1, 1, 'Appt Reminder', '2025-12-09 10:00:00', 'sent', 'sent'); -- Placeholder

-- ====================================================================
-- 7. PET RECORDS (Generated Randomly - High Volume)
-- ====================================================================
INSERT INTO pets_records (pet_id, note, created_at, images) VALUES
""")

records = []
notes_db = [
    "Ate well today", "Slept all afternoon", "Played in the park", "Vomited once", 
    "Scratching ear", "Seems happy", "Energy level low", "Stool normal", 
    "Drank lots of water", "Barking at mailman", "Purring loudly", "Coat looks shiny"
]

for get_pid in [1, 2, 3, 4]:
    # ~1.5 records per week
    curr = START_DATE
    while curr < END_DATE:
        if random.random() < 0.2: # 20% daily chance
             note = random.choice(notes_db)
             if random.random() < 0.3:
                 imgs = '["https://placehold.co/400"]'
             else:
                 imgs = '[]'
             
             time_str = f"{random.randint(8,20)}:{random.randint(10,59)}:00"
             records.append(f"({get_pid}, '{note}', '{fmt_datetime(curr, time_str)}', '{imgs}')")
        curr += datetime.timedelta(days=1)

print(",\n".join(records) + ";")

print("""
-- ====================================================================
-- 8. JWT TOKENS
-- ====================================================================
INSERT INTO jwt_tokens (user_id, access_token, key_id, token_type, expires_at) VALUES
(1, 'token_user_1', 'key1', 'Bearer', '2026-12-31 23:59:59'),
(2, 'token_user_2', 'key2', 'Bearer', '2026-12-31 23:59:59');

SET FOREIGN_KEY_CHECKS = 1;
""")
