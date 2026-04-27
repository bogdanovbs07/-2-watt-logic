from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import products

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Watt Logic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from .database import SessionLocal
    from . import models
    db = SessionLocal()
    if not db.query(models.Product).first():
        test_products = [
            models.Product(
                name="MagSafe Charger",
                description="Беспроводная зарядка для iPhone",
                price=39.99,
                category="Charger"
            ),
            models.Product(
                name="USB-C Hub 7-in-1",
                description="Хаб с HDMI, USB-A, USB-C и SD-картой",
                price=79.99,
                category="Hub"
            ),
            models.Product(
                name="Smart LED Desk Lamp",
                description="Настольная лампа с Wi-Fi и голосовым управлением",
                price=49.99,
                category="Lighting"
            ),
        ]
        db.add_all(test_products)
        db.commit()
    db.close()

app.include_router(products.router)
