from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    initial_request = db.Column(db.Text)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    topic = db.Column(db.String, nullable=False)
    notes = db.Column(db.Text)
    homework = db.Column(db.Text)
    status = db.Column(db.String, nullable=False)  # запланирована, завершена, отменена
