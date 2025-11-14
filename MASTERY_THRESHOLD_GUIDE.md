# Session Mastery Threshold Configuration (Issue #16)

## Overview

Parents can now configure how many times a child must spell a word correctly within a single practice session before the word is considered "mastered" and removed from that session's queue.

## Default Behavior

- **Default threshold**: 2
- This means a child must spell a word correctly **2 times in the same session** before it's mastered
- After mastery, the word is removed from the session queue but remains available for future sessions based on the spaced repetition schedule

## How It Works

### During a Practice Session

1. Child starts a practice session
2. Child is given words from their list ready for practice
3. When child spells a word correctly (1st time):
   - Word stays in session queue
   - Child may see the word again in the session
4. When child spells the same word correctly (2nd time):
   - Word is removed from session queue
   - Word is marked as "mastered" for this session
5. Session continues with remaining unmastered words

### Example Timeline

With 3 words (apple, banana, cherry) and threshold=2:

```
1. Get "apple" → Child spells correctly (1/2) → Still in queue
2. Get "banana" → Child spells correctly (1/2) → Still in queue  
3. Get "cherry" → Child spells correctly (1/2) → Still in queue
4. Get "apple" → Child spells correctly (2/2) → MASTERED, removed from queue
5. Get "banana" → Child spells correctly (2/2) → MASTERED, removed from queue
6. Get "cherry" → Child spells correctly (2/2) → MASTERED, removed from queue

Session complete: All 3 words mastered in 6 practice attempts
```

## Changing the Threshold

### Via API

**Get current threshold:**
```
GET /api/admin/mastery-threshold
Authentication: Required (JWT token)

Response:
{
  "mastery_threshold": 2
}
```

**Set new threshold:**
```
POST /api/admin/mastery-threshold?threshold=3
Authentication: Required (JWT token)

Response:
{
  "success": true,
  "mastery_threshold": 3
}
```

### Constraints

- Minimum: 1 (word mastered after first correct spelling)
- Maximum: 10 (word needs up to 10 correct spellings)

### Common Configurations

| Threshold | Use Case | Notes |
|-----------|----------|-------|
| 1 | Younger children or beginners | Fast mastery, more encouragement |
| 2 | Standard/default | Good balance of reinforcement |
| 3 | Advanced learners | More thorough reinforcement |
| 4+ | Very challenging words | Maximum repetition for difficult words |

## Database Schema

### Users Table Addition (Migration 2)

```sql
ALTER TABLE users ADD COLUMN session_mastery_threshold INTEGER DEFAULT 2;
```

- Each user (parent) has their own threshold setting
- Applies to all their children's practice sessions
- Defaults to 2 for new users

## Implementation Details

### Session Tracking

The `WordSession` class tracks correct attempts per word:

```python
class WordSession:
    def __init__(self, mastery_threshold=2):
        self.mastery_threshold = mastery_threshold
        self.word_correct_count = {}  # Tracks correct answers per word
        
    def mark_word_mastered(self, word_id):
        # Increment correct count
        # Only remove from queue when threshold is reached
```

### Spaced Repetition (Unchanged)

The mastery threshold affects **within-session** word removal only.

The long-term spaced repetition schedule (when words come back for review) is **not affected**:
- After 1 successful day → review in 2 days
- After 2+ successful days → review in 3 days

## Testing

Run mastery threshold tests:

```bash
cd backend
python3 test_mastery_threshold.py
```

This tests:
- Default threshold (2)
- Setting/getting threshold values
- Word mastery with different thresholds
- Threshold validation (1-10 range)

## UI Integration

For admin panel integration:

```html
<div class="mastery-threshold-setting">
  <label>Words must be practiced correctly</label>
  <input type="number" 
         id="mastery-threshold" 
         min="1" 
         max="10" 
         value="2">
  <span>times in a session before mastery</span>
  <button onclick="updateMasteryThreshold()">Save</button>
</div>
```

```javascript
async function updateMasteryThreshold() {
  const threshold = document.getElementById('mastery-threshold').value;
  const response = await fetch('/api/admin/mastery-threshold?threshold=' + threshold, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const data = await response.json();
  if (data.success) {
    alert(`Mastery threshold updated to ${data.mastery_threshold}`);
  }
}
```

## Impact on Child Progress

- **Learning Phase**: Words with low `successful_days` are shown more frequently and require threshold correct answers per session
- **Recall Phase**: Words with 2+ `successful_days` return after 2-3 days for review
- **No Impact on Spaced Repetition**: The overall learning schedule remains unchanged

## Backward Compatibility

- Existing users automatically get threshold=2 (set by migration)
- All new users get threshold=2 by default
- Can be changed at any time without affecting practice history

## Related Features

- **Successful Days** (database): Tracks days a word has been practiced correctly overall
- **Spaced Repetition**: Days until next review (2-3 days depending on successful_days)
- **Session Queue**: Words available in current session based on next_review date
