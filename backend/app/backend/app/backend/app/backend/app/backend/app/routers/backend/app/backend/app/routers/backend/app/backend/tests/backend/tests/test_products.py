"""
Тесты для эндпоинтов продуктов.
Используют тестовую БД в памяти (SQLite).
"""


class TestGetProducts:
    """Тесты для GET /products/"""

    def test_get_all_products(self, client, sample_products):
        """Получение всех товаров без параметров."""
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert "page" in data
        assert "page_size" in data
        assert data["count"] == 5
        assert len(data["data"]) == 5

    def test_search_by_query(self, client, sample_products):
        """Поиск товаров по названию."""
        response = client.get("/products/?q=Hub")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert "Hub" in data["data"][0]["name"]

    def test_filter_by_price_range(self, client, sample_products):
        """Фильтрация товаров по диапазону цен."""
        response = client.get("/products/?min_price=40&max_price=100")
        assert response.status_code == 200
        data = response.json()
        for product in data["data"]:
            assert 40 <= product["price"] <= 100

    def test_sort_by_price_asc(self, client, sample_products):
        """Сортировка по возрастанию цены."""
        response = client.get("/products/?sort=price_asc")
        assert response.status_code == 200
        data = response.json()
        prices = [p["price"] for p in data["data"]]
        assert prices == sorted(prices)

    def test_sort_by_price_desc(self, client, sample_products):
        """Сортировка по убыванию цены."""
        response = client.get("/products/?sort=price_desc")
        assert response.status_code == 200
        data = response.json()
        prices = [p["price"] for p in data["data"]]
        assert prices == sorted(prices, reverse=True)

    def test_sort_by_name_asc(self, client, sample_products):
        """Сортировка по названию (А-Я)."""
        response = client.get("/products/?sort=name_asc")
        assert response.status_code == 200
        data = response.json()
        names = [p["name"] for p in data["data"]]
        assert names == sorted(names)

    def test_filter_by_category(self, client, sample_products, sample_categories):
        """Фильтрация по категории."""
        charger_id = sample_categories[0].id
        response = client.get(f"/products/?category_id={charger_id}")
        assert response.status_code == 200
        data = response.json()
        for product in data["data"]:
            assert product["category_id"] == charger_id

    def test_pagination(self, client, sample_products):
        """Проверка пагинации."""
        response = client.get("/products/?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["count"] == 5

    def test_pagination_second_page(self, client, sample_products):
        """Проверка второй страницы."""
        response = client.get("/products/?page=2&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 2


class TestGetProductById:
    """Тесты для GET /products/{id}"""

    def test_get_existing_product(self, client, sample_products):
        """Получение существующего товара."""
        product_id = sample_products[0].id
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == sample_products[0].name
        assert data["price"] == sample_products[0].price

    def test_get_product_not_found(self, client, sample_products):
        """Запрос несуществующего товара."""
        response = client.get("/products/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Товар не найден"

    def test_get_product_with_category(self, client, sample_products, sample_categories):
        """Товар содержит вложенную категорию."""
        product = sample_products[0]  # MagSafe Charger
        response = client.get(f"/products/{product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["category"] is not None
        assert data["category"]["name"] == sample_categories[0].name


class TestGetCategories:
    """Тесты для GET /categories/"""

    def test_get_all_categories(self, client, sample_categories):
        """Получение списка категорий."""
        response = client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Charger"

    def test_get_category_by_id(self, client, sample_categories):
        """Получение категории по ID."""
        cat_id = sample_categories[0].id
        response = client.get(f"/categories/{cat_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cat_id
        assert data["name"] == "Charger"

    def test_get_category_not_found(self, client, sample_categories):
        """Запрос несуществующей категории."""
        response = client.get("/categories/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Категория не найдена"


class TestCreateCategory:
    """Тесты для POST /categories/"""

    def test_create_category(self, client, db_session):
        """Создание новой категории."""
        payload = {
            "name": "Audio",
            "description": "Аудиоустройства"
        }
        response = client.post("/categories/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Audio"
        assert data["description"] == "Аудиоустройства"
        assert "id" in data

        # Проверяем, что категория создалась в БД
        from app.models import Category
        db_category = db_session.query(Category).filter(
            Category.name == "Audio"
        ).first()
        assert db_category is not None
