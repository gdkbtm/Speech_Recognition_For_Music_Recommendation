
import speech_recognition as sr
from collections import Counter
import pandas as pd
import math

from fuzzywuzzy import fuzz, process
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

#conduct fuzzy search for artist voice input with database (csv file)
def fuzzySearchForLyrics(df, name, artistName_as_db):
    print('fuzzySearchForLyrics')
    artistMatch = False
    getMatchingSegment(df, name, artistName_as_db)
    #for i in df['name_lower']:
        #match voice input with artist name from the list
        
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

def getMatchingSegment(df, search_lyrics, artistName_as_db):
    # Option 1: Using partial_ratio to check if the group is a close match to a substring
  
    print(search_lyrics)
 
    print(df['lyrics'])
    find_lyrics = df['lyrics']
    data1 = {
        'name': [
            find_lyrics
        ]
        }
    '''
    # Create two sample DataFrames representing large datasets
    data1 = {     
        'name': [
        """
            Hello darkness, my old friend
            I've come to talk with you again
            Because a vision softly creeping
            Left its seeds while I was sleeping
            And the vision that was planted in my brain
            Still remains
            Within the sound of silence
            In restless dreams, I walked alone
            Narrow streets of cobblestone
            'Neath the halo of a street lamp
            I turned my collar to the cold and damp
            When my eyes were stabbed by the flash of a neon light
            That split the night
            And touched the sound of silence
            And in the naked light, I saw
            Ten thousand people, maybe more
            People talking without speaking
            People hearing without listening
            People writing songs that voices never shared
            And no one dared
            Disturb the sound of silence
            "Fools" said I, "You do not know
            Silence like a cancer grows
            Hear my words that I might teach you
            Take my arms that I might reach you"
            But my words, like silent raindrops fell
            And echoed in the wells of silence
            And the people bowed and prayed
            To the neon god they made
            And the sign flashed out its warning
            In the words that it was forming
            Then the sign said, "The words of the prophets are written on the subway walls
            In tenement halls"
            And whispered in the sound of silence
            """, 
            """     
            On a dark desert highway, cool wind in my hair
            Warm smell of colitas, rising up through the air
            Up ahead in the distance, I saw a shimmering light
            My head grew heavy and my sight grew dim
            I had to stop for the night
            There she stood in the doorway
            I heard the mission bell
            And I was thinking to myself
            "This could be Heaven or this could be Hell"
            Then she lit up a candle and she showed me the way
            There were voices down the corridor
            I thought I heard them say
            
            Welcome to the Hotel California
            Such a lovely place (Such a lovely place)
            Such a lovely face
            Plenty of room at the Hotel California
            Any time of year (Any time of year)
            You can find it here
            
            Her mind is Tiffany-twisted, she got the Mercedes bends
            She got a lot of pretty, pretty boys she calls friends
            How they dance in the courtyard, sweet summer sweat
            Some dance to remember, some dance to forget
            
            So I called up the Captain
            "Please bring me my wine."
            He said, "We haven't had that spirit here since nineteen sixty nine."
            And still those voices are calling from far away
            Wake you up in the middle of the night
            Just to hear them say
            
            Welcome to the Hotel California
            Such a lovely place (Such a lovely place)
            Such a lovely face
            They livin' it up at the Hotel California
            What a nice surprise (what a nice surprise)
            Bring your alibis
            
            Mirrors on the ceiling
            The pink champagne on ice
            And she said "We are all just prisoners here, of our own device"
            And in the master's chambers
            They gathered for the feast
            They stab it with their steely knives
            But they just can't kill the beast
            
            Last thing I remember
            I was running for the door
            I had to find the passage back to the place I was before
            "Relax," said the night man
            "We are programmed to receive
            You can check-out any time you like
            But you can never leave!"
            """,
            """
            A winter's day
            In a deep and dark December
            I am alone
            Gazing from my window to the streets below
            On a freshly fallen silent shroud of snow
            I am a rock I am an island
            I've built walls
            A fortress deep and mighty
            That none may penetrate
            I have no need of friendship, friendship causes pain
            It's laughter and it's loving I disdain
            I am a rock I am an island
            Don't talk of love
            Well I've heard the word before
            It's sleeping in my memory
            I won't disturb the slumber of feelings that have died
            If I never loved I never would have cried
            I am a rock I am an island
            I have my books
            And my poetry to protect me
            I am shielded in my armor
            Hiding in my room safe within my womb
            I touch no one and no one touches me
            I am a rock I am an island
            And a rock feels no pain
            And an island never cries
            """
        ]
    }
    ''' 
    df1 = pd.DataFrame(data1)

    data2 = {   
        #'songName': ['Hotel California - Remaster 2013']
        'songName': [search_lyrics]
    }
    #data2 = {   
    #    'Company_Name': ['Apple Corps']
    #}
    df2 = pd.DataFrame(data2)

    # Define a function for fuzzy matching
    def fuzzy_match_company(name, choices, scorer=fuzz.token_set_ratio, score_cutoff=60):
        """
        Performs fuzzy matching to find the best match for a given name
        within a list of choices, returning the matched name and its score.
        """
        match = process.extractOne(name, choices, scorer=scorer, score_cutoff=score_cutoff)
        if match:
            return match[0], match[1]  # Return matched name and score
        return None, None  # No match found above cutoff

    # Extract the list of company names from df2 for matching
    company_choices = df2['songName'].tolist()
    
    # Apply the fuzzy matching function to each name in df1
    # This creates new columns for the matched company name and its score
    #df1[['Matched_Company', 'Match_Score']] = df1['name'].apply(
    #    lambda x: pd.Series(fuzzy_match_company(x, company_choices))
    #)
    df1[['name','Match_Score']] = df1['name'].apply(
        lambda x: pd.Series(fuzzy_match_company(x, company_choices))
    )
    print(df1)
    print(df1['Match_Score'])

    max_value_col_A = df1['Match_Score'].idxmax()
    print('max_value_col_A ', max_value_col_A)
    print(math.isnan(max_value_col_A))
    #if(max_value_col_A.isna()):
    if(math.isnan(max_value_col_A) == False):
        print(data1['name'][max_value_col_A])
    else:
        print('No matching found for the input.')
