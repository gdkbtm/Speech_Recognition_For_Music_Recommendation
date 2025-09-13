
import speech_recognition as sr
from collections import Counter
import pandas as pd
import math
import glob
import re
#from fuzzywuzzy import fuzz, process
from rapidfuzz import process, fuzz

import os

def setMicrophone():
    artistName = str
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say artist name to get song recommendations")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        # Use Google Web Speech API
        artistName = r.recognize_google(audio)
        print("You said: " + artistName)
    except sr.UnknownValueError:
        print("Could not understand audio.")
        artistName = ''
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition")
        artistName = ''
 
    return artistName

#find the duplicate ganre in all rows and select the max one
def find_highest_duplicate(arr): 
    counts = Counter(arr)
    duplicates = [item for item, count in counts.items() if count > 1]
    no_duplicates = [item for item, count in counts.items() if count == 1]
    if duplicates:
        return max(duplicates)
    else:
        return max(no_duplicates)

#Select the genre from the row
def get_artist_genre(highest_dup):   
    first_token = highest_dup.split(',')
    #print('first_token ', first_token)
    if len(first_token) > 1:
        highest_dup = str(highest_dup)[1:-1]
        highest_dup = highest_dup.split(',')[0]
        highest_dup = str(highest_dup)[1:-1]
    else:
        highest_dup = str(highest_dup)[2:-2]
    return highest_dup;

#conduct fuzzy search for artist voice input with database (csv file)
def fuzzySearch(df, name, artistName_as_db):
    artistMatch = False
    for i in df['artists_name_lower']:
        #match voice input with artist name from the list
        a = fuzz.ratio(str(i), name.lower())
        #if match is 75%, then match the input with closest artist from the list
        if(a >= 75):
            name = i
            artistName_as_db = i
            artistMatch = True
            break
    return df, name, artistName_as_db, artistMatch

#creates CSV files for user songs (artist_selected_songs.csv) and recommended artists (artist_recommend_songs)
def create_artist_recommend(genre_data, genre_data_for_artist, genre_data_for_Recommend, artistName):
    temp_folder_path = 'music_data'
    # Saving a CSV file of the dataset for predicting purposes.
    artist_recommend_file = 'artist_recommend_songs.csv'
    artist_select_file = 'artist_selected_songs.csv'

    csv_predict = genre_data.drop(columns=['popularity'])
    # The number of data points we want to predict on when calling mlflow pyfunc predict.
    num_pred = 500
    #csv_predict[:num_pred].to_csv(os.path.join(temp_folder_path, "artists_new.csv"), index=False)
    # This CSV file contains the price of the tested diamonds.
    genre_data_for_Recommend[["artists_name", "name", "genres", "release_year", "popularity"]][:num_pred].to_csv(os.path.join(temp_folder_path, artist_recommend_file),
                                index=False)
    genre_data_for_artist[["artists_name", "name", "genres", "release_year", "popularity"]][:num_pred].to_csv(os.path.join(temp_folder_path, artist_select_file),
                                index=False)
    print('Artists recommend songs file ', artist_recommend_file, 'for', artistName, "is created.")
  
def getSongNameFromUser(user_input):
    song_lyrics_required = str
    keyword_pattern = "lyrics of"
    song_lyrics_required = str
    
    regex_pattern = keyword_pattern + "(.*)"
    
    match = re.search(regex_pattern, user_input)
    #print('match ', match)
    if match:
        found_string_and_rest = match.group(0)
        rest_part = match.group(1)
        print("Full match: ", found_string_and_rest)
        print("Rest part: ", rest_part.strip())
        song_lyrics_required = rest_part.strip()
        return song_lyrics_required;
    else:
        return None

def fuzzy_search_chunked_glob(fileName, searchSong, targetColumn, chunk_size=10000):

    strLyrics = str
    strSongName = searchSong
    #List to print header
    liName = []
    liArtist = []
    liPopularity = []
    all_matches = []
    headerData = {}
    max_index = 0

    chunks = pd.read_csv(fileName, chunksize=chunk_size)
    df = chunks

    for chunk in chunks:   
        # Extract the column you want to search from the current chunk
        columnData = chunk[targetColumn].tolist()
        #print(len(columnData))
        #convert column data to lower case
        columnData = [item.lower() for item in columnData]
        searchSong = searchSong.lower()
        # Perform fuzzy search within this chunk
        # You can adjust the scorer (e.g., fuzz.ratio, fuzz.partial_ratio) and threshold
        #matches_in_chunk = process.extract(search_term, column_data, scorer=fuzz.WRatio, score_cutoff=60)
        matches_in_chunk = process.extract(searchSong, columnData, scorer=fuzz.partial_ratio, score_cutoff=100)

        #print(matches_in_chunk)
        # Store the matches found in this chunk
        for match_text, score, index_in_chunk in matches_in_chunk:
            #print(match_text)
            original_row = chunk.iloc[index_in_chunk]
            #print(original_row.lyrics)
            all_matches.append({'match_text': match_text, 'score': score, 'original_row': original_row.to_dict()})
        #print('all_matches ', len(all_matches))

        if(len(all_matches) > 0):
            for match in all_matches:
                liName.append(match['original_row']['name']) 
                liArtist.append(match['original_row']['artists_name'])
                liPopularity.append(match['original_row']['popularity'])
            headerData = {
                "Song Name": liName,
                "Artist Name": liArtist,
                "Popularity": liPopularity
            }
            #print(all_matches[1]['original_row']['popularity'])
            li_all_matches = []
            for match in all_matches:
                li_all_matches.append(match['original_row']['popularity'])
                #print(match['original_row']['popularity'], match['original_row']['artists_name'])
            #convert to series
            s = pd.Series(li_all_matches)
            max_index = s.idxmax()
            #print(max_index)         
            strLyrics = all_matches[max_index]['original_row']['lyrics']
            strSongName = all_matches[max_index]['original_row']['name']
            #print(all_matches[max_index]['original_row']['lyrics'])
        else:
            strLyrics = ''
            #strSongName = search_term
            print('No match found')

        return all_matches, headerData, max_index, strSongName, strLyrics
    
