from django.shortcuts import render, get_object_or_404
from .models import *
# from .models import ShippingAddress

# for situations where we dont want to return a template, 
# we can return json respons
from django.http import JsonResponse
import json
import datetime 

# Create your views here.
def store(request):
    products = Product.objects.all()
    context={'products': products}
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
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
                


    print("Order:", order)
    print("Items:", items)
    context={'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        # get our cookie cart and convert it into a python dictionary
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
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']



    print("Order:", order)
    print("Items:", items)
    context={'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

# def orders(request):
#     # Call the cart function to get the items and order
#     cart_response = cart(request)

#     # Access the items and order from the cart response
#     items = cart_response.context['items']
#     order = cart_response.context['order']
#     context={'items': items, 'order':order}
#     return render(request, 'store/orders.html', context)


def orders(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        # we manually create order list for the unauthenticated user
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}

    print("Order:", order)
    print("Items:", items)
    context={'items': items, 'order':order}
    return render(request, 'store/orders.html', context)

# def view(request):
#     context={}
#     return render(request, 'store/view.html', context)

def view(request, product_id):
    # Retrieve the product using the product_id
    product = get_object_or_404(Product, id=product_id)
    
    context = {'product': product}
    return render(request, 'store/view.html', context)

def login(request):
    context={}
    return render(request, 'store/login.html', context)

def updateItem(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', status=403, safe=False)

    # Load JSON data from the request body
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')

    # Check if productId and action are provided
    if not productId or not action:
        return JsonResponse('Invalid request data', status=400, safe=False)

    try:
        product = Product.objects.get(id=productId)
    except Product.DoesNotExist:
        return JsonResponse('Product does not exist', status=404, safe=False)

    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    message = ''
    if action == 'add':
        orderItem.quantity += 1
        message = 'Item was added'
    elif action == 'remove':
        orderItem.quantity -= 1
        message = 'Item was reduced'

    if orderItem.quantity <= 0:
        orderItem.delete()
        message = 'Item was deleted'
    else:
        orderItem.save()

    return JsonResponse(message, safe=False)


def ProcessOrder(request):
    message = ''
    transaction_id= datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = 0
        if 'form' in data and 'total' in data['form']:
            total = float(data['form']['total'])
            # Rest of your code...
        else:
            return JsonResponse('Invalid request data', status=400, safe=False)

        order.transaction_id = transaction_id
        message = 'order payment not complete'
        # to ensure that transaction total cant be manipulated
        # from the client


        print('total=', total, 'float(order.get_cart_total=', float(order.get_cart_total))

        if total == float(order.get_cart_total) and total > 0:
            message = 'order payment complete'
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in ...')
        message = 'User is not logged in'
        print('User is not logged in ...')
        print('COOKIES', request.COOKIES)

        # using the form data submitted
        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(email=email)
        customer.name = name
        customer.save()

        # Check for an existing non-complete order
        order = Order.objects.filter(customer=customer, complete=False).first()
        if not order:
            order = Order.objects.create(customer=customer, complete=False)
        
        
        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            orderItem = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
            )
    
    return JsonResponse(message, safe=False)