from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)  # TMDB id
    title = db.Column(db.String(300), nullable=False, index=True)
    overview = db.Column(db.Text, default='')
    genres = db.Column(db.String(500), default='')
    keywords = db.Column(db.Text, default='')
    cast = db.Column(db.Text, default='')
    director = db.Column(db.String(300), default='')
    writers = db.Column(db.Text, default='')
    release_date = db.Column(db.Date, nullable=True, index=True)
    runtime = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, default=0.0, index=True)
    vote_count = db.Column(db.Integer, default=0)
    popularity = db.Column(db.Float, default=0.0)
    poster_path = db.Column(db.String(500), nullable=True)
    backdrop_path = db.Column(db.String(500), nullable=True)
    tagline = db.Column(db.String(500), default='')
    original_language = db.Column(db.String(20), default='')
    status = db.Column(db.String(50), default='Released')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='movie', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade='all, delete-orphan')

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id','movie_id', name='uq_user_movie_rating'),)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    rating = db.Column(db.Float, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id','movie_id', name='uq_user_movie_favorite'),)
