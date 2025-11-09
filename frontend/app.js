/**
 * Main App Module
 * Orchestrates the spelling and drawing app
 */

class SpellingApp {
    constructor() {
        this.currentWord = null;
        this.currentWordId = null;
        this.spelledLetters = [];
        this.attemptCount = 0;  // Track attempts within a session
        this.successfulDays = 0;  // Phase 4: Days successfully practiced (from backend)
        this.practicedWordsToday = new Set();  // Phase 4: Track words practiced in this session
        this.isSubmitting = false;  // Prevent double-submit

        // Audio context for sound effects
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

        this.setupElements();
        this.setupEventListeners();
        this.init();
    }

    setupElements() {
        this.wordDisplay = document.getElementById('word-display');
        this.lettersContainer = document.getElementById('letters-container');
        this.spelledDisplay = document.getElementById('spelled-display');
        this.modeIndicator = document.getElementById('mode-indicator');
        this.feedbackMessage = document.getElementById('feedback-message');

        this.undoBtn = document.getElementById('undo-btn');
        this.redoBtn = document.getElementById('redo-btn');
        this.penBtn = document.getElementById('pen-btn');
        this.eraserBtn = document.getElementById('eraser-btn');
        this.colorPicker = document.getElementById('color-picker');
        this.penSizeSlider = document.getElementById('pen-size');
        this.clearBtn = document.getElementById('clear-btn');
        this.submitBtn = document.getElementById('submit-btn');
    }

    setupEventListeners() {
        this.undoBtn.addEventListener('click', () => this.undo());
        this.redoBtn.addEventListener('click', () => this.redo());
        this.penBtn.addEventListener('click', () => this.setPenMode());
        this.eraserBtn.addEventListener('click', () => this.setEraserMode());
        this.colorPicker.addEventListener('change', (e) => this.setColor(e.target.value));
        this.penSizeSlider.addEventListener('input', (e) => this.setPenSize(e.target.value));
        this.clearBtn.addEventListener('click', () => this.clearCanvas());
        this.submitBtn.addEventListener('click', () => this.submitPractice());
    }

    async init() {
        // Check API connection
        const isHealthy = await API.checkHealth();
        if (!isHealthy) {
            console.warn('API not available, using test mode');
        }

        // Load next word
        await this.loadNextWord();
    }

    async loadNextWord() {
        const wordData = await API.getNextWord();

        if (!wordData) {
            this.wordDisplay.textContent = 'No words available';
            return;
        }

        this.currentWord = wordData.word;
        this.currentWordId = wordData.id;
        this.successfulDays = wordData.successful_days || 0;  // Phase 4: Get from backend
        this.spelledLetters = [];
        this.attemptCount = 0;  // Reset attempt count for new word
        this.isSubmitting = false;  // Reset submit flag for new word
        this.practicedWordsToday.add(this.currentWordId);  // Phase 4: Mark as practiced today

        this.wordDisplay.textContent = this.currentWord;
        this.renderLetters();
        this.updateSpelledDisplay();
        this.updateModeIndicator();
        this.clearFeedback();
        canvas.clear();
        this.updateUndoRedoButtons();
    }

    renderLetters() {
        /**
         * Phase 4: Mode switching based on successful_days (not session attempts)
         * Learning Mode (successful_days < 2): All letters visible (shuffled)
         * Recall Mode (successful_days >= 2): Text input field
         */
        this.lettersContainer.innerHTML = '';

        if (this.successfulDays < 2) {
            // Learning Mode: Show letters
            const letters = this.currentWord.toUpperCase().split('');
            const shuffledLetters = this.shuffleArray([...letters]);

            shuffledLetters.forEach((letter, index) => {
                const btn = document.createElement('button');
                btn.className = 'letter-btn';
                btn.textContent = letter;
                btn.addEventListener('click', () => this.selectLetter(letter, index));
                this.lettersContainer.appendChild(btn);
            });
        } else {
            // Recall Mode: Show text input (child types from memory)
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'recall-input';
            input.className = 'recall-input';
            input.placeholder = 'Type the word...';
            input.maxLength = this.currentWord.length;
            input.addEventListener('input', (e) => this.handleRecallInput(e));
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.submitPractice();
            });
            this.lettersContainer.appendChild(input);
            // Auto-focus on input
            setTimeout(() => input.focus(), 100);
        }
    }

    shuffleArray(array) {
        /**
         * Fisher-Yates shuffle algorithm
         * Randomizes array order
         */
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    selectLetter(letter, correctIndex) {
        /**
         * Handle letter selection in Learning Mode
         * Append to spelled letters if space available
         */
        if (this.spelledLetters.length < this.currentWord.length) {
            this.spelledLetters.push(letter);
            this.updateSpelledDisplay();
        }
    }

    handleRecallInput(e) {
        /**
         * Handle text input in Recall Mode
         * Store typed letters as spelledLetters
         */
        const input = e.target;
        this.spelledLetters = input.value.toUpperCase().split('');
        this.updateSpelledDisplay();
    }

    updateSpelledDisplay() {
        /**
         * Show spelled letters as clickable elements
         * Tap a letter to remove it
         */
        this.spelledDisplay.innerHTML = '';

        this.spelledLetters.forEach((letter, index) => {
            const letterSpan = document.createElement('span');
            letterSpan.className = 'spelled-letter';
            letterSpan.textContent = letter;
            letterSpan.style.cursor = 'pointer';

            // Add click handler
            letterSpan.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeLetter(index);
            });

            this.spelledDisplay.appendChild(letterSpan);
        });
    }

    removeLetter(index) {
        /**
         * Remove a letter from the spelled word at given index
         */
        console.log('Removing letter at index:', index);
        this.spelledLetters.splice(index, 1);
        this.updateSpelledDisplay();
    }

    undo() {
        canvas.undo();
        this.updateUndoRedoButtons();
    }

    redo() {
        canvas.redo();
        this.updateUndoRedoButtons();
    }

    updateUndoRedoButtons() {
        this.undoBtn.disabled = !canvas.canUndo();
        this.redoBtn.disabled = !canvas.canRedo();
    }

    setPenMode() {
        canvas.setMode('pen');
        this.penBtn.classList.add('active');
        this.eraserBtn.classList.remove('active');
    }

    setEraserMode() {
        canvas.setMode('eraser');
        this.eraserBtn.classList.add('active');
        this.penBtn.classList.remove('active');
    }

    setColor(color) {
        canvas.setPenColor(color);
    }

    setPenSize(size) {
        canvas.setPenSize(parseInt(size));
    }

    clearCanvas() {
        canvas.clear();
        this.updateUndoRedoButtons();
    }

    updateModeIndicator() {
        /**
         * Phase 4: Show current mode based on successful_days
         * Learning Mode: successful_days < 2
         * Recall Mode: successful_days >= 2 (permanent for this word)
         */
        if (this.modeIndicator) {
            if (this.successfulDays < 2) {
                this.modeIndicator.textContent = `Learning Mode (${this.successfulDays}/2 days mastered)`;
                this.modeIndicator.className = 'mode-learning';
            } else {
                this.modeIndicator.textContent = `Recall Mode (Mastered - typing practice)`;
                this.modeIndicator.className = 'mode-recall';
            }
        }
    }

    showFeedback(isCorrect, message) {
        /**
         * Show feedback message with animation
         */
        if (this.feedbackMessage) {
            this.feedbackMessage.textContent = message;
            this.feedbackMessage.className = isCorrect ? 'feedback-correct' : 'feedback-incorrect';
            this.feedbackMessage.style.display = 'block';
            this.feedbackMessage.style.animation = 'fadeInScale 0.5s ease-out';
            
            // Phase 8: Trigger celebration event on correct answer
            if (isCorrect) {
                document.dispatchEvent(new Event('correctAnswer'));
                this.triggerCelebration();
            }
        }
    }

    triggerCelebration() {
        /**
         * Full-screen celebration animation on success
         */
        const body = document.body;
        body.classList.add('celebration-active');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            body.classList.remove('celebration-active');
        }, 600);
    }

    clearFeedback() {
        /**
         * Clear feedback message
         */
        if (this.feedbackMessage) {
            this.feedbackMessage.style.display = 'none';
        }
    }

    playSound(type = 'correct') {
        /**
         * Play sound effect
         * Types: 'correct', 'incorrect', 'click'
         */
        try {
            const now = this.audioContext.currentTime;
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();

            osc.connect(gain);
            gain.connect(this.audioContext.destination);

            if (type === 'correct') {
                // Success sound: ascending tones
                osc.frequency.setValueAtTime(400, now);
                osc.frequency.setValueAtTime(600, now + 0.1);
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.setValueAtTime(0, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            } else if (type === 'incorrect') {
                // Error sound: descending tone
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.setValueAtTime(150, now + 0.2);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.setValueAtTime(0, now + 0.2);
                osc.start(now);
                osc.stop(now + 0.2);
            } else if (type === 'click') {
                // Click sound
                osc.frequency.setValueAtTime(200, now);
                gain.gain.setValueAtTime(0.1, now);
                gain.gain.setValueAtTime(0, now + 0.05);
                osc.start(now);
                osc.stop(now + 0.05);
            }
        } catch (e) {
            console.log('Sound not available:', e);
        }
    }

    hapticFeedback() {
        /**
         * Trigger haptic feedback if available
         */
        if (navigator.vibrate) {
            navigator.vibrate(50); // Vibrate for 50ms
        }
    }

    async submitPractice() {
        // Prevent double-submit (when only one word left and user clicks Done multiple times)
        if (this.isSubmitting) {
            return;
        }

        if (!this.currentWordId || this.spelledLetters.length === 0) {
            this.showFeedback(false, 'Please spell the word first');
            return;
        }

        this.isSubmitting = true;
        const spelledWord = this.spelledLetters.join('').toLowerCase();
        const isCorrect = spelledWord === this.currentWord.toLowerCase();
        this.attemptCount++;

        // Haptic feedback
        this.hapticFeedback();

        // Show immediate feedback with animation
        if (isCorrect) {
            this.playSound('correct');
            this.showFeedback(true, 'Correct! Well done! 🎉');
        } else {
            this.playSound('incorrect');
            if (this.attemptCount >= 2 && this.attemptCount < 3) {
                // Transitioning to Recall Mode
                this.showFeedback(false, `Not quite. Try again! (Will be Recall Mode next attempt)`);
            } else if (this.attemptCount >= 3) {
                this.showFeedback(false, `The word is: ${this.currentWord}`);
            } else {
                this.showFeedback(false, 'Not quite right. Try again!');
            }
        }

        // Get drawing as blob
        const drawingBlob = await canvas.getImageData();

        // Submit to backend
        const result = await API.submitPractice(
            this.currentWordId,
            spelledWord,
            drawingBlob,
            isCorrect
        );

        if (result.success) {
            // If correct, load next word after delay
            if (isCorrect) {
                setTimeout(() => this.loadNextWord(), 2000);
            } else {
                // If incorrect, prepare for next attempt
                setTimeout(() => {
                    this.isSubmitting = false;
                    this.spelledLetters = [];
                    this.updateSpelledDisplay();
                    this.renderLetters();
                    this.updateModeIndicator();
                    this.clearFeedback();
                    canvas.clear();
                }, 2000);
            }
        } else {
            this.isSubmitting = false;
            this.showFeedback(false, 'Error saving. Please try again.');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new SpellingApp();
});
