import json
from .models import *
from django.http import JsonResponse

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('cart', cart)

    items = []
    # we manually create order list for the unauthenticated user
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
            'product': {
                    'id':product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
            },
            'quantity': cart[i]['quantity'],
            'get_total': total,
            }
            items.append(item)

            if product.digital  == False:
                order['shipping'] = True
        except:
            pass 
    return{'items': items, 'order':order, 'cartItems':cartItems}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cokieData = cookieCart(request)
        cartItems = cokieData['cartItems']
        order = cokieData['order']
        items = cokieData['items']
    return{'items': items, 'order':order, 'cartItems':cartItems}




def guestOrder(request, data):
    print('User is not logged in ...')
    # print('COOKIES', request.COOKIES)
    # print('data ...', data)

    # using the form data submitted
    name = data['form']['name']
    email = data['form']['email']

    if not name or not email:
        print('Guest name or email is missing ...')
        return JsonResponse('Guest name or email is missing', status=400, safe=False)


    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    # Check for an existing non-complete order
    order = Order.objects.filter(customer=customer, complete=False).first()
    if not order:
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    if 'items' in data:
        for item in data['items']:
            product = Product.objects.get(id=item['product']['id'])

            print('product', product)
            orderItem, created = OrderItem.objects.get_or_create(
                product=product,
                order=order,
                defaults={'quantity': item['quantity']},
            )

    return customer, order
