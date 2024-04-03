from django.urls import path
from store.views import (ItemDetailView,
                         category_products,
                         CheckoutView,
                         HomeView,
                         OrderSummaryView,
                         add_to_cart,
                         products,
                         remove_from_cart,
                         remove_single_item_from_cart,
                         AddCouponView,
                         RequestRefundView)

app_name = 'store'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', products, name='products'),
    path('category/<int:category_id>/', category_products, name='category_products'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/',
         remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
