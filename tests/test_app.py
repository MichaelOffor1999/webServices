from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all():
    response = client.get("/getAll")
    assert response.status_code == 200
    assert isinstance(response.json()["products"], list)

def test_get_single_product_valid():
    response = client.get("/getSingleProduct?product_id=AUTO001")
    assert response.status_code == 200
    assert "Name" in response.json()

def test_get_single_product_invalid():
    response = client.get("/getSingleProduct?product_id=DOESNOTEXIST")
    assert response.status_code == 404

def test_starts_with():
    response = client.get("/startsWith?letter=s")
    assert response.status_code == 200
    assert isinstance(response.json()["products"], list)

def test_add_new_and_delete():
    client.delete("/deleteOne?product_id=UNIQUE_TEST_001")  # Clean-up just in case

    new_product = {
        "ProductID": "UNIQUE_TEST_001",
        "Name": "Test Product",
        "UnitPrice": 10.99,
        "StockQuantity": 5,
        "Description": "Test description"
    }

    # Add
    add_response = client.post("/addNew", json=new_product)
    assert add_response.status_code == 200

    # Delete
    delete_response = client.delete("/deleteOne?product_id=UNIQUE_TEST_001")
    assert delete_response.status_code == 200

    # Add
    add_response = client.post("/addNew", json=new_product)
    assert add_response.status_code == 200

    # Delete
    delete_response = client.delete("/deleteOne?product_id=UNIQUE_TEST_001")
    assert delete_response.status_code == 200
