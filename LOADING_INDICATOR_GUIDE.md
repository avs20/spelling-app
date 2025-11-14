# Loading Indicator Implementation

This guide explains the loading indicator feature added to handle slow Turso API responses.

## Overview

A loading overlay with a spinner appears when API calls take longer than 500ms to respond. This provides visual feedback to users that the app is working.

## How It Works

### Smart Delay
- The loading indicator only appears if a request takes **longer than 500ms**
- This prevents visual flashing for fast responses
- Users get immediate feedback for slow API calls

### Visual Design
- **Overlay**: Semi-transparent dark background with blur effect
- **Spinner**: Animated circular spinner in the brand color (#667eea)
- **Text**: "Loading..." message displayed below the spinner

## Implementation Details

### Files Modified

#### 1. `frontend/api.js`
Added two utility functions:
- `showLoading()` - Shows the loading overlay after 500ms delay
- `hideLoading()` - Hides the overlay and cancels pending timeouts

Added loading indicators to these API methods:
- `getCurrentUser()` - User authentication
- `getChildren()` - Fetch child profiles
- `getWords()` - Fetch word list
- `startSession()` - Start practice session
- `getNextWord()` - Get next word to practice
- `submitPractice()` - Submit practice response

#### 2. `frontend/index.html`
Added:
- HTML element for the loading overlay with spinner and text
- CSS styles for:
  - `#api-loading-overlay` - Main overlay container
  - `.loading-spinner` - Animated spinner
  - `.loading-text` - Loading message
  - `@keyframes spin` - Rotation animation

## Usage Pattern

Every slow API call now follows this pattern:

```javascript
static async apiMethod() {
    showLoading();  // Start showing loader after 500ms
    try {
        const response = await fetch(url);
        // ... handle response
        return result;
    } catch (e) {
        // ... handle error
        return null;
    } finally {
        hideLoading();  // Always hide loader when done
    }
}
```

## Customization

### Adjust Delay Time
To change when the loading indicator appears, modify this line in `api.js`:

```javascript
loadingTimeoutId = setTimeout(() => {
    // Change 500 to desired milliseconds
}, 500);
```

### Change Colors
Update the CSS in `index.html`:
- `border-top: 4px solid #667eea;` - Change spinner color
- `background: rgba(0, 0, 0, 0.5);` - Change overlay darkness

### Modify Spinner Size
Update in `index.html`:
```css
.loading-spinner {
    width: 60px;      /* Change size here */
    height: 60px;
}
```

## User Experience

1. User clicks submit or triggers API call
2. If API responds within 500ms → No loader shown (instant feel)
3. If API takes longer:
   - Loader appears after 500ms
   - User sees spinner and "Loading..." text
   - Overlay prevents accidental clicks
4. When API responds → Loader disappears immediately

## Testing

To test the loading indicator:
1. Simulate slow network in browser DevTools (Network tab → Throttling)
2. Perform any action that triggers an API call
3. You should see the loading overlay appear after ~500ms
4. It should disappear when the API responds

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Uses `backdrop-filter` for blur effect (graceful degradation in older browsers)
- Fallback is still a semi-transparent overlay
