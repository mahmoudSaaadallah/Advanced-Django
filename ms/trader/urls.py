# This new urls.py file maps each view to a simple URL.

from django.urls import path
from . import views

urlpatterns = [
    # REQ 1: N+1 Problem (Bad)
    path('1-orders-unoptimized/', views.OrderListUnoptimized.as_view(), name='orders-unoptimized'),
    
    # REQ 2: N+1 Fix (Good)
    path('2-orders-optimized/', views.OrderListOptimized.as_view(), name='orders-optimized'),
    
    # REQ 3: Dynamic Q() Search
    path('3-product-search-q/', views.ProductSearchQ.as_view(), name='product-search-q'),
    
    # REQ 4: Atomic F() Update
    path('4-product-increase-price-f/<int:pk>/', views.ProductIncreasePriceF.as_view(), name='product-increase-price'),
    
    # REQ 5: .only()
    path('5-products-only/', views.ProductListOnly.as_view(), name='products-only'),
    
    # REQ 6: .defer()
    path('6-categories-defer/', views.CategoryListDefer.as_view(), name='categories-defer'),
    
    # REQ 7: .values() (Dictionaries)
    path('7-products-as-dict/', views.ProductListValues.as_view(), name='products-as-dict'),
    
    # REQ 8: .values_list() (Tuples)
    path('8-products-as-tuple/', views.ProductListValuesList.as_view(), name='products-as-tuple'),
    
    # REQ 9: Indexed Search (Fast)
    path('9-test-indexed-search/', views.ProductIndexedTest.as_view(), name='test-indexed-search'),
    
    # REQ 10: Non-Indexed Search (Slow)
    path('10-test-non-indexed-search/', views.ProductNonIndexedTest.as_view(), name='test-non-indexed-search'),
]