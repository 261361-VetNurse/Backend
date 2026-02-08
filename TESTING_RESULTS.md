# 🧪 API Testing Results Summary

> **Test Date:** February 8, 2026  
> **Environment:** FastAPI 0.115.6 + MySQL 8.0 (Docker) + Python 3.11.9  
> **Server:** localhost:8000  
> **Test User:** user_id=2, line_id=U_test_2026_001

---

## 📊 Overall Results

| Part | Module | Tests | Result | Bugs Fixed |
|------|--------|-------|--------|------------|
| 1 | Auth & Registration | 4 | ✅ ALL PASS | 3 |
| 2 | Pet Management | 11 | ✅ ALL PASS | 1 |
| 3 | Medicine Management | 18 | ✅ ALL PASS | 3 |
| 4 | Appointments | 19 | ✅ ALL PASS | 3 |
| 5 | Symptom Records | 18 | ✅ ALL PASS | 1 |
| 6 | Dashboard & Notifications | 9 | ✅ ALL PASS | 8 |
| **Total** | | **79** | **✅ ALL PASS** | **19** |

---

## 🔧 Bugs Found & Fixed (19 total)

### Part 1: Auth & Registration (3 bugs)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `app/services/user_service_sql.py` | `register_owner` ใช้ field ผิด `fname` → ต้องเป็น `first_name` | เปลี่ยนเป็น `first_name`, `last_name`, ลบ `country` |
| 2 | `app/services/user_service_sql.py` | `register_new_pet` อ้าง `pet_data.allergies` ซึ่งไม่มีใน schema | ลบ `allergies=pet_data.allergies` ออก |
| 3 | MySQL Database | ตาราง `pets` ไม่มีคอลัมน์ `in_medical` | `ALTER TABLE pets ADD COLUMN in_medical BOOLEAN DEFAULT FALSE` |

### Part 2: Pet Management (1 bug)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 4 | `app/services/user_service_sql.py` | `data.dict()` deprecated ใน Pydantic v2 | → `data.model_dump()` |

### Part 3: Medicine Management (3 bugs)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 5 | `app/services/medicine_service_sql.py` | `date.replace(hour=...)` ใช้ไม่ได้กับ `date` object | เพิ่ม `datetime.combine()` fallback |
| 6 | `app/routers/medications_sql.py` | `response_model=NotificationDetailResponse` ไม่ตรงกับ response จริง | ลบ response_model ออก |
| 7 | `app/routers/medications_sql.py` | `.dict()` deprecated | → `.model_dump()` ใน create/update medicine |

### Part 4: Appointments (3 bugs)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 8 | `app/routers/appointments_sql.py` | Query param `status` ชนกับ `fastapi.status` import | เปลี่ยนเป็น `appt_status` พร้อม `alias="status"` |
| 9 | `app/routers/appointments_sql.py` | `get_appointment_by_id` return ORM object แต่ router ใช้ `.get()` แบบ dict | เขียน handler ใหม่ให้ access attribute โดยตรง |
| 10 | `app/routers/appointments_sql.py` | `.dict()` deprecated | → `.model_dump()` ใน update appointment |

### Part 5: Symptom Records (1 bug)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 11 | `app/routers/pet_records.py` | `.dict(exclude_unset=True)` deprecated | → `.model_dump(exclude_unset=True)` |

### Part 6: Dashboard & Notifications (8 bugs)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 12 | `app/routers/dashboard_home.py` | `jwt_record.expires_in` ไม่มีใน model | → `jwt_record.expires_at` |
| 13 | `app/routers/dashboard_home.py` | `User.id` ไม่มีใน model | → `User.user_id` |
| 14 | `app/routers/dashboard_home.py` | Query pets ไม่กรอง soft-deleted | เพิ่ม `Pet.is_deleted == False` |
| 15 | `app/routers/dashboard_home.py` | `MedicineNotification.pet` ไม่มี relationship | chain ผ่าน `MedicineNotification.medicine` → `Medicine.pet` |
| 16 | `app/routers/dashboard_home.py` | `Appointment.notification` (singular) | → `Appointment.notifications` (plural, ตาม model) |
| 17 | `app/routers/dashboard_home.py` | Appointments ไม่กรอง soft-deleted | เพิ่ม `Appointment.is_deleted == False` |
| 18 | `app/routers/dashboard_home.py` | `notif.id` / `appt.id` (PK ชื่อผิด) | → `notif.notification_id` / `appt.appointment_id` |
| 19 | `app/routers/dashboard_home.py` | Response key typo `"lrofile_image"` + `"pname"` | → `"profile_image"` + `"lname"` |

---

## 📝 Detailed Test Cases

### Part 1: Auth & Registration

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 1.1 | `GET /auth/me` | ดึงข้อมูลผู้ใช้จาก JWT | ✅ |
| 1.2 | `POST /v1/register/owner` | ลงทะเบียนเจ้าของ | ✅ |
| 1.3 | `POST /v1/register/pet` | ลงทะเบียนสัตว์เลี้ยง (Lucky) | ✅ |
| 1.4 | `GET /v1/pets` | ดึงรายการสัตว์เลี้ยง | ✅ |

### Part 2: Pet Management (11 tests)

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 2.1 | `POST /v1/register/pet` | ลงทะเบียนแมว (มิโกะจัง) | ✅ |
| 2.2 | `POST /v1/register/pet` | ลงทะเบียนสัตว์เลี้ยง (PooPoo) สำหรับทดสอบลบ | ✅ |
| 2.3 | `GET /v1/pets` | ดึงสัตว์เลี้ยงทั้งหมด (3 ตัว) | ✅ |
| 2.4 | `GET /v1/pets/1` | ดูรายละเอียด Lucky | ✅ |
| 2.5 | `PATCH /v1/pets/1` | อัพเดท weight, in_medical, breed | ✅ |
| 2.6 | `GET /v1/pets/1` | ตรวจสอบการอัพเดท | ✅ |
| 2.7 | `PATCH /v1/pets/2` | อัพเดทชื่อ+น้ำหนักแมว | ✅ |
| 2.8 | `DELETE /v1/pets/3` | Soft delete PooPoo | ✅ |
| 2.9 | `GET /v1/pets` | ตรวจสอบเหลือ 2 ตัว (กรอง deleted) | ✅ |
| 2.10 | `GET /v1/pets/3` | ตรวจสอบ 404 สำหรับสัตว์เลี้ยงที่ลบ | ✅ |
| 2.11 | `GET /v1/pets/999` | Non-existent pet 404 | ✅ |

### Part 3: Medicine Management (18 tests)

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 3.1 | `POST /v1/medications/medicines` | สร้างยา Amoxicillin (daily, 2 เวลา) | ✅ |
| 3.2 | `POST /v1/medications/medicines` | สร้างยา Prednisolone (MWF) | ✅ |
| 3.3 | `GET /v1/medications/medicines/by-pet/1` | ดูยาของ Lucky | ✅ |
| 3.4 | `GET /v1/medications/medicines/by-pet/2` | ดูยาของ Miko | ✅ |
| 3.5 | `GET /v1/medications/medicines/by-pet/1?status=active` | Filter active | ✅ |
| 3.6 | `GET /v1/medications?date=2026-02-08` | ดู notifications วันนี้ | ✅ |
| 3.7 | `GET /v1/medications/{id}` | ดูรายละเอียด notification | ✅ |
| 3.8 | `PATCH /v1/medications/{id}/taken` | กดรับยาแล้ว | ✅ |
| 3.9 | `GET /v1/medications/{id}` | ตรวจสอบ istaken=true | ✅ |
| 3.10 | `PATCH /v1/medications/medicines/{id}` | อัพเดท dosage | ✅ |
| 3.11 | `GET /v1/medications/medicines/by-pet/1` | ตรวจสอบ dosage | ✅ |
| 3.12 | `PATCH /v1/medications/medicines/{id}/stop` | หยุดยา | ✅ |
| 3.13 | `GET /v1/medications/medicines/by-pet/2?status=STOP` | Filter stopped | ✅ |
| 3.14 | `POST /v1/medications/medicines` | สร้าง Vitamin B (สำหรับลบ) | ✅ |
| 3.15 | `DELETE /v1/medications/medicines/{id}` | Soft delete ยา | ✅ |
| 3.16 | `GET /v1/medications/medicines/by-pet/1` | ตรวจสอบกรอง deleted | ✅ |
| 3.17 | `GET /v1/medications/99999` | Non-existent 404 | ✅ |
| 3.18 | `POST /v1/medications/medicines` (bad pet) | Pet ไม่ใช่ของเรา 404 | ✅ |

### Part 4: Appointments (19 tests)

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 4.1 | `POST /v1/appointments` | สร้างนัด Lucky (ABC Clinic) | ✅ |
| 4.2 | `POST /v1/appointments` | สร้างนัด Miko (XYZ Clinic) | ✅ |
| 4.3 | `POST /v1/appointments` | สร้างนัดสำหรับทดสอบลบ | ✅ |
| 4.4 | `GET /v1/appointments` | ดูนัดทั้งหมด (3 รายการ) | ✅ |
| 4.5 | `GET /v1/appointments?status=Upcoming` | Filter upcoming | ✅ |
| 4.6 | `GET /v1/appointments/1` | ดูรายละเอียดนัด | ✅ |
| 4.7 | `PATCH /v1/appointments/1` | อัพเดท location + note | ✅ |
| 4.8 | `GET /v1/appointments/1` | ตรวจสอบการอัพเดท | ✅ |
| 4.9 | `PATCH /v1/appointments/2` | อัพเดทวันนัด | ✅ |
| 4.10 | `PATCH /v1/appointments/3/cancel` | ยกเลิกนัด | ✅ |
| 4.11 | `GET /v1/appointments?status=Canceled` | Filter canceled | ✅ |
| 4.12 | `GET /v1/appointments` | ดูทั้งหมด (3 รวม canceled) | ✅ |
| 4.13 | `PATCH /v1/appointments/1` | Mark completed | ✅ |
| 4.14 | `GET /v1/appointments?status=Completed` | Filter completed | ✅ |
| 4.15 | `DELETE /v1/appointments/3` | Soft delete นัดที่ยกเลิก | ✅ |
| 4.16 | `GET /v1/appointments` | ตรวจสอบเหลือ 2 รายการ | ✅ |
| 4.17 | `GET /v1/appointments/3` | ตรวจสอบ 404 | ✅ |
| 4.18 | `GET /v1/appointments/99999` | Non-existent 404 | ✅ |
| 4.19 | `POST /v1/appointments` (bad pet) | Pet ไม่มี 400 | ✅ |

### Part 5: Symptom Records (18 tests)

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 5.1 | `POST /v1/symptom-records` | สร้างบันทึก Lucky (เบื่ออาหาร + 2 รูป) | ✅ |
| 5.2 | `POST /v1/symptom-records` | สร้างบันทึก Lucky (คัน, ไม่มีรูป) | ✅ |
| 5.3 | `POST /v1/symptom-records` | สร้างบันทึก Miko (จาม + 1 รูป) | ✅ |
| 5.4 | `POST /v1/symptom-records` | สร้างบันทึกสำหรับทดสอบลบ | ✅ |
| 5.5 | `GET /v1/symptom-records/calendar` | ดูบันทึกทั้งหมด (4 รายการ) | ✅ |
| 5.6 | `GET /v1/symptom-records/{id}` | ดูรายละเอียดบันทึก Lucky | ✅ |
| 5.7 | `GET /v1/symptom-records/{id}` | ดูรายละเอียดบันทึก Miko | ✅ |
| 5.8 | `PATCH /v1/symptom-records/{id}` | อัพเดท note เท่านั้น | ✅ |
| 5.9 | `GET /v1/symptom-records/{id}` | ตรวจสอบ note เปลี่ยน | ✅ |
| 5.10 | `PATCH /v1/symptom-records/{id}` | อัพเดท note + images | ✅ |
| 5.11 | `GET /v1/symptom-records/{id}` | ตรวจสอบ images เพิ่ม | ✅ |
| 5.12 | `DELETE /v1/symptom-records/{id}` | Hard delete บันทึก | ✅ |
| 5.13 | `GET /v1/symptom-records/{id}` | ตรวจสอบ 404 หลังลบ | ✅ |
| 5.14 | `GET /v1/symptom-records/calendar` | ตรวจสอบเหลือ 3 รายการ | ✅ |
| 5.15 | `GET /v1/symptom-records/99999` | Non-existent 404 | ✅ |
| 5.16 | `POST /v1/symptom-records` (bad pet) | Pet ไม่มี 404 | ✅ |
| 5.17 | `POST /v1/symptom-records` | สร้างบันทึกด้วย max 4 รูป | ✅ |
| 5.17b | `GET /v1/symptom-records/{id}` | ตรวจสอบ 4 รูป | ✅ |

### Part 6: Dashboard & Notifications (9 tests)

| Test | Endpoint | Description | Status |
|------|----------|-------------|--------|
| 6.1 | `GET /v1/dashboard/home` | ดึง dashboard data (pets, notifications, appointments) | ✅ |
| 6.2 | `GET /v1/medications?date=today` | ดู notifications วันนี้ (3 รายการ) | ✅ |
| 6.3 | `GET /v1/medications?pets_id=1&date=today` | Filter notifications by pet | ✅ |
| 6.4 | `GET /v1/medications?pets_id=2&date=today` | Filter Miko (ไม่มี notifications) | ✅ |
| 6.5 | `GET /v1/medications/{id}` | ดูรายละเอียด notification | ✅ |
| 6.6 | `PATCH /v1/medications/{id}/taken` | Mark as taken | ✅ |
| 6.7 | `GET /v1/medications/{id}` | ตรวจสอบ istaken=true | ✅ |
| 6.8 | `GET /v1/medications/99999` | Non-existent notification 404 | ✅ |
| 6.9 | `PATCH /v1/medications/99999/taken` | Mark non-existent taken 404 | ✅ |

---

## 🔍 Bug Pattern Analysis

### Recurring Issue: Pydantic v2 Migration (5 occurrences)
`.dict()` → `.model_dump()` พบใน 5 ไฟล์:
- `user_service_sql.py` (update_pet_info)
- `medications_sql.py` (create/update medicine)
- `appointments_sql.py` (update appointment)
- `pet_records.py` (update record)

**Root Cause:** Code เขียนด้วย Pydantic v1 syntax แต่ใช้ Pydantic v2

### Dashboard Issues (8 bugs in 1 file)
`dashboard_home.py` มี bug มากที่สุดเพราะ:
- ใช้ field name ผิด (ไม่ตรงกับ ORM model)
- Relationship path ผิด
- ไม่กรอง soft-deleted records
- Typo ใน response keys

### ORM Attribute Access (3 occurrences)
ใช้ `.get()` (dict method) กับ ORM object หรือ attribute name ผิด:
- `User.id` → `User.user_id`
- `appt.id` → `appt.appointment_id`
- `notif.id` → `notif.notification_id`

---

## 📦 Test Data State (After All Tests)

### Users
| user_id | line_id | is_registered |
|---------|---------|---------------|
| 2 | U_test_2026_001 | true |

### Pets
| pet_id | name | species | status |
|--------|------|---------|--------|
| 1 | Lucky | Dog | active (in_medical=true) |
| 2 | มิโกะจัง | Cat | active |
| 3 | PooPoo | Dog | soft-deleted |

### Medicines
| medicine_id | name | pet | status |
|-------------|------|-----|--------|
| 1 | Amoxicillin | Lucky | active (daily, 08:00/20:00) |
| 2 | Prednisolone | มิโกะจัง | STOP |
| 3 | Vitamin B | Lucky | soft-deleted |

### Appointments
| appointment_id | pet | location | status |
|----------------|-----|----------|--------|
| 1 | Lucky | VetNurse | Completed |
| 2 | มิโกะจัง | XYZ Clinic | Upcoming |
| 3 | Lucky | DEF Hospital | soft-deleted |

### Symptom Records
| record_id | pet | note (summary) |
|-----------|-----|-----------------|
| 1 | Lucky | อัพเดท: อาการดีขึ้น |
| 2 | Lucky | แพทย์วินิจฉัยเชื้อรา |
| 3 | มิโกะจัง | จามบ่อย น้ำมูกใส |
| 5 | มิโกะจัง | ทดสอบ max images (4 รูป) |

---

## ✅ Conclusion

ทดสอบ API ทั้งหมด **79 test cases** ครอบคลุม **6 modules** ผ่านทั้งหมด 100%  
พบและแก้ไข **19 bugs** ก่อน/ระหว่างการทดสอบ  
Backend API พร้อมใช้งานกับ Frontend
