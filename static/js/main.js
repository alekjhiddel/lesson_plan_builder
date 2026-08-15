/* IEP Lesson Planner - Main JavaScript */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Add smooth transitions to alerts
document.querySelectorAll('.alert').forEach(el => {
    el.style.transition = 'opacity 0.3s, transform 0.3s';
});
