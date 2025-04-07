// You can put interactivity here (e.g., dropdowns, alerts, or nav toggles)

document.addEventListener("DOMContentLoaded", () => {
    console.log("School System JS Loaded");
});


document.addEventListener("DOMContentLoaded", function () {
    const processBtn = document.getElementById("process-btn");

    if (processBtn) {
        processBtn.addEventListener("click", async function () {
            const lessonId = processBtn.dataset.lessonId;
            const url = `http://localhost:8000/api/lessons/${lessonId}/process/`;
            processBtn.disabled = true;
            processBtn.innerText = "⏳ Processing...";

            try {
                const response = await fetch(url, {
                    method: "GET",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                });

                const data = await response.json();

                if (response.ok) {
                    alert("✅ " + data.message);
                    location.reload(); // optional: reload to update UI
                } else {
                    alert("❌ " + (data.error || "Something went wrong"));
                    processBtn.disabled = false;
                    processBtn.innerText = "⚙️ Process File";
                }
            } catch (error) {
                alert("⚠️ Network error");
                processBtn.disabled = false;
                processBtn.innerText = "⚙️ Process File";
            }
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
