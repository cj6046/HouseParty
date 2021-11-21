from django.shortcuts import redirect, render
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from api.models import Room

class AuthUrl(APIView):
    """Return the authentication url from spotify"""
    def get(self, request, format=None):
        scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        auth_url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
        }).prepare().url

        return Response({'url' : auth_url}, status=status.HTTP_200_OK)


class IsAuthenticated(APIView):
    """Return whether spotify is already authenticated"""
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status' : is_authenticated}, status=status.HTTP_200_OK)

class CurrentSong(APIView):
    """Get info of the current song being played using host's spotify"""
    def get(self, request, format=None):
        """Get the information for current song from spotify api"""
        # Get the host of current room to go through host-user spotify
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = 'player/currently-playing'

        # Get json response from spotify api using function in util.py
        response = execute_spotify_api_request(host, endpoint)
        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        # Parse out information we need into local variables
        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('image')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')
        artist_string = ''
        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name
        
        # The song data that will be returned from get request
        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': 0,
            'id': song_id
        }

        # return song data as response
        return Response(song, status=status.HTTP_200_OK) 

def spotify_callback(request, format=None):
    """Redirect to the frontend from the Spotify callback"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    # print("callback expires_in: " + expires_in)
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key, refresh_token, access_token, expires_in, token_type)

    return redirect('frontend:')