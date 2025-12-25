"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app import views
from django.conf import settings
from django.conf.urls.static import static
from app.views import login_view
from app.views import logout_view
from app.views import dashboard_view
from app.views import orders_view
from app.views import  downloads_view
from app.views import  addresses_view,add_to_cart_ajax
from app.views import  account_details_view,wishlist_view,add_to_wishlist,remove_cart_item,signup_view
from app.views import compare_view, add_to_compare, remove_from_compare ,mini_cart_view,increase_cart_qty,decrease_cart_qty



urlpatterns = [
    path('admin/', admin.site.urls),
   path('', views.home, name='home'),
   path('shop/',views.shop,name='shop'),
   path('product/', views.product, name='product'),
   path('blog/', views.blog, name='blog'),
   path('page/', views.page, name='page'),
   path('cart/', views.cart, name='cart'),
   path('about/', views.about, name='about'),
   path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path("contact/", views.contact_view, name="contact"),
    # path("contact-success/", views.contact_success, name="contact_success"),
    path('faq/',views.faq,name='faq'),
    path('page404/',views.page404,name='page404'),
    path('login/', login_view, name='login'),
    path("logout/", logout_view, name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('orders/', orders_view, name='orders'),
    path('downloads/', downloads_view, name='downloads'),
    path('addresses/', addresses_view, name='addresses'),
    path('account-details/', account_details_view, name='account_details'),
     path('compare/', compare_view, name='compare'),
     path('checkout/', views.checkout, name='checkout'),
# path('razorpay-verify/', views.razorpay_verify, name='razorpay_verify'),  # implement verify view
path('order-success/<int:order_id>/', views.order_success, name='order_success'),
path('paypal-page/', views.paypal_page, name='paypal_page'),
path("order-tracking/", views.order_tracking, name="order_tracking"),

    path('compare/add/<int:id>/', add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:id>/', remove_from_compare, name='remove_from_compare'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
    path("mini-cart/", mini_cart_view, name="mini_cart"),
path("cart/increase/<int:id>/", views.increase_cart, name="increase_cart"),
path("cart/decrease/<int:id>/", views.decrease_cart, name="decrease_cart"),
path("cart/remove/<int:id>/", views.remove_cart, name="remove_cart"),
path("payment-verify/", views.payment_verify, name="payment_verify"),

path('add-to-cart-ajax/<int:id>/', add_to_cart_ajax, name='add_to_cart_ajax'),
# path("order-success/<int:order_id>/", views.order_success, name="order_success"),
path("order-success/<int:order_id>/", views.order_success, name="order_success"),
path("signup/", signup_view, name="signup"),








]











if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)