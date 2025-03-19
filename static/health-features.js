/**
 * Dr.ai - Health Features Module (Tailwind CSS version)
 * Additional features specific to the health assistant functionality
 */

const draiHealth = (function() {
    // DOM References
    let sidebar;
    let healthFeaturesContainer;
    
    /**
     * Initialize the health features
     */
    function init() {
        sidebar = document.getElementById('sidebar');
        
        // Wait a short time to ensure DOM is fully loaded
        setTimeout(() => {
            // Create health features
            createHealthFeatures();
            createHealthTopics();
            
            // Attach event listeners
            setupEventListeners();
        }, 100);
    }
    
    /**
     * Create health features section
     */
    function createHealthFeatures() {
        // Create symptom checker button
        const symptomCheckerBtn = document.createElement('button');
        symptomCheckerBtn.className = 'flex items-center gap-2.5 py-3 px-4 bg-white/5 border border-white/10 rounded-lg text-white font-medium text-sm transition-all duration-200 text-left hover:bg-white/10 hover:-translate-y-0.5';
        symptomCheckerBtn.setAttribute('id', 'symptom-checker');
        symptomCheckerBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
                <path d="M9 12H15M12 9V15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Symptom Checker</span>
        `;
        
        // Create medication reminder button
        const medicationReminderBtn = document.createElement('button');
        medicationReminderBtn.className = 'flex items-center gap-2.5 py-3 px-4 bg-white/5 border border-white/10 rounded-lg text-white font-medium text-sm transition-all duration-200 text-left hover:bg-white/10 hover:-translate-y-0.5';
        medicationReminderBtn.setAttribute('id', 'medication-reminder');
        medicationReminderBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
                <path d="M12 8V12L15 15M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Medication Reminder</span>
        `;
        
        // Create health tips button
        const healthTipsBtn = document.createElement('button');
        healthTipsBtn.className = 'flex items-center gap-2.5 py-3 px-4 bg-white/5 border border-white/10 rounded-lg text-white font-medium text-sm transition-all duration-200 text-left hover:bg-white/10 hover:-translate-y-0.5';
        healthTipsBtn.setAttribute('id', 'health-tips');
        healthTipsBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
                <path d="M12 16V12M12 8H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Health Tips</span>
        `;
        
        // Create container for health features
        healthFeaturesContainer = document.createElement('div');
        healthFeaturesContainer.className = 'flex flex-col gap-2 my-4';
        healthFeaturesContainer.id = 'health-features';
        healthFeaturesContainer.appendChild(symptomCheckerBtn);
        healthFeaturesContainer.appendChild(medicationReminderBtn);
        healthFeaturesContainer.appendChild(healthTipsBtn);
        
        // Find the right insertion point - after the subtitle
        const sidebarSubtitle = sidebar.querySelector('h5');
        if (sidebarSubtitle) {
            sidebar.insertBefore(healthFeaturesContainer, sidebarSubtitle.nextSibling);
        } else {
            // Fallback - insert at the beginning of sidebar
            sidebar.insertBefore(healthFeaturesContainer, sidebar.firstChild.nextSibling);
        }
    }
    
    /**
     * Create health topics section
     */
    function createHealthTopics() {
        // Create health topics container
        const topicsContainer = document.createElement('div');
        topicsContainer.className = 'flex flex-col gap-2 my-4';
        topicsContainer.id = 'health-topics';
        
        // Add header
        const topicsHeader = document.createElement('div');
        topicsHeader.className = 'text-xs text-white/50 uppercase tracking-wider mb-1';
        topicsHeader.textContent = 'Common Health Topics';
        topicsContainer.appendChild(topicsHeader);
        
        // Add topics items container
        const topicsItems = document.createElement('div');
        topicsItems.className = 'flex flex-col gap-1.5';
        
        // Add individual topic items
        const topics = [
            { text: 'Heart Health', prompt: 'Tell me about heart health' },
            { text: 'Mental Health', prompt: 'Mental health resources' },
            { text: 'Nutrition', prompt: 'Diet and nutrition basics' },
            { text: 'Fitness', prompt: 'Exercise recommendations' },
            { text: 'Sleep', prompt: 'Sleep improvement tips' }
        ];
        
        topics.forEach(topic => {
            const topicItem = document.createElement('button');
            topicItem.className = 'health-topic-item bg-indigo-600/10 border border-indigo-600/20 rounded-md py-2 px-3 text-white/90 text-sm text-left transition-all duration-200 hover:bg-indigo-600/20 hover:-translate-y-0.5';
            topicItem.textContent = topic.text;
            topicItem.setAttribute('data-prompt', topic.prompt);
            topicsItems.appendChild(topicItem);
        });
        
        topicsContainer.appendChild(topicsItems);
        
        // Insert after health features
        if (healthFeaturesContainer && healthFeaturesContainer.parentNode) {
            sidebar.insertBefore(topicsContainer, healthFeaturesContainer.nextSibling);
        } else {
            // Fallback if healthFeaturesContainer isn't in the DOM yet
            const historyContainer = sidebar.querySelector('.history-container');
            if (historyContainer) {
                sidebar.insertBefore(topicsContainer, historyContainer);
            } else {
                sidebar.appendChild(topicsContainer);
            }
        }
    }
    
    /**
     * Setup event listeners for health features
     */
    function setupEventListeners() {
        // Symptom checker
        const symptomChecker = document.getElementById('symptom-checker');
        if (symptomChecker) {
            symptomChecker.addEventListener('click', function() {
                draiApp.sendPrompt("I'd like to use the symptom checker. What symptoms are you experiencing?");
                closeMenuOnMobile();
            });
        }
        
        // Medication reminder
        const medicationReminder = document.getElementById('medication-reminder');
        if (medicationReminder) {
            medicationReminder.addEventListener('click', function() {
                draiApp.sendPrompt("Can you help me set up medication reminders?");
                closeMenuOnMobile();
            });
        }
        
        // Health tips
        const healthTips = document.getElementById('health-tips');
        if (healthTips) {
            healthTips.addEventListener('click', function() {
                draiApp.sendPrompt("Share a daily health tip with me");
                closeMenuOnMobile();
            });
        }
        
        // Topic items
        document.querySelectorAll('.health-topic-item').forEach(item => {
            item.addEventListener('click', function() {
                const prompt = this.getAttribute('data-prompt');
                if (prompt && typeof draiApp.sendPrompt === 'function') {
                    draiApp.sendPrompt(prompt);
                    closeMenuOnMobile();
                } else {
                    console.error('Either prompt is missing or draiApp.sendPrompt is not available');
                }
            });
        });
    }
    
    /**
     * Close menu on mobile devices
     */
    function closeMenuOnMobile() {
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('sidebar-open');
            const overlay = document.getElementById('overlay');
            if (overlay) overlay.classList.remove('active');
        }
    }
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', init);
    
    // Public API
    return {};
})();