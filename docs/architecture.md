# Архитектура системы

## Выбранная архитектура

Приложение построено как трехзвенная клиент-серверная система:

1. Клиент: статический HTML/CSS/JavaScript интерфейс, работающий в браузере.
2. Сервер: Python FastAPI REST API с ролевой авторизацией.
3. Данные: PostgreSQL, хранящий пользователей, товары, складские движения, заказы и позиции заказов.

## UML: диаграмма компонентов

```mermaid
flowchart LR
    Browser["Браузер пользователя"]
    Frontend["Frontend\nHTML/CSS/JS"]
    API["Backend API\nFastAPI"]
    Auth["Auth/RBAC\nBearer tokens"]
    DB[("PostgreSQL")]

    Browser --> Frontend
    Frontend -->|"REST/JSON"| API
    API --> Auth
    API -->|"SQLAlchemy ORM"| DB
```

## UML: модель предметной области

```mermaid
classDiagram
    class User {
      int id
      string username
      string full_name
      Role role
      string password_hash
    }

    class Product {
      int id
      string sku
      string name
      string category
      string location
      int quantity
      int min_quantity
    }

    class StockMovement {
      int id
      MovementType movement_type
      int quantity
      string comment
    }

    class Order {
      int id
      string customer_name
      OrderStatus status
      datetime created_at
    }

    class OrderItem {
      int id
      int quantity
    }

    User "1" --> "*" Order
    Product "1" --> "*" StockMovement
    Order "1" --> "*" OrderItem
    Product "1" --> "*" OrderItem
```

## UML: сценарий создания заказа

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant UI as Frontend
    participant API as FastAPI
    participant DB as PostgreSQL

    User->>UI: Заполняет форму заказа
    UI->>API: POST /orders
    API->>API: Проверяет токен и роль
    API->>DB: Проверяет товары и остатки
    DB-->>API: Данные товара
    API->>DB: Создает заказ и позиции
    API-->>UI: 201 Created
    UI-->>User: Показывает новый заказ
```
