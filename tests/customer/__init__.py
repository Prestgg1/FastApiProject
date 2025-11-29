

from services.crypto_service import CryptoService
from models.user import User
from models.customer import Customer
from datetime import datetime, timezone
from models.user import UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
import pytest_asyncio


@pytest_asyncio.fixture(name="sample_customers")
async def sample_customers_fixture(session: AsyncSession):
    users_data = [
        {
            "name": "Aysel Məmmədova",
            "email": "aysel@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": True,
        },
        {
            "name": "Elvin Həsənov",
            "email": "elvin@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": True,
        },
        {
            "name": "Leyla Quliyeva",
            "email": "leyla@example.com",
            "password": CryptoService.hash_password("password123"),
            "role": UserRole.customer,
            "status": False,
        },
    ]

    users = []
    for user_data in users_data:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password= user_data["password"],
            role= UserRole.customer,
            status=user_data["status"]
        )
        session.add(user)
        users.append(user)

    await session.commit()

    for user in users:
        await session.refresh(user)

    customers_data = [
        {
            "user_id": users[0].id,
            "finCode": "1AABBCC",
            "phone": "+994501234567",
            "birthday": datetime(1995, 5, 15),
            "city": "Bakı",
            "region": "Nəsimi",
            "street": "28 May küçəsi",
            "address": "Bina 123, Mənzil 45",
            "gender": "female",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "user_id": users[1].id,
            "finCode": "2CCDDEE",
            "phone": "+994552345678",
            "birthday": datetime(1990, 8, 20),
            "city": "Bakı",
            "region": "Yasamal",
            "street": "Azadlıq prospekti",
            "address": "Bina 45, Mənzil 12",
            "gender": "male",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "user_id": users[2].id,
            "finCode": "3EEFFGG",
            "phone": "+994703456789",
            "birthday": datetime(1988, 12, 10),
            "city": "Gəncə",
            "region": "Kəpəz",
            "street": "Heydər Əliyev prospekti",
            "address": "Bina 78, Mənzil 23",
            "gender": "female",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        session.add(customer)
        customers.append(customer)
    await session.commit()
    for customer in customers:
        await session.refresh(customer)
    return customers
