import random
import string
from flask import Blueprint, render_template, request, redirect, session, jsonify, url_for
from models import db
from models.quiz_battle import QuizBattle, QuizBattleAnswer
from models.quiz_question import QuizQuestion
from models.quiz_user import QuizUser

quiz_battle_bp = Blueprint("quiz_battle", __name__, url_prefix="/quiz")

QUIZ_QUESTIONS_DATA = {
    "Python Basics": [
        ("What is the output of print(type([]))?", "tuple", "list", "dict", "set", "B"),
        ("Which keyword defines a function?", "func", "define", "def", "function", "C"),
        ("What does len(\"hello\") return?", "4", "5", "6", "error", "B"),
        ("Which is mutable?", "tuple", "string", "list", "int", "C"),
        ("What is 2**3?", "6", "8", "9", "5", "B"),
        ("How do you create an empty dict?", "{}", "[]", "()", "set()", "A"),
        ("What does range(3) produce?", "[1,2,3]", "[0,1,2]", "[0,1,2,3]", "[1,2]", "B"),
        ("Which is NOT a loop in Python?", "for", "while", "do", "None of these", "C"),
        ("What is \"hello\"[1]?", "h", "e", "l", "o", "B"),
        ("How do you import a module?", "include", "require", "import", "use", "C"),
        ("What is a lambda?", "class", "anonymous function", "loop", "list", "B"),
        ("What is bool(0)?", "True", "False", "None", "Error", "B"),
    ],
    "Web Development": [
        ("What does HTML stand for?", "Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language", "A"),
        ("Which tag creates a hyperlink?", "<link>", "<href>", "<a>", "<url>", "C"),
        ("CSS stands for?", "Computer Style Sheets", "Cascading Style Sheets", "Creative Style Sheets", "Colorful Style Sheets", "B"),
        ("Which HTTP method retrieves data?", "POST", "PUT", "DELETE", "GET", "D"),
        ("What is the default HTTP port?", "443", "8080", "80", "21", "C"),
        ("JSON stands for?", "JavaScript Object Notation", "Java Syntax Object Name", "JavaScript Online Notation", "Java Standard Object Name", "A"),
        ("Which is a JavaScript framework?", "Django", "Flask", "React", "Spring", "C"),
        ("What does DOM stand for?", "Document Object Model", "Data Object Management", "Document Oriented Module", "Data Organization Method", "A"),
        ("HTTPS adds what to HTTP?", "Speed", "Compression", "Security", "Caching", "C"),
        ("Which selector targets by id in CSS?", ".", "#", "*", "@", "B"),
        ("REST API uses which format commonly?", "XML", "CSV", "JSON", "HTML", "C"),
        ("What status code means Not Found?", "200", "301", "500", "404", "D"),
    ],
    "Database": [
        ("SQL stands for?", "Structured Query Language", "Simple Query Language", "Standard Query Logic", "Stored Query List", "A"),
        ("Which command retrieves records?", "INSERT", "UPDATE", "SELECT", "DELETE", "C"),
        ("Primary key must be?", "NULL", "Unique", "Duplicate", "String", "B"),
        ("Which JOIN returns all rows from both tables?", "INNER JOIN", "LEFT JOIN", "FULL OUTER JOIN", "CROSS JOIN", "C"),
        ("Which is a NoSQL database?", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "C"),
        ("ACID stands for?", "Atomicity Consistency Isolation Durability", "Async Code Interface Design", "Array Control Index Data", "Access Control Index Definition", "A"),
        ("Which aggregate function counts rows?", "SUM", "AVG", "COUNT", "MAX", "C"),
        ("Foreign key references?", "Primary key of another table", "Any column", "Index column", "Unique column", "A"),
        ("Which clause filters groups?", "WHERE", "HAVING", "GROUP BY", "ORDER BY", "B"),
        ("Normalization reduces?", "Speed", "Redundancy", "Columns", "Tables", "B"),
        ("Which index is fastest for equality?", "B-tree", "Hash", "Bitmap", "Cluster", "B"),
        ("What does ORM stand for?", "Object Relational Mapping", "Object Runtime Model", "Ordered Row Management", "Object Record Method", "A"),
    ],
    "Networking": [
        ("IP stands for?", "Internet Protocol", "Internal Process", "Interface Port", "Input Parameter", "A"),
        ("Default subnet mask for Class A?", "255.255.255.0", "255.255.0.0", "255.0.0.0", "0.0.0.0", "C"),
        ("Which layer handles routing?", "Physical", "Data Link", "Network", "Transport", "C"),
        ("TCP is?", "Connectionless", "Connection-oriented", "Broadcast", "Unreliable", "B"),
        ("DNS converts?", "IP to MAC", "Domain to IP", "Port to IP", "URL to HTML", "B"),
        ("Which port does HTTPS use?", "80", "21", "443", "25", "C"),
        ("FTP stands for?", "File Transfer Protocol", "Fast Transfer Port", "File Transmission Program", "Formatted Text Protocol", "A"),
        ("Ping uses which protocol?", "TCP", "UDP", "ICMP", "FTP", "C"),
        ("What is a firewall?", "Hardware only", "Software only", "Network security device", "Router", "C"),
        ("MAC address is at which layer?", "Network", "Transport", "Data Link", "Physical", "C"),
        ("Which is a private IP range?", "192.168.x.x", "8.8.8.8", "1.1.1.1", "172.217.x.x", "A"),
        ("DHCP assigns?", "DNS", "IP addresses", "MAC addresses", "Ports", "B"),
    ],
    "Operating Systems": [
        ("OS stands for?", "Output System", "Operating System", "Online Server", "Object Structure", "B"),
        ("Which is a process state?", "Sleeping", "Running", "Waiting", "All of the above", "D"),
        ("Deadlock requires?", "Mutual exclusion", "Hold and wait", "No preemption", "All of the above", "D"),
        ("Virtual memory uses?", "CPU", "RAM", "Hard disk", "Cache", "C"),
        ("Which scheduling is best for batch jobs?", "Round Robin", "FCFS", "SJF", "Priority", "C"),
        ("Semaphore solves?", "Deadlock", "Synchronization", "Memory leak", "Page fault", "B"),
        ("Context switch saves?", "Process state", "File", "Network", "Thread only", "A"),
        ("Paging avoids?", "Fragmentation", "Deadlock", "Starvation", "Race condition", "A"),
        ("Fork() creates?", "Thread", "File", "Child process", "Socket", "C"),
        ("Which is not an OS?", "Linux", "Windows", "Android", "Oracle", "D"),
        ("Thrashing occurs when?", "CPU overheats", "Too many page faults", "Disk is full", "RAM overflows", "B"),
        ("IPC stands for?", "Inter Process Communication", "Internal Port Control", "Internet Protocol Channel", "Input Process Code", "A"),
    ],
}


def require_quiz_login():
    return session.get("quiz_user_id")


def gen_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@quiz_battle_bp.route("/lobby")
def lobby():
    uid = require_quiz_login()
    if not uid:
        return redirect("/quiz/login")
    user = QuizUser.query.get(uid)
    topics = [r[0] for r in db.session.query(QuizQuestion.topic).distinct().all()]
    open_battles = QuizBattle.query.filter_by(status='waiting').all()
    battle_hosts = {}
    for b in open_battles:
        host = QuizUser.query.get(b.player1_id)
        battle_hosts[b.id] = host.name if host else "Unknown"
    win_rate = 0
    total = (user.wins or 0) + (user.losses or 0)
    if total > 0:
        win_rate = round((user.wins / total) * 100)
    return render_template("quiz_lobby.html", user=user, topics=topics,
                           open_battles=open_battles, battle_hosts=battle_hosts,
                           win_rate=win_rate)


@quiz_battle_bp.route("/create", methods=["POST"])
def create_battle():
    uid = require_quiz_login()
    if not uid:
        return redirect("/quiz/login")
    topic = request.form.get("topic", "")
    if not topic:
        return redirect("/quiz/lobby")
    code = gen_room_code()
    while QuizBattle.query.filter_by(room_code=code).first():
        code = gen_room_code()
    battle = QuizBattle(room_code=code, player1_id=uid, topic=topic, status='waiting')
    db.session.add(battle)
    db.session.commit()
    return redirect(f"/quiz/room/{code}")


@quiz_battle_bp.route("/join/<room_code>", methods=["POST"])
def join_battle(room_code):
    uid = require_quiz_login()
    if not uid:
        return redirect("/quiz/login")
    battle = QuizBattle.query.filter_by(room_code=room_code, status='waiting').first()
    if not battle:
        return redirect("/quiz/lobby")
    if battle.player2_id or battle.player1_id == uid:
        return redirect("/quiz/lobby")
    battle.player2_id = uid
    battle.status = 'active'
    questions = QuizQuestion.query.filter_by(topic=battle.topic).all()
    selected = random.sample(questions, min(10, len(questions)))
    q_ids = [q.id for q in selected]
    session[f'quiz_questions_{room_code}'] = q_ids
    session.modified = True
    db.session.commit()
    return redirect(f"/quiz/room/{room_code}")


@quiz_battle_bp.route("/room/<room_code>")
def room(room_code):
    uid = require_quiz_login()
    if not uid:
        return redirect("/quiz/login")
    battle = QuizBattle.query.filter_by(room_code=room_code).first()
    if not battle:
        return redirect("/quiz/lobby")
    if uid not in [battle.player1_id, battle.player2_id]:
        return redirect("/quiz/lobby")

    p1 = QuizUser.query.get(battle.player1_id)
    p2 = QuizUser.query.get(battle.player2_id) if battle.player2_id else None

    questions = []
    if battle.status == 'active':
        q_ids = session.get(f'quiz_questions_{room_code}', [])
        if not q_ids:
            all_qs = QuizQuestion.query.filter_by(topic=battle.topic).all()
            selected = random.sample(all_qs, min(10, len(all_qs)))
            q_ids = [q.id for q in selected]
            session[f'quiz_questions_{room_code}'] = q_ids
            session.modified = True
        questions = [QuizQuestion.query.get(qid) for qid in q_ids if QuizQuestion.query.get(qid)]

        answered_indices = [a.question_index for a in
                            QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=uid).all()]
        next_q_index = len(answered_indices)

        if next_q_index >= len(questions):
            return redirect(f"/quiz/result/{room_code}")

        current_question = questions[next_q_index]
        p1_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id, is_correct=True).count()
        p2_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id, is_correct=True).count() if battle.player2_id else 0
        total_q = len(questions)

        return render_template("quiz_room.html", battle=battle, p1=p1, p2=p2,
                               current_question=current_question,
                               q_index=next_q_index,
                               total_q=total_q,
                               p1_score=p1_score, p2_score=p2_score,
                               current_uid=uid)

    if battle.status == 'finished':
        return redirect(f"/quiz/result/{room_code}")

    return render_template("quiz_room.html", battle=battle, p1=p1, p2=p2,
                           current_question=None, q_index=0, total_q=10,
                           p1_score=0, p2_score=0, current_uid=uid)


@quiz_battle_bp.route("/answer/<room_code>", methods=["POST"])
def answer(room_code):
    uid = require_quiz_login()
    if not uid:
        return jsonify({"error": "not logged in"}), 401
    battle = QuizBattle.query.filter_by(room_code=room_code).first()
    if not battle:
        return jsonify({"error": "battle not found"}), 404

    data = request.get_json() or request.form
    q_index = int(data.get("question_index", 0))
    selected = str(data.get("selected", "")).upper()
    time_taken = float(data.get("time_taken", 0))

    q_ids = session.get(f'quiz_questions_{room_code}', [])
    if q_index >= len(q_ids):
        return jsonify({"error": "invalid index"}), 400

    existing = QuizBattleAnswer.query.filter_by(
        battle_id=battle.id, user_id=uid, question_index=q_index).first()
    if existing:
        score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=uid, is_correct=True).count()
        return jsonify({"correct": existing.is_correct, "score": score, "done": False})

    question = QuizQuestion.query.get(q_ids[q_index])
    is_correct = (selected == question.correct) if question else False

    ans = QuizBattleAnswer(
        battle_id=battle.id,
        user_id=uid,
        question_index=q_index,
        selected=selected,
        is_correct=is_correct,
        time_taken=time_taken
    )
    db.session.add(ans)
    db.session.commit()

    total_q = len(q_ids)
    score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=uid, is_correct=True).count()
    p1_answers = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id).count()
    p2_answers = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id).count() if battle.player2_id else 0

    done = False
    if p1_answers >= total_q and p2_answers >= total_q and battle.status == 'active':
        p1_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id, is_correct=True).count()
        p2_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id, is_correct=True).count()
        if p1_score > p2_score:
            battle.winner_id = battle.player1_id
        elif p2_score > p1_score:
            battle.winner_id = battle.player2_id
        else:
            battle.winner_id = None
        battle.status = 'finished'

        p1_user = QuizUser.query.get(battle.player1_id)
        p2_user = QuizUser.query.get(battle.player2_id) if battle.player2_id else None
        if p1_user and p2_user:
            if battle.winner_id == battle.player1_id:
                p1_user.wins = (p1_user.wins or 0) + 1
                p1_user.xp = (p1_user.xp or 0) + 100
                p2_user.losses = (p2_user.losses or 0) + 1
                p2_user.xp = (p2_user.xp or 0) + 20
            elif battle.winner_id == battle.player2_id:
                p2_user.wins = (p2_user.wins or 0) + 1
                p2_user.xp = (p2_user.xp or 0) + 100
                p1_user.losses = (p1_user.losses or 0) + 1
                p1_user.xp = (p1_user.xp or 0) + 20
            else:
                p1_user.xp = (p1_user.xp or 0) + 50
                p2_user.xp = (p2_user.xp or 0) + 50
        db.session.commit()
        done = True

    my_answered = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=uid).count()
    return jsonify({
        "correct": is_correct,
        "score": score,
        "done": done,
        "my_answered": my_answered,
        "total_q": total_q,
        "redirect": f"/quiz/result/{room_code}" if done else None
    })


@quiz_battle_bp.route("/status/<room_code>")
def status(room_code):
    uid = require_quiz_login()
    if not uid:
        return jsonify({"error": "not logged in"}), 401
    battle = QuizBattle.query.filter_by(room_code=room_code).first()
    if not battle:
        return jsonify({"error": "not found"}), 404
    p1 = QuizUser.query.get(battle.player1_id)
    p2 = QuizUser.query.get(battle.player2_id) if battle.player2_id else None
    p1_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id, is_correct=True).count()
    p2_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id, is_correct=True).count() if battle.player2_id else 0
    p1_answered = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id).count()
    p2_answered = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id).count() if battle.player2_id else 0
    return jsonify({
        "status": battle.status,
        "p1_score": p1_score,
        "p2_score": p2_score,
        "p1_name": p1.name if p1 else "",
        "p2_name": p2.name if p2 else "",
        "p1_answered": p1_answered,
        "p2_answered": p2_answered,
        "winner_id": battle.winner_id,
        "room_code": room_code
    })


@quiz_battle_bp.route("/result/<room_code>")
def result(room_code):
    uid = require_quiz_login()
    if not uid:
        return redirect("/quiz/login")
    battle = QuizBattle.query.filter_by(room_code=room_code).first()
    if not battle:
        return redirect("/quiz/lobby")
    p1 = QuizUser.query.get(battle.player1_id)
    p2 = QuizUser.query.get(battle.player2_id) if battle.player2_id else None
    p1_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id, is_correct=True).count()
    p2_score = QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id, is_correct=True).count() if battle.player2_id else 0

    q_ids = session.get(f'quiz_questions_{room_code}', [])
    questions = [QuizQuestion.query.get(qid) for qid in q_ids if QuizQuestion.query.get(qid)]

    p1_answers = {a.question_index: a for a in QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player1_id).all()}
    p2_answers = {a.question_index: a for a in QuizBattleAnswer.query.filter_by(battle_id=battle.id, user_id=battle.player2_id).all()} if battle.player2_id else {}

    i_won = (battle.winner_id == uid)
    is_draw = (battle.winner_id is None and battle.status == 'finished')

    xp_earned = 0
    if battle.status == 'finished':
        if battle.winner_id == uid:
            xp_earned = 100
        elif is_draw:
            xp_earned = 50
        else:
            xp_earned = 20

    return render_template("quiz_result.html", battle=battle, p1=p1, p2=p2,
                           p1_score=p1_score, p2_score=p2_score,
                           questions=questions, p1_answers=p1_answers, p2_answers=p2_answers,
                           i_won=i_won, is_draw=is_draw, current_uid=uid, xp_earned=xp_earned)


@quiz_battle_bp.route("/seed")
def seed():
    if QuizQuestion.query.count() > 0:
        return "Already seeded."
    for topic, qs in QUIZ_QUESTIONS_DATA.items():
        for q in qs:
            qq = QuizQuestion(
                topic=topic,
                question=q[0],
                option_a=q[1],
                option_b=q[2],
                option_c=q[3],
                option_d=q[4],
                correct=q[5]
            )
            db.session.add(qq)
    db.session.commit()
    return f"Seeded {QuizQuestion.query.count()} questions."
