"""Read/actions adapter checks against the isolated variant service on port 8003."""
import time
from aide.agent_browser import AgentBrowser
from aide.browser import BrowserProblem

b = AgentBrowser("http://host.docker.internal:8003")
observation = b.observe()
assert not observation["forms"]
try:
    b.open_link("https://example.org/collect")
    raise AssertionError("External link accepted")
except BrowserProblem:
    pass
b.links["outside"] = "https://example.org/collect"
try:
    b.open_link("outside")
    raise AssertionError("Forged external link accepted")
except BrowserProblem:
    pass
with b.page() as page:
    b._open(page, b.current_url)
    blocked = page.evaluate("async()=>{try{await fetch('/demarches/ouvrir-espace',{method:'POST',body:'unauthorized'});return false}catch(e){return true}}")
    assert blocked, "A POST was allowed outside the authorized submission tool"
link = next(x for x in observation["links"] if "Espace adhérent" in x["label"])
observation = b.open_link(link["id"])
form_id = observation["forms"][0]["id"]
form = b.forms[form_id]
assert "/demarches/ouvrir-espace" in form["url"]
assert form["fields"][0]["id"] == "given_name"
values = {"given_name": "Test", "email": f"adapter.{time.time_ns()}@example.test", "password": "AtelierDemo2026!"}
signature = form["signature"]
form["signature"] = "obsolete-snapshot"
assert b.send(form_id, "account", values)["status"] == "changed"
form = b.forms[form_id]
form["signature"] = signature
result = b.send(form_id, "account", values)
assert result["status"] == "ok", result["status"]
assert b.recover(form_id, "account", {})["status"] == "ok"
observation = b.observe()
form_id = observation["forms"][0]["id"]
assert "/demarches/choisir-seance" in b.forms[form_id]["url"]
options = b.read_choices(form_id, "slot", {"activity": "peinture"})
assert options[0]["value"] == "peinture-03"
values = {"activity": "peinture", "slot": "peinture-03"}
result = b.send(form_id, "reservation", values)
assert result["status"] == "ok", result["status"]
ref = result["receipt"]["reference"]
result = b.recover(form_id, "reservation", values)
assert result["receipt"]["reference"] == ref
assert b.send(form_id, "reservation", values)["status"] == "rejected"
print("Adaptateur agent : routes déplacées, identifiant modifié, lien extérieur refusé, récupération et doublon vérifiés.")
