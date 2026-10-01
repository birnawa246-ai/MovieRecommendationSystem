-- SQLAlchemy creates these tables automatically.
-- This file documents the production database design.
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(180) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL, role VARCHAR(20) NOT NULL DEFAULT 'user', created_at TIMESTAMP NOT NULL);
CREATE TABLE movies (id INT PRIMARY KEY, title VARCHAR(300) NOT NULL, overview TEXT, genres VARCHAR(500), keywords TEXT, cast TEXT, director VARCHAR(300), writers TEXT, release_date DATE, runtime INT, rating FLOAT DEFAULT 0, vote_count INT DEFAULT 0, popularity FLOAT DEFAULT 0, poster_path VARCHAR(500), backdrop_path VARCHAR(500), tagline VARCHAR(500), original_language VARCHAR(20), status VARCHAR(50));
CREATE TABLE ratings (id INT PRIMARY KEY, user_id INT NOT NULL, movie_id INT NOT NULL, score FLOAT NOT NULL, created_at TIMESTAMP NOT NULL, UNIQUE(user_id,movie_id));
CREATE TABLE reviews (id INT PRIMARY KEY, user_id INT NOT NULL, movie_id INT NOT NULL, rating FLOAT NOT NULL, sentiment VARCHAR(20) NOT NULL, comment TEXT NOT NULL, created_at TIMESTAMP NOT NULL);
CREATE TABLE favorites (id INT PRIMARY KEY, user_id INT NOT NULL, movie_id INT NOT NULL, created_at TIMESTAMP NOT NULL, UNIQUE(user_id,movie_id));
