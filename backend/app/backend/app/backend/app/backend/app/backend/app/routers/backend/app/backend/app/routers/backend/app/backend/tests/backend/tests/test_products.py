from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_products_no_params():
    """Тест: GET /products без параметров возвращает 200 и правильную структуру."""
    response = client.get("/products/")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "count" in json_data
    assert "page" in json_data
    assert "page_size" in json_data
    assert json_data["count"] == 3
    assert json_data["page"] == 1
    assert json_data["page_size"] == 10
    assert len(json_data["data"]) == 3

def test_get_products_with_search_query():
    """Тест: GET /products?q=Hub возвращает только подходящие товары."""
    response = client.get("/products/?q=Hub")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["count"] >= 1
    for product in json_data["data"]:
        assert "Hub" in product["name"]

def test_get_products_price_filter():
    """Тест: GET /products с min_price и max_price фильтрует по цене."""
    response = client.get("/products/?min_price=40&max_price=60")
    assert response.status_code == 200
    json_data = response.json()
    for product in json_data["data"]:
        assert 40 <= product["price"] <= 60

def test_get_products_sort_price_asc():
    """Тест: GET /products?sort=price_asc сортирует по возрастанию цены."""
    response = client.get("/products/?sort=price_asc")
    assert response.status_code == 200
    json_data = response.json()
    prices = [p["price"] for p in json_data["data"]]
    assert prices == sorted(prices)

def test_get_product_by_id():
    """Тест: GET /products/1 возвращает конкретный товар."""
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data

def test_get_product_not_found():
    """Тест: GET /products/9999 возвращает 404."""
    response = client.get("/products/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"
