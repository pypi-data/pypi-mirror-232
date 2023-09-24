from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .serializers import *
from .authentication import BearerAuthen
from .permissions import IsNotAdmin
from rest_framework.authtoken.models import Token


@api_view(["POST"])
@permission_classes([AllowAny, ])
def register(request):
    serializer = UserSer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"data":{"user_token":token.key}},status=201)
    return Response({"errors": {"code":422,"message": "Validate error", "error": serializer.errors}},status=422)

@api_view(["POST"])
@permission_classes([AllowAny, ])
def login(request):
    serializer = LodinSer(data=request.data)
    if serializer.is_valid():
        if not authenticate(email = serializer.validated_data["email"],passsword = serializer.validated_data["passsword"]):
            return Response({"error": {"message" : "Authentication error"}},status=403)
        user = AbstractUser.objects.get(email=serializer.validated_data["email"])
        if user is None:
            return Response({"error": {"message" : "Authentication error"}},status=403)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"data": {"user_token": token.key}}, status=200)
    return Response({"errors": {"code":422,"message": "Validate error", "error": serializer.errors}},status=422)

@api_view(["GET"])
@permission_classes([IsAuthenticated, ])
@authentication_classes([BearerAuthen])
def logout(request):
    Token.objects.get(user=request.user).delete()
    return Response({"data": {"message":"Logout"}},status=200)

@api_view(["GET"])
@permission_classes([AllowAny, ])
def products_get(request):
    products = Product.objects.all()
    serializer = ProductSer(products, many=True)
    return Response({"data": serializer.data})

@api_view(["GET"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuthen, ])
def cart_get(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = ProductSer(cart.products.all(),many=True)
    return Response({"data": serializer.data})

@api_view(["GET","POST","DELETE"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuthen, ])
def cart_post_delete(request,pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({"error":{"code":404,"message":"Not found"}},status=404)
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        return Response({"data": {"message":"Product add to cart"}},status=201)
    if request.method == "DELETE":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.remove(product)
        return Response({"data": {"message":"Item delete in cart"}})

@api_view(["GET","POST"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuthen, ])
def order_get_post(request):
    if request.method == "GET":
        order = Order.objects.filter(user=request.user)
        serializer = OrderSer(order,many=True)
        return Response({"data": serializer.data})
    if request.method == "POST":
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            return Response({"error":{"code": 422,"message":"Cart is empty"}},status=422)
        order, _ = Order.objects.get_or_create(user=request.user,order_price=0)
        products = cart.products.all()
        if not products:
            return Response({"error":{"code": 422,"message":"Cart is empty"}},status=422)
        for product in products:
            order.products.add(product)
        cart.delete()
        return Response({"data":{"order_id": order.id,"message":"Order is progres",}},status=201)

@api_view(["GET","POST"])
@permission_classes([IsNotAdmin, ])
@authentication_classes([BearerAuthen, ])
def admin_get_post(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductSer(products, many=True)
        return Response({"data": serializer.data})
    if request.method == "POST":
        serializer = ProductSer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"id": serializer.data["id"], "message": "Product added"}}, status=201)
        return Response({"errors": {"code": 422, "message": "Validate error", "error": serializer.errors}}, status=422)



