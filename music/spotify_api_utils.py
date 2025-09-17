import os
import requests
from urllib.parse import urlencode


SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'

SCOPES = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-recently-played user-top-read playlist-read-private user-library-read streaming'

def get_spotify_auth_url():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': SCOPES,
        'show_dialog':True
    }
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

def get_spotify_tokens(code):
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data = {
            'grant_type':'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
            }
    )
    response.raise_for_status() #It raises HTTP Error whenever a bas response occurs
    return response.json()

def refresh_spotify_token(refresh_token):
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    response = requests.posts(
        SPOTIFY_TOKEN_URL,
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    response.raise_for_status()
    return response.json()

def get_user_profile(access_token):
    headers = {
        'AUTHORIZATION': f'Bearer {access_token}'
    }
    response = requests.get(f'{SPOTIFY_API_BASE_URL}/me', headers=headers)
    response.raise_for_status()
    return response.json()
    