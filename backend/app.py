from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pdfplumber
import docx2txt


SKILL_SET = [
    "python", "java", "c++", "javascript", "sql", "html", "css",
    "machine learning", "deep learning", "data analysis",
    "flask", "django", "react", "node", "docker", "git",
    "aws", "linux"
]

SECTION_KEYWORDS = {
    "skills": ["skills", "technical skills"],
    "projects": ["projects", "academic projects"],
    "experience": ["experience", "internship", "work experience"],
    "education": ["education", "qualification"]
}

ADVANCED_SKILLS = [
    "docker", "kubernetes", "aws", "azure", "gcp",
    "microservices", "mlops", "ci/cd", "system design"
]

PROJECT_IMPACT_WORDS = [
    "improved", "increased", "reduced", "optimized",
    "achieved", "built", "developed", "designed"
]

EXPERIENCE_ACTION_WORDS = [
    "led", "implemented", "managed", "designed",
    "optimized", "deployed", "collaborated"
]


IDEAL_PROFILE_TEXT = """
Strong technical skills including backend, databases, cloud, and system design.
Projects should demonstrate measurable impact and problem solving.
Experience should include internships or real-world exposure with clear outcomes.
Knowledge of version control, deployment, and scalability is expected.
"""


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    extracted_text = ""

    if file.filename.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

    elif file.filename.lower().endswith(".docx"):
        extracted_text = docx2txt.process(file_path)

    else:
        return jsonify({"error": "Unsupported file format"}), 400

    text = extracted_text.lower()

    # ---------------- INITIALIZE VARIABLES ----------------
    found_skills = []
    sections_found = []
    suggestions = []
    improvements = []

    # ---------------- SKILL EXTRACTION ----------------
    found_skills = [skill for skill in SKILL_SET if skill in text]

    # ---------------- SECTION DETECTION ----------------
    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in text for k in keywords):
            sections_found.append(section)

    # ---------------- SCORING ----------------
    score = 0

    # Skills score
    skill_score = min(len(found_skills) * 5, 40)
    score += skill_score
    if skill_score < 20:
        improvements.append("Limited technical skills detected")
        suggestions.append("Add more relevant technical skills")

    # Section score
    section_score = min(len(sections_found) * 7, 30)
    score += section_score

    if "projects" not in sections_found:
        improvements.append("Projects section missing")
        suggestions.append("Add academic or personal projects")

    if "experience" not in sections_found:
        improvements.append("Experience section missing")
        suggestions.append("Include internship or work experience")

    # Resume length score
    word_count = len(text.split())
    if 300 <= word_count <= 900:
        score += 15
    else:
        improvements.append("Resume length not optimal")
        suggestions.append("Keep resume between 1–2 pages")

    # ---------------- SMART QUALITY CHECKS ----------------

    # Advanced skill check
    advanced_found = [s for s in ADVANCED_SKILLS if s in text]
    if len(advanced_found) == 0:
        suggestions.append(
            "Consider adding advanced tools like Docker, cloud platforms, or system design concepts"
        )

    # Project quality check
    if "projects" in sections_found:
        if not any(word in text for word in PROJECT_IMPACT_WORDS):
            improvements.append("Project descriptions lack measurable impact")
            suggestions.append(
                "Quantify project outcomes (e.g., improved performance by 20%)"
            )

    # Experience strength check
    if "experience" in sections_found:
        if not any(word in text for word in EXPERIENCE_ACTION_WORDS):
            improvements.append("Experience section lacks strong action verbs")
            suggestions.append(
                "Use strong action verbs like implemented, optimized, deployed"
            )

    # Score-based qualitative feedback
    if score < 70:
        suggestions.append(
            "Resume is suitable for entry-level roles but needs strengthening for competitive positions"
        )
    elif score < 85:
        suggestions.append(
            "Good resume overall; refining skills and project impact can significantly improve it"
        )
    else:
        suggestions.append(
            "Strong resume; tailor it specifically for each job role to maximize shortlisting chances"
        )

    score = min(score, 100)

    # ---------------- AI SEMANTIC ANALYSIS (TF-IDF) ----------------

    documents = [text, IDEAL_PROFILE_TEXT.lower()]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    if similarity_score < 0.35:
        suggestions.append(
            "Strengthened backend, cloud, or system design concepts"
        )

    if similarity_score < 0.5:
        suggestions.append(
            "Projects could be improved by emphasizing measurable results and technical depth"
        )

    if similarity_score < 0.65:
        suggestions.append(
            "Experience descriptions can be improved with clearer responsibilities and outcomes"
        )



    return jsonify({
        "resume_score": score,
        "skills_found": found_skills,
        "sections_found": sections_found,
        "improvements": improvements,
        "suggestions": suggestions
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
