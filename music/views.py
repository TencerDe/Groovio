from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .spotify_client import get_track_details
# Create your views here.

def home(request):
    #This view will fetch data from Spotify API
    track_id = '0VjIjW4GlUZAMYd2vXMi3b'
    track_data = get_track_details(track_id)
    track = track_data['tracks'][0] if track_data and track_data.get('tracks') else None
    context = {
        'track': track
    }
    return render(request, 'home.html')


              