"""
URL configuration for EaseFood project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from api import views
from django.conf import settings
from django.conf.urls.static import static

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', views.SignUpView.as_view() ),
    path('api/signin/', views.SignInView.as_view(), name='signin'),

    path('api/foodcat/', views.FoodCategoryCreateView.as_view()),
    path('api/foodcat/<int:pk>/', views.FoodCategoryRetrieveUpdateDestroyView.as_view()),

    path('api/food/', views.FoodCreateListView.as_view()),
    path('api/food/<int:pk>/', views.FoodRetrieveUpdateDestroyView.as_view()),

    path('api/table/add', views.TableCreateListView.as_view()),
    path('api/table/<int:table_id>/change/', views.TableUpdateView.as_view()),
    path('api/table/<int:table_id>/delete/', views.TableDeleteView.as_view()),

    path('api/menu/<str:pin>/food/', views.FoodMenuView.as_view(), name='food_menu_api'),
    path('api/menu/<str:pin>/table/', views.TableMenuView.as_view(), name='table-menu'),
    path('api/menu/<str:pin>/category/', views.FoodCategoryMenuView.as_view(), name='food-category-menu'),

    path('api/cart/<int:table_id>/', views.CartGetAPIView.as_view(), name='cart-get'),
    path('api/cart/', views.CartAPIView.as_view(), name='cart-save'),
    path('api/cart/<int:pk>/', views.CartAPIView.as_view(), name='cart-update'),

    path('api/cart/update-quantity/', views.UpdateCartQuantityAPIView.as_view(), name='update-quantity'),

    path('api/checkout/', views.CheckoutListCreateView.as_view(), name='checkout'),
    path('api/checkout/<int:pk>/', views.CheckoutDetailView.as_view(), name='checkout-update'),
     path('api/payment/', views.PaymentView.as_view(), name='payment'),
     path('api/cart/empty/<int:table_id>/', views.EmptyCartAPIView.as_view(), name='empty-cart'),
     
     path('api/otp/', views.VerifyOTPView.as_view(), name='otp'),  # List & Create Orderspath("payment/", PaymentView.as_view(), name="payment"),  # Initiate Payment
    path("verify-payment/", views.VerifyPaymentView.as_view(), name="verify-payment"),  
    path("orders/<str:pin>/", views.OrdersByPinAPIView.as_view(), name="orders-by-pin"),
    path("orders-dashboard/<str:pin>/", views.OrdersByPinDashboardAPIView.as_view()),
    path("api/send-otp/", views.SendOTPView.as_view(), name="send-otp"),
    path("order-status/<int:pk>/", views.OrdersStatusUpdateAPIView.as_view(), name="order-status"),
    path("order-status-processing/<int:pk>/", views.OrdersStatusProcessingAPIView.as_view()),
    path("order-status-completed/<int:pk>/", views.OrdersStatusCompletedAPIView.as_view()),

]


#  path('checkout/create/', views.CreateCheckoutAPIView.as_view(), name='create-checkout'),
#     path('checkout/<int:pk>/', views.RetrieveCheckoutAPIView.as_view(), name='retrieve-checkout'),


   

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
