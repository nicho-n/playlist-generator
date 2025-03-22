import time
import requests
import spotipy
from google.cloud import logging
from dotenv import load_dotenv

def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception(f"Missing required file: {file_path}")

# Initialize Google Cloud Logging
client = logging.Client()
logger = client.logger("spotify_flux_logger")

# Load environment variables
load_dotenv()

# Spotify API credentials from environment variables
ACCESS_TOKEN_FILE = "access_token.txt"
CLIENT_ID = read_file("client_id.txt")
CLIENT_SECRET = read_file("client_secret.txt")
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYLIST_ID = "3Oof1Q9vwZpJrj0L9ohkOc"
REFRESH_TOKEN = read_file(ACCESS_TOKEN_FILE)

# API URL for the current track
FLUX_URL = "https://fluxmusic.api.radiosphere.io/channels/c7d49649-081e-4790-adda-99d8e22b19a5/current-track"

last_song = None  # Store the last fetched song

def refresh_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to refresh token: {response.json()}")
        logger.log_text(f"Failed to refresh token: {response.json()}", severity="ERROR")
        raise Exception(f"Failed to refresh token: {response.json()}")

def get_spotify_client():
    access_token = refresh_access_token()
    return spotipy.Spotify(auth=access_token)

def get_current_song():
    global last_song
    current_time = int(time.time() * 1000)
    response = requests.get(FLUX_URL, params={"time": current_time})
    
    if response.status_code == 200:
        data = response.json()
        song_name = data.get('trackInfo', {}).get('title', 'Unknown Track')
        artist_name = data.get('trackInfo', {}).get('artistCredits', 'Unknown Artist')
        current_song = f"{song_name} by {artist_name}"
        
        if current_song == last_song:
            print("Song is the same as before. Skipping Spotify API call.")
            logger.log_text("Song is the same as before. Skipping Spotify API call.", severity="INFO")
            return None
        
        last_song = current_song
        return current_song
    else:
        print(f"Failed to fetch current track. Status code: {response.status_code}")
        logger.log_text(f"Failed to fetch current track. Status code: {response.status_code}", severity="ERROR")
        return None

def add_song_to_playlist(song, sp, playlist_id):
    song_details = song.strip().split(' by ')
    if len(song_details) != 2:
        print(f"Invalid song format: {song}")
        logger.log_text(f"Invalid song format: {song}", severity="WARNING")
        return
    
    song_name, artist_name = song_details
    track_uri = search_spotify(song_name, artist_name, sp)
    if track_uri:
        existing_tracks = get_playlist_tracks(sp, playlist_id)
        if track_uri not in existing_tracks:
            if len(existing_tracks) >= 9900:
                oldest_track = existing_tracks[-1]
                sp.user_playlist_remove_all_occurrences_of_tracks(sp.current_user()['id'], playlist_id, [oldest_track])
                print("Removed oldest track to maintain playlist size limit.")
                logger.log_text("Removed oldest track to maintain playlist size limit.", severity="INFO")
            sp.user_playlist_add_tracks(sp.current_user()['id'], playlist_id, [track_uri], position=0)
            print(f"Added {song_name} by {artist_name} to the top of the playlist.")
            logger.log_text(f"Added {song_name} by {artist_name} to the top of the playlist.", severity="INFO")
        else:
            print(f"{song_name} by {artist_name} is already in the playlist.")
            logger.log_text(f"{song_name} by {artist_name} is already in the playlist.", severity="INFO")
    else:
        print(f"Could not find {song_name} by {artist_name} on Spotify.")
        logger.log_text(f"Could not find {song_name} by {artist_name} on Spotify.", severity="INFO")

def search_spotify(song_name, artist_name, sp):
    query = f"track:{song_name} artist:{artist_name}"
    result = sp.search(query, limit=1, type="track", market="US")
    
    if result['tracks']['items']:
        return result['tracks']['items'][0]['uri']
    return None

def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            tracks.append(item['track']['uri'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return tracks

def run_script():
    current_song = get_current_song()
    
    if current_song:
        sp = get_spotify_client()
        add_song_to_playlist(current_song, sp, PLAYLIST_ID)
    
    time.sleep(180)

if __name__ == "__main__":
    print("Starting app...")
    logger.log_text("Starting app...", severity="INFO")
    while True:
        run_script()
