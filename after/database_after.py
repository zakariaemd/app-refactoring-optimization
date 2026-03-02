# ============================================
# DATABASE — Connection Pool + Requêtes optimisées
# ============================================

from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import time
from models import Product, Category, Order, OrderItem, OrderStatus, Client
from cache import cached, cache
from validators import OrderValidator
from datetime import datetime


class Database:
    """
    Simule une couche d'accès aux données optimisée.
    En production : remplacer par mysql-connector avec pool.
    """

    def __init__(self):
        self._query_count  = 0
        self._query_time   = 0.0
        self._slow_queries: List[dict] = []
        self._categories   = self._seed_categories()
        self._products     = self._seed_products()
        self._clients      = self._seed_clients()
        self._orders       = self._seed_orders()

    # ============================================
    # SEED DATA (simule MySQL)
    # ============================================
    def _seed_categories(self) -> Dict[int, Category]:
        data = [(1,'Électronique'),(2,'Mode'),(3,'Maison & Jardin'),
                (4,'Sport'),(5,'Beauté'),(6,'Livres')]
        return {d[0]: Category(id=d[0], name=d[1]) for d in data}

    def _seed_products(self) -> Dict[int, Product]:
        data = [
            (1,'Smartphone X12',     599.99, 50, 1),
            (2,'Écouteurs Pro',       89.99,120, 1),
            (3,'Laptop UltraSlim', 1199.99, 30, 1),
            (4,'T-Shirt Premium',    29.99,200, 2),
            (5,'Jean Slim Fit',      59.99,150, 2),
            (6,'Chaise Ergonomique',299.99, 40, 3),
            (7,'Tapis de Yoga',      39.99,100, 4),
            (8,'Montre Sport GPS',  249.99, 60, 4),
            (9,'Crème SPF50',        24.99,180, 5),
            (10,'Marketing Digital', 34.99,150, 6),
        ]
        return {
            d[0]: Product(
                id=d[0], name=d[1], price=d[2], stock=d[3],
                category_id=d[4], created_at=datetime(2024,1,1),
                category=self._seed_categories().get(d[4])
            ) for d in data
        }

    def _seed_clients(self) -> Dict[int, Client]:
        data = [
            (1,'alice@test.com','Paris','France'),
            (2,'bob@test.com','Lyon','France'),
            (3,'carol@test.com','Marseille','France'),
        ]
        return {
            d[0]: Client(id=d[0], email=d[1], city=d[2],
                         country=d[3], created_at=datetime(2024,1,1))
            for d in data
        }

    def _seed_orders(self) -> Dict[int, Order]:
        return {
            1: Order(id=1, client_id=1, status=OrderStatus.PAID,
                     created_at=datetime(2024,1,10),
                     items=[OrderItem(1,1,1,599.99), OrderItem(2,2,1,89.99)]),
            2: Order(id=2, client_id=2, status=OrderStatus.PAID,
                     created_at=datetime(2024,2,1),
                     items=[OrderItem(3,3,1,1199.99)]),
        }

    # ============================================
    # QUERY TRACKER
    # ============================================
    @contextmanager
    def _track_query(self, name: str):
        start = time.perf_counter()
        yield
        elapsed = (time.perf_counter() - start) * 1000
        self._query_count += 1
        self._query_time  += elapsed
        if elapsed > 100:
            self._slow_queries.append({'query': name, 'ms': round(elapsed, 2)})

    # ============================================
    # OPTIMIZED QUERIES ✅
    # ============================================

    @cached(key_prefix='products_all', ttl=600)
    def get_all_products(self) -> List[Product]:
        """✅ JOIN en une seule requête + cache 10 min"""
        with self._track_query('get_all_products'):
            time.sleep(0.005)  # simule latence DB
        return list(self._products.values())

    @cached(key_prefix='product', ttl=300)
    def get_product(self, product_id: int) -> Optional[Product]:
        """✅ Requête indexée + cache"""
        with self._track_query(f'get_product:{product_id}'):
            time.sleep(0.001)
        return self._products.get(product_id)

    @cached(key_prefix='revenue', ttl=60)
    def get_total_revenue(self) -> float:
        """✅ Agrégation SQL côté serveur + cache 1 min"""
        with self._track_query('get_total_revenue'):
            time.sleep(0.003)
        return round(sum(
            o.total for o in self._orders.values()
            if o.status == OrderStatus.PAID
        ), 2)

    def create_order(self, client_id: int,
                     product_id: int, quantity: int) -> dict:
        """✅ Validation + transaction + invalidation cache"""
        product = self.get_product(product_id)
        if not product:
            return {'success': False, 'error': 'Produit introuvable'}

        validation = OrderValidator.validate(
            client_id, product_id, quantity, product.stock
        )
        if not validation.is_valid:
            return {'success': False, 'errors': validation.errors}

        with self._track_query('create_order'):
            # ✅ Mise à jour stock atomique
            self._products[product_id].stock -= quantity
            new_id = max(self._orders.keys(), default=0) + 1
            self._orders[new_id] = Order(
                id=new_id, client_id=client_id,
                status=OrderStatus.PENDING,
                created_at=datetime.now(),
                items=[OrderItem(new_id, product_id,
                                 quantity, product.price)]
            )
            # ✅ Invalider le cache revenue
            cache.invalidate('revenue:')
            cache.invalidate(f'product:{product_id}')

        return {'success': True, 'order_id': new_id,
                'total': round(quantity * product.price, 2)}

    @property
    def stats(self) -> dict:
        return {
            'total_queries':  self._query_count,
            'total_time_ms':  round(self._query_time, 2),
            'avg_query_ms':   round(
                self._query_time / self._query_count, 2
            ) if self._query_count > 0 else 0,
            'slow_queries':   self._slow_queries,
            'cache_stats':    cache.stats
        }
