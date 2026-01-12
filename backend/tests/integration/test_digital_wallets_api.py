def test_create_and_list_digital_wallets(client, test_user):
    user_id = test_user["id"]

    payload = {
        "user_id": user_id,
        "name": "Mi Wallet",
        "provider": "mercadopago",
        "identifier": "abc123",
        "currency": "ARS"
    }

    # Create
    resp = client.post("/api/v1/digital-wallets", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["provider"] == "mercadopago"
    assert body["user_id"] == user_id

    # List by user
    resp2 = client.get(f"/api/v1/digital-wallets/user/{user_id}")
    assert resp2.status_code == 200
    arr = resp2.json()
    assert isinstance(arr, list)
    assert len(arr) >= 1
    assert any(w["provider"] == "mercadopago" for w in arr)
