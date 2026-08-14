# ABCApp Online Shopping Platform

ABCApp is a modular FastAPI-based online shopping backend designed to support authentication, user management, product catalog operations, shopping carts, orders, payments, shipping, notifications, and administrative capabilities.

All business capabilities run within one FastAPI application, while shared infrastructure, business modules,and tests are separated into dedicated packages.

## Project Status

**Current stage:** Backend development and architecture hardening

### Implemented or structurally established

- FastAPI application entry point -> The application entry point is where the FastAPI application starts.
                                   Typical request flow:
                                   Client → main.py → Router → Service → Repository → Database
- Shared configuration and database foundation -> Files:core/config.py and core/database.py
- Dependency injection -> Dependency injection means that a function receives the resources it needs from the framework instead of creating those resources itself
- JWT-based authentication foundation -> JWT means JSON Web Token. It is a signed token used to prove that a user has already authenticated.Authentication answers:“Who is this user?”Authorization answers:“What is this user allowed to do?”
- Bcrypt password hashing -> Used by: Authentication and user-management functionality.Bcrypt is a one-way password-hashing algorithm
- Role-based authorization foundation -> Implements JWT-based authentication with role-aware access control for three user types — customer, seller, and admin.
  Every protected endpoint verifies token validity, user role, and resource ownership before processing the request.
- User management module -> Handles user registration, login, and profile management with bcrypt password hashing and secure JWT token issuance.
Ensures email uniqueness, enforces role assignment at registration, and never exposes passwords in any API response.
- Product catalog module -> Provides full product and category management — sellers can create and manage their own listings while admins oversee all.
Enforces business rules such as unique product names, valid category references, and stock availability on every operation.
- Shopping cart module -> Allows authenticated users to add, update, and remove products from a persistent cart tied to their account.
Validates stock availability on every cart action and prevents duplicate entries by updating quantity instead.
- Order management module -> Converts a user's cart into a confirmed order, deducting stock and recording line items with unit prices at checkout time.
Tracks each order through a full status lifecycle — from pending through processing, shipped, and delivered.
- Payment service module -> Processes payments asynchronously via an external payment gateway and updates order status based on the transaction result.
On success, triggers shipment creation and receipt notification; on failure, restores stock and alerts the user.
- Payment, shipping, and notification clients -> Encapsulates all external API communication in a dedicated integration layer built on a shared base client.
Centralises timeout handling, authentication headers, and error normalisation — making providers easy to swap or mock.
- Service-level unit tests -> Tests all core business logic in isolation using MagicMock to replace database repositories — no real DB required.
Covers auth, cart, catalog, order, and user services, verifying that every business rule behaves correctly under all conditions.
- Pytest configuration -> Provides a centralised conftest.py with reusable fixtures for test database sessions, HTTP client, and pre-built users with tokens.
Eliminates repeated setup code across all test files, ensuring consistent and reliable test environments throughout the suite.
- Application logging -> Configures structured logging at startup with consistent timestamp, level, and module-name formatting across the entire application.


## Objectives


1. Provide secure user and seller authentication.
2. Support role-based access to platform capabilities.
3. Manage products through a structured catalog module.
4. Support shopping carts and order processing.
5. Integrate with payment, shipping, and notification providers.
6. Separate API delivery, business rules, persistence, and integrations.
7. Provide a testable and maintainable backend architecture.
8. Establish a foundation for future inventory, checkout, and fulfillment capabilities.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy ORM
- Pydantic schemas
- OAuth2 password flow
- JSON Web Tokens
- Passlib
- Bcrypt
- Python-JOSE
- Pytest
- Relational database supported by SQLAlchemy
- File-based application logging



### Architectural Style

- The application runs as one deployable FastAPI backend.
- Business capabilities are separated into modules.
- Shared infrastructure is centralized under `core`.
- External systems are accessed through `integration` adapters.
- Business logic is implemented in services.
- Database access is isolated in repositories.
- Unit tests are maintained under `tests`.

This approach is appropriate for an MVP because it provides clear boundaries without the operational complexity of multiple independently deployed microservices.

### Architecture Layers

| Layer | Location | Responsibility |
|---|---|---|
| Application entry point | `main.py` | Creates the FastAPI application and registers routers |
| API layer | Module `router.py` files | Defines endpoints, dependencies, status codes, and HTTP responses |
| Validation layer | Module `schema.py` files | Validates request data and formats response data |
| Business layer | Module `service.py` files | Applies business rules and coordinates operations |
| Persistence layer | Module `repository.py` files | Performs database queries and persistence operations |
| Data model layer | Module `model.py` files | Defines SQLAlchemy entities and relationships |
| Core infrastructure | `core/` | Provides shared configuration, security, database, logging, and utilities |
| Integration layer | `integration/` | Communicates with payment, shipping, and notification providers |
| Testing layer | `tests/` | Validates services, business rules, and future API integrations |



## Confirmed Repository Structure

The following structure reflects the folders and files visible in the architecture screenshots.

### Source structure

```text
ABCApp/
└── onlineShop/
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── database.py
    │   ├── dependencies.py
    │   ├── exceptions.py
    │   ├── logging_config.py
    │   ├── security.py
    │   └── utils.py
    │
    ├── integration/
    │   ├── __init__.py
    │   ├── base_client.py
    │   ├── notification_client.py
    │   ├── payment_gateway.py
    │   └── shipping_client.py
    │
    ├── modules/
    │   ├── admin/
    │   │   ├── __init__.py
    │   │   └── router.py
    │   │
    │   ├── auth/
    │   │   └── Internal files not expanded in screenshots
    │   │
    │   ├── cart/
    │   │   └── Internal files not expanded in screenshots
    │   │
    │   ├── catalog/
    │   │   ├── __init__.py
    │   │   ├── model.py
    │   │   ├── repository.py
    │   │   ├── router.py
    │   │   ├── schema.py
    │   │   └── service.py
    │   │
    │   ├── orders/
    │   │   ├── __init__.py
    │   │   ├── model.py
    │   │   ├── repository.py
    │   │   ├── router.py
    │   │   ├── schema.py
    │   │   └── service.py
    │   │
    │   ├── payment/
    │   │   ├── __init__.py
    │   │   ├── router.py
    │   │   ├── schema.py
    │   │   └── service.py
    │   │
    │   └── users/
    │       ├── __init__.py
    │       ├── model.py
    │       ├── repository.py
    │       ├── router.py
    │       ├── schema.py
    │       └── service.py
    │
    ├── tests/
    │   ├── unit/
    │   │   ├── test_auth_services.py
    │   │   ├── test_cart_service.py
    │   │   ├── test_catalog_service.py
    │   │   ├── test_order_service.py
    │   │   └── test_user_service.py
    │   └── conftest.py
    │
    ├── main.py
    ├── pytest.ini
    └── requirements.txt

```

