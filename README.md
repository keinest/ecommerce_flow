# E-Commerce Flow 🚀

Plateforme e-commerce complète construite avec Django 5.

## Installation rapide

```bash
# 1. Cloner / décompresser le projet
cd ecommerce_flow

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

Accès : http://127.0.0.1:8000

## Structure du projet

```
ecommerce_flow/
├── config/               # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                 # Application principale
│   ├── models.py         # Shop, Product, Order, OrderItem
│   ├── views.py          # Toutes les vues (corrigées)
│   ├── urls.py           # Routes
│   ├── forms.py          # Formulaires
│   └── admin.py          # Interface admin
├── templates/            # Templates HTML
│   ├── base.html         # Layout de base avec navbar/footer
│   ├── core/             # Templates de l'app
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── shop_list.html
│   │   ├── shop_detail.html
│   │   ├── product_detail.html
│   │   ├── cart.html
│   │   └── add_product.html
│   └── registration/     # Auth templates
│       ├── login.html
│       └── register.html
├── static/               # Fichiers statiques
├── media/                # Uploads (générés)
├── manage.py
└── requirements.txt
```

## Bugs corrigés

- ✅ `product.orders.count` → annotation `Count('orderitem')`
- ✅ `@login_required` ajouté sur `checkout`
- ✅ Barre de stock bornée à 100%
- ✅ `total_revenue` affiché dans le dashboard
- ✅ `base.html` créé (était manquant → crash)
- ✅ Checkout multi-boutiques : une commande par shop
- ✅ Vérification stock max dans `add_to_cart`
- ✅ Nettoyage auto du panier si produit supprimé

## Fonctionnalités

- Gestion de boutiques et produits
- Panier en session (sans compte)
- Commandes multi-boutiques
- Dashboard avec graphiques Chart.js
- Inscription / Connexion
- Interface admin Django
