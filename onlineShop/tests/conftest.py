import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)  
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()   
    connection.close()



@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_auth_headers(client, db):
    from modules.users.model import User
    from core.security import hash_password

    admin = User(
        name="Admin",
        email="admin@test.com",
        password=hash_password("adminpass1"),
        mobile="9000000000",
        role="admin",
    )
    db.add(admin)
    db.commit()

    response = client.post("/api/auth/login", data={
        "username": "admin@test.com",   
        "password": "adminpass1",
    })
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}



@pytest.fixture(scope="function")
def customer_auth_headers(client, db):
    from modules.users.model import User
    from core.security import hash_password

    customer = User(
        name="Customer",
        email="customer@test.com",
        password=hash_password("customerpass1"),
        mobile="9111111111",
        role="customer",
    )
    db.add(customer)
    db.commit()

    response = client.post("/api/auth/login", data={
        "username": "customer@test.com",
        "password": "customerpass1",
    })
    assert response.status_code == 200, f"Customer login failed: {response.json()}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}