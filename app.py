import streamlit as st
import pickle 
import pandas  as pd
import requests
import os


def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/drive/folders/1pzd7V_f8b2mkx1RlQ5ryUdSoa6Oc58EI?usp=drive_link"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Get the confirmation token, if present
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

# Replace these with your file IDs from Google Drive
movie_dict_file_id = '1SMdnSWEVKLQeOeEjrfOeGjD7sefg_ZFl' 
similarity_file_id = '1HJ66TU3K_MWbh7mE6E-BL4JBi5LCPzM4'

# Download the files if they don't exist locally
if not os.path.exists('movie_dict.pkl'):
    download_file_from_google_drive(movie_dict_file_id, 'movie_dict.pkl')

if not os.path.exists('similarity.pkl'):
    download_file_from_google_drive(similarity_file_id, 'similarity.pkl')

# Continue with your usual code
import pickle
movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))



def fetch_poster(movie_id):
    response=requests.get("https://api.themoviedb.org/3/movie/{}?api_key=efeeca2923c7893b0cfd5384de62d8fb&language=en-US".format(movie_id))
    data=response.json()
    return "https://image.tmdb.org/t/p/w500/"+ data['poster_path']
def recommend(movie):
    movie_index=movies[movies['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key= lambda x:x[1])[1:6]
    recommended_movies=[]
    recommended_movies_posters =[]
    for i in movies_list:
        movie_id=movies.iloc[i[0]].movie_id
       
        recommended_movies.append(movies.iloc[i[0]].title)
         #fetch poster from API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies,recommended_movies_posters

st.title('Movie Recommender System')

movies_list=pickle.load(open('movie_dict.pkl','rb'))

similarity=pickle.load(open('similarity.pkl','rb'))
movies=pd.DataFrame(movies_list)


selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown",
    movies['title'].values)

if st.button("Recommend"):
    names,posters=recommend(selected_movie_name)
    col1, col2, col3,col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])



