from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .spotify_api_utils import get_spotify_auth_url, get_spotify_tokens, get_user_profile, refresh_spotify_token
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
            request.session['spotify_user_id'] = user_profile.get('id')
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
    display_name = request.session.get('spotify_display_name', 'User')
    profile_image = request.session.get('spotify_profile_image')
    
    if not access_token:
        return redirect('home')
    
    context = {
        'display_name': display_name,
        'profile_image': profile_image,
        'access_token_exists': bool(access_token)
    }
    return render(request, 'music/dashboard.html', context)

def home(request):
    return render(request, 'music/home.html')

