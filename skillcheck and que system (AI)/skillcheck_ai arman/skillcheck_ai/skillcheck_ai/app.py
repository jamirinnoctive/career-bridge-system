from flask import Flask
import json
from config import Config
from models import db
from models.user import User
from models.quiz_user import QuizUser
from models.quiz_battle import QuizBattle, QuizBattleAnswer
from models.quiz_question import QuizQuestion
from controllers.auth import auth_bp
from controllers.interview import interview_bp
from controllers.report import report_bp
from controllers.seed import seed_bp
from controllers.quiz_auth import quiz_auth_bp
from controllers.quiz_battle import quiz_battle_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.jinja_env.globals['enumerate'] = enumerate
app.jinja_env.filters['from_json'] = lambda s: json.loads(s) if s else []

app.register_blueprint(auth_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(report_bp)
app.register_blueprint(seed_bp)
app.register_blueprint(quiz_auth_bp)
app.register_blueprint(quiz_battle_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
