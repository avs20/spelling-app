# Spelling & Drawing App

A tablet-friendly web app for children to practice spelling while drawing objects. The app uses spaced repetition to optimize learning.

**Current Phase:** Phase 3 - Spelling Validation & Learning/Recall Modes (Complete) | Phase 4 - Spaced Repetition (In Progress)

---

## Features (Phase 1-3) ✓ COMPLETE

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
- **Mode Indicator** - Shows current mode and attempt tracking
- **Keep-Trying Logic** - Child keeps attempting until correct within one session
- **Session-Level Attempts** - Tracks attempts within a practice session
- **Sound & Haptic Feedback** - Audio confirmation with vibration

---

## Project Structure

```
/Spelling
├── backend/
│   ├── main.py              # FastAPI app with routes
│   ├── database.py          # SQLite setup and queries
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main app page
│   ├── style.css            # Styles
│   ├── canvas.js            # Canvas drawing logic
│   ├── api.js               # Backend API calls
│   └── app.js               # Main app orchestration
├── data/
│   ├── drawings/            # Saved drawing images
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

### Words Table (Phase 4 Update)
```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    successful_days INTEGER DEFAULT 0,
    last_practiced DATE,
    next_review DATE,
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

## API Endpoints (Phase 1)

- `GET /api/health` - Check API status
- `GET /api/words` - Get all words
- `GET /api/next-word` - Get next word to practice
- `POST /api/practice` - Submit drawing + spelling

---

## Development Phases

See [Plan.md](Plan.md) for detailed phase-by-phase development roadmap.

**Complete:**
- Phase 1 - MVP ✓
- Phase 2 - Canvas Polish & UX ✓
- Phase 3 - Spelling Validation & Learning/Recall Modes ✓

**In Progress:**
- Phase 4 - Spaced Repetition & Progress Tracking

**Planned:**
- Phase 5 - Admin Mode (Word Management)
- Phase 6 - Parent Dashboard
- Phase 7 - Data Management & Performance
- Phase 8 - Polish & Nice-to-Haves
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
