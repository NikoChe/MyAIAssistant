from datetime import datetime
from core import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)  # ✅ BigInteger
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
