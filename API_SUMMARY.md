# VetNurse Backend API Summary

## Authentication

### POST /auth/auth/line/exchange
Exchange LINE authorization code for access token.

**Input:**
```json
{ "code": "ABC123XYZ789" }
```
**Output:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "Bearer",
  "is_new_user": false,
  "user": { "id": 1, "display_name": "สมชาย ใจดี", "picture_url": "https://...", "line_id": "U1234..." }
}
```

### GET /auth/me
Get current user profile from JWT token.

**Input:** Header `Authorization: Bearer <token>`
**Output:**
```json
{ "id": 2, "display_name": "สมชาย ใจดี", "picture_url": "https://...", "role": "owner", "is_registered": true }
```

### POST /auth/notify/appointment
Send LINE push notification for appointment.

**Input:** Query params `line_id`, `topic`, `date`
**Output:** LINE API response

---

## Registration

### POST /v1/register/owner
Register owner profile information.

**Input:**
```json
{
  "first_name": "สมชาย", "last_name": "ใจดี",
  "phone": "0812345678", "email": "somchai@example.com",
  "address_line1": "123 ถนนสุขุมวิท", "address_line2": "",
  "subdistrict": "คลองเตย", "district": "คลองเตย",
  "province": "กรุงเทพมหานคร", "postal_code": "10110"
}
```
**Output:**
```json
{ "message": "Owner registered successfully" }
```

### POST /v1/register/pet
Register a new pet.

**Input:**
```json
{
  "name": "ลัคกี้", "species": "Dog", "breed": "Golden Retriever",
  "gender": "Male", "birth_date": "2022-03-15", "color": "Golden",
  "weight_kg": 25.5, "infecund": false, "in_medical": false,
  "profile_image": "https://..."
}
```
**Output:**
```json
{ "message": "Pet registered successfully", "pet_id": 1 }
```

---

## Pets

### GET /v1/pets
Get all pets owned by current user.

**Input:** Header `Authorization: Bearer <token>`
**Output:**
```json
{
  "success": true,
  "data": [
    {
      "pet_id": 1, "name": "Lucky", "species": "Dog", "breed": "Golden Retriever",
      "color": "Golden", "gender": "Male", "birth_date": "2022-03-15",
      "weight_kg": 25.5, "profile_image": "https://...",
      "in_medical": true, "infecund": false
    }
  ]
}
```

### POST /v1/pets
Register a new pet (same as /v1/register/pet).

### GET /v1/pets/{pet_id}
Get pet detail.

**Input:** Path `pet_id` (integer)
**Output:**
```json
{
  "success": true,
  "data": {
    "pet_id": 1, "name": "Lucky", "species": "Dog", "breed": "Golden Retriever",
    "color": "Golden", "gender": "Male", "birth_date": "2022-03-15",
    "weight_kg": 25.5, "profile_image": "https://...",
    "in_medical": true, "infecund": false
  }
}
```

### PATCH /v1/pets/{pet_id}
Update pet info (partial update).

**Input:**
```json
{ "name": "Lucky Jr.", "weight_kg": 28.5, "in_medical": true }
```
**Output:**
```json
{ "message": "Pet info updated" }
```

### DELETE /v1/pets/{pet_id}
Soft delete a pet.

**Output:**
```json
{ "message": "Pet deleted successfully" }
```

### POST /v1/pets/{pet_id}/symptoms
Record pet symptom.

**Input:**
```json
{ "note": "น้องซึม ไม่ยอมทานอาหาร", "tags": ["ซึม"], "images": ["https://..."] }
```
**Output:**
```json
{ "message": "Symptom recorded successfully", "note_id": 1 }
```

### GET /v1/pets/{pet_id}/medical-history
Get all medical history for a pet.

### POST /v1/pets/{pet_id}/medical-history
Add medical history record.

**Input:**
```json
{ "date": "2026-01-11", "time": "14:00", "note": "รายละเอียดการรักษา" }
```
**Output:**
```json
{ "message": "Medical history recorded", "history_id": 1 }
```

---

## Medications

### GET /v1/medications
Medicine notification feed (filtered by date).

**Input:** Query `pets_id` (optional), `date` (optional, YYYY-MM-DD, default: today)
**Output:**
```json
{
  "success": true,
  "data": [
    {
      "notification_id": 1,
      "title": "Time to give Amoxicillin to Lucky",
      "notification_at": "2026-02-08T08:00:00",
      "istaken": false, "pet_id": 1
    }
  ]
}
```

### GET /v1/medications/{notification_id}
Get notification detail with medicine and pet info.

**Output:**
```json
{
  "success": true,
  "data": {
    "notification_id": 1,
    "title": "Time to give Amoxicillin to Lucky",
    "notification_at": "2026-02-08T08:00:00",
    "istaken": true, "taken_at": "2026-02-08T22:07:04",
    "pet_id": 1, "pet_name": "Lucky", "pet_image": "https://...",
    "medicine_id": 1, "medicine_name": "Amoxicillin",
    "dosage": "2 tablets", "frequency": "-1",
    "reminder_time": ["08:00", "20:00"], "time_per_day": 2
  }
}
```

### PATCH /v1/medications/{notification_id}/taken
Mark medicine as taken.

**Output:**
```json
{ "success": true, "message": "Marked as taken" }
```

### GET /v1/medications/medicines/by-pet/{pet_id}
Get all medicines for a pet (full details).

**Output:**
```json
{
  "success": true,
  "data": [
    {
      "medicine_id": 5, "name": "Amoxicillin", "dosage": "1 tablet",
      "frequency": "-1", "status": "TAKE",
      "start_date": "2026-02-01T00:00:00", "end_date": "2026-02-28T00:00:00",
      "reminder_time": ["08:00", "20:00"],
      "notes": ["กินหลังอาหาร"], "properties": "ยาปฏิชีวนะ",
      "image_urls": ["https://..."],
      "created_at": "2026-02-01T10:00:00", "updated_at": "2026-02-01T10:00:00"
    }
  ]
}
```

### GET /v1/medications/medicines/filter?pets_id={pet_id}
Filter medicines by pet with pet info.

**Input:** Query `pets_id` (required)
**Output:**
```json
{
  "success": true,
  "data": [
    {
      "medicine_id": 1, "medicine_name": "Amoxicillin",
      "medicine_dosage": "1 tablet", "medicine_frequency": "-1",
      "pet_name": "Lucky", "pet_image": "https://...",
      "reminder_time": ["08:00", "20:00"]
    }
  ]
}
```

### POST /v1/medications/medicines
Create new medicine (auto-generates notifications).

**Input:**
```json
{
  "pet_id": 1, "name": "Amoxicillin", "dosage": "1 tablet",
  "frequency": "-1", "reminder_time": ["08:00", "20:00"],
  "start_date": "2026-02-01T00:00:00", "end_date": "2026-02-28T00:00:00"
}
```
Frequency: `-1` = daily, `0-6` = weekdays (0=Mon), `0,2,4` = multiple days

**Output:**
```json
{ "success": true, "message": "Medicine created successfully", "medicine_id": 5 }
```

### PATCH /v1/medications/medicines/{medicine_id}
Update medicine info or status.

**Input:**
```json
{ "status": "STOP", "note": "Completed treatment" }
```
Status: `TAKE` = active, `STOP` = stopped (deletes future notifications)

**Output:**
```json
{ "success": true, "message": "Medicine updated successfully" }
```

### DELETE /v1/medications/medicines/{medicine_id}
Soft delete medicine and notifications.

**Output:**
```json
{ "success": true, "message": "Medicine deleted" }
```

---

## Appointments

### GET /v1/appointments
Get appointments list with pet info.

**Input:** Query `status` (optional: Upcoming, Completed, Canceled)
**Output:**
```json
{
  "success": true,
  "data": [
    {
      "appointment_id": 1, "pet_id": 1,
      "pet_name": "Lucky", "pet_image": "https://...",
      "location": "โรงพยาบาลสัตว์ ABC",
      "appointment_date": "2026-02-15", "appointment_time": "14:00",
      "status": "Upcoming", "note": "ตรวจสุขภาพประจำปี"
    }
  ]
}
```

### GET /v1/appointments/{appointment_id}
Get appointment detail.

**Output:**
```json
{
  "success": true,
  "data": {
    "appointment_id": 1, "pet_id": 1, "user_id": 2,
    "location": "โรงพยาบาลสัตว์ ABC",
    "appointment_date": "2026-02-15T14:00:00",
    "status": "Upcoming", "note": "ตรวจสุขภาพประจำปี",
    "created_at": "2026-02-08T10:00:00", "updated_at": "2026-02-08T10:00:00"
  }
}
```

### POST /v1/appointments
Create appointment (auto-creates notification).

**Input:**
```json
{
  "pet_id": 1, "location": "โรงพยาบาลสัตว์ ABC",
  "appointment_date": "2026-02-15T14:00:00",
  "status": "Upcoming", "note": "ตรวจสุขภาพประจำปี"
}
```
**Output:**
```json
{ "success": true, "message": "Appointment created successfully", "appointment_id": 1 }
```

### PATCH /v1/appointments/{appointment_id}
Update appointment (regenerates notification if date changes).

**Input:**
```json
{ "location": "โรงพยาบาลสัตว์ XYZ", "appointment_date": "2026-02-16T15:00:00" }
```
**Output:**
```json
{ "success": true, "notification_updated": true, "notification_title_updated": false }
```

### PATCH /v1/appointments/{appointment_id}/cancel
Cancel appointment.

**Output:**
```json
{ "success": true, "status": "Canceled" }
```

### DELETE /v1/appointments/{appointment_id}
Delete appointment permanently.

**Output:**
```json
{ "success": true, "message": "Appointment deleted successfully" }
```

---

## Symptom Records

### GET /v1/symptom-records/calendar
Get all pet records for calendar view.

**Output:**
```json
{
  "success": true,
  "data": [
    {
      "record_id": 1, "pet_id": 1,
      "pet_name": "ลัคกี้", "pet_image": "https://...",
      "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
      "note_image": ["https://..."], "time_added": "2026-02-08T14:30:00"
    }
  ]
}
```

### GET /v1/symptom-records/{record_id}
Get record detail.

**Output:**
```json
{
  "success": true,
  "data": {
    "record_id": 1, "pet_id": 1,
    "pet_name": "ลัคกี้", "pet_image": "https://...",
    "date_added": "2026-02-08", "time_added": "14:30",
    "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
    "note_image": ["https://..."]
  }
}
```

### POST /v1/symptom-records
Create new record.

**Input:**
```json
{
  "pet_id": 1,
  "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
  "note_image": ["https://...", "https://..."]
}
```
Note: `note_image` max 4 items

**Output:**
```json
{ "success": true, "message": "Record created successfully", "record_id": 1 }
```

### PATCH /v1/symptom-records/{record_id}
Update record.

**Input:**
```json
{ "note": "อาการดีขึ้น", "note_image": ["https://..."] }
```
**Output:**
```json
{ "success": true, "message": "Record updated successfully" }
```

### DELETE /v1/symptom-records/{record_id}
Delete record permanently.

**Output:**
```json
{ "success": true, "message": "Record deleted successfully" }
```

---

## Dashboard

### GET /v1/dashboard/home
Get dashboard data (uses raw `access_token` header, not Bearer).

**Input:** Header `access_token: <jwt_token>`
**Output:**
```json
{
  "success": true,
  "data": {
    "fname": "สมชาย", "lname": "ใจดี",
    "profile_image": "https://...",
    "pets": [
      { "pet_id": 1, "name": "Lucky", "profile_image": "https://...", "in_medical": true }
    ],
    "medicines_notifications": [
      {
        "_id": "1", "title": "Time to give Amoxicillin to Lucky",
        "medicine_id": "1", "medicine_name": "Amoxicillin",
        "dosage": "2 tablets", "frequency": "-1",
        "reminder_time": ["08:00", "20:00"],
        "pet_id": "1", "pet_name": "Lucky", "pet_image": "https://...",
        "notification_at": "2026-02-08T08:00:00",
        "time": "08:00", "status": "pending", "istaken": false
      }
    ],
    "appointments": [
      {
        "_id": "1", "pet_id": "1",
        "pet_name": "Lucky", "pet_image": "https://...",
        "location": "โรงพยาบาลสัตว์ ABC",
        "appointment_date": "2026-02-15T14:00:00",
        "status": "Upcoming", "notification_status": "pending",
        "note": "ตรวจสุขภาพประจำปี"
      }
    ]
  }
}
```

---

## User Profile

### GET /v1/user/profile
Get user profile.

**Output:**
```json
{
  "success": true,
  "data": {
    "user_id": 2, "fname": "สมชาย", "lname": "ใจดี",
    "line_id": "U1234...", "profile_image": "https://..."
  }
}
```

### PATCH /v1/user/profile
Update user profile (partial update).

**Input:**
```json
{ "display_name": "สมชาย ใจดี", "phone": "0812345678", "email": "somchai@example.com" }
```
**Output:**
```json
{ "success": true, "message": "Profile updated successfully" }
```

---

## Upload

### POST /v1/upload/image
Upload image to Cloudflare R2.

**Input:** `multipart/form-data` - field `file` (JPEG, PNG, WEBP, max 10MB)
**Output:**
```json
{
  "success": true,
  "url": "https://pub-xxx.r2.dev/pets/uuid-123.jpg",
  "filename": "pets/uuid-123.jpg",
  "size": 204800, "content_type": "image/jpeg"
}
```

### DELETE /v1/upload/image
Delete image from R2.

**Input:** Query `filename` (e.g., `pets/uuid-123.jpg`)
**Output:**
```json
{ "success": true, "message": "Image pets/uuid-123.jpg deleted successfully" }
```
