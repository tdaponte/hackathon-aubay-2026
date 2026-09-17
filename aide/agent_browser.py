"""Observed navigation. No account/reservation route is known to this adapter.

The inherited class supplies browser lifetime, escaped controls and the
site-specific receipt reader.
"""
import copy
import hashlib
import json
import re
from contextlib import contextmanager
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from .browser import SiteBrowser, BrowserProblem, EXTRACT


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class AgentBrowser(SiteBrowser):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.current_url = self.base_url + "/"
        self.links = {}
        self.forms = {}
        self.observation = {}
        self.last_receipt = None
        self._allowed_post = None
        self._linked_session = None

    def join_session(self, ticket):
        request = Request(self.base_url + "/aide/rejoindre", method="POST", headers={"Authorization": "Bearer " + ticket})
        try:
            with urlopen(request, timeout=10) as response:
                session = json.load(response)["session"]
            with self.page() as page:
                page.context.add_cookies([{"name": "adq_session", "value": session, "url": self.base_url + "/", "httpOnly": True, "sameSite": "Lax"}])
            self._linked_session = session
        except Exception:
            raise BrowserProblem("La liaison a expiré. Rouvre l’aide depuis le site d’origine.") from None

    def _open(self, page, path):
        super()._open(page, path)
        if self._linked_session:
            live = next((cookie["value"] for cookie in page.context.cookies(self.base_url) if cookie["name"] == "adq_session"), None)
            if live != self._linked_session:
                raise BrowserProblem("La session liée n’est plus active. Rouvre l’aide depuis le site.")

    @contextmanager
    def page(self):
        with super().page() as page:
            def guard(route):
                request = route.request
                if not self._same_origin(request.url):
                    return route.abort()
                if request.method in ("GET", "HEAD"):
                    return route.continue_()
                if request.method == "POST" and request.url == self._allowed_post:
                    self._allowed_post = None
                    return route.continue_()
                return route.abort()
            page.context.route("**/*", guard)
            try:
                yield page
            finally:
                self._allowed_post = None

    def _same_origin(self, url):
        parsed = urlparse(url)
        return (parsed.scheme, parsed.netloc) == self.origin and not parsed.username and not parsed.password

    def _form(self, page):
        forms = page.locator("main form:not([data-agent-ignore] form)")
        if forms.count() == 0:
            return None
        if forms.count() != 1:
            raise BrowserProblem("Plusieurs formulaires : parcours non pris en charge.")
        raw = forms.evaluate(EXTRACT)
        if raw["method"].lower() != "post" or not self._same_origin(raw["action"]):
            raise BrowserProblem("Destination du formulaire non autorisée.")
        if forms.locator("select[multiple]").count():
            raise BrowserProblem("Les listes multiples ne font pas partie de ce parcours.")
        ids = [f["id"] for f in raw["fields"]]
        if not ids or not all(ids) or len(ids) != len(set(ids)):
            raise BrowserProblem("Champs non identifiables.")
        fields, parent = [], None
        for source in raw["fields"]:
            if source["type"] not in ("text", "email", "password", "select"):
                raise BrowserProblem("Type de champ non pris en charge.")
            field = {k: source[k] for k in ("id", "label", "required")}
            field["kind"] = "choice" if source["type"] == "select" else "secret" if source["type"] == "password" else "text"
            if source["type"] == "email":
                field["format"] = "email"
            for key in ("min_length", "max_length"):
                if source[key] is not None:
                    field[key] = int(source[key])
            if field["kind"] == "choice":
                if source["disabled"] and parent:
                    field.update(depends_on=parent, options_by_value={})
                elif source["disabled"]:
                    raise BrowserProblem("Dépendance de liste inconnue.")
                else:
                    field["options"] = source["options"]
                    parent = field["id"]
            fields.append(field)
        signature = fingerprint({"url": page.url, "raw": raw})
        form_id = "form_" + signature[:16]
        return {"id": form_id, "signature": signature, "url": page.url,
                "action": raw["action"], "fields": fields}

    def _inspect(self, page):
        self.current_url = page.url
        self.links = {}
        links = []
        for a in page.locator("a[href]:not([data-agent-ignore] a)").all():
            url = urljoin(page.url, a.get_attribute("href"))
            if not self._same_origin(url) or not a.is_visible():
                continue
            key = "link_" + fingerprint(url)[:16]
            if key not in self.links:
                self.links[key] = url
                links.append({"id": key, "label": a.inner_text().strip()[:200]})
        form = self._form(page)
        if form:
            old = self.forms.get(form["id"])
            if old:
                for new, previous in zip(form["fields"], old["fields"]):
                    if "options_by_value" in previous:
                        new["options_by_value"] = previous["options_by_value"]
            self.forms[form["id"]] = form
        # Do not serialize input values, hidden fields, scripts, cookies or private receipts.
        text = page.locator("main").evaluate("""e => {const c=e.cloneNode(true);
          c.querySelectorAll('input,textarea,select,script,style,[hidden],.receipt,[data-agent-ignore]').forEach(n=>n.remove());
          return c.textContent.replace(/\\s+/g,' ').trim().slice(0,14000)}""")
        self.observation = {"page_id": "page_" + fingerprint(page.url)[:16],
            "authenticated": page.locator("main").get_attribute("data-account-authenticated") == "true",
            "title": page.title(), "text": text, "links": links,
            "forms": [{"id": form["id"], "fields": copy.deepcopy(form["fields"])}] if form else []}
        return copy.deepcopy(self.observation)

    def observe(self):
        with self.page() as page:
            self._open(page, self.current_url)
            return self._inspect(page)

    def open_link(self, link_id):
        if link_id not in self.links:
            raise BrowserProblem("Lien absent de la dernière observation.")
        url = self.links[link_id]
        if not self._same_origin(url):
            raise BrowserProblem("Navigation extérieure interdite.")
        with self.page() as page:
            self._open(page, url)
            return self._inspect(page)

    def read_choices(self, form_id, field_id, values):
        form = self.forms[form_id]
        field = next(f for f in form["fields"] if f["id"] == field_id)
        parent = next(f for f in form["fields"] if f["id"] == field.get("depends_on"))
        chosen = values.get(parent["id"])
        if chosen not in [o["value"] for o in parent["options"]]:
            raise BrowserProblem("Une réponse de l’utilisateur est nécessaire.")
        with self.page() as page:
            self._open(page, form["url"])
            live = self._form(page)
            if not live or live["signature"] != form["signature"]:
                raise BrowserProblem("Le formulaire a changé.")
            self._control(page, parent).select_option(chosen)
            control = self._control(page, field)
            if control.is_disabled():
                raise BrowserProblem("La liste reste indisponible.")
            options = control.evaluate("e=>Array.from(e.options).filter(o=>o.value&&!o.disabled).map(o=>({value:o.value,label:o.textContent.trim()}))")
            field["options_by_value"][chosen] = options
            return options

    def send(self, form_id, purpose, values):
        form = self.forms[form_id]
        with self.page() as page:
            self._open(page, form["url"])
            live = self._form(page)
            if not live or live["signature"] != form["signature"]:
                return {"status": "changed", "observation": self._inspect(page)}
            for field in form["fields"]:
                control = self._control(page, field)
                value = values.get(field["id"], "")
                if field["kind"] == "choice":
                    options = control.evaluate("e=>Array.from(e.options).filter(o=>o.value&&!o.disabled).map(o=>({value:o.value,label:o.textContent.trim()}))")
                    expected = field.get("options_by_value", {}).get(values.get(field.get("depends_on")), field.get("options", []))
                    if not expected or next((o for o in expected if o["value"] == value), None) not in options:
                        return {"status": "changed", "observation": self._inspect(page)}
                    control.select_option(value)
                else:
                    control.fill(value)
            try:
                self._allowed_post = form["action"]
                with page.expect_response(lambda r: r.request.method == "POST" and r.url == form["action"]) as pending:
                    page.locator('main form button[type="submit"]').click()
                response = pending.value
                page.wait_for_load_state("domcontentloaded")
                if response.status == 422:
                    errors = page.locator(".error-summary").inner_text()
                    return {"status": "rejected", "codes": re.findall(r"\bE\d{3}\b", errors),
                            "errors": errors, "observation": self._inspect(page)}
                if response.status == 303:
                    # Follow the response's real destination, not a predetermined URL.
                    destination = urljoin(form["action"], response.headers.get("location", ""))
                    if not self._same_origin(destination):
                        return {"status": "uncertain"}
                    page.wait_for_url(destination)
                    return self._success(page, purpose)
                return {"status": "uncertain"}
            except Exception:
                return {"status": "uncertain"}

    def _success(self, page, purpose):
        if purpose == "reservation" and page.locator("#registration-reference").count():
            self.last_receipt = self._receipt(page)
            return {"status": "ok", "receipt": self.last_receipt, "observation": self._inspect(page)}
        # This evidence reader remains specific to the demonstrator, independently of its URLs.
        if purpose in {"account", "login"} and page.locator('main[data-account-authenticated="true"]').count():
            return {"status": "ok", "observation": self._inspect(page)}
        return {"status": "uncertain", "observation": self._inspect(page)}

    def recover(self, form_id, purpose, values):
        form = self.forms[form_id]
        with self.page() as page:
            self._open(page, form["url"])
            if purpose in {"account", "login"}:
                return self._success(page, purpose)
            choices = [f for f in form["fields"] if f["kind"] == "choice"]
            if len(choices) != 2:
                return {"status": "uncertain"}
            for link in page.locator(".existing-reservations a").all():
                if link.get_attribute("data-activity") == values.get(choices[0]["id"]) and link.get_attribute("data-slot") == values.get(choices[1]["id"]):
                    self._open(page, link.get_attribute("href"))
                    return self._success(page, purpose)
            return {"status": "uncertain", "observation": self._inspect(page)}
