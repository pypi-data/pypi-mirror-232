from .models import Category

from rest_framework import viewsets

from .serializers import CategorySerializer

from django.shortcuts import render

# Create your views here.




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
