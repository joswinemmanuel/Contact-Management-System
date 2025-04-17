const input = document.getElementById("profile_picture");
const fileNameDisplay = document.getElementById("file-name");

input.addEventListener("change", function () {
    fileNameDisplay.textContent = this.files[0]?.name || "No file chosen";
});