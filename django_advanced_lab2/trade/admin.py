from django.contrib import admin
from .models import Customer, Shipper, Category, Product, Employee, Order, OrderDetail

admin.site.register(Customer)
admin.site.register(Shipper)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(Order)
admin.site.register(OrderDetail)
