import re
from datetime import date

import pytest
from fastapi.testclient import TestClient

from ateliers.app import create_app
from ateliers.database import connect, reset
from ateliers.validation import email_valid, text_length, validate_account


ACCOUNT = {
    "first_name": "Alex", "last_name": "Martin", "email": "alex.martin@example.test",
    "password": "AtelierDemo2026!", "password_confirmation": "AtelierDemo2026!",
    "birth_date": "14/03/2001", "member_code": "001234",
}
REGISTRATION = {
    "activity": "photo", "slot": "photo-10", "experience": "aucune",
    "expectations": ["rencontrer", "apprendre"],
    "presentation_fr": "Je souhaite apprendre à prendre des photos et rencontrer des personnes.",
    "presentation_en": "I want to learn photography and meet people.",
    "terms_accepted": "on", "newsletter": "",
}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.sqlite3")) as client:
        yield client


def csrf(client, url="/compte/creation"):
    html = client.get(url).text
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


def signup(client, **updates):
    return client.post("/compte/creation", data={**ACCOUNT, **updates, "csrf": csrf(client)})


def register(client, **updates):
    return client.post("/inscription", data={**REGISTRATION, **updates, "csrf": csrf(client, "/inscription")})


@pytest.mark.parametrize("email", ["alex@example.test", "alex@example.fr", "alex@example.org", "alex@example.com"])
def test_email_suffixes(email):
    assert email_valid(email)


@pytest.mark.parametrize("email", ["alexexample.test", "alex@example", "a b@example.fr", "a@@example.fr", "a@-example.fr", "a..b@example.fr"])
def test_invalid_email(email):
    assert not email_valid(email)


def test_full_registration_persisted_and_private(client):
    assert signup(client).status_code == 200
    response = register(client)
    assert response.status_code == 200
    assert "/confirmation/ADQ-" in str(response.url)
    assert "Inscription enregistrée" in response.text
    assert "Refusées" in response.text
    assert ACCOUNT["password"] not in response.text
    assert ACCOUNT["birth_date"] not in response.text
    assert ACCOUNT["member_code"] not in response.text
    with connect(client.app.state.db_path) as db:
        account = db.execute("SELECT * FROM accounts").fetchone()
        registration = db.execute("SELECT * FROM registrations").fetchone()
        assert account["member_code"] == "001234"
        assert account["password_hash"].startswith("scrypt$")
        assert ACCOUNT["password"] not in account["password_hash"]
        assert registration["expectations"] == '["apprendre", "rencontrer"]'
        assert registration["newsletter"] == 0
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 1
    with TestClient(client.app) as stranger:
        assert stranger.get(str(response.url)).status_code == 404


@pytest.mark.parametrize("updates,code", [
    ({"email": "alexexample.test"}, "E101"),
    ({"member_code": "00A123"}, "E108"),
    ({"member_code": "１２３４５６"}, "E108"),
    ({"password": "court"}, "E103"),
    ({"password_confirmation": "different"}, "E104"),
    ({"birth_date": "31/02/2001"}, "E105"),
    ({"birth_date": "01/01/2999"}, "E106"),
    ({"first_name": "x" * 81}, "E112"),
    ({"last_name": " "}, "E100"),
])
def test_account_errors_preserve_answers_clear_passwords_and_do_not_write(client, updates, code):
    response = signup(client, **updates)
    assert response.status_code == 422
    assert code in response.text
    assert 'value="Alex"' in response.text or "first_name" in updates
    assert ACCOUNT["password"] not in response.text
    assert re.search(r'id="password"[^>]+value=""', response.text)
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 0


def test_optional_member_and_trimmed_names(client):
    response = signup(client, member_code="", first_name="  Éloïse-Anne  ", email="  alex@example.fr  ")
    assert response.status_code == 200
    with connect(client.app.state.db_path) as db:
        account = db.execute("SELECT * FROM accounts").fetchone()
        assert account["member_code"] == ""
        assert account["first_name"] == "Éloïse-Anne"
        assert account["email"] == "alex@example.fr"


@pytest.mark.parametrize("born,today,valid", [
    ("29/02/2004", date(2022, 2, 28), False),
    ("29/02/2004", date(2022, 3, 1), True),
    ("16/09/2008", date(2026, 9, 16), True),
    ("17/09/2008", date(2026, 9, 16), False),
    ("29/02/2001", date(2026, 9, 16), False),
    ("14/03", date(2026, 9, 16), False),
])
def test_dates(born, today, valid):
    assert (not validate_account({**ACCOUNT, "birth_date": born}, today=today)) == valid


def test_duplicate_account_case_insensitive(client):
    signup(client)
    with TestClient(client.app) as other:
        response = signup(other, email="ALEX.MARTIN@EXAMPLE.TEST")
        assert response.status_code == 422
        assert "E102" in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 1


@pytest.mark.parametrize("updates,code", [
    ({"activity": "unknown"}, "E109"),
    ({"slot": "poterie-07"}, "E110"),
    ({"experience": "unknown"}, "E109"),
    ({"expectations": []}, "E111"),
    ({"expectations": ["apprendre", "creer", "partager", "rencontrer"]}, "E111"),
    ({"expectations": ["apprendre", "apprendre"]}, "E111"),
    ({"expectations": ["non-propose"]}, "E109"),
    ({"presentation_fr": "x" * 201}, "E112"),
    ({"presentation_en": ""}, "E100"),
    ({"presentation_en": "x" * 201}, "E112"),
    ({"terms_accepted": ""}, "E113"),
    ({"newsletter": "invalid"}, "E109"),
])
def test_registration_errors_preserve_account_without_registration(client, updates, code):
    signup(client)
    response = register(client, **updates)
    assert response.status_code == 422
    assert code in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM registrations").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM accounts").fetchone()[0] == 1


@pytest.mark.parametrize("selections", [["apprendre"], ["apprendre", "creer"], ["apprendre", "creer", "partager"]])
def test_selection_cardinality_valid(client, selections):
    signup(client)
    assert register(client, expectations=selections).status_code == 200


def test_utf16_and_line_normalization(client):
    assert text_length("😀") == 2
    assert text_length("a\r\nb") == 3
    signup(client)
    response = register(client, presentation_fr="😀" * 100, presentation_en="a" * 200)
    assert response.status_code == 200


def test_emoji_over_limit(client):
    signup(client)
    response = register(client, presentation_fr="😀" * 100 + "x")
    assert response.status_code == 422
    assert "E112" in response.text


def test_irrelevant_english_discarded(client):
    signup(client)
    response = register(client, activity="peinture", slot="peinture-03", presentation_en="hidden data" * 300)
    assert response.status_code == 200
    assert "Présentation anglaise" not in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT presentation_en FROM registrations").fetchone()[0] == ""


def test_duplicate_registration_is_not_announced_as_new_success(client):
    signup(client)
    assert register(client).status_code == 200
    response = register(client)
    assert response.status_code == 422
    assert "E114" in response.text
    assert "Inscription enregistrée" not in response.text
    with connect(client.app.state.db_path) as db:
        assert db.execute("SELECT count(*) FROM registrations").fetchone()[0] == 1


def test_csrf_and_repeated_single_choice_rejected(client):
    assert client.post("/compte/creation", data=ACCOUNT).status_code == 403
    signup(client)
    response = register(client, activity=["photo", "peinture"])
    assert response.status_code == 403


def test_html_is_escaped(client):
    response = signup(client, first_name='<script>alert("x")</script>', member_code="x")
    assert '<script>alert("x")</script>' not in response.text
    assert "&lt;script&gt;" in response.text


def test_reset_invalidates_existing_session(client):
    signup(client)
    register(client)
    reset(client.app.state.db_path)
    response = client.get("/inscription")
    assert response.url.path == "/compte/creation"
    assert signup(client).status_code == 200
