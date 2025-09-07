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
    #
    artistName_as_db = str

    df = df.drop_duplicates(subset=['uri'], keep='first')
    #add new column
    if(len(name) > 0):
        df['artists_name_lower'] = df['artists_name'].str.lower()
        #df['artists_name'] = df['artists_name'].str.lower()
        row_count = len(df)
        #conduct fuzzy search for artist voice input with database (csv file)
        #match the artist name 
        #like if voice says 'Simon and Garfunkel', then match with 'Simon & Garfunkel' from csv file
        df, name, artistName_as_db = fuzzySearch(df, name, artistName_as_db)       
        #a = fuzz.ratio(df['artists_name_lower'], name.lower())
        filtered_df = df[df['artists_name_lower'] == name.lower()]
        print('filtered_df size', filtered_df)
        df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    #print('filtered_df.genres ', len(filtered_df))
    
    return exploded_track_df, filtered_df, artistName_as_db

# Define function to return Spotify URIs and audio feature values of top neighbors (ascending)
def n_neighbors_uri_audio(artistName_as_db, exploded_track_df, filtered_df, artist_select, start_year, end_year):
    # The artist given
    if(len(artist_select) > 0):
        print('The artist given: ', artistName_as_db)
        print('filtered_df.genres: ', filtered_df.genres)
        print('The found in csv files: ')
        #find the duplicate ganre in all rows and select the max one
        genre = find_highest_duplicate(filtered_df.genres)
        #get the genre string value
        genre = get_artist_genre(genre)
        print('The genre of the given artist: ', genre)
        print('The start year: ', min(filtered_df.release_year))
        print('The end year: ', max(filtered_df.release_year))
        #test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
        print('The acousticness: ', min(filtered_df.acousticness))
        print('The acousticness: ', max(filtered_df.acousticness))
        print('The danceability: ', min(filtered_df.danceability))
        print('The danceability: ', max(filtered_df.danceability))
        print('The energy: ', min(filtered_df.energy))
        print('The energy: ', max(filtered_df.energy))
        print('The instrumentalness: ', min(filtered_df.instrumentalness))
        print('The instrumentalness: ', max(filtered_df.instrumentalness))
        print('The valence: ', min(filtered_df.valence))
        print('The valence: ', max(filtered_df.valence))
        print('The tempo: ', min(filtered_df.tempo))
        print('The tempo: ', max(filtered_df.tempo))

    #print('nnnnn ', filtered_df.release_year)
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
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:50] # use only top 500 most popular songs
    print(len(genre_data))
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
    #print('Artists set before removing the given artist from the list: ', len(artists_id), len(artists_name))

    if(len(artist_select) > 0):    
        liRecommend_Artist = [] 
        liSelect_Artist = []
        #print(artists_name, artistName_as_db)
        #indices_to_remove = np.where(artists_name_lower == 'america')
        indices_to_remove = np.where(genre_data['artists_name_lower'] == artistName_as_db)
        indices_to_remain = np.where(genre_data['artists_name_lower'] != artistName_as_db)

        #print(indices_to_remove)
        uris = np.delete(uris, indices_to_remove)
        audios = np.delete(audios, indices_to_remove)
        artists_id = np.delete(artists_id, indices_to_remove)
        artists_name = np.delete(artists_name, indices_to_remove)
        artist_info = np.delete(artist_info, indices_to_remove)
        #print('After remove the entries from the list: ', len(artists_id), len(artists_name))

        genre_data_new = genre_data
        #print(genre_data)
        #print(indices_to_remove)
        indices_to_remove = str(indices_to_remove)[8:-4]
        #print(indices_to_remove)
        #print('Before ', len(genre_data))
       
        indices_to_remove = indices_to_remove.split(',')
        for iRemove in indices_to_remove:
            i = int(iRemove.strip())
            #print(genre_data.index[i])
            liRecommend_Artist.append(genre_data.index[i])
        for iRemove in liRecommend_Artist:
            #i = int(iRemove.strip())
            #print('TTTT ', iRemove)
            genre_data = genre_data.drop(iRemove)
            #print('After ', len(genre_data))
            #genre_data = liRecommend_Artist
        #print('After ', len(genre_data))

        #print(indices_to_remain)
        indices_to_remain = str(indices_to_remain)[8:-4]
        indices_to_remain = indices_to_remain.split(',')
        #print(indices_to_remain)
        for iRemove in indices_to_remain:
            i = int(iRemove.strip())
            #print(genre_data_new.index[i])
            liSelect_Artist.append(genre_data_new.index[i])
        for iRemove in liSelect_Artist:
            #i = int(iRemove.strip())
            #print('VVVVV ', iRemove)
            genre_data_new = genre_data_new.drop(iRemove)
            #print('After ', len(genre_data))
            #genre_data = liRecommend_Artist
        #print('After ', len(genre_data_new))

    return genre, genre_data, genre_data_new, uris, audios, artists_id, artists_name, artist_info

def getSongInfo(exploded_track_df, filtered_df, artistName, artistName_as_db):
    print('mmmm ', artistName)
    if(len(filtered_df) > 0):
        start_year = 1960
        end_year = 2000
        genre, genre_data, genre_data_new, uris, audios, artists_id, artists_name, artist_info = n_neighbors_uri_audio(artistName_as_db, exploded_track_df, filtered_df, artistName, start_year, end_year)               
    else:
        print('No match found for the artist', artistName)

    return genre_data, genre_data_new
          
if __name__ == '__main__':
    #counter to terminate after no input from user after 3 attempts
    count = 0;

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
            print(count)
            if(count == 3):
                print("No input detected. Terminating the program.")
                break
            
        time.sleep(5)  # Pause for 5 seconds to prevent excessive CPU usage

