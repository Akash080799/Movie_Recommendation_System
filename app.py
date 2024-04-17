import streamlit as st
import pandas as pd
import pickle
import numpy as np

@st.cache_data                                  #Caching the Data to avoid continous loading.
def load_required_data():
    with open("Popular_movies.pkl","rb") as f:
        popular_movies=pickle.load(f)

    with open("Active_user_indices.pkl","rb") as f:
        active_user_index=pickle.load(f)

    with open("User_details.pkl","rb") as f:
        user_details=pickle.load(f)

    with open("Original_movies.pkl","rb") as f:
        orig_movies=pickle.load(f)

    with open("Item_based_pearson.pkl","rb") as f:
        item_based_pearson=pickle.load(f)

    with open("Item_based_cosine.pkl","rb") as f:
        item_based_cosine=pickle.load(f)

    with open("Interaction_MF.pkl","rb") as f:
        interaction_MF=pickle.load(f)

    return popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF


@st.cache_data
def load_random_movies(tabName):                   #Similar to that of data page in Pega. If Once called then it will stay for the whole session.
    popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
    if tabName=="item_tab":
        random_movies = np.random.choice(orig_movies.loc[orig_movies["Movie ID"].isin(popular_movies)]['Title'].unique(),50)
        return random_movies
    elif tabName=="user_tab":
        active_users=np.random.choice(active_user_index,50)
        return active_users


st.title("OTT Recommendation System")

st.empty()
item_tab,user_tab=st.tabs(["Item-based","User-based"])
with item_tab:
    col1,col2=st.columns([0.7,0.3])
    with col1:
        st.write("#### Item-based Recommendation system")
        st.divider()
        fav_movie=st.selectbox(label="Please select your favorite movie !..",options=load_random_movies("item_tab"))
        st.empty()
        number_recommendations=st.slider(label="Please select the number of movies to be recommended !!",min_value=1,max_value=20,key="item")
        st.empty()
        isRecommend = st.button(label="Recommend!",type="primary",key="itemButton")

    with col2:
        relationship=st.radio(label="Type of measuring relationship ?",options=["Pearson-correlation","Cosine-similarity"])

    st.empty()
    if isRecommend:
        with st.container(border=True):
            st.write("Movie Recommendations")
            def getRecommendations() -> pd.DataFrame:
                popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
                if relationship=="Pearson-correlation":
                    results=item_based_pearson.loc[item_based_pearson['QueryMovieTitle']==fav_movie]['CandidateMovieTitle'][:number_recommendations].values
                    results=pd.DataFrame(results,columns=['Title\'s'])
                    print(results)

                elif relationship=="Cosine-similarity":
                    movieID=orig_movies.loc[orig_movies.Title==fav_movie]['Movie ID'].unique().min()
                    movieIndices=item_based_cosine.loc[movieID].sort_values(ascending=False).index.to_list()
                    movieIndices.remove(movieID)
                    movieIndices=movieIndices[:number_recommendations]
                    results=pd.DataFrame(orig_movies.loc[orig_movies['Movie ID'].isin(movieIndices)]['Title'].unique(),columns=['Title\'s'])
                return results

            results=getRecommendations()
            st.dataframe(results,use_container_width=True,hide_index=True)

with user_tab:
    number_recommendations=0
    st.write("#### User-based Recommendation system")
    st.divider()
    user_ID=st.selectbox(label="Please select your user ID !..",options=load_random_movies("user_tab"))
    st.empty()
    number_recommendations=st.slider(label="Please select the number of movies to be recommended !!",min_value=1,max_value=20,key="user")
    st.empty()
    isRecommend = st.button(label="Recommend!",type="primary",key="userButton")
    st.empty()

    if isRecommend:
        results=[]
        popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
        movies_rated = interaction_MF.loc[user_ID].sort_values(ascending=False).index.to_list()[:number_recommendations]
        for movie in movies_rated:
            results.append(orig_movies.loc[orig_movies['Movie ID']==movie]['Title'].values[:1][-1])
        results=pd.DataFrame(results,columns=['Title\'s'])
        with st.container(border=True):
            st.dataframe(results,use_container_width=True,hide_index=True)
