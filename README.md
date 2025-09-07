# Project Overview: Recognize user speech to recognize an artist, fuzzy search the speech words to match artists from data sourse. Get songs for the artist and get recommendation for similar artists based on genre
- Collects the user input from microphone for an music artist to be seached. Fuzzy search the voice input within data collection.
  Match if fuzzy search is >= 75%. Example, Mike Jackson will be matched Michael jackson
- Optimized ``K-Nearest Neighbors`` algorithm to recommend top songs that match user's input and its genre
- Creates a CSV file for given artist (from voice input) songs based on input. Default to first 50 songs.
- Creates a CSV file for recommended artists (based on genre) songs. Default to first 50 songs.

## Code and Resources Used
**Python Version:** 3.13 <br>
**Packages:** pandas, numpy, sklearn, speech_recognition, fuzzywuzzy<br>
**Data Source:** https://www.kaggle.com/datasets/saurabhshahane/spotgen-music-dataset <br>
**Python Speech Recognition Package:** https://realpython.com/python-speech-recognition/ <br>

Installing SpeechRecognition
- Install SpeechRecognition from a terminal with pip
  $ pip install SpeechRecognition

The Speech Recognizer Class
The primary purpose of a Recognizer instance is, of course, to recognize speech. Each instance comes with a variety of settings and functionality for recognizing speech from an audio source.
Create a Recognizer 
$ r = sr.Recognizer()

To Run the application
Connect a microphone to the system. Type on terminal 
% python music_search_by_speech.py
Application starts and see on console -
    "This script is running..."
    "Say artist name to get song recommendations"
Say artist's name in microphone clearly like 'Michael Jackson', 'Taylor Swift'
The application search the artist and creates csv files for song recommendation if pass. The cvs files are in music_data directory.
Prints "Could not understand audio.", if fails and iterates the search again for user input.
The application terminates after 3 attempts, if no input from the user.



 
