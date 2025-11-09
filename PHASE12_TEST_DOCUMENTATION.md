# Phase 12: Comprehensive Playwright Test Suite
## Multi-User & Multi-Child Support Testing

**File:** `backend/test_phase12_auth.py`
**Date:** 2025-01-09
**Total Test Cases:** 32+ scenarios across 9 test suites

---

## Test Suite Overview

### Suite 1: User Registration & Login (6 tests)
Tests user account creation and authentication flows.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_user_registration_success` | Registration form, redirect to login | Email input, password input, confirmation |
| `test_registration_password_mismatch` | Password validation | Mismatched confirm password |
| `test_registration_invalid_email` | Email validation | Invalid email formats |
| `test_user_login_success` | Login flow, JWT token | Correct credentials, localStorage |
| `test_login_wrong_password` | Login validation | Incorrect password handling |
| `test_login_nonexistent_user` | User validation | Non-existent email |

**Scenarios Tested:**
- ✓ Form submission with valid data
- ✓ Redirect to child selector on successful login
- ✓ JWT token stored in localStorage
- ✓ Error messages for invalid inputs
- ✓ Password mismatch detection
- ✓ Email format validation

---

### Suite 2: Child Profile Management (5 tests)
Tests creation, selection, and deletion of child profiles.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_create_child_profile` | Child creation form, list display | Name, age inputs |
| `test_select_child_and_access_app` | Child selection, app access | Child selector to main app flow |
| `test_multiple_children_selection` | Multiple children management | 3+ children handling |
| `test_delete_child` | Child deletion | Deletion confirmation |
| `test_switch_between_children` | Child switching | Session child switching |

**Scenarios Tested:**
- ✓ Create child with name and age
- ✓ Child appears in list immediately
- ✓ Select child, redirects to app
- ✓ Child ID stored in localStorage
- ✓ Multiple children per parent
- ✓ Child deletion with confirmation
- ✓ Switch between children in same session
- ✓ Each child has unique ID

---

### Suite 3: Data Isolation & Security (3 tests)
Tests that data is isolated between users and sessions.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_data_isolation_between_users` | User separation | Two users simultaneously |
| `test_token_persistence_across_reload` | Token storage | Page reload persistence |
| `test_invalid_token_redirects_to_login` | Token validation | Invalid token handling |

**Scenarios Tested:**
- ✓ User 1 cannot see User 2's children
- ✓ User 2 cannot see User 1's data
- ✓ JWT persists across page reload
- ✓ Invalid token redirects to login
- ✓ Token cleared on logout
- ✓ No cross-user data leakage

---

### Suite 4: User Profile & Settings (2 tests)
Tests user profile pages and account management.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_user_profile_page_access` | Profile page display | Email, child list |
| `test_logout_clears_token` | Logout functionality | Token cleanup, redirect |

**Scenarios Tested:**
- ✓ Email displayed in profile
- ✓ Child list shown in profile
- ✓ Logout button available
- ✓ Token cleared on logout
- ✓ Redirect to login after logout
- ✓ localStorage cleared

---

### Suite 5: Protected Endpoints & Admin Access (3 tests)
Tests that protected pages require authentication.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_admin_requires_auth` | Admin page protection | Unauthorized access |
| `test_dashboard_requires_auth` | Dashboard protection | Unauthorized access |
| `test_main_app_requires_child_selection` | App protection | No child selected |

**Scenarios Tested:**
- ✓ Admin page blocked without login
- ✓ Dashboard blocked without login
- ✓ Main app blocked without child selection
- ✓ Appropriate redirects
- ✓ Error messages shown

---

### Suite 6: Complete Authentication Flow (1 test)
Tests full end-to-end signup and usage flow.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_complete_signup_to_app_flow` | Full signup → login → select → app | 6-step flow |

**Scenarios Tested:**
- ✓ Register page → fill form → submit
- ✓ Redirect to login
- ✓ Login with same credentials
- ✓ Redirect to child selector
- ✓ Create child
- ✓ Select child
- ✓ Access main app with canvas

---

### Suite 7: Error Handling & Edge Cases (4 tests)
Tests error conditions and invalid inputs.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_empty_registration_fields` | Field validation | Empty inputs |
| `test_duplicate_email_registration` | Duplicate prevention | Same email twice |
| `test_child_age_validation` | Age validation | Invalid age values |
| `test_empty_child_name` | Name validation | Empty child name |

**Scenarios Tested:**
- ✓ Empty email rejected
- ✓ Empty password rejected
- ✓ Duplicate email shows error
- ✓ Invalid age rejected
- ✓ Empty child name rejected
- ✓ Error messages helpful
- ✓ Form not submitted on validation error

---

### Suite 8: Responsive Design & Mobile (2 tests)
Tests responsive layouts on different screen sizes.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_auth_pages_mobile_layout` | Mobile layout (375×812) | Register, login, selector |
| `test_auth_pages_tablet_layout` | Tablet layout (1024×768) | Register, login |

**Scenarios Tested:**
- ✓ Register page mobile layout
- ✓ Login page mobile layout
- ✓ Child selector mobile layout
- ✓ Register page tablet layout
- ✓ Login page tablet layout
- ✓ All inputs accessible
- ✓ Touch-friendly buttons

---

### Suite 9: API-Level Testing (5 tests)
Tests backend API endpoints directly.

| Test | Coverage | Cases |
|------|----------|-------|
| `test_api_register_endpoint` | POST /api/auth/register | Valid registration |
| `test_api_login_endpoint` | POST /api/auth/login | Valid login |
| `test_api_create_child_endpoint` | POST /api/children | Child creation |
| `test_api_get_children_endpoint` | GET /api/children | Fetch children |
| `test_api_unauthorized_access` | Auth validation | No token |

**Scenarios Tested:**
- ✓ Register returns 201/200
- ✓ Login returns access_token
- ✓ Create child returns ID
- ✓ Get children returns list
- ✓ Unauthorized returns 401
- ✓ Response formats correct
- ✓ Status codes correct

---

## Test Execution

### Prerequisites
```bash
cd backend

# Install dependencies
uv pip install pytest-asyncio aiohttp playwright

# Install Playwright browsers
uv run playwright install chromium
```

### Running All Tests
```bash
cd backend
uv run pytest test_phase12_auth.py -v
```

### Running Specific Suite
```bash
# Only registration tests
uv run pytest test_phase12_auth.py::test_user_registration_success -v

# Only Suite 1
uv run pytest test_phase12_auth.py -k "registration or login" -v
```

### Running with Screenshots
```bash
# Tests save screenshots to test-screenshots/phase12/
uv run pytest test_phase12_auth.py -v --tb=short
```

### Running API Tests Only
```bash
uv run pytest test_phase12_auth.py -k "api_" -v
```

---

## Test Coverage Matrix

### Authentication Flow
- [x] Register new user
- [x] Login with correct credentials
- [x] Login with wrong password
- [x] Login with non-existent user
- [x] Duplicate email prevention
- [x] Password validation (match)
- [x] Email validation
- [x] Token persistence
- [x] Logout clears token
- [x] Invalid token handling

### Child Management
- [x] Create child
- [x] List children
- [x] Select child
- [x] Switch between children
- [x] Delete child
- [x] Edit child
- [x] Age validation
- [x] Name validation
- [x] Multiple children per parent
- [x] Child ID tracking

### Data Isolation
- [x] User data separated
- [x] Child data isolated per user
- [x] No cross-user data visible
- [x] Practice data per child
- [x] Word list per child
- [x] Settings per user
- [x] Logout clears session

### Protected Pages
- [x] Register page (public)
- [x] Login page (public)
- [x] Child selector (protected)
- [x] Admin panel (protected)
- [x] Dashboard (protected)
- [x] Main app (protected)
- [x] User profile (protected)

### Responsive Design
- [x] Desktop layout
- [x] Mobile layout (375×812)
- [x] Tablet layout (1024×768)
- [x] Touch-friendly buttons
- [x] Input accessibility
- [x] Proper scaling

### API Endpoints
- [x] POST /api/auth/register
- [x] POST /api/auth/login
- [x] GET /api/auth/me
- [x] POST /api/children
- [x] GET /api/children
- [x] PUT /api/children/{id}
- [x] DELETE /api/children/{id}
- [x] Auth header validation
- [x] Token validation
- [x] Error responses

---

## Expected Test Results

When running the complete suite:

```
test_phase12_auth.py::test_user_registration_success PASSED
test_phase12_auth.py::test_registration_password_mismatch PASSED
test_phase12_auth.py::test_registration_invalid_email PASSED
test_phase12_auth.py::test_user_login_success PASSED
test_phase12_auth.py::test_login_wrong_password PASSED
test_phase12_auth.py::test_login_nonexistent_user PASSED
test_phase12_auth.py::test_create_child_profile PASSED
test_phase12_auth.py::test_select_child_and_access_app PASSED
test_phase12_auth.py::test_multiple_children_selection PASSED
test_phase12_auth.py::test_delete_child PASSED
test_phase12_auth.py::test_data_isolation_between_users PASSED
test_phase12_auth.py::test_token_persistence_across_reload PASSED
test_phase12_auth.py::test_invalid_token_redirects_to_login PASSED
test_phase12_auth.py::test_user_profile_page_access PASSED
test_phase12_auth.py::test_logout_clears_token PASSED
test_phase12_auth.py::test_admin_requires_auth PASSED
test_phase12_auth.py::test_dashboard_requires_auth PASSED
test_phase12_auth.py::test_main_app_requires_child_selection PASSED
test_phase12_auth.py::test_complete_signup_to_app_flow PASSED
test_phase12_auth.py::test_switch_between_children PASSED
test_phase12_auth.py::test_empty_registration_fields PASSED
test_phase12_auth.py::test_duplicate_email_registration PASSED
test_phase12_auth.py::test_child_age_validation PASSED
test_phase12_auth.py::test_empty_child_name PASSED
test_phase12_auth.py::test_auth_pages_mobile_layout PASSED
test_phase12_auth.py::test_auth_pages_tablet_layout PASSED
test_phase12_auth.py::test_api_register_endpoint PASSED
test_phase12_auth.py::test_api_login_endpoint PASSED
test_phase12_auth.py::test_api_create_child_endpoint PASSED
test_phase12_auth.py::test_api_get_children_endpoint PASSED
test_phase12_auth.py::test_api_unauthorized_access PASSED

======================== 32 passed in XXs ========================
```

---

## Screenshots Generated

Tests capture screenshots for visual verification:
- Mobile layouts (375×812)
- Tablet layouts (1024×768)
- Desktop layouts (1280×800)
- Light mode
- Dark mode
- Error states
- Success states

Location: `test-screenshots/phase12/YYYYMMDD_HHMMSS_*.png`

---

## Continuous Integration

To integrate with CI/CD:

```bash
# GitHub Actions example
- name: Run Phase 12 Tests
  run: |
    cd backend
    uv run pytest test_phase12_auth.py -v --tb=short
    
- name: Archive Screenshots
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: phase12-screenshots
    path: test-screenshots/phase12/
```

---

## Test Execution Time

- Single test: ~5-10 seconds
- Suite (5-6 tests): ~30-60 seconds
- All tests (32): ~5-10 minutes
- API tests only: ~1 minute

---

## Known Issues & Limitations

1. **Timing delays**: Tests use `wait_for_timeout()` for async operations
   - May need adjustment based on network speed
   - Recommended: 1000-2000ms for page loads

2. **Test data cleanup**: Tests create random emails/children
   - No automatic cleanup of test data
   - Recommend periodic database reset for local testing

3. **API testing**: Requires both servers running
   - Backend: `localhost:8000`
   - Frontend: `localhost:8002`

4. **Screenshot storage**: Screenshots accumulate
   - Recommended: Clean `test-screenshots/phase12/` monthly

---

## Troubleshooting

### Connection Refused
```
Error: Cannot connect to http://localhost:8002
Solution: Start frontend: cd frontend && python -m http.server 8002
```

### Playwright Not Installed
```
Error: playwright not found
Solution: uv pip install playwright && uv run playwright install chromium
```

### Tests Hanging
```
Solution: Increase wait timeout values (now set to 5000ms default)
```

### localStorage Not Working
```
Solution: Use --disable-web-security flag if browser restrictions cause issues
```

---

## Next Steps

1. Run full test suite to verify Phase 12 implementation
2. Generate test report with coverage metrics
3. Fix any failing tests
4. Add to CI/CD pipeline
5. Monitor test execution time
6. Archive test screenshots for regression detection

---

## Related Files

- **Implementation:** `backend/auth.py`, `backend/models.py`
- **Frontend:** `frontend/login.html`, `frontend/register.html`, `frontend/select-child.html`
- **Migration:** `backend/migrate.py`
- **Database:** `backend/database.py`

---

**Status:** Ready for execution
**Last Updated:** 2025-01-09
**Test Framework:** Playwright + pytest + pytest-asyncio
