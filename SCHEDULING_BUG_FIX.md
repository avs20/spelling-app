# Scheduling Bug Fix - November 11, 2025

## Issue
When a word was practiced correctly 2 times, it should be scheduled for review 3 days in the future. However, users reported the word reappearing unexpectedly.

## Root Cause
The `update_word_on_success_for_child()` function only updated the `child_progress` table (per-child tracking) but did NOT update the `words` table. While the main word retrieval logic uses `child_progress` as the primary source, the `words` table is used as a fallback in some queries and for consistency.

This created an inconsistent state where:
- `child_progress.next_review` was correctly set to a future date
- `words.next_review` remained at today's date (or an outdated value)

This could cause unexpected behavior in edge cases or queries that fall back to the `words` table.

## Solution
Updated `update_word_on_success_for_child()` in `backend/database.py` to also update the `words` table with:
- `successful_days`: incremented count
- `last_practiced`: today's date
- `next_review`: calculated based on the new successful_days count

This ensures both tables stay in sync.

## Scheduling Rules (Verified)
- **After 1st correct submission**: next_review = today + 2 days
  - Learning Mode (shows letters for child to select)
- **After 2nd+ correct submissions**: next_review = today + 3 days
  - Recall Mode (child types from memory)

## Testing
Created comprehensive tests to verify:
1. `test_scheduling_final.py` - Verifies both tables are updated correctly after each submission
2. `test_real_world_scheduling.py` - Simulates multi-day practice scenario
3. `test_scheduling_bug_v2.py` - Tests across multiple days with various states

All tests pass, confirming the scheduling logic works correctly and words are properly hidden until their next_review date.

## Changes Made
- File: `backend/database.py`
- Function: `update_word_on_success_for_child()` (lines 683-757)
- Addition: UPDATE statement for `words` table (lines 748-752)
