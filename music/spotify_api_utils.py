import os
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta


SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'


SCOPES = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-recently-played user-top-read playlist-read-private user-library-read streaming app-remote-control user-follow-read'

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

def refresh_spotify_token(refresh_token):
    """Refreshes the Spotify access token using the refresh token."""
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    # THIS IS THE LINE TO FIX: Change 'posts' to 'post'
    response = requests.post(token_url, headers=headers, data=data) 
    response.raise_for_status() # Raise an exception for HTTP errors
    return response.json()


def get_user_profile(access_token):
    headers = {
        'AUTHORIZATION': f'Bearer {access_token}'
    }
    response = requests.get(f'{SPOTIFY_API_BASE_URL}/me', headers=headers)
    response.raise_for_status()
    return response.json()
    
def is_token_expired(request):
    expires_at_str = request.session.get('spotify_token_expires_at')
    if not expires_at_str:
        return True
    expires_at = datetime.fromisoformat(expires_at_str)
    return datetime.now() >= (expires_at - timedelta(minutes=5))

def get_spotify_access_token(request):
    access_token = request.session.get('spotify_access_token')
    refresh_token = request.session.get('spotify_refresh_token')
    
    if not access_token:
        return None
    
    if is_token_expired(request):
        if refresh_token:
            try:
                new_tokens = refresh_spotify_token(refresh_token)
                request.session['spotify_access_token'] = new_tokens['access_tokens']
                request.session['spotify_token_expires_at'] = (
                    datetime.now() + timedelta(seconds=new_tokens['expires_in'])
                ).isoformat()
                return new_tokens['access_token']
            except requests.exceptions.HTTPError as e:
                print(f"Token refersh failed: {e}")
                request.session.pop('spotify_access_token', None)
                request.session.pop('spotify_refresh_token', None)
                request.session.pop('spotify_token_expires_at', None)
                return None
            
        else: 
            return None
    
    return access_token
    
    
def make_spotify_api_call(request, endpoint, method='GET', data=None):
    access_token = get_spotify_access_token(request)
    if not access_token:
        return {'error':'No valid Spotify access token.'}
    
    headers = {
        'Authorization':f'Bearer{access_token}',
        'Content-Type':'application/json'
    }
    
    url = f'{SPOTIFY_API_BASE_URL}{endpoint}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            response = requests.get(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.get(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return {'error':'Unsupported HTTP Method'}
        
        response.raise_for_status()
        
        if response.status_code ==  204:
            return {}
        
        return response.json()
       
    except requests.exceptions.HTTPError as e:
        if e.response.status_code ==  401:
            request.session.pop('spotify_access_token', None)
            request.session.pop('spotify_refresh_token', None)
            request.session.pop('spotify_token_expires_at]', None)
            return {'error':'Spotify token invalid or revoked. Please log in again'}
        return {'error':f'Spotify API error:{e.response.status_code}-{e.response.text}'}
    except requests.exceptions.RequestException as e:
        return {'error':f'Network/Request Error: {e}'}
    