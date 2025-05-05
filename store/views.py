from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category, Order, Slider, Page, TopDeal, Cart, CartItem, Profile
from .forms import TopDealForm, SignUpForm, LoginForm, ProductForm
from decimal import Decimal
import uuid

def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    sliders = Slider.objects.filter(is_active=True)
    top_deals = TopDeal.objects.all()
    selected_category = request.GET.get('category')
    
    if selected_category:
        products = products.filter(category_id=selected_category)
    
    return render(request, 'index.html', {
        'categories': categories,
        'products': products,
        'sliders': sliders,
        'top_deals': top_deals,
        'selected_category': selected_category,
    })

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    return render(request, 'product_details.html', {
        'product': product,
        'related_products': related_products,
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                country=form.cleaned_data.get('country'),
                language=form.cleaned_data.get('language')
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('index')

def admin_login(request):
    # Create admin user if it doesn't exist
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@example.com'
        }
    )
    if created:
        admin_user.set_password('admin2357')
        admin_user.save()
    
    if request.method == 'POST':
        if request.POST.get('username') == 'admin' and request.POST.get('password') == 'admin2357':
            login(request, admin_user)
            return redirect('admin_panel')
        messages.error(request, 'Invalid credentials')
    
    return render(request, 'admin_login.html')

@login_required
def admin_panel(request):
    active_tab = request.GET.get('tab', 'dashboard')
    context = {
        'active_tab': active_tab,
        'products': Product.objects.all(),
        'categories': Category.objects.all(),
        'orders': Order.objects.all(),
        'users': User.objects.filter(is_staff=False),
        'sliders': Slider.objects.all(),
        'pages': Page.objects.all(),
        'top_deals': TopDeal.objects.all(),
        'top_deal_form': TopDealForm(),
        'product_form': ProductForm(),
    }
    return render(request, 'admin_panel.html', context)

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart_items = []
        cart = None

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('5.00')
    total = subtotal + shipping

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        try:
            product = Product.objects.get(id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user, defaults={'cart_id': str(uuid.uuid4())})
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            if cart_item.quantity <= product.quantity:
                cart_item.save()
                messages.success(request, f"{product.name} added to cart!")
            else:
                messages.error(request, 'Not enough stock available.')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
    return redirect('cart')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 1))
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            if action == 'increase':
                if cart_item.quantity < cart_item.product.quantity:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    messages.error(request, 'Not enough stock available.')
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            else:
                if quantity <= cart_item.product.quantity:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    messages.error(request, 'Not enough stock available.')
        except (Cart.DoesNotExist, CartItem.DoesNotExist, Product.DoesNotExist):
            messages.error(request, 'Error updating cart.')
    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Item not found in cart.')
    return redirect('cart')

@login_required
def clear_cart(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.filter(cart=cart).delete()
            messages.success(request, 'Cart cleared successfully.')
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found.')
    return redirect('cart')

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'page_detail.html', {'page': page})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': 'form'})

@login_required
def add_top_deal(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add top deals.")
        return redirect('index')
        
    if request.method == 'POST':
        form = TopDealForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Top Deal added successfully!")
            return redirect('admin_panel')
        else:
            messages.error(request, "Error adding Top Deal. Please check the form.")
    else:
        form = TopDealForm()
    
    return render(request, 'add_top_deal.html', {'form': form})