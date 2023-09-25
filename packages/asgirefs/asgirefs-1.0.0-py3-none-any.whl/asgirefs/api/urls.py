from django.urls import path

from . import views


urlpatterns = [
    path('login', views.login),
    path('signup', views.signup),
    path('products', views.get_products),
    path('cart/<int:pk>', views.add_remove_from_cart),
    path('cart', views.get_cart),
    path('order', views.get_create_order),
    path('logout', views.logout),
    path('product', views.create_product),
    path('product/<int:pk>', views.edit_delete_product)
]
