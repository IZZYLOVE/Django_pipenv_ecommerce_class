from django.shortcuts import render, get_object_or_404
from .models import *
from .utils import cookieCart, cartData, guestOrder
# from .models import ShippingAddress

# for situations where we dont want to return a template, 
# we can return json respons
from django.http import JsonResponse
import json
import datetime 

# Create your views here.
def store(request):
    products = Product.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    context={'products': products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)


def orders(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context={'items': items, 'order':order, 'cartItems':cartItems}
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
        orderGrandTotal = float(order.get_cart_total)


    else:
        if 'GuestDetailsError' == guestOrder(request, data):
            return JsonResponse('Guest name or email is missing', status=400, safe=False)
        else:
            cookieData = cookieCart(request)
            items = cookieData['items']
            customer, order = guestOrder(request, data)
            orderGrandTotal = float(cookieData['order']['get_cart_total'])


    total = 0
    if 'form' in data and 'total' in data['form']:
        total = float(data['form']['total'])
        # Rest of your code...
    else:
        return JsonResponse('Invalid request data', status=400, safe=False)

    # to ensure that transaction total cant be manipulated
    order.transaction_id = transaction_id
    # from the client
    message = 'order payment not complete'

    if total == orderGrandTotal and total > 0:
        message = 'order payment complete'
        order.complete = True
    else:
        return JsonResponse(message, status=400, safe=False)
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
    return JsonResponse(message, safe=False)