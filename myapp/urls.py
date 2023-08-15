from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,    
)
from .views import (RegisterAPIView,ResetPasswordAPIView,ForgotPasswordAPIView,
                    ProductListCreateAPIView,ProductRetrieveUpdateDestroyAPIView,CategoryListCreateAPIView,
                    CategoryRetrieveUpdateDestroyAPIView,ProductListAPIView,ProductDetailAPIView,
                    AddToCartAPIView,ShoppingCartAPIView,OrderPlacementAPIView,OrderHistoryAPIView,
                    OrderListAPIView,OrderRetrieveAPIView,OrderStatusUpdateAPIView,UserManagementAPIView,
                    CustomEmailNotification)
urlpatterns = [

    #adminside
    path('products/', ProductListCreateAPIView.as_view(), name='productcreate'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='productdetail'),
    #orders
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderRetrieveAPIView.as_view(), name='order-detail'),
    #category
    path('categories/', CategoryListCreateAPIView.as_view(), name='category]create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='categorydestroy'),
    path('orders/<int:pk>/update-status/', OrderStatusUpdateAPIView.as_view(), name='order-update-status'),
    #userview
    path('users/', UserManagementAPIView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserManagementAPIView.as_view(), name='user-management'),
    path('promotionalemail/', CustomEmailNotification.as_view(), name='send-promotional-email'), 

    #USER
    path('registeruser/', RegisterAPIView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    #filtering and view 
    path('products/list/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    #Cart details
    path('add-to-cart/', AddToCartAPIView.as_view(), name='add_to_cart'),
    path('shopping-cart/',ShoppingCartAPIView.as_view(), name='shopping_cart'),
    #updating cart
    path('shopping-cart/<int:pk>/', ShoppingCartAPIView.as_view(), name='shopping_cart_detail'),
    #order
    path('place-order/', OrderPlacementAPIView.as_view(), name='place-order'),
    path('order-history/', OrderHistoryAPIView.as_view(), name='order-history')


    


]