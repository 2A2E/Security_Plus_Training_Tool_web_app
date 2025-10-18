// Practice Test UI logic - starts a practice test via the API and reuses quiz flow

document.addEventListener('DOMContentLoaded', function() {
    const questionCountSelect = document.getElementById('question-count');
    const customQuestionsDiv = document.getElementById('custom-questions');
    const customCountInput = document.getElementById('custom-count');
    const timeLimitSelect = document.getElementById('time-limit');
    const startTestBtn = document.getElementById('start-test');
    const resetConfigBtn = document.getElementById('reset-config');
    const presetCards = document.querySelectorAll('.preset-card');

    // Handle custom question count visibility
    questionCountSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customQuestionsDiv.style.display = 'block';
        } else {
            customQuestionsDiv.style.display = 'none';
            updateTimeLimit();
        }
    });

    // Update time limit option label when on auto
    function updateTimeLimit() {
        const value = questionCountSelect.value === 'custom'
            ? parseInt(customCountInput.value || '90', 10)
            : parseInt(questionCountSelect.value, 10);
        const timePerQuestion = 1.25; // 1:15
        if (timeLimitSelect.value === 'auto' && !isNaN(value)) {
            const totalMinutes = Math.ceil(value * timePerQuestion);
            const opt = timeLimitSelect.querySelector('option[value="auto"]');
            if (opt) opt.textContent = `Auto (${totalMinutes} minutes)`;
        }
    }

    customCountInput?.addEventListener('input', function() {
        if (questionCountSelect.value === 'custom') updateTimeLimit();
    });

    // Reset configuration to defaults
    resetConfigBtn.addEventListener('click', function() {
        questionCountSelect.value = '90';
        timeLimitSelect.value = '90';
        const difficulty = document.getElementById('difficulty');
        if (difficulty) difficulty.value = 'mixed';

        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });

        customQuestionsDiv.style.display = 'none';
        updateTimeLimit();
    });

    // Start test with current configuration
    startTestBtn.addEventListener('click', async function() {
        const cfg = getConfig();
        await startPracticeTest(cfg);
    });

    // Preset cards
    presetCards.forEach(card => {
        card.addEventListener('click', function() {
            applyPreset(this.dataset.preset);
        });
    });

    function getConfig() {
        const qCount = questionCountSelect.value === 'custom'
            ? parseInt(customCountInput.value || '90', 10)
            : parseInt(questionCountSelect.value, 10);

        const selectedSections = [];
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            if (checkbox.id.startsWith('chapter') && checkbox.checked) {
                const num = parseInt(checkbox.id.replace('chapter', ''), 10);
                if (!isNaN(num)) selectedSections.push(num);
            }
        });

        const difficulty = document.getElementById('difficulty')?.value;
        return {
            question_count: qCount,
            sections: selectedSections.length ? selectedSections : undefined,
            // Do not send difficulty if 'mixed' to avoid filtering out questions server-side
            difficulty: (difficulty && difficulty.toLowerCase() !== 'mixed') ? difficulty : undefined
        };
    }

    function applyPreset(preset) {
        switch (preset) {
            case 'full-exam':
                questionCountSelect.value = '90';
                timeLimitSelect.value = '90';
                const difficulty = document.getElementById('difficulty');
                if (difficulty) difficulty.value = 'mixed';
                break;
            case 'quick-practice':
                questionCountSelect.value = '20';
                timeLimitSelect.value = 'auto';
                break;
            case 'weak-areas':
                // AI analysis not implemented; behave like a mid-size mixed set
                questionCountSelect.value = '40';
                timeLimitSelect.value = 'auto';
                break;
            case 'chapter-review':
                // No special change beyond letting user toggle chapters
                break;
        }
        updateTimeLimit();
    }

    async function startPracticeTest(config) {
        try {
            const response = await fetch('/api/quiz/create/practice-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await response.json();
            if (data && data.success && data.quiz_id) {
                // Build URL with timer parameters
                const showTimer = document.getElementById('show-timer')?.checked || false;
                const timeLimitSelect = document.getElementById('time-limit');
                let timeInSeconds = 5400; // Default 90 minutes
                
                if (timeLimitSelect) {
                    const timeValue = timeLimitSelect.value;
                    if (timeValue === 'unlimited') {
                        timeInSeconds = 999999;
                    } else if (timeValue !== 'auto') {
                        timeInSeconds = parseInt(timeValue) * 60;
                    } else {
                        // Auto: 1.25 minutes per question
                        timeInSeconds = Math.ceil(config.question_count * 1.25 * 60);
                    }
                }
                
                const url = `/quiz/${data.quiz_id}/question/1?timer=${showTimer}&time_limit=${timeInSeconds}`;
                sessionStorage.removeItem('quiz_timer'); // Clear any old timer
                sessionStorage.removeItem('quiz_timer_start');
                window.location.href = url;
                return;
            }
            // Show detailed error from API
            const errorMsg = data?.error || 'Failed to start practice test.';
            console.error('Practice test creation failed:', data);
            alert(`Error: ${errorMsg}\n\nCheck browser console for details.`);
        } catch (err) {
            console.error('Network error:', err);
            alert(`Network error: ${err.message}\n\nCheck browser console for details.`);
        }
    }

    // Initialize defaults on load
    // Set default to 90 questions and update time label
    if (questionCountSelect.value !== '90') questionCountSelect.value = '90';
    updateTimeLimit();
});


