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

📖 **API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **MongoDB Motor Documentation**: https://motor.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Docker Compose Documentation**: https://docs.docker.com/compose/

---

