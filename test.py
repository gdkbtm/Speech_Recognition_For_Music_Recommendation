from thefuzz import process

song_lyrics_db = {
    "Queen - Bohemian Rhapsody": "Is this the real life? Is this just fantasy? Caught in a landslide, no escape from reality. Open your eyes, look up to the skies and see.",
    "Led Zeppelin - Stairway to Heaven": "There's a lady who's sure all that glitters is gold, and she's buying a stairway to heaven. When she gets there she knows, if the stores are all closed, with a word she can get what she came for.",
    "The Beatles - Yesterday": "Yesterday, all my troubles seemed so far away. Now it looks as though they're here to stay. Oh, I believe in yesterday.",
    "The Police - Every Breath You Take": "Every breath you take, and every move you make, every bond you break, every step you take, I'll be watching you.",
}   


def find_song_by_lyrics(query, lyrics_database):
    """
    Finds the song that best matches a snippet of lyrics.
    
    Args:
        query (str): The lyric snippet to search for.
        lyrics_database (dict): A dictionary mapping song titles to lyrics.
        
    Returns:
        tuple: A tuple containing the best matching song title and its score,
               or None if no match is found.
    """
    choices = lyrics_database.values()
    
    # Use partial_ratio to handle short queries matching parts of longer strings
    best_match_lyrics, score = process.extractOne(query, choices, scorer=process.extractOne)
    
    if score < 70: # Set a minimum confidence threshold
        return None, score

    # Find the corresponding song title for the best matching lyrics
    for song_title, lyrics in lyrics_database.items():
        if lyrics == best_match_lyrics:
            return song_title, score

    return None, 0

# Example usage
query = "all that glitters is gold, and she's buying a stairway"
song, similarity_score = find_song_by_lyrics(query, song_lyrics_db)

if song:
    print(f"Query: '{query}'")
    print(f"Best match found: '{song}' with a score of {similarity_score}")
else:
    print(f"No strong match found for '{query}'.")
