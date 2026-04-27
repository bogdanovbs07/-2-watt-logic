from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("/", response_model=dict)
async def read_products(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None,
    sort: Optional[str] = Query(
        None,
        pattern="^(price_asc|price_desc|name_asc|name_desc)$"
    ),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Получить список продуктов с фильтрацией, сортировкой и пагинацией.
    
    - **q**: поиск по названию и описанию
    - **min_price / max_price**: фильтр по цене
    - **category_id**: фильтр по категории
    - **sort**: сортировка (price_asc, price_desc, name_asc, name_desc)
    - **page**: номер страницы
    - **page_size**: количество товаров на странице
    """
    skip = (page - 1) * page_size
    products, total = crud.get_products(
        db,
        q=q,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
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
    """
    Получить детальную информацию о товаре по ID.
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )
    return db_product
