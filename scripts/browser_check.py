"""Parcours navigateur autonome sur une base temporaire, sans toucher à la démo."""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    with tempfile.TemporaryDirectory() as temporary:
        with socket.socket() as candidate:
            candidate.bind(("127.0.0.1", 0))
            port = candidate.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        env = {**os.environ, "ATELIERS_DB": str(Path(temporary) / "browser.sqlite3")}
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "ateliers.app:app", "--host", "127.0.0.1", "--port", str(port), "--no-access-log"], cwd=ROOT, env=env)
        try:
            for _ in range(100):
                try:
                    if urlopen(url + "/health", timeout=1).status == 200:
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError("Le serveur de test ne démarre pas.")
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 1050}, locale="fr-FR")
                page_errors = []
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.goto(url)
                expect(page.get_by_role("heading", name="Les ateliers du quartier.")).to_be_visible()
                page.screenshot(path=str(OUTPUT / "01-accueil.png"), full_page=True)
                page.get_by_role("link", name="Constituer mon dossier").first.click()
                page.screenshot(path=str(OUTPUT / "02-compte.png"), full_page=True)
                data = {"first_name": "Alex", "last_name": "Martin", "email": "alexexample.test", "birth_date": "31/02/2001", "password": "AtelierDemo2026!", "password_confirmation": "AtelierDemo2026!", "member_code": "00A123"}
                for key, value in data.items():
                    page.locator(f"#{key}").fill(value)
                page.get_by_role("button", name="Valider").click()
                expect(page.locator(".error-summary")).to_contain_text("E101")
                expect(page.locator(".error-summary")).to_contain_text("E105")
                expect(page.locator(".error-summary")).to_contain_text("E108")
                expect(page.locator("#password")).to_have_value("")
                page.screenshot(path=str(OUTPUT / "03-erreurs.png"), full_page=True)
                page.get_by_role("link", name="Retour aux ateliers", exact=True).click()
                page.get_by_role("link", name="Constituer mon dossier").first.click()
                expect(page.locator("#first_name")).to_have_value("Alex")
                expect(page.locator("#member_code")).to_have_value("00A123")
                for key, value in {**data, "email": "alex@example.test", "birth_date": "14/03/2001", "member_code": "001234"}.items():
                    page.locator(f"#{key}").fill(value)
                page.get_by_role("button", name="Valider").click()
                expect(page).to_have_url(url + "/inscription")
                expect(page.locator("#slot")).to_be_disabled()
                expect(page.locator("#english-field")).to_be_hidden()
                page.locator("#activity").select_option("photo")
                expect(page.locator("#english-field")).to_be_visible()
                page.locator("#slot").select_option("photo-10")
                page.locator("#experience").select_option("aucune")
                for item in ["decouvrir", "apprendre", "rencontrer", "creer"]:
                    page.locator(f"#expectation_{item}").check()
                page.locator("#presentation_fr").fill("Je souhaite apprendre la photographie et rencontrer des personnes.")
                page.locator("#presentation_en").fill("I want to learn photography and meet people.")
                page.locator("#terms_accepted").check()
                page.get_by_role("button", name="Valider").click()
                expect(page.locator(".error-summary")).to_contain_text("E111")
                page.locator("#expectation_decouvrir").uncheck()
                page.locator("#expectation_creer").uncheck()
                page.locator("#activity").select_option("peinture")
                expect(page.locator("#slot")).to_have_value("")
                expect(page.locator("#presentation_en")).to_be_disabled()
                page.locator("#activity").select_option("photo")
                page.locator("#slot").select_option("photo-10")
                page.get_by_role("link", name="Retour aux ateliers", exact=True).click()
                page.get_by_role("link", name="Espace adhérent").click()
                expect(page.locator("#activity")).to_have_value("photo")
                expect(page.locator("#slot")).to_have_value("photo-10")
                expect(page.locator("#expectation_apprendre")).to_be_checked()
                expect(page.locator("#presentation_en")).to_have_value("I want to learn photography and meet people.")
                page.screenshot(path=str(OUTPUT / "04-inscription.png"), full_page=True)
                # Demonstrate actual native maxlength behavior (typed input).
                page.locator("#presentation_fr").fill("")
                page.locator("#presentation_fr").press_sequentially("a" * 201)
                expect(page.locator("#presentation_fr")).to_have_value("a" * 200)
                page.locator("#presentation_fr").fill("Je souhaite apprendre la photographie et rencontrer des personnes.")
                page.get_by_role("button", name="Valider").click()
                expect(page.get_by_role("heading", name="Inscription enregistrée.")).to_be_visible()
                expect(page.locator("#registration-reference")).to_contain_text("ADQ-")
                page.screenshot(path=str(OUTPUT / "05-confirmation.png"), full_page=True)
                for width in [390, 320]:
                    mobile = browser.new_page(viewport={"width": width, "height": 844}, locale="fr-FR")
                    for path in ["/", "/compte/creation"]:
                        mobile.goto(url + path)
                        assert mobile.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"Débordement mobile {width}px : {path}"
                    if width == 390:
                        mobile.screenshot(path=str(OUTPUT / "06-mobile-compte.png"), full_page=True)
                    mobile.close()
                assert not page_errors, page_errors
                browser.close()
                print(json.dumps({"browser": "Chromium", "result": "ok", "screenshots": 6, "javascript_errors": page_errors, "mobile_widths": [390, 320]}, ensure_ascii=False))
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    main()
