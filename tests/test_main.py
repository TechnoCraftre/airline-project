from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_without_database(monkeypatch):
    monkeypatch.setattr("app.main.DATABASE_URL", "")
    response = client.get("/ready")
    assert response.status_code == 200


def test_create_booking_without_database(monkeypatch):
    monkeypatch.setattr("app.main.DATABASE_URL", "")
    response = client.post(
        "/bookings",
        json={"passenger_name": "Riya Sharma", "flight_number": "AI101", "seat": "12A"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "CONFIRMED"
