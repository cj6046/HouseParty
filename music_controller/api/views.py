from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'
    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response(
                {'Room Not Found' : 'Invalid Room Code'}, 
                status=status.HTTP_404_NOT_FOUND)
        return Response(
            {'Bad Request' : 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)
        
class JoinRoomView(APIView):
    lookup_url_kwarg = 'code'
    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            queryset = Room.objects.filter(code=code)
            if len(queryset) > 0:
                room = queryset[0]
                self.request.session['room_code'] = code
                return Response(
                    {'message' : 'Room joined!'}, 
                    status=status.HTTP_200_OK)
            return Response(
                {'Room Not Found' : 'Invalid Room Code'},
                status=status.HTTP_404_NOT_FOUND)
        return Response(
            {'Bad Request' : 'Code parameter not found'},
            status=status.HTTP_400_BAD_REQUEST)

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        """Handle post request for create room"""
        if not self.request.session.exists(self.request.session.session_key):
            # if a current session does not exist, create one
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data) # serialize data from the request to track data
        if serializer.is_valid(): # if the data from the POST request is valid
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host) # creates a list of any rooms that already exist with the current session_key
            if queryset.exists(): # check to see if there is anything in that list, if so, update the data with new data from POST
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
            else:
                # otherwise create a new room with necessary data and new session_key
                room = Room(host=host, guest_can_pause = guest_can_pause, votes_to_skip = votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(
            {'Bad Request' : 'Invalid data'},
            status=status.HTTP_400_BAD_REQUEST)
            