import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from sqlalchemy import func, or_, desc
from config import Config
from models import db, User, Movie, Rating, Review, Favorite
from recommender import Recommender

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
rec=Recommender(db)

with app.app_context():
    db.create_all()
    if Movie.query.count(): rec.fit()

def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if 'user_id' not in session: return redirect(url_for('login', next=request.path))
        if db.session.get(User, session['user_id']) is None:
            session.clear()
            return redirect(url_for('login', next=request.path))
        return f(*args,**kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if 'user_id' not in session: return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user or user.role!='admin': return redirect(url_for('dashboard'))
        return f(*args,**kwargs)
    return wrapper

def movie_json(m):
    return {'id':m.id,'title':m.title,'overview':m.overview,'genres':m.genres,'director':m.director,'writers':m.writers,
            'cast':m.cast,'release_date':m.release_date.isoformat() if m.release_date else None,'runtime':m.runtime,
            'rating':round(m.rating or 0,1),'vote_count':m.vote_count or 0,'popularity':round(m.popularity or 0,2),
            'poster_path':m.poster_path,'backdrop_path':m.backdrop_path,'tagline':m.tagline,'language':m.original_language}

@app.route('/')
def home(): return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        if len(name)<2 or len(pw)<6: flash('Name and a password of at least 6 characters are required.','error')
        elif User.query.filter_by(email=email).first(): flash('An account already exists for this email. Please log in.','error')
        else:
            u=User(name=name,email=email); u.set_password(pw); db.session.add(u); db.session.commit(); session['user_id']=u.id
            flash('Account created successfully. Welcome to CineMatch!','success'); return redirect(url_for('dashboard'))
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        u=User.query.filter_by(email=email).first()
        if u and u.check_password(pw): session['user_id']=u.id; return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid email or password.','error')
    return render_template('auth.html', mode='login')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    u=User.query.get(session['user_id'])
    recs=rec.recommend_for_user(u.id, 12) if rec.matrix is not None else []
    popular=Movie.query.order_by(Movie.rating.desc(),Movie.vote_count.desc()).limit(8).all()
    return render_template('dashboard.html', user=u, recommendations=recs, popular=popular)

@app.route('/movies')
@login_required
def all_movies():
    user=db.session.get(User, session['user_id'])
    page=max(request.args.get('page', 1, type=int), 1)
    q=request.args.get('q', '').strip()
    genre=request.args.get('genre', '').strip()
    query=Movie.query
    if q:
        query=query.filter(or_(Movie.title.ilike(f'%{q}%'), Movie.cast.ilike(f'%{q}%'), Movie.director.ilike(f'%{q}%')))
    if genre:
        query=query.filter(Movie.genres.ilike(f'%{genre}%'))
    pagination=query.order_by(Movie.rating.desc(), Movie.vote_count.desc(), Movie.title.asc()).paginate(page=page, per_page=48, error_out=False)
    genre_rows=Movie.query.with_entities(Movie.genres).filter(Movie.genres.isnot(None), Movie.genres != '').distinct().all()
    genres=sorted({name.strip() for (value,) in genre_rows for name in value.replace(',', '|').split('|') if name.strip()}, key=str.casefold)
    return render_template('movies.html', user=user, pagination=pagination, q=q, genre=genre, genres=genres)

@app.route('/api/genres')
@login_required
def genres_api():
    values=set()
    for m in Movie.query.with_entities(Movie.genres).all():
        for g in (m[0] or '').replace(',', '|').split('|'):
            g=g.strip()
            if g: values.add(g)
    return jsonify(sorted(values))

@app.route('/api/search')
@login_required
def search():
    q=request.args.get('q','').strip(); genre=request.args.get('genre','').strip()
    query=Movie.query
    if q: query=query.filter(or_(Movie.title.ilike(f'%{q}%'),Movie.cast.ilike(f'%{q}%'),Movie.director.ilike(f'%{q}%')))
    if genre: query=query.filter(Movie.genres.ilike(f'%{genre}%'))
    return jsonify([movie_json(m) for m in query.order_by(Movie.rating.desc(),Movie.vote_count.desc()).limit(30).all()])

@app.route('/api/recommendations')
@login_required
def recommendations_api():
    genre=request.args.get('genre','').strip()
    limit=min(max(int(request.args.get('limit',12)),1),50)
    recs=rec.recommend_for_user(session['user_id'], max(limit*3, limit)) if rec.matrix is not None else []
    if genre:
        recs=[m for m in recs if genre.lower() in (m.genres or '').lower().replace(',', '|').split('|')]
        # If the personalized list contains too few matches, fill from the catalog.
        if len(recs)<limit:
            seen={m.id for m in recs}
            extra=(Movie.query.filter(Movie.genres.ilike(f'%{genre}%'))
                   .order_by(Movie.rating.desc(), Movie.vote_count.desc()).limit(limit*2).all())
            for m in extra:
                if m.id not in seen: recs.append(m)
                if len(recs)>=limit: break
    return jsonify([movie_json(m) for m in recs[:limit]])

@app.route('/movie/<int:movie_id>')
@login_required
def movie_page(movie_id):
    m=Movie.query.get_or_404(movie_id); similar=rec.similar(movie_id,8) if rec.matrix is not None else []
    reviews=Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).limit(30).all()
    return render_template('movie.html', movie=m, similar=similar, reviews=reviews)

@app.route('/api/movie/<int:movie_id>/rate', methods=['POST'])
@login_required
def rate(movie_id):
    m=Movie.query.get_or_404(movie_id); score=float(request.json.get('score',0))
    if not 0.5<=score<=5: return jsonify(error='Rating must be 0.5 to 5'),400
    r=Rating.query.filter_by(user_id=session['user_id'],movie_id=movie_id).first()
    if r: r.score=score
    else: db.session.add(Rating(user_id=session['user_id'],movie_id=movie_id,score=score))
    db.session.commit(); rec.fit(); return jsonify(ok=True)

@app.route('/api/movie/<int:movie_id>/review', methods=['POST'])
@login_required
def review(movie_id):
    Movie.query.get_or_404(movie_id); data=request.json; score=float(data.get('rating',0)); comment=str(data.get('comment','')).strip()
    if not comment or not 0.5<=score<=5: return jsonify(error='Valid rating and review are required'),400
    sentiment='Positive' if score>=3 else 'Negative'
    db.session.add(Review(user_id=session['user_id'],movie_id=movie_id,rating=score,sentiment=sentiment,comment=comment)); db.session.commit()
    return jsonify(ok=True,sentiment=sentiment)

@app.route('/api/favorite/<int:movie_id>', methods=['POST'])
@login_required
def favorite(movie_id):
    Movie.query.get_or_404(movie_id); existing=Favorite.query.filter_by(user_id=session['user_id'],movie_id=movie_id).first()
    if existing: db.session.delete(existing); saved=False
    else: db.session.add(Favorite(user_id=session['user_id'],movie_id=movie_id)); saved=True
    db.session.commit(); return jsonify(saved=saved)

@app.route('/admin')
@admin_required
def admin():
    total_users=User.query.count(); total_movies=Movie.query.count(); total_reviews=Review.query.count(); total_ratings=Rating.query.count()
    avg=db.session.query(func.avg(Review.rating)).scalar() or 0
    positive=Review.query.filter_by(sentiment='Positive').count(); negative=Review.query.filter_by(sentiment='Negative').count()
    genre_counts={}
    for m in Movie.query.all():
        for g in (m.genres or '').split('|'):
            g=g.strip()
            if g: genre_counts[g]=genre_counts.get(g,0)+1
    top_genres=sorted(genre_counts.items(), key=lambda x:x[1], reverse=True)[:10]
    top_movies=Movie.query.order_by(Movie.rating.desc(),Movie.vote_count.desc()).limit(10).all()
    return render_template('admin.html', stats={'users':total_users,'movies':total_movies,'reviews':total_reviews,'ratings':total_ratings,'avg':round(avg,2),'positive':positive,'negative':negative}, top_genres=top_genres, top_movies=top_movies)

@app.route('/admin/rebuild-model', methods=['POST'])
@admin_required
def rebuild_model(): rec.fit(); flash('Recommendation model rebuilt from the current movie catalog.','success'); return redirect(url_for('admin'))

if __name__=='__main__': app.run(debug=True)
