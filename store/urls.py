from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-top-deal/', views.add_top_deal, name='add_top_deal'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]