# supplier/views.py

from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .serializers import SizeSupplierSerializer,InventorySupplierSerializer, ColorSupplierSerializer, SupplierSerializer, InventorySupplier, ProductDetailSupplierSerializer,CategorySupplierSerializer
from .models import SizeSupplier,ColorSupplier,CategorySupplier,Supplier,ProductDetailSupplier,InventorySupplier
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    tags=['SupplierSizes'],
    operation_description="API endpoints for managing supplier sizes",
)
class SizeSupplierViewSet(ModelViewSet):
    """
    ViewSet for managing supplier sizes.

    Provides CRUD operations for SizeSupplier objects.
    """
    serializer_class = SizeSupplierSerializer
    queryset = SizeSupplier.objects.all()
    # permission_classes = [IsAdminUser]



# ========================================================================================================================================================



@swagger_auto_schema(
    tags=['SupplierColors'],
    operation_description="API endpoints for managing supplier colors",
)
class ColorSupplierViewSet(ModelViewSet):
    """
    ViewSet for managing supplier colors.

    Provides CRUD operations for ColorSupplier objects.
    Only admin users can access these endpoints.
    """
    serializer_class = ColorSupplierSerializer
    queryset = ColorSupplier.objects.all()
    permission_classes = [IsAdminUser]



# ========================================================================================================================================================


@swagger_auto_schema(
    tags=['Suppliers'],
    operation_description="API endpoints for managing suppliers",
)
class SupplierViewSet(ModelViewSet):
    """
    ViewSet for managing suppliers.

    Provides CRUD operations for Supplier objects.
    Only admin users can access these endpoints.
    """
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    permission_classes = [IsAdminUser]


# ========================================================================================================================================================



@swagger_auto_schema(
    tags=['SupplierCategories'],
    operation_description="API endpoints for managing supplier categories",
)
class CategorySupplierViewSet(ModelViewSet):
    """
    ViewSet for managing supplier categories.
    Provides CRUD operations for CategorySupplier objects.
    Only admin users can access these endpoints.
    """
    serializer_class = CategorySupplierSerializer
    queryset = CategorySupplier.objects.all()
    permission_classes = [IsAdminUser]


# ========================================================================================================================================================



@swagger_auto_schema(
    tags=['ProductDetailSupplier'],
    operation_description="API endpoints for managing product details for suppliers",
)
class ProductDetailSupplierViewSet(ModelViewSet):
    """
    ViewSet for managing product details for suppliers.
    Provides CRUD operations for ProductDetailSupplier objects.
    """
    serializer_class = ProductDetailSupplierSerializer
    queryset = ProductDetailSupplier.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def retrieve(self, request, pk=None):
        product_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product_object)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        product_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product_object, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        product_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        product_object = get_object_or_404(self.queryset, pk=pk)
        product_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========================================================================================================================================================



@swagger_auto_schema(
    tags=['InventorySupplier'],
    operation_description="API endpoints for managing supplier inventory",
)
class InventorySupplierViewSet(ModelViewSet):
    """
    ViewSet for managing supplier inventory.
    Provides CRUD operations for InventorySupplier objects.
    """
    serializer_class = InventorySupplierSerializer
    queryset = InventorySupplier.objects.all()
    permission_classes = [IsAdminUser]

# Create your views here.
