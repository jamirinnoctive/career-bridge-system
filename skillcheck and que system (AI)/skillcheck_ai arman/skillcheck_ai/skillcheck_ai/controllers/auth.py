
from flask import Blueprint, render_template, request, redirect, session
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    return render_template("home.html")

@auth_bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.password == request.form["password"]:
            session["user_id"] = user.id
            return redirect("/dashboard")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
