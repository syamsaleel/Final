from django.contrib import admin
from .models import Category, Product,User,ShoppingCart,CartItem,Order,OrderItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(User)
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
