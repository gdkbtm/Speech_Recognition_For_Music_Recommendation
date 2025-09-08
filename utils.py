
import speech_recognition as sr
from collections import Counter
from fuzzywuzzy import fuzz
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