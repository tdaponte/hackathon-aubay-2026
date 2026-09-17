import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
import time
from contextlib import contextmanager


def default_path() -> Path:
    return Path(os.environ.get("ATELIERS_DB", Path(__file__).resolve().parent.parent / "data/ateliers-v2.sqlite3"))


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
            first_name TEXT NOT NULL, password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY, csrf TEXT NOT NULL, account_id INTEGER REFERENCES accounts(id),
            expires_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS registrations (
            reference TEXT PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id),
            activity TEXT NOT NULL, slot TEXT NOT NULL,
            UNIQUE (account_id, activity)
        );
        CREATE TABLE IF NOT EXISTS aide_handoffs (
            digest TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            expires_at REAL NOT NULL
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
            "INSERT INTO accounts (email,first_name,password_hash) VALUES (?,?,?)",
            (values["email"], values["first_name"], digest),
        )
        account_id = cursor.lastrowid
        db.execute("UPDATE sessions SET account_id = ? WHERE id = ?", (account_id, session_id))
        return account_id


def create_registration(path: Path, account_id: int, values: dict) -> str:
    reference = "ADQ-" + secrets.token_hex(6).upper()
    with connect(path) as db:
        db.execute("""INSERT INTO registrations
            (reference,account_id,activity,slot) VALUES (?,?,?,?)""",
            (reference, account_id, values["activity"], values["slot"]),
        )
    return reference


def authenticate(path: Path, session_id: str, email: str, password: str) -> bool:
    with connect(path) as db:
        account = db.execute("SELECT id,password_hash FROM accounts WHERE email=?", (email.strip(),)).fetchone()
        # A missing account still performs scrypt, with the same generic refusal.
        stored = account["password_hash"] if account else "scrypt$16384$8$1$" + "00" * 16 + "$" + "00" * 64
        try:
            algorithm, n, r, p, salt, expected = stored.split("$")
            if algorithm != "scrypt":
                return False
            digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
            valid = secrets.compare_digest(digest.hex(), expected)
        except (ValueError, TypeError):
            return False
        if not account or not valid:
            return False
        db.execute("UPDATE sessions SET account_id=? WHERE id=?", (account["id"], session_id))
        return True


def reset(path: Path):
    initialize(path)
    with connect(path) as db:
        db.execute("DELETE FROM registrations")
        db.execute("DELETE FROM sessions")
        db.execute("DELETE FROM accounts")


def create_handoff(path, session_id):
    ticket = secrets.token_urlsafe(32)
    with connect(path) as db:
        db.execute("DELETE FROM aide_handoffs WHERE expires_at < ? OR session_id=?", (time.time(), session_id))
        db.execute("INSERT INTO aide_handoffs VALUES (?,?,?)", (hashlib.sha256(ticket.encode()).hexdigest(), session_id, time.time() + 120))
    return ticket


def consume_handoff(path, ticket):
    if not isinstance(ticket, str) or len(ticket) > 100:
        return None
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("DELETE FROM aide_handoffs WHERE digest=? AND expires_at>? RETURNING session_id", (hashlib.sha256(ticket.encode()).hexdigest(), time.time())).fetchone()
        if not row:
            return None
        session = db.execute("SELECT * FROM sessions WHERE id=? AND expires_at>?", (row[0], time.time())).fetchone()
        return dict(session) if session else None
