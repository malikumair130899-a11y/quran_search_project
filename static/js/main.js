// ==========================================
// Global App State and Core Logic
// ==========================================
const app = {
    init: () => {
        app.loadTheme();
        app.setupEventListeners();
        settings.apply();
        bookmarksPanel.load();

        // Only run if the element exists (e.g., on browse.html)
        const grid = document.getElementById('surah-grid');
        if (grid && typeof surahList !== 'undefined') {
            app.renderSurahs();
        }
    },

    loadTheme: () => {
        if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    },

    setupEventListeners: () => {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                document.documentElement.classList.toggle('dark');
                localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
            });
        }

        // Close drawer overlay
        const overlay = document.getElementById('drawer-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => bookmarksPanel.toggle());
        }
    },

    showToast: (msg) => {
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toast-msg');
        if (toast && toastMsg) {
            toastMsg.innerText = msg;
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
        }
    }
};

// ==========================================
// Bookmarks Panel (LocalStorage persistence)
// ==========================================
const bookmarksPanel = {
    items: JSON.parse(localStorage.getItem('quran_bookmarks') || '[]'),

    load: () => {
        const list = document.getElementById('bookmarks-list');
        const count = document.getElementById('nav-bookmark-count');
        
        if (!list) return;

        if (bookmarksPanel.items.length === 0) {
            list.innerHTML = `<div class="text-center py-10 text-gray-400"><p>No bookmarks yet.</p></div>`;
            if (count) count.classList.add('hidden');
            return;
        }

        if (count) {
            count.innerText = bookmarksPanel.items.length;
            count.classList.remove('hidden');
        }

        // Updated template to include a clickable link to the verse
        list.innerHTML = bookmarksPanel.items.map((item, index) => `
            <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700 flex justify-between items-center group">
                <a href="/surah/${item.sid}#ayah-${item.a}" class="flex-grow">
                    <div class="hover:text-brand-600 transition-colors">
                        <span class="font-bold text-sm">Surah ${item.s}</span>
                        <div class="text-xs text-gray-500">Verse ${item.a}</div>
                    </div>
                </a>
                <button onclick="bookmarksPanel.remove(${index})" class="text-red-400 hover:text-red-600 ml-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </button>
            </div>
        `).join('');
    },

    toggle: () => {
        const drawer = document.getElementById('bookmarks-drawer');
        const overlay = document.getElementById('drawer-overlay');
        if (!drawer) return;

        drawer.classList.toggle('translate-x-full');
        if (overlay) overlay.classList.toggle('hidden');
    },

    // Updated to prevent duplicates and handle Surah ID for navigation
    add: (sName, aNum, sId) => {
        // 1. Check if already exists
        const isDuplicate = bookmarksPanel.items.some(item => item.sid === sId && item.a === aNum);
        
        if (isDuplicate) {
            if (typeof app !== 'undefined') app.showToast("Verse already bookmarked");
            return;
        }

        // 2. Add if unique (storing sName for display, sid for links)
        bookmarksPanel.items.push({ s: sName, a: aNum, sid: sId });
        localStorage.setItem('quran_bookmarks', JSON.stringify(bookmarksPanel.items));
        
        bookmarksPanel.load();
        if (typeof app !== 'undefined') app.showToast(`Saved Surah ${sName}:${aNum}`);
    },

    remove: (index) => {
        bookmarksPanel.items.splice(index, 1);
        localStorage.setItem('quran_bookmarks', JSON.stringify(bookmarksPanel.items));
        bookmarksPanel.load();
    }
};

// ==========================================
// Settings Manager
// ==========================================
const settings = {
    arabicSize: localStorage.getItem('arabicSize') || 36,
    translationSize: localStorage.getItem('translationSize') || 18,
    showEnglish: localStorage.getItem('showEnglish') !== 'false',
    showUrdu: localStorage.getItem('showUrdu') !== 'false',

    updateFontSize: (type, val) => {
        if (type === 'arabic') {
            settings.arabicSize = val;
            localStorage.setItem('arabicSize', val);
        } else {
            settings.translationSize = val;
            localStorage.setItem('translationSize', val);
        }
        settings.apply();
    },

    toggleTranslation: (lang, isChecked) => {
        if (lang === 'english') {
            settings.showEnglish = isChecked;
            localStorage.setItem('showEnglish', isChecked);
        } else {
            settings.showUrdu = isChecked;
            localStorage.setItem('showUrdu', isChecked);
        }
        settings.apply();
    },

    apply: () => {
        document.querySelectorAll('.arabic-content').forEach(el => el.style.fontSize = settings.arabicSize + 'px');
        document.querySelectorAll('.translation-content').forEach(el => el.style.fontSize = settings.translationSize + 'px');

        document.querySelectorAll('.translation-english').forEach(el =>
            settings.showEnglish ? el.classList.remove('hidden') : el.classList.add('hidden')
        );
        document.querySelectorAll('.translation-urdu').forEach(el =>
            settings.showUrdu ? el.classList.remove('hidden') : el.classList.add('hidden')
        );
    }
};

const settingsModal = {
    toggle: () => {
        const el = document.getElementById('settings-modal');
        if (el) el.classList.toggle('hidden');
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', app.init);