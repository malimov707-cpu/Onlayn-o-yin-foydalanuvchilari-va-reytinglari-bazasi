"""DataOps: tozalash (raw.db -> clean.db) + analitika + sayt (docs/index.html)"""
import sqlite3, json, os
import pandas as pd

RAW, CLEAN = "data/raw.db", "data/clean.db"
TABLES = ["countries","users","user_profiles","platforms","genres","games","game_genres","matches",
          "match_players","ratings","leaderboards","achievements","user_achievements","friends","game_reviews"]

def pdate(s):
    if pd.isna(s): return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try: return pd.to_datetime(s, format=fmt)
        except Exception: pass
    return pd.NaT

def clean():
    con = sqlite3.connect(RAW)
    t = {n: pd.read_sql(f"SELECT * FROM {n}", con) for n in TABLES}
    con.close()
    rep = {}
    raw_counts = {n: len(df) for n, df in t.items()}

    # --- users
    u = t["users"]; rep["users_raw"] = len(u)
    u["username"] = u["username"].str.strip().str.lower()
    u["email"] = u["email"].str.strip().str.lower()
    bad_email = ~u["email"].str.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", na=False)
    rep["invalid_email_removed"] = int(bad_email.sum()); u = u[~bad_email]
    before = len(u); u = u.drop_duplicates("email", keep="first")
    rep["duplicate_users_removed"] = before - len(u)
    c = t["countries"]; cmap = {}
    for _, r in c.iterrows():
        cmap[r["name"].lower()] = r["country_id"]; cmap[r["code"].lower()] = r["country_id"]
    u["country_id"] = u["country_raw"].str.strip().str.lower().map(cmap)
    rep["country_unknown"] = int(u["country_id"].isna().sum())
    bad_by = ~u["birth_year"].between(1930, 2020)
    rep["birth_year_invalid_nulled"] = int(bad_by.sum()); u.loc[bad_by, "birth_year"] = None
    u["registered_at"] = u["registered_at"].map(pdate).dt.strftime("%Y-%m-%d")
    u = u.drop(columns=["country_raw"])
    t["users"] = u
    ids = set(u["user_id"])

    # --- profiles
    p = t["user_profiles"]; p = p[p["user_id"].isin(ids)]
    rep["bad_level_fixed"] = int((p["level"] < 1).sum()); p.loc[p["level"] < 1, "level"] = 1
    p["bio"] = p["bio"].fillna("n/a"); t["user_profiles"] = p

    # --- matches
    m = t["matches"]
    bad = (m["duration_min"] < 0) | m["duration_min"].isna()
    rep["match_duration_bad"] = int(bad.sum())
    med = m.loc[~bad, "duration_min"].median(); m.loc[bad, "duration_min"] = med
    m["started_at"] = m["started_at"].map(pdate).dt.strftime("%Y-%m-%d"); t["matches"] = m
    mp = t["match_players"]; mp = mp[mp["user_id"].isin(ids)]
    bad = (mp["score"] < 0) | mp["score"].isna()
    rep["score_bad_removed"] = int(bad.sum()); t["match_players"] = mp[~bad]

    # --- ratings
    r = t["ratings"]; r = r[r["user_id"].isin(ids)]
    bad = r["elo"].isna() | ~r["elo"].between(0, 3000)
    rep["elo_bad_removed"] = int(bad.sum()); r = r[~bad]
    r["updated_at"] = r["updated_at"].map(pdate).dt.strftime("%Y-%m-%d"); t["ratings"] = r
    t["leaderboards"] = t["leaderboards"][t["leaderboards"]["user_id"].isin(ids)]

    # --- boshqalar
    ua = t["user_achievements"]; ua = ua[ua["user_id"].isin(ids)]
    ua["earned_at"] = ua["earned_at"].map(pdate).dt.strftime("%Y-%m-%d"); t["user_achievements"] = ua.drop_duplicates(["user_id", "achievement_id"])
    f = t["friends"]; n = len(f)
    f = f[(f["user_id"] != f["friend_id"]) & f["user_id"].isin(ids) & f["friend_id"].isin(ids)].drop_duplicates(["user_id","friend_id"])
    rep["friends_bad_removed"] = n - len(f)
    f["since"] = f["since"].map(pdate).dt.strftime("%Y-%m-%d"); t["friends"] = f
    gr = t["game_reviews"]; bad = ~gr["stars"].between(1, 5)
    rep["reviews_bad_removed"] = int(bad.sum()); t["game_reviews"] = gr[~bad & gr["user_id"].isin(ids)]

    # --- yangi sifat tekshiruvi: level 1..100 oralig'iga sig'masa 100 bilan cheklash
    p = t["user_profiles"]; bad_lvl = p["level"] > 100
    rep["level_over_100_capped"] = int(bad_lvl.sum()); p.loc[bad_lvl, "level"] = 100; t["user_profiles"] = p

    # Rebuild ranks after removing users; preserve ranking order within each season.
    lb = t["leaderboards"].sort_values(["game_id", "season", "rank_position", "leaderboard_id"])
    lb["rank_position"] = lb.groupby(["game_id", "season"]).cumcount() + 1
    t["leaderboards"] = lb
    rep["tables"] = {n: {"before": raw_counts[n], "after": len(t[n]),
                        "removed": raw_counts[n] - len(t[n])} for n in TABLES}
    rep["users_clean"] = len(u)
    rep["achievement_duplicates_removed"] = len(ua) - len(t["user_achievements"])

    if os.path.exists(CLEAN): os.remove(CLEAN)
    out = sqlite3.connect(CLEAN)
    out.execute("PRAGMA foreign_keys=ON")
    out.executescript(open("sql/clean_schema.sql", encoding="utf-8").read())
    # Parent tables must be populated before their dependents.
    order = ["countries", "platforms", "genres", "users", "user_profiles", "games",
             "game_genres", "matches", "match_players", "ratings", "leaderboards",
             "achievements", "user_achievements", "friends", "game_reviews"]
    for n in order:
        t[n].to_sql(n, out, index=False, if_exists="append")
    assert not out.execute("PRAGMA foreign_key_check").fetchall()
    out.close()
    return rep

def analytics():
    con = sqlite3.connect(CLEAN); q = lambda s: pd.read_sql(s, con)
    text = open("analytics.sql", encoding="utf-8").read()
    import re
    a = {name: q(sql.strip()) for name, sql in
         re.findall(r"-- name: (\w+)\n(.*?);", text, re.S)}
    con.close(); return a

from dashboard import build_site

if __name__ == "__main__":
    rep = clean(); a = analytics(); build_site(rep, a)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print(a["top_players"].head(3))
