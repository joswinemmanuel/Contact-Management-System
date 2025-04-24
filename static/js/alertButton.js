document.addEventListener('DOMContentLoaded', () => {
    const alert = document.querySelector('.alert');

    const closeAlert = () => {
        alert.style.height = alert.scrollHeight + 'px';
        requestAnimationFrame(() => {
            alert.style.height = '0px';
            alert.style.opacity = '0';
            alert.style.paddingTop = '0';
            alert.style.paddingBottom = '0';
            alert.style.marginBottom = '0';
            alert.style.visibility = 'hidden';
        });
        setTimeout(() => {
            alert.remove();
        }, 500);
    };

    if (alert) {

        requestAnimationFrame(() => {
            alert.classList.add('show');
            alert.style.height = alert.scrollHeight + 'px';
        });
        setTimeout(() => {
            closeAlert();
        }, 3000);
    }

    const closeButton = alert?.querySelector('.btn-close');
    closeButton?.addEventListener('click', () => {
        closeAlert();
    });
});

