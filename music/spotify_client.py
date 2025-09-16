import os
import requests

def get_track_details(track_id):
    api_key = os.getenv('SPOTIFY_API_KEY')
    url = f"https://spotify23.p.rapidapi.com/tracks/"
    
    querystring = {"ids":track_id}
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Key": "spotify23.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:{response.status_code}")
        return None
