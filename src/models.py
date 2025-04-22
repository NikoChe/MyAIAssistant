from flask_sqlalchemy import SQLAlchemy
from src.core import db

class Client(db.Model):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    source = db.Column(db.String(64), nullable=True)
    initial_request = db.Column(db.Text, nullable=True)
    telegram_id = db.Column(db.BigInteger, unique=True)
    username = db.Column(db.String(64), nullable=True)

class Session(db.Model):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    session_type = db.Column(db.String(32), default="default")
    answers_json = db.Column(db.JSON)
    status = db.Column(db.String(32), default="new")
    scheduled_at = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class QuestionVersion(db.Model):
    __tablename__ = "question_versions"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(32), primary_key=True)
    version_name = db.Column(db.String(64), nullable=True)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
    active = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.BigInteger)
    label = db.Column(db.String(128))
    public_access = db.Column(db.Boolean, default=False)

class Question(db.Model):
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.String(32), db.ForeignKey("question_versions.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(32), default="text")
    required = db.Column(db.Boolean, default=True)
    options = db.Column(db.JSON, nullable=True)
    order = db.Column(db.Integer, nullable=False)
