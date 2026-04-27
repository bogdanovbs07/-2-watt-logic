from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import products, categories

# Создаём все таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Watt Logic API v2.0",
    description="Curated marketplace for smart gadgets and charging solutions",
    version="2.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Заполнение БД тестовыми данными при первом запуске."""
    from .database import SessionLocal
    from . import models

    db = SessionLocal()

    # Создаём категории, если их нет
    if not db.query(models.Category).first():
        categories_data = [
            models.Category(
                name="Charger",
                description="Зарядные устройства и аксессуары"
            ),
            models.Category(
                name="Hub",
                description="USB-хабы и переходники"
            ),
            models.Category(
                name="Lighting",
                description="Умное освещение и лампы"
            ),
            models.Category(
                name="Audio",
                description="Наушники и аудиоустройства"
            ),
        ]
        db.add_all(categories_data)
        db.commit()

    # Создаём товары, если их нет
    if not db.query(models.Product).first():
        # Получаем категории
        charger = db.query(models.Category).filter(
            models.Category.name == "Charger"
        ).first()
        hub = db.query(models.Category).filter(
            models.Category.name == "Hub"
        ).first()
        lighting = db.query(models.Category).filter(
            models.Category.name == "Lighting"
        ).first()
        audio = db.query(models.Category).filter(
            models.Category.name == "Audio"
        ).first()

        test_products = [
            models.Product(
                name="MagSafe Charger",
                description="Беспроводная магнитная зарядка для iPhone 12-16",
                price=39.99,
                category_id=charger.id if charger else None
            ),
            models.Product(
                name="GaN Charger 65W",
                description="Компактное зарядное устройство на GaN-транзисторах",
                price=49.99,
                category_id=charger.id if charger else None
            ),
            models.Product(
                name="USB-C Hub 7-in-1",
                description="Хаб с HDMI 4K, USB-A 3.0, USB-C PD, SD-card",
                price=79.99,
                category_id=hub.id if hub else None
            ),
            models.Product(
                name="Thunderbolt 4 Dock",
                description="Док-станция с Thunderbolt 4, 2x HDMI, Ethernet",
                price=299.99,
                category_id=hub.id if hub else None
            ),
            models.Product(
                name="Smart LED Desk Lamp",
                description="Настольная лампа с Wi-Fi, голосовым управлением",
                price=49.99,
                category_id=lighting.id if lighting else None
            ),
            models.Product(
                name="Smart Light Strip 2m",
                description="Умная LED-лента с поддержкой Alexa и Google Home",
                price=29.99,
                category_id=lighting.id if lighting else None
            ),
            models.Product(
                name="Wireless Earbuds Pro",
                description="Беспроводные наушники с ANC и пространственным звуком",
                price=149.99,
                category_id=audio.id if audio else None
            ),
            models.Product(
                name="Bluetooth Speaker",
                description="Портативная колонка с защитой IPX7 и басами",
                price=59.99,
                category_id=audio.id if audio else None
            ),
        ]
        db.add_all(test_products)
        db.commit()

    db.close()


# Подключаем роутеры
app.include_router(products.router)
app.include_router(categories.router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Welcome to Watt Logic API v2.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
