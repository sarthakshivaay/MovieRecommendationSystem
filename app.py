import streamlit as st
import pickle
import pandas as pd
import requests
import os

# Function to download files from Dropbox
def download_file_from_dropbox(url, destination):
    try:
        response = requests.get(url, stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            st.write(f"Downloaded {destination} successfully!")
            return True
        else:
            st.error(f"Failed to download {destination}. Status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error saving {destination}: {e}")
        return False

# Replace these with your Dropbox direct download links
movie_dict_url = 'https://www.dropbox.com/scl/fi/jcjskwm53go2aqjnzn44k/movie_dict.pkl?rlkey=wye7qf4yom13h52i99pbgsgzs&st=xn4yk0be&dl=0'
similarity_url = 'https://www.dropbox.com/scl/fi/wfi9zxwcy84v8wasyvlwj/similarity.pkl?rlkey=h911dapm4ls60i7qxfy0iuhfl&st=uv4ouf00&dl=0'

# Download the files if they don't exist locally
if not os.path.exists('movie_dict.pkl'):
    st.write("Downloading movie_dict.pkl...")
    if not download_file_from_dropbox(movie_dict_url, 'movie_dict.pkl'):
        st.stop()

if not os.path.exists('similarity.pkl'):
    st.write("Downloading similarity.pkl...")
    if not download_file_from_dropbox(similarity_url, 'similarity.pkl'):
        st.stop()

# Load the downloaded files
try:
    with open('movie_dict.pkl', 'rb') as file:
        movies_list = pickle.load(file)
    with open('similarity.pkl', 'rb') as file:
        similarity = pickle.load(file)
    st.write("Files loaded successfully!")
except (pickle.UnpicklingError, EOFError) as e:
    st.error(f"Error unpickling files: {e}. The file might be corrupted or not downloaded properly.")
    st.stop()
except FileNotFoundError as e:
    st.error(f"File not found: {e}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    st.stop()

# Function to fetch movie posters from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=efeeca2923c7893b0cfd5384de62d8fb&language=en-US"
    response = requests.get(url)
    data = response.json()
    return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_movies_posters

# Streamlit App
st.title('Movie Recommender System')

movies = pd.DataFrame(movies_list)

# Dropdown to select a movie
selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown",
    movies['title'].values)

# On Recommend button click
if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    
    # Display recommendations with movie posters
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
