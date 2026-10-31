-- name: top_players
SELECT u.username, ROUND(AVG(r.elo)) avg_elo FROM ratings r JOIN users u USING(user_id)
                          GROUP BY u.user_id HAVING COUNT(*)>=2 ORDER BY avg_elo DESC LIMIT 10;

-- name: elo_by_country
SELECT c.name, ROUND(AVG(r.elo)) avg_elo FROM ratings r JOIN users u USING(user_id)
                             JOIN countries c USING(country_id) GROUP BY c.name ORDER BY avg_elo DESC;

-- name: matches_per_game
SELECT g.title, COUNT(*) matches, ROUND(AVG(m.duration_min),1) avg_min FROM matches m
                               JOIN games g USING(game_id) GROUP BY g.title ORDER BY matches DESC;

-- name: avg_stars
SELECT g.title, ROUND(AVG(stars),2) stars FROM game_reviews JOIN games g USING(game_id)
                        GROUP BY g.title ORDER BY stars DESC;

-- name: matches_monthly
SELECT substr(started_at,1,7) month, COUNT(*) matches FROM matches GROUP BY month ORDER BY month;

-- name: games_by_platform
SELECT p.name platform, COUNT(*) games FROM games g
                                 JOIN platforms p USING(platform_id) GROUP BY p.name ORDER BY games DESC;

-- name: win_rate
SELECT u.username, COUNT(*) played, ROUND(100.0*SUM(is_winner)/COUNT(*),1) win_pct
                       FROM match_players JOIN users u USING(user_id) GROUP BY user_id HAVING played>=15
                       ORDER BY win_pct DESC LIMIT 10;
