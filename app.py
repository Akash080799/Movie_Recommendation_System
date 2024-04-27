import streamlit as st
import pandas as pd
import pickle
import time
import numpy as np
import requests
from datetime import datetime

st.set_page_config(page_title="Movie Recommender System")   #Setting the Page title 

api_key=st.secrets["theMovieDb"]

def fetch_movie_poster(movie_name):                         #Accessing the API key and calling the API for movie posters
    response=requests.get(f"https://api.themoviedb.org/3/search/movie?query={movie_name}&api_key={api_key}")   
    data=response.json()
    responseCode=response.status_code
    if responseCode==200:
        fetched_details={
            "response_code":responseCode,
            "Popularity":data['results'][0]['popularity'],
            "Average_rating (*/10)":data['results'][0]['vote_average'],
            "Release_date":data['results'][0]['release_date'],
            "Movie_overview":data['results'][0]['overview'],
            "Poster_path":"https://image.tmdb.org/t/p/w500"+data["results"][0]["poster_path"]
        }
    else:
        unableDescription="Unable to Fetch the details from Movie Database"
        fetched_details={
            "response_code":responseCode,
            "Popularity":unableDescription,
            "Average_rating (*/10)":unableDescription,
            "Release_date":unableDescription,
            "Movie_overview":unableDescription,
            "Poster_path":"artifacts/Not_found.png"
        }

    return fetched_details

def write_movie_overview(overview):       #Function used to animate the overview writing of the movie recommendation
    for word in overview.split(" "):
        yield word + " "
        time.sleep(0.03)


def displayResult(error,results):                   #Function to display the generated results
    movieResults=[]
    results=results.to_numpy()
    for movie in results:
        movieDetails=[]
        title=movie[-1][:-7]
        fetched_details=fetch_movie_poster(title)
        movieDetails=[title,fetched_details]
        movieResults.append(movieDetails)
    with st.container(border=True):
            st.success("Movie Recommendations")
            if not error:
                for movie in movieResults:
                    with st.container(border=True):
                        title_col,poster_col=st.columns(2)
                        with title_col:
                            st.header(movie[0])
                            st.empty()
                            st.write("Popularity: "+str(np.round(movie[-1]["Popularity"])))
                            st.empty()
                            st.write("Average_rating (*/10): "+str(np.round(movie[-1]["Average_rating (*/10)"])))
                            st.empty()
                            st.write("Release date: "+movie[-1]['Release_date'])
                            st.write("Overview: ")
                            st.write_stream(write_movie_overview(movie[-1]["Movie_overview"]))

                        with poster_col:
                            st.image(movie[-1]['Poster_path'],use_column_width=True,width=100)

@st.cache_data                                  #Caching the Data to avoid continous loading.
def load_required_data():
    with open("D:artifacts/Popular_movies.pkl","rb") as f:
        popular_movies=pickle.load(f)

    with open("artifacts/Active_user_indices.pkl","rb") as f:
        active_user_index=pickle.load(f)

    with open("artifacts/User_details.pkl","rb") as f:
        user_details=pickle.load(f)

    with open("artifacts/Original_movies.pkl","rb") as f:
        orig_movies=pickle.load(f)

    with open("artifacts/Item_based_pearson.pkl","rb") as f:
        item_based_pearson=pickle.load(f)

    with open("artifacts/Item_based_cosine.pkl","rb") as f:   
        item_based_cosine=pickle.load(f)

    with open("artifacts/Interaction_MF.pkl","rb") as f:
        interaction_MF=pickle.load(f)

    return popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF


@st.cache_data
def load_random_movies(tabName):                   #Similar to that of data page in Pega. If Once called then it will stay for the whole session.
    popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
    if tabName=="item_tab":
        random_movies = np.random.choice(orig_movies.loc[orig_movies["Movie ID"].isin(popular_movies)]['Title'].unique(),50)
        return random_movies
    elif tabName=="user_tab":
        active_users=sorted(active_user_index)     #Returning the Sorted list of Active users..
        return active_users


st.title("OTT Recommendation System")
error=False
st.empty()
item_tab,user_tab=st.tabs(["Item-based","User-based"])
with item_tab:
        st.write("#### Item-based Collaborative Filtering")
        st.divider()
        fav_movie=st.selectbox(label="Please select your favorite movie !..",options=load_random_movies("item_tab"),index=None)
        st.empty()
        number_recommendations=st.slider(label="Please select the number of movies to be recommended !!",min_value=1,max_value=20,key="item")
        st.empty()
        isRecommend = st.button(label="Recommend!",type="primary",key="itemButton")

        relationship=np.random.choice(['Relationship-1','Relationship-2'],size=1)

        st.empty()
        if isRecommend and relationship!=None and fav_movie!=None:
            error=False
            def getRecommendations() -> pd.DataFrame:
                    popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
                    if relationship=="Relationship-1":
                        results=item_based_pearson.loc[item_based_pearson['QueryMovieTitle']==fav_movie]['CandidateMovieTitle']
                        if len(results)>number_recommendations:
                            results=results[:number_recommendations].values
                        else:
                            results=results.values
                        results=pd.DataFrame(results,columns=['Title\'s'])

                    elif relationship=="Relationship-2":
                        movieID=orig_movies.loc[orig_movies.Title==fav_movie]['Movie ID'].unique().min()
                        movieIndices=item_based_cosine.loc[movieID].sort_values(ascending=False).index.to_list()
                        movieIndices.remove(movieID)
                        if len(movieIndices)>number_recommendations:
                            movieIndices=movieIndices[:number_recommendations]
                        results=pd.DataFrame(orig_movies.loc[orig_movies['Movie ID'].isin(movieIndices)]['Title'].unique(),columns=['Title\'s'])
                    
                    return results

            results=getRecommendations()
            displayResult(error,results)

        elif isRecommend and (relationship==None or fav_movie==None):
            st.error("Please check if all the above fields are filled before hitting \"Recommend!\"")

with user_tab:
    number_recommendations=0
    st.write("#### User-based Collaborative Filtering")
    st.divider()
    isExisting=st.radio(label="Are you an Existing active user of the OTT application ?",options=["Yes","No"],index=None,horizontal=True)

    if isExisting=="Yes":
        user_ID=st.selectbox(label="Please select/ Enter your User ID",options=load_random_movies("user_tab"),index=None)
        
    if isExisting!=None:
        st.empty()
        number_recommendations=st.slider(label="Please select the number of movies to be recommended !!",min_value=1,max_value=20,key="user")
        st.empty()
        isRecommend = st.button(label="Recommend!",type="primary",key="userButton")
        st.empty()

    if isRecommend:
        results=[]
        popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
        if isExisting=="Yes" and user_ID!=None:
            error=False
            movies_rated = interaction_MF.loc[user_ID].sort_values(ascending=False).index.to_list()
            if len(movies_rated)>number_recommendations:
                movies_rated=movies_rated[:number_recommendations]
            for movie in movies_rated:
                results.append(orig_movies.loc[orig_movies['Movie ID']==movie]['Title'].values[:1][-1])

        elif isExisting=="No":
            error=False
            results=orig_movies.loc[orig_movies['Movie ID'].isin(popular_movies)]['Title'].unique()
            if len(results)>number_recommendations:
                results=results[:number_recommendations]

        elif isExisting=="Yes" and user_ID==None:
            error=True
            st.error("Please check if all the above fields are filled before hitting \"Recommend!\"")

        if isExisting != None:
            results=pd.DataFrame(results,columns=['Title\'s'])
            displayResult(error,results)
        


