from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status, generics
from .models import Color,Size,Category,ProductProperty,Product,ProductRating, Comment
from .serializers import CommentSerializer, SizeSerializer,ColorSerializer,CategorySerializer,ProductSerializer, ProductPropertySerializer
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction


@swagger_auto_schema(
    tags=['Colors'],
    operation_description="API endpoints for managing product colors",
)
class ColorViewSet(ModelViewSet):
    """
    ViewSet for managing product colors.

    Provides CRUD operations for Color objects.
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

@swagger_auto_schema(
    tags=['Sizes'],
    operation_description="API endpoints for managing product sizes",
)
class SizeViewSet(ModelViewSet):
    """
    ViewSet for managing product sizes.

    Provides CRUD operations for Size objects.
    """
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

@swagger_auto_schema(
    tags=['Categories'],
    operation_description="API endpoints for managing product categories",
)
class CategoryViewSet(ModelViewSet):
    """
    ViewSet for managing product categories.

    Provides CRUD operations for Category objects.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@swagger_auto_schema(
    tags=['Products'],
    operation_description="API endpoints for managing products",
)
class ProductViewSet(ModelViewSet):
    """
    ViewSet for managing products.

    Provides CRUD operations for Product objects.
    Note: If a category sent for a product doesn't exist in the Category table, 
    that category will be added to the Category table.

    Original Persian description:
    در این کلاس، عملیات croud روی جدول Product انجام میشود. نکته: همچنین اگر دسته بندی ای که برای محصول ارسال میشود،‌ در جدول Category وجود نداشته باشد، آن دسته بندی به جدول Category اضافه میشود.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]


@swagger_auto_schema(
    tags=['Comments'],
    operation_description="API endpoints for managing product comments",
)
class CommentView(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    View for managing product comments:
    - List all comments for a product (GET)
    - Create a new comment (POST)
    - Delete a comment (DELETE)
    """
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_description="Get all comments for a specific product by product name.",
        responses={200: CommentSerializer(many=True)}
    )
    def get_queryset(self):
        product_name = self.kwargs['product_name']
        return Comment.objects.filter(product__name=product_name)

    @swagger_auto_schema(
        operation_description="Create a new comment for a specific product",
        request_body=CommentSerializer,
        responses={201: CommentSerializer()}
    )
    def perform_create(self, serializer):
        product_name = self.kwargs['product_name']
        product = get_object_or_404(Product, name=product_name)
        serializer.save(product=product, user=self.request.user)

    @swagger_auto_schema(
        operation_description="Delete a comment by ID for a specific product",
        responses={
            204: "Comment deleted successfully",
            404: "Comment not found or permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        product_name = self.kwargs['product_name']
        comment_id = self.kwargs['comment_id']
        comment = Comment.objects.filter(id=comment_id, product__name=product_name, user=request.user).first()
        if not comment:
            return Response(status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddProductPropertyApiView(APIView):
    @swagger_auto_schema(
        tags=['Products'],
        operation_description="Add product property",
        request_body=ProductPropertySerializer,
        responses={200: ProductPropertySerializer()}
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            size_name = data.get('size', {}).get('name') if data.get('size') else None
            color_name = data.get('color', {}).get('name') if data.get('color') else None
            product_name = data.get('product', {}).get('name')

            weight = data.get('weight')
            can_sale = data.get('can_sale')
            buy_price = data.get('buy_price')
            sell_price = data.get('sell_price')

            with transaction.atomic():
                size = None
                color = None

                if size_name:
                    size, _ = Size.objects.get_or_create(name=size_name)

                if color_name:
                    color, _ = Color.objects.get_or_create(name=color_name)

                product, created = Product.objects.get_or_create(name=product_name)

                if created:
                    product_info = data.get('product')
                    product.description = product_info.get('description') if product_info else None
                    categories = product_info.get('categories', [])
                    for category_name in categories:
                        if category_name:
                            category, _ = Category.objects.get_or_create(name=category_name)
                            product.categories.add(category)
                    product.save()
                    product.save()

                product_property = ProductProperty.objects.create(
                    product=product,
                    size=size,
                    color=color,
                    weight=weight,
                    can_sale=can_sale,
                    buy_price=buy_price,
                    sell_price=sell_price
                )

                serializer = ProductPropertySerializer(product_property)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



