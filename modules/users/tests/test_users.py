import re
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

ADMIN = {"X-User-Id": "admin-1", "X-User-Role": "admin"}
STAFF_A = {"X-User-Id": "u-a", "X-User-Role": "staff"}
STAFF_B = {"X-User-Id": "u-b", "X-User-Role": "staff"}

valid_user = {
    "username": "ayu123",
    "email": "ayu@gmail.com",   # gmail wajib
    "password": "Aa1!aaaa",
    "role": "staff"
}

def test_01_create_success():
    r = client.post("/users", json=valid_user)
    assert r.status_code == 201
    body = r.json()
    assert "password" not in body
    assert re.fullmatch(r"^[a-z0-9]{6,15}$", body["username"])
    global USER_ID
    USER_ID = body["id"]

def test_02_create_invalid_email():
    # format tidak valid -> 422
    bad = valid_user | {"username": "ayu124", "email": "salah-format"}
    r = client.post("/users", json=bad)
    assert r.status_code == 422

    # domain non-gmail -> 422
    bad2 = valid_user | {"username": "ayu125", "email": "ayu@yahoo.com"}
    r2 = client.post("/users", json=bad2)
    assert r2.status_code == 422

def test_03_rbac_list_users():
    r = client.get("/users", headers=STAFF_A)
    assert r.status_code == 401 or r.status_code == 403
    r = client.get("/users", headers=ADMIN)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_04_get_self_and_forbidden_other():
    r = client.get(f"/users/{USER_ID}", headers=STAFF_A)
    if r.status_code in (401,403,404):
        rows = client.get("/users", headers=ADMIN).json()
        uid0 = rows[0]["id"]
        r = client.get(f"/users/{uid0}", headers={"X-User-Id": uid0, "X-User-Role": "staff"})
    assert r.status_code == 200
    uid = r.json()["id"]
    r2 = client.get(f"/users/{uid}", headers=STAFF_B)
    assert r2.status_code == 403

def test_05_update_self_and_no_password_leak():
    rows = client.get("/users", headers=ADMIN).json()
    uid = rows[0]["id"]
    r = client.patch(
        f"/users/{uid}",
        headers={"X-User-Id": uid, "X-User-Role": "staff"},
        json={"username": "ayu125"}
    )
    assert r.status_code == 200
    assert r.json()["username"] == "ayu125"
    assert "password" not in r.json()

def test_06_change_password_by_owner_and_admin_override():
    rows = client.get("/users", headers=ADMIN).json()
    uid = rows[0]["id"]
    r = client.post(
        f"/users/{uid}/password",
        headers={"X-User-Id": uid, "X-User-Role": "staff"},
        json={"current_password": "Salah1!a", "new_password": "New1!aaaa"}
    )
    assert r.status_code == 403
    r = client.post(
        f"/users/{uid}/password",
        headers=ADMIN,
        json={"current_password": "apaaja", "new_password": "New1!aaaa"}
    )
    assert r.status_code == 200

def test_07_delete_admin_only():
    r = client.post("/users", json={
        "username": "budi999",
        "email": "budi@gmail.com",   # gmail wajib
        "password": "Aa1!aaaa",
        "role": "staff"
    })
    uid = r.json()["id"]
    r2 = client.delete(f"/users/{uid}", headers=STAFF_A)
    assert r2.status_code in (401,403)
    r3 = client.delete(f"/users/{uid}", headers=ADMIN)
    assert r3.status_code == 204