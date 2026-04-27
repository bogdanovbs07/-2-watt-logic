from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from . import models, schemas


# --- Category CRUD ---

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    """Получить список всех категорий."""
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int):
    """Получить категорию по ID."""
    return db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()


def create_category(db: Session, category: schemas.CategoryCreate):
    """Создать новую категорию."""
    db_category = models.Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# --- Product CRUD ---

def get_products(
    db: Session,
    q: str = None,
    min_price: float = None,
    max_price: float = None,
    category_id: int = None,
    sort: str = None,
    skip: int = 0,
    limit: int = 10
):
    """Получить список продуктов с фильтрацией и сортировкой."""
    query = db.query(models.Product).options(
        joinedload(models.Product.category)
    )

    # Поиск по названию и описанию
    if q:
        query = query.filter(
            or_(
                models.Product.name.ilike(f"%{q}%"),
                models.Product.description.ilike(f"%{q}%")
            )
        )

    # Фильтр по цене
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    # Фильтр по категории
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)

    # Сортировка
    if sort == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(models.Product.price.desc())
    elif sort == "name_asc":
        query = query.order_by(models.Product.name.asc())
    elif sort == "name_desc":
        query = query.order_by(models.Product.name.desc())

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return products, total


def get_product(db: Session, product_id: int):
    """Получить продукт по ID с подгрузкой категории."""
    return db.query(models.Product).options(
        joinedload(models.Product.category)
    ).filter(
        models.Product.id == product_id
    ).first()


def create_product(db: Session, product: schemas.ProductCreate):
    """Создать новый продукт."""
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
