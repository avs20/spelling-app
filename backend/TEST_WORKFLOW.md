# Add Word Workflow Test

This test validates the complete user flow:
1. Add a new word via admin panel
2. Open the web app
3. Put correct spelling
4. Click Done button twice
5. Verify "No words pending" banner appears

## Prerequisites

1. Backend running on http://localhost:8000
2. Playwright installed and browsers available

## Running the Test

From the backend directory:

```bash
# Reset database to clean state first
uv run python -c "from database import reset_db_to_initial; reset_db_to_initial()"

# Then run the test
uv run python test_add_word_workflow.py
```

Or run directly:

```bash
python -m test_add_word_workflow
```

## What the Test Does

- **Step 1**: Logs into admin panel with password "admin123"
- **Step 2**: Adds a test word "elephant" to the database
- **Step 3**: Opens the main web app
- **Step 4**: Enters the correct spelling using either:
  - Letter buttons (Learning Mode) - for words with < 2 successful days
  - Text input (Recall Mode) - for words with >= 2 successful days
- **Step 5a**: Clicks the Done button once
- **Step 5b**: Clicks the Done button a second time
- **Step 6**: Verifies the completion banner appears

## Expected Results

✅ When all words have been successfully practiced, the app should show:
- Completion banner with "🎉 All Words Complete!"
- Main content hidden
- Success message in console

## Screenshots

All test screenshots are saved to `../test-screenshots/` directory with timestamps for reference.

## Troubleshooting

If the test fails:

1. **Check backend is running**: `http://localhost:8000/api/health`
2. **Verify admin password**: Check `frontend/admin.html` for current password
3. **Check word was added**: Login to admin panel and verify word exists
4. **Run database reset first**: Ensures clean state for testing

## Output Example

```
============================================================
ADD WORD WORKFLOW TEST
============================================================

Starting test...

🧪 Starting add word workflow test...

Step 1: 📝 Adding new word via admin panel...
   ✓ Admin logged in
   ✓ Word 'elephant' added to database

Step 2: 🎯 Opening web app...
   ✓ Web app loaded

Step 3: 🔍 Verifying 'elephant' is available...
   Current word: bee

Step 4: ✍️ Entering correct spelling 'bee'...
   Learning Mode detected - clicking 3 letters
   Clicking letter button: B
   Clicking letter button: E
   Clicking letter button: E
   ✓ Spelling entered

Step 5a: 🏁 Clicking Done button (1st time)...
   ✓ First Done clicked

Step 5b: 🏁 Clicking Done button (2nd time)...
   ✓ Second Done clicked

Step 6: ✅ Verifying completion state...
   ✅ SUCCESS: Completion banner is visible!

============================================================
✅ TEST PASSED!
============================================================

📸 Screenshots saved to: /path/to/test-screenshots
```
