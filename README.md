## API Endpoints

### General
- `GET /` - Root endpoint with API information

### Appointments API

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
// Changing appointment_date will automatically update notification (2 days before new date)
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

 