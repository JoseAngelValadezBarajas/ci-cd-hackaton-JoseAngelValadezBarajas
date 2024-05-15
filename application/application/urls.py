from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from app import views
from app.views import inventory_consult, inventory_consult_data, profile_view, user_administration, administrar_productos, editar_producto
from app.views import InsufficientStockListAPIView, InventoryEntryCreateAPIView, InventoryEntryListAPIView, InventoryExitCreateAPIView, InventoryExitListAPIView, ProductCreateAPIView, ProductDetailAPIView, ProductStockAPIView, UserEditAPIView, UserListAPIView, UserRoleChangeAPIView, get_product_stock, inventory_information, inventory_information_dashboard, login_view, register_inventory_entry, register_inventory_exit,register_view,dashboard_view
def redirect_to_login(request):
    return redirect('loginview') 

urlpatterns = [
    ##Modelos Vistas
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),
    path('login/', login_view, name='loginview'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('user-administration/', user_administration, name='user_administration'),
    path('control_products/', administrar_productos, name='administrar_productos'),
    path('editar_producto/<int:product_id>/', editar_producto, name='editar_producto'),
    path('get_product_stock/<int:product_id>/', get_product_stock, name='get_product_stock'),
    path('new_inventory/', register_inventory_entry, name='register_inventory_entry'),
    path('sales/', register_inventory_exit, name='register_inventory_exit'),
    path('informacion_inventario/', inventory_information, name='inventory_information'),
    path('informacion_inventario_dashboard/', inventory_information_dashboard, name='inventory_information_dashboard'),
    path('inventory_consult/', inventory_consult, name='inventory_consult'),
    path('inventory_consult_data/', inventory_consult_data, name='inventory_consult_data'),
    ##Modelos de API 
    path('api/register/', views.register, name='register'),
    path('api/login/', views.loginapi, name='login'),
    path('api/profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('api/profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('api/users/', UserListAPIView.as_view(), name='user-list'),
    path('api/users/<int:pk>/', UserEditAPIView.as_view(), name='user-edit'),
    path('api/users/<int:pk>/change-role/', UserRoleChangeAPIView.as_view(), name='user-change-role'),
    path('api/products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('api/products/<int:pk>/stock/', ProductStockAPIView.as_view(), name='product-stock'),
    path('api/inventory/entry/create/', InventoryEntryCreateAPIView.as_view(), name='inventory-entry-create'),
    path('api/inventory/exit/create/', InventoryExitCreateAPIView.as_view(), name='inventory-exit-create'),
    path('api/inventory/entries/', InventoryEntryListAPIView.as_view(), name='inventory-entry-list'),
    path('api/inventory/exits/', InventoryExitListAPIView.as_view(), name='inventory-exit-list'),
    path('api/inventory/insufficient/', InsufficientStockListAPIView.as_view(), name='insufficient-stock-list'),
]
