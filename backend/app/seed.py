from . import models
from .database import SessionLocal
from .security import hash_password


MARKETPLACE_PRODUCTS = [
    ("WB-DRS-001", "Платье женское базовое", "Одежда", "WB-A-01", 86, 12),
    ("WB-TSH-002", "Футболка мужская хлопковая", "Одежда", "WB-A-02", 140, 25),
    ("WB-HDY-003", "Худи унисекс oversize", "Одежда", "WB-A-03", 64, 10),
    ("WB-JNS-004", "Джинсы прямые женские", "Одежда", "WB-A-04", 52, 8),
    ("WB-SNK-005", "Кроссовки повседневные", "Обувь", "WB-B-01", 78, 12),
    ("WB-BAG-006", "Рюкзак городской черный", "Аксессуары", "WB-B-02", 44, 7),
    ("WB-CAP-007", "Бейсболка однотонная", "Аксессуары", "WB-B-03", 95, 15),
    ("WB-SOX-008", "Набор носков 5 пар", "Одежда", "WB-A-05", 210, 30),
    ("WB-BED-009", "Комплект постельного белья", "Дом", "WB-C-01", 37, 6),
    ("WB-TWL-010", "Полотенце банное махровое", "Дом", "WB-C-02", 115, 20),
    ("WB-LMP-011", "Настольная лампа LED", "Дом", "WB-C-03", 33, 5),
    ("WB-ORG-012", "Органайзер для косметики", "Дом", "WB-C-04", 59, 9),
    ("WB-SHM-013", "Шампунь восстанавливающий", "Красота", "WB-D-01", 123, 18),
    ("WB-CRM-014", "Крем для лица увлажняющий", "Красота", "WB-D-02", 88, 14),
    ("WB-MSK-015", "Маска тканевая для лица", "Красота", "WB-D-03", 260, 40),
    ("WB-TOY-016", "Конструктор детский набор", "Детские товары", "WB-E-01", 42, 6),
    ("WB-BTL-017", "Бутылочка для воды детская", "Детские товары", "WB-E-02", 73, 11),
    ("WB-BOK-018", "Книга развивающая для детей", "Книги", "WB-E-03", 68, 10),
    ("WB-PAN-019", "Сковорода антипригарная 26 см", "Кухня", "WB-F-01", 31, 5),
    ("WB-CUP-020", "Набор кружек 4 штуки", "Кухня", "WB-F-02", 56, 8),
    ("WB-KNF-021", "Набор кухонных ножей", "Кухня", "WB-F-03", 29, 5),
    ("WB-YGM-022", "Коврик для йоги нескользящий", "Спорт", "WB-G-01", 46, 7),
    ("WB-DMB-023", "Гантели неопреновые 2 кг", "Спорт", "WB-G-02", 38, 6),
    ("WB-PWR-024", "Power bank 10000 mAh", "Электроника", "WB-H-01", 84, 13),
    ("WB-CBL-025", "Кабель USB-C 1 метр", "Электроника", "WB-H-02", 190, 30),
    ("OZ-PHN-026", "Смартфон Android 128 ГБ", "Электроника", "OZ-A-01", 24, 4),
    ("OZ-EAR-027", "Наушники беспроводные", "Электроника", "OZ-A-02", 67, 10),
    ("OZ-KBD-028", "Клавиатура беспроводная", "Электроника", "OZ-A-03", 35, 6),
    ("OZ-MSE-029", "Мышь компьютерная", "Электроника", "OZ-A-04", 74, 12),
    ("OZ-MON-030", "Монитор 24 дюйма", "Электроника", "OZ-A-05", 18, 3),
    ("OZ-CHR-031", "Зарядное устройство 65W", "Электроника", "OZ-A-06", 92, 14),
    ("OZ-FLT-032", "Фильтр для воды сменный", "Дом", "OZ-B-01", 105, 16),
    ("OZ-VAC-033", "Пылесос вертикальный", "Бытовая техника", "OZ-B-02", 21, 4),
    ("OZ-IRN-034", "Утюг с паром", "Бытовая техника", "OZ-B-03", 28, 5),
    ("OZ-MCR-035", "Микроволновая печь 20 л", "Бытовая техника", "OZ-B-04", 16, 3),
    ("OZ-COF-036", "Кофеварка капельная", "Бытовая техника", "OZ-B-05", 19, 3),
    ("OZ-FOO-037", "Корм для кошек 2 кг", "Зоотовары", "OZ-C-01", 132, 22),
    ("OZ-LTR-038", "Наполнитель для лотка", "Зоотовары", "OZ-C-02", 98, 15),
    ("OZ-CHM-039", "Автошампунь концентрат", "Авто", "OZ-D-01", 61, 10),
    ("OZ-OIL-040", "Моторное масло 5W-40", "Авто", "OZ-D-02", 47, 8),
    ("OZ-TRE-041", "Домкрат гидравлический", "Авто", "OZ-D-03", 14, 3),
    ("OZ-NBK-042", "Блокнот A5 в клетку", "Канцелярия", "OZ-E-01", 180, 30),
    ("OZ-PEN-043", "Ручки шариковые набор", "Канцелярия", "OZ-E-02", 240, 35),
    ("OZ-PRN-044", "Бумага офисная A4", "Канцелярия", "OZ-E-03", 120, 20),
    ("OZ-CHA-045", "Кресло офисное эргономичное", "Мебель", "OZ-F-01", 23, 4),
    ("OZ-DSK-046", "Стол письменный компактный", "Мебель", "OZ-F-02", 17, 3),
    ("OZ-SHL-047", "Стеллаж металлический", "Мебель", "OZ-F-03", 22, 4),
    ("OZ-TEA-048", "Чай черный листовой", "Продукты", "OZ-G-01", 150, 25),
    ("OZ-COC-049", "Какао порошок натуральный", "Продукты", "OZ-G-02", 83, 13),
    ("OZ-NUT-050", "Ореховая смесь 500 г", "Продукты", "OZ-G-03", 70, 12),
]


def seed_marketplace_products() -> int:
    db = SessionLocal()
    created = 0
    try:
        existing_skus = {
            sku for (sku,) in db.query(models.Product.sku).filter(
                models.Product.sku.in_([item[0] for item in MARKETPLACE_PRODUCTS])
            )
        }
        for sku, name, category, location, quantity, min_quantity in MARKETPLACE_PRODUCTS:
            if sku in existing_skus:
                continue
            db.add(
                models.Product(
                    sku=sku,
                    name=name,
                    category=category,
                    location=location,
                    quantity=quantity,
                    min_quantity=min_quantity,
                )
            )
            created += 1
        db.commit()
        return created
    finally:
        db.close()


def seed_database() -> None:
    db = SessionLocal()
    try:
        if db.query(models.User).count() > 0:
            seed_marketplace_products()
            return

        users = [
            models.User(
                username="admin",
                full_name="Administrator",
                role=models.Role.ADMIN,
                password_hash=hash_password("admin123"),
            ),
            models.User(
                username="manager",
                full_name="Warehouse Manager",
                role=models.Role.MANAGER,
                password_hash=hash_password("manager123"),
            ),
            models.User(
                username="clerk",
                full_name="Order Clerk",
                role=models.Role.CLERK,
                password_hash=hash_password("clerk123"),
            ),
        ]
        db.add_all(users)
        db.commit()
    finally:
        db.close()

    seed_marketplace_products()
