from .seed import seed_marketplace_products


if __name__ == "__main__":
    created = seed_marketplace_products()
    print(f"Created marketplace products: {created}")
