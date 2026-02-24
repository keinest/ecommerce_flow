# 🆕 Nouvelles fonctionnalités ajoutées

## 1. Blocage de l'auto-commande
- Un propriétaire de boutique ne peut **plus ajouter ses propres produits** au panier
- Blocage également au niveau du checkout (double sécurité)
- Message d'information affiché dans la page boutique et fiche produit si vous êtes le propriétaire

## 2. Panier & Commande (acheteur)
- Tout utilisateur peut ajouter des produits d'**autres boutiques** au panier
- Passage de commande via `/commander/`
- Après la commande → redirection vers "Mes commandes"
- **Le vendeur est notifié automatiquement** dès qu'une commande est passée

## 3. Mes commandes (acheteur) — `/mes-commandes/`
- Page dédiée listant toutes vos commandes passées
- Affichage du statut en temps réel (En attente, En préparation, Expédiée, Livrée, Annulée)
- Détail des articles commandés avec prix et quantité

## 4. Gestion des commandes reçues (vendeur) — Dashboard
- Section "Commandes reçues" dans le dashboard du vendeur
- Tableau complet : client, boutique, produits, montant, statut actuel
- **Sélecteur de statut** pour mettre à jour chaque commande en un clic
- Le client est notifié automatiquement à chaque changement de statut

## 5. Notifications — `/notifications/`
- Nouveau modèle `Notification` en base de données
- **Cloche de notification** dans la navbar avec badge rouge (nombre de non-lues)
- Page dédiée listant toutes les notifications
- Marquage automatique comme "lues" à la visite de la page
- Types de notifications :
  - 🛒 `new_order` : nouvelle commande reçue (→ vendeur)
  - 🚚 `order_shipped` : commande expédiée (→ acheteur)
  - 🎉 `order_delivered` : commande livrée (→ acheteur)
  - ❌ `order_cancelled` : commande annulée (→ acheteur)

## 6. Migrations à exécuter
```bash
python manage.py makemigrations
python manage.py migrate
```

## Architecture des nouvelles URLs
| URL | Nom | Description |
|-----|-----|-------------|
| `/mes-commandes/` | `my_orders` | Commandes de l'acheteur |
| `/notifications/` | `notifications` | Liste des notifications |
| `/notifications/<id>/lire/` | `mark_notification_read` | API marquer lue |
| `/commande/<id>/statut/` | `update_order_status` | Changer statut (vendeur) |
