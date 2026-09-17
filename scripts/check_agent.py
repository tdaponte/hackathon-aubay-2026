"""Agent réel Bedrock : appels d'outils et actions sur le démonstrateur local.

Crée un compte et une réservation fictifs. Exécution : python -m scripts.check_agent.
"""
import json
import os
import time
from pathlib import Path
from aide.connected import ConnectedJourney

started = time.perf_counter()
j = ConnectedJourney.start(os.environ.get("SITE_BASE_URL", "http://site:8000"))


def check():
    if j.status != "ready":
        print(json.dumps({"status": j.status, "error": j.error, "trace": j.trace}, ensure_ascii=False))
        # Observations/tool arguments contain no user values; print only the last safe tool results.
        print(json.dumps([{"type": m.type, "content": m.content, "tools": getattr(m, 'tool_calls', [])}
                          for m in j.messages[-4:]], ensure_ascii=False))
        raise SystemExit(1)


check()
email = f"agent.{time.time_ns()}@example.test"
reject_once = os.environ.get("AGENT_REJECTION") == "1"
for field in j.step["stage"]["fields"]:
    value = "AtelierDemo2026!" if field["kind"] == "secret" else ("a..b@example.test" if reject_once else email) if field.get("format") == "email" else "Camille"
    j.set_answer(field["id"], value)
    j.advance()
check()
j.advance()
check()
if reject_once:
    assert j.step["kind"] == "field" and j.step["field"].get("format") == "email"
    assert "account" not in j.completed and j.error
    j.set_answer(j.step["field"]["id"], email)
    j.advance()  # Back to the review, which must request the cleared secret.
    j.advance()
    assert j.step["field"]["kind"] == "secret"
    j.set_answer(j.step["field"]["id"], "AtelierDemo2026!")
    j.advance()
    j.advance()
    check()
assert j.authenticated and j.step["kind"] == "done" and j.receipt is None
j.begin_action("reservation")
check()
while j.step["kind"] == "field":
    field = j.step["field"]
    j.set_answer(field["id"], j.options(field)[0]["value"])
    j.advance()
    check()
j.advance()
check()
assert j.receipt and j.completed == {"reservation"} and j.authenticated
assert not j.secrets
message_dump = str([m.model_dump() for m in j.messages])
assert email not in message_dump and "AtelierDemo2026!" not in message_dump and "Camille" not in message_dump
output = Path(os.environ.get("AGENT_REPORT", "output/agent"))
output.mkdir(parents=True, exist_ok=True)
report = {"reference": j.receipt["reference"], "model_calls": len(j.metrics),
          "elapsed_seconds": round(time.perf_counter() - started, 2), "metrics": j.metrics, "trace": j.trace}
(output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
(output / "confirmation.png").write_bytes(j.receipt["screenshot"])
print(json.dumps(report, ensure_ascii=False))
