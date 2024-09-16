import streamlit as st
import pickle
import pandas as pd
import requests
import os

# Function to download files from Google Drive
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Get the confirmation token if present
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break

    if token:
        response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)

    # Save the file to the specified destination
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    
    st.write(f"Downloaded {destination} successfully!")

# Function to verify if a file is a valid pickle file
def is_pickle_file(filepath):
    try:
        with open(filepath, 'rb') as file:
            pickle.load(file)
        return True
    except (pickle.UnpicklingError, EOFError, FileNotFoundError):
        return False

# Replace these with your file IDs from Google Drive
movie_dict_file_id = '1SMdnSWEVKLQeOeEjrfOeGjD7sefg_ZFl'
similarity_file_id = '1HJ66TU3K_MWbh7mE6E-BL4JBi5LCPzM4'

# Download the files if they don't exist locally
if not os.path.exists('movie_dict.pkl') or not is_pickle_file('movie_dict.pkl'):
    st.write("Downloading movie_dict.pkl...")
    download_file_from_google_drive(movie_dict_file_id, 'movie_dict.pkl')

if not os.path.exists('similarity.pkl') or not is_pickle_file('similarity.pkl'):
    st.write("Downloading similarity.pkl...")
    download_file_from_google_drive(similarity_file_id, 'similarity.pkl')

# Ensure files are downloaded and valid before loading them
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
