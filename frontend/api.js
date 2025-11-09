/**
 * API Module
 * Handles all backend API calls with JWT authentication (Phase 12)
 */

const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : `${window.location.origin}/api`;

// ===== AUTH TOKEN MANAGEMENT =====

function getAuthToken() {
    return localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function clearAuthToken() {
    localStorage.removeItem('authToken');
}

function getAuthHeaders() {
    const token = getAuthToken();
    if (!token) {
        return {};
    }
    return {
        'Authorization': `Bearer ${token}`
    };
}

function handleUnauthorized() {
    clearAuthToken();
    localStorage.removeItem('selectedChildId');
    window.location.href = '/login.html';
}

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

    // ===== AUTHENTICATION ENDPOINTS (Phase 12) =====

    static async register(email, password) {
        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Registration failed');
            }

            return await response.json();
        } catch (e) {
            console.error('Error registering:', e);
            throw e;
        }
    }

    static async login(email, password) {
        try {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login failed');
            }

            const data = await response.json();
            setAuthToken(data.access_token);
            return data;
        } catch (e) {
            console.error('Error logging in:', e);
            throw e;
        }
    }

    static async getCurrentUser() {
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) throw new Error('Failed to fetch user');
            return await response.json();
        } catch (e) {
            console.error('Error fetching current user:', e);
            return null;
        }
    }

    // ===== CHILD MANAGEMENT ENDPOINTS (Phase 12) =====

    static async createChild(name, age = null) {
        try {
            const response = await fetch(`${API_BASE}/children`, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, age })
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to create child');
            }

            return await response.json();
        } catch (e) {
            console.error('Error creating child:', e);
            throw e;
        }
    }

    static async getChildren() {
        try {
            const response = await fetch(`${API_BASE}/children`, {
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) throw new Error('Failed to fetch children');
            return await response.json();
        } catch (e) {
            console.error('Error fetching children:', e);
            return { children: [] };
        }
    }

    static async updateChild(childId, name, age = null) {
        try {
            const response = await fetch(`${API_BASE}/children/${childId}`, {
                method: 'PUT',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, age })
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to update child');
            }

            return await response.json();
        } catch (e) {
            console.error('Error updating child:', e);
            throw e;
        }
    }

    static async deleteChild(childId) {
        try {
            const response = await fetch(`${API_BASE}/children/${childId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to delete child');
            }

            return await response.json();
        } catch (e) {
            console.error('Error deleting child:', e);
            throw e;
        }
    }

    // ===== EXISTING ENDPOINTS (updated with auth) =====

    static async getWords() {
        try {
            const response = await fetch(`${API_BASE}/words`, {
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return { words: [] };
            }

            if (!response.ok) throw new Error('Failed to fetch words');
            return await response.json();
        } catch (e) {
            console.error('Error fetching words:', e);
            return { words: [] };
        }
    }

    static async startSession(numWords = null) {
        try {
            const childId = localStorage.getItem('selectedChildId');
            const params = new URLSearchParams();
            if (numWords) params.append('num_words', numWords);
            if (childId) params.append('child_id', childId);
            
            const url = params.toString() 
                ? `${API_BASE}/session/start?${params.toString()}`
                : `${API_BASE}/session/start`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) throw new Error('Failed to start session');
            return await response.json();
        } catch (e) {
            console.error('Error starting session:', e);
            return null;
        }
    }

    static async getNextWord() {
        try {
            const response = await fetch(`${API_BASE}/next-word`, {
                headers: getAuthHeaders()
            });

            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }

            if (!response.ok) throw new Error('Failed to fetch next word');
            return await response.json();
        } catch (e) {
            console.error('Error fetching next word:', e);
            return null;
        }
    }

    static async submitPractice(wordId, spelledWord, drawingBlob, isCorrect) {
        try {
            const formData = new FormData();
            formData.append('word_id', wordId);
            formData.append('spelled_word', spelledWord);
            formData.append('drawing', drawingBlob, 'drawing.png');
            formData.append('is_correct', isCorrect.toString());

            const response = await fetch(`${API_BASE}/practice`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });

            if (response.status === 401) {
                handleUnauthorized();
                return { success: false };
            }

            if (!response.ok) throw new Error('Failed to submit practice');
            return await response.json();
        } catch (e) {
            console.error('Error submitting practice:', e);
            return { success: false };
        }
    }
}
