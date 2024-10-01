from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from django.views import View
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from .models import Product, Order, OrderItem, ShippingAddress
from .permissions import IsSeller
from .serializers import ProductSerializer
from .utils import get_cart_data, guest_order


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing products."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]


def store(request):
    """Render the store page with a list of products and cart data."""
    try:
        data = get_cart_data(request)
        cartItems = data.get('cartItems', 0)
        products = Product.objects.all()

        context = {'products': products, 'cartItems': cartItems, 'user': request.user}
        return render(request, 'store/store.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def cart(request):
    """Render the cart page with items in the cart."""
    try:
        data = get_cart_data(request)
        cartItems = data.get('cartItems', 0)
        order = data.get('order', None)
        items = data.get('items', [])

        context = {'items': items, 'order': order, 'cartItems': cartItems}
        return render(request, 'store/cart.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def checkout(request):
    """Render the checkout page with order and cart details."""
    try:
        data = get_cart_data(request)
        cartItems = data.get('cartItems', 0)
        order = data.get('order', None)
        items = data.get('items', [])

        context = {
            'items': items,
            'order': order,
            'cartItems': cartItems,
        }
        return render(request, 'store/checkout.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_item(request):
    """Update cart items based on user actions (add/remove)."""
    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')

        product = get_object_or_404(Product, id=productId)
        order, created = Order.objects.get_or_create(user=request.user, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(user=request.user, order=order, product=product)

        # Update quantity based on action
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1
        elif action == 'remove_all':
            orderItem.delete()
            return JsonResponse({'message': 'Item was removed from the cart'}, safe=False)

        # Check the quantity and handle saving or deleting
        if orderItem.quantity <= 0:
            orderItem.delete()
            message = 'Item was removed from the cart'
        else:
            orderItem.save()
            message = 'Item was updated'

        return JsonResponse({'message': message}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def process_order(request):
    """Process the order, linking items to the user and saving shipping information."""
    transaction_id = int(datetime.datetime.now().timestamp())
    try:
        data = json.loads(request.body)

        if request.user.is_authenticated:
            user = request.user
            order, created = Order.objects.get_or_create(user=user, complete=False)
        else:
            user, order = guest_order(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        # Link all order items to the user
        orderItems = order.orderitem_set.all()
        for item in orderItems:
            item.user = user
            item.save()

        if order.shipping:
            ShippingAddress.objects.create(
                user=user,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

        # Add success message to Django's messages framework
        messages.success(request, 'Product order successful!')

        response_data = {
            'message': 'Payment Completed..',
            'transaction_id': transaction_id
        }
        return JsonResponse(response_data)

    except Exception as e:
        messages.error(request, 'There was an error processing your order.')
        print(f'Error processing order: {e}')
        return JsonResponse({'message': 'There was an error processing your order.', 'error': str(e)}, status=500)


class ProductDetailView(View):
    """View to display product details."""

    def get(self, request, pk):
        """Render the product detail page."""
        try:
            product = get_object_or_404(Product, pk=pk)
            data = get_cart_data(request)
            cartItems = data.get('cartItems', 0)

            return render(request, 'store/views.html', {
                'product': product,
                'cartItems': cartItems
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def user_orders(request):
    """Render the user orders page."""
    try:
        data = get_cart_data(request)
        cartItems = data.get('cartItems', 0)
        orders = Order.objects.filter(user=request.user, complete=True)
        order_items = OrderItem.objects.filter(order__in=orders).select_related('product')

        context = {
            'orders': orders,
            'order_items': order_items,
            'cartItems': cartItems
        }
        return render(request, 'store/orders.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def search_products(request):
    """
    Search for products by brand and category, and handle AJAX requests.

    Args:
        request: The HTTP request object containing query parameters
                 and other request-related data.

    Returns:
        JsonResponse: A JSON response containing the search results
                      if the request is AJAX.
        HttpResponse: A rendered HTML page with the search results
                      if the request is not AJAX.
    """
    try:
        data = get_cart_data(request)
        cartItems = data.get('cartItems', 0)
        query = request.GET.get('q', '')

        if query:
            products = Product.objects.filter(
                Q(brand__icontains=query) | Q(category__icontains=query)
            )
        else:
            products = Product.objects.all()

        paginator = Paginator(products, 8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            results = [{'id': product.id, 'name': product.name, 'price': product.price, 'imageURL': product.image.url}
                       for product in page_obj]
            return JsonResponse(results, safe=False)

        context = {
            'products': page_obj,
            'query': query,
            'cartItems': cartItems,
            'paginator': paginator,
        }
        return render(request, 'store/search.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def mobile(request):
    """Render the mobile products page with pagination and sorting by price."""
    try:
        # Get the sort order from the request, default is None (no sorting)
        sort_by = request.GET.get('sort', '')

        # Fetch all products in the 'mobile' category
        products = Product.objects.filter(category='mobile')

        # Sort products based on the sort_by parameter
        if sort_by == 'low_to_high':
            products = products.order_by('price')
        elif sort_by == 'high_to_low':
            products = products.order_by('-price')

        # Pagination logic
        paginator = Paginator(products, 4)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Get all unique brands for the filter sidebar
        all_brands = Product.objects.filter(category='mobile').values_list('brand', flat=True).distinct()

        # Get cart data
        cart_data = get_cart_data(request)
        cart_items = cart_data['cartItems']

        return render(request, 'store/mobiles.html', {
            'products': page_obj,
            'all_brands': all_brands,
            'cartItems': cart_items,
            'sort_by': sort_by,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def render_products(request, category, template_name):
    """Helper function to render product pages with pagination and sorting."""
    try:
        # Retrieve the sorting parameter from the request
        sort_by = request.GET.get('sort', '')  # Default to no sorting

        # Get products for the specified category
        products = Product.objects.filter(category=category)

        # Sort products based on the sort_by parameter
        if sort_by == 'low_to_high':
            products = products.order_by('price')
        elif sort_by == 'high_to_low':
            products = products.order_by('-price')

        # Pagination logic
        paginator = Paginator(products, 4)  # Show 4 products per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Get all unique brands for the filter sidebar
        all_brands = products.values_list('brand', flat=True).distinct()

        # Get cart data
        cart_data = get_cart_data(request)
        cart_items = cart_data['cartItems']

        return render(request, template_name, {
            'products': page_obj,
            'all_brands': all_brands,
            'cartItems': cart_items,
            'sort_by': sort_by,  # Pass the sort parameter to the template if needed
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def refrigerator(request):
    """Render the refrigerator products page with pagination and sorting by price."""
    return render_products(request, 'refrigerator', 'store/refrigerator.html')


def camera(request):
    """Render the camera products page with pagination and sorting by price."""
    return render_products(request, 'camera', 'store/camera.html')


def laptops(request):
    """Render the laptops products page with pagination and sorting by price."""
    return render_products(request, 'laptops', 'store/laptops.html')


def smartwatch(request):
    """Render the smartwatch products page with pagination and sorting by price."""
    return render_products(request, 'smartwatch', 'store/smartwatch.html')


def headphones(request):
    """Render the headphones products page with pagination and sorting by price."""
    return render_products(request, 'headphones', 'store/headphones.html')


def mshirts(request):
    """Render the shirts products page with pagination."""
    return render_products(request, 'm_shirts', 'store/shirts.html')


def mtshirt(request):
    """Render the t-shirt products page with pagination."""
    return render_products(request, 'm_tshirt', 'store/tshirts.html')


def mjeans(request):
    """Render the jeans products page with pagination."""
    return render_products(request, 'm_jeans', 'store/jeans.html')


def mhoodies(request):
    """Render the hoodies products page with pagination."""
    return render_products(request, 'm_hoodies', 'store/hoodies.html')


def mshoes(request):
    """Render the shoes products page with pagination."""
    return render_products(request, 'm_shoes', 'store/shoes.html')


def wshirts(request):
    """Render the women's shirts products page with pagination."""
    return render_products(request, 'w_shirts', 'store/women_shirts.html')


def wtshirt(request):
    """Render the women's t-shirt products page with pagination."""
    return render_products(request, 'w_tshirt', 'store/women_tshirts.html')


def wjeans(request):
    """Render the women's jeans products page with pagination."""
    return render_products(request, 'w_jeans', 'store/women_jeans.html')


def whoodies(request):
    """Render the women's hoodies products page with pagination."""
    return render_products(request, 'w_hoodies', 'store/women_hoodies.html')


def wshoes(request):
    """Render the women's shoes products page with pagination."""
    return render_products(request, 'w_shoes', 'store/women_shoes.html')
