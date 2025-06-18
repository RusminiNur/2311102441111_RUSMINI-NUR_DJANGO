from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Supplier, Product, Sale, Purchase
from .forms import MemberForm, SupplierForm, ProductForm, SaleForm, PurchaseForm
from django.db.models import Sum, Count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDate

def home(request):
    return render(request, 'base.html')

def member_list(request):
    members = Member.objects.all()
    form = MemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Member added successfully!')
        return redirect('member_list')
    return render(request, 'members.html', {'members': members, 'form': form})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    form = SupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Supplier added successfully!')
        return redirect('supplier_list')
    return render(request, 'suppliers.html', {'suppliers': suppliers, 'form': form})

def product_list(request):
    products = Product.objects.all()
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully!')
        return redirect('product_list')
    return render(request, 'products.html', {'products': products, 'form': form})

def cash_register(request):
    form = SaleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Sale recorded successfully!')
        return redirect('cash_register')
    return render(request, 'cash_register.html', {'form': form})

def purchase_list(request):
    purchases = Purchase.objects.all()
    form = PurchaseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Purchase recorded successfully!')
        return redirect('purchase_list')
    return render(request, 'purchases.html', {'purchases': purchases, 'form': form})

def sales_report(request):
    sales = Sale.objects.all()
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_quantity = Sale.objects.aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'sales_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'total_quantity': total_quantity
    })

@login_required
def home(request):
    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_members = Member.objects.count()
    total_suppliers = Supplier.objects.count()
    total_purchases = Purchase.objects.count()
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    return render(request, 'home.html', {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_members': total_members,
        'total_suppliers': total_suppliers,
        'total_purchases': total_purchases,
        'products': products,
        'query': query,
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # This line now works
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    return render(request, 'register.html')

@login_required
def member_list(request):
    members = Member.objects.all()
    form = MemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Member added successfully!')
        return redirect('member_list')
    return render(request, 'members.html', {'members': members, 'form': form})

@login_required
def sales_report_detailed(request):
    # Daily sales data for the last 7 days
    daily_sales = Sale.objects.annotate(date=TruncDate('sale_date')).values('date').annotate(total=Sum('total_price')).order_by('date')[:7]
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_sales]
    totals = [float(item['total'] or 0) for item in daily_sales]

    # Top 5 products by total sales
    top_products = Sale.objects.values('product__name').annotate(total=Sum('total_price')).order_by('-total')[:5]
    product_names = [item['product__name'] for item in top_products]
    product_totals = [float(item['total'] or 0) for item in top_products]

    return render(request, 'sales_report_detailed.html', {
        'daily_sales_dates': dates,
        'daily_sales_totals': totals,
        'top_product_names': product_names,
        'top_product_totals': product_totals,
    })