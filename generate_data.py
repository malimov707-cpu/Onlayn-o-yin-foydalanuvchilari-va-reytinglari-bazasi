"""Tartibsiz (iflos) ma'lumot generatori -> data/raw.db"""
import sqlite3, random, os
from datetime import date, timedelta

random.seed(42)
os.makedirs("data", exist_ok=True)
DB = "data/raw.db"
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
con.executescript(open("schema.sql", encoding="utf-8").read())

def rdate(a=2022, b=2026):
    d = date(a, 1, 1) + timedelta(days=random.randint(0, (b - a) * 365))
    return d.strftime("%Y-%m-%d") if random.random() < 0.7 else d.strftime("%d/%m/%Y")

countries = [("Uzbekistan","UZ"),("Kazakhstan","KZ"),("Russia","RU"),("Turkey","TR"),("USA","US"),
             ("Germany","DE"),("Korea","KR"),("Japan","JP"),("India","IN"),("Brazil","BR")]
con.executemany("INSERT INTO countries VALUES(?,?,?)", [(i+1, n, c) for i,(n,c) in enumerate(countries)])
platforms = ["PC","PlayStation","Xbox","Mobile"]
con.executemany("INSERT INTO platforms VALUES(?,?)", list(enumerate(platforms, 1)))
genres = ["Shooter","Strategy","RPG","Sport","Racing","Puzzle"]
con.executemany("INSERT INTO genres VALUES(?,?)", list(enumerate(genres, 1)))
titles = ["Alpha Strike","Dragon Quest X","Speed Rush","Chess Master","Goal Hero","Zombie Siege",
          "Empire Wars","Puzzle Land","Night Racer","Sky Arena","Mystic Realm","Tank Legends"]
con.executemany("INSERT INTO games VALUES(?,?,?,?)",
                [(i+1, t, random.randint(1,4), random.randint(2015,2025)) for i,t in enumerate(titles)])
for g in range(1, 13):
    for ge in random.sample(range(1,7), 2):
        con.execute("INSERT INTO game_genres VALUES(?,?)", (g, ge))

# USERS (+ xatolar)
N = 500
users = []
for i in range(1, N+1):
    name = f"player{i}"
    email = f"{name}@mail.com"
    r = random.random()
    if r < 0.05: email = email.replace("@", "")
    elif r < 0.10: email = email.upper()
    cn, cc = random.choice(countries)
    craw = random.choice([cn, cn.lower(), cn.upper(), f" {cn} ", cc, None])
    by = random.randint(1960, 2012)
    r = random.random()
    if r < 0.03: by = random.choice([1850, 2035])
    elif r < 0.06: by = None
    uname = name if random.random() > 0.1 else f"  {name.title()} "
    users.append((i, uname, email, craw, None, by, rdate(), random.choice([0,1,1,1])))
for k in range(25):  # dublikatlar
    src = random.choice(users)
    users.append((N+1+k, src[1], src[2], src[3], None, src[5], src[6], src[7]))
con.executemany("INSERT INTO users VALUES(?,?,?,?,?,?,?,?)", users)
con.executemany("INSERT INTO user_profiles VALUES(?,?,?,?,?)",
    [(u[0], u[1], random.randint(1,100) if random.random()>0.03 else -5, random.randint(0,99999),
      None if random.random()<0.4 else "gamer") for u in users[:N]])

# MATCHES
mrows, mprows = [], []
for m in range(1, 3001):
    g = random.randint(1,12)
    dur = round(random.uniform(5,60),1)
    r = random.random()
    if r < 0.03: dur = -dur
    elif r < 0.06: dur = None
    mrows.append((m, g, rdate(2025,2026), dur))
    ps = random.sample(range(1,N+1), random.randint(2,4))
    scores = [random.randint(0,5000) for _ in ps]
    win = scores.index(max(scores))
    for j,(p,s) in enumerate(zip(ps,scores)):
        if random.random()<0.02: s = -s
        elif random.random()<0.02: s = None
        mprows.append((m,p,s,1 if j==win else 0))
con.executemany("INSERT INTO matches VALUES(?,?,?,?)", mrows)
con.executemany("INSERT INTO match_players VALUES(?,?,?,?)", mprows)

# RATINGS
rid, rat = 1, []
for u in range(1, N+1):
    for g in random.sample(range(1,13), random.randint(1,3)):
        elo = int(min(max(random.gauss(1500,250), 600), 2800))
        r = random.random()
        if r < 0.02: elo = 9999
        elif r < 0.04: elo = None
        rat.append((rid,u,g,elo,rdate(2025,2026))); rid += 1
con.executemany("INSERT INTO ratings VALUES(?,?,?,?,?)", rat)

lid = 1
for g in range(1,13):
    top = sorted([r for r in rat if r[2]==g and r[3] and r[3]<3000], key=lambda x:-x[3])[:20]
    for pos, r in enumerate(top,1):
        con.execute("INSERT INTO leaderboards VALUES(?,?,?,?,?)", (lid,g,r[1],"2026-S1",pos)); lid+=1

con.executemany("INSERT INTO achievements VALUES(?,?,?)",
    [(i+1,t,p) for i,(t,p) in enumerate([("First Win",10),("10 Wins",50),("100 Matches",100),("Top 10",300),
     ("Night Owl",20),("Team Player",30),("Sharpshooter",80),("Legend",500)])])
con.executemany("INSERT INTO user_achievements VALUES(?,?,?)",
    [(random.randint(1,N), random.randint(1,8), rdate()) for _ in range(1500)])
fr = [(random.randint(1,N), random.randint(1,N), rdate()) for _ in range(1200)]
con.executemany("INSERT INTO friends VALUES(?,?,?)", fr + fr[:30])  # dublikat + o'z-o'ziga do'st
con.executemany("INSERT INTO game_reviews VALUES(?,?,?,?,?)",
    [(i, random.randint(1,N), random.randint(1,12),
      random.choice([0,11]) if random.random()<0.03 else random.randint(1,5),
      None if random.random()<0.3 else "ok") for i in range(1,801)])
con.commit(); con.close()
print("raw.db tayyor")
