from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ProductDetailView, ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [

    path('p/', include(router.urls)),

    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.update_item, name="update_item"),
    path('process-order/', views.process_order, name="process-order"),

    path('product/<int:pk>/', ProductDetailView.as_view(), name='views'),

    path('mobiles/', views.mobile, name='mobiles'),
    path('shirts/', views.mshirts, name='m_shirts'),
    path('shoes/', views.mshoes, name='m_shoes'),
    path('tshirt/', views.mtshirt, name='m_tshirt'),
    path('jeans/', views.mjeans, name='m_jeans'),
    path('hoodies/', views.mhoodies, name='m_hoodies'),
    path('wshirts/', views.wshirts, name='w_shirts'),
    path('wshoes/', views.wshoes, name='w_shoes'),
    path('wtshirt/', views.wtshirt, name='w_tshirt'),
    path('wjeans/', views.wjeans, name='w_jeans'),
    path('whoodies/', views.whoodies, name='w_hoodies'),
    path('laptops/', views.laptops, name='laptops'),
    path('smartwatch/', views.smartwatch, name='smartwatch'),
    path('headphones/', views.headphones, name='headphones'),
    path('refrigerator/', views.refrigerator, name='refrigerator'),
    path('camera/', views.camera, name='camera'),

    path('my-orders/', views.user_orders, name='orders'),

    path('search/', views.search_products, name='search'),

]
