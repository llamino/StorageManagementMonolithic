from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .serializers import SizeSupplierSerializer,InventorySupplierSerializer, ColorSupplierSerializer, SupplierSerializer, InventorySupplier, ProductDetailSupplierSerializer,CategorySupplierSerializer
from .models import SizeSupplier,ColorSupplier,CategorySupplier,Supplier,ProductDetailSupplier,InventorySupplier
from rest_framework import status

class SizeSupplierViewSet(ModelViewSet):
    serializer_class = SizeSupplierSerializer
    queryset = SizeSupplier.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        size_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(size_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        size_object = get_object_or_404(self.queryset, pk=pk)
        size_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ColorSupplierViewSet(ModelViewSet):
    serializer_class = ColorSupplierSerializer
    queryset = ColorSupplier.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        color_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(color_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        color_object = get_object_or_404(self.queryset, pk=pk)
        color_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SupplierViewSet(ModelViewSet):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(supplier_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        supplier_object = get_object_or_404(self.queryset, pk=pk)
        supplier_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategorySupplierViewSet(ModelViewSet):
    serializer_class = CategorySupplierSerializer
    queryset = CategorySupplier.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        category_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        category_object = get_object_or_404(self.queryset, pk=pk)
        category_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductDetailSupplierViewSet(ModelViewSet):
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


class InventorySupplierViewSet(ModelViewSet):
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
        print(f'amin ahmadi {request.data}')
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
