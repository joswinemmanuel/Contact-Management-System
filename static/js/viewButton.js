function openDetailsModal(contactId) {
    const modal = document.getElementById(`detailsModal-${contactId}`);
    modal.style.display = "block";
}

function closeDetailsModal(contactId) {
    const modal = document.getElementById(`detailsModal-${contactId}`);
    modal.style.display = "none";
}