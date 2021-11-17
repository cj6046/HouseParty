from django.shortcuts import redirect, render
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import update_or_create_user_tokens

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

def spotify_callback(self, request, format=None):
    """Creates hitpoint for spotify callback and redirects to the frontend"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    response = post('https://accounts.spotify/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not self.request.session.exists(self.request.session.session_key):
        self.request.session.create

    update_or_create_user_tokens(self.request.session.session_key, refresh_token, access_token, expires_in, token_type)

    return redirect('frontend:')




