// ===== Sidebar Toggle =====
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const toggleBtn = document.getElementById('sidebarToggle');

if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

// ===== Live Clock =====
function updateClock() {
    const el = document.getElementById('currentTime');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleTimeString('vi-VN', {
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    }
}
updateClock();
setInterval(updateClock, 1000);

// ===== Auto-dismiss alerts =====
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
    }, 5000);
});

// ===== Animate stat cards on load =====
document.querySelectorAll('.stat-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
        card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 100 + i * 80);
});

// ===== Animate cards =====
document.querySelectorAll('.card-glass').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(15px)';
    setTimeout(() => {
        card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 200 + i * 60);
});

// ===== Animate stat numbers =====
document.querySelectorAll('.stat-value').forEach(el => {
    const target = parseInt(el.textContent) || 0;
    if (target === 0) return;
    let current = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current >= target) clearInterval(timer);
    }, 30);
});

// ===== Confirm delete with nicer UX =====
document.querySelectorAll('form[onsubmit]').forEach(form => {
    form.addEventListener('submit', function(e) {
        // Already handled by inline onsubmit
    });
});

// ===== Mobile sidebar =====
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
            sidebar.classList.remove('mobile-open');
        }
    }
});
if (toggleBtn && window.innerWidth <= 768) {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
    });
}
