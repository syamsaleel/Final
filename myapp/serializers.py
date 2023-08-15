
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Product, Category,User,ShoppingCart, CartItem, Order, OrderItem



class RegisterSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    is_admin = serializers.BooleanField(default=False, read_only=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password','is_admin','date_joined']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'is_admin': {'read_only': True}
        }

    def validate(self, data):
        username = data['username']
        email = data['email']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists.')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists.')

        return data
    
    def create(self, validated_data):
        is_admin = validated_data.pop('is_admin', False)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.is_admin = is_admin
        user.save()
        return user
##############admin only##############
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_admin', 'date_joined']
#######################################



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")

        return value

class ProductSerializer(serializers.ModelSerializer):
    #categories = CategorySerializer(many=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity', 'image', 'categories']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
        #fields = ['id','product', 'quantity']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        product_data = data['product']
        data['product'] = {
            'id': product_data['id'],
            'name': product_data['name'],
            'description': product_data['description'],
            'price': product_data['price'],
            'quantity': product_data['quantity'],
            'image': product_data['image'],
            'categories': product_data['categories'],
        }
        total = float(product_data['price']) * data['quantity']
        data['total'] = str(total) 
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['user', 'cart_items', 'total_price']

    def get_total_price(self, obj):
        total_price = 0
        cart_items = CartItem.objects.filter(cart=obj)
        for cart_item in cart_items:
            total_price += cart_item.product.price * cart_item.quantity
        return total_price
#ssss


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    #def get_product(self, obj):
    #    product = obj.product
    #    return {
    #        'id': product.id,
    #        'name': product.name,
    #        'price': product.price,
    #        'quantity': product.quantity,  # Adjust this according to your Product model field
    #s    }

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')  # Use the related name
    user = serializers.StringRelatedField() 
    class Meta:
        model = Order
        fields = ['user', 'status', 'order_items', 'total_amount']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        user = self.context['request'].user

        order = Order.objects.create(user=user, status='order approved')

        total_amount = 0
        order_items = []

        for item_data in order_items_data:
            product_id = item_data.get('product', {}).get('id')
            quantity = item_data.get('quantity', 1)
            product = Product.objects.get(id=product_id)
            product_order = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity,product_order=product_order)
            #product.price
            total_price = product_order * quantity
            total_amount += total_price

            order_items.append({
                'product': ProductSerializer(product).data,
                'quantity': quantity,
                'total_price': total_price
            })

        order.total_amount = total_amount
        order.save()

        serializer = self.get_serializer(order)
        serializer.data['order_items'] = order_items
        serializer.data['total_amount'] = total_amount
        return serializer.data

