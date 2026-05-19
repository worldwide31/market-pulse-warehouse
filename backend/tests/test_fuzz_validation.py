import re

from hypothesis import given, strategies as st
from pydantic import ValidationError

from app.schemas import ProductCreate, UserCreate


invalid_roles = st.text(min_size=1).filter(lambda value: value not in {"admin", "manager", "clerk"})
sku_pattern = re.compile(r"^[A-Z0-9-]+$")


@given(role=invalid_roles)
def test_fuzz_rejects_unknown_roles(role):
    try:
        UserCreate(
            username="fuzzuser",
            full_name="Fuzz User",
            role=role,
            password="secret123",
        )
    except ValidationError:
        return
    raise AssertionError(f"Invalid role accepted: {role}")


@given(quantity=st.integers(max_value=-1))
def test_fuzz_rejects_negative_product_quantity(quantity):
    try:
        ProductCreate(
            sku="FUZZ-001",
            name="Fuzz Product",
            category="Fuzz",
            location="F-01",
            quantity=quantity,
            min_quantity=0,
        )
    except ValidationError:
        return
    raise AssertionError(f"Negative quantity accepted: {quantity}")


@given(sku=st.text(min_size=1, max_size=12).filter(lambda value: not sku_pattern.fullmatch(value)))
def test_fuzz_rejects_invalid_sku_format(sku):
    try:
        ProductCreate(
            sku=sku,
            name="Fuzz Product",
            category="Fuzz",
            location="F-01",
            quantity=1,
            min_quantity=0,
        )
    except ValidationError:
        return
    raise AssertionError(f"Invalid SKU accepted: {sku}")
