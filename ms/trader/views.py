from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, Product, Category
from .serializers import (
    OrderSerializer, ProductSerializer, CategorySerializer,
    ProductLightSerializer, CategoryLightSerializer
)
from django.db.models import Q, F

# 
# The "N+1 Problem" (Bad Performance)
# 
class OrderListUnoptimized(generics.ListAPIView):
    serializer_class = OrderSerializer
    # Unoptimized: This query is the problem.
    queryset = Order.objects.all()


#  The "N+1" Fix (Good Performance)

class OrderListOptimized(generics.ListAPIView):
    serializer_class = OrderSerializer
    # Optimized: Using select_related (for 'one') and prefetch_related (for 'many')
    # to reduce N+1 problem
    # this is much better as it will reduce the number of quiries that need to be made to the database to get the data
    # This is the "N+1" fix
    queryset = Order.objects.select_related(
        'customerID', 'employeeID', 'shipperID'
    ).prefetch_related(
        'order_details__productID'
    )


# Dynamic "OR" search with Q()

class ProductSearchQ(generics.ListAPIView):
    serializer_class = ProductSerializer

    # Dynamic "OR" search with Q()
    # This is the "N+1" fix as well

    def get_queryset(self):
        term = self.request.query_params.get('search')
        if term:
            # Dynamic Q() 'OR' search on product name or category name
            return Product.objects.filter(
                Q(productName__icontains=term) |
                Q(categoryID__categoryName__icontains=term)
            ).select_related('categoryID')
        
        return Product.objects.all().select_related('categoryID')


# Atomic "UPDATE" with F()

class ProductIncreasePriceF(APIView):

    # Atomic "UPDATE" with F()
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            # Atomic update: "UPDATE... SET unitPrice = unitPrice * 1.1"
            product.unitPrice = F('unitPrice') * 1.10
            product.save()
            return Response({'status': 'Price increased by 10%'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


#  Select specific fields with .only()
class ProductListOnly(generics.ListAPIView):

    """
    Uses .only() to select just the 3 fields in the serializer.
    This saves memory and bandwidth.
    """
    serializer_class = ProductLightSerializer
    # Optimized: use .only() to select just the 3 fields in the serializer
    queryset = Product.objects.only('productID', 'productName', 'unitPrice')


 # Skip specific fields with .defer()

class CategoryListDefer(generics.ListAPIView):
    """
    Uses .defer() to skip a large text field ('description').
    This saves memory and bandwidth.
    """
    serializer_class = CategoryLightSerializer
    # Optimized: use .defer() to skip the 'description' field
    queryset = Category.objects.defer('description')


#  Retrieve data as Dictionaries
class ProductListValues(APIView):
    """
    Uses .values() to get data as dictionaries.
    This bypasses the serializer and is very fast.
    """
    def get(self, request):
        # Optimized: .values() returns a list of dictionaries
        data = Product.objects.values('productID', 'productName', 'unitPrice')
        return Response(list(data))


# Retrieve data as Tuples

class ProductListValuesList(APIView):
    """
     Uses .values_list() to get data as tuples.
    This is the *fastest possible way* to get raw data.
    """
    def get(self, request):
        # Optimized: .values_list() returns a list of tuples
        data = Product.objects.values_list('productID', 'productName', 'unitPrice')
        return Response(list(data))


#  Compare Indexed vs. Non-Indexed

class ProductIndexedTest(generics.ListAPIView):
    """
    Tests search on an INDEXED column (productName).
    Check Silk: This will be very fast.
    Test with: /api/9-test-indexed-search/?term=Chai
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        term = self.request.query_params.get('term', 'Chai')
        # This lookup is FAST because 'productName' is indexed
        return Product.objects.filter(productName=term)

class ProductNonIndexedTest(generics.ListAPIView):
    """
    Tests search on a NON-INDEXED column (quantityPerUnit).
    Check Silk: This will be much slower (Full Table Scan).
    Test with: /api/10-test-non-indexed-search/?term=10 boxes x 20 bags
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        term = self.request.query_params.get('term', '10 boxes x 20 bags')
        # This lookup is SLOW because 'quantityPerUnit' is not indexed
        return Product.objects.filter(quantityPerUnit=term)