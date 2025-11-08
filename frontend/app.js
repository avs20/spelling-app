/**
 * Main App Module
 * Orchestrates the spelling and drawing app
 */

class SpellingApp {
    constructor() {
        this.currentWord = null;
        this.currentWordId = null;
        this.spelledLetters = [];
        
        this.setupElements();
        this.setupEventListeners();
        this.init();
    }

    setupElements() {
        this.wordDisplay = document.getElementById('word-display');
        this.lettersContainer = document.getElementById('letters-container');
        this.spelledDisplay = document.getElementById('spelled-display');
        
        this.penBtn = document.getElementById('pen-btn');
        this.eraserBtn = document.getElementById('eraser-btn');
        this.colorPicker = document.getElementById('color-picker');
        this.clearBtn = document.getElementById('clear-btn');
        this.submitBtn = document.getElementById('submit-btn');
    }

    setupEventListeners() {
        this.penBtn.addEventListener('click', () => this.setPenMode());
        this.eraserBtn.addEventListener('click', () => this.setEraserMode());
        this.colorPicker.addEventListener('change', (e) => this.setColor(e.target.value));
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
        this.spelledDisplay.textContent = this.spelledLetters.join('');
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

    clearCanvas() {
        canvas.clear();
    }

    async submitPractice() {
        if (!this.currentWordId || this.spelledLetters.length === 0) {
            alert('Please draw and spell the word first');
            return;
        }

        const spelledWord = this.spelledLetters.join('').toLowerCase();
        const isCorrect = spelledWord === this.currentWord.toLowerCase();

        // Get drawing as blob
        const drawingBlob = await canvas.getImageData();

        // Submit to backend
        const result = await API.submitPractice(
            this.currentWordId,
            spelledWord,
            drawingBlob
        );

        if (result.success) {
            // Show feedback
            if (isCorrect) {
                alert('Correct! Well done! 🎉');
            } else {
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
