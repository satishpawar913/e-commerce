import json
from django.db import transaction
from .models import Product, Order, OrderItem, User


def cookie_cart(request):
    """
    Retrieves and decodes the cart stored in the user's cookies.

    Args:
        request: The HTTP request object containing the cookies.

    Returns:
        A dictionary containing the total number of items, order details,
        and individual items in the cart.
    """
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        print('Failed to decode cart cookie.')
        cart = {}

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            # Ensure quantity is valid and positive
            if cart[i]['quantity'] > 0:
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = product.price * cart[i]['quantity']

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id': product.id,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL,
                    },
                    'quantity': cart[i]['quantity'],
                    'digital': product.digital,
                    'get_total': total,
                }
                items.append(item)

                if not product.digital:
                    order['shipping'] = True
        except Product.DoesNotExist:
            print(f"Product with id {i} does not exist.")
        except KeyError:
            print(f"Invalid data format for item with id {i}. Skipping.")

    return {'cartItems': cartItems, 'order': order, 'items': items}


def get_cart_data(request):
    """
    Retrieves cart data for the authenticated user or from cookies for a guest.

    Args:
        request: The HTTP request object.

    Returns:
        A dictionary containing the total number of items, order details,
        individual items in the cart, and a flag indicating if there are items.
    """
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookie_cart(request)
        cartItems = cookieData.get('cartItems', 0)
        order = cookieData.get('order', {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False})
        items = cookieData.get('items', [])

    has_items = cartItems > 0

    return {'cartItems': cartItems, 'order': order, 'items': items, 'has_items': has_items}


def guest_order(request, data):
    """
    Creates an order for a guest user based on cart items retrieved from cookies.

    Args:
        request: The HTTP request object.
        data: A dictionary containing guest user information.

    Returns:
        A tuple containing the user object and the created order object.
    """
    name = data['form']['name']
    email = data['form']['email']

    # Get cart items from cookie
    cookieData = cookie_cart(request)
    items = cookieData['items']

    # Ensure user creation or retrieval with transaction handling
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email, 'first_name': name}
        )

        # Create the order for the guest user
        order = Order.objects.create(
            user=user,
            complete=False,
        )

        # Create order items for the order
        for item in items:
            try:
                product = Product.objects.get(id=item['id'])
                quantity = item['quantity'] if item['quantity'] > 0 else abs(item['quantity'])
                OrderItem.objects.create(
                    product=product,
                    order=order,
                    user=user,
                    quantity=quantity,
                )
            except Product.DoesNotExist:
                print(f"Product with id {item['id']} does not exist.")
            except Exception as e:
                print(f"An error occurred while creating order item: {e}")

    return user, order

