class ZappyLearn {
    constructor() {
        this.selectedMood = '';
        this.selectedSubject = '';
        this.currentWorksheet = null;
        this.apiBaseUrl = 'https://zappylearn.onrender.com'; // Django backend URL
        this.initEventListeners();
    }

    initEventListeners() {
        // Mood selection
        document.querySelectorAll('.emoji-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectMood(e.target));
        });

        // Subject selection
        document.querySelectorAll('.subject-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectSubject(e.target));
        });

        // Generate worksheet
        document.getElementById('generateBtn').addEventListener('click', () => this.generateWorksheet());

        // Download PDF
        document.getElementById('pdfBtn').addEventListener('click', () => this.downloadPDF());

        // Mood text input
        document.getElementById('moodText').addEventListener('input', (e) => {
            this.selectedMood = e.target.value;
            this.clearEmojiSelection();
        });
    }

    selectMood(button) {
        // Clear text input
        document.getElementById('moodText').value = '';
        
        // Update selection
        document.querySelectorAll('.emoji-btn').forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        this.selectedMood = button.dataset.mood;
    }

    clearEmojiSelection() {
        document.querySelectorAll('.emoji-btn').forEach(btn => btn.classList.remove('selected'));
    }

    selectSubject(button) {
        document.querySelectorAll('.subject-btn').forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        this.selectedSubject = button.dataset.subject;
    }

    async generateWorksheet() {
        if (!this.selectedMood && !document.getElementById('moodText').value) {
            alert('Please tell us how you\'re feeling today! 😊');
            return;
        }

        if (!this.selectedSubject) {
            alert('Please choose a subject to get started! 📚');
            return;
        }

        const mood = this.selectedMood || document.getElementById('moodText').value;
        
        this.showLoading();

        try {
            const response = await this.fetchWorksheet(mood, this.selectedSubject);
            this.currentWorksheet = response;
            this.displayResults(response);
        } catch (error) {
            console.error('Error generating worksheet:', error);
            alert('Oops! Something went wrong. Please try again! 🔄');
        } finally {
            this.hideLoading();
        }
    }

    async fetchWorksheet(mood, subject) {
        const apiUrl = `${this.apiBaseUrl}/generate-worksheet/`;
        
        const requestData = {
            mood: mood,
            subject: subject,
            grade: '5-10'
        };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Log mood analysis for debugging
            if (data.mood_analysis) {
                console.log('Mood Analysis:', data.mood_analysis);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').style.display = 'none';
        document.getElementById('generateBtn').disabled = true;
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('generateBtn').disabled = false;
    }

    displayResults(data) {
        // Update motivation
        document.getElementById('motivationText').textContent = data.motivation;
        document.getElementById('motivationEmoji').textContent = data.motivationEmoji;

        // Create question cards
        const container = document.getElementById('questionsContainer');
        container.innerHTML = '';

        const difficulties = ['easy', 'medium', 'hard'];
        const difficultyIcons = {
            easy: '🟢',
            medium: '🟡', 
            hard: '🔴'
        };

        difficulties.forEach(difficulty => {
            const questionText = data.questions[difficulty];
            if (questionText) {
                const card = document.createElement('div');
                card.className = `question-card ${difficulty}`;
                card.innerHTML = `
                    <div class="difficulty-badge">
                        ${difficultyIcons[difficulty]} ${difficulty.toUpperCase()}
                    </div>
                    <div class="question-text">${questionText}</div>
                `;
                container.appendChild(card);
            }
        });

        // Show results with animation
        document.getElementById('results').style.display = 'block';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    async downloadPDF() {
        if (!this.currentWorksheet) {
            alert('No worksheet to download! Please generate one first.');
            return;
        }

        try {
            // Show loading state
            const pdfBtn = document.getElementById('pdfBtn');
            const originalText = pdfBtn.innerHTML;
            pdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
            pdfBtn.disabled = true;

            // Prepare data for PDF generation
            const pdfData = {
                worksheet_id: this.currentWorksheet.worksheet_id,
                mood: this.selectedMood || document.getElementById('moodText').value,
                subject: this.selectedSubject,
                motivation: this.currentWorksheet.motivation,
                motivationEmoji: this.currentWorksheet.motivationEmoji,
                questions: this.currentWorksheet.questions
            };

            // Generate PDF
            const response = await fetch(`${this.apiBaseUrl}/generate-pdf/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pdfData)
            });

            if (response.ok) {
                // Get filename from response headers
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'ZappyLearn_Worksheet.pdf';
                if (contentDisposition) {
                    const matches = contentDisposition.match(/filename="([^"]+)"/);
                    if (matches && matches[1]) {
                        filename = matches[1];
                    }
                }

                // Download the PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                // Show success message
                this.showSuccessMessage('PDF downloaded successfully! 📄');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.message || 'PDF generation failed');
            }

            // Restore button state
            pdfBtn.innerHTML = originalText;
            pdfBtn.disabled = false;

        } catch (error) {
            console.error('PDF Error:', error);
            alert('Sorry, PDF generation failed. Please try again! 📄');
            
            // Restore button state
            const pdfBtn = document.getElementById('pdfBtn');
            pdfBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF Worksheet';
            pdfBtn.disabled = false;
        }
    }

    showSuccessMessage(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Health check method to verify backend connection
    async checkBackendHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health/`);
            const data = await response.json();
            console.log('Backend health:', data);
            return data.status === 'healthy';
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .success-notification {
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
`;
document.head.appendChild(style);

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    const app = new ZappyLearn();
    
    // Check backend health on startup
    const isHealthy = await app.checkBackendHealth();
    if (!isHealthy) {
        console.warn('Backend is not responding. Please make sure the Django server is running.');
    }
});