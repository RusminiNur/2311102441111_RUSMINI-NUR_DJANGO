from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('members/', views.member_list, name='member_list'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('products/', views.product_list, name='product_list'),
    path('cash_register/', views.cash_register, name='cash_register'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('sales_report_detailed/', views.sales_report_detailed, name='sales_report_detailed'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]