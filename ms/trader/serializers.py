# serializers.py
from rest_framework import serializers
from .models import Category, Customer, Employee, Shipper, Product, Order, OrderDetail


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.categoryName', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='productID.productName', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderDetail
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customerID.companyName', read_only=True)
    employee_name = serializers.CharField(source='employeeID.employeeName', read_only=True)
    shipper_name = serializers.CharField(source='shipperID.companyName', read_only=True)
    order_details = OrderDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'



class ProductLightSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Product
        fields = ['productID', 'productName', 'unitPrice']

class CategoryLightSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['categoryID', 'categoryName']