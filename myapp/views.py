from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Category, ShoppingCart, CartItem,OrderItem,Order
from .serializers import ProductSerializer,CategorySerializer,CartItemSerializer, ShoppingCartSerializer,OrderSerializer,OrderItemSerializer,AdminUserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsAdminUserOrReadOnly
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,CreateAPIView,ListAPIView
from django.http import Http404
from django.conf import settings
from .pagination import CustomPageNumberPagination
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()



class RegisterAPIView(APIView):
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            user_name = new_user.username
            email_to = new_user.email
            ctx = {
            'user': user_name
            }
    
            message = render_to_string('mail.html', ctx)
            msg = EmailMessage(
                'Subject',
                message,
                'admin@example.com',
                [email_to],
            )
            msg.content_subtype = "html"  
            msg.send()
            return Response({'message': 'User created.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ForgotPasswordAPIView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        User = get_user_model()  
        try:
            user = User.objects.get(email=email) 
        except User.DoesNotExist:
            return Response({'error': 'No user found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        reset_link = request.build_absolute_uri(reverse('reset-password')) + f'?token={token}'

        ctx = {
            'user': user.username,
            'reset_link': reset_link,
        }
    
        message = render_to_string('reset_password.html', ctx)
        msg = EmailMessage(
            'Password Reset',
            message,
            'admin@example.com',
            [email],
            
        )
        msg.content_subtype = "html"  
        msg.send()
        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)

#class ForgotPasswordAPIView(APIView):
#    def post(self, request, format=None):
#        email = request.data.get('email')
#        User = get_user_model()  
#        try:
#            user = User.objects.get(email=email) 
#        except User.DoesNotExist:
#            return Response({'error': 'No user found with this email.'}, status=status.HTTP_404_NOT_FOUND)

#        token = default_token_generator.make_token(user)
#        base_url = "http://localhost:8000/home/reset-password/"  
#        reset_link = f"{base_url}?token={token}"

        # Send an email with the reset link
#        send_mail(
#            'Password Reset',
#            f'Click the following link to reset your password: {reset_link}',
#            'admin@example.com',
#            [email],
#            fail_silently=False,
#        )

#        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)
    
class ResetPasswordAPIView(APIView):
    def post(self, request, format=None):
        token = request.data.get('token')
        email = request.data.get('email')
        print(f"Received token: {token}")
        print(f"Received email: {email}")
        User = get_user_model()  # Corrected: Add parentheses () to call the function
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid password reset token.'}, status=status.HTTP_404_NOT_FOUND)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid password reset token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)   


#ADMIN SIDEEE
class ProductListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        if product is None:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        if product is None:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        if product is None:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated,IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk, format=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)

        order_items_serializer = OrderItemSerializer(order.orderitem_set.all(), many=True)

        response_data = serializer.data
        response_data['order_items'] = order_items_serializer.data
        response_data['customer'] = {
            'username': order.user.username,
            'email': order.user.email,
            "first_name": order.user.first_name,
            "last_name": order.user.last_name
            
        }
        response_data['total_amount'] = order.total_amount
        return Response(response_data) 
     

class OrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')

        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class UserManagementAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    def get(self, request, user_id=None):
        if user_id is None:
            users = User.objects.all()
            serializer = RegisterSerializer(users, many=True)  # Update with your actual serializer
            return Response(serializer.data)
        else:
            user = get_object_or_404(User, pk=user_id)
            serializer = RegisterSerializer(user)  # Update with your actual serializer
            return Response(serializer.data)

    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)  # Update with your actual serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomEmailNotification(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        subject = "Special Promotion!"
        #message_template = "promotional_email.html"
        site_name = "TeamBeinex"
        offer_description = request.data.get('description', "Get 20% off on all products this weekend!")

        users = User.objects.all()  # Assuming you have the User model

        for user in users:
            email_to = user.email 
            ctx = {
                'user': user.username,
                'offer_description': offer_description,
                'site_name': site_name,
            }

            message = render_to_string('proemail.html', ctx)
            msg = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email_to],
            )
            msg.content_subtype = "html"
            msg.send()

        return Response({"message": "Promotional emails sent successfully."})



#USERSIDE

class ProductListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    pagination_class=CustomPageNumberPagination
    def get(self, request, format=None):
        name = self.request.query_params.get('name')
        category_ids = request.query_params.getlist('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        products = Product.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if category_ids:
            products = products.filter(categories__id__in=category_ids)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request, format=None):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(pk=product_id)
            product_price_at_add = product.price # NNEWLY ADDED 
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        shopping_cart, _ = ShoppingCart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=shopping_cart, product=product)
        #if not created:
            # If cart item already exists, update the quantity by adding the new quantity
            #cart_item.quantity += int(quantity)
        if created:
            cart_item.price_at_add = product_price_at_add  # Set the price_at_add value
            cart_item.save()
        else:
            # If cart item is newly created, set the quantity to the new quantity
            cart_item.quantity = int(quantity)
            cart_item.save()#NEWLY ADDED
        # Check if the requested quantity exceeds the product's available quantity
        if cart_item.quantity > product.quantity:
            return Response({'error': 'Requested quantity exceeds available stock'}, status=status.HTTP_400_BAD_REQUEST)
        #cart_item.save()
        product.quantity -= cart_item.quantity
        product.save()

        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data)
    
class ShoppingCartAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ShoppingCartSerializer
    
    def get_queryset(self):
        user = self.request.user 
        return ShoppingCart.objects.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        for cart_data in serializer.data:
            cart_items = CartItem.objects.filter(cart__user=cart_data['user'])
            cart_item_serializer = CartItemSerializer(cart_items, many=True)
            cart_data['cart_items'] = cart_item_serializer.data

            total_price = 0
            for cart_item in cart_items:
                total_price += cart_item.product.price * cart_item.quantity
            cart_data['total_price'] = total_price

        return Response(serializer.data)
        
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        # Update quantities
        for item_data in data.get('cart_items', []):
            product_id = item_data.get('product', {}).get('id')
            quantity = item_data.get('quantity', 1)
            try:
                cart_item = CartItem.objects.get(cart=instance, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                pass

        # Remove products
       # remove_product_ids = data.get('remove_products', [])
       # CartItem.objects.filter(cart=instance, product_id__in=remove_product_ids).delete()

        # Recalculate total price
        cart_items = CartItem.objects.filter(cart=instance)
        total_price = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

        serializer = self.get_serializer(instance)
        serializer.data['total_price'] = total_price
        return Response({"message": "Updated quantities successfully."}, status=status.HTTP_200_OK)




class OrderPlacementAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        order_items_data = request.data.get('order_items')
        user = request.user
        total_amount = 0  # Initialize total amount
        # Create the Order instance with the calculated total_amount
        order = Order.objects.create(user=user, total_amount=total_amount, status='order approved')
        for item_data in order_items_data:
            product_id = item_data.get('product', {}).get('id')
            quantity = item_data.get('quantity', 1)
            product = Product.objects.get(id=product_id)
            product_order = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity,product_order=product_order)
            total_amount += product.price * quantity
        # Update the total_amount in the Order instance
        order.total_amount = total_amount
        order.save()

        user_address = request.data.get('address')  # Assuming address is sent in the request data
        order.address = user_address
        payment_method=request.data.get("payment_method")
        order.payment_method=payment_method
        # Send email to user
        user_subject = 'Order Confirmation'
        user_message = render_to_string('user_order.html', {'order': order})
        user_email = user.email
        user_msg = EmailMessage(user_subject, user_message, settings.EMAIL_HOST_USER, [user_email])
        user_msg.content_subtype = "html"
        user_msg.send()

        # Send email to admin
        admin_subject = 'New Order Notification'
        admin_message = render_to_string('admin_order.html', {'order': order})
        admin_email = 'Syamsaleel@gmail.com'  
        admin_msg = EmailMessage(admin_subject, admin_message, settings.EMAIL_HOST_USER, [admin_email])
        admin_msg.content_subtype = "html"
        admin_msg.send()

        #cart = user.shopping_cart
        #ordered_product_ids = [item_data['product']['id'] for item_data in order_items_data]
        #cart.cartitem_set.filter(product_id__in=ordered_product_ids).delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

class OrderHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderSerializer
    pagination_class=CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-order_date')