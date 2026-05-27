from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('products/', views.product_list, name='product_list'),
    path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('sales/<uuid:sale_id>/', views.sale_detail, name='sale_detail'),
    path('pos/', views.new_sale, name='new_sale'),
    path('sales/', views.sales_list, name='sales_list'),

    path('reports/', views.reports, name='reports'), 
]