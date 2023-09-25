from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import IsNotAdmin
from .authentication import BearerAuth


@api_view(["POST"])
@permission_classes([AllowAny, ])
def register(request):
    serializer = UserSer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"data": {"user_token": token.key}}, status=201)
    return Response({"data": {"code": 422, "message": "Validate error", "errors": serializer.errors}})


@api_view(["POST"])
@permission_classes([AllowAny, ])
def login(request):
    serializer = LoginSer(data=request.data)
    if serializer.is_valid():
        user = authenticate(email=serializer.validated_data["email"], password=serializer.validated_data["password"])
        if not user:
            return Response({"error": {"code":304,"message":"Authticate failed"}},status=304)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"data": {"user_token": token.key}},status=200)
    return Response({"errors": {"code":422,"message":"Validate error","error":serializer.errors}},status=200)

@api_view(["POST"])
@permission_classes([AllowAny, ])
def register(request):
    serializer = UserSer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user_token":token.key})
    return Response({"errors": {"code":422,"message":"Validate error","error":serializer.errors}})

@api_view(["GET"])
@permission_classes([IsAuthenticated, ])
@authentication_classes([BearerAuth, ])
def logout(request):
    Token.objects.get(user=request.user).delete()
    return Response({"data":{"massage":"Logout"}})



@api_view(["GET"])
@permission_classes([AllowAny, ])
def get_products(request):
    products = Products.objects.all()
    serializer = ProductsSer(products, many=True)
    return Response({"data": serializer.data}, status=200)


@api_view(["GET"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuth, ])
def cart_get(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = ProductsSer(cart.products, many=True)
    return Response({"data": serializer.data}, status=200)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuth, ])
def cart_post_delete(request, pk):
    try:
        item = Products.objects.get(pk=pk)
    except:
        return Response({"error": {"code": 404, "massage": "Not found"}}, status=404)
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.add(item)
        return Response({"data": {"massage": "Product add in cart"}}, status=200)
    if request.method == "DELETE":
        cart, _ = Cart.objects.get_or_create()
        cart.products.remove(item)
        return Response({"data": {"massage": "Item remove from cart"}}, status=200)


@api_view(["GET"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuth, ])
def get_order(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSer(orders)
    return Response({"data": serializer.data}, status=200)


@api_view(["GET", "POST"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuth, ])
def order_post_delete(request):
    if request.method == "GET":
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSer(orders, many=True)
        return Response({"data": serializer.data}, status=200)
    if request.method =="POST":
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            return Response({"error": {"code": 422, "massage": "Cart is empty"}}, status=422)
        order, _ = Order.objects.get_or_create(user=request.user,order_price=0)
        products = cart.products.all()
        if not products:
            return Response({"error": {"code": 422, "massage": "Cart is empty"}}, status=422)
        total = 0
        for product in products:
            order.products.add(product)
            total += product.price
        cart.delete()
        order.order_price = total
        order.save()
        return Response({"data": {"order_id": order.id, "message": "Order in processed"}}, status=201)



@api_view(["GET","POST"])
@permission_classes([IsAdminUser, ])
@authentication_classes([BearerAuth, ])
def admin_post(request):
    if request.method == "GET":
        poducts = Products.objects.all()
        serializer = ProductsSer(poducts, many=True)
        return Response({"data": serializer.data})
    if request.method == "POST":
        serializer = ProductsSer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":{"id": serializer.data["id"],"messege":"Product added"}})
        return Response({"errors": {"code": 422, "message": "Validate error", "error": serializer.errors}})


@api_view(["GET","DELETE","PATCH"])
@permission_classes([IsAdminUser, ])
@authentication_classes([BearerAuth, ])
def admin_delete_patch(request, pk):
    try:
        product = Products.objects.get(pk=pk)
    except:
        return Response({"error": {"code": 404,"message":"Not found"}})
    if request.method == "DELETE":
        product.delete()
        return Response({"data":{"message":"Product remove"}})
    if request.method == "PATCH":
        serializer = ProductsSer(data=request.data,instance=product,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data})
        return Response({"error":{"code":422,"message":"Validate data","error":serializer.errors}},status=200)