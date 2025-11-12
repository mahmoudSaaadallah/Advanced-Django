# **MS \- Django Performance Lab**

This is a Django REST Framework project designed as a hands-on lab for demonstrating and testing advanced ORM optimization techniques and performance monitoring.

The primary goal of this project is to create "unoptimized" (slow) API endpoints, identify the performance bottlenecks using professional monitoring tools, and then create "optimized" (fast) endpoints that solve those problems.

## **Core Concepts Demonstrated**

- **N+1 Query Problem:** How to find and fix it.
- **Query Optimization:** select_related, prefetch_related.
- **Dynamic Filtering:** Using Q() objects for complex "OR" searches.
- **Atomic Updates:** Using F() expressions to prevent race conditions.
- **Efficient Data Retrieval:** only(), defer(), .values(), .values_list().
- **Database Indexing:** The performance impact of indexed vs. non-indexed columns.
- **Persistent Connections:** The benefit of CONN_MAX_AGE.
- **Performance Profiling:** Using Django Debug Toolbar, Silk, and cProfile.

## **1\. Project Setup & Installation**

### **Step 1: Create a Virtual Environment**

```
\# Create a new virtual environment
python \-m venv env

\# Activate it (Windows)
.\\env\\Scripts\\activate

\# Activate it (macOS/Linux)
source env/bin/activate
```

### **Step 2: Install Dependencies**

Install all required packages at once.

```
pip install django djangorestframework django-debug-toolbar django-silk
```

### **Step 3: Configure settings.py**

Ensure your ms/settings.py file has all the necessary tools configured.

```
\# ms/settings.py

INSTALLED_APPS \= \[
\# ... other apps ...
'trader.apps.TraderConfig',
'rest_framework',
'debug_toolbar',
'silk',
\]

MIDDLEWARE \= \[
\# ... other middleware ...
'silk.middleware.SilkyMiddleware',
'debug_toolbar.middleware.DebugToolbarMiddleware',
'trader.middleware.cProfileMiddleware', \# Your custom profiler
\]

\# Allow DjDT to run on 127.0.0.1
INTERNAL_IPS \= \[
'127.0.0.1',
\]

\# Fix profiler conflict
SILKY_PYTHON_PROFILER \= False

DATABASES \= {
'default': {
\# ... other settings ...
\# Add persistent connections
'CONN_MAX_AGE': 60
}
}
```

### **Step 4: Apply Database Migrations**

First, you must apply the initial schema and the indexes we added to models.py.

```
python manage.py makemigrations trader
python manage.py migrate
```

## **2\. Running the Project**

### **Step 1: Place Your Data**

This project requires the CSV data files. Make sure they are placed in a folder named archive in your project's root directory.

```
ms/
├── archive/
│ ├── categories.csv
│ ├── customers.csv
│ ├── employees.csv
│ ├── orders.csv
│ ├── order_details.csv
│ ├── products.csv
│ └── shippers.csv
├── ms/
├── trader/
├── script.py
└── manage.py
```

### **Step 2: Populate the Database**

Run the import script. This will load all 7 CSV files into your database.

```
python script.py
```

It will ask you if you want to clear existing data. Type y to ensure a clean import.

### **Step 3: Run the Server**

You are now ready to run the project.

```
python manage.py runserver
```

## **3\. How to Use the Monitoring Tools**

- **Django Debug Toolbar (DjDT):**
  - Go to any API endpoint in your browser (e.g., `/api/2-orders-optimized/`).
  - A "DjDT" tab will appear on the right. Click it to open the panel.
  - The **"SQL"** tab is the most important. It shows you the _exact_ queries, how many, and how long they took.
- **Django Silk:**
  - Access the main dashboard by going to `http://127.0.0.1:8000/silk/`
  - Visit any API endpoint, then refresh the Silk dashboard. You can click on any request to see detailed timing and SQL queries.
- **cProfile:**
  - Add `?profile` to the end of _any_ URL.
  - Example: `http://127.0.0.1:8000/api/8-products-as-tuple/?profile`
  - The page will load, and a full performance report will be printed to your **console/terminal** (the window where `runserver` is running).

## **4\. API Endpoints Guide**

All endpoints are GET requests unless otherwise specified.

| Requirement                 | Endpoint URL                                       | Description                                                                                                                                     |
| :-------------------------- | :------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **N+1 Problem (Bad)**       | `/api/1-orders-unoptimized/               `        | **WARNING: VERY SLOW.** This endpoint is _designed_ to be slow. It runs \~5,400 SQL queries. Use DjDT or Silk to observe the N+1 problem.       |
| **N+1 Fix (Good)**          | `/api/2-orders-optimized/`                         | **FAST.** This is the fix for the N+1 problem. It uses select_related and prefetch_related and runs only 3 SQL queries.                         |
| **Dynamic Q() Search**      | `/api/3-product-search-q/ `                        | A dynamic search that uses Q(). Test it with search terms: .../?search=Chai (finds by name) .../?search=Beverages (finds by category)           |
| **Atomic F() Update**       | **POST**` /api/4-product-increase-price-f/\<id\>/` | **(POST Request)** Atomically increases a product's price by 10% using F(), preventing race conditions. e.g., .../4-product-increase-price-f/1/ |
| **only() Method**           | /`api/5-products-only/         `                   | Fetches products using .only(), retrieving _only_ the productID, productName, and unitPrice. Check the SQL query in DjDT.                       |
| **defer() Method**          | `/api/6-categories-defer/                `         | Fetches categories using .defer(), retrieving everything _except_ the description field.                                                        |
| **.values() (Dicts)**       | `/api/7-products-as-dict/                `         | Bypasses serializers and returns data as Python dictionaries using .values(). This is very fast.                                                |
| **.values_list() (Tuples)** | /`api/8-products-as-tuple/                 `       | The fastest data retrieval. Bypasses serializers and returns data as tuples (JSON arrays) using .values_list().                                 |
| **Indexed Search Test**     | `/api/9-test-indexed-search/              `        | Performs a search on an _indexed_ column (productName). Test with ?term=Chai. **Compare DB time in Silk/DjDT with \#10.**                       |
| **Non-Indexed Search**      | `/api/10-test-non-indexed-search/        `         | Performs a search on a _non-indexed_ column (quantityPerUnit). Test with ?term=10 boxes x 20 bags. **This will be noticeably slower.**          |
