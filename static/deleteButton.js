function openDeleteModal(contactId) {
    const modal = document.getElementById(`deleteModal-${contactId}`);
    modal.style.display = "block";
}

function closeDeleteModal(contactId) {
    const modal = document.getElementById(`deleteModal-${contactId}`);
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target.classList.contains('modal')) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = "none";
        });
    }
}