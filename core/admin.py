from django.contrib import admin
from .models import Shop, Category, Product, Order, OrderItem, Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notif_type', 'order', 'is_read', 'created_at']
    list_filter  = ['notif_type', 'is_read']
    search_fields = ['recipient__username', 'message']

admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
