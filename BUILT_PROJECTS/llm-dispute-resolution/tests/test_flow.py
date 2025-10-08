from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post_dispute_flow():
    payload = {
        "external_ref": "CASE-1",
        "customer_id": "c-1",
        "merchant_id": "m-1",
        "amount": 2599,
        "currency": "USD",
        "narrative": "I did not authorize this transaction at StoreXYZ"
    }
    resp = client.post("/v1/disputes", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["classification"]["label"] == "FRAUD_UNAUTHORIZED"
    assert "recommendation" in data
    metrics = client.get("/v1/metrics").json()
    assert metrics["total_cases"] >= 1
