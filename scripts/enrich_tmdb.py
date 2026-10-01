"""Enrich the catalog with release date, genres, overview, ratings and poster paths.
Requires TMDB_API_KEY in .env/environment. Run after importing credits.
This intentionally does not invent metadata when an API match is missing.
"""
import os, sys, time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import requests
from datetime import date
from app import app, db
from models import Movie

KEY=os.getenv('TMDB_API_KEY','')
if not KEY: raise SystemExit('Set TMDB_API_KEY first.')
S=requests.Session(); headers={'accept':'application/json'}
if len(KEY)==32 and all(c in '0123456789abcdefABCDEF' for c in KEY):
    S.params['api_key']=KEY
else:
    headers['Authorization']=f'Bearer {KEY}'
S.headers.update(headers)
base='https://api.themoviedb.org/3'

try:
    response=S.get(base+'/configuration',timeout=20)
    response.raise_for_status()
except requests.RequestException as e:
    status=getattr(getattr(e,'response',None),'status_code',None)
    if status:
        raise SystemExit(f'TMDB rejected the key or request (HTTP {status}); check the API credential.') from None
    raise SystemExit('Could not reach TMDB; check the network connection and retry.') from None

def get_movie(title):
    r=S.get(base+'/search/movie',headers=headers,params={'query':title,'include_adult':'false','language':'en-US'},timeout=20); r.raise_for_status()
    results=r.json().get('results',[])
    if not results:return None
    exact=[x for x in results if x.get('title','').strip().lower()==title.strip().lower()]
    return (exact or results)[0]

def get_details(tmdb_id):
    r=S.get(base+f'/movie/{tmdb_id}',headers=headers,params={'language':'en-US'},timeout=20); r.raise_for_status(); return r.json()

with app.app_context():
    movies=Movie.query.order_by(Movie.id).all(); total=len(movies)
    for i,m in enumerate(movies,1):
        try:
            x=get_movie(m.title)
            if x:
                d=get_details(x['id'])
                m.overview=d.get('overview') or m.overview
                m.release_date=date.fromisoformat(x['release_date']) if x.get('release_date') else m.release_date
                m.genres='|'.join([g.get('name','') for g in (x.get('genres') or []) if g.get('name')])
                m.rating=float(x.get('vote_average') or 0); m.vote_count=int(x.get('vote_count') or 0); m.popularity=float(x.get('popularity') or 0)
                m.poster_path=x.get('poster_path') or m.poster_path; m.backdrop_path=x.get('backdrop_path') or m.backdrop_path
                m.original_language=x.get('original_language') or m.original_language
                m.tagline=m.tagline or ''
                db.session.commit()
            print(f'[{i}/{total}] {m.title}')
        except Exception as e:
            print('SKIP',m.title,e)
        time.sleep(0.12)
