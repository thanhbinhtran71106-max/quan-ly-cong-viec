document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const htmlElement = document.documentElement;

    // Check for saved theme preference or use dark as default
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    function setTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-moon-stars-fill');
            themeIcon.classList.add('bi-sun-fill');
            if(themeText) themeText.textContent = 'Light Mode';
        } else {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-stars-fill');
            if(themeText) themeText.textContent = 'Dark Mode';
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            setTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });
    }

    // Sidebar Toggle (Mobile)
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    const mobileSidebarToggleBtn = document.getElementById('mobileSidebarToggle');
    const sidebar = document.getElementById('sidebar');

    function toggleSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
    
    if (mobileSidebarToggleBtn) {
        mobileSidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && e.target !== sidebarToggleBtn && e.target !== mobileSidebarToggleBtn) {
                sidebar.classList.remove('show');
            }
        }
    });
});
