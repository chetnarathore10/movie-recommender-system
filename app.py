import streamlit as st
import pickle
import pandas as pd
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
load_dotenv()


movies_dict = pickle.load(open('movie_dict.pkl','rb'))
similarity = pickle.load(open('crisp_similarity.pkl','rb'))

movies = pd.DataFrame(movies_dict)
API_KEY = os.getenv("TMDB_API_KEY")
FALLBACK_POSTER = "https://images.unsplash.com/photo-1546872006-42c78c0ccb29?q=80&w=1286&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0 10px 0;
        font-size: 16px;
    }
    </style>
    <div class="footer">
        Developed by <a href="https://not-darshil.netlify.app/" target="_blank"><b>not.darshil</b></a>
    </div>
"""

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url,timeout=2)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        else:
            return FALLBACK_POSTER
    except Exception as e:
        print(f"Error fetching poster for {movie_id}")
        return FALLBACK_POSTER

def fetch_poster_new(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}/images?api_key={}&language=en-US".format(movie_id,API_KEY)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
                return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return "https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=2069&auto=format&fit=crop"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for {movie_id}: {e}")
        return "https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=2069&auto=format&fit=crop"

def fetch_poster_og(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    data = response.json()
    
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    movies_list = similarity[movie_index]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_name = movies.iloc[i[0]].title
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_movies_posters.append(fetch_poster(movie_id))
        time.sleep(1)  # prevents rapid-fire requests
    return recommended_movies, recommended_movies_posters

st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",                  
    layout="centered"                      
)

st.title('🎬 Movie Recommender System')


selected_movie_name = st.selectbox(
    "Which movie did you like?",
    movies['title'].values,
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        col.text(name)
        col.image(poster)

st.markdown(footer, unsafe_allow_html=True)


