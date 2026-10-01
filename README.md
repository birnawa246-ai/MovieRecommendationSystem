# 🎬 CineMatch — Final-Year Data Science Movie Recommendation System

A portfolio-ready, full-stack **Movie Recommendation System** designed for a B.Tech final-year project and a **Data Science / ML Engineer** portfolio.

## What this project demonstrates

- Data ingestion and preprocessing from a large movie-credit dataset
- SQL database design with PostgreSQL/MySQL support
- Secure user registration and login
- Session-based authentication: after the first registration/login, the personalized dashboard opens
- Movie search by title, actor, or director
- Movie metadata: release date, rating, votes, runtime, director, writers, cast, overview and posters
- User ratings and written reviews
- Explicit **Positive / Negative feedback** classification
- Personalized ML recommendations
- Similar-movie recommendations
- Favorites
- Admin analytics dashboard
- Model rebuild workflow
- TMDB metadata/poster enrichment pipeline

## Dataset

The included `data/tmdb_5000_credits.csv` contains **4,803 movie records** with `movie_id`, `title`, `cast`, and `crew`.

The companion TMDB 5000 Movies dataset can provide fields such as budget, genres, overview, popularity, release date, runtime, vote average and vote count. The public dataset description lists these fields alongside the credits dataset. See the project source used for the dataset description: https://github.com/missvicki/TMDb-movie-data

For this reason, this project does **not fabricate** release dates, ratings or poster paths when they are absent. Use `scripts/enrich_tmdb.py` with a TMDB API key to populate those fields.

## Tech stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL or MySQL
- Session authentication
- Werkzeug password hashing

### Data Science / ML
- Pandas
- NumPy
- Scikit-learn
- TF-IDF vectorization
- Cosine similarity
- Hybrid recommendation score

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js
- Responsive dashboard UI

## Recommendation model

The model creates a movie content representation from:

`title + genres + keywords + cast + director + writers + overview + tagline`

TF-IDF converts this text into numerical vectors. Cosine similarity measures movie-to-movie similarity.

For a logged-in user, movies rated **3.5★ or higher** form a weighted user taste profile. Candidate movies are ranked using a hybrid score:

```text
Hybrid Score =
    0.75 × Content Similarity
  + 0.15 × Popularity Signal
  + 0.10 × Movie Rating Signal
```

This gives you a clear ML/data-science explanation for a viva or interview. A production version can later add collaborative filtering, matrix factorization, LightFM, or a neural recommender.

## Feedback classification

For transparent portfolio behavior:

- `rating >= 3.0` → **Positive**
- `rating < 3.0` → **Negative**

The UI displays positive and negative feedback separately. This is a rule-based baseline; an advanced version can use NLP sentiment classification from review text.

## Database architecture

```text
Users ───────< Ratings >────── Movies
  │                              │
  └────────< Reviews >───────────┘
  │                              │
  └────────< Favorites >─────────┘

Admin → Analytics → Users / Movies / Ratings / Reviews
```

The application defaults to SQLite for easy local testing, but supports PostgreSQL and MySQL through `DATABASE_URL`.

### PostgreSQL

```bash
createdb cinematch
export DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/cinematch"
```

### MySQL

```bash
mysql -u root -p -e "CREATE DATABASE cinematch;"
export DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/cinematch"
```

## Installation

### 1. Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Import the uploaded credits dataset

```bash
python scripts/import_credits.py
```

### 4. Import movie metadata (required for genre filtering)

The uploaded credits file contains cast/crew but not genres. Download the companion `tmdb_5000_movies.csv` and place it at `data/tmdb_5000_movies.csv`, then run:

```bash
python scripts/import_movies_metadata.py
```

This populates genres, release dates, ratings, runtime, overview and popularity. The two TMDB 5000 datasets are designed to be combined: the movies file contains these metadata fields and the credits file contains cast/crew. citeturn0search0turn0search7

### 5. Create admin account

```bash
export ADMIN_EMAIL="admin@cinematch.local"
export ADMIN_PASSWORD="ChangeMe@12345"
python seed_admin.py
```

Windows PowerShell:

```powershell
$env:ADMIN_EMAIL="admin@cinematch.local"
$env:ADMIN_PASSWORD="ChangeMe@12345"
python seed_admin.py
```

### 6. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## TMDB enrichment / movie posters

Create a TMDB API token/key and set:

```bash
export TMDB_API_KEY="YOUR_KEY"
```

Then run:

```bash
python scripts/enrich_tmdb.py
```

The script fills available metadata without inventing values and stores TMDB poster/backdrop paths. The frontend automatically displays posters using the TMDB image CDN when `poster_path` is available.

## User flow

```text
Register
   ↓
Account created
   ↓
Personalized Dashboard
   ↓
Search / Filter / Open Movie
   ↓
Rate + Review + Favorite
   ↓
User profile becomes richer
   ↓
ML recommendation engine updates
   ↓
More personalized recommendations
```

## Admin flow

```text
Admin Login
   ↓
Analytics Dashboard
   ├── Total Users
   ├── Movie Catalog
   ├── Ratings
   ├── Reviews
   ├── Average Review Rating
   ├── Positive vs Negative Feedback
   ├── Top Genres
   └── Top Movies
          ↓
    Rebuild ML Model
```

## Recommended final-year extensions

To make the project even stronger for a Data Science interview:

1. Add collaborative filtering using user-item ratings.
2. Add NLP sentiment analysis with TF-IDF/Logistic Regression or a transformer.
3. Add recommendation evaluation: Precision@K, Recall@K, MAP@K and NDCG@K.
4. Add A/B testing for recommendation strategies.
5. Add PostgreSQL indexes and query optimization.
6. Add Docker + Docker Compose for Flask + PostgreSQL.
7. Add an ML training notebook with EDA, feature engineering and evaluation.
8. Add model versioning and an `/api/recommendations` REST endpoint.
9. Add unit tests and CI with GitHub Actions.
10. Deploy with Render/Railway/AWS and a managed PostgreSQL database.

## Resume-ready project description

> **CineMatch — ML Movie Recommendation Platform:** Built a full-stack movie recommendation platform using Python, Flask, SQL, Pandas and Scikit-learn. Processed a 4,803+ movie credit dataset, implemented secure user authentication, movie search, ratings, review sentiment classification, favorites and a personalized hybrid recommendation engine using TF-IDF and cosine similarity. Developed an admin analytics dashboard for user activity, ratings, reviews, sentiment and catalog insights, with a TMDB enrichment pipeline for release metadata and movie posters.

## Important data note

The included credits data is used as the project's source dataset. Check the applicable TMDB/Kaggle terms and attribution requirements before public/commercial redistribution. The companion dataset is commonly described as a TMDB 5000 Movies dataset collected from The Movie Database.
