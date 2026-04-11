import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title('Netflix Content Strategy Analysis')
st.write('Analyzing Netflix catalog trends across countries, genres, ratings, and time.')

# Load data
df = pd.read_csv('netflix_titles_cleaned.csv')

# ============================================
# CHART 1: TOP 20 COUNTRIES BY TITLE COUNT
# ============================================
st.header('Top 20 Countries by Content Volume')

country_counts = df[df['country'] != ''].copy()
country_counts['country'] = country_counts['country'].str.split(', ')
country_counts = country_counts.explode('country')
top_countries = country_counts['country'].value_counts().head(20)

fig, ax = plt.subplots(figsize=(12, 6))
top_countries.plot(kind='bar', ax=ax, color='crimson')
ax.set_xlabel('Country')
ax.set_ylabel('Number of Titles')
ax.set_xticklabels(top_countries.index, rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig)


# ============================================
# CHART 2: CONTENT ADDITION TREND (Movies vs TV shows)
# ============================================
st.header('Content addition trends (Movie vs TV show')

df4 = pd.read_csv('netflix_titles_cleaned.csv', encoding='latin-1')
df4['date_added'] = pd.to_datetime(df4['date_added'].str.strip(), format='mixed')
df4['Year'] = df4['date_added'].dt.year
df4['Month'] = df4['date_added'].dt.month

content_trend = df4.groupby(['Year','type'])['title'].count().unstack(level=1)

fig, ax = plt.subplots(figsize=(12, 5))
content_trend.plot(ax=ax)
ax.set_xlabel('Year')
ax.set_ylabel('Titles Added')
plt.tight_layout()
st.pyplot(fig)

# ============================================
# CHART 3: TOP GENRE BY COUNTRY
# ============================================
st.header('Top Genres by Country')

df3 = pd.read_csv("netflix_titles_cleaned.csv")

df3['country'] = df3['country'].str.split(', ')
df3['listed_in'] = df3['listed_in'].str.split(', ')

df_exploded = df3.explode('country').explode('listed_in')
df_exploded = df_exploded[df_exploded['country'] != '']

top_genre_by_country = df_exploded.groupby('country')['listed_in'].value_counts().groupby(level=0).head(1)

fig, ax = plt.subplots(figsize=(12, 6))
top_genre_by_country.sort_values(ascending=False).head(10).plot(kind='barh', ax=ax)
plt.tight_layout()
st.pyplot(fig)


# ============================================
# CHART 4: RATING HEATMAP BY COUNTRY
# ============================================
st.header('Rating Heatmap by Country')

valid_ratings = ['G', 'PG', 'PG-13', 'R', 'NC-17',
                 'TV-Y', 'TV-Y7', 'TV-G', 'TV-PG', 'TV-14', 'TV-MA']
df4_clean = df_exploded[df_exploded['rating'].isin(valid_ratings)]
country_rating = df4_clean.groupby(['country','rating'])['title'].count().unstack(level=1)
country_rating['total'] = country_rating.sum(axis=1)
country_rating_filtered = country_rating[country_rating['total'] > 300].drop(columns='total')

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(country_rating_filtered, ax=ax)
st.pyplot(fig)