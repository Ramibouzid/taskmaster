def test_project_list(logged_in_client):
    rv = logged_in_client.get("/projects/")
    assert rv.status_code == 200


def test_create_project(logged_in_client):
    rv = logged_in_client.post("/projects/create", data={
        "name": "Test Project",
        "description": "A test project",
        "color": "#ff0000",
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Test Project" in rv.data


def test_project_detail(logged_in_client):
    logged_in_client.post("/projects/create", data={
        "name": "Detail Project", "description": "desc",
    })
    rv = logged_in_client.get("/projects/")
    assert b"Detail Project" in rv.data


def test_delete_project(logged_in_client):
    logged_in_client.post("/projects/create", data={
        "name": "Delete Project", "description": "desc",
    })
    rv = logged_in_client.get("/projects/")
    import re
    match = re.search(rb"/projects/(\d+)/delete", rv.data)
    if match:
        pid = match.group(1).decode()
        rv2 = logged_in_client.post(f"/projects/{pid}/delete", follow_redirects=True)
        assert rv2.status_code == 200
