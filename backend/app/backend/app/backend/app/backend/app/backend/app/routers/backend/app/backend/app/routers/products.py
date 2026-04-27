from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, schemas
from ..database import SessionLocal

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def read_products(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = Query(
        None,
        pattern="^(price_asc|price_desc)$"
    ),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    products, total = crud.get_products(
        db,
        q=q,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        skip=skip,
        limit=page_size
    )

    return {
        "data": [schemas.Product.from_orm(p).dict() for p in products],
        "count": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{product_id}", response_model=schemas.Product)
async def read_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )
    return db_product
