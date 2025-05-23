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

    @swagger_auto_schema(
        operation_description="List all supplier sizes",
        responses={200: SizeSupplierSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all supplier sizes."""
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific supplier size",
        responses={200: SizeSupplierSerializer()}
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific supplier size."""
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new supplier size",
        request_body=SizeSupplierSerializer,
        responses={201: SizeSupplierSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """Create a new supplier size."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Fully update a specific supplier size",
        request_body=SizeSupplierSerializer,
        responses={200: SizeSupplierSerializer()}
    )
    def update(self, request, pk=None):
        """Fully update a specific supplier size."""
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Partially update a specific supplier size",
        request_body=SizeSupplierSerializer,
        responses={200: SizeSupplierSerializer()}
    )
    def partial_update(self, request, pk=None):
        """Partially update a specific supplier size."""
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific supplier size",
        responses={204: "No content - size deleted successfully"}
    )
    def destroy(self, request, pk=None):
        """Delete a specific supplier size."""
        size_object = get_object_or_404(self.queryset, pk=pk)
        size_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @swagger_auto_schema(
        operation_description="List all supplier colors",
        responses={200: ColorSupplierSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all supplier colors."""
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific supplier color",
        responses={200: ColorSupplierSerializer()}
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific supplier color."""
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new supplier color",
        request_body=ColorSupplierSerializer,
        responses={201: ColorSupplierSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """Create a new supplier color."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Fully update a specific supplier color",
        request_body=ColorSupplierSerializer,
        responses={200: ColorSupplierSerializer()}
    )
    def update(self, request, pk=None):
        """Fully update a specific supplier color."""
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Partially update a specific supplier color",
        request_body=ColorSupplierSerializer,
        responses={200: ColorSupplierSerializer()}
    )
    def partial_update(self, request, pk=None):
        """Partially update a specific supplier color."""
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific supplier color",
        responses={204: "No content - color deleted successfully"}
    )
    def destroy(self, request, pk=None):
        """Delete a specific supplier color."""
        color_object = get_object_or_404(self.queryset, pk=pk)
        color_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @swagger_auto_schema(
        operation_description="List all suppliers",
        responses={200: SupplierSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all suppliers."""
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific supplier",
        responses={200: SupplierSerializer()}
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific supplier."""
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new supplier",
        request_body=SupplierSerializer,
        responses={201: SupplierSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """Create a new supplier."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Fully update a specific supplier",
        request_body=SupplierSerializer,
        responses={200: SupplierSerializer()}
    )
    def update(self, request, pk=None):
        """Fully update a specific supplier."""
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Partially update a specific supplier",
        request_body=SupplierSerializer,
        responses={200: SupplierSerializer()}
    )
    def partial_update(self, request, pk=None):
        """Partially update a specific supplier."""
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific supplier",
        responses={204: "No content - supplier deleted successfully"}
    )
    def destroy(self, request, pk=None):
        """Delete a specific supplier."""
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        supplier_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @swagger_auto_schema(
        operation_description="List all supplier categories",
        responses={200: CategorySupplierSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all supplier categories."""
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific supplier category",
        responses={200: CategorySupplierSerializer()}
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific supplier category."""
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new supplier category",
        request_body=CategorySupplierSerializer,
        responses={201: CategorySupplierSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """Create a new supplier category."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Fully update a specific supplier category",
        request_body=CategorySupplierSerializer,
        responses={200: CategorySupplierSerializer()}
    )
    def update(self, request, pk=None):
        """Fully update a specific supplier category."""
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Partially update a specific supplier category",
        request_body=CategorySupplierSerializer,
        responses={200: CategorySupplierSerializer()}
    )
    def partial_update(self, request, pk=None):
        """Partially update a specific supplier category."""
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific supplier category",
        responses={204: "No content - category deleted successfully"}
    )
    def destroy(self, request, pk=None):
        """Delete a specific supplier category."""
        category_object = get_object_or_404(self.queryset, pk=pk)
        category_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def retrieve(self, request, pk=None):
        object = self.queryset.get(pk=pk)
        serializer = self.serializer_class(object)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(object, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Create your views here.
