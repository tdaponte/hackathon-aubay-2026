"""Adaptateur borné au site d'ateliers : observation DOM et actions Playwright.

Une session isolée par utilisateur. Chromium est fermé après chaque opération ;
seuls les cookies / storage_state restent en mémoire, jamais dans un fichier.
"""
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse
import re
from playwright.sync_api import sync_playwright


class BrowserProblem(Exception):
    pass


EXTRACT = """
form => ({
  action: form.action,
  method: form.method,
  fields: Array.from(form.elements)
    .filter(e => e.name && e.type !== 'hidden' && !['submit','button'].includes(e.type))
    .map(e => ({
      id: e.id, name: e.name, type: e.tagName === 'SELECT' ? 'select' : e.type,
      label: Array.from(e.labels || []).map(l => l.innerText).join(' ').replace(/\\s*\\*\\s*$/, '').trim(),
      required: e.required, disabled: e.disabled,
      min_length: e.getAttribute('minlength'), max_length: e.getAttribute('maxlength'),
      options: e.tagName === 'SELECT' ? Array.from(e.options).filter(o => o.value && !o.disabled)
        .map(o => ({value:o.value, label:o.textContent.trim()})) : []
    }))
})
"""


class SiteBrowser:

    def __init__(self, base_url):
        parsed = urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise BrowserProblem("Adresse du site invalide.")
        self.base_url = base_url.rstrip("/")
        self.origin = (parsed.scheme, parsed.netloc)
        self._storage = None
        self.last_confirmation = None

    @contextmanager
    def page(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(storage_state=self._storage, locale="fr-FR", viewport={"width": 1280, "height": 1000})
            context.route("**/*", lambda route: route.continue_() if
                          (urlparse(route.request.url).scheme, urlparse(route.request.url).netloc) == self.origin else route.abort())
            page = context.new_page()
            page.set_default_timeout(10000)
            try:
                yield page
            finally:
                self._storage = context.storage_state()
                context.close()
                browser.close()

    def _open(self, page, path):
        url = urljoin(self.base_url + "/", path)
        if (urlparse(url).scheme, urlparse(url).netloc) != self.origin:
            raise BrowserProblem("Navigation hors du site refusée.")
        page.goto(url, wait_until="domcontentloaded")

    @staticmethod
    def _control(page, field):
        # Escape observed identifiers before building a CSS selector.
        selector = page.evaluate("id => '#' + CSS.escape(id)", field["id"])
        return page.locator(selector)

    def _receipt(self, page):
        reference = page.locator("#registration-reference").inner_text().strip()
        if not re.fullmatch(r"ADQ-[A-F0-9]{12}", reference):
            raise BrowserProblem("La confirmation ne contient pas de référence valide.")
        self.last_confirmation = urlparse(page.url).path
        return {
            "reference": reference,
            "activity": page.locator(".receipt h2").inner_text(),
            "slot": page.locator(".receipt-slot").inner_text(),
            "text": page.locator(".receipt").inner_text(),
            "screenshot": page.screenshot(full_page=True),
        }
