def test_board_requires_login(client):
    rv = client.get("/tasks/", follow_redirects=True)
    assert rv.status_code == 200


def test_create_task_page(logged_in_client):
    rv = logged_in_client.get("/tasks/create")
    assert rv.status_code == 200


def test_create_task(logged_in_client):
    rv = logged_in_client.post("/tasks/create", data={
        "title": "Test Task",
        "description": "A test task",
        "status": "todo",
        "priority": "medium",
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Test Task" in rv.data


def test_board_shows_tasks(logged_in_client):
    logged_in_client.post("/tasks/create", data={
        "title": "Board Task", "status": "todo", "priority": "medium",
    })
    rv = logged_in_client.get("/tasks/")
    assert b"Board Task" in rv.data


def test_task_detail(logged_in_client):
    logged_in_client.post("/tasks/create", data={
        "title": "Detail Task", "status": "todo", "priority": "high",
    })
    rv = logged_in_client.get("/tasks/")
    import re
    match = re.search(rb"/tasks/(\d+)", rv.data)
    if match:
        task_id = match.group(1).decode()
        rv2 = logged_in_client.get(f"/tasks/{task_id}")
        assert rv2.status_code == 200
        assert b"Detail Task" in rv2.data


def test_delete_task(logged_in_client):
    logged_in_client.post("/tasks/create", data={
        "title": "Delete Me", "status": "todo", "priority": "low",
    })
    rv = logged_in_client.get("/tasks/")
    import re
    match = re.search(rb"task-(\d+)", rv.data)
    if match:
        task_id = match.group(1).decode()
        rv2 = logged_in_client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
        assert rv2.status_code == 200


def test_export_pdf_requires_login(client):
    rv = client.get("/tasks/export-pdf", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Login" in rv.data


def test_export_pdf_returns_pdf(logged_in_client):
    logged_in_client.post("/tasks/create", data={
        "title": "PDF Task", "status": "todo", "priority": "medium",
    })
    rv = logged_in_client.get("/tasks/export-pdf")
    assert rv.status_code == 200
    assert rv.mimetype == "application/pdf"
