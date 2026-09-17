"""Parcours source sur une base temporaire : aucune donnée de démo modifiée."""
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
OUTPUT = ROOT / "output" / "site-v2"
OUTPUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as temporary:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "ateliers.app:app", "--host", "127.0.0.1", "--port", str(port), "--no-access-log"], cwd=ROOT, env={**os.environ, "ATELIERS_DB": str(Path(temporary) / "test.sqlite3")})
    try:
        for _ in range(100):
            try:
                urlopen(url + "/health", timeout=1)
                break
            except OSError:
                time.sleep(.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1360, "height": 1000})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url)
            page.get_by_role("link", name="Constituer mon dossier").first.click()
            for key, value in {"first_name": "Alex", "email": "alexexample.test", "password": "AtelierDemo2026!"}.items():
                page.locator("#" + key).fill(value)
            page.get_by_role("button", name="Valider").click()
            expect(page.locator(".error-summary")).to_contain_text("E101")
            expect(page.locator("#first_name")).to_have_value("Alex")
            expect(page.locator("#password")).to_have_value("")
            page.locator("#email").fill("alex@example.test")
            page.locator("#password").fill("AtelierDemo2026!")
            page.screenshot(path=str(OUTPUT / "compte.png"), full_page=True)
            page.get_by_role("button", name="Valider").click()
            expect(page.locator("#slot")).to_be_disabled()
            page.locator("#activity").select_option("photo")
            page.locator("#slot").select_option("photo-10")
            page.locator("#activity").select_option("peinture")
            expect(page.locator("#slot")).to_have_value("")
            page.locator("#activity").select_option("photo")
            page.locator("#slot").select_option("photo-10")
            page.screenshot(path=str(OUTPUT / "reservation.png"), full_page=True)
            page.get_by_role("button", name="Valider").click()
            expect(page.locator("#registration-reference")).to_contain_text("ADQ-")
            page.screenshot(path=str(OUTPUT / "confirmation.png"), full_page=True)
            assert not errors, errors
            browser.close()
            print("Site v2 : compte, erreur, créneaux et réservation réelle vérifiés.")
    finally:
        server.terminate()
        server.wait(timeout=10)
