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

    # --- users
    u = t["users"]; rep["users_raw"] = len(u)
    u["username"] = u["username"].str.strip().str.lower()
    u["email"] = u["email"].str.strip().str.lower()
    bad_email = ~u["email"].str.contains("@", na=False)
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
    ua["earned_at"] = ua["earned_at"].map(pdate).dt.strftime("%Y-%m-%d"); t["user_achievements"] = ua
    f = t["friends"]; n = len(f)
    f = f[(f["user_id"] != f["friend_id"]) & f["user_id"].isin(ids) & f["friend_id"].isin(ids)].drop_duplicates(["user_id","friend_id"])
    rep["friends_bad_removed"] = n - len(f)
    f["since"] = f["since"].map(pdate).dt.strftime("%Y-%m-%d"); t["friends"] = f
    gr = t["game_reviews"]; bad = ~gr["stars"].between(1, 5)
    rep["reviews_bad_removed"] = int(bad.sum()); t["game_reviews"] = gr[~bad & gr["user_id"].isin(ids)]

    # --- yangi sifat tekshiruvi: level 1..100 oralig'iga sig'masa 100 bilan cheklash
    p = t["user_profiles"]; bad_lvl = p["level"] > 100
    rep["level_over_100_capped"] = int(bad_lvl.sum()); p.loc[bad_lvl, "level"] = 100; t["user_profiles"] = p

    if os.path.exists(CLEAN): os.remove(CLEAN)
    out = sqlite3.connect(CLEAN)
    for n, df in t.items(): df.to_sql(n, out, index=False)
    out.close()
    return rep

def analytics():
    con = sqlite3.connect(CLEAN); q = lambda s: pd.read_sql(s, con)
    a = {
      "top_players": q("""SELECT u.username, ROUND(AVG(r.elo)) avg_elo FROM ratings r JOIN users u USING(user_id)
                          GROUP BY u.user_id HAVING COUNT(*)>=2 ORDER BY avg_elo DESC LIMIT 10"""),
      "elo_by_country": q("""SELECT c.name, ROUND(AVG(r.elo)) avg_elo FROM ratings r JOIN users u USING(user_id)
                             JOIN countries c USING(country_id) GROUP BY c.name ORDER BY avg_elo DESC"""),
      "matches_per_game": q("""SELECT g.title, COUNT(*) matches, ROUND(AVG(m.duration_min),1) avg_min FROM matches m
                               JOIN games g USING(game_id) GROUP BY g.title ORDER BY matches DESC"""),
      "avg_stars": q("""SELECT g.title, ROUND(AVG(stars),2) stars FROM game_reviews JOIN games g USING(game_id)
                        GROUP BY g.title ORDER BY stars DESC"""),
      "matches_monthly": q("SELECT substr(started_at,1,7) month, COUNT(*) matches FROM matches GROUP BY month ORDER BY month"),
      "games_by_platform": q("""SELECT p.name platform, COUNT(*) games FROM games g
                                 JOIN platforms p USING(platform_id) GROUP BY p.name ORDER BY games DESC"""),
      "win_rate": q("""SELECT u.username, COUNT(*) played, ROUND(100.0*SUM(is_winner)/COUNT(*),1) win_pct
                       FROM match_players JOIN users u USING(user_id) GROUP BY user_id HAVING played>=15
                       ORDER BY win_pct DESC LIMIT 10"""),
    }
    con.close(); return a

def build_site(rep, a):
    def tbl(df): return df.to_html(index=False, border=0, classes="t")
    charts = {
      "c1": ("bar", a["elo_by_country"]["name"].tolist(), a["elo_by_country"]["avg_elo"].tolist(), "O'rtacha ELO (davlat)"),
      "c2": ("bar", a["matches_per_game"]["title"].tolist(), a["matches_per_game"]["matches"].tolist(), "O'yinlar soni (match)"),
      "c3": ("line", a["matches_monthly"]["month"].tolist(), a["matches_monthly"]["matches"].tolist(), "Oylik matchlar"),
      "c4": ("bar", a["avg_stars"]["title"].tolist(), a["avg_stars"]["stars"].tolist(), "O'rtacha baho (1-5)"),
      "c5": ("bar", a["games_by_platform"]["platform"].tolist(), a["games_by_platform"]["games"].tolist(), "Platformalar boyicha o'yinlar"),
    }
    canv = "".join(f'<div class="card"><canvas id="{k}"></canvas></div>' for k in charts)
    js = "".join(f"new Chart(document.getElementById('{k}'),{{type:'{v[0]}',data:{{labels:{json.dumps(v[1])},"
                 f"datasets:[{{label:'{v[3]}',data:{json.dumps(v[2])},backgroundColor:'#4f46e5',borderColor:'#4f46e5'}}]}}}});"
                 for k, v in charts.items())
    qual = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rep.items())
    html = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8"><title>Onlayn o'yin reytinglari</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1"></script>
<style>body{{font-family:system-ui,sans-serif;max-width:1000px;margin:auto;padding:16px;color:#222}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}}
.card{{border:1px solid #ddd;border-radius:10px;padding:12px}}table{{border-collapse:collapse;width:100%}}
td,th{{padding:4px 8px;border-bottom:1px solid #eee;text-align:left}}</style></head><body>
<h1>Onlayn o'yin foydalanuvchilari va reytinglari</h1>
<h2>Ma'lumot sifati hisoboti (tozalash)</h2><div class="card"><table>{qual}</table></div>
<h2>Grafiklar</h2><div class="grid">{canv}</div>
<h2>Top 10 o'yinchi (ELO)</h2><div class="card">{tbl(a['top_players'])}</div>
<h2>Eng yuqori g'alaba foizi</h2><div class="card">{tbl(a['win_rate'])}</div>
<script>{js}</script></body></html>"""
    os.makedirs("docs", exist_ok=True)
    open("docs/index.html", "w", encoding="utf-8").write(html)

if __name__ == "__main__":
    rep = clean(); a = analytics(); build_site(rep, a)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print(a["top_players"].head(3))
