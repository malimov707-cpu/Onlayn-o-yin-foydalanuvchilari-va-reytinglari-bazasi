import sqlite3, subprocess, sys
import pytest

@pytest.fixture(scope="module", autouse=True)
def run_pipeline():
    subprocess.run([sys.executable, "generate_data.py"], check=True)
    subprocess.run([sys.executable, "clean_analyze.py"], check=True)

def q(sql, db="data/clean.db"):
    c = sqlite3.connect(db); r = c.execute(sql).fetchall(); c.close(); return r

def test_15_tables():
    assert q("SELECT count(*) FROM sqlite_master WHERE type='table'", "data/raw.db")[0][0] == 15
    assert q("SELECT count(*) FROM sqlite_master WHERE type='table'")[0][0] == 15

def test_no_duplicate_email():
    assert q("SELECT count(*)-count(DISTINCT email) FROM users")[0][0] == 0

def test_email_valid():
    assert q("SELECT count(*) FROM users WHERE email NOT LIKE '%@%'")[0][0] == 0

def test_elo_range():
    assert q("SELECT count(*) FROM ratings WHERE elo<0 OR elo>3000 OR elo IS NULL")[0][0] == 0

def test_scores_not_negative():
    assert q("SELECT count(*) FROM match_players WHERE score<0 OR score IS NULL")[0][0] == 0

def test_stars_range():
    assert q("SELECT count(*) FROM game_reviews WHERE stars NOT BETWEEN 1 AND 5")[0][0] == 0

def test_country_mapped():
    assert q("SELECT count(*) FROM users u LEFT JOIN countries c USING(country_id) WHERE u.country_id IS NOT NULL AND c.country_id IS NULL")[0][0] == 0
    import json
    report = json.load(open("docs/downloads/quality.json"))
    assert q("SELECT count(*) FROM users WHERE country_id IS NULL")[0][0] == report["country_unknown"]

def test_birth_year_range():
    assert q("SELECT count(*) FROM users WHERE birth_year IS NOT NULL AND birth_year NOT BETWEEN 1930 AND 2020")[0][0] == 0


def test_foreign_keys_and_primary_keys():
    assert q("PRAGMA foreign_key_check") == []
    tables = q("SELECT name FROM sqlite_master WHERE type='table'")
    for (name,) in tables:
        assert any(row[5] for row in q(f"PRAGMA table_info({name})")), name
    assert q("PRAGMA foreign_key_list(ratings)")


def test_destination_rejects_invalid_rows():
    with sqlite3.connect("data/clean.db") as con:
        con.execute("PRAGMA foreign_keys=ON")
        for sql in ["UPDATE ratings SET elo=9999", "UPDATE users SET country_id=-1", "UPDATE game_reviews SET stars=0", "UPDATE users SET email=(SELECT email FROM users LIMIT 1)"]:
            with pytest.raises(sqlite3.IntegrityError):
                con.execute(sql)
            con.rollback()


def test_unique_achievements_and_friends():
    for table, keys in [("user_achievements", "user_id,achievement_id"), ("friends", "user_id,friend_id")]:
        assert q(f"SELECT {keys} FROM {table} GROUP BY {keys} HAVING COUNT(*)>1") == []
    assert q("SELECT * FROM friends WHERE user_id=friend_id") == []


def test_continuous_leaderboards():
    assert q("SELECT game_id,season FROM leaderboards GROUP BY game_id,season HAVING MIN(rank_position)<>1 OR MAX(rank_position)<>COUNT(*)") == []


def test_dates_duration_and_level():
    from datetime import date
    for table, col in [("users","registered_at"),("matches","started_at"),("ratings","updated_at"),("user_achievements","earned_at"),("friends","since")]:
        for (value,) in q(f"SELECT {col} FROM {table}"):
            assert date.fromisoformat(value).isoformat() == value
    assert q("SELECT COUNT(*) FROM matches WHERE duration_min IS NULL OR duration_min<0")[0][0] == 0
    assert q("SELECT COUNT(*) FROM user_profiles WHERE level IS NULL OR level NOT BETWEEN 1 AND 100")[0][0] == 0


def test_reports_reconcile_and_downloads_exist():
    import json
    from pathlib import Path
    payload = json.loads(Path("docs/data.json").read_text())
    for name, counts in payload["quality"]["tables"].items():
        assert counts["before"] == counts["after"] + counts["removed"]
        assert counts["after"] == q(f"SELECT COUNT(*) FROM {name}")[0][0]
    assert payload["stats"]["users"] == len(payload["users"])
    for name in payload["analytics"]:
        assert (Path("docs/downloads") / f"{name}.csv").is_file()
    assert len(payload["analytics"]) == 7


def test_pipeline_repeatable():
    before = q("SELECT * FROM leaderboards ORDER BY leaderboard_id")
    subprocess.run([sys.executable, "clean_analyze.py"], check=True, capture_output=True)
    assert before == q("SELECT * FROM leaderboards ORDER BY leaderboard_id")
