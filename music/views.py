from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .spotify_api_utils import get_spotify_auth_url, get_spotify_tokens, get_user_profile, refresh_spotify_token, make_spotify_api_call
# Create your views here.

def spotify_login(request):
    auth_url = get_spotify_auth_url()
    return redirect(auth_url)

def spotify_call_back(request):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return render(request, 'music/error.html',{'message':f'Spotify login failed:{error}'})
    
    if code:
        try:
            tokens = get_spotify_tokens(code)
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in')
            expiration_time = datetime.now()+ timedelta(seconds=expires_in)
            
            #Storing tokens
            request.session['spotify_access_token'] = access_token
            request.session['spotify_refresh_token'] = refresh_token
            request.session['spotify_token_expires_at'] = expiration_time.isoformat()
            
            user_profile = get_user_profile(access_token)
            spotify_id = user_profile.get('id')
            
            user, created = User.objects.get_or_create(
                username = spotify_id,
                defaults= {
                    'first_name': user_profile.get('display_name'),
                    'email': user_profile.get('email')
                }
            )
            login(request, user)
            
            request.session['spotify_display_name'] = user_profile.get('display_name')
            request.session['spotify_profile_image'] = user_profile.get('images')[0]['url'] if user_profile.get('images') else None
            
            return redirect('dashboard')
            
        except request.exceptions.HTTPError as e:
            return render(request, 'music/error.html',{'message':f'Spotify token exchange failed: {e}'})
        except Exception as e:
            return render(request, 'music/error.html', {'message':f'An unexpected error occurred: {e}'})
        
    return render(request, 'music/error.hmtl', {'message':'Spotify authentication response missing code.'})

def spotify_logout(request):
    request.session.pop('spotify_access_token', None)
    request.session.pop('spotify_refresh_token', None)
    request.session.pop('spotify_token_expires_at', None)
    request.session.pop('spotify_user_id', None)
    request.session.pop('spotify_display_name', None)
    request.session.pop('spotify_profile_image', None)
    return redirect('home')

@login_required
def dashboard(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return  redirect('home')
    
    display_name = request.session.get('spotify_display_name','User')
    profile_image = request.session.get('spotify_profile_image')
    
    user_top_artists = []
    user_top_tracks = []
    user_playlists = []
    recently_played = []
    
    top_artists_response = make_spotify_api_call(request, '/me/top/artists?limit=5')
    if top_artists_response and not top_artists_response.get('error'):
        user_top_artists = top_artists_response.get('items',[])
        
    
        
    top_tracks_response = make_spotify_api_call(request, '/me/top/tracks?limit=5')
    if top_tracks_response and not top_tracks_response.get('error'):
        user_top_tracks = top_tracks_response.get('items',[])
    
    
    playlists_response = make_spotify_api_call(request, '/me/playlist?limit=5')
    if playlists_response and not playlists_response.get('error'):
        user_playlists = playlists_response.get('items',[])
    
    
    recently_played_response = make_spotify_api_call(request, '/me/player/recently_played?limit=5')
    if recently_played_response and not recently_played_response.get('error'):
        recently_played = recently_played_response.get('items',[])
   
    
    context = {
        'display_name': display_name,
        'profile_image': profile_image,
        'user_top_artists': user_top_artists,
        'user_top_tracks': user_top_tracks,
        'user_playlists': user_playlists,
        'recently_played': recently_played,
        'access_token_exists': bool(access_token),
        'spotify_user_id': request.session.get('spotify_user_id')
        }
    return render(request, 'music/dashboard.html', context)
    

@login_required
def search(request):
    """
    Handles search queries and displays results from the Spotify API.
    """
    query = request.GET.get('q', '')
    results = {}

    if query:
        # We'll use the 'data' parameter in make_spotify_api_call for GET request params
        params = {
            'q': query,
            'type': 'track,artist,album', # Search for all three types
            'limit': 12 # Get up to 12 results per type
        }
        search_response = make_spotify_api_call(request, '/search', data=params)

        if search_response and not search_response.get('error'):
            results = search_response

    context = {
        'query': query,
        'results': results
    }
    return render(request, 'core/search_results.html', context)

def home(request):
    return render(request, 'music/home.html')

