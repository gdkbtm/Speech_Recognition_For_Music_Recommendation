# Import libraries
from utils import setMicrophone, fuzzy_search_chunked_glob, getSongNameFromUser

import pandas as pd
from numpy.random import default_rng as rng
import numpy as np
import time

def setSongNameFromUser(user_input):
    all_matches = []
    strLyrics = str
    strSongName = str
    headerData = {}

    song_lyrics_required = getSongNameFromUser(user_input)
    if(song_lyrics_required == None and len(user_input) > 0):
        song_lyrics_required = user_input
    if(len(song_lyrics_required) > 0):
        file_name = 'csv_data/filtered_track_df.csv'
        
        all_matches, headerData, max_index, strSongName, strLyrics = fuzzy_search_chunked_glob(file_name, song_lyrics_required, 'lyrics')
        printLyricsForTheSong(all_matches, headerData, max_index, strLyrics, strSongName)     
    else:
        print('Could not understand input audio. Please try again')

def printLyricsForTheSong(all_matches, headerData, max_index, strLyrics, strSongName):
    #strLyrics - not used here
    if(len(strLyrics) > 0 and len(headerData) > 0):   
        print('The following songs/lyrics are available from the data source:')    
        df = pd.DataFrame(headerData)
        print(df.to_string())
        print('')    
        print('Selecting', all_matches[max_index]['original_row']['artists_name'], 'song', all_matches[max_index]['original_row']['name'], 'based on popularity index', all_matches[max_index]['original_row']['popularity'] )
        print('Find the lyrics below:')
        print('')
        print(all_matches[max_index]['original_row']['lyrics'])             
        #print(strLyrics)
    else:
        print('No lyrics found for search song', strSongName)

if __name__ == '__main__':
    #counter to terminate after no input from user after 3 attempts
    count = 1;

    while True:
        # Your code to be executed repeatedly goes here
        print("This script is running...")
        # Create a Recognizer object        
        songName = setMicrophone()
        print('Name ', songName)
        #print('aaa ', artistName.find('lyrics'))
        if(len(songName) > 0):
            #if(songName.find('lyrics') != -1):       
            setSongNameFromUser(songName)   
            count = 0 
            #else:
            #   setSongNameFromUser(songName) 
            #    count = 0                                                   
        else:
            print("Could not understand input audio.")
            count += 1 
            print('The application try for 3 attempts and terminates. Attempt number: ', count)
            if(count == 4):
                print("No input detected. Terminating the program.")
                break
            
        time.sleep(5)  # Pause for 5 seconds to prevent excessive CPU usage

