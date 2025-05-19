from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status, generics
from .models import Color,Size,Category,ProductProperty,Product,ProductRating, Comment
from .serializers import CommentSerializer, SizeSerializer,ColorSerializer,CategorySerializer,ProductSerializer
from rest_framework.views import APIView

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


class CommentView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CommentSerializer
    def get_queryset(self):
        product_name = self.kwargs['product_name']
        return Comment.objects.filter(product__name=product_name)

    def perform_create(self, serializer):
        product_name = self.kwargs['product_name']
        product = Product.objects.get(name=product_name)
        serializer.save(product=product, user=self.request.user)

    def delete(self, request, *args, **kwargs):
        product_name = self.kwargs['product_name']
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id, product__name=product_name, user=request.user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)