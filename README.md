## API Endpoints

### General
- `GET /` - Root endpoint with API information

### Appointments API

| Method | Endpoint | Description | Authentication | Ownership Verification |
|--------|----------|-------------|----------------|------------------------|
| **GET** | `/v1/appointments` | Get all appointments for current user | ✅ Required | User → Pets → Appointments |
| **GET** | `/v1/appointments?status={status}` | Filter appointments by status | ✅ Required | User → Pets → Appointments |
| **GET** | `/v1/appointments/{appointment_id}` | Get appointment details | ✅ Required | User → Pet → Appointment |
| **POST** | `/v1/appointments` | Create new appointment | ✅ Required | Verify pet ownership |
| **PATCH** | `/v1/appointments/{appointment_id}/edit` | Update appointment | ✅ Required | User → Pet → Appointment |
| **PATCH** | `/v1/appointments/{appointment_id}/cancel` | Cancel appointment | ✅ Required | User → Pet → Appointment |
| **DELETE** | `/v1/appointments/{appointment_id}` | Delete appointment | ✅ Required | User → Pet → Appointment |

#### Status Values
- `Upcoming` - Scheduled appointment
- `Completed` - Finished appointment
- `Canceled` - Cancelled appointment

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

