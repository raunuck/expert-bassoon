document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation Routing ---
    const navLinks = document.querySelectorAll('.nav-link');
    const views = document.querySelectorAll('.view');

    function switchView(targetId) {
        // Update nav links
        navLinks.forEach(link => {
            if (link.getAttribute('data-target') === targetId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Update views
        views.forEach(view => {
            if (view.id === targetId) {
                view.classList.remove('hidden');
                // Small animation reset hack
                view.style.animation = 'none';
                view.offsetHeight; /* trigger reflow */
                view.style.animation = null; 
            } else {
                view.classList.add('hidden');
            }
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            switchView(targetId);
        });
    });

    // --- Global State ---
    const notesInput = document.getElementById('notes-input');

    // --- Notes Upload ---
    const pdfUpload = document.getElementById('pdf-upload');
    const fileNameDisplay = document.getElementById('file-name');

    // Make sure marked.js is configured for safe rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({ breaks: true, gfm: true });
    }

    pdfUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        fileNameDisplay.innerText = file.name;
        notesInput.value = "Extracting text from PDF, please wait...";

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload-pdf', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to extract text from PDF');
            }

            const data = await response.json();
            notesInput.value = data.text;
        } catch (error) {
            alert(`Error: ${error.message}`);
            notesInput.value = "";
            fileNameDisplay.innerText = 'No file selected';
            pdfUpload.value = '';
        }
    });

    // --- Summary Feature ---
    const btnSummarize = document.getElementById('btn-summarize');
    const summaryTypeSelect = document.getElementById('summary-type');
    const summaryLoading = document.getElementById('summary-loading');
    const summaryResults = document.getElementById('summary-results');

    btnSummarize.addEventListener('click', async () => {
        const notes = notesInput.value;
        const summaryType = summaryTypeSelect.value;
        if (!notes.trim()) {
            alert('Please paste some notes or upload a PDF in the Notes tab first!');
            switchView('view-notes');
            return;
        }

        summaryResults.classList.add('hidden');
        summaryLoading.classList.remove('hidden');

        try {
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes, summary_type: summaryType })
            });

            if (!response.ok) throw new Error('Failed to generate summary');
            const data = await response.json();
            
            summaryResults.innerHTML = marked.parse(data.summary);
            summaryLoading.classList.add('hidden');
            summaryResults.classList.remove('hidden');
        } catch (error) {
            summaryLoading.classList.add('hidden');
            alert(`Error: ${error.message}`);
        }
    });

    // --- Quiz Feature ---
    const btnQuiz = document.getElementById('btn-quiz');
    const quizLoading = document.getElementById('quiz-loading');
    const quizResults = document.getElementById('quiz-results');
    let currentQuizData = null;

    btnQuiz.addEventListener('click', async () => {
        const notes = notesInput.value;
        if (!notes.trim()) {
            alert('Please paste some notes or upload a PDF in the Notes tab first!');
            switchView('view-notes');
            return;
        }

        quizResults.classList.add('hidden');
        quizLoading.classList.remove('hidden');

        try {
            const response = await fetch('/api/generate-quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes })
            });

            if (!response.ok) throw new Error('Failed to generate quiz');
            const data = await response.json();
            
            renderQuiz(data);
            quizLoading.classList.add('hidden');
            quizResults.classList.remove('hidden');
        } catch (error) {
            quizLoading.classList.add('hidden');
            alert(`Error: ${error.message}`);
        }
    });

    function renderQuiz(data) {
        currentQuizData = data.questions;
        
        let html = `<div class="quiz-container">`;

        data.questions.forEach((q, qIndex) => {
            html += `
                <div class="quiz-question" id="q-${qIndex}">
                    <h3>${qIndex + 1}. ${q.question}</h3>
                    <div class="quiz-options">
            `;
            q.options.forEach((opt, optIndex) => {
                html += `
                    <div class="quiz-option" data-qindex="${qIndex}" data-optval="${opt.replace(/"/g, '&quot;')}">
                        ${opt}
                    </div>
                `;
            });
            html += `</div></div>`;
        });

        html += `
                <button id="btn-submit-quiz" class="primary-btn quiz-submit-btn">Submit Answers</button>
                <div id="quiz-score" class="quiz-score hidden"></div>
            </div>
        `;

        quizResults.innerHTML = html;

        // Add event listeners for quiz options
        const options = quizResults.querySelectorAll('.quiz-option');
        options.forEach(opt => {
            opt.addEventListener('click', function() {
                const qIndex = this.getAttribute('data-qindex');
                const siblings = document.querySelectorAll(`.quiz-option[data-qindex="${qIndex}"]`);
                siblings.forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
            });
        });

        // Add event listener for submit button
        const submitBtn = document.getElementById('btn-submit-quiz');
        if (submitBtn) {
            submitBtn.addEventListener('click', evaluateQuiz);
        }
    }

    function evaluateQuiz() {
        if (!currentQuizData) return;
        let score = 0;
        const total = currentQuizData.length;

        currentQuizData.forEach((q, qIndex) => {
            const selectedOpt = document.querySelector(`.quiz-option[data-qindex="${qIndex}"].selected`);
            const allOpts = document.querySelectorAll(`.quiz-option[data-qindex="${qIndex}"]`);
            
            if (selectedOpt) {
                const userVal = selectedOpt.getAttribute('data-optval');
                if (userVal === q.correct_answer) {
                    score++;
                    selectedOpt.classList.add('correct');
                } else {
                    selectedOpt.classList.add('wrong');
                    allOpts.forEach(opt => {
                        if (opt.getAttribute('data-optval') === q.correct_answer) opt.classList.add('correct');
                    });
                }
            } else {
                allOpts.forEach(opt => {
                    if (opt.getAttribute('data-optval') === q.correct_answer) opt.classList.add('correct');
                });
            }
            allOpts.forEach(opt => opt.style.pointerEvents = 'none');
        });

        const scoreDiv = document.getElementById('quiz-score');
        scoreDiv.innerHTML = `You scored ${score} out of ${total}!`;
        scoreDiv.classList.remove('hidden');
        document.getElementById('btn-submit-quiz').classList.add('hidden');
    }

    // --- Chat Feature ---
    const chatHistoryEl = document.getElementById('chat-history');
    const chatInput = document.getElementById('chat-input');
    const btnSendChat = document.getElementById('btn-send-chat');
    let chatHistory = [];

    function appendChatMessage(role, text) {
        const div = document.createElement('div');
        div.className = `chat-message ${role === 'user' ? 'user-message' : 'ai-message'}`;
        div.innerHTML = role === 'model' ? marked.parse(text) : text;
        chatHistoryEl.appendChild(div);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

    async function sendChatMessage() {
        const notes = notesInput.value;
        const text = chatInput.value.trim();
        
        if (!notes.trim()) {
            alert('Please paste some notes or upload a PDF in the Notes tab first!');
            switchView('view-notes');
            return;
        }
        
        if (!text) return;

        appendChatMessage('user', text);
        chatHistory.push({ role: 'user', text: text });
        chatInput.value = '';

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-message ai-message';
        loadingDiv.innerText = 'Thinking...';
        loadingDiv.id = 'chat-loading';
        chatHistoryEl.appendChild(loadingDiv);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    notes: notes,
                    chat_history: chatHistory
                })
            });

            if (!response.ok) throw new Error('Failed to get response');
            const data = await response.json();
            
            document.getElementById('chat-loading').remove();
            appendChatMessage('model', data.reply);
            chatHistory.push({ role: 'model', text: data.reply });

        } catch (error) {
            document.getElementById('chat-loading').remove();
            appendChatMessage('model', 'Error: ' + error.message);
            chatHistory.pop(); // Remove the user message from memory if request failed
        }
    }

    btnSendChat.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
});
