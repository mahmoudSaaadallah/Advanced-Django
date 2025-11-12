# import_data.py
import os
import csv
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ms.settings')
django.setup()

from trader.models import Category, Customer, Employee, Shipper, Product, Order, OrderDetail

def import_categories(csv_file_path):
    """Import categories from CSV"""
    print("Importing categories...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Category.objects.get_or_create(
                categoryID=row['categoryID'],
                defaults={
                    'categoryName': row['categoryName'],
                    'description': row['description']
                }
            )
    print("Categories imported successfully!")

def import_customers(csv_file_path):
    """Import customers from CSV"""
    print("Importing customers...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Customer.objects.get_or_create(
                customerID=row['customerID'],
                defaults={
                    'companyName': row['companyName'],
                    'contactName': row['contactName'],
                    'contactTitle': row.get('contactTitle', ''),
                    'city': row['city'],
                    'country': row['country']
                }
            )
    print("Customers imported successfully!")

def import_employees(csv_file_path):
    """Import employees from CSV"""
    print("Importing employees...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Handle reportsTo field (might be empty)
            reports_to = None
            if row.get('reportsTo') and row['reportsTo'].strip():
                try:
                    reports_to = Employee.objects.get(employeeID=row['reportsTo'])
                except Employee.DoesNotExist:
                    print(f"Warning: Manager with ID {row['reportsTo']} not found for employee {row['employeeName']}")
            
            Employee.objects.get_or_create(
                employeeID=row['employeeID'],
                defaults={
                    'employeeName': row['employeeName'],
                    'title': row['title'],
                    'city': row['city'],
                    'country': row['country'],
                    'reportsTo': reports_to
                }
            )
    print("Employees imported successfully!")

def import_shippers(csv_file_path):
    """Import shippers from CSV"""
    print("Importing shippers...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Shipper.objects.get_or_create(
                shipperID=row['shipperID'],
                defaults={
                    'companyName': row['companyName']
                }
            )
    print("Shippers imported successfully!")

def import_products(csv_file_path):
    """Import products from CSV"""
    print("Importing products...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get category
            try:
                category = Category.objects.get(categoryID=row['categoryID'])
            except Category.DoesNotExist:
                print(f"Warning: Category ID {row['categoryID']} not found for product {row['productName']}")
                continue
            
            # Handle discontinued field (convert string to boolean)
            discontinued = row.get('discontinued', '0').strip().lower() in ['1', 'true', 'yes']
            
            Product.objects.get_or_create(
                productID=row['productID'],
                defaults={
                    'productName': row['productName'],
                    'quantityPerUnit': row['quantityPerUnit'],
                    'unitPrice': float(row['unitPrice']),
                    'discontinued': discontinued,
                    'categoryID': category
                }
            )
    print("Products imported successfully!")

def import_orders(csv_file_path):
    """Import orders from CSV"""
    print("Importing orders...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get related objects
            try:
                customer = Customer.objects.get(customerID=row['customerID'])
            except Customer.DoesNotExist:
                print(f"Warning: Customer ID {row['customerID']} not found for order {row['orderID']}")
                continue
            
            try:
                employee = Employee.objects.get(employeeID=row['employeeID'])
            except Employee.DoesNotExist:
                print(f"Warning: Employee ID {row['employeeID']} not found for order {row['orderID']}")
                continue
            
            try:
                shipper = Shipper.objects.get(shipperID=row['shipperID'])
            except Shipper.DoesNotExist:
                print(f"Warning: Shipper ID {row['shipperID']} not found for order {row['orderID']}")
                continue
            
            # Parse dates
            def parse_date(date_str):
                if date_str and date_str.strip():
                    return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
                return None
            
            order_date = parse_date(row['orderDate'])
            required_date = parse_date(row['requiredDate'])
            shipped_date = parse_date(row.get('shippedDate', ''))
            
            Order.objects.get_or_create(
                orderID=row['orderID'],
                defaults={
                    'customerID': customer,
                    'employeeID': employee,
                    'orderDate': order_date,
                    'requiredDate': required_date,
                    'shippedDate': shipped_date,
                    'shipperID': shipper,
                    'freight': float(row.get('freight', 0))
                }
            )
    print("Orders imported successfully!")

def import_order_details(csv_file_path):
    """Import order details from CSV"""
    print("Importing order details...")
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get related objects
            try:
                order = Order.objects.get(orderID=row['orderID'])
            except Order.DoesNotExist:
                print(f"Warning: Order ID {row['orderID']} not found for order detail")
                continue
            
            try:
                product = Product.objects.get(productID=row['productID'])
            except Product.DoesNotExist:
                print(f"Warning: Product ID {row['productID']} not found for order detail")
                continue
            
            OrderDetail.objects.get_or_create(
                orderID=order,
                productID=product,
                defaults={
                    'unitPrice': float(row['unitPrice']),
                    'quantity': int(row['quantity']),
                    'discount': float(row.get('discount', 0))
                }
            )
    print("Order details imported successfully!")

def clear_all_data():
    """Clear all existing data (optional)"""
    print("Clearing existing data...")
    OrderDetail.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Shipper.objects.all().delete()
    Employee.objects.all().delete()
    Customer.objects.all().delete()
    Category.objects.all().delete()
    print("All data cleared!")

def main():
    # Define your CSV file paths
    csv_files = {
        'categories': 'archive/categories.csv',
        'customers': 'archive/customers.csv',
        'employees': 'archive/employees.csv',
        'shippers': 'archive/shippers.csv',
        'products': 'archive/products.csv',
        'orders': 'archive/orders.csv',
        'order_details': 'archive/order_details.csv'
    }
    
    # Check if CSV files exist
    for file_type, file_path in csv_files.items():
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found!")
    
    # Ask user if they want to clear existing data
    response = input("Do you want to clear existing data before import? (y/n): ")
    if response.lower() == 'y':
        clear_all_data()
    
    # Import data in correct order to maintain foreign key relationships
    try:
        import_categories(csv_files['categories'])
        import_customers(csv_files['customers'])
        import_employees(csv_files['employees'])
        import_shippers(csv_files['shippers'])
        import_products(csv_files['products'])
        import_orders(csv_files['orders'])
        import_order_details(csv_files['order_details'])
        
        print("\n" + "="*50)
        print("Data import completed successfully!")
        print("="*50)
        print(f"Categories: {Category.objects.count()}")
        print(f"Customers: {Customer.objects.count()}")
        print(f"Employees: {Employee.objects.count()}")
        print(f"Shippers: {Shipper.objects.count()}")
        print(f"Products: {Product.objects.count()}")
        print(f"Orders: {Order.objects.count()}")
        print(f"Order Details: {OrderDetail.objects.count()}")
        
    except Exception as e:
        print(f"Error during import: {str(e)}")

if __name__ == '__main__':
    main()