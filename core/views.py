import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .models import Shop, Product, Order, OrderItem, Category, Notification
from .forms import CustomUserCreationForm, ShopForm, ProductForm


def create_notification(recipient, notif_type, order, message):
    Notification.objects.create(recipient=recipient, notif_type=notif_type, order=order, message=message)


def home(request):
    shops = Shop.objects.all()[:6]
    products = Product.objects.filter(stock__gt=0).select_related('category', 'shop')[:8]
    total_products = Product.objects.count()
    total_sales = Order.objects.filter(status='delivered').count()
    return render(request, 'core/index.html', {
        'shops': shops, 'products': products,
        'total_products': total_products, 'total_sales': total_sales,
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte créé avec succès ! Connectez-vous.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    user_shops = request.user.shops.all()
    total_products = Product.objects.filter(shop__in=user_shops).count()
    total_orders   = Order.objects.filter(shop__in=user_shops).count()
    total_revenue  = (
        Order.objects.filter(shop__in=user_shops, status='delivered')
        .aggregate(Sum('total'))['total__sum'] or 0
    )
    today = timezone.now()
    last_12_months, sales_data = [], []
    for i in range(11, -1, -1):
        date = today - timedelta(days=30 * i)
        last_12_months.append(date.strftime('%b'))
        sales_data.append(
            Order.objects.filter(shop__in=user_shops, created_at__year=date.year, created_at__month=date.month).count()
        )
    recent_products = (
        Product.objects.filter(shop__in=user_shops)
        .annotate(sales_count=Count('orderitem'))
        .order_by('-created_at')[:5]
    )
    incoming_orders = (
        Order.objects.filter(shop__in=user_shops)
        .select_related('customer', 'shop')
        .prefetch_related('items__product')
        .order_by('-created_at')[:20]
    )
    qs = Order.objects.filter(shop__in=user_shops)
    pending_orders    = qs.filter(status='pending').count()
    delivered_orders  = qs.filter(status='delivered').count()
    processing_orders = qs.filter(status='processing').count()
    cancelled_orders  = qs.filter(status='cancelled').count()
    unread_notifs = request.user.notifications.filter(is_read=False).count()

    return render(request, 'core/dashboard.html', {
        'shops': user_shops,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'chart_labels': json.dumps(last_12_months, cls=DjangoJSONEncoder),
        'chart_data': json.dumps(sales_data, cls=DjangoJSONEncoder),
        'recent_products': recent_products,
        'incoming_orders': incoming_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'processing_orders': processing_orders,
        'cancelled_orders': cancelled_orders,
        'unread_notifs': unread_notifs,
    })


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.shop.owner != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette commande.")
        return redirect('dashboard')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in allowed:
            messages.error(request, "Statut invalide.")
            return redirect('dashboard')
        order.status = new_status
        order.save(update_fields=['status'])
        status_msgs = {
            'processing': f'Votre commande #{order.id} de « {order.shop.name} » est en cours de préparation.',
            'shipped':    f'Votre commande #{order.id} de « {order.shop.name} » a été expédiée ! 🚚',
            'delivered':  f'Votre commande #{order.id} de « {order.shop.name} » a été livrée. Merci ! 🎉',
            'cancelled':  f'Votre commande #{order.id} de « {order.shop.name} » a été annulée.',
        }
        if new_status in status_msgs:
            create_notification(
                recipient=order.customer,
                notif_type=f'order_{new_status}',
                order=order,
                message=status_msgs[new_status],
            )
        label = dict(Order.STATUS_CHOICES).get(new_status, new_status)
        messages.success(request, f'Commande #{order.id} → {label}')
    return redirect('dashboard')


@login_required
def my_orders(request):
    orders = (
        request.user.orders
        .select_related('shop')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'core/my_orders.html', {'orders': orders})


@login_required
def notifications_view(request):
    notifs = request.user.notifications.select_related('order__shop').all()
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifs': notifs})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, pk=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return JsonResponse({'status': 'ok'})


@login_required
def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            messages.success(request, f'Boutique « {shop.name} » créée avec succès !')
            return redirect('shop_detail', pk=shop.pk)
    else:
        form = ShopForm()
    return render(request, 'core/create_shop.html', {'form': form})


def shop_list(request):
    shops = Shop.objects.all().annotate(product_count=Count('products'))
    return render(request, 'core/shop_list.html', {'shops': shops})


def shop_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    products = shop.products.filter(stock__gt=0).select_related('category')
    is_owner = request.user.is_authenticated and shop.owner == request.user
    return render(request, 'core/shop_detail.html', {'shop': shop, 'products': products, 'is_owner': is_owner})


@login_required
def add_product(request, pk):
    shop = get_object_or_404(Shop, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(shop, request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, f'Produit « {product.name} » ajouté avec succès.')
            return redirect('shop_detail', pk=shop.pk)
    else:
        form = ProductForm(shop)
    return render(request, 'core/add_product.html', {'form': form, 'shop': shop})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    is_owner = request.user.is_authenticated and product.shop.owner == request.user
    return render(request, 'core/product_detail.html', {'product': product, 'is_owner': is_owner})


def cart_detail(request):
    cart = request.session.get('cart', {})
    items, total = [], 0
    for product_id, quantity in list(cart.items()):
        try:
            product = Product.objects.get(pk=int(product_id))
            subtotal = product.price * quantity
            total += subtotal
            items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            del cart[product_id]
            request.session['cart'] = cart
    return render(request, 'core/cart.html', {'items': items, 'total': total})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated and product.shop.owner == request.user:
        messages.error(request, "Vous ne pouvez pas ajouter vos propres produits au panier.")
        return redirect('product_detail', pk=product_id)
    if product.stock <= 0:
        messages.error(request, f'« {product.name} » est en rupture de stock.')
        return redirect('product_detail', pk=product_id)
    cart = request.session.get('cart', {})
    current_qty = cart.get(str(product_id), 0)
    if current_qty >= product.stock:
        messages.warning(request, f'Stock maximum atteint pour « {product.name} ».')
        return redirect('cart_detail')
    cart[str(product_id)] = current_qty + 1
    request.session['cart'] = cart
    messages.success(request, f'« {product.name} » ajouté au panier.')
    return redirect('cart_detail')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Produit retiré du panier.')
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Votre panier est vide.')
        return redirect('shop_list')

    items_to_process = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id))
        except Product.DoesNotExist:
            messages.error(request, 'Un produit de votre panier est introuvable.')
            return redirect('cart_detail')
        if product.shop.owner == request.user:
            messages.error(
                request,
                f'« {product.name} » appartient à votre boutique « {product.shop.name} ». '
                'Impossible de commander vos propres produits.'
            )
            return redirect('cart_detail')
        if product.stock < quantity:
            messages.error(request, f'Stock insuffisant pour « {product.name} » (disponible : {product.stock}).')
            return redirect('cart_detail')
        items_to_process.append((product, quantity))

    shops_map: dict = {}
    for product, quantity in items_to_process:
        sid = product.shop_id
        if sid not in shops_map:
            shops_map[sid] = {'shop': product.shop, 'items': []}
        shops_map[sid]['items'].append((product, quantity))

    for sid, data in shops_map.items():
        order = Order.objects.create(customer=request.user, shop=data['shop'], status='pending', total=0)
        order_total = 0
        product_names = []
        for product, quantity in data['items']:
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
            product.stock -= quantity
            product.save(update_fields=['stock'])
            order_total += product.price * quantity
            product_names.append(product.name)
        order.total = order_total
        order.save(update_fields=['total'])

        buyer_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        create_notification(
            recipient=data['shop'].owner,
            notif_type='new_order',
            order=order,
            message=(
                f"🛒 Nouvelle commande #{order.id} sur « {data['shop'].name} » "
                f"de {buyer_name} — {order_total:.2f} € ({', '.join(product_names)})."
            ),
        )

    request.session['cart'] = {}
    messages.success(request, '🎉 Commande passée avec succès ! Le vendeur a été notifié.')
    return redirect('my_orders')
