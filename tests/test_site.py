import re
import pytest
from fastapi.testclient import TestClient
from ateliers.app import create_app
from ateliers.database import connect, reset, default_path
from ateliers.validation import email_valid

ACCOUNT = {"first_name": "Alex", "email": "alex.martin@example.test", "password": "AtelierDemo2026!"}
RESERVATION = {"activity": "photo", "slot": "photo-10"}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.sqlite3")) as client:
        yield client


def csrf(client, url="/compte/creation"):
    return re.search(r'name="csrf" value="([^"]+)"', client.get(url).text).group(1)


def signup(client, **updates):
    return client.post("/compte/creation", data={**ACCOUNT, **updates, "csrf": csrf(client)})


def register(client, **updates):
    return client.post("/inscription", data={**RESERVATION, **updates, "csrf": csrf(client, "/inscription")})


@pytest.mark.parametrize("value", ["a@exemple.fr", "alex@example.test", "a@example.com", "a@example.org"])
def test_valid_email(value):
    assert email_valid(value)


def test_login_existing_account_and_reservation(client):
    signup(client)
    with TestClient(client.app) as returning:
        assert str(returning.get("/inscription").url).endswith("/compte/connexion")
        response = returning.post("/compte/connexion", data={"email": ACCOUNT["email"].upper(), "password": ACCOUNT["password"], "csrf": csrf(returning, "/compte/connexion")})
        assert response.status_code == 200
        assert 'data-account-authenticated="true"' in response.text
        assert "/confirmation/ADQ-" in str(register(returning).url)
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 1


@pytest.mark.parametrize("email,password", [(ACCOUNT["email"], "WrongPassword123"), ("unknown@example.test", ACCOUNT["password"]), (ACCOUNT["email"], "short")])
def test_login_refusal_keeps_secret_private(client, email, password):
    signup(client)
    with TestClient(client.app) as returning:
        response = returning.post("/compte/connexion", data={"email": email, "password": password, "csrf": csrf(returning, "/compte/connexion")})
        assert response.status_code == 422 and "E120" in response.text
        assert password not in response.text
        assert 'data-account-authenticated="false"' in response.text
        assert returning.post("/compte/connexion", data={"email": email, "password": password}).status_code == 403


@pytest.mark.parametrize("value", ["aexample.fr", "a@example", "a b@example.fr", "a@@example.fr", "a@-example.fr", "a..b@example.fr"])
def test_invalid_email(value):
    assert not email_valid(value)


def test_real_flow_and_private_confirmation(client):
    assert signup(client).status_code == 200
    response = register(client)
    assert "/confirmation/ADQ-" in str(response.url)
    assert "Inscription enregistrée" in response.text
    assert ACCOUNT["password"] not in response.text
    with connect(client.app.state.db_path) as db:
        account = db.execute("SELECT * FROM accounts").fetchone()
        reservation = db.execute("SELECT * FROM registrations").fetchone()
        assert account["first_name"] == "Alex"
        assert account["password_hash"].startswith("scrypt$")
        assert reservation["slot"] == "photo-10"
        assert set(account.keys()) == {"id", "email", "first_name", "password_hash"}
        assert set(reservation.keys()) == {"reference", "account_id", "activity", "slot"}
    with TestClient(client.app) as stranger:
        assert stranger.get(str(response.url)).status_code == 404


@pytest.mark.parametrize("field,value,code", [
    ("first_name", "", "E100"), ("first_name", "a"*81, "E112"),
    ("email", "", "E100"), ("email", "alexexample.test", "E101"),
    ("email", "alex@example", "E101"), ("password", "", "E100"),
    ("password", "short", "E103"), ("password", "x"*129, "E103"),
])
def test_invalid_account_preserves_non_secret(client, field, value, code):
    response = signup(client, **{field: value})
    assert response.status_code == 422 and code in response.text
    assert 'type="password"' in response.text and ACCOUNT["password"] not in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 0


@pytest.mark.parametrize("password", ["a"*12, "x"*128, "😀"*6])
def test_password_boundaries(client, password):
    assert signup(client, password=password).status_code == 200


def test_duplicate_email_case_insensitive(client):
    signup(client)
    with TestClient(client.app) as other:
        response = signup(other, email=ACCOUNT["email"].upper())
        assert response.status_code == 422 and "E102" in response.text


@pytest.mark.parametrize("updates,code", [
    ({"activity": ""}, "E100"), ({"slot": ""}, "E100"),
    ({"activity": "inconnue"}, "E109"), ({"slot": "poterie-07"}, "E110"),
])
def test_invalid_reservation_retains_account(client, updates, code):
    signup(client)
    response = register(client, **updates)
    assert response.status_code == 422 and code in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM registrations").fetchone()[0] == 0


def test_duplicate_and_other_activity(client):
    signup(client)
    register(client)
    assert register(client).status_code == 422
    assert "E114" in register(client).text
    assert register(client, activity="peinture", slot="peinture-03").status_code == 200


def test_csrf_and_repeated_scalar(client):
    assert client.post("/compte/creation", data=ACCOUNT).status_code == 403
    response = client.post("/compte/creation", data={**ACCOUNT, "email": ["a@example.test", "b@example.test"], "csrf": csrf(client)})
    assert response.status_code == 403


def test_reset_and_default_v2(client, monkeypatch):
    signup(client)
    register(client)
    reset(client.app.state.db_path)
    assert signup(client).status_code == 200
    monkeypatch.delenv("ATELIERS_DB", raising=False)
    assert default_path().name == "ateliers-v2.sqlite3"


def test_no_removed_fields_in_html(client):
    html = client.get("/compte/creation").text
    for key in ["last_name", "birth_date", "member_code", "password_confirmation"]:
        assert 'name="' + key + '"' not in html
    signup(client)
    html = client.get("/inscription").text
    for key in ["experience", "expectations", "presentation_fr", "presentation_en", "newsletter", "terms_accepted"]:
        assert 'name="' + key + '"' not in html
    assert "anglais" not in html.lower()


def test_handoff_single_use_shares_account_and_reservations(client):
    from urllib.parse import urlparse, parse_qs
    assert client.post("/aide/ouvrir").status_code == 403
    opened = client.post("/aide/ouvrir", data={"csrf": csrf(client)}, follow_redirects=False)
    ticket = parse_qs(urlparse(opened.headers["location"]).query)["handoff"][0]
    with TestClient(client.app) as agent:
        joined = agent.post("/aide/rejoindre", headers={"Authorization": "Bearer " + ticket})
        assert joined.status_code == 200
        assert agent.post("/aide/rejoindre", headers={"Authorization": "Bearer " + ticket}).status_code == 403
        agent.cookies.set("adq_session", joined.json()["session"], domain="testserver.local", path="/")
        signup(agent)
        assert ACCOUNT["email"] in client.get("/").text
        confirmation = register(agent)
        reference = re.search(r"ADQ-[A-F0-9]{12}", confirmation.text).group(0)
        assert reference in client.get("/inscription").text
        assert client.post("/compte/deconnexion", data={"csrf": csrf(client, "/inscription")}).status_code == 200
        assert ACCOUNT["email"] not in client.get("/").text
        assert str(agent.get("/inscription").url).endswith("/compte/connexion")


def test_handoff_expired_unknown_and_revoked(client):
    from ateliers.database import create_handoff, consume_handoff
    csrf(client)
    session_id = client.cookies.get("adq_session")
    ticket = create_handoff(client.app.state.db_path, session_id)
    with connect(client.app.state.db_path) as db:
        db.execute("UPDATE aide_handoffs SET expires_at=0")
    assert consume_handoff(client.app.state.db_path, ticket) is None
    assert consume_handoff(client.app.state.db_path, "forged") is None
    ticket = create_handoff(client.app.state.db_path, session_id)
    client.post("/compte/deconnexion", data={"csrf": csrf(client)})
    assert consume_handoff(client.app.state.db_path, ticket) is None
