from datetime import datetime
from core import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String)
    initial_request = db.Column(db.Text)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    session_type = db.Column(db.String, nullable=False)
    answers_json = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, nullable=False, default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuestionVersion(db.Model):
    __tablename__ = 'question_versions'
    id = db.Column(db.String, primary_key=True)  # v1.0.0
    owner_id = db.Column(db.BigInteger, nullable=False)
    label = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.String, db.ForeignKey('question_versions.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, default='text')  # text, choice, date, etc
    required = db.Column(db.Boolean, default=True)
    options = db.Column(db.JSON, nullable=True)  # для кнопок
    order = db.Column(db.Integer, default=0)
