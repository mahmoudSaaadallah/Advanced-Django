from django.db import models

class Category(models.Model):
    categoryID = models.AutoField(primary_key=True)
    categoryName = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.categoryName

    class Meta:
        verbose_name_plural = "Categories"


class Customer(models.Model):
    customerID = models.CharField(max_length=5, primary_key=True)
    companyName = models.CharField(max_length=100)
    contactName = models.CharField(max_length=100)
    contactTitle = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.companyName


class Employee(models.Model):
    employeeID = models.AutoField(primary_key=True)
    employeeName = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    reportsTo = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='subordinates'
    )

    def __str__(self):
        return self.employeeName


class Shipper(models.Model):
    shipperID = models.AutoField(primary_key=True)
    companyName = models.CharField(max_length=100)

    def __str__(self):
        return self.companyName


class Product(models.Model):
    productID = models.AutoField(primary_key=True)
    productName = models.CharField(max_length=100)
    quantityPerUnit = models.CharField(max_length=100)
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    discontinued = models.BooleanField(default=False)
    categoryID = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='products'
    )

    def __str__(self):
        return self.productName


class Order(models.Model):
    orderID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE,
        related_name='orders'
    )
    employeeID = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders'
    )
    orderDate = models.DateField()
    requiredDate = models.DateField()
    shippedDate = models.DateField(blank=True, null=True)
    shipperID = models.ForeignKey(
        Shipper, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders'
    )
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.orderID}"

    class Meta:
        ordering = ['-orderDate']


class OrderDetail(models.Model):
    orderID = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='order_details'
    )
    productID = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='order_details'
    )
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2 )
    quantity = models.PositiveIntegerField(db_index=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.orderID} - Product {self.productID}"

    class Meta:
        unique_together = ['orderID', 'productID']
        verbose_name_plural = "Order Details"

    @property
    def total_price(self):
        return (self.unitPrice * self.quantity) * (1 - self.discount)