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

## **PHASE 4: Spaced Repetition & Progress Tracking (Week 2-3)**
**Goal:** Implement intelligent review scheduling based on successful practice days.

**Database Changes:**
- Add `successful_days` (int, default 0) - how many different days she's successfully practiced this word
- Add `last_practiced` (date) - last day she practiced this word successfully
- Add `next_review` (date) - when to show this word again

**Features:**
- Track successful practices across multiple days (not session attempts)
- Only increment `successful_days` once per day per word (even if practiced multiple times that day)
- Wrong answers don't reset counter, just schedule sooner review
- Mode switches at `successful_days = 2` (Learning Mode → Recall Mode permanently)

**Review Scheduling Logic:**

After **successful practice** (gets correct):
- If first success today: increment `successful_days`, set `last_practiced = today`
- Calculate `next_review`:
  - `successful_days = 0` → `next_review = today + 1` (tomorrow)
  - `successful_days = 1` → `next_review = today + 2` (in 2 days)
  - `successful_days >= 2` → `next_review = today + 3` (in 3+ days, max 4)

After **unsuccessful practice** (gets wrong):
- Don't change `successful_days` or `last_practiced`
- Set `next_review = today + 1` (retry sooner, but child keeps trying in this session until correct)

**Word Selection:**
- Show only words where `next_review <= today`
- Never show same word twice in one session
- Shuffle selection order

**Example Flow:**
- Day 1: "bee" wrong → keep trying in session
- Day 1: "bee" correct → `successful_days = 1`, `next_review = Day 3`
- Day 3: "bee" correct → `successful_days = 2` (Recall Mode now), `next_review = Day 6`
- Day 6: "bee" (Recall Mode) correct → `next_review = Day 9`

**Deliverables:**
- Database updated with new tracking columns
- Words automatically scheduled for review based on successful days
- "Today's words" list shows words where `next_review <= today`
- Mode switches permanently after 2 successful days
- Progress persists across sessions and days
- Child never practices same word twice in one session

---

## **PHASE 5: Admin Mode - Word Management (Week 3)**
**Goal:** Let parent/teacher add and manage words.

**Features:**
- Admin interface at `/admin.html`
- Add word form: word name + category
- Upload reference image for each word
- List all words with edit/delete buttons
- Simple auth guard (password or token-based)
- Prevent child from accessing admin

**Deliverables:**
- Parent can add new words without touching code
- Reference images stored and associated with words
- Word management fully self-serve

---

## **PHASE 6: Parent/Teacher Dashboard (Week 3-4)**
**Goal:** Give parents visibility into child's progress.

**Features:**
- Dashboard showing:
  - Words completed today/this week
  - Accuracy % per word
  - Learning trend (line chart)
  - Hardest words (sorted by wrong attempts)
  - Drawing gallery (thumbnails of attempts)
- Export progress as PDF/CSV
- View child's drawings with timestamps

**Deliverables:**
- Parent can monitor progress
- Identify weak areas
- See child's artwork evolution

---

## **PHASE 7: Data Management & Performance (Week 4)**
**Goal:** Optimize and secure data handling.

**Features:**
- Image compression for saved drawings (PNG to JPEG, reduce size)
- Offline-first capability (service worker caching)
- Data backup/export feature
- Old drawing cleanup (keep last 10 per word)
- Database indexing for queries

**Deliverables:**
- App works offline
- Storage efficient
- Tablet performance smooth even with 100+ drawings

---

## **PHASE 8: Polish & Nice-to-Haves (Week 4-5)**
**Goal:** Make experience delightful.

**Features:**
- Progress badges/milestones (e.g., "5 words learned!")
- Celebration animations on completing word
- Sound library (background music, success chimes)
- Dark mode for evening use
- Multi-child profiles (track different kids)
- Customizable reward system

**Deliverables:**
- App feels rewarding and fun
- Encourages repeated practice

---

## **PHASE 9: Testing & Tablet Compatibility (Week 5)**
**Goal:** Ensure stability across devices.

**Features:**
- Test on iPad, Android tablets
- Different screen sizes/orientations
- Touch sensitivity with stylus vs finger
- Browser compatibility (Chrome, Safari)
- Performance testing (load time, responsiveness)

**Deliverables:**
- Works reliably on target tablets
- No crashes or lag

---

## **PHASE 10: Launch & Expansion (Week 6+)**
**Goal:** Deploy and add more word categories.

**Features:**
- Deploy to simple hosting (Heroku, local network)
- Add more word categories (baby animals, colors, vehicles, etc.)
- Parent feedback loop
- Minor bug fixes

**Deliverables:**
- App live and usable
- Feedback from real users
- Foundation for future expansion