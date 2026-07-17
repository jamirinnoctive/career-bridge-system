from models import db

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100))
    question = db.Column(db.Text)
    option_a = db.Column(db.String(300))
    option_b = db.Column(db.String(300))
    option_c = db.Column(db.String(300))
    option_d = db.Column(db.String(300))
    correct = db.Column(db.String(1))
    difficulty = db.Column(db.String(20), default='medium')
