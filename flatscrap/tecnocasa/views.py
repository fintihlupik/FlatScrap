from django.shortcuts import render, get_object_or_404
from .models import Property
from .forms import PropertyForm
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import PropertySerializer
from rest_framework.response import Response

@api_view(['GET'])
def getAlProperties(request):
    flats = Property.objects.all() 
    serializer = PropertySerializer(flats, many=True) 
    return Response(serializer.data)


