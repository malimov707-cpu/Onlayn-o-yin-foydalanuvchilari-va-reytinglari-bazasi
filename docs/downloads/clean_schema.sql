-- Validated destination schema. Raw schema intentionally accepts dirty data.
CREATE TABLE countries(country_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, code TEXT NOT NULL UNIQUE);
CREATE TABLE platforms(platform_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE genres(genre_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE users(user_id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT NOT NULL UNIQUE CHECK(email LIKE '%_@_%._%'), country_id INTEGER REFERENCES countries(country_id), birth_year INTEGER CHECK(birth_year BETWEEN 1930 AND 2020), registered_at TEXT NOT NULL, is_active INTEGER NOT NULL CHECK(is_active IN (0,1)));
CREATE TABLE user_profiles(user_id INTEGER PRIMARY KEY REFERENCES users(user_id), display_name TEXT, level INTEGER NOT NULL CHECK(level BETWEEN 1 AND 100), xp INTEGER CHECK(xp>=0), bio TEXT NOT NULL);
CREATE TABLE games(game_id INTEGER PRIMARY KEY, title TEXT NOT NULL, platform_id INTEGER NOT NULL REFERENCES platforms(platform_id), release_year INTEGER);
CREATE TABLE game_genres(game_id INTEGER NOT NULL REFERENCES games(game_id), genre_id INTEGER NOT NULL REFERENCES genres(genre_id), PRIMARY KEY(game_id,genre_id));
CREATE TABLE matches(match_id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(game_id), started_at TEXT NOT NULL, duration_min REAL NOT NULL CHECK(duration_min>=0));
CREATE TABLE match_players(match_id INTEGER NOT NULL REFERENCES matches(match_id), user_id INTEGER NOT NULL REFERENCES users(user_id), score INTEGER NOT NULL CHECK(score>=0), is_winner INTEGER NOT NULL CHECK(is_winner IN (0,1)), PRIMARY KEY(match_id,user_id));
CREATE TABLE ratings(rating_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(user_id), game_id INTEGER NOT NULL REFERENCES games(game_id), elo INTEGER NOT NULL CHECK(elo BETWEEN 0 AND 3000), updated_at TEXT NOT NULL, UNIQUE(user_id,game_id));
CREATE TABLE leaderboards(leaderboard_id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(game_id), user_id INTEGER NOT NULL REFERENCES users(user_id), season TEXT NOT NULL, rank_position INTEGER NOT NULL CHECK(rank_position>0), UNIQUE(game_id,season,rank_position), UNIQUE(game_id,season,user_id));
CREATE TABLE achievements(achievement_id INTEGER PRIMARY KEY, title TEXT NOT NULL, points INTEGER NOT NULL CHECK(points>=0));
CREATE TABLE user_achievements(user_id INTEGER NOT NULL REFERENCES users(user_id), achievement_id INTEGER NOT NULL REFERENCES achievements(achievement_id), earned_at TEXT NOT NULL, PRIMARY KEY(user_id,achievement_id));
CREATE TABLE friends(user_id INTEGER NOT NULL REFERENCES users(user_id), friend_id INTEGER NOT NULL REFERENCES users(user_id), since TEXT NOT NULL, PRIMARY KEY(user_id,friend_id), CHECK(user_id<>friend_id));
CREATE TABLE game_reviews(review_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(user_id), game_id INTEGER NOT NULL REFERENCES games(game_id), stars INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5), comment TEXT);
CREATE INDEX idx_matches_game_date ON matches(game_id,started_at);
CREATE INDEX idx_ratings_game_elo ON ratings(game_id,elo);
CREATE INDEX idx_reviews_game ON game_reviews(game_id);
