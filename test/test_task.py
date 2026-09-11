def get_auth_header(client, username, email, password):
    client.post("/users/", json={
        "user_name": username,
        "email": email,
        "password": password,
    })
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_and_get_task(client):
    headers = get_auth_header(client, "test_user", "testuser@example.com", "password123")
    create_res = client.post(
        '/task/',
        json={"title": "PyTest Integration Task", "description": "Testing FastAPI"},
        headers=headers
    )
    assert create_res.status_code == 201
    assert create_res.json()["title"] == "PyTest Integration Task"

    get_res = client.get("/tasks/", headers=headers)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1

def test_unauthorized_task_access_forbidden(client):
    headers_a = get_auth_header(client, "test_user", "testuser@example.com", "password123")
    task_res = client.post(
        "/tasks/",
        json={"title": "User A Private Secret Task"},
        headers=headers_a,
    )
    task_id = task_res.json()["id"]

    headers_b = get_auth_header(client, "userb", "userb@example.com", "pass123")
    delete_res = client.delete(f"/tasks/{task_id}", headers=headers_b)

    assert delete_res.status_code == 403
    assert delete_res.json()["detail"] == "Not authorized to delete this task"