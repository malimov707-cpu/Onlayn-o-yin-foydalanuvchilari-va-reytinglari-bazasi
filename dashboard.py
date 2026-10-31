"""Export the static dashboard and reproducible, downloadable reports."""
import csv
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

LABELS = {
    'invalid_email_removed': "Noto‘g‘ri email o‘chirildi", 'duplicate_users_removed': 'Takror foydalanuvchi o‘chirildi',
    'country_unknown': 'Davlati noma’lum (saqlandi)', 'birth_year_invalid_nulled': 'Tug‘ilgan yil bo‘sh qoldirildi',
    'bad_level_fixed': 'Manfiy daraja tuzatildi', 'match_duration_bad': 'Davomiylik mediana bilan to‘ldirildi',
    'score_bad_removed': 'Noto‘g‘ri score o‘chirildi', 'elo_bad_removed': 'Noto‘g‘ri ELO o‘chirildi',
    'friends_bad_removed': 'Noto‘g‘ri do‘stlik o‘chirildi', 'reviews_bad_removed': 'Noto‘g‘ri baho aniqlandi',
    'level_over_100_capped': '100 dan yuqori daraja cheklandi', 'achievement_duplicates_removed': 'Takror yutuq o‘chirildi',
}

def build_site(rep, a):
    root = Path('docs'); root.mkdir(exist_ok=True)
    downloads = root / 'downloads'; downloads.mkdir(exist_ok=True)
    with sqlite3.connect('data/clean.db') as con:
        users = con.execute('SELECT u.username,c.name country,u.is_active,ROUND(AVG(r.elo)) elo FROM users u LEFT JOIN countries c USING(country_id) LEFT JOIN ratings r USING(user_id) GROUP BY u.user_id ORDER BY elo DESC,u.username').fetchall()
        games = con.execute('SELECT g.title,p.name platform,COUNT(DISTINCT m.match_id) matches FROM games g JOIN platforms p USING(platform_id) LEFT JOIN matches m USING(game_id) GROUP BY g.game_id ORDER BY matches DESC').fetchall()
        active = con.execute('SELECT COUNT(*) FROM users WHERE is_active=1').fetchone()[0]
    for name, frame in a.items(): frame.to_csv(downloads / f'{name}.csv', index=False)
    with (downloads/'quality.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['table','before','after','removed'])
        for name, counts in rep['tables'].items(): w.writerow([name,counts['before'],counts['after'],counts['removed']])
    (downloads/'quality.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    for file in ['analytics.sql','sql/clean_schema.sql']:
        shutil.copyfile(file, downloads/Path(file).name)
    payload = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'quality': rep, 'labels': LABELS,
        'analytics': {k:json.loads(v.to_json(orient='records')) for k,v in a.items()},
        'users':[dict(zip(['username','country','active','elo'],r)) for r in users],
        'games':[dict(zip(['title','platform','matches'],r)) for r in games],
        'stats':{'users':len(users),'games':len(games),'matches':rep['tables']['matches']['after'],'active':active},
    }
    (root/'data.json').write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    for file in ['index.html','app.js','style.css']: shutil.copyfile(Path('web')/file,root/file)
