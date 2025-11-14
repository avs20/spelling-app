# Testing Guide

## Quick Start

### Start the Server
```bash
cd backend
source .venv/bin/activate
python -m uvicorn main:app --port 8000 --reload
```

Server will be available at `http://localhost:8000`

---

## Website Testing

### Run All Tests
```bash
node test_website_ui.js
```

### Expected Output
```
✓ All tests passed!
Total Tests: 27
Passed: 27
Failed: 0
```

### What's Tested
- ✅ All HTML pages load correctly
- ✅ Static assets (CSS, JS) served properly
- ✅ Canvas element present for drawing
- ✅ Authentication pages functional
- ✅ Admin interface accessible
- ✅ Dashboard available

### Test Coverage
- Landing page (`/`)
- Admin page (`/admin`)
- Dashboard page (`/dashboard`)
- Login page (`/login`)
- Register page (`/register`)
- Child selector page (`/select-child`)
- User profile page (`/user-profile`)
- Static CSS and JavaScript files

---

## API Testing

### Run Integration Tests
```bash
./test_integration.sh
```

### Manual Testing with cURL

#### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "testuser@example.com",
  "created_date": "2025-11-14 12:00:00"
}
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the token for subsequent requests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 3. Create a Child
```bash
curl -X POST http://localhost:8000/api/children \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emma",
    "age": 5
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Emma",
  "age": 5,
  "created_date": "2025-11-14 12:00:00"
}
```

Save the child ID:
```bash
CHILD_ID="1"
```

#### 4. Add a Word (Admin)
```bash
curl -X POST http://localhost:8000/api/admin/words \
  -H "Authorization: Bearer $TOKEN" \
  -F "word=bee" \
  -F "category=insect"
```

**Response:**
```json
{
  "success": true,
  "word_id": 1,
  "message": "Word 'bee' added successfully"
}
```

#### 5. Get Next Word for Practice
```bash
curl "http://localhost:8000/api/next-word?child_id=$CHILD_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "word": "bee",
  "category": "insect",
  "successful_days": 0,
  "session": null
}
```

#### 6. Submit Practice (with Drawing)
```bash
curl -X POST http://localhost:8000/api/practice \
  -H "Authorization: Bearer $TOKEN" \
  -F "word_id=1" \
  -F "spelled_word=bee" \
  -F "drawing=@/path/to/drawing.png" \
  -F "is_correct=true" \
  -F "child_id=$CHILD_ID"
```

**Response:**
```json
{
  "success": true,
  "message": "Practice saved",
  "drawing_filename": "uuid-123.png"
}
```

#### 7. Get Dashboard Statistics
```bash
curl "http://localhost:8000/api/dashboard/stats?child_id=$CHILD_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "words_today": 2,
  "words_this_week": 5,
  "overall_accuracy": 100.0,
  "total_practices": 11
}
```

---

## API Endpoints Reference

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | None | Register new user |
| POST | `/api/auth/login` | None | Login user |
| GET | `/api/auth/me` | JWT | Get current user |

### Children Management
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/children` | JWT | Create child |
| GET | `/api/children` | JWT | List user's children |
| PUT | `/api/children/{id}` | JWT | Update child |
| DELETE | `/api/children/{id}` | JWT | Delete child |

### Words (Admin)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/admin/words` | JWT | List all words |
| POST | `/api/admin/words` | JWT | Add new word |
| PUT | `/api/admin/words/{id}` | JWT | Update word |
| DELETE | `/api/admin/words/{id}` | JWT | Delete word |

### Practice
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/next-word` | JWT | Get next word |
| POST | `/api/practice` | JWT | Submit practice |

### Dashboard
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/dashboard/stats` | JWT | Overall stats |
| GET | `/api/dashboard/word-accuracy` | JWT | Per-word metrics |
| GET | `/api/dashboard/trend` | JWT | 7-day trend |
| GET | `/api/dashboard/drawings` | JWT | Drawing gallery |

### Health
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | None | Server status |

---

## Authentication Header Format

All protected endpoints require the Authorization header:

```bash
-H "Authorization: Bearer <ACCESS_TOKEN>"
```

Example:
```bash
curl "http://localhost:8000/api/next-word?child_id=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Error Handling

### Missing Authentication
**Status Code:** 403
```json
{
  "detail": "Not authenticated"
}
```

### Invalid Token
**Status Code:** 403
```json
{
  "detail": "Invalid token"
}
```

### Unauthorized Access (Wrong Child)
**Status Code:** 403
```json
{
  "detail": "Unauthorized access to this child"
}
```

### Resource Not Found
**Status Code:** 404
```json
{
  "detail": "Not Found"
}
```

### Validation Error
**Status Code:** 422
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "password"],
      "msg": "Field required"
    }
  ]
}
```

---

## Performance Testing

### Load Test (Optional)
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/health
```

### Response Times (Baseline)
- Health check: < 10ms
- Get next word: < 50ms
- Submit practice: < 200ms
- Dashboard stats: < 300ms

---

## Debugging

### Enable Verbose Logging
```bash
export LOG_LEVEL=DEBUG
python -m uvicorn main:app --log-level debug
```

### Check Database
```bash
sqlite3 data/spelling_app.db ".schema"
sqlite3 data/spelling_app.db "SELECT * FROM users;"
```

### View Server Logs
```bash
# Recent 50 lines
tail -50 /path/to/uvicorn.log
```

---

## Common Issues

### Port Already in Use
```bash
# Kill existing process
lsof -i :8000
kill -9 <PID>

# Or use different port
python -m uvicorn main:app --port 8001
```

### CORS Errors
- Check CORS middleware in `backend/main.py`
- Verify frontend URL is in `allow_origins`

### Database Locked
- Restart the server
- Check for multiple instances running
- Ensure file permissions are correct

---

## Next Steps

1. **Website Testing:** Visit `http://localhost:8000` in your browser
2. **Manual Flow:** Go through register → create child → add word → practice
3. **Dashboard:** View stats at `http://localhost:8000/dashboard`
4. **API Testing:** Use provided cURL examples or REST client (Postman, Insomnia)

---

## Resources

- [API Documentation](API_AND_WEBSITE_TEST_REPORT.md)
- [Project Plan](Plan.md)
- [Phase 12 Progress](Plan.md#phase-12-multi-user--multi-child-support-week-6-7)
- [Testing Reference](TESTING.md)
