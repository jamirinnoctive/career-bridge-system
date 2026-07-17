from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from models.question import Question
from models.result import Result
from models import db
from utils.nlp_engine import key_terms, key_phrases, semantic_model
import uuid
import json
from sentence_transformers import util as st_util

interview_bp = Blueprint("interview", __name__)

FILLER_WORDS = ['um', 'uh', 'like', 'basically', 'you know', 'actually', 'literally', 'right', 'so', 'well', 'okay', 'sort of', 'kind of']

ROLES = [
    {"key": "Python Developer", "icon": "🐍", "color": "#3776ab", "desc": "Python, OOP, frameworks, optimization"},
    {"key": "Java Developer", "icon": "☕", "color": "#f89820", "desc": "Java, Spring, JVM, design patterns"},
    {"key": "Testing/QA", "icon": "🧪", "color": "#6f42c1", "desc": "Manual, automation, Selenium, STLC"},
    {"key": "DevOps", "icon": "⚙️", "color": "#e34c26", "desc": "CI/CD, Docker, Kubernetes, IaC"},
    {"key": "Full Stack Developer", "icon": "🌐", "color": "#2ecc71", "desc": "Frontend + Backend + DB + APIs"},
    {"key": "Frontend Developer", "icon": "🎨", "color": "#f1c40f", "desc": "HTML, CSS, JS, React, responsive"},
    {"key": "Backend Developer", "icon": "🔧", "color": "#e74c3c", "desc": "APIs, databases, caching, queues"},
    {"key": "Data Science", "icon": "📊", "color": "#9b59b6", "desc": "ML, statistics, Python, visualization"},
    {"key": "Cybersecurity", "icon": "🔒", "color": "#1abc9c", "desc": "Threats, encryption, OWASP, pentesting"},
    {"key": "Project Manager", "icon": "📋", "color": "#3498db", "desc": "Agile, Scrum, risk, stakeholders"},
    {"key": "Cloud Engineer", "icon": "☁️", "color": "#0ea5e9", "desc": "AWS, Azure, GCP, cloud architecture"},
    {"key": "Database Administrator", "icon": "🗄️", "color": "#b45309", "desc": "SQL, NoSQL, indexing, performance tuning"},
    {"key": "Machine Learning Engineer", "icon": "🤖", "color": "#7c3aed", "desc": "ML models, deployment, pipelines, MLOps"},
    {"key": "Mobile Developer", "icon": "📱", "color": "#059669", "desc": "Android, iOS, React Native, Flutter"},
    {"key": "Computer Networks", "icon": "🌐", "color": "#dc2626", "desc": "TCP/IP, routing, protocols, network security"},
    {"key": "Software Architect", "icon": "🏗️", "color": "#d97706", "desc": "System design, patterns, scalability, microservices"},
]


def count_fillers(text):
    count = 0
    lower = text.lower()
    for word in FILLER_WORDS:
        import re
        matches = re.findall(r'\b' + re.escape(word) + r'\b', lower)
        count += len(matches)
    return count


def score_answer(user_answer, correct_answer):
    """Score an answer against the model answer using two signals:
    1) concept coverage — what fraction of the correct answer's key terms
       (nouns/verbs/adjectives, lemmatized) actually appear in the user's answer.
       This is the primary signal: it directly measures "did you mention the
       right things", and is immune to a short answer that happens to share
       the same general topic as the correct one.
    2) semantic similarity — sentence-transformer embedding similarity, used
       as a smaller supporting signal so paraphrased-but-correct answers
       (different words, same meaning) aren't penalized by exact-term coverage alone.
    Also returns the correct answer's key phrases that never showed up in the
    user's answer, for "you missed mentioning X" feedback.
    """
    user_answer = (user_answer or "").strip()
    correct_terms = key_terms(correct_answer)

    if len(user_answer.split()) < 3 or not correct_terms:
        return 0, "Needs Work", key_phrases(correct_answer)[:6]

    user_term_set = key_terms(user_answer)

    def stem(word):
        return word[:5] if len(word) > 5 else word

    user_stems = {stem(w) for w in user_term_set}
    covered = {t for t in correct_terms if t in user_term_set or stem(t) in user_stems}
    coverage = len(covered) / len(correct_terms)

    emb = semantic_model.encode([user_answer, correct_answer], convert_to_tensor=True)
    similarity = st_util.cos_sim(emb[0], emb[1]).item()  # roughly 0..0.8 for related text
    sim_norm = max(0.0, min(1.0, similarity / 0.8))

    combined = coverage * 0.75 + sim_norm * 0.25
    score = round(max(0, min(100, combined * 100)))

    correct_phrases = key_phrases(correct_answer)[:10]
    missing = [
        phrase for phrase in correct_phrases
        if not any((w in user_term_set or stem(w) in user_stems) for w in phrase.split())
    ][:6]

    if score >= 75:
        status = "Excellent"
    elif score >= 55:
        status = "Good"
    elif score >= 35:
        status = "Partial"
    else:
        status = "Needs Work"
    return score, status, missing


@interview_bp.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    past_count = Result.query.filter_by(user_id=user_id).count()
    return render_template("dashboard.html", roles=ROLES, past_count=past_count)


@interview_bp.route("/interview/<role>")
def start_interview(role):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # Get all questions for this role
    all_questions = Question.query.filter_by(role=role).all()
    if not all_questions:
        return redirect("/dashboard")

    # Find question IDs this user has already seen for this role (unique only)
    from models.result import Result
    seen_ids = list(set([r.question_id for r in Result.query.filter_by(user_id=user_id, role=role).all()]))

    # Pick unseen questions first, then recycle if needed — always exactly 10, no duplicates
    import random
    unseen = [q for q in all_questions if q.id not in seen_ids]
    seen_qs = [q for q in all_questions if q.id in seen_ids]

    if len(unseen) >= 10:
        selected = random.sample(unseen, 10)
    elif len(unseen) + len(seen_qs) >= 10:
        needed = 10 - len(unseen)
        extra = random.sample(seen_qs, needed)
        selected = unseen + extra
        random.shuffle(selected)
    else:
        # Fewer than 10 total — use all, no duplicates
        combined = list({q.id: q for q in all_questions}.values())
        selected = random.sample(combined, min(10, len(combined)))

    # Always exactly 10, guaranteed unique
    selected = selected[:10]

    sess_id = str(uuid.uuid4())
    session['interview_session_id'] = sess_id
    session['interview_role'] = role
    session['interview_questions'] = [q.id for q in selected]
    session['interview_q_index'] = 0
    session.modified = True

    return redirect(url_for('interview.question_page', role=role, num=1))


@interview_bp.route("/interview/<role>/question/<int:num>", methods=["GET", "POST"])
def question_page(role, num):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    if session.get('interview_role') != role:
        return redirect(url_for('interview.start_interview', role=role))

    q_ids = session.get('interview_questions', [])
    total = len(q_ids)

    if num < 1 or num > total:
        return redirect(url_for('interview.start_interview', role=role))

    if request.method == "POST":
        q_id = int(request.form.get("q_id", 0))
        answer = request.form.get("answer", "").strip()
        filler_count = int(request.form.get("filler_count", 0))
        word_count = len(answer.split()) if answer else 0

        q = Question.query.get(q_id)
        if q and answer:
            sc, status, missing_points = score_answer(answer, q.answer)
        else:
            sc, status, missing_points = 0, "Skipped", []

        sess_id = session.get('interview_session_id')
        r = Result(
            user_id=user_id,
            question_id=q_id,
            session_id=sess_id,
            role=role,
            answer=answer,
            score=sc,
            status=status,
            filler_count=filler_count,
            word_count=word_count,
            missing_points=json.dumps(missing_points)
        )
        db.session.add(r)
        db.session.commit()

        if num >= total:
            return redirect(url_for('interview.session_result', session_id=sess_id))
        else:
            return redirect(url_for('interview.question_page', role=role, num=num + 1))

    q_id = q_ids[num - 1]
    question = Question.query.get(q_id)
    return render_template("interview.html",
                           question=question,
                           role=role,
                           num=num,
                           total=total,
                           progress=int((num / total) * 100),
                           sess_id=session.get('interview_session_id', ''))


@interview_bp.route("/result/session/<session_id>")
def session_result(session_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    results = Result.query.filter_by(session_id=session_id, user_id=user_id).all()
    if not results:
        return redirect("/dashboard")

    total_score = sum(r.score for r in results)
    avg_score = total_score // len(results) if results else 0
    total_fillers = sum(r.filler_count for r in results)
    total_words = sum(r.word_count for r in results)
    avg_words = total_words // len(results) if results else 0
    role = results[0].role if results else ""

    if avg_score >= 80:
        grade = "A"
        grade_color = "#2ecc71"
        grade_msg = "Outstanding Performance!"
    elif avg_score >= 65:
        grade = "B"
        grade_color = "#3498db"
        grade_msg = "Good Performance!"
    elif avg_score >= 50:
        grade = "C"
        grade_color = "#f39c12"
        grade_msg = "Average Performance"
    elif avg_score >= 35:
        grade = "D"
        grade_color = "#e67e22"
        grade_msg = "Below Average"
    else:
        grade = "F"
        grade_color = "#e74c3c"
        grade_msg = "Needs Significant Improvement"

    q_map = {}
    for r in results:
        q = Question.query.get(r.question_id)
        if q:
            q_map[r.id] = q

    return render_template("result.html",
                           results=results,
                           q_map=q_map,
                           avg_score=avg_score,
                           total_score=total_score,
                           total_fillers=total_fillers,
                           avg_words=avg_words,
                           grade=grade,
                           grade_color=grade_color,
                           grade_msg=grade_msg,
                           role=role)


@interview_bp.route("/result/<int:user_id>")
def show_result(user_id):
    return redirect("/dashboard")
