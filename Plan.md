**Tech Stack:**
- Python backend (FastAPI)
- HTML5 canvas for drawing
- SQLite for data storage
- Runs in browser on tablet

**Child Profile:** UKG age, loves drawing, can recognize letters, 30-min attention span, starting with 2-3 words per day.

**Word Lists:** Starting with insects (bee, spider, butterfly, mosquito), will expand to baby animals later.

---

## **PHASE 1: MVP - Core Canvas & Basic Spelling (Week 1)** ✓ COMPLETE

**Goal:** Get drawing + spelling working end-to-end with minimal features.

**Features Implemented:**
- ✓ Drawing canvas with pen mode (touch + stylus support)
- ✓ Eraser mode with 20px brush size
- ✓ Visual cursor indicators (pen = circle, eraser = square)
- ✓ Color picker for pen
- ✓ Clear canvas button
- ✓ Letter input system (all letters visible in shuffled order)
- ✓ Learning Mode - child taps letters sequentially
- ✓ Submit button that saves drawing + spelled word
- ✓ SQLite database with Word and Practice tables
- ✓ 3 test words (bee, spider, butterfly)
- ✓ Spelling validation (case-insensitive)
- ✓ FastAPI backend with CORS enabled
- ✓ Drawing storage as PNG files with unique IDs
- ✓ Practice logging with correctness tracking

**Deliverables Complete:**
- ✓ Child can draw on tablet with pen/eraser
- ✓ Child can spell word by tapping letters (in random order)
- ✓ Drawing saved as image file with UUID
- ✓ Practice logged in database with correctness flag
- ✓ Feedback shown on correct/incorrect spelling
- ✓ Auto-loads next word after submission
- ✓ Tested on local machine (ready for tablet testing)

**What's NOT in Phase 1 (planned for later):**
- Undo/Redo
- Spaced repetition scheduling
- Admin panel for word management
- Parent dashboard
- Multi-child profiles
- Offline support

**Testing:** Tested locally with touch/mouse. Ready for tablet testing.

---

## **PHASE 2: Canvas Polish & UX (Week 1-2)** ✓ COMPLETE

**Goal:** Make canvas professional and child-friendly.

**Features Implemented:**
- ✓ Eraser mode (toggle pen/eraser) - from Phase 1
- ✓ Undo/Redo buttons (10-step history)
- ✓ Brush size slider (1-15px pen width)
- ✓ Letter removal - click/tap letter box to delete
- ✓ Touch-friendly buttons with icons
- ✓ Sound effects on correct/incorrect spelling
- ✓ Haptic feedback (vibration) on submit
- ✓ Responsive design for different tablet sizes
- ✓ Polished UI with smooth interactions
- ✓ Disabled state for undo/redo buttons when not available

**Deliverables Complete:**
- ✓ Smooth canvas experience with undo/redo
- ✓ Kids can correct mistakes easily (canvas: 10 steps, spelling: remove any letter)
- ✓ Visual/audio feedback feels rewarding
- ✓ Adjustable pen size for different drawing styles
- ✓ Haptic + audio confirmation on submit
- ✓ Intuitive letter removal with visual feedback (blue boxes)

---

## **PHASE 3: Spelling Validation & Learning/Recall Modes (Week 2)** ✓ COMPLETE

**Goal:** Auto-validate spelling and switch modes based on successful practice days.

**Features Implemented:**
- ✓ Auto-validate spelling (case-insensitive, exact match)
- ✓ Learning Mode (successful_days < 2): All letters visible, child taps in order
- ✓ Recall Mode (successful_days >= 2): Child must type/remember letters without hints
- ✓ Show correct/incorrect feedback with animations
- ✓ Track attempts within a session (child keeps trying until correct)
- ✓ Mode indicator showing current mode
- ✓ Animated feedback messages (green for correct, red for incorrect)

**Key Behavior:**
- Child attempts word in appropriate mode until correct
- Only incorrect attempts within same session (no limit, keeps trying)
- Once correct within session → moves to next word
- **Important:** `successful_days` increments only once per day per word
- If she gets it right on attempt 1 or 2 of a session → still counts as 1 successful day

**Deliverables:**
- ✓ Spelling validation working with visual feedback
- ✓ Mode switching based on successful days (not session attempts)
- ✓ Animated feedback messages
- ✓ Child-friendly UI with mode indicator

---

## **PHASE 4: Spaced Repetition & Progress Tracking (Week 2-3)** ✓ COMPLETE

**Goal:** Implement intelligent review scheduling based on successful practice days.

**Database Changes Implemented:**
- ✓ Added `successful_days` (int, default 0) - days successfully practiced this word
- ✓ Added `last_practiced` (date) - last day of successful practice
- ✓ Added `next_review` (date) - when to show word next
- ✓ Initialize test words with `next_review = today`

**Features Implemented:**
- ✓ Track successful practices across multiple days (not session attempts)
- ✓ Increment `successful_days` only once per day per word (prevents gaming the system)
- ✓ Wrong answers don't reset counter, just schedule sooner review
- ✓ Mode permanently switches at `successful_days = 2` (Learning Mode → Recall Mode)
- ✓ Only show words where `next_review <= today`
- ✓ Never show same word twice in one session

**Review Scheduling Logic Implemented:**

After **successful practice**:
- If first success today: increment `successful_days`, set `last_practiced = today`
- Calculate `next_review` automatically:
  - `successful_days = 0 → 1` → review in 2 days
  - `successful_days = 1 → 2` → review in 3 days (enters Recall Mode)
  - `successful_days >= 2` → review in 3 days (max, keeps word fresh)

After **unsuccessful practice**:
- Don't change `successful_days` or `last_practiced`
- Child keeps trying in session until correct
- Set `next_review = today + 1` for sooner retry

**Example Flow:**
- Day 1: "bee" correct (1st success) → `successful_days = 1`, `next_review = Day 3`
- Day 2: "bee" not shown (next_review = Day 3)
- Day 3: "bee" correct (2nd success) → `successful_days = 2`, enters Recall Mode, `next_review = Day 6`
- Day 6: "bee" in Recall Mode, correct → `next_review = Day 9`

**Backend Endpoints:**
- `GET /api/next-word` - Returns word + `successful_days` for mode determination
- `GET /api/words-for-today` - Lists all words ready for practice (where `next_review <= today`)
- `POST /api/practice` - Calls `update_word_on_success()` if correct

**Frontend Logic:**
- Mode determined entirely by `successful_days` from backend (not local attempts)
- Learning Mode: `successful_days < 2` (letters visible, tap to spell)
- Recall Mode: `successful_days >= 2` (type from memory, permanent)
- Tracks `practicedWordsToday` set to prevent repeats in one session
- Mode indicator shows progress ("0/2 days mastered" → "Mastered - typing practice")

**Deliverables:**
- ✓ Database updated with 3 new tracking columns
- ✓ Words automatically scheduled for review based on successful days
- ✓ API returns `successful_days` to frontend for mode determination
- ✓ Mode switches permanently after 2 successful days
- ✓ Progress persists across sessions and days
- ✓ Child never practices same word twice in one session
- ✓ Spaced repetition prevents forgetting while respecting attention span (2-4 day max gaps)

---

## **PHASE 5: Admin Mode - Word Management (Week 3)** ✓ COMPLETE
**Goal:** Let parent/teacher add and manage words.

**Features Implemented:**
- ✓ Admin interface at `/admin.html`
- ✓ Add word form: word name + category
- ✓ Upload reference image for each word
- ✓ List all words with delete buttons
- ✓ Simple auth guard (password-based: admin123)
- ✓ Prevent child from accessing admin
- ✓ Database updated with reference_image column
- ✓ API endpoints: POST/GET/PUT/DELETE /api/admin/words

**Deliverables Complete:**
- ✓ Parent can add new words without touching code
- ✓ Reference images stored in data/references/
- ✓ Word management fully self-serve
- ✓ All words displayed with metadata (successful_days, next_review)
- ✓ Tests passing for all admin functionality

---

## **PHASE 6: Parent/Teacher Dashboard (Week 3-4)** ✓ COMPLETE
**Goal:** Give parents visibility into child's progress.

**Features Implemented:**
- ✓ Dashboard showing:
  - ✓ Words completed today/this week
  - ✓ Overall accuracy percentage
  - ✓ Total practices count
  - ✓ Learning trend (7-day bar chart)
  - ✓ Hardest words (sorted by accuracy)
  - ✓ Drawing gallery (recent 20 attempts with thumbnails)
- ✓ View child's drawings with timestamps
- ✓ Real-time statistics with refresh button
- ✓ Color-coded performance indicators
- ✓ API endpoints for all dashboard data

**Deliverables Complete:**
- ✓ Parent can monitor progress via /dashboard.html
- ✓ Identify weak areas (words sorted by difficulty)
- ✓ See child's artwork evolution with correct/incorrect badges
- ✓ Visual charts for practice trends
- ✓ All tests passing (8 tests)

---

## **PHASE 7: Data Management & Performance (Week 4)** ✓ COMPLETE
**Goal:** Optimize and secure data handling.

**Features Implemented:**
- ✓ Image compression utilities (PNG to JPEG with PIL)
- ✓ Data backup/export feature (timestamped backups)
- ✓ Old drawing cleanup (keep last N per word, default 10)
- ✓ Database optimization (VACUUM command)
- ✓ Storage statistics tracking
- ✓ API endpoints for data management

**Deliverables Complete:**
- ✓ Storage efficient with cleanup tools
- ✓ Database backup functionality working
- ✓ Performance monitoring via storage stats
- ✓ All tests passing (7 tests)

---

## **PHASE 8: Polish & Nice-to-Haves (Week 4-5)** ✓ COMPLETE
**Goal:** Make experience delightful.

**Features Implemented:**
- ✓ Progress badges/milestones (shows words practiced this week)
- ✓ Celebration animations on completing word (badge bounces)
- ✓ Dark mode for evening use (toggle button with localStorage persistence)
- ✓ Progress badge with click-to-view details
- ✓ Auto-updating badge every 30 seconds
- ✓ Event-driven celebration triggers

**Deliverables Complete:**
- ✓ App feels rewarding and fun
- ✓ Dark mode working with theme persistence
- ✓ Celebration animations on correct answers
- ✓ Progress visibility with weekly word count
- ✓ Child-friendly UI enhancements

---

## **PHASE 9: Testing & Tablet Compatibility (Week 5)** ✓ COMPLETE
**Goal:** Ensure stability across devices.

**Features Implemented:**
- ✓ Visual regression testing with Playwright (17 screenshots)
- ✓ Automated compatibility test suite (browser features, touch, canvas, performance)

## Smart Word Cycling (In Progress)
- ✓ Prevent consecutive duplicate words in a session (WordSession.get_next_word_id)
- ✓ Support selecting N words for today's session (WordSession.__init__)
- ✓ Implement Anki-like queue system
  - ✓ Create queue of selected words
  - ✓ Cycle through words (no duplicates in a row)
  - ✓ Remove from current position on correct, keep in pool (mark_word_mastered)
  - ✓ Session tracks mastered/remaining words
- ✓ Add /api/session/start endpoint to initialize session
- ✓ Modify /api/next-word to use session queue when active
- ✓ Update practice endpoint to track word status in session
- TODO: Frontend UI to start session with word limit (modal/button)
- TODO: Display session progress indicator in UI
- TODO: Handle session completion (show stats)
- ✓ Screenshot capture with timestamp for verification
- ✓ Text report generation with test results
- ✓ Different screen sizes/orientations tested (desktop, mobile, tablet)
- ✓ Browser compatibility tests (Chrome, Safari, Edge, Firefox)
- ✓ Performance testing (load time, render speed, memory usage)
- ✓ Touch and pointer events testing
- ✓ Auto-save test results to localStorage

**Deliverables Complete:**
- ✓ Automated visual testing captures all app screens
- ✓ Compatibility tests verify browser support
- ✓ Performance benchmarks documented
- ✓ Screenshots saved for manual verification
- ✓ TESTING.md guide created with manual testing checklist
- ✓ 25 backend unit tests passing
- ✓ Ready for real device testing

---

## **PHASE 10: Launch & Expansion (Week 6+)** ✓ COMPLETE
**Goal:** Deploy and add more word categories.

**Features Implemented:**
- ✓ Deployed to Fly.io (production hosting)
- ✓ Created deployment configs for multiple platforms (Fly.io, Railway, Vercel)
- ✓ Comprehensive deployment documentation (DEPLOYMENT.md, DEPLOY-FAST.md, PRICING.md)
- ✓ Fixed file paths for production environment
- ✓ Environment detection (local vs Docker/production)
- ✓ HTTPS enabled automatically
- ✓ Persistent storage configured (1GB volume)
- ✓ Global CDN deployment

**Platform Choice - Fly.io:**
- **Why:** Fastest free option (~500ms cold start, no sleep), persistent storage, always-on
- **Cost:** $0/month (stays within free tier: 256MB RAM, 160GB bandwidth, 3GB storage)
- **Performance:** ⭐⭐⭐⭐⭐ (no cold starts unlike Render's 30s+ delays)
- **Alternatives evaluated:** Railway ($5/mo), Vercel (serverless, no SQLite), Render (slow)

**Deliverables Complete:**
- ✓ App live at https://spelling-drawing-app.fly.dev
- ✓ Production-ready with all features working
- ✓ Auto-scaling and auto-start configured
- ✓ Deployment docs for future updates
- ✓ Multi-platform configs ready (Fly.io, Railway, Vercel, Docker)
- ✓ Foundation for future expansion complete

---

## **PHASE 11: Bug Fix - Static File Serving** ✓ COMPLETE
**Goal:** Fix 404 errors on CSS and JavaScript file loading.

**Issue Identified:**
- Backend was mounting static files at `/static/` (line 49 in main.py)
- HTML files were requesting files from root (`/style.css`, `/app.js`, etc.)
- Result: 404 errors in logs for style.css, api.js, app.js, canvas.js, favicon.ico
- App appeared unstyled/broken in production

**Fix Implemented:**
- ✓ Updated backend to mount static files at `/static/` path
- ✓ Updated frontend HTML files to reference static assets correctly:
  - `index.html`: Changed to `/static/style.css`, `/static/api.js`, `/static/canvas.js`, `/static/app.js`
  - Verified admin.html and dashboard.html don't reference external stylesheets
- ✓ Tested all 25 backend unit tests - all passing
- ✓ Deployed to production on Fly.io
- ✓ Verified static assets now load correctly

**Deliverables Complete:**
- ✓ All CSS and JavaScript files loading without 404 errors
- ✓ App displays correctly with proper styling
- ✓ No browser console errors from missing assets
- ✓ All tests passing
- ✓ Production deployment working smoothly

---

## **PHASE 12: Multi-User & Multi-Child Support (Week 6-7)** In Progress
**Goal:** Add user accounts, child profiles, and complete data isolation.

**Current State:**
- Single global database with no user/child distinction
- All progress visible to anyone on internet
- No authentication except hardcoded admin password
- No way to restrict access to dashboards

**Database Changes Needed:**
- Create `users` table (id, email, password_hash, created_date)
- Create `children` table (id, user_id, name, age, created_date)
- Add `child_id` foreign key to `practices` and `words` tables (or make words per-child)
- Add `user_id` to admin records for tracking who created words
- Decide: shared word list per family vs global word list?

**Authentication System:**
- Password hashing (bcrypt or similar)
- JWT tokens for API access
- Session management (token expiry: 24 hours)
- Refresh token strategy
- Password reset flow

**API Changes:**
- `POST /api/auth/register` - Create parent account
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Invalidate session
- `GET /api/auth/me` - Get current user info
- Middleware to verify JWT on protected endpoints
- `POST /api/children` - Create child profile
- `GET /api/children` - List user's children
- `PUT /api/children/{child_id}` - Update child
- `DELETE /api/children/{child_id}` - Delete child
- All practice/word endpoints now require `child_id` parameter

**Frontend Changes:**
- Login page (`login.html`)
- Register page (`register.html`)
- Child selector UI (after login)
- Store JWT token in localStorage
- Include Authorization header in all API calls
- Redirect to login if token invalid
- User profile page with child management

**Access Control:**
- `/admin` only accessible to logged-in user
- `/dashboard` only shows logged-in user's data
- `/` (main app) only accessible after selecting a child
- All API endpoints require valid JWT + correct child_id

**Implementation Order:**
1. Database schema migration
2. Auth endpoints (register, login, logout)
3. JWT middleware
4. Child management endpoints
5. Update all existing endpoints to require auth
6. Frontend: login/register pages
7. Frontend: child selector
8. Frontend: update all API calls
9. Data migration strategy for existing data
10. Testing (auth flows, access control, isolation)

**Migration Strategy for Existing Data:**
- Create default parent account or import option
- Allow parent to import existing practice data to a child
- Option to reset and start fresh with new setup

**Decisions Made:**
- ✓ Hybrid word model: Core words (global) + family custom words (private)
- ✓ No account sharing for now (one parent per account)
- ✓ Keep admin interface, update to manage family/child data
- Skip public profiles for now (data always private)

**Word List Architecture (Hybrid):**
- Core words table: "bee", "spider", "butterfly" (global, shared by all families)
- Family custom words: parents add words visible only to their children
- Add `user_id` to words table (NULL = core/global, set = family-owned)
- Practices always tied to specific child (private)
- When getting words for a child: show core words + their family's custom words

**Implementation Details:**
- Modify `words` table: add `user_id` column (nullable)
- Core words created during init with `user_id = NULL`
- When parent adds word via `/api/admin/words`: set `user_id = current_user_id`
- Get words endpoint filters: `WHERE user_id IS NULL OR user_id = current_user_id`
- Delete word: parent can only delete their own words, not core words
- Admin interface: show core words (read-only) + family's custom words (edit/delete)

**Updated Admin Interface:**
- Show family/child selector at top
- Display core words (locked, can't delete)
- Display family's custom words (can edit/delete)
- Add word form adds to current family only
- Access control: parent can only manage their own family's words

---

## **PHASE 12 - Files to Create & Modify**

**Backend - Database (backend/database.py):**
- Modify: Add `users` table schema
- Modify: Add `children` table schema
- Modify: Add `user_id` column to `words` table (nullable)
- Modify: Add `child_id` column to `practices` table
- Modify: Update all queries to filter by user/child
- Add: `create_user()`, `get_user_by_email()`, `verify_password()`, `hash_password()`
- Add: `create_child()`, `get_user_children()`, `get_child_by_id()`
- Add: `get_words_for_child()` (core words + family's custom words)
- Add: Migration function to add new columns to existing tables

**Backend - Authentication (backend/auth.py) - NEW FILE:**
- JWT configuration (secret key, algorithm, expiry)
- `hash_password()` - bcrypt hash
- `verify_password()` - bcrypt verify
- `create_access_token()` - generate JWT
- `verify_token()` - decode and validate JWT
- `get_current_user()` - FastAPI dependency for protected routes

**Backend - Models (backend/models.py) - NEW FILE:**
- `UserRegisterRequest` - email, password
- `UserLoginRequest` - email, password
- `UserResponse` - user info (no password)
- `ChildCreateRequest` - name, age
- `ChildResponse` - child info with parent
- `WordResponse` - updated with user_id
- `PracticeRequest` - updated with child_id

**Backend - Main (backend/main.py):**
- Modify: Add JWT middleware to verify tokens
- Modify: Update all endpoints to require auth
- Modify: Add `child_id` parameter to practice/word endpoints
- Add: `POST /api/auth/register` - create parent account
- Add: `POST /api/auth/login` - login and get JWT token
- Add: `POST /api/auth/logout` - logout (client-side token removal)
- Add: `GET /api/auth/me` - get current user
- Add: `POST /api/children` - create child
- Add: `GET /api/children` - list user's children
- Add: `PUT /api/children/{child_id}` - update child
- Add: `DELETE /api/children/{child_id}` - delete child
- Modify: `/api/next-word` - add child_id filter
- Modify: `/api/practice` - require auth, filter by child_id
- Modify: `/api/admin/words` - require auth, set user_id
- Modify: All dashboard endpoints - require auth, filter by user
- Remove: Old hardcoded admin password auth

**Backend - Requirements (backend/requirements.txt):**
- Add: `bcrypt>=4.0.0`
- Add: `python-jose[cryptography]>=3.3.0`
- Add: `pydantic-settings>=2.0.0`

**Backend - Migration (backend/migrate.py) - NEW FILE:**
- Run database schema migrations
- Add users/children tables
- Add user_id/child_id columns
- Handle existing data (create default user or prompt)
- Called once on startup

**Frontend - Login Page (frontend/login.html) - NEW FILE:**
- Email + password form
- Register link
- Submit to `/api/auth/login`
- Store JWT in localStorage
- Redirect to child selector on success

**Frontend - Register Page (frontend/register.html) - NEW FILE:**
- Email + password + confirm password form
- Login link
- Submit to `/api/auth/register`
- Validate passwords match
- Redirect to login on success

**Frontend - Child Selector (frontend/select-child.html) - NEW FILE:**
- List user's children
- Select child button
- "Create new child" form
- Store selected child_id in localStorage
- Redirect to main app (/) on selection

**Frontend - User Profile (frontend/user-profile.html) - NEW FILE:**
- Show logged-in user email
- List children with edit/delete buttons
- Create child form
- Logout button
- Access from main app

**Frontend - Main App (frontend/index.html):**
- Modify: Check for JWT token on load, redirect to login if missing
- Modify: Check for selected child_id, redirect to child selector if missing
- Modify: Add user profile link (top right)
- Modify: Add logout button
- Modify: Show current child name in UI

**Frontend - API Utilities (frontend/api.js):**
- Modify: Add `setAuthToken()` to store JWT
- Modify: Add `getAuthToken()` to retrieve JWT
- Modify: Add `clearAuthToken()` to logout
- Modify: Add Authorization header to all API calls: `Authorization: Bearer {token}`
- Modify: Add `child_id` parameter to all practice/word API calls
- Modify: Handle 401 errors - redirect to login
- Add: `login(email, password)` - POST /api/auth/login
- Add: `register(email, password)` - POST /api/auth/register
- Add: `getCurrentUser()` - GET /api/auth/me
- Add: `createChild(name, age)` - POST /api/children
- Add: `getChildren()` - GET /api/children
- Add: `updateChild(child_id, name, age)` - PUT /api/children/{child_id}
- Add: `deleteChild(child_id)` - DELETE /api/children/{child_id}

**Frontend - Admin Page (frontend/admin.html):**
- Modify: Add child/family selector at top
- Modify: Show core words as read-only section
- Modify: Show family custom words with edit/delete buttons
- Modify: Add word form only adds to family
- Modify: Restrict access to logged-in parent
- Modify: Update all API calls to include auth header

**Frontend - Dashboard (frontend/dashboard.html):**
- Modify: Add logout button
- Modify: Show only logged-in user's children data
- Modify: Add child selector (view different child's stats)
- Modify: Filter all stats by selected child_id
- Modify: Restrict access to logged-in parent

**Frontend - App Logic (frontend/app.js):**
- Modify: Add auth check on page load
- Modify: Redirect to login if no token
- Modify: Add child selection on startup
- Modify: Pass child_id to all API calls
- Add: `ensureAuthenticated()` - check token validity
- Add: `ensureChildSelected()` - check child_id selected
- Add: Redirect handlers for auth failures

---

**Summary of Changes:**
- **New files:** 8 (2 backend, 6 frontend)
- **Modified files:** 9 (5 backend, 4 frontend)
- **Core changes:** Database schema, auth system, child selection flow, API protection
- **Breaking changes:** All endpoints now require authentication