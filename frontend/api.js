/**
 * API Module
 * Handles all backend API calls
 */

const API_BASE = 'http://localhost:8000/api';

class API {
    static async checkHealth() {
        try {
            const response = await fetch(`${API_BASE}/health`);
            return response.ok;
        } catch (e) {
            console.error('API health check failed:', e);
            return false;
        }
    }

    static async getWords() {
        try {
            const response = await fetch(`${API_BASE}/words`);
            if (!response.ok) throw new Error('Failed to fetch words');
            return await response.json();
        } catch (e) {
            console.error('Error fetching words:', e);
            return { words: [] };
        }
    }

    static async getNextWord() {
        try {
            const response = await fetch(`${API_BASE}/next-word`);
            if (!response.ok) throw new Error('Failed to fetch next word');
            return await response.json();
        } catch (e) {
            console.error('Error fetching next word:', e);
            return null;
        }
    }

    static async submitPractice(wordId, spelledWord, drawingBlob) {
        try {
            const formData = new FormData();
            formData.append('word_id', wordId);
            formData.append('spelled_word', spelledWord);
            formData.append('drawing', drawingBlob, 'drawing.png');

            const response = await fetch(`${API_BASE}/practice`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to submit practice');
            return await response.json();
        } catch (e) {
            console.error('Error submitting practice:', e);
            return { success: false };
        }
    }
}
