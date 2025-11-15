from rest_framework import serializers
from .models import Customer, Shipper, Product, Order, OrderDetail

class ProductSerializer(serializers.ModelSerializer):
    categoryID = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderDetail
        fields = ('product','unitPrice','quantity','discount')

class OrderSerializer(serializers.ModelSerializer):
    customerID = serializers.StringRelatedField()
    employeeID = serializers.StringRelatedField()
    shipperID = serializers.StringRelatedField()
    # order_details = OrderDetailSerializer(many=True)
    class Meta:
        model = Order
        fields = ('orderID','customerID','employeeID','shipperID','orderDate','shippedDate','freight')

class CustomerSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'

class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        fields = '__all__'
