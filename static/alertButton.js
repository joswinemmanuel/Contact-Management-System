document.addEventListener('DOMContentLoaded', () => {
    const alert = document.querySelector('.alert.fade');

    if (alert) {
        setTimeout(() => {
            alert.classList.add('show');
        }, 100);
    }

    const closeButton = alert?.querySelector('.btn-close');
    closeButton?.addEventListener('click', () => {
        alert.classList.remove('show');
        setTimeout(() => {
            alert.remove();
        }, 300);
    });
});