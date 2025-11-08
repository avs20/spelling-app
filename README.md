# Spelling & Drawing App

A tablet-friendly web app for children to practice spelling while drawing objects. The app uses spaced repetition to optimize learning.

**Current Phase:** Phase 8 - Polish & Nice-to-Haves (Complete)

---

## Features (Phase 1-8) ✓ COMPLETE

**Phase 1 - MVP:**
- **Drawing Canvas** - Large, touch-optimized canvas for drawing with pen/stylus
- **Pen Mode** - Draw with adjustable pen color
- **Eraser Mode** - Large eraser (20px) for child-friendly corrections
- **Mode Cursor** - Visual cursor changes between pen (circle) and eraser (square)
- **Color Picker** - Choose pen color
- **Clear Button** - Reset entire canvas
- **Letter Input (Shuffled)** - All letters visible in random order, tap to spell
- **Learning Mode** - Child taps letters sequentially to complete the word
- **Drawing Storage** - Save drawings as PNG files with unique IDs
- **Practice Tracking** - Log spelling attempts to database
- **Spelling Validation** - Auto-check if spelling is correct
- **API Backend** - FastAPI with SQLite database
- **CORS Support** - Frontend and backend communication enabled
- **Touch Support** - Full touch and stylus support for tablets

**Phase 2 - Canvas Polish & UX:**
- **Undo/Redo** - Up to 10 steps, easy mistake correction
- **Brush Size Slider** - Adjustable pen width (1-15px) for different drawing styles
- **Letter Removal** - Click any letter box to remove it (tap to fix mistakes)
- **Sound Effects** - Ascending tone for correct, descending for incorrect
- **Haptic Feedback** - Vibration on submit (on supported devices)
- **Responsive Design** - Optimized for tablets and different screen sizes
- **Polish UI** - Child-friendly buttons, smooth interactions

**Phase 3 - Spelling Validation & Learning/Recall Modes:**
- **Spelling Auto-Validation** - Real-time feedback (correct/incorrect)
- **Learning Mode** - All letters visible for first 2 successful days
- **Recall Mode** - Type word from memory after 2 successful days
- **Animated Feedback** - Green for correct, red for incorrect with scaling animation
- **Mode Indicator** - Shows current mode and progress tracking
- **Keep-Trying Logic** - Child keeps attempting until correct within one session
- **Sound & Haptic Feedback** - Audio confirmation with vibration

**Phase 4 - Spaced Repetition & Progress Tracking:**
- **Multi-Day Tracking** - `successful_days` counts days practiced (not session attempts)
- **Review Scheduling** - Words scheduled: +2 days after 1st success, +3 days after 2nd+ successes
- **Smart Mode Switching** - Permanent (not session-based): Learning Mode (0-1 successful days) → Recall Mode (2+ successful days)
- **Daily Limits** - `successful_days` increments max once per day (prevents practicing same word multiple times counting)
- **Today's Queue** - Only words where `next_review <= today` are shown
- **Session Deduplication** - Never show same word twice in one practice session
- **Progress Persistence** - All tracking data persists across sessions and days
- **API Endpoints** - `/api/next-word` returns `successful_days`, `/api/words-for-today` for dashboard

**Phase 5 - Admin Mode - Word Management:**
- **Admin Interface** - Dedicated admin panel at `/admin.html` with password protection
- **Add Words** - Form to add new words with category and optional reference image
- **Delete Words** - Remove words and all associated practice records
- **Word List** - View all words with metadata (successful_days, next_review, category)
- **Reference Images** - Upload and store reference images for each word
- **API Endpoints** - Full CRUD: POST/GET/PUT/DELETE at `/api/admin/words`
- **Password Protection** - Simple password guard to prevent child access
- **Auto-Initialization** - New words automatically ready for practice today

**Phase 6 - Parent/Teacher Dashboard:**
- **Progress Statistics** - Words completed today/this week, overall accuracy, total practices
- **Practice Trend** - 7-day bar chart showing daily practice activity
- **Word Performance** - Accuracy per word sorted by difficulty (hardest first)
- **Drawing Gallery** - Recent 20 drawings with thumbnails, word names, and correct/incorrect badges
- **Real-time Refresh** - Refresh button to reload latest data
- **Color Indicators** - Visual highlighting for difficult words (accuracy < 70%)
- **Dashboard Interface** - Clean, responsive dashboard at `/dashboard.html`
- **API Endpoints** - `/api/dashboard/stats`, `/trend`, `/word-accuracy`, `/drawings`

**Phase 7 - Data Management & Performance:**
- **Storage Statistics** - Track database size, drawings size, total storage used
- **Cleanup Tools** - Remove old drawings (keep last N per word, configurable)
- **Database Optimization** - VACUUM command to reclaim space and improve performance
- **Backup System** - Create timestamped database backups
- **Image Compression** - PNG to JPEG compression utilities (PIL/Pillow)
- **Performance Monitoring** - Real-time storage stats API
- **API Endpoints** - `/api/data/storage-stats`, `/cleanup`, `/optimize`, `/backup`

**Phase 8 - Polish & Nice-to-Haves:**
- **Dark Mode** - Toggle between light and dark themes with localStorage persistence
- **Progress Badge** - Floating badge showing words practiced this week
- **Celebration Animation** - Badge bounces on correct answers
- **Weekly Progress** - Real-time display of words practiced this week
- **Theme Persistence** - Dark mode preference saved across sessions
- **Event-Driven Updates** - Progress updates triggered on correct answers
- **Click Interaction** - Badge shows encouraging message when clicked

---

## Project Structure

```
/Spelling
├── backend/
│   ├── main.py              # FastAPI app with routes
│   ├── database.py          # SQLite setup and queries
│   ├── test_admin.py        # Phase 5 admin tests
│   ├── test_dashboard.py    # Phase 6 dashboard tests
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main app page
│   ├── admin.html           # Phase 5 admin panel
│   ├── dashboard.html       # Phase 6 parent dashboard
│   ├── style.css            # Styles
│   ├── canvas.js            # Canvas drawing logic
│   ├── api.js               # Backend API calls
│   └── app.js               # Main app orchestration
├── data/
│   ├── drawings/            # Saved drawing images
│   ├── references/          # Phase 5 reference images
│   └── spelling.db          # SQLite database
├── Plan.md                  # Phase-by-phase development plan
├── Agents.md                # Development guidelines
└── README.md                # This file
```

---

## Setup & Installation

### Requirements

- Python 3.8+
- Modern web browser (Chrome, Safari, Edge)
- uv package manager (for running Python)

### Install uv

If you don't have uv installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add to PATH:
```bash
source ~/.local/bin/env
```

Verify installation:
```bash
uv --version
```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment and install dependencies:
   ```bash
   ~/.local/bin/uv venv
   ~/.local/bin/uv pip install -r requirements.txt
   ```

3. Run the server (in Terminal 1):
   ```bash
   ~/.local/bin/uv run python main.py
   ```

   You should see:
   ```
   Uvicorn running on http://0.0.0.0:8000
   ```

### Frontend Setup

1. In a new terminal, navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Start the web server (in Terminal 2):
   ```bash
   ~/.local/bin/uv run python -m http.server 8002
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8002/index.html
   ```

### Running the App

Keep both terminals running:
- **Terminal 1:** Backend API on `http://localhost:8000`
- **Terminal 2:** Frontend on `http://localhost:8002`

The app will automatically connect to the backend and load the first word.

---

## Usage

1. **Load App** - Navigate to the app URL
2. **See Word** - The current word is displayed at the top
3. **Draw** - Use the canvas to draw the object
4. **Spell** - Tap the letters in order to spell the word
5. **Submit** - Click "Done" to save the drawing and spelling
6. **Next** - The app automatically loads the next word

### Canvas Controls

- **Pen Button** - Switch to drawing mode
- **Eraser Button** - Switch to eraser mode
- **Color Picker** - Choose pen color
- **Clear Button** - Clear entire canvas
- **Brush Size** - (Phase 2) Adjust pen thickness

---

## Database

The app uses SQLite with two main tables:

### Words Table (Phase 4 & 5 Updates)
```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    successful_days INTEGER DEFAULT 0,
    last_practiced DATE,
    next_review DATE,
    reference_image TEXT,
    created_date TIMESTAMP
);
```

### Practices Table
```sql
CREATE TABLE practices (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL,
    spelled_word TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    drawing_filename TEXT,
    practiced_date TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id)
);
```

Default test words: bee, spider, butterfly (insects category)

### Key Tracking Fields:
- **successful_days**: How many different days child successfully practiced (max counts once per day)
- **last_practiced**: Last date of successful practice
- **next_review**: When to show word next (never before this date)
- **is_correct**: Whether practice attempt was correct (for logging)

---

## API Endpoints

**Practice Endpoints:**
- `GET /api/health` - Check API status
- `GET /api/words` - Get all words
- `GET /api/next-word` - Get next word to practice
- `GET /api/words-for-today` - Get all words ready for practice today
- `POST /api/practice` - Submit drawing + spelling

**Admin Endpoints (Phase 5):**
- `GET /api/admin/words` - Get all words with full details
- `POST /api/admin/words` - Add new word
- `PUT /api/admin/words/{id}` - Update word
- `DELETE /api/admin/words/{id}` - Delete word

**Dashboard Endpoints (Phase 6):**
- `GET /api/dashboard/stats` - Get overall practice statistics
- `GET /api/dashboard/word-accuracy` - Get accuracy per word
- `GET /api/dashboard/trend?days=7` - Get practice trend
- `GET /api/dashboard/drawings?limit=20` - Get recent drawings

---

## Development Phases

See [Plan.md](Plan.md) for detailed phase-by-phase development roadmap.

**Complete:**
- Phase 1 - MVP ✓
- Phase 2 - Canvas Polish & UX ✓
- Phase 3 - Spelling Validation & Learning/Recall Modes ✓
- Phase 4 - Spaced Repetition & Progress Tracking ✓
- Phase 5 - Admin Mode (Word Management) ✓
- Phase 6 - Parent Dashboard ✓
- Phase 7 - Data Management & Performance ✓
- Phase 8 - Polish & Nice-to-Haves ✓

**Planned:**
- Phase 9 - Testing & Tablet Compatibility
- Phase 10 - Launch & Expansion

---

## Browser Compatibility

- Chrome 90+
- Safari 14+
- Edge 90+
- Mobile browsers on iPad/Android tablets

### Touch Support

The app fully supports:
- Touch screens (finger)
- Stylus input (Apple Pencil, Samsung S Pen, etc.)
- Mouse input (for testing)

---

## Troubleshooting

### API Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings if running on different domains
- Check browser console for detailed error messages

### Drawings Not Saving
- Verify `data/drawings/` directory exists and is writable
- Check database permissions
- Review backend logs for errors

### Canvas Not Responding
- Ensure browser supports HTML5 Canvas
- Check browser's hardware acceleration settings
- Clear browser cache if experiencing issues

---

## Future Features

Planned in upcoming phases:
- Eraser mode
- Undo/Redo
- Spelling validation with feedback
- Spaced repetition scheduling
- Admin panel for word management
- Parent/teacher dashboard
- Progress tracking and analytics
- Offline support
- Multi-child profiles
- Celebration animations

---

## Notes for Development

- Follow guidelines in [Agents.md](Agents.md)
- Update README when adding features
- Test on actual tablet devices regularly
- Keep child interface simple and touch-friendly
- All images saved to `data/drawings/` with timestamps

---

## License

This project is developed for educational purposes.
