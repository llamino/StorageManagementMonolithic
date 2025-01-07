from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Color,Size,Category,ProductProperty,Product,ProductRating
from .serializers import SizeSerializer,ColorSerializer,CategorySerializer,ProductSerializer


class ColorViewSet(ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class SizeViewSet(ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    '''
     در این کلاس، عملیات croud روی جدول Product انجام میشود. نکته: همچنین اگر دسته بندی ای که برای محصول ارسال میشود،‌ در جدول Category وجود نداشته باشد، آن دسته بندی به جدول Category اضافه میشود.
    '''
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]

