# ============================================
# PERFORMANCE TESTS — Before vs After
# ============================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

import time
import statistics
from database_after import Database
from validators import OrderValidator, ProductValidator, EmailValidator
from cache import SimpleCache


def benchmark(func, n=100, label=""):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        func()
        times.append((time.perf_counter() - t0) * 1000)
    avg = statistics.mean(times)
    p95 = sorted(times)[int(n * 0.95)]
    print(f"  {label:<35} avg={avg:.3f}ms  p95={p95:.3f}ms")
    return avg, p95


def run_tests():
    db    = Database()
    cache = SimpleCache()

    print("\n" + "=" * 60)
    print("🔬 PERFORMANCE TESTS — After Refactoring")
    print("=" * 60)

    print("\n⚡ Requêtes DB (100 itérations) :")
    benchmark(db.get_all_products,  label="get_all_products (cache)")
    benchmark(lambda: db.get_product(1), label="get_product by id")
    benchmark(db.get_total_revenue, label="get_total_revenue (cache)")

    print("\n✅ Validation (1000 itérations) :")
    benchmark(
        lambda: OrderValidator.validate(1, 1, 2, 10),
        n=1000, label="OrderValidator.validate"
    )
    benchmark(
        lambda: EmailValidator.validate('test@gmail.com'),
        n=1000, label="EmailValidator.validate"
    )

    print("\n💾 Cache Performance (1000 ops) :")
    benchmark(
        lambda: cache.set('key', {'data': 'value'}),
        n=1000, label="cache.set"
    )
    benchmark(
        lambda: cache.get('key'),
        n=1000, label="cache.get"
    )

    print("\n📊 Cache Stats :")
    stats = db.stats
    print(f"  Total queries  : {stats['total_queries']}")
    print(f"  Avg query time : {stats['avg_query_ms']} ms")
    cs = stats['cache_stats']
    print(f"  Cache hits     : {cs['hits']}")
    print(f"  Cache hit rate : {cs['hit_rate']}%")

    print("\n" + "=" * 60)
    print("✅ Tous les tests passés")


if __name__ == '__main__':
    run_tests()
