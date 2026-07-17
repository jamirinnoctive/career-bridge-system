from flask import Blueprint, render_template, request, redirect, session
from models import db
from models.quiz_user import QuizUser

quiz_auth_bp = Blueprint("quiz_auth", __name__, url_prefix="/quiz")


@quiz_auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing = QuizUser.query.filter_by(email=request.form["email"]).first()
        if existing:
            return render_template("quiz_register.html", error="Email already registered.")
        user = QuizUser(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/quiz/login")
    return render_template("quiz_register.html")


@quiz_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = QuizUser.query.filter_by(email=request.form["email"]).first()
        if user and user.password == request.form["password"]:
            session["quiz_user_id"] = user.id
            session["quiz_user_name"] = user.name
            return redirect("/quiz/lobby")
        return render_template("quiz_login.html", error="Invalid email or password.")
    return render_template("quiz_login.html")


@quiz_auth_bp.route("/logout")
def logout():
    session.pop("quiz_user_id", None)
    session.pop("quiz_user_name", None)
    return redirect("/")
