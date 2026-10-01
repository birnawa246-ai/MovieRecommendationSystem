from functools import lru_cache
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from models import Movie, Rating

class Recommender:
    def __init__(self, db):
        self.db = db
        self.vectorizer = None
        self.matrix = None
        self.movie_ids = []
        self.id_to_idx = {}

    def fit(self):
        movies = Movie.query.order_by(Movie.id).all()
        self.movie_ids = [m.id for m in movies]
        self.id_to_idx = {mid:i for i,mid in enumerate(self.movie_ids)}
        corpus=[]
        for m in movies:
            corpus.append(' '.join([
                m.title or '', m.genres or '', m.keywords or '', m.cast or '',
                m.director or '', m.writers or '', m.overview or '', m.tagline or ''
            ]))
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=1, max_features=50000)
        self.matrix = self.vectorizer.fit_transform(corpus) if corpus else None

    def _popularity(self, movie):
        # Smooth popularity signal to reduce bias toward tiny vote counts.
        votes = max(movie.vote_count or 0, 1)
        rating = movie.rating or 0
        return float(np.tanh(np.log1p(votes)/10.0) * (rating/10.0) + np.tanh((movie.popularity or 0)/100.0)*0.15)

    def recommend_for_user(self, user_id, limit=12):
        if self.matrix is None: return []
        rated = Rating.query.filter_by(user_id=user_id).all()
        positive = [(r.movie_id, r.score) for r in rated if r.score >= 3.5 and r.movie_id in self.id_to_idx]
        seen = {r.movie_id for r in rated}
        if not positive:
            movies = Movie.query.order_by(Movie.rating.desc(), Movie.vote_count.desc()).limit(limit).all()
            return movies
        weighted=[]; weights=[]
        for mid, score in positive:
            weighted.append(self.matrix[self.id_to_idx[mid]].toarray()[0])
            weights.append(score-2.5)
        profile=np.average(np.vstack(weighted), axis=0, weights=np.array(weights))
        sims=cosine_similarity(profile.reshape(1,-1), self.matrix).ravel()
        candidates=[]
        for i,mid in enumerate(self.movie_ids):
            if mid in seen: continue
            m=Movie.query.get(mid)
            hybrid=0.75*float(sims[i]) + 0.15*self._popularity(m) + 0.10*(m.rating or 0)/10
            candidates.append((hybrid,m))
        candidates.sort(key=lambda x:x[0], reverse=True)
        return [m for _,m in candidates[:limit]]

    def similar(self, movie_id, limit=8):
        if self.matrix is None or movie_id not in self.id_to_idx: return []
        idx=self.id_to_idx[movie_id]
        sims=cosine_similarity(self.matrix[idx], self.matrix).ravel()
        order=np.argsort(-sims)
        out=[]
        for i in order:
            mid=self.movie_ids[i]
            if mid==movie_id: continue
            out.append(Movie.query.get(mid))
            if len(out)>=limit: break
        return out
