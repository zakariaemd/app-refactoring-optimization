# ============================================
# APP BEFORE REFACTORING ❌
# Problèmes : pas de cache, requêtes N+1,
# pas de validation, code non structuré
# ============================================

import mysql.connector
import json
import time

# Connexion recréée à chaque requête ❌
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root",
        password="", database="ecommerce"
    )

# ❌ Problème N+1 : 1 requête par produit
def get_products_with_category():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    result = []
    for p in products:
        cursor.execute(
            f"SELECT * FROM categories WHERE id={p[4]}"  # ❌ SQL injection possible
        )
        cat = cursor.fetchone()
        result.append({
            'id': p[0], 'name': p[1],
            'price': p[2], 'category': cat
        })
    db.close()
    return result

# ❌ Pas de validation des entrées
def create_order(client_id, product_id, quantity):
    db = get_db()
    cursor = db.cursor()
    # ❌ Pas de vérification stock
    # ❌ Pas de transaction
    cursor.execute(
        f"INSERT INTO orders VALUES (NULL, {client_id}, NOW(), 'pending')"
    )
    order_id = cursor.lastrowid
    cursor.execute(
        f"INSERT INTO order_items VALUES "
        f"(NULL, {order_id}, {product_id}, {quantity}, 0)"
    )
    db.commit()
    db.close()
    return order_id

# ❌ Calcul du CA sans index, sans cache
def get_total_revenue():
    db = get_db()
    cursor = db.cursor()
    # ❌ Charge TOUTES les commandes en mémoire
    cursor.execute("SELECT * FROM orders WHERE status='paid'")
    orders = cursor.fetchall()
    total = 0
    for o in orders:
        total += o[2]  # ❌ Index magique non documenté
    db.close()
    return total

# ❌ Fonction 200 lignes sans découpage
def process_everything(data):
    # validation + traitement + email + log = tout dans 1 fonction
    pass
