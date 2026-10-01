"""Import the companion TMDB 5000 Movies CSV.
Place tmdb_5000_movies.csv in data/ before running this script.
It supplies genres, release date, runtime, ratings, popularity, overview and more.
"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import app, db
from models import Movie

ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/'data'/'tmdb_5000_movies.csv'
if not CSV.exists(): raise SystemExit(f'Missing {CSV}. Download the companion TMDB 5000 Movies CSV and place it in data/.')

def names(value):
    try:
        arr=json.loads(value) if isinstance(value,str) else []
        return '|'.join(x.get('name','') for x in arr if x.get('name'))
    except Exception: return ''

with app.app_context():
    df=pd.read_csv(CSV, low_memory=False)
    updated=0
    for _,r in df.iterrows():
        mid=int(r.get('id'))
        m=Movie.query.get(mid)
        if not m:
            m=Movie(id=mid, title=str(r.get('title') or 'Untitled')); db.session.add(m)
        m.title=str(r.get('title') or m.title)
        m.overview=str(r.get('overview') or '')
        m.genres=names(r.get('genres'))
        m.keywords=names(r.get('keywords'))
        m.release_date=pd.to_datetime(r.get('release_date'), errors='coerce').date() if pd.notna(r.get('release_date')) else m.release_date
        m.runtime=int(r.get('runtime')) if pd.notna(r.get('runtime')) else m.runtime
        m.rating=float(r.get('vote_average') or 0)
        m.vote_count=int(r.get('vote_count') or 0)
        m.popularity=float(r.get('popularity') or 0)
        m.original_language=str(r.get('original_language') or '')
        m.tagline=str(r.get('tagline') or '')
        updated+=1
    db.session.commit()
    print(f'Imported metadata for {updated} movies.')
