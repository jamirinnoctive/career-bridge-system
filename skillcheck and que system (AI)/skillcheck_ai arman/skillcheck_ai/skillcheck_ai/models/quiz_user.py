from models import db

class QuizUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    xp = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
