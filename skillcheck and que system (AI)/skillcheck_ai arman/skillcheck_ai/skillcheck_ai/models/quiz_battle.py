from models import db
from datetime import datetime

class QuizBattle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True)
    player1_id = db.Column(db.Integer)
    player2_id = db.Column(db.Integer, nullable=True)
    topic = db.Column(db.String(100))
    status = db.Column(db.String(20), default='waiting')
    winner_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizBattleAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    battle_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    question_index = db.Column(db.Integer)
    selected = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean)
    time_taken = db.Column(db.Float)
