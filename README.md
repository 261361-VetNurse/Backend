**Layered Architecture:**
- **Routers** (`app/routers/`): Handle HTTP requests/responses
- **Services** (`app/services/`): Business logic and database operations
- **Schemas** (`app/schemas/`): Pydantic models for validation
- **Config** (`app/config.py`): Application settings
- **Database** (`app/database.py`): MongoDB connection

## Database Schema

### Collections Overview

| Collection | Description | Primary Keys |
|-----------|-------------|--------------|
| `USERS` | User accounts | `_id` (ObjectId) |
| `PETS` | Pet profiles | `_id` (ObjectId), `user_id` (FK) |
| `MEDICINES` | Medicine records | `_id` (ObjectId), `user_id` (FK), `pet_id` (FK) |
| `MEDICINES_NOTIFICATION` | Medicine reminder notifications | `_id` (ObjectId), `medicine_id` (FK), `user_id` (FK), `pet_id` (FK) |
| `APPOINTMENTS` | Vet appointments | `_id` (ObjectId), `user_id` (FK), `pet_id` (FK) |
| `APPOINTMENTS_NOTIFICATION` | Appointment reminders | `_id` (ObjectId), `appointment_id` (FK), `user_id` (FK), `pet_id` (FK) |
| `PETS_RECORDS` | Pet health records | `_id` (ObjectId), `pet_id` (FK) |
| `JWT` | Authentication tokens | `access_token`, `user_id` |

### MEDICINES Collection Schema

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",           // Owner of the pet
  "pet_id": "ObjectId",            // Pet that takes this medicine
  "name": "string",                // Medicine name
  "notes": ["string"],             // Array of notes (max 3)
  "properties": "string",          // Medicine properties
  "image_urls": ["string"],        // Medicine images
  "dosage": "string",              // e.g., "1 tablet", "2 ml"
  "frequency": "string",           // ENUM: "-1" (daily) or "0-6" (Mon-Sun)
  "status": "string",              // ENUM: "TAKE" or "STOP"
  "reminder_time": ["datetime"],   // Array of reminder times
  "start_date": "datetime",        // Start date of medication
  "end_date": "datetime",          // End date of medication
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Frequency Values:**
- `"-1"` = Daily (every day)
- `"0"` = Monday only
- `"1"` = Tuesday only
- `"2"` = Wednesday only
- `"3"` = Thursday only
- `"4"` = Friday only
- `"5"` = Saturday only
- `"6"` = Sunday only
- `"0,2,4"` = Multiple days (Mon, Wed, Fri)

**Status Values:**
- `"TAKE"` = Active medication
- `"STOP"` = Stopped medication

### MEDICINES_NOTIFICATION Collection Schema

```json
{
  "_id": "ObjectId",
  "pet_id": "ObjectId",
  "user_id": "ObjectId",
  "medicine_id": "ObjectId",
  "title": "string",               // Notification message
  "notification_at": "datetime",   // When to send notification
  "sending_status": "string",      // e.g., "not_sent", "sent"
  "status": "string",              // e.g., "pending", "completed"
  "sending_count": "int",          // Number of times sent
  "istaken": "bool",               // Whether medicine was taken
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## API Endpoints

### General
- `GET /` - Root endpoint with API information

### Appointments API
### 📋 Medications API (`/v1/medications`)

All endpoints require authentication via `access_token` header.

#### Group A: Notification Feed & Actions

| Method | Endpoint | Description | Request | Response | Database Access |
|--------|----------|-------------|---------|----------|-----------------|
| **GET** | `/v1/medications` | Get notification feed | Query: `pets_id` (optional), `date` (YYYY-MM-DD, optional) | `{success, data: [NotificationFeedItem]}` | `MEDICINES_NOTIFICATION`, `PETS` |
| **GET** | `/v1/medications/{notification_id}` | Get notification details | Path: `notification_id` | `{success, data: NotificationDetail}` | `MEDICINES_NOTIFICATION` |
| **PATCH** | `/v1/medications/{notification_id}/taken` | Mark as taken/not taken | Path: `notification_id`, Body: `{istaken: bool}` (optional) | `{success, message, data}` | `MEDICINES_NOTIFICATION` |

**NotificationFeedItem Schema:**
```json
{
  "_id": "string",
  "title": "string",
  "notification_at": "datetime",
  "istaken": "bool",
  "pet_id": "string"
}
```

**NotificationDetail Schema:**
```json
{
  "_id": "string",
  "pet_id": "string",
  "user_id": "string",
  "medicine_id": "string",
  "title": "string",
  "notification_at": "datetime",
  "sending_status": "string",
  "status": "string",
  "sending_count": "int",
  "istaken": "bool",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Group B: Medicine Management

| Method | Endpoint | Description | Request | Response | Database Access |
|--------|----------|-------------|---------|----------|-----------------|
| **GET** | `/v1/medications/{notification_id}/{medicine_id}` | Get medicine details | Path: `notification_id`, `medicine_id` | `{success, data: MedicineResponse}` | `MEDICINES_NOTIFICATION`, `MEDICINES`, `PETS` |
| **PATCH** | `/v1/medications/{notification_id}/{medicine_id}/edit` | Update medicine | Path: `notification_id`, `medicine_id`, Body: `MedicineUpdate` | `{success, message, data}` | `MEDICINES`, `MEDICINES_NOTIFICATION`, `PETS` |
| **PATCH** | `/v1/medications/{notification_id}/{medicine_id}/delete` | Delete medicine | Path: `notification_id`, `medicine_id` | `{success, message, data}` | `MEDICINES`, `MEDICINES_NOTIFICATION`, `PETS` |

**MedicineResponse Schema:**
```json
{
  "_id": "string",
  "user_id": "string",
  "pet_id": "string",
  "name": "string",
  "notes": ["string"],
  "properties": "string",
  "image_urls": ["string"],
  "dosage": "string",
  "frequency": "string",      // "-1" or "0-6"
  "status": "string",         // "TAKE" or "STOP"
  "reminder_time": ["datetime"],
  "start_date": "datetime",
  "end_date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**MedicineUpdate Schema:**
```json
{
  "name": "string (optional)",
  "dosage": "string (optional)",
  "frequency": "string (optional)",    // "-1" or "0-6"
  "status": "string (optional)",       // "TAKE" or "STOP"
  "reminder_time": ["datetime"] (optional),
  "start_date": "datetime (optional)",
  "end_date": "datetime (optional)",
  "note": "string (optional)"          // Added to notes array (max 3)
}
```

#### Bonus: Create Medicine

| Method | Endpoint | Description | Request | Response | Database Access |
|--------|----------|-------------|---------|----------|-----------------|
| **POST** | `/v1/medications/medicine` | Create new medicine | Body: `MedicineCreate` | `{success, message, data}` | `MEDICINES`, `MEDICINES_NOTIFICATION`, `PETS` |

**MedicineCreate Schema:**
```json
{
  "pet_id": "string",
  "name": "string",
  "notes": ["string"] (optional),
  "properties": "string (optional)",
  "image_urls": ["string"] (optional),
  "dosage": "string (optional)",
  "frequency": "string",           // "-1" or "0-6"
  "status": "string (optional)",   // "TAKE" or "STOP", default: "TAKE"
  "reminder_time": ["datetime"],
  "start_date": "datetime",
  "end_date": "datetime"
}
```

#### Scenario A: Schedule Change
When updating `frequency`, `start_date`, `end_date`, or `reminder_time`:
1. Deletes future untaken notifications
2. Generates new notifications for next 2 days

#### Scenario B: Medicine Stopped
When updating `status` to `"STOP"`:
1. Adds optional note to `notes` array (max 3 notes kept)
2. Deletes all future notifications

#### Auto-Generation System
- **Initial Creation**: Generates notifications for next 2 days
- **Daily Scheduler**: Runs at midnight (00:00) to generate notifications for next 2 days
- **Only Active**: Only generates for medicines with `status: "TAKE"`

### Dashboard API (`/v1/dashboard`)
- `GET /v1/dashboard/home` - Get dashboard data

---

## 📝 API Usage Examples

### Example 1: Get All Notifications (No Filter)
```bash
GET /v1/medications
Headers: 
  access_token: mock_token_user_1_long_live

Response:
{
  "success": true,
  "data": [
    {
      "_id": "67890abcdef",
      "title": "Time to give Amoxycillin to Lucky",
      "notification_at": "2026-01-16T08:00:00",
      "istaken": false,
      "pet_id": "12345abcdef"
    },
    {
      "_id": "67890abcdeg",
      "title": "Time to give Vitamin Gel to Mochi",
      "notification_at": "2026-01-16T10:00:00",
      "istaken": false,
      "pet_id": "12345abcdeg"
    }
  ]
}
```

### Example 2: Get Notifications by Pet ID
```bash
GET /v1/medications?pets_id=12345abcdef
Headers: 
  access_token: mock_token_user_1_long_live

Response:
{
  "success": true,
  "data": [
    {
      "_id": "67890abcdef",
      "title": "Time to give Amoxycillin to Lucky",
      "notification_at": "2026-01-16T08:00:00",
      "istaken": false,
      "pet_id": "12345abcdef"
    }
  ]
}
```

### Example 3: Get Notifications by Date
```bash
GET /v1/medications?date=2026-01-17
Headers: 
  access_token: mock_token_user_1_long_live

Response:
{
  "success": true,
  "data": [
    {
      "_id": "67890abcdeh",
      "title": "Time to give Amoxycillin to Lucky",
      "notification_at": "2026-01-17T08:00:00",
      "istaken": false,
      "pet_id": "12345abcdef"
    }
  ]
}
```

### Example 4: Get Notifications by Pet ID and Date
```bash
GET /v1/medications?pets_id=12345abcdef&date=2026-01-17
Headers: 
  access_token: mock_token_user_1_long_live

Response:
{
  "success": true,
  "data": [
    {
      "_id": "67890abcdeh",
      "title": "Time to give Amoxycillin to Lucky",
      "notification_at": "2026-01-17T08:00:00",
      "istaken": false,
      "pet_id": "12345abcdef"
    }
  ]
}
```

### Example 5: Create New Medicine
```bash
POST /v1/medications/medicine
Headers: 
  access_token: mock_token_user_1_long_live
  Content-Type: application/json

Body:
{
  "pet_id": "12345abcdef",
  "name": "Antibiotics",
  "dosage": "2 tablets",
  "frequency": "-1",
  "status": "TAKE",
  "reminder_time": ["2026-01-16T09:00:00", "2026-01-16T21:00:00"],
  "start_date": "2026-01-16T00:00:00",
  "end_date": "2026-01-23T00:00:00"
}

Response:
{
  "success": true,
  "message": "Medicine created successfully",
  "data": {
    "medicine_id": "abc123def456",
    "notifications_created": 14
  }
}
```

### Example 6: Update Medicine (Change Schedule)
```bash
PATCH /v1/medications/{notification_id}/{medicine_id}/edit
Headers: 
  access_token: mock_token_user_1_long_live
  Content-Type: application/json

Body:
{
  "frequency": "0,2,4",
  "reminder_time": ["2026-01-16T10:00:00"]
}

Response:
{
  "success": true,
  "message": "Medicine updated successfully",
  "data": {
    "medicine_id": "abc123def456",
    "notifications_deleted": 10,
    "notifications_created": 6,
    "note_added": false
  }
}
```

### Example 7: Stop Medicine
```bash
PATCH /v1/medications/{notification_id}/{medicine_id}/edit
Headers: 
  access_token: mock_token_user_1_long_live
  Content-Type: application/json

Body:
{
  "status": "STOP",
  "note": "Pet recovered, no longer needs medication"
}

Response:
{
  "success": true,
  "message": "Medicine updated successfully",
  "data": {
    "medicine_id": "abc123def456",
    "notifications_deleted": 8,
    "notifications_created": 0,
    "note_added": true
  }
}
```

| Method | Endpoint | Description | 
|--------|----------|-------------|
| **GET** | `/v1/appointments` | Get all appointments for current user |
| **GET** | `/v1/appointments?status={status}` | Filter appointments by status  |
| **GET** | `/v1/appointments/{appointment_id}` | Get appointment details |
| **POST** | `/v1/appointments` | Create new appointment|
| **PATCH** | `/v1/appointments/{appointment_id}/edit` | Update appointment|
| **PATCH** | `/v1/appointments/{appointment_id}/cancel` | Cancel appointment  |
| **DELETE** | `/v1/appointments/{appointment_id}` | Delete appointment  |

#### Status Values
- `Upcoming` - Scheduled appointment
- `Completed` - Finished appointment
- `Canceled` - Cancelled appointment

#### Request Body Schemas

**POST /v1/appointments - Create Appointment**
```typescript
{
  pet_id: string          // Required - Pet ObjectId
  location: string        // Required - Appointment location
  appointment_date: string // Required - ISO 8601 datetime (e.g., "2026-02-15T10:00:00")
  status: string          // Required - "Upcoming" | "Completed" | "Canceled"
  note?: string           // Optional - Additional notes
}
```

**PATCH /v1/appointments/{appointment_id}/edit - Update Appointment**
```typescript
{
  location?: string        // Optional - Update location
  appointment_date?: string // Optional - Update date (ISO 8601)
  status?: string          // Optional - Update status
  note?: string           // Optional - Update notes
}
// Note: At least one field must be provided
// Changing appointment_date will automatically update notification immediately
```

**PATCH /v1/appointments/{appointment_id}/cancel - Cancel Appointment**
```
No body required
// Sets status to "Canceled" automatically
```

**DELETE /v1/appointments/{appointment_id} - Delete Appointment**
```
No body required
// Cascade deletes: Removes appointment and associated notifications
```

#### Request Examples

**Create Appointment:**
```json
POST /v1/appointments
Headers: { "access_token": "your_token" }
Body: {
  "pet_id": "507f1f77bcf86cd799439011",
  "location": "Happy Paws Clinic",
  "appointment_date": "2026-02-15T10:00:00",
  "status": "Upcoming",
  "note": "Monthly checkup"
}
```

**Filter by Status:**
```
GET /v1/appointments?status=Upcoming
Headers: { "access_token": "your_token" }
```

**Update Appointment:**
```json
PATCH /v1/appointments/{appointment_id}/edit
Headers: { "access_token": "your_token" }
Body: {
  "location": "New Vet Clinic",
  "appointment_date": "2026-02-16T14:00:00"
}
```

#### Response Example
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "pet_id": "507f1f77bcf86cd799439012",
    "location": "Happy Paws Clinic",
    "appointment_date": "2026-02-15T10:00:00",
    "status": "Upcoming",
    "note": "Monthly checkup",
    "created_at": "2026-01-16T10:00:00",
    "updated_at": "2026-01-16T10:00:00"
  }
}
```
## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **MongoDB Motor Documentation**: https://motor.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Docker Compose Documentation**: https://docs.docker.com/compose/

---

 