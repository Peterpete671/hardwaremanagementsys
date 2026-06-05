from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),

    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/<uuid:sale_id>/', views.sale_detail, name='sale_detail'),
    path('pos/', views.new_sale, name='new_sale'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # User Management (ADMIN ONLY)
    path('admin/users/', views.users_list, name='users_list'),
    path('admin/users/create/', views.create_user, name='create_user'),
    path('admin/users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('admin/users/<uuid:user_id>/assign-role/', views.assign_role, name='assign_role'),
    path('admin/users/<uuid:user_id>/remove-role/<uuid:role_id>/', views.remove_role, name='remove_role'),
    path('admin/users/<uuid:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),

    # Role Management (ADMIN ONLY)
    path('admin/roles/', views.roles_list, name='roles_list'),

    #Product image upload
    path('products/<uuid:product_id>/upload-image/', views.product_image_upload, name='product_image_upload'),

    #Create product
    path('products/create/', views.create_product, name='create_product'),
]