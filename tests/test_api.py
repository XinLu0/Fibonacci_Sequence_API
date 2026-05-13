import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (10, 55),
        (20, 6765),
    ],
)
def test_valid_inputs(client, n, expected):
    response = client.get(f"/fibonacci?n={n}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["n"] == n
    assert body["result"] == expected


def test_missing_parameter(client):
    response = client.get("/fibonacci")
    assert response.status_code == 422


def test_negative_parameter(client):
    response = client.get("/fibonacci?n=-1")
    assert response.status_code == 422


def test_non_integer_parameter(client):
    response = client.get("/fibonacci?n=abc")
    assert response.status_code == 422


def test_very_large_n(client):
    response = client.get("/fibonacci?n=100001")
    assert response.status_code == 422
    assert "excessive" in response.get_json()["error"].lower()


def test_boundary_n(client):
    response = client.get("/fibonacci?n=1000")
    assert response.status_code == 200


def test_response_content_type(client):
    response = client.get("/fibonacci?n=5")
    assert "application/json" in response.content_type
