import pandas as pd
import sqlite3

df = pd.read_csv("netflix_titles.csv", encoding ='latin1')
print(df.head())

conn = sqlite3.connect(":memory:")
df.to_sql("netflix", conn, index=False, if_exists="replace")

test = pd.read_sql("""select "title" 
                      from netflix
                      limit 5""", conn)
print(test.head())

country = pd.read_sql("""
select "country", count(title) as content
from netflix
where country != ''
group by "country"
order by count(title) desc
limit 5
""", conn)
print(country)

total = pd.read_sql("""
SELECT COUNT(*) as total_rows,
       COUNT(country) as non_null_country
FROM netflix
""", conn)
print(total)

missing = pd.read_sql("""
SELECT ROUND (
    (COUNT(title) - COUNT(NULLIF(country, ''))) *100.0 / COUNT(title),2)  AS missing_pct
FROM netflix
""", conn)
print(missing)

# Table 1 — content details
content = df[['show_id', 'type', 'title', 'country', 'release_year', 'rating']].copy()
content.to_sql("content", conn, index=False, if_exists="replace")
print(content)

# Table 2 — directors
directors = df[['show_id', 'director']].dropna().copy()
directors.to_sql("directors", conn, index=False, if_exists="replace")
print(directors)

content = pd.read_sql("""
SELECT content.title, directors.director
FROM content
LEFT JOIN directors ON directors.show_id = content.show_id
Limit 10
""", conn)
print(content)

# Window function version
window = pd.read_sql("""
SELECT title, rating, release_year,
    RANK() OVER (PARTITION BY rating ORDER BY release_year DESC) AS rank
FROM content
WHERE type = 'Movie'
LIMIT 10
""", conn)
print("WINDOW FUNCTION:")
print(window)

# Group by version
group = pd.read_sql("""
SELECT title, rating, release_year
FROM content
WHERE type = 'Movie'
GROUP BY rating
ORDER BY release_year DESC
LIMIT 10
""", conn)
print("\nGROUP BY:")
print(group)

directors = pd.read_sql("""
SELECT * FROM (
    SELECT content.country, directors.director, 
           COUNT(directors.director) as director_count,
           RANK() OVER (PARTITION BY content.country 
                        ORDER BY COUNT(directors.director) DESC) as rank
    FROM content
    LEFT JOIN directors ON directors.show_id = content.show_id
    WHERE content.country != ''
    GROUP BY content.country, directors.director
) WHERE rank <= 3
""", conn)
pd.set_option('display.max_columns', None)
print(directors.head(10))

newest = pd.read_sql("""
SELECT * FROM (
SELECT title, release_year, country,
    rank () over (partition by country order by release_year DESC) as rank
FROM content
WHERE country != ''
) WHERE rank = 1
""", conn)

oldest = pd.read_sql("""
SELECT * FROM (
SELECT title, release_year, country,
    rank () over (partition by country order by release_year ASC) as rank
FROM content
WHERE country != ''
) WHERE rank = 1
""", conn)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(newest.head(10))
print(oldest.head(10))

