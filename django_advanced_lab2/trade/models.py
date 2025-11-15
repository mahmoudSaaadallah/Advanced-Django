from django.db import models

class Customer(models.Model):
    customerID = models.CharField(max_length=20, primary_key=True)
    companyName = models.CharField(max_length=200, db_index=True)
    contactName = models.CharField(max_length=200, null=True, blank=True)
    contactTitle = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.companyName

class Shipper(models.Model):
    shipperID = models.IntegerField(primary_key=True)
    companyName = models.CharField(max_length=200, db_index=True)

    def __str__(self):
        return self.companyName

class Category(models.Model):
    categoryID = models.IntegerField(primary_key=True)
    categoryName = models.CharField(max_length=200, db_index=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.categoryName

class Product(models.Model):
    productID = models.IntegerField(primary_key=True)
    productName = models.CharField(max_length=255, db_index=True)
    quantityPerUnit = models.CharField(max_length=200, null=True, blank=True)
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    discontinued = models.BooleanField(default=False)
    categoryID = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')

    def __str__(self):
        return self.productName

class Employee(models.Model):
    employeeID = models.IntegerField(primary_key=True)
    employeeName = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    reportsTo = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')

    def __str__(self):
        return self.employeeName

class Order(models.Model):
    orderID = models.IntegerField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    employeeID = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='orders')
    orderDate = models.DateField(null=True, blank=True)
    requiredDate = models.DateField(null=True, blank=True)
    shippedDate = models.DateField(null=True, blank=True)
    shipperID = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, related_name='orders')
    freight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Order {self.orderID}"

class OrderDetail(models.Model):
    orderID = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_details')
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    discount = models.FloatField(default=0.0)

    class Meta:
        unique_together = (('orderID','productID'),)

    def __str__(self):
        return f"{self.orderID.orderID} - {self.productID.productName}"
