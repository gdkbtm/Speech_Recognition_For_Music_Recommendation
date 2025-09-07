# Import libraries
from utils import find_highest_duplicate, get_artist_genre, create_artist_recommend, fuzzySearch, setMicrophone

import glob
import pandas as pd
import datetime
from sklearn.neighbors import NearestNeighbors
import streamlit.components.v1 as components
from numpy.random import default_rng as rng
import numpy as np
import time

# Define list of genres and audio features of songs for audience to choose from
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]

def read_data():
    #global df  # Declare df as global within the function
    all_files = glob.glob("csv_data/*.csv")
    list_contact_csv = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        #add all csv data
        list_contact_csv.append(df) 
    df = pd.concat(list_contact_csv, axis=0, ignore_index=True)

    return df

def load_data(name):
    filtered_df = []
    df = read_data()
    # variable to store the artist name match from data source
    # If user input is Mike Jackson, the datasource match to Michael Jackson
    artistName_as_db = str

    df = df.drop_duplicates(subset=['uri'], keep='first')
    #add new column
    if(len(name) > 0):
        df['artists_name_lower'] = df['artists_name'].str.lower()
        row_count = len(df)
        #conduct fuzzy search for artist voice input with database (csv file)
        #match the artist name 
        #like if voice says 'Simon and Garfunkel', then match with 'Simon & Garfunkel' from csv file
        df, name, artistName_as_db = fuzzySearch(df, name, artistName_as_db)       
        filtered_df = df[df['artists_name_lower'] == name.lower()]
        #print('filtered_df size', filtered_df)
        df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    
    return exploded_track_df, filtered_df, artistName_as_db

# Define function to return Spotify URIs and audio feature values of top neighbors (ascending)
def n_neighbors_uri_audio(artistName_as_db, exploded_track_df, filtered_df, artist_select, start_year, end_year):
    # The artist given
    if(len(artist_select) > 0):
        print('The artist given: ', artistName_as_db)
        print('The found in csv files: ')
        #find the duplicate ganre in all rows and select the max one
        genre = find_highest_duplicate(filtered_df.genres)
        print('genre111 ', genre)
        #get the genre string value
        genre = get_artist_genre(genre)
        print('genre222 ', genre)
        print('The genre of the given artist: ', genre)
        print('The start year: ', min(filtered_df.release_year))
        print('The end year: ', max(filtered_df.release_year))       

    if(len(artist_select) == 0):
        genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    else:
        genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=min(filtered_df.release_year)) & (exploded_track_df["release_year"]<=max(filtered_df.release_year))]
        #calculate test_feat from given attributes 
        #get the max and and min for the artist and get the difference 
        acousticness = (max(filtered_df.acousticness) - min(filtered_df.acousticness))/2
        danceability = (max(filtered_df.danceability) - min(filtered_df.danceability))/2
        energy = (max(filtered_df.energy) - min(filtered_df.energy))/2
        instrumentalness = (max(filtered_df.instrumentalness) - min(filtered_df.instrumentalness))/2
        valence = (max(filtered_df.valence) - min(filtered_df.valence))/2
        tempo = (max(filtered_df.tempo) - min(filtered_df.tempo))/2
        test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500] # use only top 500 most popular songs
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
    
    #Search nearest neighbor
    artists_name_lower = genre_data.iloc[n_neighbors]['artists_name_lower'].to_numpy()
    artists_id = genre_data.iloc[n_neighbors]['artists_id'].to_numpy()    
    artists_name = genre_data.iloc[n_neighbors]['artists_name'].to_numpy()
    artist_info = [genre_data.iloc[n_neighbors]['artists_id'].to_numpy(), genre_data.iloc[n_neighbors]['artists_name'].to_numpy()]
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()

    if(len(artist_select) > 0):    
        liRecommend_Artist = [] 
        liSelect_Artist = []
        #Remove user input arists songs from the list
        indices_to_remove = np.where(genre_data['artists_name_lower'] == artistName_as_db)
        #Remove all other arists songs and keep only user input arists songs
        indices_to_remain = np.where(genre_data['artists_name_lower'] != artistName_as_db)

        uris = np.delete(uris, indices_to_remove)
        audios = np.delete(audios, indices_to_remove)
        artists_id = np.delete(artists_id, indices_to_remove)
        artists_name = np.delete(artists_name, indices_to_remove)
        artist_info = np.delete(artist_info, indices_to_remove)

        #genre_data_new is for to filter out artists songs.
        #genre_data is for to filter out recommended artists songs.
        genre_data_new = genre_data
        indices_to_remove = str(indices_to_remove)[8:-4]
         
        indices_to_remove = indices_to_remove.split(',')
        for iRemove in indices_to_remove:
            i = int(iRemove.strip())
            liRecommend_Artist.append(genre_data.index[i])
        for iRemove in liRecommend_Artist:
             genre_data = genre_data.drop(iRemove)
       
        indices_to_remain = str(indices_to_remain)[8:-4]
        indices_to_remain = indices_to_remain.split(',')
        for iRemove in indices_to_remain:
            i = int(iRemove.strip())
            liSelect_Artist.append(genre_data_new.index[i])
        for iRemove in liSelect_Artist:
            genre_data_new = genre_data_new.drop(iRemove)
 
    return genre, genre_data, genre_data_new, uris, audios, artists_id, artists_name, artist_info

def getSongInfo(exploded_track_df, filtered_df, artistName, artistName_as_db):
    if(len(filtered_df) > 0):
        start_year = 1960
        end_year = 2000
        genre, genre_data, genre_data_new, uris, audios, artists_id, artists_name, artist_info = n_neighbors_uri_audio(artistName_as_db, exploded_track_df, filtered_df, artistName, start_year, end_year)               
    else:
        print('No match found for the artist', artistName)

    return genre_data, genre_data_new
          
if __name__ == '__main__':
    #counter to terminate after no input from user after 3 attempts
    count = 1;

    while True:
        # Your code to be executed repeatedly goes here
        print("This script is running...")
        # Create a Recognizer object        
        artistName = setMicrophone()
        print('Name ', artistName)
        if(len(artistName) > 0):
            exploded_track_df, filtered_df, artistName_as_db = load_data(artistName)
            if(len(filtered_df) > 0):
                genre_data, genre_data_new = getSongInfo(exploded_track_df, filtered_df, artistName, artistName_as_db)
                create_artist_recommend(genre_data, genre_data_new, artistName)
                 #reset the counter
                count = 0 
            else:
                print("Could not understand input audio.")                     
        else:
            print("Could not understand input audio.")
            count += 1 
            print('The application try for 3 attempts and terminates. Attempt number: ', count)
            if(count == 4):
                print("No input detected. Terminating the program.")
                break
            
        time.sleep(5)  # Pause for 5 seconds to prevent excessive CPU usage

