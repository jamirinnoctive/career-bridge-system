
class Config:
    SECRET_KEY = "skillcheck_secret"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/skillcheck_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
