import streamlit as st
import pandas as pd
import pickle
import numpy as np

st.set_page_config(page_title="Movie Recommender System")

def displayResult(error,results):                   #Function to display the generated results
    with st.container(border=True):
            st.write("Movie Recommendations")
            if not error:
                st.dataframe(results,use_container_width=True,hide_index=True)

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
        active_users=sorted(active_user_index)     #Returning the Sorted list of Active users..
        return active_users


st.title("OTT Recommendation System")
error=False
st.empty()
item_tab,user_tab=st.tabs(["Item-based","User-based"])
with item_tab:
    col1,col2=st.columns([0.7,0.3])
    with col1:
        st.write("#### Item-based Recommendation system")
        st.divider()
        fav_movie=st.selectbox(label="Please select your favorite movie !..",options=load_random_movies("item_tab"),index=None)
        st.empty()
        number_recommendations=st.slider(label="Please select the number of movies to be recommended !!",min_value=1,max_value=20,key="item")
        st.empty()
        isRecommend = st.button(label="Recommend!",type="primary",key="itemButton")

    with col2:
        relationship=st.radio(label="Type of measuring relationship ?",options=["Relationship-1","Relationship-2"],index=None)

    st.empty()
    if isRecommend and relationship!=None and fav_movie!=None:
        error=False
        def getRecommendations() -> pd.DataFrame:
                popular_movies,active_user_index,user_details,orig_movies,item_based_pearson,item_based_cosine,interaction_MF=load_required_data()
                if relationship=="Relationship-1":
                    results=item_based_pearson.loc[item_based_pearson['QueryMovieTitle']==fav_movie]['CandidateMovieTitle'][:number_recommendations].values
                    results=pd.DataFrame(results,columns=['Title\'s'])
                    print(results)

                elif relationship=="Relationship-2":
                    movieID=orig_movies.loc[orig_movies.Title==fav_movie]['Movie ID'].unique().min()
                    movieIndices=item_based_cosine.loc[movieID].sort_values(ascending=False).index.to_list()
                    movieIndices.remove(movieID)
                    movieIndices=movieIndices[:number_recommendations]
                    results=pd.DataFrame(orig_movies.loc[orig_movies['Movie ID'].isin(movieIndices)]['Title'].unique(),columns=['Title\'s'])
                return results

        results=getRecommendations()
        displayResult(error,results)

    elif isRecommend and (relationship==None or fav_movie==None):
        st.error("Please check if all the above fields are filled before hitting \"Recommend!\"")

with user_tab:
    number_recommendations=0
    st.write("#### User-based Recommendation system")
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
            movies_rated = interaction_MF.loc[user_ID].sort_values(ascending=False).index.to_list()[:number_recommendations]
            for movie in movies_rated:
                results.append(orig_movies.loc[orig_movies['Movie ID']==movie]['Title'].values[:1][-1])

        elif isExisting=="No":
            error=False
            results=orig_movies.loc[orig_movies['Movie ID'].isin(popular_movies)]['Title'].unique()[:number_recommendations]

        elif isExisting=="Yes" and user_ID==None:
            error=True
            st.error("Please check if all the above fields are filled before hitting \"Recommend!\"")

        if isExisting != None:
            results=pd.DataFrame(results,columns=['Title\'s'])
            displayResult(error,results)
        


