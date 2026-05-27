from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from decimal import Decimal
from datetime import datetime, timedelta

from accounts.models import User, Role, UserRole
from inventory.models import Product, Category, Warehouse, StockMovement
from sales.models import Sale, SaleItem, Payments
from finance.models import Account, LedgerEntry


def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    # THIS LINE WAS MISSING OR INCORRECTLY INDENTED
    return render(request, 'frontend/login.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard with key metrics."""
    user_roles = request.user.user_roles.filter(is_active=True).values_list('role__name', flat=True)
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    total_sales = Sale.objects.filter(status='COMPLETED').count()
    today_sales = Sale.objects.filter(status='COMPLETED', created_at__date=today).count()
    week_sales = Sale.objects.filter(status='COMPLETED', created_at__date__gte=week_ago).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    revenue_entries = LedgerEntry.objects.filter(
        account__name='Revenue',
        created_at__date__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    low_stock = []
    products = Product.objects.filter(track_stock=True, is_active=True)[:10]
    for product in products:
        stock = StockMovement.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        if stock < 10:
            low_stock.append({
                'product': product,
                'stock': stock
            })
    
    recent_sales = Sale.objects.select_related('warehouse', 'sold_by').order_by('-created_at')[:5]
    
    context = {
        'user_roles': user_roles,
        'total_sales': total_sales,
        'today_sales': today_sales,
        'week_revenue': revenue_entries,
        'low_stock': low_stock[:5],
        'recent_sales': recent_sales,
    }
    return render(request, 'frontend/dashboard.html', context)


@login_required
def product_list(request):
    """List all products."""
    products = Product.objects.select_related('category').filter(is_active=True)
    
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(sku__icontains=search) | Q(name__icontains=search)
        )
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories = Category.objects.filter(is_active=True)
    
    products_with_stock = []
    for product in products:
        stock = StockMovement.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        products_with_stock.append({
            'product': product,
            'stock': stock
        })
    
    context = {
        'products': products_with_stock,
        'categories': categories,
        'search': search,
    }
    return render(request, 'frontend/product_list.html', context)


@login_required
def product_detail(request, product_id):
    """Product detail page."""
    product = Product.objects.select_related('category').get(id=product_id)
    
    stock = StockMovement.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    movements = StockMovement.objects.filter(product=product).select_related(
        'warehouse', 'created_by'
    ).order_by('-created_at')[:10]
    
    context = {
        'product': product,
        'stock': stock,
        'movements': movements,
    }
    return render(request, 'frontend/product_detail.html', context)


@login_required
def sales_list(request):
    """List all sales."""
    sales = Sale.objects.select_related('warehouse', 'sold_by').order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        sales = sales.filter(status=status)
    
    context = {
        'sales': sales,
        'statuses': ['PENDING', 'COMPLETED', 'VOIDED', 'REFUNDED'],
    }
    return render(request, 'frontend/sales_list.html', context)


@login_required
def sale_detail(request, sale_id):
    """Sale detail page."""
    sale = Sale.objects.select_related('warehouse', 'sold_by').get(id=sale_id)
    items = sale.items.select_related('product').all()
    payments = sale.payments.select_related('received_by').all()
    
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    balance = sale.grand_total - total_paid
    
    context = {
        'sale': sale,
        'items': items,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'frontend/sale_detail.html', context)


@login_required
def new_sale(request):
    """Create new sale (POS interface)."""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related('category')[:50]
    
    products_with_stock = []
    for product in products:
        stock = StockMovement.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        products_with_stock.append({
            'product': product,
            'stock': stock
        })
    
    context = {
        'warehouses': warehouses,
        'products': products_with_stock,
    }
    return render(request, 'frontend/new_sale.html', context)


@login_required
def reports(request):
    """Reports dashboard."""
    can_view = request.user.user_roles.filter(
        role__name__in=['ADMIN', 'MANAGER'],
        is_active=True
    ).exists()
    
    if not can_view and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view reports')
        return redirect('dashboard')
    
    date_from = request.GET.get('date_from', (datetime.now() - timedelta(days=30)).date())
    date_to = request.GET.get('date_to', datetime.now().date())
    
    revenue = LedgerEntry.objects.filter(
        account__name='Revenue',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    cogs = LedgerEntry.objects.filter(
        account__name='Cost of Goods Sold',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    profit = revenue - cogs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    sales_count = Sale.objects.filter(
        status='COMPLETED',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    ).count()
    
    average_sale = (revenue / sales_count) if sales_count > 0 else 0
    
    top_products = SaleItem.objects.filter(
        sale__status='COMPLETED',
        sale__created_at__date__gte=date_from,
        sale__created_at__date__lte=date_to
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('line_total')
    ).order_by('-total_revenue')[:10]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'revenue': revenue,
        'cogs': cogs,
        'profit': profit,
        'margin': margin,
        'sales_count': sales_count,
        'average_sale': average_sale,
        'top_products': top_products,
    }
    return render(request, 'frontend/reports.html', context)