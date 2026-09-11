def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "user_name": "test_user",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 201, f"Failed: {response.json()}"
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "testuser@example.com"


def test_login_user(client):
    
    create_res = client.post(
        "/users/",
        json={
            "user_name": "test_user",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    assert create_res.status_code == 201, f"User creation before login failed: {create_res.json()}"

    response = client.post(
        "/auth/login",
        data={"username": "test_user", "password": "password123"},
    )

    assert response.status_code == 200, f"Login failed: {response.json()}"
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"