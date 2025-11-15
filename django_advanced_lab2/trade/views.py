from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection
from django.db.models import Q, F
from .models import Order, Product
from .serializers import OrderSerializer, ProductSerializer
from django.core.cache import cache
from django.http import JsonResponse
from trade.models import Product
from django.shortcuts import render
from datetime import datetime
import time
import cProfile
import pstats
import io
import random
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .tasks import generate_report, process_image

# Low-level Caching API
def heavy_computation_view(request):
    key = "heavy_data"
    data = cache.get(key)
    if data is None:
        time.sleep(3)
        data = {"message": "Calculated data", "value": 42}
        cache.set(key, data, timeout=60)
    return JsonResponse(data)

#Per-View Caching
def query_stats(prefix):
    total = sum(float(q.get("time") or 0) for q in connection.queries)
    return {
        "prefix": prefix,
        "query_count": len(connection.queries),
        "total_sql_time": total
    }

#Template Fragment Caching
def dashboard(request):
    stats = random.randint(100, 999)
    now = datetime.now()
    return render(request, "dashboard.html", {"stats": stats, "now": now})


#Database Query Caching (Manual Pattern)
def cached_products(request):
    key = "all_products"
    products = cache.get(key)
    if products is None:
        products = list(Product.objects.values("id", "name", "price"))
        cache.set(key, products, 300)
    return JsonResponse({"count": len(products), "products": products})



@method_decorator(csrf_exempt, name='dispatch')
class TaskView(View):

    def get(self, request, task_name):
        if task_name == 'report':
            report_id = request.GET.get('report_id', 'default_report')
            task = generate_report.delay(report_id)
            return JsonResponse({"task_id": task.id, "message": f"Report generation started for {report_id}"})

        elif task_name == 'process-image':
            image_path = request.GET.get('image_path', '/default/path/image.jpg')
            task = process_image.delay(image_path)
            return JsonResponse({"task_id": task.id, "message": f"Image processing started for {image_path}"})

        else:
            return JsonResponse({"error": "Invalid task"}, status=400)



def profile_callable(func, *args, **kwargs):
    pr = cProfile.Profile()
    pr.enable()
    result = func(*args, **kwargs)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
    ps.print_stats()
    return result, s.getvalue()


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # ---------- N+1 problem ----------(51 Queries)
    @action(detail=False, url_path='nplus1')
    def nplus1(self, request):
        connection.queries.clear()
        products = list(Product.objects.all()[:50])
        return Response(ProductSerializer(products, many=True).data)

    # ---------- Lab 2 ----------
    @action(detail=False, url_path='demo')
    def demo(self, request):
        response_data = {}

        # ---------- Q() filter ----------
        connection.queries.clear()
        start = time.perf_counter()
        qres = Product.objects.filter(Q(productName__icontains='ch') | Q(unitPrice__lt=20))[:50]
        duration = time.perf_counter() - start
        response_data["Q_filter"] = {
            "duration": duration,
            "rows": qres.count(),
            **query_stats("Q() filter")
        }

        # ---------- F() update ----------
        start = time.perf_counter()
        ids = list(Product.objects.values_list('pk', flat=True)[:5])
        Product.objects.filter(pk__in=ids).update(unitPrice=F('unitPrice') + 1)
        duration = time.perf_counter() - start
        response_data["F_update"] = {
            "duration": duration,
            **query_stats("F() update")
        }

        # ---------- only() ----------
        connection.queries.clear()
        start = time.perf_counter()
        for p in Product.objects.all().only('productName')[:100]:
            _ = p.productName
        duration = time.perf_counter() - start
        response_data["only_iteration"] = {
            "duration": duration,
            "queries": len(connection.queries)
        }

        # ---------- defer() ----------
        connection.queries.clear()
        start = time.perf_counter()
        for p in Product.objects.all().defer('unitPrice')[:100]:
            _ = p.productName
        duration = time.perf_counter() - start
        response_data["defer_iteration"] = {
            "duration": duration,
            "queries": len(connection.queries)
        }

        # ---------- values() ----------
        start = time.perf_counter()
        v = list(Product.objects.values('productName', 'unitPrice')[:50])
        duration = time.perf_counter() - start
        response_data["values"] = {
            "duration": duration,
            "rows": len(v)
        }

        # ---------- values_list() ----------
        start = time.perf_counter()
        vl = list(Product.objects.values_list('productName', 'unitPrice')[:50])
        duration = time.perf_counter() - start
        response_data["values_list"] = {
            "duration": duration,
            "rows": len(vl)
        }

        # ---------- Index performance ----------
        index_perf = {}
        for field in ['productName', 'unitPrice']:
            connection.queries.clear()
            start = time.perf_counter()
            _ = list(Product.objects.filter(**{f"{field}__icontains": 'a'})[:100])
            duration = time.perf_counter() - start
            index_perf[field] = {
                "duration": duration,
                "queries": len(connection.queries)
            }
        response_data["index_perf"] = index_perf

        return Response(response_data)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # ---------- select_related  ----------(1 Query)
    @action(detail=False, url_path='optimized')
    def optimized(self, request):
        connection.queries.clear()
        start = time.perf_counter()

        qs = Order.objects.select_related("customerID", "employeeID", "shipperID").all()[:200]
        data = OrderSerializer(qs, many=True).data

        duration = time.perf_counter() - start
        stats = query_stats("select_related")

        return Response({
            "duration": duration,
            **stats,
            "results": data[:5]
        })

    # ---------- select_related + prefetch_related  ----------(2 Queries)
    @action(detail=False, url_path='prefetch')
    def prefetch(self, request):
        connection.queries.clear()
        start = time.perf_counter()

        qs = Order.objects.select_related("customerID", "employeeID", "shipperID") \
                          .prefetch_related("details")[:200]

        data = OrderSerializer(qs, many=True).data

        duration = time.perf_counter() - start
        stats = query_stats("select_related + prefetch_related")

        return Response({
            "duration": duration,
            **stats,
            "results": data[:5]
        })

    # ---------- cProfile profiling for heavy queries ----------
    @action(detail=False, url_path='profile-demo')
    def profile_demo(self, request):
        def demo_function():
            qs = Order.objects.select_related('customerID', 'employeeID').prefetch_related('details')[:500]
            out = []
            for o in qs:
                out.append({
                    'id': o.orderID,
                    'customerID': o.customerID.companyName if o.customerID else None,
                    'items': [
                        {'product': od.productID.productName if od.productID else None,
                         'qty': od.quantity} for od in o.details.all()
                    ]
                })
            return out

        data, profile_output = profile_callable(demo_function)
        return Response({
            "result_sample": data[:5],
            "profile_output": profile_output
        })
