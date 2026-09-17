"""Real conversation: create, book, then sign in again in a fresh browser session."""
import json
import os
import re
import shutil
import time
from urllib.parse import urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

OUTPUT = Path("output/interface-conversationnelle")
OUTPUT.mkdir(parents=True, exist_ok=True)
email_value = f"conversation.{time.time_ns()}@example.test"
password = "AtelierDemo2026!"
started = time.perf_counter()
expect.set_options(timeout=90000)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    recording = os.environ.get("RECORD_DEMO") == "1"
    video_dir = Path("output/demo-secours")
    video_options = {"record_video_dir": str(video_dir / "raw"), "record_video_size": {"width": 1280, "height": 1000}} if recording else {}
    context = browser.new_context(viewport={"width": 1280, "height": 1000}, **video_options)
    source = context.new_page()
    source.goto("http://host.docker.internal:8000/compte/creation")

    def launch(source):
        # Docker's browser reaches Windows through this alias. Only the public
        # redirect hostname is translated; the POST and single-use ticket are real.
        def redirect(route):
            response = route.fetch(max_redirects=0)
            headers = dict(response.headers)
            headers["location"] = headers["location"].replace("127.0.0.1", "host.docker.internal")
            route.fulfill(response=response, headers=headers)
        source.context.route("**/aide/ouvrir", redirect)
        with source.context.expect_page() as opened:
            source.get_by_role("button", name="M’aider avec ce site", exact=True).click()
        help_page = opened.value
        help_page.set_default_timeout(90000)
        try:
            expect(help_page.get_by_role("heading", name="Actions", exact=True)).to_be_visible(timeout=60000)
        except Exception:
            address = urlparse(help_page.url)
            print("Help launch failed:", address.hostname, address.path, flush=True)
            print(help_page.locator('body').inner_text()[:2500], flush=True)
            help_page.screenshot(path=str(OUTPUT / "launch-failure.png"))
            raise
        assert "handoff" not in help_page.url
        return help_page

    page = launch(source)
    help_video = page.video
    page.set_default_timeout(90000)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def click(label):
        page.get_by_role("button", name=label, exact=True).click()

    def answer(value, field_id):
        field = page.locator('.st-key-input_' + field_id + ' input')
        expect(field).to_be_visible()
        field.fill(value)
        click("Envoyer ma réponse")

    def plain():
        text = page.locator('.st-key-action_panel').inner_text().lower()
        assert "secret d’authentification" not in text and "secret d'authentification" not in text
        assert "session de rattachement" not in text
        assert password not in text
        assert page.locator('.st-key-context_panel').inner_text() == stable_context

    expect(page.get_by_role("heading", name="Actions", exact=True)).to_be_visible()
    stable_context = page.locator('.st-key-context_panel').inner_text()
    assert "association" in stable_context
    page.screenshot(path=str(OUTPUT / "01-accueil.png"), full_page=True)
    page.locator('.st-key-reservation_action button').click()
    expect(page.get_by_text("Connecte-toi ou crée un compte pour réserver une activité.", exact=True)).to_be_visible()
    expect(page.locator('.st-key-action_panel input')).to_have_count(0)
    page.locator('.st-key-account_action button').click()
    page.locator('.st-key-choose_account button').click()
    answer("Camille", "first_name")
    answer("camilleexample.test", "email")
    expect(page.get_by_text("Il manque le signe @", exact=False)).to_be_visible()
    page.screenshot(path=str(OUTPUT / "02-erreur-email.png"), full_page=True)
    click("Retour")
    expect(page.locator('.st-key-action_panel input')).to_have_value("Camille")
    click("Envoyer ma réponse")
    expect(page.locator('.st-key-action_panel input')).to_have_value("camilleexample.test")
    answer(email_value, "email")
    expect(page.get_by_label("Mot de passe", exact=True)).to_have_attribute("type", "password")
    answer(password, "password")
    expect(page.get_by_text("Renseigné — valeur masquée", exact=True)).to_be_visible()
    plain()
    page.get_by_role("button", name="Modifier", exact=True).first.click()
    expect(page.locator('.st-key-action_panel input')).to_have_value("Camille")
    page.locator('.st-key-action_panel input').fill("Camille Démo")
    click("Enregistrer ma modification")
    expect(page.get_by_role("button", name="Créer mon compte", exact=True)).to_be_visible()
    page.screenshot(path=str(OUTPUT / "03-recapitulatif-compte.png"), full_page=True)
    click("Créer mon compte")
    expect(page.get_by_text("Ton compte est créé.", exact=True)).to_be_visible()
    source.reload()
    expect(source.locator('.account-status')).to_contain_text(email_value)
    expect(source.locator('.existing-reservations')).to_contain_text("Aucune réservation pour ce compte.")
    source.screenshot(path=str(OUTPUT / "preuve-compte-site.png"), full_page=True)
    expect(page.get_by_role("radio")).to_have_count(0)
    plain()
    click("Réserver une activité")
    photo = page.get_by_role("radio", name="Photographie", exact=True)
    expect(photo).to_be_visible()
    expect(page.get_by_role("radio", checked=True)).to_have_count(0)
    photo.focus()
    photo.press("Space")
    expect(photo).to_be_checked()
    click("Envoyer ma réponse")
    slot = page.get_by_role("radio", name="10 octobre 2026, 14 h–16 h", exact=True)
    expect(slot).to_be_visible()
    expect(page.get_by_role("radio", checked=True)).to_have_count(0)
    plain()
    page.locator('.st-key-input_slot').get_by_text("10 octobre 2026, 14 h–16 h", exact=True).click()
    click("Envoyer ma réponse")
    page.get_by_role("button", name="Modifier", exact=True).first.click()
    page.locator('.st-key-input_activity').get_by_text("Peinture", exact=True).click()
    click("Enregistrer ma modification")
    slot = page.get_by_role("radio", name="3 octobre 2026, 10 h–12 h", exact=True)
    expect(slot).to_be_visible()
    expect(page.get_by_role("radio", checked=True)).to_have_count(0)
    page.locator('.st-key-input_slot').get_by_text("3 octobre 2026, 10 h–12 h", exact=True).click()
    click("Enregistrer ma modification")
    expect(page.get_by_role("heading", name="Vérifie ta réservation")).to_be_visible()
    plain()
    page.screenshot(path=str(OUTPUT / "04-reservation.png"), full_page=True)
    for width in [390, 320]:
        page.set_viewport_size({"width": width, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
    page.screenshot(path=str(OUTPUT / "05-mobile.png"), full_page=True)
    page.get_by_role("heading", name="Vérifie ta réservation").scroll_into_view_if_needed()
    page.screenshot(path=str(OUTPUT / "05-mobile-actions.png"), full_page=True)
    click("Réserver cet atelier")
    expect(page.get_by_text("Le site a confirmé ta réservation.", exact=True)).to_be_visible()
    reference = re.search(r"ADQ-[A-F0-9]{12}", page.locator("body").inner_text()).group(0)
    source.reload()
    expect(source.locator('.existing-reservations')).to_contain_text(reference)
    expect(source.locator('.existing-reservations li')).to_have_count(1)
    source.screenshot(path=str(OUTPUT / "preuve-reservation-site.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 1000})
    plain()
    page.screenshot(path=str(OUTPUT / "06-confirmation.png"), full_page=True)
    click("Retour aux actions")
    expect(page.get_by_text("Tu es connecté à ton compte.", exact=True)).to_be_visible()

    # Log out explicitly, then relaunch help in the new shared anonymous session.
    source.get_by_role("button", name="Se déconnecter", exact=True).click()
    expect(source.get_by_text("Aucun compte connecté dans cet onglet.", exact=True)).to_be_visible()
    page.close()
    page = launch(source)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.locator('.st-key-account_action button').click()
    page.locator('.st-key-choose_login button').click()
    answer(email_value, "email")
    expect(page.get_by_label("Mot de passe", exact=True)).to_have_attribute("type", "password")
    answer(password, "password")
    stable_context = page.locator('.st-key-context_panel').inner_text()
    plain()
    click("Me connecter")
    expect(page.get_by_text("Tu es connecté à ton compte.", exact=True)).to_be_visible()
    source.goto("http://host.docker.internal:8000/inscription")
    expect(source.locator('.account-status')).to_contain_text(email_value)
    expect(source.locator('.existing-reservations')).to_contain_text(reference)
    expect(page.get_by_role("button", name="Réserver une activité", exact=True)).to_be_visible()
    page.screenshot(path=str(OUTPUT / "07-connexion.png"), full_page=True)
    plain()
    assert not errors, errors
    result = {"result": "ok", "reference": reference, "existing_account_login": True, "shared_source_session": True,
              "elapsed_seconds": round(time.perf_counter() - started, 2),
              "mobile_widths": [390, 320], "javascript_errors": errors}
    (OUTPUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    source_video = source.video
    context.close()
    if recording:
        shutil.copyfile(help_video.path(), video_dir / "aide-parcours-reel.webm")
        shutil.copyfile(source_video.path(), video_dir / "site-preuves-reelles.webm")
        print("Videos du parcours automatise disponibles dans output/demo-secours.")
    browser.close()
