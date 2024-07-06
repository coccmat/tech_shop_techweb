from django.urls import path, include
from .views import *
urlpatterns = [
    path('', product_list, name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/add_review/', AddReviewView.as_view(), name='add_review'),
    path('product/add/', AddProductView.as_view(), name='add_product'),
    path('product/<int:pk>/manage/', ManageProductView.as_view(), name='manage_product'),
    path('order_history/', OrderListView.as_view(), name='order_history'),
    path('vendor_dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('order/create/', create_order, name='create_order'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    
    path('product/<int:pk>/request_notification/', RequestNotification.as_view(), name='request_notification'),
    path('notification_list/', NotificationListView.as_view(), name='notification_list'),
    
    path('search/', SearchResultsView.as_view(), name='search_results'),

    path('sales_dashboard/', VendorSaleDashboardView.as_view(), name='sales_dashboard'),

    path('unread_notification_count/', unread_notification_count, name='unread_notification_count'),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('delete_read_notifications/', delete_read_notifications, name='delete_read_notifications'),

    path('sales/', SalesListView.as_view(), name='sales_list'),
    path('sales/confirm/<int:item_id>/', ConfirmOrderView.as_view(), name='confirm_order'),
    ]