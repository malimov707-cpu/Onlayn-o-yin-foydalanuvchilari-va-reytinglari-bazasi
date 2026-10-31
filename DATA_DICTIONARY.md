# Tozalangan baza ustunlari lug‘ati

Raw bazada users.country_raw dastlabki davlat matnini saqlaydi; clean bazada u country_id bilan almashtiriladi.

## countries — Davlatlar lug‘ati

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| country_id | INTEGER | PK 1 | Davlat identifikatori; users uchun noma’lum bo‘lsa NULL |
| name | TEXT | — | Nom |
| code | TEXT | — | Davlat kodi |

## users — Foydalanuvchi hisoblari

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| user_id | INTEGER | PK 1 | Foydalanuvchi identifikatori |
| username | TEXT | — | Normallashtirilgan foydalanuvchi nomi |
| email | TEXT | — | Kichik harfli yagona email |
| country_id | INTEGER |  FK → countries.country_id | Davlat identifikatori; users uchun noma’lum bo‘lsa NULL |
| birth_year | INTEGER | — | Tug‘ilgan yil, 1930–2020 yoki NULL |
| registered_at | TEXT | — | Ro‘yxatdan o‘tgan sana, YYYY-MM-DD |
| is_active | INTEGER | — | Faollik belgisi: 0 yoki 1 |

## user_profiles — Foydalanuvchi profili

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| user_id | INTEGER | PK 1 FK → users.user_id | Foydalanuvchi identifikatori |
| display_name | TEXT | — | Ko‘rsatiladigan ism |
| level | INTEGER | — | Daraja, 1–100 |
| xp | INTEGER | — | Tajriba ballari, manfiy emas |
| bio | TEXT | — | Profil tavsifi |

## platforms — O‘yin platformalari

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| platform_id | INTEGER | PK 1 | Platforma identifikatori |
| name | TEXT | — | Nom |

## genres — Janrlar lug‘ati

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| genre_id | INTEGER | PK 1 | Janr identifikatori |
| name | TEXT | — | Nom |

## games — O‘yinlar katalogi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| game_id | INTEGER | PK 1 | O‘yin identifikatori |
| title | TEXT | — | O‘yin/yutuq nomi |
| platform_id | INTEGER |  FK → platforms.platform_id | Platforma identifikatori |
| release_year | INTEGER | — | Chiqarilgan yil |

## game_genres — O‘yin va janr bog‘lanishi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| game_id | INTEGER | PK 1 FK → games.game_id | O‘yin identifikatori |
| genre_id | INTEGER | PK 2 FK → genres.genre_id | Janr identifikatori |

## matches — O‘tkazilgan matchlar

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| match_id | INTEGER | PK 1 | Match identifikatori |
| game_id | INTEGER |  FK → games.game_id | O‘yin identifikatori |
| started_at | TEXT | — | Match sanasi, YYYY-MM-DD |
| duration_min | REAL | — | Davomiylik (daqiqa), manfiy emas |

## match_players — Matchdagi foydalanuvchi natijasi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| match_id | INTEGER | PK 1 FK → matches.match_id | Match identifikatori |
| user_id | INTEGER | PK 2 FK → users.user_id | Foydalanuvchi identifikatori |
| score | INTEGER | — | Ishtirok ballari, manfiy emas |
| is_winner | INTEGER | — | G‘alaba belgisi: 0 yoki 1 |

## ratings — Foydalanuvchining o‘yindagi ELO reytingi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| rating_id | INTEGER | PK 1 | Reyting yozuvi identifikatori |
| user_id | INTEGER |  FK → users.user_id | Foydalanuvchi identifikatori |
| game_id | INTEGER |  FK → games.game_id | O‘yin identifikatori |
| elo | INTEGER | — | ELO reytingi, 0–3000 |
| updated_at | TEXT | — | Yangilangan sana, YYYY-MM-DD |

## leaderboards — O‘yin va mavsum reyting o‘rinlari

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| leaderboard_id | INTEGER | PK 1 | Leaderboard yozuvi identifikatori |
| game_id | INTEGER |  FK → games.game_id | O‘yin identifikatori |
| user_id | INTEGER |  FK → users.user_id | Foydalanuvchi identifikatori |
| season | TEXT | — | Mavsum belgisi |
| rank_position | INTEGER | — | O‘yin/mavsumdagi uzluksiz o‘rin, 1 dan |

## achievements — Yutuqlar lug‘ati

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| achievement_id | INTEGER | PK 1 | Yutuq identifikatori |
| title | TEXT | — | O‘yin/yutuq nomi |
| points | INTEGER | — | Yutuq ballari, manfiy emas |

## user_achievements — Foydalanuvchiga berilgan bir martalik yutuqlar

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| user_id | INTEGER | PK 1 FK → users.user_id | Foydalanuvchi identifikatori |
| achievement_id | INTEGER | PK 2 FK → achievements.achievement_id | Yutuq identifikatori |
| earned_at | TEXT | — | Yutuq olingan sana, YYYY-MM-DD |

## friends — Yo‘naltirilgan do‘stlik bog‘lanishi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| user_id | INTEGER | PK 1 FK → users.user_id | Foydalanuvchi identifikatori |
| friend_id | INTEGER | PK 2 FK → users.user_id | Do‘st hisobining identifikatori |
| since | TEXT | — | Do‘stlik sanasi, YYYY-MM-DD |

## game_reviews — Foydalanuvchi bahosi va sharhi

| Ustun | Tur | Kalit/bog‘lanish | Tavsif |
|---|---|---|---|
| review_id | INTEGER | PK 1 | Sharh identifikatori |
| user_id | INTEGER |  FK → users.user_id | Foydalanuvchi identifikatori |
| game_id | INTEGER |  FK → games.game_id | O‘yin identifikatori |
| stars | INTEGER | — | Baho, 1–5 |
| comment | TEXT | — | Sharh matni, NULL bo‘lishi mumkin |

## Qo‘shimcha cheklovlar

Email yagona. Ratings `(user_id, game_id)` yagona. Leaderboard `(game_id, season, rank_position)` va `(game_id, season, user_id)` yagona. Birlamchi tarkibli kalitlar game_genres, match_players, user_achievements va friends takrorlarini cheklaydi. Do‘stlik o‘z-o‘ziga bog‘lanmaydi. To‘liq DDL: `sql/clean_schema.sql`.