import hashlib
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connect(path: Path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            password_hash TEXT NOT NULL, birth_date TEXT NOT NULL, member_code TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY, csrf TEXT NOT NULL, account_id INTEGER REFERENCES accounts(id),
            expires_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS registrations (
            reference TEXT PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id),
            activity TEXT NOT NULL, slot TEXT NOT NULL, experience TEXT NOT NULL,
            expectations TEXT NOT NULL, presentation_fr TEXT NOT NULL, presentation_en TEXT NOT NULL,
            terms_accepted INTEGER NOT NULL CHECK (terms_accepted = 1), newsletter INTEGER NOT NULL,
            UNIQUE (account_id, activity)
        );
        """)


def get_session(path: Path, token: str | None) -> dict:
    with connect(path) as db:
        db.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
        session = db.execute("SELECT * FROM sessions WHERE id = ?", (token,)).fetchone() if token else None
        if session:
            return dict(session)
        session = {"id": secrets.token_urlsafe(32), "csrf": secrets.token_urlsafe(32),
                   "account_id": None, "expires_at": time.time() + 86400}
        db.execute("INSERT INTO sessions VALUES (:id, :csrf, :account_id, :expires_at)", session)
        return session


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def create_account(path: Path, session_id: str, values: dict) -> int:
    digest = password_hash(values["password"])
    with connect(path) as db:
        cursor = db.execute(
            "INSERT INTO accounts (email,first_name,last_name,password_hash,birth_date,member_code) VALUES (?,?,?,?,?,?)",
            (values["email"], values["first_name"], values["last_name"], digest,
             values["birth_date"], values.get("member_code", "")),
        )
        account_id = cursor.lastrowid
        db.execute("UPDATE sessions SET account_id = ? WHERE id = ?", (account_id, session_id))
        return account_id


def create_registration(path: Path, account_id: int, values: dict) -> str:
    reference = "ADQ-" + secrets.token_hex(6).upper()
    with connect(path) as db:
        db.execute("""INSERT INTO registrations
            (reference,account_id,activity,slot,experience,expectations,presentation_fr,presentation_en,terms_accepted,newsletter)
            VALUES (?,?,?,?,?,?,?,?,1,?)""",
            (reference, account_id, values["activity"], values["slot"], values["experience"],
             json.dumps(values["expectations"]), values["presentation_fr"], values["presentation_en"],
             int(values.get("newsletter") == "on")),
        )
    return reference


def reset(path: Path):
    initialize(path)
    with connect(path) as db:
        db.execute("DELETE FROM registrations")
        db.execute("DELETE FROM sessions")
        db.execute("DELETE FROM accounts")
