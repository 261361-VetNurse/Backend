# 🧪 Medications API Testing Guide

## 📋 Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Test Data Overview](#test-data-overview)
3. [Postman Collection](#postman-collection)
4. [Test Scenarios](#test-scenarios)
5. [Expected Results](#expected-results)

---

## 🚀 Setup Instructions

### Step 1: Generate Mock Data
```bash
cd D:\SE\Backend\app\schemas
python generate_mock_data_new.py
```

**Important:** Copy the IDs printed at the end! You'll need them for Postman.

### Step 2: Start FastAPI Server
```bash
cd D:\SE\Backend
uvicorn app.main:app --reload
```

### Step 3: Import Postman Collection
1. Open Postman
2. Click **Import** → Select `POSTMAN_MEDICATIONS_TESTS.json`
3. Update Collection Variables with IDs from Step 1:
   - `pet1_id`
   - `pet2_id`
   - `notification_id`
   - `medicine_id`

---

## 📊 Test Data Overview

### Users
| User | Access Token | Pets | Medicines |
|------|--------------|------|-----------|
| TestUser1 | `mock_token_user_1_long_live` | 2 (Lucky, Mochi) | 2 |
| TestUser2 | `mock_token_user_2_long_live` | 1 (Cooper) | 0 |

### Medicines Details

#### Medicine 1: Amoxycillin (for Lucky the Dog)
- **Frequency:** Daily (every day)
- **Times:** 08:00, 20:00
- **Duration:** 7 days from today
- **Expected Notifications:** 14 (7 days × 2 times/day)

#### Medicine 2: Vitamin Gel (for Mochi the Cat)
- **Frequency:** Mon, Wed, Fri (days 0, 2, 4)
- **Times:** 10:00
- **Duration:** 30 days from today
- **Expected Notifications:** ~13 (approximately 13 Mon/Wed/Fri in 30 days)

---

## 🎯 Test Scenarios

### GROUP A: Notification Feed & Actions

#### ✅ Test 1: Get All Medications (Today, All Pets)
**Endpoint:** `GET /v1/medications`  
**Headers:** `access_token: mock_token_user_1_long_live`

**Expected Result:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "...",
      "title": "ได้เวลากินยา Amoxycillin ของน้อง Lucky แล้ว",
      "notification_at": "2026-01-16T08:00:00",
      "istaken": false,
      "pet_id": "..."
    },
    {
      "_id": "...",
      "title": "ได้เวลากินยา Amoxycillin ของน้อง Lucky แล้ว",
      "notification_at": "2026-01-16T20:00:00",
      "istaken": false,
      "pet_id": "..."
    }
    // More notifications if today is Mon/Wed/Fri (Mochi's vitamins)
  ]
}
```

**What to Check:**
- ✓ Status code: 200
- ✓ Returns only TODAY's notifications
- ✓ Includes notifications from both pets (Lucky and Mochi)
- ✓ All `istaken` are `false` initially

---

#### ✅ Test 2: Filter by Pet ID
**Endpoint:** `GET /v1/medications?pets_id={pet1_id}`  
**Query Param:** `pets_id` = Lucky's ID

**Expected Result:**
- Only returns Lucky's (Dog) notifications
- Mochi's (Cat) notifications are excluded

---

#### ✅ Test 3: Filter by Date
**Endpoint:** `GET /v1/medications?date=2026-01-20`  
**Query Param:** `date` = Future date

**Expected Result:**
- Returns notifications scheduled for that specific date
- If it's Monday (check calendar), should include Mochi's vitamin

**Date Validation:**
- Monday (0) - Should have both medicines if within 7 days
- Wednesday (2) - Should have Mochi's vitamin
- Friday (4) - Should have Mochi's vitamin
- Other days - Only Lucky's medicine

---

#### ✅ Test 4: Get Notification Detail
**Endpoint:** `GET /v1/medications/{notification_id}`

**Expected Result:**
```json
{
  "success": true,
  "data": {
    "_id": "...",
    "pet_id": "...",
    "user_id": "...",
    "medicine_id": "...",
    "title": "ได้เวลากินยา Amoxycillin ของน้อง Lucky แล้ว",
    "notification_at": "2026-01-16T08:00:00",
    "sending_status": "pending",
    "status": "active",
    "sending_count": 0,
    "istaken": false,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

**What to Check:**
- ✓ Full notification object returned
- ✓ All fields present
- ✓ Contains `medicine_id` for linking

---

#### ✅ Test 5: Mark as Taken
**Endpoint:** `PATCH /v1/medications/{notification_id}/taken`  
**Body:**
```json
{
  "istaken": true
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine marked as taken",
  "data": {
    "notification_id": "...",
    "istaken": true
  }
}
```

**Verification:**
1. Run Test 1 again → That notification should show `istaken: true`
2. Run Test 4 again → `istaken` field updated to `true`

---

### GROUP B: Medicine Management

#### ✅ Test 6: Get Medicine Detail
**Endpoint:** `GET /v1/medications/{notification_id}/{medicine_id}`

**Expected Result:**
```json
{
  "success": true,
  "data": {
    "_id": "...",
    "user_id": "...",
    "pet_id": "...",
    "name": "Amoxycillin",
    "notes": ["Take after meal"],
    "properties": "Antibiotic",
    "dosage": "1 tablet",
    "frequency": "Daily",
    "status": "Active",
    "reminder_time": ["2000-01-01T08:00:00", "2000-01-01T20:00:00"],
    "start_date": "...",
    "end_date": "...",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

---

#### ✅ Test 7: Edit Medicine (Simple Name Change)
**Endpoint:** `PATCH /v1/medications/{notification_id}/{medicine_id}/edit`  
**Body:**
```json
{
  "name": "Amoxycillin 500mg"
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine updated successfully",
  "data": {
    "medicine_id": "...",
    "notifications_deleted": 0,
    "notifications_created": 0,
    "note_added": false
  }
}
```

**What to Check:**
- ✓ No notifications regenerated (name change doesn't affect schedule)
- ✓ Run Test 6 again → Name should be updated

---

#### ✅ Test 8: Edit Medicine (Scenario A - Schedule Change)
**Endpoint:** `PATCH /v1/medications/{notification_id}/{medicine_id}/edit`  
**Body:**
```json
{
  "frequency": "0,1,2,3,4",
  "reminder_time": ["09:00", "21:00"],
  "end_date": "2026-01-30T00:00:00Z"
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine updated successfully",
  "data": {
    "medicine_id": "...",
    "notifications_deleted": 12,  // Approximate: future untaken notifications
    "notifications_created": 20,  // Approximate: new schedule (10 days × 2 times)
    "note_added": false
  }
}
```

**What Happens:**
1. Deletes all **future** notifications where `istaken: false`
2. Regenerates notifications with new schedule:
   - Weekdays only (Mon-Fri)
   - New times: 09:00, 21:00
   - Extended to Jan 30

**Verification:**
- Run Test 1 → Should see new notification times (09:00, 21:00)
- No Saturday/Sunday notifications

---

#### ✅ Test 9: Edit Medicine (Scenario B - Stop Medicine)
**Endpoint:** `PATCH /v1/medications/{notification_id}/{medicine_id}/edit`  
**Body:**
```json
{
  "status": "stopped",
  "note": "Pet recovered, no longer needs medication"
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine updated successfully",
  "data": {
    "medicine_id": "...",
    "notifications_deleted": 10,  // All future notifications
    "notifications_created": 0,
    "note_added": true
  }
}
```

**What Happens:**
1. Adds note to `notes` array (max 3 notes kept)
2. Changes status to "stopped"
3. Deletes **ALL** future notifications (even taken ones)

**Verification:**
- Run Test 6 → Check `notes` array has new note
- Run Test 1 → No future notifications for this medicine
- Run Test 6 → Status should be "stopped"

---

#### ✅ Test 10: Delete Medicine (Cascade)
**Endpoint:** `PATCH /v1/medications/{notification_id}/{medicine_id}/delete`

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine and related notifications deleted successfully",
  "data": {
    "medicine_id": "...",
    "medicine_deleted": true,
    "notifications_deleted": 14
  }
}
```

**What Happens:**
1. Deletes the medicine document
2. Cascade deletes **ALL** notifications (past and future)

**Verification:**
- Run Test 6 → Should return 404 Not Found
- Run Test 1 → No notifications from that medicine

---

### BONUS: Create Medicine

#### ✅ Test 11: Create Daily Medicine
**Endpoint:** `POST /v1/medications/medicine`  
**Body:**
```json
{
  "pet_id": "{pet1_id}",
  "name": "Heartgard Plus",
  "notes": ["Give with food"],
  "properties": "Heartworm prevention",
  "dosage": "1 chewable tablet",
  "frequency": "daily",
  "reminder_time": ["08:00"],
  "start_date": "2026-01-16T00:00:00Z",
  "end_date": "2026-02-16T00:00:00Z"
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Medicine created successfully",
  "data": {
    "medicine_id": "...",
    "notifications_created": 31  // 31 days × 1 time/day
  }
}
```

---

#### ✅ Test 12: Create Medicine with Specific Days
**Endpoint:** `POST /v1/medications/medicine`  
**Body:**
```json
{
  "pet_id": "{pet2_id}",
  "name": "Omega-3 Supplement",
  "frequency": "1,3,5",
  "reminder_time": ["10:00", "18:00"],
  "start_date": "2026-01-16T00:00:00Z",
  "end_date": "2026-03-16T00:00:00Z"
}
```

**Expected Result:**
- Creates medicine for Mochi (Cat)
- Frequency: Tuesday (1), Thursday (3), Saturday (5)
- 2 times per day
- Duration: 2 months
- Expected notifications: ~26 (13 weeks × 3 days/week × 2 times/day ÷ 7)

---

### ERROR CASES

#### ❌ Test 13: Invalid Access Token
**Endpoint:** `GET /v1/medications`  
**Headers:** `access_token: invalid_token_12345`

**Expected Result:**
```json
{
  "detail": "Invalid access token"
}
```
**Status Code:** 401 Unauthorized

---

#### ❌ Test 14: Access Other User's Pet
**Endpoint:** `GET /v1/medications?pets_id={pet1_id}`  
**Headers:** `access_token: mock_token_user_2_long_live`  
*(User 2 trying to access User 1's pet)*

**Expected Result:**
```json
{
  "detail": "Pet does not belong to current user"
}
```
**Status Code:** 403 Forbidden

---

#### ❌ Test 15: Invalid ObjectId Format
**Endpoint:** `GET /v1/medications/invalid_id_format`

**Expected Result:**
```json
{
  "detail": "Invalid notification ID format"
}
```
**Status Code:** 400 Bad Request

---

#### ❌ Test 16: Create Medicine for Non-Existent Pet
**Endpoint:** `POST /v1/medications/medicine`  
**Body:**
```json
{
  "pet_id": "507f1f77bcf86cd799439011",
  "name": "Test Medicine",
  ...
}
```

**Expected Result:**
```json
{
  "detail": "Pet not found"
}
```
**Status Code:** 404 Not Found

---

## 📝 Testing Checklist

### Basic Functionality
- [ ] Can retrieve all medications for today
- [ ] Can filter by pet ID
- [ ] Can filter by specific date
- [ ] Can get notification detail
- [ ] Can mark notification as taken
- [ ] Can mark notification as not taken
- [ ] Can get medicine detail
- [ ] Can create new medicine

### Business Logic
- [ ] Daily frequency creates notifications for all 7 days
- [ ] Weekly frequency creates notifications for Mondays only
- [ ] Specific days (e.g., "0,2,4") creates correct day pattern
- [ ] Multiple reminder times create multiple notifications per day
- [ ] Notifications only generated within start_date to end_date range

### Scenario A: Schedule Change
- [ ] Changing frequency deletes future untaken notifications
- [ ] New notifications regenerated with updated schedule
- [ ] Taken notifications are NOT deleted
- [ ] Past notifications remain unchanged

### Scenario B: Stop Medicine
- [ ] Status change to "stopped" triggers special logic
- [ ] Note is added to notes array
- [ ] Maximum 3 notes are kept (oldest removed)
- [ ] ALL future notifications deleted (including taken ones)

### Cascade Delete
- [ ] Deleting medicine removes it from database
- [ ] All related notifications deleted (past and future)
- [ ] Other medicines unaffected

### Security & Validation
- [ ] Invalid token returns 401
- [ ] Accessing other user's data returns 403
- [ ] Invalid ObjectId format returns 400
- [ ] Non-existent resources return 404
- [ ] Invalid date format rejected
- [ ] Missing required fields rejected

---

## 🎯 Success Criteria

Your implementation is **COMPLETE** when:

✅ All 16 test scenarios pass  
✅ Error cases return appropriate status codes  
✅ Business logic (Scenario A & B) works correctly  
✅ Notifications auto-generate on medicine creation  
✅ Cascade delete removes all related data  
✅ Access control prevents unauthorized access  
✅ Date/time filtering works accurately  

---

## 💡 Tips for Debugging

1. **Check MongoDB directly:**
   ```javascript
   use pet_medic_db
   db.MEDICINES_NOTIFICATION.find({}).pretty()
   db.MEDICINES.find({}).pretty()
   ```

2. **Enable FastAPI debug logs:**
   Add `print()` statements in service functions to trace execution

3. **Check notification counts:**
   - After creating medicine: Count should match expected
   - After editing schedule: Old deleted + New created
   - After stopping: All future deleted

4. **Verify dates:**
   - Use Python to check weekday: `datetime(2026, 1, 16).weekday()` (0=Mon)
   - Ensure notification_at combines date + time correctly

5. **Test with real dates:**
   - Use actual dates (not dummy data) for accurate testing
   - Check timezone handling (UTC vs local time)

---

## 🚨 Common Issues & Solutions

### Issue: No notifications returned
**Solution:** Check if date matches frequency days

### Issue: Wrong notification count
**Solution:** Verify date range calculation includes both start and end dates

### Issue: Notifications not deleted on edit
**Solution:** Check if future detection (`notification_at >= current_time`) is correct

### Issue: 403 Forbidden on valid request
**Solution:** Verify user_id in JWT matches user_id in database records

---

**Happy Testing! 🎉**
