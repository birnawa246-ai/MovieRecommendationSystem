import sys, os, json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import app, db
from models import Movie
import pandas as pd

CSV=Path(__file__).resolve().parents[1]/'data'/'tmdb_5000_credits.csv'

def parse(s):
    try:return json.loads(s) if isinstance(s,str) else []
    except:return []

with app.app_context():
    df=pd.read_csv(CSV)
    added=0
    for _,r in df.iterrows():
        m=Movie.query.get(int(r.movie_id))
        if not m: m=Movie(id=int(r.movie_id)); db.session.add(m); added+=1
        cast=parse(r.cast); crew=parse(r.crew)
        m.title=str(r.title)
        m.cast='|'.join([x.get('name','') for x in sorted(cast,key=lambda x:x.get('order',999))[:12] if x.get('name')])
        m.director='|'.join(dict.fromkeys([x.get('name','') for x in crew if x.get('job')=='Director' and x.get('name')]))
        m.writers='|'.join(dict.fromkeys([x.get('name','') for x in crew if x.get('department')=='Writing' and x.get('name')]))
    db.session.commit()
    print(f'Imported/updated {len(df)} rows; added {added} movies.')
