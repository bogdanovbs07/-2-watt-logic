from sqlalchemy.orm import Session
from . import models

def get_products(
    db: Session,
    q: str = None,
    min_price: float = None,
    max_price: float = None,
    sort: str = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(models.Product)

    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    if sort == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(models.Product.price.desc())

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return products, total

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
