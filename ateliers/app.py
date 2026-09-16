import json
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import database
from .content import ACCOUNT_FIELDS, ACTIVITIES, CATALOG_TEXT, EXPERIENCES, EXPECTATIONS, LOCATION, TERMS
from .validation import validate_account, validate_registration

ROOT = Path(__file__).resolve().parent
COOKIE = "adq_session"


def create_app(db_path: Path | None = None) -> FastAPI:
    path = db_path or Path(os.environ.get("ATELIERS_DB", ROOT.parent / "data" / "ateliers.sqlite3"))

    @asynccontextmanager
    async def lifespan(app):
        database.initialize(path)
        yield

    app = FastAPI(title="Les ateliers du quartier", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.db_path = path
    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    templates = Jinja2Templates(directory=ROOT / "templates")

    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        is_page = not request.url.path.startswith("/static/") and request.url.path != "/health"
        if is_page:
            request.state.session = database.get_session(path, request.cookies.get(COOKIE))
        response = await call_next(request)
        if is_page:
            response.set_cookie(COOKIE, request.state.session["id"], httponly=True, samesite="lax", max_age=86400)
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'self'"
        return response

    def render(request, template, *, status=200, **context):
        return templates.TemplateResponse(request=request, name=template, context={
            "session": request.state.session, "activities": ACTIVITIES, "experiences": EXPERIENCES,
            "expectations": EXPECTATIONS, "location": LOCATION, "terms": TERMS,
            "values": {}, "errors": [], **context,
        }, status_code=status)

    async def form_values(request, allowed, multi=()):
        form = await request.form(max_fields=40, max_files=0)
        csrf = form.get("csrf", "")
        if not isinstance(csrf, str) or not secrets.compare_digest(csrf, request.state.session["csrf"]):
            return None
        values = {}
        for key in allowed:
            items = form.getlist(key)
            if any(not isinstance(item, str) for item in items):
                return None
            if key in multi:
                values[key] = items
            elif len(items) > 1:
                return None
            else:
                values[key] = items[0] if items else ""
        return values

    def invalid_request(request):
        return render(request, "message.html", status=403, title="Demande non recevable",
                      message="La session ou les données de ce formulaire ne sont plus valides. Rechargez la page pour reprendre.")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return render(request, "home.html", title="Les ateliers du quartier", catalog_text=CATALOG_TEXT)

    @app.get("/compte/creation", response_class=HTMLResponse)
    def account_page(request: Request):
        if request.state.session["account_id"]:
            return RedirectResponse("/inscription", 303)
        return render(request, "account.html", title="Ouverture de l’espace adhérent", fields=ACCOUNT_FIELDS)

    @app.post("/compte/creation", response_class=HTMLResponse)
    async def account_post(request: Request):
        values = await form_values(request, [field[0] for field in ACCOUNT_FIELDS])
        if values is None:
            return invalid_request(request)
        if request.state.session["account_id"]:
            return render(request, "message.html", status=409, title="Espace déjà créé",
                          message="E102 — Identifiant électronique déjà affecté.", continue_url="/inscription")
        errors = validate_account(values)
        if not errors:
            try:
                database.create_account(path, request.state.session["id"], values)
                return RedirectResponse("/inscription", 303)
            except sqlite3.IntegrityError:
                errors = ["E102 — Identifiant électronique déjà affecté."]
        values.pop("password", None)
        values.pop("password_confirmation", None)
        return render(request, "account.html", status=422, title="Ouverture de l’espace adhérent",
                      fields=ACCOUNT_FIELDS, values=values, errors=errors)

    @app.get("/inscription", response_class=HTMLResponse)
    def registration_page(request: Request):
        if not request.state.session["account_id"]:
            return RedirectResponse("/compte/creation", 303)
        return render(request, "registration.html", title="Demande de participation à une session")

    @app.post("/inscription", response_class=HTMLResponse)
    async def registration_post(request: Request):
        if not request.state.session["account_id"]:
            return RedirectResponse("/compte/creation", 303)
        fields = ["activity", "slot", "experience", "expectations", "presentation_fr", "presentation_en", "terms_accepted", "newsletter"]
        values = await form_values(request, fields, multi=("expectations",))
        if values is None:
            return invalid_request(request)
        errors = validate_registration(values)
        if not errors:
            # Canonical option order is used in storage and confirmation.
            values["expectations"] = [item for item in EXPECTATIONS if item in values["expectations"]]
            try:
                reference = database.create_registration(path, request.state.session["account_id"], values)
                return RedirectResponse(f"/confirmation/{reference}", 303)
            except sqlite3.IntegrityError:
                errors = ["E114 — Participation déjà enregistrée pour cette activité."]
        return render(request, "registration.html", status=422, title="Demande de participation à une session",
                      values=values, errors=errors)

    @app.get("/confirmation/{reference}", response_class=HTMLResponse)
    def confirmation(request: Request, reference: str):
        with database.connect(path) as db:
            row = db.execute("""SELECT r.*, a.first_name,a.last_name,a.email
                FROM registrations r JOIN accounts a ON a.id=r.account_id
                WHERE r.reference=? AND r.account_id=?""",
                (reference, request.state.session["account_id"])).fetchone()
        if not row:
            return render(request, "message.html", status=404, title="Confirmation introuvable",
                          message="Cette inscription n’est pas accessible dans votre session.")
        registration = dict(row)
        registration["expectations"] = json.loads(registration["expectations"])
        return render(request, "confirmation.html", title="Inscription enregistrée", registration=registration)

    return app


app = create_app()
