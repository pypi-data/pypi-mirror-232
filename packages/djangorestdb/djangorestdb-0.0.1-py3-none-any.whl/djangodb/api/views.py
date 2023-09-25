from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .serializers import ProductSerializer, CartSerializer, OrderSerializer
from .models import *


# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def productview(request):
    product = Product.objects.all()
    serializer = ProductSerializer(product, many=True)
    return Response({"data": serializer.data}, status=200)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def productpost(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return Response({"data": {"id": data['id'], "message": "product added"}}, status=201)
    return Response({"data": {"code": 422, "message": "Validation error", 'errors': serializer.errors}})

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def productcrud(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({"error": {"code":404, "message": "Not Found"}}, status=404)
    if request.method == "PATCH":
        serializer = ProductSerializer(instance=product, data=request.data, partial=True )
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data})
        return Response({"data": {"code": 422, "message": "Validation error", 'errors': serializer.errors}})
    elif request.method == 'DELETE':
        product.delete()
        return Response({"data": {"message": "Product removed"}} ,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cartview(request):
    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart, many=True)
    return Response({"data": serializer.data} ,status=200)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cartedit(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({"error": {"code": 404, "message": "Not Found"}}, status=404)
    if request.method == 'POST':
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
    if request.method == 'DELETE':
        cart = Cart.objects.get(user=request.user)
        cart.products.remove(product)
        return Response({"data": {"message": "Item removed from cart"}},status=200)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orderview(request):
    if request.method == 'GET':
        order = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
