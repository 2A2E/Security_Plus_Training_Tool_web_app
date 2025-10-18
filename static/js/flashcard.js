/**
 * Flashcard Manager - Handles flashcard navigation, flip animations, and mode switching
 */
class FlashcardManager {
    constructor(options) {
        this.sessionId = options.sessionId;
        this.currentCard = options.currentCard;
        this.totalCards = options.totalCards;
        this.sectionTitle = options.sectionTitle;
        this.initialCard = options.initialCard;
        
        // State management
        this.isFlipped = false;
        this.viewMode = 'single'; // 'single' or 'scroll'
        this.allCards = [];
        this.currentCardIndex = this.currentCard - 1;
        
        // Pagination state for scroll mode
        this.currentPage = 1;
        this.totalPages = 1;
        this.perPage = 50;
        
        // DOM elements
        this.mainFlashcard = document.getElementById('main-flashcard');
        this.flipBtn = document.getElementById('flip-btn');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.singleModeBtn = document.getElementById('single-mode-btn');
        this.scrollModeBtn = document.getElementById('scroll-mode-btn');
        this.singleCardMode = document.getElementById('single-card-mode');
        this.scrollMode = document.getElementById('scroll-mode');
        this.flashcardsList = document.getElementById('flashcards-list');
        this.cardCounter = document.querySelector('.card-counter');
        
        // Bind methods
        this.handleFlip = this.handleFlip.bind(this);
        this.handleNavigation = this.handleNavigation.bind(this);
        this.handleModeSwitch = this.handleModeSwitch.bind(this);
        this.handleKeyboard = this.handleKeyboard.bind(this);
    }
    
    init() {
        this.setupEventListeners();
        this.loadAllCards();
        this.updateCardDisplay();
    }
    
    setupEventListeners() {
        // Flip button
        if (this.flipBtn) {
            this.flipBtn.addEventListener('click', this.handleFlip);
        }
        
        // Navigation buttons
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.handleNavigation('previous'));
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.handleNavigation('next'));
        }
        
        // Mode toggle buttons
        if (this.singleModeBtn) {
            this.singleModeBtn.addEventListener('click', () => this.handleModeSwitch('single'));
        }
        if (this.scrollModeBtn) {
            this.scrollModeBtn.addEventListener('click', () => this.handleModeSwitch('scroll'));
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboard);
        
        // Card click to flip
        if (this.mainFlashcard) {
            this.mainFlashcard.addEventListener('click', this.handleFlip);
        }
    }
    
    async loadAllCards(page = 1) {
        try {
            const response = await fetch(`/api/flashcards/${this.sessionId}/all?page=${page}&per_page=${this.perPage}`);
            const data = await response.json();
            
            if (data.success) {
                this.allCards = data.flashcards;
                this.currentPage = data.pagination.current_page;
                this.totalPages = data.pagination.total_pages;
                this.totalCards = data.pagination.total_cards;
                this.perPage = data.pagination.per_page;
                
                this.renderScrollMode();
                this.updatePaginationControls();
            } else {
                console.error('Failed to load cards:', data.error);
            }
        } catch (error) {
            console.error('Error loading cards:', error);
        }
    }
    
    async handleNavigation(direction) {
        try {
            let newCardNumber = this.currentCard;
            
            if (direction === 'next' && this.currentCard < this.totalCards) {
                newCardNumber = this.currentCard + 1;
            } else if (direction === 'previous' && this.currentCard > 1) {
                newCardNumber = this.currentCard - 1;
            } else {
                return;
            }
            
            const response = await fetch(`/api/flashcards/${this.sessionId}/card/${newCardNumber}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentCard = data.flashcard.card_number;
                this.currentCardIndex = this.currentCard - 1;
                this.updateCardContent(data.flashcard);
                this.updateNavigationButtons();
                this.resetFlipState();
            } else {
                console.error('Navigation failed:', data.error);
            }
        } catch (error) {
            console.error('Error navigating:', error);
        }
    }
    
    async setCurrentCard(cardNumber) {
        try {
            const response = await fetch(`/api/flashcards/${this.sessionId}/card/${cardNumber}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentCard = data.flashcard.card_number;
                this.currentCardIndex = this.currentCard - 1;
                this.updateCardContent(data.flashcard);
                this.updateNavigationButtons();
                this.resetFlipState();
            } else {
                console.error('Set card failed:', data.error);
            }
        } catch (error) {
            console.error('Error setting card:', error);
        }
    }
    
    handleFlip() {
        if (this.mainFlashcard) {
            this.mainFlashcard.classList.toggle('flipped');
            this.isFlipped = !this.isFlipped;
        }
    }
    
    handleModeSwitch(mode) {
        if (mode === this.viewMode) return;
        
        this.viewMode = mode;
        
        // Update button states
        this.singleModeBtn.classList.toggle('active', mode === 'single');
        this.scrollModeBtn.classList.toggle('active', mode === 'scroll');
        
        // Show/hide appropriate mode
        this.singleCardMode.style.display = mode === 'single' ? 'block' : 'none';
        this.scrollMode.style.display = mode === 'scroll' ? 'block' : 'none';
        // Show counter only in single-card mode
        if (this.cardCounter) {
            this.cardCounter.style.display = mode === 'single' ? 'flex' : 'none';
        }
        
        // Update scroll mode if needed
        if (mode === 'scroll') {
            if (this.allCards.length === 0) {
                this.loadAllCards(1);
            } else {
                this.renderScrollMode();
                this.updatePaginationControls();
            }
        }
    }
    
    handleKeyboard(event) {
        if (this.viewMode !== 'single') return;
        
        switch (event.code) {
            case 'ArrowLeft':
                event.preventDefault();
                if (!this.prevBtn.disabled) {
                    this.handleNavigation('previous');
                }
                break;
            case 'ArrowRight':
                event.preventDefault();
                if (!this.nextBtn.disabled) {
                    this.handleNavigation('next');
                }
                break;
            case 'Space':
                event.preventDefault();
                this.handleFlip();
                break;
        }
    }
    
    updateCardContent(card) {
        // Update front text
        const frontText = document.getElementById('card-front-text');
        if (frontText) {
            frontText.textContent = card.front;
        }
        
        // Update back text
        const backText = document.getElementById('card-back-text');
        if (backText) {
            backText.textContent = card.back;
        }
        
        // Update category
        const categoryElements = document.querySelectorAll('.card-category');
        categoryElements.forEach(el => {
            el.textContent = card.category;
        });
        
        // Update card counter
        if (this.cardCounter) {
            const currentCardSpan = this.cardCounter.querySelector('.current-card');
            const totalCardsSpan = this.cardCounter.querySelector('.total-cards');
            if (currentCardSpan) currentCardSpan.textContent = card.card_number;
            if (totalCardsSpan) totalCardsSpan.textContent = card.total_cards;
        }
    }
    
    updateNavigationButtons() {
        this.prevBtn.disabled = this.currentCard <= 1;
        this.nextBtn.disabled = this.currentCard >= this.totalCards;
    }
    
    resetFlipState() {
        this.mainFlashcard.classList.remove('flipped');
        this.isFlipped = false;
    }
    
    updateCardDisplay() {
        // Update initial card content
        this.updateCardContent(this.initialCard);
        this.updateNavigationButtons();
    }
    
    renderScrollMode() {
        if (!this.flashcardsList || this.allCards.length === 0) return;
        
        this.flashcardsList.innerHTML = '';
        
        this.allCards.forEach((card, index) => {
            const cardElement = this.createScrollCard(card, card.card_number);
            this.flashcardsList.appendChild(cardElement);
        });
    }
    
    updatePaginationControls() {
        const paginationContainer = document.getElementById('pagination-controls');
        const paginationBottom = document.getElementById('pagination-controls-bottom');
        
        if (!paginationContainer || !paginationBottom) return;
        
        // Clear both containers
        paginationContainer.innerHTML = '';
        paginationBottom.innerHTML = '';
        
        if (this.totalPages <= 1) {
            paginationContainer.style.display = 'none';
            paginationBottom.style.display = 'none';
            return;
        }
        
        paginationContainer.style.display = 'flex';
        paginationBottom.style.display = 'flex';
        
        // Create pagination controls
        const createPaginationControls = (container) => {
            // Previous button
            const prevBtn = document.createElement('button');
            prevBtn.className = 'pagination-btn';
            prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i> Previous';
            prevBtn.disabled = !this.currentPage || this.currentPage <= 1;
            prevBtn.addEventListener('click', () => this.loadAllCards(this.currentPage - 1));
            container.appendChild(prevBtn);
            
            // Page info
            const pageInfo = document.createElement('span');
            pageInfo.className = 'pagination-info';
            pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages} (${this.totalCards} total cards)`;
            container.appendChild(pageInfo);
            
            // Next button
            const nextBtn = document.createElement('button');
            nextBtn.className = 'pagination-btn';
            nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
            nextBtn.disabled = !this.currentPage || this.currentPage >= this.totalPages;
            nextBtn.addEventListener('click', () => this.loadAllCards(this.currentPage + 1));
            container.appendChild(nextBtn);
        };
        
        createPaginationControls(paginationContainer);
        createPaginationControls(paginationBottom);
    }
    
    async handlePageChange(page) {
        await this.loadAllCards(page);
    }
    
    createScrollCard(card, cardNumber) {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'scroll-flashcard';
        cardDiv.dataset.cardNumber = cardNumber;
        
        cardDiv.innerHTML = `
            <div class="scroll-card-header">
                <span class="card-number">Card ${cardNumber}</span>
                <span class="card-category">${card.category}</span>
                <span class="card-difficulty ${card.difficulty.toLowerCase()}">${card.difficulty}</span>
            </div>
            <div class="scroll-card-content">
                <div class="scroll-card-side front">
                    <div class="scroll-card-text">${card.front}</div>
                    <div class="scroll-card-hint">
                        <i class="fas fa-lightbulb"></i>
                        <span>Click to reveal answer</span>
                    </div>
                </div>
                <div class="scroll-card-side back">
                    <div class="scroll-card-text">${card.back}</div>
                </div>
            </div>
        `;
        
        // Add click handler for flip
        cardDiv.addEventListener('click', () => {
            cardDiv.classList.toggle('flipped');
        });
        
        return cardDiv;
    }
    
    // Public methods for external use
    getCurrentCard() {
        return this.currentCard;
    }
    
    getTotalCards() {
        return this.totalCards;
    }
    
    getViewMode() {
        return this.viewMode;
    }
    
    destroy() {
        // Clean up event listeners
        document.removeEventListener('keydown', this.handleKeyboard);
    }
}

// Utility functions
function formatCardText(text) {
    // Basic text formatting for better display
    return text.replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardManager;
}
