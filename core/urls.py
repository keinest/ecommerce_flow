from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('boutiques/', views.shop_list, name='shop_list'),
    path('boutique/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('produit/<int:pk>/', views.product_detail, name='product_detail'),

    # Authentification
    path('inscription/', views.register, name='register'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard vendeur
    path('dashboard/', views.dashboard, name='dashboard'),
    path('creer-boutique/', views.create_shop, name='create_shop'),
    path('boutique/<int:pk>/ajouter-produit/', views.add_product, name='add_product'),
    path('commande/<int:order_id>/statut/', views.update_order_status, name='update_order_status'),

    # Espace acheteur
    path('mes-commandes/', views.my_orders, name='my_orders'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notif_id>/lire/', views.mark_notification_read, name='mark_notification_read'),

    # Panier
    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/supprimer/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('commander/', views.checkout, name='checkout'),
]
