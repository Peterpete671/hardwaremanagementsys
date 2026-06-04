"""
Run this from your project root:
    python fix_templates.py

It rewrites every broken template file in-place with correct Django template syntax.
"""
import os

TEMPLATE_DIR = os.path.join('frontend', 'templates', 'frontend')

def fix(filename, content):
    path = os.path.join(TEMPLATE_DIR, filename)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f'Fixed: {filename}')


# ── dashboard.html ──────────────────────────────────────────────────────────
fix('dashboard.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <h1 class="text-3xl font-bold text-gray-800">Dashboard</h1>
    <a href="{% url 'new_sale' %}" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow">
        <i class="fas fa-plus mr-2"></i>New Sale
    </a>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="bg-white p-6 rounded-xl shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-500 text-sm">Total Sales</p>
                <h2 class="text-3xl font-bold text-gray-800 mt-2">{{ total_sales }}</h2>
            </div>
            <div class="bg-blue-100 p-4 rounded-full">
                <i class="fas fa-shopping-cart text-blue-600 text-2xl"></i>
            </div>
        </div>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-500 text-sm">Products</p>
                <h2 class="text-3xl font-bold text-gray-800 mt-2">{{ total_products }}</h2>
            </div>
            <div class="bg-green-100 p-4 rounded-full">
                <i class="fas fa-box text-green-600 text-2xl"></i>
            </div>
        </div>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-500 text-sm">Users</p>
                <h2 class="text-3xl font-bold text-gray-800 mt-2">{{ total_users }}</h2>
            </div>
            <div class="bg-yellow-100 p-4 rounded-full">
                <i class="fas fa-users text-yellow-600 text-2xl"></i>
            </div>
        </div>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-md">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-500 text-sm">Revenue</p>
                <h2 class="text-3xl font-bold text-gray-800 mt-2">KES {{ revenue }}</h2>
            </div>
            <div class="bg-red-100 p-4 rounded-full">
                <i class="fas fa-money-bill-wave text-red-600 text-2xl"></i>
            </div>
        </div>
    </div>
</div>

<div class="bg-white rounded-xl shadow-md p-6 mb-8">
    <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold text-gray-800">Recent Sales</h2>
        <a href="{% url 'sales_list' %}" class="text-blue-600 hover:text-blue-800 font-medium">View All</a>
    </div>
    <div class="overflow-x-auto">
        <table class="min-w-full border border-gray-200 rounded-lg overflow-hidden">
            <thead class="bg-gray-100">
                <tr>
                    <th class="px-4 py-3 text-left text-gray-700">Invoice</th>
                    <th class="px-4 py-3 text-left text-gray-700">Customer</th>
                    <th class="px-4 py-3 text-left text-gray-700">Amount</th>
                    <th class="px-4 py-3 text-left text-gray-700">Date</th>
                    <th class="px-4 py-3 text-left text-gray-700">Status</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
                {% for sale in recent_sales %}
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-3">{{ sale.sale_number }}</td>
                    <td class="px-4 py-3">{{ sale.customer_name }}</td>
                    <td class="px-4 py-3">KES {{ sale.grand_total }}</td>
                    <td class="px-4 py-3">{{ sale.created_at|date:"M d, Y" }}</td>
                    <td class="px-4 py-3">
                        <span class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">{{ sale.status }}</span>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" class="px-4 py-6 text-center text-gray-500">No recent sales found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <a href="{% url 'product_list' %}" class="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
        <div class="flex items-center space-x-4">
            <div class="bg-blue-100 p-4 rounded-full"><i class="fas fa-box text-blue-600 text-2xl"></i></div>
            <div>
                <h3 class="text-lg font-bold text-gray-800">Manage Products</h3>
                <p class="text-gray-500 text-sm">Add, edit and manage inventory</p>
            </div>
        </div>
    </a>
    <a href="{% url 'new_sale' %}" class="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
        <div class="flex items-center space-x-4">
            <div class="bg-green-100 p-4 rounded-full"><i class="fas fa-cash-register text-green-600 text-2xl"></i></div>
            <div>
                <h3 class="text-lg font-bold text-gray-800">Create Sale</h3>
                <p class="text-gray-500 text-sm">Record new customer sales</p>
            </div>
        </div>
    </a>
    <a href="{% url 'reports' %}" class="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
        <div class="flex items-center space-x-4">
            <div class="bg-yellow-100 p-4 rounded-full"><i class="fas fa-chart-line text-yellow-600 text-2xl"></i></div>
            <div>
                <h3 class="text-lg font-bold text-gray-800">Reports</h3>
                <p class="text-gray-500 text-sm">View sales and finance reports</p>
            </div>
        </div>
    </a>
</div>
{% endblock %}
""")


# ── product_list.html ────────────────────────────────────────────────────────
fix('product_list.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Products{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-gray-800">Products</h1>
</div>
<div class="bg-white p-4 rounded-lg shadow mb-6">
    <form method="GET" class="flex gap-4">
        <input type="text" name="search" placeholder="Search by SKU or name" value="{{ search }}" class="flex-1 px-4 py-2 border rounded-lg" />
        <select name="category" class="px-4 py-2 border rounded-lg">
            <option value="">All Categories</option>
            {% for category in categories %}
            <option value="{{ category.id }}">{{ category.name }}</option>
            {% endfor %}
        </select>
        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            <i class="fas fa-search mr-2"></i>Search
        </button>
    </form>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
    {% for item in products %}
    <div class="bg-white rounded-lg shadow hover:shadow-lg transition">
        <div class="p-6">
            <div class="flex justify-between items-start mb-4">
                <h3 class="font-bold text-lg text-gray-800">{{ item.product.name }}</h3>
                <span class="text-xs px-2 py-1 rounded {% if item.stock > 10 %}bg-green-100 text-green-800{% elif item.stock > 0 %}bg-yellow-100 text-yellow-800{% else %}bg-red-100 text-red-800{% endif %}">
                    {{ item.stock }} in stock
                </span>
            </div>
            <p class="text-sm text-gray-600 mb-2">SKU: {{ item.product.sku }}</p>
            <p class="text-sm text-gray-600 mb-4">{{ item.product.category.name }}</p>
            <div class="flex justify-between items-center">
                <p class="text-2xl font-bold text-blue-600">KES {{ item.product.unit_price }}</p>
                <a href="{% url 'product_detail' item.product.id %}" class="text-blue-600 hover:text-blue-800">
                    <i class="fas fa-eye"></i>
                </a>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-span-4 text-center py-12 text-gray-500">No products found</div>
    {% endfor %}
</div>
{% endblock %}
""")


# ── reports.html ─────────────────────────────────────────────────────────────
fix('reports.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Reports{% endblock %}

{% block content %}
<h1 class="text-3xl font-bold text-gray-800 mb-6">Financial Reports</h1>
<div class="bg-white p-4 rounded-lg shadow mb-6">
    <form method="GET" class="flex gap-4">
        <input type="date" name="date_from" value="{{ date_from }}" class="px-4 py-2 border rounded-lg" />
        <input type="date" name="date_to" value="{{ date_to }}" class="px-4 py-2 border rounded-lg" />
        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            <i class="fas fa-filter mr-2"></i>Apply
        </button>
    </form>
</div>
<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div class="bg-white p-6 rounded-lg shadow">
        <p class="text-gray-500 text-sm mb-2">Revenue</p>
        <p class="text-3xl font-bold text-green-600">KES {{ revenue|floatformat:2 }}</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow">
        <p class="text-gray-500 text-sm mb-2">Cost of Goods Sold</p>
        <p class="text-3xl font-bold text-red-600">KES {{ cogs|floatformat:2 }}</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow">
        <p class="text-gray-500 text-sm mb-2">Gross Profit</p>
        <p class="text-3xl font-bold text-blue-600">KES {{ profit|floatformat:2 }}</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow">
        <p class="text-gray-500 text-sm mb-2">Profit Margin</p>
        <p class="text-3xl font-bold text-red-600">{{ margin|floatformat:2 }}%</p>
    </div>
</div>
<div class="bg-white p-6 rounded-lg shadow mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Sales Summary</h2>
    <div class="grid grid-cols-2 gap-4">
        <div>
            <p class="text-gray-600">Total Sales</p>
            <p class="text-2xl font-bold">{{ sales_count }}</p>
        </div>
        <div>
            <p class="text-gray-600">Average Sale Value</p>
            <p class="text-2xl font-bold">KES {{ average_sale|floatformat:2 }}</p>
        </div>
    </div>
</div>
<div class="bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Top Selling Products</h2>
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead class="border-b">
                <tr>
                    <th class="text-left py-2">Product</th>
                    <th class="text-right py-2">Quantity</th>
                    <th class="text-right py-2">Revenue</th>
                </tr>
            </thead>
            <tbody>
                {% for product in top_products %}
                <tr class="border-b">
                    <td class="py-3">{{ product.product__name }}</td>
                    <td class="text-right py-3">{{ product.total_quantity }}</td>
                    <td class="text-right py-3 font-semibold">KES {{ product.total_revenue|floatformat:2 }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3" class="text-center py-4 text-gray-500">No sales data</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""")


# ── sales_list.html ──────────────────────────────────────────────────────────
fix('sales_list.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Sales History{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-gray-800">Sales History</h1>
    <a href="{% url 'new_sale' %}" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
        <i class="fas fa-plus mr-2"></i>New Sale
    </a>
</div>
<div class="bg-white p-4 rounded-lg shadow mb-6">
    <form method="GET" class="flex gap-4">
        <select name="status" class="px-4 py-2 border rounded-lg">
            <option value="">All Status</option>
            {% for status_option in statuses %}
            <option value="{{ status_option }}">{{ status_option }}</option>
            {% endfor %}
        </select>
        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            <i class="fas fa-filter mr-2"></i>Filter
        </button>
    </form>
</div>
<div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="w-full">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sale #</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warehouse</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sold By</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
            {% for sale in sales %}
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ sale.sale_number }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sale.created_at|date:"M d, Y H:i" }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sale.warehouse.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sale.sold_by.username }}</td>
                <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">KES {{ sale.grand_total }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full {% if sale.status == 'COMPLETED' %}bg-green-100 text-green-800{% elif sale.status == 'PENDING' %}bg-yellow-100 text-yellow-800{% elif sale.status == 'VOIDED' %}bg-red-100 text-red-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                        {{ sale.status }}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <a href="{% url 'sale_detail' sale.id %}" class="text-blue-600 hover:text-blue-800">
                        <i class="fas fa-eye"></i> View
                    </a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">No sales found</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
""")


# ── sale_detail.html ─────────────────────────────────────────────────────────
fix('sale_detail.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Sale Details - {{ sale.sale_number }}{% endblock %}

{% block content %}
<div class="mb-6">
    <a href="{% url 'sales_list' %}" class="text-blue-600 hover:underline">
        <i class="fas fa-arrow-left mr-2"></i>Back to Sales
    </a>
</div>
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 space-y-6">
        <div class="bg-white p-6 rounded-lg shadow">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h1 class="text-3xl font-bold text-gray-800">{{ sale.sale_number }}</h1>
                    <p class="text-gray-600">{{ sale.created_at|date:"F d, Y H:i" }}</p>
                </div>
                <span class="px-3 py-1 text-sm rounded-full {% if sale.status == 'COMPLETED' %}bg-green-100 text-green-800{% elif sale.status == 'PENDING' %}bg-yellow-100 text-yellow-800{% elif sale.status == 'VOIDED' %}bg-red-100 text-red-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                    {{ sale.status }}
                </span>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-sm text-gray-600">Warehouse</p>
                    <p class="font-semibold">{{ sale.warehouse.name }}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Sold By</p>
                    <p class="font-semibold">{{ sale.sold_by.username }}</p>
                </div>
            </div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Items</h2>
            <table class="w-full">
                <thead class="border-b">
                    <tr>
                        <th class="text-left py-2">Product</th>
                        <th class="text-right py-2">Qty</th>
                        <th class="text-right py-2">Unit Price</th>
                        <th class="text-right py-2">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr class="border-b">
                        <td class="py-3">
                            <p class="font-semibold">{{ item.product.name }}</p>
                            <p class="text-sm text-gray-600">{{ item.product.sku }}</p>
                        </td>
                        <td class="text-right py-3">{{ item.quantity }}</td>
                        <td class="text-right py-3">KES {{ item.unit_price }}</td>
                        <td class="text-right py-3 font-semibold">KES {{ item.line_total }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot class="border-t-2">
                    <tr>
                        <td colspan="3" class="text-right py-3 font-bold">Subtotal:</td>
                        <td class="text-right py-3 font-bold">KES {{ sale.subtotal }}</td>
                    </tr>
                    <tr>
                        <td colspan="3" class="text-right py-2">Discount:</td>
                        <td class="text-right py-2">KES {{ sale.discount_total }}</td>
                    </tr>
                    <tr>
                        <td colspan="3" class="text-right py-2">Tax:</td>
                        <td class="text-right py-2">KES {{ sale.tax_total }}</td>
                    </tr>
                    <tr class="border-t-2">
                        <td colspan="3" class="text-right py-3 text-lg font-bold">Grand Total:</td>
                        <td class="text-right py-3 text-2xl font-bold text-blue-600">KES {{ sale.grand_total }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Payments</h2>
            {% if payments %}
            <table class="w-full">
                <thead class="border-b">
                    <tr>
                        <th class="text-left py-2">Method</th>
                        <th class="text-left py-2">Amount</th>
                        <th class="text-left py-2">Reference</th>
                        <th class="text-left py-2">Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for payment in payments %}
                    <tr class="border-b">
                        <td class="py-3">{{ payment.payment_method }}</td>
                        <td class="py-3 font-semibold">KES {{ payment.amount }}</td>
                        <td class="py-3 text-sm text-gray-600">{{ payment.reference_code|default:"—" }}</td>
                        <td class="py-3 text-sm">{{ payment.created_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="text-gray-500 text-center py-4">No payments recorded</p>
            {% endif %}
        </div>
    </div>
    <div class="lg:col-span-1">
        <div class="bg-white p-6 rounded-lg shadow sticky top-4">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Summary</h2>
            <div class="space-y-3 mb-6">
                <div class="flex justify-between">
                    <span class="text-gray-600">Total Amount:</span>
                    <span class="font-bold">KES {{ sale.grand_total }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Total Paid:</span>
                    <span class="font-bold text-green-600">KES {{ total_paid }}</span>
                </div>
                <div class="flex justify-between border-t pt-3">
                    <span class="text-gray-600 font-bold">Balance:</span>
                    <span class="font-bold {% if balance > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                        KES {{ balance }}
                    </span>
                </div>
            </div>
            {% if sale.status == 'PENDING' %}
            {% if balance == 0 %}
            <button class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 mb-2">
                <i class="fas fa-check mr-2"></i>Complete Sale
            </button>
            {% endif %}
            <button class="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700">
                <i class="fas fa-times mr-2"></i>Void Sale
            </button>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
""")


# ── users_list.html ──────────────────────────────────────────────────────────
fix('users_list.html', """\
{% extends 'frontend/base.html' %}
{% block title %}User Management{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-gray-800">User Management</h1>
    <a href="{% url 'create_user' %}" class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
        <i class="fas fa-plus mr-2"></i>Create User
    </a>
</div>
<div class="bg-white p-4 rounded-lg shadow mb-6">
    <form method="GET" class="flex gap-4">
        <input type="text" name="search" placeholder="Search by username or email" value="{{ search }}"
            class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500" />
        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            <i class="fas fa-search mr-2"></i>Search
        </button>
        {% if search %}
        <a href="{% url 'users_list' %}" class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">Clear</a>
        {% endif %}
    </form>
</div>
<div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="w-full">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Roles</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
            {% for u in users %}
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <p class="font-medium text-gray-900">{{ u.username }}</p>
                    {% if u.is_superuser %}
                    <span class="text-xs px-2 py-1 rounded bg-purple-100 text-purple-800">Superuser</span>
                    {% endif %}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ u.email|default:"—" }}</td>
                <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-1">
                        {% for ur in u.user_roles.all %}
                        {% if ur.is_active %}
                        <span class="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">{{ ur.role.name }}</span>
                        {% endif %}
                        {% empty %}
                        <span class="text-xs text-gray-400 italic">No roles</span>
                        {% endfor %}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full {% if u.is_active %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                        {% if u.is_active %}Active{% else %}Inactive{% endif %}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <a href="{% url 'user_detail' u.id %}" class="text-blue-600 hover:text-blue-800">
                        <i class="fas fa-edit mr-1"></i>Manage
                    </a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" class="px-6 py-10 text-center text-gray-400">
                    <i class="fas fa-users text-3xl mb-2 block"></i>No users found
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<div class="mt-4 text-sm text-gray-500">{{ users|length }} user{{ users|length|pluralize }} found</div>
{% endblock %}
""")


# ── create_user.html ─────────────────────────────────────────────────────────
fix('create_user.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Create User{% endblock %}

{% block content %}
<div class="mb-6">
    <a href="{% url 'users_list' %}" class="text-blue-600 hover:underline">
        <i class="fas fa-arrow-left mr-2"></i>Back to Users
    </a>
</div>
<div class="max-w-2xl mx-auto">
    <div class="bg-white p-8 rounded-lg shadow">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">
            <i class="fas fa-user-plus mr-2 text-blue-600"></i>Create New User
        </h1>
        {% if errors %}
        <div class="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-6">
            <p class="font-bold mb-2"><i class="fas fa-exclamation-circle mr-1"></i>Please fix the following errors:</p>
            <ul class="list-disc list-inside space-y-1">
                {% for error in errors %}
                <li>{{ error }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        <form method="POST" class="space-y-5">
            {% csrf_token %}
            <div>
                <label class="block text-gray-700 font-semibold mb-1">Username <span class="text-red-500">*</span></label>
                <input type="text" name="username" value="{{ username|default:'' }}" required autocomplete="off"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                <p class="text-xs text-gray-500 mt-1">Must be unique. Letters, numbers, and underscores only.</p>
            </div>
            <div>
                <label class="block text-gray-700 font-semibold mb-1">Email <span class="text-red-500">*</span></label>
                <input type="email" name="email" value="{{ email|default:'' }}" required autocomplete="off"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
            </div>
            <div>
                <label class="block text-gray-700 font-semibold mb-1">Password <span class="text-red-500">*</span></label>
                <input type="password" name="password" required autocomplete="new-password"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                <p class="text-xs text-gray-500 mt-1">Minimum 6 characters.</p>
            </div>
            <div>
                <label class="block text-gray-700 font-semibold mb-1">Confirm Password <span class="text-red-500">*</span></label>
                <input type="password" name="password_confirm" required autocomplete="new-password"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
            </div>
            <div>
                <label class="block text-gray-700 font-semibold mb-1">Assign Role <span class="text-red-500">*</span></label>
                <select name="role" required
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 bg-white">
                    <option value="">Select a role...</option>
                    {% for role in roles %}
                    <option value="{{ role.id }}">{{ role.name }}{% if role.description %} - {{ role.description }}{% endif %}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="flex gap-4 pt-2">
                <button type="submit" class="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold">
                    <i class="fas fa-check mr-2"></i>Create User
                </button>
                <a href="{% url 'users_list' %}" class="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-semibold text-center">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
""")


# ── roles_list.html ──────────────────────────────────────────────────────────
fix('roles_list.html', """\
{% extends 'frontend/base.html' %}
{% block title %}Role Management{% endblock %}

{% block content %}
<div class="mb-6">
    <h1 class="text-3xl font-bold text-gray-800">Role Management</h1>
    <p class="text-gray-500 mt-1">System roles and their current assignments</p>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
    {% for role in roles %}
    <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
        <div class="flex justify-between items-start mb-3">
            <h2 class="text-xl font-bold text-gray-800">{{ role.name }}</h2>
            <div class="text-right">
                <span class="text-3xl font-bold text-blue-600">{{ role.user_count }}</span>
                <p class="text-xs text-gray-500">active user{{ role.user_count|pluralize }}</p>
            </div>
        </div>
        {% if role.description %}
        <p class="text-gray-600 text-sm mb-4">{{ role.description }}</p>
        {% else %}
        <p class="text-gray-400 text-sm italic mb-4">No description</p>
        {% endif %}
        <div class="border-t pt-3 flex justify-between items-center">
            <p class="text-xs text-gray-400">Created {{ role.created_at|date:"F d, Y" }}</p>
            <a href="{% url 'users_list' %}" class="text-xs text-blue-600 hover:underline">
                View users <i class="fas fa-arrow-right ml-1"></i>
            </a>
        </div>
    </div>
    {% empty %}
    <div class="col-span-full bg-white p-10 rounded-lg shadow text-center text-gray-400">
        <i class="fas fa-shield-alt text-4xl mb-3 block"></i>
        No roles found. Run <code class="bg-gray-100 px-2 py-1 rounded text-sm">python manage.py setup_roles</code> to create the default roles.
    </div>
    {% endfor %}
</div>
<div class="bg-blue-50 border border-blue-200 p-6 rounded-lg">
    <h3 class="font-bold text-blue-900 mb-4">
        <i class="fas fa-info-circle mr-2"></i>Role Permissions Reference
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-900">
        <div class="space-y-3">
            <div>
                <p class="font-semibold">ADMIN</p>
                <p class="text-blue-700">Full system access - manage users and roles, view all reports and audit logs.</p>
            </div>
            <div>
                <p class="font-semibold">MANAGER</p>
                <p class="text-blue-700">Manage sales, view financial reports, manage inventory, void and refund sales.</p>
            </div>
        </div>
        <div class="space-y-3">
            <div>
                <p class="font-semibold">CASHIER</p>
                <p class="text-blue-700">Create and complete sales, process payments, view products and stock levels.</p>
            </div>
            <div>
                <p class="font-semibold">STOREKEEPER</p>
                <p class="text-blue-700">Manage inventory, make stock adjustments, manage warehouses and products.</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""")


# ── user_detail.html ─────────────────────────────────────────────────────────
fix('user_detail.html', """\
{% extends 'frontend/base.html' %}
{% block title %}{{ target_user.username }} - User Details{% endblock %}

{% block content %}
<div class="mb-6">
    <a href="{% url 'users_list' %}" class="text-blue-600 hover:underline">
        <i class="fas fa-arrow-left mr-2"></i>Back to Users
    </a>
</div>
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 space-y-6">
        <div class="bg-white p-6 rounded-lg shadow">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h1 class="text-3xl font-bold text-gray-800">{{ target_user.username }}</h1>
                    <p class="text-gray-500 mt-1">{{ target_user.email|default:"No email set" }}</p>
                </div>
                <span class="px-3 py-1 text-sm rounded-full font-medium {% if target_user.is_active %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                    {% if target_user.is_active %}Active{% else %}Inactive{% endif %}
                </span>
            </div>
            <div class="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                    <p class="text-gray-500">Member Since</p>
                    <p class="font-semibold">{{ target_user.date_joined|date:"F d, Y" }}</p>
                </div>
                <div>
                    <p class="text-gray-500">Last Login</p>
                    <p class="font-semibold">
                        {% if target_user.last_login %}
                        {{ target_user.last_login|date:"F d, Y H:i" }}
                        {% else %}
                        Never
                        {% endif %}
                    </p>
                </div>
            </div>
            <div class="border-t pt-4 space-y-2 text-sm text-gray-700">
                <label class="flex items-center gap-2">
                    {% if target_user.is_staff %}
                    <input type="checkbox" checked disabled class="accent-blue-600">
                    {% else %}
                    <input type="checkbox" disabled class="accent-blue-600">
                    {% endif %}
                    Staff status (Django admin access)
                </label>
                <label class="flex items-center gap-2">
                    {% if target_user.is_superuser %}
                    <input type="checkbox" checked disabled class="accent-blue-600">
                    {% else %}
                    <input type="checkbox" disabled class="accent-blue-600">
                    {% endif %}
                    Superuser (bypasses all permission checks)
                </label>
            </div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Assigned Roles</h2>
            <div class="space-y-3 mb-6">
                {% for ur in user_roles %}
                {% if ur.is_active %}
                <div class="flex justify-between items-center p-3 bg-blue-50 border border-blue-100 rounded-lg">
                    <div>
                        <p class="font-semibold text-gray-900">{{ ur.role.name }}</p>
                        {% if ur.role.description %}
                        <p class="text-sm text-gray-600 mt-0.5">{{ ur.role.description }}</p>
                        {% endif %}
                        <p class="text-xs text-gray-400 mt-1">Assigned {{ ur.assigned_at|date:"F d, Y" }}</p>
                    </div>
                    <form method="POST" action="{% url 'remove_role' target_user.id ur.role.id %}"
                          onsubmit="return confirm('Remove this role?')">
                        {% csrf_token %}
                        <button type="submit" class="text-red-500 hover:text-red-700 px-3 py-1 rounded hover:bg-red-50" title="Remove role">
                            <i class="fas fa-times"></i>
                        </button>
                    </form>
                </div>
                {% endif %}
                {% empty %}
                <p class="text-gray-400 italic py-4 text-center">No roles assigned yet.</p>
                {% endfor %}
            </div>
            {% if available_roles %}
            <div class="border-t pt-4">
                <h3 class="font-semibold text-gray-700 mb-3">Add Role</h3>
                <form method="POST" action="{% url 'assign_role' target_user.id %}" class="flex gap-3">
                    {% csrf_token %}
                    <select name="role_id" required
                        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 bg-white">
                        <option value="">Select a role...</option>
                        {% for role in available_roles %}
                        <option value="{{ role.id }}">{{ role.name }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                        <i class="fas fa-plus mr-1"></i>Add
                    </button>
                </form>
            </div>
            {% else %}
            <div class="border-t pt-4">
                <p class="text-sm text-gray-400 italic">All available roles are already assigned.</p>
            </div>
            {% endif %}
        </div>
    </div>
    <div class="lg:col-span-1">
        <div class="bg-white p-6 rounded-lg shadow sticky top-4 space-y-3">
            <h2 class="text-xl font-bold text-gray-800 mb-2">Actions</h2>
            {% if target_user.id != request.user.id %}
            <form method="POST" action="{% url 'toggle_user_status' target_user.id %}"
                  onsubmit="return confirm('Toggle status for this user?')">
                {% csrf_token %}
                {% if target_user.is_active %}
                <button type="submit" class="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 font-medium">
                    <i class="fas fa-ban mr-2"></i>Deactivate User
                </button>
                {% else %}
                <button type="submit" class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-medium">
                    <i class="fas fa-check mr-2"></i>Activate User
                </button>
                {% endif %}
            </form>
            {% else %}
            <p class="text-xs text-gray-400 italic text-center py-1">You cannot deactivate your own account.</p>
            {% endif %}
            <a href="{% url 'users_list' %}" class="block w-full bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 text-center font-medium">
                <i class="fas fa-arrow-left mr-2"></i>Back to List
            </a>
            <div class="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500 break-all">
                <span class="font-semibold">User ID:</span><br>{{ target_user.id }}
            </div>
        </div>
    </div>
</div>
{% endblock %}
""")

print("\\nAll templates fixed successfully.")