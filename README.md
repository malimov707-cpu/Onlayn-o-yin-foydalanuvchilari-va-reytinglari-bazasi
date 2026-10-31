# Onlayn o'yin foydalanuvchilari va reytinglari bazasi

Mavzu №5. 15 jadvalli ma'lumotlar bazasi, tartibsiz (iflos) ma'lumotlarni tozalash (DataOps),
analitika, sayt (GitHub Pages) va CI/CD.

## Pipeline
`schema.sql` -> `generate_data.py` (iflos data/raw.db) -> `clean_analyze.py` (data/clean.db + docs/index.html) -> `pytest` -> GitHub Actions -> GitHub Pages

## Ishga tushirish
```bash
pip install -r requirements.txt
python generate_data.py
python clean_analyze.py     # docs/index.html (sayt) hosil bo'ladi
pytest -v
```

## 15 jadval
countries, users, user_profiles, platforms, genres, games, game_genres, matches, match_players,
ratings, leaderboards, achievements, user_achievements, friends, game_reviews

## Tartibsiz ma'lumot muammolari va yechimi
| Muammo | Yechim |
|---|---|
| Dublikat foydalanuvchilar / do'stlar | `drop_duplicates` |
| Noto'g'ri email (`@` yo'q), katta-kichik harf | olib tashlash / `lower()` |
| Davlat nomi turlicha (UZBEKISTAN, uz, " uzbekistan ") | `countries` jadvali bilan moslashtirish |
| Tug'ilgan yil 1850/2035 | `NULL` qilish |
| Sana formatlari aralash | yagona `YYYY-MM-DD` |
| Manfiy/bo'sh score, davomiylik | o'chirish / mediana bilan to'ldirish |
| ELO = 9999 yoki bo'sh | o'chirish (0..3000 oralig'i) |
| Baho 0 yoki 11 | o'chirish (1..5) |

## Rollar
| A'zo | Rol | Vazifa |
|---|---|---|
| 1 | Data Engineer / DB | `schema.sql`, ER-diagramma |
| 2 | DataOps | `generate_data.py`, `clean_analyze.py`, sifat hisoboti |
| 3 | Data Analyst | SQL so'rovlar, grafiklar, xulosa |
| 4 | Tester (QA) | `tests/`, test hisoboti |
| 5 | DevOps / CI-CD | `.github/workflows/ci.yml`, GitHub Pages, branch qoidalari |
