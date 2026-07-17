from models import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    category = db.Column(db.String(50))
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
