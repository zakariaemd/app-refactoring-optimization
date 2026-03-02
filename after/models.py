# ============================================
# MODELS — Dataclasses typées
# ============================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class OrderStatus(Enum):
    PENDING   = "pending"
    PAID      = "paid"
    SHIPPED   = "shipped"
    CANCELLED = "cancelled"


@dataclass
class Category:
    id:   int
    name: str


@dataclass
class Product:
    id:          int
    name:        str
    price:       float
    stock:       int
    category_id: int
    created_at:  datetime
    category:    Optional[Category] = None

    def is_available(self, qty: int = 1) -> bool:
        return self.stock >= qty

    def to_dict(self) -> dict:
        return {
            'id':       self.id,
            'name':     self.name,
            'price':    self.price,
            'stock':    self.stock,
            'category': self.category.name if self.category else None
        }


@dataclass
class Client:
    id:         int
    email:      str
    city:       str
    country:    str
    created_at: datetime


@dataclass
class OrderItem:
    id:         int
    product_id: int
    quantity:   int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    id:         int
    client_id:  int
    status:     OrderStatus
    created_at: datetime
    items:      List[OrderItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return round(sum(i.subtotal for i in self.items), 2)

    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self.items)
