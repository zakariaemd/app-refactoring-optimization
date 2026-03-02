# ============================================
# VALIDATORS — Validation centralisée
# ============================================

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    is_valid: bool
    errors:   List[str]

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.is_valid = False


class OrderValidator:
    MIN_QUANTITY = 1
    MAX_QUANTITY = 100

    @staticmethod
    def validate(client_id: int, product_id: int,
                 quantity: int, stock: int) -> ValidationResult:
        result = ValidationResult(is_valid=True, errors=[])

        if not isinstance(client_id, int) or client_id <= 0:
            result.add_error("client_id invalide")

        if not isinstance(product_id, int) or product_id <= 0:
            result.add_error("product_id invalide")

        if not isinstance(quantity, int) or \
           quantity < OrderValidator.MIN_QUANTITY or \
           quantity > OrderValidator.MAX_QUANTITY:
            result.add_error(
                f"Quantité doit être entre "
                f"{OrderValidator.MIN_QUANTITY} et "
                f"{OrderValidator.MAX_QUANTITY}"
            )

        if quantity > stock:
            result.add_error(
                f"Stock insuffisant : {stock} disponibles, "
                f"{quantity} demandés"
            )

        return result


class ProductValidator:
    @staticmethod
    def validate(name: str, price: float, stock: int) -> ValidationResult:
        result = ValidationResult(is_valid=True, errors=[])

        if not name or len(name.strip()) < 2:
            result.add_error("Nom produit trop court")

        if not isinstance(price, (int, float)) or price <= 0:
            result.add_error("Prix doit être positif")

        if not isinstance(stock, int) or stock < 0:
            result.add_error("Stock ne peut pas être négatif")

        return result


class EmailValidator:
    PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @classmethod
    def validate(cls, email: str) -> bool:
        return bool(cls.PATTERN.match(email))
