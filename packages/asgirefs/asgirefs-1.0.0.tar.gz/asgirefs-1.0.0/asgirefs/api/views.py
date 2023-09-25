from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Cart

from .serializers import *


class IsAuthenticatedAndNotAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_superuser and
                    not request.user.is_staff)


NOT_FOUND = {
    'error': {
        'code': 404,
        'message': 'Not found'
    }
}


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(email=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])

        if not user:
            return Response({
                'error': {
                    'code': 401,
                    "message": "Authentication failed"
                }
            }, 401)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'data': {
                'user_token': token.key
            }
        })
    else:
        return Response({
            'error': {
                'code': 422,
                'message': "Validation error",
                "errors": serializer.errors
            }
        }, 422)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'data': {
                'user_token': token.key
            }
        }, 201)
    else:
        return Response({
            'error': {
                'code': 422,
                'message': "Validation error",
                "errors": serializer.errors
            }
        }, 422)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)

    return Response({
        'data': serializer.data
    })


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def add_remove_from_cart(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response(NOT_FOUND, 404)

    cart, _ = Cart.objects.get_or_create(user=request.user)\

    if request.method == 'POST':
        cart.products.add(product)
        return Response({
            'data': {
                'message': 'Product add to cart'
            }
        }, 201)
    elif request.method == 'DELETE':
        cart.products.remove(product)
        return Response({
            'data': {
                'message': 'Item removed from cart'
            }
        })


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def get_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    response = []
    id = 1

    for item in cart.products.all():
        response.append({
            'id': id,
            'product_id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price
        })
        id += 1

    return Response({'data': response})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def get_create_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if cart.products.count() == 0:
            return Response({
                "error": {
                    "code": 422,
                    "message": 'Cart is empty'
                }
            }, 422)

        order = Order(user=request.user, order_price=0)
        order.save()
        total = 0
        for product in cart.products.all():
            order.products.add(product)
            total += product.price

        order.order_price = total
        order.save()

        cart.products.clear()

        return Response({
            'data': {
                'order_id': order.pk,
                'message': 'Order is processed'
            }
        })

    elif request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)

        return Response({'data': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    token = Token.objects.get(user=request.user)
    token.delete()

    return Response({
        'data': {
            "message": 'logout'
        }
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()

        return Response({
            'data': {
                'id': product.pk,
                'message': 'Product added'
            }
        }, 201)
    else:
        return Response({
            'error': {
                'code': 422,
                'message': "Validation error",
                "errors": serializer.errors
            }
        }, 422)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def edit_delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response(NOT_FOUND, 404)

    if request.method == 'PATCH':
        serializer = ProductSerializer(instance=product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data': serializer.data
            })
        else:
            return Response({
                'error': {
                    'code': 422,
                    'message': "Validation error",
                    "errors": serializer.errors
                }
            }, 422)
    elif request.method == 'DELETE':
        product.delete()
        return Response({
            'data': {
                'message': "Product removed"
            }
        })
