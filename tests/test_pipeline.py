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
