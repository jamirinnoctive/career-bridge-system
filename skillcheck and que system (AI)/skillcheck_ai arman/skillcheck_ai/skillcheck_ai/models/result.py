from models import db
from datetime import datetime

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    session_id = db.Column(db.String(100))
    role = db.Column(db.String(100))
    answer = db.Column(db.Text)
    score = db.Column(db.Integer)
    status = db.Column(db.String(20))
    filler_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    missing_points = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
