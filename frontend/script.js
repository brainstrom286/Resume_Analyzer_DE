const form = document.getElementById("resumeForm");
const results = document.getElementById("results");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = document.getElementById("resume").files[0];
    if (!file) return alert("Upload resume");

    const formData = new FormData();
    formData.append("resume", file);

    const res = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();

    document.getElementById("score").innerText = data.resume_score;

    // Skills
    const skillsBox = document.getElementById("skillsFound");
    skillsBox.innerHTML = "";
    data.skills_found.forEach(skill => {
        skillsBox.innerHTML += `<span class="skill">${skill}</span>`;
    });

    // Improvements
    const imp = document.getElementById("improvements");
    imp.innerHTML = "";

    if (data.improvements.length === 0) {
        imp.innerHTML = `<li style="color:#86efac;">No major issues detected !!</li>`;
    } else {
        data.improvements.forEach(i => {
            imp.innerHTML += `<li>${i}</li>`;
        });
    }


    // Suggestions
    const sug = document.getElementById("suggestions");
    sug.innerHTML = "";
    data.suggestions.forEach(s => {
        sug.innerHTML += `<li>${s}</li>`;
    });

    results.style.display = "block";
});
