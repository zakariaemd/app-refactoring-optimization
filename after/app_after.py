# ============================================
# APP AFTER REFACTORING ✅
# Architecture propre, modulaire, optimisée
# ============================================

from database_after import Database
from validators import EmailValidator
import time

def run_demo():
    """Démonstration complète de l'application refactorisée"""
    db = Database()

    print("=" * 55)
    print("✅ APP AFTER REFACTORING — Démonstration")
    print("=" * 55)

    # 1. GET PRODUCTS — avec cache
    print("\n📦 1. Récupération produits (avec cache)...")
    t0 = time.perf_counter()
    products = db.get_all_products()
    t1 = time.perf_counter()
    print(f"   → {len(products)} produits en {(t1-t0)*1000:.2f}ms")

    # 2. Deuxième appel → cache hit
    t0 = time.perf_counter()
    products = db.get_all_products()
    t1 = time.perf_counter()
    print(f"   → Cache hit : {(t1-t0)*1000:.2f}ms ⚡")

    # 3. CREATE ORDER — avec validation
    print("\n🛒 2. Création commande avec validation...")
    result = db.create_order(
        client_id=1, product_id=1, quantity=2
    )
    print(f"   → {result}")

    # 4. Validation erreur
    result_err = db.create_order(
        client_id=-1, product_id=999, quantity=500
    )
    print(f"   → Erreur attendue : {result_err}")

    # 5. Email validation
    print("\n📧 3. Validation emails...")
    emails = ['valid@gmail.com', 'invalid-email', 'test@domain.fr']
    for e in emails:
        valid = EmailValidator.validate(e)
        print(f"   {e:<30} → {'✅' if valid else '❌'}")

    # 6. Revenue
    print("\n💰 4. Calcul CA total...")
    revenue = db.get_total_revenue()
    print(f"   → CA Total : {revenue:,.2f} €")

    # 7. Stats DB
    print("\n📊 5. Stats Base de Données :")
    stats = db.stats
    for k, v in stats.items():
        if k != 'slow_queries':
            print(f"   {k:<20} : {v}")

    print("\n" + "=" * 55)
    print("✅ Démonstration terminée")

if __name__ == '__main__':
    run_demo()
