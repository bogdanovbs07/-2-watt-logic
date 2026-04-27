import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models

# Создаём тестовую БД в памяти
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def override_get_db():
    """Переопределяем зависимость get_db для тестов."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """Создаём таблицы перед каждым тестом и удаляем после."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    """Фикстура тестового клиента с переопределённой БД."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def db_session():
    """Фикстура для прямого доступа к тестовой БД."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def sample_categories(db_session):
    """Фикстура с тестовыми категориями."""
    categories = [
        models.Category(name="Charger", description="Зарядные устройства"),
        models.Category(name="Hub", description="USB-хабы"),
        models.Category(name="Lighting", description="Освещение"),
    ]
    db_session.add_all(categories)
    db_session.commit()
    for cat in categories:
        db_session.refresh(cat)
    return categories


@pytest.fixture()
def sample_products(db_session, sample_categories):
    """Фикстура с тестовыми товарами."""
    products = [
        models.Product(
            name="MagSafe Charger",
            description="Беспроводная зарядка",
            price=39.99,
            category_id=sample_categories[0].id
        ),
        models.Product(
            name="USB-C Hub",
            description="Хаб на 7 портов",
            price=79.99,
            category_id=sample_categories[1].id
        ),
        models.Product(
            name="LED Desk Lamp",
            description="Настольная лампа",
            price=49.99,
            category_id=sample_categories[2].id
        ),
        models.Product(
            name="Wireless Earbuds",
            description="Беспроводные наушники",
            price=149.99,
            category_id=None
        ),
        models.Product(
            name="Bluetooth Speaker",
            description="Портативная колонка",
            price=59.99,
            category_id=None
        ),
    ]
    db_session.add_all(products)
    db_session.commit()
    for prod in products:
        db_session.refresh(prod)
    return products
