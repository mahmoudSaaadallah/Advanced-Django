from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from .views import OrderViewSet, ProductViewSet
from . import views
from .views import TaskView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path("heavy/", views.heavy_computation_view, name="heavy_computation"),
    path("stats/", views.query_stats, name="query_stats"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("products/", views.cached_products, name="cached_products"),
    path('tasks/<str:task_name>/', TaskView.as_view(), name='task_handler'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
