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

## **PHASE 2: Canvas Polish & UX (Week 1-2)**
**Goal:** Make canvas professional and child-friendly.

**Features:**
- Eraser mode (toggle pen/eraser)
- Brush size slider
- Undo/Redo buttons (3-5 steps)
- Large, touch-friendly buttons with icons
- Sound effects on correct spelling
- Haptic feedback (vibration) on submit
- Responsive design for different tablet sizes

**Deliverables:**
- Smooth canvas experience
- Kids can correct mistakes easily
- Visual/audio feedback feels rewarding

---

## **PHASE 3: Spelling Validation & Learning/Recall Modes (Week 2)**
**Goal:** Validate spelling and switch modes based on practice count.

**Features:**
- Auto-validate spelling (case-insensitive, exact match)
- Learning Mode (first 2 attempts): All letters visible, child taps in order
- Recall Mode (3+ attempts): Child must type/remember letters
- Show correct/incorrect feedback with animation
- Track attempt count per word per session

**Deliverables:**
- Spelling validation working
- Mode switching based on practice count
- Visual feedback for correct/wrong answers

---

## **PHASE 4: Spaced Repetition & Progress Tracking (Week 2-3)**
**Goal:** Implement intelligent review scheduling.

**Features:**
- Calculate `next_review` date based on correctness (correct → longer gap, wrong → sooner)
- Display "today's words" queue
- Progress tracking: practice_count, correct_count, last_practiced, next_review
- Store multiple drawing filenames per word
- Prevent same word twice in one session

**Deliverables:**
- Words automatically scheduled for review
- Dashboard shows next word to practice
- Progress data persists across sessions

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