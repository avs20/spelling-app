/**
 * Canvas Drawing Module
 * Handles pen/eraser drawing with touch and mouse support
 */

class DrawingCanvas {
    constructor(canvasId = 'drawing-canvas') {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        this.drawMode = 'pen'; // 'pen' or 'eraser'
        this.penColor = '#000000';
        this.penSize = 3;
        this.eraserSize = 20; // Large eraser for children
        this.isDrawing = false;
        
        this.setupCanvas();
        this.setupEventListeners();
    }

    setupCanvas() {
        // Set canvas size to fill container
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Clear canvas with white background
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set initial cursor
        this.updateCursor();
    }

    resizeCanvas() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = Math.max(400, window.innerHeight - 500);
        
        // Redraw on resize (for now, just clear)
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setupEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());

        // Touch events (for stylus/finger on tablet)
        this.canvas.addEventListener('touchstart', (e) => this.startDrawing(e));
        this.canvas.addEventListener('touchmove', (e) => this.draw(e));
        this.canvas.addEventListener('touchend', () => this.stopDrawing());
        this.canvas.addEventListener('touchcancel', () => this.stopDrawing());

        // Prevent default touch behaviors
        this.canvas.addEventListener('touchstart', (e) => e.preventDefault(), { passive: false });
        this.canvas.addEventListener('touchmove', (e) => e.preventDefault(), { passive: false });
    }

    startDrawing(e) {
        this.isDrawing = true;
        const pos = this.getPosition(e);
        this.ctx.beginPath();
        this.ctx.moveTo(pos.x, pos.y);
    }

    draw(e) {
        if (!this.isDrawing) return;

        const pos = this.getPosition(e);

        if (this.drawMode === 'pen') {
            this.ctx.strokeStyle = this.penColor;
            this.ctx.lineWidth = this.penSize;
            this.ctx.lineCap = 'round';
            this.ctx.lineJoin = 'round';
            this.ctx.globalCompositeOperation = 'source-over';
            this.ctx.lineTo(pos.x, pos.y);
            this.ctx.stroke();
        } else if (this.drawMode === 'eraser') {
            this.ctx.clearRect(pos.x - this.eraserSize / 2, pos.y - this.eraserSize / 2, this.eraserSize, this.eraserSize);
        }
    }

    stopDrawing() {
        this.isDrawing = false;
        this.ctx.closePath();
    }

    getPosition(e) {
        const rect = this.canvas.getBoundingClientRect();
        
        let clientX, clientY;
        if (e.touches) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }

        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }

    setMode(mode) {
        if (mode === 'pen' || mode === 'eraser') {
            this.drawMode = mode;
            this.updateCursor();
        }
    }

    updateCursor() {
        if (this.drawMode === 'pen') {
            this.canvas.style.cursor = 'url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI0IiBmaWxsPSIjMDAwIi8+PC9zdmc+") 12 12, crosshair';
        } else if (this.drawMode === 'eraser') {
            this.canvas.style.cursor = 'url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB4PSI0IiB5PSI0IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIGZpbGw9IiNGRkYiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+") 12 12, auto';
        }
    }

    setPenColor(color) {
        this.penColor = color;
    }

    setPenSize(size) {
        this.penSize = size;
    }

    setEraserSize(size) {
        this.eraserSize = size;
    }

    clear() {
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    getImageData() {
        /**
         * Convert canvas to blob for upload
         * Returns a Promise that resolves with the blob
         */
        return new Promise(resolve => {
            this.canvas.toBlob(resolve, 'image/png');
        });
    }
}

// Initialize canvas
const canvas = new DrawingCanvas();
