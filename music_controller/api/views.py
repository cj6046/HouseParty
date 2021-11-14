from django.db.models.query import QuerySet
from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    """Handle getting a room as an API View"""
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
    """Model Joining a Room in an API View"""
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
    """Model the Room in an API View"""
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
            
class UserInRoom(APIView):
    """Handle the session check when coming back to home page"""
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data = {
            'code' : self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    """Handle the session update when rooms are left"""
    def post(self, request, format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()
        return Response({'Message':'Success'}, status = status.HTTP_200_OK)

class UpdateRoomView(APIView):
    """Update the Room api based on host user preferences"""
    serializer_class = UpdateSerializer

    def patch(self, request, format=None):
        """Submit patch request to update room only if user is host"""
        # Check for current valid session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # Get serialized data and make sure data is valid
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'Bad Request':'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        guest_can_pause = serializer.data.get('guest_can_pause')
        votes_to_skip = serializer.data.get('votes_to_skip')
        code = serializer.data.get('code')

        # Find room according to code (making sure it exists)
        queryset = Room.objects.filter(code=code)
        if not queryset.exists():
            return Response({'Error':'Room Not Found'}, status=status.HTTP_404_NOT_FOUND)
        room = queryset[0]

        # Make sure user is host
        user_id = self.request.session.session_key
        if not user_id is room.host:
            return Response({'Error':'Invalid access'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update room data
        room.guest_can_pause = guest_can_pause
        room.votes_to_skip = votes_to_skip
        room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
        return Response({'Success','Room Settings Updated'}, status=status.HTTP_200_OK)

