# Phase 12 Test Execution Guide
## Complete test scenarios with expected behavior

---

## Quick Start

```bash
# Make script executable
chmod +x RUN_PHASE12_TESTS.sh

# Run all tests (5-10 minutes)
./RUN_PHASE12_TESTS.sh all

# Or run specific test suites
./RUN_PHASE12_TESTS.sh auth      # Auth tests only
./RUN_PHASE12_TESTS.sh child     # Child management only
./RUN_PHASE12_TESTS.sh api       # API tests only
./RUN_PHASE12_TESTS.sh quick     # 4 smoke tests (1-2 min)
```

---

## Test Suite Details

### Suite 1: User Registration & Login (6 tests)

#### Test 1.1: `test_user_registration_success`
**Purpose:** Verify successful user registration

**Steps:**
1. Navigate to `/register.html`
2. Fill email: `parent1_{timestamp}@test.com`
3. Fill password: `SecurePass123!`
4. Fill confirm password: `SecurePass123!`
5. Click "Register" button

**Expected Behavior:**
- Form submits without validation errors
- Redirects to `/login.html`
- Success message appears
- No token in localStorage yet

**Failure Scenarios:**
- Form doesn't submit → Check HTML form element IDs
- No redirect → Check JavaScript redirect logic
- 400/500 error → Check backend registration endpoint

---

#### Test 1.2: `test_registration_password_mismatch`
**Purpose:** Verify password mismatch validation

**Steps:**
1. Navigate to `/register.html`
2. Fill email: `test_{timestamp}@test.com`
3. Fill password: `Password123!`
4. Fill confirm password: `DifferentPass123!`
5. Click "Register" button

**Expected Behavior:**
- Form shows error: "Passwords do not match" or similar
- Form does NOT submit
- Stays on `/register.html`

**Failure Scenarios:**
- No error message → Check HTML error display
- Form submits anyway → Check client-side validation

---

#### Test 1.3: `test_registration_invalid_email`
**Purpose:** Verify email format validation

**Steps:**
1. Navigate to `/register.html`
2. Fill email: `not-an-email`
3. Fill password: `ValidPass123!`
4. Fill confirm password: `ValidPass123!`
5. Click "Register" button

**Expected Behavior:**
- Form shows email validation error
- Form does NOT submit
- Error contains "email"

**Failure Scenarios:**
- Invalid email accepted → Check email validation
- Wrong error message → Check validator message

---

#### Test 1.4: `test_user_login_success`
**Purpose:** Verify successful login

**Steps:**
1. Register user (see Test 1.1)
2. On login page, fill email: `{same email}`
3. Fill password: `SecurePass123!`
4. Click "Login" button

**Expected Behavior:**
- Redirects to `/select-child.html`
- JWT token in localStorage as "token"
- Token is a valid JWT (can be decoded)

**Failure Scenarios:**
- Redirects to wrong page → Check redirect logic
- No token stored → Check localStorage.setItem()
- 401 error → Check backend password hashing

---

#### Test 1.5: `test_login_wrong_password`
**Purpose:** Verify wrong password rejection

**Steps:**
1. Navigate to `/login.html`
2. Fill email: `anyuser@test.com`
3. Fill password: `WrongPassword123!`
4. Click "Login" button

**Expected Behavior:**
- Error message appears (e.g., "Invalid credentials")
- Stays on `/login.html`
- No token stored

**Failure Scenarios:**
- Login succeeds anyway → Check password verification
- No error message → Check error display element

---

#### Test 1.6: `test_login_nonexistent_user`
**Purpose:** Verify non-existent user rejection

**Steps:**
1. Navigate to `/login.html`
2. Fill email: `nonexistent_{timestamp}@test.com`
3. Fill password: `AnyPass123!`
4. Click "Login" button

**Expected Behavior:**
- Error message appears
- Stays on `/login.html`
- No token stored

**Failure Scenarios:**
- Account created automatically → Check backend logic
- Wrong error message → Check user lookup

---

### Suite 2: Child Profile Management (5 tests)

#### Test 2.1: `test_create_child_profile`
**Purpose:** Verify child creation

**Steps:**
1. Register and login (see Tests 1.1, 1.4)
2. On `/select-child.html`, fill child name: `Emma`
3. Fill child age: `5`
4. Click "Create Child" button

**Expected Behavior:**
- Child appears in list as "Emma, age 5"
- No page reload needed
- Child ID generated and stored

**Failure Scenarios:**
- Child not in list → Check child creation API
- Wrong name displayed → Check API response
- 400 error → Check validation

---

#### Test 2.2: `test_select_child_and_access_app`
**Purpose:** Verify child selection and app access

**Steps:**
1. Register, login, create child `Lily` age `4` (see above)
2. In child list, click "Select Lily" button

**Expected Behavior:**
- Redirects to `/index.html` (main app)
- Child ID stored in localStorage as "selected_child_id"
- Canvas element visible

**Failure Scenarios:**
- Wrong redirect → Check navigation logic
- No child ID stored → Check localStorage usage
- Canvas not visible → Check app initialization

---

#### Test 2.3: `test_multiple_children_selection`
**Purpose:** Verify multiple children per parent

**Steps:**
1. Register and login
2. Create 3 children:
   - Child1, age 4
   - Child2, age 5
   - Child3, age 6

**Expected Behavior:**
- All 3 children visible in list
- Each has select button
- Can select any child
- Each child has unique ID

**Failure Scenarios:**
- Only last child shown → Check list rendering
- Same ID for all → Check ID generation
- Can't select some → Check button generation

---

#### Test 2.4: `test_delete_child`
**Purpose:** Verify child deletion

**Steps:**
1. Register, login, create child `ToDelete`
2. Click "Delete" button next to child
3. Confirm if dialog appears

**Expected Behavior:**
- Child removed from list
- No longer visible on reload
- Data permanently deleted

**Failure Scenarios:**
- Child still in list → Check deletion API
- Deletion fails → Check error handling
- Need confirmation → Check for confirmation dialog

---

#### Test 2.5: `test_switch_between_children`
**Purpose:** Verify switching children in same session

**Steps:**
1. Register, login, create 2 children: `Child_A` and `Child_B`
2. Select `Child_A` → go to main app
3. Note `selected_child_id` value
4. Return to `/select-child.html`
5. Select `Child_B`

**Expected Behavior:**
- Each child has different ID in localStorage
- Can switch back and forth
- No logout needed
- Token stays valid

**Failure Scenarios:**
- Same ID for both → Check ID generation
- Token invalid after switch → Check auth flow
- Can't select second child → Check permissions

---

### Suite 3: Data Isolation & Security (3 tests)

#### Test 3.1: `test_data_isolation_between_users`
**Purpose:** Verify users cannot see each other's data

**Steps:**
1. In Page 1:
   - Register as `parent1_{ts}@test.com`
   - Login
   - Create child `User1Child`
2. In Page 2:
   - Register as `parent2_{ts}@test.com`
   - Login
3. In Page 2, verify `User1Child` is NOT visible
4. Create child `User2Child` in Page 2
5. In Page 1, verify `User2Child` is NOT visible

**Expected Behavior:**
- Page 1 user only sees `User1Child`
- Page 2 user only sees `User2Child`
- Complete data separation
- No cross-user leakage

**Failure Scenarios:**
- One user sees other's child → Critical security issue
- Shared API response → Check child filtering
- Shared localStorage → Check per-user token validation

---

#### Test 3.2: `test_token_persistence_across_reload`
**Purpose:** Verify JWT persists across page reloads

**Steps:**
1. Register and login
2. Note token value: `const token1 = localStorage.getItem("token")`
3. Reload page: `page.reload()`
4. Note token value again: `const token2 = localStorage.getItem("token")`
5. Verify `token1 === token2`

**Expected Behavior:**
- Same token value before and after reload
- Token not null/undefined
- Can continue using app after reload

**Failure Scenarios:**
- Token changes → Check localStorage usage
- Token lost → Check persistence logic
- Can't continue → Check auth check on load

---

#### Test 3.3: `test_invalid_token_redirects_to_login`
**Purpose:** Verify invalid tokens are rejected

**Steps:**
1. Set token to invalid value: `localStorage.setItem("token", "invalid.token.here")`
2. Navigate to `/select-child.html`
3. Wait for response

**Expected Behavior:**
- Redirected to `/login.html` or error shown
- Invalid token rejected at API level
- Clean error message

**Failure Scenarios:**
- No redirect → Check auth guard implementation
- Cryptic error → Check error message
- App loads anyway → Check token validation

---

### Suite 4: User Profile & Settings (2 tests)

#### Test 4.1: `test_user_profile_page_access`
**Purpose:** Verify user profile page displays correctly

**Steps:**
1. Register and login
2. Navigate to `/user-profile.html`

**Expected Behavior:**
- Email displayed
- Child list shown
- Edit buttons visible
- Logout button present

**Failure Scenarios:**
- Email not shown → Check API response
- Child list empty → Check child fetch
- No logout → Check button rendering

---

#### Test 4.2: `test_logout_clears_token`
**Purpose:** Verify logout clears authentication

**Steps:**
1. Register, login, navigate to profile
2. Click "Logout" button
3. Check token in localStorage
4. Check current page

**Expected Behavior:**
- Token removed from localStorage
- Redirects to `/login.html`
- Cannot access protected pages
- Fresh token not in memory

**Failure Scenarios:**
- Token still present → Check logout logic
- No redirect → Check navigation
- Can still access app → Check auth guard

---

### Suite 5: Protected Endpoints (3 tests)

#### Test 5.1: `test_admin_requires_auth`
**Purpose:** Verify admin panel requires login

**Steps:**
1. Without logging in, navigate to `/admin.html`

**Expected Behavior:**
- Either redirects to `/login.html`
- Or shows permission denied message
- Cannot access word management

**Failure Scenarios:**
- Admin loads without auth → Security issue
- No redirect → Check admin.html auth guard

---

#### Test 5.2: `test_dashboard_requires_auth`
**Purpose:** Verify dashboard requires login

**Steps:**
1. Without logging in, navigate to `/dashboard.html`

**Expected Behavior:**
- Redirects to `/login.html`
- Cannot view statistics

**Failure Scenarios:**
- Dashboard loads → Security issue

---

#### Test 5.3: `test_main_app_requires_child_selection`
**Purpose:** Verify main app requires child selection

**Steps:**
1. Login but don't select child
2. Try accessing `/index.html` directly

**Expected Behavior:**
- Redirects to `/select-child.html`
- Cannot draw/practice

**Failure Scenarios:**
- App loads without child → Logic issue
- Errors when trying to practice → Missing child checks

---

### Suite 6: Complete Flow (1 test)

#### Test 6.1: `test_complete_signup_to_app_flow`
**Purpose:** Verify complete signup to app flow

**Steps:**
1. Register new account
2. Login with same credentials
3. Create child
4. Select child
5. Access main app

**Expected Behavior:**
- Each step completes successfully
- Proper redirects at each stage
- Can draw on canvas
- Token persists throughout

**Failure Scenarios:**
- Any step fails → See individual test failures

---

### Suite 7: Error Handling (4 tests)

#### Test 7.1: `test_empty_registration_fields`
**Purpose:** Verify empty fields are rejected

**Steps:**
1. Navigate to `/register.html`
2. Click "Register" without filling anything

**Expected Behavior:**
- Form validation prevents submission
- Error messages appear for each empty field

**Failure Scenarios:**
- Form submits → Check client validation

---

#### Test 7.2: `test_duplicate_email_registration`
**Purpose:** Verify duplicate email prevention

**Steps:**
1. Register with email `duplicate_{ts}@test.com`
2. Try registering again with same email

**Expected Behavior:**
- Second registration fails
- Error: "Email already registered" or similar
- First account unchanged

**Failure Scenarios:**
- Two accounts created → Check uniqueness constraint
- Wrong error message → Check error text

---

#### Test 7.3: `test_child_age_validation`
**Purpose:** Verify child age validation

**Steps:**
1. Login
2. Try creating child with age: `invalid`

**Expected Behavior:**
- Form rejects non-numeric age
- Error message shown

**Failure Scenarios:**
- Invalid age accepted → Check validation

---

#### Test 7.4: `test_empty_child_name`
**Purpose:** Verify empty child name rejected

**Steps:**
1. Login
2. Try creating child with empty name
3. Fill age: `5`

**Expected Behavior:**
- Form requires name
- Error shown or submission blocked

**Failure Scenarios:**
- Child created with no name → Check validation

---

### Suite 8: Responsive Design (2 tests)

#### Test 8.1: `test_auth_pages_mobile_layout`
**Purpose:** Verify mobile layout (375×812)

**Steps:**
1. Navigate to `/register.html` in mobile viewport
2. Navigate to `/login.html` in mobile viewport
3. Navigate to `/select-child.html` in mobile viewport

**Expected Behavior:**
- All inputs visible and accessible
- Text readable
- Buttons touch-friendly
- No horizontal scrolling
- Proper spacing on small screen

**Failure Scenarios:**
- Inputs cut off → Check CSS viewport
- Buttons too small → Check touch targets (min 44×44px)
- Text too small → Check font size

---

#### Test 8.2: `test_auth_pages_tablet_layout`
**Purpose:** Verify tablet layout (1024×768)

**Steps:**
1. Navigate to auth pages in tablet viewport

**Expected Behavior:**
- Better use of horizontal space
- All elements visible
- Centered content preferred
- Landscape orientation supported

**Failure Scenarios:**
- Layout breaks → Check responsive CSS
- Wasted space → Optimize for tablet

---

### Suite 9: API Testing (5 tests)

#### Test 9.1: `test_api_register_endpoint`
**Purpose:** Verify POST /api/auth/register

**Request:**
```json
POST /api/auth/register
Content-Type: application/json

{
  "email": "api_test_{ts}@test.com",
  "password": "ApiTest123!"
}
```

**Expected Response:**
```json
HTTP 201 or 200
{
  "id": "uuid",
  "email": "api_test_{ts}@test.com",
  "created_date": "2025-01-09T..."
}
```

**Failure Scenarios:**
- 400 → Invalid input
- 409 → Email already exists
- 500 → Server error

---

#### Test 9.2: `test_api_login_endpoint`
**Purpose:** Verify POST /api/auth/login

**Request:**
```json
POST /api/auth/login
Content-Type: application/json

{
  "email": "api_test_{ts}@test.com",
  "password": "ApiTest123!"
}
```

**Expected Response:**
```json
HTTP 200
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Failure Scenarios:**
- 401 → Invalid credentials
- 404 → User not found

---

#### Test 9.3: `test_api_create_child_endpoint`
**Purpose:** Verify POST /api/children

**Request:**
```
POST /api/children
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "TestChild",
  "age": 5
}
```

**Expected Response:**
```json
HTTP 201
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "TestChild",
  "age": 5,
  "created_date": "2025-01-09T..."
}
```

**Failure Scenarios:**
- 401 → No/invalid token
- 400 → Invalid input
- 500 → Server error

---

#### Test 9.4: `test_api_get_children_endpoint`
**Purpose:** Verify GET /api/children

**Request:**
```
GET /api/children
Authorization: Bearer {token}
```

**Expected Response:**
```json
HTTP 200
[
  {
    "id": "uuid",
    "name": "Child1",
    "age": 5,
    ...
  },
  ...
]
```

**Failure Scenarios:**
- 401 → No/invalid token
- 500 → Server error

---

#### Test 9.5: `test_api_unauthorized_access`
**Purpose:** Verify API rejects unauthorized access

**Request:**
```
GET /api/children
(no Authorization header)
```

**Expected Response:**
```json
HTTP 401
{
  "detail": "Not authenticated" or similar
}
```

**Failure Scenarios:**
- 200 → Security issue, API not protected

---

## Test Execution Report Template

After running tests, create a report:

```
# Phase 12 Test Execution Report
Date: 2025-01-09
Tester: [Name]

## Results Summary
- Total Tests: 32
- Passed: XX
- Failed: XX
- Errors: XX
- Success Rate: XX%

## Test Suite Breakdown
- [x] Suite 1: Auth (6/6 passed)
- [x] Suite 2: Child Management (5/5 passed)
- [ ] Suite 3: Data Isolation (2/3 failed)
  - ✗ test_data_isolation_between_users
    Error: User 2 can see User 1's children
    Root Cause: GET /api/children not filtering by user_id
    Fix: Add WHERE user_id = current_user_id

## Environment
- Backend URL: http://localhost:8000
- Frontend URL: http://localhost:8002
- Browser: Chromium (Playwright)
- OS: macOS / Linux / Windows

## Artifacts
- Screenshots: test-screenshots/phase12/
- Logs: /tmp/backend.log, /tmp/frontend.log

## Recommendations
1. [List any fixes needed]
2. [List any improvements]
```

---

## Continuous Monitoring

### Before Each Push
```bash
./RUN_PHASE12_TESTS.sh quick
```

### Before Merging
```bash
./RUN_PHASE12_TESTS.sh all
```

### CI/CD Integration
Tests automatically run on each commit to main branch.

---

## Getting Help

### Test Fails with "Connection Refused"
```bash
# Start servers manually
cd backend && uv run python main.py &
cd frontend && python -m http.server 8002 &

# Then run tests
uv run pytest test_phase12_auth.py -v
```

### Test Hangs
- Increase timeout: Modify `await page.wait_for_timeout(5000)` to `10000`
- Check server logs: `tail -f /tmp/backend.log`

### Screenshots Not Saving
```bash
mkdir -p test-screenshots/phase12
chmod -R 755 test-screenshots
```

### aiohttp Import Error
```bash
uv pip install aiohttp
```

---

**Last Updated:** 2025-01-09
**Version:** 1.0
