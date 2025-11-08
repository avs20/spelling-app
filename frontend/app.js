/**
 * Main App Module
 * Orchestrates the spelling and drawing app
 */

class SpellingApp {
    constructor() {
        this.currentWord = null;
        this.currentWordId = null;
        this.spelledLetters = [];
        
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
        this.spelledLetters = [];
        
        this.wordDisplay.textContent = this.currentWord;
        this.renderLetters();
        this.updateSpelledDisplay();
        canvas.clear();
        this.updateUndoRedoButtons();
    }

    renderLetters() {
        /**
         * Phase 1: Learning Mode - All letters visible (shuffled)
         * Child taps letters in order to spell the word
         */
        this.lettersContainer.innerHTML = '';
        
        const letters = this.currentWord.toUpperCase().split('');
        const shuffledLetters = this.shuffleArray([...letters]);
        
        shuffledLetters.forEach((letter, index) => {
            const btn = document.createElement('button');
            btn.className = 'letter-btn';
            btn.textContent = letter;
            btn.addEventListener('click', () => this.selectLetter(letter, index));
            this.lettersContainer.appendChild(btn);
        });
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
         * Track which letter was selected
         * In Phase 1, we just append it to spelled letters
         */
        if (this.spelledLetters.length < this.currentWord.length) {
            this.spelledLetters.push(letter);
            this.updateSpelledDisplay();
        }
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
        if (!this.currentWordId || this.spelledLetters.length === 0) {
            alert('Please draw and spell the word first');
            return;
        }

        const spelledWord = this.spelledLetters.join('').toLowerCase();
        const isCorrect = spelledWord === this.currentWord.toLowerCase();

        // Haptic feedback
        this.hapticFeedback();

        // Get drawing as blob
        const drawingBlob = await canvas.getImageData();

        // Submit to backend
        const result = await API.submitPractice(
            this.currentWordId,
            spelledWord,
            drawingBlob
        );

        if (result.success) {
            // Show feedback with sound
            if (isCorrect) {
                this.playSound('correct');
                alert('Correct! Well done! 🎉');
            } else {
                this.playSound('incorrect');
                alert(`Not quite right. The word is: ${this.currentWord}`);
            }

            // Load next word
            await this.loadNextWord();
        } else {
            alert('Error saving practice. Please try again.');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new SpellingApp();
});
