document.addEventListener("DOMContentLoaded", function() {
    const historyDiv = document.querySelector("#history");
    const missionDiv = document.querySelector("#mission");

    historyDiv.addEventListener("click", function(event) {
        const fullDescription = historyDiv.querySelector(".full-description");
        if (fullDescription.style.display === "block") {
            fullDescription.style.display = "none";
        } else {
            fullDescription.style.display = "block";
        }
    });

    missionDiv.addEventListener("click", function(event) {
        const missionFullDescription = missionDiv.querySelector(".mission-full-description");
        if (missionFullDescription.style.display === "block") {
            missionFullDescription.style.display = "none";
        } else {
            missionFullDescription.style.display = "block";
        }
    });
});