# Healthcare Management System

A modern, scalable healthcare management platform built with FastAPI, following industry best practices and clean architecture principles.

## 🎯 Project Philosophy

This project is built with a strong focus on:

- **SOLID Principles** - Especially Single Responsibility Principle (SRP)
- **KISS** (Keep It Simple, Stupid) - Simple, maintainable code
- **DRY** (Don't Repeat Yourself) - Reusable components
- **Separation of Concerns** - Clear boundaries between layers
- **Clean Architecture** - Independent, testable business logic

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│         Routes (API Layer)          │  ← HTTP handlers, validation
├─────────────────────────────────────┤
│      Services (Business Logic)      │  ← Core business rules
├─────────────────────────────────────┤
│       Models (Data Layer)           │  ← Database entities
├─────────────────────────────────────┤
│         Database (SQLModel)         │  ← Data persistence
└─────────────────────────────────────┘
```

### Directory Structure

```
project/
├── services/              # Business logic layer (SRP compliant)
│   ├── __init__.py
│   ├── user_service.py    # User CRUD operations
│   ├── customer_service.py
│   ├── doctor_service.py
│   ├── auth_service.py    # Authentication logic
│   └── crypto_service.py  # Password hashing
│
├── routes/                # API endpoints (thin controllers)
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── user_routes.py
│   └── customer_routes.py
│
├── models/                # SQLModel entities
│   ├── __init__.py
│   ├── user.py
│   ├── customer.py
│   ├── doctor.py
│   └── refresh_token.py
│
├── schemas/               # Pydantic schemas for validation
│   ├── __init__.py
│   ├── user_schema.py
│   └── auth_schema.py
│
├── database.py           # Database configuration
├── main.py              # Application entry point
└── .env                 # Environment variables
```

## ✨ Key Features

### Service Layer Pattern

Each service handles a single entity with complete CRUD operations:

```python
class UserService:
    """Handles all User-related operations"""
    
    @staticmethod
    async def get_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
        """Single responsibility: Get user by ID"""
        return await db.get(User, user_id)
    
    @staticmethod
    async def create(email: str, password: str, name: str, role: UserRole, db: AsyncSession) -> User:
        """Single responsibility: Create new user"""
        # Validation
        # Business logic
        # Database operation
```

**Benefits:**
- ✅ Each service has one reason to change
- ✅ Easy to test in isolation
- ✅ Reusable across different routes
- ✅ Clear separation of concerns

### Authentication System

JWT-based authentication with refresh tokens:

- Access tokens (15 minutes)
- Refresh tokens (30 days)
- Device-based session management
- Password hashing with bcrypt
- Token revocation support

### Database Flexibility

Supports both PostgreSQL and SQLite with automatic environment detection:

```python
# Development: SQLite (automatic)
ENVIRONMENT=development

# Production: PostgreSQL
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (auto-setup for dev)
- Redis (optional, for caching)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd healthcare-platform
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
python manage_db.py init
```

6. Run the application:
```bash
uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API documentation

## 🔐 Environment Variables

```env
# Environment
ENVIRONMENT=development  # development, staging, production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Authentication
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis (optional)
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
```

## 📚 API Documentation

### Authentication Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe",
  "finCode": "1234567",
  "phone": "+994501234567",
  "device_id": "web-browser-chrome"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "device_id": "web-browser-chrome"
}
```

#### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token",
  "device_id": "web-browser-chrome"
}
```

#### Protected Route Example
```http
GET /auth/me
Authorization: Bearer <access_token>
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_user_service.py
```

## 🎨 Code Style & Best Practices

### SOLID Principles in Action

#### Single Responsibility Principle (SRP)
Each service handles only one entity:
- `UserService` → User operations only
- `CustomerService` → Customer operations only
- `AuthService` → Authentication logic only

#### Open/Closed Principle
Services are open for extension but closed for modification through inheritance and composition.

#### Dependency Inversion
High-level modules (routes) depend on abstractions (service interfaces), not concrete implementations.

### KISS (Keep It Simple, Stupid)

```python
# ❌ Complex, hard to maintain
async def complex_user_creation(data, db, validate, hash, create, notify):
    if validate(data):
        hashed = hash(data.password)
        user = create(data, hashed)
        notify(user)
        return user

# ✅ Simple, clear, maintainable
async def create_user(email: str, password: str, name: str, db: AsyncSession):
    user = User(email=email, password=hash_password(password), name=name)
    db.add(user)
    await db.commit()
    return user
```

### DRY (Don't Repeat Yourself)

```python
# Reusable service methods instead of duplicating code
user = await UserService.get_by_email(email, db)  # Used everywhere
customer = await CustomerService.get_by_user_id(user_id, db)  # Reusable
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Refresh token rotation
- Device-based session management
- SQL injection prevention (SQLModel ORM)
- Input validation with Pydantic
- CORS configuration
- Rate limiting ready

## 📊 Database Management

```bash
# Initialize database
python manage_db.py init

# Reset database (development only)
python manage_db.py reset
```

### Environment-Specific Configs

- Development: SQLite, debug logging
- Staging: PostgreSQL, info logging
- Production: PostgreSQL, error logging, Redis cache

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow the coding standards
4. Write tests for new features
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Coding Standards

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Keep functions small and focused (SRP)
- Write unit tests for services
- Use async/await consistently

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- SQLModel for elegant ORM
- Pydantic for robust validation
- The open-source community

## 📧 Contact

Project Maintainer - Your Name
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

